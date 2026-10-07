"""R11 — geradores e leituras executáveis do algoritmo para aranhas.

Este módulo NÃO reconstrói um algoritmo melhor que o artigo. As variantes
``spider-A``, ``spider-B`` e ``spider-U`` seguem as decisões documentadas em
``leituras-r11-certificadores.md``. Onde INT-A não determina quais terminais
sobram numa radial mista e desbalanceada, a implementação devolve
``unspecified`` em vez de escolher uma regra por conveniência.
"""

from __future__ import annotations

from collections import deque

from io_instancia import adjacencia, conferir_fidelidade, gravar
from path_cycle import (
    _path_alg1_ordem,
    _resultado,
    _r_valido,
    r_oficial,
    terminais_deterministicos,
)

VARIANTS = ('spider-A', 'spider-B', 'spider-U')


def construir_spider(comprimentos, S, T, r):
    """Constrói uma aranha com centro ``c`` e radiais ``r{i}_{d}``.

    ``d`` é a distância ao centro, começando em 1. Cada comprimento deve ser
    >=1 e devem existir pelo menos três radiais.
    """
    comprimentos = [int(x) for x in comprimentos]
    if len(comprimentos) < 3 or any(x < 1 for x in comprimentos):
        raise ValueError('spider exige pelo menos 3 radiais não vazias')
    V = ['c']
    arestas = []
    for i, L in enumerate(comprimentos):
        anterior = 'c'
        for d in range(1, L + 1):
            v = f'r{i}_{d}'
            V.append(v)
            arestas.append((anterior, v))
            anterior = v
    conferir_fidelidade(S, T, V, arestas, r, permitir_intersecao=True)
    return list(S), list(T), V, adjacencia(arestas), arestas, int(r), 'c'


def comprimentos_quase_iguais(n, k):
    """Particiona n-1 em k radiais; resto vai para as primeiras radiais."""
    n, k = int(n), int(k)
    if k < 3 or n < k + 1:
        raise ValueError(f'n={n}, k={k} não formam aranha')
    q, resto = divmod(n - 1, k)
    return [q + (1 if i < resto else 0) for i in range(k)]


def diametro_spider(comprimentos):
    a, b = sorted((int(x) for x in comprimentos), reverse=True)[:2]
    return a + b


def _grafo(V, adj):
    Vset = set(V)
    g = {v: [] for v in V}
    for u in V:
        for v, w in adj.get(u, ()):
            if w != 1:
                raise ValueError(f'aresta {u}-{v} tem peso {w}; R11 cobre passos unitários')
            if v in Vset and v not in g[u]:
                g[u].append(v)
    return g


def decompor_spider(V, adj):
    """Devolve ``(center, radiais, depth, radial_of)`` ou ``None``.

    Cada radial é listada do vizinho do centro até a folha.
    """
    V = list(V)
    if len(V) < 4:
        return None
    try:
        g = _grafo(V, adj)
    except ValueError:
        return None
    # Conectividade e número de arestas de uma árvore.
    vistos = set()
    fila = deque([V[0]])
    vistos.add(V[0])
    while fila:
        u = fila.popleft()
        for v in g[u]:
            if v not in vistos:
                vistos.add(v)
                fila.append(v)
    if len(vistos) != len(V):
        return None
    m2 = sum(len(g[v]) for v in V)
    if m2 != 2 * (len(V) - 1):
        return None
    centros = [v for v in V if len(g[v]) >= 3]
    if len(centros) != 1 or any(len(g[v]) > 2 for v in V if v not in centros):
        return None
    c = centros[0]

    radiais = []
    depth = {c: 0}
    radial_of = {c: None}
    for rid, primeiro in enumerate(sorted(g[c], key=str)):
        radial = []
        anterior, atual, d = c, primeiro, 1
        while True:
            radial.append(atual)
            depth[atual] = d
            radial_of[atual] = rid
            prox = [v for v in g[atual] if v != anterior]
            if not prox:
                break
            if len(prox) != 1:
                return None
            anterior, atual = atual, prox[0]
            d += 1
        radiais.append(radial)
    return c, radiais, depth, radial_of


def _tree_distance(u, v, center, depth, radial_of):
    if u == v:
        return 0
    if u == center:
        return depth[v]
    if v == center:
        return depth[u]
    if radial_of[u] == radial_of[v]:
        return abs(depth[u] - depth[v])
    return depth[u] + depth[v]


def _add_unique(C, Cset, vertices):
    for v in vertices:
        if v not in Cset:
            C.append(v)
            Cset.add(v)


