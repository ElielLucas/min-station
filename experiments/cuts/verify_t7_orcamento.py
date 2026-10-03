#!/usr/bin/env python3
"""T7: TimeLimit e WorkLimit, sozinho e com a máquina carregada.

Duas instâncias de tamanhos diferentes, mesma configuração (seed 42, 1 thread,
heurística/cortes/presolve desligados para a busca sair da raiz). A carga são
processos ocupando os núcleos; o solver continua com Threads=1.

Não altera o orçamento dos experimentos já publicados.
"""

import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from baseline import construir_modelo_baseline
from harness import load_instance, measure_mip

INSTANCIAS = [
    ROOT / 'instances/hc9u.txt',
    ROOT / 'instances/benchmark-v1/mapf/mapf-empty-32-32-m25-f4.txt',
]
TL = 3.0
PARAMS = {'Heuristics': 0, 'Cuts': 0, 'Presolve': 0}


def _queimar():
    x = 0
    while True:
        x = (x * 1664525 + 1013904223) & 0xFFFFFFFF


def _carga(n):
    import multiprocessing as mp
    procs = [mp.Process(target=_queimar, daemon=True) for _ in range(n)]
    for p in procs:
        p.start()
    time.sleep(0.3)
    return procs


def _parar(procs):
    for p in procs:
        p.terminate()
    for p in procs:
        p.join(timeout=2)


def _medir(caminho, time_limit, work_limit, carga):
    S, T, V, _adj, A_r, _r = load_instance(str(caminho))
    params = dict(PARAMS)
    if work_limit is not None:
        params['WorkLimit'] = work_limit
    procs = _carga(os.cpu_count() or 1) if carga else []
    try:
        res = measure_mip(
            S, T, V, A_r, 'int', [],
            seed=42, threads=1, time_limit=time_limit, params=params,
        )
    finally:
        _parar(procs)
    return {
        'instancia': caminho.name,
        'n': len(V),
        'carga': carga,
        'time_limit': time_limit,
        'work_limit': work_limit,
        'status': res['mip_status'],
        'nos': res['node_count'],
        'work': res['work'],
        'parede_s': res['time_mip_s'],
    }


def _lp_worklimit(caminho):
    S, T, V, _adj, A_r, _r = load_instance(str(caminho))
    modelo, _y, f, _na, _nv = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.Params.Threads = 1
    for var in f.values():
        var.vtype = GRB.CONTINUOUS
    modelo.Params.WorkLimit = 0.05
    modelo.optimize()
    status = modelo.Status
    work = float(modelo.Work)
    modelo.dispose()
    return status, work


def main():
    linhas = []
    for caminho in INSTANCIAS:
        base = _medir(caminho, TL, None, False)
        linhas.append(('TimeLimit sozinho', base))
        linhas.append(('TimeLimit com carga', _medir(caminho, TL, None, True)))
        teto = base['work']
        linhas.append(('WorkLimit sozinho', _medir(caminho, GRB.INFINITY, teto, False)))
        linhas.append(('WorkLimit com carga', _medir(caminho, GRB.INFINITY, teto, True)))
    print(f'{"condicao":22} {"instancia":32} {"n":5} {"status":6} {"nos":7} {"work":8} {"parede_s":8}')
    for nome, r in linhas:
        print(f'{nome:22} {r["instancia"]:32} {r["n"]:5} {r["status"]:6} {r["nos"]:7} {r["work"]:8.3f} {r["parede_s"]:8.3f}')
    status_lp, work_lp = _lp_worklimit(INSTANCIAS[0])
    print(f'LP WorkLimit hc9u status={status_lp} (WORK_LIMIT={GRB.WORK_LIMIT}) work={work_lp:.3f}')


if __name__ == '__main__':
    main()
