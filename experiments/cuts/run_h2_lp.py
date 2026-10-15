"""AS16: LP-only four-arm experiment and explicitly post-hoc same-pool control.

Run from repository root:
  python experiments/cuts/run_h2_lp.py --output-dir results/benchmark/as16-new
  python experiments/cuts/run_h2_lp.py --output-dir /tmp/as16-smoke --cases NAME1 NAME2

No output is overwritten. Gurobi is required for numeric LP evidence. Every arm
runs in its own process under an absolute 90 s wall deadline (load/K included).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing as mp
from pathlib import Path
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, ROOT / 'experiments' / 'benchmark',
               ROOT / 'experiments' / 'formulation-comparison',
               ROOT / 'experiments' / 'alternative-formulations', HERE):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as00_families import load_specs, raw_family_keys  # noqa: E402
from as00_protocol import PILOT  # noqa: E402
from as02_model_a import Instance, compile_u, prepare_K  # noqa: E402
from as04_arms import canonical_k, k_digest  # noqa: E402
from fc_instances import load_manifest, load_instance  # noqa: E402
from h2_oracle import PhysicalInstance  # noqa: E402
from h2_oracle_schema import VALIDATOR_IDENTITY, canonical_json, digest  # noqa: E402
from h2_separator import SeparatorOptions, separate_h2  # noqa: E402
from h2_supports import select_supports  # noqa: E402

SCHEMA = 'AS16-LP-v1'
ARMS = ('U', 'U_K', 'U_H2', 'U_K_H2')
FIXED_ARMS = ('U_FIXED_H2', 'U_K_FIXED_H2')
ALL_ARMS = ARMS + FIXED_ARMS
PLAN_FILE = ROOT / 'docs/technical/plans/execucao/as16-preregistro-lp-h2.json'


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get_commit():
    run = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=False)
    return run.stdout.strip() if run.returncode == 0 else None


def load_plan(path=PLAN_FILE):
    raw = Path(path).read_bytes()
    plan = json.loads(raw)
    if (plan['schema_version'] != 'AS16-PLAN-v1' or tuple(plan['arm_ids']) != ARMS
            or len(plan['cases']) != 6 or len({c['name'] for c in plan['cases']}) != 6
            or any(c['split'] != 'desenvolvimento' for c in plan['cases'])):
        raise ValueError('INVALID_INPUT: preregistro AS16 inválido')
    if {c['name'] for c in plan['cases']} != set(PILOT):
        raise ValueError('INVALID_INPUT: partição piloto diverge do AS00')
    if plan['budget']['wall_seconds_per_arm'] != 90 or plan['budget']['threads'] != 4:
        raise ValueError('INVALID_INPUT: política experimental não corresponde ao pré-registro')
    if len({c['raw_graph_id'] for c in plan['cases']}) != len(plan['cases']):
        raise ValueError('INVALID_INPUT: grafos brutos não independentes no piloto')
    return plan, hashlib.sha256(raw).hexdigest()


def validate_sources(plan, root=ROOT):
    """Before any optimization verify six files, manifests, raw graph provenance."""
    if sha256_file(root / 'instances/manifest.csv') != plan['manifest_sha256']:
        raise ValueError('INVALID_INPUT: manifesto mudou')
    if sha256_file(root / 'instances/benchmark-v1/spec.csv') != plan['spec_sha256']:
        raise ValueError('INVALID_INPUT: spec de proveniência mudou')
    manifest = {Path(row['nome']).stem: row for row in load_manifest(root / 'instances/manifest.csv')}
    specs = load_specs(root / 'instances/benchmark-v1/spec.csv')
    for src, sha in plan['source_versions'].items():
        if sha256_file(root / src) != sha:
            raise ValueError(f'INVALID_INPUT: componente congelado mudou: {src}')
    for case in plan['cases']:
        row = manifest.get(case['name'])
        if row is None or row['caminho'] != case['path']:
            raise ValueError(f'INVALID_INPUT: manifesto sem {case["name"]}')
        if case['source_sha256'] != sha256_file(root / case['path']):
            raise ValueError(f'INVALID_INPUT: bytes alterados em {case["name"]}')
        if row['particao'] != 'desenvolvimento':
            raise ValueError('INVALID_INPUT: vazamento de avaliação')
        graph_id, family_id = raw_family_keys(row, specs)
        if graph_id != case['raw_graph_id'] or family_id != case['family_id']:
            raise ValueError('INVALID_INPUT: proveniência divergente')
    return manifest


def _elapsed(start):
    return max(0., time.monotonic() - start)


def _remaining(deadline):
    return max(0., deadline - time.monotonic())


def _phase(timings, name, callback):
    start = time.monotonic()
    try:
        return callback()
    finally:
        timings[name] = timings.get(name, 0.) + _elapsed(start)


def _ensure_budget(deadline):
    if _remaining(deadline) <= 0:
        raise TimeoutError('orçamento total de parede esgotado')


def _solver(compiled, policy, deadline):
    """Build LP by compiling COMP/U exactly; no change to U or K."""
    import gurobipy as gp
    _ensure_budget(deadline)
    model = gp.Model('AS16-LP')
    model.Params.OutputFlag = 0
    for key, value in policy.items():
        if key == 'MemLimitGiB':
            model.Params.MemLimit = value
        else:
            setattr(model.Params, key, value)
    cols = []
    for v in compiled.variables:
        cols.append(model.addVar(lb=v.lb, ub=v.ub if math.isfinite(v.ub) else gp.GRB.INFINITY,
                                 vtype=gp.GRB.CONTINUOUS, name=v.name))
    model.setObjective(gp.quicksum(c * cols[j] for j, c in compiled.objective.items()), gp.GRB.MINIMIZE)
    for eq in compiled.equations:
        expr = gp.quicksum(c * cols[j] for j, c in eq.terms)
        if eq.sense == '==':
            model.addConstr(expr == eq.rhs, name=eq.name)
        elif eq.sense == '>=':
            model.addConstr(expr >= eq.rhs, name=eq.name)
        elif eq.sense == '<=':
            model.addConstr(expr <= eq.rhs, name=eq.name)
        else:
            raise ValueError('INVALID_INPUT: sense')
    model.update()
    return model, {k[1]: cols[j] for k, j in compiled.columns.items() if k[0] == 'y'}, gp


def _optimize(model, gp, deadline, ycols):
    _ensure_budget(deadline)
    model.Params.TimeLimit = max(0.001, _remaining(deadline))
    start = time.monotonic()
    model.optimize()
    duration = _elapsed(start)
    statuses = {gp.GRB.OPTIMAL: 'OPTIMAL', gp.GRB.TIME_LIMIT: 'TIME_LIMIT',
                gp.GRB.INFEASIBLE: 'INFEASIBLE', gp.GRB.INTERRUPTED: 'UNKNOWN',
                gp.GRB.NUMERIC: 'UNKNOWN', gp.GRB.MEM_LIMIT: 'NOT_MEASURED_MEMORY'}
    status = statuses.get(model.Status, 'UNKNOWN')
    return {'status': status, 'lp_objective': float(model.ObjVal) if status == 'OPTIMAL' else None,
            'y_star': {v: max(0., min(1., float(c.X))) for v, c in ycols.items()}
            if status == 'OPTIMAL' else None,
            'solver_wall_s': duration, 'solver_runtime_s': float(model.Runtime),
            'solver_work': float(model.Work)}


def _add_cut(model, ycols, gp, cut):
    if set(v for v, _ in cut['coefficients']) - set(ycols):
        raise ValueError('INVALID_INPUT: H2 fora de V')
    model.addConstr(gp.quicksum(float(c) * ycols[v] for v, c in cut['coefficients']) >= 2,
                    name='H2[' + cut['cut_hash'][:16] + ']')


def _work_arm(case, row, root, arm, policy, separator_config, deadline, pool=None):
    timings = {}
    if arm not in ALL_ARMS:
        raise ValueError('INVALID_INPUT: braço desconhecido')
    _ensure_budget(deadline)
    loaded = _phase(timings, 'load_and_reachability_s', lambda: load_instance(row, root=root))
    if int(loaded.r) != loaded.r or loaded.r < 1 or loaded.instance_sha256 != case['source_sha256']:
        raise ValueError('INVALID_INPUT: autonomia/SHA inconsistente')
    ins = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), tuple(loaded.A_r), int(loaded.r))
    # ms_utils reads unit weights as float 1.0, while AS14 requires exact int 1.
    if any(weight != 1 for neighbours in loaded.adj.values() for _, weight in neighbours):
        raise ValueError('INVALID_INPUT: grafo físico não unitário')
    physical_adj = {v: tuple((w, 1) for w, _ in loaded.adj.get(v, ())) for v in loaded.V}
    physical = PhysicalInstance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T), physical_adj, int(loaded.r))
    _ensure_budget(deadline)
    # This cost is paid in EVERY arm, including U_H2 even when K is NOT applied.
    K = _phase(timings, 'k_preparation_s', lambda: canonical_k(ins, prepare_K(ins, loaded.adj, ins.r)))
    use_k = arm in ('U_K', 'U_K_H2', 'U_K_FIXED_H2')
    _ensure_budget(deadline)
    compiled = _phase(timings, 'model_construction_s', lambda: compile_u(ins, K if use_k else (), relax=True))
    max_vars = separator_config['max_variables']
    if len(compiled.variables) > max_vars:
        return {'status': 'NOT_MEASURED_CAP', 'reason': 'variáveis excedem cap pré-registrado',
                'n_variables': len(compiled.variables), 'timings': timings, 'k_sha256': k_digest(ins, K),
                'applied_k_count': len(K) if use_k else 0}
    _ensure_budget(deadline)
    (model, ycols, gp) = _phase(timings, 'gurobi_build_s', lambda: _solver(compiled, policy, deadline))
    first = _phase(timings, 'lp_base_optimize_s', lambda: _optimize(model, gp, deadline, ycols))
    output = {'status': first['status'], 'base_lp_objective': first['lp_objective'],
              'lp_objective': first['lp_objective'], 'time_to_first_lp_s': sum(timings.values()),
              'solver_base': {k: v for k, v in first.items() if k != 'y_star'},
              'timings': timings, 'n_variables': model.NumVars,
              'n_constraints_initial': model.NumConstrs, 'k_sha256': k_digest(ins, K),
              'prepared_k_count': len(K), 'applied_k_count': len(K) if use_k else 0,
              'physical_fingerprint': physical.fingerprint, 'cuts': [],
              'separation': None, 'h2_accepted': 0, 'h2_redundant': 0}
    if first['status'] != 'OPTIMAL':
        return output
    if arm not in ('U_H2', 'U_K_H2', 'U_FIXED_H2', 'U_K_FIXED_H2'):
        return output
    if arm in FIXED_ARMS:
        if pool is None or pool['instance_sha256'] != physical.fingerprint:
            raise ValueError('INVALID_INPUT: pool não corresponde à instância')
        selected = []
        for cut in pool['cuts']:
            # Both fixed-pool controls MUST install every identical certified row;
            # LP-point redundancy is metadata, never a selective application.
            if cut['instance_sha256'] != physical.fingerprint or cut['rhs'] != 2:
                raise ValueError('INVALID_INPUT: corte no pool inválido')
            if 2 - sum(c * first['y_star'][v] for v, c in cut['coefficients']) <= separator_config['min_violation']:
                output['h2_redundant'] += 1
            selected.append(cut)
        output['pool_origin'] = 'POST_HOC_FROM_ONLINE_DEVELOPMENT_ONLY'
        output['timings']['support_selection_s'] = 0.0
        output['timings']['h2_certification_s'] = 0.0
        output['pool_size'] = len(pool['cuts'])
    else:
        _ensure_budget(deadline)
        cut_budget = min(separator_config['separator_budget_s'], _remaining(deadline))
        opt = SeparatorOptions(total_budget_s=cut_budget,
                               per_support_budget_s=separator_config['per_support_budget_s'],
                               max_supports=separator_config['max_supports'],
                               max_pairs=separator_config['max_pairs'],
                               max_oracle_calls=separator_config['max_oracle_calls'],
                               max_candidates_per_support=separator_config['max_candidates_per_support'],
                               max_cuts=separator_config['max_cuts'],
                               min_violation=separator_config['min_violation'])
        supports = _phase(timings, 'support_selection_s',
                          lambda: select_supports(physical.V, first['y_star'],
                              k_supports=K, max_supports=opt.max_supports,
                              max_pairs=opt.max_pairs))
        _ensure_budget(deadline)
        opt = SeparatorOptions(**{**opt.__dict__,
            'total_budget_s': min(cut_budget, _remaining(deadline))})
        report = _phase(timings, 'h2_certification_s',
                        lambda: separate_h2(physical, first['y_star'],
                            proposed_supports=supports, options=opt))
        output['separation'] = report.to_dict()
        output['separation']['external_proposal_policy'] = 'AS15_SELECT_SUPPORTS_CANONICAL_REORDER'
        selected = [cut.to_dict() for cut in report.cuts]
    seen = set()
    for cut in selected:
        if cut['cut_hash'] in seen:
            output['h2_redundant'] += 1
            continue
        seen.add(cut['cut_hash'])
        _ensure_budget(deadline)
        _add_cut(model, ycols, gp, cut)
        output['cuts'].append(cut)
    output['h2_accepted'] = len(output['cuts'])
    if not output['cuts']:
        output['separation_status'] = ('NO_POOL_CUT' if arm in FIXED_ARMS else
                                       output['separation']['status'])
        return output
    model.update()
    second = _phase(timings, 'lp_reoptimization_s', lambda: _optimize(model, gp, deadline, ycols))
    output['status'] = second['status']
    output['lp_objective'] = second['lp_objective']
    output['solver_final'] = {k: v for k, v in second.items() if k != 'y_star'}
    output['n_constraints_final'] = model.NumConstrs
    return output


def _worker(conn, case, row, root, arm, policy, config, deadline, pool):
    try:
        # Only the child imports and uses Gurobi; no solver state is shared.
        result = _work_arm(case, row, root, arm, policy, config, deadline, pool)
        conn.send({'data': result})
    except MemoryError:
        conn.send({'data': {'status': 'NOT_MEASURED_MEMORY', 'reason': 'MemoryError'}})
    except TimeoutError:
        conn.send({'data': {'status': 'TIME_LIMIT', 'reason': 'wall budget expired in preparation'}})
    except ModuleNotFoundError as exc:
        conn.send({'data': {'status': 'ERROR', 'reason': f'missing dependency: {exc.name}'}})
    except Exception as exc:  # Keep the row, never silently drop failure.
        conn.send({'data': {'status': 'ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                            'traceback': traceback.format_exc(limit=5)}})
    finally:
        conn.close()


def run_arm(case, row, root, arm, plan, *, pool=None):
    start = time.monotonic()
    budget = plan['budget']['wall_seconds_per_arm']
    receiver, sender = mp.Pipe(duplex=False)
    process = mp.get_context('spawn').Process(target=_worker,
                args=(sender, case, row,
                      root, arm, plan['solver_parameters'], plan['separation'], start + budget, pool))
    process.start()
    sender.close()
    try:
        if receiver.poll(max(0., start + budget - time.monotonic())):
            result = receiver.recv()['data']
        else:
            result = {'status': 'TIME_LIMIT', 'reason': 'hard wall deadline (worker terminated)'}
    except EOFError:
        result = {'status': 'ERROR', 'reason': 'worker died without a payload (possibly OOM)'}
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()
            process.join()
        receiver.close()
    return {'schema_version': SCHEMA, 'stage': 'AS16', 'name': case['name'],
            'source_file': case['path'], 'instance_sha256': case['source_sha256'],
            'raw_graph_id': case['raw_graph_id'], 'arm_id': arm,
            'budget_s': budget, 'elapsed_wall_s': _elapsed(start),
            'validator_identity': VALIDATOR_IDENTITY, **result}


def pool_for_case(case_rows):
    """Same certified H2 union, post-hoc, only from online development arms."""
    cuts = {}
    physical_sha = None
    for row in case_rows:
        if row['arm_id'] not in ('U_H2', 'U_K_H2') or row['status'] != 'OPTIMAL':
            continue
        if physical_sha is None:
            physical_sha = row.get('physical_fingerprint')
        elif physical_sha != row.get('physical_fingerprint'):
            raise ValueError('INVALID_INPUT: inconsistent physical fingerprints')
        for cut in row.get('cuts', []):
            if cut['instance_sha256'] != physical_sha or not cut['certificate_hashes']:
                raise ValueError('INVALID_INPUT: missing H2 certificate')
            cuts[cut['cut_hash']] = cut
    return {'schema_version': 'AS16-POOL-v1', 'stage': 'AS16',
            'instance_sha256': physical_sha, 'source': 'post-hoc union of online AS15 certified H2',
            'cuts': [cuts[k] for k in sorted(cuts)]}


def write_json_new(path, payload):
    with Path(path).open('x', encoding='utf-8') as file:
        file.write(canonical_json(payload) + '\n')


def execute(plan, plan_sha, root, out, names, *, dry_run=False):
    rows_by_name = validate_sources(plan, root)
    selection = [c for c in plan['cases'] if c['name'] in names]
    if not selection or len(selection) != len(names):
        raise ValueError('INVALID_INPUT: seleção deve conter nomes de desenvolvimento pré-registrados')
    if not dry_run and importlib.util.find_spec('gurobipy') is None:
        raise RuntimeError('Gurobi indisponível: instalar gurobipy/licença ou usar --dry-run')
    if out.exists():
        raise FileExistsError(f'append-only: saída existente {out}')
    out.mkdir(parents=True, exist_ok=False)
    manifest = {'schema_version': SCHEMA, 'stage': 'AS16', 'plan_sha256': plan_sha,
                'source_commit': get_commit(), 'mode': 'DRY_RUN' if dry_run else 'LP',
                'cases': [x['name'] for x in selection], 'arms': list(ARMS),
                'post_hoc_same_pool_arms': list(FIXED_ARMS), 'solver_policy': plan['solver_parameters'],
                'budget': plan['budget'], 'separation': plan['separation'],
                'execution_environment': {'python': sys.version.split()[0],
                    'gurobi_available': importlib.util.find_spec('gurobipy') is not None}}
    write_json_new(out / 'manifest.json', manifest)
    rows = []
    for case in selection:
        own_rows = []
        for arm in ARMS:
            result = ({'schema_version': SCHEMA, 'stage': 'AS16', 'name': case['name'],
                       'instance_sha256': case['source_sha256'], 'raw_graph_id': case['raw_graph_id'],
                       'arm_id': arm, 'status': 'NOT_RUN', 'elapsed_wall_s': 0.,
                       'budget_s': plan['budget']['wall_seconds_per_arm']}
                      if dry_run else run_arm(case, rows_by_name[case['name']], root, arm, plan))
            own_rows.append(result)
            rows.append(result)
        pool = pool_for_case(own_rows) if not dry_run else None
        pool_hash = None
        if pool and pool['instance_sha256']:
            pool_hash = digest(pool)
            write_json_new(out / f'{case["name"]}-pool.json', pool)
        for arm in FIXED_ARMS:
            if dry_run or not pool or not pool['instance_sha256']:
                status, reason = 'NOT_RUN', 'pool H2 ausente; controle não executado'
                result = {'schema_version': SCHEMA, 'stage': 'AS16', 'name': case['name'],
                          'instance_sha256': case['source_sha256'], 'raw_graph_id': case['raw_graph_id'],
                          'arm_id': arm, 'status': status, 'reason': reason, 'elapsed_wall_s': 0.,
                          'budget_s': plan['budget']['wall_seconds_per_arm']}
            else:
                result = run_arm(case, rows_by_name[case['name']], root, arm, plan, pool=pool)
                result['pool_sha256'] = pool_hash
            rows.append(result)
    write_json_new(out / 'rows.json', rows)
    from analyze_h2_lp import analyze
    report = analyze(plan, manifest, rows)
    write_json_new(out / 'analysis.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=PLAN_FILE)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', default=None, help='2 nomes para smoke, 6 para piloto')
    parser.add_argument('--dry-run', action='store_true', help='sem solver; valida entradas e estrutura de saída')
    args = parser.parse_args()
    plan, sha = load_plan(args.plan)
    names = set(args.cases if args.cases else (c['name'] for c in plan['cases']))
    report = execute(plan, sha, args.root, args.output_dir, names, dry_run=args.dry_run)
    print(json.dumps({'gate': report['gate'], 'output_dir': str(args.output_dir),
                      'arm_rows': report['arm_rows']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
