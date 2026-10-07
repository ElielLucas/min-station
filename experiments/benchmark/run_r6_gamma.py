#!/usr/bin/env python3
"""R6 — tabela Γ. Pré-registro: docs/technical/reference/pre-registro-r5.md.

Não mede F-CC. Não corre o teste primal (isso é run_r6_primal.py).
"""

import csv
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAIZ = HERE.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / 'experiments' / 'cuts'))
sys.path.insert(0, str(RAIZ / 'experiments' / 'structural'))

from gurobipy import GRB

import bp
import hb
import sc
import tr
from independent_validator import opt_por_enumeracao
from medir import nucleo, otimo_base
from tabela_linha_base import melhor

MANIFESTO = RAIZ / 'instances' / 'manifest.csv'
LINHA = RAIZ / 'results' / 'benchmark' / 'linha_base.csv'
SAIDA = RAIZ / 'results' / 'benchmark' / 'r6-gamma.csv'
FORA_M = {
    'hc12p.txt',
    'puc-hc12p-seed-r1.txt',
    'puc-w3c571-seed-r1.txt',
}
CAMPOS = [
    'nome', 'amostra', 'familia', 'classe_gamma', 'opt', 'opt_core', 'gamma',
    'gamma_lo', 'gamma_hi', 'fonte_opt', 'fonte_core', 'lb_star', 'ub_star',
    'status_core', 'n', 'm', 'nota',
]


def familia(nome):
    if nome.startswith('pucn-'):
        return 'pucn'
    if nome.startswith('puc-'):
        return 'puc'
    if nome.startswith('pace18-'):
        return 'pace18'
    if nome.startswith('mapf-'):
        return 'mapf'
    if nome.startswith('vienna-'):
        return 'vienna'
    return nome.split('-')[0].replace('.txt', '')


def _ceil(x):
    return int(math.ceil(float(x) - 1e-6))


def _floor(x):
    return int(math.floor(float(x) + 1e-6))


def _anexar(linhas, linha):
    linhas.append(linha)


def nucleo_da_linha(grupo):
    nucs = [r for r in grupo if r['braco'] == 'nucleo']
    if not nucs:
        return None, None, None
    # prefer status 2
    ok = [r for r in nucs if int(r['mip_status']) == 2 and r.get('mip_obj') not in (None, '')]
    if ok:
        r = min(ok, key=lambda x: float(x['mip_obj']))
        return _ceil(r['mip_obj']), 2, 'linha_base.nucleo'
    return None, int(nucs[0]['mip_status']), 'linha_base.nucleo_nao_otimo'


def manifesto():
    with MANIFESTO.open(encoding='utf-8') as fh:
        return [r for r in csv.DictReader(fh) if r['classe'] == 'principal']


