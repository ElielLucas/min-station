#!/usr/bin/env python3
"""R11c — verificações pós-lote dos contraexemplos mínimos.

Não faz parte do lote oficial e não altera ``r11-certificadores.csv``.
Serve apenas para reproduzir as reduções documentadas em
``auditoria-r11-divergencias.md`` usando o validador independente.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from independent_validator import opt_por_enumeracao, viavel
from path_cycle import (
    certificar_cycle,
    certificar_path,
    construir_cycle,
    construir_path,
)
from r11_catalog import catalogo_oficial
from spider import certificar_spider


def _check_path_minimo():
    S, T, V, adj, _arestas, r = construir_path(2, ['v0'], ['v1'], 1)
    res = certificar_path(S, T, V, adj, r)
    opt = opt_por_enumeracao(S, T, V, adj, r)
    feasible = viavel(S, T, V, adj, r, res['C'])

    assert res['status'] == 'ok', res
    assert res['C'] == ['v0'], res
    assert res['obj'] == 1, res
    assert feasible is True
    assert opt == 0, opt
    print('ok: path-min-n2-r1 -> alg=1, feasible=True, opt=0')


def _check_cycle_minimo():
    S, T, V, adj, _arestas, r = construir_cycle(3, ['v0'], ['v1'], 1)
    res = certificar_cycle(S, T, V, adj, r)
    opt = opt_por_enumeracao(S, T, V, adj, r)
    feasible = viavel(S, T, V, adj, r, res['C'])

    assert res['status'] == 'ok', res
    assert res['obj'] == 1, res
    assert feasible is True
    assert opt == 0, opt
    print('ok: cycle-min-n3-r1 -> alg=1, feasible=True, opt=0')


def _check_spider_r2():
    inst = next(x for x in catalogo_oficial() if x['id'] == 'spider-reading-02')
    opt = opt_por_enumeracao(
        inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'],
    )
    assert opt == 2, opt

    esperado = {
        'spider-A': (1, False),
        'spider-B': (3, True),
        'spider-U': (1, False),
    }
    for variant, (obj, feasible_expected) in esperado.items():
        res = certificar_spider(
            inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'], variant,
        )
        assert res['status'] == 'ok', (variant, res)
        feasible = viavel(
            inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'], res['C'],
        )
        assert res['obj'] == obj, (variant, res)
        assert feasible is feasible_expected, (variant, feasible, res)
        print(
            f'ok: spider-reading-02 {variant} -> '
            f'alg={obj}, feasible={feasible}, opt=2'
        )


def main():
    _check_path_minimo()
    _check_cycle_minimo()
    _check_spider_r2()
    print('ok: verify_r11_counterexamples')


if __name__ == '__main__':
    main()
