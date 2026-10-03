#!/usr/bin/env python3
"""T14: validade do C6 em casos enumerados, controle negativo em BP, LB em HB.

A previsão (LB ≈ 1 por bolsão, OPT = 3) está em
docs/technical/reference/c6-hall-primeiro-salto.md e foi escrita antes desta
medição. Corte inválido interrompe antes de medir o LB.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

from gurobipy import GRB, quicksum

import bp
import hb
from baseline import construir_modelo_baseline
from cuts import corte_ponderado_valido, generate_C6, build_neighborhoods
from medir import lp_com_cortes
from ms_utils import construir_arcos_alcance


def _adj(V, arestas):
    adj = {u: [] for u in V}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def _cortes(S, T, V, adj, r):
    A = construir_arcos_alcance(V, adj, r)
    N_plus, N_minus = build_neighborhoods(A)
    return generate_C6(S, T, N_plus, N_minus), A


def _minimo_base(S, T, V, adj, r, termos):
    A = construir_arcos_alcance(V, adj, r)
    modelo, y, _f, _na, _nv = construir_modelo_baseline(S, T, V, A)
    modelo.Params.OutputFlag = 0
    modelo.Params.Threads = 1
    modelo.Params.Seed = 42
    modelo.setObjective(quicksum(coef * y[v] for v, coef in termos if v in y), GRB.MINIMIZE)
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(f'minimo ponderado status {modelo.Status}')
    valor = float(modelo.ObjVal)
    modelo.dispose()
    return valor


def _validar(rotulo, S, T, V, adj, r, cortes, exigir_enumeracao):
    invalidos = []
    for termos, rhs in cortes:
        if exigir_enumeracao and len(termos) <= 22:
            if not corte_ponderado_valido(S, T, V, adj, r, termos, rhs):
                invalidos.append((termos, rhs, 'enumeração'))
                continue
        minimo = _minimo_base(S, T, V, adj, r, termos)
        if minimo < rhs - 1e-6:
            invalidos.append((termos, rhs, f'base {minimo}'))
    if invalidos:
        print(f'{rotulo}: {len(invalidos)} cortes inválidos; medição interrompida')
        for item in invalidos[:5]:
            print(' ', item[2], 'rhs', item[1], 'termos', item[0][:8])
        raise SystemExit(1)
    print(f'{rotulo}: {len(cortes)} cortes válidos')


def main():
    S, T, V, adj, arestas, r, _delta = hb.construir(4, 2, 1)
    (cortes, _inc), _A = _cortes(S, T, V, adj, r)
    _validar('HB q=4', S, T, V, adj, r, cortes, True)

    S, T, V, adj, arestas, r, _delta = hb.construir(6, 1, 1)
    (cortes, inc), _A = _cortes(S, T, V, adj, r)
    if inc:
        raise SystemExit(f'HB q=6 enumeração incompleta: {inc}')
    alvo = [c for c in cortes if c[1] == 5]
    if not alvo:
        raise SystemExit('HB q=6 não gerou desigualdade com δ=5')
    _validar('HB q=6 δ=5', S, T, V, adj, r, alvo, True)

    items, q, B = [3, 1], 2, 2
    S, T, V, adj, arestas, r = bp.construir(items, q, B)
    (cortes, _inc), _A = _cortes(S, T, V, adj, r)
    _validar('BP [3,1] controle', S, T, V, adj, r, cortes, True)

    print('validação fechada; medição do LB em HB')
    for q, ndir, p, opt in [(4, 2, 1, 2), (6, 1, 1, 3), (6, 1, 2, 3), (8, 1, 1, 3)]:
        S, T, V, adj, arestas, r, delta = hb.construir(q, ndir, p)
        lp, counts = lp_com_cortes(S, T, V, adj, r, {'C1', 'C2', 'C4', 'C6'})
        fecha = lp >= opt - 1e-6
        leitura = 'REFUTADO' if fecha else 'gap aberto, compatível com LB ≈ 1'
        print(
            f'HB q={q} ndir={ndir} p={p}: LP+C6={lp:.4f} OPT={opt} '
            f'cortes={counts["C6"]} incompletas={counts["C6_incompletas"]} {leitura}'
        )


if __name__ == '__main__':
    main()
