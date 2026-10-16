"""AS20: bounded, deterministic candidate supports for real-instance HL screening.

Candidates are hypotheses only; the physical AS14 oracle certifies every cut.
There is no global subset enumeration or dependency on H2 separation.
"""
from __future__ import annotations

from itertools import combinations
import math
from h2_oracle_schema import order_vertices, vertex_key


def select_hl_supports(vertices, y_star, *, k_supports, max_support_size=10,
                       max_supports=3, max_pairs=24):
    """Prefer small K supports/unions with low LP mass; never truncate a K set.

    Returns tuple of full supports. Large K supports are reported as excluded in
    diagnostics; their proper subsets are NOT asserted to be physically relevant.
    """
    for name, val in [('max_support_size', max_support_size),
                      ('max_supports', max_supports), ('max_pairs', max_pairs)]:
        if type(val) is not int or val < 0:
            raise ValueError(f'{name} must be nonnegative int')
    V = order_vertices(vertices)
    if len(V) != len(set(V)) or set(y_star) != set(V):
        raise ValueError('invalid vertices or LP point')
    if any(type(y_star[v]) not in (int, float) or not math.isfinite(y_star[v])
           or y_star[v] < -1e-6 or y_star[v] > 1 + 1e-6 for v in V):
        raise ValueError('invalid y_star')
    ksets = set()
    for raw in k_supports:
        support = order_vertices(raw)
        if not support or len(support) != len(set(support)) or not set(support) <= set(V):
            raise ValueError('invalid K support')
        ksets.add(support)
    ordered = sorted(ksets, key=lambda s: (len(s), tuple(vertex_key(v) for v in s)))
    feasible = [s for s in ordered if len(s) <= max_support_size]
    proposals = set(feasible)
    # Pairs are considered only among *eligible* K sets, not arbitrary V.
    # Rank by union size first so that the bounded pair quota actually probes
    # overlapping constraints instead of arbitrary disjoint sets.
    pair_choices = []
    for a, b in combinations(feasible, 2):
        joined = order_vertices(set(a) | set(b))
        if len(joined) <= max_support_size:
            pair_choices.append(joined)
    pair_choices.sort(key=lambda s: (len(s), sum(y_star[v] for v in s),
                                     tuple(vertex_key(v) for v in s)))
    considered_pairs = len(feasible) * (len(feasible) - 1) // 2
    retained_pairs = min(max_pairs, len(pair_choices))
    proposals.update(pair_choices[:max_pairs])
    # Prefer supports that jointly cover multiple K inequalities. The K4
    # witness requires a union of pairs (all four relays), not one K pair.
    def priority(s):
        cover_count = sum(set(k) <= set(s) for k in feasible)
        return (-cover_count, sum(y_star[v] for v in s), len(s),
                tuple(vertex_key(v) for v in s))
    ordered_proposals = sorted(proposals, key=priority)
    selected = tuple(ordered_proposals[:max_supports])
    return selected, {
        'policy': 'AS20_K_SMALL_AND_UNIONS_V1',
        'k_count': len(ksets), 'k_eligible_count': len(feasible),
        'k_excluded_by_size': len(ksets) - len(feasible),
        'k_pairs_considered': considered_pairs,
        'k_pair_unions_within_size_cap': len(pair_choices),
        'k_pair_unions_retained': retained_pairs,
        'candidate_count': len(proposals), 'selected_count': len(selected),
        'selected_support_sizes': [len(s) for s in selected],
        'no_eligible_support': not proposals,
    }
