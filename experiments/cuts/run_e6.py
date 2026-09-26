"""
E6: branch-and-cut em y com corte lazy combinatório (linha A2).

Compara duas configurações:
  NUCLEO : y-space com C1 estático, sem lazy (controle)
  BC-LAZY: y-space com C1 estático + corte combinatório lazy via max-flow

Gabaritos sintéticos primeiro (smoke test do callback), depois hc9u e
bip42p com TL=900s.

Resultado: results/cuts/e6_bc_y.csv
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from harness import load_instance
from bc_yspace import solve_bc_yspace, prepare_static_c1
from synthetic import make_Direct0, make_TermRelay, make_Sec59, make_SharedTerminal

INST_DIR = ROOT / 'instances'
OUT_CSV  = ROOT / 'results' / 'cuts' / 'e6_bc_y.csv'

SEED    = 42
THREADS = 4
TL_REAL = 900

INSTANCES = [
    ('hc9u.txt', None, 32),      # teto do núcleo já provado (E3); LB>32 é sucesso
    ('bip42p.txt', None, None),
]

HEADER = [
    'instancia', 'R', 'n', 'm', 'n_arcos',
    'config', 'obj', 'bound', 'gap', 'status',
    'n_lazy_cuts', 'n_lazy_calls', 'time_s',
    'teto_nucleo', 'seed', 'threads',
]


def _fmt(v, dec=4):
    return f'{v:.{dec}f}' if v is not None else 'None'


def run_gabaritos_smoke_test():
    print('=== E6: smoke test do callback (gabaritos) ===\n')
    ok = True
    casos = [
        ('Direct0', make_Direct0, 0.0),
        ('TermRelay', make_TermRelay, 1.0),
        ('SharedTerminal', make_SharedTerminal, 1.0),
        ('Sec59(L=7)', lambda: make_Sec59(L=7, r=1), 7.0),
    ]
    for nome, maker, esperado in casos:
        S, T, V, adj, A_r, r, meta = maker()
        static = prepare_static_c1(S, T, A_r)
        res = solve_bc_yspace(S, T, V, A_r, static_cuts=static,
                               time_limit=60, seed=SEED, threads=1,
                               use_lazy=True)
        obtido = res['obj']
        passou = obtido is not None and abs(obtido - esperado) < 1e-6
        tag = 'PASS' if passou else 'FAIL'
        if not passou:
            ok = False
        print(f'  {nome:<16} esperado={esperado}  obtido={_fmt(obtido)}  '
              f'lazy_calls={res["n_lazy_calls"]}  lazy_cuts={res["n_lazy_cuts"]}  {tag}')
    if not ok:
        print('\nABORTANDO: gabarito(s) falhou no callback lazy.')
        sys.exit(1)
    print('\n  Todos os gabaritos PASS.\n')


def run_instance(fname, r_override, teto_nucleo):
    path = INST_DIR / fname
    if not path.exists():
        print(f'  {fname}: não encontrado — pulando')
        return []

    S, T, V, adj, A_r, r = load_instance(path, R=r_override)
    n, m, na = len(V), len(S), len(A_r)
    print(f'\n  {fname}  (n={n}, m={m}, |A_r|={na}, R={r})')

    static = prepare_static_c1(S, T, A_r)

    rows = []
    for cfg_name, use_lazy in [('NUCLEO', False), ('BC-LAZY', True)]:
        res = solve_bc_yspace(S, T, V, A_r, static_cuts=static,
                               time_limit=TL_REAL, seed=SEED, threads=THREADS,
                               use_lazy=use_lazy)
        status_map = {2: 'OPT', 9: 'TL', 11: 'INT'}
        st = status_map.get(res['status'], str(res['status']))
        print(f'    {cfg_name:<8}  obj={_fmt(res["obj"])}  bound={_fmt(res["bound"])}  '
              f'gap={_fmt(res["gap"])}  st={st}  lazy_cuts={res["n_lazy_cuts"]}  '
              f't={_fmt(res["time_s"],1)}s')
        rows.append({
            'instancia': fname, 'R': r, 'n': n, 'm': m, 'n_arcos': na,
            'config': cfg_name,
            'obj': res['obj'], 'bound': res['bound'], 'gap': res['gap'],
            'status': res['status'],
            'n_lazy_cuts': res['n_lazy_cuts'], 'n_lazy_calls': res['n_lazy_calls'],
            'time_s': round(res['time_s'], 3),
            'teto_nucleo': teto_nucleo,
            'seed': SEED, 'threads': THREADS,
        })
    return rows


def main():
    run_gabaritos_smoke_test()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    print('=== E6: hc9u e bip42p (TL=900s) ===')
    for fname, r_override, teto in INSTANCES:
        all_rows += run_instance(fname, r_override, teto)

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)
    print(f'\n[E6] {len(all_rows)} linhas salvas em {OUT_CSV}')

    print('\n=== Resumo E6: LB acima do teto do núcleo? ===')
    by_inst = {}
    for row in all_rows:
        by_inst.setdefault(row['instancia'], []).append(row)
    for inst, rows in by_inst.items():
        teto = rows[0]['teto_nucleo']
        print(f'\n  {inst} (teto do núcleo={teto})')
        for r in rows:
            supera = (teto is not None and r['bound'] is not None
                      and r['bound'] > teto + 1e-6)
            tag = ' <-- LB acima do teto do núcleo!' if supera else ''
            print(f'    {r["config"]:<8}  bound={_fmt(r["bound"])}  '
                  f'obj={_fmt(r["obj"])}{tag}')


if __name__ == '__main__':
    main()
