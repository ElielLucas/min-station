"""
E12: CBI × NUCLEO × COMP em PUC/PUCN. Plano pós-E13, §4.

Três braços, mesmos cortes C1+C2+C4, nenhum MIP start:
  COMP    measure_mip, base U, fluxo contínuo. TimeLimit do solver = 600 s,
          igual ao protocolo de dificuldade (o braço serve de verificação
          contra o manifesto).
  NUCLEO  IP em y só com os cortes estáticos, sem oráculo.
  CBI     solve_cbi corrigido, sem ub_start. O TL de 600 s é de relógio e
          inclui iterações, oráculo e reconstrução do mestre.

A carga da instância e a geração dos cortes ficam fora do TL, em t_cortes_s.
Gurobi 12.0.3, 4 threads, seed 42 na fase A, 2 fatias. Exige PYTHONHASHSEED=0.
Só instâncias com S∩T vazio.

Uso:
  PYTHONHASHSEED=0 python experiments/benchmark/run_e12.py --fase D --fatia 1/2
  PYTHONHASHSEED=0 python experiments/benchmark/run_e12.py --fase A --fatia 2/2
  PYTHONHASHSEED=0 python experiments/benchmark/run_e12.py --fase R --fatia 1/2
"""
import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path

from gurobipy import GRB
import gurobipy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from harness import load_instance, prepare_cuts, measure_mip
from cuts import build_neighborhoods
from bc_yspace import solve_cbi
from yspace import _build_ymodel

OUT_DIR = ROOT / 'results' / 'benchmark'
MANIFESTO = ROOT / 'instances' / 'manifest.csv'
TL = 600.0
THREADS = 4

DESENVOLVIMENTO = (
    'puc-bip42p-regiao-f2.txt',
    'puc-hc10p-seed-r1.txt',
    'pucn-cc3-10n-seed-r1.txt',
)
AVALIACAO = (
    'puc-cc9-2p-seed-r1.txt',
    'puc-cc11-2u-seed-r1.txt',
    'puc-cc12-2u-seed-r1.txt',
    'puc-hc9u-regiao-f4.txt',
    'puc-hc9u-seed-r1.txt',
    'puc-hc11p-seed-r1.txt',
    'puc-w23c23-seed-r1.txt',
    'pucn-cc7-3n-regiao-f2.txt',
    'pucn-cc7-3n-seed-r1.txt',
)
CONTROLE = (
    'mapf-random-32-32-10-m50-f8.txt',
    'mapf-empty-32-32-m25-f4.txt',
)
BRACOS = ('COMP', 'NUCLEO', 'CBI')
CAMPOS = [
    'nome', 'braco', 'seed', 'fase', 'n', 'm', 'n_arcos_alcance', 'n_cortes',
    't_cortes_s', 'lb', 'ub', 'gap', 'status', 'status_nome', 't_metodo_s',
    't_otimo_s', 'iteracoes', 'oracle_calls', 'n_z', 't_mestre_s', 't_oraculo_s',
    'node_count', 'pythonhashseed', 'threads', 'tl_s', 'gurobi', 'commit',
]


def _commit():
    try:
        h = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                    cwd=ROOT, text=True).strip()
        sujo = subprocess.check_output(['git', 'status', '--porcelain'],
                                       cwd=ROOT, text=True).strip()
        return h + ('-dirty' if sujo else '')
    except Exception:
        return 'desconhecido'


def _f(valor):
    if valor is None or valor == '':
        return None
    return float(valor)


def _celula(valor):
    if valor is None:
        return ''
    if isinstance(valor, float):
        return round(valor, 6)
    return valor


def nucleo(V, cortes, seed, threads, tl):
    t0 = time.monotonic()
    mip, _y = _build_ymodel(V, cortes, integer=True, seed=seed, threads=threads,
                            time_limit=tl)
    mip.Params.TimeLimit = max(0.0, tl - (time.monotonic() - t0))
    mip.optimize()
    try:
        ub = float(mip.ObjVal) if mip.SolCount > 0 else None
    except Exception:
        ub = None
    try:
        lb = float(mip.ObjBound)
    except Exception:
        lb = None
    try:
        nos = int(mip.NodeCount)
    except Exception:
        nos = None
    t = time.monotonic() - t0
    return lb, ub, mip.Status, t, nos


def gravar(w, fh, base, lb, ub, status, status_nome, t_metodo, nos, extra):
    otimo = status_nome == 'OPTIMAL'
    gap = None
    if lb is not None and ub not in (None, 0):
        gap = max(0.0, (ub - lb) / ub)
    linha = dict(base)
    linha.update(
        lb=_celula(lb), ub=_celula(ub), gap=_celula(gap), status=status,
        status_nome=status_nome, t_metodo_s=_celula(t_metodo),
        t_otimo_s=_celula(t_metodo) if otimo else '',
        node_count='' if nos is None else nos,
    )
    linha.update(extra)
    w.writerow(linha)
    fh.flush()
    print(f"{base['nome'][:-4]:32} {base['braco']:6} {status_nome:10} "
          f"lb={lb} ub={ub} t={t_metodo:.1f}s", flush=True)


