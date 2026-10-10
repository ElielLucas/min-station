"""FC-02: avaliação pura da comparabilidade do par inteiro COMP+K / F-CC+K.

Não consulta solver nem reexecuta modelos. Atesta somente integridade do
protocolo experimental; não é certificado racional de otimalidade (FC-03).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PairAssessment:
    status: str
    reason: str = ''
    instance_sha256: str | None = None
    k_sha256: str | None = None


def assess_primary_pair(instance, comp, fcc):
    """Somente `PAIR_VALID` autoriza análise pareada.

    Casos faltantes/interrompidos NÃO constituem resultados completos. Erros
    explícitos de identidade, corte ou testemunha são erros de integridade.
    """
    if comp is None or fcc is None:
        return PairAssessment('PAIR_NOT_AVAILABLE', 'Um ou ambos os braços primários não executados')

    incomplete = ('CAP_EXCEEDED', 'TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER',
                  'TIMEOUT_VALIDATION', 'SOLVER_UNAVAILABLE', 'WORKER_ERROR')
    for result in (comp, fcc):
        if result.status_name == 'WORKER_ERROR' and (
                'INTEGRITY_ERROR' in result.reason or 'corte inválido' in result.reason):
            return PairAssessment('INTEGRITY_ERROR',
                                  f'Falha na integridade/validade dos cortes: {result.reason.splitlines()[0]}')

    valid_solver_statuses = {'OPTIMAL', 'TIME_LIMIT', 'INFEASIBLE'}
    if (comp.status_name in incomplete or fcc.status_name in incomplete or
            comp.status_name not in valid_solver_statuses or
            fcc.status_name not in valid_solver_statuses):
        return PairAssessment('PAIR_NOT_AVAILABLE',
                              f'Execução incompleta/não interpretável: '
                              f'COMP={comp.status_name}, F-CC+K={fcc.status_name}')

    expected_instance = instance.instance_sha256
    if (not expected_instance or comp.instance_sha256 != expected_instance or
            fcc.instance_sha256 != expected_instance):
        return PairAssessment('INTEGRITY_ERROR', 'Hash da instância divergente ou ausente')

    if (not comp.k_sha256 or not fcc.k_sha256 or
            comp.k_sha256 != fcc.k_sha256):
        return PairAssessment('INTEGRITY_ERROR', 'Hash de K divergente ou ausente', expected_instance)

    if (not comp.k_validated or not fcc.k_validated or
            comp.n_K is None or fcc.n_K is None or
            comp.n_K != fcc.n_K or
            comp.n_K_added != comp.n_K or fcc.n_K_added != fcc.n_K):
        return PairAssessment('INTEGRITY_ERROR',
                              'Cortes K não validados ou não inteiramente aplicados',
                              expected_instance, comp.k_sha256)

    for name, result in (('COMP', comp), ('F-CC+K', fcc)):
        if result.objective_ub is not None and result.physically_validated is not True:
            return PairAssessment('INVALID_PHYSICAL_WITNESS',
                                  f'{name} tem incumbente sem validação física independente',
                                  expected_instance, comp.k_sha256)

    return PairAssessment('PAIR_VALID', '', expected_instance, comp.k_sha256)
