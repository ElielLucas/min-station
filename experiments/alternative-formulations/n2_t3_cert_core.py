"""N2-T3 / E1 (T1--T3): núcleo racional, Teorema L e oráculo analítico N1.

Referência normativa: n2-t2b-master-dual-pricing-revisao.md v2.1, §§6.1–6.3.
Esta camada não importa Gurobi, não altera o RMP, não verifica a validade
física de K e NÃO publica certificados do problema inteiro MIN-STATION.

RationalDual é uma cópia racional independente do DualSnapshot numérico da
N2-T2B. O cálculo privado de L1 não certifica nada sozinho: evaluate_theorem_l
recalcula a prova N1 para o MESMO vetor, sem confiar em 'ell', flags, ObjBound
ou no digest isoladamente. ENUM, N2, G2, histórico e H-K ficam para E2–E5.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from types import MappingProxyType

ZERO = Fraction(0)
ONE = Fraction(1)
CERTIFIED = 'CERTIFIED'
UNCERTIFIED = 'UNCERTIFIED'
LP_SCOPE = 'FULL_FCC_K_LP_ONLY'  # NÃO atesta H-K nem um LB físico


def _freeze(mapping: Mapping) -> Mapping:
    return MappingProxyType(dict(mapping))


def _vertices(items, name: str, *, empty_ok: bool = False) -> tuple:
    """Identificadores int/str (não bool), compatíveis com a ordenação do master."""
    if isinstance(items, (str, bytes)):
        raise ValueError(f'{name} deve ser uma coleção de vértices')
    try:
        raw = tuple(items)
    except TypeError as exc:
        raise ValueError(f'{name} deve ser uma coleção') from exc
    if (not empty_ok and not raw) or any(type(v) not in (int, str) for v in raw):
        raise ValueError(f'{name} exige IDs int/str e cardinalidade válida')
    try:
        ordered = tuple(sorted(raw))
    except TypeError as exc:
        raise ValueError(f'{name} contém IDs não ordenáveis entre si') from exc
    if len(set(ordered)) != len(ordered):
        raise ValueError(f'{name} contém duplicatas')
    return ordered


def _cuts(cuts, V: tuple) -> tuple:
    if isinstance(cuts, (str, bytes)):
        raise ValueError('K deve conter coleções de vértices')
    seen = set()
    for cut in cuts:
        Z = frozenset(_vertices(cut, 'Z'))
        if not Z <= set(V):
            raise ValueError('corte K contém vértices fora de V')
        seen.add(Z)
    try:
        return tuple(sorted(seen, key=lambda z: tuple(sorted(z))))
    except TypeError as exc:
        raise ValueError('K contém IDs não ordenáveis') from exc


def _direct_pairs(pairs, S: tuple, T: tuple) -> tuple:
    """Cópia canônica do suporte D do snapshot (não inferir D do vetor dual)."""
    if isinstance(pairs, (str, bytes)):
        raise ValueError('D inválido')
    try:
        raw = tuple(pairs)
    except TypeError as exc:
        raise ValueError('D deve ser coleção de pares') from exc
    if any(not isinstance(p, tuple) or len(p) != 2
           or p[0] not in S or p[1] not in T for p in raw):
        raise ValueError('D contém pares fora de S×T')
    if len(set(raw)) != len(raw):
        raise ValueError('D contém duplicatas')
    return tuple(sorted(raw))


def canonical_k_hash(K: tuple) -> str:
    """Mesmo digest de K usado em RestrictedMaster quando K é explícito.

    A ordem recebida deve ser canônica (como em cortes_ordenados). Esta função
    calcula identidade de conteúdo; NÃO demonstra validade de cada corte.
    """
    serial = [sorted(str(v) for v in Z) for Z in K]
    encoded = json.dumps(serial, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(encoded.encode('utf8')).hexdigest()


def _rational(value, name: str) -> Fraction:
    """Floats são convertidos à razão binária EXATA; não usa Fraction(str(x))."""
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f'{name} contém NaN/infinito')
        return Fraction.from_float(value)
    if type(value) is int:
        return Fraction(value)
    if type(value) is Fraction:
        return value
    raise ValueError(f'{name} exige int, Fraction ou float finito')


def _rational_map(raw: Mapping, keys: tuple, name: str, *, nonnegative=False) -> Mapping:
    if not isinstance(raw, Mapping) or set(raw) != set(keys):
        raise ValueError(f'índices de {name} não coincidem com o domínio')
    out = {}
    for key in keys:
        num = _rational(raw[key], name)
        out[key] = max(ZERO, num) if nonnegative else num
    return _freeze(out)


def _tag(vertex) -> tuple:
    return ('int', vertex) if type(vertex) is int else ('str', vertex)


def _frac_pair(f: Fraction) -> tuple[int, int]:
    return f.numerator, f.denominator


def _canonical_payload(*, S, T, V, K, D, instance_key, revision, solve_id,
                       k_hash, pi, tau, mu, kappa) -> dict:
    return {
        'format': 'MIN-STATION-N2-T3-RATIONAL-DUAL-V1',
        'instance_key': instance_key, 'k_hash': k_hash,
        'revision': revision, 'solve_id': solve_id,
        'S': [_tag(s) for s in S], 'T': [_tag(t) for t in T],
        'V': [_tag(v) for v in V],
        'K': [[_tag(v) for v in sorted(Z)] for Z in K],
        'D': [[_tag(s), _tag(t)] for s, t in D],
        'pi': [_frac_pair(pi[s]) for s in S],
        'tau': [_frac_pair(tau[t]) for t in T],
        'mu': [_frac_pair(mu[v]) for v in V],
        'kappa': [_frac_pair(kappa[Z]) for Z in K],
    }


def vector_digest(payload: dict) -> str:
    """SHA-256 determinístico do payload canônico, sem dependência de PYTHONHASHSEED."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(canonical.encode('utf8')).hexdigest()