def main():
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise SystemExit('E12 exige PYTHONHASHSEED=0')
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', required=True, choices=('D', 'A', 'R'))
    ap.add_argument('--fatia', required=True)
    ap.add_argument('--seed', type=int, default=None)
    args = ap.parse_args()
    k, n = map(int, args.fatia.split('/'))
    if n != 2:
        raise SystemExit('o E12 usa 2 fatias; 3 satura a máquina')

    if args.fase == 'D':
        nomes = list(DESENVOLVIMENTO)
        seeds = [42]
    elif args.fase == 'A':
        nomes = list(AVALIACAO) + list(CONTROLE)
        seeds = [42]
    else:
        from tabela_e12 import instancias_margem
        nomes = instancias_margem(OUT_DIR)
        seeds = [43, 44]
        if args.seed is not None:
            seeds = [args.seed]
        if not nomes:
            raise SystemExit('fase R: nenhuma instância de avaliação na margem')

    manifesto = {r['nome']: r for r in csv.DictReader(MANIFESTO.open(encoding='utf-8'))}
    faltando = [nome for nome in nomes if nome not in manifesto]
    if faltando:
        raise SystemExit(f'ausente no manifesto: {faltando}')
    nomes.sort(key=lambda nome: int(manifesto[nome]['n_arcos_alcance'] or 10**12))
    minhas = [nome for i, nome in enumerate(nomes) if i % n == k - 1]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f'e12_fatia{k}.csv'
    feitas = set()
    if out.exists() and out.stat().st_size:
        feitas = {(r['nome'], r['braco'], r['seed'], r['fase'])
                  for r in csv.DictReader(out.open(encoding='utf-8'))}
    novo = not out.exists() or out.stat().st_size == 0
    versao = '.'.join(map(str, gurobipy.gurobi.version()))
    commit = _commit()
    nomes_status = {GRB.OPTIMAL: 'OPTIMAL', GRB.TIME_LIMIT: 'TIME_LIMIT',
                    GRB.INFEASIBLE: 'INFEASIBLE', GRB.INF_OR_UNBD: 'INF_OR_UNBD'}

    with out.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for seed in seeds:
            for nome in minhas:
                row = manifesto[nome]
                S, T, V, adj, A_r, r = load_instance(ROOT / row['caminho'])
                if set(S) & set(T):
                    raise SystemExit(f'{nome} tem S∩T; o E12 não roda nessas')
                t0 = time.monotonic()
                cortes, cont = prepare_cuts(S, T, V, adj, A_r, r, {'C1', 'C2', 'C4'})
                t_cortes = time.monotonic() - t0
                N_plus, _ = build_neighborhoods(A_r)
                base = {
                    'nome': nome, 'seed': seed, 'fase': args.fase,
                    'n': len(V), 'm': len(S), 'n_arcos_alcance': len(A_r),
                    'n_cortes': cont['unicos'], 't_cortes_s': round(t_cortes, 3),
                    'pythonhashseed': '0', 'threads': THREADS, 'tl_s': TL,
                    'gurobi': versao, 'commit': commit,
                    'iteracoes': '', 'oracle_calls': '', 'n_z': '',
                    't_mestre_s': '', 't_oraculo_s': '',
                }
                for braco in BRACOS:
                    if (nome, braco, str(seed), args.fase) in feitas:
                        continue
                    base['braco'] = braco
                    if braco == 'COMP':
                        res = measure_mip(S, T, V, A_r, 'cont', cortes, seed=seed,
                                          threads=THREADS, time_limit=TL)
                        nome_st = nomes_status.get(res['mip_status'], str(res['mip_status']))
                        gravar(w, fh, base, res['mip_bound'], res['mip_obj'],
                               res['mip_status'], nome_st, res['time_mip_s'],
                               res['node_count'], {})
                    elif braco == 'NUCLEO':
                        lb, ub, status, t, nos = nucleo(V, cortes, seed, THREADS, TL)
                        nome_st = nomes_status.get(status, str(status))
                        gravar(w, fh, base, lb, ub, status, nome_st, t, nos, {})
                    else:
                        res = solve_cbi(S, T, V, cortes, N_plus, time_limit=TL,
                                        seed=seed, threads=THREADS)
                        nome_st = 'OPTIMAL' if res['status'] == 'OPT' else 'TIME_LIMIT'
                        extra = {
                            'iteracoes': res['iterations'],
                            'oracle_calls': res['oracle_calls'],
                            'n_z': res['n_z_cuts'],
                            't_mestre_s': round(res['master_time_s'], 3),
                            't_oraculo_s': round(res['oracle_time_s'], 3),
                        }
                        gravar(w, fh, base, res['bound'], res['obj'], res['status'],
                               nome_st, res['time_s'], res['node_count'], extra)


if __name__ == '__main__':
    main()
