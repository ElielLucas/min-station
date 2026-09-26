"""
E1': Validação em instâncias sintéticas.

Para cada instância: computa z_LP da BASE-C e depois com cada família de cortes
adicionada cumulativamente. Compara com os valores teóricos.

Resultado: results/cuts/e1_sinteticos.csv  +  saída PASS/FAIL no terminal.
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from harness import prepare_cuts, measure_lp, measure_mip
from synthetic import make_F1, make_F2, make_Tri, make_Sec59

OUT_CSV = ROOT / 'results' / 'cuts' / 'e1_sinteticos.csv'

SEED    = 42
THREADS = 1

HEADER = [
    'instancia', 'n', 'm', 'n_arcos',
    'config',
    'z_LP_obs', 'z_LP_teo',
    'n_c1', 'n_c2', 'n_c4', 'n_c3',
    'status', 'pass_fail',
]

TOL = 1e-4


def lp_value(S, T, V, adj, A_r, r, active_cuts, use_c3=False):
    cuts_spec, counts = prepare_cuts(S, T, V, adj, A_r, r, active_cuts)
    res = measure_lp(S, T, V, A_r, 'cont', cuts_spec,
                     use_c3=use_c3, c3_max_rounds=20,
                     seed=SEED, threads=THREADS)
    return res['lp_bound'], counts, res.get('n_c3_cuts', 0), res['lp_status']


def run_instance(maker_fn, meta_override=None):
    S, T, V, adj, A_r, r, meta = maker_fn()
    if meta_override:
        meta.update(meta_override)

    name    = meta['name']
    z_LP_t  = meta.get('z_LP')
    LP_cov  = meta.get('LP_cov')
    OPT     = meta.get('OPT')

    n = len(V)
    m = len(S)
    na = len(A_r)

    print(f'\n── {name}  (n={n}, m={m}, |A_r|={na}) ──────────')
    rows = []

    configs = [
        ('BASE-C',           set(),              False, z_LP_t),
        ('BASE-C+C1',        {'C1'},             False, None),
        ('BASE-C+C1+C2',     {'C1','C2'},        False, None),
        ('BASE-C+C1+C2+C4',  {'C1','C2','C4'},   False, LP_cov),
        ('BASE-C+C1+C2+C4+C3',{'C1','C2','C4'}, True,  LP_cov),
    ]

    for cfg_name, active, use_c3, teo in configs:
        try:
            val, counts, nc3, status = lp_value(S, T, V, adj, A_r, r, active, use_c3)
        except Exception as e:
            print(f'  {cfg_name}: ERRO {e}')
            continue

        pf = '?'
        if teo is not None and val is not None:
            pf = 'PASS' if abs(val - teo) <= TOL else 'FAIL'

        val_str = f'{val:.6f}' if val is not None else 'None'
        teo_str = f'{teo:.6f}' if teo is not None else '—'
        print(f'  {cfg_name:<30}  LP={val_str}  teo={teo_str}  {pf}')

        rows.append({
            'instancia': name,
            'n':         n,
            'm':         m,
            'n_arcos':   na,
            'config':    cfg_name,
            'z_LP_obs':  val,
            'z_LP_teo':  teo,
            'n_c1':      counts.get('C1', 0),
            'n_c2':      counts.get('C2', 0),
            'n_c4':      counts.get('C4', 0),
            'n_c3':      nc3,
            'status':    status,
            'pass_fail': pf,
        })

    # Verifica OPT via MIP completo na instância BASE-C sem cortes
    if OPT is not None:
        mip = measure_mip(S, T, V, A_r, 'cont', [], seed=SEED, threads=THREADS, time_limit=60)
        obs_opt = mip['mip_obj']
        pf = 'PASS' if (obs_opt is not None and abs(obs_opt - OPT) <= TOL) else 'FAIL'
        print(f'  OPT verificado: obs={obs_opt}  teo={OPT}  {pf}')

    return rows


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []

    # F1 com m=2, k=2
    all_rows += run_instance(lambda: make_F1(m=2, k=2, r=1))

    # F1 com m=2, k=3  (z_LP=7, OPT=13)
    all_rows += run_instance(lambda: make_F1(m=2, k=3, r=1))

    # F2 com k=1
    all_rows += run_instance(lambda: make_F2(k=1, L=3, r=1))

    # F2 com k=2
    all_rows += run_instance(lambda: make_F2(k=2, L=3, r=1))

    # Tri
    all_rows += run_instance(make_Tri)

    # §5.9 com L=7 (BC-y sem cortes clássicos dá raiz=2 < z_LP=7/3)
    all_rows += run_instance(lambda: make_Sec59(L=7, r=1))

    with OUT_CSV.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)

    print(f'\n[E1\'] {len(all_rows)} linhas salvas em {OUT_CSV}')

    # Resumo
    fails = [r for r in all_rows if r['pass_fail'] == 'FAIL']
    if fails:
        print(f'\nATENÇÃO: {len(fails)} verificação(ões) FAIL:')
        for r in fails:
            print(f"  {r['instancia']} / {r['config']}: obs={r['z_LP_obs']} teo={r['z_LP_teo']}")
    else:
        n_checked = sum(1 for r in all_rows if r['pass_fail'] in ('PASS', 'FAIL'))
        print(f'\nTodos os {n_checked} testes verificáveis: PASS')


if __name__ == '__main__':
    main()
