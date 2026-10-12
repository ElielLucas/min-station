"""AS06: piloto MIP pareado, pós-AS05, estritamente exploratório.

Sem heurística nova, sem alteração nos compiladores, no validador físico ou em
resultados históricos. Cada braço paga integralmente preparação, K, build,
solve e validação em um único orçamento supervisionado por FC01.
"""
from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE, HERE.parent / 'alternative-formulations', HERE.parent / 'benchmark'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as02_model_a import Instance, compile_a, compile_u  # noqa: E402
from as03_grouping import instance_fingerprint, partition_two, refine_four, is_nested  # noqa: E402
from as03_size import BuildBudget, decide_build, estimate_size  # noqa: E402
from as04_arms import k_digest  # noqa: E402
from as04_runner import _load_timed, validate_physical_ub  # noqa: E402
from as04_schema import digest  # noqa: E402
from as05_diag_core import _timed_k  # noqa: E402
from as05_protocol import sha256_file  # noqa: E402
from fc_budget import run_bounded  # noqa: E402

SCHEMA = 'AS06-MIP-PLAN-v1'
RESULT = 'AS06-MIP-RESULT-v1'
MANIFEST = 'AS06-MIP-MANIFEST-v1'
ANALYSIS = 'AS06-MIP-ANALYSIS-v1'
PRIMARY = ('U', 'U_K')
SECONDARY = 'A4_K'
SECONDARY_CASES = ('mapf-room-32-32-4-m10-f8', 'puc-w3c571-seed-r1', 'vienna-I056-regiao-f4')
PARENT_PLAN = 'results/benchmark/as05-factorial-plan-v1.json'
PARENT_REPORT = 'results/benchmark/as05-factorial-001/report.json'
SOURCE = 'instances/manifest.csv'
CENSORS = frozenset(('TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER', 'TIMEOUT_VALIDATION',
                    'MEMORY_LIMIT', 'WORKER_ERROR', 'SOLVER_UNAVAILABLE', 'NOT_BUILT_SIZE',
                    'NOT_BUILT_MEMORY', 'NOT_BUILT_BUDGET', 'NOT_APPLICABLE',
                    'SOLVER_ERROR', 'VALIDATION_FAIL'))


