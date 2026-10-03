"""Família TR: k corredores de comprimento L, r passos, degraus a cada σ.

m origens ligadas a todas as entradas. Corredor j: e_j – c_{j,1} … c_{j,L} – x_j.
x_j liga todos os destinos. D = L + 3. σ = None significa sem degraus.
"""

from io_instancia import adjacencia, conferir_fidelidade, gravar


def construir(k, L, r, sigma, m=2):
    if k < 1 or L < 1 or r < 1 or m < 1:
        raise ValueError('parâmetros de TR inválidos')
    S = [f's{i}' for i in range(m)]
    T = [f't{i}' for i in range(m)]
    V = list(S) + list(T)
    arestas = []
    corredores = []
    for j in range(k):
        e = f'e{j}'
        internos = [f'c{j}_{i}' for i in range(1, L + 1)]
        x = f'x{j}'
        caminho = [e] + internos + [x]
        corredores.append(caminho)
        V.extend(caminho)
        for u, v in zip(caminho, caminho[1:]):
            arestas.append((u, v))
        for s in S:
            arestas.append((s, e))
        for t in T:
            arestas.append((x, t))
    if sigma is not None:
        for ell in range(1, L + 1):
            if ell % sigma != 0:
                continue
            for j in range(k - 1):
                arestas.append((f'c{j}_{ell}', f'c{j + 1}_{ell}'))
    conferir_fidelidade(S, T, V, arestas, r)
    return S, T, V, adjacencia(arestas), arestas, r, corredores


def opt_formula(L, r):
    D = L + 3
    return (D + r - 1) // r - 1


def emitir(pasta, k, L, r, sigma, m=2, seed=0):
    S, T, V, _adj, arestas, _r, _cor = construir(k, L, r, sigma, m)
    sig = 'inf' if sigma is None else str(sigma)
    nome = f'tr-k{k}-L{L}-r{r}-sig{sig}-m{m}.txt'
    meta = {
        'nome': nome,
        'familia': 'tr',
        'instancia_original': f'tr-k{k}-L{L}-r{r}-sig{sig}',
        'fonte': 'gerador estrutural TR',
        'problema_original': 'MIN-STATION de Das, família TR',
        'url': '',
        'referencia': 'familias-estruturais.md',
        'transformacao': 'G-UNIT; não dirigido; passos unitários',
        'regra_ST': 'm origens nas entradas, m destinos nas saídas dos corredores',
        'regra_r': f'r={r}',
        'seed': seed,
        'observacao': f'k={k};L={L};r={r};sigma={sig};m={m};D={L + 3}',
    }
    caminho, digest = gravar(pasta, nome, S, T, V, arestas, r, meta)
    return {
        'caminho': caminho, 'sha256': digest, 'S': S, 'T': T, 'V': V,
        'arestas': arestas, 'r': r, 'k': k, 'L': L, 'sigma': sigma, 'm': m,
    }
