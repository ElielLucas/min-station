"""AS-05-DIAG: diagnóstico prospectivo pós-piloto, SEM reescrever AS-00/AS-05.

Separação explícita entre evidência exploratória de desenvolvimento e promoção
científica. Todos os solves usam compiladores AS-02 e supervisão FC-01.
"""
from __future__ import annotations

import csv
import hashlib
import json
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

from as02_model_a import Instance, compile_a  # noqa: E402
from as03_grouping import instance_fingerprint, partition_two  # noqa: E402
from as04_arms import canonical_k, compile_arm, k_digest  # noqa: E402
from as04_compare import assess_pair  # noqa: E402
from as04_runner import _load_timed, _optimize  # noqa: E402
from as04_schema import ArmResult, SolverPolicy, digest  # noqa: E402
from as05_protocol import read_plan, sha256_file  # noqa: E402
from as05_diag_cut_fast import ExactCutValidator  # noqa: E402
from fc_budget import run_bounded  # noqa: E402
from experiments.cuts.cuts import (  # noqa: E402
    assert_valid_cuts, build_neighborhoods, cortes_ordenados,
    generate_C1, generate_C2, generate_C4_DM,
)

DIAG_SCHEMA = 'AS05-DIAG-PLAN-v1'
RESULT_SCHEMA = 'AS05-DIAG-RESULT-v1'
POLICIES = ('reachability_degree', 'balanced', 'reachability_overlap')
STAGES = ('cuts', 'censored', 'grouping')
CENSORED_STATUS = {'TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER', 'TIMEOUT_VALIDATION',
                   'MEMORY_LIMIT', 'SOLVER_ERROR', 'WORKER_ERROR', 'NOT_BUILT_SIZE', 'NOT_AUTHORIZED'}


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


def _pilot_cases(root: Path, pilot_dir: Path) -> tuple[dict, dict]:
    from as05_pilot import verify_pilot

    report = verify_pilot(pilot_dir)
    plan, _ = read_plan(pilot_dir / 'plan.json', root)
    if report.get('execution_class') != 'OWNER_AUTHORIZED_EXPLORATORY':
        raise ValueError('DIAG: exige piloto exploratório anterior com integridade válida')
    if report.get('scientific_homologation') != 'PENDING':
        raise ValueError('DIAG: não deve reinterpretar gate científico')
    return plan, report


def make_diagnostic_plan(root: Path, pilot_dir: Path) -> dict:
    baseline, report = _pilot_cases(root, pilot_dir)
    all_cases = {item['name']: item for item in baseline['pilot_cases']}
    statuses = {item['name']: item['arm_statuses'] for item in report['cases']}
    if set(all_cases) != set(statuses) or len(all_cases) != 6:
        raise ValueError('DIAG: piloto original incompleto')
    censored = sorted(name for name, arms in statuses.items()
                      if any(arms.get(arm) != 'OPTIMAL_NUMERIC' for arm in ('U', 'U_K', 'A2_K')))
    completed = sorted(set(all_cases) - set(censored))
    if len(censored) != 2 or len(completed) != 4:
        raise ValueError('DIAG: seleção deve ser pré-registrada em novo protocolo, não inferida silenciosamente')
    return {
        'schema': DIAG_SCHEMA,
        'parent_pilot_dir': str(pilot_dir.relative_to(root)),
        'parent_pilot_manifest_sha256': sha256_file(pilot_dir / 'manifest.json'),
        'parent_pilot_report_sha256': sha256_file(pilot_dir / 'lp_gate.json'),
        'parent_plan_sha256': sha256_file(pilot_dir / 'plan.json'),
        'cases': {'cuts': censored, 'censored': censored, 'grouping': completed},
        'case_source_sha256': {name: all_cases[name]['source_sha256'] for name in sorted(all_cases)},
        'arms': {'censored': ['U', 'U_K', 'A2_K'],
                 'grouping': ['U_K'] + [f'A2_K@{p}' for p in POLICIES]},
        'policies': list(POLICIES),
        'grouping_seed': baseline['policy']['grouping_seed'],
        'solver': {'backend': 'gurobi', 'mode': 'LP', 'seed': baseline['policy']['seed'],
                   'threads': baseline['policy']['threads'],
                   'memory_limit_bytes': baseline['policy']['memory_limit_bytes'],
                   'warm_start': 'none'},
        'budgets_seconds_per_arm': {'cuts': 300, 'censored': 300,
                                    'grouping': baseline['policy']['wall_budget_s_per_arm']},
        'max_variables': 1_000_000,
        'classification': 'POSTHOC_DIAGNOSTIC_DEVELOPMENT_ONLY',
        'scientific_gate': 'PENDING',
        'preparation_policy': 'U_WITHOUT_K; EACH_PLUS_K_PREPARES_AND_VALIDATES_K_IN_OWN_BUDGET',
        'cut_validator_policy': 'PRECOMPUTED_NEIGHBORHOODS; SAME_GENERATORS_AS_AS02',
        'censored_preserved_in_parent': True,
        'hypotheses': [
            'Reusable N_plus/N_minus may reduce repetitive cut validation costs',
            'U prep should exclude unused K; compare end-to-end and solver-only separately',
            'A2 grouping policies may yield different LP bounds on development cases',
        ],
    }


