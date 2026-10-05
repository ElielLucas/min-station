#!/usr/bin/env python3
"""T8 / R2: partição por grafo de origem, sem vazamento.

A partição D/A é função só de instancia_original (SHA-256).
As 12 instâncias SC da Fase E entram como classe estrutural.
Correções C4-DM e H17 no manifesto não podem sumir.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src' / 'converters'))

from build_manifest import lado_origem  # noqa: E402

MANIFESTO = ROOT / 'instances' / 'manifest.csv'
GRUPOS = ROOT / 'instances' / 'grupos_origem.csv'

FASE_E_SC = {
    'sc-gf2-k8.txt',
    'sc-gf2-k9.txt',
    *(f'sc-rigida-k{k}-s{s}.txt' for k in (8, 9) for s in range(100, 105)),
}
C4DM = {
    'b-b09-intercalado-f2-rho.txt': ('2.0', '2.0'),
    'mapf-den312d-m50-f2-rho.txt': ('4.0', '9.0'),
    'mapf-room-32-32-4-m25-f4-rho.txt': ('16.0', '19.0'),
}
CLASSES = {'F': 35, 'A': 28, 'M': 4, 'D': 3}


def main():
    if not GRUPOS.is_file() or not MANIFESTO.is_file():
        raise SystemExit('rode build_manifest.py --so-grupos antes')

    with GRUPOS.open(encoding='utf-8') as fh:
        grupos = list(csv.DictReader(fh))
    vazados = {g['instancia_original'] for g in grupos if g['vazamento'] == 'sim'}

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
    if vazados:
        falhas.append(f'vazamento {sorted(vazados)}')
    if puc.get('duplicata_de') != 'hc9u.txt':
        falhas.append(f'puc-hc9u-seed-r1 duplicata_de={puc.get("duplicata_de")!r}')
    if hc.get('duplicata_de'):
        falhas.append('hc9u.txt não é o canônico do par')
    for classe, n in CLASSES.items():
        if classes[classe] != n:
            falhas.append(f'classe {classe}: {classes[classe]} != {n}')
    if sum(1 for l in linhas if l['classe'] == 'principal') != 75:
        falhas.append('principal != 75')
    if len(linhas) != 149:
        falhas.append(f'linhas {len(linhas)} != 149')
    ausentes = FASE_E_SC - set(por_nome)
    if ausentes:
        falhas.append(f'Fase E SC ausente: {sorted(ausentes)}')
    for nome in sorted(FASE_E_SC & set(por_nome)):
        row = por_nome[nome]
        if row.get('classe') != 'estrutural' or row.get('particao') != 'estrutural':
            falhas.append(f'{nome} classe/particao={row.get("classe")}/{row.get("particao")}')
    for nome, (lb, ub) in C4DM.items():
        row = por_nome[nome]
        if row.get('lb') != lb or row.get('ub') != ub:
            falhas.append(f'C4-DM {nome}: lb/ub={row.get("lb")}/{row.get("ub")} != {lb}/{ub}')
    for row in linhas:
        if not row['caminho'].startswith('instances/benchmark-v1/'):
            continue
        esperado = lado_origem(row['instancia_original'])
        if row.get('particao') != esperado:
            falhas.append(
                f'{row["nome"]} particao={row.get("particao")!r} != {esperado!r}'
            )

    pares = sorted(
        (l['duplicata_de'], l['nome']) for l in linhas if l.get('duplicata_de')
    )
    print('duplicatas:', pares)
    print('classes benchmark-v1:', dict(classes))
    print('vazamentos:', sorted(vazados) or 0)
    if falhas:
        for f in falhas:
            print('FALHA:', f)
        raise SystemExit(1)
    print('ok')


if __name__ == '__main__':
    main()
