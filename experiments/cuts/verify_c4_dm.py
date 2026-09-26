"""
Regressão de validade de generate_C4_DM.

Exige que TODO corte gerado seja válido, segundo dois instrumentos que têm de
concordar:

  1. is_valid_cut (cuts.py) reprova/aprova a desigualdade y(Z) >= 1;
  2. integer_oracle sobre V∖Z — se V∖Z é viável, existe solução com y(Z) = 0
     e o corte é inválido, com testemunha explícita.

Divergência entre os dois instrumentos também é falha: significa que um dos
dois está errado e nenhum resultado que dependa deles é confiável.

Por que repetir com PYTHONHASHSEED diferente: generate_C4_DM percorre `set`s
antes do emparelhamento máximo, que não é único, então a família gerada muda
entre processos. Uma única execução pode passar por sorte. O driver relança
este mesmo arquivo em subprocessos, porque PYTHONHASHSEED só tem efeito no
início do interpretador.

Cobertura: os gabaritos de synthetic.py, todas as instâncias principais com
S∩T != 0 (onde o defeito de 2026-09-26 aparece) e um controle com S∩T = 0.

Uso:
  python experiments/cuts/verify_c4_dm.py [--seeds 3] [--sem-instancias]
"""
import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import synthetic as syn
from cuts import build_neighborhoods, generate_C4_DM, integer_oracle, is_valid_cut
from harness import load_instance

GABARITOS = [
    ('F1(2,2)', syn.make_F1, dict(m=2, k=2, r=1)),
    ('F1(2,3)', syn.make_F1, dict(m=2, k=3, r=1)),
    ('F2(k=1)', syn.make_F2, dict(k=1, L=3, r=1)),
    ('Tri', syn.make_Tri, dict(r=1)),
    ('Sec59(L=7)', syn.make_Sec59, dict(L=7, r=1)),
    ('Direct0', syn.make_Direct0, dict(r=1)),
    ('TermRelay', syn.make_TermRelay, dict(r=1)),
    ('StayPut', syn.make_StayPut, dict(r=1)),
    ('SharedTerminal', syn.make_SharedTerminal, dict(r=1)),
    ('TermRelayForced', syn.make_TermRelayForced, dict(r=1)),
]

CONTROLE = [
    'instances/benchmark-v1/puc/puc-hc9u-seed-r1.txt',
    'instances/benchmark-v1/pucn/pucn-cc7-3n-seed-r1.txt',
    'instances/benchmark-v1/mapf/mapf-room-32-32-4-m10-f8.txt',
]


def checar(label, S, T, V, A_r):
    """Devolve (n_cortes, invalidos, divergencias) e imprime uma linha."""
    N_plus, N_minus = build_neighborhoods(A_r)
    cortes = generate_C4_DM(S, T, N_plus, N_minus)
    invalidos = divergencias = 0
    for Z in cortes:
        aprovado = is_valid_cut(S, T, A_r, set(Z), N_plus, N_minus)
        resto_viavel = integer_oracle(S, T, N_plus, set(V) - set(Z))[0]
        # corte válido  <=>  V∖Z inviável
        if aprovado == resto_viavel:
            divergencias += 1
        if resto_viavel:
            invalidos += 1
    st = len(set(S) & set(T))
    marca = ''
    if invalidos:
        marca = f'  <-- {invalidos} INVÁLIDO(S)'
    if divergencias:
        marca += f'  <-- {divergencias} DIVERGÊNCIA(S) ENTRE INSTRUMENTOS'
    print(f'  {label:38s} S∩T={st:3d} |C4|={len(cortes):4d} inval={invalidos:3d}{marca}', flush=True)
    return len(cortes), invalidos, divergencias


def instancias_com_intersecao():
    """Instâncias principais do manifesto em que S ∩ T != 0."""
    from ms_utils import ler_instancia
    achadas = []
    man = ROOT / 'instances' / 'manifest.csv'
    for row in csv.DictReader(man.open(encoding='utf-8')):
        if row['classe'] != 'principal':
            continue
        dados = ler_instancia(str(ROOT / row['caminho']))
        if set(dados['S']) & set(dados['T']):
            achadas.append(row['caminho'])
    return achadas


def rodada(com_instancias):
    invalidos = divergencias = 0
    print(f'== PYTHONHASHSEED={os.environ.get("PYTHONHASHSEED")} ==')
    print(' gabaritos:')
    for label, fn, kw in GABARITOS:
        S, T, V, adj, A_r, r, _ = fn(**kw)
        _, inv, div = checar(label, S, T, V, A_r)
        invalidos += inv
        divergencias += div

    if com_instancias:
        print(' instâncias com S∩T != 0:')
        for caminho in instancias_com_intersecao():
            S, T, V, adj, A_r, r = load_instance(ROOT / caminho)
            _, inv, div = checar(Path(caminho).stem, S, T, V, A_r)
            invalidos += inv
            divergencias += div

        print(' controle (S∩T = 0):')
        for caminho in CONTROLE:
            S, T, V, adj, A_r, r = load_instance(ROOT / caminho)
            _, inv, div = checar(Path(caminho).stem, S, T, V, A_r)
            invalidos += inv
            divergencias += div

    return invalidos, divergencias


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--sem-instancias', action='store_true',
                    help='só os gabaritos (rápido)')
    ap.add_argument('--worker', action='store_true', help='uso interno do driver')
    args = ap.parse_args()

    if args.worker:
        inval, diverg = rodada(not args.sem_instancias)
        return 1 if (inval or diverg) else 0

    falhas = 0
    for seed in range(args.seeds):
        env = dict(os.environ, PYTHONHASHSEED=str(seed))
        cmd = [sys.executable, __file__, '--worker']
        if args.sem_instancias:
            cmd.append('--sem-instancias')
        falhas += subprocess.call(cmd, env=env) != 0
        print()

    if falhas:
        print(f'FALHA: corte inválido ou divergência entre instrumentos em {falhas} '
              f'de {args.seeds} execuções.')
        return 1
    print(f'OK: nenhum corte inválido em {args.seeds} execuções com sementes de hash distintas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
