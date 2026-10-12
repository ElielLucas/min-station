"""AS05 diagnóstico v2: reensaio versionado, exato, isolado da campanha v1.

O pré-registro do estudo v1, seus relatórios e o gate científico são imutáveis.
A2+K usa explicitamente reachability_degree/seed 42; K usa verificação
bitset-v2 integral com comparação legada de sentinela.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from as04_schema import SolverPolicy, digest
from as05_diag_core import (
    _checkpoint_name, _contrast, _manifest_rows, _read_or_run_checkpoint,
    _run_one, _verify_model_identity, _write_json, validate_diagnostic_plan,
    verify_diagnostic_stage,
)
from as05_protocol import sha256_file

RETEST_SCHEMA = 'AS05-DIAG-RETEST-PLAN-v2'
RESULT_SCHEMA = 'AS05-DIAG-RETEST-RESULT-v2'
MANIFEST_SCHEMA = 'AS05-DIAG-RETEST-INTEGRITY-v2'
ANALYSIS_SCHEMA = 'AS05-DIAG-RETEST-ANALYSIS-v2'
STAGES = ('cuts', 'censored')
K_VALIDATOR = 'bitset-v2'
A2_POLICY = 'reachability_degree'
VIENNA_K_SHA256 = '64d3500a49c52bbf3ea9a3ffd718711c2e6a809585d7f91db311ef44a3606796'
W3C_K_SHA256 = '42b9f6336b56241a1318326d5df68d04ec1f1c8a427b74b7462eea116766e23f'
PRIOR_PLAN = 'results/benchmark/as05-diagnostic-plan-v1.json'
PRIOR_CUTS = 'results/benchmark/as05-diagnostic-001/cuts'
PRIOR_CENSORED = 'results/benchmark/as05-diagnostic-001/censored'
PRIOR_GROUPING = 'results/benchmark/as05-diagnostic-001/grouping'


def make_retest_plan(root: Path) -> dict:
    """Plano v2 é função determinística do plano e das observações v1, sem solves."""
    root = root.resolve()
    prior_file = root / PRIOR_PLAN
    prior = validate_diagnostic_plan(json.loads(prior_file.read_text(encoding='utf-8')), root)
    prior_stages = {}
    for stage, location in (('cuts', PRIOR_CUTS), ('censored', PRIOR_CENSORED),
                            ('grouping', PRIOR_GROUPING)):
        directory = root / location
        report = verify_diagnostic_stage(directory)
        if report['stage'] != stage or report['plan_sha256'] != sha256_file(prior_file):
            raise ValueError(f'RETEST-V2: {stage} não corresponde ao plano v1')
        prior_stages[stage] = sha256_file(directory / 'manifest.json')
    censored = list(prior['cases']['censored'])
    if censored != ['puc-w3c571-seed-r1', 'vienna-I056-regiao-f4']:
        raise ValueError('RETEST-V2: conjunto de censurados inesperado')
    # A política não é escolhida por resultado; é a política normativa da AS-03.
    return {
        'schema': RETEST_SCHEMA,
        'parent_plan_path': PRIOR_PLAN,
        'parent_plan_sha256': sha256_file(prior_file),
        'parent_stage_manifest_sha256': prior_stages,
        'original_pilot_report_sha256': prior['parent_pilot_report_sha256'],
        'case_source_sha256': {key: prior['case_source_sha256'][key] for key in censored},
        'cases': {'cuts': censored, 'censored': censored},
        'arms': {'censored': [
            {'arm': 'U', 'grouping_policy': None},
            {'arm': 'U_K', 'grouping_policy': None},
            {'arm': 'A2_K', 'grouping_policy': A2_POLICY},
        ]},
        'K_validator': K_VALIDATOR,
        'K_validator_legacy_spot_check': 1,
        'expected_k_sha256': {'puc-w3c571-seed-r1': W3C_K_SHA256,
                              'vienna-I056-regiao-f4': VIENNA_K_SHA256},
        'k_hash_provenance': {'puc-w3c571-seed-r1': 'v2-no-solver-preflight',
                              'vienna-I056-regiao-f4': 'v1-completed-profile'},
        'grouping_seed': prior['grouping_seed'],
        'solver': dict(prior['solver']),
        'budgets_seconds_per_arm': {'cuts': prior['budgets_seconds_per_arm']['cuts'],
                                    'censored': prior['budgets_seconds_per_arm']['censored']},
        'max_variables': prior['max_variables'],
        'classification': 'EXPLORATORY_POSTHOC_RETEST_V2',
        'scientific_gate': 'PENDING',
        'scientific_promotion': 'NOT_AUTHORIZED',
        'changes_from_v1': [
            'A2_K explicit AS03 reachability_degree policy, seed unchanged',
            'Same generators K, exact dual-reachability and full matching validator',
            'Independent frozen outputs, original LP and grouping results untouched',
        ],
    }


def validate_retest_plan(plan: dict, root: Path) -> dict:
    if plan.get('schema') != RETEST_SCHEMA or plan != make_retest_plan(root):
        raise ValueError('RETEST-V2: plano inválido ou diferente das evidências de origem')
    return plan


def _jobs(stage: str, plan: dict):
    return ([(None, None)] if stage == 'cuts' else
            [(x['arm'], x['grouping_policy']) for x in plan['arms']['censored']])


def _verify_k_prior(case_name: str, run: dict, plan: dict) -> None:
    expected = plan['expected_k_sha256'].get(case_name)
    if not expected or run.get('status') not in ('PROFILED', 'OPTIMAL_NUMERIC'):
        return
    actual = (run.get('cut_profile') or {}).get('k_sha256')
    if actual is not None and actual != expected:
        raise ValueError(f'RETEST-V2: K divergente do hash pré-fixado em {case_name}')


def run_retest_stage(*, root: Path, plan_path: Path, stage: str, output_dir: Path,
                     run_one=_run_one, resume: bool = False) -> Path:
    root = root.resolve()
    if stage not in STAGES:
        raise ValueError('RETEST-V2: etapa desconhecida')
    plan = validate_retest_plan(json.loads(plan_path.read_text(encoding='utf-8')), root)
    if output_dir.exists():
        if not resume or (output_dir/'report.json').exists():
            raise FileExistsError('RETEST-V2: não sobrescrever relatório existente')
        if not (output_dir/'plan.json').is_file() or sha256_file(output_dir/'plan.json') != sha256_file(plan_path):
            raise ValueError('RETEST-V2: checkpoint não corresponde ao plano')
    else:
        if resume:
            raise FileNotFoundError('RETEST-V2: --resume requer diretório parcial')
        output_dir.mkdir(parents=True)
        (output_dir/'plan.json').write_bytes(plan_path.read_bytes())
    prior = validate_diagnostic_plan(json.loads((root / PRIOR_PLAN).read_text(encoding='utf-8')), root)
    rows = _manifest_rows(root, prior)
    solver = plan['solver']
    policy = SolverPolicy(seed=solver['seed'], threads=solver['threads'],
                          budget_s=plan['budgets_seconds_per_arm'][stage],
                          memory_limit_bytes=solver['memory_limit_bytes'])
    cases = []
    summary = []
    for name in plan['cases'][stage]:
        runs = []
        for index, (arm, grouping) in enumerate(_jobs(stage, plan)):
            job = ('retest-v2', stage, arm, grouping, plan['K_validator'])

            def execute(arm=arm, grouping=grouping):
                return run_one(rows[name], root=root,
                               kind='cuts' if stage == 'cuts' else 'lp',
                               arm=arm, group_policy=grouping,
                               solver=solver, budget=policy.budget_s,
                               max_variables=plan['max_variables'],
                               grouping_seed=plan['grouping_seed'],
                               validator_method=plan['K_validator'])

            run = _read_or_run_checkpoint(output_dir, name, index, job, execute, resume=resume)
            if run.get('arm_id') != arm or run.get('grouping_policy') != grouping:
                raise ValueError('RETEST-V2: braço/política não corresponde ao checkpoint')
            _verify_k_prior(name, run, plan)
            runs.append(run)
        if stage == 'cuts':
            contrasts = {}
        else:
            _verify_model_identity(runs)
            contrasts = {
                'K_EFFECT': _contrast(runs[0], runs[1], policy, effect='K_EFFECT'),
                'A_EFFECT': _contrast(runs[1], runs[2], policy, effect='A_EFFECT'),
            }
        cases.append({'name': name, 'runs': runs, 'contrasts': contrasts})
        for run in runs:
            summary.append({
                'case_name': name, 'arm': run.get('arm_id'),
                'grouping_policy': run.get('grouping_policy'),
                'status': run['status'], 'reason': run.get('reason', ''),
                'lp_opt_value': run.get('lp_opt_value'),
                'wall_total_s': run.get('wall_total_s'),
                'solver_runtime_s': run.get('solver_runtime_s'),
                'k_sha256': run.get('reference_k_sha256') or (run.get('cut_profile') or {}).get('k_sha256'),
                'k_validation_s': (run.get('cut_profile') or {}).get('phase_wall_s', {}).get('validation_bitset_v2_s'),
                'partition_sha256': run.get('partition_sha256'),
            })
    report = {
        'schema': RESULT_SCHEMA, 'stage': stage,
        'plan_sha256': sha256_file(plan_path),
        'parent_plan_sha256': plan['parent_plan_sha256'],
        'parent_original_report_sha256': plan['original_pilot_report_sha256'],
        'expected_cases': plan['cases'][stage], 'cases': cases,
        'validator': K_VALIDATOR, 'a2_policy': A2_POLICY,
        'classification': plan['classification'], 'scientific_gate': 'PENDING',
        'scientific_promotion': 'NOT_AUTHORIZED',
        'limitations': ['Reensaio exploratório não substitui gate AS05',
                        'Validação K exata não equivale a homologação independente',
                        'Braços interrompidos permanecem censurados'],
    }
    _write_json(output_dir/'report.json', report)
    with (output_dir/'arms.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    paths = [output_dir/p for p in ('plan.json', 'report.json', 'arms.csv')]
    paths += [p for p in sorted((output_dir/'checkpoints').rglob('*')) if p.is_file()]
    _write_json(output_dir/'manifest.json', {'schema': MANIFEST_SCHEMA,
                                              'files': {p.relative_to(output_dir).as_posix(): sha256_file(p)
                                                        for p in paths}})
    return output_dir/'report.json'


def verify_retest_stage(folder: Path) -> dict:
    plan = json.loads((folder/'plan.json').read_text(encoding='utf-8'))
    report = json.loads((folder/'report.json').read_text(encoding='utf-8'))
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    stage = report.get('stage')
    if stage not in STAGES or plan.get('schema') != RETEST_SCHEMA or report.get('schema') != RESULT_SCHEMA:
        raise ValueError('RETEST-V2: schema inesperado')
    if (report.get('scientific_gate') != 'PENDING' or report.get('scientific_promotion') != 'NOT_AUTHORIZED'
            or report.get('classification') != plan.get('classification')
            or report.get('validator') != plan.get('K_validator')
            or report.get('a2_policy') != A2_POLICY):
        raise ValueError('RETEST-V2: tentativa de promoção científica')
    if (report.get('plan_sha256') != sha256_file(folder/'plan.json')
            or report.get('parent_plan_sha256') != plan['parent_plan_sha256']
            or report.get('parent_original_report_sha256') != plan['original_pilot_report_sha256']):
        raise ValueError('RETEST-V2: proveniência inválida')
    if (report.get('expected_cases') != plan['cases'][stage]
            or [case['name'] for case in report['cases']] != plan['cases'][stage]):
        raise ValueError('RETEST-V2: instâncias omitidas/adicionadas')
    expected_paths = {'plan.json', 'report.json', 'arms.csv'}
    for case in report['cases']:
        if len(case.get('runs', [])) != len(_jobs(stage, plan)):
            raise ValueError('RETEST-V2: braços ausentes')
        for index, (arm, grouping) in enumerate(_jobs(stage, plan)):
            rel = _checkpoint_name(case['name'], index)
            checkpoint = folder/rel
            sidecar = checkpoint.with_suffix('.sha256')
            expected_paths.update({rel, sidecar.relative_to(folder).as_posix()})
            if not checkpoint.is_file() or not sidecar.is_file() or sha256_file(checkpoint) != sidecar.read_text(encoding='ascii').strip():
                raise ValueError('RETEST-V2: checkpoint corrompido/ausente')
            payload = json.loads(checkpoint.read_text(encoding='utf-8'))
            expected_job = ['retest-v2', stage, arm, grouping, plan['K_validator']]
            if (payload.get('case') != case['name'] or payload.get('index') != index
                    or payload.get('job') != expected_job or payload.get('result') != case['runs'][index]
                    or case['runs'][index].get('arm_id') != arm
                    or case['runs'][index].get('grouping_policy') != grouping):
                raise ValueError('RETEST-V2: checkpoint diverge de braço/política/relatório')
            _verify_k_prior(case['name'], case['runs'][index], plan)
    if manifest.get('schema') != MANIFEST_SCHEMA or set(manifest.get('files', {})) != expected_paths:
        raise ValueError('RETEST-V2: manifesto incompleto/inesperado')
    for name, expected in manifest['files'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or not (folder/path).is_file() or sha256_file(folder/path) != expected:
            raise ValueError(f'RETEST-V2: integridade divergente: {name}')
    return report


def analyze_retest(*, root: Path, plan_path: Path, results_dir: Path,
                   output_dir: Path) -> Path:
    """Duas etapas v2 + agrupamento v1. Não inventa resultados ausentes."""
    plan = validate_retest_plan(json.loads(plan_path.read_text(encoding='utf-8')), root)
    if output_dir.exists():
        raise FileExistsError('RETEST-V2: análise append-only')
    reports = {}
    for stage in STAGES:
        reports[stage] = verify_retest_stage(results_dir/stage)
        if reports[stage]['plan_sha256'] != sha256_file(plan_path):
            raise ValueError('RETEST-V2: os relatórios não utilizam o plano fornecido')
    prior_grouping = verify_diagnostic_stage(root / PRIOR_GROUPING)
    if sha256_file(root/PRIOR_GROUPING/'manifest.json') != plan['parent_stage_manifest_sha256']['grouping']:
        raise ValueError('RETEST-V2: agrupamento v1 divergente')
    cuts = []
    retries = []
    for item in reports['cuts']['cases']:
        run = item['runs'][0]
        cuts.append({'case': item['name'], 'status': run['status'],
                     'K_sha256': (run.get('cut_profile') or {}).get('k_sha256'),
                     'K_validation_s': (run.get('cut_profile') or {}).get('phase_wall_s', {}).get('validation_bitset_v2_s'),
                     'counts': (run.get('cut_profile') or {}).get('counts')})
    for item in reports['censored']['cases']:
        arms = {r['arm_id']: r for r in item['runs']}
        retries.append({'case': item['name'],
                        'status_by_arm': {key: run['status'] for key, run in arms.items()},
                        'lp_by_arm': {key: run.get('lp_opt_value') for key, run in arms.items()},
                        'wall_s_by_arm': {key: run['wall_total_s'] for key, run in arms.items()},
                        'A_effect': item['contrasts']['A_EFFECT'],
                        'K_effect': item['contrasts']['K_EFFECT'],
                        'partition_sha256': arms['A2_K'].get('partition_sha256')})
    unresolved = any(x['status'] != 'PROFILED' for x in cuts) or any(
        x['A_effect']['status'] != 'MATCHED_COMPLETE'
        or x['K_effect']['status'] != 'MATCHED_COMPLETE' for x in retries)
    recommendation = ('INVESTIGATE_FURTHER' if unresolved else
                      'RETEST_COMPLETE_EXPLORATORY_NO_AUTOMATIC_PROMOTION')
    result = {'schema': ANALYSIS_SCHEMA, 'classification': 'EXPLORATORY_POSTHOC_RETEST_V2',
              'scientific_gate': 'PENDING', 'scientific_promotion': 'NOT_AUTHORIZED',
              'basis_plan_sha256': sha256_file(plan_path),
              'stage_manifest_sha256': {stage: sha256_file(results_dir/stage/'manifest.json')
                                         for stage in STAGES},
              'grouping_v1_manifest_sha256': plan['parent_stage_manifest_sha256']['grouping'],
              'grouping_v1_complete_cases': len(prior_grouping['cases']),
              'cut_profiles': cuts, 'censored_retests': retries, 'recommendation': recommendation,
              'limitations': ['A2 v2 permanece política pré-escolhida, não selecionada por LP',
                              'Não substituir resultados originais nem promoção científica',
                              'Comparação de agrupamentos v1 não foi reexecutada']}
    output_dir.mkdir(parents=True, exist_ok=False)
    _write_json(output_dir/'analysis.json', result)
    lines = ['# AS-05 — Reensaio diagnóstico v2', '',
             '**Classificação:** exploratória, sem homologação científica.', '',
             f'**Decisão:** `{recommendation}`', '',
             '## Cortes K', '', '| Caso | Status | Cortes | Validação K (s) |',
             '|---|---|---:|---:|']
    for item in cuts:
        lines.append(f"| {item['case']} | {item['status']} | {item['counts'].get('unique', '—') if item['counts'] else '—'} | {item['K_validation_s'] if item['K_validation_s'] is not None else '—'} |")
    lines += ['', '## Reensaios LP', '',
              '| Caso | U | U+K | A2+K | Ganho A2 relativo |',
              '|---|---|---|---|---:|']
    for item in retries:
        st = item['status_by_arm']
        gain = item['A_effect'].get('relative_gain')
        lines.append(f"| {item['case']} | {st['U']} | {st['U_K']} | {st['A2_K']} | {gain*100:.4f}% |" if gain is not None else
                     f"| {item['case']} | {st['U']} | {st['U_K']} | {st['A2_K']} | — |")
    lines += ['', '## Proveniência', '',
              f"- Plano v2 SHA-256: `{result['basis_plan_sha256']}`",
              f"- Agrupamento v1 preservado: `{result['grouping_v1_manifest_sha256']}`",
              '- A política A2+K do reensaio é `reachability_degree` com a seed do plano v1.',
              '- A comparação original de quatro casos e a decisão AS05 não foram alteradas.', '']
    (output_dir/'analysis.md').write_text('\n'.join(lines), encoding='utf-8')
    with (output_dir/'arms.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['case', 'arm', 'status', 'lp_opt_value', 'wall_s'])
        for item in retries:
            for arm, status in item['status_by_arm'].items():
                writer.writerow([item['case'], arm, status,
                                 item['lp_by_arm'][arm], item['wall_s_by_arm'][arm]])
    files = ('analysis.json', 'analysis.md', 'arms.csv')
    _write_json(output_dir/'manifest.json', {'schema': 'AS05-DIAG-RETEST-ANALYSIS-INTEGRITY-v2',
                                              'files': {name: sha256_file(output_dir/name) for name in files}})
    return output_dir/'analysis.json'
