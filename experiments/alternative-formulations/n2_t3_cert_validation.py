"""N2-T3 / E5: evidências físicas de K, primal racional U/G2 e baseline B0.

ATENÇÃO: CERTIFIED no E1–E4 refere-se apenas ao LP completo F-CC+K.
A promoção para MIN-STATION exige validação nova dos cortes da própria instância,
identidade integral do grafo/alcance e recomputação das provas dos oráculos.
B0 é independente; sem prova verificável nunca é certificado.
"""
from __future__ import annotations

import itertools
import math
import time
import sys
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType

# ruff: noqa: E402
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from cuts import assert_valid_cuts
from n2_t3_cert_box import build_rational_pricing_lp, evaluate_box_theorem_l
from n2_t3_cert_core import (
    CERTIFIED, LP_SCOPE, UNCERTIFIED, CertifiedIteration, _cuts, _rational,
    _tag, _validated_dual, _vertices, canonical_k_hash, evaluate_theorem_l,
    _integer_rounding_formula, vector_digest,
)
from n2_t3_cert_enum import evaluate_enum_theorem_l, graph_digest
from n2_t3_cert_integration import CertifiedCGResult, CertificationOptions, run_certified_column_generation

ZERO = Fraction(0)
ONE = Fraction(1)
TOLERANCE = Fraction(1, 1_000_000)
PHYSICAL_SCOPE = 'MIN_STATION_INTEGER_LOWER_BOUND'
G2_PASSED = 'CONVERGED_CERTIFIED'
G2_NOT_PROVED = 'NOT_CONVERGED_CERTIFIED'


def _seal_map(mapping):
    return MappingProxyType(dict(mapping))


def _rational_map(data, keys, name):
    if not isinstance(data, Mapping) or set(data) != set(keys):
        raise ValueError(f'{name}: índices obrigatórios diferentes dos recebidos')
    return _seal_map({k: _rational(data[k], name) for k in keys})


def _canon_instance(S, T, V, adj, A_r, r, K, k_hash):
    S, T, V = _vertices(S, 'S'), _vertices(T, 'T'), _vertices(V, 'V')
    if not S or len(S) != len(T) or not set(S + T) <= set(V):
        raise ValueError('S,T não vazios, contidos em V, com cardinalidades iguais')
    if type(r) not in (int, float) or not math.isfinite(r) or r < 1:
        raise ValueError('r inválido')
    if not isinstance(adj, Mapping) or not set(adj) <= set(V):
        raise ValueError('adj fora do domínio')
    G = {v: set() for v in V}
    for u in V:
        seen = set()
        for v, length in adj.get(u, ()):
            if v not in G or v == u or length != 1 or v in seen:
                raise ValueError('G precisa ser simples, unitário e sobre V')
            seen.add(v)
        G[u].update(seen)
    if any(u not in G[v] for u in V for v in G[u]):
        raise ValueError('G precisa ser não dirigido e simétrico')
    visited = {V[0]}
    queue = deque([V[0]])
    while queue:
        u = queue.popleft()
        for v in G[u] - visited:
            visited.add(v)
            queue.append(v)
    if visited != set(V):
        raise ValueError('G desconexo')
    if isinstance(A_r, (str, bytes)):
        raise ValueError('A_r inválido')
    arcs = tuple(A_r)
    if any(not isinstance(p, tuple) or len(p) != 2 or p[0] not in G or
           p[1] not in G or p[0] == p[1] for p in arcs) or len(set(arcs)) != len(arcs):
        raise ValueError('A_r precisa conter arcos válidos distintos e não reflexivos')
    expected = set()
    for s in V:
        lengths = {s: 0}
        bfs = deque([s])
        while bfs:
            u = bfs.popleft()
            if lengths[u] + 1 > r:
                continue
            for v in G[u]:
                if v not in lengths:
                    lengths[v] = lengths[u] + 1
                    bfs.append(v)
        expected.update((s, v) for v, d in lengths.items() if s != v and d <= r)
    if set(arcs) != expected:
        raise ValueError('A_r não coincide exatamente com G^r')
    K = _cuts(K, V)
    actual_hash = canonical_k_hash(K)
    if k_hash is not None and k_hash != actual_hash:
        raise ValueError('hash de K divergente')
    H = {v: frozenset(u for a, u in expected if a == v) for v in V}
    D = tuple((s, t) for s in S for t in T if s == t or (s, t) in expected)
    graph_hash = graph_digest(H, V)
    canonical = {
        'format': 'MIN-STATION-N2-T3-INSTANCE-V1',
        'S': [_tag(s) for s in S], 'T': [_tag(t) for t in T],
        'V': [_tag(v) for v in V], 'r': (Fraction(r).numerator, Fraction(r).denominator),
        'G': [[_tag(u), _tag(v)] for i, u in enumerate(V) for v in V[i + 1:] if v in G[u]],
        'A_r': [[_tag(u), _tag(v)] for u, v in sorted(expected)],
        'K': [[_tag(v) for v in sorted(Z)] for Z in K],
        'k_hash': actual_hash,
    }
    digest = vector_digest(canonical)
    return S, T, V, K, D, _seal_map(H), tuple(sorted(expected)), actual_hash, graph_hash, digest


