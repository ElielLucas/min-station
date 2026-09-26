"""
E7: BC-y completo vs compacto (COMP) — bateria comparativa.

Pergunta: o branch-and-cut só em y (família 𝒵, Teorema 6) supera o
modelo compacto nos regimes R-a (grafos reais), R-b (hipercubo/bip) e
R-c (grafos grandes)?

Configurações por instância:
  COMP  : compacto (fluxo contínuo) + C1+C2+C4 estáticos, TL=300 s
  BC-Y  : bc_yspace com C1 estático + lazy MIPSOL + user cuts MIPNODE
           + MIP start guloso, TL=300 s

Resultado: results/cuts/e7_comparative.csv
"""

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from baseline import construir_modelo_baseline
from harness import load_instance, prepare_cuts, measure_mip
from bc_yspace import solve_bc_yspace, prepare_static_c1
import synthetic as syn

INST_DIR = ROOT / 'instances'
OUT_CSV  = ROOT / 'results' / 'cuts' / 'e7_comparative.csv'

SEED    = 42
THREADS = 4
TL      = 300

INSTANCES = [
    # (fname, R_override, regime, ref_opt)
    ('Chicago_n400_m1130_st15.txt',       7,    'R-a', 17),
    ('Barcelona_n930_m2522_st_15.txt',    5,    'R-a', 15),
    ('Philadelphia_n800_m2404_st_5.txt',  2,    'R-a', 41),
    ('Philadelphia_n800_m2404_st_25.txt', 3,    'R-a', None),
    ('hc9u.txt',                          None, 'R-b', None),
    ('bip42p.txt',                        200,  "R-b'", None),
    ('cc12-2p.txt',                       500,  'R-c', None),
]

HEADER = [
    'instancia', 'R', 'regime', 'n', 'm', 'n_arcos',
    'config',
    'n_static_cuts',
    'obj', 'bound', 'gap', 'status',
    'time_s',
    'n_lazy_cuts', 'n_lazy_calls',
    'n_user_cuts', 'n_user_calls',
    'callback_time_s', 'cb_fraction',
    'bcy_sol_feasible',
    'ref_opt', 'seed', 'threads',
]


def _verify_bcy_sol(S, T, V, A_r, y_star):
    """Fixa y=y_star no compacto e retorna 'FEASIBLE'/'INFEASIBLE'/None."""
    if y_star is None:
        return None
    try:
        modelo, y_c, _, _, _ = construir_modelo_baseline(S, T, V, A_r)
        modelo.Params.OutputFlag = 0
        for v in V:
            val = 1.0 if y_star.get(v, 0.0) > 0.5 else 0.0
            y_c[v].lb = val
            y_c[v].ub = val
        modelo.update()
        modelo.optimize()
        return 'FEASIBLE' if modelo.Status == GRB.OPTIMAL else 'INFEASIBLE'
    except Exception as e:
        return f'ERROR:{e}'


def run_comp(fname, S, T, V, adj, A_r, r, regime, ref_opt):
    """Executa configuração COMP (compacto + C1+C2+C4)."""
    cuts_spec, counts = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
    n_cuts = counts['unicos']
    mip = measure_mip(S, T, V, A_r, 'cont', cuts_spec,
                      seed=SEED, threads=THREADS, time_limit=TL)
    status_map = {2: 'OPT', 9: 'TL', 11: 'INT', 3: 'INF'}
    st = status_map.get(mip['mip_status'], str(mip['mip_status']))
    print(f'    COMP     obj={mip["mip_obj"]}  bnd={mip["mip_bound"]}  '
          f'gap={mip["mip_gap"]}  st={st}  t={mip["time_mip_s"]:.1f}s')
    return {
        'instancia': fname, 'R': r, 'regime': regime,
        'n': len(V), 'm': len(S), 'n_arcos': len(A_r),
        'config': 'COMP',
        'n_static_cuts': n_cuts,
        'obj': mip['mip_obj'], 'bound': mip['mip_bound'],
        'gap': mip['mip_gap'], 'status': st,
        'time_s': round(mip['time_mip_s'], 3),
        'n_lazy_cuts': None, 'n_lazy_calls': None,
        'n_user_cuts': None, 'n_user_calls': None,
        'callback_time_s': None, 'cb_fraction': None,
        'bcy_sol_feasible': None,
        'ref_opt': ref_opt, 'seed': SEED, 'threads': THREADS,
    }


