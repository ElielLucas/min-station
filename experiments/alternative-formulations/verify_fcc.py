#!/usr/bin/env python3
"""Cruzamento P1 e P7 da spec B: F-CC vs viavel; qij vs forma separada."""

import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

from fcc import enumerar_conexos, lp_fcc, fcc_y_viavel
from independent_validator import viavel
from synthetic import (
    make_CaminhoABC,
    make_Direct0,
    make_SharedTerminal,
    make_StayPut,
    make_StayPutIsolado,
    make_TermRelay,
)


def _checa_enumerador():
    # triângulo: 7 subconjuntos conexos não vazios
    V = ['a', 'b', 'c']
    neigh = {'a': {'b', 'c'}, 'b': {'a', 'c'}, 'c': {'a', 'b'}}
    Ws, trunc = enumerar_conexos(neigh, V, 100)
    if trunc or len(Ws) != 7:
        raise AssertionError(f'triângulo: {len(Ws)} conjuntos, trunc={trunc}')
    # caminho a-b-c: 6 conexos (não {a,c})
    neigh = {'a': {'b'}, 'b': {'a', 'c'}, 'c': {'b'}}
    Ws, trunc = enumerar_conexos(neigh, V, 100)
    got = {frozenset(W) for W in Ws}
    esperado = {
        frozenset(['a']), frozenset(['b']), frozenset(['c']),
        frozenset(['a', 'b']), frozenset(['b', 'c']),
        frozenset(['a', 'b', 'c']),
    }
    if trunc or got != esperado:
        raise AssertionError(f'caminho: {got}')


def _p1(nome, S, T, V, adj, A_r, r):
    falhas = []
    verts = list(V)
    for k in range(len(verts) + 1):
        for C in combinations(verts, k):
            valido = viavel(S, T, verts, adj, r, C)
            modelo = fcc_y_viavel(S, T, V, A_r, C, forma='qij', max_W=200000)
            if valido != modelo:
                falhas.append(f'{nome} C={C}: viavel={valido} fcc={modelo}')
    return falhas


def _p7(nome, S, T, V, A_r):
    z_q, _ = lp_fcc(S, T, V, A_r, forma='qij')
    z_s, _ = lp_fcc(S, T, V, A_r, forma='separada')
    if abs(z_q - z_s) > 1e-6:
        return [f'{nome}: qij={z_q} separada={z_s}']
    return []


def main():
    _checa_enumerador()
    falhas = []
    fabricas = (
        make_StayPutIsolado,
        make_StayPut,
        make_CaminhoABC,
        make_Direct0,
        make_TermRelay,
        make_SharedTerminal,
    )
    for fab in fabricas:
        S, T, V, adj, A_r, r, meta = fab()
        nome = meta['name']
        print(f'P1+P7 {nome} n={len(V)}')
        falhas.extend(_p1(nome, S, T, V, adj, A_r, r))
        falhas.extend(_p7(nome, S, T, V, A_r))
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
