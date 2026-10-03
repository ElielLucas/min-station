"""
E14: nas quatro D/A de gap absoluto 2, o residual é dual ou o UB ainda cai?

Lê LB_melhor e UB_melhor dos CSVs do E13 (maior LB e menor UB entre controle,
focus600 e focus1800). Roda o COMP (U + C1+C2+C4) com

  Cutoff = UB_melhor - 0,5
  MIPFocus = 3

TL 4 h, seed 42, 4 threads, 2 fatias. Nunca 3 fatias: 12 threads de solver
saturam a máquina (ver run_e13.py).

Documentação consultada do Gurobi, na versão instalada 12.0.3
(https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html):

- Cutoff: soluções piores que o valor não interessam. Se o ótimo é igual ou
  melhor que o corte, o solver devolve essa solução; caso contrário termina
  com status CUTOFF. Nesta instalação, GRB.CUTOFF == 6.
- MIPFocus=3 concentra o esforço no limite (bound). MIPFocus=2 concentra em
  provar otimalidade quando achar soluções boas não é o problema; o plano pede
  ênfase no bound, então o valor usado é 3.

Critério, por instância, sem declarar OPT fora do status CUTOFF:
- CUTOFF e nenhuma solução < UB_melhor: não existe inteiro melhor que o corte,
  logo OPT = UB_melhor e o residual era dual;
- solução com objetivo < UB_melhor: o UB ainda não estava saturado;
- TIME_LIMIT sem nenhum dos dois: inconclusivo; registra o LB final.

Uso:
  python experiments/benchmark/run_e14.py --fatia 1/2
  python experiments/benchmark/run_e14.py --fatia 2/2
"""
import argparse
import csv
import sys
from pathlib import Path

import gurobipy
from gurobipy import GRB

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from harness import load_instance, prepare_cuts, measure_mip

OUT_DIR = ROOT / 'results' / 'benchmark'
ALVO = (
    'mapf-room-32-32-4-m10-f8.txt',
    'mapf-room-32-32-4-m25-f4-rho.txt',
    'vienna-I056-regiao-f4.txt',
    'vienna-I065-intercalado-f2.txt',
)
CAMPOS = [
    'nome', 'lb_melhor', 'ub_melhor', 'gap_absoluto', 'cutoff', 'mipfocus',
    'lb', 'ub', 'status', 'status_nome', 't_solver_s', 'veredito',
    'seed', 'threads', 'tl_s', 'gurobi',
]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def melhores_e13():
    base = []
    for arq in sorted(OUT_DIR.glob('e13_base*.csv')):
        base += list(csv.DictReader(arq.open(encoding='utf-8')))
    longo = {}
    for arq in sorted(OUT_DIR.glob('e13_longo*.csv')):
        for row in csv.DictReader(arq.open(encoding='utf-8')):
            longo[row['nome']] = row
    out = {}
    for row in base:
        lg = longo.get(row['nome'], {})
        lbs = [x for x in (_f(row['lb_controle']), _f(row['lb_focus600']),
                           _f(lg.get('lb_focus1800'))) if x is not None]
        ubs = [x for x in (_f(row['ub_controle']), _f(row['ub_focus600']),
                           _f(lg.get('ub_focus1800'))) if x is not None]
        out[row['nome']] = (max(lbs), min(ubs), row['caminho'] if 'caminho' in row else '')
    return out


def instancias(manifesto):
    por_nome = {r['nome']: r for r in csv.DictReader(manifesto.open(encoding='utf-8'))}
    e13 = melhores_e13()
    linhas = []
    for nome in ALVO:
        if nome not in por_nome or nome not in e13:
            raise SystemExit(f'instância do E14 ausente: {nome}')
        lb, ub, _ = e13[nome]
        if abs((ub - lb) - 2) > 1e-6:
            raise SystemExit(f'{nome}: gap absoluto {ub - lb}, o E14 exige 2')
        row = dict(por_nome[nome])
        row['lb_melhor'] = lb
        row['ub_melhor'] = ub
        linhas.append(row)
    linhas.sort(key=lambda r: int(r['n_arcos_alcance']))
    return linhas


def classificar(status, obj, ub):
    if obj is not None and obj < ub - 1e-6:
        return 'primal'
    if status == GRB.CUTOFF:
        return 'opt_ub'
    if status == GRB.TIME_LIMIT:
        return 'inconclusivo'
    return 'outro'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--tl', type=float, default=14400)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))
    if n != 2:
        raise SystemExit('o E14 usa 2 fatias; 3 satura a máquina')

    linhas = instancias(ROOT / 'instances' / 'manifest.csv')
    minhas = [r for i, r in enumerate(linhas) if i % n == k - 1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f'e14_fatia{k}.csv'
    feitas = set()
    if out.exists():
        feitas = {r['nome'] for r in csv.DictReader(out.open(encoding='utf-8'))}
    novo = not out.exists()
    versao = '.'.join(map(str, gurobipy.gurobi.version()))
    nomes = {
        GRB.CUTOFF: 'CUTOFF', GRB.OPTIMAL: 'OPTIMAL', GRB.TIME_LIMIT: 'TIME_LIMIT',
        GRB.INFEASIBLE: 'INFEASIBLE', GRB.INF_OR_UNBD: 'INF_OR_UNBD',
    }

    with out.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for row in minhas:
            if row['nome'] in feitas:
                continue
            ub = row['ub_melhor']
            corte = ub - 0.5
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            cortes, _ = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res = measure_mip(
                S, T, V, A_r, 'cont', cortes, seed=args.seed, threads=args.threads,
                time_limit=args.tl, params={'Cutoff': corte, 'MIPFocus': 3},
            )
            veredito = classificar(res['mip_status'], res['mip_obj'], ub)
            w.writerow({
                'nome': row['nome'], 'lb_melhor': row['lb_melhor'], 'ub_melhor': ub,
                'gap_absoluto': ub - row['lb_melhor'], 'cutoff': corte, 'mipfocus': 3,
                'lb': res['mip_bound'], 'ub': res['mip_obj'], 'status': res['mip_status'],
                'status_nome': nomes.get(res['mip_status'], str(res['mip_status'])),
                't_solver_s': round(res['time_mip_s'], 2), 'veredito': veredito,
                'seed': args.seed, 'threads': args.threads, 'tl_s': args.tl,
                'gurobi': versao,
            })
            fh.flush()
            print(f'{row["nome"][:-4]:38s} {veredito}  lb={res["mip_bound"]} '
                  f'ub={res["mip_obj"]} status={res["mip_status"]} '
                  f't={res["time_mip_s"]:.0f}s', flush=True)


if __name__ == '__main__':
    main()
