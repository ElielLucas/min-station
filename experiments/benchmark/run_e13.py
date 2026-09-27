"""
E13: o gap das instâncias difíceis de MAPF/Vienna é primal ou dual?

E10, E10b e a fase `comp` do E10b não responderam, porque usaram heurísticas
construtivas em Python como instrumento e elas são piores que o próprio B&B do
Gurobi para achar solução (resultados-e9-e10-pli.md §3.1, §4.1). Aqui o
instrumento é o solver: roda o COMP com ênfase primal (MIPFocus=1) e observa
quanto o incumbente se move.

Braços, todos com C1+C2+C4, seed 42 e 4 threads, nas 13 D/A de MAPF e Vienna:

  controle   COMP padrão, TL 600 s  — referência medida com o C4-DM corrigido
  focus600   MIPFocus=1, TL 600 s   — mesmo orçamento, ênfase primal
  focus1800  MIPFocus=1, TL 1800 s  — só onde focus600 mexer no UB

O braço `controle` não é redundante: os valores do manifesto foram medidos
antes da correção de generate_C4_DM (correcao-c4-dm.md), e duas destas 13
(mapf-den312d-m50-f2-rho e vienna-I065-regiao-f4) tiveram a família de cortes
alterada por ela. Onde o controle reproduzir o manifesto, serve de verificação
de reprodutibilidade.

Critério pré-registrado, sobre Δ_UB = queda relativa do UB contra o controle:
  - gap primal: Δ_UB >= 5% em >= 7 das 13;
  - gap dual:   Δ_UB <  1% em >= 9 das 13, mesmo com TL triplicado;
  - qualquer outro desfecho é inconclusivo.
Os dois ramos comparam contra o incumbente, nunca contra o OPT, que é
desconhecido aqui — são evidências para priorizar o E11, não provas.

Condição de execução (importa para a comparabilidade): o manifesto foi gerado
com 2 processos de 4 threads numa máquina de 12 núcleos. Rodar aqui com 3
fatias satura a máquina (12 threads do solver + overhead), cada solver recebe
menos CPU e entrega LB pior e UB maior no mesmo TL — medido: o braço controle
divergiu do manifesto em 5 de 6 instâncias, com LB caindo e UB subindo, mesmo
onde a família de cortes é idêntica. Use **2 fatias**, replicando o manifesto.

Uso:
  python experiments/benchmark/run_e13.py --fase base [--fatia 1/2]
  python experiments/benchmark/run_e13.py --fase longo [--fatia 1/2]
"""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from harness import load_instance, prepare_cuts, measure_mip

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT_DIR = ROOT / 'results' / 'benchmark'
FAMILIAS = ('mapf', 'vienna')
CAMPOS_BASE = [
    'nome', 'familia', 'regime', 'n', 'm', 'n_arcos_alcance', 'n_cortes',
    'lb_manifesto', 'ub_manifesto',
    'lb_controle', 'ub_controle', 'gap_controle', 'status_controle', 't_controle_s',
    'lb_focus600', 'ub_focus600', 'gap_focus600', 'status_focus600', 't_focus600_s',
    'delta_ub_600', 'controle_bate_manifesto', 'seed', 'threads', 'tl_s',
]
CAMPOS_LONGO = [
    'nome', 'familia', 'ub_controle', 'ub_focus600',
    'lb_focus1800', 'ub_focus1800', 'gap_focus1800', 'status_focus1800', 't_focus1800_s',
    'delta_ub_1800', 'seed', 'threads', 'tl_s',
]


def instancias():
    linhas = [r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))
              if r['caminho'].startswith('instances/benchmark-v1/')
              and r['dificuldade'] in ('D', 'A')
              and r['caminho'].split('/')[2] in FAMILIAS]
    linhas.sort(key=lambda r: int(r['n_arcos_alcance']))
    return linhas


def _f(x):
    return float(x) if x not in ('', None) else None


def _delta(ub_ref, ub_novo):
    """Queda relativa do UB contra a referência. None quando não dá para comparar."""
    if ub_ref is None or ub_novo is None or ub_ref <= 0:
        return None
    return (ub_ref - ub_novo) / ub_ref


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


