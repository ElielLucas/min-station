#!/usr/bin/env python3
"""Linha de base pré-registrada (Spec A R3/R4).

--calibrar mede Work/parede na instância declarada, 4 threads, TL 20 s.
--medir resolve as 75 principal. Retoma pelas linhas já gravadas.
"""

import argparse
import csv
import hashlib
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
from yspace import _build_ymodel

MANIFESTO = RAIZ / 'instances' / 'manifest.csv'
SAIDA = RAIZ / 'results' / 'benchmark' / 'linha_base.csv'
CORTES_PY = RAIZ / 'experiments' / 'cuts' / 'cuts.py'
CALIBRE = RAIZ / 'instances' / 'estrutural' / 'bp' / 'bp-nao-q8-B60-s0.txt'
BRACOS = ('base', 'comp', 'nucleo')
SEEDS_DA = (42, 43, 44)
SEED_FM = (42,)
THREADS = 4
GUARD_S = 1800
FORA_AVANCO = {
    'hc12p.txt',
    'puc-hc12p-seed-r1.txt',
    'puc-w3c571-seed-r1.txt',
}
CAMPOS = [
    'nome', 'caminho', 'braco', 'seed', 'threads', 'work_limit', 'guard_s',
    'dificuldade', 'particao', 'fora_avanco', 'sha256', 'commit',
    'cuts_sha256', 'fonte_certificado', 'mip_status', 'guarda_parede',
    'mip_obj', 'mip_bound', 'mip_gap', 'node_count', 'work',
    'time_modelo_s', 'time_mip_s', 'time_to_first_incumbent_s',
    'time_to_best_incumbent_s', 'time_to_proof_s', 'n_cortes',
]


def cuts_sha256():
    return hashlib.sha256(CORTES_PY.read_bytes()).hexdigest()


def seeds_de(dificuldade):
    if dificuldade in ('D', 'A'):
        return SEEDS_DA
    return SEED_FM


def instancias():
    with MANIFESTO.open(encoding='utf-8') as fh:
        rows = [r for r in csv.DictReader(fh) if r['classe'] == 'principal']
    rows.sort(key=lambda r: (float(r['n'] or 0), r['nome']))
    return rows


def _ja_feitos():
    if not SAIDA.is_file():
        return set()
    with SAIDA.open(encoding='utf-8') as fh:
        return {
            (r['nome'], r['braco'], int(r['seed']))
            for r in csv.DictReader(fh)
        }


def _anexar(linha):
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    novo = not SAIDA.exists()
    with SAIDA.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        w.writerow({k: linha.get(k, '') for k in CAMPOS})
        fh.flush()


def _resolver_nucleo(V, cortes, seed, work_limit):
    t0 = time.monotonic()
    modelo, _y = _build_ymodel(
        V, cortes, integer=True, seed=seed, threads=THREADS, time_limit=GUARD_S,
    )
    t_modelo = time.monotonic() - t0
    modelo.Params.WorkLimit = work_limit
    incumbente = {'primeiro': None, 'melhor': None, 'obj': None}

    def cb(m, where):
        if where != GRB.Callback.MIPSOL:
            return
        t = float(m.cbGet(GRB.Callback.RUNTIME))
        ub = float(m.cbGet(GRB.Callback.MIPSOL_OBJ))
        if incumbente['primeiro'] is None:
            incumbente['primeiro'] = t
        if incumbente['obj'] is None or ub < incumbente['obj'] - 1e-8:
            incumbente['obj'] = ub
            incumbente['melhor'] = t

    t0 = time.monotonic()
    modelo.optimize(cb)
    dt = time.monotonic() - t0
    status = modelo.Status
    obj = float(modelo.ObjVal) if modelo.SolCount else None
    bound = float(modelo.ObjBound)
    gap = float(modelo.MIPGap) if modelo.SolCount else None
    saida = {
        'mip_obj': obj, 'mip_bound': bound, 'mip_gap': gap, 'mip_status': status,
        'node_count': int(modelo.NodeCount),
        'time_mip_s': dt, 'time_modelo_s': t_modelo,
        'time_to_first_incumbent_s': incumbente['primeiro'],
        'time_to_best_incumbent_s': incumbente['melhor'],
        'time_to_proof_s': dt if status == GRB.OPTIMAL else None,
        'work': float(modelo.Work),
    }
    modelo.dispose()
    return saida


