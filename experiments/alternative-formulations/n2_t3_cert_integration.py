"""N2-T3 / E4 (T7--T8): integração opt-in de N1/ENUM/N2 com o root CG.

O controlador numérico da N2-T2B segue tendo como retorno ColumnGenerationResult
UNCERTIFIED. A API pública run_certified_column_generation retorna um envelope
separado com limites certificados SOMENTE para o LP F-CC+K completo.

A certificação captura o DualSnapshot da resolução corrente antes de qualquer
add_column/dispose, usa o grafo H obtido do PRÓPRIO master validado e recalcula
cada prova via os validadores E1/E2/E3. Não existe teste de G2 nem H-K físico.

Todos os três oráculos E4 operam em Python sem novos solves de Gurobi: N2 usa
multiplicadores racionais zero (válidos, potencialmente fracos), sem chamar
SciPy/HiGHS. Tempo de CPU faz parte do wall_time do controlador; Work do solver
permanece contabilizado exclusivamente pelas chamadas master/pricing existentes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType

from n2_t3_cert_box import (
    BoxAbstention,
    build_rational_pricing_lp,
    certify_box_bound,
    evaluate_box_theorem_l,
)
from n2_t3_cert_core import (
    CERTIFIED,
    LP_SCOPE,
    UNCERTIFIED,
    CertifiedIteration,
    GlobalPricingBound,
    analytical_bound_n1,
    evaluate_theorem_l,
    rationalize_snapshot,
)
from n2_t3_cert_enum import (
    EnumAbstention,
    enumerate_global_bound,
    evaluate_enum_theorem_l,
    graph_digest,
)


@dataclass(frozen=True)
class CertificationOptions:
    """Controle de trabalho sem novos solves numéricos de certificação nesta E4.

    enum_cap=None desliga ENUM. use_n2=True liga N2 com theta=nu=0,
    sem LP auxiliar; max_*_vertices limita o custo da aritmética combinatória.
    O tempo disponível é o restante do orçamento global do controlador.
    """

    use_n1: bool = True
    enum_cap: int | None = None
    use_n2: bool = True
    max_enum_vertices: int = 10
    max_n2_vertices: int = 24
    instance_key: str | None = None

    def __post_init__(self):
        for name in ('use_n1', 'use_n2'):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f'{name} deve ser bool')
        if self.enum_cap is not None and (type(self.enum_cap) is not int or self.enum_cap < 0):
            raise ValueError('enum_cap deve ser None ou inteiro >= 0')
        for name in ('max_enum_vertices', 'max_n2_vertices'):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f'{name} deve ser inteiro >= 1')
        if self.instance_key is not None and (not isinstance(self.instance_key, str)
                                              or not self.instance_key.strip()):
            raise ValueError('instance_key deve ser uma string não vazia')
        if not (self.use_n1 or self.enum_cap is not None or self.use_n2):
            raise ValueError('habilite pelo menos uma rota de certificação')


@dataclass(frozen=True)
class SourceAttempt:
    """Resultado e evidência auditável da rota, sem ponteiro para Gurobi."""

    source: str
    status: str
    reason: str
    bound: GlobalPricingBound | None
    verification: CertifiedIteration | None
    elapsed_wall: float


@dataclass(frozen=True)
class IterationCertification:
    """Cópia exclusivamente de objetos racionais/estruturais do snapshot."""

    iteration: int
    revision: int
    solve_id: int
    instance_key: str
    vector_digest: str | None
    k_hash: str
    h_digest: str | None
    attempts: tuple[SourceAttempt, ...]
    best_certificate: CertifiedIteration | None
    elapsed_wall: float
    note: str
    dual: object | None = None  # E5: vetor racional imutável para revalidar provas.


@dataclass(frozen=True)
class CertifiedCGResult:
    """Certificado LP em paralelo ao resultado CG NUMÉRICO (base_result).

    Uma afirmação CERTIFIED aqui é LB<=z_Q do LP F-CC+K, não LB de MIN-STATION.
    Falta verificar validade física de K e U/G2 na E5. Nunca herdar a
    estacionariedade numérica do controlador como convergência certificada.
    """

    base_result: object
    certification_history: tuple[IterationCertification, ...]
    best_certificate: CertifiedIteration | None
    certification_status: str
    scope: str
    justification: str
    total_certification_wall: float
    convergence_status: str = 'NOT_CHECKED_G2'

    @property
    def lb_exact(self) -> Fraction | None:
        return self.best_certificate.lb_exact if self.best_certificate is not None else None

    @property
    def source(self) -> str | None:
        return self.best_certificate.source if self.best_certificate is not None else None


def _attempt(source: str, bound, verifier, started: float, *, clock):
    if isinstance(bound, (EnumAbstention, BoxAbstention)):
        return SourceAttempt(source, UNCERTIFIED, bound.reason, None, None,
                             max(0.0, clock() - started))
    if not isinstance(bound, GlobalPricingBound):
        return SourceAttempt(source, UNCERTIFIED, 'oráculo não forneceu bound global',
                             None, None, max(0.0, clock() - started))
    result = verifier(bound)
    if (not isinstance(result, CertifiedIteration)
            or result.status != CERTIFIED or result.scope != LP_SCOPE
            or result.source != source or type(result.lb_exact) is not Fraction
            or not result.justification):
        reason = (result.justification if isinstance(result, CertifiedIteration)
                  else 'verificador não produziu certificado LP válido')
        return SourceAttempt(source, UNCERTIFIED, reason, None,
                             result if isinstance(result, CertifiedIteration) else None,
                             max(0.0, clock() - started))
    return SourceAttempt(source, CERTIFIED, result.justification, bound, result,
                         max(0.0, clock() - started))


def _failure(source, exc, started, *, clock):
    return SourceAttempt(source, UNCERTIFIED,
                         f'{type(exc).__name__}: {exc}', None, None,
                         max(0.0, clock() - started))


class _CertificationRecorder:
    """Dois estágios: prepare não publica; accept só após check de orçamento.

    O controlador chama prepare somente com o DualSnapshot atual e aceita o
    registro somente se seu próprio teste overrun() não detectou ultrapassagem.
    Certificados de passos anteriores sobrevivem a falhas posteriores.
    """

    def __init__(self, options: CertificationOptions, *, clock=time.monotonic):
        self.options = options
        self.clock = clock
        self.history = []
        self.best = None
        self.total_wall = 0.0
        self._instance_key = None
        self._h_digest = None
        self._k_hash = None

    def prepare(self, master, snapshot, *, iteration: int,
                remaining_time: float | None) -> IterationCertification:
        began = self.clock()
        try:
            H = MappingProxyType({v: frozenset(ns)
                                  for v, ns in master.reach_graph.items()})
            h_hash = graph_digest(H, tuple(master.V))
        except Exception as exc:
            attempt = _failure('IDENTITY', exc, began, clock=self.clock)
            return IterationCertification(
                iteration=iteration,
                revision=snapshot.revision, solve_id=snapshot.solve_id,
                instance_key=self._instance_key or 'UNAVAILABLE',
                vector_digest=None, k_hash=master.k_hash, h_digest=None,
                attempts=(attempt,), best_certificate=None,
                elapsed_wall=max(0.0, self.clock() - began),
                note='falha de identidade do grafo; sem novo certificado',
            )
        # Identidade automática derivada do H efetivamente validado pelo master.
        # O digest do dual adiciona S,T,D,K e números à identidade.
        instance_key = self.options.instance_key or f'E4:{h_hash}:{master.k_hash}'
        if self._instance_key is None:
            self._instance_key, self._h_digest = instance_key, h_hash
            self._k_hash = master.k_hash
        elif (instance_key, h_hash, master.k_hash) != (self._instance_key,
                                                       self._h_digest, self._k_hash):
            return IterationCertification(
                iteration=iteration,
                revision=snapshot.revision, solve_id=snapshot.solve_id,
                instance_key=instance_key, vector_digest=None,
                k_hash=master.k_hash, h_digest=h_hash,
                attempts=(_failure('IDENTITY',
                                   ValueError('master alterou instância/H/K entre iterações'),
                                   began, clock=self.clock),),
                best_certificate=None,
                elapsed_wall=max(0.0, self.clock() - began),
                note='identidade do master divergente; sem novo certificado',
            )

        def available():
            return remaining_time is None or self.clock() - began < remaining_time

        attempts = []
        dual = None
        try:
            # DualSnapshot recebido diretamente do master atual (não reconstruído
            # após invalidação); os IDs e D são validados no core E1.
            dual = rationalize_snapshot(snapshot, instance_key, master.S, master.T,
                                        master.V, master.K)
        except Exception as exc:
            attempts.append(_failure('VECTOR', exc, began, clock=self.clock))

        if dual is not None:
            if self.options.use_n1:
                started = self.clock()
                if available():
                    try:
                        bound = analytical_bound_n1(dual)
                        attempts.append(_attempt('N1', bound,
                                                 lambda b: evaluate_theorem_l(dual, b, dual.D),
                                                 started, clock=self.clock))
                    except Exception as exc:
                        attempts.append(_failure('N1', exc, started, clock=self.clock))
                else:
                    attempts.append(SourceAttempt('N1', UNCERTIFIED,
                                                   'tempo global insuficiente', None, None, 0.0))

            if self.options.enum_cap is not None:
                started = self.clock()
                if len(dual.V) > self.options.max_enum_vertices:
                    attempts.append(SourceAttempt('ENUM', UNCERTIFIED,
                                                   'tamanho excede max_enum_vertices',
                                                   None, None, 0.0))
                elif not available():
                    attempts.append(SourceAttempt('ENUM', UNCERTIFIED,
                                                   'tempo global insuficiente', None, None, 0.0))
                else:
                    try:
                        remain = (None if remaining_time is None else
                                  max(0.0, remaining_time - (self.clock() - began)))
                        bound = enumerate_global_bound(
                            dual, H, self.options.enum_cap, time_limit_seconds=remain)
                        attempts.append(_attempt(
                            'ENUM', bound,
                            lambda b: evaluate_enum_theorem_l(dual, b, dual.D, H,
                                                              self.options.enum_cap),
                            started, clock=self.clock))
                    except Exception as exc:
                        attempts.append(_failure('ENUM', exc, started, clock=self.clock))

            if self.options.use_n2:
                started = self.clock()
                if len(dual.V) > self.options.max_n2_vertices:
                    attempts.append(SourceAttempt('N2', UNCERTIFIED,
                                                   'tamanho excede max_n2_vertices',
                                                   None, None, 0.0))
                elif not available():
                    attempts.append(SourceAttempt('N2', UNCERTIFIED,
                                                   'tempo global insuficiente', None, None, 0.0))
                else:
                    try:
                        lp = build_rational_pricing_lp(dual, H)
                        # E4: theta=nu=0 (sem solver adicional, Work=0 extra).
                        bound = certify_box_bound(dual, H, lp)
                        attempts.append(_attempt(
                            'N2', bound,
                            lambda b: evaluate_box_theorem_l(dual, H, lp, b, dual.D),
                            started, clock=self.clock))
                    except Exception as exc:
                        attempts.append(_failure('N2', exc, started, clock=self.clock))

        certified = [a.verification for a in attempts if a.status == CERTIFIED]
        best = max(certified, key=lambda c: c.lb_exact, default=None)
        return IterationCertification(
            iteration=iteration,
            revision=snapshot.revision,
            solve_id=snapshot.solve_id,
            instance_key=instance_key,
            vector_digest=dual.vector_digest if dual is not None else None,
            k_hash=master.k_hash,
            h_digest=h_hash,
            attempts=tuple(attempts),
            best_certificate=best,
            elapsed_wall=max(0.0, self.clock() - began),
            note=('LP F-CC+K; H-K e G2 não verificados'
                  if best is not None else 'sem novo certificado global verificável'),
            dual=dual,
        )

    def accept(self, event: IterationCertification) -> None:
        if not isinstance(event, IterationCertification):
            raise ValueError('evento de certificação inválido')
        if (self.history and event.iteration <= self.history[-1].iteration):
            raise ValueError('evento de certificação fora da ordem das iterações')
        self.history.append(event)
        self.total_wall += event.elapsed_wall
        if (event.best_certificate is not None and
                (self.best is None or event.best_certificate.lb_exact > self.best.lb_exact)):
            self.best = event.best_certificate

    def finish(self, base_result) -> CertifiedCGResult:
        best = self.best
        return CertifiedCGResult(
            base_result=base_result,
            certification_history=tuple(self.history),
            best_certificate=best,
            certification_status=CERTIFIED if best is not None else UNCERTIFIED,
            scope=LP_SCOPE,
            justification=(
                f'{best.source}: limite inferior racional certificado para LP completo '
                f'F-CC+K; iteração solve_id={best.solve_id}; H-K e G2 pendentes'
                if best is not None else
                'Nenhum bound LP certificado nesta execução; não converter z_R/ObjBound em LB'),
            total_certification_wall=self.total_wall,
        )


def run_certified_column_generation(
        S, T, V, adj, A_r, r, *, options: CertificationOptions | None = None,
        clock=time.monotonic, **cg_kwargs) -> CertifiedCGResult:
    """Executa CG N2-T2B normal com recorder opt-in; retorna envelope LP.

    Não recebe outro certification_hook (reservado à integração interna).
    max_iterations, work_limit, time_limit e parâmetros Gurobi seguem a API CG.
    E5 deverá conferir validade física de K, primal U/G2 e B0 separadamente.
    """
    if options is None:
        options = CertificationOptions()
    if not isinstance(options, CertificationOptions):
        raise ValueError('options deve ser CertificationOptions')
    if 'certification_hook' in cg_kwargs or 'clock' in cg_kwargs:
        raise ValueError('certification_hook e clock são internos à integração')
    # Import tardio: operações aritméticas E1/E2/E3 não requerem Gurobi.
    from n2_t2b_column_generation import run_column_generation

    recorder = _CertificationRecorder(options, clock=clock)
    base = run_column_generation(S, T, V, adj, A_r, r,
                                 certification_hook=recorder, clock=clock, **cg_kwargs)
    return recorder.finish(base)
