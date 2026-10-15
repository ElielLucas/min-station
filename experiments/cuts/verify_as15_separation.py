#!/usr/bin/env python3
"""AS15 local physical audit (not an independent-person review)."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for folder in (ROOT / 'experiments/cuts', ROOT / 'experiments/structural',
               ROOT / 'experiments/alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from h2_oracle import PhysicalInstance
from h2_separator import SeparatorOptions, separate_h2
from h2_oracle_schema import order_vertices
from independent_validator import viavel
from verify_as13_foundations import k_cuts, reach_arcs, solve_comp_lp
from hb import construir


def subsets(V):
    for k in range(len(V) + 1):
        yield from combinations(V, k)


def case(V, S, T, edges, r=1):
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def audit(seed=1515):
    rng = random.Random(seed)
    controls = (
        case('abc','a','c',[('a','b'),('b','c')]),
        case('abcd','a','d',[('a','b'),('b','c'),('c','d')]),
        case(('s1','s2','w','t1','t2'), ('s1','s2'), ('t1','t2'),
             [('s1','w'),('s2','w'),('w','t1'),('w','t2')]),
    )
    options = SeparatorOptions(total_budget_s=None, per_support_budget_s=None,
                                max_supports=128, max_cuts=128)
    emitted = viable_masks_checked = expected_count = heuristic_hits = oracle_calls = 0
    for i in controls:
        for _ in range(3):
            y = {v: rng.uniform(.05,.45) for v in i.V}
            exact = {}
            feasible = [set(C) for C in subsets(i.V)
                        if viavel(i.S,i.T,i.V,i.adj,i.r,C)]
            viable_masks_checked += len(feasible)
            for R in subsets(i.V):
                F = set(i.V) - set(R)
                if viavel(i.S,i.T,i.V,i.adj,i.r,F):
                    continue
                B = {v for v in R if not viavel(i.S,i.T,i.V,i.adj,i.r,F | {v})}
                if not B:
                    continue  # equivalent cover, not new H2
                coefficients = {v: 1 if v in B else 2 for v in R}
                if 2 - sum(coefficients[v]*y[v] for v in R) > 1e-7:
                    exact[order_vertices(R)] = coefficients
            exhaustive = separate_h2(i, y, proposed_supports=list(subsets(i.V)), options=options)
            heuristic = separate_h2(i, y, options=options)
            assert {c.support for c in exhaustive.cuts} == set(exact), 'exhaustive recall mismatch'
            for report in (exhaustive, heuristic):
                oracle_calls += report.oracle_calls
                for cut in report.cuts:
                    emitted += 1
                    assert dict(cut.coefficients) == exact[cut.support], 'physical Bhat mismatch'
                    assert cut.violation > options.min_violation, 'not violated'
                    for C in feasible:
                        assert sum(c for v, c in cut.coefficients if v in C) >= 2, 'invalid cut'
            expected_count += len(exact)
            heuristic_hits += len({c.support for c in heuristic.cuts} & set(exact))
    assert expected_count > 0 and emitted > 0
    assert heuristic_hits <= expected_count

    S,T,V,adj,_,r,_ = construir(4,2,1)
    hb = PhysicalInstance(tuple(V),tuple(S),tuple(T),adj,r)
    arcs = reach_arcs(V,adj,r)
    K = k_cuts(S,T,V,adj,r,arcs)
    comp_k_lp, y, _ = solve_comp_lp(S,T,V,arcs,K)
    report = separate_h2(hb,y,k_supports=K,options=options)
    full, = [cut for cut in report.cuts if cut.support == order_vertices(V)]
    assert all(c == 1 for _,c in full.coefficients) and full.rhs == 2
    strengthened, _, _ = solve_comp_lp(S,T,V,arcs,K,[(dict(full.coefficients),2)])
    assert abs(comp_k_lp - 1) < 1e-8 and abs(strengthened - 2) < 1e-8
    return {
        'schema_version': 'AS15-LOCAL-AUDIT-v1', 'stage': 'AS15',
        'status': 'LOCAL_PASS_EXTERNAL_REVIEW_PENDING', 'seed': seed,
        'controls': len(controls), 'fractional_vectors_per_control': 3,
        'physically_feasible_installations_checked': viable_masks_checked,
        'exhaustive_violated_nondegenerate_H2': expected_count,
        'heuristic_violated_H2_hits': heuristic_hits,
        'heuristic_recall': heuristic_hits / expected_count,
        'precision': 1.0, 'emitted_rows_physically_checked': emitted,
        'oracle_calls_audit': oracle_calls,
        'HB': {'instance_sha256': hb.fingerprint, 'vertices': len(V),
               'base_COMP_K_LP': comp_k_lp, 'after_H2_LP': strengthened,
               'nonredundant_H2_cut_hash': full.cut_hash,
               'certificate_sha256': full.certificate_sha256,
               'h2_rhs': full.rhs, 'h2_violation': full.violation},
        'source_sha256': {name: hashlib.sha256((ROOT/'experiments/cuts'/name).read_bytes()).hexdigest()
                          for name in ('h2_cut.py','h2_supports.py','h2_separator.py','test_h2_separator.py')},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='save append-only audit JSON')
    args = parser.parse_args()
    result = audit()
    data = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(data)
    print(data, end='')


if __name__ == '__main__':
    main()
