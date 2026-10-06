#!/usr/bin/env python3
"""F3: LP da F-CC contra base, cortes e núcleo. Pré-registro em pre-registro-f3.md.

Não mede F-C3. Não altera caps depois de ver valores.
"""

import csv
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'structural'))

from gurobipy import GRB, Model, quicksum

from fcc import CapExceeded, enumerar_conexos, grafo_H, lp_fcc
from harness import measure_lp, prepare_cuts
from independent_validator import opt_por_enumeracao
from medir import nucleo, otimo_base
from ms_utils import construir_arcos_alcance
from synthetic import (
    make_CaminhoABC,
    make_Direct0,
    make_F1,
    make_F2,
    make_Sec59,
    make_SharedTerminal,
    make_StayPut,
    make_StayPutIsolado,
    make_TermRelay,
    make_TermRelayForced,
    make_Tri,
)
import bp
import hb
import sc
import tr

# Caps congelados em pre-registro-f3.md
N_MAX = 21
MAX_W = 200000
N_OPT_ENUM = 16
SEED = 42
EPS = 1e-6

CSV_PATH = RAIZ / 'results' / 'alternative-formulations' / 'f3-fcc.csv'


def _lp_set_cover(elems, conjuntos):
    modelo = Model('sc-lp')
    modelo.Params.OutputFlag = 0
    modelo.Params.Seed = SEED
    modelo.Params.Threads = 1
    y = [modelo.addVar(lb=0.0) for _ in conjuntos]
    modelo.setObjective(quicksum(y), GRB.MINIMIZE)
    for x in elems:
        modelo.addConstr(
            quicksum(y[j] for j, conj in enumerate(conjuntos) if x in conj) >= 1
        )
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        modelo.dispose()
        raise RuntimeError(f'set-cover LP status {modelo.Status}')
    val = float(modelo.ObjVal)
    modelo.dispose()
    return val


def _excluidas_pre():
    return [
        {'nome': 'HB q=6 ndir=1 p=1', 'tipo': 'hb', 'motivo': 'n=28 > n_max=21'},
        {'nome': 'HB q=8 ndir=1 p=1', 'tipo': 'hb', 'motivo': 'n=38 > n_max=21'},
        {'nome': 'HB q=6 ndir=1 p=2', 'tipo': 'hb', 'motivo': 'n=25 > n_max=21'},
        {'nome': 'BP-[2,2,2] q=2', 'tipo': 'bp-nao', 'motivo': 'n=23 > n_max=21'},
        {'nome': 'TR k=3 L=5', 'tipo': 'tr', 'motivo': 'n=25 > n_max=21'},
        {'nome': 'SC-GF2 k=4', 'tipo': 'sc-gf2', 'motivo': 'n=45 > n_max=21'},
        {'nome': 'F1(k=3)', 'tipo': 'f1', 'motivo': 'n=17, não está no conjunto medido'},
        {'nome': 'F2(k=2)', 'tipo': 'f2', 'motivo': 'n=17, não está no conjunto medido'},
        {'nome': 'familia-20/15 F-C3', 'tipo': 'fc3-claim', 'motivo': 'não reconstruível'},
        {'nome': 'aranhas Spec D', 'tipo': 'spider', 'motivo': 'Spec D indisponível'},
    ]


def _instancias():
    out = []

    def gadget(fab, tipo):
        S, T, V, adj, A_r, r, meta = fab()
        out.append({
            'nome': meta['name'], 'tipo': tipo, 'S': S, 'T': T, 'V': V,
            'adj': adj, 'A_r': A_r, 'r': r, 'sc': None,
        })

    gadget(make_Direct0, 'gadget')
    gadget(make_TermRelay, 'gadget')
    gadget(make_TermRelayForced, 'gadget')
    gadget(make_StayPut, 'gadget')
    gadget(make_StayPutIsolado, 'gadget')
    gadget(make_SharedTerminal, 'gadget')
    gadget(make_CaminhoABC, 'gadget')
    gadget(make_Tri, 'tri')
    gadget(lambda: make_F1(m=2, k=2, r=1), 'f1')
    gadget(lambda: make_F2(k=1, L=3, r=1), 'f2')
    gadget(lambda: make_Sec59(L=7, r=1), 'sec59')

    S, T, V, adj, _e, r, _d = hb.construir(4, 2, 1)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append({
        'nome': 'HB-q4-ndir2-p1', 'tipo': 'hb', 'S': S, 'T': T, 'V': V,
        'adj': adj, 'A_r': A_r, 'r': r, 'sc': None,
    })
    S, T, V, adj, _e, r, _d = hb.construir(5, 2, 1)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append({
        'nome': 'HB-q5-ndir2-p1', 'tipo': 'hb', 'S': S, 'T': T, 'V': V,
        'adj': adj, 'A_r': A_r, 'r': r, 'sc': None,
    })

    S, T, V, adj, _e, r = bp.construir([3, 1], 2, 2)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append({
        'nome': 'BP-nao-[3,1]-q2', 'tipo': 'bp-nao', 'S': S, 'T': T, 'V': V,
        'adj': adj, 'A_r': A_r, 'r': r, 'sc': None,
    })

    S, T, V, adj, _e, r, _c = tr.construir(2, 5, 2, None, m=2)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append({
        'nome': 'TR-k2-L5-r2', 'tipo': 'tr', 'S': S, 'T': T, 'V': V,
        'adj': adj, 'A_r': A_r, 'r': r, 'sc': None,
    })

    S, T, V, adj, _e, r, elems, conjuntos = sc.construir_gf2(3)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append({
        'nome': 'SC-GF2-k3', 'tipo': 'sc-gf2', 'S': S, 'T': T, 'V': V,
        'adj': adj, 'A_r': A_r, 'r': r,
        'sc': (elems, conjuntos),
    })
    return out


