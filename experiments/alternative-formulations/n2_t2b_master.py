"""N2-T2B / Entrega 1: master LP restrito F-CC+K e dual numérico.

Contrato: docs/technical/plans/execucao/n2-t2b-implementacao-master-dual.md.
Matemática: revisão v2.1, §§2--4. Não implementa pricing, geração de
colunas, certificação ou escrita de resultados. ObjVal e L são somente
diagnósticos do RMP; nenhum deles é um LB certificado de MIN-STATION.

Uso (mesmos S,T,V,adj,A_r,r de fcc_k):
    with RestrictedMaster(S, T, V, adj, A_r, r, K=K, k_hash=digest) as master:
        result = master.solve(params={'Threads': 1, 'Seed': 42})
        if result.dual is not None:
            rc = master.reduced_cost((W, I, J))
            master.add_column((W, I, J))  # invalida o snapshot anterior
            result = master.solve()

Sempre inclui a semente (V,S,T). K fornecido é canonicalizado, conferido
contra k_hash (se informado), e validado pelo harness existente; não é
regenerado. A procedência do K fornecido continua sendo responsabilidade
do chamador, como em build_fcc_plus_k. Sem K, usa exatamente prepare_k.

solve() retorna duais somente para LP OPTIMAL com verificações numéricas
aprovadas. Outros status não expõem ObjVal nem multiplicadores. Falhas do
solver são explícitas em error; erros de entrada levantam ValueError.
Não há projeção silenciosa de Pi: preservam-se os floats do solver para
comparar RC. Violações são reportadas/testadas, não certificadas. A futura
certificação racional deve ser um componente separado (N2-T3).
"""
# E402: bootstrap do diretório experimental; E741: notação normativa W,I,J.
# ruff: noqa: E402, E741
import hashlib
import json
import math
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(HERE))

import gurobipy as gp
from gurobipy import GRB
from cuts import cortes_ordenados
from fcc import B_de, grafo_H, pares_diretos
from fcc_k import prepare_k
from harness import add_cuts_to_model
from ms_utils import construir_arcos_alcance


class DuplicateColumnError(ValueError):
    """A mesma tripla (W,I,J), independentemente da ordem, já existe."""


class StaleDualError(RuntimeError):
    """Snapshot não pertence à última resolução desta versão do master."""


def _freeze(values):
    return MappingProxyType(dict(values))


def _canonical_column(column):
    try:
        parts = tuple(column)
        if len(parts) != 3 or any(isinstance(p, (str, bytes)) for p in parts):
            raise ValueError('q deve conter três coleções: (W,I,J)')
        return tuple(frozenset(p) for p in parts)
    except (TypeError, ValueError) as exc:
        raise ValueError('q deve conter três coleções de vértices: (W,I,J)') from exc


def _connected(W, H):
    if not W:
        return False
    seen = {next(iter(W))}
    stack = list(seen)
    while stack:
        for v in H[stack.pop()] & W - seen:
            seen.add(v)
            stack.append(v)
    return seen == W


def _numeric_map(values, keys, name):
    if set(values) != set(keys):
        raise ValueError(f'índices incorretos em {name}')
    result = {k: float(values[k]) for k in keys}
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError(f'{name} contém NaN ou infinito')
    return _freeze(result)


@dataclass(frozen=True)
class DualValues:
    """Um único vetor numérico imutável; não é certificado dual global.

    pi,tau são livres; mu=-Pi(R3), kappa=Pi(K). eta paga somente o UB
    nativo de y. Multiplicadores não são arredondados/projetados aqui.
    Métodos de RC deste objeto também servem para analisar vetores
    históricos; no master use reduced_cost(), que verifica a iteração.
    """
    pi: Mapping
    tau: Mapping
    mu: Mapping
    kappa: Mapping
    eta: Mapping
    L: float

    def column_rc(self, column):
        """μ(W)-π(I)-τ(J); o chamador deve fornecer uma coluna admissível."""
        W, I, J = _canonical_column(column)
        # Ordenação fixa: não variar soma/resultado com PYTHONHASHSEED.
        return math.fsum([self.mu[v] for v in sorted(W)]
                         + [-self.pi[s] for s in sorted(I)]
                         + [-self.tau[t] for t in sorted(J)])

    def direct_rc(self, pair):
        """Custo reduzido de um par direto: -π_s-τ_t."""
        s, t = pair
        return -self.pi[s] - self.tau[t]