@dataclass(frozen=True)
class RationalDual:
    """Vetor pós-projeção identificado; NÃO é prova da validade dos cortes K."""
    pi: Mapping
    tau: Mapping
    mu: Mapping
    kappa: Mapping
    S: tuple
    T: tuple
    V: tuple
    K: tuple
    D: tuple  # pares diretos efetivos do DualSnapshot do master
    instance_key: str
    revision: int
    solve_id: int
    k_hash: str
    vector_digest: str

    @property
    def m(self) -> int:
        return len(self.S)


@dataclass(frozen=True)
class GlobalPricingBound:
    """Candidato racional de bound global; objeto sozinho NÃO é certificado.

    evaluate_theorem_l valida novamente a única fonte habilitada na E1 (N1).
    Atestados de ENUM/N2 não são aceitos até os verificadores de E2/E3.
    """
    ell: Fraction
    source: str
    vector_digest: str
    evidence: Mapping


@dataclass(frozen=True)
class TheoremLValues:
    """Cálculo matemático puro: não contém certificação nem hipótese de prova."""
    eta: Mapping
    l_exact: Fraction
    delta_exact: Fraction
    ell_exact: Fraction
    a_exact: Fraction
    branch_zero: Fraction
    branch_mass: Fraction
    branch_ratio: Fraction
    lb_exact: Fraction
    winning_branch: str


@dataclass(frozen=True)
class CertifiedIteration:
    """CERTIFIED significa LB<=z_Q do LP F-CC+K, NÃO LB físico MIN-STATION."""
    status: str
    scope: str
    lb_exact: Fraction | None
    source: str | None
    justification: str
    revision: int
    solve_id: int
    vector_digest: str
    k_hash: str
    l_exact: Fraction | None
    delta_exact: Fraction | None
    ell_exact: Fraction | None
    winning_branch: str | None


