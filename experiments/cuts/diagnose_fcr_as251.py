#!/usr/bin/env python3
"""AS25.1: post-hoc FC-R diagnosis on the six AS25 development cases (LP only).

Evidence class DIAGNOSTIC_POST_HOC: explains AS25 numbers; never enters a gate.

Examples (repository root):
  poetry run python experiments/cuts/diagnose_fcr_as251.py index --output results/benchmark/as251-diagnostico-001/index.json
  poetry run python experiments/cuts/diagnose_fcr_as251.py trace --case mapf-room-32-32-4-m10-f8 \
      --policy as25 --output results/benchmark/as251-diagnostico-001/trace-mapf-as25.json
  # closure of the declared family: no cut caps, rounds until no violated row
  poetry run python experiments/cuts/diagnose_fcr_as251.py trace --case puc-cc9-2p-seed-r1 \
      --policy singleton --per-round 1000000 --total 1000000 --rounds 400 --output ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import tracemalloc

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from run_fcr_lp_as25 import (ROOT, Instance, compile_u, prepare_K, canonical_k, load_instance,
                             load_plan, validate_sources, _solver, _optimize, _point, _add_fcr,
                             get_commit, sha256_file, write_json_new)
from experiments.cuts.fcr_lp_policy import IndexedFCR
from experiments.cuts.fcr_lp_policy_as251 import FastIndexedFCR

EVIDENCE = 'DIAGNOSTIC_POST_HOC'
# policy -> (index factory, include_larger)
POLICIES = {
    'as25': lambda ins: IndexedFCR(ins, max_larger=12, include_larger=True),
    'singleton': lambda ins: FastIndexedFCR(ins, max_larger=12, include_larger=False),
    'infra': lambda ins: FastIndexedFCR(ins, max_larger=12, include_larger=True),
    'as251': lambda ins: FastIndexedFCR(ins, max_larger=12, larger_mode='escalate'),
    'deficit': lambda ins: FastIndexedFCR(ins, max_larger=12, selection='deficit'),
    'deficit_escalate': lambda ins: FastIndexedFCR(ins, max_larger=12, selection='deficit',
                                                   larger_mode='escalate'),
}


def _timed(callback):
    tracemalloc.start()
    start = time.monotonic()
    value = callback()
    elapsed = time.monotonic()-start
    peak = tracemalloc.get_traced_memory()[1]/2**20
    tracemalloc.stop()
    return value, elapsed, peak


def index_report(ins, *, compare_as25=True):
    """Index build cost and plan equality, AS25 vs AS25.1, for one instance."""
    rows = []
    for include in (False, True):
        fast, fast_s, fast_mib = _timed(lambda: FastIndexedFCR(ins, max_larger=12, include_larger=include))
        row = {'include_larger': include, 'regions': len(fast.regions),
               'larger_generated': fast.plan.larger_generated,
               'as251_index_s': fast_s, 'as251_peak_traced_mib': fast_mib}
        if compare_as25:
            slow, slow_s, slow_mib = _timed(lambda: IndexedFCR(ins, max_larger=12, include_larger=include))
            row.update(as25_index_s=slow_s, as25_peak_traced_mib=slow_mib,
                       plan_equal=slow.plan == fast.plan,
                       regions_equal=[(r.vertices, r.direction, r.demand, r.kind) for r in slow.regions] ==
                                     [(r.vertices, r.direction, r.demand, r.kind) for r in fast.regions])
        rows.append(row)
    return {'n_vertices': len(ins.V), 'n_arcs_H': len(ins.A_r), 'm': len(ins.S), 'r': ins.r,
            'overlap_S_T': len(set(ins.S) & set(ins.T)), 'index': rows}


def _digest(items):
    return hashlib.sha256(repr(items).encode()).hexdigest()


def trace(ins, compiled, solver_parameters, index, *, per_round, total, rounds, tolerance=1e-6):
    """Cutting loop on COMP(+K) LP with per-round cost and objective."""
    deadline = time.monotonic()+86400
    model, ycols, gp = _solver(compiled, solver_parameters, deadline)
    current = _optimize(model, gp, deadline, ycols)
    if current['status'] != 'OPTIMAL':
        return {'status': current['status'], 'rounds': []}
    base = current['lp_objective']
    columns, seen, added, out = model.getVars(), set(), 0, []
    converged = False
    for number in range(1, rounds+1):
        if total-added <= 0:
            break
        start = time.monotonic()
        y, f = _point(model, compiled, current['y_star'])
        point_s = time.monotonic()-start
        report = index.separate(y, f, tolerance=tolerance, max_cuts=min(per_round, total-added),
                                exclude_signatures=seen)
        cuts = report['cuts']
        if not cuts:
            converged = report['status'] in ('COMPLETE_DECLARED_FAMILY', 'COMPLETE_SINGLETONS_SELECTED_HEURISTIC')
            out.append({'round': number, 'status': report['status'], 'stats': report['stats'],
                        'emitted': 0, 'objective': current['lp_objective']})
            break
        start = time.monotonic()
        for cut in cuts:
            _add_fcr(model, compiled, columns, gp, cut)
            seen.add(cut.signature)
        model.update()
        insert_s = time.monotonic()-start
        added += len(cuts)
        current = _optimize(model, gp, deadline, ycols)
        events = [e for e in report['events'] if e['decision'] in ('ADDED', 'CUT_CAP')]
        out.append({'round': number, 'status': report['status'], 'stats': report['stats'],
                    'emitted': len(cuts),
                    'emitted_singleton': sum(1 for c in cuts if len(c.region) == 1),
                    'emitted_larger': sum(1 for c in cuts if len(c.region) > 1),
                    'nnz': sum(len(c.terms) for c in cuts),
                    'deficit_added_max': max((e['deficit'] for e in events if e['decision'] == 'ADDED'), default=None),
                    'deficit_added_min': min((e['deficit'] for e in events if e['decision'] == 'ADDED'), default=None),
                    'deficit_capped_max': max((e['deficit'] for e in events if e['decision'] == 'CUT_CAP'), default=None),
                    'signature_digest': _digest([c.signature for c in cuts]),
                    'terms_digest': _digest([c.terms for c in cuts]),
                    'point_extraction_s': point_s, 'separation_s': report['stats']['elapsed_s'],
                    'insertion_s': insert_s, 'reoptimization_s': current['solver_wall_s'],
                    'status_lp': current['status'], 'objective': current['lp_objective']})
        if current['status'] != 'OPTIMAL':
            break
    final = current['lp_objective']
    return {'status': current['status'], 'base_objective': base, 'final_objective': final,
            'relative_gain': (final-base)/abs(base) if final is not None and abs(base) > 1e-10 else None,
            'rows_added': added, 'converged_no_violation': converged, 'rounds': out}


def _case_instance(name):
    plan, _, base = load_plan()
    rows = validate_sources(base, ROOT)
    case = [c for c in plan['cases'] if c['name'] == name]
    if not case:
        raise ValueError('INVALID_INPUT: not an AS25 development case')
    loaded = load_instance(rows[name], root=ROOT)
    if loaded.instance_sha256 != case[0]['source_sha256']:
        raise ValueError('INVALID_INPUT: source hash')
    ins = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), tuple(loaded.A_r), int(loaded.r))
    return plan, case[0], loaded, ins


def _header(mode):
    return {'schema_version': 'AS251-DIAG-v1', 'stage': 'AS25.1', 'mode': mode,
            'evidence_class': EVIDENCE, 'enters_gate': False,
            'source_commit': get_commit(),
            'code_sha256': {rel: sha256_file(ROOT/rel) for rel in (
                'experiments/cuts/fcr_lp_policy.py', 'experiments/cuts/fcr_lp_policy_as251.py',
                'experiments/cuts/diagnose_fcr_as251.py')}}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('mode', choices=('index', 'trace'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append', help='AS25 development case; repeatable for index')
    parser.add_argument('--skip-as25', action='store_true', help='index: do not time the AS25 index')
    parser.add_argument('--policy', choices=sorted(POLICIES), default='as25')
    parser.add_argument('--per-round', type=int, default=32)
    parser.add_argument('--total', type=int, default=128)
    parser.add_argument('--rounds', type=int, default=6)
    parser.add_argument('--no-k', action='store_true', help='trace on COMP instead of COMP+K')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('append-only output exists: '+str(args.output))
    report = _header(args.mode)
    if args.mode == 'index':
        names = args.case or [c['name'] for c in load_plan()[0]['cases']]
        report['cases'] = {}
        for name in names:
            _, case, _, ins = _case_instance(name)
            report['cases'][name] = {'instance_sha256': case['source_sha256'],
                                     **index_report(ins, compare_as25=not args.skip_as25)}
            print(name, json.dumps(report['cases'][name]['index']), flush=True)
    else:
        if not args.case or len(args.case) != 1:
            raise ValueError('trace requires exactly one --case')
        plan, case, loaded, ins = _case_instance(args.case[0])
        K = () if args.no_k else canonical_k(ins, prepare_K(ins, loaded.adj, ins.r))
        compiled = compile_u(ins, K, relax=True)
        index, index_s, _ = _timed(lambda: POLICIES[args.policy](ins))
        report.update(case=case['name'], instance_sha256=case['source_sha256'],
                      formulation='COMP' if args.no_k else 'COMP+K', policy=args.policy,
                      limits={'per_round': args.per_round, 'total': args.total, 'rounds': args.rounds},
                      solver_parameters=plan['solver_parameters'], index_s=index_s,
                      **trace(ins, compiled, plan['solver_parameters'], index,
                              per_round=args.per_round, total=args.total, rounds=args.rounds))
        print(json.dumps({k: report[k] for k in ('case', 'policy', 'status', 'base_objective',
                                                 'final_objective', 'relative_gain', 'rows_added',
                                                 'converged_no_violation')}))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json_new(args.output, report)


if __name__ == '__main__':
    main()
