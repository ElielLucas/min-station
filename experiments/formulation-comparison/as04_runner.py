"""AS-04: execução multiarmas isolada no budget FC-01.

Cada braço repete e paga carregamento+alcance+K (sem custo compartilhado oculto).
Sem Gurobi, preserva SOLVER_ERROR e não inventa valores. F-CC restrita/CORE
são declaradas não comparáveis nesta fase, até adaptador completo homologado.
"""
from __future__ import annotations

import resource
import sys
import time
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE.parent / 'alternative-formulations', HERE.parent / 'benchmark'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as04_arms import Instance, canonical_k, compile_arm, k_digest  # noqa: E402
from as04_schema import ArmResult, SolverPolicy, SCHEMA  # noqa: E402
from as04_compare import compare_case  # noqa: E402
from as03_grouping import instance_fingerprint  # noqa: E402
from as02_validation_gate import GateEvidence, assess  # noqa: E402
from as02_model_a import prepare_K  # noqa: E402
from fc_budget import run_bounded  # noqa: E402
import fc_instances  # noqa: E402


class TooLarge(Exception):
    """Model dimension refusal, not an infeasibility proof."""


def _optimize(compiled, mode: str, policy: SolverPolicy, ctx):
    import gurobipy as gp

    model = gp.Model('AS04-matched')
    model.Params.OutputFlag = 0
    model.Params.Threads = policy.threads
    model.Params.Seed = policy.seed
    # Separar presolve não é suportado neste adapter: Runtime inclui presolve.
    model.Params.TimeLimit = max(1e-6, ctx.require_remaining())
    vars_ = []
    for v in compiled.variables:
        vars_.append(model.addVar(lb=v.lb,
                                  ub=v.ub if v.ub != float('inf') else gp.GRB.INFINITY,
                                  vtype=gp.GRB.BINARY if v.binary else gp.GRB.CONTINUOUS,
                                  name=v.name))
    model.setObjective(gp.quicksum(coef*vars_[j] for j, coef in compiled.objective.items()), gp.GRB.MINIMIZE)
    for eq in compiled.equations:
        expr = gp.quicksum(coef*vars_[j] for j, coef in eq.terms)
        if eq.sense == '==':
            model.addConstr(expr == eq.rhs, name=eq.name)
        elif eq.sense == '<=':
            model.addConstr(expr <= eq.rhs, name=eq.name)
        else:
            model.addConstr(expr >= eq.rhs, name=eq.name)
    model.update()
    size = (model.NumVars, model.NumConstrs, model.NumNZs)
    ctx.phase('solve')
    model.Params.TimeLimit = max(1e-6, ctx.require_remaining())
    model.optimize()
    ctx.phase('validation')
    grb = gp.GRB
    status = ('OPTIMAL_NUMERIC' if model.Status == grb.OPTIMAL else
              'TIME_LIMIT' if model.Status == grb.TIME_LIMIT else
              'INFEASIBLE' if model.Status == grb.INFEASIBLE else 'SOLVER_ERROR')
    if mode == 'MIP' and status == 'TIME_LIMIT' and model.SolCount == 0:
        status = 'NO_INCUMBENT'
    data = {'solver_version': '.'.join(str(x) for x in gp.gurobi.version()),
            'status': status, 'n_variables': size[0], 'n_constraints': size[1],
            'n_nonzeros': size[2], 'solver_runtime_s': float(model.Runtime),
            'solver_work': float(model.Work), 'nodes': float(model.NodeCount),
            'lp_opt_value': None, 'mip_numeric_bound': None,
            'mip_numeric_incumbent': None, 'installed': None}
    if mode == 'LP' and status == 'OPTIMAL_NUMERIC':
        data['lp_opt_value'] = float(model.ObjVal)
    if mode == 'MIP' and status in ('OPTIMAL_NUMERIC', 'TIME_LIMIT'):
        data['mip_numeric_bound'] = float(model.ObjBound)
        if model.SolCount:
            data['mip_numeric_incumbent'] = float(model.ObjVal)
            data['installed'] = tuple(sorted(k[1] for k, j in compiled.columns.items()
                                              if k[0] == 'y' and vars_[j].X > .5))
    return data


