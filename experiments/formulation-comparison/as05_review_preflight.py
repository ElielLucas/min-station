"""Diagnóstico documental AS-05: NÃO homologa ciência nem executa solves.

Uso:
  PYTHONPATH=. python3 experiments/formulation-comparison/as05_review_preflight.py \
    --root . --plan results/benchmark/as05-prospective-plan-v1.json \
    --evidence docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json

A revisão independente deve ser verificada externamente por pessoa distinta.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALTERNATIVE = HERE.parent / 'alternative-formulations'
for folder in (HERE, ALTERNATIVE):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root: Path, plan_path: Path, evidence_path: Path) -> dict:
    """Retorna bloqueios; nenhuma combinação de strings certifica autoria independente."""
    root = root.resolve()
    problems: list[str] = []
    notes: list[str] = []
    digest = None
    if not plan_path.is_file():
        problems.append(f'PLANO_AUSENTE: {plan_path}')
    else:
        try:
            from as05_protocol import read_plan, plan_digest
            plan, _ = read_plan(plan_path, root)
            digest = plan_digest(plan)
            for case in plan['pilot_cases']:
                source = root / case['source_file']
                if not source.is_file():
                    problems.append(f'INSTANCIA_AUSENTE: {case["name"]}: {source}')
                elif _fingerprint(source) != case['source_sha256']:
                    problems.append(f'INSTANCIA_HASH_DIVERGENTE: {case["name"]}')
            notes.append('Plano verificado contra AS-00 e manifesto; sem resolução de modelos')
        except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            problems.append(f'PLANO_INVALIDO: {type(exc).__name__}: {exc}')
    if not evidence_path.is_file():
        problems.append(f'EVIDENCIA_AUSENTE: {evidence_path}')
        evidence = {}
    else:
        try:
            evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
            if not isinstance(evidence, dict):
                raise ValueError('Raiz JSON não é objeto')
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(f'EVIDENCIA_INVALIDA: {type(exc).__name__}: {exc}')
            evidence = {}
    verdict = evidence.get('as04_verdict')
    if verdict != 'PASS':
        problems.append(f'AS04_NAO_HOMOLOGADA: as04_verdict={verdict!r}')
    data = evidence.get('as02_evidence')
    if isinstance(data, dict):
        from as02_validation_gate import GateEvidence, assess
        try:
            gate_status = assess(GateEvidence(**data))
            if gate_status != 'PASS':
                problems.append(f'AS01_AS02_NAO_HOMOLOGADAS: {gate_status}')
        except (TypeError, ValueError) as exc:
            problems.append(f'AS02_GATE_MALFORMADO: {exc}')
    else:
        problems.append('AS02_EVIDENCIA_AUSENTE')
    reviewers = evidence.get('reviewers')
    if not isinstance(reviewers, dict):
        problems.append('REVISORES_AUSENTES')
        reviewers = {}
    for feature in ('as01', 'as02', 'as04'):
        r = reviewers.get(feature)
        if not isinstance(r, dict):
            problems.append(f'REVISOR_{feature.upper()}_AUSENTE')
            continue
        for field in ('author', 'reviewer', 'evidence_path'):
            if not isinstance(r.get(field), str) or not r[field].strip():
                problems.append(f'REVISOR_{feature.upper()}_{field.upper()}_AUSENTE')
        if (isinstance(r.get('author'), str) and r.get('author') and
                r.get('author') == r.get('reviewer')):
            problems.append(f'REVISOR_{feature.upper()}_IGUAL_AO_AUTOR')
        path = r.get('evidence_path')
        if isinstance(path, str) and path.strip():
            report = Path(path)
            if not report.is_absolute():
                report = root / report
            if not report.is_file():
                problems.append(f'PARECER_{feature.upper()}_ARQUIVO_AUSENTE: {report}')
            elif report.stat().st_size == 0:
                problems.append(f'PARECER_{feature.upper()}_ARQUIVO_VAZIO: {report}')
    notes.append('O gate e os caminhos só verificam declarações; não atestam independência nem conteúdo dos pareceres')
    notes.append('Nenhuma campanha LP/MIP foi executada por esta ferramenta')
    return {'schema': 'AS05-REVIEW-PREFLIGHT-v1',
            'status': 'BLOCKED' if problems else 'DECLARATIONS_COMPLETE_UNVERIFIED',
            'plan_digest': digest, 'blockers': problems, 'notes': notes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--plan', type=Path, default=Path('results/benchmark/as05-prospective-plan-v1.json'))
    parser.add_argument('--evidence', type=Path, default=Path('docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json'))
    parser.add_argument('--output', type=Path, help='JSON diagnóstico opcional; não é certificado')
    args = parser.parse_args()
    root = args.root.resolve()
    plan = args.plan if args.plan.is_absolute() else root / args.plan
    evidence = args.evidence if args.evidence.is_absolute() else root / args.evidence
    report = inspect(root, plan, evidence)
    message = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    print(message, end='')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(message, encoding='utf-8')
    return 2 if report['blockers'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