def numerical_dual(S, T, V, K, *, pi, tau, mu, kappa):
    """Reconstrói η e L do vetor completo recebido, sem certificar nada.

    Pode avaliar vetores dirigidos (por exemplo η>0) sem exigir que o
    simplex escolha uma base específica. Verifica índices e finitude.
    Preserva sinais recebidos: a auditoria de solve mede as violações.
    """
    S, T, V, K = tuple(S), tuple(T), tuple(V), tuple(K)
    pi = _numeric_map(pi, S, 'pi')
    tau = _numeric_map(tau, T, 'tau')
    mu = _numeric_map(mu, V, 'mu')
    kappa = _numeric_map(kappa, K, 'kappa')
    incidence = {v: [] for v in V}
    for Z in K:
        for v in Z:
            incidence[v].append(kappa[Z])
    eta = {v: max(0.0, math.fsum([mu[v], -1.0] + incidence[v])) for v in V}
    L = math.fsum(list(pi.values()) + list(tau.values())
                  + list(kappa.values()) + [-eta[v] for v in V])
    if not math.isfinite(L) or not all(math.isfinite(x) for x in eta.values()):
        raise ValueError('reconstrução dual não finita')
    return DualValues(pi, tau, mu, kappa, _freeze(eta), L)


@dataclass(frozen=True)
class DualChecks:
    """Resíduos absolutos em floats; não demonstram certificação exata."""
    duality_gap: float
    max_rc_error: float
    max_dual_violation: float
    tolerance: float

    @property
    def passed(self):
        return max(self.duality_gap, self.max_rc_error,
                   self.max_dual_violation) <= self.tolerance


@dataclass(frozen=True)
class DualSnapshot:
    """Vetor e verificações de uma resolução específica, sem dados mutáveis."""
    values: DualValues
    revision: int
    solve_id: int
    k_hash: str
    column_rc: Mapping
    direct_rc: Mapping
    solver_column_rc: Mapping
    solver_direct_rc: Mapping
    checks: DualChecks


@dataclass(frozen=True)
class MasterResult:
    """Resultado do RMP; ausência de dual nunca é preenchida com zeros."""
    status: int | None
    status_name: str
    objective_rmp: float | None
    dual: DualSnapshot | None
    error: str | None
    parameters: Mapping
    gurobi_version: tuple
    revision: int
    solve_id: int
    runtime: float | None
    work: float | None
    scope: str = 'RMP_NUMERICAL_ONLY'


_STATUS_NAMES = {
    getattr(GRB, name): name for name in (
        'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED',
        'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT',
        'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL', 'INPROGRESS', 'USER_OBJ_LIMIT',
        'WORK_LIMIT', 'MEM_LIMIT',
    )
}
_DEFAULT_PARAMS = {'OutputFlag': 0, 'Seed': 42, 'Threads': 1, 'Method': 1}
_ALLOWED_PARAMS = frozenset({
    'Seed', 'Threads', 'Method', 'Presolve', 'Crossover', 'FeasibilityTol',
    'OptimalityTol', 'NumericFocus', 'TimeLimit', 'WorkLimit', 'IterationLimit',
})