def make_plan(root: Path, *, stage: str = 'screening', parent_analysis: Path | None = None) -> dict:
    """Gera plano exato; estágio de 600 s só após análise de 300 s com GO.

    O plano referenciado no disco é congelado por SHA ao executar. O desenho
    secundário utiliza três casos selecionados exploratoriamente na AS05.
    """
    root = root.resolve()
    old = json.loads((root/PARENT_PLAN).read_text(encoding='utf-8'))
    if old.get('schema') != 'AS05-FACTORIAL-PLAN-v1' or len(old['cases']) != 6:
        raise ValueError('AS06: origem fatorial inválida')
    from as05_factorial import verify_experiment
    report = verify_experiment(root / 'results/benchmark/as05-factorial-001')
    if (report.get('expected_cases') != [c['name'] for c in old['cases']]
            or report.get('expected_arms') != old['arms']
            or any(run['status'] != 'OPTIMAL_NUMERIC' for c in report['cases'] for run in c['runs'])):
        raise ValueError('AS06: relatório LP fatorial não concluiu os 36 braços')
    if any(c['split'] != 'desenvolvimento' for c in old['cases']):
        raise ValueError('AS06: split de avaliação proibido')
    if old['grouping'] != {'policy': 'reachability_degree', 'seed': 42,
                           'a4_rule': 'refine_four(parent_A2, authorized=True)',
                           'authorization_scope': 'EXPLORATORY_FACTORIAL_ONLY'}:
        raise ValueError('AS06: agrupamento LP de origem diverge')
    if stage not in ('screening', 'replication'):
        raise ValueError('AS06: estágio desconhecido')
    if stage == 'replication':
        if parent_analysis is None:
            raise ValueError('AS06: replicação exige análise do piloto')
        from as06_reporting import verify_analysis  # import tardio evita ciclo
        analysis = verify_analysis(parent_analysis, expected_stage='screening')
        if analysis['decision'] != 'GO_REPLICATION_EXPLORATORY':
            raise ValueError('AS06: gate de replicação NÃO alcançado')
        parent_rel = str(parent_analysis.resolve().relative_to(root))
        nseeds, arms, budget = (42, 43, 44), list(PRIMARY), 600
        parent_hash = sha256_file(parent_analysis/'analysis.json')
    else:
        parent_rel, parent_hash = None, None
        nseeds, arms, budget = (42,), list(PRIMARY), 300
    cases = []
    for c in old['cases']:
        case = {k: c[k] for k in ('name', 'manifest_name', 'source_sha256',
                                'raw_graph_id', 'graph_source', 'split')}
        case['arms'] = list(arms)
        if stage == 'screening' and c['name'] in SECONDARY_CASES:
            case['arms'].append(SECONDARY)
        cases.append(case)
    return {
        'schema': SCHEMA, 'stage': stage, 'classification': 'EXPLORATORY_DEVELOPMENT_ONLY',
        'scientific_gate': 'PENDING', 'scientific_promotion': 'NOT_AUTHORIZED',
        'parent_sha256': {p: sha256_file(root/p) for p in (PARENT_PLAN, PARENT_REPORT,
          'results/benchmark/as05-factorial-001/manifest.json', SOURCE)},
        'replication_parent_analysis': parent_rel, 'replication_parent_sha256': parent_hash,
        'cases': cases, 'seeds': list(nseeds), 'budget_seconds_per_arm': budget,
        'solver': {'backend': 'gurobi', 'threads': 4, 'warm_start': 'none',
                   'MIPGap': 1e-4, 'OutputFlag': 0,
                   'memory_limit_bytes': old['solver']['memory_limit_bytes'],
                   'callback_sample_s': 5.0, 'callback_max_incumbents': 24,
                   'validation_reserve_s': 30 if stage == 'screening' else 60},
        'limits': {'max_variables': 2_000_000, 'max_constraints': 2_000_000,
                   'max_memory_proxy_bytes': 8 * 1024**3, 'min_solve_reserve_s': 1},
        'grouping': {'policy': 'reachability_degree', 'seed': 42,
                     'a4_rule': 'refine_four(parent_A2, authorized=True)'},
        'k_policy': old['k_policy'],
        'comparison': {'primary': list(PRIMARY), 'secondary': SECONDARY,
                       'secondary_cases': list(SECONDARY_CASES) if stage == 'screening' else [],
                       'no_shared_preparation_credit': True,
                       'equal_solver_settings': True, 'no_warm_start': True},
        'advance_gate': {'absolute_gap_gain_min': 0.02, 'relative_gap_reduction_min': 0.25,
                         'severe_gap_regression_max': 0.01,
                         'minimum_graph_sources': 2, 'minimum_raw_graphs': 2,
                         'valid_physical_ub_required_in_both': True,
                         'replication_requires_screening_go': True},
        'limitations': ['Controles AS05 fatorial usados somente para escolher o secundário',
                        'Não testa instâncias de avaliação',
                        'Sem homologação independente da matemática',
                        'Sem inferir UB física a partir de ObjVal',
                        'Tempo de validação física dentro do budget total'],
    }


def validate_plan(plan: dict, root: Path) -> dict:
    parent = plan.get('replication_parent_analysis')
    if parent is not None:
        rel = Path(parent)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('AS06: caminho de parent inseguro')
    expected = make_plan(root, stage=plan.get('stage'),
                         parent_analysis=root/parent if parent is not None else None)
    if plan != expected:
        raise ValueError('AS06: plano alterado, source ou protocolo divergente')
    return plan


def load_rows(root: Path, plan: dict) -> dict:
    import fc_instances
    rows = {row['nome']: row for row in fc_instances.load_manifest(root/SOURCE)}
    result = {}
    for c in plan['cases']:
        row = rows[c['manifest_name']]
        if row['sha256'] != c['source_sha256']:
            raise ValueError(f'AS06: hash divergente: {c["name"]}')
        result[c['name']] = row
    return result