def validate_diagnostic_plan(plan: dict, root: Path) -> dict:
    if plan.get('schema') != DIAG_SCHEMA:
        raise ValueError('DIAG: schema do plano inválido')
    parent = root / plan['parent_pilot_dir']
    expected = make_diagnostic_plan(root, parent)
    if plan != expected:
        raise ValueError('DIAG: plano não corresponde ao protocolo/relatório original; crie novo adendo')
    return plan


def _manifest_rows(root: Path, plan: dict) -> dict:
    import fc_instances

    rows = {x['nome']: x for x in fc_instances.load_manifest(root / 'instances/manifest.csv')}
    baseline, _ = read_plan(root / plan['parent_pilot_dir'] / 'plan.json', root)
    items = {}
    for case in baseline['pilot_cases']:
        if case['name'] not in plan['case_source_sha256']:
            raise ValueError('DIAG: caso inesperado')
        row = rows[case['manifest_name']]
        if row['sha256'] != plan['case_source_sha256'][case['name']]:
            raise ValueError('DIAG: SHA da instância diverge do pré-registro')
        items[case['name']] = row
    return items


def _timed_k(instance: Instance, loaded, ctx=None, *, validator_method: str = 'legacy') -> tuple[tuple, dict]:
    """Mesmo K= C1+C2+C4-DM que AS02; usa vizinhanças uma única vez.

    Nunca pula assert_valid_cuts. Métricas só são publicadas após conclusão
    do worker; tempo interrompido é contabilizado pelo supervisor em wall_phases.
    """
    times = {}
    counts = {}

    def phase(name, func):
        if ctx is not None:
            ctx.phase(f'k_{name}')
        start = time.monotonic()
        value = func()
        times[name + '_s'] = time.monotonic() - start
        return value

    plus, minus = phase('neighborhoods', lambda: build_neighborhoods(instance.A_r))
    c1 = phase('c1', lambda: generate_C1(instance.S, instance.T, plus, minus))
    c2 = phase('c2', lambda: generate_C2(instance.S, instance.T, loaded.adj, instance.r, instance.V))
    c4 = phase('c4_dm', lambda: generate_C4_DM(instance.S, instance.T, plus, minus))
    for name, cuts in (('c1', c1), ('c2', c2), ('c4_dm', c4)):
        counts[name + '_raw'] = len(cuts)
    cuts = phase('canonicalize', lambda: canonical_k(instance, cortes_ordenados(c1+c2+c4)))
    counts['unique'] = len(cuts)
    if validator_method == 'legacy':
        phase('validation_cached', lambda: assert_valid_cuts(
            instance.S, instance.T, instance.A_r, cuts, origem='AS05-DIAG',
            N_plus=plus, N_minus=minus))
    elif validator_method == 'bitset-v2':
        validator = phase('validator_setup', lambda: ExactCutValidator(
            instance.S, instance.T, instance.A_r, N_plus=plus, N_minus=minus))
        phase('validation_bitset_v2', lambda: validator.check_all(
            cuts, origem='AS05-DIAG-V2', audit_legacy_up_to=1))
    else:
        raise ValueError('DIAG: método de validação K não reconhecido')
    # Não confundir o tempo de validação com solução do modelo.
    return cuts, {'phase_wall_s': times, 'counts': counts,
                  'k_sha256': k_digest(instance, cuts), 'k_validated': True,
                  'validator_method': validator_method}


