"""AS-02: formulação A por grupos, sem modificar o baseline histórico.

`compile_a` gera o sistema linear auditável e independente de solver;
`build_A` traduz EXATAMENTE esse sistema para Gurobi. `compile_u`
implementa o controle U contínuo com os mesmos cortes K.

Entrada: grafo original não direcionado e unitário, A_r calculado externamente;
S e T são conjuntos de vértices distintos, de mesmo tamanho e possivelmente
sobrepostos. K são cortes congelados Σ_{v∈Z} y_v >= 1 (sem C3 iterativo).
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from math import inf
from typing import Iterable


@dataclass(frozen=True)
class Instance:
    V: tuple[str, ...]
    S: tuple[str, ...]
    T: tuple[str, ...]
    A_r: tuple[tuple[str, str], ...]
    r: int

    @classmethod
    def from_synthetic(cls, sample: tuple) -> "Instance":
        S, T, V, _adj, A_r, r, _meta = sample
        return cls(tuple(V), tuple(S), tuple(T), tuple(A_r), int(r))


@dataclass(frozen=True)
class Variable:
    name: str
    lb: float = 0.0
    ub: float = inf
    binary: bool = False


@dataclass(frozen=True)
class Equation:
    name: str
    terms: tuple[tuple[int, float], ...]
    sense: str
    rhs: float


@dataclass
class CompiledModel:
    variables: list[Variable]
    equations: list[Equation]
    objective: dict[int, float]
    columns: dict[tuple, int]
    families: dict[str, int]

    @property
    def n_nonzeros(self) -> int:
        return sum(len(eq.terms) for eq in self.equations)


class _Compiler:
    def __init__(self):
        self.variables: list[Variable] = []
        self.equations: list[Equation] = []
        self.columns: dict[tuple, int] = {}
        self.objective: dict[int, float] = {}
        self.families: dict[str, int] = {}

    def var(self, key, name, *, binary=False, ub=inf):
        assert key not in self.columns
        idx = len(self.variables)
        self.columns[key] = idx
        self.variables.append(Variable(name, ub=float(ub), binary=binary))
        return idx

    def row(self, family, name, terms, sense, rhs):
        coeff: dict[int, float] = {}
        for col, coef in terms:
            coeff[col] = coeff.get(col, 0.0) + float(coef)
        data = tuple(sorted((j, v) for j, v in coeff.items() if v))
        self.equations.append(Equation(name, data, sense, float(rhs)))
        self.families[family] = self.families.get(family, 0) + 1

    def output(self):
        return CompiledModel(self.variables, self.equations, self.objective,
                             self.columns, self.families)


def _validated_instance(instance: Instance):
    V, S, T = instance.V, instance.S, instance.T
    if not V or len(V) != len(set(V)):
        raise ValueError("V deve ser não vazio e sem duplicações")
    if not S or len(S) != len(T) or len(S) != len(set(S)) or len(T) != len(set(T)):
        raise ValueError("S e T devem ser conjuntos não vazios, distintos internamente e equicardinais")
    if not set(chain(S, T)) <= set(V):
        raise ValueError("Origem/destino fora de V")
    if not isinstance(instance.r, int) or instance.r < 1:
        raise ValueError("Autonomia r deve ser inteiro positivo")
    arcs = instance.A_r
    if len(arcs) != len(set(arcs)) or any(u == v or u not in V or v not in V for u, v in arcs):
        raise ValueError("A_r tem duplicação, laço ou vértice desconhecido")
    incoming = {v: [] for v in V}
    outgoing = {v: [] for v in V}
    for arc in arcs:
        u, v = arc
        incoming[v].append(arc)
        outgoing[u].append(arc)
    return incoming, outgoing


def _partition(S, groups):
    raw = tuple(tuple(g) for g in groups)
    if any(len(g) != len(set(g)) for g in raw):
        raise ValueError("Origem repetida dentro do grupo")
    parts = tuple(frozenset(g) for g in raw)
    if not parts or any(not p for p in parts):
        raise ValueError("Partição ausente ou grupo vazio")
    counts = list(chain.from_iterable(parts))
    if len(counts) != len(set(counts)) or set(counts) != set(S):
        raise ValueError("Partição de S deve cobrir cada origem exatamente uma vez")
    # Ordem estável para evitar diferenças de fingerprint por hash seed.
    return tuple(sorted(parts, key=lambda p: tuple(sorted(p))))


def _cuts(V, K):
    cuts = tuple(frozenset(c) for c in K)
    if any(not c <= set(V) for c in cuts):
        raise ValueError("Corte K com vértice desconhecido")
    return tuple(sorted(set(cuts), key=lambda c: tuple(sorted(c))))


def _station_and_cuts(c: _Compiler, V, K, relax):
    y = {v: c.var(('y', v), f'y[{v}]', binary=not relax, ub=1) for v in V}
    c.objective = {j: 1.0 for j in y.values()}
    for i, Z in enumerate(_cuts(V, K)):
        c.row('A6', f'A6[{i}]', ((y[v], 1) for v in sorted(Z)), '>=', 1)
    return y


def compile_a(instance: Instance, groups: Iterable[Iterable[str]],
              K=(), *, relax=False) -> CompiledModel:
    """Cria A1–A7, sem impor uma alocação fixa de destinos aos grupos.

    Partições inválidas são recusadas ANTES da criação de um modelo/solver.
    """
    incoming, outgoing = _validated_instance(instance)
    blocks = _partition(instance.S, groups)
    V, T, S, m = instance.V, instance.T, set(instance.S), len(instance.S)
    c = _Compiler()
    y = _station_and_cuts(c, V, K, relax)
    f, g, p, h = {}, {}, {}, {}
    for i, B in enumerate(blocks):
        for u, v in instance.A_r:
            f[i, u, v] = c.var(('f', i, u, v), f'f[{i},{u},{v}]')
        for v in V:
            g[i, v] = c.var(('g', i, v), f'g[{i},{v}]')
        for t in T:
            p[i, t] = c.var(('p', i, t), f'p[{i},{t}]', ub=1)
        for v in sorted(B.intersection(T)):
            h[i, v] = c.var(('h', i, v), f'h[{i},{v}]', ub=1)
        for v in V:
            hterm = [(h[i, v], 1)] if (i, v) in h else []
            pterm = [(p[i, v], -1)] if v in T else []
            c.row('A1', f'A1[{i},{v}]',
                  ([(f[i, u, w], 1) for u, w in incoming[v]] +
                   hterm + pterm + [(g[i, v], -1)]), '==', 0)
            c.row('A2', f'A2[{i},{v}]',
                  ([(f[i, u, w], 1) for u, w in outgoing[v]] +
                   hterm + [(g[i, v], -1)]), '==', int(v in B))
            c.row('A4', f'A4[{i},{v}]',
                  [(g[i, v], 1), (y[v], -(len(B) - int(v in B)))], '<=', 0)
    for t in T:
        c.row('A3', f'A3[{t}]', ((p[i, t], 1) for i in range(len(blocks))), '==', 1)
    for v in V:
        kappa = m - int(v in S or v in T)
        c.row('A5', f'A5[{v}]',
              [(g[i, v], 1) for i in range(len(blocks))] + [(y[v], -kappa)], '<=', 0)
    return c.output()


def compile_u(instance: Instance, K=(), *, relax=False) -> CompiledModel:
    """Controle U/COMP+K com fluxo contínuo, para comparação de LP/MIP.

    A versão histórica de U usa fluxo inteiro; com y binário, a rede de
    fluxo tem solução inteira quando viável. Isso NÃO altera o histórico.
    """
    incoming, outgoing = _validated_instance(instance)
    V, S, T, m = instance.V, set(instance.S), set(instance.T), len(instance.S)
    c = _Compiler()
    y = _station_and_cuts(c, V, K, relax)
    f = {(u, v): c.var(('F', u, v), f'F[{u},{v}]') for u, v in instance.A_r}
    for v in V:
        a, b = int(v in S), int(v in T)
        cin = [(f[e], 1) for e in incoming[v]]
        cout = [(f[e], 1) for e in outgoing[v]]
        c.row('U_bal', f'U_bal[{v}]', cout + [(j, -coef) for j, coef in cin], '==', a-b)
        c.row('U_in', f'U_in[{v}]', cin + [(y[v], -(m-b))], '<=', b)
        c.row('U_out', f'U_out[{v}]', cout + [(y[v], -(m-a))], '<=', a)
    return c.output()


def build_A(instance: Instance, groups: Iterable[Iterable[str]], K=(), *, relax=False):
    """Adapter Gurobi; retorna (model, variáveis por chave, metadados).

    Não chama optimize(); se Gurobi faltar, a falha é explícita.
    """
    compiled = compile_a(instance, groups, K, relax=relax)
    from gurobipy import Model, GRB, quicksum

    model = Model('AS02-A-GROUPED')
    model.Params.OutputFlag = 0
    variables = [model.addVar(lb=v.lb, ub=v.ub if v.ub != inf else GRB.INFINITY,
                              vtype=GRB.BINARY if v.binary else GRB.CONTINUOUS,
                              name=v.name) for v in compiled.variables]
    model.setObjective(quicksum(coef * variables[j] for j, coef in compiled.objective.items()),
                       GRB.MINIMIZE)
    for row in compiled.equations:
        expr = quicksum(coef * variables[j] for j, coef in row.terms)
        if row.sense == '==':
            model.addConstr(expr == row.rhs, name=row.name)
        elif row.sense == '<=':
            model.addConstr(expr <= row.rhs, name=row.name)
        else:
            model.addConstr(expr >= row.rhs, name=row.name)
    model.update()
    metadata = {
        'n_variables': model.NumVars,
        'n_constraints': model.NumConstrs,
        'n_nonzeros': model.NumNZs,
        'constraint_families': dict(compiled.families),
        'relax': relax,
        'K_count': compiled.families.get('A6', 0),
    }
    return model, {key: variables[idx] for key, idx in compiled.columns.items()}, metadata


def prepare_K(instance: Instance, adj, r) -> tuple[frozenset[str], ...]:
    """Mesmas famílias C1+C2+C4-DM/ordem do harness histórico; sem C3/C6.

    Usa somente os geradores puros de experiments/cuts/cuts.py.
    """
    if r != instance.r:
        raise ValueError('Autonomia da instância e dos cortes divergente')
    _validated_instance(instance)
    from experiments.cuts.cuts import (
        build_neighborhoods, generate_C1, generate_C2, generate_C4_DM,
        cortes_ordenados, assert_valid_cuts,
    )

    plus, minus = build_neighborhoods(instance.A_r)
    cuts = (generate_C1(instance.S, instance.T, plus, minus) +
            generate_C2(instance.S, instance.T, adj, r, instance.V) +
            generate_C4_DM(instance.S, instance.T, plus, minus))
    ordered = cortes_ordenados(cuts)
    assert_valid_cuts(instance.S, instance.T, instance.A_r, ordered,
                      origem='AS02 prepare_K')
    return tuple(ordered)