def expected_slots(plan: dict):
    return [(c, seed, arm) for c in plan['cases'] for seed in plan['seeds'] for arm in c['arms']]


def preflight(root: Path, plan: dict) -> list[dict]:
    import fc_instances
    rows = load_rows(root, plan)
    result = []
    for c in plan['cases']:
        loaded = fc_instances.load_instance(rows[c['name']], root=root)
        instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                            tuple(loaded.A_r), int(loaded.r))
        for arm in c['arms']:
            if arm == SECONDARY:
                g2 = partition_two(instance, policy=plan['grouping']['policy'], seed=42)
                g4 = refine_four(instance, g2, authorized=True)
                est = estimate_size(instance, g4.blocks)
                decision = decide_build(c['name'], arm, g4, est, BuildBudget(
                    max_variables=plan['limits']['max_variables'],
                    max_constraints=plan['limits']['max_constraints'],
                    max_memory_bytes=plan['limits']['max_memory_proxy_bytes']))
                status, nvars, ncons, ram = decision.status, est.variables, est.constraints, est.memory_proxy_bytes
            else:
                nvars, ncons, ram = len(instance.V)+len(instance.A_r), 3*len(instance.V), None
                status = ('READY_FOR_BUILD' if max(nvars/plan['limits']['max_variables'],
                    ncons/plan['limits']['max_constraints']) <= 1 else 'NOT_BUILT_SIZE')
            result.append({'case': c['name'], 'arm': arm, 'seeds': list(plan['seeds']),
                           'status_without_K': status, 'variables_without_K': nvars,
                           'constraints_without_K': ncons, 'memory_proxy_bytes': ram})
    return result


def compile_mip(instance: Instance, arm: str, K=(), grouping=None):
    if arm == 'U':
        if K:
            raise ValueError('AS06: COMP sem K não aceita cortes')
        return compile_u(instance, K=(), relax=False)
    if arm == 'U_K':
        return compile_u(instance, K=K, relax=False)
    if arm == SECONDARY:
        if grouping is None:
            raise ValueError('AS06: A4_K exige partição')
        return compile_a(instance, grouping.blocks, K=K, relax=False)
    raise ValueError('AS06: braço não autorizado')


def physical_trace(loaded, snapshots: list[dict], final_installed, final_numeric_ub):
    """Valida incumbentes pelo grafo físico; não confunde série numérica com UB física."""
    trace = []
    best_ub = None
    first_s = best_s = None
    invalid = 0
    for event in snapshots:
        installed = tuple(event['installed'])
        val = validate_physical_ub(loaded, installed)
        numeric = event.get('numeric_ub')
        if val is None or numeric is None or abs(val-numeric) > 1e-4:
            invalid += 1
            trace.append({'solver_s': event['solver_s'], 'physical_ub': None,
                          'validation': 'REJECTED'})
            continue
        if best_ub is None or val < best_ub:
            best_ub, best_s = val, event['solver_s']
            if first_s is None:
                first_s = event['solver_s']
        trace.append({'solver_s': event['solver_s'], 'physical_ub': best_ub,
                      'validation': 'VALIDATED'})
    final = None
    if final_installed is not None:
        final = validate_physical_ub(loaded, tuple(final_installed))
        if final is None or final_numeric_ub is None or abs(final-final_numeric_ub) > 1e-4:
            invalid += 1
            final = None
    if final is not None and (best_ub is None or final < best_ub):
        best_ub = final
        best_s = None  # evento não observado, não inventar timestamp
    return {'physical_validated_ub': final, 'physical_best_observed_ub': best_ub,
            'time_to_first_validated_ub_solver_s': first_s,
            'time_to_best_validated_ub_solver_s': best_s,
            'physical_trace': trace, 'invalid_incumbents': invalid}


