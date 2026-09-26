"""
Protocolo de dificuldade do benchmark-v1 (plano-benchmark-v1.md §6).

Método de referência: COMP = baseline (variante U, fluxo contínuo) + cortes
estáticos C1+C2+C4; Gurobi, 4 threads, seed 42, TL 600 s.

Classes: F = ótimo provado em ≤ 60 s; M = ótimo em ≤ 600 s; D = gap final ≤ 10%;
A = gap > 10% ou sem incumbente; X = não executada (|A_r| acima do limite de
memória).

Executa as instâncias de instances/benchmark-v1 listadas no manifesto, grava uma
linha por instância em results/benchmark/dificuldade_v1[_fatiaK].csv e pula as
já presentes (retomável). `--fatia k/n` divide o trabalho entre processos.

Uso: python experiments/benchmark/run_dificuldade.py [--fatia 1/2] [--tl 600]
"""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

import gurobipy
from harness import load_instance, prepare_cuts, measure_mip

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT_DIR = ROOT / 'results' / 'benchmark'
LIMITE_ARCOS = 4_000_000
CAMPOS = ['nome', 'caminho', 'n', 'm', 'r', 'n_arcos_alcance', 'n_cortes', 'lb', 'ub', 'gap',
          'status', 't_solver_s', 't_total_s', 'dificuldade', 'tl_s', 'threads', 'seed',
          'gurobi', 'metodo']


def classificar(status, t, gap, ub):
    if status == 2:
        return 'F' if t <= 60 else 'M'
    if ub is None:
        return 'A'
    return 'D' if gap is not None and gap <= 0.10 else 'A'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--tl', type=float, default=600)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))

    linhas = [r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))
              if r['caminho'].startswith('instances/benchmark-v1/')]
    linhas.sort(key=lambda r: int(r['n_arcos_alcance'] or 10**12))
    minhas = [r for i, r in enumerate(linhas) if i % n == k - 1]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / (f'dificuldade_v1_fatia{k}.csv' if n > 1 else 'dificuldade_v1.csv')
    feitas = set()
    if out.exists():
        feitas = {r['nome'] for r in csv.DictReader(out.open(encoding='utf-8'))}
    novo = not out.exists()
    versao = '.'.join(map(str, gurobipy.gurobi.version()))

    with out.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for row in minhas:
            if row['nome'] in feitas:
                continue
            t0 = time.monotonic()
            base = {'nome': row['nome'], 'caminho': row['caminho'], 'n': row['n'], 'm': row['m'],
                    'r': row['r'], 'n_arcos_alcance': row['n_arcos_alcance'], 'tl_s': args.tl,
                    'threads': 4, 'seed': 42, 'gurobi': versao, 'metodo': 'COMP (U + C1+C2+C4)'}
            if row['n_arcos_alcance'] and int(row['n_arcos_alcance']) > LIMITE_ARCOS:
                base.update(status='nao_executada', dificuldade='X')
                w.writerow(base)
                fh.flush()
                print(f'{row["nome"]:36s} X (|A_r|={row["n_arcos_alcance"]})', flush=True)
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            cortes, cont = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res = measure_mip(S, T, V, A_r, 'cont', cortes, seed=42, threads=4,
                              time_limit=args.tl)
            ub, lb, gap = res['mip_obj'], res['mip_bound'], res['mip_gap']
            dif = classificar(res['mip_status'], res['time_mip_s'], gap, ub)
            base.update(n_cortes=cont['unicos'], lb=lb, ub=ub, gap=gap, status=res['mip_status'],
                        t_solver_s=round(res['time_mip_s'], 2),
                        t_total_s=round(time.monotonic() - t0, 2), dificuldade=dif)
            w.writerow(base)
            fh.flush()
            print(f'{row["nome"]:36s} {dif}  ub={ub} lb={lb} t={res["time_mip_s"]:.1f}s', flush=True)


if __name__ == '__main__':
    main()