def _overlap_partition(instance: Instance, seed: int) -> tuple[tuple[str, ...], ...]:
    """Duas comunidades equilibradas via similaridade Jaccard das vizinhanças.

    Escolha pré-determinada, usa apenas A_r; nunca observa objetivo/solver.
    Versão separada da AS-03 normativa. Custos O(|A_r|+|S|² d).
    """
    S = tuple(sorted(instance.S))
    if len(S) < 2:
        raise ValueError('Agrupamento A2 inaplicável para |S|<2')
    signature = {s: set() for s in S}
    for u, v in instance.A_r:
        if u in signature:
            signature[u].add(v)

    def similarity(a, b):
        inter = len(signature[a] & signature[b])
        union = len(signature[a] | signature[b])
        return inter / union if union else 1.0

    anchor = sorted(S, key=lambda v: (-len(signature[v]), v))[0]
    far = sorted((v for v in S if v != anchor), key=lambda v: (similarity(anchor, v), v))[0]
    ordering = sorted(S, key=lambda v: (
        -(similarity(v, anchor)-similarity(v, far)),
        hashlib.sha256(f'{seed}:{v}'.encode()).hexdigest(), v))
    split = (len(S)+1)//2
    blocks = (tuple(sorted(ordering[:split])), tuple(sorted(ordering[split:])))
    return tuple(sorted(blocks))


def grouping_blocks(instance: Instance, policy: str, seed: int):
    if policy not in POLICIES or type(seed) is not int or seed < 0:
        raise ValueError('DIAG: política/seed não pré-registradas')
    if policy != 'reachability_overlap':
        group = partition_two(instance, policy, seed)
        return group.blocks, group.partition_hash
    blocks = _overlap_partition(instance, seed)
    fingerprint = instance_fingerprint(instance)
    identity = digest({'version': 'AS05-DIAG-OVERLAP-v1', 'instance_sha256': fingerprint,
                       'blocks': blocks, 'policy': policy, 'seed': seed})
    return blocks, identity


