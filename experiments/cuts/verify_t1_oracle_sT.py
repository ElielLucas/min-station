"""
Regressão T1: permanência em S∩T no oráculo e na separação fracionária.

Compara integer_oracle e separate_classical_fracs com
construir_modelo_baseline (Gurobi, y fixado por C) em todo C ⊆ V nos seis
gabaritos de synthetic.py e em dois casos de permanência pura isolada.

Também confere:
- o arco v_out→v_in de capacidade 1 existe só para v ∈ S∩T;
- onde a viabilidade não muda em relação à rede sem permanência, o corte Z
  também não muda.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB

import synthetic as syn
from baseline import construir_modelo_baseline
from cuts import (
    InstanciaInviavel,
    _build_flow_net_aggregate,
    _edmonds_karp,
    _extract_Z,
    _reachable_set,
    build_neighborhoods,
    integer_oracle,
    separate_classical_fracs,
)


def base_viavel(S, T, V, A_r, C):
    modelo, y, _f, _na, _nv = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.Params.Threads = 1
    Cset = set(C)
    for v in V:
        val = 1.0 if v in Cset else 0.0
        y[v].lb = val
        y[v].ub = val
    modelo.optimize()
    ok = modelo.Status == GRB.OPTIMAL
    modelo.dispose()
    return ok


def sep_viavel(S, T, V, A_r, C):
    y = {v: (1.0 if v in set(C) else 0.0) for v in V}
    try:
        cortes = separate_classical_fracs(S, T, A_r, y)
    except InstanciaInviavel:
        return False
    return len(cortes) == 0


def permanencia_pura(vertices):
    """S=T=vértices isolados. OPT=0 por permanência, sem aresta."""
    V = list(vertices)
    return V, V, V, {}, [], 1, {'name': f'Pura-{len(V)}'}


def oraculo_sem_permanencia(S, T, N_plus, C):
    """Rede anterior à T1: sem arco v_out→v_in. Referência só para o Z."""
    m = len(S)
    S_set, T_set = set(S), set(T)
    C_set = set(C)
    nodes = S_set | T_set | C_set
    INF = 1e9
    graph, cap = {}, {}

    def arc(u, v, c):
        graph.setdefault(u, {})[v] = None
        graph.setdefault(v, {})[u] = None
        cap[(u, v)] = cap.get((u, v), 0.0) + c
        cap.setdefault((v, u), 0.0)

    for v in nodes:
        is_S, is_T = v in S_set, v in T_set
        if is_S:
            arc('_s', f'{v}_out', 1.0)
        if is_T:
            arc(f'{v}_in', '_t', 1.0)
        cap_relay = float(m - 1 if (is_S or is_T) else m) if v in C_set else 0.0
        arc(f'{v}_in', f'{v}_out', cap_relay)
    for u in nodes:
        for w in N_plus.get(u, ()):
            if w in nodes:
                arc(f'{u}_out', f'{w}_in', INF)
    flow = _edmonds_karp(graph, cap, '_s', '_t')
    if flow >= m - 1e-6:
        return True, None
    X = _reachable_set(graph, cap, '_s')
    Z = _extract_Z(X, nodes, S_set, T_set, m)
    for u in nodes:
        if f'{u}_out' not in X:
            continue
        for w in N_plus.get(u, ()):
            if w not in nodes:
                Z.add(w)
    return False, frozenset(Z)


def checar_arcos(S, T, V, A_r):
    """Capacidade v_out→v_in é 1 sse v ∈ S∩T; nenhum arco novo fora disso."""
    y = {v: 0.0 for v in V}
    _g, cap, _V, _m = _build_flow_net_aggregate(S, T, A_r, y)
    inter = set(S) & set(T)
    erros = 0
    for v in V:
        c_stay = cap.get((f'{v}_out', f'{v}_in'), 0.0)
        if v in inter:
            if abs(c_stay - 1.0) > 1e-9:
                erros += 1
                print(f'  arco de permanência ausente em {v}: cap={c_stay}')
        elif c_stay > 1e-9:
            erros += 1
            print(f'  arco indevido v_out→v_in em {v} ∉ S∩T: cap={c_stay}')
    return erros


def enumerar(label, S, T, V, A_r):
    N_plus, _N_minus = build_neighborhoods(A_r)
    div = z_div = 0
    n = 0
    for mascara in range(1 << len(V)):
        C = [V[i] for i in range(len(V)) if mascara & (1 << i)]
        n += 1
        base = base_viavel(S, T, V, A_r, C)
        ora, Z = integer_oracle(S, T, N_plus, C)
        sep = sep_viavel(S, T, V, A_r, C)
        if ora != base or sep != base:
            div += 1
            print(f'  DIVERGÊNCIA {label}: C={C} base={base} oráculo={ora} sep={sep}')
        antigo, Z_ant = oraculo_sem_permanencia(S, T, N_plus, C)
        if antigo == ora and not ora and Z != Z_ant:
            z_div += 1
            print(f'  Z mudou sem mudar viabilidade {label}: C={C} Z={sorted(Z)} antigo={sorted(Z_ant)}')
    return n, div, z_div


def casos():
    saida = []
    for fn in (
        syn.make_Direct0,
        syn.make_TermRelay,
        syn.make_Tri,
        syn.make_StayPut,
        syn.make_SharedTerminal,
        syn.make_TermRelayForced,
    ):
        S, T, V, _adj, A_r, _r, meta = fn()
        saida.append((meta['name'], S, T, V, A_r))
    for nome, verts in (('Pura-1', ['v']), ('Pura-2', ['v1', 'v2'])):
        S, T, V, _adj, A_r, _r, _meta = permanencia_pura(verts)
        saida.append((nome, S, T, V, A_r))
    return saida


def main():
    total_n = total_div = total_z = total_arco = 0
    print(f'{"caso":<18} {"n":>5} {"div":>5} {"Z":>5} {"arcos":>6}')
    for label, S, T, V, A_r in casos():
        n, div, z_div = enumerar(label, S, T, V, A_r)
        arcos = checar_arcos(S, T, V, A_r)
        total_n += n
        total_div += div
        total_z += z_div
        total_arco += arcos
        print(f'{label:<18} {n:>5} {div:>5} {z_div:>5} {arcos:>6}')

    # Permanência pura isolada: viável com C=∅ e com y=1, sem InstanciaInviavel.
    S, T, V, _a, A_r, _r, _m = permanencia_pura(['v'])
    N_plus, _ = build_neighborhoods(A_r)
    ok_vazio, _Z = integer_oracle(S, T, N_plus, [])
    if not ok_vazio:
        total_div += 1
        print('FALHA: permanência pura com C=∅ ficou inviável')
    for yv in (0.0, 1.0):
        try:
            separate_classical_fracs(S, T, A_r, {'v': yv})
        except InstanciaInviavel as exc:
            total_div += 1
            print(f'FALHA: separate_classical_fracs y={yv} levantou {exc}')

    print(f'total {total_n} casos, {total_div} divergências, {total_z} Z alterados, {total_arco} arcos errados')
    return total_div + total_z + total_arco


if __name__ == '__main__':
    sys.exit(main())