def medir(inst):
    S, T, V, adj, A_r, r = inst['S'], inst['T'], inst['V'], inst['adj'], inst['A_r'], inst['r']
    n = len(V)
    linha = {
        'nome': inst['nome'],
        'tipo': inst['tipo'],
        'n': n,
        'm': len(S),
        'r': r,
        'lp_base': '',
        'lp_c1c2c4': '',
        'nucleo': '',
        'lp_fcc': '',
        'lp_fc3': 'OPEN',
        'opt': '',
        'fonte_opt': '',
        'gamma': '',
        'n_W': '',
        'lp_setcover': '',
        'status': '',
        'motivo': '',
    }
    if n > N_MAX:
        linha['status'] = 'excluida'
        linha['motivo'] = f'n={n} > n_max={N_MAX}'
        return linha

    neigh = grafo_H(V, A_r)
    Ws, _t = enumerar_conexos(neigh, V, MAX_W + 1)
    nW = len(Ws)
    linha['n_W'] = nW
    fcc_cap = nW > MAX_W

    res0 = measure_lp(S, T, V, A_r, 'cont', [], seed=SEED, threads=1)
    cortes, _c = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    res1 = measure_lp(S, T, V, A_r, 'cont', cortes, seed=SEED, threads=1)
    nuc = nucleo(S, T, V, adj, r)
    linha['lp_base'] = res0['lp_bound']
    linha['lp_c1c2c4'] = res1['lp_bound']
    linha['nucleo'] = nuc

    if n <= N_OPT_ENUM:
        opt = opt_por_enumeracao(S, T, V, adj, r)
        fonte = 'enum'
    else:
        opt = otimo_base(S, T, V, adj, r)
        fonte = 'mip_base'
    linha['opt'] = opt
    linha['fonte_opt'] = fonte
    linha['gamma'] = (opt - nuc) if opt is not None else ''

    if inst['sc'] is not None:
        linha['lp_setcover'] = _lp_set_cover(*inst['sc'])

    if fcc_cap:
        linha['status'] = 'excluida'
        linha['motivo'] = f'|W|={nW} > max_W={MAX_W}'
        return linha

    try:
        z, meta = lp_fcc(S, T, V, A_r, forma='separada', max_W=MAX_W, seed=SEED, threads=1)
        linha['lp_fcc'] = z
        linha['n_W'] = meta['n_W']
        linha['status'] = 'ok'
    except CapExceeded as e:
        linha['status'] = 'excluida'
        linha['motivo'] = str(e)
        return linha

    if linha['lp_fcc'] != '' and linha['lp_fcc'] + EPS < linha['lp_base']:
        linha['status'] = 'P2_REFUTADO'
        linha['motivo'] = f'LP F-CC {linha["lp_fcc"]} < LP base {linha["lp_base"]}'
    return linha


def main():
    os.environ.setdefault('PYTHONHASHSEED', '0')
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        'nome', 'tipo', 'n', 'm', 'r', 'lp_base', 'lp_c1c2c4', 'nucleo',
        'lp_fcc', 'lp_fc3', 'opt', 'fonte_opt', 'gamma', 'n_W',
        'lp_setcover', 'status', 'motivo',
    ]
    linhas = []
    for inst in _instancias():
        print('medir', inst['nome'], 'n=', len(inst['V']), flush=True)
        lin = medir(inst)
        print(' ', lin['status'], lin.get('lp_fcc'), 'opt', lin.get('opt'), lin.get('motivo'), flush=True)
        linhas.append(lin)
        if lin['status'] == 'P2_REFUTADO':
            break
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for lin in linhas:
            w.writerow({k: lin.get(k, '') for k in campos})
    print('csv', CSV_PATH)
    for ex in _excluidas_pre():
        print('excluida-pre', ex['nome'], ex['motivo'])
    if any(l['status'] == 'P2_REFUTADO' for l in linhas):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
