#!/usr/bin/env python3
"""T12: determinismo, Apêndice B e acordo entre enumeração e modelo base."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import bp
from independent_validator import avisar_se_desconexo, opt_por_enumeracao, viavel
from io_instancia import texto_instancia
from medir import lp_com_cortes, nucleo, otimo_base

PASTA = RAIZ / 'instances' / 'estrutural' / 'bp'
CASOS = [
    ([1, 1, 2], 2, 2, 'sim', 8, 8),
    ([2, 2, 1, 1], 2, 3, 'sim', 10, 10),
    ([3, 1], 2, 2, 'nao', 6, 7),
    ([2, 2, 2], 2, 3, 'nao', 8, 9),
]


def _enum_ate(S, T, V, adj, r, teto):
    from itertools import combinations
    vertices = list(V)
    for k in range(teto + 1):
        for C in combinations(vertices, k):
            if viavel(S, T, vertices, adj, r, C):
                return k
    return None


def main():
    falhas = []
    for items, q, B, rotulo, lb, opt in CASOS:
        cert = bp.particao_exata(items, q, B)
        if rotulo == 'sim' and cert is None:
            falhas.append(f'{items}: DP não achou partição')
        if rotulo == 'nao' and cert is not None:
            falhas.append(f'{items}: DP achou partição indevida')
        origem = 'plantio' if rotulo == 'sim' else 'dp-bin-packing'
        texto_cert = str(cert) if cert is not None else 'inexistente'
        a = bp.emitir(PASTA, items, q, B, 0, rotulo, texto_cert, origem)
        b = bp.emitir(PASTA, items, q, B, 0, rotulo, texto_cert, origem)
        if a['sha256'] != b['sha256']:
            falhas.append(f'{items}: sha divergente')
        S, T, V, arestas, r = a['S'], a['T'], a['V'], a['arestas'], a['r']
        adj = {u: [] for u in V}
        for u, v in arestas:
            adj.setdefault(u, []).append((v, 1))
            adj.setdefault(v, []).append((u, 1))
        if set(S) & set(T) or len(S) != len(T):
            falhas.append(f'{items}: fidelidade')
        avisar_se_desconexo(V, adj, S, T)
        base = otimo_base(S, T, V, adj, r)
        nuc = nucleo(S, T, V, adj, r)
        lp, counts = lp_com_cortes(S, T, V, adj, r, {'C1', 'C2', 'C4'})
        zlp, _ = lp_com_cortes(S, T, V, adj, r, set())
        if abs(base - opt) > 1e-6 or abs(nuc - lb) > 1e-6 or abs(lp - lb) > 1e-6 or abs(zlp - 3) > 1e-6:
            falhas.append(
                f'{items}: base={base} nucleo={nuc} lp={lp} zlp={zlp} esperado opt={opt} lb={lb}'
            )
        if len(V) <= 16:
            enumerado = opt_por_enumeracao(S, T, V, adj, r)
            if enumerado != int(base):
                falhas.append(f'{items}: enumeração {enumerado} != base {base}')
        elif rotulo == 'sim' and cert is not None:
            C = [f'u{i}' for i in range(len(items))]
            C += [f'v{j}' for j in range(q)]
            for j, membros in enumerate(cert):
                for i in membros:
                    C.append(f'c{i}_{j}')
            if len(C) != lb or not viavel(S, T, V, adj, r, C):
                falhas.append(f'{items}: certificado plantado não é solução de tamanho {lb}')
        print(f'{items} {rotulo}: |V|={len(V)} m={len(S)} opt={base} lp={lp} nucleo={nuc} C1={counts["C1"]}')
    bruto_a = texto_instancia(['s'], ['t'], ['s', 't', 'u'], [('s', 'u'), ('u', 't')], 1, {'familia': 'bp'})
    bruto_b = texto_instancia(['s'], ['t'], ['s', 't', 'u'], [('s', 'u'), ('u', 't')], 1, {'familia': 'bp'})
    if bruto_a != bruto_b:
        falhas.append('texto não determinístico')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
