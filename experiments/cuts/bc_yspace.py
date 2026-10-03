"""
Branch-and-cut em y-space com corte combinatório lazy (linha A2).

O corte lazy (Teorema 6) separa, para cada incumbente inteiro ȳ, um conjunto
Z ∈ 𝒵 tal que ȳ é inviável no problema com fluxo agregado, adicionando
y(Z) ≥ 1. Por construção, esse corte é válido sem ressalva.

E8 substitui as peças do E7 identificadas como confundidoras
(`resultados-e7-pli.md` §5.1):
  1. MIP start: `build_primal_solution` (primal.py), reverse-delete + busca
     local, sempre devolve solução viável (o guloso do E7 podia parar antes
     de flow=m).
  2. Lazy no MIPSOL: `integer_oracle` (rede restrita S∪T∪C) em vez de
     `_build_flow_net_aggregate` sobre A_r inteiro — decisivo em instâncias
     com |A_r| grande (cc12-2p).
  3. Guarda de tempo explícita no callback via `cbGet(RUNTIME)` +
     `model.terminate()`, já que o `TimeLimit` do Gurobi não interrompe uma
     chamada de callback em andamento (estourou 5× em cc12-2p no E7).
  4. User cuts no MIPNODE: mantido do E7 (separação fracionária clássica,
     nós rasos).
"""

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from cuts import (
    build_neighborhoods,
    generate_C1,
    integer_oracle,
    separate_classical_fracs,
    InstanciaInviavel,
    cortes_ordenados,
    vertices_do_corte,
)
from yspace import _build_ymodel
from primal import build_primal_solution


# ── Branch-and-cut principal ───────────────────────────────────────────────────

