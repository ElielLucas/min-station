"""AS25: indexed FC-R/FC-R-T separation for real LPs.

Same inequalities and AS24 region policy; indexing the reachability arcs avoids
an O(|A|) scan for every candidate.  Q is exact for each L, not globally.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import time
from typing import Mapping

from .fcr_regions import choose_regions
from .fcr_rows import FCRRow, construct_row, _graph


@dataclass(frozen=True)
class IndexedRegion:
    vertices: tuple[str, ...]
    direction: str
    demand: int
    kind: str


class IndexedFCR:
    def __init__(self, instance, *, max_larger=12, include_larger=True):
        vertices, arcs = _graph(instance)
        self.instance = instance
        self.vertex_set = vertices
        self.arc_set = set(arcs)
        self.out = defaultdict(list)
        self.inc = defaultdict(list)
        for u, v in arcs:
            self.out[u].append((u, v))
            self.inc[v].append((u, v))
        self.S, self.T = set(instance.S), set(instance.T)
        self.plan = choose_regions(instance, max_larger=max_larger, include_larger=include_larger)
        self.regions = []
        for kind, candidates in (('singleton', self.plan.singletons), ('heuristic', self.plan.larger)):
            for L in candidates:
                signed = len(self.S.intersection(L))-len(self.T.intersection(L))
                if signed:
                    self.regions.append(IndexedRegion(L,'origin' if signed>0 else 'destination',abs(signed),kind))

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
        start=time.monotonic()
        cuts=[]
        events=[]
        seen=set(exclude_signatures)
        stats=dict(singletons_eligible=len(self.plan.singletons),singletons_checked=0,
                   larger_generated=self.plan.larger_generated,larger_selected=len(self.plan.larger),
                   larger_discarded=self.plan.larger_discarded,larger_checked=0,
                   examined=0,violated=0,emitted=0,duplicates=0,capped=0,no_violation=0,
                   global_region_separation=False)
        timeout=False
        for candidate in self.regions:
            if time_limit_s is not None and time.monotonic()-start>=time_limit_s:
                timeout=True
                break
            R=set(candidate.vertices)
            aggregate=defaultdict(float)
            total=0.0
            for vertex in R:
                arcs = self.out[vertex] if candidate.direction=='origin' else self.inc[vertex]
                for u,v in arcs:
                    exterior=v if candidate.direction=='origin' else u
                    if exterior in R:continue
                    value=float(f.get((u,v),0.))
                    total += value
                    exempt=self.T if candidate.direction=='origin' else self.S
                    if exterior not in exempt:
                        aggregate[exterior]+=value
            eligible=sorted(aggregate)
            Q=tuple(v for v in eligible if aggregate[v]>candidate.demand*float(y.get(v,0.)))
            lhs=total-sum(aggregate[v]-candidate.demand*float(y.get(v,0.)) for v in Q)
            deficit=candidate.demand-lhs
            stats['examined']+=1
            stats['singletons_checked' if candidate.kind=='singleton' else 'larger_checked']+=1
            event={'kind':candidate.kind,'region':list(candidate.vertices),
                   'direction':candidate.direction,'demand':candidate.demand,
                   'q_size':len(Q),'deficit':deficit}
            if deficit>tolerance:
                stats['violated']+=1
                signature=(candidate.direction,candidate.vertices,Q)
                if signature in seen:
                    stats['duplicates']+=1
                    event['decision']='DUPLICATE'
                elif len(cuts)>=max_cuts:
                    stats['capped']+=1
                    event['decision']='CUT_CAP'
                else:
                    # Canonical AS24 constructor independently validates Q and emits
                    # coefficients on H, including mandatory terminal exclusions.
                    row=construct_row(self.instance,candidate.vertices,Q,candidate.direction)
                    cuts.append(row)
                    seen.add(row.signature)
                    stats['emitted']+=1
                    event['decision']='ADDED'
                    event['certificate']=row.algebraic_certificate
            else:
                stats['no_violation']+=1
                event['decision']='NO_VIOLATION_IN_FIXED_REGION'
            events.append(event)
        stats['elapsed_s']=time.monotonic()-start
        stats['singleton_complete']=stats['singletons_checked']==stats['singletons_eligible']
        stats['larger_complete_selected']=stats['larger_checked']==stats['larger_selected']
        stats['coverage']='ALL_ELIGIBLE_SINGLETONS' if stats['singleton_complete'] else 'PARTIAL_SINGLETONS'
        stats['reason']='TIME_LIMIT' if timeout else None
        if not stats['singleton_complete']:status='PARTIAL_SINGLETONS'
        elif timeout or not stats['larger_complete_selected']:status='PARTIAL_HEURISTIC'
        elif stats['capped']:status='CUT_CAP_REACHED'
        elif stats['larger_discarded']:status='COMPLETE_SINGLETONS_SELECTED_HEURISTIC'
        else:status='COMPLETE_DECLARED_FAMILY'
        return {'status':status,'cuts':tuple(cuts),'events':events,'stats':stats}
