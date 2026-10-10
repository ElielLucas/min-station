"""N2-T2B / Entrega 2: oráculo de pricing MIP P0--P5 para o master F-CC+K.

Matemática: revisão v2.1, §§4--5 (custo reduzido, forma P0--P5, P-PROJ) e
§§5.3, 6.3 (política de certificação). Não implementa geração de colunas,
certificação N2-T3, ENUM/N1/N2 nem escrita de resultados.

Uso (snapshot da última resolução OPTIMAL do master):
    result = master.solve()
    pricing = price(master, result.dual, params={'TimeLimit': 10})
    if pricing.outcome == NEGATIVE_COLUMN:
        column = pricing.column   # já validada por master.validate_column
        # inserir no master é responsabilidade do laço (Entrega 3)

Garantias e limites:
- O MIP P0--P5 é exato por projeção sobre (x,a,b) (P-PROJ); a solução é
  numérica. Toda coluna extraída é validada combinatoriamente pelo master e
  seu custo reduzido é recalculado a partir do vetor dual, não do ObjVal.
- Um status OPTIMAL, ObjBound ou ObjBoundC NÃO prova ausência de colunas
  negativas: certification_status é sempre UNCERTIFIED e
  proves_no_negative_column é sempre False nesta entrega. O bound do solver
  é registrado somente como diagnóstico (ObjBoundC).
- Uma execução interrompida pode devolver coluna aproveitável; uma execução
  sem coluna negativa nada prova sobre Q.
- O pricing não modifica o master.
"""
# E402: bootstrap do diretório experimental; E741: notação normativa W,I,J.
# ruff: noqa: E402, E741
import math
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gurobipy as gp
from gurobipy import GRB
from n2_t2b_master import DualValues, StaleDualError

# Desfechos da chamada (outcome).
NEGATIVE_COLUMN = 'NEGATIVE_COLUMN'
NONNEGATIVE_INCUMBENT = 'NONNEGATIVE_INCUMBENT'
NO_INCUMBENT = 'NO_INCUMBENT'
INVALID_INCUMBENT = 'INVALID_INCUMBENT'
OBJECTIVE_MISMATCH = 'OBJECTIVE_MISMATCH'
SOLVER_ERROR = 'SOLVER_ERROR'

# Término do solver (termination), separado do desfecho combinatório.
NUMERICALLY_OPTIMAL = 'NUMERICALLY_OPTIMAL'
TIME_LIMIT = 'TIME_LIMIT'
OTHER_LIMIT = 'OTHER_LIMIT'
SOLVER_FAILURE = 'SOLVER_FAILURE'

UNCERTIFIED = 'UNCERTIFIED'

_STATUS_NAMES = {
    getattr(GRB, name): name for name in (
        'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED',
        'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT',
        'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL', 'INPROGRESS', 'USER_OBJ_LIMIT',
        'WORK_LIMIT', 'MEM_LIMIT',
    )
}
_OTHER_LIMITS = frozenset({
    GRB.ITERATION_LIMIT, GRB.NODE_LIMIT, GRB.SOLUTION_LIMIT, GRB.INTERRUPTED,
    GRB.USER_OBJ_LIMIT, GRB.WORK_LIMIT, GRB.MEM_LIMIT, GRB.SUBOPTIMAL,
})
# Aceitação do incumbente: toda binária de P0--P5 (x, a, b, rho) deve estar a no
# máximo esta distância de {0,1}. É independente do IntFeasTol do solver (que o
# chamador pode afrouxar): valores mais distantes não definem uma configuração
# inteira e o incumbente é rejeitado. Não é margem de certificação.
INTEGRALITY_TOLERANCE = 1e-6

# MIPGap=0 e IntFeasTol mínimo: só reduzem resíduos numéricos, não certificam.
_DEFAULT_PARAMS = {'OutputFlag': 0, 'Seed': 42, 'Threads': 1,
                   'MIPGap': 0.0, 'MIPGapAbs': 0.0, 'IntFeasTol': 1e-9}
