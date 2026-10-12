"""AS05-DIAG: congelar plano e executar diagnóstico pós-AS05 sem promoção científica."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (ROOT, HERE, HERE.parent / 'alternative-formulations'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from as05_diag_core import (  # noqa: E402
    STAGES, make_diagnostic_plan, run_diagnostic_stage,
    validate_diagnostic_plan, verify_diagnostic_stage, _write_json,
)
from as04_schema import digest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--init-plan', type=Path)
    group.add_argument('--check-plan', type=Path)
    group.add_argument('--stage', choices=STAGES)
    group.add_argument('--verify', type=Path)
    parser.add_argument('--pilot-dir', type=Path,
                        default=Path('results/benchmark/as05-pilot-owner-exploratory-001'))
    parser.add_argument('--plan', type=Path,
                        default=Path('results/benchmark/as05-diagnostic-plan-v1.json'))
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--resume', action='store_true', help='Retomar checkpoint íntegro por braço')
    args = parser.parse_args()
    if args.init_plan:
        if args.init_plan.exists():
            parser.error('DIAG: plano é append-only; não sobrescrever')
        plan = make_diagnostic_plan(args.root, args.root / args.pilot_dir)
        args.init_plan.parent.mkdir(parents=True, exist_ok=True)
        _write_json(args.init_plan, plan)
        print(f'AS05_DIAG_PLAN_CREATED SHA256={digest(plan)} (SEM SOLVES)')
        return
    if args.check_plan:
        plan = validate_diagnostic_plan(json.loads(args.check_plan.read_text(encoding='utf-8')),
                                        args.root)
        print(f'AS05_DIAG_PLAN_VALID SHA256={digest(plan)} (SEM SOLVES)')
        return
    if args.verify:
        report = verify_diagnostic_stage(args.verify)
        print(f'AS05_DIAG_VERIFY_PASS stage={report["stage"]} cases={len(report["cases"])}')
        return
    if not args.output_dir:
        parser.error('--stage exige --output-dir')
    path = run_diagnostic_stage(root=args.root, plan_path=args.plan, stage=args.stage,
                                output_dir=args.output_dir, resume=args.resume)
    report = verify_diagnostic_stage(path.parent)
    print(f'AS05_DIAG_STAGE_COMPLETED {args.stage} cases={len(report["cases"])}')
    for case in report['cases']:
        print(case['name'], [(x.get('arm_id') or 'CUTS', x['status']) for x in case['runs']])
    print(f'AS05_DIAG_REPORT_WRITTEN {path}')
    print('AS05_SCIENTIFIC_GATE PENDING | DIAGNOSTIC_ONLY')


if __name__ == '__main__':
    main()
