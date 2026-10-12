"""Consolida diagnóstico pós-AS05; nenhuma conclusão é gate científico GO."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from as05_diag_core import (STAGES, _write_json, validate_diagnostic_plan,
                            verify_diagnostic_stage)
from as05_protocol import sha256_file


def _positive(value):
    return type(value) in (float, int) and math.isfinite(value) and value > 0


def build_analysis(*, root: Path, plan_path: Path, stage_folders: dict[str, Path],
                   output_dir: Path) -> Path:
    if output_dir.exists():
        raise FileExistsError('DIAG: análise append-only; diretório já existe')
    plan = validate_diagnostic_plan(json.loads(plan_path.read_text(encoding='utf-8')), root)
    reports = {}
    for stage in STAGES:
        report = verify_diagnostic_stage(stage_folders[stage])
        if report.get('stage') != stage or report.get('plan_sha256') != sha256_file(plan_path):
            raise ValueError(f'DIAG: relatório {stage} não é do mesmo plano')
        if report.get('parent_report_sha256') != plan['parent_pilot_report_sha256']:
            raise ValueError('DIAG: os três relatórios devem partir do mesmo piloto')
        if [x['name'] for x in report['cases']] != plan['cases'][stage]:
            raise ValueError(f'DIAG: {stage} alterou o conjunto de instâncias')
        reports[stage] = report
    cut_cases, retry_cases, policy_rows = [], [], []
    for case in reports['cuts']['cases']:
        run = case['runs'][0]
        times = run.get('cut_profile', {}).get('phase_wall_s', {})
        dominant = max(times, key=times.get) if times else None
        cut_cases.append({'case_name': case['name'], 'status': run['status'],
                          'family_dominant': dominant,
                          'dominant_s': times.get(dominant) if dominant else None,
                          'unique_cuts': run.get('cut_profile', {}).get('counts', {}).get('unique'),
                          'k_sha256': run.get('cut_profile', {}).get('k_sha256'),
                          'phase_wall_s': times, 'supervisor_wall_phases_s': run.get('wall_phases_s')})
    for case in reports['censored']['cases']:
        runs = case['runs']
        retry_cases.append({'case_name': case['name'],
                            'statuses': {r['arm_id']: r['status'] for r in runs},
                            'K_EFFECT': case['contrasts']['K_EFFECT'],
                            'A_EFFECT': case['contrasts']['A_EFFECT'],
                            'u_without_k_wall_s': next(r['wall_total_s'] for r in runs if r['arm_id'] == 'U'),
                            'u_k_wall_s': next(r['wall_total_s'] for r in runs if r['arm_id'] == 'U_K'),
                            'a2_k_wall_s': next(r['wall_total_s'] for r in runs if r['arm_id'] == 'A2_K')})
    material_count = 0
    for case in reports['grouping']['cases']:
        for group in plan['policies']:
            run = next(x for x in case['runs'] if x['grouping_policy'] == group)
            contrast = case['contrasts'][group]
            rel = contrast.get('relative_gain')
            ratio = contrast.get('wall_ratio')
            material = (contrast['status'] == 'MATCHED_COMPLETE'
                        and rel is not None and rel >= 0.01
                        and _positive(ratio) and ratio <= 3.0)
            material_count += bool(material)
            policy_rows.append({'case_name':case['name'], 'policy':group,
                                'status': run['status'],
                                'partition_sha256': run.get('partition_sha256'),
                                'lp_opt_value': run.get('lp_opt_value'),
                                'lp_delta_over_u_k': contrast.get('lp_delta'),
                                'relative_gain': rel, 'wall_ratio': ratio,
                                'solver_runtime_ratio': contrast.get('solver_runtime_ratio'),
                                'material_exploratory': bool(material)})
    censored_after_retry = [r['case_name'] for r in retry_cases
                            if r['A_EFFECT']['status'] != 'MATCHED_COMPLETE'
                            or r['K_EFFECT']['status'] != 'MATCHED_COMPLETE']
    unresolved_cut = [c['case_name'] for c in cut_cases if c['status'] != 'PROFILED']
    incomplete_policy = [r['case_name']+':'+r['policy'] for r in policy_rows
                         if r['status'] != 'OPTIMAL_NUMERIC']
    if unresolved_cut or censored_after_retry or incomplete_policy:
        recommendation = 'INVESTIGATE_FURTHER'
        explanation = 'O diagnóstico ainda contém cortes, braços ou políticas censurados'
    elif not material_count:
        recommendation = 'A2_NO_MATERIAL_LP_ADVANTAGE_IN_DEVELOPMENT'
        explanation = 'Nenhuma política A2 pré-selecionada apresentou ganho LP material/custo aceitável'
    else:
        recommendation = 'FOLLOW_UP_REPLICATION_REQUIRED'
        explanation = 'Ganho exploratório observado; exige repetição, independência e gate científico próprios'
    report = {'schema':'AS05-DIAG-ANALYSIS-v1',
              'classification':'EXPLORATORY_POSTHOC_DEVELOPMENT_ONLY',
              'scientific_homologation':'PENDING',
              'scientific_promotion':'NOT_AUTHORIZED',
              'basis_plan_sha256':sha256_file(plan_path),
              'stages_sha256':{stage:sha256_file(stage_folders[stage]/'manifest.json')
                                for stage in STAGES},
              'cuts':cut_cases, 'censored_retries':retry_cases,
              'grouping':policy_rows, 'n_material_exploratory':material_count,
              'unresolved_cut_cases':unresolved_cut,
              'censored_after_retry':censored_after_retry,
              'incomplete_policy_cases':incomplete_policy,
              'recommendation':recommendation, 'explanation':explanation,
              'limitations':[
                  'Não substitui o gate científico AS05 original',
                  'Políticas novas avaliadas somente no conjunto de desenvolvimento',
                  'Seleção da melhor política após observar resultados é exploratória',
                  'Não reutilizar resultados nos casos de avaliação AS00 sem novo pré-registro',
                  'Retomar reprodutibilidade/independência antes de promoção da AS06',
              ]}
    output_dir.mkdir(parents=True, exist_ok=False)
    output = output_dir/'diagnostic_analysis.json'
    _write_json(output, report)
    with (output_dir/'grouping.csv').open('w', encoding='utf-8', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(policy_rows[0]))
        writer.writeheader()
        writer.writerows(policy_rows)
    note = ['# AS05 — Interpretação do diagnóstico', '',
            '**Natureza:** investigação exploratória pós-piloto, sem homologação independente.', '',
            f'**Encaminhamento:** `{recommendation}`.', '', explanation, '',
            '## Perfil dos cortes K', '',
            '| Instância | Status | Fase dominante | Cortes únicos |',
            '|---|---|---|---:|']
    for item in cut_cases:
        note.append(f"| {item['case_name']} | {item['status']} | {item['family_dominant'] or '—'} | {item['unique_cuts'] if item['unique_cuts'] is not None else '—'} |")
    note += ['', '## Retestes das instâncias censuradas', '',
             '| Instância | U | U+K | A2+K | Efeito A |',
             '|---|---|---|---|---|']
    for item in retry_cases:
        s=item['statuses']
        note.append(f"| {item['case_name']} | {s['U']} | {s['U_K']} | {s['A2_K']} | {item['A_EFFECT']['status']} |")
    note += ['', '## Políticas de agrupamento (desenvolvimento)', '',
             '| Instância | Política | Status | Ganho A2 relativo | Custo total A2/U+K |',
             '|---|---|---|---:|---:|']
    for item in policy_rows:
        rel = '—' if item['relative_gain'] is None else f"{item['relative_gain']*100:.4f}%"
        wall = '—' if item['wall_ratio'] is None else f"{item['wall_ratio']:.3f}×"
        note.append(f"| {item['case_name']} | {item['policy']} | {item['status']} | {rel} | {wall} |")
    note += ['', '## Limitações', '']
    note += ['- '+x for x in report['limitations']]
    (output_dir/'diagnostic_analysis.md').write_text('\n'.join(note)+'\n',encoding='utf-8')
    files = ('diagnostic_analysis.json','diagnostic_analysis.md','grouping.csv')
    _write_json(output_dir/'manifest.json', {'schema':'AS05-DIAG-ANALYSIS-INTEGRITY-v1',
                                             'files':{name:sha256_file(output_dir/name)
                                                      for name in files}})
    return output