def _solve_mip(compiled, policy: dict, ctx, loaded):
    """Gurobi MIP; checkpoints numéricos e validação retrospectiva independente."""
    import gurobipy as gp
    m = gp.Model('AS06-MIP')
    m.Params.OutputFlag = 0
    m.Params.Threads = policy['threads']
    m.Params.Seed = policy['seed']
    m.Params.MIPGap = policy['MIPGap']
    available = ctx.require_remaining()-policy['validation_reserve_s']
    if available <= 1.0:
        return {'status':'NOT_BUILT_BUDGET', 'reason':'Reserva de validação física inviabiliza solve'}
    m.Params.TimeLimit = available
    variables = [m.addVar(lb=v.lb, ub=v.ub if math.isfinite(v.ub) else gp.GRB.INFINITY,
                          vtype=gp.GRB.BINARY if v.binary else gp.GRB.CONTINUOUS, name=v.name)
                 for v in compiled.variables]
    ys = [(k[1], variables[j]) for k, j in compiled.columns.items() if k[0] == 'y']
    if not ys or len(ys) != len(loaded.V) or any(not compiled.variables[compiled.columns[('y',v)]].binary for v in loaded.V):
        raise ValueError('AS06: todas e somente as variáveis y devem ser binárias')
    m.setObjective(gp.quicksum(coef*variables[j] for j, coef in compiled.objective.items()), gp.GRB.MINIMIZE)
    for eq in compiled.equations:
        expr = gp.quicksum(coef*variables[j] for j, coef in eq.terms)
        m.addConstr(expr == eq.rhs if eq.sense == '==' else expr <= eq.rhs if eq.sense == '<=' else expr >= eq.rhs, name=eq.name)
    m.update()
    dims = {'n_variables': m.NumVars, 'n_constraints': m.NumConstrs, 'n_nonzeros': m.NumNZs}
    last_s = -float('inf')
    bound_trace = []
    ub_snapshots = []
    dropped_incumbents = 0
    callback_errors = []
    max_events = policy['callback_max_incumbents']

    def cb(model, where):
        nonlocal last_s, dropped_incumbents
        try:
            if where not in (gp.GRB.Callback.MIP, gp.GRB.Callback.MIPSOL):
                return
            now = float(model.cbGet(gp.GRB.Callback.RUNTIME))
            if where == gp.GRB.Callback.MIP and now - last_s >= policy['callback_sample_s']:
                lb = float(model.cbGet(gp.GRB.Callback.MIP_OBJBND))
                ub = float(model.cbGet(gp.GRB.Callback.MIP_OBJBST))
                bound_trace.append({'solver_s': now, 'numeric_lb': lb if math.isfinite(lb) and abs(lb)<1e99 else None,
                                    'numeric_incumbent': ub if math.isfinite(ub) and abs(ub)<1e99 else None,
                                    'nodes': float(model.cbGet(gp.GRB.Callback.MIP_NODCNT))})
                last_s = now
            if where == gp.GRB.Callback.MIPSOL:
                obj = float(model.cbGet(gp.GRB.Callback.MIPSOL_OBJ))
                # Reter os primeiros eventos; overflow é sinalizado, não inventar primeiro UB validado.
                if len(ub_snapshots) >= max_events:
                    dropped_incumbents += 1
                    return
                vals = model.cbGetSolution([var for _,var in ys])
                installed = [name for (name, _), val in zip(ys, vals) if val > .5]
                ub_snapshots.append({'solver_s': now, 'numeric_ub': obj, 'installed': installed})
        except Exception as exc:  # callbacks Gurobi não podem mascarar falha de captura
            callback_errors.append(f'{type(exc).__name__}: {exc}')
            model.terminate()

    ctx.phase('solve')
    remaining = ctx.require_remaining()-policy['validation_reserve_s']
    if remaining <= 1.0:
        return {'status':'NOT_BUILT_BUDGET', 'reason':'Montagem consumiu reserva de validação física'}
    m.Params.TimeLimit = remaining
    m.optimize(cb)
    ctx.phase('validation')
    grb = gp.GRB
    status = ('OPTIMAL_NUMERIC' if m.Status == grb.OPTIMAL else
              'TIME_LIMIT' if m.Status == grb.TIME_LIMIT else
              'INFEASIBLE' if m.Status == grb.INFEASIBLE else 'SOLVER_ERROR')
    if callback_errors:
        status = 'SOLVER_ERROR'
    numeric_ub = float(m.ObjVal) if m.SolCount else None
    final_installed = ([name for name,var in ys if var.X > .5] if m.SolCount else None)
    valid = physical_trace(loaded, ub_snapshots, final_installed, numeric_ub)
    if valid['invalid_incumbents']:
        status = 'VALIDATION_FAIL'
    if status == 'TIME_LIMIT' and m.SolCount == 0:
        status = 'NO_INCUMBENT'
    numeric_bound = (float(m.ObjBound) if status in ('OPTIMAL_NUMERIC','TIME_LIMIT','NO_INCUMBENT')
                     and math.isfinite(float(m.ObjBound)) else None)
    if status == 'VALIDATION_FAIL' or status == 'SOLVER_ERROR':
        numeric_bound, numeric_ub = None, None
        valid['physical_validated_ub'] = None
        valid['physical_best_observed_ub'] = None
        final_installed = None
    physical_ub = valid['physical_validated_ub']
    gap = (max(0., (physical_ub-numeric_bound)/max(1.,abs(physical_ub)))
           if physical_ub is not None and numeric_bound is not None else None)
    return {**dims, 'status': status, 'solver_version': '.'.join(map(str,gp.gurobi.version())),
            'peak_rss_kb': int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
            'solver_runtime_s': float(m.Runtime), 'solver_work': float(m.Work),
            'nodes': float(m.NodeCount), 'mip_numeric_bound': numeric_bound,
            'mip_numeric_incumbent': numeric_ub, 'installed': final_installed if physical_ub is not None else None,
            'validated_mip_gap': gap, 'numeric_bound_trace': bound_trace,
            'numeric_callback_dropped_incumbents': dropped_incumbents,
            'callback_errors': callback_errors, **valid}


