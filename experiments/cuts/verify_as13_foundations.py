#!/usr/bin/env python3
"""AS13: auditoria matematico-computacional de H2 e HL; NAO e separador.

Reproduz testemunhas sem Gurobi, usando o compilador COMP e scipy/HiGHS.
Viabilidade: reachability por relés instalados versus validador independente
por estados (vertice, bateria). Cortes novos nao sao adicionados ao produto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in (ROOT / 'experiments/cuts', ROOT / 'experiments/structural', ROOT / 'experiments/alternative-formulations'):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from independent_validator import viavel  # oraculo por bateria; independente de A_r
from hb import construir as construir_hb
from cuts import build_neighborhoods, generate_C1, generate_C2, generate_C4_DM, is_valid_cut
from as02_model_a import Instance, compile_u


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def sha(obj):
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def from_edges(V, S, T, edges, r=1):
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    for v in V:
        adj[v].sort()
    return tuple(S), tuple(T), tuple(V), adj, r


def reach_arcs(V, adj, r):
    """Distances in the ORIGINAL unit graph, independent of installed stations."""
    result = []
    for s in V:
        seen = {s}
        q = deque([(s, 0)])
        while q:
            v, dist = q.popleft()
            if dist == r:
                continue
            for w, weight in adj[v]:
                assert weight == 1
                if w not in seen:
                    seen.add(w)
                    result.append((s, w))
                    q.append((w, dist + 1))
    return tuple(sorted(result))


def reach_matching_oracle(S, T, V, A_r, C):
    """Matching via A_r and intermediate relays C; independent of battery BFS."""
    C = set(C)
    T = set(T)
    neigh = {v: [] for v in V}
    for u, v in A_r:
        neigh[u].append(v)
    reachable = {}
    for s in S:
        dst = set([s]) & T
        seen = {s}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in neigh[u]:
                if w in T:
                    dst.add(w)
                if w in C and w not in seen:
                    seen.add(w)
                    q.append(w)
        reachable[s] = tuple(sorted(dst))
    mt = {}
    def aug(s, seen):
        for t in reachable[s]:
            if t in seen:
                continue
            seen.add(t)
            if t not in mt or aug(mt[t], seen):
                mt[t] = s
                return True
        return False
    return sum(aug(s, set()) for s in S) == len(S)


def k_cuts(S, T, V, adj, r, A_r):
    p, n = build_neighborhoods(A_r)
    K = generate_C1(S, T, p, n) + generate_C2(S, T, adj, r, V) + generate_C4_DM(S, T, p, n)
    return sorted(set(map(frozenset, K)), key=lambda z: tuple(sorted(z)))


def solve_comp_lp(S, T, V, A_r, K, more=()):
    """Convert the EXISTING compiled U to scipy LP, no Gurobi required."""
    from scipy.optimize import linprog
    import numpy as np
    comp = compile_u(Instance(tuple(V), tuple(S), tuple(T), tuple(A_r), 1), K, relax=True)
    n = len(comp.variables)
    objective = np.zeros(n)
    for j, coef in comp.objective.items():
        objective[j] = coef
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    for row in comp.equations:
        lhs = np.zeros(n)
        for j, coef in row.terms:
            lhs[j] = coef
        if row.sense == '==':
            a_eq.append(lhs); b_eq.append(row.rhs)
        elif row.sense == '<=':
            a_ub.append(lhs); b_ub.append(row.rhs)
        else:
            a_ub.append(-lhs); b_ub.append(-row.rhs)
    for coefficients, rhs in more:
        lhs = np.zeros(n)
        for v, coef in coefficients.items():
            lhs[comp.columns[('y', v)]] += coef
        a_ub.append(-lhs); b_ub.append(-rhs)
    result = linprog(objective, A_ub=a_ub or None, b_ub=b_ub or None,
                     A_eq=a_eq or None, b_eq=b_eq or None,
                     bounds=[(var.lb, None if math.isinf(var.ub) else var.ub)
                             for var in comp.variables], method='highs')
    if not result.success:
        raise AssertionError(f'LP failure: {result.message}')
    return float(result.fun), {v: float(result.x[comp.columns[('y', v)]]) for v in V}, comp


def h2_for_support(S, T, V, adj, r, R, *, partial_insufficient=None):
    """Certified H2 for a FIXED R; only called in AS13 on tiny controls."""
    R = frozenset(R)
    F = set(V) - R
    if viavel(S, T, V, adj, r, F):
        return None
    candidates = R if partial_insufficient is None else frozenset(partial_insufficient)
    assert set(candidates) <= R
    B = {v for v in candidates if not viavel(S, T, V, adj, r, F | {v})}
    # On partial classification, every unexamined v gets coefficient 2.
    coefs = {v: 1 if v in B else 2 for v in R}
    return coefs, 2, B


def k4():
    W = tuple('w' + str(i) for i in range(1, 5))
    ij = list(combinations(range(1, 5), 2))
    S = tuple(f's{i}{j}' for i, j in ij)
    T = tuple(f't{i}{j}' for i, j in ij)
    edges = []
    for (i, j), s, t in zip(ij, S, T):
        edges.extend([(s, f'w{i}'), (s, f'w{j}'), (t, f'w{i}'), (t, f'w{j}')])
    return from_edges(W + S + T, S, T, edges), W


def enumerate_feasible(S, T, V, adj, r):
    out = []
    for k in range(len(V) + 1):
        for sub in combinations(V, k):
            if viavel(S, T, V, adj, r, sub):
                out.append(tuple(sub))
    return out


def physical_optimum_by_cardinality(S, T, V, adj, r):
    """Calculate a physical optimum, not a pre-filled expected value.

    Search installations by increasing cardinality. Exhaustive over the
    smaller levels until the first feasible witness, using the physical
    battery-state oracle. The result is a certified cardinality for the
    examined finite instance; the returned count is the number of calls.
    """
    checked = 0
    for k in range(len(V) + 1):
        for installed in combinations(V, k):
            checked += 1
            if viavel(S, T, V, adj, r, installed):
                return {'optimum': k, 'witness': list(installed),
                        'station_subsets_checked': checked}
    return {'optimum': None, 'witness': None,
            'station_subsets_checked': checked}


def verify_k4_exhaustive_physical(instance, W, *, include_mask_viability=False):
    """Audit all 2^|V| station subsets against the independent K4 criterion.

    With ``include_mask_viability``, return the *observed* per-mask physical
    classifications for the subsequent H2 support audit. This internal array
    is never serialized as a reported metric.
    """
    S, T, V, adj, r = instance
    smallest = None
    witness = None
    examined = 0
    classifications = [] if include_mask_viability else None
    for mask in range(1 << len(V)):
        C = tuple(v for j, v in enumerate(V) if mask & (1 << j))
        actual = viavel(S, T, V, adj, r, C)
        expected = sum(w in C for w in W) >= len(W) - 1
        if actual != expected:
            raise AssertionError(
                f'K4 physical mismatch on mask={mask}: physical={actual}, '
                f'structural={expected}, installed={C}'
            )
        examined += 1
        if classifications is not None:
            classifications.append(actual)
        if actual and (smallest is None or len(C) < smallest):
            smallest = len(C)
            witness = list(C)
    if examined != (1 << len(V)):
        raise AssertionError('K4 physical enumeration did not cover all masks')
    if witness is None:
        raise AssertionError('K4 has no physically feasible installation')
    result = {'optimum': smallest, 'witness': witness,
              'station_subsets_checked': examined}
    if classifications is not None:
        result['_mask_viability'] = tuple(classifications)
    return result


def check_all_h2_at_k4_fractional(instance, W, *, mask_viability=None):
    """Audit every K4 support using PHYSICALLY observed feasibility.

    The structural formula is an independently justified reference, not the
    source of the classifications used for H2. ``mask_viability`` must come
    from the battery oracle scan; a fault injected in a single classification
    must be rejected. A literal counter or a skipped loop cannot pass this.
    """
    S, T, V, adj, r = instance
    ix = {v: j for j, v in enumerate(V)}
    wbits = sum(1 << ix[w] for w in W)
    total = 1 << len(V)
    full = total - 1
    if mask_viability is None:
        physical = verify_k4_exhaustive_physical(
            instance, W, include_mask_viability=True)
        mask_viability = physical['_mask_viability']
    if len(mask_viability) != total:
        raise AssertionError('K4 H2 audit: incomplete mask classifications')

    def is_physically_feasible(mask):
        actual = mask_viability[mask]
        expected = (mask & wbits).bit_count() >= len(W) - 1
        if actual != expected:
            raise AssertionError(f'K4 H2 classification mismatch at mask={mask}')
        return actual

    count = 0
    tight = 0
    for rm in range(total):
        fm = full ^ rm
        if is_physically_feasible(fm):
            continue
        B = []
        G = []
        for j in range(len(V)):
            if rm & (1 << j):
                if not is_physically_feasible(fm | (1 << j)):
                    B.append(j)
                else:
                    G.append(j)
        lhs = sum(2/3 if (1 << j) & wbits else 0 for j in B) + \
              2 * sum(2/3 if (1 << j) & wbits else 0 for j in G)
        if lhs < 2 - 1e-9:
            raise AssertionError(f'K4 violated H2 on mask {rm}, lhs={lhs}')
        count += 1
        if abs(lhs - 2) < 1e-8:
            tight += 1
    if count != 45056 or tight != 16384:
        raise AssertionError(f'K4 H2 support coverage changed: {count}, {tight}')
    return count, tight


def small_controls():
    """Five complementary microcontrols, including global infeasibility."""
    return [
        from_edges(('u','s','t'),('u','s'),('s','t'),(('u','s'),('s','t')),1),
        from_edges(('a','b','c'),('a',),('c',),(('a','b'),('b','c')),1),
        from_edges(('a','b','c','d'),('a',),('d',),(('a','b'),('b','c'),('c','d')),1),
        from_edges(('s1','s2','w','t1','t2'),('s1','s2'),('t1','t2'),
                   (('s1','w'),('s2','w'),('w','t1'),('w','t2')),1),
        from_edges(('s','t'),('s',),('t',),(),1),  # globally infeasible even if C=V
    ]


def compare_oracles_for_masks(case, masks, *, case_name):
    """Do not trust a count unless each mask was genuinely compared."""
    S, T, V, adj, r = case
    arcs = reach_arcs(V, adj, r)
    masks = tuple(masks)
    if not masks:
        raise AssertionError(f'{case_name}: no oracle comparisons')
    count = 0
    for mask in masks:
        C = tuple(v for j, v in enumerate(V) if mask & (1 << j))
        physical = viavel(S, T, V, adj, r, C)
        matching = reach_matching_oracle(S, T, V, arcs, C)
        if physical != matching:
            raise AssertionError(f'{case_name}: oracle mismatch at mask={mask}')
        count += 1
    if count != len(masks):
        raise AssertionError(f'{case_name}: oracle scan skipped masks')
    return count


def check_oracle_agreement_hb_k4():
    instance, _ = k4()
    hb = construir_hb(4, 2, 1)
    cases = [
        ('HB', (hb[0], hb[1], hb[2], hb[3], hb[5])),
        ('K4', instance),
    ]
    count = 0
    for name, case in cases:
        V = case[2]
        masks = {0, (1 << len(V)) - 1}
        for j in range(len(V)):
            masks.add(1 << j)
        for i, j in combinations(range(len(V)), 2):
            masks.add((1 << i) | (1 << j))
        for k in range(200):
            masks.add((k * 229 + k * k * 37) & ((1 << len(V)) - 1))
        count += compare_oracles_for_masks(case, sorted(masks), case_name=name)
    if count != 674:
        raise AssertionError(f'HB/K4 oracle audit coverage is {count}, expected 674')
    return {'station_subsets_compared': count}


def check_oracle_agreement_controls(controls):
    count = 0
    for i, case in enumerate(controls):
        count += compare_oracles_for_masks(
            case, range(1 << len(case[2])), case_name=f'control-{i}')
    expected = sum(1 << len(case[2]) for case in controls)
    if count != expected:
        raise AssertionError(f'Control oracle audit: {count}/{expected} subsets')
    return {'battery_vs_reach_cases': count, 'cases': len(controls)}


def hl_beta_from_patterns(patterns, alpha):
    """Exact (integer here) beta for a nonempty set of physical patterns."""
    if not patterns:
        raise ValueError('Phi_R is empty (globally infeasible instance)')
    return min(sum(alpha[v] for v in P) for P in patterns)


def check_exhaustive_small_cuts(controls):
    """Exhaustive H2/H2-partial/HL plus independent physical classification.

    No count is accepted without independently comparing battery and reach
    oracles. HL beta is cross-checked against GLOBAL physical projections,
    which differ in construction from its optimistic-complement patterns.
    """
    exhaustive_h2 = 0
    exhaustive_hl = 0
    global_infeasible = 0
    positive_beta = 0
    for i, (S, T, V, adj, r) in enumerate(controls):
        all_subsets = [set(v for j,v in enumerate(V) if mask & (1 << j))
                       for mask in range(1 << len(V))]
        arcs = reach_arcs(V, adj, r)
        physical = []
        for mask, C in enumerate(all_subsets):
            battery = viavel(S, T, V, adj, r, C)
            matching = reach_matching_oracle(S, T, V, arcs, C)
            if battery != matching:
                raise AssertionError(f'Exhaustive control-{i}: oracle mismatch mask={mask}')
            if battery:
                physical.append(C)
        if not physical:
            global_infeasible += 1
            # An empty support must expose global infeasibility (0 >= 2).
            if h2_for_support(S, T, V, adj, r, ()) != ({}, 2, set()):
                raise AssertionError('Globally infeasible control missing H2 empty support')
            if viavel(S, T, V, adj, r, V) or reach_matching_oracle(S, T, V, arcs, V):
                raise AssertionError('Globally infeasible control has a feasible full installation')
            # Phi_empty is empty; never invent beta for an empty projection.
            if [P for P in (set(),) if viavel(S,T,V,adj,r,set(V) | P)]:
                raise AssertionError('Globally infeasible control has nonempty Phi_empty')
            continue
        for R in all_subsets:
            h2 = h2_for_support(S, T, V, adj, r, R)
            if h2 is None:
                continue
            coefs, rhs, _ = h2
            for C in physical:
                if sum(coefs.get(v, 0) for v in C) < rhs:
                    raise AssertionError(f'H2 excludes physical control-{i}: R={R}, C={C}')
            for v in R:
                partial = h2_for_support(
                    S, T, V, adj, r, R, partial_insufficient={v})
                if partial is None:
                    raise AssertionError('H2 partial missing for nontrivial support')
                pcoefs, prhs, _ = partial
                for C in physical:
                    if sum(pcoefs.get(w, 0) for w in C) < prhs:
                        raise AssertionError(f'H2 partial excludes physical C={C}')
            exhaustive_h2 += 1
            F = set(V) - set(R)
            patterns = []
            for P in all_subsets:
                if P <= R:
                    candidate = F | P
                    battery = viavel(S, T, V, adj, r, candidate)
                    matching = reach_matching_oracle(S, T, V, arcs, candidate)
                    if battery != matching:
                        raise AssertionError(f'HL control-{i}: oracle disagreement R={R}, P={P}')
                    if battery:
                        patterns.append(P)
            if not patterns:
                raise AssertionError('Feasible control with empty Phi_R')
            alpha = {v: (j % 3) + 1 for j, v in enumerate(V) if v in R}
            beta = hl_beta_from_patterns(patterns, alpha)
            projections = {frozenset(C & R) for C in physical}
            if projections != {frozenset(P) for P in patterns}:
                raise AssertionError('HL projection identity fails')
            independent_beta = min(sum(alpha.get(v, 0) for v in C) for C in physical)
            if beta != independent_beta:
                raise AssertionError(f'HL beta differs from global physical projection: '
                                     f'{beta} vs {independent_beta} for R={R}')
            for C in physical:
                if sum(alpha.get(v, 0) for v in C) < beta:
                    raise AssertionError(f'HL excludes physical C={C}')
            if beta > 0:
                positive_beta += 1
            exhaustive_hl += 1
    if (exhaustive_h2 != 32 or exhaustive_hl != 32 or
            positive_beta == 0 or global_infeasible != 1):
        raise AssertionError(f'Incomplete small-cut enumeration: '
                             f'H2={exhaustive_h2}, HL={exhaustive_hl}, '
                             f'beta>0={positive_beta}, global_infeasible={global_infeasible}')
    return {'H2_nontrivial_supports': exhaustive_h2,
            'HL_nontrivial_supports': exhaustive_hl,
            'HL_positive_beta_supports': positive_beta,
            'globally_infeasible_controls': global_infeasible}


def verify():
    details = {}
    # HB constructed by project's own generator: confirm K, LP and IP by physical enumeration.
    S, T, V, adj, edges, r, delta = construir_hb(4, 2, 1)
    A = reach_arcs(V, adj, r)
    K = k_cuts(S,T,V,adj,r,A)
    assert len(V) == 16 and len(S) == 6 and len(K) == 4
    assert all(is_valid_cut(S,T,A,Z) for Z in K)
    hb_base, hb_y, _ = solve_comp_lp(S,T,V,A,K)
    hb_h2, _, _ = solve_comp_lp(S,T,V,A,K,[({v: 1 for v in V}, 2)])
    assert abs(hb_base - 1) < 1e-8 and abs(hb_h2 - 2) < 1e-8
    assert not any(viavel(S,T,V,adj,r,(v,)) for v in V)
    assert viavel(S,T,V,adj,r,('x0_0','x0_1'))
    hb_optimum = physical_optimum_by_cardinality(S, T, V, adj, r)
    assert hb_optimum['optimum'] == 2, hb_optimum
    assert all(sum(v in Z for v in ('x0_0',)) >= 1 for Z in K)
    hb_h2_terms = h2_for_support(S,T,V,adj,r,V)
    assert hb_h2_terms is not None and len(hb_h2_terms[2]) == 16
    details['HB']={'n':len(V),'m':len(S),'r':r,'K_count':len(K), 'lp_COMP_K':hb_base,
        'lp_COMP_K_H2':hb_h2,'ip_phys_opt':hb_optimum['optimum'],
        'ip_phys_witness_computed':hb_optimum['witness'],
        'ip_phys_search_subsets_checked':hb_optimum['station_subsets_checked'],
        'witness_K_feasible_phys_infeasible':['x0_0'],
        'witness_phys_feasible':['x0_0','x0_1'],
        'K':[sorted(x) for x in K],
        'graph_sha256':sha({'S':S,'T':T,'V':V,'edges':sorted(tuple(sorted(e)) for e in edges),'r':r})}
    # 4-relay construction: structural proof = feasible iff >=3 relays, even if every terminal is equipped.
    instance,W = k4()
    S,T,V,adj,r = instance
    A = reach_arcs(V,adj,r)
    K = k_cuts(S,T,V,adj,r,A)
    assert len(K)==6 and all(Z <= set(W) and len(Z)==2 for Z in K)
    k4_base,_,_=solve_comp_lp(S,T,V,A,K)
    h2_triples = [({v:1 for v in set(W)-{w}},2) for w in W]
    k4_h2,_,_=solve_comp_lp(S,T,V,A,K,h2_triples)
    # Independently derive the four triple rows from ACTUALLY MATERIALIZED K.
    # For each triple, the three pair-cover lines sum to 2*y(triple)>=3;
    # rounding the integer left side yields y(triple)>=2 (rank-1 CG).
    cg_triples = []
    for missing in W:
        triple = set(W) - {missing}
        source_pairs = [Z for Z in K if set(Z) <= triple]
        expected_pairs = {frozenset(pair) for pair in combinations(sorted(triple), 2)}
        if set(source_pairs) != expected_pairs or len(source_pairs) != 3:
            raise AssertionError(f'K4 CG derivation unavailable for triple {sorted(triple)}')
        cg_triples.append(({w: 1 for w in triple}, 2))
    k4_cg_lp, _, _ = solve_comp_lp(S, T, V, A, K, cg_triples)
    k4_hl,_,_=solve_comp_lp(S,T,V,A,K,[({w:1 for w in W},3)])
    assert abs(k4_cg_lp-k4_h2) < 1e-9
    assert abs(k4_base-2)<1e-8 and abs(k4_h2-8/3)<1e-8 and abs(k4_hl-3)<1e-8
    # Every K4 station set is physically checked, including terminal choices.
    # The IP optimum is derived from the enumerated viable installations.
    k4_optimum = verify_k4_exhaustive_physical(
        instance, W, include_mask_viability=True)
    if '_mask_viability' not in k4_optimum:
        raise AssertionError('K4 physical mask evidence was not produced')
    mask_viability = k4_optimum.pop('_mask_viability')
    assert k4_optimum['optimum'] == 3, k4_optimum
    support_count, tight_count = check_all_h2_at_k4_fractional(
        instance, W, mask_viability=mask_viability)
    details['K4']={'n':len(V),'m':len(S),'r':r,'K_count':len(K),
        'lp_COMP_K':k4_base,'lp_COMP_K_H2':k4_h2,'lp_COMP_K_H2_HL':k4_hl,
        'lp_COMP_K_plus_CG_triples':k4_cg_lp,
        'CG_triples_exactly_H2_triples_on_K4':cg_triples==h2_triples,
        'ip_phys_opt':k4_optimum['optimum'],
        'ip_phys_witness_computed':k4_optimum['witness'],
        'battery_station_subsets_checked':k4_optimum['station_subsets_checked'],
        'H2_supports_nontrivial_checked':support_count,'H2_supports_tight_at_fractional_point':tight_count,
        'graph_sha256':sha({'S':S,'T':T,'V':V,'edges':sorted(tuple(sorted((u,v))) for u in V for v,_ in adj[u] if u<v),'r':r})}
    # Every loop is a dedicated, independently testable gate: skipping a loop
    # must fail the suite rather than return an apparently valid literal count.
    controls = small_controls()
    details['oracle_agreement_HB_K4'] = check_oracle_agreement_hb_k4()
    details['controls'] = check_oracle_agreement_controls(controls)
    S0,T0,V0,A0,r0 = controls[0]
    assert viavel(S0,T0,V0,A0,r0,())  # S intersection T / direct assignment
    S1,T1,V1,A1,r1 = controls[1]
    assert not viavel(S1,T1,V1,A1,r1,()) and viavel(S1,T1,V1,A1,r1,('b',))
    S2,T2,V2,A2,r2 = controls[2]
    assert not viavel(S2,T2,V2,A2,r2,('b',))
    assert not viavel(S2,T2,V2,A2,r2,('c',)) and viavel(S2,T2,V2,A2,r2,('b','c'))
    S3,T3,V3,A3,r3 = controls[3]
    assert viavel(S3,T3,V3,A3,r3,('w',))
    details['exhaustive_small_cuts'] = check_exhaustive_small_cuts(controls)
    assert details['oracle_agreement_HB_K4']['station_subsets_compared'] == 674
    assert details['controls']['battery_vs_reach_cases'] == 68
    assert details['exhaustive_small_cuts']['H2_nontrivial_supports'] == 32
    assert details['exhaustive_small_cuts']['HL_nontrivial_supports'] == 32
    assert details['exhaustive_small_cuts']['globally_infeasible_controls'] == 1
    assert details['exhaustive_small_cuts']['HL_positive_beta_supports'] > 0
    return details


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output', help='write JSON summary to this path (no overwrite)')
    args=p.parse_args()
    details=verify()
    import scipy
    import platform
    record={'schema':'AS13-FOUNDATIONS-MATH-VALIDATION-v3',
        'source_commit':'ed1a04740e59f2c8ae4f13e9a62b69624032fa62',
        'source_snapshot':'min-station(20261014-050142).zip (AS13 R2 correction over supplied project snapshot)',
        'source_blob_sha': {
            'experiments/cuts/cuts.py':'d305457f3b60a7f263106e624e3a0b821d99f935',
            'experiments/cuts/independent_validator.py':'73c99798b2afcfbdfa57b53d1d368446f573c0bc',
            'experiments/structural/hb.py':'855d93c6b1b306cc27c51cbd90702a58a8132f95',
            'experiments/alternative-formulations/as02_model_a.py':'b1d9b5a6387e89966665c40026156068bc6c3dbb'},
        'python_version':platform.python_version(), 'scipy_version':scipy.__version__,
        'solver':'SciPy linprog HiGHS for LP; brute battery BFS for physical feasibility',
        'status':'LOCAL_CHECKS_PASS_INDEPENDENT_FAIL_RECHECK_REQUIRED',
        'scientific_gate':'FAIL_UNTIL_INDEPENDENT_RECHECK',
        'as14':'BLOCKED',
        'results':details}
    if args.output:
        path=Path(args.output)
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as f:
            json.dump(record,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write('\n')
    print(canonical_json(record))

if __name__=='__main__':
    main()
