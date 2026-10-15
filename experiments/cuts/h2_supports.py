"""AS15: deterministic, bounded proposals of H2 supports (never certificates)."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping

from h2_oracle_schema import order_vertices, vertex_key


@dataclass(frozen=True)
class SupportProposal:
    support: tuple
    source: str
    mass: float


def select_supports(vertices, y_star: Mapping, *, k_supports=(), hall_supports=(),
                    max_supports: int = 32, max_support_size: int | None = None,
                    max_pairs: int = 32) -> tuple[SupportProposal, ...]:
    """Anchor V, then Hall/K unions, fractional support and primitive seeds.

    Inputs from K/Hall only propose R; they never certify a coefficient.
    No global enumeration of subsets is performed, even for large V.
    """
    V = order_vertices(vertices)
    vset = set(V)
    if len(V) != len(vset):
        raise ValueError('duplicate vertices')
    for name, val in [('max_supports', max_supports), ('max_pairs', max_pairs)]:
        if type(val) is not int or val < 0:
            raise ValueError(f'{name} must be nonnegative int')
    if max_support_size is not None and (type(max_support_size) is not int or max_support_size < 0):
        raise ValueError('max_support_size must be nonnegative int or None')
    if set(y_star) != vset:
        raise ValueError('y_star keys must match V')
    cap = len(V) if max_support_size is None else max_support_size
    proposals: dict[tuple, tuple[int, str]] = {}

    def register(raw, source, priority):
        for vertex in raw:
            vertex_key(vertex)
        R = order_vertices(set(raw))
        if not R or len(R) > cap or not set(R) <= vset:
            if not set(R) <= vset:
                raise ValueError('support outside V')
            return
        if R not in proposals or priority < proposals[R][0]:
            proposals[R] = (priority, source)

    register(V, 'FULL_V', 0)
    halls = sorted({order_vertices(set(s)) for s in hall_supports}, key=lambda r: tuple(vertex_key(v) for v in r))
    ks = sorted({order_vertices(set(s)) for s in k_supports}, key=lambda r: tuple(vertex_key(v) for v in r))
    for R in halls:
        register(R, 'HALL', 1)
    # Unions of small cover/Hall supports are candidates for stronger H2 rows.
    combined = sorted(set(halls + ks), key=lambda r: tuple(vertex_key(v) for v in r))
    for i, (a, b) in enumerate(combinations(combined, 2)):
        if i >= max_pairs:
            break
        register(set(a) | set(b), 'K_HALL_UNION', 2)
    fractional = tuple(v for v in V if 1e-9 < y_star[v] < 1 - 1e-9)
    register(fractional, 'FRACTIONAL', 3)
    for R in ks:
        register(R, 'K', 4)
    # Stable prioritization; no dependence on dict/set iteration or PYTHONHASHSEED.
    ordered = sorted(proposals.items(), key=lambda item: (
        item[1][0], sum(y_star[v] for v in item[0]), len(item[0]),
        tuple(vertex_key(v) for v in item[0])))
    return tuple(SupportProposal(s, src, float(sum(y_star[v] for v in s)))
                 for s, (_, src) in ordered[:max_supports])
