"""
Regressão T3: cinco mecanismos de corretude nos casos de terminal.

Mecanismos: modelo base, oráculo, separação fracionária, is_valid_cut,
validador independente. Sai com código diferente de zero se algum par
divergir.

--sem-permanencia compara o modelo base com a rede anterior à T1 (sem
arco de permanência). Nesse modo o sucesso é reproduzir a falha no caso
de permanência pura isolada: a suíte teria pego o defeito original.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB

import independent_validator as iv
import synthetic as syn
from baseline import construir_modelo_baseline
from cuts import (
    InstanciaInviavel,
    _edmonds_karp,
    build_neighborhoods,
    integer_oracle,
    is_valid_cut,
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


def corte_viavel(S, T, V, A_r, C):
    """is_valid_cut(Z) afirma que V\\Z é inviável. Z = V\\C testa C."""
    Z = [v for v in V if v not in set(C)]
    return not is_valid_cut(S, T, A_r, Z)


def oraculo_sem_permanencia(S, T, N_plus, C):
    m = len(S)
    if m == 0:
        return True
    S_set, T_set, C_set = set(S), set(T), set(C)
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
    return flow >= m - 1e-6


def casos():
    from ms_utils import construir_arcos_alcance

    itens = [
        syn.make_StayPutIsolado,
        syn.make_SharedTerminal,
        syn.make_StayPut,
        syn.make_TermRelay,
        syn.make_TermRelayForced,
        syn.make_CaminhoABC,
    ]
    saida = []
    for fn in itens:
        S, T, V, adj, A_r, r, meta = fn()
        saida.append((meta['name'], S, T, V, adj, A_r, r))
    saida.append((
        'Pura-2', ['v1', 'v2'], ['v1', 'v2'], ['v1', 'v2'],
        {'v1': [], 'v2': []}, [], 1,
    ))
    V = ['a', 'b']
    adj = syn._adj_undirected([('a', 'b', 1)])
    saida.append((
        'ST-igual-V', ['a', 'b'], ['a', 'b'], V, adj,
        construir_arcos_alcance(V, adj, 1), 1,
    ))
    saida.append(('m0', [], [], ['a'], {'a': []}, [], 1))
    return saida


def comparar(sem_permanencia):
    divergencias = []
    for nome, S, T, V, adj, A_r, r in casos():
        N_plus, _ = build_neighborhoods(A_r)
        n = len(V)
        for mask in range(1 << n):
            C = [V[i] for i in range(n) if mask & (1 << i)]
            if sem_permanencia:
                votos = {
                    'base': base_viavel(S, T, V, A_r, C),
                    'oraculo_antigo': oraculo_sem_permanencia(S, T, N_plus, C),
                }
            else:
                votos = {
                    'base': base_viavel(S, T, V, A_r, C),
                    'oraculo': integer_oracle(S, T, N_plus, C)[0],
                    'separacao': sep_viavel(S, T, V, A_r, C),
                    'is_valid_cut': corte_viavel(S, T, V, A_r, C),
                    'validador': iv.viavel(S, T, V, adj, r, C),
                }
            valores = set(votos.values())
            if len(valores) > 1:
                pares = sorted(votos.items())
                divergencias.append((nome, C, pares))
                print(f'DIVERGÊNCIA {nome} C={C} {votos}')
    return divergencias


def main():
    sem = '--sem-permanencia' in sys.argv
    divs = comparar(sem)
    if sem:
        nomes = {nome for nome, _C, _pares in divs}
        if 'StayPutIsolado' not in nomes:
            print('a rede sem permanência NÃO falhou em StayPutIsolado')
            return 1
        print(f'rede antiga reproduz o defeito em {sorted(nomes)}')
        return 0
    print(f'{len(divs)} divergências')
    return 1 if divs else 0


if __name__ == '__main__':
    sys.exit(main())
