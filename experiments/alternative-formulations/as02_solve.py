"""Executores da AS-02: Gurobi no projeto, HiGHS/SciPy para auditoria local.

Não converte timeouts/erros em objetivo zero ou em certificados.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class SolveResult:
    status: str
    objective: float | None
    backend: str
    provenance: str


def solve_gurobi(compiled, fixed_y=None, *, time_limit=60, threads=1):
    from gurobipy import Model, GRB, quicksum

    model = Model('AS02-auditoria')
    model.Params.OutputFlag = 0
    model.Params.Threads = threads
    model.Params.Seed = 0
    model.Params.TimeLimit = time_limit
    fixed_y = fixed_y or {}
    var = []
    for v in compiled.variables:
        value = fixed_y.get(v.name[2:-1]) if v.name.startswith('y[') else None
        lb, ub = ((value, value) if value is not None else (v.lb, v.ub))
        var.append(model.addVar(lb=lb, ub=ub if ub != inf else GRB.INFINITY,
                                vtype=GRB.BINARY if v.binary else GRB.CONTINUOUS,
                                name=v.name))
    model.setObjective(quicksum(coef * var[j] for j, coef in compiled.objective.items()), GRB.MINIMIZE)
    for row in compiled.equations:
        expr = quicksum(coef * var[j] for j, coef in row.terms)
        if row.sense == '==':
            model.addConstr(expr == row.rhs, name=row.name)
        elif row.sense == '<=':
            model.addConstr(expr <= row.rhs, name=row.name)
        else:
            model.addConstr(expr >= row.rhs, name=row.name)
    model.optimize()
    if model.Status == GRB.OPTIMAL:
        return SolveResult('OPTIMAL', model.ObjVal, 'gurobi', 'LP-numérico' if not any(v.binary for v in compiled.variables) else 'MIP-numérico')
    if model.Status == GRB.INFEASIBLE:
        return SolveResult('INFEASIBLE', None, 'gurobi', 'solver')
    return SolveResult(f'UNRESOLVED_{model.Status}', None, 'gurobi', 'solver')


def solve_scipy(compiled, fixed_y=None, *, time_limit=60):
    """Backend de teste não requerido no Poetry, separado do Gurobi principal."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix

    row_i, col_i, data, lows, ups = [], [], [], [], []
    for i, eq in enumerate(compiled.equations):
        for j, value in eq.terms:
            row_i.append(i)
            col_i.append(j)
            data.append(value)
        lows.append(eq.rhs if eq.sense in ('==', '>=') else -inf)
        ups.append(eq.rhs if eq.sense in ('==', '<=') else inf)
    n = len(compiled.variables)
    a = coo_matrix((data, (row_i, col_i)), shape=(len(lows), n)).tocsr()
    objective = np.zeros(n)
    for j, coef in compiled.objective.items():
        objective[j] = coef
    lo = np.array([v.lb for v in compiled.variables])
    hi = np.array([v.ub for v in compiled.variables])
    fixed_y = fixed_y or {}
    for j, var in enumerate(compiled.variables):
        if var.name.startswith('y[') and var.name[2:-1] in fixed_y:
            lo[j] = hi[j] = float(fixed_y[var.name[2:-1]])
    output = milp(objective, integrality=np.array([int(v.binary) for v in compiled.variables]),
                  bounds=Bounds(lo, hi), constraints=LinearConstraint(a, lows, ups),
                  options={'time_limit': float(time_limit)})
    if output.status == 0:
        return SolveResult('OPTIMAL', float(output.fun), 'scipy-highs', 'LP-numérico' if not any(v.binary for v in compiled.variables) else 'MIP-numérico')
    if output.status == 2:
        return SolveResult('INFEASIBLE', None, 'scipy-highs', 'solver')
    return SolveResult(f'UNRESOLVED_{output.status}', None, 'scipy-highs', 'solver')


def solve(compiled, fixed_y=None, *, backend='gurobi', time_limit=60):
    if backend == 'gurobi':
        return solve_gurobi(compiled, fixed_y=fixed_y, time_limit=time_limit)
    if backend == 'scipy-highs':
        return solve_scipy(compiled, fixed_y=fixed_y, time_limit=time_limit)
    raise ValueError(f'Backend desconhecido: {backend}')
