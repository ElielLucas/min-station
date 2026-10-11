"""AS-04: pareamento estrito e efeitos identificados por contraste.

Par censurado preservado no denominador; sem preenchimento de medidas ausentes.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from as04_schema import ArmResult, EFFECTS, digest


@dataclass(frozen=True)
class Pair:
    effect: str
    left: str
    right: str
    status: str
    reason: str
    lp_delta: float | None = None
    wall_delta_s: float | None = None

    def to_dict(self):
        return vars(self).copy()


def assess_pair(left: ArmResult | None, right: ArmResult | None, *, effect: str) -> Pair:
    if effect not in EFFECTS:
        raise ValueError('Contraste não preregistrado')
    a, b = EFFECTS[effect]
    if left is None or right is None:
        return Pair(effect, a, b, 'NOT_MEASURED', 'Braço ausente; manter no denominador')
    if left.arm_id != a or right.arm_id != b:
        raise ValueError('Contraste com braços trocados')
    fields = ('case_name', 'mode', 'instance_sha256', 'structural_sha256',
              'solver_policy_sha256', 'reference_k_sha256')
    for f in fields:
        lv, rv = getattr(left, f), getattr(right, f)
        if lv and rv and lv != rv:
            return Pair(effect, a, b, 'INTEGRITY_ERROR',
                        f'Divergência explícita de {f}')
    if not left.model_complete or not right.model_complete:
        return Pair(effect, a, b, 'NOT_COMPARABLE',
                    f'Modelo não completo: {a}={left.status}; {b}={right.status}')
    if any(not getattr(left, f) or not getattr(right, f) for f in fields):
        return Pair(effect, a, b, 'INTEGRITY_ERROR', 'Identidade/K/política ausente de modelo completo')
    if (digest(left.solver_policy) != left.solver_policy_sha256 or
            digest(right.solver_policy) != right.solver_policy_sha256):
        return Pair(effect, a, b, 'INTEGRITY_ERROR', 'Conteúdo da política difere do SHA declarado')
    if not left.k_validated or not right.k_validated:
        return Pair(effect, a, b, 'INTEGRITY_ERROR', 'K não validado por fonte independente')
    if a == 'U':
        if left.applied_k_sha256 is not None or right.applied_k_sha256 != right.reference_k_sha256:
            return Pair(effect, a, b, 'INTEGRITY_ERROR', 'Ablação não é WITHOUT_K ou U_K não aplica K')
    elif (left.applied_k_sha256 != right.applied_k_sha256 or
          left.applied_k_sha256 != left.reference_k_sha256):
        return Pair(effect, a, b, 'INTEGRITY_ERROR', 'Hashes de K diferentes')
    if left.mode != right.mode:
        return Pair(effect, a, b, 'INTEGRITY_ERROR', 'Modalidades LP/MIP divergentes')
    if not (left.model_complete and right.model_complete):
        return Pair(effect, a, b, 'NOT_COMPARABLE', 'Modelo incompleto, restrito ou não construído')
    if left.status != 'OPTIMAL_NUMERIC' or right.status != 'OPTIMAL_NUMERIC':
        return Pair(effect, a, b, 'MATCHED_CENSORED', f'{a}={left.status}; {b}={right.status}')
    if left.mode == 'LP':
        if left.lp_opt_value is None or right.lp_opt_value is None:
            return Pair(effect, a, b, 'MATCHED_CENSORED', 'LP ótimo ausente')
        return Pair(effect, a, b, 'MATCHED_COMPLETE', 'LP ótimo numérico em ambos',
                    right.lp_opt_value-left.lp_opt_value,
                    (right.wall_total_s-left.wall_total_s if
                     left.wall_total_s is not None and right.wall_total_s is not None else None))
    if left.physical_validated_ub is None or right.physical_validated_ub is None:
        return Pair(effect, a, b, 'MATCHED_CENSORED', 'MIP sem duas instalações validadas fisicamente')
    return Pair(effect, a, b, 'MATCHED_COMPLETE', 'MIP com duas instalações validadas',
                None, (right.wall_total_s-left.wall_total_s if
                       left.wall_total_s is not None and right.wall_total_s is not None else None))


def compare_case(records: list[ArmResult], *, expected_effects=tuple(EFFECTS)):
    by_arm = {}
    for result in records:
        if result.arm_id in by_arm:
            raise ValueError('Linha duplicada por braço/modo; comparar LP e MIP separadamente')
        by_arm[result.arm_id] = result
    pairs = [assess_pair(by_arm.get(EFFECTS[e][0]), by_arm.get(EFFECTS[e][1]), effect=e)
             for e in expected_effects]
    return {'pairs': [p.to_dict() for p in pairs],
            'pair_status_counts': dict(Counter(p.status for p in pairs)),
            'expected_arm_count': len(by_arm),
            'observed_arm_count': len(records)}
