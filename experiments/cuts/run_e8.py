"""
E8: comparação COMP vs. BC-Y' vs. CBI em condições equivalentes.

Condições comuns por instância:
  - mesmos cortes estáticos (C1+C2+C4) nos três métodos;
  - a mesma solução primal (`primal.build_primal_solution`, candidatos em todo
    V), calculada uma vez, FORA do limite de tempo, e entregue como MIP start
    ao COMP e ao BC-Y' e como incumbente inicial ao CBI;
  - o mesmo TL de solver (TL segundos) e os mesmos Threads/Seed.

Diferenças de método, declaradas no CSV: BC-Y' usa LazyConstraints=1 e
user cuts só quando |A_r| <= 500 mil; CBI usa PoolSearchMode=2.

Tempos: `t_solver_s` é o tempo do método (optimize do Gurobi no COMP e no
BC-Y'; laço inteiro no CBI); `t_total_s` inclui construção de modelo e
verificação. O primal tem coluna própria.

Métrica das instâncias (open-questions Q2): hc9u é o MIN-STATION de Das;
hc10p e bip42p têm pesos, mas A_r = E, o que as torna idênticas a Das com r=1;
cc12-2p é extensão ponderada; as TNTP são extensão ponderada e dirigida.

Uso: python run_e8.py [--seeds 42 43 44] [--tl 300]
Resultado: results/cuts/e8_comparative.csv
"""

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import gurobipy
from gurobipy import GRB
from baseline import construir_modelo_baseline
from harness import load_instance, prepare_cuts, measure_mip
from cuts import build_neighborhoods
from bc_yspace import solve_bc_yspace, solve_cbi
from primal import build_primal_solution
import synthetic as syn

INST_DIR = ROOT / 'instances'
OUT_CSV = ROOT / 'results' / 'cuts' / 'e8_comparative.csv'

THREADS = 4
PRIMAL_BUDGET = 60.0

# (arquivo, R override, regime, métrica, referência)
# Referências: Chicago/Barcelona provadas no E4/E7; Philadelphia st5 = 41 é
# referência histórica não reprovada nesta linha de trabalho. cc12-2p = 6
# certificado por verify_e8_cc12_opt.py (results/cuts/e8_certificado_cc12.txt).
INSTANCES = [
    ('Chicago_n400_m1130_st15.txt', 7, 'R-a', 'ponderada+dirigida', 17),
    ('Barcelona_n930_m2522_st_15.txt', 5, 'R-a', 'ponderada+dirigida', 15),
    ('Philadelphia_n800_m2404_st_5.txt', 2, 'R-a', 'ponderada+dirigida', 41),
    ('Philadelphia_n800_m2404_st_25.txt', 3, 'R-a', 'ponderada+dirigida', None),
    ('hc9u.txt', None, 'R-b', 'das', None),
    ('hc10p.txt', None, 'R-b', 'das(r=1 via A_r=E)', None),
    ('bip42p.txt', 200, "R-b'", 'das(r=1 via A_r=E)', None),
    ('cc12-2p.txt', 500, 'R-c', 'ponderada', 6),
]

HEADER = [
    'instancia', 'R', 'regime', 'metrica', 'n', 'm', 'n_arcos',
    'config', 'seed', 'n_static_cuts',
    'primal_obj', 'primal_t_s', 'primal_terminais',
    'obj', 'bound', 'gap', 'status', 't_solver_s', 't_total_s',
    'lazy_ou_iter', 'usercuts_ou_oraculo', 'params_metodo',
    'y_star_feasible_compacto',
    'ref_opt', 'threads', 'tl_s', 'gurobi', 'formulacao', 'commit',
]


def _commit():
    try:
        h = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                    cwd=ROOT, text=True).strip()
        sujo = subprocess.check_output(['git', 'status', '--porcelain'],
                                       cwd=ROOT, text=True).strip()
        return h + ('-dirty' if sujo else '')
    except Exception:
        return 'desconhecido'


GUROBI = '.'.join(map(str, gurobipy.gurobi.version()))
COMMIT = _commit()