def run_bcy(fname, S, T, V, adj, A_r, r, regime, ref_opt):
    """Executa configuração BC-Y (bc_yspace com C1 + lazy + user cuts + MIP start)."""
    static = prepare_static_c1(S, T, A_r)
    n_cuts = len(set(map(frozenset, static)))

    t0 = time.monotonic()
    res = solve_bc_yspace(
        S, T, V, A_r,
        static_cuts=static,
        time_limit=TL,
        seed=SEED, threads=THREADS,
        use_lazy=True,
        use_mip_start=True,
        use_user_cuts=True,
        max_node_user_cuts=200,
    )
    elapsed = time.monotonic() - t0

    status_map = {2: 'OPT', 9: 'TL', 11: 'INT', 3: 'INF'}
    st = status_map.get(res['status'], str(res['status']))
    print(f'    BC-Y     obj={res["obj"]}  bnd={res["bound"]}  '
          f'gap={res["gap"]}  st={st}  t={res["time_s"]:.1f}s  '
          f'lazy={res["n_lazy_cuts"]}  uc={res["n_user_cuts"]}  '
          f'cb={res["cb_fraction"]:.1%}')

    # verifica a solução BC-Y no compacto usando o y* real do incumbente
    feasible = None
    if res.get('y_star') is not None:
        feasible = _verify_bcy_sol(S, T, V, A_r, res['y_star'])

    return {
        'instancia': fname, 'R': r, 'regime': regime,
        'n': len(V), 'm': len(S), 'n_arcos': len(A_r),
        'config': 'BC-Y',
        'n_static_cuts': n_cuts,
        'obj': res['obj'], 'bound': res['bound'],
        'gap': res['gap'], 'status': st,
        'time_s': round(res['time_s'], 3),
        'n_lazy_cuts': res['n_lazy_cuts'], 'n_lazy_calls': res['n_lazy_calls'],
        'n_user_cuts': res['n_user_cuts'], 'n_user_calls': res['n_user_calls'],
        'callback_time_s': round(res['callback_time_s'], 3),
        'cb_fraction': round(res['cb_fraction'], 4),
        'bcy_sol_feasible': feasible,
        'ref_opt': ref_opt, 'seed': SEED, 'threads': THREADS,
    }


def run_instance(fname, r_override, regime, ref_opt):
    path = INST_DIR / fname
    if not path.exists():
        print(f'  {fname}: não encontrado — pulando')
        return []

    try:
        S, T, V, adj, A_r, r = load_instance(path, R=r_override)
    except Exception as e:
        print(f'  {fname}: erro ao carregar — {e}')
        return []

    print(f'\n  {fname}  (n={len(V)}, m={len(S)}, |A_r|={len(A_r)}, R={r})')

    rows = []
    rows.append(run_comp(fname, S, T, V, adj, A_r, r, regime, ref_opt))
    rows.append(run_bcy(fname, S, T, V, adj, A_r, r, regime, ref_opt))
    return rows


# ── Smoke test em gabaritos ───────────────────────────────────────────────────

def smoke_test():
    """Testa BC-Y nos gabaritos pequenos. Aborta se algum falhar."""
    print('=== E7 Smoke test nos gabaritos ===\n')
    ok = True
    for label, fn in [
        ('Direct0', syn.make_Direct0),
        ('TermRelay', syn.make_TermRelay),
        ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut),
        ('SharedTerminal', syn.make_SharedTerminal),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        static = prepare_static_c1(S, T, A_r)
        try:
            res = solve_bc_yspace(S, T, V, A_r, static_cuts=static,
                                  time_limit=30, seed=SEED, threads=2,
                                  use_lazy=True, use_mip_start=True,
                                  use_user_cuts=True)
            expected = meta.get('OPT')
            got = res['obj']
            match = (got == expected) if expected is not None else True
            tag = 'PASS' if match else 'FAIL'
            print(f'  {label:<16} OPT esperado={expected}  obtido={got}  '
                  f'lazy={res["n_lazy_cuts"]}  uc={res["n_user_cuts"]}  [{tag}]')
            if not match:
                ok = False
        except Exception as e:
            print(f'  {label:<16} EXCEÇÃO: {type(e).__name__}: {e}')
            ok = False
    print()
    return ok


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    if not smoke_test():
        print('SMOKE FALHOU — abortando bateria.')
        return

    print('=== E7: Bateria BC-Y vs COMP (TL=300s) ===')
    all_rows = []
    for fname, r_override, regime, ref_opt in INSTANCES:
        rows = run_instance(fname, r_override, regime, ref_opt)
        all_rows.extend(rows)

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)

    print(f'\n[E7] {len(all_rows)} linhas salvas em {OUT_CSV}')

    # Resumo
    print('\n=== Resumo E7: BC-Y vs COMP ===')
    print(f'  {"Instância":<40} {"Config":<8} {"obj":>5} {"bnd":>6} {"gap":>7} {"t":>6}  st')
    for row in all_rows:
        inst = row['instancia'].replace('.txt', '')
        obj  = f'{row["obj"]}' if row['obj'] is not None else '-'
        bnd  = f'{row["bound"]:.1f}' if row['bound'] is not None else '-'
        gap  = f'{row["gap"]:.4f}' if row['gap'] is not None else '-'
        t    = f'{row["time_s"]:.0f}s'
        print(f'  {inst:<40} {row["config"]:<8} {obj:>5} {bnd:>6} {gap:>7} {t:>6}  {row["status"]}')


if __name__ == '__main__':
    main()
