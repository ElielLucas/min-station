#!/usr/bin/env python3
"""R6 primal: COMP vs COMP+MIPFocus=1. Controle = linha_base braco=comp.

Pré-registro: docs/technical/reference/pre-registro-r5.md
WorkLimit=164, 4 threads, seeds 42/43/44, D/A desenvolvimento, m<1000.
"""

import csv
import hashlib
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'structural'))

from gurobipy import GRB

from harness import load_instance, measure_mip, prepare_cuts
from io_instancia import commit_atual

MANIFESTO = RAIZ / 'instances' / 'manifest.csv'
CONTROLE = RAIZ / 'results' / 'benchmark' / 'linha_base.csv'
SAIDA = RAIZ / 'results' / 'benchmark' / 'r6-primal.csv'
CORTES_PY = RAIZ / 'experiments' / 'cuts' / 'cuts.py'
WORK = 164
GUARD = 1800
THREADS = 4
SEEDS = (42, 43, 44)
FORA_M = {
    'hc12p.txt',
    'puc-hc12p-seed-r1.txt',
    'puc-w3c571-seed-r1.txt',
}
CAMPOS = [
    'nome', 'caminho', 'braco', 'seed', 'threads', 'work_limit',
    'mipfocus', 'familia', 'sha256', 'commit', 'cuts_sha256',
    'mip_status', 'guarda_parede', 'mip_obj', 'mip_bound', 'mip_gap',
    'node_count', 'work', 'time_modelo_s', 'time_mip_s',
    'time_to_first_incumbent_s', 'time_to_best_incumbent_s',
    'time_to_proof_s', 'n_cortes', 'm',
]


def familia(nome):
    if nome.startswith('pucn-'):
        return 'pucn'
    if nome.startswith('puc-'):
        return 'puc'
    if nome.startswith('pace18-'):
        return 'pace18'
    if nome.startswith('mapf-'):
        return 'mapf'
    if nome.startswith('vienna-'):
        return 'vienna'
    return nome.split('-')[0].replace('.txt', '')


def cuts_sha():
    return hashlib.sha256(CORTES_PY.read_bytes()).hexdigest()


def alvos():
    out = []
    with MANIFESTO.open(encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['classe'] != 'principal':
                continue
            if r.get('dificuldade') not in ('D', 'A'):
                continue
            if 'desenvolvimento' not in r.get('particao', ''):
                continue
            if r['nome'] in FORA_M:
                continue
            if int(float(r['m'])) >= 1000:
                continue
            out.append(r)
    out.sort(key=lambda r: (float(r['n'] or 0), r['nome']))
    return out


def feitos():
    if not SAIDA.is_file():
        return set()
    with SAIDA.open(encoding='utf-8') as fh:
        return {(r['nome'], r['braco'], int(r['seed'])) for r in csv.DictReader(fh)}


def anexar(linha):
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    novo = not SAIDA.exists()
    with SAIDA.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        w.writerow({k: linha.get(k, '') for k in CAMPOS})
        fh.flush()


def copiar_controle():
    """Uma vez: copia comp da linha de base como braço control."""
    ja = feitos()
    commit = commit_atual()
    gerador = cuts_sha()
    with CONTROLE.open(encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    nomes = {r['nome'] for r in alvos()}
    n = 0
    for r in rows:
        if r['braco'] != 'comp' or r['nome'] not in nomes:
            continue
        chave = (r['nome'], 'control', int(r['seed']))
        if chave in ja:
            continue
        linha = {k: '' for k in CAMPOS}
        linha.update({
            'nome': r['nome'],
            'caminho': r['caminho'],
            'braco': 'control',
            'seed': r['seed'],
            'threads': r['threads'],
            'work_limit': r['work_limit'],
            'mipfocus': 'default',
            'familia': familia(r['nome']),
            'sha256': r['sha256'],
            'commit': commit,
            'cuts_sha256': gerador,
            'mip_status': r['mip_status'],
            'guarda_parede': r.get('guarda_parede', ''),
            'mip_obj': r.get('mip_obj', ''),
            'mip_bound': r.get('mip_bound', ''),
            'mip_gap': r.get('mip_gap', ''),
            'node_count': r.get('node_count', ''),
            'work': r.get('work', ''),
            'time_modelo_s': r.get('time_modelo_s', ''),
            'time_mip_s': r.get('time_mip_s', ''),
            'time_to_first_incumbent_s': r.get('time_to_first_incumbent_s', ''),
            'time_to_best_incumbent_s': r.get('time_to_best_incumbent_s', ''),
            'time_to_proof_s': r.get('time_to_proof_s', ''),
            'n_cortes': r.get('n_cortes', ''),
            'm': '',
        })
        anexar(linha)
        n += 1
    print(f'controle copiado: {n} linhas novas', flush=True)


def medir_foco():
    ja = feitos()
    commit = commit_atual()
    gerador = cuts_sha()
    for row in alvos():
        nome = row['nome']
        for seed in SEEDS:
            if (nome, 'mipfocus1', seed) in ja:
                continue
            t0 = time.monotonic()
            S, T, V, adj, A_r, r = load_instance(
                RAIZ / row['caminho'],
                R=float(row['r_usado']) if row.get('r_usado') else None,
            )
            cortes, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res = measure_mip(
                S, T, V, A_r, 'cont', list(cortes),
                seed=seed, threads=THREADS, time_limit=GUARD,
                params={'WorkLimit': WORK, 'MIPFocus': 1},
                coletar_incumbente=True,
            )
            status = res['mip_status']
            linha = {
                'nome': nome,
                'caminho': row['caminho'],
                'braco': 'mipfocus1',
                'seed': seed,
                'threads': THREADS,
                'work_limit': WORK,
                'mipfocus': 1,
                'familia': familia(nome),
                'sha256': row['sha256'],
                'commit': commit,
                'cuts_sha256': gerador,
                'mip_status': status,
                'guarda_parede': 1 if status == GRB.TIME_LIMIT else 0,
                'n_cortes': counts['unicos'],
                'm': len(S),
            }
            for chave in (
                'mip_obj', 'mip_bound', 'mip_gap', 'node_count', 'work',
                'time_modelo_s', 'time_mip_s',
                'time_to_first_incumbent_s', 'time_to_best_incumbent_s',
                'time_to_proof_s',
            ):
                linha[chave] = res.get(chave, '')
            anexar(linha)
            print(
                f'{nome[:-4]} foco s={seed}: status={status} '
                f'lb={res.get("mip_bound")} ub={res.get("mip_obj")} '
                f'{time.monotonic()-t0:.1f}s',
                flush=True,
            )


def main():
    os.environ.setdefault('PYTHONHASHSEED', '0')
    copiar_controle()
    medir_foco()


if __name__ == '__main__':
    main()
