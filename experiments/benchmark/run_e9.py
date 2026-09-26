"""
E9: diagnóstico de raiz nas instâncias difíceis (D/A) do benchmark-v1, mais
oito instâncias F de regressão (uma por família, a de menor |A_r|).

Pergunta (plano-pos-e8-adiado.md, repriorização 2026-09-26): nas instâncias
difíceis fiéis a Das, o gap é dual ou primal, e qual família de cortes o
produz? Mede, por instância:

  (a) z_LP puro (sem cortes a priori);
  (b) + C1;
  (c) + C1 + C2;
  (d) + C1 + C2 + C4  (controle — igual ao protocolo de dificuldade);
  (g) IP do núcleo de cobertura (C1+C2+C4, y binário, sem fluxo), TL 60 s —
      LB da primeira iteração do CBI (as seguintes acrescentam cortes 𝒵 e
      só podem subir);
  L_bot: limite combinatório provado (bounds_r6.py).

Escopo restrito em relação ao plano original: NÃO inclui (e) C3 exato
iterado nem os itens de R6 além de L_bot. C3 exige um oráculo fracionário
restrito a S∪T∪supp(y*) (como integer_oracle, mas para y contínuo) que
ainda não existe — sem ele, check_C3_violations materializa A_r inteiro por
origem e por rodada, o que é o mesmo tipo de custo que travou o E7 nas
instâncias com |A_r| grande (até 1,9 milhão aqui). Os demais itens de R6
(bandas, empacotamento) dependem de escolhas não especificadas sem
ambiguidade (ver bounds_r6.py). Registrado como pendência, não decidido
silenciosamente.

Uso: python experiments/benchmark/run_e9.py [--fatia 1/3] [--tl-nucleo 60]
"""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(ROOT / 'experiments' / 'benchmark'))

from harness import load_instance, prepare_cuts, measure_lp
from cuts import build_neighborhoods
from yspace import solve_ip_yspace
from bounds_r6 import l_bot

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT_DIR = ROOT / 'results' / 'benchmark'
CAMPOS = [
    'nome', 'familia', 'caminho', 'classe_dif', 'regime', 'n', 'm', 'r', 'n_arcos_alcance',
    'ub_ref', 'fonte_ub',
    'z_lp', 'z_lp_status', 't_zlp_s',
    'root_c1', 'c1_status', 'n_c1', 't_c1_s',
    'root_c1c2', 'c1c2_status', 'n_c1c2', 't_c1c2_s',
    'root_c1c2c4', 'c1c2c4_status', 'n_c1c2c4', 't_c1c2c4_s',
    'ip_nucleo_obj', 'ip_nucleo_bound', 'ip_nucleo_status', 't_nucleo_s',
    'l_bot', 't_lbot_s',
    'threads', 'seed', 'tl_nucleo_s',
]