def _validated_dual(dual: RationalDual) -> None:
    """Revalida dados e digest antes de qualquer atestado operacional."""
    if not isinstance(dual, RationalDual):
        raise ValueError('RationalDual requerido')
    if not isinstance(dual.instance_key, str) or not dual.instance_key:
        raise ValueError('instance_key é obrigatório')
    if type(dual.revision) is not int or dual.revision < 0 or type(dual.solve_id) is not int or dual.solve_id < 1:
        raise ValueError('revision/solve_id inválidos')
    S, T, V = (_vertices(seq, label) for seq, label in
               ((dual.S, 'S'), (dual.T, 'T'), (dual.V, 'V')))
    if (S, T, V) != (dual.S, dual.T, dual.V) or len(S) != len(T) or not set(S + T) <= set(V):
        raise ValueError('S/T/V incompatíveis com o master')
    K = _cuts(dual.K, V)
    if K != dual.K or dual.k_hash != canonical_k_hash(K):
        raise ValueError('K/hash incoerente')
    D = _direct_pairs(dual.D, S, T)
    if D != dual.D:
        raise ValueError('D fora de ordem canônica')
    for name, keys, nonneg in [('pi', S, False), ('tau', T, False),
                               ('mu', V, True), ('kappa', K, True)]:
        data = getattr(dual, name)
        if (not isinstance(data, Mapping) or set(data) != set(keys)
                or any(type(data[k]) is not Fraction or (nonneg and data[k] < ZERO)
                       for k in keys)):
            raise ValueError(f'domínio racional projetado inválido em {name}')
    current = vector_digest(_canonical_payload(
        S=S, T=T, V=V, K=K, D=D, instance_key=dual.instance_key,
        revision=dual.revision, solve_id=dual.solve_id,
        k_hash=dual.k_hash, pi=dual.pi, tau=dual.tau,
        mu=dual.mu, kappa=dual.kappa))
    if current != dual.vector_digest:
        raise ValueError('digest inconsistente com o vetor racional')


def rationalize_snapshot(snapshot, instance_key: str, S, T, V, K) -> RationalDual:
    """Extrai um único DualSnapshot numérico para Fraction, com projeção prévia.

    O hash de K é recalculado e comparado com snapshot.k_hash. É somente uma
    checagem de consistência estrutural; H-K será verificado em E5.
    """
    if snapshot is None or not hasattr(snapshot, 'values'):
        raise ValueError('DualSnapshot não disponível')
    if not isinstance(instance_key, str) or not instance_key:
        raise ValueError('instance_key não vazio é obrigatório')
    S = _vertices(S, 'S')
    T = _vertices(T, 'T')
    V = _vertices(V, 'V')
    if len(S) != len(T) or not set(S + T) <= set(V):
        raise ValueError('S,T devem estar em V e ter mesma cardinalidade')
    K = _cuts(K, V)
    digest_k = canonical_k_hash(K)
    if snapshot.k_hash != digest_k:
        raise ValueError('hash de K do snapshot incompatível com o conteúdo recebido')
    if type(snapshot.revision) is not int or snapshot.revision < 0:
        raise ValueError('revision inválida')
    if type(snapshot.solve_id) is not int or snapshot.solve_id < 1:
        raise ValueError('solve_id inválido')
    if not isinstance(getattr(snapshot, 'direct_rc', None), Mapping):
        raise ValueError('snapshot não contém o conjunto completo D do master')
    D = _direct_pairs(snapshot.direct_rc, S, T)
    values = snapshot.values
    pi = _rational_map(values.pi, S, 'pi')
    tau = _rational_map(values.tau, T, 'tau')
    mu = _rational_map(values.mu, V, 'mu', nonnegative=True)
    kappa = _rational_map(values.kappa, K, 'kappa', nonnegative=True)
    payload = _canonical_payload(
        S=S, T=T, V=V, K=K, D=D, instance_key=instance_key,
        revision=snapshot.revision, solve_id=snapshot.solve_id,
        k_hash=digest_k, pi=pi, tau=tau, mu=mu, kappa=kappa)
    dual = RationalDual(pi, tau, mu, kappa, S, T, V, K, D, instance_key,
                        snapshot.revision, snapshot.solve_id, digest_k,
                        vector_digest(payload))
    _validated_dual(dual)
    return dual