def _verify_y(S, T, V, A_r, y_star):
    if y_star is None:
        return None
    modelo, y_c, _, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    for v in V:
        val = 1.0 if y_star.get(v, 0.0) > 0.5 else 0.0
        y_c[v].lb = val
        y_c[v].ub = val
    modelo.update()
    modelo.optimize()
    return 'FEASIBLE' if modelo.Status == GRB.OPTIMAL else 'INFEASIBLE'


def _status(code):
    return {2: 'OPT', 9: 'TL', 3: 'INF', 11: 'INTERROMPIDO'}.get(code, str(code))


def run_comp(S, T, V, A_r, cuts_spec, y_start, seed, tl):
    mip = measure_mip(S, T, V, A_r, 'cont', cuts_spec, seed=seed,
                      threads=THREADS, time_limit=tl, y_start=y_start)
    return {
        'obj': mip['mip_obj'], 'bound': mip['mip_bound'], 'gap': mip['mip_gap'],
        'status': _status(mip['mip_status']), 't_solver': mip['time_mip_s'],
        'x1': None, 'x2': None, 'params': 'default', 'y_star': None,
    }


def run_bcy(S, T, V, A_r, cuts_spec, y_start, seed, tl):
    res = solve_bc_yspace(S, T, V, A_r, static_cuts=cuts_spec, time_limit=tl,
                          seed=seed, threads=THREADS, use_lazy=True,
                          use_mip_start=False, y_start=y_start,
                          use_user_cuts=True)
    st = _status(res['status'])
    if res.get('tl_estourado'):
        st += '+guarda_TL'
    params = 'LazyConstraints=1;user_cuts=' + ('on' if res['user_cuts_ativos'] else 'off')
    return {
        'obj': res['obj'], 'bound': res['bound'], 'gap': res['gap'], 'status': st,
        't_solver': res['time_s'], 'x1': res['n_lazy_cuts'],
        'x2': res['n_user_cuts'], 'params': params, 'y_star': res.get('y_star'),
    }


def run_cbi(S, T, V, cuts_spec, N_plus, ub_start, seed, tl):
    res = solve_cbi(S, T, V, cuts_spec, N_plus, time_limit=tl, seed=seed,
                    threads=THREADS, ub_start=ub_start)
    return {
        'obj': res['obj'], 'bound': res['bound'], 'gap': res['gap'],
        'status': res['status'], 't_solver': res['time_s'],
        'x1': res['iterations'], 'x2': res['oracle_calls'],
        'params': 'PoolSearchMode=2;PoolSolutions=50', 'y_star': res.get('y_star'),
    }


def run_instance(fname, r_override, regime, metrica, ref_opt, seeds, tl):
    path = INST_DIR / fname
    if not path.exists():
        print(f'  {fname}: não encontrado — pulando', flush=True)
        return []
    S, T, V, adj, A_r, r = load_instance(path, R=r_override)
    n, m, na = len(V), len(S), len(A_r)
    print(f'\n  {fname}  (n={n}, m={m}, |A_r|={na}, R={r}, {metrica})', flush=True)

    t0 = time.monotonic()
    cuts_spec, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    N_plus, _ = build_neighborhoods(A_r)
    print(f'    cortes estáticos: {counts["unicos"]} (t={time.monotonic()-t0:.1f}s)', flush=True)

    t0 = time.monotonic()
    primal = build_primal_solution(S, T, V, N_plus, seed=42, total_budget=PRIMAL_BUDGET)
    primal_t = time.monotonic() - t0
    if primal is None:
        print('    primal: instância inviável — pulando', flush=True)
        return []
    y_start = primal['y_bin']
    ub_start = {'C': primal['C'], 'obj': primal['n_estacoes']}
    print(f'    primal: {primal["n_estacoes"]} estações '
          f'({primal["n_terminais_em_C"]} em terminais), t={primal_t:.1f}s', flush=True)

    rows = []
    for seed in seeds:
        for cfg, fn in [
            ('COMP', lambda: run_comp(S, T, V, A_r, cuts_spec, y_start, seed, tl)),
            ("BC-Y'", lambda: run_bcy(S, T, V, A_r, cuts_spec, y_start, seed, tl)),
            ('CBI', lambda: run_cbi(S, T, V, cuts_spec, N_plus, ub_start, seed, tl)),
        ]:
            t0 = time.monotonic()
            res = fn()
            feas = _verify_y(S, T, V, A_r, res['y_star']) if res['y_star'] else None
            dt = time.monotonic() - t0
            print(f'    [seed {seed}] {cfg:<6} obj={res["obj"]} bnd={res["bound"]} '
                  f'st={res["status"]} t_solver={res["t_solver"]:.1f}s '
                  f't_total={dt:.1f}s feas={feas}', flush=True)
            rows.append({
                'instancia': fname, 'R': r, 'regime': regime, 'metrica': metrica,
                'n': n, 'm': m, 'n_arcos': na, 'config': cfg, 'seed': seed,
                'n_static_cuts': counts['unicos'],
                'primal_obj': primal['n_estacoes'], 'primal_t_s': round(primal_t, 3),
                'primal_terminais': primal['n_terminais_em_C'],
                'obj': res['obj'], 'bound': res['bound'], 'gap': res['gap'],
                'status': res['status'], 't_solver_s': round(res['t_solver'], 3),
                't_total_s': round(dt, 3), 'lazy_ou_iter': res['x1'],
                'usercuts_ou_oraculo': res['x2'], 'params_metodo': res['params'],
                'y_star_feasible_compacto': feas, 'ref_opt': ref_opt,
                'threads': THREADS, 'tl_s': tl, 'gurobi': GUROBI,
                'formulacao': 'U', 'commit': COMMIT,
            })
    return rows