def _diag_worker(ctx, row, root: str, kind: str, arm: str | None, group_policy: str | None,
                 solver: dict, budget: float, max_variables: int, grouping_seed: int,
                 validator_method: str = 'legacy'):
    if solver['memory_limit_bytes'] is not None:
        resource.setrlimit(resource.RLIMIT_AS,
                           (solver['memory_limit_bytes'], solver['memory_limit_bytes']))
    ctx.phase('preparation')
    loaded, input_wall, reach_wall = _load_timed(row, root)
    if int(loaded.r) != loaded.r:
        raise ValueError('DIAG: autonomia não inteira')
    instance = Instance(tuple(loaded.V), tuple(loaded.S), tuple(loaded.T),
                        tuple(loaded.A_r), int(loaded.r))
    base = {'instance_sha256': loaded.instance_sha256,
            'structural_sha256': instance_fingerprint(instance),
            'input_load_s': input_wall, 'reachability_s': reach_wall}
    if kind == 'cuts':
        ctx.phase('k_preparation')
        _, metrics = _timed_k(instance, loaded, ctx, validator_method=validator_method)
        return {'status': 'PROFILED', **base, 'cut_profile': metrics}

    if arm not in ('U', 'U_K', 'A2_K'):
        raise ValueError('DIAG: braço não autorizado')
    if arm == 'A2_K' and group_policy not in POLICIES:
        raise ValueError('DIAG: política não autorizada')
    cut_profile = None
    if arm == 'U':
        # NÃO atribuir ao controle U o custo de um K que não utiliza.
        K, khash = (), None
    else:
        ctx.phase('k_preparation')
        K, cut_profile = _timed_k(instance, loaded, ctx, validator_method=validator_method)
        khash = k_digest(instance, K)
    ctx.phase('model_build')
    if arm in ('U', 'U_K'):
        estimate = len(instance.V) + len(instance.A_r)
    else:
        estimate = len(instance.V) + 2 * (len(instance.A_r)+len(instance.V)+len(instance.S))
    if estimate > max_variables:
        return {'status': 'NOT_BUILT_SIZE', 'reason': f'Estimativa {estimate} > {max_variables}',
                **base, 'reference_k_sha256': khash,
                'applied_k_sha256': khash if arm != 'U' else None,
                'k_validated': arm != 'U', 'model_complete': False,
                'cut_profile': cut_profile, 'k_prepared_for_this_arm': arm != 'U'}
    if arm == 'A2_K' and group_policy == 'reachability_overlap':
        blocks, partition_sha = grouping_blocks(instance, group_policy, grouping_seed)
        compiled = compile_a(instance, blocks, K=K, relax=True)
    else:
        compiled, partition_sha = compile_arm(arm, instance, K, mode='LP',
                                               grouping_policy=group_policy or 'reachability_degree',
                                               seed=grouping_seed)
    if len(compiled.variables) > max_variables:
        return {'status': 'NOT_BUILT_SIZE', 'reason': 'Cap de variáveis reais excedido',
                **base, 'reference_k_sha256': khash,
                'applied_k_sha256': khash if arm != 'U' else None,
                'k_validated': arm != 'U', 'model_complete': False,
                'cut_profile': cut_profile, 'k_prepared_for_this_arm': arm != 'U'}
    pol = SolverPolicy(seed=solver['seed'], threads=solver['threads'], budget_s=budget,
                       memory_limit_bytes=solver['memory_limit_bytes'])
    try:
        solved = _optimize(compiled, 'LP', pol, ctx)
    except (ImportError, ModuleNotFoundError) as exc:
        solved = {'status': 'SOLVER_ERROR', 'reason': f'{type(exc).__name__}: {exc}',
                  'n_variables': len(compiled.variables),
                  'n_constraints': len(compiled.equations),
                  'n_nonzeros': compiled.n_nonzeros, 'model_complete': False}
    return {**base, **solved, 'reference_k_sha256': khash,
            'applied_k_sha256': khash if arm != 'U' else None,
            'k_validated': arm != 'U',
            'model_complete': solved.get('model_complete', solved['status'] != 'SOLVER_ERROR'),
            'partition_sha256': partition_sha, 'cut_profile': cut_profile,
            'k_prepared_for_this_arm': arm != 'U'}


def _run_one(row: dict, *, root: Path, kind: str, solver: dict,
             budget: float, max_variables: int, grouping_seed: int,
             arm: str | None = None, group_policy: str | None = None,
             validator_method: str = 'legacy') -> dict:
    raw = run_bounded(_diag_worker, row, str(root), kind, arm, group_policy,
                      solver, budget, max_variables, grouping_seed, validator_method, budget_s=budget)
    basis = {'case_name': row['nome'], 'kind': kind, 'arm_id': arm,
             'grouping_policy': group_policy, 'wall_total_s': raw.wall_total_s,
             'wall_phases_s': dict(raw.phase_wall_s), 'reason': raw.reason}
    if raw.status == 'COMPLETED':
        return {**basis, **raw.value}
    status = raw.status if raw.status in CENSORED_STATUS else 'SOLVER_ERROR'
    return {**basis, 'status': status, 'reason': raw.reason,
            'lp_opt_value': None, 'model_complete': False}


def _arm_result(raw: dict, pol: SolverPolicy, *, ref: str | None) -> ArmResult:
    arm = raw['arm_id']
    complete = bool(raw.get('model_complete', False))
    # Referência K de U é incorporada da execução U_K correspondente, sem
    # atribuir a U tempo de construção/validação de K.
    khash = ref if arm == 'U' else raw.get('reference_k_sha256')
    return ArmResult(case_name=raw['case_name'], arm_id=arm, mode='LP',
                     status=raw['status'], reason=raw.get('reason', ''),
                     instance_sha256=raw.get('instance_sha256'),
                     structural_sha256=raw.get('structural_sha256'),
                     reference_k_sha256=khash,
                     applied_k_sha256=None if arm == 'U' else raw.get('applied_k_sha256'),
                     k_validated=bool(ref) if arm == 'U' else bool(raw.get('k_validated', False)),
                     solver_policy_sha256=pol.sha256, solver_policy=asdict(pol),
                     model_complete=complete,
                     wall_total_s=raw['wall_total_s'], wall_phases_s=raw['wall_phases_s'],
                     solver_version=raw.get('solver_version'),
                     input_load_s=raw.get('input_load_s'),
                     reachability_s=raw.get('reachability_s'),
                     solver_runtime_s=raw.get('solver_runtime_s'),
                     solver_work=raw.get('solver_work'), nodes=raw.get('nodes'),
                     n_variables=raw.get('n_variables'),
                     n_constraints=raw.get('n_constraints'), n_nonzeros=raw.get('n_nonzeros'),
                     partition_sha256=raw.get('partition_sha256'),
                     lp_opt_value=raw.get('lp_opt_value'))