def _load_timed(row: dict, root: str):
    """Instrumenta o loader FC sem editar FC: alcance medido dentro do load.

    Patching é privado ao worker isolado por spawn (sem threads). O tempo
    restante do loader cobre leitura, checagem de hashes, parse e adjacência.
    """
    original = fc_instances.construir_arcos_alcance
    reach_wall = 0.0

    def measure(*args, **kwargs):
        nonlocal reach_wall
        start = time.monotonic()
        try:
            return original(*args, **kwargs)
        finally:
            reach_wall += time.monotonic() - start

    started = time.monotonic()
    fc_instances.construir_arcos_alcance = measure
    try:
        loaded = fc_instances.load_instance(row, root=Path(root))
    finally:
        fc_instances.construir_arcos_alcance = original
    total = time.monotonic() - started
    return loaded, max(0.0, total-reach_wall), reach_wall


def validate_physical_ub(loaded, installed):
    """Única entrada de validação: oráculo independente no grafo original."""
    from experiments.cuts.independent_validator import viavel
    if len(set(installed)) != len(installed) or not set(installed) <= set(loaded.V):
        return None
    if not viavel(loaded.S, loaded.T, loaded.V, loaded.adj, int(loaded.r), installed):
        return None
    return len(installed)


def _arm_worker(ctx, row: dict, root: str, arm_id: str, mode: str,
                policy: SolverPolicy, grouping_policy: str, allow_a4: bool,
                max_variables: int, as02_gate: GateEvidence, grouping_seed: int | None = None):
    if policy.memory_limit_bytes is not None:
        resource.setrlimit(resource.RLIMIT_AS, (policy.memory_limit_bytes,
                                               policy.memory_limit_bytes))
    if arm_id not in ('U', 'U_K', 'A2_K', 'A4_K'):
        return {'status': 'NOT_AUTHORIZED', 'reason': 'Adapter completo não homologado; não comparar RMP/F-CC parcial',
                'model_complete': False}
    if arm_id in ('A2_K', 'A4_K') and assess(as02_gate) != 'PASS':
        return {'status': 'NOT_AUTHORIZED', 'reason': f'AS-02 gate: {assess(as02_gate)}',
                'model_complete': False}
    if arm_id == 'A4_K' and not allow_a4:
        return {'status': 'NOT_AUTHORIZED', 'reason': 'A4 requer gate AS-05', 'model_complete': False}
    ctx.phase('preparation')
    loaded, input_wall, reach_wall = _load_timed(row, root)
    if int(loaded.r) != loaded.r:
        raise ValueError('Autonomia não integral para AS02')
    instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                        tuple(loaded.A_r), int(loaded.r))
    inst_hash = instance_fingerprint(instance)
    ctx.phase('k_preparation')
    K = canonical_k(instance, prepare_K(instance, loaded.adj, int(loaded.r)))
    khash = k_digest(instance, K)
    ctx.phase('model_build')
    # Cap seguro de tamanho preliminar: não criar um modelo enorme antes de verificar.
    if arm_id in ('U', 'U_K'):
        guess = len(instance.V) + len(instance.A_r)
    else:
        k = 2 if arm_id == 'A2_K' else 4
        guess = (len(instance.V) + k*(len(instance.A_r)+len(instance.V)+len(instance.S))
                 + len(set(instance.S) & set(instance.T)))
    if guess > max_variables:
        return {'status': 'NOT_BUILT_SIZE', 'reason': f'Estimativa de variáveis {guess} > cap {max_variables}',
                'input_load_s': input_wall, 'reachability_s': reach_wall,
                'instance_sha256': loaded.instance_sha256,
                'structural_sha256': inst_hash, 'reference_k_sha256': khash,
                'applied_k_sha256': None if arm_id == 'U' else khash,
                'k_validated': True, 'model_complete': False}
    compiled, part_hash = compile_arm(arm_id, instance, K, mode=mode,
                                      grouping_policy=grouping_policy,
                                      seed=policy.seed if grouping_seed is None else grouping_seed,
                                      allow_a4=allow_a4)
    if len(compiled.variables) > max_variables:
        return {'status': 'NOT_BUILT_SIZE', 'reason': f'Variáveis reais > cap {max_variables}',
                'input_load_s': input_wall, 'reachability_s': reach_wall,
                'instance_sha256': loaded.instance_sha256, 'structural_sha256': inst_hash,
                'reference_k_sha256': khash,
                'applied_k_sha256': None if arm_id == 'U' else khash,
                'k_validated': True, 'model_complete': False}
    try:
        result = _optimize(compiled, mode, policy, ctx)
    except (ImportError, ModuleNotFoundError) as exc:
        # O build do sistema AS02 foi medido. Não descartar identidade/tempo
        # de preparação só porque o backend Gurobi não está instalado.
        return {'status': 'SOLVER_ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                'input_load_s': input_wall, 'reachability_s': reach_wall,
                'instance_sha256': loaded.instance_sha256,
                'structural_sha256': inst_hash, 'reference_k_sha256': khash,
                'applied_k_sha256': None if arm_id == 'U' else khash,
                'k_validated': True, 'model_complete': False,
                'n_variables': len(compiled.variables),
                'n_constraints': len(compiled.equations),
                'n_nonzeros': compiled.n_nonzeros,
                'partition_sha256': part_hash}
    valid_ub = None
    if mode == 'MIP' and result.get('installed') is not None:
        valid_ub = validate_physical_ub(loaded, result['installed'])
        if valid_ub is None:
            result['status'] = 'VALIDATION_FAIL'
            result['reason'] = 'Instalação rejeitada por validador físico independente'
            result['installed'] = None
            result['mip_numeric_bound'] = None
            result['mip_numeric_incumbent'] = None
    result.update({'input_load_s': input_wall, 'reachability_s': reach_wall,
                   'physical_validated_ub': valid_ub,
                   'instance_sha256': loaded.instance_sha256,
                   'structural_sha256': inst_hash,
                   'reference_k_sha256': khash,
                   'applied_k_sha256': None if arm_id == 'U' else khash,
                   'k_validated': True, 'partition_sha256': part_hash,
                   'peak_rss_kb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'model_complete': True})
    return result


def run_arm(row: dict, *, root: Path, arm_id: str, mode: str, policy: SolverPolicy,
            as02_gate: GateEvidence | None = None, grouping_policy='reachability_degree',
            allow_a4=False, max_variables=1_000_000,
            grouping_seed: int | None = None) -> ArmResult:
    """FC-01 supervisor aplica tempo à carga, alcance, K, build, solve e validação."""
    if max_variables < 1:
        raise ValueError('max_variables deve ser positivo')
    gate = as02_gate or GateEvidence()
    raw = run_bounded(_arm_worker, row, str(root), arm_id, mode, policy,
                      grouping_policy, allow_a4, max_variables, gate, grouping_seed,
                      budget_s=policy.budget_s)
    if raw.status == 'COMPLETED':
        obj = raw.value
        status = obj.pop('status')
        reason = obj.pop('reason', '')
        # Nunca publicar claimed statuses vindos de pre-registro.
        return ArmResult(case_name=row['nome'], arm_id=arm_id, mode=mode, status=status,
                         instance_sha256=obj.pop('instance_sha256', None),
                         structural_sha256=obj.pop('structural_sha256', None),
                         reference_k_sha256=obj.pop('reference_k_sha256', None),
                         applied_k_sha256=obj.pop('applied_k_sha256', None),
                         k_validated=obj.pop('k_validated', False),
                         solver_policy_sha256=policy.sha256, solver_policy=asdict(policy),
                         wall_total_s=raw.wall_total_s,
                         wall_phases_s=dict(raw.phase_wall_s),
                         reason=reason, **obj)
    status = (raw.status if raw.status in ('TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER',
                                            'TIMEOUT_VALIDATION') else 'MEMORY_LIMIT'
              if 'MemoryError' in raw.reason else 'SOLVER_ERROR')
    return ArmResult(case_name=row['nome'], arm_id=arm_id, mode=mode, status=status,
                     reason=raw.reason, instance_sha256=None, structural_sha256=None,
                     reference_k_sha256=None, applied_k_sha256=None, k_validated=False,
                     solver_policy_sha256=policy.sha256, solver_policy=asdict(policy),
                     wall_total_s=raw.wall_total_s, wall_phases_s=dict(raw.phase_wall_s))


def run_case(row: dict, *, root: Path, arm_ids=('U', 'U_K', 'A2_K'), mode='LP',
             policy: SolverPolicy | None = None, as02_gate: GateEvidence | None = None,
             allow_a4=False, max_variables=1_000_000,
             grouping_seed: int | None = None) -> dict:
    if len(arm_ids) != len(set(arm_ids)):
        raise ValueError('Braço duplicado')
    policy = policy or SolverPolicy()
    rows = [run_arm(row, root=root, arm_id=arm, mode=mode, policy=policy,
                    as02_gate=as02_gate, allow_a4=allow_a4,
                    max_variables=max_variables, grouping_seed=grouping_seed) for arm in arm_ids]
    return {'schema': SCHEMA, 'case_name': row['nome'], 'mode': mode,
            'policy_sha256': policy.sha256, 'arms': [x.to_dict() for x in rows],
            'comparison': compare_case(rows)}