def _stations_l1a_outgoing(radial, origins, r, depth):
    """SP-L1-A em radial sem alvos locais: guloso por distância em arestas.

    A origem mais profunda determina as estações a cada r arestas no sentido
    folha→centro. Esta função só é usada quando todos os terminais locais são
    origens; radiais mistas desbalanceadas são ``unspecified`` no contrato R11.
    """
    if not origins:
        return []
    dmax = max(depth[s] for s in origins)
    pos = dmax - int(r)
    station_depths = set()
    while pos > 0:
        station_depths.add(pos)
        pos -= int(r)
    by_depth = {depth[v]: v for v in radial}
    return [by_depth[d] for d in sorted(station_depths, reverse=True)]


def _remaining_battery(origin, Cset, r, depth, radial_of):
    rid = radial_of[origin]
    d0 = depth[origin]
    encountered = [depth[v] for v in Cset if radial_of.get(v) == rid and depth[v] <= d0]
    if encountered:
        nearest_center = min(encountered)
        return int(r) - nearest_center
    return int(r) - d0


def _radial_phase(S, T, radiais, depth, radial_of, r, variant):
    """Processa radiais e devolve estações + estado agregado em c.

    INT-A está fechado apenas quando a radial é balanceada (resolvida como
    caminho) ou contém terminais de um único lado. Mistura desbalanceada não
    determina quais terminais ficam em L_R/L_T e retorna ``unspecified``.
    """
    Sset, Tset = set(S), set(T)
    C, Cset = [], set()
    remaining_origins = []
    remaining_targets = []
    traces = []

    for rid, radial in enumerate(radiais):
        local_S = [v for v in radial if v in Sset]
        local_T = [v for v in radial if v in Tset]
        ordem_leaf_center = list(reversed(radial))

        if local_S and local_T and len(local_S) != len(local_T):
            return None, None, None, (
                f'INT-A não fecha radial mista desbalanceada rid={rid} '
                f'|S_i|={len(local_S)} |T_i|={len(local_T)}'
            )

        if variant == 'spider-B':
            # SP-L1-B: costura PATH-ALG1 mesmo em radial com só origens ou só alvos.
            res = _path_alg1_ordem(
                ordem_leaf_center, local_S, local_T, r,
                variant='spider-L1B', require_equal=False,
            )
            if res['status'] != 'ok':
                return None, None, None, f'L1B rid={rid}: {res["notes"]}'
            _add_unique(C, Cset, res['C'])
        elif local_S and local_T:
            # INT-A: se a cardinalidade local fecha, resolve a subinstância caminho.
            res = _path_alg1_ordem(
                ordem_leaf_center, local_S, local_T, r,
                variant='spider-INT-A', require_equal=True,
            )
            if res['status'] != 'ok':
                return None, None, None, f'INT-A rid={rid}: {res["notes"]}'
            _add_unique(C, Cset, res['C'])
        elif local_S:
            _add_unique(C, Cset, _stations_l1a_outgoing(radial, local_S, r, depth))

        # Com cardinalidades iguais a INT-A consome todos os terminais locais.
        if len(local_S) == len(local_T):
            traces.append(f'R{rid}:internal={len(local_S)}')
            continue
        if local_S and not local_T:
            remaining_origins.extend(local_S)
            traces.append(f'R{rid}:out={len(local_S)}')
        elif local_T and not local_S:
            remaining_targets.extend(local_T)
            traces.append(f'R{rid}:in={len(local_T)}')

    robots = [
        {'s': s, 'battery': _remaining_battery(s, Cset, r, depth, radial_of)}
        for s in remaining_origins
    ]
    return C, robots, remaining_targets, ';'.join(traces)


