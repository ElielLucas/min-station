"""
Atributos estruturais e métricos de uma instância MIN-STATION (benchmark-v1, §5–6).

Duas famílias de atributos:
  - topológicos, no grafo simples não dirigido subjacente (grau, folhas,
    diâmetro em saltos, largura de árvore estimada, planaridade, simetria);
  - métricos, na métrica da própria instância (pesos e direção do arquivo, como
    `ms_utils.construir_arcos_alcance` usa): λ*, |A_r| e densidade do alcance.

λ* é a distância de gargalo do emparelhamento S–T: o menor λ tal que existe
emparelhamento perfeito usando só pares com d(s,t) ≤ λ. Vale OPT = 0 ⟺ r ≥ λ*:
sem estação nenhum robô recarrega, então cada um precisa de um destino a
distância ≤ r, e com r ≥ λ* o emparelhamento de gargalo resolve.
"""

import sys
from collections import defaultdict, deque
from heapq import heappop, heappush
from pathlib import Path

import networkx as nx
from networkx.algorithms.approximation import treewidth_min_degree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ms_utils import construir_adjacencia, construir_arcos_alcance

LIMITE_DIAMETRO_EXATO = 3000
LIMITE_TREEWIDTH = 5000
LIMITE_ALCANCE = 20000


def _dijkstra(adj, s):
    dist = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        d, u = heappop(pq)
        if d > dist[u]:
            continue
        for w, c in adj.get(u, ()):
            nd = d + c
            if nd < dist.get(w, float('inf')):
                dist[w] = nd
                heappush(pq, (nd, w))
    return dist


def lambda_estrela(S, T, adj):
    """Distância de gargalo do emparelhamento S–T na métrica de `adj` (inf se não houver)."""
    T_set = set(T)
    dist = {s: {t: d for t, d in _dijkstra(adj, s).items() if t in T_set} for s in S}
    valores = sorted({d for ds in dist.values() for d in ds.values()})
    m = len(S)

    def tem_perfeito(lam):
        G = nx.Graph()
        esq = [('s', s) for s in S]
        G.add_nodes_from(esq)
        G.add_nodes_from(('t', t) for t in T)
        G.add_edges_from((('s', s), ('t', t)) for s in S
                         for t, d in dist[s].items() if d <= lam)
        mate = nx.bipartite.hopcroft_karp_matching(G, top_nodes=esq)
        return sum(1 for k in mate if k[0] == 's') == m

    if not valores or not tem_perfeito(valores[-1]):
        return float('inf')
    lo, hi = 0, len(valores) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if tem_perfeito(valores[mid]):
            hi = mid
        else:
            lo = mid + 1
    return valores[lo]


def _classes_refinamento(G, S_set, T_set):
    """Número de classes do refinamento de cores 1-WL com cor inicial (em S, em T)."""
    cor = {v: (v in S_set, v in T_set) for v in G}
    n_classes = len(set(cor.values()))
    while True:
        assin = {v: (cor[v], tuple(sorted(cor[w] for w in G[v]))) for v in G}
        ids = {a: i for i, a in enumerate(sorted(set(assin.values()), key=repr))}
        cor = {v: ids[assin[v]] for v in G}
        novo = len(ids)
        if novo == n_classes:
            return novo
        n_classes = novo


def _diametro(G):
    if G.number_of_nodes() <= LIMITE_DIAMETRO_EXATO:
        return nx.diameter(G), True
    # varredura dupla: limite inferior
    v0 = next(iter(G))
    d1 = nx.single_source_shortest_path_length(G, v0)
    u = max(d1, key=d1.get)
    d2 = nx.single_source_shortest_path_length(G, u)
    return max(d2.values()), False


