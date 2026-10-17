#!/usr/bin/env python3
"""AS25.1: preregistered LP confirmation of the optimized FC-R separator (NO MIP).

Examples:
  poetry run python experiments/cuts/run_fcr_lp_as251.py --output-dir /tmp/as251-dry --dry-run
  poetry run python experiments/cuts/run_fcr_lp_as251.py --output-dir results/benchmark/as251-fcr-lp-001

Four arms per AS25 development case, each in its own process with a 90-second
total wall budget: U_K, U_K_FCR_AS25 (original AS25 separator), U_K_FCR_INFRA
(cheaper index, same rows) and U_K_FCR_AS251 (cheaper index + singleton-first).
Outputs are append-only and must use a new directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from run_h2_lp import (ROOT, Instance, compile_u, prepare_K, canonical_k, k_digest, load_instance,
                       validate_sources, sha256_file, _solver, _optimize, _phase, _ensure_budget,
                       _elapsed, _remaining, get_commit, write_json_new)
from run_fcr_lp_as25 import (PLAN_FILE as AS25_PLAN_FILE, load_plan as load_as25_plan,
                             _point, _add_fcr, _usage_mb, _source_dirty)
from experiments.cuts.fcr_lp_policy import IndexedFCR
from experiments.cuts.fcr_lp_policy_as251 import FastIndexedFCR

SCHEMA = 'AS251-FCR-LP-v1'
PLAN_FILE = ROOT/'docs/technical/plans/execucao/as251-preregistro-fcr-lp.json'
ARMS = ('U_K', 'U_K_FCR_AS25', 'U_K_FCR_INFRA', 'U_K_FCR_AS251')
ARM_POLICIES = {
    'U_K_FCR_AS25': {'index': 'IndexedFCR', 'selection': 'lexicographic', 'larger_mode': 'always', 'audit_rows': True},
    'U_K_FCR_INFRA': {'index': 'FastIndexedFCR', 'selection': 'lexicographic', 'larger_mode': 'always', 'audit_rows': False},
    'U_K_FCR_AS251': {'index': 'FastIndexedFCR', 'selection': 'lexicographic', 'larger_mode': 'escalate', 'audit_rows': False},
}
CLASSIFICATION_CONSTANTS = {
    'candidate_arm': 'U_K_FCR_AS251', 'control_arm': 'U_K', 'minimum_relative_gain': 0.01,
    'minimum_independent_raw_graphs': 2, 'maximum_cost_multiple': 2.0,
    'efficiency_minimum_median_overhead_reduction': 0.5, 'infra_objective_tolerance': 1e-6,
}
CHECKED_SOURCES = (
    'experiments/cuts/fcr_rows.py', 'experiments/cuts/fcr_regions.py',
    'experiments/cuts/fcr_lp_policy.py', 'experiments/cuts/fcr_lp_policy_as251.py',
    'experiments/cuts/run_fcr_lp_as25.py', 'experiments/cuts/run_fcr_lp_as251.py',
    'experiments/cuts/analyze_fcr_lp_as251.py',
)


def load_plan(path=PLAN_FILE, *, as25_path=AS25_PLAN_FILE):
    """Frozen AS25.1 plan; cases, solver, budget and FC-R numbers must equal AS25."""
    planpath = Path(path)
    plan = json.loads(planpath.read_text(encoding='utf-8'))
    as25, as25_sha, base = load_as25_plan(as25_path)
    if plan.get('schema_version') != 'AS251-FCR-PLAN-v1' or plan.get('stage') != 'AS25.1':
        raise ValueError('INVALID_INPUT: AS25.1 plan schema')
    if plan.get('as25_plan_sha256') != as25_sha or plan.get('as16_plan_sha256') != as25['as16_plan_sha256']:
        raise ValueError('INVALID_INPUT: AS25 plan hash differs')
    for key in ('cases', 'solver_parameters', 'budget', 'fcr'):
        if plan.get(key) != as25[key]:
            raise ValueError(f'INVALID_INPUT: {key} differs from AS25')
    if plan.get('as25_reference_gate') != as25['gate']:
        raise ValueError('INVALID_INPUT: AS25 reference gate altered')
    if tuple(plan.get('arms', ())) != ARMS or plan.get('arm_policies') != ARM_POLICIES:
        raise ValueError('INVALID_INPUT: arms or arm policies altered')
    classification = plan.get('classification', {})
    if {k: classification.get(k) for k in CLASSIFICATION_CONSTANTS} != CLASSIFICATION_CONSTANTS:
        raise ValueError('INVALID_INPUT: AS25.1 classification altered')
    if not plan.get('preregistered_before_campaign') or plan.get('mip_automatically_authorized') is not False:
        raise ValueError('INVALID_INPUT: preregistration/MIP boundary changed')
    if plan.get('constraints') != ['only development', 'no MIP', 'no evaluation', 'no change COMP or K',
                                   'no change AS24/AS25 code', 'append only']:
        raise ValueError('INVALID_INPUT: research boundaries changed')
    return plan, sha256_file(planpath), base


def _digest(items):
    return hashlib.sha256(repr(items).encode()).hexdigest()


def make_index(arm, ins, fcr):
    policy = ARM_POLICIES[arm]
    if policy['index'] == 'IndexedFCR':
        return IndexedFCR(ins, max_larger=fcr['max_larger'], include_larger=True)
    return FastIndexedFCR(ins, max_larger=fcr['max_larger'], include_larger=True,
                          selection=policy['selection'], larger_mode=policy['larger_mode'],
                          audit_rows=policy['audit_rows'])


def fcr_loop(model, compiled, gp, first, index, fcr, deadline, record, timings, ycols):
    """AS25 cutting loop with per-round objective, cost split and row digests."""
    columns = model.getVars()
    seen, row_count, current, scans = set(), 0, first, []
    for iteration in range(fcr['max_rounds']):
        if _remaining(deadline) < fcr['min_reopt_remaining_s']:
            record.update(status='TIME_LIMIT', lp_objective=None,
                          reason='insufficient wall budget to complete FC-R reoptimization')
            break
        _ensure_budget(deadline)
        remaining = fcr['max_cuts_total']-row_count
        if remaining <= 0:
            break
        y, f = _phase(timings, 'lp_point_extraction_s', lambda: _point(model, compiled, current['y_star']))
        sep_budget = min(fcr['max_separation_wall_s'], max(0, _remaining(deadline)-fcr['min_reopt_remaining_s']))
        report = _phase(timings, 'fcr_separation_s', lambda: index.separate(
            y, f, tolerance=fcr['min_violation'], max_cuts=min(remaining, fcr['max_cuts_per_round']),
            time_limit_s=sep_budget, exclude_signatures=seen))
        stats, cuts = report['stats'], report['cuts']
        record['fcr_candidates'] += stats['examined']
        record['fcr_violated'] += stats['violated']
        record['fcr_duplicates'] += stats['duplicates']
        record['fcr_cut_cap_encountered'] |= stats['capped'] > 0
        scans.append((stats['singleton_complete'],
                      stats['larger_complete_selected'] or bool(stats.get('larger_deferred'))))
        start = time.monotonic()
        for cut in cuts:
            _ensure_budget(deadline)
            _add_fcr(model, compiled, columns, gp, cut)
            seen.add(cut.signature)
        model.update()
        timings['fcr_insertion_s'] = timings.get('fcr_insertion_s', 0.)+_elapsed(start)
        row_count += len(cuts)
        nnz = sum(len(c.terms) for c in cuts)
        record['fcr_nnz'] += nnz
        record['fcr_added'] = row_count
        summary = {'round': iteration+1, 'separator_status': report['status'],
                   'stats': {k: v for k, v in stats.items()}, 'emitted': len(cuts), 'nnz': nnz,
                   'emitted_singleton': sum(1 for c in cuts if len(c.region) == 1),
                   'emitted_larger': sum(1 for c in cuts if len(c.region) > 1),
                   'signature_digest': _digest([c.signature for c in cuts]),
                   'terms_digest': _digest([c.terms for c in cuts]),
                   'objective_after': None}
        record['fcr_rounds'].append(summary)
        if not cuts:
            break
        if _remaining(deadline) < fcr['min_reopt_remaining_s']:
            record.update(status='TIME_LIMIT', lp_objective=None, reason='insufficient wall budget after separation')
            break
        current = _phase(timings, 'lp_reoptimization_s', lambda: _optimize(model, gp, deadline, ycols))
        summary['objective_after'] = current['lp_objective']
        summary['reoptimization_s'] = current['solver_wall_s']
        record.update(status=current['status'], lp_objective=current['lp_objective'],
                      n_constraints_final=int(model.NumConstrs), n_nonzeros_final=int(model.NumNZs))
        if current['status'] != 'OPTIMAL':
            break
        if current['lp_objective']+1e-5 < first['lp_objective']:
            record.update(status='ERROR', lp_objective=None, reason='LP objective decreased after valid FC-R')
            break
    record['fcr_total_cut_cap_reached'] = row_count >= fcr['max_cuts_total']
    record['singleton_complete_all_scans'] = all(s for s, _ in scans) if scans else False
    record['larger_complete_or_deferred_all_scans'] = all(l for _, l in scans) if scans else False
    return record


def _work_arm(case, row, root, arm, policy, fcr, deadline):
    if arm not in ARMS:
        raise ValueError('INVALID_INPUT: arm')
    timings = {}
    _ensure_budget(deadline)
    loaded = _phase(timings, 'load_and_reachability_s', lambda: load_instance(row, root=root))
    if loaded.instance_sha256 != case['source_sha256'] or int(loaded.r) != loaded.r or loaded.r < 1:
        raise ValueError('INVALID_INPUT: source hash/autonomy')
    if any(w != 1 for nbr in loaded.adj.values() for _, w in nbr):
        raise ValueError('INVALID_INPUT: nonunit physical graph')
    ins = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), tuple(loaded.A_r), int(loaded.r))
    K = _phase(timings, 'k_preparation_s', lambda: canonical_k(ins, prepare_K(ins, loaded.adj, ins.r)))
    _ensure_budget(deadline)
    compiled = _phase(timings, 'model_construction_s', lambda: compile_u(ins, K, relax=True))
    record = {'status': 'NOT_RUN', 'timings': timings, 'n_variables': len(compiled.variables),
              'n_constraints_initial': len(compiled.equations), 'applied_k_count': len(K),
              'k_sha256': k_digest(ins, K), 'lp_objective': None, 'base_lp_objective': None,
              'fcr_added': 0, 'fcr_violated': 0, 'fcr_duplicates': 0, 'fcr_candidates': 0, 'fcr_nnz': 0,
              'fcr_rounds': [], 'fcr_cut_cap_encountered': False, 'fcr_total_cut_cap_reached': False,
              'singleton_complete_all_scans': None, 'larger_complete_or_deferred_all_scans': None,
              'arm_policy': ARM_POLICIES.get(arm), 'peak_rss_mb': _usage_mb()}
    if len(compiled.variables) > fcr['max_variables']:
        record.update(status='NOT_MEASURED_CAP', reason='variable limit')
        return record
    _ensure_budget(deadline)
    model, ycols, gp = _phase(timings, 'gurobi_build_s', lambda: _solver(compiled, policy, deadline))
    first = _phase(timings, 'lp_base_optimize_s', lambda: _optimize(model, gp, deadline, ycols))
    record.update(status=first['status'], lp_objective=first['lp_objective'],
                  base_lp_objective=first['lp_objective'], n_nonzeros_initial=int(model.NumNZs))
    if first['status'] == 'OPTIMAL' and arm != 'U_K':
        index = _phase(timings, 'fcr_region_index_s', lambda: make_index(arm, ins, fcr))
        fcr_loop(model, compiled, gp, first, index, fcr, deadline, record, timings, ycols)
    record['peak_rss_mb'] = _usage_mb()
    return record


def _worker(conn, case, row, root, arm, policy, fcr, deadline):
    try:
        data = _work_arm(case, row, root, arm, policy, fcr, deadline)
    except MemoryError:
        data = {'status': 'NOT_MEASURED_MEMORY'}
    except TimeoutError:
        data = {'status': 'TIME_LIMIT', 'reason': 'deadline during preparation/solver'}
    except (ModuleNotFoundError, ImportError) as exc:
        data = {'status': 'ERROR', 'reason': f'dependency unavailable: {exc}'}
    except Exception as exc:
        data = {'status': 'ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                'traceback': traceback.format_exc(limit=4)}
    try:
        conn.send(data)
    finally:
        conn.close()


def run_arm(case, row, root, arm, plan):
    start = time.monotonic()
    deadline = start+plan['budget']['wall_seconds_per_arm']
    ctx = mp.get_context('spawn')
    receiver, sender = ctx.Pipe(duplex=False)
    child = ctx.Process(target=_worker, args=(sender, case, row, root, arm,
                                              plan['solver_parameters'], plan['fcr'], deadline))
    child.start()
    sender.close()
    try:
        if receiver.poll(_remaining(deadline)):
            try:
                data = receiver.recv()
            except EOFError:
                data = {'status': 'ERROR', 'reason': 'worker exited without data'}
        else:
            data = {'status': 'TIME_LIMIT', 'reason': 'hard 90s wall deadline; worker terminated'}
    finally:
        if child.is_alive():
            child.terminate()
        child.join(timeout=2)
        if child.is_alive():
            child.kill()
            child.join(timeout=1)
        receiver.close()
    return {'schema_version': SCHEMA, 'stage': 'AS25.1', 'name': case['name'],
            'source_file': case['path'], 'instance_sha256': case['source_sha256'],
            'raw_graph_id': case['raw_graph_id'], 'arm_id': arm,
            'elapsed_wall_s': _elapsed(start), 'budget_s': plan['budget']['wall_seconds_per_arm'], **data}


def execute(plan, plan_sha, source, root, out, names, *, dry_run=False):
    rows_by_name = validate_sources(source, root)
    selection = [c for c in plan['cases'] if c['name'] in names]
    if not selection or len(selection) != len(names):
        raise ValueError('INVALID_INPUT: unknown or duplicated case, development only')
    if not dry_run and importlib.util.find_spec('gurobipy') is None:
        raise RuntimeError('Gurobi unavailable; use --dry-run to verify protocol')
    if out.exists():
        raise FileExistsError('append-only output exists: '+str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=False)
    manifest = {'schema_version': SCHEMA, 'stage': 'AS25.1', 'mode': 'DRY_RUN' if dry_run else 'LP',
                'plan_sha256': plan_sha, 'as25_plan_sha256': plan['as25_plan_sha256'],
                'source_commit': get_commit(), 'source_has_tracked_modifications': _source_dirty(root),
                'code_sha256': {rel: sha256_file(root/rel) for rel in CHECKED_SOURCES},
                'cases': [c['name'] for c in selection], 'raw_graph_ids': [c['raw_graph_id'] for c in selection],
                'arms': list(ARMS), 'arm_policies': ARM_POLICIES, 'budget': plan['budget'],
                'fcr': plan['fcr'], 'solver_parameters': plan['solver_parameters'],
                'gurobi_available': importlib.util.find_spec('gurobipy') is not None,
                'scope': 'development only; LP only; no MIP'}
    write_json_new(out/'manifest.json', manifest)
    rows = []
    for c in selection:
        for arm in ARMS:
            rows.append({'schema_version': SCHEMA, 'stage': 'AS25.1', 'name': c['name'],
                         'raw_graph_id': c['raw_graph_id'], 'instance_sha256': c['source_sha256'],
                         'arm_id': arm, 'status': 'NOT_RUN', 'budget_s': 90, 'elapsed_wall_s': 0.,
                         'reason': 'DRY_RUN does not solve LP'} if dry_run else
                        run_arm(c, rows_by_name[c['name']], root, arm, plan))
    write_json_new(out/'rows.json', rows)
    from analyze_fcr_lp_as251 import analyze
    result = analyze(plan, manifest, rows)
    write_json_new(out/'analysis.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=PLAN_FILE)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', default=None,
                        help='development subset for smoke test; cannot support a full classification')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    plan, sha, base = load_plan(args.plan)
    names = set(args.cases) if args.cases is not None else {c['name'] for c in plan['cases']}
    if args.cases is not None and len(names) != len(args.cases):
        raise ValueError('duplicate case name')
    analysis = execute(plan, sha, base, ROOT, args.output_dir, names, dry_run=args.dry_run)
    print(json.dumps({'classification': analysis['classification'], 'as25_reference_gate': analysis['as25_reference_gate'],
                      'cases': len(names), 'rows': analysis['arm_rows'], 'output_dir': str(args.output_dir)},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
