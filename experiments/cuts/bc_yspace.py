"""
E6: branch-and-cut só em y, com corte combinatório lazy (linha A2).

Motivação (E5, Bloco A/D): o núcleo de cobertura de hc9u resolve em 2,1s
com OPT=32 (E3), mas essa solução de 32 estações é INVIÁVEL no problema
com fluxo (max-flow=108 < m=128, verificado em verify_structure.py). Como
o núcleo é uma relaxação (Teorema 6, subconjunto de 𝒵), isso prova que
OPT(hc9u) > 32 estritamente e que o núcleo está esgotado — nenhum reforço
dele (zero-half, mochila, simetria) pode mover o número. O resíduo é de
acoplamento Hall multi-salto, exatamente a família 𝒵 completa do
Teorema 6, que é separável por max-flow na rede N(y).

Este módulo implementa o primeiro callback do repositório: MIPSOL lazy que,
para cada incumbente inteiro ȳ, testa viabilidade via max-flow na rede
agregada corrigida (cuts._build_flow_net_aggregate) e adiciona
y(Z) >= 1 quando ȳ é inviável. Por construção (Teorema 6), esse corte é
válido sem ressalva: nenhuma quebra de simetria ou heurística está
envolvida.
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
    _build_flow_net_aggregate,
    _edmonds_karp,
    _reachable_set,
    _extract_Z,
    InstanciaInviavel,
)
from yspace import _build_ymodel


def solve_bc_yspace(S, T, V, A_r, static_cuts=None, time_limit=900,
                     seed=42, threads=4, use_lazy=True):
    """
    Branch-and-cut em y-space. static_cuts: cortes a priori (ex.: C1).

    use_lazy: se True, ativa o callback MIPSOL com o corte combinatório
    lazy (Teorema 6). Se False, resolve só com static_cuts (controle).

    Retorna dict com: obj, bound, gap, status, time_s, n_lazy_cuts,
                      n_lazy_calls.
    """
    S_set, T_set = set(S), set(T)
    m = len(S)

    mip, y = _build_ymodel(V, static_cuts or [], integer=True, seed=seed,
                            threads=threads, time_limit=time_limit)

    contador = {'cuts': 0, 'calls': 0}

    def callback(modelo, where):
        if where != GRB.Callback.MIPSOL:
            return
        contador['calls'] += 1
        y_bin = {v: modelo.cbGetSolution(y[v]) for v in V}
        y_bin = {v: (1.0 if val > 0.5 else 0.0) for v, val in y_bin.items()}

        graph, cap, V_all, m_ = _build_flow_net_aggregate(S, T, A_r, y_bin)
        flow = _edmonds_karp(graph, cap, '_s', '_t')
        if flow >= m_ - 1e-6:
            return  # ȳ é viável, nenhum corte necessário

        reachable = _reachable_set(graph, cap, '_s')
        Z = _extract_Z(reachable, V_all, S_set, T_set, m_)
        if not Z:
            raise InstanciaInviavel(
                f'callback E6: corte mínimo de capacidade {flow:.6f} < m={m_} '
                'com Z=∅: instância inviável mesmo com y ≡ 1'
            )
        vs = [v for v in Z if v in y]
        if vs:
            modelo.cbLazy(sum(y[v] for v in vs) >= 1)
            contador['cuts'] += 1

    if use_lazy:
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

    return {
        'obj': obj,
        'bound': bound,
        'gap': gap,
        'status': status,
        'time_s': elapsed,
        'n_lazy_cuts': contador['cuts'],
        'n_lazy_calls': contador['calls'],
    }


def prepare_static_c1(S, T, A_r):
    N_plus, N_minus = build_neighborhoods(A_r)
    return generate_C1(S, T, N_plus, N_minus)
