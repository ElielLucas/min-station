"""Gate AS-02 fail-closed: teste não homologa prova nem autoriza piloto difícil."""
from dataclasses import dataclass


@dataclass(frozen=True)
class GateEvidence:
    as01_verdict: str = 'PENDING'
    as01_independent_reviewer: bool = False
    physical_exhaustion_passed: bool = False
    sec59_lp_passed: bool = False
    math_counterexample: bool = False
    as02_independent_reviewer: bool = False


def assess(evidence: GateEvidence) -> str:
    if evidence.math_counterexample or evidence.as01_verdict == 'FAIL':
        return 'MATH_GATE_FAIL'
    if evidence.as01_verdict != 'PASS' or not evidence.as01_independent_reviewer:
        return 'AS01_REVIEW_PENDING'
    if not evidence.physical_exhaustion_passed or not evidence.sec59_lp_passed:
        return 'AS02_VALIDATION_FAIL'
    if not evidence.as02_independent_reviewer:
        return 'AS02_REVIEW_PENDING'
    return 'PASS'


def require_hard_campaign_authorization(evidence: GateEvidence) -> None:
    status = assess(evidence)
    if status != 'PASS':
        raise RuntimeError(f'AS-02 não autoriza campanha difícil: {status}')
