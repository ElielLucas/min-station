#!/usr/bin/env python3
"""Piloto da fase P.

--dry-run monta cada célula, confere hash e pré-condição, e não chama optimize.
--calibrar mede trabalho por segundo numa instância e não grava resultado de célula.
--medir resolve o que o documento congelado lista. Retoma pelas linhas já gravadas.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'src' / 'converters'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))

import networkx as nx
from gurobipy import GRB

import bp
import hb
import sc
from harness import measure_mip, prepare_cuts
from independent_validator import avisar_se_desconexo, viavel
from instance_features import _classes_refinamento
from io_instancia import commit_atual
from ms_utils import construir_arcos_alcance
from yspace import _build_ymodel

PASTA = {
    'bp': RAIZ / 'instances' / 'estrutural' / 'bp',
    'hb': RAIZ / 'instances' / 'estrutural' / 'hb',
    'sc': RAIZ / 'instances' / 'estrutural' / 'sc',
}
DRY = RAIZ / 'results' / 'structural' / 'piloto_dryrun.csv'
MED = RAIZ / 'results' / 'structural' / 'piloto_fase_p.csv'
METODOS = ('base', 'comp', 'nucleo', 'comp_c6')
SOLVER_SEED = 42
THREADS = 4
GUARD_S = 1800


def _adj(V, arestas):
    adj = {u: [] for u in V}
    for u, v in arestas:
        adj.setdefault(u, []).append((v, 1))
        adj.setdefault(v, []).append((u, 1))
    return adj


def _wl_ind(V, arestas, S, T):
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(arestas)
    nums = []
    for w in V:
        if not str(w).startswith('w'):
            continue
        Gd = G.copy()
        Gd.add_node(f'pin-{w}')
        Gd.add_edge(w, f'pin-{w}')
        nums.append(_classes_refinamento(Gd, set(S), set(T)))
    return min(nums)


def celulas():
    """27 células. TR ficou de fora pela decisão de T16, anterior a este piloto."""
    saida = []
    for q in (4, 6, 8):
        for rotulo in ('sim', 'nao'):
            for seed in (0, 1):
                saida.append({
                    'id': f'bp-q{q}-{rotulo}-s{seed}',
                    'familia': 'bp',
                    'q': q, 'rotulo': rotulo, 'seed': seed,
                    'fatia': seed,
                })
    for k in (5, 6, 7):
        saida.append({'id': f'sc-gf2-k{k}', 'familia': 'sc', 'k': k, 'rigido': False, 'seed': 0, 'fatia': 0})
        for seed in (0, 1):
            saida.append({
                'id': f'sc-rigida-k{k}-s{seed}',
                'familia': 'sc', 'k': k, 'rigido': True, 'seed': seed, 'fatia': 1,
            })
    for k in (1, 4, 8):
        for p, fatia in ((1, 0), (6, 1)):
            saida.append({
                'id': f'hb-q6-p{p}-k{k}',
                'familia': 'hb', 'q': 6, 'ndir': 1, 'p': p, 'k': k, 'seed': 0,
                'fatia': fatia,
            })
    return saida


def _estacoes_hb(q, ndir, p, k):
    delta = q - ndir
    por_bolsao = min((delta + p - 1) // p, 3)
    C = []
    for j in range(k):
        if por_bolsao >= 3 and ndir >= 1:
            C.extend([f'c{j}_0', f'a{j}_0', f'x{j}_0'])
        else:
            for i in range((delta + p - 1) // p):
                C.append(f'x{j}_{i}')
    return C


def montar(cel):
    if cel['familia'] == 'bp':
        B = 60
        if cel['rotulo'] == 'sim':
            items, cert = bp.plantar_sim(cel['q'], B, cel['seed'])
            origem = 'plantio'
        else:
            items = bp.plantar_nao(cel['q'], B, cel['seed'])
            cert = None
            origem = 'dp-bin-packing'
        part = bp.particao_exata(items, cel['q'], B)
        if cel['rotulo'] == 'sim' and part is None:
            raise RuntimeError(f'{cel["id"]}: plantio sem partição')
        if cel['rotulo'] == 'nao' and part is not None:
            raise RuntimeError(f'{cel["id"]}: perturbação ainda empacota')
        texto = str(cert) if cert is not None else 'inexistente'
        inst = bp.emitir(PASTA['bp'], items, cel['q'], B, cel['seed'], cel['rotulo'], texto, origem)
        inst['precondicao'] = 'particao-dp'
    elif cel['familia'] == 'hb':
        inst = hb.emitir(PASTA['hb'], cel['q'], cel['ndir'], cel['p'], cel['k'], 2, 0)
        C = _estacoes_hb(cel['q'], cel['ndir'], cel['p'], cel['k'])
        adj = _adj(inst['V'], inst['arestas'])
        previsto = hb.previsao_opt(cel['q'], cel['ndir'], cel['p'], cel['k'])[1]
        if len(C) != previsto or not viavel(inst['S'], inst['T'], inst['V'], adj, 1, C):
            raise RuntimeError(f'{cel["id"]}: limite superior construído não é viável')
        inst['precondicao'] = f'ub-viavel={previsto};lb-certificado-base'
    else:
        inst = sc.emitir(PASTA['sc'], cel['k'], cel['seed'], cel['rigido'], time_limit=30)
        if cel['rigido']:
            if inst['certificado'] is None:
                inst['excluir'] = 'IP de set cover não provou o ótimo em 30 s'
                inst['precondicao'] = 'sem-certificado'
            else:
                gf = sc.construir_gf2(cel['k'])
                ind_gf = _wl_ind(gf[2], gf[4], gf[0], gf[1])
                ind = _wl_ind(inst['V'], inst['arestas'], inst['S'], inst['T'])
                inst['precondicao'] = f'ind={ind};ind_gf2={ind_gf};opt_cover={inst["certificado"]}'
                if ind <= ind_gf:
                    inst['excluir'] = 'simetria individualizada não é menor que a do GF2'
        else:
            inst['precondicao'] = 'teorema-opt-k'
    inst.setdefault('excluir', '')
    return inst


def dry_run(lista):
    DRY.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        'id', 'familia', 'fatia', 'caminho', 'sha256', 'n', 'm', 'r',
        'precondicao', 'excluir', 'commit',
    ]
    linhas = []
    for cel in lista:
        t0 = time.monotonic()
        a = montar(cel)
        b = montar(cel)
        adj = _adj(a['V'], a['arestas'])
        avisar_se_desconexo(a['V'], adj, a['S'], a['T'])
        if a['sha256'] != b['sha256']:
            raise RuntimeError(f'{cel["id"]}: hash instável')
        if set(a['S']) & set(a['T']) or len(a['S']) != len(a['T']):
            raise RuntimeError(f'{cel["id"]}: fidelidade')
        linha = {
            'id': cel['id'], 'familia': cel['familia'], 'fatia': cel['fatia'],
            'caminho': str(a['caminho'].relative_to(RAIZ)),
            'sha256': a['sha256'], 'n': len(a['V']), 'm': len(a['S']), 'r': a['r'],
            'precondicao': a['precondicao'], 'excluir': a['excluir'],
            'commit': commit_atual(),
        }
        linhas.append(linha)
        print(f'{cel["id"]}: n={linha["n"]} m={linha["m"]} {time.monotonic()-t0:.2f}s {linha["excluir"] or "ok"}', flush=True)
    with DRY.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f'{len(linhas)} células em {DRY.relative_to(RAIZ)}')


def _ja_feitos():
    if not MED.exists():
        return set()
    with MED.open(encoding='utf-8') as fh:
        return {(r['id'], r['metodo']) for r in csv.DictReader(fh)}


def _anexar(linha, campos):
    MED.parent.mkdir(parents=True, exist_ok=True)
    novo = not MED.exists()
    with MED.open('a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        if novo:
            w.writeheader()
        w.writerow(linha)


def _resolver_nucleo(S, T, V, adj, r, work_limit, seed=SOLVER_SEED):
    A = construir_arcos_alcance(V, adj, r)
    cortes, counts = prepare_cuts(S, T, V, adj, A, r, {'C1', 'C2', 'C4'})
    t0 = time.monotonic()
    modelo, _y = _build_ymodel(
        V, cortes, integer=True, seed=seed, threads=THREADS, time_limit=GUARD_S,
    )
    t_modelo = time.monotonic() - t0
    modelo.Params.WorkLimit = work_limit
    incumbente = {'primeiro': None, 'melhor': None, 'obj': None}

    def cb(m, where):
        if where != GRB.Callback.MIPSOL:
            return
        t = float(m.cbGet(GRB.Callback.RUNTIME))
        ub = float(m.cbGet(GRB.Callback.MIPSOL_OBJ))
        if incumbente['primeiro'] is None:
            incumbente['primeiro'] = t
        if incumbente['obj'] is None or ub < incumbente['obj'] - 1e-8:
            incumbente['obj'] = ub
            incumbente['melhor'] = t

    t0 = time.monotonic()
    modelo.optimize(cb)
    dt = time.monotonic() - t0
    status = modelo.Status
    obj = float(modelo.ObjVal) if modelo.SolCount else None
    bound = float(modelo.ObjBound)
    gap = float(modelo.MIPGap) if modelo.SolCount else None
    saida = {
        'mip_obj': obj, 'mip_bound': bound, 'mip_gap': gap, 'mip_status': status,
        'sol_count': modelo.SolCount, 'node_count': int(modelo.NodeCount),
        'time_mip_s': dt, 'time_modelo_s': t_modelo,
        'time_to_first_incumbent_s': incumbente['primeiro'],
        'time_to_best_incumbent_s': incumbente['melhor'],
        'time_to_proof_s': dt if status == GRB.OPTIMAL else None,
        'work': float(modelo.Work),
        'n_cortes': counts['unicos'],
    }
    modelo.dispose()
    return saida


def resolver(inst, metodo, work_limit, seed=SOLVER_SEED):
    S, T, V = inst['S'], inst['T'], inst['V']
    adj = _adj(V, inst['arestas'])
    r = inst['r']
    if metodo == 'nucleo':
        return _resolver_nucleo(S, T, V, adj, r, work_limit, seed)
    familias = set()
    if metodo == 'comp':
        familias = {'C1', 'C2', 'C4'}
    elif metodo == 'comp_c6':
        familias = {'C1', 'C2', 'C4', 'C6'}
    A = construir_arcos_alcance(V, adj, r)
    cortes, counts = prepare_cuts(S, T, V, adj, A, r, familias)
    extras = list(counts.get('C6_cortes') or [])
    res = measure_mip(
        S, T, V, A, 'int', list(cortes) + extras,
        seed=seed, threads=THREADS, time_limit=GUARD_S,
        params={'WorkLimit': work_limit}, coletar_incumbente=True,
    )
    res['n_cortes'] = counts.get('unicos', 0) + counts.get('C6', 0)
    return res


CAMPOS_MED = [
    'id', 'familia', 'fatia', 'metodo', 'sha256', 'seed_solver', 'threads',
    'work_limit', 'guard_s', 'mip_status', 'mip_obj', 'mip_bound', 'mip_gap',
    'node_count', 'work', 'time_mip_s', 'time_modelo_s',
    'time_to_first_incumbent_s', 'time_to_best_incumbent_s', 'time_to_proof_s',
    'n_cortes', 'commit',
]


def medir(lista, work_limit, fatia):
    feitos = _ja_feitos()
    for cel in lista:
        if fatia is not None and cel['fatia'] != fatia:
            continue
        inst = montar(cel)
        if inst['excluir']:
            print(f'{cel["id"]}: excluída ({inst["excluir"]})', flush=True)
            continue
        for metodo in METODOS:
            if metodo == 'comp_c6' and cel['familia'] not in ('hb', 'bp', 'sc'):
                continue
            if (cel['id'], metodo) in feitos:
                continue
            t0 = time.monotonic()
            res = resolver(inst, metodo, work_limit)
            linha = {
                'id': cel['id'], 'familia': cel['familia'], 'fatia': cel['fatia'],
                'metodo': metodo, 'sha256': inst['sha256'], 'seed_solver': SOLVER_SEED,
                'threads': THREADS, 'work_limit': work_limit, 'guard_s': GUARD_S,
                'commit': commit_atual(),
            }
            for chave in CAMPOS_MED:
                if chave in res:
                    linha[chave] = res[chave]
            _anexar(linha, CAMPOS_MED)
            print(
                f'{cel["id"]} {metodo}: status={res["mip_status"]} '
                f'obj={res["mip_obj"]} bound={res["mip_bound"]} '
                f'nos={res["node_count"]} work={res["work"]:.3f} '
                f'{time.monotonic()-t0:.1f}s',
                flush=True,
            )


def calibrar():
    """Uma corrida curta, threads=1, para ler trabalho por segundo de parede."""
    cel = {'id': 'bp-q8-nao-s0', 'familia': 'bp', 'q': 8, 'rotulo': 'nao', 'seed': 0, 'fatia': 0}
    inst = montar(cel)
    S, T, V = inst['S'], inst['T'], inst['V']
    adj = _adj(V, inst['arestas'])
    A = construir_arcos_alcance(V, adj, inst['r'])
    t0 = time.monotonic()
    res = measure_mip(
        S, T, V, A, 'int', [],
        seed=SOLVER_SEED, threads=1, time_limit=20, coletar_incumbente=False,
    )
    parede = time.monotonic() - t0
    taxa = res['work'] / parede if parede else 0
    print(
        f'calibracao bp-q8-nao-s0 base threads=1 TL=20: '
        f'status={res["mip_status"]} work={res["work"]:.4f} parede={parede:.3f} '
        f'taxa={taxa:.4f} work/s n={len(V)}'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--calibrar', action='store_true')
    ap.add_argument('--medir', action='store_true')
    ap.add_argument('--work-limit', type=float, default=None)
    ap.add_argument('--fatia', type=int, default=None)
    args = ap.parse_args()
    lista = celulas()
    if args.dry_run:
        dry_run(lista)
    elif args.calibrar:
        calibrar()
    elif args.medir:
        if args.work_limit is None:
            raise SystemExit('medir exige --work-limit')
        medir(lista, args.work_limit, args.fatia)
    else:
        raise SystemExit('escolha --dry-run, --calibrar ou --medir')


if __name__ == '__main__':
    main()