def certificar_spider(S, T, V, adj, r, variant='spider-A'):
    if variant not in VARIANTS:
        return _resultado('invalid_input', variant, notes='variante spider desconhecida')
    if len(S) != len(T):
        return _resultado('invalid_input', variant, notes='|S| diferente de |T|')
    if not _r_valido(r):
        return _resultado('invalid_input', variant, notes=f'r inválido: {r!r}')
    if len(set(V)) != len(V) or len(set(S)) != len(S) or len(set(T)) != len(T):
        return _resultado('invalid_input', variant, notes='repetição em V, S ou T')
    if set(S) - set(V) or set(T) - set(V):
        return _resultado('invalid_input', variant, notes='terminal fora de V')

    dec = decompor_spider(V, adj)
    if dec is None:
        return _resultado('invalid_input', variant, notes='G não é aranha simples conectada')
    center, radiais, depth, radial_of = dec

    # SP-R4-UNSPEC da variante conservadora.
    if variant == 'spider-U' and set(S) & set(T):
        return _resultado('unspecified', variant, notes='SP-R4-UNSPEC: S∩T não vazio')

    C, robots, targets, trace = _radial_phase(
        S, T, radiais, depth, radial_of, int(r), variant,
    )
    if C is None:
        return _resultado('unspecified', variant, notes=trace)
    Cset = set(C)

    # Terminais no centro entram no agregado sem cancelar S∩T.
    if center in set(S):
        robots.append({'s': center, 'battery': int(r)})
    if center in set(T):
        targets.append(center)

    if len(robots) != len(targets):
        return _resultado(
            'unspecified', variant, C,
            notes=(
                f'{trace}; L_R/L_T não fecham sob INT-A: '
                f'{len(robots)} vs {len(targets)}'
            ),
        )

    if variant == 'spider-U' and any(x['battery'] == 0 for x in robots):
        return _resultado(
            'unspecified', variant, C,
            notes=f'{trace}; SP-R5-UNSPEC: r_prime=0',
        )

    # Se alguma leitura literal não leva o robô ao centro, preserva C e não
    # inventa reparo. O conjunto pode ser marcado inviável pelo validador.
    if any(x['battery'] < 0 for x in robots):
        return _resultado(
            'ok', variant, C,
            notes=f'{trace}; radial_reach_failure_before_center',
        )

    # PR-L2: carga restante decrescente × distância ao centro decrescente.
    robots = sorted(robots, key=lambda x: (-x['battery'], str(x['s'])))
    targets = sorted(targets, key=lambda t: (-depth[t], str(t)))
    pares = list(zip(robots, targets))

    # C1: todos alcançam diretamente seu alvo com a carga restante.
    c1 = all(rb['battery'] >= depth[t] for rb, t in pares)

    # C2-3: escolher a estação radial já colocada mais próxima do centro.
    radial_stations = [v for v in C if v != center]
    sigma = None
    c2 = False
    if radial_stations:
        sigma = min(radial_stations, key=lambda v: (depth[v], str(v)))
        robots_reach = all(rb['battery'] >= depth[sigma] for rb, _t in pares)
        targets_reach = all(
            _tree_distance(sigma, t, center, depth, radial_of) <= int(r)
            for _rb, t in pares
        )
        c2 = robots_reach and targets_reach

    if not c1 and not c2 and robots:
        if center not in Cset:
            C.append(center)
            Cset.add(center)

    pareamento = ','.join(
        f'{rb["s"]}:{rb["battery"]}->{t}:{depth[t]}' for rb, t in pares
    )
    notes = (
        f'{trace};center={center};C1={int(c1)};C2={int(c2)};'
        f'sigma={sigma};pairs={pareamento}'
    )
    return _resultado('ok', variant, C, notes)


def emitir_spider(
    pasta,
    ident,
    comprimentos,
    m,
    seed=None,
    r=None,
    politica=None,
    S=None,
    T=None,
    papel='',
):
    comprimentos = [int(x) for x in comprimentos]
    n = 1 + sum(comprimentos)
    V = ['c'] + [
        f'r{i}_{d}' for i, L in enumerate(comprimentos) for d in range(1, L + 1)
    ]
    if S is None or T is None:
        if seed is None:
            raise ValueError('seed obrigatória quando S/T não são fornecidos')
        S, T, politica = terminais_deterministicos(
            V, 'spider', n, m, seed, politica, center='c',
        )
    if r is None:
        if seed is None:
            raise ValueError('seed obrigatória quando r não é fornecido')
        r = r_oficial(seed, diametro_spider(comprimentos))
    S, T, V, _adj, arestas, r, center = construir_spider(comprimentos, S, T, r)
    meta = {
        'nome': ident,
        'familia': 'spider',
        'fonte': 'R11 Spec D',
        'referencia': 'pre-registro-r11-certificadores.md',
        'regra_ST': politica or 'hand',
        'regra_r': str(r),
        'seed': 'hand' if seed is None else seed,
        'papel': papel,
        'radiais': ','.join(map(str, comprimentos)),
        'center': center,
    }
    caminho, digest = gravar(pasta, f'{ident}.txt', S, T, V, arestas, r, meta)
    return {
        'id': ident, 'familia': 'spider', 'S': S, 'T': T, 'V': V,
        'adj': adjacencia(arestas), 'arestas': arestas, 'r': r,
        'seed': seed, 'politica': politica or 'hand', 'papel': papel,
        'comprimentos': comprimentos, 'center': center,
        'caminho': caminho, 'sha256': digest,
    }
