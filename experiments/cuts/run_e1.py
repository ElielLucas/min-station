"""
E1: Instâncias reais com cortes cumulativos (configurações A–E).

Para cada instância e configuração, mede:
  1. LP puro (com C3 iterativo em E)
  2. Raiz sem cortes Gurobi (Cuts=0, Presolve=0, NodeLimit=0)
  3. Raiz padrão Gurobi (NodeLimit=0)

Resultado: results/cuts/e1_raiz.csv
"""

import csv
import sys
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
)

OUT_CSV  = ROOT / 'results' / 'cuts' / 'e1_raiz.csv'
INST_DIR = ROOT / 'instances'

SEED    = 42
THREADS = 4
TL_ROOT = 120   # segundos por medida de raiz

# Instâncias dos três regimes descritos no documento
INSTANCES = [
    # Regime R-b: terminais densos, autonomia pequena
    'hc9u.txt',
    'hc10p.txt',
    # Regime R-a: longo curso TNTP
    'Chicago_n400_m1130_st5.txt',
    'Philadelphia_n800_m2404_st_25.txt',
    # Regime R-c: r grande, cobertura densa
    'cc10-2p.txt',
    'cc12-2p.txt',
]

# Configurações cumulativas (BASE-C)
CONFIGS = [
    ('A', set(),              False),   # BASE-C, sem cortes
    ('B', {'C1'},             False),   # + C1
    ('C', {'C1', 'C2'},       False),   # + C2
    ('D', {'C1', 'C2', 'C4'}, False),   # + C4-DM
    ('E', {'C1', 'C2', 'C4'}, True),    # + C3 iterativo no LP
]

HEADER = [
    'instance', 'R', 'n', 'm', 'n_arcos',
    'config', 'f_type',
    'n_c1', 'n_c2', 'n_c4',
    'lp_bound', 'n_c3_cuts', 'n_c3_rounds', 'time_lp_s',
    'root_no_gurobi', 'time_root_no_s',
    'root_standard',  'time_root_std_s',
    'seed', 'threads',
]


def run_instance_configs(fname):
    path = INST_DIR / fname
    if not path.exists():
        print(f'[E1] {fname} não encontrado — pulando')
        return []

    print(f'\n[E1] {fname}')
    try:
        S, T, V, adj, A_r, r = load_instance(path)
    except Exception as e:
        print(f'  ERRO ao carregar: {e}')
        return []

    print(f'  n={len(V)}, m={len(S)}, |A_r|={len(A_r)}, R={r}')

    rows = []
    for cfg_name, active_cuts, use_c3 in CONFIGS:
        print(f'  Config {cfg_name} ... ', end='', flush=True)

        try:
            cuts_spec, counts = prepare_cuts(S, T, V, adj, A_r, r, active_cuts)

            lp_res = measure_lp(S, T, V, A_r, 'cont', cuts_spec,
                                use_c3=use_c3, c3_max_rounds=20,
                                seed=SEED, threads=THREADS)

            root_no = measure_root(S, T, V, A_r, 'cont', cuts_spec,
                                   gurobi_cuts=0, presolve=0,
                                   seed=SEED, threads=THREADS, time_limit=TL_ROOT)

            root_std = measure_root(S, T, V, A_r, 'cont', cuts_spec,
                                    gurobi_cuts=-1, presolve=-1,
                                    seed=SEED, threads=THREADS, time_limit=TL_ROOT)

            lb_no  = root_no['root_bound']
            lb_std = root_std['root_bound']
            lp_val = lp_res['lp_bound']
            print(f"LP={_fmt(lp_val)}  raiz-sem={_fmt(lb_no)}  raiz-pad={_fmt(lb_std)}")

            rows.append({
                'instance':       fname,
                'R':              r,
                'n':              len(V),
                'm':              len(S),
                'n_arcos':        len(A_r),
                'config':         cfg_name,
                'f_type':         'cont',
                'n_c1':           counts['C1'],
                'n_c2':           counts['C2'],
                'n_c4':           counts['C4'],
                'lp_bound':       lp_val,
                'n_c3_cuts':      lp_res.get('n_c3_cuts', 0),
                'n_c3_rounds':    lp_res.get('n_c3_rounds', 0),
                'time_lp_s':      round(lp_res['time_lp_s'], 3),
                'root_no_gurobi': lb_no,
                'time_root_no_s': round(root_no['time_root_s'], 3),
                'root_standard':  lb_std,
                'time_root_std_s':round(root_std['time_root_s'], 3),
                'seed':           SEED,
                'threads':        THREADS,
            })

        except Exception as e:
            print(f'ERRO: {e}')

    return rows


def _fmt(v):
    return f'{v:.4f}' if v is not None else 'None'


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for fname in INSTANCES:
        all_rows += run_instance_configs(fname)

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)

    print(f'\n[E1] {len(all_rows)} linhas salvas em {OUT_CSV}')

    # Tabela resumo: melhora do limitante por instância
    print('\n=== Resumo E1: ganho de limitante ===')
    by_inst = {}
    for row in all_rows:
        by_inst.setdefault(row['instance'], {})[row['config']] = row

    for inst, cfgs in by_inst.items():
        print(f'\n  {inst}')
        base_lp  = cfgs.get('A', {}).get('lp_bound')
        base_std = cfgs.get('A', {}).get('root_standard')
        for cfg in ['A', 'B', 'C', 'D', 'E']:
            if cfg not in cfgs:
                continue
            r = cfgs[cfg]
            lp  = r['lp_bound']
            std = r['root_standard']
            gain_lp  = f'+{lp  - base_lp:.4f}' if (lp  is not None and base_lp  is not None) else '?'
            gain_std = f'+{std - base_std:.4f}' if (std is not None and base_std is not None) else '?'
            print(f'    {cfg}  LP={_fmt(lp)} ({gain_lp})  '
                  f'raiz-std={_fmt(std)} ({gain_std})')


if __name__ == '__main__':
    main()
