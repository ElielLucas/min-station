#!/usr/bin/env python3
"""T17: fórmula do ótimo, contagem de ótimos do núcleo, variante com degrau."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import tr
from independent_validator import viavel
from medir import otimo_base, otimos_do_nucleo

PASTA = RAIZ / 'instances' / 'estrutural' / 'tr'
# k, L, r, n_otimos_esperados, n_viaveis_esperados
CASOS = [(2, 5, 2, 8, 2), (3, 5, 2, 27, 3)]


def _adj(V, arestas):
    adj = {u: [] for u in V}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def main():
    falhas = []
    for k, L, r, n_opt, n_via in CASOS:
        a = tr.emitir(PASTA, k, L, r, None)
        b = tr.emitir(PASTA, k, L, r, None)
        if a['sha256'] != b['sha256']:
            falhas.append(f'k={k}: sha divergente')
        adj = _adj(a['V'], a['arestas'])
        formula = tr.opt_formula(L, r)
        base = otimo_base(a['S'], a['T'], a['V'], adj, r)
        opt, achados = otimos_do_nucleo(a['S'], a['T'], a['V'], adj, r)
        if achados is None:
            falhas.append(f'k={k}: pool truncado')
            continue
        viaveis = [C for C in achados if viavel(a['S'], a['T'], a['V'], adj, r, C)]
        print(
            f'TR k={k} L={L} r={r}: |V|={len(a["V"])} formula={formula} base={base} '
            f'nucleo={opt} otimos={len(achados)} viaveis={len(viaveis)}'
        )
        if abs(base - formula) > 1e-6 or abs(opt - formula) > 1e-6:
            falhas.append(f'k={k}: base={base} nucleo={opt} formula={formula}')
        if len(achados) != n_opt or len(viaveis) != n_via:
            falhas.append(
                f'k={k}: contagem {len(achados)} otimos / {len(viaveis)} viáveis, '
                f'Apêndice B pede {n_opt}/{n_via}'
            )
        degrau = tr.emitir(PASTA, k, L, r, sigma=r)
        if degrau['sha256'] == a['sha256']:
            falhas.append(f'k={k}: degrau σ=r gerou o mesmo arquivo que σ=∞')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