def _topk_prizes(dual: RationalDual) -> tuple[Fraction, int, tuple]:
    """Calcula min/max das parcelas N1 sem descartar prêmios negativos."""
    sp = sorted(dual.pi.values(), reverse=True)
    tp = sorted(dual.tau.values(), reverse=True)
    scores = tuple((sum(sp[:k], ZERO) + sum(tp[:k], ZERO))
                   for k in range(1, dual.m + 1))
    best = max(scores)
    best_k = scores.index(best) + 1
    return best, best_k, scores


def analytical_bound_n1(dual: RationalDual, S=None, T=None, V=None) -> GlobalPricingBound:
    """Prova global N1: min_v μ_v − max_k(Top_k π + Top_k τ)."""
    _validated_dual(dual)
    if S is not None and _vertices(S, 'S') != dual.S:
        raise ValueError('S incompatível com vetor')
    if T is not None and _vertices(T, 'T') != dual.T:
        raise ValueError('T incompatível com vetor')
    if V is not None and _vertices(V, 'V') != dual.V:
        raise ValueError('V incompatível com vetor')
    maximum, best_k, scores = _topk_prizes(dual)
    smallest = min(dual.mu.values())
    return GlobalPricingBound(
        ell=smallest - maximum, source='N1', vector_digest=dual.vector_digest,
        evidence=_freeze({'formula': 'N1-v2.1', 'minimum_mu': smallest,
                          'maximum_prizes': maximum, 'best_k': best_k,
                          'prize_sums': scores, 'domain_m': dual.m,
                          'instance_key': dual.instance_key,
                          'revision': dual.revision, 'solve_id': dual.solve_id,
                          'k_hash': dual.k_hash}))


def _theorem_l_formula(dual: RationalDual, ell: Fraction, D) -> TheoremLValues:
    """L0/L1 exatos SEM certificação; reservado a avaliação/testes matemáticos."""
    _validated_dual(dual)
    ell = _rational(ell, 'ell')
    pairs = _direct_pairs(D, dual.S, dual.T)
    incidence = {v: ZERO for v in dual.V}
    for Z in dual.K:
        for v in Z:
            incidence[v] += dual.kappa[Z]
    eta = _freeze({v: max(ZERO, dual.mu[v] + incidence[v] - ONE)
                   for v in dual.V})
    L = (sum(dual.pi.values(), ZERO) + sum(dual.tau.values(), ZERO)
         + sum(dual.kappa.values(), ZERO) - sum(eta.values(), ZERO))
    delta = min((ZERO, *(-dual.pi[s] - dual.tau[t] for s, t in pairs)))
    a = min(ZERO, ell)
    branch_mass = L + dual.m * min(a, delta)
    branch_ratio = (L + dual.m * delta) / (ONE - a)
    values = {'ZERO': ZERO, 'MASS': branch_mass, 'RATIO': branch_ratio}
    winner = max(values, key=values.__getitem__)  # desempate documentado ZERO > MASS > RATIO
    return TheoremLValues(eta, L, delta, ell, a, ZERO,
                          branch_mass, branch_ratio, values[winner], winner)


def _abstain(dual: RationalDual, reason: str) -> CertifiedIteration:
    return CertifiedIteration(UNCERTIFIED, LP_SCOPE, None, None, reason,
                              dual.revision, dual.solve_id, dual.vector_digest,
                              dual.k_hash, None, None, None, None)


