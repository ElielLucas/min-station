#!/usr/bin/env python3
"""Execução oficial R11 — só roda após manifesto/hash congelado.

Pré-condições:
1. ``prepare_r11.py`` já materializou as instâncias;
2. ``instances/estrutural/r11-manifest.csv`` está versionado/conferido;
3. ``verify_r11.py`` já passou;
4. o pré-registro está fechado.

Este arquivo está pronto para execução, mas sua mera presença não produz
instâncias, CSV ou resultados.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(ROOT / 'experiments' / 'alternative-formulations'))

from gurobipy import GRB

from baseline import construir_modelo_baseline
from fcc import CapExceeded, opt_fcc
from independent_validator import opt_por_enumeracao, viavel
from io_instancia import commit_atual
from ms_utils import construir_arcos_alcance
from path_cycle import certificar_cycle, certificar_path
from r11_catalog import (
    BASELINE_TIME_LIMIT,
    MAX_W,
    N_OPT_ENUM,
    SOLVER_SEED,
    THREADS,
    catalogo_oficial,
    variantes_para,
)
from spider import certificar_spider

MANIFEST = ROOT / 'instances' / 'estrutural' / 'r11-manifest.csv'
CSV_PATH = ROOT / 'results' / 'structural' / 'r11-certificadores.csv'
EPS = 1e-6


def _sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _carregar_manifesto():
    if not MANIFEST.exists():
        raise RuntimeError(
            'manifesto R11 ausente. Execute e versione prepare_r11.py antes do lote oficial.'
        )
    with MANIFEST.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    by_id = {r['id']: r for r in rows}
    if len(by_id) != len(rows):
        raise RuntimeError('IDs duplicados no manifesto R11')
    return by_id


def _validar_manifesto(catalogo, manifesto):
    ids_cat = {x['id'] for x in catalogo}
    ids_man = set(manifesto)
    if ids_cat != ids_man:
        faltam = sorted(ids_cat - ids_man)
        sobram = sorted(ids_man - ids_cat)
        raise RuntimeError(f'manifesto != catálogo; faltam={faltam}; sobram={sobram}')
    for inst in catalogo:
        row = manifesto[inst['id']]
        path = ROOT / row['arquivo']
        if not path.exists():
            raise RuntimeError(f'arquivo ausente: {path}')
        got = _sha256_file(path)
        if got != row['sha256']:
            raise RuntimeError(
                f'hash divergente {inst["id"]}: manifesto={row["sha256"]} atual={got}'
            )
        for key, val in [('familia', inst['familia']), ('estrato', inst['estrato'])]:
            if row[key] != str(val):
                raise RuntimeError(f'{inst["id"]}: {key} manifesto={row[key]} catálogo={val}')
        for key, val in [('n', inst['n']), ('m', inst['m']), ('r', inst['r'])]:
            if float(row[key]) != float(val):
                raise RuntimeError(f'{inst["id"]}: {key} manifesto={row[key]} catálogo={val}')


def _baseline_opt(inst):
    A_r = construir_arcos_alcance(inst['V'], inst['adj'], inst['r'])
    model, _y, _f, _na, _nv = construir_modelo_baseline(
        inst['S'], inst['T'], inst['V'], A_r,
    )
    model.Params.OutputFlag = 0
    model.Params.Seed = SOLVER_SEED
    model.Params.Threads = THREADS
    model.Params.TimeLimit = BASELINE_TIME_LIMIT
    t0 = time.perf_counter()
    model.optimize()
    runtime = time.perf_counter() - t0
    status = int(model.Status)
    out = {
        'obj': None,
        'status': 'OPTIMAL' if status == GRB.OPTIMAL else (
            'TIME_LIMIT' if status == GRB.TIME_LIMIT else str(status)
        ),
        'runtime': runtime,
        'gurobi_status': status,
    }
    if status == GRB.OPTIMAL:
        out['obj'] = float(model.ObjVal)
    model.dispose()
    return out, A_r


def _fcc_opt(inst, A_r):
    try:
        val, meta = opt_fcc(
            inst['S'], inst['T'], inst['V'], A_r,
            forma='separada', max_W=MAX_W, seed=SOLVER_SEED,
            threads=THREADS, time_limit=BASELINE_TIME_LIMIT,
        )
        return {
            'obj': val,
            'status': 'OPTIMAL',
            'n_W': meta.get('n_W'),
            'runtime': meta.get('runtime'),
        }
    except CapExceeded:
        return {'obj': None, 'status': 'cap_exceeded', 'n_W': None, 'runtime': None}
    except RuntimeError as exc:
        return {'obj': None, 'status': f'not_optimal:{exc}', 'n_W': None, 'runtime': None}


def _refs(inst):
    enum_obj = None
    enum_status = 'not_run_cap'
    if inst['n'] <= N_OPT_ENUM:
        enum_obj = opt_por_enumeracao(
            inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'],
        )
        enum_status = 'OPTIMAL' if enum_obj is not None else 'no_feasible_solution'

    baseline, A_r = _baseline_opt(inst)
    fcc = _fcc_opt(inst, A_r)

    if enum_status == 'OPTIMAL':
        opt = float(enum_obj)
        fonte = 'enum'
    elif baseline['status'] == 'OPTIMAL':
        opt = float(baseline['obj'])
        fonte = 'mip_base'
    else:
        opt = None
        fonte = ''

    reference_failure = False
    reasons = []
    if enum_status == 'OPTIMAL' and baseline['status'] == 'OPTIMAL':
        if abs(float(enum_obj) - float(baseline['obj'])) > EPS:
            reference_failure = True
            reasons.append(f'enum={enum_obj} != baseline={baseline["obj"]}')
    if opt is not None and fcc['status'] == 'OPTIMAL':
        if abs(float(fcc['obj']) - float(opt)) > EPS:
            reference_failure = True
            reasons.append(f'fcc={fcc["obj"]} != opt={opt}')
    if opt is None:
        reference_failure = True
        reasons.append('sem referência exacta')

    return {
        'opt': opt,
        'fonte_opt': fonte,
        'enum_obj': enum_obj,
        'enum_status': enum_status,
        'baseline_obj': baseline['obj'],
        'baseline_status': baseline['status'],
        'baseline_runtime': baseline['runtime'],
        'fcc_obj': fcc['obj'],
        'fcc_status': fcc['status'],
        'fcc_runtime': fcc['runtime'],
        'n_W': fcc['n_W'],
        'reference_failure': reference_failure,
        'reference_notes': '; '.join(reasons),
    }


def _alg(inst, variant):
    t0 = time.perf_counter()
    if variant == 'path-alg1':
        res = certificar_path(inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'])
    elif variant == 'cycle-alg2':
        res = certificar_cycle(inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'])
    elif variant.startswith('spider-'):
        res = certificar_spider(
            inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'], variant,
        )
    else:
        raise ValueError(variant)
    runtime = time.perf_counter() - t0
    feasible = None
    if res['status'] == 'ok':
        feasible = viavel(
            inst['S'], inst['T'], inst['V'], inst['adj'], inst['r'], res['C'],
        )
    return res, feasible, runtime


def _classificar(res, feasible, refs):
    if refs['reference_failure']:
        return 'reference_failure', False, False
    if res['status'] == 'unspecified':
        return 'unspecified', False, False
    if res['status'] != 'ok':
        return 'implementation_error', False, False
    if res['obj'] != len(res['C']):
        return 'implementation_error', False, False
    if not feasible:
        return 'infeasible_solution', False, False
    opt = refs['opt']
    acordo_obj = abs(float(res['obj']) - float(opt)) <= EPS
    if acordo_obj:
        return 'agreement', True, True
    if float(res['obj']) > float(opt):
        return 'suboptimal', False, True
    return 'objective_below_reference', False, True


def main():
    catalogo = catalogo_oficial()
    manifesto = _carregar_manifesto()
    _validar_manifesto(catalogo, manifesto)

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    commit = commit_atual()
    linhas = []
    for inst in catalogo:
        print('refs', inst['id'], flush=True)
        refs = _refs(inst)
        for variant in variantes_para(inst):
            print(' ', variant, flush=True)
            res, feasible, alg_runtime = _alg(inst, variant)
            resultado, acordo_obj, acordo_viab = _classificar(res, feasible, refs)
            row = {
                'id': inst['id'],
                'familia': inst['familia'],
                'variante': variant,
                'n': inst['n'],
                'm': inst['m'],
                'r': inst['r'],
                'seed': '' if inst['seed'] is None else inst['seed'],
                'sha256': manifesto[inst['id']]['sha256'],
                'estrato': inst['estrato'],
                'n_radiais': '' if not inst.get('radiais') else len(inst['radiais']),
                'alg_status': res['status'],
                'alg_obj': '' if res['obj'] is None else res['obj'],
                'alg_C': json.dumps(res['C'], ensure_ascii=False),
                'alg_viavel': '' if feasible is None else int(bool(feasible)),
                'alg_runtime': alg_runtime,
                'opt': '' if refs['opt'] is None else refs['opt'],
                'fonte_opt': refs['fonte_opt'],
                'baseline_obj': '' if refs['baseline_obj'] is None else refs['baseline_obj'],
                'baseline_status': refs['baseline_status'],
                'baseline_runtime': refs['baseline_runtime'],
                'enum_obj': '' if refs['enum_obj'] is None else refs['enum_obj'],
                'enum_status': refs['enum_status'],
                'fcc_obj': '' if refs['fcc_obj'] is None else refs['fcc_obj'],
                'fcc_status': refs['fcc_status'],
                'fcc_runtime': '' if refs['fcc_runtime'] is None else refs['fcc_runtime'],
                'fc3_status': 'OPEN',
                'acordo_obj': int(bool(acordo_obj)),
                'acordo_viabilidade': int(bool(acordo_viab)),
                'resultado': resultado,
                'max_W': MAX_W,
                'n_W': '' if refs['n_W'] is None else refs['n_W'],
                'solver_seed': SOLVER_SEED,
                'threads': THREADS,
                'notes': '; '.join(x for x in [res['notes'], refs['reference_notes']] if x),
                'commit': commit,
            }
            linhas.append(row)

    campos = [
        'id', 'familia', 'variante', 'n', 'm', 'r', 'seed', 'sha256', 'estrato',
        'n_radiais', 'alg_status', 'alg_obj', 'alg_C', 'alg_viavel', 'alg_runtime',
        'opt', 'fonte_opt', 'baseline_obj', 'baseline_status', 'baseline_runtime',
        'enum_obj', 'enum_status', 'fcc_obj', 'fcc_status', 'fcc_runtime',
        'fc3_status', 'acordo_obj', 'acordo_viabilidade', 'resultado', 'max_W',
        'n_W', 'solver_seed', 'threads', 'notes', 'commit',
    ]
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print('csv', CSV_PATH)


if __name__ == '__main__':
    main()