def _contrast(left: dict, right: dict, policy: SolverPolicy, *, effect: str) -> dict:
    ref = left.get('reference_k_sha256') or right.get('reference_k_sha256')
    if effect == 'K_EFFECT' and left['arm_id'] == 'U':
        # U não consumiu K; sua referência é proveniência do braço U_K.
        left = {**left, 'reference_k_sha256': ref}
    if not ref:
        return {'status': 'NOT_COMPARABLE', 'reason': 'K de referência ausente',
                'lp_delta': None, 'relative_gain': None, 'wall_ratio': None,
                'solver_runtime_ratio': None}
    a, b = _arm_result(left, policy, ref=ref), _arm_result(right, policy, ref=ref)
    pair = assess_pair(a, b, effect=effect)
    za, zb = a.lp_opt_value, b.lp_opt_value
    if pair.status != 'MATCHED_COMPLETE' or za is None or zb is None:
        return {'status': pair.status, 'reason': pair.reason, 'lp_delta': None,
                'relative_gain': None, 'wall_ratio': None, 'solver_runtime_ratio': None}
    return {'status': pair.status, 'reason': pair.reason,
            'lp_delta': zb-za, 'relative_gain': (zb-za)/max(abs(za), 1),
            'wall_ratio': b.wall_total_s/a.wall_total_s if a.wall_total_s else None,
            'solver_runtime_ratio': (b.solver_runtime_s/a.solver_runtime_s
                                     if a.solver_runtime_s and b.solver_runtime_s else None)}


def _verify_model_identity(rows: list[dict]) -> None:
    valid = [row for row in rows if row.get('model_complete')]
    for key in ('instance_sha256', 'structural_sha256'):
        values = {row.get(key) for row in valid}
        if None in values or len(values) > 1:
            raise ValueError(f'DIAG: divergência entre braços em {key}')
    khashes = {row.get('reference_k_sha256') for row in valid if row['arm_id'] != 'U'}
    if None in khashes or len(khashes) > 1:
        raise ValueError('DIAG: divergência ou ausência K entre braços +K')


def _checkpoint_name(case: str, index: int) -> str:
    if not case or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in case):
        raise ValueError('DIAG: nome de caso inseguro para checkpoint')
    return f'checkpoints/{case}/arm-{index:02d}.json'


def _read_or_run_checkpoint(folder: Path, case: str, index: int, job: tuple,
                            execute, *, resume: bool) -> dict:
    """Checkpoint por braço + SHA sidecar: retomada somente íntegra.

    O payload é assinado pelo hash dos próprios bytes; não é uma assinatura
    criptográfica externa, portanto não atesta honestidade do executor.
    """
    relative = _checkpoint_name(case, index)
    path = folder / relative
    digest_path = path.with_suffix('.sha256')
    if path.exists() or digest_path.exists():
        if not resume or not path.is_file() or not digest_path.is_file():
            raise ValueError(f'DIAG: checkpoint parcial/inesperado: {relative}')
        if sha256_file(path) != digest_path.read_text(encoding='ascii').strip():
            raise ValueError(f'DIAG: checkpoint adulterado: {relative}')
        payload = json.loads(path.read_text(encoding='utf-8'))
        if (payload.get('case') != case or payload.get('index') != index
                or payload.get('job') != list(job)):
            raise ValueError('DIAG: checkpoint não pertence ao plano/slot')
        return payload['result']
    if resume and folder.joinpath('report.json').exists():
        raise ValueError('DIAG: relatório final já publicado; não completar parcialmente')
    value = execute()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    _write_json(temp, {'case': case, 'index': index, 'job': list(job), 'result': value})
    temp.replace(path)
    digest_path.write_text(sha256_file(path) + '\n', encoding='ascii')
    return value