def selecionar_instancias():
    linhas = [r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))
              if r['caminho'].startswith('instances/benchmark-v1/')]
    da = [r for r in linhas if r['dificuldade'] in ('D', 'A')]

    fam = {}
    for r in linhas:
        fam.setdefault(r['caminho'].split('/')[2], []).append(r)
    f_regressao = []
    for f, g in sorted(fam.items()):
        fs = [r for r in g if r['dificuldade'] == 'F']
        if fs:
            f_regressao.append(min(fs, key=lambda r: int(r['n_arcos_alcance'])))

    vistos = set()
    selecionadas = []
    for r in da + f_regressao:
        if r['nome'] not in vistos:
            vistos.add(r['nome'])
            selecionadas.append(r)
    return selecionadas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--tl-nucleo', type=float, default=60)
    ap.add_argument('--tl-lp', type=float, default=300)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))

    linhas = selecionar_instancias()
    linhas.sort(key=lambda r: int(r['n_arcos_alcance']))
    minhas = [r for i, r in enumerate(linhas) if i % n == k - 1]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / (f'e9_raiz_fatia{k}.csv' if n > 1 else 'e9_raiz.csv')
    feitas = set()
    if out.exists():
        feitas = {r['nome'] for r in csv.DictReader(out.open(encoding='utf-8'))}
    novo = not out.exists()

    with out.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for row in minhas:
            if row['nome'] in feitas:
                continue
            t0 = time.monotonic()
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            N_plus, _ = build_neighborhoods(A_r)

            base = {
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'caminho': row['caminho'], 'classe_dif': row['dificuldade'],
                'regime': row['regime'], 'n': len(V), 'm': len(S), 'r': r,
                'n_arcos_alcance': len(A_r),
                'ub_ref': row['ub_melhor'] or row['ub'], 'fonte_ub': 'ub_melhor' if row['ub_melhor'] else 'ub (protocolo COMP)',
                'threads': 4, 'seed': 42, 'tl_nucleo_s': args.tl_nucleo,
            }

            t1 = time.monotonic()
            res_a = measure_lp(S, T, V, A_r, 'cont', [], time_limit=args.tl_lp)
            base['z_lp'] = res_a['lp_bound']
            base['z_lp_status'] = res_a['lp_status']
            base['t_zlp_s'] = round(time.monotonic() - t1, 3)

            t1 = time.monotonic()
            cortes_c1, cont_c1 = prepare_cuts(S, T, V, adj, A_r, r, {'C1'})
            res_b = measure_lp(S, T, V, A_r, 'cont', cortes_c1, time_limit=args.tl_lp)
            base['root_c1'] = res_b['lp_bound']
            base['c1_status'] = res_b['lp_status']
            base['n_c1'] = cont_c1['unicos']
            base['t_c1_s'] = round(time.monotonic() - t1, 3)

            t1 = time.monotonic()
            cortes_c1c2, cont_c1c2 = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2'})
            res_c = measure_lp(S, T, V, A_r, 'cont', cortes_c1c2, time_limit=args.tl_lp)
            base['root_c1c2'] = res_c['lp_bound']
            base['c1c2_status'] = res_c['lp_status']
            base['n_c1c2'] = cont_c1c2['unicos']
            base['t_c1c2_s'] = round(time.monotonic() - t1, 3)

            t1 = time.monotonic()
            cortes_ctrl, cont_ctrl = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res_d = measure_lp(S, T, V, A_r, 'cont', cortes_ctrl, time_limit=args.tl_lp)
            base['root_c1c2c4'] = res_d['lp_bound']
            base['c1c2c4_status'] = res_d['lp_status']
            base['n_c1c2c4'] = cont_ctrl['unicos']
            base['t_c1c2c4_s'] = round(time.monotonic() - t1, 3)

            t1 = time.monotonic()
            res_g = solve_ip_yspace(S, T, V, adj, A_r, r, time_limit=args.tl_nucleo,
                                     seed=42, threads=4, validate_cuts=False)
            base['ip_nucleo_obj'] = res_g['ip_obj']
            base['ip_nucleo_bound'] = res_g['ip_bound']
            base['ip_nucleo_status'] = res_g['ip_status']
            base['t_nucleo_s'] = round(time.monotonic() - t1, 3)

            t1 = time.monotonic()
            base['l_bot'] = l_bot(S, T, N_plus)
            base['t_lbot_s'] = round(time.monotonic() - t1, 3)

            w.writerow(base)
            fh.flush()
            t_total = time.monotonic() - t0
            print(f'{row["nome"]:38s} z_lp={_f(base["z_lp"])} c1={_f(base["root_c1"])} '
                  f'c1c2={_f(base["root_c1c2"])} ctrl={_f(base["root_c1c2c4"])} '
                  f'nucleo={_f(base["ip_nucleo_bound"])} l_bot={_f(base["l_bot"])} '
                  f'ub={base["ub_ref"]}  t={t_total:.1f}s', flush=True)


def _f(x):
    return f'{x:.2f}' if isinstance(x, (int, float)) else str(x)


if __name__ == '__main__':
    main()
