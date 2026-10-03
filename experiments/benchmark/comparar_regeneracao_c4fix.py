"""
Compara o protocolo de dificuldade antes e depois da regeneração com o C4-DM
corrigido. O antes está em results/benchmark/historico/dificuldade_v1_pre_c4fix_*.csv;
o depois, em results/benchmark/dificuldade_v1_fatia*.csv.

Grava results/benchmark/regeneracao_c4fix.csv e lista quem entrou ou saiu de D/A.

--checar-manifesto compara o manifesto atual com uma cópia anterior e aborta
(código 1) se alguma coluna fora de dificuldade, lb, ub, fonte_lb_ub,
lb_melhor, ub_melhor e fonte_melhor mudou.

Uso:
  python experiments/benchmark/comparar_regeneracao_c4fix.py
  python experiments/benchmark/comparar_regeneracao_c4fix.py --checar-manifesto copia.csv
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'results' / 'benchmark'
OUT = RES / 'regeneracao_c4fix.csv'
PERMITIDAS = {
    'dificuldade', 'lb', 'ub', 'fonte_lb_ub', 'lb_melhor', 'ub_melhor', 'fonte_melhor',
}
CAMPOS = [
    'nome', 'lb_antes', 'ub_antes', 'dif_antes',
    'lb_depois', 'ub_depois', 'dif_depois',
    'lb_mudou', 'ub_mudou', 'dif_mudou', 'movimento_DA',
]


def ler(padrao):
    linhas = {}
    for arq in sorted(RES.glob(padrao)):
        for row in csv.DictReader(arq.open(encoding='utf-8')):
            linhas[row['nome']] = row
    return linhas


def da(classe):
    return classe in ('D', 'A')


def comparar():
    antes = ler('historico/dificuldade_v1_pre_c4fix_*.csv')
    depois = ler('dificuldade_v1_fatia*.csv')
    if not antes or not depois:
        print('faltam CSVs de antes ou de depois')
        return 1
    nomes = sorted(set(antes) | set(depois))
    entrou, saiu = [], []
    with OUT.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        w.writeheader()
        for nome in nomes:
            a, d = antes.get(nome, {}), depois.get(nome, {})
            dif_a, dif_d = a.get('dificuldade', ''), d.get('dificuldade', '')
            if da(dif_d) and not da(dif_a):
                movimento = 'entrou'
                entrou.append(nome)
            elif da(dif_a) and not da(dif_d):
                movimento = 'saiu'
                saiu.append(nome)
            else:
                movimento = ''
            w.writerow({
                'nome': nome,
                'lb_antes': a.get('lb', ''), 'ub_antes': a.get('ub', ''), 'dif_antes': dif_a,
                'lb_depois': d.get('lb', ''), 'ub_depois': d.get('ub', ''), 'dif_depois': dif_d,
                'lb_mudou': a.get('lb', '') != d.get('lb', ''),
                'ub_mudou': a.get('ub', '') != d.get('ub', ''),
                'dif_mudou': dif_a != dif_d,
                'movimento_DA': movimento,
            })
    print(f'{len(nomes)} instâncias em {OUT.relative_to(ROOT)}')
    print(f'entraram em D/A ({len(entrou)}):')
    for nome in entrou:
        print(f'  {nome}')
    print(f'saíram de D/A ({len(saiu)}):')
    for nome in saiu:
        print(f'  {nome}')
    return 0


def checar_manifesto(copia):
    antigo = {r['nome']: r for r in csv.DictReader(Path(copia).open(encoding='utf-8'))}
    novo = {r['nome']: r for r in csv.DictReader((ROOT / 'instances' / 'manifest.csv').open(encoding='utf-8'))}
    if set(antigo) != set(novo):
        print('o conjunto de instâncias do manifesto mudou')
        return 1
    ruins = []
    for nome, a in antigo.items():
        d = novo[nome]
        if list(a) != list(d):
            print(f'colunas diferentes em {nome}')
            return 1
        for col in a:
            if col in PERMITIDAS:
                continue
            if a[col] != d[col]:
                ruins.append((nome, col, a[col], d[col]))
    if ruins:
        print(f'{len(ruins)} alteração(ões) fora das colunas permitidas:')
        for nome, col, va, vd in ruins[:30]:
            print(f'  {nome} {col}: {va!r} -> {vd!r}')
        return 1
    print('manifesto: só as colunas de resultado mudaram')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checar-manifesto', metavar='COPIA')
    args = ap.parse_args()
    if args.checar_manifesto:
        return checar_manifesto(args.checar_manifesto)
    return comparar()


if __name__ == '__main__':
    sys.exit(main() or 0)
