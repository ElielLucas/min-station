#!/usr/bin/env python3
"""T13: Apêndice B, C1 e C2 vazios, enumeração no menor bolsão, determinismo."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import hb
from independent_validator import avisar_se_desconexo, opt_por_enumeracao
from io_instancia import texto_instancia
from medir import lp_com_cortes, nucleo, otimo_base

PASTA = RAIZ / 'instances' / 'estrutural' / 'hb'
# q, ndir, p, |V|, m, OPT, z_LP, LP com cortes, núcleo
CASOS = [
    (4, 2, 1, 16, 6, 2, 0.333, 1.000, 1),
    (5, 2, 1, 21, 8, 3, 0.375, 1.083, 1),
    (6, 1, 1, 28, 11, 3, 0.455, 1.291, 1),
    (8, 1, 1, 38, 15, 3, 0.467, 1.343, 1),
    (6, 1, 2, 25, 11, 3, 0.455, 1.273, 1),
]


def _adj(V, arestas):
    adj = {u: [] for u in V}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def main():
    falhas = []
    for q, ndir, p, n, m, opt, zlp, lp_esp, nuc_esp in CASOS:
        a = hb.emitir(PASTA, q, ndir, p)
        b = hb.emitir(PASTA, q, ndir, p)
        if a['sha256'] != b['sha256']:
            falhas.append(f'q={q} p={p}: sha divergente')
        if len(a['V']) != n or len(a['S']) != m:
            falhas.append(f'q={q} p={p}: |V|={len(a["V"])} m={len(a["S"])}')
        adj = _adj(a['V'], a['arestas'])
        avisar_se_desconexo(a['V'], adj, a['S'], a['T'])
        base = otimo_base(a['S'], a['T'], a['V'], adj, 1)
        nuc = nucleo(a['S'], a['T'], a['V'], adj, 1)
        lp, counts = lp_com_cortes(a['S'], a['T'], a['V'], adj, 1, {'C1', 'C2', 'C4'})
        puro, _ = lp_com_cortes(a['S'], a['T'], a['V'], adj, 1, set())
        if counts['C1'] or counts['C2']:
            falhas.append(f'q={q} p={p}: C1={counts["C1"]} C2={counts["C2"]}')
        if abs(base - opt) > 1e-6 or abs(nuc - nuc_esp) > 1e-6:
            falhas.append(f'q={q} p={p}: opt={base} nucleo={nuc}')
        if abs(puro - zlp) > 0.002 or abs(lp - lp_esp) > 0.002:
            falhas.append(f'q={q} p={p}: zlp={puro} lp={lp}')
        enumerado = opt_por_enumeracao(a['S'], a['T'], a['V'], adj, 1)
        if enumerado != int(base):
            falhas.append(f'q={q} p={p}: enumeração {enumerado} != base {base}')
        print(f'q={q} ndir={ndir} p={p}: opt={base} zlp={puro:.3f} lp={lp:.3f} nucleo={nuc} C4={counts["C4"]}')
    meta = {'familia': 'hb'}
    if texto_instancia(['s'], ['t'], ['s', 't'], [('s', 't')], 1, meta) != texto_instancia(
        ['s'], ['t'], ['s', 't'], [('s', 't')], 1, meta
    ):
        falhas.append('texto não determinístico')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
