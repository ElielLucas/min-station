#!/usr/bin/env python3
"""R7 — anatomia do platô do núcleo. Sem CBI. Cap N=200.

Pré-registro: docs/technical/reference/pre-registro-r5.md
"""

import csv
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'structural'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'alternative-formulations'))

from gurobipy import GRB

import bp
import tr
from cuts import build_neighborhoods, integer_oracle
from fcc import B_de, grafo_H, pares_diretos
from harness import load_instance, prepare_cuts
from independent_validator import _emparelhamento, viavel
from ms_utils import construir_arcos_alcance
from yspace import _build_ymodel

N_CAP = 200
SAIDA = RAIZ / 'results' / 'benchmark' / 'r7-plato.csv'
RESUMO = RAIZ / 'results' / 'benchmark' / 'r7-plato-resumo.csv'
CAMPOS = [
    'instancia', 'idx', 'opt_core', 'n_estacoes', 'estacoes',
    'n_componentes', 'tamanhos_componentes', 'oracle_viavel', 'Z',
    'n_Z', 'validador_viavel', 'hdesc', 'n_origens_sem_par',
    'truncado_pool',
]


def componentes_H(C, neigh):
    Cset = list(C)
    visto = set()
    comps = []
    for v in Cset:
        if v in visto:
            continue
        fila = deque([v])
        visto.add(v)
        comp = []
        while fila:
            u = fila.popleft()
            comp.append(u)
            for w in neigh.get(u, ()):
                if w in C and w not in visto:
                    visto.add(w)
                    fila.append(w)
        comps.append(tuple(sorted(comp, key=str)))
    return comps


def matching_componentes(S, T, A_r, C, neigh):
    D = pares_diretos(S, T, A_r)
    alcance = {s: set() for s in S}
    for s, t in D:
        alcance[s].add(t)
    for K in componentes_H(C, neigh):
        BK = B_de(K, neigh)
        origens = [s for s in S if s in BK]
        destinos = [t for t in T if t in BK]
        for s in origens:
            alcance[s].update(destinos)
    casados = _emparelhamento(list(S), alcance)
    sem = [s for s in S if not alcance[s]]
    return casados == len(S), alcance, sem


def pool_nucleo(S, T, V, adj, A_r, r, teto):
    cortes, _ = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    modelo, y = _build_ymodel(
        V, cortes, integer=True, seed=42, threads=4, time_limit=600,
    )
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        st = modelo.Status
        modelo.dispose()
        raise RuntimeError(f'núcleo status {st}')
    opt = float(modelo.ObjVal)
    modelo.addConstr(modelo.getObjective() == opt)
    modelo.Params.PoolSolutions = teto
    modelo.Params.PoolSearchMode = 2
    modelo.optimize()
    achados = []
    for i in range(modelo.SolCount):
        modelo.Params.SolutionNumber = i
        C = tuple(v for v in V if y[v].Xn > 0.5)
        achados.append(C)
    trunc = modelo.SolCount >= teto
    modelo.dispose()
    # únicos
    vistos = []
    seen = set()
    for C in achados:
        key = frozenset(C)
        if key in seen:
            continue
        seen.add(key)
        vistos.append(C)
    return opt, vistos, trunc


