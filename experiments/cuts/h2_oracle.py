"""AS14: certified tri-state physical matching oracle; no Gurobi integration.

The physical reachability routine is reused from independent_validator.py;
only the deterministic matching and its Hall certificate are added here.
The oracle operates on permitted *physical* stations, not current LP y*.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Mapping
from types import MappingProxyType

from independent_validator import _grafo_unitario, destinos_alcancaveis
from h2_oracle_schema import (Status, ViabilityResult, digest, order_vertices,
                              vertex_key)
from h2_oracle_cache import CertifiedCache


@dataclass(frozen=True)
class PhysicalInstance:
    V: tuple
    S: tuple
    T: tuple
    adj: Mapping
    r: int

    def __post_init__(self):
        vertices = tuple(self.V)
        sources = tuple(self.S)
        targets = tuple(self.T)
        for v in vertices + sources + targets:
            vertex_key(v)
        if len(set(vertices)) != len(vertices) or len(set(sources)) != len(sources) or len(set(targets)) != len(targets):
            raise ValueError('V, S and T must not contain duplicates')
        if len(sources) != len(targets):
            raise ValueError('|S| must equal |T|')
        if not set(sources + targets) <= set(vertices):
            raise ValueError('S and T must be contained in V')
        if type(self.r) is not int or self.r < 0:
            raise ValueError('r must be a nonnegative integer')
        if set(self.adj) != set(vertices):
            raise ValueError('adj keys must exactly match V')
        arcs = set()
        for u, neighbors in self.adj.items():
            if not isinstance(neighbors, (list, tuple)):
                raise ValueError('adj entries must be lists/tuples of (vertex, weight)')
            for w, weight in neighbors:
                if w not in set(vertices) or weight != 1 or type(weight) is not int:
                    raise ValueError('only unit edges between vertices of V are accepted')
                if w == u:
                    raise ValueError('self loops are not accepted')
                if (u, w) in arcs:
                    raise ValueError('duplicate directed edge')
                arcs.add((u, w))
        if any((w, u) not in arcs for u, w in arcs):
            raise ValueError('undirected graph requires symmetric adjacency')
        # Defend instance identity against mutation of the caller's V/S/T/adj.
        # Frozen dataclass alone does not freeze nested adjacency lists.
        object.__setattr__(self, 'V', vertices)
        object.__setattr__(self, 'S', sources)
        object.__setattr__(self, 'T', targets)
        object.__setattr__(self, 'adj', MappingProxyType({
            v: tuple((w, 1) for w, _ in self.adj[v]) for v in vertices
        }))

    @property
    def fingerprint(self) -> str:
        edges = set()
        for u, neighbors in self.adj.items():
            for w, _ in neighbors:
                edges.add(tuple(order_vertices((u, w))))
        edge_rows = sorted(edges, key=lambda pair: tuple(vertex_key(x) for x in pair))
        def row(x):
            return list(vertex_key(x))
        return digest({'graph': 'undirected-unit', 'V': [row(x) for x in order_vertices(self.V)],
                       'S': [row(x) for x in order_vertices(self.S)],
                       'T': [row(x) for x in order_vertices(self.T)],
                       'edges': [[row(u), row(v)] for u, v in edge_rows], 'r': self.r})

    @classmethod
    def from_tuple(cls, instance):
        # Existing AS13/independent-validator convention: (S, T, V, adj, r).
        S, T, V, adj, r = instance
        return cls(V, S, T, adj, r)


def _max_matching_with_hall(S, T, reach, probe):
    """Exact deterministic Kuhn augmentation + alternating-path Hall witness."""
    right_owner = {}

    def augment(s, seen):
        probe()
        for t in order_vertices(reach[s]):
            probe()
            if t in seen:
                continue
            seen.add(t)
            if t not in right_owner or augment(right_owner[t], seen):
                right_owner[t] = s
                return True
        return False

    for s in order_vertices(S):
        probe()
        augment(s, set())
    left_partner = {s: t for t, s in right_owner.items()}
    if len(right_owner) == len(S):
        return len(right_owner), tuple((s, left_partner[s]) for s in order_vertices(S)), (), ()

    # Alternating reachability from unmatched origins. All edges from visited
    # origins are traversed to destinations; matched edges return to origins.
    left_seen = set(S) - set(left_partner)
    frontier = list(order_vertices(left_seen))
    while frontier:
        probe()
        s = frontier.pop()
        for t in order_vertices(reach[s]):
            probe()
            other = right_owner.get(t)
            if other is not None and other not in left_seen:
                left_seen.add(other)
                frontier.append(other)
    neighbors = {t for s in left_seen for t in reach[s]}
    if len(neighbors) >= len(left_seen):
        raise AssertionError('matching deficiency did not produce a Hall witness')
    return len(right_owner), (), order_vertices(left_seen), order_vertices(neighbors)


class _BudgetExceeded(Exception):
    pass


class MatchingOracle:
    def __init__(self, cache: CertifiedCache | None = None, clock=None):
        self.cache = cache if cache is not None else CertifiedCache()
        self.clock = clock if clock is not None else time.monotonic
        self.calls = 0
        self.physical_computations = 0
        self.unknown_count = 0
        self.total_elapsed_wall_s = 0.0

    def check(self, instance: PhysicalInstance, allowed_stations, budget_s: float | None = None) -> ViabilityResult:
        if not isinstance(instance, PhysicalInstance):
            raise TypeError('instance must be a PhysicalInstance')
        supplied = tuple(allowed_stations)
        for v in supplied:
            vertex_key(v)
        stations = tuple(order_vertices(set(supplied)))
        if not set(stations) <= set(instance.V):
            raise ValueError('allowed stations must be a subset of physical V')
        if budget_s is not None and (isinstance(budget_s, bool) or not isinstance(budget_s, (int, float))
                                     or not math.isfinite(budget_s) or budget_s < 0):
            raise ValueError('budget_s must be finite and nonnegative, or None')
        budget = float(budget_s) if budget_s is not None else None
        sha = instance.fingerprint
        fingerprint = digest({'instance_sha256': sha,
                              'allowed_stations': [list(vertex_key(x)) for x in stations]})
        self.calls += 1
        begin = self.clock()

        def elapsed():
            return max(0., self.clock() - begin)

        def probe():
            if budget is not None and elapsed() >= budget:
                raise _BudgetExceeded()

        def result(status, size=None, witness=(), hall_origins=(), hall_destinations=(), reason=None, cache_hit=False):
            duration = elapsed()
            return ViabilityResult(status=status, instance_sha256=sha, allowed_stations=stations,
                                   robot_count=len(instance.S), matching_size=size,
                                   elapsed_wall_s=duration, budget_s=budget, calls=self.calls,
                                   fingerprint=fingerprint, witness=witness,
                                   hall_origins=hall_origins, hall_destinations=hall_destinations,
                                   reason=reason, cache_hit=cache_hit)

        try:
            probe()
            hit = self.cache.get(sha, stations)
            if hit is not None:
                probe()
                answer = result(hit.status, hit.matching_size, hit.witness,
                                hit.hall_origins, hit.hall_destinations, cache_hit=True)
                # The result() clock read can cross the deadline even if the
                # preceding probe passed (cache hit is still budgeted).
                # Check again before returning a certified cached result.
                probe()
                self.total_elapsed_wall_s += answer.elapsed_wall_s
                return answer
            self.physical_computations += 1
            graph = _grafo_unitario(instance.V, instance.adj)
            reach = {}
            for s in order_vertices(instance.S):
                probe()
                reach[s] = destinos_alcancaveis(s, instance.T, stations, graph, instance.r)
                probe()
            size, witness, hall_s, hall_t = _max_matching_with_hall(instance.S, instance.T, reach, probe)
            probe()
            status = Status.VIABLE if size == len(instance.S) else Status.INFEASIBLE
            # Internal certification: witnesses are checked against physical reach
            # and Hall neighbor set is computed from the *whole* reach graph.
            if status is Status.VIABLE:
                assert len(set(t for _, t in witness)) == len(witness)
                assert all(t in reach[s] for s, t in witness)
            else:
                assert len(hall_t) < len(hall_s)
                assert set(hall_t) == set().union(*(reach[s] for s in hall_s))
            answer = result(status, size, witness, hall_s, hall_t)
            # If the clock exceeded the budget between certification and return,
            # downgrade before cache writes or downstream classification.
            probe()
            self.cache.put(answer)
            self.total_elapsed_wall_s += answer.elapsed_wall_s
            return answer
        except _BudgetExceeded:
            answer = result(Status.UNKNOWN, reason='TIME_BUDGET_EXCEEDED')
            self.unknown_count += 1
            self.total_elapsed_wall_s += answer.elapsed_wall_s
            return answer
        except Exception as exc:
            # Contradictions are treated as UNKNOWN and reported; no invalid cut.
            answer = result(Status.UNKNOWN, reason=f'ORACLE_ERROR:{type(exc).__name__}')
            self.unknown_count += 1
            self.total_elapsed_wall_s += answer.elapsed_wall_s
            return answer

    def metrics(self) -> dict:
        return {'calls': self.calls, 'physical_computations': self.physical_computations,
                'cache_hits': self.cache.hits, 'cache_misses': self.cache.misses,
                'unknown_count': self.unknown_count,
                'total_elapsed_wall_s': self.total_elapsed_wall_s}


@dataclass(frozen=True)
class H2Classification:
    state: str  # CERTIFIED, NO_CUT, UNKNOWN
    instance_sha256: str
    support: tuple
    complement: tuple
    Bhat: tuple
    coefficients: tuple[tuple, ...]
    rhs: int | None
    examined: tuple
    unknown_candidates: tuple
    reason: str | None = None

    def to_dict(self):
        return {'schema_version': 'AS14-H2-CLASSIFICATION-v1', 'state': self.state,
                'instance_sha256': self.instance_sha256, 'support': list(self.support),
                'complement': list(self.complement), 'Bhat': list(self.Bhat),
                'coefficients': [[v, c] for v, c in self.coefficients], 'rhs': self.rhs,
                'examined': list(self.examined), 'unknown_candidates': list(self.unknown_candidates),
                'reason': self.reason}


def classify_h2(oracle: MatchingOracle, instance: PhysicalInstance, support,
                candidates=None, budget_s: float | None = None) -> H2Classification:
    """Certify H2 for a fixed R. UNKNOWN vertices get coefficient 2, never 1.

    A VIABLE complement makes the support ineligible for H2, and an UNKNOWN
    complement prevents emitting any certificate. Only explicitly proven
    INFEASIBLE single-station additions enter Bhat.
    """
    R = frozenset(support)
    if not R <= set(instance.V):
        raise ValueError('support must be a subset of V')
    examine = R if candidates is None else frozenset(candidates)
    if not examine <= R:
        raise ValueError('candidates must be a subset of support')
    if budget_s is not None and (isinstance(budget_s, bool) or not isinstance(budget_s, (float, int))
                                 or not math.isfinite(budget_s) or budget_s < 0):
        raise ValueError('invalid budget')
    R_sorted = order_vertices(R)
    F = frozenset(instance.V) - R
    F_sorted = order_vertices(F)
    start = oracle.clock()

    def remaining():
        if budget_s is None:
            return None
        return max(0., budget_s - max(0., oracle.clock() - start))

    complement = oracle.check(instance, F, budget_s=remaining())
    base = {'instance_sha256': instance.fingerprint, 'support': R_sorted,
            'complement': F_sorted}
    if complement.status is Status.UNKNOWN:
        return H2Classification('UNKNOWN', **base, Bhat=(), coefficients=(), rhs=None,
                                examined=(), unknown_candidates=order_vertices(examine),
                                reason='COMPLEMENT_NOT_CERTIFIED')
    if complement.status is Status.VIABLE:
        return H2Classification('NO_CUT', **base, Bhat=(), coefficients=(), rhs=None,
                                examined=(), unknown_candidates=(), reason='COMPLEMENT_VIABLE')
    Bhat = set()
    examined = []
    unknown = []
    for v in order_vertices(examine):
        outcome = oracle.check(instance, F | {v}, budget_s=remaining())
        examined.append(v)
        if outcome.status is Status.INFEASIBLE:
            Bhat.add(v)
        elif outcome.status is Status.UNKNOWN:
            unknown.append(v)
    coeffs = tuple((v, 1 if v in Bhat else 2) for v in R_sorted)
    return H2Classification('CERTIFIED', **base, Bhat=order_vertices(Bhat),
                            coefficients=coeffs, rhs=2, examined=tuple(examined),
                            unknown_candidates=tuple(unknown))
