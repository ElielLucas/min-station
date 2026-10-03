"""
Regressão T2: validador (vértice, bateria) + emparelhamento contra o modelo
base no Gurobi e contra o oráculo corrigido.

Protocolo de validacao-formulacao-base.md ("Verificação recomendada"):
grafos conexos rotulados, n ≤ 5, r ∈ {1,2,3}, m ≤ 3, inclusive S∩T ≠ ∅,
mesma viabilidade para cada C. n ≤ 4 roda exaustivo contra o Gurobi.
n = 5 compara validador e oráculo em todo C, e o Gurobi numa amostra
documentada: a enumeração rotulada completa contra o solver não cabe no
tempo de uma regressão (ver a saída desta suíte).
"""
import argparse
import random
import sys
import time
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB

import independent_validator as iv
import synthetic as syn
from baseline import construir_modelo_baseline
from cuts import build_neighborhoods, integer_oracle
from ms_utils import construir_arcos_alcance


def base_modelo(S, T, V, A_r):
    modelo, y, _f, _na, _nv = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.Params.Threads = 1
    return modelo, y


def base_viavel(modelo, y, V, C):
    Cset = set(C)
    for v in V:
        val = 1.0 if v in Cset else 0.0
        y[v].lb = val
        y[v].ub = val
    modelo.optimize()
    return modelo.Status == GRB.OPTIMAL


def base_opt(modelo, y, V):
    for v in V:
        y[v].lb = 0.0
        y[v].ub = 1.0
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        return None
    return int(round(modelo.ObjVal))


def conexos(n):
    verts = [str(i) for i in range(n)]
    pares = [(verts[i], verts[j]) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1 << len(pares)):
        edges = [pares[k] for k in range(len(pares)) if mask & (1 << k)]
        visto = set()
        if verts:
            fila = [verts[0]]
            visto.add(verts[0])
            adj = {v: [] for v in verts}
            for u, w in edges:
                adj[u].append(w)
                adj[w].append(u)
            i = 0
            while i < len(fila):
                u = fila[i]
                i += 1
                for w in adj[u]:
                    if w not in visto:
                        visto.add(w)
                        fila.append(w)
        if len(visto) == n:
            yield verts, [(u, w, 1) for u, w in edges]


def adj_de(V, edges):
    adj = {v: [] for v in V}
    for u, w, peso in edges:
        adj[u].append((w, peso))
        adj[w].append((u, peso))
    return adj


def sem_rede_de_fluxo():
    import ast
    arvore = ast.parse(Path(iv.__file__).read_text(encoding='utf-8'))
    proibidos = {'integer_oracle', '_build_flow_net_aggregate', '_edmonds_karp', 'cuts'}
    achados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                if alias.name.split('.')[0] in proibidos:
                    achados.add(alias.name)
        elif isinstance(no, ast.ImportFrom) and no.module and no.module.split('.')[0] in proibidos:
            achados.add(no.module)
        elif isinstance(no, ast.Name) and no.id in proibidos:
            achados.add(no.id)
        elif isinstance(no, ast.Attribute) and no.attr in proibidos:
            achados.add(no.attr)
    return sorted(achados)


def checar_bateria():
    """r=1 no caminho a-b-c: sem estação a não alcança c; com estação em b, alcança."""
    V = ['a', 'b', 'c']
    adj = adj_de(V, [('a', 'b', 1), ('b', 'c', 1)])
    g = iv._grafo_unitario(V, adj)
    sem = iv.destinos_alcancaveis('a', ['c'], [], g, 1)
    com = iv.destinos_alcancaveis('a', ['c'], ['b'], g, 1)
    erros = 0
    if 'c' in sem:
        erros += 1
        print('  bateria: a alcançou c com r=1 e C=∅')
    if 'c' not in com:
        erros += 1
        print('  bateria: a não alcançou c com estação em b')
    return erros


def checar_opt_gabaritos():
    erros = 0
    S, T, V, adj, _A, r, meta = syn.make_SharedTerminal()
    opt = iv.opt_por_enumeracao(S, T, V, adj, r)
    if opt != 1:
        erros += 1
        print(f'  SharedTerminal OPT={opt}, esperado 1')
    pura_adj = {}
    opt0 = iv.opt_por_enumeracao(['v'], ['v'], ['v'], pura_adj, 1)
    if opt0 != 0:
        erros += 1
        print(f'  permanência pura OPT={opt0}, esperado 0')
    if 'v' not in iv.destinos_alcancaveis('v', ['v'], [], {'v': []}, 1):
        erros += 1
        print('  origem em S∩T não é alcançável de si com C=∅')
    return erros


def todos_C(V):
    n = len(V)
    for mask in range(1 << n):
        yield [V[i] for i in range(n) if mask & (1 << i)]


def comparar_instancia(S, T, V, adj, r, A_r, N_plus, modelo, y, contra_gurobi):
    div = 0
    nC = 0
    for C in todos_C(V):
        nC += 1
        meu = iv.viavel(S, T, V, adj, r, C)
        ora = integer_oracle(S, T, N_plus, C)[0]
        if meu != ora:
            div += 1
        if contra_gurobi:
            base = base_viavel(modelo, y, V, C)
            if meu != base:
                div += 1
    if contra_gurobi:
        opt_v = iv.opt_por_enumeracao(S, T, V, adj, r)
        opt_b = base_opt(modelo, y, V)
        if opt_v != opt_b:
            div += 1
    return nC, div


