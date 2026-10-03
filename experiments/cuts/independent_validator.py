"""
Validador de viabilidade independente da rede de fluxo agregada.

Decide se um conjunto de estações C é viável para o MIN-STATION de Das
(arestas de peso 1) explorando estados (vértice, bateria) no grafo original
e um emparelhamento bipartido entre origens e destinos alcançáveis.

Não usa A_r, integer_oracle, a rede agregada nem o Edmonds-Karp de cuts.py.
"""
import sys
from collections import deque
from itertools import combinations


def _grafo_unitario(V, adj):
    """Lista de vizinhos por vértice. Recusa peso diferente de 1."""
    g = {v: [] for v in V}
    for u, lista in adj.items():
        if u not in g:
            g[u] = []
        for v, w in lista:
            if w != 1:
                raise ValueError(
                    f'aresta {u}-{v} tem peso {w}; este validador cobre só autonomia em passos'
                )
            g.setdefault(v, [])
            g[u].append(v)
    return g


def _componentes(V, g):
    visto = set()
    comps = []
    for origem in V:
        if origem in visto:
            continue
        fila = deque([origem])
        visto.add(origem)
        comp = []
        while fila:
            u = fila.popleft()
            comp.append(u)
            for w in g.get(u, ()):
                if w not in visto:
                    visto.add(w)
                    fila.append(w)
        comps.append(comp)
    return comps


def avisar_se_desconexo(V, adj, S, T):
    """
    Das pressupõe G conexo. Componentes que são um único vértice em S∩T
    são permanência pura e não disparam aviso: o caso é exigido pela
    regressão de permanência. Qualquer outro desconexidade avisa em stderr.
    """
    g = _grafo_unitario(V, adj)
    comps = _componentes(list(V), g)
    if len(comps) <= 1:
        return
    inter = set(S) & set(T)
    for comp in comps:
        if len(comp) == 1 and comp[0] in inter:
            continue
        print(
            'aviso: grafo desconexo; Das pressupõe G conexo',
            file=sys.stderr,
        )
        return


def destinos_alcancaveis(origem, T, C, g, r):
    """
    Destinos alcançáveis a partir de origem.

    Estado (v, b): bateria restante em v, antes de gastar arestas de saída.
    Cada aresta consome 1. Entrar em vértice de C repõe a bateria em r.
    Se origem ∈ T, ela é alcançável com custo zero, com ou sem estação.
    """
    Tset = set(T)
    Cset = set(C)
    alcance = set()
    if origem in Tset:
        alcance.add(origem)
    if r < 0:
        return alcance
    vistos = {(origem, r)}
    fila = deque([(origem, r)])
    while fila:
        v, b = fila.popleft()
        if v in Tset:
            alcance.add(v)
        if b < 1:
            continue
        for w in g.get(v, ()):
            nb = r if w in Cset else b - 1
            estado = (w, nb)
            if estado in vistos:
                continue
            vistos.add(estado)
            fila.append(estado)
    return alcance


def _emparelhamento(origens, alcance):
    """Emparelhamento máximo bipartido. Cobre as origens sse devolve len(origens)."""
    par_destino = {}

    def augmentar(s, visto):
        for t in alcance[s]:
            if t in visto:
                continue
            visto.add(t)
            if t not in par_destino or augmentar(par_destino[t], visto):
                par_destino[t] = s
                return True
        return False

    casados = 0
    for s in origens:
        if augmentar(s, set()):
            casados += 1
    return casados


def viavel(S, T, V, adj, r, C):
    """True sse existe um robô por origem, cada um numa rota até um destino distinto."""
    if len(S) != len(T):
        raise ValueError(f'|S|={len(S)} diferente de |T|={len(T)}')
    if len(S) == 0:
        return True
    g = _grafo_unitario(V, adj)
    alcance = {
        s: destinos_alcancaveis(s, T, C, g, r)
        for s in S
    }
    return _emparelhamento(list(S), alcance) == len(S)


def opt_por_enumeracao(S, T, V, adj, r):
    """Menor |C| viável, enumerando os subconjuntos de V. None se nenhum for viável."""
    vertices = list(V)
    for k in range(len(vertices) + 1):
        for C in combinations(vertices, k):
            if viavel(S, T, vertices, adj, r, C):
                return k
    return None
