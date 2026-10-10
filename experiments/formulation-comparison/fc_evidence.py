"""FC-03: provenance-separated evidence. No Gurobi dependency.

Solver status, independent rational proof, and physical installation validation
are DIFFERENT axes. This module never generates or claims a rational certificate.
A caller must supply a distinct verifier to accept an external proof artifact.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Callable

SOLVER_NUMERIC_OPTIMAL = 'SOLVER_NUMERIC_OPTIMAL'
SOLVER_NUMERIC_BOUND = 'SOLVER_NUMERIC_BOUND'
SOLVER_NUMERIC_STATUS_ONLY = 'SOLVER_NUMERIC_STATUS_ONLY'
NOT_MEASURED = 'NOT_MEASURED'
RATIONAL_VERIFIED = 'RATIONAL_VERIFIED'
NOT_CERTIFIED = 'NOT_CERTIFIED'
INCONCLUSIVE = 'INCONCLUSIVE'
CERTIFIED_GAP_AVAILABLE = 'CERTIFIED_GAP_AVAILABLE'
PHYSICAL_GLOBAL_LB = 'PHYSICAL_GLOBAL_LB'


def context_digest(*, instance_sha256: str, formulation: str, modality: str,
                   k_sha256: str | None, model_complete: bool) -> str:
    """Stable *context* ID, NOT a checksum of the complete constraint matrix."""
    if not instance_sha256 or not formulation or not modality:
        raise ValueError('Identity fields required')
    payload = {
        'schema': 'FC03-model-context-v1', 'instance_sha256': instance_sha256,
        'formulation': formulation, 'modality': modality,
        'k_sha256': k_sha256, 'model_complete': bool(model_complete),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'))
                          .encode('utf-8')).hexdigest()


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return None
    return float(value) if math.isfinite(value) else None


def solver_classification(status: str, *, model_complete: bool,
                          numeric_bound: float | None = None) -> str:
    """Complete model may have numeric solver bound; restricted one never gets global LB."""
    if status == 'OPTIMAL' and model_complete:
        return SOLVER_NUMERIC_OPTIMAL
    if status == 'TIME_LIMIT' and model_complete and _number(numeric_bound) is not None:
        return SOLVER_NUMERIC_BOUND
    if status in ('OPTIMAL', 'TIME_LIMIT', 'INFEASIBLE'):
        return SOLVER_NUMERIC_STATUS_ONLY
    return NOT_MEASURED


def safe_solver_bound(result) -> float | None:
    """Numeric diagnostic lower bound only for a complete MIP with recognized solver state.

    Never use RMP/pricing ObjBound or a truncated model as a MIN-STATION LB.
    """
    if getattr(result, 'formulation', '') not in ('comp_mip', 'fcc_k', 'baseline'):
        return None
    status = getattr(result, 'status_name', '')
    if status not in ('OPTIMAL', 'TIME_LIMIT') or not getattr(result, 'model_complete', False):
        return None
    return _number(getattr(result, 'objective_lb', None))


def physical_upper_bound(result) -> int | None:
    """A validated installation's exact cardinality is an integer feasible UB.

    Do NOT round an unvalidated floating solver objective to fabricate an UB.
    """
    if getattr(result, 'physically_validated', None) is not True:
        return None
    if getattr(result, 'physical_ub_status', '') != 'UB_PHYSICAL_VALIDATED':
        return None
    installed = getattr(result, 'installed', None)
    if installed is None or not isinstance(installed, (tuple, list, set)):
        return None
    if len(set(installed)) != len(installed):
        return None
    objective = _number(getattr(result, 'objective_ub', None))
    if objective is None or abs(objective - len(installed)) > 1e-5:
        return None
    return len(installed)


@dataclass(frozen=True)
class RationalClaim:
    """Untrusted claim presented to independent verifier, never accepted directly."""
    numerator: int
    denominator: int
    proof_path: str
    proof_sha256: str
    proof_id: str
    model_context_sha256: str
    instance_sha256: str
    scope: str = PHYSICAL_GLOBAL_LB


@dataclass(frozen=True)
class VerificationReceipt:
    """Independent verifier output. Must be created by provided verifier callback."""
    accepted: bool
    verifier_id: str
    proof_sha256: str
    model_context_sha256: str
    instance_sha256: str
    exact_numerator: int
    exact_denominator: int
    scope: str


@dataclass(frozen=True)
class VerifiedRationalEvidence:
    value: Fraction
    proof_id: str
    proof_sha256: str
    verifier_id: str
    model_context_sha256: str
    instance_sha256: str
    scope: str


def accept_independent_proof(claim: RationalClaim, *, expected_model_context_sha256: str,
                             expected_instance_sha256: str,
                             verifier: Callable[[RationalClaim], VerificationReceipt]
                             ) -> VerifiedRationalEvidence:
    """Verify provenance, file hash, exact fraction and independent verifier receipt.

    This function never solves or checks rational math itself. The callback MUST
    be a genuine, separately audited mathematical verifier in production. The
    experiment runner does NOT supply such a callback and produces no proofs.
    """
    if not callable(verifier):
        raise ValueError('Independent verifier callable is mandatory')
    if claim.scope != PHYSICAL_GLOBAL_LB:
        raise ValueError('Only a global physical lower-bound proof is acceptable')
    if (not expected_model_context_sha256 or not expected_instance_sha256 or
            claim.model_context_sha256 != expected_model_context_sha256 or
            claim.instance_sha256 != expected_instance_sha256):
        raise ValueError('Proof not bound to the expected model/instance')
    if (isinstance(claim.numerator, bool) or isinstance(claim.denominator, bool) or
            not isinstance(claim.numerator, int) or not isinstance(claim.denominator, int) or
            claim.denominator <= 0 or not claim.proof_id or not claim.proof_sha256):
        raise ValueError('Invalid exact rational/proof identity')
    artifact = Path(claim.proof_path)
    if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest() != claim.proof_sha256:
        raise ValueError('Proof artifact missing or SHA-256 mismatch')
    receipt = verifier(claim)
    if not isinstance(receipt, VerificationReceipt) or not receipt.accepted:
        raise ValueError('Independent verifier did not accept the proof')
    if (not receipt.verifier_id or receipt.proof_sha256 != claim.proof_sha256 or
            receipt.model_context_sha256 != claim.model_context_sha256 or
            receipt.instance_sha256 != claim.instance_sha256 or
            receipt.scope != claim.scope or
            isinstance(receipt.exact_numerator, bool) or
            isinstance(receipt.exact_denominator, bool) or
            receipt.exact_denominator <= 0 or
            Fraction(receipt.exact_numerator, receipt.exact_denominator) !=
            Fraction(claim.numerator, claim.denominator)):
        raise ValueError('Verifier receipt does not match proof and checked context')
    return VerifiedRationalEvidence(
        value=Fraction(claim.numerator, claim.denominator),
        proof_id=claim.proof_id, proof_sha256=claim.proof_sha256,
        verifier_id=receipt.verifier_id, model_context_sha256=claim.model_context_sha256,
        instance_sha256=claim.instance_sha256, scope=claim.scope,
    )


def attach_independent_proof(result, claim: RationalClaim, *, verifier):
    """Opt-in adapter. Never invoked by the experimental solver runner."""
    if not getattr(result, 'model_complete', False):
        raise ValueError('Restricted/truncated model cannot attach this global proof')
    proof = accept_independent_proof(
        claim, expected_model_context_sha256=getattr(result, 'model_context_sha256', None),
        expected_instance_sha256=getattr(result, 'instance_sha256', None), verifier=verifier,
    )
    return replace(result, rational_evidence=proof, certification=RATIONAL_VERIFIED)


def checked_rational_lb(result, *, instance_sha256: str):
    proof = getattr(result, 'rational_evidence', None)
    if (not isinstance(proof, VerifiedRationalEvidence) or
            proof.scope != PHYSICAL_GLOBAL_LB or not getattr(result, 'model_complete', False) or
            proof.instance_sha256 != instance_sha256 or
            proof.model_context_sha256 != getattr(result, 'model_context_sha256', None) or
            not proof.verifier_id or not proof.proof_id):
        return None
    return proof.value


def certified_gap(result, *, instance_sha256: str):
    """Exactly computed gap only if same-instance LB proof AND validated physical UB."""
    lb = checked_rational_lb(result, instance_sha256=instance_sha256)
    ub = physical_upper_bound(result)
    if lb is None or ub is None or lb > ub:
        return INCONCLUSIVE, None, None
    gap = Fraction(ub) - lb
    return CERTIFIED_GAP_AVAILABLE, gap, (gap / ub if ub > 0 else None)


def exact_text(value: Fraction | None) -> str:
    if value is None:
        return ''
    return f'{value.numerator}/{value.denominator}'
