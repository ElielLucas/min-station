"""
E10b: primal por reparo da solução do núcleo de cobertura, nas 30 instâncias
D/A do benchmark-v1.

Pergunta (resultados-e9-e10-pli.md): o gap de MAPF/Vienna é primal ou dual?
Nenhum construtor do E10 alcançou o UB do COMP; o reverse-delete a partir de
C = V não escala e o H3 a partir de C = ∅ usava um desempate ruim.

Fase `construcao`: núcleo (C1+C2+C4, y binário, TL 60 s) → reparo guloso a
partir da solução do núcleo → poda → busca local, até 120 s
(`primal.build_primal_from_core`). Compara com o UB do COMP@600 s do
protocolo de dificuldade e grava a solução em e10b_starts[_fatiaK].jsonl.

Fase `comp`: roda o COMP (U + C1+C2+C4, 4 threads, seed 42, TL 600 s) com
essa solução como MIP start, nas instâncias em que o reparo venceu o UB do
COMP, para ver se o LB também se move.

Critério (plano): reparo < UB do COMP em ≥ 50% das MAPF/Vienna ⇒ o gargalo
era primal. Reparo ≈ UB do COMP e LB parado ⇒ evidência de gap dual.

Uso:
  python experiments/benchmark/run_e10b.py --fase construcao [--fatia 1/3]
  python experiments/benchmark/run_e10b.py --fase comp [--fatia 1/3]
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from harness import load_instance, prepare_cuts, measure_mip
from cuts import build_neighborhoods, integer_oracle
from yspace import solve_ip_yspace
from primal import build_primal_from_core

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT_DIR = ROOT / 'results' / 'benchmark'
CAMPOS_CONSTR = [
    'nome', 'familia', 'regime', 'n', 'm', 'n_arcos_alcance',
    'lb_comp_600s', 'ub_comp_600s',
    'nucleo_obj', 'nucleo_bound', 'nucleo_status', 't_nucleo_s',
    'n_reparo', 'n_poda', 'n_final', 't_reparo_s', 't_primal_s',
    'vence_comp600', 'seed', 'tl_nucleo_s', 'tl_primal_s',
]
CAMPOS_COMP = [
    'nome', 'familia', 'regime', 'n_start', 'lb_comp_600s', 'ub_comp_600s',
    'lb_com_start', 'ub_com_start', 'gap_com_start', 'status', 't_solver_s',
    'seed', 'threads', 'tl_s',
]


def instancias_da():
    linhas = [r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))
              if r['caminho'].startswith('instances/benchmark-v1/') and r['dificuldade'] in ('D', 'A')]
    linhas.sort(key=lambda r: int(r['n_arcos_alcance']))
    return linhas


def _abrir(out, campos):
    feitas = set()
    if out.exists():
        feitas = {r['nome'] for r in csv.DictReader(out.open(encoding='utf-8'))}
    novo = not out.exists()
    fh = out.open('a', newline='', encoding='utf-8')
    w = csv.DictWriter(fh, fieldnames=campos)
    if novo:
        w.writeheader()
    return fh, w, feitas


def _f(x):
    return float(x) if x not in ('', None) else None


def fase_construcao(minhas, k, n, args):
    out = OUT_DIR / (f'e10b_construcao_fatia{k}.csv' if n > 1 else 'e10b_construcao.csv')
    starts = OUT_DIR / (f'e10b_starts_fatia{k}.jsonl' if n > 1 else 'e10b_starts.jsonl')
    fh, w, feitas = _abrir(out, CAMPOS_CONSTR)
    with fh:
        for row in minhas:
            if row['nome'] in feitas:
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            N_plus, _ = build_neighborhoods(A_r)

            t0 = time.monotonic()
            nuc = solve_ip_yspace(S, T, V, adj, A_r, r, time_limit=args.tl_nucleo,
                                  seed=args.seed, threads=4)
            t_nuc = time.monotonic() - t0

            res = None
            if nuc['C'] is not None:
                res = build_primal_from_core(S, T, V, N_plus, nuc['C'], seed=args.seed,
                                             total_budget=args.tl_primal)
            ub600 = _f(row['ub'])
            n_final = res['n_estacoes'] if res else None
            if res:
                assert integer_oracle(S, T, N_plus, res['C'])[0]
                with starts.open('a', encoding='utf-8') as fs:
                    fs.write(json.dumps({'nome': row['nome'], 'C': sorted(res['C'])}) + '\n')

            w.writerow({
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'regime': row['regime'], 'n': len(V), 'm': len(S), 'n_arcos_alcance': len(A_r),
                'lb_comp_600s': _f(row['lb']), 'ub_comp_600s': ub600,
                'nucleo_obj': nuc['ip_obj'], 'nucleo_bound': nuc['ip_bound'],
                'nucleo_status': nuc['ip_status'], 't_nucleo_s': round(t_nuc, 2),
                'n_reparo': res['n_reparo'] if res else None,
                'n_poda': res['n_poda'] if res else None,
                'n_final': n_final,
                't_reparo_s': round(res['t_reparo_s'], 2) if res else None,
                't_primal_s': round(res['tempo_s'], 2) if res else None,
                'vence_comp600': (n_final is not None and (ub600 is None or n_final < ub600)),
                'seed': args.seed, 'tl_nucleo_s': args.tl_nucleo, 'tl_primal_s': args.tl_primal,
            })
            fh.flush()
            print(f'{row["nome"]:38s} nucleo={nuc["ip_obj"]} reparo={res["n_reparo"] if res else None} '
                  f'final={n_final} ub600={ub600}', flush=True)


def fase_comp(minhas, k, n, args):
    construcao = {}
    for arq in OUT_DIR.glob('e10b_construcao*.csv'):
        for r in csv.DictReader(arq.open(encoding='utf-8')):
            construcao[r['nome']] = r
    starts = {}
    for arq in OUT_DIR.glob('e10b_starts*.jsonl'):
        for ln in arq.open(encoding='utf-8'):
            d = json.loads(ln)
            starts[d['nome']] = set(d['C'])

    out = OUT_DIR / (f'e10b_comp_fatia{k}.csv' if n > 1 else 'e10b_comp.csv')
    fh, w, feitas = _abrir(out, CAMPOS_COMP)
    with fh:
        for row in minhas:
            c = construcao.get(row['nome'])
            if row['nome'] in feitas or not c or c['vence_comp600'] != 'True':
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            C = starts[row['nome']]
            cortes, _ = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res = measure_mip(S, T, V, A_r, 'cont', cortes, seed=args.seed, threads=4,
                              time_limit=args.tl_comp, y_start={v: 1.0 for v in C})
            w.writerow({
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'regime': row['regime'], 'n_start': len(C),
                'lb_comp_600s': _f(row['lb']), 'ub_comp_600s': _f(row['ub']),
                'lb_com_start': res['mip_bound'], 'ub_com_start': res['mip_obj'],
                'gap_com_start': res['mip_gap'], 'status': res['mip_status'],
                't_solver_s': round(res['time_mip_s'], 2),
                'seed': args.seed, 'threads': 4, 'tl_s': args.tl_comp,
            })
            fh.flush()
            print(f'{row["nome"]:38s} start={len(C)} lb={res["mip_bound"]} ub={res["mip_obj"]} '
                  f'(sem start: lb={row["lb"]} ub={row["ub"]})', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', choices=['construcao', 'comp'], required=True)
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--tl-nucleo', type=float, default=60)
    ap.add_argument('--tl-primal', type=float, default=120)
    ap.add_argument('--tl-comp', type=float, default=600)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))
    minhas = [r for i, r in enumerate(instancias_da()) if i % n == k - 1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.fase == 'construcao':
        fase_construcao(minhas, k, n, args)
    else:
        fase_comp(minhas, k, n, args)


if __name__ == '__main__':
    main()