_ALLOWED_PARAMS = frozenset({
    'Seed', 'Threads', 'TimeLimit', 'WorkLimit', 'NodeLimit', 'SolutionLimit',
    'IterationLimit', 'MIPGap', 'MIPGapAbs', 'IntFeasTol', 'FeasibilityTol',
    'OptimalityTol', 'NumericFocus', 'Presolve', 'Heuristics', 'Cuts', 'MIPFocus',
})


class PricingInputError(ValueError):
    """Vetor dual ou parâmetros incompatíveis com o master."""


@dataclass(frozen=True)
class PricingResult:
    """Registro auditável de uma chamada; nunca é certificado de LB.

    outcome descreve a coluna (validação combinatória + RC recalculado);
    termination descreve o solver. column só é não nula se validada.
    reduced_cost é recalculado do vetor dual; mip_objective é o ObjVal.
    solver_bound (ObjBoundC) é diagnóstico numérico, não um ℓ válido.
    pricing_label é sempre 'heuristic' no sentido da spec (story 2B AC3-AC4):
    MIP numérico não prova ausência de coluna negativa (revisão v2.1 §6.3).
    """
    outcome: str
    termination: str
    status: int | None
    status_name: str
    column: tuple | None
    reduced_cost: float | None
    mip_objective: float | None
    objective_mismatch: float | None
    max_integrality_violation: float | None
    solver_bound: float | None
    solution_count: int
    dual_source: str
    revision: int | None
    solve_id: int | None
    k_hash: str
    entry_tolerance: float
    mismatch_tolerance: float
    parameters: Mapping
    gurobi_version: tuple
    runtime: float | None
    work: float | None
    error: str | None
    integrality_tolerance: float = INTEGRALITY_TOLERANCE
    pricing_label: str = 'heuristic'
    certification_status: str = UNCERTIFIED
    proves_no_negative_column: bool = False
    scope: str = 'PRICING_NUMERICAL_ONLY'

    @property
    def is_negative_column(self):
        return self.outcome == NEGATIVE_COLUMN


def _check_vector(master, values):
    """Mesmos índices do master e somente floats finitos."""
    if not isinstance(values, DualValues):
        raise PricingInputError('esperado DualValues de n2_t2b_master')
    for name, mapping, keys in (('pi', values.pi, master.S), ('tau', values.tau, master.T),
                                ('mu', values.mu, master.V), ('kappa', values.kappa, master.K)):
        if set(mapping) != set(keys):
            raise PricingInputError(f'índices de {name} não coincidem com o master')
        for k in keys:
            x = mapping[k]
            if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x):
                raise PricingInputError(f'{name} contém valor ausente ou não finito')


def _objective_coefficients(master, values):
    """Coeficientes de P0: +μ_v em x_v, -π_s em a_s, -τ_t em b_t."""
    return ({v: float(values.mu[v]) for v in master.V},
            {s: -float(values.pi[s]) for s in master.S},
            {t: -float(values.tau[t]) for t in master.T})


def _add_eligibility_balance(md, master, H, x, a, b):
    """P1 (elegibilidade por N_H[·]) e P2 (balanço, |I|>=1)."""
    for s in master.S:
        md.addConstr(a[s] <= gp.quicksum(x[v] for v in sorted({s} | H[s])), name=f'P1a[{s}]')
    for t in master.T:
        md.addConstr(b[t] <= gp.quicksum(x[v] for v in sorted({t} | H[t])), name=f'P1b[{t}]')
    md.addConstr(gp.quicksum(a.values()) == gp.quicksum(b.values()), name='P2bal')
    md.addConstr(gp.quicksum(a.values()) >= 1, name='P2min')


