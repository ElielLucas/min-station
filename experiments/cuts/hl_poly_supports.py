"""AS22: stratified hypotheses for small HL supports, never validity proofs.

K interactions receive a reserved slot whenever a distinct interaction
candidate exists; otherwise the slot is explicitly unfilled. Any projection
of a large K is heuristic and must be certified from scratch.
"""
from __future__ import annotations

import math
from itertools import combinations
from h2_oracle_schema import order_vertices, vertex_key


def select_poly_supports(vertices, y_star, *, k_supports,
                         max_support_size=8, max_supports=4,
                         max_k_seeds=48, max_pairs=64,
                         min_interaction_slots=2):
    for name, x in (('max_support_size',max_support_size),
                    ('max_supports',max_supports), ('max_k_seeds',max_k_seeds),
                    ('max_pairs',max_pairs), ('min_interaction_slots',min_interaction_slots)):
        if type(x) is not int or x < (1 if name=='max_support_size' else 0):
            raise ValueError(f'invalid {name}')
    V = order_vertices(vertices)
    if len(V) != len(set(V)) or set(y_star) != set(V) or any(
       type(y_star[v]) not in (int,float) or not math.isfinite(y_star[v])
       or not 0 <= y_star[v] <= 1 for v in V):
        raise ValueError('invalid LP point')
    Ks = set()
    for raw in k_supports:
        R = order_vertices(raw)
        if not R or len(R)!=len(set(raw)) or not set(R)<=set(V):
            raise ValueError('invalid K support')
        Ks.add(R)
    seeds=sorted(Ks,key=lambda k:(len(k),sum(y_star[v] for v in k),
                      tuple(vertex_key(v) for v in k)))[:max_k_seeds]
    singles = {}
    interactions = {}
    for k in seeds:
        if len(k)<=max_support_size:
            singles[k] = 'WHOLE_K'
        else:
            ranked=sorted(k,key=lambda v:(-y_star[v],vertex_key(v)))
            singles[order_vertices(ranked[:max_support_size])] = 'LARGE_K_PROJECTION'
    candidates=[]
    for a,b in combinations(seeds,2):
        both=order_vertices(set(a)|set(b))
        if len(both)<=max_support_size:
            kind='K_UNION'
            projected=both
        elif set(a)&set(b):
            overlap=set(a)&set(b)
            ranked=sorted(both,key=lambda v:(-(v in overlap),-y_star[v],vertex_key(v)))
            projected=order_vertices(ranked[:max_support_size])
            kind='K_PAIR_PROJECTION'
        else:
            continue
        candidates.append((projected,kind))
    # Rank intersection-rich interactions first so pair quota cannot be
    # consumed by arbitrary disjoint candidates.
    candidates.sort(key=lambda item:(-sum(y_star[v] for v in item[0]),
        len(item[0]),tuple(vertex_key(v) for v in item[0]),item[1]))
    for R,kind in candidates[:max_pairs]:
        if R not in singles and R not in interactions:
            interactions[R]=kind
    # K4 remains discoverable through the union of distinct K constraints.
    def score(item):
        R,kind=item
        coverage=sum(set(k)<=set(R) for k in seeds)
        return (-coverage, -sum(0<y_star[v]<1 for v in R),
                sum(y_star[v] for v in R), len(R),
                tuple(vertex_key(v) for v in R), kind)
    ranked_i=sorted(interactions.items(),key=score)
    ranked_s=sorted(singles.items(),key=score)
    quota=min(min_interaction_slots,max_supports,len(ranked_i))
    selected=ranked_i[:quota]
    used={r for r,_ in selected}
    for row in sorted([*ranked_i[quota:],*ranked_s],key=score):
        if len(selected)>=max_supports:break
        if row[0] not in used:
            selected.append(row)
            used.add(row[0])
    return tuple(R for R,_ in selected), {
        'policy':'AS22_STRATIFIED_K_INTERACTION_V1',
        'selection_is_not_certification':True,
        'k_count':len(Ks), 'k_seeds_considered':len(seeds),
        'pair_candidates_considered':len(candidates),
        'pair_candidates_retained':min(max_pairs,len(candidates)),
        'interaction_candidates':len(ranked_i),
        'interaction_slots_requested':min(min_interaction_slots,max_supports),
        'interaction_slots_filled':quota,
        'candidate_count':len(singles)+len(interactions),
        'selected_count':len(selected),
        'selected_kinds':[kind for _,kind in selected],
        'selected_support_sizes':[len(R) for R,_ in selected],
        'no_eligible_support':not selected,
    }