def run_diagnostic_stage(*, root: Path, plan_path: Path, stage: str,
                         output_dir: Path, run_one=_run_one, resume: bool = False) -> Path:
    if stage not in STAGES:
        raise ValueError('DIAG: etapa inválida')
    plan = validate_diagnostic_plan(json.loads(plan_path.read_text(encoding='utf-8')), root)
    if output_dir.exists():
        if not resume or (output_dir/'report.json').exists():
            raise FileExistsError('DIAG: resultado final existe ou retomada sem --resume')
        if not (output_dir/'plan.json').is_file() or sha256_file(output_dir/'plan.json') != sha256_file(plan_path):
            raise ValueError('DIAG: plano do checkpoint difere do plano congelado')
    else:
        if resume:
            raise FileNotFoundError('DIAG: --resume requer saída parcial existente')
        output_dir.mkdir(parents=True, exist_ok=False)
        (output_dir/'plan.json').write_bytes(plan_path.read_bytes())
    rows = _manifest_rows(root, plan)
    solver = dict(plan['solver'])
    policy = SolverPolicy(seed=solver['seed'], threads=solver['threads'],
                          budget_s=plan['budgets_seconds_per_arm'][stage],
                          memory_limit_bytes=solver['memory_limit_bytes'])
    collected = []
    summary = []
    for name in plan['cases'][stage]:
        row = rows[name]
        if stage == 'cuts':
            jobs = [(None, None)]
        elif stage == 'censored':
            jobs = [(arm, None) for arm in ('U', 'U_K', 'A2_K')]
        else:
            jobs = [('U_K', None)] + [('A2_K', group) for group in plan['policies']]
        runs = []
        for idx, (arm, group) in enumerate(jobs):
            def execute(arm=arm, group=group):
                return run_one(row, root=root, kind='cuts' if stage == 'cuts' else 'lp',
                               arm=arm, group_policy=group, solver=solver,
                               budget=policy.budget_s, max_variables=plan['max_variables'],
                               grouping_seed=plan['grouping_seed'])
            runs.append(_read_or_run_checkpoint(output_dir, name, idx,
                                                (stage, arm, group), execute, resume=resume))
        if stage == 'cuts':
            contrasts = {}
        else:
            _verify_model_identity(runs)
            if stage == 'censored':
                contrasts = {'K_EFFECT': _contrast(runs[0], runs[1], policy, effect='K_EFFECT'),
                             'A_EFFECT': _contrast(runs[1], runs[2], policy, effect='A_EFFECT')}
            else:
                contrasts = {group: _contrast(runs[0], run, policy, effect='A_EFFECT')
                             for group, run in zip(plan['policies'], runs[1:])}
        collected.append({'name': name, 'runs': runs, 'contrasts': contrasts})
        for run in runs:
            summary.append({'case_name': name, 'arm': run.get('arm_id'),
                            'grouping_policy': run.get('grouping_policy'),
                            'status': run['status'], 'lp_opt_value': run.get('lp_opt_value'),
                            'wall_total_s': run.get('wall_total_s'),
                            'solver_runtime_s': run.get('solver_runtime_s'),
                            'k_prep_s': sum(value for key, value in run.get('wall_phases_s', {}).items()
                                            if key.startswith('k_')),
                            'k_sha256': run.get('reference_k_sha256'),
                            'partition_sha256': run.get('partition_sha256'),
                            'n_variables': run.get('n_variables')})
    report = {'schema': RESULT_SCHEMA, 'stage': stage,
              'classification': plan['classification'],
              'scientific_gate': 'PENDING', 'scientific_promotion': 'NOT_AUTHORIZED',
              'plan_sha256': sha256_file(plan_path),
              'parent_report_sha256': plan['parent_pilot_report_sha256'],
              'expected_cases': list(plan['cases'][stage]),
              'cases': collected,
              'diagnostic_only': True,
              'limitations': ['Não altera o denominador ou gate da AS05 original',
                              'Resultados LP numéricos não são certificados racionais',
                              'Tempos end-to-end incluem spawn e validação por braço',
                              'Política overlap é nova e exploratória'],
              'schema_version': 1}
    report_path = output_dir / 'report.json'
    _write_json(report_path, report)
    with (output_dir / 'arms.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]) if summary else
                                ['case_name', 'arm', 'grouping_policy', 'status'])
        writer.writeheader()
        writer.writerows(summary)
    artifacts = [output_dir / 'report.json', output_dir / 'plan.json', output_dir / 'arms.csv']
    artifacts.extend(p for p in sorted((output_dir/'checkpoints').rglob('*')) if p.is_file())
    inventory = {p.relative_to(output_dir).as_posix(): sha256_file(p) for p in artifacts}
    _write_json(output_dir / 'manifest.json', {'schema': 'AS05-DIAG-INTEGRITY-v1',
                                               'files': inventory})
    return report_path

