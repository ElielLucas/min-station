"""N2-T3 / E2 (T4): ENUM racional exato do pricing F-CC+K na raiz.

Para o grafo de alcance H informado (H=G^r, a conferir na integração E4),
a busca percorre TODOS os subconjuntos W não vazios e H-conexos, inclusive
os sem terminais elegíveis. Para cada W viável otimiza I,J por TopK racional.

IMPORTANTE:
- cap atingido, inclusive exatamente, é TRUNCADO (sem prova de cobertura),
  como em fcc.enumerar_conexos; jamais utilizar mínimo parcial como ell global.
- Retorna GlobalPricingBound somente quando COMPLETO. Fora disso, abstenção.
- evaluate_enum_theorem_l refaz a busca e compara todas as evidências antes
  de atestar LB <= z_Q do LP completo F-CC+K; não atesta K para MIN-STATION.
- Não requer Gurobi. Mantém fcc.py e N2-T2B completamente inalterados.
- O vínculo entre o H fornecido e o H efetivamente construído pelo master é
  responsabilidade da integração E4. Um hash de H não prova essa igualdade.
"""

from __future__ import annotations

import math
import time
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from fractions import Fraction

from n2_t3_cert_core import (
    CERTIFIED,
    LP_SCOPE,
    UNCERTIFIED,
    CertifiedIteration,
    GlobalPricingBound,
    RationalDual,
    _abstain,
    _freeze,
    _theorem_l_formula,
    _validated_dual,
    vector_digest,
)

ZERO = Fraction(0)
ENUM_SOURCE = 'ENUM'
_ENUM_FORMULA = 'ENUM-TOPK-v2.1'


@dataclass(frozen=True)
class EnumAbstention:
    """Ausência de certificado global. Nenhuma cota parcial é publicada."""

    status: str
    source: str
    vector_digest: str
    graph_digest: str | None
    cap: int
    visited_connected_w: int
    eligible_w: int
    truncated: bool
    reason: str
    ell: None = None


def _canonical_graph(dual: RationalDual, H: Mapping) -> dict:
    """Exige grafo simples, simétrico, conexo e com V exatamente igual ao dual.

    O operador/integrador deve fornecer H da mesma instância do master.
    D calculado a partir de H é conferido com D do snapshot racional.
    """
    if not isinstance(H, Mapping) or set(H) != set(dual.V):
        raise ValueError('H deve ter exatamente os vértices do vetor racional')
    vertices = set(dual.V)
    out = {}
    for v in dual.V:
        raw = H[v]
        if isinstance(raw, (str, bytes)):
            raise ValueError('vizinhança inválida em H')
        try:
            adjacent = frozenset(raw)
        except TypeError as exc:
            raise ValueError('vizinhança não iterável em H') from exc
        if v in adjacent or not adjacent <= vertices:
            raise ValueError('H deve ser simples e sem vértices fora de V')
        out[v] = adjacent
    if any(u not in out[v] for u in dual.V for v in out[u]):
        raise ValueError('H precisa ser não dirigido (adjacências simétricas)')
    visited = {dual.V[0]}
    queue = deque([dual.V[0]])
    while queue:
        u = queue.popleft()
        for v in out[u] - visited:
            visited.add(v)
            queue.append(v)
    if visited != vertices:
        raise ValueError('H deve ser conexo no domínio autorizado')
    direct = tuple((s, t) for s in dual.S for t in dual.T
                   if s == t or t in out[s])
    if direct != dual.D:
        raise ValueError('D do snapshot não corresponde aos pares diretos de H')
    return out


def graph_digest(H: Mapping, V) -> str:
    """Hash canônico de H: identidade de conteúdo, não prova de H=G^r."""
    vertices = tuple(V)
    def tag(v):
        return ['int', v] if type(v) is int else ['str', v]
    encoded = {
        'format': 'MIN-STATION-N2-T3-H-V1',
        'V': [tag(v) for v in vertices],
        'edges': [[tag(u), tag(v)] for i, u in enumerate(vertices)
                  for v in vertices[i + 1:] if v in H[u]],
    }
    return vector_digest(encoded)


def _abstention(dual, graph_hash, cap, visited, eligible, reason):
    return EnumAbstention(UNCERTIFIED, ENUM_SOURCE, dual.vector_digest,
                          graph_hash, cap, visited, eligible, True, reason)


