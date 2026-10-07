"""Catálogo congelado de instâncias da Spec D / R11.

Este módulo contém somente definições determinísticas. Não chama solver,
validador ou certificador. ``prepare_r11.py`` materializa estas definições e
registra os SHA-256 antes do lote oficial.
"""

from __future__ import annotations

from path_cycle import (
    construir_cycle,
    construir_path,
    diametro_cycle,
    diametro_path,
    politica_oficial,
    r_oficial,
    terminais_deterministicos,
)
from spider import (
    comprimentos_quase_iguais,
    construir_spider,
    diametro_spider,
)


N_OPT_ENUM = 16
N_MEDIUM_MAX = 32
MAX_W = 200000
SOLVER_SEED = 42
THREADS = 1
BASELINE_TIME_LIMIT = 1800


def _path(ident, n, m, r, S, T, papel, estrato='micro', seed=None, politica='hand'):
    S, T, V, adj, arestas, r = construir_path(n, S, T, r)
    return {
        'id': ident, 'familia': 'path', 'estrato': estrato, 'n': len(V),
        'm': len(S), 'S': S, 'T': T, 'V': V, 'adj': adj, 'arestas': arestas,
        'r': r, 'seed': seed, 'politica': politica, 'papel': papel,
        'radiais': None,
    }


def _cycle(ident, n, m, r, S, T, papel, estrato='micro', seed=None, politica='hand'):
    S, T, V, adj, arestas, r = construir_cycle(n, S, T, r)
    return {
        'id': ident, 'familia': 'cycle', 'estrato': estrato, 'n': len(V),
        'm': len(S), 'S': S, 'T': T, 'V': V, 'adj': adj, 'arestas': arestas,
        'r': r, 'seed': seed, 'politica': politica, 'papel': papel,
        'radiais': None,
    }


def _spider(
    ident, comprimentos, m, r, S, T, papel, estrato='micro', seed=None, politica='hand',
):
    S, T, V, adj, arestas, r, center = construir_spider(comprimentos, S, T, r)
    return {
        'id': ident, 'familia': 'spider', 'estrato': estrato, 'n': len(V),
        'm': len(S), 'S': S, 'T': T, 'V': V, 'adj': adj, 'arestas': arestas,
        'r': r, 'seed': seed, 'politica': politica, 'papel': papel,
        'radiais': list(comprimentos), 'center': center,
    }


def _random_path(ident, n, m, seed, estrato):
    V = [f'v{i}' for i in range(n)]
    politica = politica_oficial('path', n, m, seed)
    S, T, _ = terminais_deterministicos(V, 'path', n, m, seed, politica)
    r = r_oficial(seed, diametro_path(n))
    return _path(ident, n, m, r, S, T, 'deterministic-seeded', estrato, seed, politica)


def _random_cycle(ident, n, m, seed, estrato):
    V = [f'v{i}' for i in range(n)]
    politica = politica_oficial('cycle', n, m, seed)
    S, T, _ = terminais_deterministicos(V, 'cycle', n, m, seed, politica)
    r = r_oficial(seed, diametro_cycle(n))
    return _cycle(ident, n, m, r, S, T, 'deterministic-seeded', estrato, seed, politica)


def _random_spider(ident, n, k, m, seed, estrato):
    comprimentos = comprimentos_quase_iguais(n, k)
    V = ['c'] + [
        f'r{i}_{d}' for i, L in enumerate(comprimentos) for d in range(1, L + 1)
    ]
    politica = politica_oficial('spider', n, m, seed)
    S, T, _ = terminais_deterministicos(
        V, 'spider', n, m, seed, politica, center='c',
    )
    r = r_oficial(seed, diametro_spider(comprimentos))
    return _spider(
        ident, comprimentos, m, r, S, T, 'deterministic-seeded',
        estrato, seed, politica,
    )


