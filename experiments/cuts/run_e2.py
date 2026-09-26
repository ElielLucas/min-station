"""
E2: Laço de planos de corte só em y (LP) — 4 estágios cumulativos.
E3: IP em y-space (núcleo de cobertura inteiro).

Resultados:
  results/cuts/e2_yspace.csv
  results/cuts/e3_cobertura_ip.csv

Não use lin23, lin37 (pesadas demais para validação rápida).
"""

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from harness import load_instance
from yspace import solve_lp_cutting_plane, solve_ip_yspace
from synthetic import make_F1, make_F2, make_Tri, make_Sec59

INST_DIR  = ROOT / 'instances'
OUT_E2    = ROOT / 'results' / 'cuts' / 'e2_yspace.csv'
OUT_E3    = ROOT / 'results' / 'cuts' / 'e3_cobertura_ip.csv'

SEED      = 42
THREADS   = 4
MAX_ROUNDS = 30
TIME_STAGE = 600   # s por estágio no LP
TIME_IP    = 600   # s para o IP em E3


# ── Instâncias E2 (LP) ────────────────────────────────────────────────────────
# R corresponde às referências históricas, não ao R gravado no arquivo, quando
# houver override (Chicago st15: R=26 no arquivo é trivial, referência é R=7).

E2_INSTANCES_REAL = [
    # regime R-b
    ('hc9u.txt', None),
    ('hc10p.txt', None),
    # regime R-a
    ('Philadelphia_n800_m2404_st_25.txt', None),
    ('Barcelona_n930_m2522_st_25.txt', None),
    ('Chicago_n400_m1130_st15.txt', 7),
    ('Barcelona_n930_m2522_st_50.txt', None),   # se existir
    # regime R-c
    ('cc10-2p.txt', None),
    # cc12-2p só se couber no tempo
]


# ── Instâncias E3 (IP) ────────────────────────────────────────────────────────

E3_INSTANCES_REAL = [
    # R-b (leve em y)
    ('hc9u.txt', None),
    ('hc10p.txt', None),
    ('hc11p.txt', None),
    ('hc12p.txt', None),
    ('bip42p.txt', None),
    # R-a
    ('Philadelphia_n800_m2404_st_25.txt', None),
    ('Barcelona_n930_m2522_st_50.txt', None),
    # R-c
    ('cc10-2p.txt', None),
    ('cc12-2p.txt', None),
]


HEADER_E2 = [
    'instancia', 'R', 'r_origem', 'n', 'm', 'n_arcos',
    'lp_s1', 'lp_s2', 'lp_s3', 'lp_s4',
    'cuts_s1', 'cuts_s2', 'cuts_s3', 'cuts_s4',
    'time_s1', 'time_s2', 'time_s3', 'time_s4',
    'total_time', 'validado', 'seed', 'threads',
]

HEADER_E3 = [
    'instancia', 'R', 'r_origem', 'n', 'm', 'n_arcos',
    'n_static_cuts', 'n_c1', 'n_c2', 'n_c4',
    'ip_obj', 'ip_bound', 'ip_gap', 'ip_status', 'time_s',
    'validado', 'seed', 'threads',
]

# E2 valida por padrão (é onde C3/fracs clássicos/C5 são separados
# dinamicamente — as famílias do defeito encontrado na rodada E5).
VALIDATE_E2 = True
# E3 só usa C1+C2+C4 estáticos, já auditados por oráculo nos gabaritos;
# validar custaria O(|A_r|) por corte sem ganho. Ligar caso a caso se
# necessário (fica registrado na coluna 'validado' do CSV).
VALIDATE_E3 = False


def _fmt(v, decimals=4):
    if v is None:
        return 'None'
    return f'{v:.{decimals}f}'


# ── Gabaritos sintéticos para E2 ─────────────────────────────────────────────

def run_e2_synthetic():
    """Verifica os gabaritos antes das instâncias reais."""
    print('\n=== E2: Gabaritos sintéticos ===')
    ok = True

    cases = [
        ('§5.9(L=7)', lambda: make_Sec59(L=7, r=1),
         {1: 2.0, 3: 7.0, 4: 7.0}),  # fecha em 7 já no estágio 3 (fracs clássicos
                                     # corrigidos, E5); C5 (estágio 4) não é necessário
        ('F2(k=1)',   lambda: make_F2(k=1, L=3, r=1),
         {1: 1.0}),             # C4-DM fecha em 1 no estágio 1
        ('Tri',       make_Tri,
         {1: 1.5}),             # C1 fecha em 1.5 no estágio 1
    ]

    for name, maker, expected in cases:
        S, T, V, adj, A_r, r, _ = maker()
        res = solve_lp_cutting_plane(S, T, V, adj, A_r, r,
                                     max_rounds=MAX_ROUNDS,
                                     time_per_stage=60,
                                     seed=SEED, threads=1)
        for stage, exp_val in expected.items():
            obs = res['stage_lp'].get(stage)
            ok_s = obs is not None and abs(obs - exp_val) < 0.01
            tag  = 'PASS' if ok_s else 'FAIL'
            if not ok_s:
                ok = False
            print(f'  {name} estágio {stage}: obs={_fmt(obs)} exp={_fmt(exp_val,4)} {tag}')

    if not ok:
        print('\nABORTANDO: gabarito(s) falhou. Verificar implementação.')
        sys.exit(1)

    print('  Todos os gabaritos PASS.\n')


