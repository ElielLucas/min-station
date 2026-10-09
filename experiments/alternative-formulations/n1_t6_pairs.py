"""N1-T6: tres pares deterministas, com UMA substituicao de aresta por controle.

Nao mede LP, nao usa Gurobi. Os parametros da geracao sao congelados pelo
runner ANTES de invocar build_pair(). Nenhuma busca, seed ou selecao adaptativa.
"""
from __future__ import annotations

from collections import deque

# Cada familia e uma construcao distinta, nao uma seed de um mesmo grafo.
RECIPES = (
    {
        'id': 'T6-TRI-01', 'family': 'tri', 'factory': 'Tri(r=1)',
        'remove': ['s1', 'b'], 'add': ['s1', 'c'],
        'obstruction': 'sobreposicao ciclica das incidencias origem/destino em tres reles',
        'change': 'relocalizar somente s1-b para s1-c; rompe a simetria do ciclo',
    },
    {
        'id': 'T6-F2-01', 'family': 'f2', 'factory': 'F2(k=1,L=3,r=1)',
        'remove': ['b1', 'c1'], 'add': ['b1', 'g1'],
        'obstruction': 'duas origens competem diretamente pelo mesmo destino c1 (bolsao de Hall)',
        'change': 'relocalizar somente b1-c1 para b1-g1; remove incidencia comum a c1',
    },
    {
        'id': 'T6-SEC59-01', 'family': 'sec59', 'factory': 'Sec59(L=4,r=1)',
        'remove': ['s2', 't1'], 'add': ['s2', 't2'],
        'obstruction': 'duas origens compartilham t1 e acesso alternativo exige corredor longo',
        'change': 'relocalizar somente s2-t1 para s2-t2; injeta atalho direto de controle',
    },
)


def _edge(a, b):
    if a == b:
        raise ValueError('laço nao permitido')
    return tuple(sorted((a, b)))


def _edges(adj):
    result = set()
    for u, nbrs in adj.items():
        for v, weight in nbrs:
            if float(weight) != 1.0:
                raise ValueError('T6 somente arestas unitarias')
            result.add(_edge(u, v))
    return result


def _connected(vertices, edges):
    if not vertices:
        return True
    adj = {v: [] for v in vertices}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = {vertices[0]}
    queue = deque([vertices[0]])
    while queue:
        for v in adj[queue.popleft()]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == len(vertices)


def _factory(name):
    from synthetic import make_Tri, make_F2, make_Sec59
    if name == 'Tri(r=1)':
        return make_Tri(r=1)
    if name == 'F2(k=1,L=3,r=1)':
        return make_F2(k=1, L=3, r=1)
    if name == 'Sec59(L=4,r=1)':
        return make_Sec59(L=4, r=1)
    raise ValueError(f'factory nao registrada: {name}')


def _obstruction_holds(recipe, edges):
    family = recipe['family']
    if family == 'tri':
        return all(_edge(*e) in edges for e in (
            ('s1','a'),('s1','b'),('s2','b'),('s2','c'),
            ('s3','c'),('s3','a'),('t1','a'),('t1','b'),
            ('t2','b'),('t2','c'),('t3','c'),('t3','a')))
    if family == 'f2':
        return all(_edge(*e) in edges for e in (('a1','c1'),('b1','c1'),
                              ('a1','x1'),('b1','x1'),('x1','d1')))
    if family == 'sec59':
        return all(_edge(*e) in edges for e in (
            ('s1','t1'),('s2','t1'),('s1','w1'),('s2','w1'),
            ('w1','w2'),('w2','w3'),('w3','w4'),('w4','t2')))
    return False


def build_pair(recipe):
    """Retorna dois grafos; a variante de controle troca exatamente uma aresta."""
    from ms_utils import construir_arcos_alcance
    S, T, V, adj, _ar, r, _meta = _factory(recipe['factory'])
    S, T, V = list(S), list(T), list(V)
    if len(V) > 10 or len(S) != 3 or len(T) != 3 or r != 1:
        raise AssertionError('fora do tamanho/tipo pre-registrado')
    original = _edges(adj)
    rem, add = _edge(*recipe['remove']), _edge(*recipe['add'])
    if rem not in original or add in original:
        raise AssertionError('substituicao de aresta nao corresponde ao protocolo')
    control = (original - {rem}) | {add}
    if not _obstruction_holds(recipe, original) or _obstruction_holds(recipe, control):
        raise AssertionError('obstrucao ausente na variante ou ainda presente no controle')
    if not all(_connected(V, e) for e in (original, control)):
        raise AssertionError('grafo desconexo')
    def create(role, edges):
        adj2 = {v: [] for v in V}
        for a, b in sorted(edges):
            adj2[a].append((b, 1))
            adj2[b].append((a, 1))
        ar = construir_arcos_alcance(V, adj2, r)
        return {'name': recipe['id'] + '-' + role, 'pair_id': recipe['id'],
                'family': recipe['family'], 'role': role, 'S': S, 'T': T, 'V': V,
                'r': r, 'edges': [list(e) for e in sorted(edges)],
                'A_r': [list(e) for e in sorted(ar)], 'adj': adj2}
    a, b = create('obstruction', original), create('control', control)
    if len(a['edges']) != len(b['edges']) or len(a['V']) != len(b['V']):
        raise AssertionError('pareamento altera dimensoes ou numero de arestas')
    if set(tuple(e) for e in a['edges']) - set(tuple(e) for e in b['edges']) != {rem}:
        raise AssertionError('troca nao unica')
    if set(tuple(e) for e in b['edges']) - set(tuple(e) for e in a['edges']) != {add}:
        raise AssertionError('troca nao unica')
    return a, b


def shortcut_diagnostics(graph):
    """Auditoria descritiva; ausencia de OPT=0 e atestada na fase certify."""
    S, T, ar = set(graph['S']), set(graph['T']), set(map(tuple, graph['A_r']))
    direct = sorted([list(e) for e in ar if e[0] in S and e[1] in T])
    terminal_links = sorted([list(e) for e in ar if e[0] in S | T and e[1] in S | T])
    return {'direct_origin_destination_arcs': direct,
            'terminal_to_terminal_arcs': terminal_links,
            'terminals_can_be_stations': True,
            'terminal_shortcut_review': 'Apenas diagnostico; OPT=0 exclui par na fase certify; '
                                        'atalho introduzido no controle e explicito na receita'}
