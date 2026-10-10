#!/usr/bin/env python3
"""N2-T6: read-only audit of frozen N2-T5 artifacts and scientific failure.

Run from repository root:
    python experiments/alternative-formulations/verify_n2_t6_gate.py

This independently checks artifact bytes, accounting, frozen controls and
negative gate criteria. It does NOT re-prove E5 certificates from their dual
witnesses; that was the separately accepted N2-T3 audit responsibility.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / 'experiments/alternative-formulations/n2-t1-freeze.json'
RESULTS = ROOT / 'results/alternative-formulations/n2-t5-prospectivo'
MANIFEST = 'n2-t5-manifest.json'
CSV_NAME = 'n2-t5-medicoes.csv'
CURVE_NAME = 'n2-t5-lb-versus-work.csv'
COSTS_NAME = 'n2-t5-custos.md'
SVG_NAME = 'n2-t5-lb-versus-work.svg'

# Anchors from the exact manifest presented for the prospective experiment.
# Deliberately do not replace these with values read from an editable manifest.
EXPECTED_FREEZE_SHA256 = 'b036e9d0fe8f446dfcaca2716df85054c73dbb8702484aacce3c807e6574de71'
EXPECTED_ARTIFACTS = {
    CSV_NAME: '2e1215e135561d4af962318f15eeaa96be0d04aed09a8e801765ae577958bac5',
    CURVE_NAME: 'c0be65a1fe79f7da59be50bc3b184e0143f6c97a7f0153e66464c26a43563d5d',
    COSTS_NAME: '0b6700ed47b257e1fb5aa368d5bd1b5ec17bbf832d691b89625c912601258d0a',
    SVG_NAME: '520f82c4e0e64dec45c3d4d11ce5c61abfe150aaaedc76c5bd9cecd0f55f9920',
}
EXPECTED_NAMES = (
    'HB-q4-ndir2-p1', 'BP-nao-[3,1]-q2',
    'HB-q6-ndir2-p1', 'BP-nao-[2,2,2]-q2',
)
TOL = Fraction(1, 1_000_000)


class AuditError(ValueError):
    """The underlying experiment cannot be accepted as auditable."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AuditError(reason)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def frac(value: str, label: str, *, required: bool = True) -> Fraction | None:
    if value is None or not value.strip():
        if required:
            raise AuditError(f'{label}: valor ausente')
        return None
    try:
        out = Fraction(value.strip())
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise AuditError(f'{label}: fração inválida') from exc
    return out


def decimal_fraction(value: object, label: str) -> Fraction:
    try:
        d = Decimal(str(value))
    except InvalidOperation as exc:
        raise AuditError(f'{label}: decimal inválido') from exc
    require(d.is_finite(), f'{label}: não finito')
    return Fraction(d)


def nonnegative_float(value: str, label: str) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f'{label}: float inválido') from exc
    require(math.isfinite(num) and num >= 0, f'{label}: negativo ou não finito')
    return num