def fase_base(minhas, k, n, args):
    out = OUT_DIR / (f'e13_base_fatia{k}.csv' if n > 1 else 'e13_base.csv')
    fh, w, feitas = _abrir(out, CAMPOS_BASE)
    with fh:
        for row in minhas:
            if row['nome'] in feitas:
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            cortes, cont = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})

            ctrl = measure_mip(S, T, V, A_r, 'cont', cortes, seed=args.seed,
                               threads=args.threads, time_limit=args.tl)
            focus = measure_mip(S, T, V, A_r, 'cont', cortes, seed=args.seed,
                                threads=args.threads, time_limit=args.tl,
                                params={'MIPFocus': 1})

            lb_man, ub_man = _f(row['lb']), _f(row['ub'])
            d600 = _delta(ctrl['mip_obj'], focus['mip_obj'])
            bate = (lb_man is not None and ctrl['mip_bound'] is not None
                    and abs(lb_man - ctrl['mip_bound']) < 1e-6
                    and ub_man is not None and ctrl['mip_obj'] is not None
                    and abs(ub_man - ctrl['mip_obj']) < 1e-6)

            w.writerow({
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'regime': row['regime'], 'n': len(V), 'm': len(S),
                'n_arcos_alcance': len(A_r), 'n_cortes': cont['unicos'],
                'lb_manifesto': lb_man, 'ub_manifesto': ub_man,
                'lb_controle': ctrl['mip_bound'], 'ub_controle': ctrl['mip_obj'],
                'gap_controle': ctrl['mip_gap'], 'status_controle': ctrl['mip_status'],
                't_controle_s': round(ctrl['time_mip_s'], 2),
                'lb_focus600': focus['mip_bound'], 'ub_focus600': focus['mip_obj'],
                'gap_focus600': focus['mip_gap'], 'status_focus600': focus['mip_status'],
                't_focus600_s': round(focus['time_mip_s'], 2),
                'delta_ub_600': None if d600 is None else round(d600, 6),
                'controle_bate_manifesto': bate,
                'seed': args.seed, 'threads': args.threads, 'tl_s': args.tl,
            })
            fh.flush()
            print(f'{row["nome"][:-4]:38s} controle lb={ctrl["mip_bound"]} ub={ctrl["mip_obj"]}  '
                  f'focus lb={focus["mip_bound"]} ub={focus["mip_obj"]}  '
                  f'dUB={"—" if d600 is None else f"{d600:+.1%}"}  '
                  f'manifesto={"bate" if bate else "DIFERE"}', flush=True)


def fase_longo(minhas, k, n, args):
    base = {}
    for arq in OUT_DIR.glob('e13_base*.csv'):
        for r in csv.DictReader(arq.open(encoding='utf-8')):
            base[r['nome']] = r

    out = OUT_DIR / (f'e13_longo_fatia{k}.csv' if n > 1 else 'e13_longo.csv')
    fh, w, feitas = _abrir(out, CAMPOS_LONGO)
    with fh:
        for row in minhas:
            b = base.get(row['nome'])
            if row['nome'] in feitas or not b:
                continue
            # roda onde o focus600 não provou otimalidade: é onde o TL maior pode mover algo
            if str(b['status_focus600']) == '2':
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            cortes, _ = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
            res = measure_mip(S, T, V, A_r, 'cont', cortes, seed=args.seed,
                              threads=args.threads, time_limit=args.tl_longo,
                              params={'MIPFocus': 1})
            ub_ctrl = _f(b['ub_controle'])
            d = _delta(ub_ctrl, res['mip_obj'])
            w.writerow({
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'ub_controle': ub_ctrl, 'ub_focus600': _f(b['ub_focus600']),
                'lb_focus1800': res['mip_bound'], 'ub_focus1800': res['mip_obj'],
                'gap_focus1800': res['mip_gap'], 'status_focus1800': res['mip_status'],
                't_focus1800_s': round(res['time_mip_s'], 2),
                'delta_ub_1800': None if d is None else round(d, 6),
                'seed': args.seed, 'threads': args.threads, 'tl_s': args.tl_longo,
            })
            fh.flush()
            print(f'{row["nome"][:-4]:38s} 1800s lb={res["mip_bound"]} ub={res["mip_obj"]}  '
                  f'(controle ub={ub_ctrl})  dUB={"—" if d is None else f"{d:+.1%}"}', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', choices=['base', 'longo'], required=True)
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--tl', type=float, default=600)
    ap.add_argument('--tl-longo', type=float, default=1800)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))
    minhas = [r for i, r in enumerate(instancias()) if i % n == k - 1]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.fase == 'base':
        fase_base(minhas, k, n, args)
    else:
        fase_longo(minhas, k, n, args)


if __name__ == '__main__':
    main()
