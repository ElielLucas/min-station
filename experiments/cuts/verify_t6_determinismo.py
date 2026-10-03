#!/usr/bin/env python3
"""T6: a ordem dos cortes no modelo não depende de PYTHONHASHSEED.

Cada processo imprime a ordem antiga (set de frozenset, o defeito) e a ordem
nova (prepare_cuts + restrições do mestre em y). O processo pai compara as
sementes 0, 1, 2 e 3.

A ordem antiga precisa divergir em pelo menos um par de sementes: é a
regressão negativa do parecer §3.1. A ordem nova precisa ser idêntica.
O conjunto de cortes é o mesmo nos dois casos.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

INSTANCIAS = [
    ROOT / 'instances/benchmark-v1/steinlib-b/b-b15-regiao-f4.txt',
    ROOT / 'instances/benchmark-v1/pace2018/pace18-t2-001-regiao-f2.txt',
]
SEMENTES = ('0', '1', '2', '3')


def _ordem_antiga(cortes):
    return [tuple(sorted(z)) for z in {frozenset(Z) for Z in cortes}]


def _hash(ordem):
    bruto = json.dumps(ordem, ensure_ascii=True).encode()
    return hashlib.sha256(bruto).hexdigest()


def _rodar_processo(semente):
    codigo = r'''
import hashlib, json, sys
from pathlib import Path
HERE = Path(%r)
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
from harness import prepare_cuts, load_instance
from yspace import _build_ymodel

def ordem_antiga(cortes):
    return [tuple(sorted(z)) for z in {frozenset(Z) for Z in cortes}]

def h(ordem):
    return hashlib.sha256(json.dumps(ordem).encode()).hexdigest()

saida = {}
for caminho in %r:
    S, T, V, adj, A_r, r = load_instance(caminho)
    cortes, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    nova = [tuple(sorted(z)) for z in cortes]
    antiga = ordem_antiga(cortes)
    modelo, _ = _build_ymodel(V, cortes, integer=True, time_limit=1, threads=1)
    restricoes = []
    for c in modelo.getConstrs():
        linha = modelo.getRow(c)
        vs = sorted(linha.getVar(i).VarName for i in range(linha.size()))
        restricoes.append(tuple(vs))
    modelo.dispose()
    nome = Path(caminho).name
    saida[nome] = {
        'n': counts['unicos'],
        'conjunto': h(sorted(nova)),
        'antiga': h(antiga),
        'nova': h(nova),
        'restricoes': h(restricoes),
        'antiga_igual_conjunto': sorted(antiga) == sorted(nova),
    }
print(json.dumps(saida))
''' % (str(HERE), [str(p) for p in INSTANCIAS])
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = semente
    proc = subprocess.run(
        [sys.executable, '-c', codigo],
        cwd=str(ROOT), env=env, capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main():
    for caminho in INSTANCIAS:
        if not caminho.is_file():
            raise SystemExit(f'instância ausente: {caminho}')
    por_semente = {s: _rodar_processo(s) for s in SEMENTES}
    falhas = []
    for nome in por_semente['0']:
        base = por_semente['0'][nome]
        antigas = {por_semente[s][nome]['antiga'] for s in SEMENTES}
        novas = {por_semente[s][nome]['nova'] for s in SEMENTES}
        restricoes = {por_semente[s][nome]['restricoes'] for s in SEMENTES}
        conjuntos = {por_semente[s][nome]['conjunto'] for s in SEMENTES}
        if len(conjuntos) != 1:
            falhas.append(f'{nome}: o conjunto de cortes mudou entre sementes')
        if len(antigas) < 2:
            falhas.append(f'{nome}: a ordem antiga não divergiu (regressão negativa ausente)')
        if len(novas) != 1 or len(restricoes) != 1:
            falhas.append(f'{nome}: a ordem nova ainda depende da semente')
        if not all(por_semente[s][nome]['antiga_igual_conjunto'] for s in SEMENTES):
            falhas.append(f'{nome}: deduplicação antiga e nova não têm o mesmo conjunto')
        print(f'{nome}: n={base["n"]}  ordens_antigas={len(antigas)}  '
              f'ordem_nova={next(iter(novas))[:12]}')
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print(f'ok: {len(INSTANCIAS)} instâncias, sementes {",".join(SEMENTES)}, '
          'conjunto estável e ordem nova idêntica')


if __name__ == '__main__':
    main()
