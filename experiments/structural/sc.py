"""Família SC-GF2 e um gêmeo rígido de mesmas margens.

U = GF(2)^k sem o zero, n = 2^k − 1. Conjuntos F_a = {x : a·x = 1}.
Vértices w_a, s_x, t_x. Aresta s_x–w_a sse a·x = 1, e w_a–t_x para todo par.
r = 1, m = n.

O gêmeo preserva n, o tamanho de conjunto 2^(k−1) e o grau de elemento
2^(k−1), por trocas a partir da matriz de GF2. O OPT do gêmeo é o de um IP
de set cover sobre o mesmo sistema, não o do MIN-STATION.
"""

import random

from gurobipy import GRB, Model, quicksum

from io_instancia import adjacencia, conferir_fidelidade, gravar


def _vetores(k):
    return [i for i in range(1, 1 << k)]


def _dot(a, x, k):
    bits = a & x
    s = 0
    for _ in range(k):
        s ^= bits & 1
        bits >>= 1
    return s


def sistema_gf2(k):
    elems = _vetores(k)
    conjuntos = []
    for a in elems:
        conjuntos.append([x for x in elems if _dot(a, x, k) == 1])
    return elems, conjuntos


def _matriz(elems, conjuntos):
    idx = {x: i for i, x in enumerate(elems)}
    return [[1 if elems[i] in set(conj) else 0 for i in range(len(elems))] for conj in conjuntos], idx


def trocar(conjuntos, elems, rng, passos):
    """2-troca que preserva somas de linha e de coluna."""
    n = len(elems)
    pos = {x: i for i, x in enumerate(elems)}
    alvos = [set(c) for c in conjuntos]
    feitos = 0
    tentativas = 0
    while feitos < passos and tentativas < passos * 50:
        tentativas += 1
        a, b = rng.sample(range(n), 2)
        so_a = list(alvos[a] - alvos[b])
        so_b = list(alvos[b] - alvos[a])
        if not so_a or not so_b:
            continue
        x = rng.choice(so_a)
        y = rng.choice(so_b)
        alvos[a].remove(x)
        alvos[a].add(y)
        alvos[b].remove(y)
        alvos[b].add(x)
        feitos += 1
    if feitos == 0:
        raise RuntimeError('nenhuma troca no gêmeo')
    return [sorted(s, key=lambda v: pos[v]) for s in alvos]


def opt_set_cover(elems, conjuntos, time_limit=None):
    """IP de set cover. Certificado fora do MIN-STATION."""
    modelo = Model('set-cover-estrutural')
    modelo.Params.OutputFlag = 0
    if time_limit is not None:
        modelo.Params.TimeLimit = time_limit
    y = [modelo.addVar(vtype=GRB.BINARY) for _ in conjuntos]
    modelo.setObjective(quicksum(y), GRB.MINIMIZE)
    pertence = {x: [] for x in elems}
    for j, conj in enumerate(conjuntos):
        for x in conj:
            pertence[x].append(j)
    for x in elems:
        modelo.addConstr(quicksum(y[j] for j in pertence[x]) >= 1)
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        modelo.dispose()
        if time_limit is None:
            raise RuntimeError(f'set cover status {modelo.Status}')
        return None
    valor = int(round(modelo.ObjVal))
    modelo.dispose()
    return valor


def construir_de_sistema(elems, conjuntos):
    W = [f'w{i}' for i in range(len(elems))]
    S = [f's{i}' for i in range(len(elems))]
    T = [f't{i}' for i in range(len(elems))]
    pos = {x: i for i, x in enumerate(elems)}
    V = S + T + W
    arestas = []
    for j, conj in enumerate(conjuntos):
        for x in conj:
            arestas.append((S[pos[x]], W[j]))
        for i in range(len(elems)):
            arestas.append((W[j], T[i]))
    r = 1
    conferir_fidelidade(S, T, V, arestas, r)
    return S, T, V, adjacencia(arestas), arestas, r


def construir_gf2(k):
    elems, conjuntos = sistema_gf2(k)
    return (*construir_de_sistema(elems, conjuntos), elems, conjuntos)


def construir_rigido(k, seed, passos=None):
    elems, conjuntos = sistema_gf2(k)
    rng = random.Random(seed)
    passos = passos if passos is not None else 20 * len(elems)
    conjuntos = trocar(conjuntos, elems, rng, passos)
    return (*construir_de_sistema(elems, conjuntos), elems, conjuntos)


def emitir(pasta, k, seed, rigido, time_limit=None):
    if rigido:
        S, T, V, _adj, arestas, r, elems, conjuntos = construir_rigido(k, seed)
        rotulo = f'sc-rigida-k{k}-s{seed}'
        certificado = opt_set_cover(elems, conjuntos, time_limit=time_limit)
        origem = 'ip-set-cover' if certificado is not None else 'ip-set-cover-sem-prova'
    else:
        S, T, V, _adj, arestas, r, elems, conjuntos = construir_gf2(k)
        rotulo = f'sc-gf2-k{k}'
        origem = 'teorema-opt-k'
        certificado = k
        seed = 0
    nome = rotulo + '.txt'
    meta = {
        'nome': nome,
        'familia': 'sc',
        'instancia_original': f'sc-k{k}',
        'fonte': 'gerador estrutural SC',
        'problema_original': 'MIN-STATION de Das, família SC',
        'url': '',
        'referencia': 'familias-estruturais.md',
        'transformacao': 'G-UNIT; não dirigido; passos unitários',
        'regra_ST': 's_x origens, t_x destinos, w_a estações da cobertura',
        'regra_r': 'r=1',
        'seed': seed,
        'observacao': (
            f'k={k};rigido={int(rigido)};certificado={certificado};'
            f'origem_certificado={origem}'
        ),
    }
    caminho, digest = gravar(pasta, nome, S, T, V, arestas, r, meta)
    return {
        'caminho': caminho, 'sha256': digest, 'S': S, 'T': T, 'V': V,
        'arestas': arestas, 'r': r, 'k': k, 'rigido': rigido,
        'elems': elems, 'conjuntos': conjuntos,
        'certificado': certificado, 'origem_certificado': origem,
    }
