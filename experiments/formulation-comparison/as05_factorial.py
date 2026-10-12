"""AS05-FAC: experimento fatorial exploratório LP (2/4 grupos x sem/com K).

Nunca altera o piloto AS05, a AS04 ou resultados AS05-DIAG v1/v2.
Seis braços completos por instância, com pré-registro de desenvolvimento,
worker por braço supervisionado, checkpoints append-only e integridade SHA256.
"""
from __future__ import annotations

import csv
import io
import json
import math
import resource
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE.parent / 'alternative-formulations', HERE.parent / 'benchmark'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as02_model_a import Instance, compile_a, compile_u  # noqa: E402
from as03_grouping import NotApplicable, is_nested, partition_two, refine_four  # noqa: E402
from as03_size import BuildBudget, decide_build, estimate_size  # noqa: E402
from as04_arms import k_digest  # noqa: E402
from as04_runner import _load_timed, _optimize  # noqa: E402
from as04_schema import SolverPolicy  # noqa: E402
from as05_diag_core import (  # noqa: E402
    _checkpoint_name, _read_or_run_checkpoint, _timed_k, _write_json,
)
from as05_protocol import read_plan, sha256_file  # noqa: E402
from fc_budget import run_bounded  # noqa: E402

SCHEMA = 'AS05-FACTORIAL-PLAN-v1'
RESULT_SCHEMA = 'AS05-FACTORIAL-RESULT-v1'
MANIFEST_SCHEMA = 'AS05-FACTORIAL-MANIFEST-v1'
ANALYSIS_SCHEMA = 'AS05-FACTORIAL-ANALYSIS-v1'
ARMS = ('U', 'U_K', 'A2', 'A2_K', 'A4', 'A4_K')
WITH_K = frozenset(('U_K', 'A2_K', 'A4_K'))
GROUPED = frozenset(('A2', 'A2_K', 'A4', 'A4_K'))
A4 = frozenset(('A4', 'A4_K'))
PARENT = 'results/benchmark/as05-prospective-plan-v1.json'
V2_PLAN = 'results/benchmark/as05-diagnostic-retest-plan-v2.json'
V2_ANALYSIS = 'results/benchmark/as05-diagnostic-v2-001/analysis/analysis.json'
ORIGINAL_PILOT = 'results/benchmark/as05-pilot-owner-exploratory-001/lp_gate.json'
CENSOR = frozenset(('NOT_APPLICABLE', 'NOT_BUILT_SIZE', 'NOT_BUILT_MEMORY',
                    'NOT_BUILT_BUDGET', 'TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER',
                    'TIMEOUT_VALIDATION', 'MEMORY_LIMIT', 'SOLVER_ERROR', 'WORKER_ERROR',
                    'SOLVER_UNAVAILABLE', 'TIME_LIMIT'))


def make_plan(root: Path) -> dict:
    """Seleção fixa de seis casos AS00, independente de valores LP posteriores."""
    root = root.resolve()
    parent, _ = read_plan(root/PARENT, root)
    cases = list(parent['pilot_cases'])
    if len(cases) != 6 or len({case['name'] for case in cases}) != 6:
        raise ValueError('FACTORIAL: são obrigatórias seis instâncias de desenvolvimento')
    if any(case['split'] != 'desenvolvimento' for case in cases):
        raise ValueError('FACTORIAL: split avaliação não autorizado')
    seed = parent['policy']['seed']
    if parent['policy']['grouping_seed'] != seed:
        raise ValueError('FACTORIAL: grouping seed original divergente')
    files = (PARENT, V2_PLAN, V2_ANALYSIS, ORIGINAL_PILOT)
    for path in files:
        if not (root/path).is_file():
            raise FileNotFoundError(f'FACTORIAL: evidência anterior ausente: {path}')
    v2 = json.loads((root/V2_PLAN).read_text(encoding='utf-8'))
    if v2.get('K_validator') != 'bitset-v2' or v2.get('grouping_seed') != seed:
        raise ValueError('FACTORIAL: precondições técnicas v2 divergentes')
    return {
        'schema': SCHEMA,
        'parent_file_sha256': {p: sha256_file(root/p) for p in files},
        'source_manifest_sha256': sha256_file(root/'instances/manifest.csv'),
        'cases': [{k: case[k] for k in ('name', 'manifest_name', 'source_sha256',
                                      'raw_graph_id', 'graph_source', 'split')}
                  for case in cases],
        'arms': list(ARMS),
        'mode': 'LP',
        'grouping': {'policy': 'reachability_degree', 'seed': seed,
                     'a4_rule': 'refine_four(parent_A2, authorized=True)',
                     'authorization_scope': 'EXPLORATORY_FACTORIAL_ONLY'},
        'solver': {'backend': 'gurobi', 'threads': parent['policy']['threads'],
                   'seed': seed, 'warm_start': 'none',
                   'memory_limit_bytes': parent['policy']['memory_limit_bytes']},
        'budget_seconds_per_arm': 300,
        'limits': {'max_variables': 2_000_000, 'max_constraints': 2_000_000,
                   'max_memory_proxy_bytes': 8 * (1024**3),
                   'min_remaining_build_seconds': 1.0},
        'k_policy': {'validator': 'bitset-v2', 'generator': 'C1+C2+C4-DM',
                     'charge_only_with_k': True,
                     'expected_previous_hashes': dict(v2['expected_k_sha256'])},
        'classification': 'POSTHOC_EXPLORATORY_DEVELOPMENT_ONLY',
        'scientific_gate': 'PENDING', 'scientific_promotion': 'NOT_AUTHORIZED',
        'requirements': {
            'all_cases_all_arms_retained': True,
            'no_lp_value_on_censor': True,
            'u_and_a_without_k_do_not_generate_k': True,
            'same_parent_A2_for_A2_and_A4_with_without_k': True,
            'new_results_never_replace_AS05_or_v2': True,
            'no_per_case_posthoc_partition_choice': True,
        },
    }