def scientific_decision(rows: list[dict[str, str]], freeze: dict) -> dict:
    """Apply only predetermined *negative* gates; positive result needs review.

    Returns N2 FAIL when a necessary pre-registered criterion is violated.
    Otherwise returns REVIEW_REQUIRED, never automatically N2 PASS.
    """
    controls = freeze['instances']
    require(len(rows) == len(controls) == 4, 'esperadas quatro instâncias')
    problems: list[str] = []
    measured: list[dict] = []
    for i, (row, control) in enumerate(zip(rows, controls, strict=True)):
        name = control['name']
        require(row['name'] == name, f'ordem/identidade divergente: {i}')
        require(row['family'] == control['family'], f'{name}: família divergente')
        require(int(row['level']) == control['level'], f'{name}: nível divergente')
        require(int(row['n']) == control['n'] and int(row['m']) == control['m'],
                f'{name}: dimensões divergentes')
        require(int(row['r']) == control['r'], f'{name}: alcance divergente')
        require(row['instance_sha256'] == control['instance_sha256'],
                f'{name}: hash de instância divergente')
        if 'k_sha256' in control:
            require(row['k_sha256'] == control['k_sha256'],
                    f'{name}: hash K divergente')
        require(row['freeze_sha256'] == EXPECTED_FREEZE_SHA256,
                f'{name}: freeze SHA divergente')
        require(row['path'] == 'B/F-CC+K ROOT_ONLY', f'{name}: caminho divergente')
        require(int(row['seed']) == 42 and int(row['threads']) == 4,
                f'{name}: parâmetros alterados')
        require(nonnegative_float(row['work_cap'], 'work_cap') == 164,
                f'{name}: orçamento Work alterado')
        require(nonnegative_float(row['wall_cap_s'], 'wall_cap_s') == 1800,
                f'{name}: guarda temporal alterada')
        work = nonnegative_float(row['work_total'], f'{name}: work_total')
        wall = nonnegative_float(row['wall_total_s'], f'{name}: wall_total_s')
        require(work <= 164 + 1e-8 and wall <= 1800 + 1e-8,
                f'{name}: orçamento excedido')
        work_components = sum(nonnegative_float(row[x], f'{name}: {x}') for x in
                              ('work_comp_lp', 'work_core_ip', 'work_master', 'work_pricing'))
        require(abs(work_components - work) <= 1e-7,
                f'{name}: contabilidade Work inconsistente')
        require(int(row['work_unmeasured_calls']) == 0,
                f'{name}: chamadas sem Work medido')
        require(row['physical_status'] == 'CERTIFIED' and
                row['status'] == 'CERTIFIED_PHYSICAL_LB',
                f'{name}: certificado físico ausente')
        lb = frac(row['physical_lb_exact'], f'{name}: LB físico')
        require(lb is not None and lb >= 0, f'{name}: LB negativo')
        require(frac(row['lb_continuous_exact'], f'{name}: LB LP') == lb,
                f'{name}: LB LP e físico divergentes')
        require(row['lp_status'] == 'CERTIFIED' and row['lp_source'] in ('N1', 'ENUM', 'N2'),
                f'{name}: origem LP não certificada')
        require(row['g2_status'] == 'NOT_CONVERGED_CERTIFIED',
                f'{name}: G2 divergente da medição registrada')
        require(row['stop_reason'] == 'NUMERICAL_STATIONARY',
                f'{name}: parada divergente')
        require(row['b0_certificate_status'] == 'UNCERTIFIED' and
                not row['b0_certified_exact'],
                f'{name}: B0 não comprovado não pode ser promovido a certificado')
        b0 = frac(row['b0_reference'], f'{name}: B0')
        require(b0 is not None, f'{name}: B0 ausente')
        require(frac(row['gain_over_b0_reference'], f'{name}: ganho') == lb - b0,
                f'{name}: ganho não coincide com LB-B0')
        require(int(row['physical_integer_lb']) == math.ceil(lb - TOL),
                f'{name}: arredondamento inteiro divergente')
        if control['level'] == 1:
            require(b0 == decimal_fraction(control['B0_reference'], f'{name}: B0 congelado'),
                    f'{name}: B0 histórico divergente')
            lp = decimal_fraction(control['full_lp_reference'], f'{name}: LP congelado')
            require(frac(row['full_lp_historical'], f'{name}: LP histórico') == lp,
                    f'{name}: LP histórico divergente')
            delta = lp - b0
            require(delta > 0, f'{name}: incremento congelado não positivo')
            recovery = (lb - b0) / delta
            require(frac(row['recovery_fraction_level1'], f'{name}: recuperação') == recovery,
                    f'{name}: recuperação divergente')
            if recovery < Fraction(1, 2):
                problems.append(f'{name}: recuperação {recovery} < 1/2')
        else:
            require(not row['full_lp_historical'] and not row['recovery_fraction_level1'],
                    f'{name}: LP/recuperação nível 2 indevidamente imputados')
            require(abs(b0 - decimal_fraction(row['b0_comp_lp'], f'{name}: COMP')) <= TOL or
                    abs(b0 - decimal_fraction(row['b0_core_ip'], f'{name}: core')) <= TOL,
                    f'{name}: B0 não coincide com componente informado')
        if lb <= b0:
            problems.append(f'{name}: LB certificado {lb} não excede B0 {b0}')
        measured.append({'name': name, 'family': control['family'],
                         'level': control['level'], 'b0': str(b0), 'lb': str(lb),
                         'gain': str(lb - b0), 'work': work, 'wall_s': wall})
    return {'decision': 'N2 FAIL' if problems else 'MANUAL_REVIEW_REQUIRED',
            'blocking_reasons': problems, 'measured': measured,
            'note': 'PASS nunca é emitido automaticamente; requer revisão científica/independente.'}