# ── Runner E2 ─────────────────────────────────────────────────────────────────

def run_e2():
    print('\n=== E2: LP em y-space (instâncias reais) ===')
    OUT_E2.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    for fname, r_override in E2_INSTANCES_REAL:
        path = INST_DIR / fname
        if not path.exists():
            print(f'  {fname}: não encontrado — pulando')
            continue

        try:
            S, T, V, adj, A_r, r = load_instance(path, R=r_override)
        except Exception as e:
            print(f'  {fname}: erro ao carregar — {e}')
            continue
        r_origem = 'override' if r_override is not None else 'arquivo'

        n, m, na = len(V), len(S), len(A_r)
        print(f'\n  {fname}  (n={n}, m={m}, |A_r|={na}, R={r}, {r_origem})')

        res = solve_lp_cutting_plane(S, T, V, adj, A_r, r,
                                     max_rounds=MAX_ROUNDS,
                                     time_per_stage=TIME_STAGE,
                                     seed=SEED, threads=THREADS,
                                     validate_cuts=VALIDATE_E2)

        sl = res['stage_lp']
        sc = res['stage_cuts']
        st = res['stage_time']

        print(f'    S1: LP={_fmt(sl[1])} ({sc[1]} cortes, {_fmt(st[1],1)}s)')
        print(f'    S2: LP={_fmt(sl[2])} (+{sc[2]} C3, {_fmt(st[2],1)}s)')
        print(f'    S3: LP={_fmt(sl[3])} (+{sc[3]} fracs, {_fmt(st[3],1)}s)')
        print(f'    S4: LP={_fmt(sl[4])} (+{sc[4]} C5, {_fmt(st[4],1)}s)')
        print(f'    total={_fmt(res["total_time"],1)}s')

        rows.append({
            'instancia':  fname,
            'R':          r,
            'r_origem':   r_origem,
            'n':          n,
            'm':          m,
            'n_arcos':    na,
            'lp_s1':      sl[1],
            'lp_s2':      sl[2],
            'lp_s3':      sl[3],
            'lp_s4':      sl[4],
            'cuts_s1':    sc[1],
            'cuts_s2':    sc[2],
            'cuts_s3':    sc[3],
            'cuts_s4':    sc[4],
            'time_s1':    round(st[1], 3),
            'time_s2':    round(st[2], 3),
            'time_s3':    round(st[3], 3),
            'time_s4':    round(st[4], 3),
            'total_time': round(res['total_time'], 3),
            'validado':   VALIDATE_E2,
            'seed':       SEED,
            'threads':    THREADS,
        })

    with OUT_E2.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER_E2)
        w.writeheader()
        w.writerows(rows)

    print(f'\n[E2] {len(rows)} instâncias salvas em {OUT_E2}')
    return rows


# ── Runner E3 ─────────────────────────────────────────────────────────────────

def run_e3():
    print('\n=== E3: IP em y-space (núcleo de cobertura) ===')
    OUT_E3.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    for fname, r_override in E3_INSTANCES_REAL:
        path = INST_DIR / fname
        if not path.exists():
            print(f'  {fname}: não encontrado — pulando')
            continue

        try:
            S, T, V, adj, A_r, r = load_instance(path, R=r_override)
        except Exception as e:
            print(f'  {fname}: erro ao carregar — {e}')
            continue
        r_origem = 'override' if r_override is not None else 'arquivo'

        n, m, na = len(V), len(S), len(A_r)
        print(f'\n  {fname}  (n={n}, m={m}, |A_r|={na}, R={r}, {r_origem})')

        res = solve_ip_yspace(S, T, V, adj, A_r, r,
                              time_limit=TIME_IP, seed=SEED, threads=THREADS,
                              validate_cuts=VALIDATE_E3)

        status_map = {1: 'loaded', 2: 'optimal', 3: 'infeasible', 5: 'unbounded',
                      9: 'TL', 11: 'interrupted'}
        st_name = status_map.get(res['ip_status'], str(res['ip_status']))

        print(f'    cortes: {res["n_static_cuts"]} '
              f'(C1={res["n_c1"]}, C2={res["n_c2"]}, C4={res["n_c4"]})')
        print(f'    OBJ={_fmt(res["ip_obj"])}  bound={_fmt(res["ip_bound"])}  '
              f'gap={_fmt(res["ip_gap"])}  status={st_name}  t={_fmt(res["time_s"],1)}s')

        rows.append({
            'instancia':     fname,
            'R':             r,
            'r_origem':      r_origem,
            'n':             n,
            'm':             m,
            'n_arcos':       na,
            'n_static_cuts': res['n_static_cuts'],
            'n_c1':          res['n_c1'],
            'n_c2':          res['n_c2'],
            'n_c4':          res['n_c4'],
            'ip_obj':        res['ip_obj'],
            'ip_bound':      res['ip_bound'],
            'ip_gap':        res['ip_gap'],
            'ip_status':     res['ip_status'],
            'time_s':        round(res['time_s'], 3),
            'validado':      VALIDATE_E3,
            'seed':          SEED,
            'threads':       THREADS,
        })

    with OUT_E3.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER_E3)
        w.writeheader()
        w.writerows(rows)

    print(f'\n[E3] {len(rows)} instâncias salvas em {OUT_E3}')
    return rows


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    run_e2_synthetic()
    run_e2()
    run_e3()


if __name__ == '__main__':
    main()
