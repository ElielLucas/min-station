"""Família HB: bolsão de Hall com relé, r = 1.

Por bolsão: q origens A completas com ndir destinos diretos C; relés X em
blocos disjuntos de p origens; δ = q − ndir destinos distantes D, cada um
ligado a todos os relés e a um balanceador e_d com destino próprio g_d.
k bolsões se ligam por um caminho de L >= 2 vértices não terminais.
"""

from io_instancia import adjacencia, conferir_fidelidade, gravar


def delta_de(q, ndir):
    if ndir >= q:
        raise ValueError(f'ndir={ndir} não gera deficiência em q={q}')
    return q - ndir


def construir(q, ndir, p, k=1, L=2):
    if p < 1 or L < 2 or k < 1:
        raise ValueError('p >= 1, L >= 2, k >= 1')
    delta = delta_de(q, ndir)
    V, S, T, arestas = [], [], [], []
    for j in range(k):
        A = [f'a{j}_{i}' for i in range(q)]
        C = [f'c{j}_{i}' for i in range(ndir)]
        n_reles = (q + p - 1) // p
        X = [f'x{j}_{i}' for i in range(n_reles)]
        D = [f'd{j}_{i}' for i in range(delta)]
        E = [f'e{j}_{i}' for i in range(delta)]
        G = [f'g{j}_{i}' for i in range(delta)]
        S.extend(A)
        S.extend(E)
        T.extend(C)
        T.extend(D)
        T.extend(G)
        V.extend(A + C + X + D + E + G)
        for a in A:
            for c in C:
                arestas.append((a, c))
        for i, x in enumerate(X):
            for a in A[i * p:(i + 1) * p]:
                arestas.append((a, x))
        for d, e, g in zip(D, E, G):
            for x in X:
                arestas.append((x, d))
            arestas.append((d, e))
            arestas.append((e, g))
        if j > 0:
            cadeia = [f'z{j}_{t}' for t in range(L)]
            V.extend(cadeia)
            anterior = f'g{j - 1}_0'
            caminho = [anterior] + cadeia + [G[0]]
            for u, v in zip(caminho, caminho[1:]):
                arestas.append((u, v))
    r = 1
    conferir_fidelidade(S, T, V, arestas, r)
    return S, T, V, adjacencia(arestas), arestas, r, delta


def previsao_opt(q, ndir, p, k=1):
    """min(ceil(δ/p), 3) por bolsão, vezes k. O fator k é a hipótese de aditividade."""
    delta = delta_de(q, ndir)
    um = min((delta + p - 1) // p, 3)
    return um, um * k


def emitir(pasta, q, ndir, p, k=1, L=2, seed=0):
    S, T, V, _adj, arestas, r, delta = construir(q, ndir, p, k, L)
    nome = f'hb-q{q}-ndir{ndir}-p{p}-k{k}-L{L}.txt'
    meta = {
        'nome': nome,
        'familia': 'hb',
        'instancia_original': f'hb-q{q}-ndir{ndir}-p{p}-k{k}',
        'fonte': 'gerador estrutural HB',
        'problema_original': 'MIN-STATION de Das, família HB',
        'url': '',
        'referencia': 'familias-estruturais.md',
        'transformacao': 'G-UNIT; não dirigido; passos unitários',
        'regra_ST': 'origens A e balanceadores; destinos diretos, distantes e dos balanceadores',
        'regra_r': 'r=1',
        'seed': seed,
        'observacao': f'q={q};ndir={ndir};p={p};k={k};L={L};delta={delta}',
    }
    caminho, digest = gravar(pasta, nome, S, T, V, arestas, r, meta)
    return {
        'caminho': caminho, 'sha256': digest, 'S': S, 'T': T, 'V': V,
        'arestas': arestas, 'r': r, 'q': q, 'ndir': ndir, 'p': p,
        'k': k, 'L': L, 'delta': delta,
    }
