"""AS24: auditable canonical FC-R rows on the reachability digraph H.

No solver and no physical enumeration required.  This is a valid inequality
for *integer station decisions* in COMP, not a constraint on the LP itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Mapping


@dataclass(frozen=True)
class FCRRow:
    direction: str
    region: tuple[str, ...]
    q: tuple[str, ...]
    demand: int
    # key=('F',tail,head) or ('y',vertex), coefficient positive integer
    terms: tuple[tuple[tuple[str, ...], int], ...]
    rhs: int

    @property
    def signature(self) -> tuple:
        return (self.direction, self.region, self.q)

    @property
    def name(self) -> str:
        return f'FC-R-{self.direction}[{",".join(self.region)};{",".join(self.q)}]'

    @property
    def algebraic_certificate(self) -> dict:
        return {
            'family': 'FC-R' if self.direction == 'origin' else 'FC-R-T',
            'region': list(self.region), 'q': list(self.q),
            'demand': self.demand,
            'rhs': self.rhs,
            'flow_terms': [[k[1], k[2], c] for k, c in self.terms if k[0] == 'F'],
            'station_terms': [[k[1], c] for k, c in self.terms if k[0] == 'y'],
            'proof': ('balance + exclusion of terminal heads' if self.direction == 'origin'
                      else 'balance + exclusion of source tails'),
        }

    def as_compiled(self, columns: Mapping[tuple, int]):
        """Adapt to AS23 audit row without changing the COMP compiler."""
        from experiments.cuts.verify_fcr_witness import make_row
        return make_row(self.name, ((columns[k], c) for k, c in self.terms), '>=', self.rhs)


def _graph(instance):
    vertices = set(instance.V)
    if not vertices or len(vertices) != len(instance.V):
        raise ValueError('V must be nonempty and unique')
    if len(instance.S) != len(instance.T) or len(set(instance.S)) != len(instance.S) or len(set(instance.T)) != len(instance.T):
        raise ValueError('S/T must be distinct internally and equicardinal')
    if not set(instance.S).union(instance.T) <= vertices:
        raise ValueError('unknown terminal')
    arcs = tuple(instance.A_r)
    if len(set(arcs)) != len(arcs) or any(u not in vertices or v not in vertices or u == v for u, v in arcs):
        raise ValueError('invalid arcs of H')
    return vertices, arcs


def _canonical_vertices(raw, vertices, name: str) -> tuple[str, ...]:
    values = tuple(raw)
    if len(values) != len(set(values)) or not set(values) <= vertices:
        raise ValueError(f'{name} is not a subset of V without duplicates')
    return tuple(sorted(values))


def eligible_frontier(instance, region, direction: str) -> tuple[str, ...]:
    """Frontier eligible for activation; terminal exemptions are mandatory."""
    vertices, arcs = _graph(instance)
    region = _canonical_vertices(region, vertices, 'L')
    if not region:
        raise ValueError('empty region')
    R = set(region)
    if direction == 'origin':
        return tuple(sorted({v for u, v in arcs if u in R and v not in R} - set(instance.T)))
    if direction == 'destination':
        return tuple(sorted({u for u, v in arcs if v in R and u not in R} - set(instance.S)))
    raise ValueError('unknown direction')


def region_excess(instance, region, direction: str) -> int:
    vertices, _ = _graph(instance)
    L = _canonical_vertices(region, vertices, 'L')
    d = len(set(instance.S).intersection(L)) - len(set(instance.T).intersection(L))
    if direction == 'origin':
        return d
    if direction == 'destination':
        return -d
    raise ValueError('unknown direction')


def construct_row(instance, region, q, direction='origin') -> FCRRow:
    """Reject invalid L/Q rather than constructing a possibly invalid cut."""
    vertices, arcs = _graph(instance)
    L = _canonical_vertices(region, vertices, 'L')
    Q = _canonical_vertices(q, vertices, 'Q')
    if not L:
        raise ValueError('empty region')
    demand = region_excess(instance, L, direction)
    if demand <= 0:
        raise ValueError('non-positive directional excess')
    if not set(Q) <= set(eligible_frontier(instance, L, direction)):
        raise ValueError('Q contains an ineligible terminal, region vertex or non-frontier vertex')
    R, chosen = set(L), set(Q)
    if direction == 'origin':
        flow = [('F',u,v) for u,v in arcs if u in R and v not in R and v not in chosen]
    else:
        flow = [('F',u,v) for u,v in arcs if v in R and u not in R and u not in chosen]
    terms = tuple(sorted([(key, 1) for key in flow] + [(('y',v), demand) for v in Q]))
    return FCRRow(direction, L, Q, demand, terms, demand)


def evaluate(row: FCRRow, y: Mapping, f: Mapping):
    """Exact for Fraction/int inputs; for floats preserves native precision."""
    result = 0
    for key, coeff in row.terms:
        val = f.get((key[1], key[2]), 0) if key[0] == 'F' else y.get(key[1], 0)
        if not isinstance(val, (int, float, Fraction)) or not math.isfinite(float(val)):
            raise ValueError('nonfinite or nonnumeric candidate')
        result += coeff * val
    return result