def _add_connectivity(md, master, H, x):
    """P3--P5: raiz única, fonte g na raiz, fluxo de conectividade em A_H."""
    n = len(master.V)
    arcs = [(u, w) for u in master.V for w in sorted(H[u])]
    rho = {v: md.addVar(vtype=GRB.BINARY, name=f'rho[{v}]') for v in master.V}
    g = {v: md.addVar(lb=0, ub=GRB.INFINITY, name=f'g[{v}]') for v in master.V}
    f = {e: md.addVar(lb=0, ub=GRB.INFINITY, name=f'f[{e[0]},{e[1]}]') for e in arcs}
    md.addConstr(gp.quicksum(rho.values()) == 1, name='P3root')
    for v in master.V:
        md.addConstr(rho[v] <= x[v], name=f'P3rx[{v}]')
        md.addConstr(g[v] <= n * rho[v], name=f'P3g[{v}]')
        md.addConstr(g[v] + gp.quicksum(f[u, v] for u in sorted(H[v]))
                     - gp.quicksum(f[v, w] for w in sorted(H[v])) == x[v], name=f'P4[{v}]')
    for (u, w) in arcs:
        md.addConstr(f[u, w] <= (n - 1) * x[u], name=f'P5u[{u},{w}]')
        md.addConstr(f[u, w] <= (n - 1) * x[w], name=f'P5w[{u},{w}]')


def build_pricing_model(master, values):
    """Modelo P0--P5 (Gurobi) e handles (x, a, b). O chamador faz dispose."""
    H = master.reach_graph
    md = gp.Model('N2-T2B-PRICING-P0-P5')
    try:
        md.Params.OutputFlag = 0
        cx, ca, cb = _objective_coefficients(master, values)
        x = {v: md.addVar(vtype=GRB.BINARY, obj=cx[v], name=f'x[{v}]') for v in master.V}
        a = {s: md.addVar(vtype=GRB.BINARY, obj=ca[s], name=f'a[{s}]') for s in master.S}
        b = {t: md.addVar(vtype=GRB.BINARY, obj=cb[t], name=f'b[{t}]') for t in master.T}
        md.ModelSense = GRB.MINIMIZE
        _add_eligibility_balance(md, master, H, x, a, b)
        _add_connectivity(md, master, H, x)
        md.update()
        return md, x, a, b
    except Exception:
        md.dispose()
        raise


def _binary_values(md):
    """Valores do incumbente de todas as binárias do modelo (x, a, b, rho)."""
    binaries = [var for var in md.getVars() if var.VType == GRB.BINARY]
    return md.getAttr('X', binaries)


def _integrality_violation(values):
    """max dist(valor, {0,1}); infinito se houver valor não finito."""
    if not all(math.isfinite(v) for v in values):
        return math.inf
    return max((min(abs(v), abs(1 - v)) for v in values), default=0.0)


def _termination(status):
    if status == GRB.OPTIMAL:
        return NUMERICALLY_OPTIMAL
    if status == GRB.TIME_LIMIT:
        return TIME_LIMIT
    if status in _OTHER_LIMITS:
        return OTHER_LIMIT
    return SOLVER_FAILURE


