#!/usr/bin/env python3
"""T15: SC-GF2 no Apêndice B, gêmeo rígido, classes_wl e tempo de montagem em k=5."""

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'src' / 'converters'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import networkx as nx

import sc
from independent_validator import opt_por_enumeracao
from instance_features import _classes_refinamento
from medir import lp_com_cortes, nucleo, otimo_base

PASTA = RAIZ / 'instances' / 'estrutural' / 'sc'
# k, |V|, m, OPT, LP+C1
CASOS = [(3, 21, 7, 3, 1.75), (4, 45, 15, 4, 1.875)]


def _adj(V, arestas):
    adj = {u: [] for u in V}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def _wl(V, arestas, S, T):
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(arestas)
    return _classes_refinamento(G, set(S), set(T))


def _wl_individualizado(V, arestas, S, T):
    """1-WL depois de pendurar um vértice privado em cada estação w.

    classes_wl puro colapsa em 3 para qualquer sistema com as mesmas margens,
    porque S, T e W são as únicas cores estáveis. A individualização é a
    medida equivalente que enxerga a quebra de transitividade.
    """
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(arestas)
    contagens = []
    for w in V:
        if not str(w).startswith('w'):
            continue
        Gd = G.copy()
        pin = f'pin-{w}'
        Gd.add_node(pin)
        Gd.add_edge(w, pin)
        contagens.append(_classes_refinamento(Gd, set(S), set(T)))
    return min(contagens), max(contagens)


def _margens(elems, conjuntos, k):
    n = len(elems)
    esperado = 1 << (k - 1)
    if any(len(c) != esperado for c in conjuntos):
        return False
    grau = {x: 0 for x in elems}
    for c in conjuntos:
        for x in c:
            grau[x] += 1
    return len(conjuntos) == n and all(g == esperado for g in grau.values())


def main():
    falhas = []
    for k, n, m, opt, lp_esp in CASOS:
        a = sc.emitir(PASTA, k, 0, rigido=False)
        b = sc.emitir(PASTA, k, 0, rigido=False)
        if a['sha256'] != b['sha256']:
            falhas.append(f'k={k}: sha divergente')
        if len(a['V']) != n or len(a['S']) != m:
            falhas.append(f'k={k}: |V|={len(a["V"])} m={len(a["S"])}')
        if not _margens(a['elems'], a['conjuntos'], k):
            falhas.append(f'k={k}: margens do GF2')
        adj = _adj(a['V'], a['arestas'])
        base = otimo_base(a['S'], a['T'], a['V'], adj, 1)
        nuc = nucleo(a['S'], a['T'], a['V'], adj, 1)
        lp, counts = lp_com_cortes(a['S'], a['T'], a['V'], adj, 1, {'C1'})
        if abs(base - opt) > 1e-6 or abs(lp - lp_esp) > 1e-6 or abs(nuc - opt) > 1e-6:
            falhas.append(f'k={k}: base={base} lp={lp} nucleo={nuc}')
        if k <= 3:
            enumerado = opt_por_enumeracao(a['S'], a['T'], a['V'], adj, 1)
            if enumerado != opt:
                falhas.append(f'k={k}: enumeração {enumerado}')
        print(f'GF2 k={k}: opt={base} lpC1={lp:.4f} nucleo={nuc} C1={counts["C1"]} wl={_wl(a["V"], a["arestas"], a["S"], a["T"])}')

    for k in (3, 4):
        gf = sc.emitir(PASTA, k, 0, rigido=False)
        wl_gf = _wl(gf['V'], gf['arestas'], gf['S'], gf['T'])
        ind_gf, _ = _wl_individualizado(gf['V'], gf['arestas'], gf['S'], gf['T'])
        for seed in (0, 1):
            tw = sc.emitir(PASTA, k, seed, rigido=True)
            outro = sc.emitir(PASTA, k, seed, rigido=True)
            if tw['sha256'] != outro['sha256']:
                falhas.append(f'gêmeo k={k} s={seed}: sha divergente')
            if not _margens(tw['elems'], tw['conjuntos'], k):
                falhas.append(f'gêmeo k={k} s={seed}: margens')
            if tw['certificado'] != sc.opt_set_cover(tw['elems'], tw['conjuntos']):
                falhas.append(f'gêmeo k={k} s={seed}: IP divergiu de si mesmo')
            wl = _wl(tw['V'], tw['arestas'], tw['S'], tw['T'])
            ind, ind_max = _wl_individualizado(tw['V'], tw['arestas'], tw['S'], tw['T'])
            separa = ind > ind_gf
            print(
                f'gêmeo k={k} s={seed}: OPT_cover={tw["certificado"]} '
                f'wl={wl} wl_gf2={wl_gf} ind={ind}..{ind_max} ind_gf2={ind_gf} separa={separa}'
            )
            if wl != wl_gf:
                falhas.append(f'gêmeo k={k} s={seed}: classes_wl puro mudou ({wl} != {wl_gf})')
            if not separa:
                falhas.append(
                    f'gêmeo k={k} s={seed}: individualização não separa (ind {ind} <= {ind_gf})'
                )

    t0 = time.monotonic()
    S, T, V, adj, arestas, r, _e, _c = sc.construir_gf2(5)
    dt = time.monotonic() - t0
    print(f'GF2 k=5: montagem {dt:.3f}s |V|={len(V)} arestas={len(arestas)}')
    if dt > 30:
        falhas.append(f'montagem k=5 lenta: {dt:.1f}s')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