def _best_topk(dual: RationalDual, W: frozenset, H: Mapping):
    """Min rc sobre I,J para W, usando todos os k>=1, sem descartar negativos."""
    B = set(W)
    for v in W:
        B.update(H[v])
    origins = [s for s in dual.S if s in B]
    destinations = [t for t in dual.T if t in B]
    kmax = min(len(origins), len(destinations))
    if not kmax:
        return None
    ordered_origins = sorted(origins, key=lambda s: (-dual.pi[s], dual.S.index(s)))
    ordered_destinations = sorted(destinations, key=lambda t: (-dual.tau[t], dual.T.index(t)))
    cost = sum((dual.mu[v] for v in W), ZERO)
    prizes = ZERO
    best_rc = None
    winner = None
    for k in range(1, kmax + 1):
        prizes += dual.pi[ordered_origins[k - 1]] + dual.tau[ordered_destinations[k - 1]]
        rc = cost - prizes
        if best_rc is None or rc < best_rc:
            best_rc = rc
            winner = (k, tuple(sorted(ordered_origins[:k])),
                      tuple(sorted(ordered_destinations[:k])))
    return best_rc, winner


def _enumerate(dual, H, cap, graph_hash, *, deadline, interrupt_requested):
    """BFS de conjuntos conexos (sem dependência de Gurobi/fcc.py).

    Tem semântica conservadora de enumerar_conexos: cap == quantidade total
    marca truncamento mesmo se nenhum conjunto realmente faltar.
    """
    if cap == 0:
        return _abstention(dual, graph_hash, cap, 0, 0, 'cap=0: cobertura não iniciada')
    queue = deque()
    seen = set()
    visited = 0
    eligible = 0
    best = None
    winning = None
    visit_items = []

    def check_interrupt():
        if deadline is not None and time.monotonic() >= deadline:
            return True
        if interrupt_requested is not None:
            try:
                return bool(interrupt_requested())
            except InterruptedError:
                return True
        return False

    def add_and_evaluate(W):
        nonlocal visited, eligible, best, winning
        seen.add(W)
        queue.append(W)
        visited += 1
        visit_items.append(tuple(sorted(W)))
        candidate = _best_topk(dual, W, H)
        if candidate is not None:
            eligible += 1
            rc, (k, origins, destinations) = candidate
            if best is None or rc < best:
                best = rc
                winning = (tuple(sorted(W)), k, origins, destinations)
        return visited >= cap

    for v in dual.V:
        if check_interrupt():
            return _abstention(dual, graph_hash, cap, visited, eligible,
                               'interrupção antes de comprovar cobertura')
        if add_and_evaluate(frozenset((v,))):
            return _abstention(dual, graph_hash, cap, visited, eligible,
                               'cap atingido exatamente ou antes da cobertura')
    while queue:
        if check_interrupt():
            return _abstention(dual, graph_hash, cap, visited, eligible,
                               'interrupção antes de comprovar cobertura')
        W = queue.popleft()
        frontier = set()
        for v in W:
            frontier.update(H[v])
        for v in sorted(frontier - W):
            if check_interrupt():
                return _abstention(dual, graph_hash, cap, visited, eligible,
                                   'interrupção antes de comprovar cobertura')
            extended = W | {v}
            if extended in seen:
                continue
            if add_and_evaluate(extended):
                return _abstention(dual, graph_hash, cap, visited, eligible,
                                   'cap atingido exatamente ou antes da cobertura')

    if best is None:  # impossível: H conexo e S,T não vazios dão (V,S,T)
        raise AssertionError('ENUM completo sem configuração admissível')

    witness_w, witness_k, witness_origins, witness_destinations = winning
    evidence = _freeze({
        'formula': _ENUM_FORMULA,
        'instance_key': dual.instance_key,
        'revision': dual.revision,
        'solve_id': dual.solve_id,
        'k_hash': dual.k_hash,
        'vector_digest': dual.vector_digest,
        'graph_digest': graph_hash,
        'cap': cap,
        'truncated': False,
        'visited_connected_w': visited,
        'eligible_w': eligible,
        'visited_digest': vector_digest({
            'format': 'ENUM-W-COVERAGE-V1',
            'connected_w': visit_items,
        }),
        'witness_w': witness_w,
        'witness_k': witness_k,
        'witness_origins': witness_origins,
        'witness_destinations': witness_destinations,
        'witness_rc': best,
        'algorithm': 'connected-set-BFS-exhaustive',
    })
    return GlobalPricingBound(best, ENUM_SOURCE, dual.vector_digest, evidence)