def validate_curves(curve: list[dict[str, str]], rows: list[dict[str, str]]) -> None:
    groups: dict[str, list[dict[str, str]]] = {}
    for point in curve:
        require(point['name'] in EXPECTED_NAMES, 'curva: instância não congelada')
        groups.setdefault(point['name'], []).append(point)
    require(len(curve) == sum(int(row['n_curve_points']) for row in rows),
            'curva: número total de pontos inconsistente')
    require(set(groups) == set(EXPECTED_NAMES), 'curva: faltam instâncias')
    for row in rows:
        name = row['name']
        points = groups[name]
        require(len(points) == int(row['n_curve_points']), f'{name}: pontos incompletos')
        last_work = -1.0
        last_wall = -1.0
        last_lb = Fraction(-1)
        for i, point in enumerate(points):
            require(int(point['iteration']) == i, f'{name}: iteração faltante/repetida')
            work = nonnegative_float(point['cumulative_work'], f'{name}: curva work')
            wall = nonnegative_float(point['cumulative_wall_s'], f'{name}: curva wall')
            require(work + 1e-8 >= last_work and wall + 1e-8 >= last_wall,
                    f'{name}: curva não monotônica em Work/Wall')
            require(work <= nonnegative_float(row['work_total'], 'Work final') + 1e-8,
                    f'{name}: ponto supera Work final')
            require(wall <= nonnegative_float(row['wall_total_s'], 'Wall final') + 1e-8,
                    f'{name}: ponto supera tempo final')
            require(point['lb_status'] == 'CERTIFIED', f'{name}: curva sem prova')
            require(point['lb_source'] == row['lp_source'],
                    f'{name}: origem do certificado divergente')
            lb = frac(point['lb_exact'], f'{name}: ponto LB')
            require(lb is not None and lb >= last_lb,
                    f'{name}: curva de melhor LB retrocedeu')
            require(int(point['pricing_calls']) == i + 1,
                    f'{name}: chamadas de pricing inconsistentes')
            last_work, last_wall, last_lb = work, wall, lb
        require(last_lb == frac(row['physical_lb_exact'], f'{name}: LB final'),
                f'{name}: curva termina em LB diferente')
        require(int(points[-1]['pricing_calls']) == int(row['pricing_calls']),
                f'{name}: total de pricing divergente')
        require(points[-1]['note'] == row['stop_reason'],
                f'{name}: parada da curva divergente')


def audit(root: Path = ROOT, results: Path | None = None,
          *, expected_artifacts: dict[str, str] = EXPECTED_ARTIFACTS) -> dict:
    """Audit exact on-disk files; does not write or solve anything."""
    if results is None:
        results = root / 'results/alternative-formulations/n2-t5-prospectivo'
    freeze_path = root / 'experiments/alternative-formulations/n2-t1-freeze.json'
    require(sha256(freeze_path) == EXPECTED_FREEZE_SHA256,
            'freeze N2-T1: SHA-256 divergente')
    with freeze_path.open(encoding='utf-8') as f:
        freeze = json.load(f)
    require(freeze.get('state') == 'FROZEN' and freeze.get('path') == 'B',
            'freeze N2-T1 não corresponde ao caminho pré-registrado')
    require(tuple(x['name'] for x in freeze['instances']) == EXPECTED_NAMES,
            'quatro instâncias congeladas divergentes')
    with (results / MANIFEST).open(encoding='utf-8') as f:
        manifest = json.load(f)
    require(manifest.get('task') == 'N2-T5' and
            manifest.get('status') == 'MEASURED_PENDING_N2_T6',
            'manifesto N2-T5 incompatível')
    require(manifest.get('freeze_sha256') == EXPECTED_FREEZE_SHA256,
            'manifesto vinculado a outro freeze')
    require(manifest.get('instances_in_freeze_order') == list(EXPECTED_NAMES),
            'manifesto: ordem de instâncias divergente')
    require(manifest.get('n_rows') == 4 and manifest.get('n_physical_certified') == 4,
            'manifesto: contagem de provas divergente')
    require(manifest.get('protocol') == freeze['protocol'],
            'manifesto: protocolo não coincide com freeze')
    require(manifest.get('scope') == 'prospective, root only',
            'manifesto: escopo divergente')
    for filename, expected_hash in expected_artifacts.items():
        require(manifest.get('artifacts_sha256', {}).get(filename) == expected_hash,
                f'{filename}: digest publicado não coincide com âncora')
        require(sha256(results / filename) == expected_hash,
                f'{filename}: bytes não coincidem com SHA-256 publicado')
    rows = read_csv(results / CSV_NAME)
    require([x['name'] for x in rows] == list(EXPECTED_NAMES),
            'CSV: linhas ausentes/duplicadas/fora de ordem')
    report = scientific_decision(rows, freeze)
    validate_curves(read_csv(results / CURVE_NAME), rows)
    report.update({'task': 'N2-T6', 'audit_status': 'VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS',
                   'freeze_sha256': EXPECTED_FREEZE_SHA256,
                   'artifact_sha256': dict(expected_artifacts),
                   'limitations': [
                       'Verificação de arquivo e invariantes não substitui reauditoria das provas E5.',
                       'B0 é referência numérica/histórica e não certificado físico E5.',
                       'O resultado N2 FAIL é sobre o protocolo congelado, não impossibilidade matemática.',
                   ]})
    return report


def main() -> int:
    try:
        report = audit()
    except (AuditError, FileNotFoundError, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({'task': 'N2-T6', 'audit_status': 'AUDIT_FAILED',
                          'reason': str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['decision'] == 'N2 FAIL' else 3


if __name__ == '__main__':
    raise SystemExit(main())
