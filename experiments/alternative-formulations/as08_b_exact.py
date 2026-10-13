"""AS-08/T2a — modelo B COMPLETO por enumeração, apenas para grafos pequenos.

Sem pricing, sem geração de colunas e sem alegar que a igualdade de objetivos
numéricos demonstra equivalência de projeções. Usa o compilador de linhas da
AS-02 para adaptar-se aos mesmos backends; constrói independentemente B1-B4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from as02_model_a import Instance, CompiledModel, _Compiler, _cuts, _validated_instance


class PathEnumerationLimit(ValueError):
    """A enumeração não terminou dentro do limite; resultados não são exatos."""


@dataclass(frozen=True)
class Paths:
    by_source: dict[str, tuple[tuple[str, ...], ...]]
    count: int


def enumerate_paths(instance: Instance, *, max_vertices: int = 9,
                    max_paths: int = 20_000) -> Paths:
    """Todos os caminhos SIMPLES de s a qualquer t, inclusive (s) se s∈T.

    Explora um dígrafo sem laços; o cap é global e provoca erro, nunca
    truncamento silencioso. Terminais podem ser internos (não encerra DFS).
    """
    _validated_instance(instance)
    if max_vertices < 1 or max_paths < 1:
        raise ValueError('limites devem ser positivos')
    if len(instance.V) > max_vertices:
        raise PathEnumerationLimit(f'n={len(instance.V)} excede max_vertices={max_vertices}')
    out = {v: [] for v in instance.V}
    for u, v in instance.A_r:
        out[u].append(v)
    for u in out:
        out[u].sort()
    destinations = set(instance.T)
    paths: dict[str, tuple[tuple[str, ...], ...]] = {}
    count = 0
    for s in instance.S:
        found = []
        # A pilha usa caminho e conjunto visitado: 0 <= comprimento <= n-1.
        stack = [(s, (s,), frozenset((s,)))]
        while stack:
            node, walk, visited = stack.pop()
            if node in destinations:
                count += 1
                if count > max_paths:
                    raise PathEnumerationLimit(f'mais de {max_paths} caminhos simples; B incompleta')
                found.append(walk)
            for nxt in reversed(out[node]):
                if nxt not in visited:
                    stack.append((nxt, walk + (nxt,), visited | {nxt}))
        paths[s] = tuple(sorted(found))
    return Paths(paths, count)


def compile_b(instance: Instance, K: Iterable[Iterable[str]] = (), *, relax: bool = True,
              max_vertices: int = 9, max_paths: int = 20_000,
              global_links: bool = True) -> tuple[CompiledModel, Paths]:
    """B0-B4+BK: x_P >= 0, y∈[0,1] no LP, binário no MIP.

    `global_links=False` só para teste mutante da F-h histórica; NÃO é B.
    B4 restrita a T\\S é equivalente à B4 completa (prova da AS08-T1).
    """
    paths = enumerate_paths(instance, max_vertices=max_vertices, max_paths=max_paths)
    c = _Compiler()
    y = {v: c.var(('y', v), f'y[{v}]', binary=not relax, ub=1) for v in instance.V}
    c.objective = {idx: 1.0 for idx in y.values()}
    # Um identificador por coluna, independentemente da ordem dos caminhos.
    x = {}
    touching = {(s, v): [] for s in instance.S for v in instance.V if v != s}
    terminating = {t: [] for t in instance.T}
    for s in instance.S:
        for p in paths.by_source[s]:
            idx = c.var(('x', s, p), f'x[{s},{"/".join(p)}]')
            x[s, p] = idx
            terminating[p[-1]].append((idx, 1.0))
            for v in p[1:-1]:
                touching[s, v].append((idx, 1.0))
    for s in instance.S:
        c.row('B1', f'B1[{s}]', ((x[s, p], 1) for p in paths.by_source[s]), '==', 1)
    for t in instance.T:
        c.row('B2', f'B2[{t}]', terminating[t], '==', 1)
    for s in instance.S:
        for v in instance.V:
            if v != s:
                c.row('B3', f'B3[{s},{v}]', touching[s, v] + [(y[v], -1)], '<=', 0)
    if global_links:
        for v in instance.V:
            if v in instance.T and v not in instance.S:
                kappa = len(instance.S) - 1
                c.row('B4', f'B4[{v}]',
                      [term for s in instance.S for term in touching.get((s, v), ())]
                      + [(y[v], -kappa)], '<=', 0)
    for i, cut in enumerate(_cuts(instance.V, K)):
        c.row('BK', f'BK[{i}]', ((y[v], 1) for v in sorted(cut)), '>=', 1)
    return c.output(), paths


def check_b_system(compiled: CompiledModel, instance: Instance, paths: Paths,
                   y_values: dict[str, float], x_values: dict[tuple[str, tuple[str, ...]], float],
                   *, tolerance: float = 1e-8) -> dict:
    """Sensor independente de famílias B: lê coeficientes do compilado.

    Para testes de testemunhas explícitas; não é verificador físico.
    """
    if set(y_values) != set(instance.V):
        raise ValueError('vetor y incompleto')
    expected = {(s, p) for s in instance.S for p in paths.by_source[s]}
    if set(x_values) != expected:
        raise ValueError('vetor x incompleto')
    values = {('y', v): y for v, y in y_values.items()}
    values.update({('x', s, p): x for (s, p), x in x_values.items()})
    vector = [float(values[key]) for key, _ in sorted(compiled.columns.items(), key=lambda kv: kv[1])]
    domains = [v.lb - tolerance <= value <= v.ub + tolerance for v, value in zip(compiled.variables, vector)]
    failures = []
    for eq in compiled.equations:
        lhs = sum(vector[idx] * coeff for idx, coeff in eq.terms)
        if (eq.sense == '==' and abs(lhs-eq.rhs)>tolerance or
            eq.sense == '<=' and lhs > eq.rhs+tolerance or
            eq.sense == '>=' and lhs < eq.rhs-tolerance):
            failures.append(eq.name)
    return {'feasible': all(domains) and not failures,
            'violated_rows': failures, 'domain_violation': not all(domains)}
