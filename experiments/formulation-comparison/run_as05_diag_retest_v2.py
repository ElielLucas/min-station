"""AS05-DIAG-V2: novo plano versionado para reparar política A2 e validação K."""
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

from as05_diag_retest_v2 import (  # noqa: E402
    analyze_retest, make_retest_plan, run_retest_stage,
    validate_retest_plan, verify_retest_stage, STAGES,
)
from as05_diag_core import _write_json  # noqa: E402
from as04_schema import digest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--init-plan', action='store_true')
    group.add_argument('--check-plan', action='store_true')
    group.add_argument('--stage', choices=STAGES)
    group.add_argument('--verify', type=Path)
    group.add_argument('--analyze', action='store_true')
    parser.add_argument('--plan', type=Path,
                        default=Path('results/benchmark/as05-diagnostic-retest-plan-v2.json'))
    parser.add_argument('--results-dir', type=Path,
                        default=Path('results/benchmark/as05-diagnostic-v2-001'))
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.init_plan:
        if args.plan.exists():
            parser.error('RETEST-V2: plano já existe; não sobrescrever')
        plan = make_retest_plan(args.root)
        args.plan.parent.mkdir(parents=True, exist_ok=True)
        _write_json(args.plan, plan)
        print(f'AS05_RETEST_V2_PLAN_CREATED SHA256={digest(plan)} (SEM SOLVES)')
    elif args.check_plan:
        plan = validate_retest_plan(json.loads(args.plan.read_text(encoding='utf-8')), args.root)
        print(f'AS05_RETEST_V2_PLAN_VALID SHA256={digest(plan)} (SEM SOLVES)')
    elif args.stage:
        target = args.output_dir or args.results_dir/args.stage
        report_path = run_retest_stage(root=args.root, plan_path=args.plan,
                                       stage=args.stage, output_dir=target, resume=args.resume)
        report = verify_retest_stage(report_path.parent)
        for case in report['cases']:
            print(case['name'], [(r.get('arm_id') or 'CUTS', r['status']) for r in case['runs']])
        print(f'AS05_RETEST_V2_STAGE_COMPLETED {args.stage} report={report_path}')
        print('AS05_SCIENTIFIC_GATE PENDING | DIAGNOSTIC_ONLY')
    elif args.verify:
        report = verify_retest_stage(args.verify)
        print(f'AS05_RETEST_V2_VERIFIED {report["stage"]} cases={len(report["cases"])}')
    else:
        target = args.output_dir or args.results_dir/'analysis'
        output = analyze_retest(root=args.root, plan_path=args.plan,
                                results_dir=args.results_dir, output_dir=target)
        print(f'AS05_RETEST_V2_ANALYSIS_WRITTEN {output}')
        print('AS05_SCIENTIFIC_GATE PENDING | DIAGNOSTIC_ONLY')


if __name__ == '__main__':
    main()