def varrer(max_n, semente, amostra_n5):
    div = 0
    n_inst = 0
    n_com_inter = 0
    nC = 0
    t0 = time.monotonic()
    for n in range(1, max_n + 1):
        for V, edges in conexos(n):
            adj = adj_de(V, edges)
            for r in (1, 2, 3):
                A_r = construir_arcos_alcance(V, adj, r)
                N_plus, _ = build_neighborhoods(A_r)
                for m in range(1, min(3, n) + 1):
                    for S in combinations(V, m):
                        for T in combinations(V, m):
                            S, T = list(S), list(T)
                            n_inst += 1
                            if set(S) & set(T):
                                n_com_inter += 1
                            modelo, y = base_modelo(S, T, V, A_r)
                            c, d = comparar_instancia(
                                S, T, V, adj, r, A_r, N_plus, modelo, y, True,
                            )
                            modelo.dispose()
                            nC += c
                            div += d
    t_ex = time.monotonic() - t0

    rng = random.Random(semente)
    grafos = list(conexos(5))
    rng.shuffle(grafos)
    n5_inst = n5_div = n5_C = 0
    t1 = time.monotonic()
    for V, edges in grafos:
        if n5_inst >= amostra_n5:
            break
        adj = adj_de(V, edges)
        for r in (1, 2, 3):
            if n5_inst >= amostra_n5:
                break
            A_r = construir_arcos_alcance(V, adj, r)
            N_plus, _ = build_neighborhoods(A_r)
            pares = []
            for m in range(1, 4):
                for S in combinations(V, m):
                    for T in combinations(V, m):
                        pares.append((list(S), list(T)))
            rng.shuffle(pares)
            for S, T in pares:
                if n5_inst >= amostra_n5:
                    break
                n5_inst += 1
                if set(S) & set(T):
                    n_com_inter += 1
                modelo, y = base_modelo(S, T, V, A_r)
                c, d = comparar_instancia(
                    S, T, V, adj, r, A_r, N_plus, modelo, y, True,
                )
                modelo.dispose()
                n5_C += c
                n5_div += d
    t_n5 = time.monotonic() - t1
    return {
        'div': div + n5_div,
        'n_inst': n_inst,
        'n_com_inter': n_com_inter,
        'nC': nC,
        't_ex': t_ex,
        'n5_inst': n5_inst,
        'n5_C': n5_C,
        't_n5': t_n5,
        'grafos_n5': len(grafos),
    }


def gabaritos_contra_oraculo():
    div = 0
    n = 0
    casos = [
        syn.make_Direct0,
        syn.make_TermRelay,
        syn.make_Tri,
        syn.make_StayPut,
        syn.make_SharedTerminal,
        syn.make_TermRelayForced,
    ]
    for fn in casos:
        S, T, V, adj, A_r, r, meta = fn()
        N_plus, _ = build_neighborhoods(A_r)
        modelo, y = base_modelo(S, T, V, A_r)
        c, d = comparar_instancia(S, T, V, adj, r, A_r, N_plus, modelo, y, True)
        modelo.dispose()
        n += c
        div += d
        if d:
            print(f'  divergência no gabarito {meta["name"]}')
    for verts in (['v'], ['v1', 'v2']):
        S = T = V = list(verts)
        adj = {v: [] for v in V}
        A_r = []
        N_plus, _ = build_neighborhoods(A_r)
        modelo, y = base_modelo(S, T, V, A_r)
        c, d = comparar_instancia(S, T, V, adj, 1, A_r, N_plus, modelo, y, True)
        modelo.dispose()
        n += c
        div += d
    return n, div


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=4)
    parser.add_argument('--amostra-n5', type=int, default=60)
    parser.add_argument('--semente', type=int, default=42)
    args = parser.parse_args()

    proibidos = sem_rede_de_fluxo()
    if proibidos:
        print(f'validador referencia a rede de fluxo: {proibidos}')
        return 1
    erros = checar_bateria() + checar_opt_gabaritos()
    n_gab, div_gab = gabaritos_contra_oraculo()
    erros += div_gab
    print(f'gabaritos: {n_gab} conjuntos C, {div_gab} divergências')
    stats = varrer(args.max_n, args.semente, args.amostra_n5)
    erros += stats['div']
    if stats['n_com_inter'] == 0:
        erros += 1
        print('nenhuma instância com S∩T ≠ ∅')
    print(
        f"exaustivo n≤{args.max_n}: {stats['n_inst']} instâncias, "
        f"{stats['nC']} conjuntos C, {stats['t_ex']:.1f}s"
    )
    print(
        f"amostra n=5: {stats['n5_inst']} de um universo de "
        f"{stats['grafos_n5']} grafos conexos rotulados, "
        f"{stats['n5_C']} conjuntos C, {stats['t_n5']:.1f}s"
    )
    print(f"instâncias com S∩T ≠ ∅ (contagem acumulada): {stats['n_com_inter']}")
    print(f'divergências: {erros}')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
