#!/usr/bin/env python3
"""T8: o agrupamento do manifesto reproduz o inventário manual.

11 grafos de origem vazam entre desenvolvimento e avaliação.
2 grafos têm duas variantes, ambas em avaliação.
hc9u.txt e puc-hc9u-seed-r1.txt são a mesma estrutura.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFESTO = ROOT / 'instances' / 'manifest.csv'
GRUPOS = ROOT / 'instances' / 'grupos_origem.csv'

VAZADOS = {
    'I065', 'apia-1.graphml', 'b06', 'b12', 'b18', 'bip42p',
    'cc10-2u', 'hc10p', 'hc9u', 'lin06', 'w23c23',
}
AVALIACAO_DUPLA = {'cc7-3n', 'i160-301'}
CLASSES = {'F': 35, 'A': 28, 'M': 4, 'D': 3}


def main():
    if not GRUPOS.is_file() or not MANIFESTO.is_file():
        raise SystemExit('rode build_manifest.py --so-grupos antes')

    with GRUPOS.open(encoding='utf-8') as fh:
        grupos = list(csv.DictReader(fh))
    vazados = {g['instancia_original'] for g in grupos if g['vazamento'] == 'sim'}
    dupla_aval = set()
    for g in grupos:
        particoes = g['particoes'].split(' | ')
        if len(particoes) >= 2 and set(particoes) == {'avaliacao'}:
            dupla_aval.add(g['instancia_original'])

    with MANIFESTO.open(encoding='utf-8') as fh:
        linhas = list(csv.DictReader(fh))
    por_nome = {l['nome']: l for l in linhas}
    hc = por_nome['hc9u.txt']
    puc = por_nome['puc-hc9u-seed-r1.txt']

    classes = Counter(
        l['dificuldade'] for l in linhas
        if l['classe'] == 'principal' and l['caminho'].startswith('instances/benchmark-v1/')
    )
    falhas = []
    if vazados != VAZADOS:
        falhas.append(f'vazamento {sorted(vazados)} != {sorted(VAZADOS)}')
    if dupla_aval != AVALIACAO_DUPLA:
        falhas.append(f'avaliação dupla {sorted(dupla_aval)} != {sorted(AVALIACAO_DUPLA)}')
    if puc.get('duplicata_de') != 'hc9u.txt':
        falhas.append(f'puc-hc9u-seed-r1 duplicata_de={puc.get("duplicata_de")!r}')
    if hc.get('duplicata_de'):
        falhas.append('hc9u.txt não é o canônico do par')
    if 'avaliacao' not in puc.get('particoes_do_grupo', '') or 'legado' not in puc.get('particoes_do_grupo', ''):
        falhas.append(f'particoes de hc9u: {puc.get("particoes_do_grupo")}')
    for classe, n in CLASSES.items():
        if classes[classe] != n:
            falhas.append(f'classe {classe}: {classes[classe]} != {n}')
    if sum(1 for l in linhas if l['classe'] == 'principal') != 75:
        falhas.append('principal != 75')
    if len(linhas) != 92:
        falhas.append(f'linhas {len(linhas)} != 92')

    pares = sorted(
        (l['duplicata_de'], l['nome']) for l in linhas if l.get('duplicata_de')
    )
    print('duplicatas:', pares)
    print('classes benchmark-v1:', dict(classes))
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