def _worker(ctx, row, root: str, arm: str, seed: int, plan: dict):
    if arm not in ('U', 'U_K', SECONDARY) or seed not in plan['seeds']:
        raise ValueError('AS06: braço/seed não autorizado')
    cap = plan['solver']['memory_limit_bytes']
    if cap is not None:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    ctx.phase('preparation')
    loaded, input_wall, reach_wall = _load_timed(row, root)
    instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                        tuple(loaded.A_r), int(loaded.r))
    base = {'instance_sha256': loaded.instance_sha256,
            'structural_sha256': instance_fingerprint(instance),
            'input_load_s': input_wall, 'reachability_s': reach_wall,
            'k_prepared_for_this_arm': arm != 'U', 'model_complete': False}
    limits = plan['limits']
    g4, g2 = None, None
    if arm == SECONDARY:
        g2 = partition_two(instance, policy=plan['grouping']['policy'], seed=plan['grouping']['seed'])
        g4 = refine_four(instance, g2, authorized=True)
        if g4.parent_hash != g2.partition_hash or not is_nested(g2.blocks, g4.blocks):
            raise ValueError('AS06: A4 não aninhada')
        est = estimate_size(instance, g4.blocks)
        dec = decide_build(row['nome'], arm, g4, est, BuildBudget(
            max_variables=limits['max_variables'], max_constraints=limits['max_constraints'],
            max_memory_bytes=limits['max_memory_proxy_bytes'],
            remaining_seconds=ctx.remaining(),
            minimum_build_reserve_seconds=limits['min_solve_reserve_s']))
        if dec.status != 'READY_FOR_BUILD':
            return {**base, 'status': dec.status, 'reason': dec.reason,
                    'size_estimate': vars(est), 'k_prepared_for_this_arm': False}
    elif (len(instance.V)+len(instance.A_r) > limits['max_variables'] or
          3*len(instance.V) > limits['max_constraints']):
        return {**base, 'status': 'NOT_BUILT_SIZE', 'reason': 'COMP excede cap',
                'k_prepared_for_this_arm': False}
    K, khash, profile = (), None, None
    if arm != 'U':
        ctx.phase('k_preparation')
        K, profile = _timed_k(instance, loaded, ctx, validator_method='bitset-v2')
        khash = k_digest(instance, K)
        expected = plan['k_policy']['expected_previous_hashes'].get(row['nome'].removesuffix('.txt'))
        if expected is not None and khash != expected:
            raise ValueError('AS06: K diverge da versão v2')
    if arm == SECONDARY:
        est = estimate_size(instance, g4.blocks, k_cuts=tuple(tuple(z) for z in K))
        dec = decide_build(row['nome'], arm, g4, est, BuildBudget(
            max_variables=limits['max_variables'], max_constraints=limits['max_constraints'],
            max_memory_bytes=limits['max_memory_proxy_bytes'],
            remaining_seconds=ctx.remaining(), minimum_build_reserve_seconds=limits['min_solve_reserve_s']))
        if dec.status != 'READY_FOR_BUILD':
            return {**base, 'status': dec.status, 'reason': dec.reason,
                    'size_estimate': vars(est), 'reference_k_sha256': khash}
    if ctx.remaining() <= limits['min_solve_reserve_s']:
        return {**base, 'status': 'NOT_BUILT_BUDGET', 'reason': 'Reserva de tempo insuficiente',
                'reference_k_sha256': khash}
    ctx.phase('model_build')
    compiled = compile_mip(instance, arm, K=K, grouping=g4)
    if len(compiled.variables)>limits['max_variables'] or len(compiled.equations)>limits['max_constraints']:
        return {**base, 'status': 'NOT_BUILT_SIZE', 'reason': 'Excesso pós-build',
                'reference_k_sha256': khash}
    solver_pol = {**plan['solver'], 'seed': seed}
    if ctx.remaining() <= solver_pol['validation_reserve_s']+1.0:
        return {**base, 'status':'NOT_BUILT_BUDGET',
                'reason':'Reserva para solução e validação física insuficiente',
                'reference_k_sha256':khash, 'applied_k_sha256':khash}
    try:
        solved = _solve_mip(compiled, solver_pol, ctx, loaded)
    except (ImportError, ModuleNotFoundError) as exc:
        solved = {'status': 'SOLVER_ERROR', 'reason': f'{type(exc).__name__}: {exc}'}
    if solved['status'] in CENSORS:
        for field in ('mip_numeric_bound', 'mip_numeric_incumbent', 'physical_validated_ub', 'validated_mip_gap'):
            solved[field] = None
        solved['installed'] = None
    return {**base, **solved, 'model_complete': solved['status'] in
            ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'NO_INCUMBENT','INFEASIBLE', 'VALIDATION_FAIL'),
            'reference_k_sha256': khash, 'applied_k_sha256': khash,
            'cut_profile': profile, 'partition_sha256': g4.partition_hash if g4 else None,
            'a4_parent_sha256': g4.parent_hash if g4 else None,
            'n_k_cuts': len(K), 'n_variables': len(compiled.variables),
            'n_constraints': len(compiled.equations), 'n_nonzeros': compiled.n_nonzeros}


def run_arm(row: dict, *, root: Path, plan: dict, arm: str, seed: int) -> dict:
    budget = plan['budget_seconds_per_arm']
    outcome = run_bounded(_worker, row, str(root), arm, seed, plan, budget_s=budget)
    basis = {'case_name': row['nome'], 'arm_id': arm, 'seed': seed,
             'status': None, 'reason': outcome.reason, 'wall_total_s': outcome.wall_total_s,
             'wall_phases_s': dict(outcome.phase_wall_s), 'mip_numeric_bound': None,
             'mip_numeric_incumbent': None, 'physical_validated_ub': None,
             'validated_mip_gap': None, 'model_complete': False}
    if outcome.status == 'COMPLETED':
        basis.update(outcome.value)
        return basis
    basis['status'] = outcome.status if outcome.status in CENSORS else (
        'MEMORY_LIMIT' if 'MemoryError' in outcome.reason or outcome.status == 'CAP_EXCEEDED'
        else 'WORKER_ERROR')
    return basis
