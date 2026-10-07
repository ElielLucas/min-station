"""R11 — caminhos e ciclos: geradores e certificadores literais de Das.

O certificador de caminho implementa PATH-ALG1 exatamente como documentado em
``docs/technical/reference/leituras-r11-certificadores.md``. Em particular,
``Vcounter`` conta vértices ativos e os testes ``v in S`` e ``v in T`` são
independentes. Não há reparo para fazê-lo coincidir com o baseline.

O certificador de ciclo implementa Algorithm 2: remove cada aresta do ciclo,
lineariza o caminho no sentido canônico, executa PATH-ALG1 e conserva a última
solução em empate (teste ``<=``).
"""

from __future__ import annotations

import hashlib
from collections import deque

from io_instancia import adjacencia, conferir_fidelidade, gravar

VAR_PATH = 'path-alg1'
VAR_CYCLE = 'cycle-alg2'


def _resultado(status, variant, C=None, notes=''):
    C = [] if C is None else list(C)
    return {
        'status': status,
        'C': C,
        'obj': len(C) if status == 'ok' else None,
        'variant': variant,
        'notes': notes,
    }


def _r_valido(r):
    try:
        return float(r) == int(r) and int(r) >= 1
    except (TypeError, ValueError):
        return False


def _vizinhos(V, adj):
    Vset = set(V)
    g = {v: [] for v in V}
    for u in V:
        for v, w in adj.get(u, ()):
            if w != 1:
                raise ValueError(f'aresta {u}-{v} tem peso {w}; R11 cobre passos unitários')
            if v in Vset and v not in g[u]:
                g[u].append(v)
    return g


def _conectado(V, g):
    if not V:
        return False
    visto = {V[0]}
    fila = deque([V[0]])
    while fila:
        u = fila.popleft()
        for v in g[u]:
            if v not in visto:
                visto.add(v)
                fila.append(v)
    return len(visto) == len(V)


def ordem_caminho(V, adj):
    """Ordem canônica de um caminho; ``None`` se o grafo não for caminho."""
    V = list(V)
    if not V:
        return None
    g = _vizinhos(V, adj)
    if not _conectado(V, g):
        return None
    if len(V) == 1:
        return V
    pontas = [v for v in V if len(g[v]) == 1]
    if len(pontas) != 2 or any(len(g[v]) not in (1, 2) for v in V):
        return None
    atual = min(pontas, key=str)
    anterior = None
    ordem = []
    while atual is not None:
        ordem.append(atual)
        prox = [v for v in g[atual] if v != anterior]
        if not prox:
            break
        if len(prox) != 1:
            return None
        anterior, atual = atual, prox[0]
    return ordem if len(ordem) == len(V) else None


def ordem_ciclo(V, adj):
    """Ordem canônica de um ciclo simples com pelo menos três vértices."""
    V = list(V)
    if len(V) < 3:
        return None
    g = _vizinhos(V, adj)
    if not _conectado(V, g) or any(len(g[v]) != 2 for v in V):
        return None
    inicio = min(V, key=str)
    primeiro = min(g[inicio], key=str)
    ordem = [inicio]
    anterior, atual = inicio, primeiro
    while atual != inicio:
        if atual in ordem:
            return None
        ordem.append(atual)
        prox = [v for v in g[atual] if v != anterior]
        if len(prox) != 1:
            return None
        anterior, atual = atual, prox[0]
    return ordem if len(ordem) == len(V) else None


def _path_alg1_ordem(ordem, S, T, r, variant=VAR_PATH, require_equal=True):
    """Algorithm 1 literal sobre uma ordem já validada."""
    if not _r_valido(r):
        return _resultado('invalid_input', variant, notes=f'r inválido: {r!r}')
    if require_equal and len(S) != len(T):
        return _resultado(
            'invalid_input', variant,
            notes=f'|S|={len(S)} diferente de |T|={len(T)}',
        )
    Vset = set(ordem)
    if set(S) - Vset or set(T) - Vset:
        return _resultado('invalid_input', variant, notes='terminal fora da ordem do caminho')

    Sset, Tset = set(S), set(T)
    C = []
    Cset = set()
    tcounter = 0
    vcounter = 0
    for v in ordem:
        # DAS-A1 P2 e P3: dois if independentes.
        if v in Sset:
            tcounter += 1
        if v in Tset:
            tcounter -= 1
        # DAS-A1 P4: Vcounter conta vértices, não arestas.
        if tcounter != 0:
            vcounter += 1
            if vcounter == int(r):
                if v not in Cset:
                    C.append(v)
                    Cset.add(v)
                vcounter = 0

    notes = f'tcounter_final={tcounter};vcounter_final={vcounter};ordem={"|".join(map(str, ordem))}'
    return _resultado('ok', variant, C, notes)


