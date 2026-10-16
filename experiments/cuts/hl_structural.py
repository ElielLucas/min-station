"""AS21: deterministic, explicitly heuristic HL support hypotheses.

Small whole K sets, bounded unions, and projections of large overlapping K
sets are candidates only. A projected set does NOT inherit K validity and no
inequality follows from selection. Every emitted inequality must independently
pass physical certification (hl_layered.py).
"""
from __future__ import annotations

from itertools import combinations
import math
from h2_oracle_schema import order_vertices, vertex_key


def select_structural_supports(vertices, y_star, *, k_supports,
                               max_support_size=14, max_supports=4,
                               max_pairs=32, max_k_seeds=48):
    for name, value in (('max_support_size', max_support_size),
                        ('max_supports', max_supports), ('max_pairs', max_pairs),
                        ('max_k_seeds', max_k_seeds)):
        if type(value) is not int or value < (1 if name == 'max_support_size' else 0):
            raise ValueError(f'invalid {name}')
    V = order_vertices(vertices)
    if len(set(V)) != len(V) or set(y_star) != set(V):
        raise ValueError('invalid V / LP point')
    if any(type(y_star[v]) not in (int, float) or not math.isfinite(y_star[v])
           or y_star[v] < 0 or y_star[v] > 1 for v in V):
        raise ValueError('invalid LP point')
    ksets = set()
    for raw in k_supports:
        k = order_vertices(raw)
        if not k or len(k) != len(set(k)) or not set(k) <= set(V):
            raise ValueError('invalid K support')
        ksets.add(k)
    ordered = sorted(ksets, key=lambda k: (len(k),
                     math.fsum(y_star[v] for v in k), tuple(vertex_key(v) for v in k)))
    eligible = [k for k in ordered if len(k) <= max_support_size]
    # Do not allow a huge K catalog to create an unbounded O(|K|^2) pass.
    seeds = sorted(ordered, key=lambda k: (len(k),
                   math.fsum(y_star[v] for v in k), tuple(vertex_key(v) for v in k)))[:max_k_seeds]
    proposals = {k: 'WHOLE_K' for k in eligible}
    pair_candidates = []
    for a, b in combinations(seeds, 2):
        joined = order_vertices(set(a) | set(b))
        if len(joined) <= max_support_size:
            pair_candidates.append((joined, 'K_UNION'))
        elif set(a) & set(b):
            # Rank intersection first; then high LP weights. These vertices
            # are hypotheses only (never silently reinterpret as a whole K).
            a_set, b_set = set(a), set(b)
            ranking = sorted(joined, key=lambda v: (-(v in a_set and v in b_set),
                                          -y_star[v], vertex_key(v)))
            projected = order_vertices(ranking[:max_support_size])
            pair_candidates.append((projected, 'K_PAIR_PROJECTION'))
    # Bound candidate work even when many pairs are eligible.
    pair_candidates.sort(key=lambda it: (-sum(y_star[v] for v in it[0]),
                         len(it[0]), tuple(vertex_key(v) for v in it[0]), it[1]))
    for support, kind in pair_candidates[:max_pairs]:
        if support not in proposals:
            proposals[support] = kind
    projected_singles = 0
    for big in (k for k in seeds if len(k) > max_support_size):
        ranking = sorted(big, key=lambda v: (-y_star[v], vertex_key(v)))
        projected = order_vertices(ranking[:max_support_size])
        if projected not in proposals:
            proposals[projected] = 'LARGE_K_PROJECTION'
            projected_singles += 1
    def rank(item):
        R, kind = item
        covered = sum(set(k) <= set(R) for k in seeds)
        # Multiple covered constraints before single support. Prefer a small
        # LP mass so a low cardinality rhs can actually violate the point.
        return (-covered, math.fsum(y_star[v] for v in R),
                -sum(0 < y_star[v] < 1 for v in R), len(R),
                tuple(vertex_key(v) for v in R), kind)
    selected = sorted(proposals.items(), key=rank)[:max_supports]
    return tuple(R for R, _ in selected), {
        'policy': 'AS21_K_INTERACTIONS_AND_PROJECTIONS_V1',
        'projection_requires_independent_oracle_certification': True,
        'k_count': len(ksets), 'k_eligible_count': len(eligible),
        'k_excluded_by_size': len(ksets) - len(eligible),
        'k_seeds_examined': len(seeds), 'pairs_considered': len(seeds)*(len(seeds)-1)//2,
        'pair_candidates_prequota': len(pair_candidates),
        'pair_candidates_retained': min(max_pairs, len(pair_candidates)),
        'large_k_projections_added': projected_singles,
        'candidate_count': len(proposals), 'selected_count': len(selected),
        'selected_support_sizes': [len(R) for R, _ in selected],
        'selected_kinds': [kind for _, kind in selected],
        'no_eligible_support': not selected,
    }