def solve_bc_yspace(S, T, V, A_r, static_cuts=None, time_limit=900,
                    seed=42, threads=4, use_lazy=True,
                    use_mip_start=True, use_user_cuts=True,
                    max_node_user_cuts=200, primal_budget=60.0,
                    y_start=None, user_cuts_max_arcs=500_000):
    """
    Branch-and-cut em y-space.

    Parâmetros
    ----------
    static_cuts     : cortes a priori (ex.: C1+C2+C4); adicionados antes da otimização.
    use_lazy        : ativa callback MIPSOL com corte combinatório lazy (Teorema 6),
                      separado pelo oráculo restrito (`integer_oracle`).
    use_mip_start   : ativa `build_primal_solution` (reverse-delete + busca local)
                      para fornecer um incumbente inicial sempre viável.
    use_user_cuts   : ativa separação fracionária clássica no MIPNODE (nós rasos).
    max_node_user_cuts : limite de nós explorados para user cuts (nós "rasos").
    primal_budget   : orçamento de tempo (s) para a heurística primal do MIP start.
    y_start         : dict v -> 0/1 já calculado fora (ex.: o mesmo start entregue ao
                      compacto); se dado, `use_mip_start` é ignorado.
    user_cuts_max_arcs : acima deste |A_r| os user cuts ficam desligados, porque a
                      separação fracionária ainda monta a rede agregada completa.

    Retorna dict com: obj, bound, gap, status, time_s, n_lazy_cuts, n_lazy_calls,
                      n_user_cuts, n_user_calls, callback_time_s, cb_fraction,
                      y_star, tl_estourado.
    """
    S_set, T_set = set(S), set(T)
    m = len(S)
    N_plus, N_minus = build_neighborhoods(A_r)

    mip, y = _build_ymodel(V, static_cuts or [], integer=True, seed=seed,
                            threads=threads, time_limit=time_limit)

    if y_start is None and use_mip_start:
        primal = build_primal_solution(S, T, V, N_plus, seed=seed,
                                       total_budget=primal_budget)
        y_start = primal['y_bin'] if primal is not None else None
    if y_start is not None:
        for v in V:
            y[v].Start = y_start.get(v, 0.0)
        mip.update()

    if use_user_cuts and len(A_r) > user_cuts_max_arcs:
        use_user_cuts = False

    contador = {
        'lazy_cuts': 0, 'lazy_calls': 0,
        'user_cuts': 0, 'user_calls': 0,
        'cb_time': 0.0, 'tl_estourado': False,
    }

    def callback(modelo, where):
        if where not in (GRB.Callback.MIPSOL, GRB.Callback.MIPNODE):
            return
        t_cb = time.monotonic()

        if where == GRB.Callback.MIPSOL and use_lazy:
            # Corretude antes de tudo: TODO incumbente inteiro tem de ser
            # validado pelo oráculo antes que o callback devolva o controle
            # ao Gurobi, senão ele aceita a solução sem checagem. A guarda de
            # tempo (abaixo) só pode disparar `terminate()` DEPOIS da
            # validação desta chamada — nunca antes. Um bug anterior chamava
            # `terminate()` logo no início do callback, e o Gurobi aceitava
            # como incumbente final o ȳ que estava sendo avaliado naquele
            # instante sem ter recebido o corte lazy correspondente:
            # verificado no compacto, era INFEASIBLE (Chicago, obj=14 vs.
            # OPT=17 real).
            contador['lazy_calls'] += 1
            y_bin = {v: modelo.cbGetSolution(y[v]) for v in V}
            C = frozenset(v for v, val in y_bin.items() if val > 0.5)

            viavel, Z = integer_oracle(S, T, N_plus, C)
            if not viavel:
                if not Z:
                    raise InstanciaInviavel(
                        f'callback BC-y lazy: Z=∅ com C={sorted(C)[:10]}...'
                    )
                vs = vertices_do_corte(Z, y)
                if vs:
                    modelo.cbLazy(sum(y[v] for v in vs) >= 1)
                    contador['lazy_cuts'] += 1

        elif (where == GRB.Callback.MIPNODE and use_user_cuts
              and modelo.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL):
            node_cnt = int(modelo.cbGet(GRB.Callback.MIPNODE_NODCNT))
            if node_cnt <= max_node_user_cuts:
                contador['user_calls'] += 1
                y_frac = {v: modelo.cbGetNodeRel(y[v]) for v in V}
                try:
                    new_cuts = separate_classical_fracs(S, T, A_r, y_frac)
                except InstanciaInviavel:
                    new_cuts = []
                for Z in cortes_ordenados(new_cuts):
                    vs = vertices_do_corte(Z, y)
                    if vs:
                        modelo.cbCut(sum(y[v] for v in vs) >= 1)
                        contador['user_cuts'] += 1

        # Guarda de tempo: só DEPOIS de validar/cortar o incumbente ou node
        # atual. Serve para encerrar a busca (nenhum novo incumbente será
        # aceito sem validação, já feita acima) quando um oráculo
        # individualmente caro (rede grande) estourar o TimeLimit nativo do
        # Gurobi, que não interrompe uma chamada de callback em andamento.
        try:
            if modelo.cbGet(GRB.Callback.RUNTIME) > time_limit:
                contador['tl_estourado'] = True
                modelo.terminate()
        except Exception:
            pass  # RUNTIME não disponível neste where; TimeLimit do Gurobi ainda vale

        contador['cb_time'] += time.monotonic() - t_cb

    if use_lazy or use_user_cuts:
        mip.Params.LazyConstraints = 1
        t0 = time.monotonic()
        mip.optimize(callback)
        elapsed = time.monotonic() - t0
    else:
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
    y_star = None
    if mip.SolCount > 0:
        try:
            y_star = {v: y[v].X for v in V}
        except Exception:
            y_star = None

    cb_frac = contador['cb_time'] / elapsed if elapsed > 1e-6 else 0.0

    return {
        'obj': obj,
        'bound': bound,
        'gap': gap,
        'status': status,
        'time_s': elapsed,
        'n_lazy_cuts': contador['lazy_cuts'],
        'n_lazy_calls': contador['lazy_calls'],
        'n_user_cuts': contador['user_cuts'],
        'n_user_calls': contador['user_calls'],
        'callback_time_s': contador['cb_time'],
        'cb_fraction': cb_frac,
        'y_star': y_star,
        'tl_estourado': contador['tl_estourado'],
        'user_cuts_ativos': use_user_cuts,
    }


def prepare_static_c1(S, T, A_r):
    N_plus, N_minus = build_neighborhoods(A_r)
    return generate_C1(S, T, N_plus, N_minus)


# ── CBI: Benders combinatório com mestre exato iterado (E8, Bloco 4) ──────────