def certificar_path(S, T, V, adj, r, ordem=None):
    """Executa PATH-ALG1; não consulta baseline, enumeração ou solver."""
    V = list(V)
    if len(set(V)) != len(V) or len(set(S)) != len(S) or len(set(T)) != len(T):
        return _resultado('invalid_input', VAR_PATH, notes='repetição em V, S ou T')
    if ordem is None:
        try:
            ordem = ordem_caminho(V, adj)
        except ValueError as exc:
            return _resultado('invalid_input', VAR_PATH, notes=str(exc))
    else:
        ordem = list(ordem)
        if set(ordem) != set(V) or len(ordem) != len(V):
            return _resultado('invalid_input', VAR_PATH, notes='ordem não é permutação de V')
    if ordem is None:
        return _resultado('invalid_input', VAR_PATH, notes='G não é caminho simples conectado')
    return _path_alg1_ordem(ordem, S, T, r)


def certificar_cycle(S, T, V, adj, r, ordem=None):
    """Executa DAS-A2 com sentinela C=V e desempate pela última quebra."""
    V = list(V)
    if len(set(V)) != len(V) or len(set(S)) != len(S) or len(set(T)) != len(T):
        return _resultado('invalid_input', VAR_CYCLE, notes='repetição em V, S ou T')
    if len(S) != len(T):
        return _resultado('invalid_input', VAR_CYCLE, notes='|S| diferente de |T|')
    if not _r_valido(r):
        return _resultado('invalid_input', VAR_CYCLE, notes=f'r inválido: {r!r}')
    if ordem is None:
        try:
            ordem = ordem_ciclo(V, adj)
        except ValueError as exc:
            return _resultado('invalid_input', VAR_CYCLE, notes=str(exc))
    else:
        ordem = list(ordem)
        if set(ordem) != set(V) or len(ordem) != len(V):
            return _resultado('invalid_input', VAR_CYCLE, notes='ordem não é permutação de V')
    if ordem is None or len(ordem) < 3:
        return _resultado('invalid_input', VAR_CYCLE, notes='G não é ciclo simples com n>=3')

    melhor = list(ordem)  # CYCLE-SENTINEL: C <- V.
    vencedor = None
    tamanhos = []
    n = len(ordem)
    for i in range(n):
        # Remove {v_i, v_(i+1)} e percorre do sucessor até v_i.
        ordem_path = ordem[i + 1:] + ordem[:i + 1]
        res = _path_alg1_ordem(ordem_path, S, T, r, variant=VAR_PATH)
        if res['status'] != 'ok':
            return _resultado(
                'invalid_input', VAR_CYCLE,
                notes=f'quebra={i}; path-alg1 status={res["status"]}: {res["notes"]}',
            )
        X = res['C']
        tamanhos.append(len(X))
        # DAS-A2: <=, portanto empate fica com a última quebra.
        if len(X) <= len(melhor):
            melhor = list(X)
            vencedor = i

    notes = (
        f'break_winner={vencedor};break_sizes={",".join(map(str, tamanhos))};'
        f'cycle_order={"|".join(map(str, ordem))}'
    )
    return _resultado('ok', VAR_CYCLE, melhor, notes)


def construir_path(n, S, T, r):
    if int(n) != n or n < 1:
        raise ValueError('path exige n>=1 inteiro')
    V = [f'v{i}' for i in range(int(n))]
    arestas = [(V[i], V[i + 1]) for i in range(len(V) - 1)]
    conferir_fidelidade(S, T, V, arestas, r, permitir_intersecao=True)
    return list(S), list(T), V, adjacencia(arestas), arestas, int(r)


def construir_cycle(n, S, T, r):
    if int(n) != n or n < 3:
        raise ValueError('cycle exige n>=3 inteiro')
    V = [f'v{i}' for i in range(int(n))]
    arestas = [(V[i], V[(i + 1) % len(V)]) for i in range(len(V))]
    conferir_fidelidade(S, T, V, arestas, r, permitir_intersecao=True)
    return list(S), list(T), V, adjacencia(arestas), arestas, int(r)


def diametro_path(n):
    return max(0, int(n) - 1)


def diametro_cycle(n):
    return int(n) // 2


def _ordem_hash(vertices, familia, n, m, seed):
    """Ordenação pseudoaleatória reprodutível sem depender de ``random``."""
    def chave(v):
        bruto = f'R11|{familia}|{n}|{m}|{seed}|{v}'.encode('utf-8')
        return hashlib.sha256(bruto).hexdigest(), str(v)
    return sorted(vertices, key=chave)


def politica_oficial(familia, n, m, seed):
    if familia not in ('path', 'cycle', 'spider'):
        raise ValueError(f'família desconhecida: {familia}')
    politicas = ['disj', 'sit1', 'sitm', 'stay']
    if familia == 'spider':
        politicas.append('sit_center')
    return politicas[(int(n) + 3 * int(m) + int(seed)) % len(politicas)]


