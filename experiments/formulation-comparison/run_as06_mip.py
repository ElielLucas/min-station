"""AS-06: piloto MIP COMP vs COMP+K; A4+K secundário (exploratório)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
for folder in (ROOT,HERE,HERE.parent/'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0,str(folder))

from as06_mip import make_plan, preflight, validate_plan, expected_slots  # noqa: E402
from as06_reporting import run_campaign, verify_campaign, analyze_campaign, verify_analysis  # noqa: E402
from as05_diag_core import _write_json  # noqa: E402
from as05_protocol import sha256_file  # noqa: E402


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    choice=parser.add_mutually_exclusive_group(required=True)
    for flag in ('init-plan','init-replication-plan','check-plan','preflight','execute',
                 'verify','analyze','verify-analysis'):
        choice.add_argument('--'+flag,action='store_true')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--plan',type=Path,default=Path('results/benchmark/as06-mip-plan-v1.json'))
    parser.add_argument('--output-dir',type=Path,default=Path('results/benchmark/as06-mip-screening-001'))
    parser.add_argument('--replication-parent',type=Path,
                        default=Path('results/benchmark/as06-mip-screening-001/analysis'))
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--audit-physical',action='store_true')
    args=parser.parse_args()
    root=args.root.resolve()
    planpath=args.plan if args.plan.is_absolute() else root/args.plan
    folder=args.output_dir if args.output_dir.is_absolute() else root/args.output_dir
    parent=args.replication_parent if args.replication_parent.is_absolute() else root/args.replication_parent
    if args.init_plan or args.init_replication_plan:
        if planpath.exists():
            parser.error('AS06: plano já existe: não sobrescrever')
        stage='replication' if args.init_replication_plan else 'screening'
        plan=make_plan(root,stage=stage,parent_analysis=parent if args.init_replication_plan else None)
        planpath.parent.mkdir(parents=True,exist_ok=True)
        _write_json(planpath,plan)
        print(f'AS06_PLAN_CREATED stage={stage} slots={len(expected_slots(plan))} SHA256={sha256_file(planpath)}')
    elif args.check_plan or args.preflight:
        plan=validate_plan(json.loads(planpath.read_text(encoding='utf-8')),root)
        print(f'AS06_PLAN_VALID stage={plan["stage"]} slots={len(expected_slots(plan))} SHA256={sha256_file(planpath)}')
        if args.preflight:
            print(json.dumps({'schema':'AS06-MIP-PREFLIGHT-v1','cases':preflight(root,plan)},
                             ensure_ascii=False,indent=2))
            print('AS06_PREFLIGHT_PASS (SEM SOLVES)')
    elif args.execute:
        output=run_campaign(root=root,plan_path=planpath,output_dir=folder,resume=args.resume)
        report=verify_campaign(output.parent,root=root)
        print(f'AS06_MIP_COMPLETED stage={report["stage"]} slots={report["expected_slots"]}')
        for case in report['cases']:
            print(case['name'], [(s['seed'],[(r['arm_id'],r['status']) for r in s['runs']])
                                     for s in case['seeds']])
        print('AS06_SCIENTIFIC_GATE PENDING | EXPLORATORY_ONLY')
    elif args.verify:
        report=verify_campaign(folder,root=root,audit_physical=args.audit_physical)
        print(f'AS06_MIP_VERIFIED slots={report["expected_slots"]} audit_physical={args.audit_physical}')
    elif args.analyze:
        output=analyze_campaign(folder,folder/'analysis',root=root)
        print(f'AS06_MIP_ANALYSIS_WRITTEN {output}')
        print('AS06_SCIENTIFIC_GATE PENDING | EXPLORATORY_ONLY')
    elif args.verify_analysis:
        r=verify_analysis(folder/'analysis')
        print(f'AS06_ANALYSIS_VERIFIED decision={r["decision"]}')


if __name__=='__main__':
    main()