def por_instancia():
    with LINHA.open(encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    por = {}
    for r in rows:
        por.setdefault(r['nome'], []).append(r)
    return por


def linha_exact_ou_interval(row, grupo, amostra):
    nome = row['nome']
    lb, _, _ = melhor(grupo, 'mip_bound', 'lb', ('base', 'comp', 'nucleo'))
    ub, _, _ = melhor(grupo, 'mip_obj', 'ub', ('base', 'comp'))
    core, st, fonte_c = nucleo_da_linha(grupo)
    m = int(float(row['m']))
    n = int(float(row['n']))
    base = {
        'nome': nome, 'amostra': amostra, 'familia': familia(nome),
        'n': n, 'm': m, 'lb_star': lb, 'ub_star': ub,
        'fonte_core': fonte_c, 'status_core': st if st is not None else '',
        'opt': '', 'gamma': '', 'gamma_lo': '', 'gamma_hi': '', 'nota': '',
        'fonte_opt': '', 'opt_core': core if core is not None else '',
        'classe_gamma': 'unknown',
    }
    if core is None:
        base['classe_gamma'] = 'unknown'
        base['nota'] = 'núcleo sem prova'
        return base
    if amostra == 'exact-F-legado' and lb is not None and ub is not None and lb == ub:
        base['classe_gamma'] = 'exact'
        base['opt'] = lb
        base['fonte_opt'] = 'linha_base LB*=UB*'
        base['gamma'] = lb - core
        return base
    if lb is not None and ub is not None:
        # OPT não provado; núcleo sim. Spec C: intervalo, nunca um valor.
        lo = max(0, lb - core)
        hi = ub - core
        base['classe_gamma'] = 'interval'
        base['gamma_lo'] = lo
        base['gamma_hi'] = hi
        base['fonte_opt'] = 'LB*/UB* Spec A R4'
        base['nota'] = 'OPT não provado; intervalo, não valor'
        if amostra == 'exact-F-legado':
            base['amostra'] = 'interval-F-legado'
        return base
    if amostra == 'exact-F-legado':
        base['classe_gamma'] = 'unknown'
        base['nota'] = 'F/legado sem LB*=UB* ou núcleo incompleto'
        return base
    return base


def estruturais():
    out = []
    # SC
    for k in (3, 4):
        S, T, V, adj, _e, r, _el, _c = sc.construir_gf2(k)
        core = nucleo(S, T, V, adj, r)
        opt = k
        out.append({
            'nome': f'SC-GF2-k{k}', 'amostra': 'exact-estrutural', 'familia': 'sc',
            'classe_gamma': 'exact', 'opt': opt, 'opt_core': int(round(core)),
            'gamma': opt - int(round(core)), 'gamma_lo': '', 'gamma_hi': '',
            'fonte_opt': 'teorema OPT=k', 'fonte_core': 'medir.nucleo',
            'lb_star': '', 'ub_star': '', 'status_core': 2,
            'n': len(V), 'm': len(S), 'nota': '',
        })
    # BP nao novo
    for seed in (0, 1):
        items = bp.plantar_nao(2, 10, seed)
        q = 2
        S, T, V, adj, _e, r = bp.construir(items, q, 10)
        core = nucleo(S, T, V, adj, r)
        opt = bp.limite_cobertura(items, q) + 1  # sem partição
        if bp.particao_exata(items, q, 10) is not None:
            raise RuntimeError(f'BP seed {seed} tem partição; não é não')
        out.append({
            'nome': f'BP-nao-q2-B10-s{seed}', 'amostra': 'exact-estrutural',
            'familia': 'bp-nao', 'classe_gamma': 'exact',
            'opt': opt, 'opt_core': int(round(core)),
            'gamma': opt - int(round(core)), 'gamma_lo': '', 'gamma_hi': '',
            'fonte_opt': 'DP sem partição → 2n+q+1', 'fonte_core': 'medir.nucleo',
            'lb_star': '', 'ub_star': '', 'status_core': 2,
            'n': len(V), 'm': len(S), 'nota': f'items={items}',
        })
    # BP minúsculo
    S, T, V, adj, _e, r = bp.construir([3, 1], 2, 2)
    core = nucleo(S, T, V, adj, r)
    opt = opt_por_enumeracao(S, T, V, adj, r)
    out.append({
        'nome': 'BP-nao-[3,1]-q2', 'amostra': 'exact-estrutural',
        'familia': 'bp-nao', 'classe_gamma': 'exact',
        'opt': opt, 'opt_core': int(round(core)),
        'gamma': opt - int(round(core)), 'gamma_lo': '', 'gamma_hi': '',
        'fonte_opt': 'enum independent_validator', 'fonte_core': 'medir.nucleo',
        'lb_star': '', 'ub_star': '', 'status_core': 2,
        'n': len(V), 'm': len(S), 'nota': 'Apêndice B; validador n=16',
    })
    # HB
    for q, ndir, p, fonte_opt in (
        (4, 2, 1, 'enum'),
        (5, 2, 1, 'mip_base'),
    ):
        S, T, V, adj, _e, r, _d = hb.construir(q, ndir, p)
        core = nucleo(S, T, V, adj, r)
        if fonte_opt == 'enum':
            opt = opt_por_enumeracao(S, T, V, adj, r)
            fo = 'enum independent_validator'
        else:
            opt = int(round(otimo_base(S, T, V, adj, r)))
            fo = 'mip_base T5'
        out.append({
            'nome': f'HB-q{q}-ndir{ndir}-p{p}', 'amostra': 'exact-estrutural',
            'familia': 'hb', 'classe_gamma': 'exact',
            'opt': opt, 'opt_core': int(round(core)),
            'gamma': opt - int(round(core)), 'gamma_lo': '', 'gamma_hi': '',
            'fonte_opt': fo, 'fonte_core': 'medir.nucleo',
            'lb_star': '', 'ub_star': '', 'status_core': 2,
            'n': len(V), 'm': len(S), 'nota': '',
        })
    # TR
    S, T, V, adj, _e, r, _c = tr.construir(2, 5, 2, None, m=2)
    core = nucleo(S, T, V, adj, r)
    opt = tr.opt_formula(5, 2)
    out.append({
        'nome': 'TR-k2-L5-r2', 'amostra': 'exact-estrutural',
        'familia': 'tr', 'classe_gamma': 'exact',
        'opt': opt, 'opt_core': int(round(core)),
        'gamma': opt - int(round(core)), 'gamma_lo': '', 'gamma_hi': '',
        'fonte_opt': 'fórmula TR (D+r-1)//r - 1', 'fonte_core': 'medir.nucleo',
        'lb_star': '', 'ub_star': '', 'status_core': 2,
        'n': len(V), 'm': len(S), 'nota': 'Γ esperado 0; platô',
    })
    return out


def main():
    por = por_instancia()
    linhas = []
    for row in manifesto():
        nome = row['nome']
        grupo = por.get(nome, [])
        dif = row.get('dificuldade', '')
        part = row.get('particao', '')
        if dif in ('D', 'A') and 'desenvolvimento' in part and nome not in FORA_M:
            _anexar(linhas, linha_exact_ou_interval(row, grupo, 'interval-DA'))
        elif (dif == 'F' or part == 'legado' or 'legado' in part) and dif not in ('D', 'A'):
            # legado sem dificuldade, ou F
            if dif == 'F' or (not dif and 'legado' in part):
                _anexar(linhas, linha_exact_ou_interval(row, grupo, 'exact-F-legado'))
    linhas.extend(estruturais())
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        w.writeheader()
        for lin in linhas:
            w.writerow({k: lin.get(k, '') for k in CAMPOS})
            g = lin.get('gamma', '')
            print(
                f"{lin['nome']} {lin['classe_gamma']} core={lin.get('opt_core')} "
                f"opt={lin.get('opt')} Γ={g} lo={lin.get('gamma_lo')} "
                f"hi={lin.get('gamma_hi')}",
                flush=True,
            )
    print('csv', SAIDA)


if __name__ == '__main__':
    main()