def smoke_test(tl=30):
    print('=== E8 smoke test nos gabaritos (primal + COMP + BC-Y\' + CBI) ===\n', flush=True)
    ok = True
    for label, fn in [
        ('Direct0', syn.make_Direct0), ('TermRelay', syn.make_TermRelay),
        ('TermRelayForced', syn.make_TermRelayForced),
        ('Tri', syn.make_Tri), ('StayPut', syn.make_StayPut),
        ('SharedTerminal', syn.make_SharedTerminal),
        ('Sec59', lambda: syn.make_Sec59(L=7, r=1)),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        opt_ref = meta.get('OPT')
        cuts_spec, _ = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
        N_plus, _ = build_neighborhoods(A_r)
        primal = build_primal_solution(S, T, V, N_plus, total_budget=5)
        partes = []
        if primal is None or _verify_y(S, T, V, A_r, primal['y_bin']) != 'FEASIBLE':
            ok = False
            partes.append('primal=FALHOU')
        else:
            partes.append(f'primal={primal["n_estacoes"]}')
            y_start = primal['y_bin']
            ub = {'C': primal['C'], 'obj': primal['n_estacoes']}
            for nome, res in [
                ('COMP', run_comp(S, T, V, A_r, cuts_spec, y_start, 42, tl)),
                ("BC-Y'", run_bcy(S, T, V, A_r, cuts_spec, y_start, 42, tl)),
                ('CBI', run_cbi(S, T, V, cuts_spec, N_plus, ub, 42, tl)),
            ]:
                good = (res['obj'] == opt_ref)
                if res['y_star'] is not None:
                    good = good and _verify_y(S, T, V, A_r, res['y_star']) == 'FEASIBLE'
                ok = ok and good
                partes.append(f'{nome}={res["obj"]}[{"OK" if good else "FAIL"}]')
        print(f'  {label:<16} OPT_ref={opt_ref}  ' + '  '.join(partes), flush=True)
    print(flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='+', default=[42])
    ap.add_argument('--tl', type=float, default=300)
    ap.add_argument('--so-smoke', action='store_true')
    args = ap.parse_args()

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not smoke_test():
        print('SMOKE FALHOU — abortando bateria.', flush=True)
        sys.exit(1)
    if args.so_smoke:
        return

    print(f'=== E8: COMP vs BC-Y\' vs CBI (TL={args.tl:.0f}s, seeds={args.seeds}, '
          f'gurobi={GUROBI}, commit={COMMIT}) ===', flush=True)
    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        for spec in INSTANCES:
            for row in run_instance(*spec, seeds=args.seeds, tl=args.tl):
                w.writerow(row)
            fh.flush()
    print(f'\n[E8] resultados em {OUT_CSV}', flush=True)


if __name__ == '__main__':
    main()