def calcular_atributos(dados, r=None):
    """
    dados: dict de `ms_utils.ler_instancia` (S, T, V, E, R). r sobrescreve o R do arquivo.
    Retorna dict de atributos (valores None quando o cálculo foi pulado por tamanho).
    """
    S, T, V, E = dados['S'], dados['T'], dados['V'], dados['E']
    r = float(dados['R'] if r is None else r)
    S_set, T_set = set(S), set(T)

    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from((u, v) for u, v, _ in E if u != v)
    n = G.number_of_nodes()
    graus = [d for _, d in G.degree()]
    folhas = {v for v in G if G.degree(v) <= 1}
    arcos = {(u, v) for u, v, _ in E}
    pesos = {w for *_, w in E}

    at = {
        'n': n,
        'arestas_nao_dirigidas': G.number_of_edges(),
        'arcos_arquivo': len(E),
        'arcos_sem_reverso': sum(1 for u, v in arcos if (v, u) not in arcos),
        'pesos_distintos': len(pesos),
        'peso_min': min(pesos) if pesos else None,
        'peso_max': max(pesos) if pesos else None,
        'conexo': nx.is_connected(G) if n else False,
        'grau_medio': round(sum(graus) / n, 3) if n else 0,
        'grau_max': max(graus) if graus else 0,
        'frac_folhas': round(len(folhas) / n, 4) if n else 0,
        'm': len(S),
        'r': r,
        'frac_terminais': round(len(S_set | T_set) / n, 4) if n else 0,
        'frac_terminais_folha': round(len((S_set | T_set) & folhas) / max(1, len(S_set | T_set)), 4),
        'rho_S_inter_T': round(len(S_set & T_set) / max(1, len(S)), 4),
        'planar': nx.check_planarity(G)[0],
        'classes_wl': _classes_refinamento(G, S_set, T_set),
    }
    at['frac_classes_wl'] = round(at['classes_wl'] / n, 4) if n else 0

    if at['conexo']:
        at['diametro_saltos'], at['diametro_exato'] = _diametro(G)
    else:
        at['diametro_saltos'], at['diametro_exato'] = None, None

    at['treewidth_ub'] = (treewidth_min_degree(G)[0]
                          if n <= LIMITE_TREEWIDTH else None)

    adj = construir_adjacencia(E)
    lam = lambda_estrela(S, T, adj)
    at['lambda_estrela'] = lam
    at['demanda_saltos'] = round(lam / r, 3) if r > 0 and lam != float('inf') else None
    at['opt_zero'] = (r >= lam)

    if n <= LIMITE_ALCANCE:
        n_ar = len(construir_arcos_alcance(V, adj, r))
        at['n_arcos_alcance'] = n_ar
        at['densidade_alcance'] = round(n_ar / (n * (n - 1)), 5) if n > 1 else 0
    else:
        at['n_arcos_alcance'] = None
        at['densidade_alcance'] = None

    at['classe_tamanho'] = classe_tamanho(at['n_arcos_alcance'])
    at['regime'] = regime(at)
    return at


def classe_tamanho(n_arcos_alcance):
    """P: |A_r| ≤ 2·10⁴; M: ≤ 2·10⁵; G: acima (benchmark-v1 §6)."""
    if n_arcos_alcance is None:
        return 'G?'
    if n_arcos_alcance <= 20_000:
        return 'P'
    if n_arcos_alcance <= 200_000:
        return 'M'
    return 'G'


def regime(at):
    """
    Regimes dos relatórios E1–E8, a partir dos atributos:
      R-c: alcance denso (|A_r| ≥ 15% dos pares; com 5% Chicago R7 caía em R-c,
           contra a leitura dos relatórios, que a tratam como longo curso);
      R-b: terminais densos (≥ 15% dos vértices);
      R-a: terminais esparsos e demanda de saltos ≥ 3;
      misto: o restante.
    """
    dens = at.get('densidade_alcance')
    if dens is not None and dens >= 0.15:
        return 'R-c'
    if at['frac_terminais'] >= 0.15:
        return 'R-b'
    if at.get('demanda_saltos') is not None and at['demanda_saltos'] >= 3:
        return 'R-a'
    return 'misto'