def verify_diagnostic_stage(folder: Path) -> dict:
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 'AS05-DIAG-INTEGRITY-v1':
        raise ValueError('DIAG: manifesto inválido')
    report = json.loads((folder / 'report.json').read_text(encoding='utf-8'))
    plan = json.loads((folder / 'plan.json').read_text(encoding='utf-8'))
    stage = report.get('stage')
    if stage not in STAGES or plan.get('schema') != DIAG_SCHEMA:
        raise ValueError('DIAG: estágio/plano não reconhecidos')
    if (report.get('scientific_gate') != 'PENDING'
            or report.get('scientific_promotion') != 'NOT_AUTHORIZED'
            or report.get('classification') != plan.get('classification')):
        raise ValueError('DIAG: promoção científica indevida')
    if (sha256_file(folder / 'plan.json') != report.get('plan_sha256')
            or report.get('parent_report_sha256') != plan.get('parent_pilot_report_sha256')):
        raise ValueError('DIAG: plano ou origem alterados após execução')
    expected_cases = plan['cases'][stage]
    if (report.get('expected_cases') != expected_cases
            or [x.get('name') for x in report.get('cases', [])] != expected_cases):
        raise ValueError('DIAG: casos censurados/ausentes foram descartados')
    expected_files = {'plan.json', 'report.json', 'arms.csv'}
    for case in report['cases']:
        name = case['name']
        expected_jobs = ([(None, None)] if stage == 'cuts' else
                         [(x, None) for x in ('U', 'U_K', 'A2_K')] if stage == 'censored' else
                         [('U_K', None)] + [('A2_K', x) for x in plan['policies']])
        if len(case.get('runs', [])) != len(expected_jobs):
            raise ValueError('DIAG: quantidade de braços divergente')
        for index, (arm, grouping) in enumerate(expected_jobs):
            relative = _checkpoint_name(name, index)
            checkpoint = folder / relative
            suffix = checkpoint.with_suffix('.sha256')
            relative_sha = suffix.relative_to(folder).as_posix()
            expected_files.update((relative, relative_sha))
            if not checkpoint.is_file() or not suffix.is_file():
                raise ValueError(f'DIAG: checkpoint ausente: {relative}')
            if sha256_file(checkpoint) != suffix.read_text(encoding='ascii').strip():
                raise ValueError(f'DIAG: SHA de checkpoint inválido: {relative}')
            payload = json.loads(checkpoint.read_text(encoding='utf-8'))
            if (payload.get('case') != name or payload.get('index') != index
                    or payload.get('job') != [stage, arm, grouping]
                    or payload.get('result') != case['runs'][index]):
                raise ValueError(f'DIAG: relatório diverge do checkpoint: {relative}')
    if set(manifest.get('files', {})) != expected_files:
        raise ValueError('DIAG: manifesto omitiu/adicionou artefatos')
    for name, digest_expected in manifest['files'].items():
        file_path = Path(name)
        if file_path.is_absolute() or '..' in file_path.parts or not (folder / name).is_file():
            raise ValueError(f'DIAG: caminho de artefato inválido: {name}')
        if sha256_file(folder / name) != digest_expected:
            raise ValueError(f'DIAG: hash divergente em {name}')
    return report
