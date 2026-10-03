"""Família BP: bin packing plantado como MIN-STATION de Das.

Construção: para cada caixa j, vértice v_j com B folhas de destino; para cada
item i de tamanho e_i, vértice u_i com e_i folhas de origem e q conectores
c_{i,j} nas arestas u_i–c_{i,j}–v_j. r = 1. m = soma e_i = q B.

O certificado de partição sai do plantio ou da programação dinâmica abaixo.
Nenhum dos dois chama o modelo MIN-STATION.
"""

import random

from io_instancia import adjacencia, conferir_fidelidade, gravar


def particao_exata(items, q, B):
    """Devolve uma lista de q listas de índices, ou None se não houver partição.

    Busca item a item, da maior peça para a menor, com poda de caixas de carga
    igual. O cache de falha usa a carga ordenada. Não usa MIN-STATION.
    """
    itens = [int(x) for x in items]
    if sum(itens) != q * B or any(x > B or x < 0 for x in itens):
        return None
    ordem = sorted(range(len(itens)), key=lambda i: -itens[i])
    cargas = [0] * q
    caixa_de = [None] * len(itens)
    falhas = set()

    def rec(k):
        if k == len(ordem):
            return True
        chave = (k, tuple(sorted(cargas)))
        if chave in falhas:
            return False
        i = ordem[k]
        vistos = set()
        for j in range(q):
            if cargas[j] in vistos:
                continue
            vistos.add(cargas[j])
            if cargas[j] + itens[i] > B:
                continue
            cargas[j] += itens[i]
            caixa_de[i] = j
            if rec(k + 1):
                return True
            cargas[j] -= itens[i]
            caixa_de[i] = None
        falhas.add(chave)
        return False

    if not rec(0):
        return None
    caixas = [[] for _ in range(q)]
    for i, j in enumerate(caixa_de):
        caixas[j].append(i)
    return caixas


def plantar_sim(q, B, seed):
    """Três inteiros por caixa, cada um no intervalo aberto (B/4, B/2), soma B."""
    lo = B // 4 + 1
    hi = (B - 1) // 2
    if lo > hi:
        raise ValueError(f'B={B} não admite tripleto inteiro em (B/4, B/2)')
    rng = random.Random(seed)
    itens = []
    caixas = []
    for _j in range(q):
        achou = None
        for _ in range(100000):
            a = rng.randint(lo, hi)
            b = rng.randint(lo, hi)
            c = B - a - b
            if lo <= c <= hi:
                achou = (a, b, c)
                break
        if achou is None:
            raise RuntimeError(f'não achei tripleto para B={B}')
        base = len(itens)
        itens.extend(achou)
        caixas.append([base, base + 1, base + 2])
    return itens, caixas


def plantar_nao(q, B, seed):
    """Mesma soma qB, perturbação +1/−1, sem partição exata."""
    itens, _ = plantar_sim(q, B, seed)
    rng = random.Random(seed + 997)
    n = len(itens)
    for _ in range(n * n * 4):
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j or itens[j] <= 1:
            continue
        trial = list(itens)
        trial[i] += 1
        trial[j] -= 1
        if particao_exata(trial, q, B) is None:
            return trial
    raise RuntimeError(f'perturbação não quebrou a partição q={q} B={B} seed={seed}')


def construir(items, q, B):
    itens = [int(x) for x in items]
    if sum(itens) != q * B:
        raise ValueError(f'soma {sum(itens)} != {q}*{B}')
    V, S, T, arestas = [], [], [], []
    caixas = [f'v{j}' for j in range(q)]
    V.extend(caixas)
    for j, v in enumerate(caixas):
        for b in range(B):
            t = f't{j}_{b}'
            T.append(t)
            V.append(t)
            arestas.append((v, t))
    for i, e in enumerate(itens):
        u = f'u{i}'
        V.append(u)
        for k in range(e):
            s = f's{i}_{k}'
            S.append(s)
            V.append(s)
            arestas.append((s, u))
        for j in range(q):
            c = f'c{i}_{j}'
            V.append(c)
            arestas.append((u, c))
            arestas.append((c, caixas[j]))
    r = 1
    conferir_fidelidade(S, T, V, arestas, r)
    return S, T, V, adjacencia(arestas), arestas, r


def limite_cobertura(items, q):
    """LB = 2n + q. n é o número de itens."""
    return 2 * len(items) + q


def emitir(pasta, items, q, B, seed, rotulo, certificado, origem):
    S, T, V, _adj, arestas, r = construir(items, q, B)
    nome = f'bp-{rotulo}-q{q}-B{B}-s{seed}.txt'
    meta = {
        'nome': nome,
        'familia': 'bp',
        'instancia_original': f'bp-q{q}-B{B}-s{seed}',
        'fonte': 'gerador estrutural BP',
        'problema_original': 'MIN-STATION de Das, família BP',
        'url': '',
        'referencia': 'familias-estruturais.md',
        'transformacao': 'G-UNIT; não dirigido; passos unitários',
        'regra_ST': 'folhas de origem e de destino, uma por unidade de item e de caixa',
        'regra_r': 'r=1',
        'seed': seed,
        'observacao': (
            f'items={",".join(str(x) for x in items)};q={q};B={B};'
            f'rotulo={rotulo};certificado={certificado};origem_certificado={origem};'
            f'LB={limite_cobertura(items, q)}'
        ),
    }
    caminho, digest = gravar(pasta, nome, S, T, V, arestas, r, meta)
    return {
        'caminho': caminho, 'sha256': digest, 'S': S, 'T': T, 'V': V,
        'arestas': arestas, 'r': r, 'items': list(items), 'q': q, 'B': B,
        'rotulo': rotulo, 'certificado': certificado, 'origem_certificado': origem,
        'lb': limite_cobertura(items, q),
    }
