"""AS-09 experimental: cumulative battery-state formulation C (unit undirected G).

Preserves the baseline compiler and numerical solver interface, but does not
assert that LP y-projections of C and COMP are equal without a separate proof.
No experimental artifact or historical result is modified by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from as02_model_a import Instance, CompiledModel, _Compiler, _cuts, _validated_instance


@dataclass(frozen=True)
class PhysicalGraph:
    """Canonical oriented arcs of an undirected, unit-length physical graph."""
    arcs: tuple[tuple[str, str], ...]
    edges: tuple[tuple[str, str], ...]


def prepare_physical_graph(instance: Instance, adj: Mapping) -> PhysicalGraph:
    """Refuse weighted/directed/malformed graphs rather than changing semantics."""
    _validated_instance(instance)
    vertices = set(instance.V)
    if set(adj) != vertices:
        raise ValueError('Adjacência física deve conter exatamente V')
    directed = set()
    for v in instance.V:
        neighbors = adj[v]
        if not isinstance(neighbors, (list, tuple)):
            raise ValueError('Lista de adjacência física inválida')
        seen = set()
        for neighbor in neighbors:
            if not isinstance(neighbor, (tuple, list)) or len(neighbor) != 2:
                raise ValueError('Aresta física deve ter (vértice, custo)')
            w, length = neighbor
            if w not in vertices or w == v or w in seen:
                raise ValueError('Aresta desconhecida, laço ou repetida')
            if isinstance(length, bool) or not isinstance(length, (int, float)) or not isfinite(length) or length != 1:
                raise ValueError('AS09 exige arestas físicas de custo exatamente unitário')
            directed.add((v, w))
            seen.add(w)
    if any((v, u) not in directed for u, v in directed):
        raise ValueError('AS09 exige G físico não direcionado, com ambas orientações')
    edges = tuple(sorted({tuple(sorted((u, v))) for u, v in directed}))
    return PhysicalGraph(tuple(sorted(directed)), edges)


def dimension_estimate(instance: Instance, graph: PhysicalGraph, n_cuts: int = 0) -> dict:
    """Dimension BEFORE presolve; K generation/reachability are NOT free."""
    n, m, r, e = len(instance.V), len(instance.T), instance.r, len(graph.edges)
    return {
        'n_variables': n + 2 * r * e + n * r + m * (r + 1),
        'n_constraints': n * (r + 1) + m + n + n_cuts,
        'n_movement_variables': 2 * r * e,
        'n_recharge_variables': n * r,
        'n_absorption_variables': m * (r + 1),
        'n_station_variables': n,
    }


def compile_c(instance: Instance, adj: Mapping, K=(), *, relax: bool = True,
              physical_graph: PhysicalGraph | None = None) -> CompiledModel:
    """Exact translation of C1/C2/C3 with zero-length s=t path via e[t,0].

    All flows are nonnegative continuous; only station y is binary in IP.
    C3 uses a *sum over recharge levels*, not separate z[q] <= m*y.
    """
    graph = prepare_physical_graph(instance, adj) if physical_graph is None else physical_graph
    vertices, S, T, m, r = instance.V, set(instance.S), set(instance.T), len(instance.S), instance.r
    c = _Compiler()
    y = {v: c.var(('y', v), 'y[' + str(v) + ']', binary=not relax, ub=1) for v in vertices}
    c.objective = {j: 1.0 for j in y.values()}
    f = {}
    for q in range(r):
        for u, v in graph.arcs:
            f[q, u, v] = c.var(('F', q, u, v), f'F[{q},{u},{v}]')
    z = {}
    for v in vertices:
        for q in range(1, r + 1):
            z[v, q] = c.var(('z', v, q), f'z[{v},{q}]')
    absorption = {}
    for t in instance.T:
        for q in range(r + 1):
            absorption[t, q] = c.var(('e', t, q), f'e[{t},{q}]', ub=1)
    entering = {v: [] for v in vertices}
    leaving = {v: [] for v in vertices}
    for u, v in graph.arcs:
        leaving[u].append((u, v))
        entering[v].append((u, v))
    for v in vertices:
        for q in range(r + 1):
            terms = []
            if q >= 1:
                terms += [(f[q - 1, u, v], 1) for u, _ in entering[v]]
            if q == 0:
                terms += [(z[v, ell], 1) for ell in range(1, r + 1)]
            if q < r:
                terms += [(f[q, v, w], -1) for _, w in leaving[v]]
            if q >= 1:
                terms.append((z[v, q], -1))
            if v in T:
                terms.append((absorption[v, q], -1))
            c.row('C1', f'C1[{v},{q}]', terms, '==', -int(q == 0 and v in S))
    for t in instance.T:
        c.row('C2', f'C2[{t}]', ((absorption[t, q], 1) for q in range(r + 1)), '==', 1)
    for v in vertices:
        kappa = m - int(v in S or v in T)
        c.row('C3', f'C3[{v}]',
              [(z[v, q], 1) for q in range(1, r + 1)] + [(y[v], -kappa)], '<=', 0)
    for i, Z in enumerate(_cuts(vertices, K)):
        c.row('K', f'K[{i}]', ((y[v], 1) for v in sorted(Z)), '>=', 1)
    output = c.output()
    expected = dimension_estimate(instance, graph, len(_cuts(vertices, K)))
    if len(output.variables) != expected['n_variables'] or len(output.equations) != expected['n_constraints']:
        raise AssertionError('Erro interno de contagem na compilação de C')
    return output