def _solve(master, values, *, dual_source, revision, solve_id, params,
           entry_tolerance, mismatch_tolerance):
    params = dict(params or {})
    if set(params) - _ALLOWED_PARAMS:
        raise PricingInputError(f'parâmetros não permitidos: {sorted(set(params) - _ALLOWED_PARAMS)}')
    for name, tol in (('entry_tolerance', entry_tolerance),
                      ('mismatch_tolerance', mismatch_tolerance)):
        if not math.isfinite(tol) or tol < 0:
            raise PricingInputError(f'{name} deve ser finita e não negativa')
    _check_vector(master, values)
    md, x, a, b = build_pricing_model(master, values)
    status, status_name, termination = None, 'SOLVER_ERROR', SOLVER_FAILURE
    column = rc = objective = mismatch = viol = bound = runtime = work = error = None
    sol_count = 0
    outcome = SOLVER_ERROR
    try:
        try:
            for name, value in (_DEFAULT_PARAMS | params).items():
                md.setParam(name, value)
        except gp.GurobiError as exc:
            raise PricingInputError(f'parâmetro Gurobi inválido: {exc}') from exc
        used = MappingProxyType({name: md.getParamInfo(name)[2]
                                 for name in sorted(_ALLOWED_PARAMS | set(_DEFAULT_PARAMS))})
        try:
            md.optimize()
            status = int(md.Status)
            status_name = _STATUS_NAMES.get(status, f'UNKNOWN_STATUS_{status}')
            termination = _termination(status)
            runtime, work = float(md.Runtime), float(md.Work)
            sol_count = int(md.SolCount)
            try:
                bound = float(md.ObjBoundC)
            except (gp.GurobiError, AttributeError):
                bound = None
            if sol_count == 0:
                outcome = NO_INCUMBENT if termination != SOLVER_FAILURE else SOLVER_ERROR
            else:
                objective = float(md.ObjVal)
                viol = _integrality_violation(_binary_values(md))
                W = frozenset(v for v, var in x.items() if var.X > 0.5)
                I = frozenset(s for s, var in a.items() if var.X > 0.5)
                J = frozenset(t for t, var in b.items() if var.X > 0.5)
                try:
                    if viol > INTEGRALITY_TOLERANCE:
                        raise ValueError(f'incumbente não inteiro: violação {viol!r} > '
                                         f'{INTEGRALITY_TOLERANCE!r}')
                    column = master.validate_column((W, I, J))
                except ValueError as exc:
                    column = None
                    outcome, error = INVALID_INCUMBENT, f'incumbente rejeitado: {exc}'
                else:
                    rc = values.column_rc(column)
                    mismatch = abs(objective - rc)
                    if not math.isfinite(objective) or mismatch > mismatch_tolerance:
                        outcome = OBJECTIVE_MISMATCH
                        error = f'|ObjVal - rc| = {mismatch!r} > {mismatch_tolerance!r}'
                        column = None
                    elif rc < -entry_tolerance:
                        outcome = NEGATIVE_COLUMN
                    else:
                        outcome = NONNEGATIVE_INCUMBENT
            if termination == SOLVER_FAILURE and error is None:
                error = f'status do solver: {status_name}'
        except gp.GurobiError as exc:
            outcome, termination = SOLVER_ERROR, SOLVER_FAILURE
            error = f'GurobiError [{exc.errno}]: {exc}'
    finally:
        md.dispose()
    return PricingResult(
        outcome=outcome, termination=termination, status=status, status_name=status_name,
        column=column, reduced_cost=rc, mip_objective=objective,
        objective_mismatch=mismatch, max_integrality_violation=viol, solver_bound=bound,
        solution_count=sol_count, dual_source=dual_source, revision=revision,
        solve_id=solve_id, k_hash=master.k_hash, entry_tolerance=entry_tolerance,
        mismatch_tolerance=mismatch_tolerance, parameters=used,
        gurobi_version=tuple(gp.gurobi.version()), runtime=runtime, work=work, error=error,
    )


def price(master, snapshot, *, params=None, entry_tolerance=1e-7, mismatch_tolerance=1e-6):
    """Pricing com o snapshot da última resolução OPTIMAL deste master.

    Rejeita snapshot de outro master, revisão ou resolução (StaleDualError),
    mesma regra de RestrictedMaster.reduced_cost. Não altera o master.
    """
    if snapshot is None:
        raise PricingInputError('snapshot dual ausente')
    try:
        current = master.extract_duals()
    except RuntimeError as exc:
        raise StaleDualError(f'master sem dual corrente: {exc}') from exc
    if snapshot is not current or snapshot.k_hash != master.k_hash:
        raise StaleDualError('dual de outro master, revisão ou resolução')
    return _solve(master, snapshot.values, dual_source='MASTER_SNAPSHOT',
                  revision=snapshot.revision, solve_id=snapshot.solve_id, params=params,
                  entry_tolerance=entry_tolerance, mismatch_tolerance=mismatch_tolerance)


def price_vector(master, values, *, params=None, entry_tolerance=1e-7,
                 mismatch_tolerance=1e-6):
    """Pricing para um vetor arbitrário com os índices do master.

    O vetor não é vinculado a nenhuma resolução (dual_source=ARBITRARY_VECTOR);
    usar para controles e análise. O laço de colunas deve usar price().
    """
    return _solve(master, values, dual_source='ARBITRARY_VECTOR', revision=None,
                  solve_id=None, params=params, entry_tolerance=entry_tolerance,
                  mismatch_tolerance=mismatch_tolerance)
