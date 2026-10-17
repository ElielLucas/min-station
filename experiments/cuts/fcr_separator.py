"""AS24: separate fixed-region FC-R/FC-R-T, then a declared list of regions.

The Q decision is exact for each selected region.  Coverage over regions is
complete ONLY for strict-excess singletons if the scan was not interrupted.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
import time
from typing import Mapping

from .fcr_rows import construct_row, eligible_frontier, region_excess, evaluate, FCRRow, _graph
from .fcr_regions import choose_regions


@dataclass(frozen=True)
class FixedResult:
    region: tuple[str, ...]
    direction: str
    q_opt: tuple[str, ...]
    lhs: int | float | Fraction
    rhs: int
    deficit: int | float | Fraction
    row: FCRRow


def _number(value):
    if not isinstance(value, (int, float, Fraction)) or not math.isfinite(float(value)):
        raise ValueError('nonfinite or nonnumeric LP point')
    return value


def _validate_point(instance, y, f, *, epsilon=1e-8):
    vertices, arcs = _graph(instance)
    if not isinstance(epsilon, (int, float)) or not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError('invalid domain tolerance')
    arc_set = set(arcs)
    if any(v not in vertices for v in y) or any(a not in arc_set for a in f):
        raise ValueError('point uses nonexistent vertex or reachability arc')
    for value in y.values():
        val = _number(value)
        if val < -epsilon or val > 1 + epsilon:
            raise ValueError('y outside [0,1]')
    for value in f.values():
        if _number(value) < -epsilon:
            raise ValueError('negative flow')


def separate_fixed(instance, region, y: Mapping, f: Mapping,
                   direction='origin') -> FixedResult:
    """Exact optimal Q with stable exclusion of ties, no cardinality cap."""
    _validate_point(instance, y, f)
    R = set(region)
    demand = region_excess(instance, region, direction)
    if demand <= 0:
        raise ValueError('balanced or wrong-sign region')
    allowed = eligible_frontier(instance, region, direction)
    if direction == 'origin':
        flux = {v: sum((f.get((u,w), 0) for u,w in instance.A_r if u in R and w == v), 0)
                for v in allowed}
    elif direction == 'destination':
        flux = {v: sum((f.get((u,w), 0) for u,w in instance.A_r if w in R and u == v), 0)
                for v in allowed}
    else:
        raise ValueError('unknown direction')
    Q = tuple(v for v in allowed if flux[v] > demand*y.get(v, 0))
    row = construct_row(instance, region, Q, direction)
    lhs = evaluate(row, y, f)
    return FixedResult(row.region, direction, Q, lhs, demand, demand-lhs, row)


@dataclass
class ScanResult:
    cuts: tuple[FCRRow, ...]
    events: list[dict]
    stats: dict
    status: str


def scan(instance, y: Mapping, f: Mapping, *, max_larger=12,
         include_larger=True, max_cuts=64, tolerance=1e-7,
         time_limit_s: float | None=None) -> ScanResult:
    """One-pass separation, no LP reoptimization (which belongs to AS25).

    Cut cap limits emitted cuts, not processed singletons.  Time limits may
    interrupt the singleton scan; in that case status is PARTIAL_SINGLETONS.
    """
    if not isinstance(max_cuts, int) or max_cuts < 0:
        raise ValueError('invalid cut cap')
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('invalid violation tolerance')
    if time_limit_s is not None and (not math.isfinite(time_limit_s) or time_limit_s < 0):
        raise ValueError('invalid time budget')
    _validate_point(instance, y, f)
    plan = choose_regions(instance, max_larger=max_larger, include_larger=include_larger)
    start = time.monotonic()
    events = []
    cuts = []
    seen = set()
    counts = dict(singletons_eligible=len(plan.singletons), singletons_checked=0,
                  larger_generated=plan.larger_generated, larger_selected=len(plan.larger),
                  larger_discarded=plan.larger_discarded, larger_checked=0,
                  examined=0, violated=0, emitted=0, duplicates=0,
                  capped=0, no_violation=0)
    reason = None
    for kind, regions in [('singleton',plan.singletons),('heuristic',plan.larger)]:
        for L in regions:
            if time_limit_s is not None and time.monotonic()-start >= time_limit_s:
                reason = 'TIME_LIMIT'
                break
            if kind == 'singleton':counts['singletons_checked'] += 1
            else:counts['larger_checked'] += 1
            direction = 'origin' if region_excess(instance,L,'origin') > 0 else 'destination'
            result = separate_fixed(instance, L, y, f, direction)
            counts['examined'] += 1
            event = {'kind':kind,'region':list(result.region),'direction':direction,
                     'q':list(result.q_opt),'demand':result.rhs,
                     'lhs':str(result.lhs),'deficit':str(result.deficit),
                     'signature':repr(result.row.signature)}
            if result.deficit > tolerance:
                counts['violated'] += 1
                if result.row.signature in seen:
                    counts['duplicates'] += 1
                    event['decision'] = 'DUPLICATE'
                elif len(cuts) < max_cuts:
                    cuts.append(result.row)
                    seen.add(result.row.signature)
                    counts['emitted'] += 1
                    event['decision'] = 'ADDED'
                    event['certificate'] = result.row.algebraic_certificate
                else:
                    counts['capped'] += 1
                    event['decision'] = 'CUT_CAP'
            else:
                counts['no_violation'] += 1
                event['decision'] = 'NO_VIOLATION_IN_FIXED_REGION'
            events.append(event)
        if reason:
            break
    counts['elapsed_s'] = time.monotonic()-start
    counts['singleton_complete'] = counts['singletons_checked'] == counts['singletons_eligible']
    counts['larger_complete_selected'] = counts['larger_checked'] == counts['larger_selected']
    if not counts['singleton_complete']:
        status = 'PARTIAL_SINGLETONS'
    elif reason or not counts['larger_complete_selected']:
        status = 'PARTIAL_HEURISTIC'
    elif counts['capped']:
        status = 'CUT_CAP_REACHED'
    else:
        status = 'COMPLETE_DECLARED_FAMILY' if not plan.larger_discarded else 'COMPLETE_SINGLETONS_SELECTED_HEURISTIC'
    counts['coverage'] = ('ALL_ELIGIBLE_SINGLETONS' if counts['singleton_complete'] else 'PARTIAL_SINGLETONS')
    counts['global_region_separation'] = False
    counts['reason'] = reason
    return ScanResult(tuple(cuts),events,counts,status)
