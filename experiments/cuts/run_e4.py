"""
E4: Árvore curta (300 s) com e sem cortes estáticos.

Compara três configurações no mesmo conjunto de instâncias:
  BASE-I : fluxo inteiro, sem cortes
  BASE-C : fluxo contínuo, sem cortes
  CORTES : BASE-C + melhor conjunto estático (C1+C2+C4 a priori)

Resultado: results/cuts/e4_arvore.csv
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from harness import load_instance, prepare_cuts, measure_mip

INST_DIR = ROOT / 'instances'
OUT_CSV  = ROOT / 'results' / 'cuts' / 'e4_arvore.csv'

SEED     = 42
THREADS  = 4
TL       = 300   # s por execução

# Instâncias com ótimo ou faixa conhecidos; sem lin23, lin37
# R corresponde às referências históricas, não ao R gravado no arquivo:
# Chicago st15 R7=17*, Barcelona st15 R5=15*, Barcelona st25 R5=16*,
# Philadelphia st5 R2=41*, Philadelphia st25 R3=[42,46], hc9u R1=[31,40]
INSTANCES = [
    ('Chicago_n400_m1130_st15.txt',       7,    17),
    ('Barcelona_n930_m2522_st_15.txt',    5,    15),
    ('Barcelona_n930_m2522_st_25.txt',    5,    16),
    ('Philadelphia_n800_m2404_st_5.txt',  2,    41),
    ('Philadelphia_n800_m2404_st_25.txt', 3,    None),  # aberta
    ('hc9u.txt',                          None, None),  # aberta; R do arquivo já é 1
]

HEADER = [
    'instancia', 'R', 'r_origem', 'n', 'm', 'n_arcos',
    'config',
    'n_cuts',
    'root_no', 'root_std',
    'mip_obj', 'mip_bound', 'mip_gap', 'mip_status',
    'time_s',
    'ref_opt',
    'seed', 'threads',
]


def _fmt(v, dec=4):
    return f'{v:.{dec}f}' if v is not None else 'None'


def run_instance(fname, r_override, ref_opt):
    path = INST_DIR / fname
    if not path.exists():
        print(f'  {fname}: não encontrado — pulando')
        return []

    try:
        S, T, V, adj, A_r, r = load_instance(path, R=r_override)
    except Exception as e:
        print(f'  {fname}: erro ao carregar — {e}')
        return []
    r_origem = 'override' if r_override is not None else 'arquivo'

    n, m, na = len(V), len(S), len(A_r)
    print(f'\n  {fname}  (n={n}, m={m}, |A_r|={na}, R={r})')

    configs = [
        ('BASE-I',  'int',  set()),
        ('BASE-C',  'cont', set()),
        ('CORTES',  'cont', {'C1', 'C2', 'C4'}),
    ]

    rows = []
    for cfg_name, f_type, active in configs:
        cuts_spec, counts = prepare_cuts(S, T, V, adj, A_r, r, active)
        n_cuts = sum(counts.values())

        # Uma única execução MIP com TL=300s; root_bound = ObjBound após raiz
        mip = measure_mip(S, T, V, A_r, f_type, cuts_spec,
                          seed=SEED, threads=THREADS, time_limit=TL)

        status_map = {2: 'OPT', 9: 'TL', 11: 'INT'}
        st = status_map.get(mip['mip_status'], str(mip['mip_status']))

        print(f'    {cfg_name:<8}  obj={_fmt(mip["mip_obj"])}  '
              f'bnd={_fmt(mip["mip_bound"])}  gap={_fmt(mip["mip_gap"])}  '
              f'st={st}  t={_fmt(mip["time_mip_s"],1)}s')

        rows.append({
            'instancia':  fname,
            'R':          r,
            'r_origem':   r_origem,
            'n':          n,
            'm':          m,
            'n_arcos':    na,
            'config':     cfg_name,
            'n_cuts':     n_cuts,
            'root_no':    None,   # não medido em E4 para economizar tempo
            'root_std':   None,
            'mip_obj':    mip['mip_obj'],
            'mip_bound':  mip['mip_bound'],
            'mip_gap':    mip['mip_gap'],
            'mip_status': mip['mip_status'],
            'time_s':     round(mip['time_mip_s'], 3),
            'ref_opt':    ref_opt,
            'seed':       SEED,
            'threads':    THREADS,
        })

    return rows


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []

    print('=== E4: Árvore curta (TL=300s) ===')
    for fname, r_override, ref_opt in INSTANCES:
        all_rows += run_instance(fname, r_override, ref_opt)

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)

    print(f'\n[E4] {len(all_rows)} linhas salvas em {OUT_CSV}')

    # Resumo: verifica ótimos conhecidos
    print('\n=== Resumo E4: ótimos ===')
    by_inst = {}
    for row in all_rows:
        by_inst.setdefault(row['instancia'], []).append(row)
    for inst, rows in by_inst.items():
        ref = rows[0]['ref_opt']
        print(f'\n  {inst}  (ref={ref})')
        for r in rows:
            gap_str = f"gap={_fmt(r['mip_gap'])}" if r['mip_gap'] is not None else ''
            opt_ok  = ref is not None and r['mip_obj'] is not None and abs(r['mip_obj'] - ref) < 0.5
            tag     = ' ✓' if opt_ok else ''
            print(f'    {r["config"]:<8}  obj={_fmt(r["mip_obj"])}  '
                  f'bnd={_fmt(r["mip_bound"])}  {gap_str}{tag}')


if __name__ == '__main__':
    main()
