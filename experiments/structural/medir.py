"""Medições pequenas das famílias: base, LP, núcleo. Não é o piloto."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))
sys.path.insert(0, str(HERE))

from gurobipy import GRB

from baseline import construir_modelo_baseline
from harness import measure_lp, prepare_cuts
from ms_utils import construir_arcos_alcance
from yspace import _build_ymodel


def otimo_base(S, T, V, adj, r):
    A = construir_arcos_alcance(V, adj, r)
    modelo, _y, _f, _na, _nv = construir_modelo_baseline(S, T, V, A)
    modelo.Params.OutputFlag = 0
    modelo.Params.Threads = 1
    modelo.Params.Seed = 42
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(f'base status {modelo.Status}')
    valor = float(modelo.ObjVal)
    modelo.dispose()
    return valor


def lp_com_cortes(S, T, V, adj, r, familias):
    A = construir_arcos_alcance(V, adj, r)
    cortes, counts = prepare_cuts(S, T, V, adj, A, r, familias)
    extras = list(counts.get('C6_cortes') or [])
    res = measure_lp(S, T, V, A, 'cont', list(cortes) + extras, seed=42, threads=1)
    return res['lp_bound'], counts


def nucleo(S, T, V, adj, r):
    A = construir_arcos_alcance(V, adj, r)
    cortes, _ = prepare_cuts(S, T, V, adj, A, r, {'C1', 'C2', 'C4'})
    modelo, _y = _build_ymodel(V, cortes, integer=True, seed=42, threads=1, time_limit=120)
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(f'núcleo status {modelo.Status}')
    valor = float(modelo.ObjVal)
    modelo.dispose()
    return valor


def otimos_do_nucleo(S, T, V, adj, r, teto=5000):
    """Todos os ótimos do núcleo inteiro. None se o pool enche antes de esgotar."""
    A = construir_arcos_alcance(V, adj, r)
    cortes, _ = prepare_cuts(S, T, V, adj, A, r, {'C1', 'C2', 'C4'})
    modelo, y = _build_ymodel(V, cortes, integer=True, seed=42, threads=1, time_limit=120)
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(f'núcleo status {modelo.Status}')
    opt = float(modelo.ObjVal)
    modelo.addConstr(modelo.getObjective() == opt)
    modelo.Params.PoolSolutions = teto
    modelo.Params.PoolSearchMode = 2
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(f'pool status {modelo.Status}')
    achados = []
    for i in range(modelo.SolCount):
        modelo.Params.SolutionNumber = i
        C = tuple(v for v in V if y[v].Xn > 0.5)
        achados.append(C)
    truncado = modelo.SolCount >= teto
    modelo.dispose()
    if truncado:
        return opt, None
    return opt, achados