def r_oficial(seed, diametro):
    opcoes = [1, 2, int(diametro)]
    r = opcoes[int(seed) % 3]
    return max(1, int(r))


def terminais_deterministicos(V, familia, n, m, seed, politica=None, center=None):
    """Constrói S/T segundo a política congelada do pré-registro R11."""
    V = list(V)
    m = int(m)
    if m < 1 or m > len(V):
        raise ValueError(f'm={m} inválido para n={len(V)}')
    politica = politica or politica_oficial(familia, n, m, seed)

    if politica == 'sit_center':
        if familia != 'spider' or center not in V:
            raise ValueError('sit_center exige spider e centro válido')
        if m == 1:
            return [center], [center], politica
        resto = _ordem_hash([v for v in V if v != center], familia, n, m, seed)
        if len(resto) < 2 * (m - 1):
            raise ValueError('vértices insuficientes para sit_center com resto disjunto')
        S = [center] + resto[:m - 1]
        T = [center] + resto[m - 1:2 * (m - 1)]
        return S, T, politica

    ordem = _ordem_hash(V, familia, n, m, seed)
    if politica == 'disj':
        if len(ordem) < 2 * m:
            raise ValueError('vértices insuficientes para política disj')
        return ordem[:m], ordem[m:2 * m], politica
    if politica == 'sit1':
        if m == 1:
            return [ordem[0]], [ordem[0]], politica
        necessario = 1 + 2 * (m - 1)
        if len(ordem) < necessario:
            raise ValueError('vértices insuficientes para política sit1')
        comum = ordem[0]
        S = [comum] + ordem[1:m]
        T = [comum] + ordem[m:2 * m - 1]
        return S, T, politica
    if politica == 'sitm':
        k = min(m, 2)
        necessario = k + 2 * (m - k)
        if len(ordem) < necessario:
            raise ValueError('vértices insuficientes para política sitm')
        comuns = ordem[:k]
        pos = k
        S = comuns + ordem[pos:pos + (m - k)]
        pos += (m - k)
        T = comuns + ordem[pos:pos + (m - k)]
        return S, T, politica
    if politica == 'stay':
        base = ordem[:m]
        return base, list(base), politica
    raise ValueError(f'política desconhecida: {politica}')


def emitir_path(pasta, ident, n, m, seed=None, r=None, politica=None, S=None, T=None, papel=''):
    V = [f'v{i}' for i in range(int(n))]
    if S is None or T is None:
        if seed is None:
            raise ValueError('seed obrigatória quando S/T não são fornecidos')
        S, T, politica = terminais_deterministicos(V, 'path', n, m, seed, politica)
    if r is None:
        if seed is None:
            raise ValueError('seed obrigatória quando r não é fornecido')
        r = r_oficial(seed, diametro_path(n))
    S, T, V, _adj, arestas, r = construir_path(n, S, T, r)
    meta = {
        'nome': ident,
        'familia': 'path',
        'fonte': 'R11 Spec D',
        'referencia': 'pre-registro-r11-certificadores.md',
        'regra_ST': politica or 'hand',
        'regra_r': str(r),
        'seed': 'hand' if seed is None else seed,
        'papel': papel,
    }
    caminho, digest = gravar(pasta, f'{ident}.txt', S, T, V, arestas, r, meta)
    return {
        'id': ident, 'familia': 'path', 'S': S, 'T': T, 'V': V,
        'adj': adjacencia(arestas), 'arestas': arestas, 'r': r,
        'seed': seed, 'politica': politica or 'hand', 'papel': papel,
        'caminho': caminho, 'sha256': digest,
    }


def emitir_cycle(pasta, ident, n, m, seed=None, r=None, politica=None, S=None, T=None, papel=''):
    V = [f'v{i}' for i in range(int(n))]
    if S is None or T is None:
        if seed is None:
            raise ValueError('seed obrigatória quando S/T não são fornecidos')
        S, T, politica = terminais_deterministicos(V, 'cycle', n, m, seed, politica)
    if r is None:
        if seed is None:
            raise ValueError('seed obrigatória quando r não é fornecido')
        r = r_oficial(seed, diametro_cycle(n))
    S, T, V, _adj, arestas, r = construir_cycle(n, S, T, r)
    meta = {
        'nome': ident,
        'familia': 'cycle',
        'fonte': 'R11 Spec D',
        'referencia': 'pre-registro-r11-certificadores.md',
        'regra_ST': politica or 'hand',
        'regra_r': str(r),
        'seed': 'hand' if seed is None else seed,
        'papel': papel,
    }
    caminho, digest = gravar(pasta, f'{ident}.txt', S, T, V, arestas, r, meta)
    return {
        'id': ident, 'familia': 'cycle', 'S': S, 'T': T, 'V': V,
        'adj': adjacencia(arestas), 'arestas': arestas, 'r': r,
        'seed': seed, 'politica': politica or 'hand', 'papel': papel,
        'caminho': caminho, 'sha256': digest,
    }