def catalogo_oficial():
    out = []

    # Path — micro, casos à mão.
    out.extend([
        _path('path-hand-opt0-r2', 3, 1, 2, ['v0'], ['v2'], 'VAL-A2 / VP-OPT0'),
        _path('path-hand-one-r1', 3, 1, 1, ['v0'], ['v2'], 'VAL-A2 origem+meio'),
        _path('path-hand-stay', 5, 1, 2, ['v2'], ['v2'], 'permanência'),
        _path('path-hand-sit', 5, 2, 2, ['v0', 'v2'], ['v2', 'v4'], 'S∩T'),
        _path(
            'path-hand-sit-nperm', 5, 2, 1,
            ['v0', 'v1'], ['v1', 'v4'],
            'interseção presente, matching ordenado não força permanência em v1',
        ),
        _path('path-hand-diam', 8, 1, 7, ['v0'], ['v7'], 'r>=diam'),
    ])
    for ident, n, m, seed in [
        ('path-m-n8-m1-s42', 8, 1, 42),
        ('path-m-n8-m2-s42', 8, 2, 42),
        ('path-m-n8-m2-s43', 8, 2, 43),
        ('path-m-n12-m2-s42', 12, 2, 42),
        ('path-m-n16-m4-s42', 16, 4, 42),
        ('path-m-n16-m4-s43', 16, 4, 43),
    ]:
        out.append(_random_path(ident, n, m, seed, 'micro'))
    for ident, n, m in [
        ('path-M-n24-m2-s42', 24, 2),
        ('path-M-n24-m4-s42', 24, 4),
        ('path-M-n32-m4-s42', 32, 4),
    ]:
        out.append(_random_path(ident, n, m, 42, 'medium'))

    # Cycle — micro e medium.
    out.extend([
        _cycle('cycle-hand-n3-opt0', 3, 1, 2, ['v0'], ['v1'], 'OPT 0 possível'),
        _cycle('cycle-hand-n5-r1', 5, 1, 1, ['v0'], ['v2'], 'uma estação / quebras'),
        _cycle(
            'cycle-hand-breaks', 6, 2, 1,
            ['v0', 'v3'], ['v2', 'v5'],
            'quebras com cardinalidades diferentes antes do mínimo',
        ),
        _cycle(
            'cycle-hand-sym', 6, 2, 2,
            ['v0', 'v3'], ['v1', 'v4'], 'simetria',
        ),
        _cycle(
            'cycle-hand-sit', 6, 2, 1,
            ['v0', 'v2'], ['v2', 'v4'], 'S∩T',
        ),
        _cycle(
            'cycle-hand-stay', 6, 2, 1,
            ['v0', 'v3'], ['v0', 'v3'], 'S=T / permanência',
        ),
    ])
    for ident, n, m, seed in [
        ('cycle-m-n8-m2-s42', 8, 2, 42),
        ('cycle-m-n12-m2-s43', 12, 2, 43),
        ('cycle-m-n16-m4-s42', 16, 4, 42),
    ]:
        out.append(_random_cycle(ident, n, m, seed, 'micro'))
    for ident, n, m in [
        ('cycle-M-n24-m2-s42', 24, 2),
        ('cycle-M-n32-m4-s42', 32, 4),
    ]:
        out.append(_random_cycle(ident, n, m, 42, 'medium'))

    # Spider — cinco leituras obrigatórias.
    out.extend([
        _spider(
            'spider-reading-01', [3, 3, 1], 1, 2,
            ['r0_3'], ['r1_3'], 'SP-R1',
        ),
        _spider(
            'spider-reading-02', [1, 5, 1], 1, 2,
            ['r0_1'], ['r1_5'], 'SP-R2: d(s,c)=1, d(c,t)=5',
        ),
        _spider(
            'spider-reading-03', [4, 4, 4], 3, 2,
            ['r0_4', 'r1_4', 'r2_4'], ['r0_2', 'r2_2', 'r2_1'],
            'SP-R3: interno + cruzado + radial alvo já ativa',
        ),
        _spider(
            'spider-reading-04', [2, 2, 1], 2, 2,
            ['c', 'r0_2'], ['c', 'r1_2'], 'SP-R4: c em S∩T + par cruzado',
        ),
        _spider(
            'spider-reading-05', [1, 3, 1], 1, 1,
            ['r0_1'], ['r1_3'], 'SP-R5: r_prime=0',
        ),
    ])

    # Spider — cobertura manual adicional.
    out.extend([
        _spider('spider-hand-min3', [1, 1, 1], 1, 1, ['r0_1'], ['r1_1'], 'aranha mínima'),
        _spider('spider-hand-rad1', [1, 3, 4], 1, 2, ['r1_3'], ['r2_4'], 'radial unitária presente'),
        _spider('spider-hand-len', [1, 3, 6], 1, 2, ['r2_6'], ['r1_3'], 'radiais 1,3,6'),
        _spider('spider-hand-same', [2, 4, 3], 1, 2, ['r1_4'], ['r1_1'], 'movimento intramural'),
        _spider('spider-hand-cross', [3, 3, 2], 1, 2, ['r0_3'], ['r1_3'], 'movimento cruzado'),
        _spider(
            'spider-hand-mix', [4, 4, 3], 2, 2,
            ['r0_4', 'r1_4'], ['r0_2', 'r2_3'], 'um interno + um cruzado',
        ),
        _spider('spider-hand-cs', [3, 2, 1], 1, 2, ['c'], ['r0_3'], 'c em S'),
        _spider('spider-hand-ct', [3, 2, 1], 1, 2, ['r0_3'], ['c'], 'c em T'),
        _spider(
            'spider-hand-diam', [3, 2, 1], 1, 5,
            ['r0_3'], ['r1_2'], 'r=diam',
        ),
    ])

    out.append(_random_spider('spider-m-n16-m2-s42', 16, 3, 2, 42, 'micro'))
    out.append(_random_spider('spider-m-n16-m4-s43', 16, 4, 4, 43, 'micro'))
    out.append(_random_spider('spider-M-n24-k3-m2-s42', 24, 3, 2, 42, 'medium'))
    out.append(_random_spider('spider-M-n32-k4-m4-s42', 32, 4, 4, 42, 'medium'))

    ids = [x['id'] for x in out]
    if len(ids) != len(set(ids)):
        raise AssertionError('IDs duplicados no catálogo R11')
    if any(x['n'] > N_MEDIUM_MAX for x in out):
        raise AssertionError('catálogo excede n_medium_max')
    return out


def variantes_para(inst):
    if inst['familia'] == 'path':
        return ['path-alg1']
    if inst['familia'] == 'cycle':
        return ['cycle-alg2']
    if inst['familia'] == 'spider':
        return ['spider-A', 'spider-B', 'spider-U']
    raise ValueError(inst['familia'])
