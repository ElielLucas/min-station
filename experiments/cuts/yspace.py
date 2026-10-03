"""
Modelo só em y (sem fluxo) para E2 e E3.

LP em y-space: min Σ y[v]  s.t.  y(Z) >= 1 para cada corte Z, 0 <= y[v] <= 1
IP em y-space: igual, mas y[v] ∈ {0,1}

Laço de separação para E2:
  Estágio 1: C1 + C2 + C4-DM estáticos
  Estágio 2: + C3 (origens e destinos) iterativo
  Estágio 3: + cortes fracionários clássicos (rede N(y*))
  Estágio 4: + C5 heurístico (limiar)

Cada estágio adiciona cortes ao LP e re-resolve até convergência ou max_rounds.
"""

import sys
import time
from pathlib import Path
from collections import deque

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from gurobipy import GRB, Model, quicksum
from cuts import (
    build_neighborhoods,
    generate_C1,
    generate_C2,
    generate_C4_DM,
    check_C3_violations,
    check_C3_violations_dest,
    separate_classical_fracs,
    generate_C5_threshold,
    assert_valid_cuts,
    cortes_ordenados,
    vertices_do_corte,
)


# ── Modelo base em y ──────────────────────────────────────────────────────────

def _build_ymodel(V, static_cuts, integer=False, seed=42, threads=4,
                  time_limit=600, output_flag=False, validate=None):
    """
    Constrói modelo em y-space com os cortes estáticos já embutidos.

    validate: opcional, tupla (S, T, A_r, N_plus, N_minus) para checar os
    cortes estáticos antes de adicioná-los (aborta com CorteInvalido se
    algum for inválido). N_plus/N_minus são obrigatórios aqui (não None)
    para não reconstruir vizinhanças a cada corte em instâncias grandes.
    """
    if validate is not None:
        S, T, A_r, N_plus, N_minus = validate
        assert_valid_cuts(S, T, A_r, static_cuts, origem='_build_ymodel',
                           N_plus=N_plus, N_minus=N_minus)

    m = Model()
    m.Params.OutputFlag = 0 if not output_flag else 1
    m.Params.Seed       = seed
    m.Params.Threads    = threads
    m.Params.TimeLimit  = time_limit

    vtype = GRB.BINARY if integer else GRB.CONTINUOUS
    y = {v: m.addVar(lb=0.0, ub=1.0, vtype=vtype, name=f'y[{v}]') for v in V}
    m.setObjective(quicksum(y.values()), GRB.MINIMIZE)
    m.update()

    for Z in cortes_ordenados(static_cuts):
        vs = vertices_do_corte(Z, y)
        if vs:
            m.addConstr(quicksum(y[v] for v in vs) >= 1)

    m.update()
    return m, y


def _extract_y_star(lp, y):
    return {v: lp.getVarByName(f'y[{v}]').X for v in y}


def _add_cuts(lp, y, cuts, validate=None, origem=''):
    """
    validate: opcional, tupla (S, T, A_r, N_plus, N_minus). Se dado, aborta
    com CorteInvalido antes de adicionar qualquer corte da leva caso algum
    seja inválido.
    """
    if validate is not None:
        S, T, A_r, N_plus, N_minus = validate
        assert_valid_cuts(S, T, A_r, cuts, origem=origem,
                           N_plus=N_plus, N_minus=N_minus)

    n = 0
    for Z in cortes_ordenados(cuts):
        vs = [v for v in vertices_do_corte(Z) if lp.getVarByName(f'y[{v}]') is not None]
        if vs:
            lp.addConstr(quicksum(lp.getVarByName(f'y[{v}]') for v in vs) >= 1)
            n += 1
    return n


# ── Laço de planos de corte (E2) ──────────────────────────────────────────────