def evaluate_theorem_l(dual: RationalDual, bound: GlobalPricingBound, D,
                       m: int | None = None) -> CertifiedIteration:
    """E1: certifica o LB de P_Q SOMENTE após refazer e verificar prova N1.

    GlobalPricingBound é apenas um *pedido* de avaliação; mesmo com source=N1
    e digest coincidente, uma prova forjada/ell>c* não passa. Outras origens
    retornam UNCERTIFIED até as implementações verificadoras E2/E3.
    """
    _validated_dual(dual)
    if m is not None and (type(m) is not int or m != dual.m):
        raise ValueError('m diferente de |S|=|T|')
    if not isinstance(bound, GlobalPricingBound):
        return _abstain(dual, 'não há bound global verificável (ObjBound/ell bruto não bastam)')
    if bound.source != 'N1':
        return _abstain(dual, 'fonte de prova ainda não habilitada na E1; MIP não certifica')
    if bound.vector_digest != dual.vector_digest:
        return _abstain(dual, 'bound global pertence a outro vetor/iteração')
    expected = analytical_bound_n1(dual)
    if (type(bound.ell) is not Fraction or bound.ell != expected.ell
            or not isinstance(bound.evidence, Mapping)
            or dict(bound.evidence) != dict(expected.evidence)):
        return _abstain(dual, 'evidência N1 incompatível com recálculo racional')
    pairs = _direct_pairs(D, dual.S, dual.T)
    if pairs != dual.D:
        return _abstain(dual, 'D não coincide com os pares diretos do snapshot do master')
    terms = _theorem_l_formula(dual, expected.ell, dual.D)
    return CertifiedIteration(
        CERTIFIED, LP_SCOPE, terms.lb_exact, 'N1',
        'N1 global recalculado em Fraction para o vetor projetado; '
        'Teorema L aplicado ao LP F-CC+K; H-K e LB físico NÃO verificados nesta E1',
        dual.revision, dual.solve_id, dual.vector_digest, dual.k_hash,
        terms.l_exact, terms.delta_exact, terms.ell_exact,
        terms.winning_branch)


def _require_lb(result: CertifiedIteration) -> Fraction:
    if (not isinstance(result, CertifiedIteration)
            or result.status != CERTIFIED or result.scope != LP_SCOPE
            or type(result.lb_exact) is not Fraction
            or result.source != 'N1'):
        raise ValueError('operação de publicação exige LB_CG CERTIFIED da E1')
    return result.lb_exact


def floor_export(result: CertifiedIteration, decimal_places: int = 12) -> Decimal:
    """Decimal exato com piso dirigido; nenhuma operação Decimal com rounding.

    Para qualquer lb racional e p>=0, floor(lb*10**p)/10**p <= lb.
    """
    lb = _require_lb(result)
    if type(decimal_places) is not int or not 0 <= decimal_places <= 100:
        raise ValueError('decimal_places deve ser inteiro entre 0 e 100')
    scale = 10 ** decimal_places
    raw = (lb.numerator * scale) // lb.denominator
    if decimal_places == 0:
        return Decimal(str(raw))
    sign = '-' if raw < 0 else ''
    digits = str(abs(raw)).zfill(decimal_places + 1)
    return Decimal(f'{sign}{digits[:-decimal_places]}.{digits[-decimal_places:]}')


def floor_float(result: CertifiedIteration) -> float:
    """Maior float representável <= LB; detecta overflow sem piso finito."""
    lb = _require_lb(result)
    try:
        candidate = float(lb)
    except OverflowError:
        candidate = math.inf if lb > 0 else -math.inf
    if candidate == math.inf:
        return math.nextafter(math.inf, -math.inf)
    if candidate == -math.inf:
        raise OverflowError('não há float finito que represente piso deste LB')
    if Fraction.from_float(candidate) > lb:
        candidate = math.nextafter(candidate, -math.inf)
    return candidate


def _integer_rounding_formula(lb: Fraction) -> int:
    """Fórmula pura ceil(LB−1e−6), sem selo de LB para o problema inteiro.

    Só depois de provar H-K, em E5, esse número poderá ser apresentado como
    limite inferior para o objetivo INTEIRO de MIN-STATION. Não é LB de z_Q.
    """
    if type(lb) is not Fraction:
        raise ValueError('fórmula exige racional exato')
    value = lb - Fraction(1, 1_000_000)
    return -(-value.numerator // value.denominator)


def conservative_integer_bound(result: CertifiedIteration) -> int:
    """Publicação deliberadamente bloqueada em E1: H-K será atestado em E5.

    Ceil de um LB para o LP pode EXCEDER o ótimo fracionário z_Q, logo
    arredondar e expor como certificado físico sem H-K seria enganoso.
    """
    _require_lb(result)
    raise RuntimeError('H-K ainda não foi validado: LB inteiro físico indisponível na E1')
