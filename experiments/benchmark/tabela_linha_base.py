#!/usr/bin/env python3
"""Agrega linha_base.csv em LB*/UB* por instância (Spec A R4)."""

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CSV = RAIZ / 'results' / 'benchmark' / 'linha_base.csv'
PRE = RAIZ / 'docs' / 'technical' / 'reference' / 'linha-de-base-pre-registro.md'

BRACOS = ('base', 'comp', 'nucleo')
SEEDS_DA = {42, 43, 44}
SEEDS_FM = {42}
FORA = {
    'hc12p.txt',
    'puc-hc12p-seed-r1.txt',
    'puc-w3c571-seed-r1.txt',
}


def desenho():
    n = 0
    with (RAIZ / 'instances' / 'manifest.csv').open(encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['classe'] != 'principal':
                continue
            seeds = SEEDS_DA if r.get('dificuldade') in ('D', 'A') else SEEDS_FM
            n += 3 * len(seeds)
    return n


def melhor(linhas, chave, sentido):
    cand = []
    for r in linhas:
        raw = r.get(chave)
        if raw in (None, ''):
            continue
        cand.append((float(raw), r['braco'], r['seed']))
    if not cand:
        return None, '', ''
    valor, braco, seed = (max if sentido == 'lb' else min)(cand)
    return valor, braco, seed


def main():
    if not CSV.is_file():
        raise SystemExit(f'sem {CSV}')
    with CSV.open(encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    esperado = desenho()
    if len(rows) != esperado:
        print(f'AVISO: {len(rows)} linhas != desenho {esperado}', file=sys.stderr)
    sem_prov = [r for r in rows if not r.get('sha256') or not r.get('commit')]
    if sem_prov:
        raise SystemExit(f'{len(sem_prov)} linhas sem sha256/commit')

    por = {}
    for r in rows:
        por.setdefault(r['nome'], []).append(r)

    print('# LB* / UB* da linha de base\n')
    print(f'Fonte: `{CSV.relative_to(RAIZ)}`. Contrato: `{PRE.relative_to(RAIZ)}`.')
    print(f'Linhas: {len(rows)} (desenho {esperado}).\n')
    print('| Instância | Dificuldade | Partição | Fora AV | LB* | fonte LB* | UB* | fonte UB* | guarda |')
    print('|---|---|---|---|---:|---|---:|---|---|')
    for nome in sorted(por):
        grupo = por[nome]
        lb, lb_b, lb_s = melhor(grupo, 'mip_bound', 'lb')
        ub, ub_b, ub_s = melhor(grupo, 'mip_obj', 'ub')
        guarda = any(r.get('guarda_parede') == '1' for r in grupo)
        dif = grupo[0].get('dificuldade', '')
        part = grupo[0].get('particao', '')
        fora = 'sim' if nome in FORA else ''
        lb_txt = '' if lb is None else f'{lb:g}'
        ub_txt = '' if ub is None else f'{ub:g}'
        lb_src = f'{lb_b} seed {lb_s}' if lb is not None else 'ausente'
        ub_src = f'{ub_b} seed {ub_s}' if ub is not None else 'ausente'
        print(
            f'| {nome} | {dif} | {part} | {fora} | {lb_txt} | {lb_src} | '
            f'{ub_txt} | {ub_src} | {"sim" if guarda else ""} |'
        )


if __name__ == '__main__':
    main()
