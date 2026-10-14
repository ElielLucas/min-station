#!/usr/bin/env python3
"""AS13 installation gate: required proof files must exist in THIS checkout.

This is not a mathematical verifier and never turns the Opus FAIL into GO.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    'docs/technical/reference/formulacoes/as13-cortes-h2-hl-fundamentos.md': ('Proposição P1', 'Proposição P2'),
    'docs/technical/reference/formulacoes/as13-prova-h2.md': ('Teorema H2', 'Certificação parcial segura'),
    'docs/technical/reference/formulacoes/as13-prova-hl.md': ('Teorema HL', 'projeção exata'),
    'docs/technical/reference/experimentos/as13-testemunhas-e-gate.md': ('CG/zero-half', 'AS14'),
    'experiments/cuts/verify_as13_foundations.py': ('verify_k4_exhaustive_physical', 'physical_optimum_by_cardinality'),
    'experiments/cuts/test_as13_foundations.py': ('test_as13_05_k4_exhaustive_rejects_one_false_positive',
                                                 'test_as13_05_ip_is_computed_from_physical_oracle'),
}


def check_installation(root: Path) -> dict:
    root = root.resolve()
    errors = []
    installed = []
    for rel, phrases in REQUIRED.items():
        p = root / rel
        if not p.is_file():
            errors.append(f'MISSING: {rel}')
            continue
        content = p.read_text(encoding='utf-8')
        if len(content.strip()) < 150:
            errors.append(f'EMPTY_OR_TRUNCATED: {rel}')
            continue
        for phrase in phrases:
            if phrase not in content:
                errors.append(f'MISSING_EXPECTED_SECTION: {rel} -> {phrase}')
        installed.append(rel)
    status = 'FILES_PRESENT_NOT_SCIENTIFIC_GO' if not errors else 'FAIL_MISSING_DELIVERABLES'
    return {'schema': 'AS13-INSTALLATION-GATE-v1', 'root': str(root),
            'status': status, 'installed_files_checked': len(installed),
            'required_file_count': len(REQUIRED), 'errors': errors,
            'scientific_gate': 'FAIL_UNTIL_NEW_INDEPENDENT_REVIEW',
            'as14': 'BLOCKED'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    data = check_installation(args.root)
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not data['errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