def enumerate_global_bound(dual: RationalDual, H: Mapping, cap: int,
                           *, time_limit_seconds: float | None = None,
                           interrupt_requested: Callable[[], bool] | None = None):
    """Exato se e somente se há cobertura completa; caso contrário, abstenção.

    H: adjacências de H=G^r para a MESMA instância do master, fornecido em E4.
    cap: máximo de W conectados visitados. Exigir cap > total, não cap == total.
    time_limit_seconds: relógio de parede (componente ENUM, sem resolver MIP).
    """
    _validated_dual(dual)
    if type(cap) is not int or cap < 0:
        raise ValueError('cap deve ser inteiro >=0')
    if time_limit_seconds is not None:
        if (type(time_limit_seconds) not in (int, float)
                or not math.isfinite(time_limit_seconds)
                or time_limit_seconds < 0):
            raise ValueError('time_limit_seconds deve ser finito e >=0')
    if interrupt_requested is not None and not callable(interrupt_requested):
        raise ValueError('interrupt_requested deve ser callable')
    # Verificar todos os dados combinatórios ANTES de calcular qualquer bound.
    canonical_H = _canonical_graph(dual, H)
    h_hash = graph_digest(canonical_H, dual.V)
    deadline = (None if time_limit_seconds is None
                else time.monotonic() + time_limit_seconds)
    return _enumerate(dual, canonical_H, cap, h_hash,
                      deadline=deadline, interrupt_requested=interrupt_requested)


def evaluate_enum_theorem_l(dual: RationalDual, bound, D, H: Mapping,
                            cap: int) -> CertifiedIteration:
    """Revalida a cobertura do ENUM *reexecutando-o* e aplica L0/L1 exatos.

    A recomputação deliberada impede que GlobalPricingBound, evidence ou ell
    fornecidos pelo chamador sejam certificados somente por terem um hash.
    O resultado continua limitado ao LP F-CC+K; H-K ainda será verificado E5.
    """
    _validated_dual(dual)
    if not isinstance(bound, GlobalPricingBound) or bound.source != ENUM_SOURCE:
        return _abstain(dual, 'ENUM ausente/não completo; sem ell global da rota ENUM')
    if bound.vector_digest != dual.vector_digest:
        return _abstain(dual, 'ENUM pertence a outro vetor/iteração')
    try:
        pairs = tuple(D)
    except TypeError:
        return _abstain(dual, 'pares diretos D ausentes/inválidos')
    if pairs != dual.D:
        return _abstain(dual, 'pares diretos D divergentes do vetor do master')
    try:
        verified = enumerate_global_bound(dual, H, cap)
    except (ValueError, TypeError) as exc:
        return _abstain(dual, f'H/cap inválidos na verificação ENUM: {exc}')
    if isinstance(verified, EnumAbstention):
        return _abstain(dual, 'ENUM verificador não comprovou cobertura integral')
    if (type(bound.ell) is not Fraction
            or bound.ell != verified.ell
            or not isinstance(bound.evidence, Mapping)
            or dict(bound.evidence) != dict(verified.evidence)):
        return _abstain(dual, 'ENUM evidência/ell não coincide com recomputação exata')
    result = _theorem_l_formula(dual, verified.ell, dual.D)
    return CertifiedIteration(
        CERTIFIED, LP_SCOPE, result.lb_exact, ENUM_SOURCE,
        'ENUM: cobertura completa de todos W conexos de H e TopK em Fraction; '
        f'vetor={dual.vector_digest}; H={verified.evidence["graph_digest"]}; '
        'Teorema L para o LP completo; H=G^r vinculado ao master em E4; '
        'H-K/MIN-STATION ainda não verificados',
        dual.revision, dual.solve_id, dual.vector_digest, dual.k_hash,
        result.l_exact, result.delta_exact, result.ell_exact,
        result.winning_branch,
    )
