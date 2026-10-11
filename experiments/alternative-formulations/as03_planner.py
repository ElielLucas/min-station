"""AS-03: planejamento de A2/A4 auditável sem construir modelos.

Este módulo não escolhe a melhor política com base em resultados do solver.
Um registro por braço é produzido inclusive na ausência de admissibilidade.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from as03_grouping import (
    POLICY_VERSION, Grouping, NotApplicable, partition_two, refine_four,
)
from as03_size import BuildBudget, BuildDecision, decide_build, estimate_size


@dataclass(frozen=True)
class PlannedArm:
    grouping: Grouping | None
    decision: BuildDecision

    def to_record(self) -> dict[str, Any]:
        return {
            **self.decision.to_record(),
            'blocks': [list(g) for g in self.grouping.blocks] if self.grouping else None,
            'parent_hash': self.grouping.parent_hash if self.grouping else None,
            'instance_hash': self.grouping.instance_hash if self.grouping else None,
            'policy_version': POLICY_VERSION,
        }


def plan_a2(instance, case_name: str, *, policy: str = 'reachability_degree',
            seed: int = 0, budget: BuildBudget | None = None,
            k_cuts: tuple[tuple[str, ...], ...] = ()) -> PlannedArm:
    budget = budget if budget is not None else BuildBudget()
    try:
        grouping = partition_two(instance, policy, seed)
    except NotApplicable as exc:
        return PlannedArm(None, decide_build(case_name, 'A2_PLUS_K', None, None, budget,
                                              reason_if_na=str(exc)))
    estimate = estimate_size(instance, grouping.blocks, k_cuts=k_cuts)
    return PlannedArm(grouping, decide_build(case_name, 'A2_PLUS_K', grouping, estimate, budget))


def plan_a4(instance, case_name: str, parent: PlannedArm, *,
            authorized_by_as05: bool = False, policy: str | None = None,
            seed: int | None = None, budget: BuildBudget | None = None,
            k_cuts: tuple[tuple[str, ...], ...] = ()) -> PlannedArm:
    budget = budget if budget is not None else BuildBudget()
    if not authorized_by_as05:
        return PlannedArm(None, BuildDecision('NOT_AUTHORIZED', 'AS05 não liberou A4',
            case_name, 'A4_PLUS_K', True, None, None, None, None,
            policy or (parent.grouping.policy if parent.grouping else 'reachability_degree'),
            seed if seed is not None else (parent.grouping.seed if parent.grouping else 0)))
    if parent.grouping is None or parent.decision.status != 'READY_FOR_BUILD':
        return PlannedArm(None, decide_build(case_name, 'A4_PLUS_K', None, None, budget,
            reason_if_na='A2 não admissível; não é possível refinar'))
    try:
        grouping = refine_four(instance, parent.grouping, policy=policy, seed=seed,
                               authorized=True)
    except NotApplicable as exc:
        return PlannedArm(None, decide_build(case_name, 'A4_PLUS_K', None, None, budget,
            reason_if_na=str(exc)))
    estimate = estimate_size(instance, grouping.blocks, k_cuts=k_cuts)
    return PlannedArm(grouping, decide_build(case_name, 'A4_PLUS_K', grouping, estimate, budget))
