"""
Reavaliação das instâncias afetadas pelo defeito de cortes inválidos em
generate_C4_DM (correcao-c4-dm.md).

Roda o protocolo de dificuldade (COMP = baseline U + C1+C2+C4, Gurobi, 4
threads, seed 42, TL 600 s — igual a run_dificuldade.py) nas instâncias
principais com S∩T != 0, e compara LB, UB e classe com o que está no
manifesto, produzido antes da correção.

Só essas instâncias precisam ser refeitas: a causa raiz era a remoção de S∩T
do bipartido de Dulmage-Mendelsohn, então com S∩T = 0 a família de cortes
gerada não muda pela correção de validade. A ordenação acrescentada junto
(determinismo) pode mover o LB em +-1 em qualquer instância, o que está
registrado em correcao-c4-dm.md e não é refeito aqui.

Uso:
  python experiments/benchmark/reavaliar_c4dm.py [--tl 600]   # mede e grava o CSV
  python experiments/benchmark/reavaliar_c4dm.py --aplicar    # leva ao manifesto
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

from harness import load_instance, prepare_cuts, measure_mip
from ms_utils import ler_instancia
from run_dificuldade import classificar

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT = ROOT / 'results' / 'benchmark' / 'reavaliacao_c4dm.csv'
CAMPOS = ['nome', 'caminho', 'n', 'm', 'n_arcos_alcance', 'card_st',
          'n_cortes_antes', 'n_cortes_depois',
          'lb_antes', 'ub_antes', 'dif_antes',
          'lb_depois', 'ub_depois', 'gap_depois', 'dif_depois', 'status', 't_solver_s',
          'lb_mudou', 'ub_mudou', 'tl_s', 'threads', 'seed']


def afetadas():
    alvo = []
    for row in csv.DictReader(MANIFESTO.open(encoding='utf-8')):
        if row['classe'] != 'principal':
            continue
        dados = ler_instancia(str(ROOT / row['caminho']))
        st = set(dados['S']) & set(dados['T'])
        if st:
            alvo.append((row, len(st)))
    alvo.sort(key=lambda p: int(p[0]['n_arcos_alcance'] or 10**12))
    return alvo


def _f(x):
    return float(x) if x not in ('', None) else None


def aplicar_ao_manifesto():
    """Leva lb/ub/dificuldade do CSV de reavaliação ao manifesto, só onde mudou."""
    if not OUT.exists():
        print(f'{OUT} não existe — rode a medição primeiro.')
        return 1
    novos = {r['nome']: r for r in csv.DictReader(OUT.open(encoding='utf-8'))}

    linhas = list(csv.DictReader(MANIFESTO.open(encoding='utf-8')))
    campos = list(linhas[0].keys())
    mudadas = 0
    for row in linhas:
        n = novos.get(row['nome'])
        if not n or not (n['lb_mudou'] == 'True' or n['ub_mudou'] == 'True'):
            continue
        print(f"{row['nome'][:-4]:38s} lb {row['lb']} -> {n['lb_depois']}   "
              f"ub {row['ub']} -> {n['ub_depois']}   dif {row['dificuldade']} -> {n['dif_depois']}")
        row['lb'] = n['lb_depois']
        row['ub'] = n['ub_depois']
        row['dificuldade'] = n['dif_depois']
        row['fonte_lb_ub'] = 'COMP (U + C1+C2+C4), TL 600 s, seed 42; reavaliado (correcao-c4-dm.md)'
        mudadas += 1

    if not mudadas:
        print('nenhuma mudança a aplicar.')
        return 0
    with MANIFESTO.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f'\n{mudadas} linha(s) atualizada(s) em {MANIFESTO.relative_to(ROOT)}.')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tl', type=float, default=600)
    ap.add_argument('--aplicar', action='store_true',
                    help='leva o resultado já medido ao manifesto')
    args = ap.parse_args()

    if args.aplicar:
        return aplicar_ao_manifesto()

    alvo = afetadas()
    print(f'{len(alvo)} instâncias principais com S∩T != 0\n', flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    feitas = set()
    if OUT.exists():
        feitas = {r['nome'] for r in csv.DictReader(OUT.open(encoding='utf-8'))}
    novo = not OUT.exists()

    with OUT.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for row, card_st in alvo:
            if row['nome'] in feitas:
                continue
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            cortes, cont = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})

            t0 = time.monotonic()
            res = measure_mip(S, T, V, A_r, 'cont', cortes, seed=42, threads=4,
                              time_limit=args.tl)
            t_total = time.monotonic() - t0

            lb_a, ub_a = _f(row['lb']), _f(row['ub'])
            lb_d, ub_d = res['mip_bound'], res['mip_obj']
            dif_d = classificar(res['mip_status'], res['time_mip_s'], res['mip_gap'], ub_d)

            w.writerow({
                'nome': row['nome'], 'caminho': row['caminho'], 'n': len(V), 'm': len(S),
                'n_arcos_alcance': len(A_r), 'card_st': card_st,
                'n_cortes_antes': row['n_cortes'] if 'n_cortes' in row else '',
                'n_cortes_depois': cont['unicos'],
                'lb_antes': lb_a, 'ub_antes': ub_a, 'dif_antes': row['dificuldade'],
                'lb_depois': lb_d, 'ub_depois': ub_d, 'gap_depois': res['mip_gap'],
                'dif_depois': dif_d, 'status': res['mip_status'],
                't_solver_s': round(res['time_mip_s'], 2),
                'lb_mudou': lb_a is not None and lb_d is not None and abs(lb_a - lb_d) > 1e-6,
                'ub_mudou': ub_a is not None and ub_d is not None and abs(ub_a - ub_d) > 1e-6,
                'tl_s': args.tl, 'threads': 4, 'seed': 42,
            })
            fh.flush()
            alerta = ''
            if lb_a is not None and lb_d is not None and lb_d < lb_a - 1e-6:
                alerta = '   <-- LB CAIU: o anterior estava inflado por corte inválido'
            print(f'{row["nome"][:-4]:38s} S∩T={card_st:3d} '
                  f'antes lb={lb_a} ub={ub_a} ({row["dificuldade"]})  '
                  f'depois lb={lb_d} ub={ub_d} ({dif_d}){alerta}', flush=True)


if __name__ == '__main__':
    sys.exit(main() or 0)
