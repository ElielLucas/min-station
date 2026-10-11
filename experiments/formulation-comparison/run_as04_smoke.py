"""Smoke local AS-04: compiladores U/U+K/A2+K com HiGHS, SEM campanha difícil.

O backend experimental principal da AS-04 é Gurobi em worker supervisionado;
este smoke apenas confirma integração estrutural e LP de regressão.
"""
from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE.parent / 'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from experiments.cuts.synthetic import make_Sec59  # noqa: E402
from as02_model_a import Instance, prepare_K  # noqa: E402
from as02_solve import solve_scipy  # noqa: E402
from as04_arms import compile_arm, k_digest  # noqa: E402
from as04_schema import ArmResult, SolverPolicy  # noqa: E402
from as04_compare import compare_case  # noqa: E402


def main():
    sample = make_Sec59(L=7)
    inst = Instance.from_synthetic(sample)
    cuts = prepare_K(inst, sample[3], inst.r)
    khash = k_digest(inst, cuts)
    policy = SolverPolicy()
    rows = []
    for arm in ('U', 'U_K', 'A2_K'):
        compiled, phash = compile_arm(arm, inst, cuts, mode='LP', seed=0)
        result = solve_scipy(compiled, time_limit=25)
        if result.status != 'OPTIMAL':
            raise RuntimeError(f'Sec59 não resolvido: {arm}={result.status}')
        rows.append(ArmResult(
            case_name='Sec59(L=7)', arm_id=arm, mode='LP', status='OPTIMAL_NUMERIC',
            instance_sha256='synthetic-sec59-l7', structural_sha256='sec59-stable',
            reference_k_sha256=khash,
            applied_k_sha256=None if arm == 'U' else khash,
            k_validated=True, solver_policy_sha256=policy.sha256,
            solver_policy=asdict(policy),
            model_complete=True, lp_opt_value=result.objective,
            partition_sha256=phash, n_variables=len(compiled.variables),
            n_constraints=len(compiled.equations), n_nonzeros=compiled.n_nonzeros))
        print(f'{arm}: LP={result.objective:.9f} vars={len(compiled.variables)}')
    assert abs(rows[1].lp_opt_value-11/3) < 1e-6
    # A política automática AS-03 NÃO é a partição especial do testemunho AS-02.
    assert abs(rows[2].lp_opt_value-11/3) < 1e-6
    from as02_model_a import compile_a
    special = solve_scipy(compile_a(inst, (('s1', 's2'), ('s3',)), cuts,
                                    relax=True), time_limit=25)
    assert special.status == 'OPTIMAL' and abs(special.objective-9/2) < 1e-6
    print(f'A2_K_PARTICAO_TESTEMUNHA: LP={special.objective:.9f} (não pré-selecionada pela AS-03)')
    comparison = compare_case(rows)
    assert comparison['pairs'][0]['status'] == 'MATCHED_COMPLETE'
    assert comparison['pairs'][1]['status'] == 'MATCHED_COMPLETE'
    assert comparison['pairs'][2]['status'] == 'NOT_MEASURED'
    print('AS04_SMOKE_PASS (HiGHS local; sem campanha ou revisão matemática independente)')


if __name__ == '__main__':
    main()
