#!/usr/bin/env python3
"""Verificação local da implementação R11 antes do lote oficial.

Não produz o CSV oficial. Divergências já pré-identificadas nas leituras são
assertadas como comportamento esperado do certificador literal, não reparadas.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from independent_validator import opt_por_enumeracao, viavel
from path_cycle import certificar_cycle, certificar_path, construir_cycle, construir_path
from spider import certificar_spider, construir_spider, decompor_spider


def _contract(res):
    assert res['status'] in {'ok', 'unspecified', 'invalid_input'}, res
    assert {'status', 'C', 'obj', 'variant', 'notes'} <= set(res), res
    if res['status'] == 'ok':
        assert res['obj'] == len(res['C']), res
    else:
        assert res['obj'] is None, res


def _path_case(n, S, T, r):
    S, T, V, adj, _e, r = construir_path(n, S, T, r)
    res = certificar_path(S, T, V, adj, r)
    _contract(res)
    return S, T, V, adj, r, res


def _cycle_case(n, S, T, r):
    S, T, V, adj, _e, r = construir_cycle(n, S, T, r)
    res = certificar_cycle(S, T, V, adj, r)
    _contract(res)
    return S, T, V, adj, r, res


def _spider_case(lengths, S, T, r, variant):
    S, T, V, adj, _e, r, _c = construir_spider(lengths, S, T, r)
    res = certificar_spider(S, T, V, adj, r, variant)
    _contract(res)
    return S, T, V, adj, r, res


def verificar_paths():
    # VP-OPT0 / PATH-05: divergência literal conhecida de VAL-A2.
    S, T, V, adj, r, res = _path_case(3, ['v0'], ['v2'], 2)
    assert res['C'] == ['v1'], res
    assert viavel(S, T, V, adj, r, [])
    assert opt_por_enumeracao(S, T, V, adj, r) == 0
    assert viavel(S, T, V, adj, r, res['C'])

    # Uma estação na definição; Algorithm 1 pode supercontar e isso é observado.
    S, T, V, adj, r, res = _path_case(4, ['v0'], ['v3'], 2)
    assert viavel(S, T, V, adj, r, res['C'])
    assert opt_por_enumeracao(S, T, V, adj, r) == 1

    # Permanência total.
    S, T, V, adj, r, res = _path_case(5, ['v2'], ['v2'], 2)
    assert res['C'] == [] and viavel(S, T, V, adj, r, res['C'])

    # Dois if independentes em S∩T.
    S, T, V, adj, r, res = _path_case(5, ['v0', 'v2'], ['v2', 'v4'], 2)
    assert res['status'] == 'ok'

    # Interseção não força permanência do robô que está no vértice comum.
    S, T, V, adj, r, res = _path_case(5, ['v0', 'v1'], ['v1', 'v4'], 1)
    assert res['status'] == 'ok'

    # r >= diâmetro: referência OPT 0; o literal é apenas observado.
    S, T, V, adj, r, res = _path_case(8, ['v0'], ['v7'], 7)
    assert opt_por_enumeracao(S, T, V, adj, r) == 0


def verificar_cycles():
    S, T, V, adj, r, res = _cycle_case(3, ['v0'], ['v1'], 2)
    assert res['status'] == 'ok'
    assert opt_por_enumeracao(S, T, V, adj, r) == 0

    # VC-BREAKS: o notes deve preservar os n resultados e a última quebra vencedora.
    S, T, V, adj, r, res = _cycle_case(6, ['v0', 'v3'], ['v2', 'v5'], 1)
    assert 'break_sizes=' in res['notes'] and 'break_winner=' in res['notes']
    tamanhos = res['notes'].split('break_sizes=', 1)[1].split(';', 1)[0].split(',')
    assert len(set(tamanhos)) > 1, res

    S, T, V, adj, r, res = _cycle_case(6, ['v0', 'v2'], ['v2', 'v4'], 1)
    assert res['status'] == 'ok'

    S, T, V, adj, r, res = _cycle_case(6, ['v0', 'v3'], ['v0', 'v3'], 1)
    assert res['C'] == [], res


def verificar_spiders():
    # Classe mínima e decomposição: cada folha adjacente é radial de um vértice.
    S, T, V, adj, r, _res = _spider_case([1, 1, 1], ['r0_1'], ['r1_1'], 1, 'spider-A')
    dec = decompor_spider(V, adj)
    assert dec is not None and [len(x) for x in dec[1]] == [1, 1, 1]

    # SP-R2: a leitura literal A coloca apenas o centro e o conjunto é inviável.
    S, T, V, adj, r, res = _spider_case([1, 5, 1], ['r0_1'], ['r1_5'], 2, 'spider-A')
    assert set(res['C']) == {'c'}, res
    assert not viavel(S, T, V, adj, r, res['C'])
    assert opt_por_enumeracao(S, T, V, adj, r) == 2

    # B é uma costura distinta e não deve ser silenciosamente igualada a A.
    _S, _T, _V, _adj, _r, res_b = _spider_case([1, 5, 1], ['r0_1'], ['r1_5'], 2, 'spider-B')
    assert res_b['variant'] == 'spider-B'

    # SP-R4: KEEP em A; silêncio conservador em U.
    args = ([2, 2, 1], ['c', 'r0_2'], ['c', 'r1_2'], 2)
    *_x, res_a = _spider_case(*args, 'spider-A')
    *_x, res_u = _spider_case(*args, 'spider-U')
    assert res_a['status'] == 'ok'
    assert res_u['status'] == 'unspecified' and 'SP-R4' in res_u['notes']

    # SP-R5: A aceita r'=0; U não inventa comportamento.
    args = ([1, 3, 1], ['r0_1'], ['r1_3'], 1)
    *_x, res_a = _spider_case(*args, 'spider-A')
    *_x, res_u = _spider_case(*args, 'spider-U')
    assert res_a['status'] == 'ok'
    assert res_u['status'] == 'unspecified' and 'SP-R5' in res_u['notes']

    # INT-A não fecha radial mista desbalanceada: deve dizer unspecified.
    *_x, res = _spider_case(
        [4, 4, 4],
        ['r0_4', 'r1_4', 'r2_4'],
        ['r0_2', 'r2_2', 'r2_1'],
        2,
        'spider-A',
    )
    assert res['status'] == 'unspecified' and 'INT-A' in res['notes']


def main():
    verificar_paths()
    verificar_cycles()
    verificar_spiders()
    print('ok: verify_r11')


if __name__ == '__main__':
    main()