def analisar(nome, S, T, V, adj, A_r, r):
    neigh = grafo_H(V, A_r)
    N_plus, _nm = build_neighborhoods(A_r)
    opt, Cs, trunc = pool_nucleo(S, T, V, adj, A_r, r, N_CAP)
    n = len(V)
    linhas = []
    z_elimina = defaultdict(int)
    n_hdesc = n_inf = n_feas = n_nao_hdesc = 0
    for i, C in enumerate(Cs):
        orc_ok, Z = integer_oracle(S, T, N_plus, C)
        val_ok = ''
        if n <= 16:
            val_ok = viavel(S, T, V, adj, r, C)
        match_ok, alcance, sem = matching_componentes(S, T, A_r, C, neigh)
        comps = componentes_H(C, neigh)
        inf = (not orc_ok) or (val_ok is False)
        if orc_ok and (val_ok is True or val_ok == ''):
            n_feas += 1
            hdesc = 0
        else:
            n_inf += 1
            hdesc = 1 if not match_ok else 0
            if hdesc:
                n_hdesc += 1
            else:
                n_nao_hdesc += 1
        if Z:
            z_elimina[frozenset(Z)] += 1
        linhas.append({
            'instancia': nome,
            'idx': i,
            'opt_core': opt,
            'n_estacoes': len(C),
            'estacoes': ' '.join(str(v) for v in C),
            'n_componentes': len(comps),
            'tamanhos_componentes': ','.join(str(len(k)) for k in comps),
            'oracle_viavel': int(orc_ok),
            'Z': ' '.join(sorted(map(str, Z))) if Z else '',
            'n_Z': len(Z) if Z else 0,
            'validador_viavel': val_ok if val_ok != '' else '',
            'hdesc': hdesc,
            'n_origens_sem_par': len(sem),
            'truncado_pool': int(trunc),
        })
    return linhas, {
        'instancia': nome,
        'opt_core': opt,
        'n_gravados': len(Cs),
        'truncado': int(trunc),
        'n_viaveis_oracle': n_feas,
        'n_inviaveis': n_inf,
        'n_hdesc': n_hdesc,
        'n_inviaveis_nao_hdesc': n_nao_hdesc,
        'n_Z_distintos': len(z_elimina),
        'max_elimina_um_Z': max(z_elimina.values()) if z_elimina else 0,
    }


def instancias():
    out = []
    S, T, V, adj, _e, r, _c = tr.construir(2, 5, 2, None, m=2)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append(('TR-k2-L5-r2', S, T, V, adj, A_r, r))
    S, T, V, adj, _e, r = bp.construir([3, 1], 2, 2)
    A_r = construir_arcos_alcance(V, adj, r)
    out.append(('BP-nao-[3,1]-q2', S, T, V, adj, A_r, r))
    p = RAIZ / 'instances' / 'benchmark-v1' / 'mapf' / 'mapf-maze-32-32-2-m10-f4.txt'
    S, T, V, adj, A_r, r = load_instance(p)
    out.append(('mapf-maze-32-32-2-m10-f4', S, T, V, adj, A_r, r))
    cand = list((RAIZ / 'instances').rglob('lin-lin03-regiao-f4.txt'))
    if not cand:
        raise FileNotFoundError('lin-lin03-regiao-f4.txt')
    S, T, V, adj, A_r, r = load_instance(cand[0])
    out.append(('lin-lin03-regiao-f4', S, T, V, adj, A_r, r))
    p = RAIZ / 'instances' / 'benchmark-v1' / 'puc' / 'puc-cc9-2p-seed-r1.txt'
    S, T, V, adj, A_r, r = load_instance(p)
    out.append(('puc-cc9-2p-seed-r1', S, T, V, adj, A_r, r))
    return out


def main():
    todas = []
    resumos = []
    for nome, S, T, V, adj, A_r, r in instancias():
        print('platô', nome, 'n=', len(V), flush=True)
        linhas, res = analisar(nome, S, T, V, adj, A_r, r)
        print(
            f"  core={res['opt_core']} gravados={res['n_gravados']} "
            f"viáveis={res['n_viaveis_oracle']} inf={res['n_inviaveis']} "
            f"hdesc={res['n_hdesc']} trunc={res['truncado']}",
            flush=True,
        )
        todas.extend(linhas)
        resumos.append(res)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        w.writeheader()
        for lin in todas:
            w.writerow(lin)
    campos_r = list(resumos[0].keys()) if resumos else []
    with RESUMO.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos_r)
        w.writeheader()
        for r in resumos:
            w.writerow(r)
    print('csv', SAIDA, RESUMO)


if __name__ == '__main__':
    main()
