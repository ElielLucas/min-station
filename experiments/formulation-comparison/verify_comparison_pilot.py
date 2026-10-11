#!/usr/bin/env python3
"""FC-05: gate operacional independente, somente leitura, sobre um piloto FC-04.

Uma indicação READY_FOR_EXTENDED nunca é prova racional, recomendação de
superioridade nem autorização para disparar uma campanha longa. Requer auditoria
FC-04 de TODOS os bytes antes de aceitar o gate calculado a partir do CSV.

CLI::
    python experiments/formulation-comparison/verify_comparison_pilot.py \
        results/formulation-comparison/pilot-YYYYMMDDTHHMMSSZ
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

from verify_comparison_artifacts import ROOT, verify as verify_artifacts

SCHEMA = 'FC05-v1'
READY = 'READY_FOR_EXTENDED'
NOT_READY = 'NOT_READY'
LP_ARMS = ('lp_base', 'lp_comp', 'lp_fcc_k')
MIP_ARMS = ('comp_mip', 'fcc_k')
PILOT_SELECTED = ('hb-q4-ndir2-p1-k1-L2.txt', 'bp-nao-q2-B2-s0.txt')
HASH_RE = re.compile(r'^[a-f0-9]{64}$')
TOL = 1e-6


def _num(value, *, nonnegative=False):
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    if not math.isfinite(number) or (nonnegative and number < 0):
        return None
    return number


def _integer(value):
    n = _num(value, nonnegative=True)
    if n is None or abs(n - round(n)) > TOL:
        return None
    return int(round(n))


def _true(value):
    return str(value).lower() == 'true'


def _label(row):
    """Distingue LP base/COMP, que compartilham formulation=baseline no CSV FC03."""
    if row.get('modality') == 'A':
        raw = (row.get('observations') or '').split(';', 1)[0].strip()
        return raw if raw in LP_ARMS else 'UNKNOWN_LP'
    if row.get('modality') == 'B':
        return (row.get('formulation') or '').strip()
    return 'UNKNOWN_MODALITY'


def _reasons_for_row(row, arm, *, budget_s, expected_hash):
    reasons = []
    if row.get('status') != 'OPTIMAL':
        reasons.append(f'CENSORED_OR_NOT_OPTIMAL:{arm}:{row.get("status") or "MISSING"}')
    if not _true(row.get('model_complete')):
        reasons.append(f'INCOMPLETE_MODEL:{arm}')
    if row.get('instance_sha256') != expected_hash:
        reasons.append(f'INSTANCE_HASH_MISMATCH:{arm}')
    if row.get('solver_evidence') != 'SOLVER_NUMERIC_OPTIMAL':
        reasons.append(f'MISSING_NUMERIC_OPTIMALITY_EVIDENCE:{arm}')
    if row.get('evidence_schema') != 'FC03-v1':
        reasons.append(f'UNEXPECTED_EVIDENCE_SCHEMA:{arm}')
    if row.get('solver_numeric_status') != row.get('status'):
        reasons.append(f'SOLVER_STATUS_MISMATCH:{arm}')
    wall = _num(row.get('wall_total_s'), nonnegative=True)
    solver = _num(row.get('solver_runtime_s'), nonnegative=True)
    work = _num(row.get('work'), nonnegative=True)
    if wall is None or wall <= 0 or solver is None or work is None:
        reasons.append(f'MISSING_COST_MEASUREMENT:{arm}')
    elif wall > budget_s + max(0.25, budget_s * 0.005):
        reasons.append(f'GLOBAL_BUDGET_EXCEEDED:{arm}')
    elif solver > wall + 0.05:
        reasons.append(f'SOLVER_RUNTIME_GREATER_THAN_WALL:{arm}')
    # Sem prova independente, campos de prova e gap têm de permanecer vazios.
    proof = row.get('rational_verification')
    if proof == 'NOT_CERTIFIED':
        if (row.get('rational_verified_lb_exact') or
                row.get('certified_gap_abs_exact') or
                row.get('certified_gap_rel_exact') or
                row.get('certified_gap_status') != 'INCONCLUSIVE'):
            reasons.append(f'UNSUPPORTED_RATIONAL_CERTIFICATION:{arm}')
    elif proof != 'RATIONAL_VERIFIED' or not row.get('rational_proof_id'):
        reasons.append(f'INVALID_RATIONAL_EVIDENCE:{arm}')
    return reasons


def gate_from_rows(rows, manifest):
    """Avalia todos os pares pré-selecionados, sem solver e sem ler arquivos.

    Este cálculo é *provisório* quando realizado antes do manifesto final. Para
    autorizar READY é obrigatório executar evaluate(), que verifica SHA-256.
    """
    reasons = []
    if manifest.get('tier') != 'pilot':
        reasons.append('INVALID_TIER:pilot_required')
    if set(manifest.get('modalities', [])) != {'A', 'B'}:
        reasons.append('INCOMPLETE_MODALITIES:A_B_required')
    chosen = manifest.get('formulations', [])
    if not set(MIP_ARMS).issubset(set(chosen)):
        reasons.append('MISSING_PRIMARY_MIP_ARMS')
    if len(chosen) != len(set(chosen)) or set(chosen) - set(MIP_ARMS + ('baseline',)):
        reasons.append('UNEXPECTED_FORMULATIONS')
    if manifest.get('errors'):
        reasons.append('RUNNER_ERRORS_RECORDED')
    config = manifest.get('config') or {}
    lp_budget = _num(config.get('lp_time_limit_s'))
    mip_budget = _num(config.get('time_limit_s'))
    if lp_budget is None or mip_budget is None or lp_budget <= 0 or mip_budget <= 0:
        reasons.append('INVALID_BUDGET_CONFIGURATION')
    elif lp_budget > 60 or mip_budget > 120:
        reasons.append('PILOT_BUDGET_ABOVE_PREREGISTERED_CAP')
    instances = manifest.get('instances', [])
    names = [x.get('nome') for x in instances if isinstance(x, dict)]
    expected = {x['nome']: x.get('instance_sha256') for x in instances
                if isinstance(x, dict) and x.get('nome')}
    if not names or len(names) != len(set(names)) or len(expected) != len(names):
        reasons.append('INVALID_INSTANCE_SELECTION')
    if tuple(names) != PILOT_SELECTED:
        reasons.append('PILOT_SELECTION_DIFFERS_FROM_PREREGISTRATION')
    for name, digest in expected.items():
        if not HASH_RE.fullmatch(str(digest)):
            reasons.append(f'INVALID_INSTANCE_DIGEST:{name}')
    unexpected = sorted({r.get('instance_name') for r in rows} - set(expected))
    if unexpected:
        reasons.append(f'UNEXPECTED_CSV_INSTANCES:{unexpected}')
    grouped = {}
    for row in rows:
        name = row.get('instance_name')
        arm = _label(row)
        grouped.setdefault(name, {}).setdefault(arm, []).append(row)
    per_instance = []
    for name in names:
        local = []
        by_arm = grouped.get(name, {})
        expected_arms = set(LP_ARMS + MIP_ARMS)
        if 'baseline' in manifest.get('formulations', []):
            expected_arms.add('baseline')
        extra = sorted(set(by_arm) - expected_arms)
        if extra:
            local.append(f'UNEXPECTED_ARMS:{extra}')
        record = {}
        for arm in LP_ARMS + MIP_ARMS:
            matches = by_arm.get(arm, [])
            if len(matches) != 1:
                local.append(f'ARM_COUNT:{arm}:{len(matches)}')
                continue
            row = matches[0]
            record[arm] = row
            if lp_budget is not None and mip_budget is not None:
                local.extend(_reasons_for_row(
                    row, arm, budget_s=lp_budget if arm in LP_ARMS else mip_budget,
                    expected_hash=expected.get(name),
                ))
        baseline = by_arm.get('baseline', [])
        if baseline and (len(baseline) != 1 or
                         baseline[0].get('comparison_role') != 'ablation_no_k' or
                         baseline[0].get('pair_status') != 'ABLATION_ONLY'):
            local.append('INVALID_ABLATION_LABEL')
        if 'baseline' in manifest.get('formulations', []) and len(baseline) != 1:
            local.append(f'ABLATION_ARM_COUNT:{len(baseline)}')
        if len(record) == len(LP_ARMS + MIP_ARMS):
            comp, fcc = record['comp_mip'], record['fcc_k']
            k_values = [record[arm].get('k_sha256') for arm in
                        ('lp_comp', 'lp_fcc_k', 'comp_mip', 'fcc_k')]
            if any(not HASH_RE.fullmatch(str(k)) for k in k_values) or len(set(k_values)) != 1:
                local.append('K_HASH_MISMATCH')
            k_numbers = [_integer(record[arm].get('n_K')) for arm in
                         ('lp_comp', 'lp_fcc_k', 'comp_mip', 'fcc_k')]
            if any(x is None for x in k_numbers) or len(set(k_numbers)) != 1:
                local.append('K_COUNT_MISMATCH')
            for arm, row in (('comp_mip', comp), ('fcc_k', fcc)):
                if row.get('comparison_role') != 'primary' or row.get('pair_status') != 'PAIR_VALID':
                    local.append(f'PAIR_NOT_VALID:{arm}')
                if (row.get('pair_instance_sha256') != expected.get(name) or
                        row.get('pair_k_sha256') != row.get('k_sha256')):
                    local.append(f'PAIR_IDENTITY_MISMATCH:{arm}')
                if (not _true(row.get('k_validated')) or
                        _integer(row.get('n_K_added')) != _integer(row.get('n_K'))):
                    local.append(f'K_NOT_FULLY_APPLIED:{arm}')
                ub = _integer(row.get('physical_feasible_ub'))
                inc = _num(row.get('solver_numeric_mip_incumbent'), nonnegative=True)
                obj = _num(row.get('objective_primal'), nonnegative=True)
                if (not _true(row.get('physically_validated')) or ub is None or
                        inc is None or obj is None or
                        abs(ub - obj) > TOL or abs(inc - obj) > TOL or
                        not row.get('physical_ub_provenance', '').startswith('INDEPENDENT_VALIDATOR:')):
                    local.append(f'INVALID_PHYSICAL_WITNESS:{arm}')
                if _num(row.get('solver_numeric_mip_lb')) is None:
                    local.append(f'MISSING_NUMERIC_MIP_BOUND:{arm}')
            ubs = [_integer(comp.get('physical_feasible_ub')),
                   _integer(fcc.get('physical_feasible_ub'))]
            if None not in ubs and ubs[0] != ubs[1]:
                local.append('DIFFERENT_NUMERIC_MIP_OPTIMA')
            if None not in ubs:
                for arm in LP_ARMS:
                    lp = _num(record[arm].get('solver_numeric_lp_objective'))
                    if lp is None:
                        local.append(f'MISSING_NUMERIC_LP:{arm}')
                    elif lp > min(ubs) + TOL:
                        local.append(f'LP_EXCEEDS_PHYSICAL_UB:{arm}')
            if record['lp_base'].get('k_sha256'):
                local.append('LP_BASE_SHOULD_HAVE_NO_K')
        measurements = {}
        for arm in LP_ARMS + MIP_ARMS:
            matches = by_arm.get(arm, [])
            row = matches[0] if len(matches) == 1 else None
            measurements[arm] = {
                'status': row.get('status') if row else 'NOT_MEASURED',
                'solver_numeric_lp': _num(row.get('solver_numeric_lp_objective')) if row else None,
                'solver_numeric_mip_incumbent': _num(row.get('solver_numeric_mip_incumbent'))
                if row else None,
                'physical_feasible_ub': _integer(row.get('physical_feasible_ub')) if row else None,
                'wall_total_s': _num(row.get('wall_total_s'), nonnegative=True) if row else None,
                'solver_work': _num(row.get('work'), nonnegative=True) if row else None,
            }
        per_instance.append({
            'instance': name, 'instance_sha256': expected.get(name),
            'status': READY if not local else NOT_READY,
            'reasons': sorted(set(local)),
            'observed_primary_rows': sum(len(by_arm.get(x, [])) for x in MIP_ARMS),
            'observed_lp_rows': sum(len(by_arm.get(x, [])) for x in LP_ARMS),
            'measurements': measurements,
        })
    not_ready_total = sum(x['status'] == NOT_READY for x in per_instance)
    summary = {
        'selected_total': len(names),
        'primary_pair_valid_total': sum(x['status'] == READY for x in per_instance),
        'not_ready_total': not_ready_total,
        'censored_or_missing_total': sum(
            any(r.startswith(('CENSORED_OR_NOT_OPTIMAL:', 'ARM_COUNT:')) for r in x['reasons'])
            for x in per_instance
        ),
        'raw_rows_total': len(rows),
    }
    decision = READY if not reasons and not not_ready_total and names else NOT_READY
    return {
        'schema': SCHEMA,
        'candidate_gate': decision,
        'audit_required_for_final_gate': True,
        'scope': 'preselected_pilot_instances_only',
        'selected_instances': names,
        'summary': summary,
        'global_reasons': sorted(set(reasons)),
        'instances': per_instance,
        'interpretation': 'operational_readiness_only_not_superiority_or_rational_optimality',
        'automatic_extended_execution': False,
    }


def _markdown(gate):
    lines = [
        '# FC-05 — Relatório do piloto corrigido', '',
        f'**Gate preliminar:** `{gate["candidate_gate"]}`',
        '**Decisão final:** depende de `verify_comparison_pilot.py` e da auditoria FC-04.',
        '', '## Escopo e limitações', '',
        'Amostra diagnóstica restrita às instâncias pré-selecionadas. COMP+K × F-CC+K é',
        'o par primário. Baseline sem K é apenas ablação. Resultados `SOLVER_NUMERIC_OPTIMAL`',
        'não são provas racionais. A decisão do gate não demonstra superioridade entre',
        'formulações e não autoriza execução automática de 3.600 segundos.', '',
        '## Denominadores e casos não medidos', '',
        f'- Instâncias selecionadas: {gate["summary"]["selected_total"]}',
        f'- Pares operacionais válidos: {gate["summary"]["primary_pair_valid_total"]}',
        f'- Instâncias não prontas: {gate["summary"]["not_ready_total"]}',
        f'- Instâncias censuradas/incompletas: {gate["summary"]["censored_or_missing_total"]}',
        '', '## Casos individuais', '',
        '| Instância | Gate preliminar | Motivos |', '|---|---|---|',
    ]
    for x in gate['instances']:
        reasons = '; '.join(x['reasons']) or '—'
        lines.append(f'| {x["instance"]} | {x["status"]} | {reasons} |')
    lines += ['', '## Medições observadas por braço', '',
              '| Instância | Braço | Status | LP numérico | Incumbente MIP numérica | UB física | Wall (s) | Work |',
              '|---|---|---|---:|---:|---:|---:|---:|']
    for x in gate['instances']:
        for arm, measurement in x['measurements'].items():
            def display(key):
                value = measurement[key]
                return str(value) if value is not None else '—'
            lines.append(
                f'| {x["instance"]} | {arm} | {display("status")} | '
                f'{display("solver_numeric_lp")} | '
                f'{display("solver_numeric_mip_incumbent")} | '
                f'{display("physical_feasible_ub")} | '
                f'{display("wall_total_s")} | {display("solver_work")} |'
            )
    lines += ['', '## Motivos globais', '']
    lines += [f'- {reason}' for reason in gate['global_reasons']] or ['- Nenhum identificado']
    lines += ['', '## Conferência obrigatória', '',
              'Execute `verify_comparison_pilot.py` sobre este diretório após o manifesto',
              'ser finalizado. O verificador checa todos os SHA-256, recomputa o gate e',
              'rejeita divergências. Uma rodada censurada permanece documentada.', '']
    return '\n'.join(lines)


def publish_candidate(run_dir: Path, rows, manifest_stub):
    """Grava o relatório ANTES do manifesto FC-04, para inclusão no inventário."""
    run_dir = Path(run_dir)
    json_path = run_dir / 'pilot_gate.json'
    md_path = run_dir / 'pilot_report.md'
    if json_path.exists() or md_path.exists():
        raise FileExistsError('FC05: relatório do piloto já existe, não sobrescrever')
    gate = gate_from_rows(rows, manifest_stub)
    json_path.write_text(json.dumps(gate, ensure_ascii=False, sort_keys=True, indent=2) + '\n',
                         encoding='utf-8')
    md_path.write_text(_markdown(gate), encoding='utf-8')
    return gate


def evaluate(run_dir: Path, *, root: Path = ROOT):
    """Retorna gate final; somente leitura e condicionado à auditoria FC-04."""
    run_dir = Path(run_dir).resolve()
    root = Path(root).resolve()
    problems = []
    audit_ok, audit_problems = verify_artifacts(run_dir, root=root)
    if not audit_ok:
        problems += [f'ARTIFACT_AUDIT:{p}' for p in audit_problems]
    manifest_path = run_dir / 'manifest.json'
    csv_path = run_dir / 'results.csv'
    candidate_path = run_dir / 'pilot_gate.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        with csv_path.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        recomputed = gate_from_rows(rows, manifest)
        if candidate != recomputed:
            problems.append('PUBLISHED_CANDIDATE_DOES_NOT_MATCH_CSV_AND_MANIFEST')
        manifest_rel = candidate_path.relative_to(root).as_posix()
        if manifest_rel not in manifest.get('generated_files_sha256', {}):
            problems.append('CANDIDATE_NOT_INCLUDED_IN_MANIFEST')
    except (OSError, ValueError, KeyError, TypeError, AttributeError,
            json.JSONDecodeError, csv.Error) as exc:
        return {
            'status': NOT_READY, 'artifact_audit': 'FAIL' if not audit_ok else 'PASS',
            'problems': problems + [f'INVALID_OR_MISSING_PILOT_REPORT:{exc}'],
            'candidate_gate': None,
        }
    decision = READY if not problems and recomputed['candidate_gate'] == READY else NOT_READY
    instance_problems = [f'{item["instance"]}:{reason}'
                         for item in recomputed['instances'] for reason in item['reasons']]
    return {
        'status': decision,
        'artifact_audit': 'PASS' if audit_ok else 'FAIL',
        'candidate_gate': recomputed['candidate_gate'],
        'summary': recomputed['summary'],
        'instances': recomputed['instances'],
        'problems': problems + recomputed['global_reasons'] + instance_problems,
        'scope': recomputed['scope'],
        'rational_certification_claimed': False,
        'superiority_claimed': False,
        'extended_run_triggered': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args(argv)
    result = evaluate(args.run_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result['status'] == READY else 1


if __name__ == '__main__':
    raise SystemExit(main())