def solve_cbi(S, T, V, static_cuts, N_plus, time_limit=300, seed=42, threads=4,
              pool_solutions=50, ub_start=None):
    """
    Mestre exato iterado: resolve o núcleo (IP em y) sem pool até o ótimo,
    testa a incumbente no oráculo restrito e, se ela for inviável, acrescenta
    o corte 𝒵. Cada optimize deixa 5 s de reserva quando ainda há prazo, para
    o teste e para a iteração seguinte. O mestre é reconstruído a cada
    iteração como antes.

    Ótimo provado só quando o mestre terminou com status OPTIMAL e a
    incumbente é viável: o núcleo é uma relaxação (Teorema 6), então
    seu ótimo é LB e a solução viável é UB com o mesmo valor. Se o mestre
    parou pelo tempo, uma incumbente viável é só UB.

    LB reportado = maior ObjBound finito entre as iterações (cortes só são
    acrescentados, então todo ObjBound é LB válido do problema real).

    ub_start: dict opcional {'C': frozenset, 'obj': float} (ex.: heurística
    primal), usado como incumbente inicial.

    pool_solutions permanece na assinatura e não é aplicado: o pool antes do
    único optimize impedia o mestre de terminar.

    Retorna dict com: obj, bound, gap, status, time_s, iterations,
                      oracle_calls, n_cuts_total, n_z_cuts, master_time_s,
                      oracle_time_s, node_count, y_star.
    """
    all_cuts = cortes_ordenados(static_cuts or [])
    vistos = set(all_cuts)
    n_static = len(all_cuts)
    nogoods = []  # C's que reapareceram apesar do corte y(Z)>=1 gerado para elas
    t0 = time.monotonic()
    it = 0
    oracle_calls = 0
    master_s = 0.0
    oracle_s = 0.0
    node_count = 0
    lb = None
    best_C = ub_start['C'] if ub_start else None
    best_obj = float(ub_start['obj']) if ub_start else None
    testadas_inviaveis = set()

    def _resultado(status):
        gap = None
        if best_obj is not None and lb is not None and best_obj > 0:
            gap = max(0.0, (best_obj - lb) / best_obj)
        return {
            'obj': best_obj, 'bound': lb, 'gap': gap, 'status': status,
            'time_s': time.monotonic() - t0, 'iterations': it,
            'oracle_calls': oracle_calls, 'n_cuts_total': len(all_cuts),
            'n_z_cuts': len(all_cuts) - n_static,
            'master_time_s': master_s, 'oracle_time_s': oracle_s,
            'node_count': node_count,
            'y_star': ({v: (1.0 if v in best_C else 0.0) for v in V}
                       if best_C is not None else None),
        }

    while True:
        remaining = time_limit - (time.monotonic() - t0)
        if remaining <= 0.5:
            break
        it += 1

        # Reserva para testar a incumbente e abrir outra iteração. Sem ela,
        # o mestre que não fecha consome o prazo e o corte 𝒵 não chega a ser gerado.
        reserva = 5.0
        limite = remaining if remaining <= reserva + 1 else remaining - reserva
        mip, y = _build_ymodel(V, all_cuts, integer=True, seed=seed,
                               threads=threads, time_limit=limite)
        for C_ng in sorted(nogoods, key=lambda c: tuple(sorted(c))):
            mip.addConstr(
                sum(y[v] for v in V if v not in C_ng)
                + sum((1 - y[v]) for v in sorted(C_ng)) >= 1
            )
        tm = time.monotonic()
        mip.optimize()
        master_s += time.monotonic() - tm
        try:
            node_count += int(mip.NodeCount)
        except Exception:
            pass

        mestre_otimo = (mip.Status == GRB.OPTIMAL)
        try:
            b = float(mip.ObjBound)
            if b > float('-inf') and (lb is None or b > lb):
                lb = b
        except Exception:
            pass
        if mip.SolCount == 0:
            break
        opt_val = mip.ObjVal
        C = frozenset(v for v in V if y[v].X > 0.5)
        if mestre_otimo and abs(len(C) - opt_val) > 0.5:
            break

        if C in testadas_inviaveis:
            # Reapareceu apesar do corte gerado para ela (Z pode conter
            # vértice de C quando a saturação é interna a um vértice
            # instalado; o corte fica satisfeito por C). No-good explícito
            # na próxima reconstrução do mestre garante progresso.
            if C not in nogoods:
                nogoods.append(C)
            continue

        oracle_calls += 1
        to = time.monotonic()
        viavel, Z = integer_oracle(S, T, N_plus, C)
        oracle_s += time.monotonic() - to
        if viavel:
            if best_obj is None or len(C) < best_obj:
                best_C, best_obj = C, float(len(C))
            if mestre_otimo and abs(len(C) - opt_val) <= 0.5:
                lb = best_obj
                return _resultado('OPT')
        else:
            testadas_inviaveis.add(C)
            fz = frozenset(Z)
            if fz not in vistos:
                vistos.add(fz)
                all_cuts.append(fz)
                all_cuts.sort(key=lambda z: tuple(sorted(z)))

        if best_obj is not None and lb is not None and best_obj <= lb + 1e-9:
            return _resultado('OPT')

    return _resultado('TL')