def solve_lp_cutting_plane(S, T, V, adj, A_r, r,
                           max_rounds=30, time_per_stage=600,
                           seed=42, threads=4, validate_cuts=True):
    """
    LP em y-space com laço de separação em 4 estágios.

    validate_cuts: se True (padrão), cada corte é checado antes de entrar
    no modelo (aborta com CorteInvalido em caso de bug). Desligar só por
    custo, deixando isso explícito no chamador.

    Retorna dict com:
      stage_lp: dict {estágio: LP bound ao final}
      stage_cuts: dict {estágio: número de cortes adicionados nesse estágio}
      stage_time: dict {estágio: tempo em segundos}
      final_lp: LP bound final
      total_time: tempo total
      y_star: solução LP final
    """
    t_total = time.monotonic()
    N_plus, N_minus = build_neighborhoods(A_r)
    validate = (S, T, A_r, N_plus, N_minus) if validate_cuts else None

    # estágio 1: cortes estáticos a priori
    t0 = time.monotonic()
    static_C1 = generate_C1(S, T, N_plus, N_minus)
    static_C2 = generate_C2(S, T, adj, r, V)
    static_C4 = generate_C4_DM(S, T, N_plus, N_minus)
    static_all = cortes_ordenados(static_C1 + static_C2 + static_C4)

    lp, y = _build_ymodel(V, static_all, integer=False, seed=seed,
                           threads=threads, time_limit=time_per_stage,
                           validate=validate)
    lp.optimize()
    s1_lp = lp.ObjVal if lp.Status == GRB.OPTIMAL else None
    s1_cuts = len(static_all)
    s1_time = time.monotonic() - t0

    if lp.Status != GRB.OPTIMAL:
        return _failed_result(s1_lp, s1_cuts, s1_time, time.monotonic() - t_total)

    # estágio 2: C3 origens + destinos iterativo
    t0 = time.monotonic()
    s2_cuts = 0
    for _ in range(max_rounds):
        y_star = _extract_y_star(lp, y)
        c3_o = check_C3_violations(S, T, A_r, y_star)
        c3_d = check_C3_violations_dest(S, T, A_r, y_star)
        new_cuts = cortes_ordenados(c3_o + c3_d)
        if not new_cuts:
            break
        n = _add_cuts(lp, y, new_cuts, validate=validate, origem='C3')
        s2_cuts += n
        if n == 0:
            break
        lp.optimize()
        if lp.Status != GRB.OPTIMAL:
            break
    s2_lp = lp.ObjVal if lp.Status == GRB.OPTIMAL else None
    s2_time = time.monotonic() - t0

    # estágio 3: cortes fracionários clássicos via N(y*)
    t0 = time.monotonic()
    s3_cuts = 0
    for _ in range(max_rounds):
        y_star = _extract_y_star(lp, y)
        new_cuts = separate_classical_fracs(S, T, A_r, y_star)
        if not new_cuts:
            break
        n = _add_cuts(lp, y, new_cuts, validate=validate, origem='fracs_classicos')
        s3_cuts += n
        if n == 0:
            break
        lp.optimize()
        if lp.Status != GRB.OPTIMAL:
            break
    s3_lp = lp.ObjVal if lp.Status == GRB.OPTIMAL else None
    s3_time = time.monotonic() - t0

    # estágio 4: C5 heurístico (limiar)
    t0 = time.monotonic()
    s4_cuts = 0
    thresholds = (0.5, 0.3, 0.1, 0.01)
    for _ in range(max_rounds):
        y_star = _extract_y_star(lp, y)
        new_cuts = generate_C5_threshold(S, T, A_r, y_star, thresholds=thresholds)
        if not new_cuts:
            break
        n = _add_cuts(lp, y, new_cuts, validate=validate, origem='C5')
        s4_cuts += n
        if n == 0:
            break
        lp.optimize()
        if lp.Status != GRB.OPTIMAL:
            break
    s4_lp   = lp.ObjVal if lp.Status == GRB.OPTIMAL else None
    s4_time  = time.monotonic() - t0
    y_star   = _extract_y_star(lp, y) if lp.Status == GRB.OPTIMAL else {}

    return {
        'stage_lp':   {1: s1_lp, 2: s2_lp, 3: s3_lp, 4: s4_lp},
        'stage_cuts': {1: s1_cuts, 2: s2_cuts, 3: s3_cuts, 4: s4_cuts},
        'stage_time': {1: s1_time, 2: s2_time, 3: s3_time, 4: s4_time},
        'final_lp':   s4_lp,
        'total_time': time.monotonic() - t_total,
        'y_star':     y_star,
    }


def _failed_result(lp, cuts, t_stage, t_total):
    return {
        'stage_lp':   {1: lp, 2: None, 3: None, 4: None},
        'stage_cuts': {1: cuts, 2: 0, 3: 0, 4: 0},
        'stage_time': {1: t_stage, 2: 0, 3: 0, 4: 0},
        'final_lp':   lp,
        'total_time': t_total,
        'y_star':     {},
    }


# ── IP em y-space (E3) ────────────────────────────────────────────────────────

def solve_ip_yspace(S, T, V, adj, A_r, r,
                    extra_cuts=None,
                    time_limit=600, seed=42, threads=4, validate_cuts=False):
    """
    IP em y-space: y ∈ {0,1}^V, cortes C1+C2+C4 + extra_cuts.

    validate_cuts: padrão False aqui, diferente de solve_lp_cutting_plane,
    porque validar custa O(|A_r|) por corte (is_valid_cut faz uma BFS no grafo
    inteiro) — proibitivo com |A_r| grande. A rede de segurança de C1/C2/C4-DM
    é a regressão verify_c4_dm.py, não a validação em tempo de execução.
    Ligue explicitamente se passar extra_cuts de origem não auditada.

    Até 2026-09-26 esta docstring afirmava que C1/C2/C4-DM "já são validadas
    por oráculo nos gabaritos de regressão da rodada E5". Era falso — nenhuma
    regressão cobria a saída de generate_C4_DM, que gerava cortes inválidos
    com S∩T != 0 (ver correcao-c4-dm.md).

    Retorna dict com: ip_obj, ip_bound, ip_gap, ip_status, time_s,
                      n_static_cuts, n_c1, n_c2, n_c4.
    """
    N_plus, N_minus = build_neighborhoods(A_r)
    c1 = generate_C1(S, T, N_plus, N_minus)
    c2 = generate_C2(S, T, adj, r, V)
    c4 = generate_C4_DM(S, T, N_plus, N_minus)
    static = cortes_ordenados(c1 + c2 + c4 + (extra_cuts or []))

    validate = (S, T, A_r, N_plus, N_minus) if validate_cuts else None
    mip, y = _build_ymodel(V, static, integer=True, seed=seed,
                            threads=threads, time_limit=time_limit,
                            validate=validate)

    t0 = time.monotonic()
    mip.optimize()
    elapsed = time.monotonic() - t0

    status = mip.Status
    try:
        obj = float(mip.ObjVal) if mip.SolCount > 0 else None
    except Exception:
        obj = None
    try:
        bound = float(mip.ObjBound)
    except Exception:
        bound = None
    try:
        gap = float(mip.MIPGap) if mip.SolCount > 0 else None
    except Exception:
        gap = None
    C = frozenset(v for v, var in y.items() if var.X > 0.5) if mip.SolCount > 0 else None

    return {
        'ip_obj':          obj,
        'ip_bound':        bound,
        'ip_gap':          gap,
        'ip_status':       status,
        'time_s':          elapsed,
        'n_static_cuts':   len(static),
        'n_c1':            len(c1),
        'n_c2':            len(c2),
        'n_c4':            len(c4),
        'C':               C,
    }
