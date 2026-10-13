"""AS08/T2b — oráculo de pricing independente de enumeração de caminhos.

Custos nos vértices internos w[s,v]=gamma[s,v]+mu[v]>=0, origem/destino
não cobrados. Dijkstra por origem, admitindo terminais intermediários e (s).
O modo Fraction permite certificar mínimos de custo reduzido exatamente.

A instância é validada e a adjacência é construída uma única vez
(`prepare_pricing`), e não a cada origem. O Dijkstra guarda predecessores em
vez de copiar o caminho a cada relaxação; o resultado continua exato: para
cada destino alcançável, o custo reduzido mínimo e um caminho simples que o
realiza. Em empates, o caminho escolhido pode diferir da versão anterior (a
ordem do heap passou de (d, caminho) para (d, vértice)), mas o custo é o mesmo
e a escolha é determinística.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator, Mapping

from as02_model_a import Instance, _validated_instance


class PricedPath:
    """Destino precificado; o caminho é reconstruído da árvore só quando lido.

    Materializar os |S|·|T| caminhos custava mais que o próprio Dijkstra nas
    instâncias grandes, e a maioria nunca é lida (só os de custo negativo).
    """
    __slots__ = ('source', 'target', 'reduced_cost', '_path', '_tree')

    def __init__(self, source, target, path, reduced_cost, *, tree=None):
        self.source, self.target, self.reduced_cost = source, target, reduced_cost
        self._path, self._tree = (tuple(path) if path is not None else None), tree

    @property
    def path(self) -> tuple[str, ...]:
        if self._path is None:
            self._path = self._tree.path_to(self.target)
            self._tree = None
        return self._path

    def __repr__(self):
        return f'PricedPath({self.source!r}, {self.target!r}, {self.path!r}, {self.reduced_cost!r})'

    def __eq__(self, other):
        return (isinstance(other, PricedPath) and
                (self.source, self.target, self.reduced_cost, self.path) ==
                (other.source, other.target, other.reduced_cost, other.path))

    __hash__ = None


class _PathTree:
    """Árvore de predecessores de um Dijkstra; prefixos compartilhados em cache."""
    __slots__ = ('pred', 'built')

    def __init__(self, source, pred):
        self.pred, self.built = pred, {source: (source,)}

    def path_to(self, t):
        built, pred = self.built, self.pred
        chain = []
        v = t
        while v not in built:
            chain.append(v)
            v = pred[v]
        prefix = built[v]
        for w in reversed(chain):
            prefix = prefix + (w,)
            built[w] = prefix
        return prefix


@dataclass(frozen=True)
class PricingGraph:
    """Instância validada + adjacência ordenada, reutilizável entre origens e iterações."""
    instance: Instance
    S: frozenset
    T: frozenset
    V: frozenset
    targets: tuple[str, ...]
    adjacency: Mapping[str, tuple[str, ...]]


def prepare_pricing(instance: Instance) -> PricingGraph:
    _validated_instance(instance)
    adjacency = {v: [] for v in instance.V}
    for u, v in instance.A_r:
        adjacency[u].append(v)
    return PricingGraph(instance, frozenset(instance.S), frozenset(instance.T),
                        frozenset(instance.V), tuple(sorted(instance.T)),
                        {v: tuple(sorted(out)) for v, out in adjacency.items()})


def _converter(exact):
    return (lambda x: x if isinstance(x, Fraction) else Fraction(str(x))) if exact else float


def canonical_weights(instance: Instance | PricingGraph, gamma: Mapping, mu: Mapping, *, exact=False):
    """Não aceita coeficientes negativos/NaN: Dijkstra seria inválido."""
    graph = instance if isinstance(instance, PricingGraph) else None
    S = graph.S if graph else frozenset(instance.S)
    V = graph.V if graph else frozenset(instance.V)
    to_num = _converter(exact)
    gs, ms = {}, {}
    for (s, v), raw in gamma.items():
        if s not in S or v not in V or v == s:
            raise ValueError('gamma contém índice não permitido')
        value = to_num(raw)
        if value < 0 or (not exact and not math.isfinite(value)):
            raise ValueError('gamma precisa ser não negativo e finito')
        gs[s, v] = value
    for v, raw in mu.items():
        if v not in V:
            raise ValueError('mu contém vértice não permitido')
        value = to_num(raw)
        if value < 0 or (not exact and not math.isfinite(value)):
            raise ValueError('mu precisa ser não negativo e finito')
        ms[v] = value
    return gs, ms


def _checked_duals(graph: PricingGraph, pi: Mapping, tau: Mapping, exact: bool):
    if set(pi) != graph.S or set(tau) != graph.T:
        raise ValueError('duais pi/tau incompletos ou com índices extras')
    conv = _converter(exact)
    pis = {s: conv(pi[s]) for s in graph.S}
    taus = {t: conv(tau[t]) for t in graph.T}
    if not exact and any(not math.isfinite(v) for v in (*pis.values(), *taus.values())):
        raise ValueError('pi/tau não finitos')
    return pis, taus


def _price_prepared(graph: PricingGraph, source: str, pival, taus: Mapping,
                    gs: Mapping, ms: Mapping, zero, scale=None) -> tuple[PricedPath, ...]:
    """Dijkstra com custo no vértice de saída u≠origem: w(u)=gamma[s,u]+mu[u].

    Para assim que todos os destinos foram fixados (distâncias já definitivas).
    Predecessores só apontam para vértices fixados, logo formam uma árvore e
    todo caminho reconstruído é simples. A origem nunca é vértice interno.
    Com `scale`, os pesos são inteiros (valor·scale) e o custo reduzido volta
    a Fraction exata no fim.
    """
    adjacency = graph.adjacency
    T = graph.T
    dist = {source: zero}
    pred = {}
    done = set()
    remaining = len(T)
    heap = [(zero, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        if u in T:
            remaining -= 1
            if not remaining:
                break
        nd = d if u == source else d + gs.get(u, zero) + ms.get(u, zero)
        for v in adjacency[u]:
            if v == source or v in done:
                continue
            old = dist.get(v)
            if old is None or nd < old:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(heap, (nd, v))
    tree = _PathTree(source, pred)
    out = []
    for t in graph.targets:
        if t in done:
            rc = dist[t] - pival - taus[t]
            out.append(PricedPath(source, t, None, Fraction(rc, scale) if scale else rc, tree=tree))
    # Um preço por destino: (custo, destino) já é chave total e determinística.
    return tuple(sorted(out, key=lambda x: (x.reduced_cost, x.target)))


def _prepared_duals(graph: PricingGraph, pi, tau, gamma, mu, exact):
    """Valida os duais uma vez e agrupa gamma por origem.

    No modo exato, todos os valores racionais são multiplicados pelo mmc dos
    denominadores: o Dijkstra opera em inteiros (sem normalizar Fraction a
    cada soma) e o resultado é idêntico ao da aritmética Fraction.
    """
    pis, taus = _checked_duals(graph, pi, tau, exact)
    gs, ms = canonical_weights(graph, gamma, mu, exact=exact)
    scale = None
    if exact:
        scale = math.lcm(1, *(x.denominator for x in
                              (*pis.values(), *taus.values(), *gs.values(), *ms.values())))
        as_int = lambda x: x.numerator * (scale // x.denominator)
        pis = {k: as_int(x) for k, x in pis.items()}
        taus = {k: as_int(x) for k, x in taus.items()}
        gs = {k: as_int(x) for k, x in gs.items()}
        ms = {k: as_int(x) for k, x in ms.items()}
    by_source = {s: {} for s in graph.S}
    for (s, v), value in gs.items():
        by_source[s][v] = value
    return pis, taus, by_source, ms, (0 if exact else 0.0), scale


def iter_price(graph: PricingGraph, pi: Mapping, tau: Mapping, gamma: Mapping, mu: Mapping,
               *, exact=False) -> Iterator[tuple[str, tuple[PricedPath, ...]]]:
    """Gera (origem, preços) na ordem de instance.S; duais validados uma só vez."""
    pis, taus, by_source, ms, zero, scale = _prepared_duals(graph, pi, tau, gamma, mu, exact)
    for s in graph.instance.S:
        yield s, _price_prepared(graph, s, pis[s], taus, by_source[s], ms, zero, scale)


def price_source(instance: Instance, source: str, pi: Mapping, tau: Mapping,
                 gamma: Mapping, mu: Mapping, *, exact=False,
                 graph: PricingGraph | None = None) -> tuple[PricedPath, ...]:
    """Um caminho mínimo por destino, incluindo (s) quando s∈T.

    Para certificar custos mínimos não requer enumerar caminhos; a lista de
    preços contém todos os destinos alcançáveis, nunca apenas o melhor global.
    """
    graph = graph or prepare_pricing(instance)
    if source not in graph.S:
        raise ValueError('origem não pertence a S')
    pis, taus, by_source, ms, zero, scale = _prepared_duals(graph, pi, tau, gamma, mu, exact)
    return _price_prepared(graph, source, pis[source], taus, by_source[source], ms, zero, scale)


def price_all(instance: Instance, pi: Mapping, tau: Mapping, gamma: Mapping, mu: Mapping,
              *, exact=False, graph: PricingGraph | None = None) -> dict[str, tuple[PricedPath, ...]]:
    return dict(iter_price(graph or prepare_pricing(instance), pi, tau, gamma, mu, exact=exact))


def minimum_reduced_cost(priced: Mapping[str, tuple[PricedPath, ...]], source: str):
    """None sinaliza ausência de caminhos; nunca significa custo 0."""
    paths = priced[source]
    return min((p.reduced_cost for p in paths), default=None)
