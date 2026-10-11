"""AS-04: executar uma instância e salvar relatório íntegro/append-only.

Não configura AS-05/AS-06; default é apenas infraestrutura/comparador.
A2 exige AS-01/AS-02 formalmente revisadas; A4 também autorização AS-05.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from as04_runner import run_case  # noqa: E402
from as04_schema import ARM_IDS, SolverPolicy  # noqa: E402
from as04_reporting import publish_run, verify_run  # noqa: E402
from as02_validation_gate import GateEvidence  # noqa: E402
from fc_instances import load_manifest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--case', required=True, help='Nome exato no instances/manifest.csv')
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='Diretório novo: não sobreescrever resultados anteriores')
    parser.add_argument('--arms', default='U,U_K,A2_K')
    parser.add_argument('--mode', choices=('LP', 'MIP'), default='LP')
    parser.add_argument('--budget-s', type=float, default=120.0)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--max-variables', type=int, default=1_000_000)
    parser.add_argument('--as02-gate-file', type=Path,
                        help='Evidência de gate revisado, não um bypass por flag')
    parser.add_argument('--as05-a4-authorized', action='store_true',
                        help='Requer autorização AS-05 verificável separadamente')
    args = parser.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(','))
    if not arms or len(set(arms)) != len(arms) or any(a not in ARM_IDS for a in arms):
        parser.error('Lista de braços inválida ou duplicada')
    rows = load_manifest(args.root / 'instances' / 'manifest.csv')
    matches = [row for row in rows if row['nome'] == args.case]
    if len(matches) != 1:
        parser.error('Instância ausente ou ambígua no manifesto')
    evidence = GateEvidence()
    if args.as02_gate_file is not None:
        gate_data = json.loads(args.as02_gate_file.read_text(encoding='utf-8'))
        evidence = GateEvidence(**gate_data)
        # Declarar booleans no JSON é uma evidência local insuficiente para
        # certificar independência. O revisor deve auditar o arquivo de origem.
    result = run_case(matches[0], root=args.root, arm_ids=arms, mode=args.mode,
                      policy=SolverPolicy(seed=args.seed, threads=args.threads,
                                          budget_s=args.budget_s),
                      as02_gate=evidence, allow_a4=args.as05_a4_authorized,
                      max_variables=args.max_variables)
    path = publish_run(result, args.output_dir, expected_arms=arms)
    assert verify_run(path)
    for arm in result['arms']:
        print(f"{arm['arm_id']} [{arm['status']}] lp={arm['lp_opt_value']} "
              f"mip_bound={arm['mip_numeric_bound']} physical_ub={arm['physical_validated_ub']} "
              f"wall={arm['wall_total_s']:.3f}s")
    for pair in result['comparison']['pairs']:
        print(f"{pair['effect']}: {pair['status']} ({pair['reason']})")
    print(f'AS04_REPORT_WRITTEN {path}')


if __name__ == '__main__':
    main()
