"""AS25.1: FC-R/FC-R-T separation with a cheaper index and ranked selection.

Same inequalities, same exact Q for each fixed L and the same declared region
family as AS24/AS25 (all strict-excess singletons + at most ``max_larger``
heuristic regions).  Only the bookkeeping changes:

* the region plan is built once in O(|V| + |A| log |A|); AS24's
  ``choose_regions`` revalidates all arcs of H for every candidate region
  (O(|V||A| + |A|^2)), which dominated AS25 wall time;
* the frontier of each region on H is static between LP rounds, so it is
  cached at construction instead of rescanned;
* rows are assembled from the cached frontier.  ``audit_rows=True`` also builds
  every emitted row with the canonical AS24 ``construct_row`` and refuses any
  difference.

Selection policies (``selection``):

* ``'lexicographic'`` reproduces AS25: violated rows are emitted in region
  order until the cut cap;
* ``'deficit'`` ranks violated rows by deficit (ties: region order).

``larger_mode='escalate'`` examines the heuristic larger regions only in a
call where no new singleton row is violated.  Coverage reporting never claims
more than what was examined; Q remains exact only for each examined L.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
import time
from typing import Mapping

from .fcr_regions import RegionPlan
from .fcr_rows import FCRRow, construct_row, _graph

SELECTIONS = ('lexicographic', 'deficit')
LARGER_MODES = ('always', 'escalate')


def fast_region_plan(instance, *, max_larger: int=12, include_larger: bool=True) -> RegionPlan:
    """Same RegionPlan as ``fcr_regions.choose_regions``, validating H once."""
    if not isinstance(max_larger, int) or max_larger < 0:
        raise ValueError('invalid regional cap')
    vertices, arcs = _graph(instance)
    S, T = set(instance.S), set(instance.T)

    def signed(region):
        return sum(1 for v in region if v in S)-sum(1 for v in region if v in T)

    singles = tuple((v,) for v in sorted(vertices) if signed((v,)) != 0)
    if not include_larger:
        return RegionPlan(singles, (), 0, 0, max_larger)
    adj = {v: set() for v in vertices}
    for u, v in arcs:
        adj[u].add(v)
        adj[v].add(u)
    potential = {tuple(sorted((u, v))) for u, v in arcs}
    for items in (sorted(S-T), sorted(T-S)):
        for u, v in combinations(items, 2):
            if adj[u].intersection(adj[v]):
                potential.add((u, v))
    valid = sorted((R for R in potential if signed(R) != 0),
                   key=lambda r: (-abs(signed(r)), r))
    chosen = tuple(valid[:max_larger])
    return RegionPlan(singles, chosen, len(valid), len(valid)-len(chosen), max_larger)


@dataclass(frozen=True)
class CachedRegion:
    vertices: tuple[str, ...]
    direction: str
    demand: int
    kind: str
    # (arc, exterior vertex, exterior eligible for Q) for every frontier arc of H
    frontier: tuple[tuple[tuple[str, str], str, bool], ...]


class FastIndexedFCR:
    def __init__(self, instance, *, max_larger=12, include_larger=True,
                 selection='lexicographic', larger_mode='always', audit_rows=False):
        if selection not in SELECTIONS:
            raise ValueError('unknown selection policy')
        if larger_mode not in LARGER_MODES:
            raise ValueError('unknown larger-region mode')
        vertices, arcs = _graph(instance)
        self.instance = instance
        self.selection = selection
        self.larger_mode = larger_mode
        self.audit_rows = audit_rows
        self.vertex_set = vertices
        self.arc_set = set(arcs)
        out = {v: [] for v in vertices}
        inc = {v: [] for v in vertices}
        for u, v in arcs:
            out[u].append((u, v))
            inc[v].append((u, v))
        S, T = set(instance.S), set(instance.T)
        self.plan = fast_region_plan(instance, max_larger=max_larger, include_larger=include_larger)
        self.regions = []
        for kind, candidates in (('singleton', self.plan.singletons), ('heuristic', self.plan.larger)):
            for L in candidates:
                signed = len(S.intersection(L))-len(T.intersection(L))
                if not signed:
                    continue
                direction = 'origin' if signed > 0 else 'destination'
                R = set(L)
                exempt = T if direction == 'origin' else S
                frontier = []
                for vertex in L:
                    for u, v in (out[vertex] if direction == 'origin' else inc[vertex]):
                        exterior = v if direction == 'origin' else u
                        if exterior not in R:
                            frontier.append(((u, v), exterior, exterior not in exempt))
                self.regions.append(CachedRegion(L, direction, abs(signed), kind, tuple(frontier)))

    def _row(self, region: CachedRegion, Q: tuple[str, ...]) -> FCRRow:
        chosen = set(Q)
        flow = [(('F', u, v), 1) for (u, v), exterior, _ in region.frontier if exterior not in chosen]
        terms = tuple(sorted(flow+[(('y', v), region.demand) for v in Q]))
        row = FCRRow(region.direction, region.vertices, Q, region.demand, terms, region.demand)
        if self.audit_rows:
            canonical = construct_row(self.instance, region.vertices, Q, region.direction)
            if canonical != row:
                raise AssertionError('AS25.1 row differs from canonical AS24 row')
        return row

    def _evaluate(self, region: CachedRegion, y: Mapping, f: Mapping):
        aggregate = {}
        total = 0.0
        for arc, exterior, eligible in region.frontier:
            value = float(f.get(arc, 0.))
            total += value
            if eligible:
                aggregate[exterior] = aggregate.get(exterior, 0.)+value
        Q = tuple(v for v in sorted(aggregate) if aggregate[v] > region.demand*float(y.get(v, 0.)))
        lhs = total-sum(aggregate[v]-region.demand*float(y.get(v, 0.)) for v in Q)
        return Q, region.demand-lhs

    def separate(self, y: Mapping, f: Mapping, *, max_cuts=32, tolerance=1e-6,
                 time_limit_s=None, exclude_signatures=()):
        if max_cuts < 0 or tolerance < 0 or not math.isfinite(float(tolerance)):
            raise ValueError('invalid FCR policy parameters')
        if time_limit_s is not None and (time_limit_s < 0 or not math.isfinite(float(time_limit_s))):
            raise ValueError('invalid separation time limit')
        if not set(y) <= self.vertex_set or not set(f) <= self.arc_set:
            raise ValueError('invalid LP variables')
        if any(not math.isfinite(float(v)) or v < -1e-6 or v > 1+1e-6 for v in y.values()):
            raise ValueError('invalid LP station values')
        if any(not math.isfinite(float(v)) or v < -1e-6 for v in f.values()):
            raise ValueError('invalid LP flow values')
        start = time.monotonic()
        seen = set(exclude_signatures)
        stats = dict(singletons_eligible=len(self.plan.singletons), singletons_checked=0,
                     larger_generated=self.plan.larger_generated, larger_selected=len(self.plan.larger),
                     larger_discarded=self.plan.larger_discarded, larger_checked=0,
                     examined=0, violated=0, emitted=0, duplicates=0, capped=0, no_violation=0,
                     global_region_separation=False, selection=self.selection,
                     larger_mode=self.larger_mode, larger_deferred=False)
        events, pending = [], []
        timeout = False
        for kind in ('singleton', 'heuristic'):
            if (kind == 'heuristic' and self.larger_mode == 'escalate' and
                    any(e['kind'] == 'singleton' for e, _ in pending)):
                stats['larger_deferred'] = bool(self.plan.larger)
                break
            for region in self.regions:
                if region.kind != kind:
                    continue
                if time_limit_s is not None and time.monotonic()-start >= time_limit_s:
                    timeout = True
                    break
                Q, deficit = self._evaluate(region, y, f)
                stats['examined'] += 1
                stats['singletons_checked' if kind == 'singleton' else 'larger_checked'] += 1
                event = {'kind': kind, 'region': list(region.vertices), 'direction': region.direction,
                         'demand': region.demand, 'q_size': len(Q), 'deficit': deficit}
                events.append(event)
                if deficit <= tolerance:
                    stats['no_violation'] += 1
                    event['decision'] = 'NO_VIOLATION_IN_FIXED_REGION'
                    continue
                stats['violated'] += 1
                if (region.direction, region.vertices, Q) in seen:
                    stats['duplicates'] += 1
                    event['decision'] = 'DUPLICATE'
                    continue
                pending.append((event, (region, Q)))
            if timeout:
                break
        order = list(range(len(pending)))
        if self.selection == 'deficit':
            order.sort(key=lambda i: -pending[i][0]['deficit'])
        cuts = []
        for rank, i in enumerate(order):
            event, (region, Q) = pending[i]
            if len(cuts) >= max_cuts:
                stats['capped'] += 1
                event['decision'] = 'CUT_CAP'
                continue
            row = self._row(region, Q)
            cuts.append(row)
            seen.add(row.signature)
            stats['emitted'] += 1
            event['decision'] = 'ADDED'
            event['selection_rank'] = rank
            event['nnz'] = len(row.terms)
            event['certificate'] = row.algebraic_certificate
        stats['elapsed_s'] = time.monotonic()-start
        stats['singleton_complete'] = stats['singletons_checked'] == stats['singletons_eligible']
        stats['larger_complete_selected'] = stats['larger_checked'] == stats['larger_selected']
        stats['coverage'] = 'ALL_ELIGIBLE_SINGLETONS' if stats['singleton_complete'] else 'PARTIAL_SINGLETONS'
        stats['reason'] = 'TIME_LIMIT' if timeout else None
        if not stats['singleton_complete']:
            status = 'PARTIAL_SINGLETONS'
        elif timeout:
            status = 'PARTIAL_HEURISTIC'
        elif stats['larger_deferred']:
            status = 'CUT_CAP_REACHED' if stats['capped'] else 'COMPLETE_SINGLETONS_LARGER_DEFERRED'
        elif not stats['larger_complete_selected']:
            status = 'PARTIAL_HEURISTIC'
        elif stats['capped']:
            status = 'CUT_CAP_REACHED'
        elif stats['larger_discarded']:
            status = 'COMPLETE_SINGLETONS_SELECTED_HEURISTIC'
        else:
            status = 'COMPLETE_DECLARED_FAMILY'
        return {'status': status, 'cuts': tuple(cuts), 'events': events, 'stats': stats}
