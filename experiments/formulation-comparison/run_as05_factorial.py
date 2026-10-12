"""Executa/compara seis braços LP exploratórios: U, U+K, A2, A2+K, A4, A4+K."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE, HERE.parent/'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as05_factorial import (  # noqa: E402
    analyze_experiment, make_plan, preflight_sizes, run_experiment, validate_plan, verify_experiment,
)
from as05_diag_core import _write_json  # noqa: E402
from as04_schema import digest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--init-plan', action='store_true')
    selection.add_argument('--check-plan', action='store_true')
    selection.add_argument('--preflight', action='store_true')
    selection.add_argument('--execute', action='store_true')
    selection.add_argument('--verify', action='store_true')
    selection.add_argument('--analyze', action='store_true')
    parser.add_argument('--plan', type=Path,
                        default=Path('results/benchmark/as05-factorial-plan-v1.json'))
    parser.add_argument('--output-dir', type=Path,
                        default=Path('results/benchmark/as05-factorial-001'))
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.init_plan:
        if args.plan.exists():
            parser.error('FACTORIAL: plano já existe; não sobrescrever')
        p = make_plan(root)
        args.plan.parent.mkdir(parents=True, exist_ok=True)
        _write_json(args.plan, p)
        print(f'AS05_FACTORIAL_PLAN_CREATED SHA256={digest(p)} (SEM SOLVES)')
    elif args.check_plan:
        p = validate_plan(json.loads(args.plan.read_text(encoding='utf-8')), root)
        print(f'AS05_FACTORIAL_PLAN_VALID SHA256={digest(p)} (SEM SOLVES)')
    elif args.preflight:
        p = validate_plan(json.loads(args.plan.read_text(encoding='utf-8')), root)
        rows = preflight_sizes(root, p)
        print(json.dumps({'schema':'AS05-FACTORIAL-PREFLIGHT-v1',
                          'plan_sha256':digest(p),'sizes_without_A6':rows},
                         ensure_ascii=False, indent=2))
        print('AS05_FACTORIAL_PREFLIGHT_PASS (SEM SOLVES; tamanho antes de A6)')
    elif args.execute:
        path = run_experiment(root=root, plan_path=args.plan, output_dir=args.output_dir,
                              resume=args.resume)
        report = verify_experiment(path.parent)
        print(f'AS05_FACTORIAL_COMPLETED cases={len(report["cases"])} arms={len(report["expected_arms"])}')
        for case in report['cases']:
            print(case['name'], [(r['arm_id'], r['status']) for r in case['runs']])
        print(f'AS05_FACTORIAL_REPORT_WRITTEN {path}')
        print('AS05_SCIENTIFIC_GATE PENDING | EXPLORATORY_ONLY')
    elif args.verify:
        p = verify_experiment(args.output_dir)
        print(f'AS05_FACTORIAL_VERIFIED cases={len(p["cases"])} arms={len(p["expected_arms"])}')
    elif args.analyze:
        path = analyze_experiment(args.output_dir, args.output_dir/'analysis')
        print(f'AS05_FACTORIAL_ANALYSIS_WRITTEN {path}')
        print('AS05_SCIENTIFIC_GATE PENDING | EXPLORATORY_ONLY')


if __name__ == '__main__':
    main()
