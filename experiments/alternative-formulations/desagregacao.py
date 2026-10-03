"""Fluxo desagregado por origem, estações em todo V.

A formulação está em docs/technical/reference/desagregacao-por-origem.md.
Não substitui baseline.py.
"""

import time

from gurobipy import GRB, Model, quicksum


def construir_modelo_desagregado(S, T, V, arcos):
    """Devolve (modelo, y, p, f). y binário, fluxo 0/1 por origem."""
    S, T, V = list(S), list(T), list(V)
    T_set = set(T)
    modelo = Model('MIN-STATION-DESAGREGADO')
    y = {v: modelo.addVar(vtype=GRB.BINARY, name=f'y[{v}]') for v in V}
    p = {
        (s, t): modelo.addVar(vtype=GRB.BINARY, name=f'p[{s},{t}]')
        for s in S for t in T
    }
    f = {
        (s, u, v): modelo.addVar(vtype=GRB.BINARY, name=f'f[{s},{u},{v}]')
        for s in S for (u, v) in arcos
    }
    modelo.setObjective(quicksum(y[v] for v in V), GRB.MINIMIZE)
    for s in S:
        modelo.addConstr(quicksum(p[s, t] for t in T) == 1)
    for t in T:
        modelo.addConstr(quicksum(p[s, t] for s in S) == 1)

    entrada = {(s, v): [] for s in S for v in V}
    saida = {(s, v): [] for s in S for v in V}
    for s in S:
        for u, v in arcos:
            saida[s, u].append(f[s, u, v])
            entrada[s, v].append(f[s, u, v])

    for s in S:
        for v in V:
            entra = quicksum(entrada[s, v])
            sai = quicksum(saida[s, v])
            demanda = p[s, v] if v in T_set else 0
            oferta = 1 if v == s else 0
            modelo.addConstr(sai - entra == oferta - demanda, name=f'bal[{s},{v}]')
            if v in T_set:
                modelo.addConstr(entra <= p[s, v] + y[v])
            else:
                modelo.addConstr(entra <= y[v])
            if v == s:
                modelo.addConstr(sai <= 1)
            else:
                modelo.addConstr(sai <= y[v])
    modelo.update()
    return modelo, y, p, f


def medir_par(S, T, V, arcos, construir_base):
    """z_LP e OPT dos dois modelos, com tamanho e tempos de montagem e de LP."""
    t0 = time.monotonic()
    base, _y, _f, n_arcos, n_verts = construir_base(S, T, V, arcos)
    t_base = time.monotonic() - t0
    base.Params.OutputFlag = 0
    base.Params.Threads = 1
    base.Params.Seed = 42
    lp = base.relax()
    lp.Params.OutputFlag = 0
    t0 = time.monotonic()
    lp.optimize()
    t_lp_base = time.monotonic() - t0
    z_base = float(lp.ObjVal)
    base.optimize()
    if base.Status != GRB.OPTIMAL:
        raise RuntimeError(f'base status {base.Status}')
    opt_base = float(base.ObjVal)
    n_vars_base = base.NumVars
    n_cons_base = base.NumConstrs
    base.dispose()
    lp.dispose()

    t0 = time.monotonic()
    des, _y, _p, _f = construir_modelo_desagregado(S, T, V, arcos)
    t_des = time.monotonic() - t0
    des.Params.OutputFlag = 0
    des.Params.Threads = 1
    des.Params.Seed = 42
    dlp = des.relax()
    dlp.Params.OutputFlag = 0
    t0 = time.monotonic()
    dlp.optimize()
    t_lp_des = time.monotonic() - t0
    z_des = float(dlp.ObjVal)
    des.optimize()
    if des.Status != GRB.OPTIMAL:
        raise RuntimeError(f'desagregado status {des.Status}')
    opt_des = float(des.ObjVal)
    linha = {
        'z_lp_base': z_base,
        'z_lp_des': z_des,
        'opt_base': opt_base,
        'opt_des': opt_des,
        'vars_base': n_vars_base,
        'cons_base': n_cons_base,
        'vars_des': des.NumVars,
        'cons_des': des.NumConstrs,
        'arcos': n_arcos,
        'vertices': n_verts,
        't_montar_base': t_base,
        't_montar_des': t_des,
        't_lp_base': t_lp_base,
        't_lp_des': t_lp_des,
    }
    des.dispose()
    dlp.dispose()
    return linha