@dataclass(frozen=True)
class KEvidence:
    """Verificação computada, não flag fornecida pelo chamador."""
    S: tuple
    T: tuple
    V: tuple
    K: tuple
    D: tuple
    H: Mapping
    A_r: tuple
    k_hash: str
    h_digest: str
    instance_digest: str
    validated_cuts: int
    justification: str
    adj: Mapping
    r: int | float


def validate_k_evidence(S, T, V, adj, A_r, r, K, *, k_hash=None) -> KEvidence:
    """Refaz identidade, alcance e assert_valid_cuts da implementação congelada.

    A rotina NÃO gera novo K; o K original deve ser passado explicitamente.
    """
    parts = _canon_instance(S, T, V, adj, A_r, r, K, k_hash)
    S, T, V, K, D, H, arcs, kh, hd, identity = parts
    assert_valid_cuts(S, T, arcs, K, origem='N2-T3-E5-H-K')
    frozen_adj = _seal_map({v: tuple((u, length) for u, length in adj.get(v, ()))
                            for v in V})
    return KEvidence(S, T, V, K, D, H, arcs, kh, hd, identity, len(K),
                     f'K validado por assert_valid_cuts ({len(K)} cortes); '
                     f'H=G^r e A_r conferidos; instance_digest={identity}',
                     frozen_adj, r)


def _verified_context(evidence: KEvidence) -> KEvidence:
    if not isinstance(evidence, KEvidence):
        raise ValueError('KEvidence verificável é obrigatório')
    refreshed = validate_k_evidence(evidence.S, evidence.T, evidence.V, evidence.adj,
                                    evidence.A_r, evidence.r, evidence.K, k_hash=evidence.k_hash)
    if refreshed != evidence:
        raise ValueError('KEvidence alterada ou de outra instância')
    return refreshed


@dataclass(frozen=True)
class RationalPrimalWitness:
    """Coeficientes do RMP, representados por frações racionais exatas."""
    y: Mapping
    lam: Mapping
    d: Mapping


@dataclass(frozen=True)
class PrimalUpperBound:
    status: str
    instance_digest: str
    k_hash: str
    u_exact: Fraction
    witness: RationalPrimalWitness
    justification: str


def initial_primal_witness(evidence: KEvidence) -> RationalPrimalWitness:
    """A configuração semente (V,S,T), com y=1, é viável no domínio autorizado."""
    q = (frozenset(evidence.V), frozenset(evidence.S), frozenset(evidence.T))
    return RationalPrimalWitness(_seal_map({v: ONE for v in evidence.V}),
                                 _seal_map({q: ONE}), _seal_map({p: ZERO for p in evidence.D}))


