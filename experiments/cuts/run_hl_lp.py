#!/usr/bin/env python3
"""AS20 — limited independent HL real-development LP screen.

Usage from repository root:
  python experiments/cuts/run_hl_lp.py --output-dir results/benchmark/as20-hl-lp-001
  python experiments/cuts/run_hl_lp.py --output-dir /tmp/as20-check --dry-run

Only the six AS16 development instances, never evaluation, are eligible. No
existing results are overwritten. This does not authorize an HL MIP pilot.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing as mp
from pathlib import Path
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from run_h2_lp import (ROOT, Instance, PhysicalInstance, compile_u, prepare_K,
                       canonical_k, k_digest, load_instance, load_plan as load_as16_plan,
                       validate_sources, sha256_file, _solver, _optimize,
                       _phase, _ensure_budget, _elapsed, _remaining, get_commit,
                       write_json_new)
from h2_oracle_schema import VALIDATOR_IDENTITY, digest
from hl_local import HLOptions, separate_hl
from hl_supports import select_hl_supports

SCHEMA = 'AS20-HL-LP-v1'
PLAN_FILE = ROOT / 'docs/technical/plans/execucao/as20-preregistro-hl-lp.json'
ARMS = ('U_K', 'U_K_HL')


def load_plan(path=PLAN_FILE, *, as16_path=None):
    plan_path = Path(path)
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    source, source_sha = load_as16_plan(as16_path) if as16_path else load_as16_plan()
    if plan.get('schema_version') != 'AS20-HL-PLAN-v1' or plan.get('stage') != 'AS20':
        raise ValueError('INVALID_INPUT: schema do plano HL')
    if plan.get('as16_plan_sha256') != source_sha:
        raise ValueError('INVALID_INPUT: AS16 preregister altered')
    if plan.get('cases') != source['cases'] or tuple(plan.get('arms', ())) != ARMS:
        raise ValueError('INVALID_INPUT: casos/arm_ids fora do piloto congelado')
    if plan.get('solver_parameters') != source['solver_parameters']:
        raise ValueError('INVALID_INPUT: política Gurobi diferente de AS16')
    if plan.get('budget', {}).get('wall_seconds_per_arm') != 90:
        raise ValueError('INVALID_INPUT: orçamento de 90s por braço')
    if (plan.get('preregistered_before_real_lp') is not True or
            plan.get('gate') != {
                'minimum_relative_gain': 0.01,
                'minimum_independent_raw_graphs': 2,
                'maximum_cost_multiple': 2.0,
                'require_full_six_cases': True,
                'no_mip_authorization': True,
            } or plan.get('constraints') != [
                'only development', 'no MIP', 'no evaluation',
                'no change COMP K or H2', 'append only']):
        raise ValueError('INVALID_INPUT: scientific gate/safety constraints changed')
    sep = plan.get('hl', {})
    if (sep.get('max_support_size') != 10 or sep.get('max_supports') != 3
            or sep.get('max_pairs') != 24 or sep.get('max_oracle_calls') != 2200
            or sep.get('total_budget_s') != 24 or sep.get('per_support_budget_s') != 12
            or sep.get('min_violation') != 1e-7 or sep.get('max_variables') != 1000000
            or sep.get('max_cuts') != 3):
        raise ValueError('INVALID_INPUT: caps HL diferentes do pré-registro')
    return plan, sha256_file(plan_path), source


def _physical(loaded):
    if int(loaded.r) != loaded.r or loaded.r < 1:
        raise ValueError('INVALID_INPUT: non-integral r')
    if any(weight != 1 for neighbors in loaded.adj.values() for _, weight in neighbors):
        raise ValueError('INVALID_INPUT: non-unit physical edges')
    return PhysicalInstance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                            {v: tuple((w, 1) for w, _ in loaded.adj.get(v, ())) for v in loaded.V},
                            int(loaded.r))


def _add_hl_cut(model, ycols, gp, cut):
    if not set(cut.support) <= set(ycols):
        raise ValueError('INVALID_INPUT: HL outside model')
    if cut.rhs <= 0 or any(a < 0 for _, a in cut.coefficients):
        raise ValueError('INVALID_INPUT: invalid HL inequality')
    model.addConstr(gp.quicksum(float(a) * ycols[v] for v, a in cut.coefficients)
                    >= float(cut.rhs), name='HL[' + cut.cut_hash[:16] + ']')


def _work_arm(case, row, root, arm, policy, config, deadline):
    if arm not in ARMS:
        raise ValueError('INVALID_INPUT: unknown arm')
    timings = {}
    _ensure_budget(deadline)
    loaded = _phase(timings, 'load_and_reachability_s', lambda: load_instance(row, root=root))
    if loaded.instance_sha256 != case['source_sha256']:
        raise ValueError('INVALID_INPUT: source hash mismatch')
    ins = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), tuple(loaded.A_r), int(loaded.r))
    physical = _phase(timings, 'physical_instance_s', lambda: _physical(loaded))
    _ensure_budget(deadline)
    K = _phase(timings, 'k_preparation_s', lambda: canonical_k(ins, prepare_K(ins, loaded.adj, ins.r)))
    _ensure_budget(deadline)
    compiled = _phase(timings, 'model_construction_s', lambda: compile_u(ins, K, relax=True))
    data = {'status': 'NOT_RUN', 'timings': timings, 'physical_fingerprint': physical.fingerprint,
            'prepared_k_count': len(K), 'k_sha256': k_digest(ins, K),
            'n_variables': len(compiled.variables), 'n_constraints_initial': len(compiled.equations),
            'hl_accepted': 0, 'cuts': [], 'separation': None, 'selection': None,
            'lp_objective': None, 'base_lp_objective': None}
    if len(compiled.variables) > config['max_variables']:
        data.update(status='NOT_MEASURED_CAP', reason='COMP+K exceeds variable cap')
        return data
    _ensure_budget(deadline)
    model, ycols, gp = _phase(timings, 'gurobi_build_s', lambda: _solver(compiled, policy, deadline))
    first = _phase(timings, 'lp_base_optimize_s', lambda: _optimize(model, gp, deadline, ycols))
    data.update(status=first['status'], lp_objective=first['lp_objective'],
                base_lp_objective=first['lp_objective'],
                solver_base={key: value for key, value in first.items() if key != 'y_star'},
                time_to_first_lp_s=sum(timings.values()))
    if first['status'] != 'OPTIMAL' or arm == 'U_K':
        return data
    # Support ranking is based only on the COMP+K fractional LP point.
    _ensure_budget(deadline)
    supports, selection = _phase(timings, 'support_selection_s', lambda: select_hl_supports(
        physical.V, first['y_star'], k_supports=K,
        max_support_size=config['max_support_size'], max_supports=config['max_supports'],
        max_pairs=config['max_pairs']))
    data['selection'] = selection
    if not supports:
        data['separation_status'] = 'NO_ELIGIBLE_SUPPORT'
        return data
    _ensure_budget(deadline)
    opt = HLOptions(max_support_size=config['max_support_size'],
                    max_oracle_calls=config['max_oracle_calls'],
                    max_supports=config['max_supports'],
                    total_budget_s=min(config['total_budget_s'], _remaining(deadline)),
                    per_support_budget_s=config['per_support_budget_s'],
                    min_violation=config['min_violation'])
    report = _phase(timings, 'hl_certification_s', lambda: separate_hl(
        physical, first['y_star'], supports=supports, options=opt))
    data['separation'] = report.to_dict()
    # An oracle budget/UNKNOWN is not a negative finding against HL.
    data['separation_status'] = report.status
    selected = list(report.cuts[:config['max_cuts']])
    data['cuts'] = [cut.to_dict() for cut in selected]
    if not selected:
        return data
    for cut in selected:
        _ensure_budget(deadline)
        _add_hl_cut(model, ycols, gp, cut)
    data['hl_accepted'] = len(selected)
    model.update()
    second = _phase(timings, 'lp_reoptimization_s', lambda: _optimize(model, gp, deadline, ycols))
    data['status'] = second['status']
    data['lp_objective'] = second['lp_objective']
    data['solver_final'] = {key: value for key, value in second.items() if key != 'y_star'}
    data['n_constraints_final'] = model.NumConstrs
    # Numeric sanity check: strengthening cannot produce a smaller optimum.
    if (second['status'] == 'OPTIMAL' and first['lp_objective'] is not None
            and second['lp_objective'] + 1e-5 < first['lp_objective']):
        data.update(status='ERROR', reason='HL LP objective decreased; investigate numerical error')
    return data


def _worker(conn, case, row, root, arm, policy, config, deadline):
    try:
        conn.send({'event': 'finished', 'data': _work_arm(case, row, root, arm, policy, config, deadline)})
    except MemoryError:
        conn.send({'event': 'finished', 'data': {'status': 'NOT_MEASURED_MEMORY'}})
    except TimeoutError:
        conn.send({'event': 'finished', 'data': {'status': 'TIME_LIMIT', 'reason': 'deadline during preparation'}})
    except ModuleNotFoundError as exc:
        conn.send({'event': 'finished', 'data': {'status': 'ERROR', 'reason': f'missing {exc.name}'}})
    except Exception as exc:
        conn.send({'event': 'finished', 'data': {'status': 'ERROR',
                   'reason': f'{type(exc).__name__}: {exc}', 'traceback': traceback.format_exc(limit=5)}})
    finally:
        conn.close()


def run_arm(case, row, root, arm, plan):
    start = time.monotonic()
    deadline = start + plan['budget']['wall_seconds_per_arm']
    receiver, sender = mp.get_context('spawn').Pipe(duplex=False)
    child = mp.get_context('spawn').Process(target=_worker, args=(
        sender, case, row, root, arm, plan['solver_parameters'], plan['hl'], deadline))
    child.start()
    sender.close()
    try:
        if receiver.poll(_remaining(deadline)):
            data = receiver.recv().get('data', {'status': 'ERROR', 'reason': 'unexpected worker payload'})
        else:
            data = {'status': 'TIME_LIMIT', 'reason': 'hard wall deadline (worker terminated)'}
    except EOFError:
        data = {'status': 'ERROR', 'reason': 'worker died without results'}
    finally:
        if child.is_alive():
            child.terminate()
        child.join(timeout=2)
        if child.is_alive():
            child.kill()
            child.join()
        receiver.close()
    return {'schema_version': SCHEMA, 'stage': 'AS20', 'name': case['name'],
            'source_file': case['path'], 'instance_sha256': case['source_sha256'],
            'raw_graph_id': case['raw_graph_id'], 'arm_id': arm,
            'elapsed_wall_s': _elapsed(start), 'budget_s': plan['budget']['wall_seconds_per_arm'],
            'validator_identity': VALIDATOR_IDENTITY, **data}


def execute(plan, plan_sha, source, root, out, names, *, dry_run=False):
    manifest_rows = validate_sources(source, root)
    selection = [case for case in plan['cases'] if case['name'] in names]
    if not selection or len(selection) != len(names):
        raise ValueError('INVALID_INPUT: only AS16 development cases allowed')
    if not dry_run and importlib.util.find_spec('gurobipy') is None:
        raise RuntimeError('Gurobi missing; use --dry-run only for validation')
    if out.exists():
        raise FileExistsError(f'append-only: output already exists: {out}')
    out.mkdir(parents=True, exist_ok=False)
    manifest = {'schema_version': SCHEMA, 'mode': 'DRY_RUN' if dry_run else 'LP',
                'plan_sha256': plan_sha, 'as16_plan_sha256': plan['as16_plan_sha256'],
                'source_commit': get_commit(), 'cases': [case['name'] for case in selection],
                'arms': list(ARMS), 'budget': plan['budget'], 'hl': plan['hl'],
                'solver_parameters': plan['solver_parameters'],
                'gurobi_available': importlib.util.find_spec('gurobipy') is not None}
    write_json_new(out / 'manifest.json', manifest)
    rows = []
    for case in selection:
        for arm in ARMS:
            result = ({'schema_version': SCHEMA, 'stage': 'AS20', 'name': case['name'],
                       'instance_sha256': case['source_sha256'], 'raw_graph_id': case['raw_graph_id'],
                       'arm_id': arm, 'status': 'NOT_RUN', 'budget_s': 90, 'elapsed_wall_s': 0.}
                      if dry_run else run_arm(case, manifest_rows[case['name']], root, arm, plan))
            rows.append(result)
    write_json_new(out / 'rows.json', rows)
    from analyze_hl_lp import analyze
    analysis = analyze(plan, manifest, rows)
    write_json_new(out / 'analysis.json', analysis)
    return analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=PLAN_FILE)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', default=None, help='subset for development smoke; no evaluation')
    parser.add_argument('--dry-run', action='store_true', help='validate inputs; no solver and no scientific result')
    args = parser.parse_args()
    plan, sha, source = load_plan(args.plan)
    names = set(args.cases) if args.cases is not None else {case['name'] for case in plan['cases']}
    result = execute(plan, sha, source, ROOT, args.output_dir, names, dry_run=args.dry_run)
    print(json.dumps({'status': result['gate'], 'cases': len(names),
                      'rows': result['arm_rows'], 'output_dir': str(args.output_dir)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