def validate_plan(plan: dict, root: Path) -> dict:
    if plan.get('schema') != SCHEMA or plan != make_plan(root):
        raise ValueError('FACTORIAL: plano alterado ou fonte/protocolo divergente')
    return plan


def load_rows(root: Path, plan: dict) -> dict:
    import fc_instances

    rows = {row['nome']: row for row in fc_instances.load_manifest(root/'instances/manifest.csv')}
    found = {}
    for case in plan['cases']:
        row = rows[case['manifest_name']]
        if row['sha256'] != case['source_sha256']:
            raise ValueError(f'FACTORIAL: fonte divergente: {case["name"]}')
        found[case['name']] = row
    return found


def preflight_sizes(root: Path, plan: dict) -> list[dict]:
    """Estima os seis braços sem gerar K, montar modelos ou chamar solvers.

    A6 não entra nesta estimativa preliminar; será conferida durante o
    próprio worker +K após preparação e validação integral dos cortes.
    """
    import fc_instances

    rows = load_rows(root, plan)
    output = []
    for case in plan['cases']:
        loaded = fc_instances.load_instance(rows[case['name']], root=root)
        instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                            tuple(loaded.A_r), int(loaded.r))
        g2 = partition_two(instance, policy=plan['grouping']['policy'],
                           seed=plan['grouping']['seed'])
        g4 = (refine_four(instance, g2, authorized=True)
              if min(map(len, g2.blocks)) >= 2 else None)
        for arm in ARMS:
            grouping = g2 if arm in ('A2', 'A2_K') else g4 if arm in A4 else None
            if arm in GROUPED and grouping is None:
                status, nvars, memory = 'NOT_APPLICABLE', None, None
            elif grouping is not None:
                est = estimate_size(instance, grouping.blocks)
                decision = decide_build(case['name'], arm, grouping, est,
                    BuildBudget(max_variables=plan['limits']['max_variables'],
                                max_constraints=plan['limits']['max_constraints'],
                                max_memory_bytes=plan['limits']['max_memory_proxy_bytes']))
                status, nvars, memory = decision.status, est.variables, est.memory_proxy_bytes
            else:
                nvars = len(instance.V) + len(instance.A_r)
                memory = None
                status = 'READY_FOR_BUILD' if nvars <= plan['limits']['max_variables'] else 'NOT_BUILT_SIZE'
            output.append({'case': case['name'], 'arm': arm, 'status': status,
                           'n_variables_without_a6': nvars,
                           'memory_proxy_bytes': memory,
                           'n_vertices': len(instance.V), 'n_reach_arcs': len(instance.A_r),
                           'n_origins': len(instance.S)})
    return output


def partitions(instance: Instance, *, policy: str, seed: int):
    """Mesma A2 para os quatro braços A, com A4 estritamente aninhada."""
    g2 = partition_two(instance, policy=policy, seed=seed)
    g4 = refine_four(instance, g2, authorized=True)
    if g4.parent_hash != g2.partition_hash or not is_nested(g2.blocks, g4.blocks):
        raise ValueError('FACTORIAL: A4 não aninhada em A2')
    return g2, g4