def _column(q, ctx: KEvidence):
    if not isinstance(q, tuple) or len(q) != 3:
        raise ValueError('lambda: chave deve ser (W,I,J)')
    try:
        W, origins, destinations = (frozenset(part) for part in q)
    except TypeError as exc:
        raise ValueError('coluna inválida') from exc
    if not W or not W <= set(ctx.V) or not origins or len(origins) != len(destinations):
        raise ValueError('coluna com domínios ou balanço inválidos')
    if not origins <= set(ctx.S) or not destinations <= set(ctx.T):
        raise ValueError('terminais fora de S,T')
    closure = W | frozenset().union(*(ctx.H[v] for v in W))
    if not origins | destinations <= closure:
        raise ValueError('coluna sem elegibilidade no alcance H')
    discovered = {next(iter(W))}
    frontier = list(discovered)
    while frontier:
        for v in ctx.H[frontier.pop()] & W - discovered:
            discovered.add(v)
            frontier.append(v)
    if discovered != W:
        raise ValueError('W desconexo em H')
    return W, origins, destinations


def verify_primal_rational(ctx: KEvidence, witness: RationalPrimalWitness) -> PrimalUpperBound:
    """Prova construtiva exata de U: R1/R2/R3/K, domínios e objetivo."""
    _verified_context(ctx)
    if not isinstance(witness, RationalPrimalWitness):
        raise ValueError('RationalPrimalWitness necessário')
    if not isinstance(witness.y, Mapping) or not isinstance(witness.d, Mapping) or not isinstance(witness.lam, Mapping):
        raise ValueError('testemunho precisa fornecer três mapas')
    y = _rational_map(witness.y, ctx.V, 'y')
    d = _rational_map(witness.d, ctx.D, 'd')
    if any(x < ZERO or x > ONE for x in y.values()) or any(x < ZERO for x in d.values()):
        raise ValueError('bounds de y/d violados')
    lambdas = {}
    for key, value in witness.lam.items():
        q = _column(key, ctx)
        if q in lambdas:
            raise ValueError('lambda contém colunas duplicadas')
        weight = _rational(value, 'lambda')
        if weight < ZERO:
            raise ValueError('lambda negativa')
        lambdas[q] = weight
    for s in ctx.S:
        if sum((a for (_, origins, _), a in lambdas.items() if s in origins), ZERO) + sum(
                (d[(u, t)] for u, t in ctx.D if u == s), ZERO) != ONE:
            raise ValueError(f'R1 não satisfeita em {s!r}')
    for t in ctx.T:
        if sum((a for (_, _, destinations), a in lambdas.items() if t in destinations), ZERO) + sum(
                (d[(s, u)] for s, u in ctx.D if u == t), ZERO) != ONE:
            raise ValueError(f'R2 não satisfeita em {t!r}')
    for v in ctx.V:
        if sum((a for (W, _, _), a in lambdas.items() if v in W), ZERO) > y[v]:
            raise ValueError(f'R3 não satisfeita em {v!r}')
    for Z in ctx.K:
        if sum((y[v] for v in Z), ZERO) < ONE:
            raise ValueError(f'K não satisfeito para Z={tuple(sorted(Z))!r}')
    canonical = RationalPrimalWitness(y, _seal_map(lambdas), d)
    U = sum(y.values(), ZERO)
    return PrimalUpperBound(CERTIFIED, ctx.instance_digest, ctx.k_hash, U, canonical,
                            'Viabilidade racional de R1/R2/R3/K e bounds comprovada exatamente; '
                            'U é upper bound do LP completo F-CC+K')


