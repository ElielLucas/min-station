"""
E0: Valida que BASE-I (f inteiro) e BASE-C (f contínuo) produzem o mesmo ótimo.

Executa sobre hc9u + instâncias pequenas. Registra LP, raiz e MIP para ambas.
Resultado: results/cuts/e0_resultados.csv
"""

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from harness import (
    load_instance,
    prepare_cuts,
    measure_lp,
    measure_root,
    measure_mip,
)

OUT_CSV  = ROOT / 'results' / 'cuts' / 'e0_resultados.csv'
INST_DIR = ROOT / 'instances'

# Instâncias selecionadas para E0 (pequenas/médias que resolvem em < 120s)
INSTANCES = [
    'hc9u.txt',
    'cc10-2p.txt',
    'lin23.txt',
    'Chicago_n400_m1130_st5.txt',
    'Barcelona_n930_m2522_st_15.txt',
]

SEED    = 42
THREADS = 4
TL_MIP  = 120   # segundos por MIP completo


HEADER = [
    'instance', 'R', 'n', 'm', 'n_arcos',
    'f_type',
    'lp_bound', 'lp_status', 'time_lp_s',
    'root_no_gurobi', 'root_standard', 'time_root_no_s', 'time_root_std_s',
    'mip_obj', 'mip_bound', 'mip_gap', 'mip_status', 'time_mip_s',
    'seed', 'threads',
]


def run_one(name, S, T, V, adj, A_r, r, f_type):
    print(f'  [{f_type}] LP ... ', end='', flush=True)
    lp_res = measure_lp(S, T, V, A_r, f_type, [], seed=SEED, threads=THREADS)
    print(f"LP={lp_res['lp_bound']:.4f}  raiz-sem ... ", end='', flush=True)

    root_no = measure_root(S, T, V, A_r, f_type, [],
                           gurobi_cuts=0, presolve=0,
                           seed=SEED, threads=THREADS, time_limit=60)
    print(f"raiz-pad ... ", end='', flush=True)

    root_std = measure_root(S, T, V, A_r, f_type, [],
                            gurobi_cuts=-1, presolve=-1,
                            seed=SEED, threads=THREADS, time_limit=60)
    print(f"MIP ... ", end='', flush=True)

    mip = measure_mip(S, T, V, A_r, f_type, [],
                      seed=SEED, threads=THREADS, time_limit=TL_MIP)
    print(f"OPT={mip['mip_obj']}")

    return {
        'instance':        name,
        'R':               r,
        'n':               len(V),
        'm':               len(S),
        'n_arcos':         len(A_r),
        'f_type':          f_type,
        'lp_bound':        lp_res['lp_bound'],
        'lp_status':       lp_res['lp_status'],
        'time_lp_s':       round(lp_res['time_lp_s'], 3),
        'root_no_gurobi':  root_no['root_bound'],
        'root_standard':   root_std['root_bound'],
        'time_root_no_s':  round(root_no['time_root_s'], 3),
        'time_root_std_s': round(root_std['time_root_s'], 3),
        'mip_obj':         mip['mip_obj'],
        'mip_bound':       mip['mip_bound'],
        'mip_gap':         mip['mip_gap'],
        'mip_status':      mip['mip_status'],
        'time_mip_s':      round(mip['time_mip_s'], 3),
        'seed':            SEED,
        'threads':         THREADS,
    }


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for fname in INSTANCES:
        path = INST_DIR / fname
        if not path.exists():
            print(f'[E0] Pulando {fname} (não encontrado)')
            continue
        print(f'\n[E0] {fname}')
        try:
            S, T, V, adj, A_r, r = load_instance(path)
        except Exception as e:
            print(f'  ERRO ao carregar: {e}')
            continue

        for f_type in ['int', 'cont']:
            try:
                row = run_one(fname, S, T, V, adj, A_r, r, f_type)
                rows.append(row)
            except Exception as e:
                print(f'  ERRO em f_type={f_type}: {e}')

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)

    print(f'\n[E0] {len(rows)} linhas salvas em {OUT_CSV}')

    # Resumo: verificar coincidência de ótimos
    print('\n=== Resumo E0: BASE-I vs BASE-C ===')
    by_inst = {}
    for row in rows:
        by_inst.setdefault(row['instance'], {})[row['f_type']] = row
    for inst, d in by_inst.items():
        if 'int' in d and 'cont' in d:
            oi = d['int']['mip_obj']
            oc = d['cont']['mip_obj']
            match = '✓' if (oi is not None and oc is not None and abs(oi - oc) < 1e-4) else '✗'
            print(f"  {inst}: BASE-I={oi}  BASE-C={oc}  {match}")


if __name__ == '__main__':
    main()