def compile_factorial(instance: Instance, arm: str, *, cuts=(),
                      groups2=None, groups4=None):
    """Compiladores AS02 existentes, sem recriar sistemas lineares."""
    if arm not in ARMS:
        raise ValueError('FACTORIAL: braço desconhecido')
    if arm not in WITH_K and cuts:
        raise ValueError('FACTORIAL: corte aplicado a braço sem K')
    if arm in ('U', 'U_K'):
        return compile_u(instance, K=cuts if arm in WITH_K else (), relax=True)
    group = groups2 if arm in ('A2', 'A2_K') else groups4
    if group is None:
        raise ValueError('FACTORIAL: partição ausente')
    if arm in A4 and (groups2 is None or group.parent_hash != groups2.partition_hash
                      or not is_nested(groups2.blocks, group.blocks)):
        raise ValueError('FACTORIAL: A4 deve refinar a mesma A2')
    return compile_a(instance, group.blocks, K=cuts if arm in WITH_K else (), relax=True)


def _base_record(loaded, instance, *, arm, group2, group4):
    from as03_grouping import instance_fingerprint

    chosen = group4 if arm in A4 else group2 if arm in GROUPED else None
    return {
        'instance_sha256': loaded.instance_sha256,
        'structural_sha256': instance_fingerprint(instance),
        'a2_partition_sha256': group2.partition_hash if group2 else None,
        'a4_partition_sha256': group4.partition_hash if group4 else None,
        'partition_sha256': chosen.partition_hash if chosen else None,
        'a4_parent_sha256': group4.parent_hash if group4 else None,
    }