def check_g2(ctx: KEvidence, upper: PrimalUpperBound | None,
             lb: CertifiedIteration | None, *, instance_key: str,
             evidence: CertifiedCGResult | None = None,
             max_enum_verification_vertices: int = 10) -> bool:
    """G2 é propriedade do valor do LP; não decorre de otimalidade numérica."""
    if not isinstance(ctx, KEvidence) or not isinstance(upper, PrimalUpperBound):
        return False
    try:
        _verified_context(ctx)
    except (ValueError, TypeError, KeyError):
        return False
    if (not isinstance(lb, CertifiedIteration) or lb.status != CERTIFIED
            or lb.scope != LP_SCOPE or type(lb.lb_exact) is not Fraction
            or lb.k_hash != ctx.k_hash or not lb.justification
            or upper.status != CERTIFIED or upper.instance_digest != ctx.instance_digest
            or upper.k_hash != ctx.k_hash or instance_key != ctx.instance_digest):
        return False
    try:
        verified = verify_primal_rational(ctx, upper.witness)
    except (ValueError, TypeError, KeyError):
        return False
    # A classe CertifiedIteration, isoladamente, pode ser instanciada pelo
    # chamador. Exigir a trilha completa e revalidar os oráculos de origem.
    if evidence is None:
        return False
    verified_lb, _notes = _verify_e4_events(
        evidence, ctx, max_enum_vertices=max_enum_verification_vertices)
    return (verified_lb == lb and upper.u_exact == verified.u_exact and
            ZERO <= upper.u_exact - lb.lb_exact <= TOLERANCE)


def _direct_physical_reach(ctx: KEvidence, C):
    """Pares diretos ou com recarga em C: matching bipartido sem floats."""
    C = set(C)
    direct = set(ctx.D)
    available = {}
    for s in ctx.S:
        discovered = {s}
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in ctx.H[u]:
                if v in C and v not in discovered:
                    discovered.add(v)
                    queue.append(v)
        available[s] = {t for t in ctx.T if (s, t) in direct or
                        any(t == x or t in ctx.H[x] for x in discovered if x in C)}
    return available


def _physical_feasible(ctx: KEvidence, C) -> bool:
    edges = _direct_physical_reach(ctx, C)
    right_match = {}

    def augment(s, visited):
        for t in sorted(edges[s]):
            if t in visited:
                continue
            visited.add(t)
            if t not in right_match or augment(right_match[t], visited):
                right_match[t] = s
                return True
        return False

    return all(augment(s, set()) for s in ctx.S)


@dataclass(frozen=True)
class BaselineEvidence:
    """B0 não é LB do LP; apenas valor que possui prova física independente."""
    status: str
    source: str
    candidate: Fraction | None
    b0_exact: Fraction | None
    instance_digest: str
    checked_subsets: int
    justification: str
    max_vertices: int = 12


