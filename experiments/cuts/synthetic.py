"""
Construtores de instâncias sintéticas para validação de cortes (E1').

Cada função retorna (S, T, V, adj, A_r, r, meta) onde:
  - S, T, V: listas de nomes de vértices
  - adj: dict {u: [(v, weight)]} para Dijkstra e C2
  - A_r: lista de arcos (u, v) com d(u,v) <= r
  - r: autonomia
  - meta: dict com valores teóricos (OPT, z_LP, LP_cov)

Instâncias confirmadas pelo documento direcoes-pli-min-station.md.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ms_utils import construir_arcos_alcance


def _adj_undirected(edges):
    """Constrói adj bidirecional a partir de arestas (u, v, w)."""
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return dict(adj)


# ── F1: grafo de raios (gap de autonomia) ────────────────────────────────────

def make_F1(m=2, k=2, r=1):
    """
    m robôs, k vértices de relay por raio, autonomia r=1.
    Hub central h; raios de origem e destino dedicados.

    Valores esperados:
      OPT    = 2*m*k + 1
      z_LP   = 2*k + 1
      LP_cov = OPT
    """
    edges = []
    V     = ['h']
    S     = []
    T     = []

    for i in range(1, m + 1):
        s_i = f's{i}'
        t_i = f't{i}'
        S.append(s_i)
        T.append(t_i)
        V.append(s_i)
        V.append(t_i)

        # Raio de origem: s_i — p_i1 — ... — p_ik — h
        prev = s_i
        for j in range(1, k + 1):
            p = f'p{i}{j}'
            V.append(p)
            edges.append((prev, p, 1))
            prev = p
        edges.append((prev, 'h', 1))

        # Raio de destino: h — q_i1 — ... — q_ik — t_i
        prev = 'h'
        for j in range(1, k + 1):
            q = f'q{i}{j}'
            V.append(q)
            edges.append((prev, q, 1))
            prev = q
        edges.append((prev, t_i, 1))

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name':   f'F1(m={m},k={k})',
        'OPT':    2 * m * k + 1,
        'z_LP':   float(2 * k + 1),
        'LP_cov': float(2 * m * k + 1),
    }


# ── F2: bolsões de Hall ──────────────────────────────────────────────────────

def make_F2(k=1, L=3, r=1):
    """
    k bolsões de Hall, m = 3k robôs, autonomia r=1.
    Bolsões ligados por caminhos de L vértices não terminais.

    Estrutura de cada bolsão j (1-indexed):
      origens a_j, b_j, e_j; relé x_j; destinos c_j, d_j, g_j
      arestas: a_j–c_j, b_j–c_j, a_j–x_j, b_j–x_j, x_j–d_j, d_j–e_j, e_j–g_j

    Entre bolsão j e j+1: caminho de L nós intermediários z_{j,1}...z_{j,L}.

    Valores esperados:
      OPT    = k
      z_LP   = 1/3   (k cancela)
      LP_cov = k
    """
    edges  = []
    V      = []
    S      = []
    T      = []

    for j in range(1, k + 1):
        a, b, e_v = f'a{j}', f'b{j}', f'e{j}'
        x          = f'x{j}'
        c, d, g   = f'c{j}', f'd{j}', f'g{j}'

        S += [a, b, e_v]
        T += [c, d, g]
        V += [a, b, e_v, x, c, d, g]

        edges += [
            (a,   c,   1),
            (b,   c,   1),
            (a,   x,   1),
            (b,   x,   1),
            (x,   d,   1),
            (d,   e_v, 1),
            (e_v, g,   1),
        ]

        # Ligação com bolsão anterior via caminho intermediário
        if j > 1:
            prev_g = f'g{j-1}'
            chain  = [f'z{j-1}_{l}' for l in range(1, L + 1)]
            V     += chain
            path   = [prev_g] + chain + [g]
            for u, v in zip(path, path[1:]):
                edges.append((u, v, 1))

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name':   f'F2(k={k},L={L})',
        'OPT':    float(k),
        'z_LP':   1.0 / 3.0,
        'LP_cov': float(k),
    }


# ── Tri: instância triangular (gap de Hall puro) ─────────────────────────────

def make_Tri(r=1):
    """
    m=3 robôs, 3 relés, autonomia r=1.
    Cada par (s_i, t_i) é vizinho de dois relés que se sobrepõem ciclicamente.

    Arestas: s1–a, s1–b, t1–a, t1–b,
             s2–b, s2–c, t2–b, t2–c,
             s3–c, s3–a, t3–c, t3–a.

    Valores esperados:
      OPT    = 2
      z_LP   = 1
      LP_cov = 1.5
    """
    S     = ['s1', 's2', 's3']
    T     = ['t1', 't2', 't3']
    relés = ['a',  'b',  'c']
    V     = S + T + relés

    edges = [
        ('s1', 'a', 1), ('s1', 'b', 1),
        ('t1', 'a', 1), ('t1', 'b', 1),
        ('s2', 'b', 1), ('s2', 'c', 1),
        ('t2', 'b', 1), ('t2', 'c', 1),
        ('s3', 'c', 1), ('s3', 'a', 1),
        ('t3', 'c', 1), ('t3', 'a', 1),
    ]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name':   'Tri',
        'OPT':    2.0,
        'z_LP':   1.0,
        'LP_cov': 1.5,
    }


# ── §5.9: contraexemplo BC-y sem cortes fracionários clássicos ───────────────

def make_Sec59(L=7, r=1):
    """
    m=3 robôs, caminho longo de L nós, autonomia r=1.

    Arestas: s1–t1, s2–t1, s1–w1, s2–w1,
             w1–w2–...–wL,
             wL–t2, t2–s3, s3–t3.

    Para L=7: OPT=7, z_LP=7/3, BC-y (sem cortes fracionários clássicos) dá raiz=2.

    Valores esperados:
      OPT    = L
      z_LP   = L / 3
      root_sem_corte_classico = 2   (para L >= 7)
    """
    S = ['s1', 's2', 's3']
    T = ['t1', 't2', 't3']

    path = [f'w{i}' for i in range(1, L + 1)]
    V    = S + T + path

    edges = [
        ('s1', 't1', 1),
        ('s2', 't1', 1),
        ('s1', 'w1', 1),
        ('s2', 'w1', 1),
    ]
    for i in range(len(path) - 1):
        edges.append((path[i], path[i + 1], 1))
    edges += [
        (path[-1], 't2', 1),
        ('t2',     's3', 1),
        ('s3',     't3', 1),
    ]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name':         f'Sec59(L={L})',
        'OPT':          float(L),
        'z_LP':         L / 3.0,
        'root_bc_sem_frac': 2.0,   # valor teórico para L >= 7
    }


# ── Gabaritos de regressão E5 — validade de cortes ────────────────────────────

def make_Direct0(r=1):
    """
    S={s1,s2}, T={t1,t2}, arestas s1-t1, s2-t2, autonomia r=1.

    Cada robô tem aresta direta até seu próprio alvo: OPT=0, sem estação
    alguma. É a instância Chicago-st15-R26 (OPT=0 provado) em miniatura,
    usada como teste de regressão do defeito 1 (arco terminal errado na
    rede agregada): nenhuma família de cortes pode gerar y(Z)>=1 aqui, pois
    qualquer corte seria violado pela solução ótima y=0.
    """
    S = ['s1', 's2']
    T = ['t1', 't2']
    V = S + T
    edges = [('s1', 't1', 1), ('s2', 't2', 1)]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name':   'Direct0',
        'OPT':    0.0,
        'z_LP':   0.0,
        'LP_cov': 0.0,
    }


def make_TermRelay(r=1):
    """
    S={s1,s2}, T={t1,t2}, arestas s1-t1, s2-t1, t1-t2, autonomia r=1.

    Robô 1 chega direto em t1 (uso terminal, grátis). Robô 2 só alcança t2
    passando por t1 (uso de relé, cobrado). OPT=1, única solução y_t1=1.
    Regressão do defeito 1 (o arco terminal errado impede a chegada
    grátis) e do defeito 2 (Z sem excluir terminais: t1 só entra no corte
    quando precisa servir de relé, não quando só recebe sua própria
    unidade).
    """
    S = ['s1', 's2']
    T = ['t1', 't2']
    V = S + T
    edges = [('s1', 't1', 1), ('s2', 't1', 1), ('t1', 't2', 1)]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name': 'TermRelay',
        'OPT':  1.0,
    }


# ── Gabaritos de regressão E5 — variante U (S ∩ T ≠ ∅) ────────────────────────

def make_StayPut(r=1):
    """
    S = T = {a, b}, aresta a-b, autonomia r=1.

    Todos os robôs já estão em seus alvos (caso S=T de
    validacao-formulacao-base.md §A.9): cada um fica parado, sem exigir
    estação nem caminho algum. OPT=0.

    Com a formulação separada antiga (balanços de origem e destino
    independentes), este modelo seria declarado INVIÁVEL para todo
    v ∈ S∩T=S=T (soma dos dois balanços dá 0=2). Com a variante U, é
    viável e resolve em OPT=0. A asserção principal deste gabarito é a
    viabilidade, não o valor de OPT.
    """
    S = ['a', 'b']
    T = ['a', 'b']
    V = ['a', 'b']
    edges = [('a', 'b', 1)]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name': 'StayPut',
        'OPT':  0.0,
    }


def make_SharedTerminal(r=1):
    """
    Estrela K_{1,4}: centro v, folhas p1..p4. S={v,p1,p2}, T={v,p3,p4},
    autonomia r=1 (caso de validacao-formulacao-base.md §A.9).

    O robô que parte de v também é alvo de outro (v ∈ S∩T): fica parado em
    v sem custo. Isso libera o trânsito por v para UM robô relé de graça
    (p_i -> v -> p_j). Mas há dois robôs (de p1 e p2) que precisam alcançar
    {p3,p4}, cada um via 2 saltos por v — só um passa de graça; o segundo
    exige estação. OPT=1, única solução y_v=1.

    Testa o tratamento de S∩T na rede agregada (_build_flow_net_aggregate):
    v recebe os dois arcos de unidade própria (σ→v_out e v_in→τ) e ainda
    assim precisa de trânsito pago para o segundo robô relé.
    """
    S = ['v', 'p1', 'p2']
    T = ['v', 'p3', 'p4']
    V = ['v', 'p1', 'p2', 'p3', 'p4']
    edges = [('v', 'p1', 1), ('v', 'p2', 1), ('v', 'p3', 1), ('v', 'p4', 1)]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name': 'SharedTerminal',
        'OPT':  1.0,
    }


def make_TermRelayForced(r=1):
    """
    S={s1,s2}, T={t1,t2}, arestas s1-t1, s2-t1, t1-t2, t2-x, autonomia r=1.

    O robô 2 só alcança t2 passando por t1, e o vértice não terminal x
    (pendurado em t2) não ajuda ninguém. OPT=1, única solução y_t1=1: o ótimo
    exige estação em um destino. Com estações restritas a V∖(S∪T) a instância
    fica inviável, o que torna o gabarito um teste direto de qualquer rotina
    que só considere não terminais (heurística primal, vértices obrigatórios).
    """
    S = ['s1', 's2']
    T = ['t1', 't2']
    V = ['s1', 's2', 't1', 't2', 'x']
    edges = [('s1', 't1', 1), ('s2', 't1', 1), ('t1', 't2', 1), ('t2', 'x', 1)]

    adj = _adj_undirected(edges)
    A_r = construir_arcos_alcance(V, adj, r)

    return S, T, V, adj, A_r, r, {
        'name': 'TermRelayForced',
        'OPT':  1.0,
    }
