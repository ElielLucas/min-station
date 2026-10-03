#!/usr/bin/env python3
"""Fase E da família SC. Orçamento e métodos iguais aos do piloto."""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import sc
from io_instancia import commit_atual
from piloto import CAMPOS_MED, PASTA, resolver

OUT = RAIZ / 'results' / 'structural' / 'fase_e_sc.csv'
WORK = 297
SEEDS_GER = (100, 101, 102, 103, 104)
SEEDS_SOLVER = (42, 43, 44)
METODOS = ('base', 'comp', 'nucleo', 'comp_c6')


def _feitos():
    if not OUT.exists():
        return set()
    with OUT.open(encoding='utf-8') as fh:
        return {(r['id'], r['metodo'], r['seed_solver']) for r in csv.DictReader(fh)}


def _anexar(linha):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    novo = not OUT.exists()
    with OUT.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS_MED)
        if novo:
            w.writeheader()
        w.writerow(linha)


def instancias():
    saida = []
    for k in (8, 9):
        inst = sc.emitir(PASTA['sc'], k, 0, False)
        saida.append((f'sc-gf2-k{k}', inst))
        for seed in SEEDS_GER:
            inst = sc.emitir(PASTA['sc'], k, seed, True, time_limit=90)
            if inst['certificado'] is None:
                print(f'sc-rigida-k{k}-s{seed}: sem certificado, fora da avaliação', flush=True)
                continue
            saida.append((f'sc-rigida-k{k}-s{seed}', inst))
    return saida


def main():
    feitos = _feitos()
    for ident, inst in instancias():
        for seed in SEEDS_SOLVER:
            for metodo in METODOS:
                if (ident, metodo, str(seed)) in feitos:
                    continue
                res = resolver(inst, metodo, WORK, seed=seed)
                linha = {
                    'id': ident, 'familia': 'sc', 'fatia': 'avaliacao',
                    'metodo': metodo, 'sha256': inst['sha256'], 'seed_solver': seed,
                    'threads': 4, 'work_limit': WORK, 'guard_s': 1800,
                    'commit': commit_atual(),
                }
                for chave in CAMPOS_MED:
                    if chave in res:
                        linha[chave] = res[chave]
                _anexar(linha)
                print(
                    f'{ident} seed={seed} {metodo}: status={res["mip_status"]} '
                    f'obj={res["mip_obj"]} bound={res["mip_bound"]} '
                    f'nos={res["node_count"]} work={res["work"]:.2f}',
                    flush=True,
                )


if __name__ == '__main__':
    main()