class RestrictedMaster:
    """RMP contínuo qij+K, inicializado somente com (V,S,T).

    V/S/T usam os mesmos identificadores ordenáveis dos módulos existentes.
    adj contém os dois sentidos das arestas unitárias. A_r é conferido
    contra construir_arcos_alcance para não misturar métricas com K.
    O modelo Gurobi e seus handles são privados: alterar _model/_lam etc.
    diretamente viola o contrato e invalida a rastreabilidade de snapshots.
    """

    def __init__(self, S, T, V, adj, A_r, r, *, K=None, k_hash=None):
        self.S, self.T, self.V = tuple(sorted(S)), tuple(sorted(T)), tuple(sorted(V))
        self._validate_instance(adj, A_r, r)
        self.D = tuple(pares_diretos(self.S, self.T, self._A_r))
        if K is None:
            cuts, digest, _counts = prepare_k(self.S, self.T, self.V, adj, self._A_r, r)
        else:
            cuts = cortes_ordenados(K)
            # Mesma serialização de fcc_k.build_fcc_plus_k; não há helper
            # público para apenas o hash, e o módulo histórico é imutável.
            canonical = [sorted(str(v) for v in Z) for Z in cuts]
            digest = hashlib.sha256(json.dumps(
                canonical, ensure_ascii=False, separators=(',', ':'),
            ).encode('utf8')).hexdigest()
        if k_hash is not None and digest != k_hash:
            raise ValueError('K congelado não coincide com o hash fornecido')
        if any(not Z or not set(Z) <= set(self.V) for Z in cuts):
            raise ValueError('K exige cortes não vazios contidos em V')
        self.K, self.k_hash = tuple(cuts), digest
        self._revision, self._solve_id = 0, 0
        self._last_result = None
        self._disposed = False
        self._model = gp.Model('N2-T2B-RMP-FCC-K')
        try:
            md = self._model
            md.Params.OutputFlag = 0
            self._y = {v: md.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS,
                                    obj=1, name=f'y[{i}]') for i, v in enumerate(self.V)}
            self._d = {e: md.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS,
                                    name=f'd[{i}]') for i, e in enumerate(self.D)}
            self._lam = {}
            md.ModelSense = GRB.MINIMIZE
            self._r1 = {s: md.addConstr(gp.quicksum(self._d[e] for e in self.D if e[0] == s)
                                       == 1, name=f'R1[{i}]') for i, s in enumerate(self.S)}
            self._r2 = {t: md.addConstr(gp.quicksum(self._d[e] for e in self.D if e[1] == t)
                                       == 1, name=f'R2[{i}]') for i, t in enumerate(self.T)}
            self._r3 = {v: md.addConstr(-self._y[v] <= 0, name=f'R3[{i}]')
                        for i, v in enumerate(self.V)}
            md.update()
            before = md.NumConstrs
            added = add_cuts_to_model(md, self._y, self.K,
                                     validate=(self.S, self.T, self._A_r))
            md.update()
            if added != len(self.K):
                raise RuntimeError(f'K: esperados {len(self.K)}, adicionados {added}')
            self._k_rows = dict(zip(self.K, md.getConstrs()[before:], strict=True))
            for i, row in enumerate(self._k_rows.values()):
                row.ConstrName = f'K[{i}]'
            self.add_column((self.V, self.S, self.T))
            md.update()
        except Exception:
            self.dispose()
            raise

    def _validate_instance(self, adj, A_r, r):
        Vset = set(self.V)
        if not Vset or any(len(set(seq)) != len(seq) for seq in (self.V, self.S, self.T)):
            raise ValueError('V deve ser não vazio; V, S e T não podem ter duplicatas')
        if not self.S or len(self.S) != len(self.T) or not set(self.S) | set(self.T) <= Vset:
            raise ValueError('exige S,T contidos em V e |S|=|T|>=1')
        if not math.isfinite(r) or r < 1:
            raise ValueError('autonomia deve ser finita e >=1')
        if not set(adj) <= Vset:
            raise ValueError('adj contém vértices fora de V')
        H_G = {v: set() for v in self.V}
        for v in self.V:
            for w, cost in adj.get(v, ()):
                if w not in Vset or w == v or cost != 1 or w in H_G[v]:
                    raise ValueError('G deve ser simples e unitário, com extremos em V')
                H_G[v].add(w)
        if any(v not in H_G[w] for v in self.V for w in H_G[v]):
            raise ValueError('adj deve representar G não dirigido nos dois sentidos')
        if not _connected(Vset, H_G):
            raise ValueError('G deve ser conexo')
        arcs = tuple(A_r)
        expected = set(construir_arcos_alcance(self.V, adj, r))
        if set(arcs) != expected or len(arcs) != len(expected):
            raise ValueError('A_r não coincide com o alcance de G e r')
        self._A_r = tuple(sorted(arcs))
        self._H = grafo_H(self.V, self._A_r)

    @property
    def reach_graph(self):
        """H=G^r validado (vizinhanças abertas, imutáveis) para o pricing."""
        return _freeze({v: frozenset(self._H[v]) for v in self.V})

    @property
    def columns(self):
        """Q_R em ordem de inserção; triplas e conjuntos são imutáveis."""
        return tuple(self._lam)

    @property
    def metadata(self):
        """Metadados estruturais; não contém resultado experimental."""
        return _freeze({'k_hash': self.k_hash, 'n_K': len(self.K),
                        'n_K_added': len(self._k_rows), 'n_D': len(self.D),
                        'n_columns': len(self._lam), 'Q_R': self.columns,
                        'revision': self._revision})

    def validate_column(self, column):
        """Valida exatamente Q; não fixa matching nem exige I/J dentro de W."""
        W, I, J = _canonical_column(column)
        if not W or not W <= set(self.V) or not _connected(W, self._H):
            raise ValueError('W deve ser não vazio, contido em V e conexo em H')
        if not I or len(I) != len(J) or not I <= set(self.S) or not J <= set(self.T):
            raise ValueError('exige I⊆S, J⊆T e 1<=|I|=|J|')
        BW = B_de(W, self._H)
        if not I | J <= BW:
            raise ValueError('terminais de I/J devem pertencer a B(W)')
        return W, I, J

    def _ensure_open(self):
        if self._disposed:
            raise RuntimeError('master já encerrado')

    def add_column(self, column):
        """Insere uma coluna válida; erros de validação não alteram o RMP."""
        self._ensure_open()
        column = self.validate_column(column)
        if column in self._lam:
            raise DuplicateColumnError('coluna (W,I,J) duplicada')
        W, I, J = column
        rows = ([self._r1[s] for s in sorted(I)] + [self._r2[t] for t in sorted(J)]
                + [self._r3[v] for v in sorted(W)])
        # Não há coeficiente em K: cortes dependem somente de y.
        self._last_result = None
        self._lam[column] = self._model.addVar(
            lb=0, ub=GRB.INFINITY, obj=0, vtype=GRB.CONTINUOUS,
            column=gp.Column([1.0] * len(rows), rows), name=f'lam[{len(self._lam)}]',
        )
        self._revision += 1
        return column

    def _dual_snapshot(self, tolerance):
        md = self._model
        if md.Status != GRB.OPTIMAL or md.IsMIP:
            raise RuntimeError('duais exigem LP contínuo com status OPTIMAL')
        values = numerical_dual(
            self.S, self.T, self.V, self.K,
            pi={s: c.Pi for s, c in self._r1.items()},
            tau={t: c.Pi for t, c in self._r2.items()},
            mu={v: -c.Pi for v, c in self._r3.items()},
            kappa={Z: c.Pi for Z, c in self._k_rows.items()},
        )
        rc = {q: values.column_rc(q) for q in self._lam}
        drc = {e: values.direct_rc(e) for e in self.D}
        solver_rc = _numeric_map({q: v.RC for q, v in self._lam.items()}, self._lam, 'RC lambda')
        solver_drc = _numeric_map({e: v.RC for e, v in self._d.items()}, self.D, 'RC d')
        errors = [abs(rc[q] - solver_rc[q]) for q in rc]
        errors += [abs(drc[e] - solver_drc[e]) for e in drc]
        for v in self.V:
            # RC nativo de y NÃO contém eta; o UB é tratado pelo solver.
            native_rc = math.fsum([1.0, -values.mu[v]]
                                  + [-values.kappa[Z] for Z in self.K if v in Z])
            if not math.isfinite(self._y[v].RC):
                raise ValueError('RC y não finito')
            errors.append(abs(native_rc - self._y[v].RC))
        violations = [-x for x in (*values.mu.values(), *values.kappa.values(),
                                   *rc.values(), *drc.values())]
        checks = DualChecks(abs(md.ObjVal - values.L), max(errors, default=0.0),
                            max([0.0] + violations), tolerance)
        return DualSnapshot(values, self._revision, self._solve_id, self.k_hash,
                            _freeze(rc), _freeze(drc), solver_rc, solver_drc, checks)

    def solve(self, *, params=None, check_tolerance=1e-7):
        """Resolve somente o LP. Limites são por chamada, não orçamento de CG.

        Params permitidos constam de _ALLOWED_PARAMS. Os defaults são
        restaurados em cada chamada (inclusive limites infinitos), para
        não reutilizar TimeLimit/WorkLimit acidentalmente. O futuro laço
        deverá passar o orçamento restante e somar Work por sua conta.
        check_tolerance é diagnóstico absoluto, não margem de certificado.
        """
        self._ensure_open()
        params = dict(params or {})
        if set(params) - _ALLOWED_PARAMS:
            raise ValueError(f'parâmetros não permitidos: {sorted(set(params) - _ALLOWED_PARAMS)}')
        if not math.isfinite(check_tolerance) or check_tolerance <= 0:
            raise ValueError('check_tolerance deve ser finita e positiva')
        self._last_result = None
        self._solve_id += 1
        md = self._model
        md.resetParams()
        try:
            for name, value in (_DEFAULT_PARAMS | params).items():
                md.setParam(name, value)
        except gp.GurobiError as exc:
            raise ValueError(f'parâmetro Gurobi inválido: {exc}') from exc
        used = _freeze({name: md.getParamInfo(name)[2]
                        for name in sorted(_ALLOWED_PARAMS | set(_DEFAULT_PARAMS))})
        objective = dual = error = runtime = work = None
        status = None
        status_name = 'SOLVER_ERROR'
        try:
            md.optimize()
            status = int(md.Status)
            status_name = _STATUS_NAMES.get(status, f'UNKNOWN_STATUS_{status}')
            runtime, work = float(md.Runtime), float(md.Work)
            if status == GRB.OPTIMAL:
                objective = float(md.ObjVal)
                if not math.isfinite(objective):
                    raise ValueError('objetivo RMP não finito')
                candidate = self._dual_snapshot(check_tolerance)
                if candidate.checks.passed:
                    dual = candidate
                else:
                    error = f'checagem dual numérica falhou: {candidate.checks}'
        except (gp.GurobiError, ValueError) as exc:
            code = f' [{exc.errno}]' if isinstance(exc, gp.GurobiError) else ''
            error = f'{type(exc).__name__}{code}: {exc}'
        result = MasterResult(status, status_name, objective, dual, error, used,
                              tuple(gp.gurobi.version()), self._revision, self._solve_id,
                              runtime, work)
        self._last_result = result
        return result

    def extract_duals(self):
        """Último snapshot válido; nunca consulta Pi após status não ótimo."""
        self._ensure_open()
        if self._last_result is None or self._last_result.dual is None:
            raise RuntimeError('nenhum dual disponível da última resolução OPTIMAL')
        if self._model.Status != GRB.OPTIMAL or self._model.IsMIP:
            raise RuntimeError('modelo não está em estado LP OPTIMAL')
        return self._last_result.dual

    def reduced_cost(self, column, *, snapshot=None):
        """Valida q e usa somente o vetor da última resolução deste master."""
        if snapshot is not None and (self._last_result is None
                                     or snapshot is not self._last_result.dual):
            raise StaleDualError('dual de outro master, revisão ou resolução')
        current = self.extract_duals()
        return current.values.column_rc(self.validate_column(column))

    def primal_values(self):
        """Cópias imutáveis da solução numérica ótima; não são certificado U."""
        self.extract_duals()
        return _freeze({'y': _freeze({v: x.X for v, x in self._y.items()}),
                        'd': _freeze({e: x.X for e, x in self._d.items()}),
                        'lambda': _freeze({q: x.X for q, x in self._lam.items()})})

    def dispose(self):
        """Libera somente o modelo pertencente a este objeto; idempotente."""
        if not self._disposed:
            self._last_result = None
            self._model.dispose()
            self._disposed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, *_exc):
        self.dispose()
