"""
Limite combinatório R6 (direcoes-pli-min-station.md §10, item R6): L_bot.

L_bot := min_π max_s h*(s, π(s)), sobre bijeções π: S → T, onde h*(s,t) é o
número mínimo de vértices interiores de um caminho s→t em A_r (distância em
saltos em A_r, menos 1). Limite inferior provado (§2.2c): toda solução com
alguma bijeção π contém o interior da rota de cada robô, logo
|C| ≥ max_s h*(s, π(s)) para a bijeção realizada, e L_bot é o melhor caso
sobre todas as bijeções.

Calculado pela mesma técnica de instance_features.lambda_estrela (busca
binária sobre distâncias + emparelhamento bipartido máximo), mas com
distância em saltos dirigidos em A_r, não a métrica original do grafo.

Os demais itens de R6 do plano (bandas ⌈D_s/r⌉−1 sobre uma atribuição fixa,
empacotamento de cortes C1/C2 disjuntos, ⌈LP(C1)⌉) não entram aqui: exigem
decidir qual atribuição usar nas bandas e qual critério de empacotamento,
não especificados sem ambiguidade no plano — ficam para quando isso for
decidido, em vez de arriscar uma fórmula não verificada.
"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cuts'))

import networkx as nx


def _bfs_hops(src, N_plus):
    dist = {src: 0}
    fila = deque([src])
    while fila:
        u = fila.popleft()
        for w in N_plus.get(u, ()):
            if w not in dist:
                dist[w] = dist[u] + 1
                fila.append(w)
    return dist


def l_bot(S, T, N_plus):
    """L_bot := min_pi max_s h*(s, pi(s)), h*(s,t) = dist_saltos(s,t) - 1 em A_r."""
    T_set = set(T)
    hstar = {}
    for s in S:
        dist = _bfs_hops(s, N_plus)
        hstar[s] = {t: dist[t] - 1 for t in T_set if t in dist}

    valores = sorted({d for ds in hstar.values() for d in ds.values()})
    m = len(S)

    def tem_perfeito(lam):
        G = nx.Graph()
        esq = [('s', s) for s in S]
        G.add_nodes_from(esq)
        G.add_nodes_from(('t', t) for t in T)
        G.add_edges_from((('s', s), ('t', t)) for s in S
                         for t, d in hstar[s].items() if d <= lam)
        mate = nx.bipartite.hopcroft_karp_matching(G, top_nodes=esq)
        return sum(1 for k in mate if k[0] == 's') == m

    if not valores or not tem_perfeito(valores[-1]):
        return None  # sem bijeção viável nem com todo A_r — instância inviável
    lo, hi = 0, len(valores) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if tem_perfeito(valores[mid]):
            hi = mid
        else:
            lo = mid + 1
    return valores[lo]
