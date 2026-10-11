"""Smoke test estrutural AS-03, sem Gurobi, para executar no repositório.

PYTHONPATH=. python3 experiments/alternative-formulations/run_as03_smoke.py
"""
from __future__ import annotations

from as02_model_a import Instance, compile_a
from as03_grouping import is_nested
from as03_planner import plan_a2, plan_a4
from as03_size import BuildBudget


def main():
    sample = Instance(
        V=('a', 'b', 'c', 'd', 'e', 'f', 'g'),
        S=('a', 'b', 'c', 'd'),
        T=('d', 'e', 'f', 'g'),
        A_r=(('a', 'e'), ('e', 'b'), ('b', 'f'), ('f', 'c'),
             ('c', 'g'), ('g', 'd'), ('d', 'a')),
        r=2,
    )
    a2 = plan_a2(sample, 'smoke-as03', policy='reachability_degree',
                 budget=BuildBudget(max_variables=100000))
    assert a2.decision.status == 'READY_FOR_BUILD'
    a4_hold = plan_a4(sample, 'smoke-as03', a2)
    assert a4_hold.decision.status == 'NOT_AUTHORIZED'
    # Autorização de fixture de teste; NÃO significa gate AS-05 realizado.
    a4 = plan_a4(sample, 'smoke-as03', a2, authorized_by_as05=True)
    assert a4.decision.status == 'READY_FOR_BUILD'
    assert is_nested(a2.grouping.blocks, a4.grouping.blocks)
    for arm in (a2, a4):
        c = compile_a(sample, arm.grouping.blocks, relax=True)
        assert len(c.variables) == arm.decision.estimate.variables
        assert len(c.equations) == arm.decision.estimate.constraints
        print(f'{arm.decision.arm_id}: k={arm.grouping.k} '
              f'vars={len(c.variables)} rows={len(c.equations)} '
              f'partition_sha256={arm.grouping.partition_hash[:16]}...')
    low_cap = plan_a2(sample, 'smoke-as03-cap', budget=BuildBudget(max_variables=1))
    assert low_cap.decision.status == 'NOT_BUILT_SIZE'
    assert low_cap.decision.applicable and low_cap.decision.measured_lp is None
    print('AS03_SMOKE_PASS (estrutural; sem LP/MIP e sem gate AS-05)')


if __name__ == '__main__':
    main()
