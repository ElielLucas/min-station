#!/usr/bin/env python3
"""AS28 C3-cut: piloto LP preregistrado, SEM MIP.

Dry-run (sem Gurobi):
 python experiments/cuts/run_c3_lp_as28.py --dry-run --output-dir /tmp/as28-dry
Execucao real (somente apos commit do codigo/pre-registro):
 poetry run python experiments/cuts/run_c3_lp_as28.py --output-dir results/benchmark/as28-c3-lp-001

Usa exatamente U_K, adicionando apenas y(Z)>=1 certificado por conectividade
individual para a amostra fixa de origens e destinos. Distingue selecao
parcial de um fechamento completo. Cada braco tem processo e deadline proprios.
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
from run_h2_lp import (ROOT, Instance, compile_u, prepare_K, canonical_k,
                       load_instance, validate_sources, sha256_file,
                       _solver, _optimize, _phase, _ensure_budget,
                       _elapsed, _remaining, get_commit, write_json_new)
from run_fcr_lp_as25 import _source_dirty
from c3_cut_screen_as28 import screen_c3

SCHEMA = 'AS28-C3-LP-v1'
PLAN_FILE = ROOT/'docs/technical/plans/execucao/as28-preregistro-c3-lp.json'
REF_PLAN = ROOT/'docs/technical/plans/execucao/as251-preregistro-fcr-lp.json'
ARMS = ('U_K', 'U_K_C3')
SOURCE_FILES = ('experiments/cuts/cuts.py', 'experiments/cuts/c3_cut_screen_as28.py',
                'experiments/cuts/run_c3_lp_as28.py',
                'experiments/cuts/analyze_c3_lp_as28.py',
                'experiments/alternative-formulations/as02_model_a.py',
                'experiments/cuts/run_h2_lp.py')


def load_plan(path=PLAN_FILE, ref_path=REF_PLAN, root=ROOT):
    path = Path(path)
    p = json.loads(path.read_text(encoding='utf-8'))
    previous = json.loads(Path(ref_path).read_text(encoding='utf-8'))
    if p.get('schema_version') != 'AS28-C3-PLAN-v1' or p.get('stage') != 'AS28':
        raise ValueError('INVALID_INPUT: schema/stage')
    if p.get('reference_as251_sha256') != sha256_file(ref_path):
        raise ValueError('INVALID_INPUT: reference plan hash changed')
    if p['cases'] != previous['cases'] or p['solver_parameters'] != previous['solver_parameters']:
        raise ValueError('INVALID_INPUT: development cases/solver diverge from AS25.1')
    if tuple(p.get('arms', ())) != ARMS:
        raise ValueError('INVALID_INPUT: arm IDs')
    if p.get('budget', {}).get('wall_seconds_per_arm') != 90:
        raise ValueError('INVALID_INPUT: wall budget')
    if p['screen'] != dict(sources_per_side=8, max_rounds=2, max_cuts_per_round=16,
                           max_cuts_total=32, separation_wall_seconds_per_round=12,
                           min_reopt_remaining_s=2, min_violation=1e-6,
                           max_variables=1000000):
        raise ValueError('INVALID_INPUT: screen settings changed')
    if p['gate'] != dict(minimum_relative_gain=0.01, minimum_independent_raw_graphs=2,
                          maximum_cost_multiple=2, min_paired_optimal=4,
                          require_complete_selected_scans=True, no_mip_authorization=True):
        raise ValueError('INVALID_INPUT: gate changed')
    if p.get('constraints') != ['only development', 'LP only', 'no MIP', 'no evaluation',
                                'no change COMP or K or historical C3',
                                'append only', 'selected sources not globally exhaustive']:
        raise ValueError('INVALID_INPUT: constraints')
    if not p.get('preregistered_before_campaign') or p.get('mip_automatically_authorized') is not False:
        raise ValueError('INVALID_INPUT: authorization')
    for rel, digest in p['source_versions'].items():
        if sha256_file(root/rel) != digest:
            raise ValueError(f'INVALID_INPUT: frozen source changed: {rel}')
    return p, sha256_file(path)


def _work_arm(case, source_row, root, arm, policy, settings, deadline):
    phases = {}
    loaded = _phase(phases, 'load_and_reachability_s',
                    lambda: load_instance(source_row, root=root))
    if loaded.instance_sha256 != case['source_sha256'] or int(loaded.r) != loaded.r:
        raise ValueError('INVALID_INPUT: instance hash/autonomy')
    if any(w != 1 for nbr in loaded.adj.values() for _, w in nbr):
        raise ValueError('INVALID_INPUT: nonunit edge length in principal study')
    ins = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), tuple(loaded.A_r), int(loaded.r))
    K = _phase(phases, 'k_preparation_s',
               lambda: canonical_k(ins, prepare_K(ins, loaded.adj, ins.r)))
    compiled = _phase(phases, 'model_compilation_s', lambda: compile_u(ins, K, relax=True))
    rec = {'status': 'NOT_RUN', 'lp_objective': None, 'timings': phases,
           'n_c3_cuts': 0, 'c3_rounds': [], 'source_counts': {'S': len(ins.S), 'T': len(ins.T)},
           'complete_selected_all_scans': False, 'global_c3_closed': False,
           'policy': settings if arm != 'U_K' else None}
    if len(compiled.variables) > settings['max_variables']:
        rec.update(status='NOT_MEASURED_CAP', reason='variable count')
        return rec
    _ensure_budget(deadline)
    model, ycols, gp = _phase(phases, 'gurobi_build_s', lambda: _solver(compiled, policy, deadline))
    initial = _phase(phases, 'first_lp_optimize_s', lambda: _optimize(model, gp, deadline, ycols))
    rec.update(status=initial['status'], lp_objective=initial['lp_objective'],
               first_lp_objective=initial['lp_objective'])
    if arm == 'U_K' or rec['status'] != 'OPTIMAL':
        return rec
    remaining = settings['max_cuts_total']
    seen = set()
    full_scans = []
    prior_obj = initial['lp_objective']
    current = initial
    for round_number in range(1, settings['max_rounds']+1):
        if _remaining(deadline) <= settings['min_reopt_remaining_s']:
            rec.update(status='TIME_LIMIT', lp_objective=None,
                       reason='insufficient remaining budget for separation/reoptimization')
            break
        y_star = current['y_star']
        sep_budget = min(settings['separation_wall_seconds_per_round'],
                         max(0., _remaining(deadline)-settings['min_reopt_remaining_s']))
        report = _phase(phases, 'c3_separation_s', lambda: screen_c3(
            ins.S, ins.T, ins.A_r, y_star, case_name=case['name'],
            sources_per_side=settings['sources_per_side'],
            min_violation=settings['min_violation'],
            max_cuts=min(remaining, settings['max_cuts_per_round']),
            max_seconds=sep_budget, seen=seen))
        complete = report['status'] == 'COMPLETE_SELECTED'
        full_scans.append(complete)
        round_rec = {'round': round_number, 'separator_status': report['status'],
                     'candidate_terminals': report['candidate_terminals'],
                     'examined_terminals': report['examined_terminals'],
                     'violated_terminals': report['violated_terminals'],
                     'duplicates': report['duplicates'], 'emitted': report['emitted'],
                     'selected_sources': report['source_terminals'],
                     'selected_destinations': report['destination_terminals'],
                     'separation_s': report['elapsed_s'], 'objective_after': None}
        rec['c3_rounds'].append(round_rec)
        if report['status'] in ('PARTIAL_EMPTY_CUT', 'PARTIAL_CERTIFICATE_FAILED',
                                'PARTIAL_NUMERICAL_AMBIGUITY'):
            rec.update(status='UNSAFE_SEPARATOR', lp_objective=None,
                       reason=report['status'])
            break
        if not report['rows']:
            break
        insertion = time.monotonic()
        for row in report['rows']:
            _ensure_budget(deadline)
            Z = row['support']
            assert Z not in seen
            if row['lhs'] >= 1-settings['min_violation']:
                raise ValueError('UNSAFE: nonviolated C3 row')
            if any(v not in ycols for v in Z):
                raise ValueError('UNSAFE: C3 support outside V')
            model.addConstr(gp.quicksum(ycols[v] for v in Z) >= 1,
                            name=f'AS28_C3_{round_number}_{len(seen)}')
            seen.add(Z)
        model.update()
        phases['c3_insertion_s'] = phases.get('c3_insertion_s', 0.)+_elapsed(insertion)
        remaining -= report['emitted']
        rec['n_c3_cuts'] += report['emitted']
        if _remaining(deadline) <= settings['min_reopt_remaining_s']:
            rec.update(status='TIME_LIMIT', lp_objective=None, reason='not enough time to reoptimize')
            break
        current = _phase(phases, 'lp_reoptimization_s',
                         lambda: _optimize(model, gp, deadline, ycols))
        round_rec['objective_after'] = current['lp_objective']
        rec.update(status=current['status'], lp_objective=current['lp_objective'])
        if rec['status'] != 'OPTIMAL':
            break
        if current['lp_objective'] < prior_obj-1e-5:
            rec.update(status='ERROR', lp_objective=None, reason='LP bound decreased after valid cuts')
            break
        prior_obj = current['lp_objective']
        if remaining <= 0:
            break
    rec['complete_selected_all_scans'] = bool(full_scans) and all(full_scans)
    rec['cut_cap_reached'] = remaining <= 0
    rec['n_constraints_final'] = int(model.NumConstrs)
    return rec


def _worker(conn, case, row, root, arm, policy, settings, deadline):
    try:
        result = _work_arm(case, row, root, arm, policy, settings, deadline)
    except MemoryError:
        result = {'status': 'NOT_MEASURED_MEMORY'}
    except TimeoutError:
        result = {'status': 'TIME_LIMIT', 'reason': 'deadline during model preparation'}
    except Exception as exc:
        result = {'status': 'ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                  'traceback': traceback.format_exc(limit=5)}
    try:
        conn.send(result)
    finally:
        conn.close()


def run_arm(case, row, root, arm, plan):
    start = time.monotonic()
    deadline = start+plan['budget']['wall_seconds_per_arm']
    ctx = mp.get_context('spawn')
    receiver, sender = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_worker, args=(sender, case, row, root, arm,
                                             plan['solver_parameters'], plan['screen'], deadline))
    proc.start()
    sender.close()
    try:
        if receiver.poll(_remaining(deadline)):
            try:
                data = receiver.recv()
            except EOFError:
                data = {'status': 'ERROR', 'reason': 'child exited without data'}
        else:
            data = {'status': 'TIME_LIMIT', 'reason': 'hard wall deadline; child terminated'}
    finally:
        if proc.is_alive():
            proc.terminate()
        proc.join(timeout=2)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=1)
        receiver.close()
    return {'schema_version': SCHEMA, 'name': case['name'],
            'instance_sha256': case['source_sha256'], 'raw_graph_id': case['raw_graph_id'],
            'arm_id': arm, 'elapsed_wall_s': _elapsed(start),
            'budget_s': plan['budget']['wall_seconds_per_arm'], **data}


def execute(plan, plan_sha, root, out, names, *, dry_run=False):
    # Reutiliza a validacao da particao AS16 (mesma referencia dos seis casos).
    from run_h2_lp import load_plan as load_as16_plan
    as16, _ = load_as16_plan()
    manifest = validate_sources(as16, root)
    selection = [c for c in plan['cases'] if c['name'] in names]
    if len(selection) != len(names) or not selection:
        raise ValueError('INVALID_INPUT: unknown development case')
    if out.exists():
        raise FileExistsError('append-only output path exists: '+str(out))
    if not dry_run and importlib.util.find_spec('gurobipy') is None:
        raise RuntimeError('Gurobi unavailable: use --dry-run')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(exist_ok=False)
    meta = {'schema_version': SCHEMA, 'mode': 'DRY_RUN' if dry_run else 'LP',
            'plan_sha256': plan_sha, 'reference_as251_sha256': plan['reference_as251_sha256'],
            'source_commit': get_commit(), 'source_has_tracked_modifications': _source_dirty(root),
            'code_sha256': {p: sha256_file(root/p) for p in SOURCE_FILES},
            'cases': [c['name'] for c in selection], 'arms': ARMS,
            'solver_parameters': plan['solver_parameters'], 'budget': plan['budget'],
            'screen': plan['screen'], 'scope': 'development, LP only, bounded C3 selection'}
    write_json_new(out/'manifest.json', meta)
    results = []
    for case in selection:
        for arm in ARMS:
            if dry_run:
                result = {'schema_version': SCHEMA, 'name': case['name'],
                          'raw_graph_id': case['raw_graph_id'], 'arm_id': arm,
                          'status': 'NOT_RUN', 'reason': 'dry-run does not solve LP',
                          'elapsed_wall_s': 0., 'budget_s': plan['budget']['wall_seconds_per_arm']}
            else:
                result = run_arm(case, manifest[case['name']], root, arm, plan)
            results.append(result)
    write_json_new(out/'rows.json', results)
    from analyze_c3_lp_as28 import analyze
    summary = analyze(plan, meta, results)
    write_json_new(out/'analysis.json', summary)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', type=Path, default=PLAN_FILE)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--cases', nargs='+', default=None)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    plan, sha = load_plan(args.plan)
    names = set(args.cases) if args.cases is not None else {c['name'] for c in plan['cases']}
    if args.cases is not None and len(names) != len(args.cases):
        raise ValueError('INVALID_INPUT: duplicate case')
    result = execute(plan, sha, ROOT, args.output_dir, names, dry_run=args.dry_run)
    print(json.dumps({'classification': result['classification'],
                      'paired_optimal': result['paired_optimal'], 'rows': result['arm_rows'],
                      'output_dir': str(args.output_dir)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