def _factorial_worker(ctx, row: dict, root: str, arm: str, plan: dict):
    """Worker isolado; cada braço paga sua preparação/validação e montagem."""
    if arm not in ARMS:
        raise ValueError('FACTORIAL: braço fora do protocolo')
    if plan['solver']['memory_limit_bytes'] is not None:
        cap = plan['solver']['memory_limit_bytes']
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    ctx.phase('preparation')
    loaded, input_wall, reach_wall = _load_timed(row, root)
    instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                        tuple(loaded.A_r), int(loaded.r))
    if int(loaded.r) != loaded.r:
        raise ValueError('FACTORIAL: autonomia não inteira')
    g2, g4 = None, None
    try:
        if arm in GROUPED:
            g2 = partition_two(instance, policy=plan['grouping']['policy'],
                               seed=plan['grouping']['seed'])
            if min(map(len, g2.blocks)) >= 2:
                g4 = refine_four(instance, g2, authorized=True)
                if not is_nested(g2.blocks, g4.blocks):
                    raise ValueError('FACTORIAL: grupos A4 não aninhados')
            elif arm in A4:
                raise NotApplicable('FACTORIAL: A4 requer ao menos duas origens por grupo A2')
    except NotApplicable as exc:
        return {'status': 'NOT_APPLICABLE', 'reason': str(exc),
                'model_complete': False, 'k_prepared_for_this_arm': False,
                'input_load_s': input_wall,
                'reachability_s': reach_wall, **_base_record(loaded, instance,
                                                            arm=arm, group2=g2, group4=g4)}
    base = {**_base_record(loaded, instance, arm=arm, group2=g2, group4=g4),
            'input_load_s': input_wall, 'reachability_s': reach_wall,
            'k_prepared_for_this_arm': False}
    # O filtro de memória/tamanho é feito ANTES de preparar K em modelos A grandes.
    limits = plan['limits']
    if arm in GROUPED:
        estimate = estimate_size(instance, (g2 if arm in ('A2', 'A2_K') else g4).blocks)
        build = decide_build(row['nome'], arm, g2 if arm in ('A2', 'A2_K') else g4,
                             estimate, BuildBudget(
                                 max_variables=limits['max_variables'],
                                 max_constraints=limits['max_constraints'],
                                 max_memory_bytes=limits['max_memory_proxy_bytes'],
                                 remaining_seconds=ctx.remaining(),
                                 minimum_build_reserve_seconds=limits['min_remaining_build_seconds']))
        size = vars(estimate)
        if build.status != 'READY_FOR_BUILD':
            return {**base, 'status': build.status, 'reason': build.reason,
                    'model_complete': False, 'size_estimate': size}
    else:
        n, a = len(instance.V), len(instance.A_r)
        size = {'variables': n+a, 'constraints': 3*n,
                'memory_estimator': 'U_size_counts_only_proxy_not_certified'}
        if n+a > limits['max_variables'] or 3*n > limits['max_constraints']:
            return {**base, 'status': 'NOT_BUILT_SIZE', 'reason': 'Controle U excede cap',
                    'model_complete': False, 'size_estimate': size}
    K, cut_profile, khash = (), None, None
    if arm in WITH_K:
        ctx.phase('k_preparation')
        K, cut_profile = _timed_k(instance, loaded, ctx, validator_method='bitset-v2')
        base['k_prepared_for_this_arm'] = True
        khash = k_digest(instance, K)
        expected = plan['k_policy']['expected_previous_hashes'].get(row['nome'].removesuffix('.txt'))
        if expected and khash != expected:
            raise ValueError('FACTORIAL: conjunto K difere da referência v2')
    if arm in GROUPED and K:
        # Acrescentar A6 no tamanho previsto sem reconstruir a partição.
        estimate = estimate_size(instance, (g2 if arm in ('A2', 'A2_K') else g4).blocks,
                                 k_cuts=tuple(tuple(x) for x in K))
        size = vars(estimate)
        decision = decide_build(row['nome'], arm, g2 if arm in ('A2', 'A2_K') else g4,
                                estimate, BuildBudget(max_variables=limits['max_variables'],
                                max_constraints=limits['max_constraints'],
                                max_memory_bytes=limits['max_memory_proxy_bytes'],
                                remaining_seconds=ctx.remaining(),
                                minimum_build_reserve_seconds=limits['min_remaining_build_seconds']))
        if decision.status != 'READY_FOR_BUILD':
            return {**base, 'status': decision.status, 'reason': decision.reason,
                    'model_complete': False, 'size_estimate': size,
                    'reference_k_sha256': khash, 'cut_profile': cut_profile}
    if ctx.remaining() < limits['min_remaining_build_seconds']:
        return {**base, 'status': 'NOT_BUILT_BUDGET', 'reason': 'Prazo restante para montar modelo insuficiente',
                'model_complete': False, 'size_estimate': size,
                'reference_k_sha256': khash, 'cut_profile': cut_profile}
    ctx.phase('model_build')
    compiled = compile_factorial(instance, arm, cuts=K, groups2=g2, groups4=g4)
    if len(compiled.variables) > limits['max_variables'] or len(compiled.equations) > limits['max_constraints']:
        return {**base, 'status': 'NOT_BUILT_SIZE', 'reason': 'Modelo excede cap pós-build',
                'model_complete': False, 'size_estimate': size,
                'reference_k_sha256': khash, 'cut_profile': cut_profile}
    policy = SolverPolicy(seed=plan['solver']['seed'], threads=plan['solver']['threads'],
                          budget_s=plan['budget_seconds_per_arm'],
                          memory_limit_bytes=plan['solver']['memory_limit_bytes'])
    try:
        result = _optimize(compiled, 'LP', policy, ctx)
    except (ImportError, ModuleNotFoundError) as exc:
        result = {'status': 'SOLVER_ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                  'model_complete': False, 'lp_opt_value': None}
    status = result['status']
    result['model_complete'] = status in ('OPTIMAL_NUMERIC', 'TIME_LIMIT', 'INFEASIBLE')
    if status != 'OPTIMAL_NUMERIC':
        result['lp_opt_value'] = None
    return {**base, **result, 'size_estimate': size,
            'reference_k_sha256': khash,
            'applied_k_sha256': khash if arm in WITH_K else None,
            'k_validated': arm in WITH_K, 'cut_profile': cut_profile,
            'n_variables': result.get('n_variables', len(compiled.variables)),
            'n_constraints': result.get('n_constraints', len(compiled.equations)),
            'n_nonzeros': result.get('n_nonzeros', compiled.n_nonzeros)}


def run_arm(row: dict, *, root: Path, arm: str, plan: dict) -> dict:
    outcome = run_bounded(_factorial_worker, row, str(root), arm, plan,
                          budget_s=plan['budget_seconds_per_arm'])
    record = {'case_name': row['nome'], 'arm_id': arm,
              'grouping_policy': plan['grouping']['policy'] if arm in GROUPED else None,
              'status': None, 'reason': outcome.reason,
              'wall_total_s': outcome.wall_total_s,
              'wall_phases_s': dict(outcome.phase_wall_s),
              'lp_opt_value': None, 'model_complete': False}
    if outcome.status == 'COMPLETED':
        record.update(outcome.value)
        if record['status'] != 'OPTIMAL_NUMERIC':
            record['lp_opt_value'] = None
        return record
    if outcome.status in CENSOR:
        record['status'] = outcome.status
    elif outcome.status in ('CAP_EXCEEDED',):
        record['status'] = 'MEMORY_LIMIT'
    else:
        record['status'] = 'MEMORY_LIMIT' if 'MemoryError' in outcome.reason else 'WORKER_ERROR'
    return record


def _is_opt(run: dict) -> bool:
    value = run.get('lp_opt_value')
    return run.get('status') == 'OPTIMAL_NUMERIC' and run.get('model_complete') is True \
        and type(value) in (int, float) and math.isfinite(value)


def _contrast(a: dict, b: dict) -> dict:
    if not _is_opt(a) or not _is_opt(b):
        return {'status': 'NOT_COMPARABLE', 'lp_delta': None, 'relative_gain': None,
                'wall_ratio': None, 'solver_ratio': None,
                'reason': f'{a["status"]} versus {b["status"]}'}
    delta = b['lp_opt_value']-a['lp_opt_value']
    denom = max(abs(a['lp_opt_value']), 1.0)
    return {'status': 'MATCHED_COMPLETE', 'lp_delta': delta,
            'relative_gain': delta/denom,
            'wall_ratio': (b['wall_total_s']/a['wall_total_s'] if a.get('wall_total_s') else None),
            'solver_ratio': (b['solver_runtime_s']/a['solver_runtime_s']
                             if a.get('solver_runtime_s') and b.get('solver_runtime_s') else None),
            'reason': 'Dois LP ótimos numéricos; não certificados racionais'}


PAIRS = {
    'K_ON_U': ('U', 'U_K'),
    'GROUP_2_NO_K': ('U', 'A2'),
    'GROUP_4_NO_K': ('A2', 'A4'),
    'A4_VS_U_NO_K': ('U', 'A4'),
    'K_ON_A2': ('A2', 'A2_K'),
    'K_ON_A4': ('A4', 'A4_K'),
    'REFINEMENT_WITH_K': ('A2_K', 'A4_K'),
    'A2_OVER_U_K': ('U_K', 'A2_K'),
    'A4_OVER_U_K': ('U_K', 'A4_K'),
}


def verify_case(case: dict, plan: dict) -> None:
    if [r.get('arm_id') for r in case['runs']] != list(ARMS):
        raise ValueError('FACTORIAL: braço faltante/repetido/fora de ordem')
    runs = {r['arm_id']: r for r in case['runs']}
    for r in case['runs']:
        if r.get('status') == 'OPTIMAL_NUMERIC' and not _is_opt(r):
            raise ValueError('FACTORIAL: ótimo LP sem valor numérico válido')
        if r.get('status') != 'OPTIMAL_NUMERIC' and r.get('model_complete') is True and r.get('status') not in ('TIME_LIMIT','INFEASIBLE'):
            raise ValueError('FACTORIAL: modelo censurado indevidamente marcado completo')
        if r['status'] in CENSOR or r['status'] != 'OPTIMAL_NUMERIC':
            if r.get('lp_opt_value') is not None:
                raise ValueError('FACTORIAL: limite LP censurado indevidamente publicado')
        if r['arm_id'] not in WITH_K and (r.get('k_prepared_for_this_arm') is True
                                           or r.get('applied_k_sha256') is not None):
            raise ValueError('FACTORIAL: K cobrado/aplicado a braço sem K')
        if r['arm_id'] in GROUPED and r.get('grouping_policy') != plan['grouping']['policy']:
            raise ValueError('FACTORIAL: mudança pós-hoc de política de agrupamento')
    complete = [r for r in case['runs'] if _is_opt(r)]
    for key in ('instance_sha256', 'structural_sha256'):
        known = {r.get(key) for r in complete}
        if None in known or len(known) > 1:
            raise ValueError(f'FACTORIAL: instâncias divergentes em {key}')
    kknown = {r.get('reference_k_sha256') for r in case['runs'] if r['arm_id'] in WITH_K
              and r.get('reference_k_sha256') is not None}
    if len(kknown) > 1:
        raise ValueError('FACTORIAL: cortes K divergentes nos três braços')
    for arm in WITH_K:
        run = runs[arm]
        if _is_opt(run) and (not run.get('k_prepared_for_this_arm')
                            or not run.get('k_validated')
                            or not run.get('reference_k_sha256')
                            or run.get('applied_k_sha256') != run.get('reference_k_sha256')):
            raise ValueError('FACTORIAL: K não validado/com hash incorreto')
    for family in (('A2', 'A2_K'), ('A4', 'A4_K')):
        values = {runs[arm].get('partition_sha256') for arm in family if _is_opt(runs[arm])}
        if len(values) > 1:
            raise ValueError('FACTORIAL: partição mudou entre sem/com K')
    a2s = {r.get('a2_partition_sha256') for r in complete if r['arm_id'] in GROUPED}
    if None in a2s and a2s:
        raise ValueError('FACTORIAL: hash de A2 ausente em braço agrupado completo')
    a4s = {r.get('a4_partition_sha256') for r in complete
           if r['arm_id'] in GROUPED and r.get('a4_partition_sha256') is not None}
    if len(a2s) > 1 or len(a4s) > 1:
        raise ValueError('FACTORIAL: pai/filhos aninhados não consistentes')
    for arm in A4:
        r = runs[arm]
        if _is_opt(r) and r.get('a4_parent_sha256') != r.get('a2_partition_sha256'):
            raise ValueError('FACTORIAL: A4 não vinculada ao pai A2')
    # Monotonicidade esperada: não converta tolerâncias numéricas em teorema.
    for left, right in (('U', 'A2'), ('A2', 'A4'), ('U_K', 'A2_K'),
                        ('A2_K', 'A4_K'), ('U', 'U_K'), ('A2', 'A2_K'), ('A4', 'A4_K')):
        if _is_opt(runs[left]) and _is_opt(runs[right]):
            a, b = runs[left]['lp_opt_value'], runs[right]['lp_opt_value']
            if b < a - 1e-6 * max(1., abs(a), abs(b)):
                raise ValueError(f'FACTORIAL: monotonicidade LP violada: {left}->{right}')


def csv_arm_rows(cases: list[dict]) -> list[dict]:
    return [{
        'case': case['name'], 'arm': run['arm_id'], 'status': run['status'],
        'reason': run.get('reason', ''), 'lp_opt_value': run.get('lp_opt_value'),
        'wall_total_s': run.get('wall_total_s'),
        'solver_runtime_s': run.get('solver_runtime_s'),
        'n_variables': run.get('n_variables'),
        'n_constraints': run.get('n_constraints'),
        'n_nonzeros': run.get('n_nonzeros'),
        'partition_sha256': run.get('partition_sha256'),
        'reference_k_sha256': run.get('reference_k_sha256'),
        'estimated_memory_proxy_bytes': (run.get('size_estimate') or {}).get('memory_proxy_bytes'),
        'k_preparation_s': sum(v for k, v in run.get('wall_phases_s', {}).items()
                               if k.startswith('k_')),
        'model_build_s': run.get('wall_phases_s', {}).get('model_build'),
    } for case in cases for run in case['runs']]


def serialize_csv(rows: list[dict]) -> str:
    buffer = io.StringIO(newline='')
    if not rows:
        raise ValueError('FACTORIAL: linhas vazias')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def run_experiment(*, root: Path, plan_path: Path, output_dir: Path,
                   resume: bool = False, runner=run_arm) -> Path:
    root = root.resolve()
    plan = validate_plan(json.loads(plan_path.read_text(encoding='utf-8')), root)
    if output_dir.exists():
        if not resume or (output_dir/'report.json').exists():
            raise FileExistsError('FACTORIAL: saída já existe (append-only)')
        if sha256_file(output_dir/'plan.json') != sha256_file(plan_path):
            raise ValueError('FACTORIAL: checkpoint incompatível com plano')
    else:
        if resume:
            raise FileNotFoundError('FACTORIAL: --resume exige execução parcial')
        output_dir.mkdir(parents=True)
        (output_dir/'plan.json').write_bytes(plan_path.read_bytes())
    rows = load_rows(root, plan)
    cases = []
    for c in plan['cases']:
        name = c['name']
        runs = []
        for i, arm in enumerate(ARMS):
            job = ('factorial-v1', arm, plan['grouping']['policy'], plan['grouping']['seed'],
                   plan['k_policy']['validator'])
            def execute(arm=arm, name=name):
                return runner(rows[name], root=root, arm=arm, plan=plan)
            run = _read_or_run_checkpoint(output_dir, name, i, job, execute, resume=resume)
            if run.get('arm_id') != arm:
                raise ValueError('FACTORIAL: identidade de checkpoint incorreta')
            runs.append(run)
        item = {'name': name, 'runs': runs}
        verify_case(item, plan)
        item['contrasts'] = {key: _contrast(runs[ARMS.index(a)], runs[ARMS.index(b)])
                             for key, (a, b) in PAIRS.items()}
        cases.append(item)

    result = {'schema': RESULT_SCHEMA, 'classification': plan['classification'],
              'plan_sha256': sha256_file(plan_path), 'scientific_gate': 'PENDING',
              'scientific_promotion': 'NOT_AUTHORIZED', 'expected_arms': list(ARMS),
              'expected_cases': [c['name'] for c in plan['cases']], 'cases': cases,
              'limitations': ['Exploratório; não altera as campanhas AS05 e DIAG-v2',
                              'Resultados LP ótimos numéricos; sem certificado racional',
                              'Resultados censurados permanecem no denominador',
                              'A4 autorizada apenas neste experimento exploratório']}
    _write_json(output_dir/'report.json', result)
    (output_dir/'arms.csv').write_text(serialize_csv(csv_arm_rows(cases)), encoding='utf-8')
    paths = [output_dir/name for name in ('plan.json', 'report.json', 'arms.csv')]
    paths += sorted(p for p in (output_dir/'checkpoints').rglob('*') if p.is_file())
    _write_json(output_dir/'manifest.json', {'schema': MANIFEST_SCHEMA,
                'files': {p.relative_to(output_dir).as_posix(): sha256_file(p) for p in paths}})
    return output_dir/'report.json'


def verify_experiment(folder: Path) -> dict:
    planfile = folder/'plan.json'
    plan = json.loads(planfile.read_text(encoding='utf-8'))
    report = json.loads((folder/'report.json').read_text(encoding='utf-8'))
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if plan.get('schema') != SCHEMA or report.get('schema') != RESULT_SCHEMA:
        raise ValueError('FACTORIAL: schema inválido')
    if (report.get('plan_sha256') != sha256_file(planfile) or
        report.get('expected_cases') != [c['name'] for c in plan['cases']] or
        report.get('expected_arms') != list(ARMS) or
        report.get('scientific_gate') != 'PENDING' or
        report.get('scientific_promotion') != 'NOT_AUTHORIZED' or
        report.get('classification') != plan['classification']):
        raise ValueError('FACTORIAL: relatório divergente do plano')
    if len(report['cases']) != len(plan['cases']):
        raise ValueError('FACTORIAL: instâncias omitidas')
    if (folder/'arms.csv').read_text(encoding='utf-8') != serialize_csv(csv_arm_rows(report['cases'])):
        raise ValueError('FACTORIAL: arms.csv divergente dos resultados')
    expect = {'plan.json', 'report.json', 'arms.csv'}
    for c, pc in zip(report['cases'], plan['cases']):
        if c['name'] != pc['name']:
            raise ValueError('FACTORIAL: ordem/caso alterado')
        verify_case(c, plan)
        for run in c['runs']:
            if _is_opt(run) and run.get('instance_sha256') != pc['source_sha256']:
                raise ValueError('FACTORIAL: hash real não confere com instância pré-registrada')
            expected_k = plan['k_policy']['expected_previous_hashes'].get(c['name'])
            if expected_k and run.get('reference_k_sha256') and run['reference_k_sha256'] != expected_k:
                raise ValueError('FACTORIAL: K não corresponde à v2 registrada')
        run_items = c['runs']
        if c['contrasts'] != {key: _contrast(run_items[ARMS.index(a)], run_items[ARMS.index(b)])
                              for key, (a, b) in PAIRS.items()}:
            raise ValueError('FACTORIAL: contraste divergente das fontes')
        for i, arm in enumerate(ARMS):
            rel = _checkpoint_name(c['name'], i)
            check = folder/rel
            side = check.with_suffix('.sha256')
            expect.update((rel, side.relative_to(folder).as_posix()))
            if not check.is_file() or not side.is_file() or sha256_file(check) != side.read_text(encoding='ascii').strip():
                raise ValueError('FACTORIAL: checkpoint inválido')
            payload = json.loads(check.read_text(encoding='utf-8'))
            if (payload.get('result') != run_items[i] or payload.get('index') != i
                or payload.get('case') != c['name']
                or payload.get('job') != ['factorial-v1', arm, plan['grouping']['policy'],
                                        plan['grouping']['seed'], plan['k_policy']['validator']]):
                raise ValueError('FACTORIAL: resultado não confere com checkpoint')
    if manifest.get('schema') != MANIFEST_SCHEMA or set(manifest.get('files', {})) != expect:
        raise ValueError('FACTORIAL: manifesto incompleto')
    for rel, expected in manifest['files'].items():
        path = Path(rel)
        if path.is_absolute() or '..' in path.parts or not (folder/path).is_file() or sha256_file(folder/path) != expected:
            raise ValueError(f'FACTORIAL: SHA divergente: {rel}')
    return report


def analyze_experiment(folder: Path, outdir: Path) -> Path:
    report = verify_experiment(folder)
    if outdir.exists():
        raise FileExistsError('FACTORIAL: análise append-only')
    output = {'schema': ANALYSIS_SCHEMA, 'classification': report['classification'],
              'scientific_gate': 'PENDING', 'scientific_promotion': 'NOT_AUTHORIZED',
              'parent_report_sha256': sha256_file(folder/'report.json'),
              'expected_cases': report['expected_cases'],
              'effects': {}, 'cases': [], 'recommendation': None}
    for case in report['cases']:
        effect = case['contrasts']
        runs = case['runs']
        output['cases'].append({
            'name': case['name'],
            'status_by_arm': {r['arm_id']: r['status'] for r in runs},
            'lp_by_arm': {r['arm_id']: r.get('lp_opt_value') for r in runs},
            'n_variables_by_arm': {r['arm_id']: r.get('n_variables') for r in runs},
            'wall_s_by_arm': {r['arm_id']: r['wall_total_s'] for r in runs},
            'effects': effect,
            'interaction_refinement_k': (
                effect['REFINEMENT_WITH_K']['lp_delta'] - effect['GROUP_4_NO_K']['lp_delta']
                if (effect['REFINEMENT_WITH_K']['lp_delta'] is not None and
                    effect['GROUP_4_NO_K']['lp_delta'] is not None) else None)})
    for key in PAIRS:
        values = [c['effects'][key] for c in output['cases']]
        comp = [v for v in values if v['status'] == 'MATCHED_COMPLETE']
        output['effects'][key] = {'n_comparable': len(comp), 'n_total': len(values),
                                  'n_strict_gain': sum(v['lp_delta'] > 1e-6 for v in comp),
                                  'n_material_1pct': sum(v['relative_gain'] >= .01 for v in comp),
                                  'relative_gain_by_case': {
                                      c['name']: c['effects'][key]['relative_gain']
                                      for c in output['cases']}}
    if any(r['status'] != 'OPTIMAL_NUMERIC' for c in report['cases'] for r in c['runs']):
        recommendation = 'INVESTIGATE_CENSORED'
    elif output['effects']['REFINEMENT_WITH_K']['n_material_1pct'] or output['effects']['GROUP_4_NO_K']['n_material_1pct']:
        recommendation = 'PROMISING_EXPLORATORY_REPLICATION_REQUIRED'
    else:
        recommendation = 'NO_MATERIAL_REFINEMENT_IN_DEVELOPMENT'
    output['recommendation'] = recommendation
    output['limitations'] = ['Sem seleção/ajuste pós-hoc em casos de avaliação',
                             '1% apenas leitura descritiva, não gate científico GO',
                             'Nem todo braço tem solução se censurado; mantém N=6']
    outdir.mkdir(parents=True)
    _write_json(outdir/'analysis.json', output)
    rows = []
    for c in output['cases']:
        for arm, value in c['lp_by_arm'].items():
            rows.append({'case': c['name'], 'arm': arm,
                         'status': c['status_by_arm'][arm], 'lp': value,
                         'wall_s': c['wall_s_by_arm'][arm],
                         'n_variables': c['n_variables_by_arm'][arm]})
    with (outdir/'arms.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    effect_rows = []
    for case in output['cases']:
        for name, value in case['effects'].items():
            effect_rows.append({'case': case['name'], 'contrast': name,
                'status': value['status'], 'lp_delta': value['lp_delta'],
                'relative_gain': value['relative_gain'], 'wall_ratio': value['wall_ratio'],
                'solver_ratio': value['solver_ratio'],
                'interaction_refinement_k': case['interaction_refinement_k']})
    (outdir/'effects.csv').write_text(serialize_csv(effect_rows), encoding='utf-8')
    lines = ['# AS-05 — Comparação fatorial exploratória (A2/A4 × K)', '',
             '**Estado:** exploratório; sem revisão independente nem promoção automática.', '',
             f"**Interpretação:** `{recommendation}`", '',
             '| Instância | U | U+K | A2 | A2+K | A4 | A4+K |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for case in output['cases']:
        a = case['lp_by_arm']
        lines.append('| ' + case['name'] + ' | ' + ' | '.join(
            f'{a[key]:.6f}' if a[key] is not None else '—' for key in ARMS) + ' |')
    lines += ['', '## Efeitos e cobertura', '',
              '| Contraste | Comparáveis | Ganhos > 0,000001 | Ganhos ≥ 1% |',
              '|---|---:|---:|---:|']
    for effect, stats in output['effects'].items():
        lines.append(f"| {effect} | {stats['n_comparable']}/6 | {stats['n_strict_gain']} | {stats['n_material_1pct']} |")
    lines += ['', '## Interação entre cortes e refinamento', '',
              'Interação = [LP(A4+K) − LP(A2+K)] − [LP(A4) − LP(A2)].',
              'Pode ser positiva, zero ou negativa; não é um critério de promoção isolado.', '',
              '| Instância | Interação LP |', '|---|---:|']
    for case in output['cases']:
        d = case['interaction_refinement_k']
        lines.append(f"| {case['name']} | {d:.6f} |" if d is not None else
                     f"| {case['name']} | — |")
    lines += ['', '## Limitações', ''] + ['- ' + t for t in output['limitations']]
    (outdir/'analysis.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    _write_json(outdir/'manifest.json', {'schema': 'AS05-FACTORIAL-ANALYSIS-INTEGRITY-v1',
                'files': {name: sha256_file(outdir/name) for name in ('analysis.json', 'analysis.md', 'arms.csv', 'effects.csv')}})
    return outdir/'analysis.md'