def verify_baseline(ctx: KEvidence, candidate=None, *, source='EXHAUSTIVE_PHYSICAL',
                    max_vertices: int = 12, solver_status: str | None = None) -> BaselineEvidence:
    """Prova independente opcional via todos os C de tamanho <ceil(candidate).

    Não afirma que core/COMP foi resolvido: este ramo audita a VALIDADE do
    valor candidato como LB físico. Acima do cap, ou só com incumbente de
    core interrompido, abster; jamais fabricar baseline via ObjBound.
    """
    _verified_context(ctx)
    if source not in ('EXHAUSTIVE_PHYSICAL', 'COMP_LP', 'CORE_IP'):
        raise ValueError('origem B0 desconhecida')
    if type(max_vertices) is not int or max_vertices < 1:
        raise ValueError('max_vertices inválido')
    value = None if candidate is None else _rational(candidate, 'B0')
    def refused(why):
        return BaselineEvidence(UNCERTIFIED, source, value, None, ctx.instance_digest, 0, why, max_vertices)
    if value is None or value < ZERO:
        return refused('B0 ausente ou negativo; sem certificação')
    if solver_status is not None and solver_status != 'OPTIMAL_VERIFIED':
        return refused('core/COMP incompleto ou incumbente apenas; prova insuficiente')
    if value == ZERO:
        return BaselineEvidence(CERTIFIED, source, value, value, ctx.instance_digest, 0,
                                'B0=0 comprovado pela não negatividade da quantidade de estações; '
                                'origem declarada não auditada', max_vertices)
    if len(ctx.V) > max_vertices:
        return refused('instância excede limite seguro da verificação exaustiva de B0')
    # Uma instalação usa número inteiro de estações. Examinar todo C com
    # |C| < ceil(B0). Se algum for viável, B0 não é LB do inteiro.
    threshold = -(-value.numerator // value.denominator)
    checked = 0
    for k in range(min(threshold, len(ctx.V) + 1)):
        for C in itertools.combinations(ctx.V, k):
            checked += 1
            if _physical_feasible(ctx, C):
                return BaselineEvidence(UNCERTIFIED, source, value, None,
                                        ctx.instance_digest, checked,
                                        f'contraprova: instalação viável com {k} estações', max_vertices)
    return BaselineEvidence(CERTIFIED, source, value, value, ctx.instance_digest, checked,
                            'Candidato B0 validado como LB físico por busca exaustiva independente '
                            f'de todas instalações com tamanho <ceil(B0); {checked} subconjuntos. '
                            f'Origem alegada {source}; isto NÃO atesta a reconstrução da baseline '
                            'congelada COMP/core nem os seus ótimos individuais', max_vertices)


@dataclass(frozen=True)
class FinalCertificate:
    """Envelope final: LP, MIN-STATION inteiro, B0 e convergência isolados."""
    numerical_result: object
    lp_status: str
    lp_lb_exact: Fraction | None
    lp_source: str | None
    physical_status: str
    physical_lb_exact: Fraction | None
    physical_integer_lb: int | None
    scope: str
    k_evidence: KEvidence | None
    primal_upper: PrimalUpperBound | None
    convergence_status: str
    baseline: BaselineEvidence | None
    b0_exact: Fraction | None
    justification: str
    audit_history: tuple
    audit_warnings: tuple
    validation_wall: float

    def as_dict(self):
        def ratio(value):
            return (None if value is None else
                    {'numerator': value.numerator, 'denominator': value.denominator})
        def floor_12(value):
            if value is None:
                return None
            number = (value.numerator * 10**12) // value.denominator
            sign = '-' if number < 0 else ''
            digits = str(abs(number)).zfill(13)
            return sign + digits[:-12] + '.' + digits[-12:]
        return {'lp_status': self.lp_status, 'lp_lb_exact': ratio(self.lp_lb_exact),
                'lp_source': self.lp_source, 'lp_lb_floor_12dp': floor_12(self.lp_lb_exact),
                'physical_lb_floor_12dp': floor_12(self.physical_lb_exact),
                'physical_status': self.physical_status,
                'physical_lb_exact': ratio(self.physical_lb_exact),
                'physical_integer_lb': self.physical_integer_lb,
                'scope': self.scope, 'convergence_status': self.convergence_status,
                'b0_status': self.baseline.status if self.baseline else UNCERTIFIED,
                'b0_exact': ratio(self.b0_exact), 'justification': self.justification,
                'k_hash': self.k_evidence.k_hash if self.k_evidence else None,
                'instance_digest': self.k_evidence.instance_digest if self.k_evidence else None,
                'rmp_objective_diagnostic': getattr(self.numerical_result, 'rmp_objective', None),
                'n_certificate_events': len(self.audit_history),
                'validation_wall_s': self.validation_wall,
                'audit_warnings': self.audit_warnings}


def _verify_e4_events(result: CertifiedCGResult, ctx: KEvidence, *, max_enum_vertices=10):
    if not isinstance(result, CertifiedCGResult):
        return None, ('resultado E4 inválido',)
    if result.scope != LP_SCOPE or not result.justification:
        return None, ('escopo/status do E4 incompatível',)
    valid = []
    notes = []
    for event in result.certification_history:
        dual = getattr(event, 'dual', None)
        if dual is None:
            notes.append(f'iteração {event.iteration}: sem vetor racional preservado')
            continue
        try:
            _validated_dual(dual)
            if (dual.S, dual.T, dual.V, dual.K, dual.D) != (ctx.S, ctx.T, ctx.V, ctx.K, ctx.D):
                raise ValueError('S/T/V/K/D não coincidem com a instância')
            if (dual.instance_key != ctx.instance_digest or event.instance_key != ctx.instance_digest
                    or event.h_digest != ctx.h_digest or dual.k_hash != ctx.k_hash
                    or event.vector_digest != dual.vector_digest
                    or (dual.revision, dual.solve_id) != (event.revision, event.solve_id)):
                raise ValueError('identidade de vetor, master, grafo ou revisão divergente')
            for attempt in event.attempts:
                if attempt.status != CERTIFIED or attempt.bound is None:
                    continue
                if attempt.source == 'N1':
                    checked = evaluate_theorem_l(dual, attempt.bound, ctx.D)
                elif attempt.source == 'ENUM':
                    if len(ctx.V) > max_enum_vertices:
                        raise ValueError('ENUM excede cap de auditoria E5')
                    cap = attempt.bound.evidence.get('cap')
                    checked = evaluate_enum_theorem_l(dual, attempt.bound, ctx.D, ctx.H, cap)
                elif attempt.source == 'N2':
                    lp = build_rational_pricing_lp(dual, ctx.H)
                    checked = evaluate_box_theorem_l(dual, ctx.H, lp, attempt.bound, ctx.D)
                else:
                    raise ValueError('fonte de prova E4 desconhecida')
                if (checked.status != CERTIFIED or checked != attempt.verification):
                    raise ValueError('evidência global ou certificado L1 adulterado')
                valid.append(checked)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            notes.append(f'iteração {event.iteration}: {type(exc).__name__}: {exc}')
    return max(valid, key=lambda c: c.lb_exact, default=None), tuple(notes)


def finalize_verified_result(result: CertifiedCGResult, ctx: KEvidence,
                             *, primal: RationalPrimalWitness | None = None,
                             baseline: BaselineEvidence | None = None,
                             max_enum_verification_vertices: int = 10) -> FinalCertificate:
    """Consolida somente provas reexecutáveis de E4; jamais promove flags."""
    start_validation = time.monotonic()
    _verified_context(ctx)
    if type(max_enum_verification_vertices) is not int or max_enum_verification_vertices < 1:
        raise ValueError('max_enum_verification_vertices inválido')
    best, notes = _verify_e4_events(result, ctx, max_enum_vertices=max_enum_verification_vertices)
    upper = verify_primal_rational(ctx, primal) if primal is not None else None
    if best is not None and best.k_hash == ctx.k_hash:
        physical_status = CERTIFIED
        physical_lb = best.lb_exact
        integer_lb = _integer_rounding_formula(physical_lb)
        scope = PHYSICAL_SCOPE
    else:
        physical_status, physical_lb, integer_lb, scope = UNCERTIFIED, None, None, LP_SCOPE
    verified_b0 = None
    if baseline is not None:
        verified_b0 = verify_baseline(ctx, baseline.candidate, source=baseline.source,
                                          max_vertices=baseline.max_vertices)
        if (baseline.status != verified_b0.status or
                baseline.b0_exact != verified_b0.b0_exact or
                baseline.instance_digest != ctx.instance_digest):
            verified_b0 = BaselineEvidence(UNCERTIFIED, baseline.source, baseline.candidate,
                                           None, ctx.instance_digest, 0,
                                           'B0 não coincidiu com nova verificação de prova', baseline.max_vertices)
    convergence = (G2_PASSED if best is not None and upper is not None and
                   check_g2(ctx, upper, best, instance_key=ctx.instance_digest,
                            evidence=result,
                            max_enum_verification_vertices=max_enum_verification_vertices)
                   else G2_NOT_PROVED)
    reason = ('LB LP verificado e promovido a MIN-STATION com validade de K; '
              if physical_status == CERTIFIED else
              'Sem novo certificado físico: identidade/evidência de LB do LP insuficiente; ')
    reason += ('G2 comprovado por U racional; ' if convergence == G2_PASSED else
               'G2 não demonstrado; ')
    reason += ('B0 em campo independente, ' + ('certificado' if verified_b0.status == CERTIFIED else 'não certificado')
               if verified_b0 else 'B0 ausente')
    return FinalCertificate(result.base_result if isinstance(result, CertifiedCGResult) else None,
                            CERTIFIED if best is not None else UNCERTIFIED,
                            best.lb_exact if best else None, best.source if best else None,
                            physical_status, physical_lb, integer_lb, scope, ctx, upper,
                            convergence, verified_b0,
                            verified_b0.b0_exact if verified_b0 and verified_b0.status == CERTIFIED else None,
                            reason, result.certification_history if isinstance(result, CertifiedCGResult) else (),
                            notes, time.monotonic() - start_validation)


def run_verified_column_generation(
        S, T, V, adj, A_r, r, *, K, k_hash=None,
        options: CertificationOptions | None = None,
        primal: RationalPrimalWitness | None = None,
        b0_candidate=None, b0_source='EXHAUSTIVE_PHYSICAL',
        max_b0_vertices=12, **cg_kwargs) -> FinalCertificate:
    """E5 opt-in completo: valida K ANTES da otimização, gera e reaudita provas.

    O modo legado run_column_generation e a interface da E4 não são alterados.
    """
    started = time.monotonic()
    overall_time_limit = cg_kwargs.get('time_limit')
    ctx = validate_k_evidence(S, T, V, adj, A_r, r, K, k_hash=k_hash)
    if options is None:
        options = CertificationOptions()
    if not isinstance(options, CertificationOptions):
        raise ValueError('options inválido')
    if options.instance_key not in (None, ctx.instance_digest):
        raise ValueError('instance_key fornecido não coincide com a instância verificada')
    settings = CertificationOptions(
        use_n1=options.use_n1, enum_cap=options.enum_cap, use_n2=options.use_n2,
        max_enum_vertices=options.max_enum_vertices,
        max_n2_vertices=options.max_n2_vertices, instance_key=ctx.instance_digest)
    if 'K' in cg_kwargs or 'k_hash' in cg_kwargs or 'options' in cg_kwargs:
        raise ValueError('K/hash/options devem vir somente dos parâmetros de E5')
    if overall_time_limit is not None:
        if type(overall_time_limit) not in (float, int) or not math.isfinite(overall_time_limit) or overall_time_limit < 0:
            raise ValueError('time_limit inválido')
        remaining = overall_time_limit - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError('orçamento de tempo esgotado durante a validação de K')
        cg_kwargs['time_limit'] = remaining
    e4 = run_certified_column_generation(S, T, V, adj, A_r, r,
                                         K=ctx.K, k_hash=ctx.k_hash,
                                         options=settings, **cg_kwargs)
    base = primal if primal is not None else initial_primal_witness(ctx)
    b0 = (None if b0_candidate is None else verify_baseline(
        ctx, b0_candidate, source=b0_source, max_vertices=max_b0_vertices))
    final = finalize_verified_result(e4, ctx, primal=base, baseline=b0,
                                     max_enum_verification_vertices=options.max_enum_vertices)
    if overall_time_limit is not None and time.monotonic() - started >= overall_time_limit:
        # Provas terminadas após o prazo não são aceitas como resultado
        # produzido dentro do orçamento pre-registrado. O LP E4 anterior
        # continua auditável, mas a promoção física/G2/B0 fica suspensa.
        from dataclasses import replace
        if final.baseline is not None:
            baseline_discarded = replace(final.baseline, status=UNCERTIFIED, b0_exact=None,
                                         justification='auditoria B0 terminou fora do orçamento global de tempo')
        else:
            baseline_discarded = None
        final = replace(final, physical_status=UNCERTIFIED, physical_lb_exact=None,
                        physical_integer_lb=None, scope=LP_SCOPE, baseline=baseline_discarded,
                        convergence_status=G2_NOT_PROVED, b0_exact=None,
                        justification=(final.justification + '; auditoria E5 terminou '
                                       'fora do limite global de tempo: selo físico/B0 recusado'))
    return final
