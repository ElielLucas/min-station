"""
E10: primal construtivo — H3 (aumento guloso a partir de C=∅) + H6 (busca
local) contra o reverse-delete atual (a partir de C=V), nas 30 instâncias
D/A do benchmark-v1.

Pergunta (plano-pos-e8-adiado.md): quanto do gap das classes D/A é primal?
O reverse-delete de `primal.py` parte de C=V e, em instância grande, gasta
o orçamento inteiro e devolve C=V — inútil onde é mais necessário.

Critério pré-registrado: H3 vence se bater o reverse-delete em ≥80% das
30 D/A e o UB@600s do COMP (protocolo de dificuldade) em ≥50%. Caso
contrário, fica registrado que o gargalo é dual, não primal, e a linha sai
da agenda — resultado tão útil quanto o oposto.

Ambos os construtores rodam com o mesmo orçamento total (60s) e a mesma
seed, para comparação justa.

Uso: python experiments/benchmark/run_e10.py [--fatia 1/3] [--tl 60]
"""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from harness import load_instance
from cuts import build_neighborhoods
from primal import build_primal_solution, build_primal_h3

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
OUT_DIR = ROOT / 'results' / 'benchmark'
CAMPOS = [
    'nome', 'familia', 'caminho', 'regime', 'n', 'm', 'n_arcos_alcance',
    'ub_comp_600s', 'ub_melhor',
    'n_estacoes_reverse', 't_reverse_s',
    'n_estacoes_h3', 't_h3_s',
    'vence_reverse', 'vence_comp600',
    'seed', 'tl_s',
]


def selecionar_instancias():
    linhas = [r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))
              if r['caminho'].startswith('instances/benchmark-v1/')]
    return [r for r in linhas if r['dificuldade'] in ('D', 'A')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fatia', default='1/1')
    ap.add_argument('--tl', type=float, default=60.0)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))

    linhas = selecionar_instancias()
    linhas.sort(key=lambda r: int(r['n_arcos_alcance']))
    minhas = [r for i, r in enumerate(linhas) if i % n == k - 1]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / (f'e10_primal_fatia{k}.csv' if n > 1 else 'e10_primal.csv')
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
            S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
            N_plus, _ = build_neighborhoods(A_r)

            t0 = time.monotonic()
            res_rd = build_primal_solution(S, T, V, N_plus, seed=args.seed,
                                            total_budget=args.tl)
            t_rd = time.monotonic() - t0
            n_rd = res_rd['n_estacoes'] if res_rd else None

            t0 = time.monotonic()
            res_h3 = build_primal_h3(S, T, V, N_plus, seed=args.seed,
                                      construct_budget=min(20.0, args.tl / 3),
                                      local_search_budget=args.tl,
                                      total_budget=args.tl)
            t_h3 = time.monotonic() - t0
            n_h3 = res_h3['n_estacoes'] if res_h3 else None

            ub600 = float(row['ub']) if row['ub'] else None
            vence_reverse = (n_h3 is not None and n_rd is not None and n_h3 < n_rd)
            vence_comp600 = (n_h3 is not None and ub600 is not None and n_h3 < ub600)

            linha = {
                'nome': row['nome'], 'familia': row['caminho'].split('/')[2],
                'caminho': row['caminho'], 'regime': row['regime'],
                'n': len(V), 'm': len(S), 'n_arcos_alcance': len(A_r),
                'ub_comp_600s': ub600, 'ub_melhor': row['ub_melhor'] or '',
                'n_estacoes_reverse': n_rd, 't_reverse_s': round(t_rd, 2),
                'n_estacoes_h3': n_h3, 't_h3_s': round(t_h3, 2),
                'vence_reverse': vence_reverse, 'vence_comp600': vence_comp600,
                'seed': args.seed, 'tl_s': args.tl,
            }
            w.writerow(linha)
            fh.flush()
            print(f'{row["nome"]:38s} reverse={n_rd} h3={n_h3} ub600={ub600}  '
                  f'vence_reverse={vence_reverse} vence_comp600={vence_comp600}', flush=True)


if __name__ == '__main__':
    main()