def resolver(caminho, r_usado, braco, seed, work_limit):
    r_val = float(r_usado) if r_usado not in (None, '') else None
    S, T, V, adj, A_r, r = load_instance(RAIZ / caminho, R=r_val)
    if braco == 'base':
        res = measure_mip(
            S, T, V, A_r, 'int', [],
            seed=seed, threads=THREADS, time_limit=GUARD_S,
            params={'WorkLimit': work_limit}, coletar_incumbente=True,
        )
        res['n_cortes'] = 0
        return res
    cortes, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    if braco == 'nucleo':
        res = _resolver_nucleo(V, cortes, seed, work_limit)
        res['n_cortes'] = counts['unicos']
        return res
    res = measure_mip(
        S, T, V, A_r, 'cont', list(cortes),
        seed=seed, threads=THREADS, time_limit=GUARD_S,
        params={'WorkLimit': work_limit}, coletar_incumbente=True,
    )
    res['n_cortes'] = counts['unicos']
    return res


def calibrar():
    S, T, V, _adj, A_r, _r = load_instance(CALIBRE)
    t0 = time.monotonic()
    res = measure_mip(
        S, T, V, A_r, 'int', [],
        seed=42, threads=THREADS, time_limit=20, coletar_incumbente=False,
    )
    parede = time.monotonic() - t0
    work = float(res['work'])
    taxa = work / parede if parede else 0.0
    limite = 600.0 * work / parede if parede else 0.0
    print(
        f'calibracao {CALIBRE.name} base threads={THREADS} TL=20: '
        f'status={res["mip_status"]} work={work:.4f} parede={parede:.3f} '
        f'taxa={taxa:.4f} work/s WorkLimit={limite:.4f} n={len(V)}'
    )


def medir(work_limit):
    feitos = _ja_feitos()
    commit = commit_atual()
    gerador = cuts_sha256()
    for row in instancias():
        nome = row['nome']
        for braco in BRACOS:
            for seed in seeds_de(row.get('dificuldade', '')):
                if (nome, braco, seed) in feitos:
                    continue
                t0 = time.monotonic()
                res = resolver(
                    row['caminho'], row.get('r_usado'), braco, seed, work_limit,
                )
                status = res['mip_status']
                linha = {
                    'nome': nome,
                    'caminho': row['caminho'],
                    'braco': braco,
                    'seed': seed,
                    'threads': THREADS,
                    'work_limit': work_limit,
                    'guard_s': GUARD_S,
                    'dificuldade': row.get('dificuldade', ''),
                    'particao': row.get('particao', ''),
                    'fora_avanco': 1 if nome in FORA_AVANCO else 0,
                    'sha256': row['sha256'],
                    'commit': commit,
                    'cuts_sha256': gerador,
                    'fonte_certificado': 'solver',
                    'mip_status': status,
                    'guarda_parede': 1 if status == GRB.TIME_LIMIT else 0,
                    'n_cortes': res.get('n_cortes', ''),
                }
                for chave in (
                    'mip_obj', 'mip_bound', 'mip_gap', 'node_count', 'work',
                    'time_modelo_s', 'time_mip_s',
                    'time_to_first_incumbent_s', 'time_to_best_incumbent_s',
                    'time_to_proof_s',
                ):
                    linha[chave] = res.get(chave, '')
                _anexar(linha)
                print(
                    f'{nome[:-4]} {braco} s={seed}: status={status} '
                    f'lb={res.get("mip_bound")} ub={res.get("mip_obj")} '
                    f'work={res.get("work")} {time.monotonic()-t0:.1f}s',
                    flush=True,
                )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--calibrar', action='store_true')
    ap.add_argument('--medir', action='store_true')
    ap.add_argument('--work-limit', type=float, default=None)
    args = ap.parse_args()
    if args.calibrar:
        calibrar()
    elif args.medir:
        if args.work_limit is None:
            raise SystemExit('medir exige --work-limit')
        medir(args.work_limit)
    else:
        raise SystemExit('escolha --calibrar ou --medir')


if __name__ == '__main__':
    main()
