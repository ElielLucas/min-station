"""AS-05: registrar plano prospectivo ou executar piloto com gate externo revisado."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for directory in (ROOT, HERE, HERE.parent/'alternative-formulations'):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from as05_protocol import make_plan, plan_digest, sha256_file, read_plan  # noqa: E402
from as05_pilot import run_pilot, verify_pilot  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--init-plan',type=Path,help='Arquivo NOVO para adendo prospectivo sem solves')
    group.add_argument('--check-plan',type=Path,help='Validar plano sem solves')
    group.add_argument('--execute',action='store_true',help='Rodar 6x3 braços com Gurobi e gates')
    group.add_argument('--execute-exploratory',action='store_true',
                       help='Rodar piloto exploratorio com autorizacao expressa do responsavel')
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--gate-file',type=Path)
    parser.add_argument('--owner-authorization',type=Path,
                        help='Registro versionado da autorizacao do responsavel (exploratorio)')
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--max-variables',type=int,default=1_000_000)
    args = parser.parse_args()
    if args.init_plan:
        if args.init_plan.exists():
            parser.error('Destino do plano já existe; adendo é append-only')
        as00path = args.root/'results/benchmark/protocol.json'
        as00 = json.loads(as00path.read_text(encoding='utf-8'))
        plan = make_plan(as00, as00_sha256=sha256_file(as00path),
                         manifest_sha256=sha256_file(args.root/'instances/manifest.csv'))
        args.init_plan.parent.mkdir(parents=True,exist_ok=True)
        args.init_plan.write_text(json.dumps(plan,ensure_ascii=False,sort_keys=True,
                                            indent=2)+'\n',encoding='utf-8')
        print(f'AS05_PLAN_CREATED {args.init_plan} SHA256={plan_digest(plan)} (SEM SOLVES)')
        return
    if args.check_plan:
        plan,_ = read_plan(args.check_plan,args.root)
        print(f'AS05_PLAN_VALID SHA256={plan_digest(plan)} (SEM SOLVES)')
        return
    if not (args.plan and args.gate_file and args.output_dir):
        parser.error('--execute requer --plan, --gate-file e --output-dir')
    if args.execute_exploratory and not args.owner_authorization:
        parser.error('--execute-exploratory exige --owner-authorization')
    if args.execute and args.owner_authorization:
        parser.error('--execute nao aceita --owner-authorization; utilize --execute-exploratory')
    report_path = run_pilot(root=args.root,plan_path=args.plan,evidence_path=args.gate_file,
                            output_dir=args.output_dir,max_variables=args.max_variables,
                            owner_authorization_path=args.owner_authorization)
    report = verify_pilot(args.output_dir)
    if args.execute_exploratory:
        print(f'AS05_EXPLORATORY_SCREENING {report["screening_decision"]["verdict"]}')
        print('AS05_SCIENTIFIC_GATE PENDING (autorizacao do responsavel nao equivale a revisao independente)')
    else:
        print(f'AS05_GATE {report["decision"]["verdict"]}: {report["decision"]["reason"]}')
    print(f'AS05_REPORT_WRITTEN {report_path}')


if __name__=='__main__':
    main()
