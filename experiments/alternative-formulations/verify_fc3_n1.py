#!/usr/bin/env python3
"""N1-T3: validação em duas direções antes de QUALQUER comparação LP.

Execução: PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_fc3_n1.py
Não usar `--lp-only`: a ordem é obrigatória. Instâncias SOURCE opcionais
são verificadas após a equivalência e só quando cabem nos caps.

Artefatos novos gerados: n1-t3-validacao.csv e n1-t3-lp-invariantes.csv;
não modifica resultados históricos.
"""
import argparse
import csv
from itertools import combinations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for path in (str(HERE), str(ROOT), str(ROOT / 'experiments' / 'cuts')):
    if path not in sys.path:
        sys.path.insert(0, path)

from gurobipy import GRB
from independent_validator import viavel, opt_por_enumeracao
from synthetic import (make_CaminhoABC, make_Direct0, make_SharedTerminal,
                       make_StayPut, make_StayPutIsolado, make_TermRelay,
                       make_TermRelayForced, make_Tri)
from fc3 import FC3SizeExceeded, build_fc3_plus_k, construir_modelo_fc3, lp_fc3
from fcc import lp_fcc
from fcc_k import build_fcc_plus_k, prepare_k
from source_controls_fc3_n1 import (make_source_c5, make_source_g2,
                                    make_two_components)

EPS = 1e-6
OUT = ROOT / 'results' / 'alternative-formulations'


def _status_is_feasible(model, label):
    if model.Status not in (GRB.OPTIMAL, GRB.INFEASIBLE):
        raise RuntimeError(f'{label}: status não certificado {model.Status}')
    return model.Status == GRB.OPTIMAL


def _fix_y(model, y, V, C):
    chosen = set(C)
    for v in V:
        y[v].LB = float(v in chosen)
        y[v].UB = float(v in chosen)
    model.update()
    model.optimize()


def _unfix_y(model, y, V):
    for v in V:
        y[v].LB, y[v].UB = 0.0, 1.0
    model.update()


def validate_instance(inst):
    S, T, V, adj, A_r, r, meta = inst
    name = meta['name']
    K, khash, _ = prepare_k(S, T, V, adj, A_r, r)
    fcck, ycc, _, metacc = build_fcc_plus_k(
        S, T, V, adj, A_r, r, K=K, k_hash=khash)
    c3k = None
    try:
        c3k, yc3, _, metac3 = build_fc3_plus_k(
            S, T, V, adj, A_r, r, K=K, k_hash=khash)
        c3, yc3raw, _, meta_raw = construir_modelo_fc3(S, T, V, A_r)
    except Exception:
        if c3k is not None:
            c3k.dispose()
        fcck.dispose()
        raise
    try:
        assert metacc['k_hash'] == metac3['k_hash'] == khash
        for model in (fcck, c3k, c3):
            model.Params.OutputFlag = 0
            model.Params.Threads = 1
            model.Params.Seed = 42
            model.Params.DualReductions = 0
            model.Params.Method = 1
        counts = {'n_instalacoes': 0, 'viavel_sim_fc3_nao': 0,
                  'viavel_nao_fc3_sim': 0, 'viavel_sim_fcck_nao': 0,
                  'viavel_nao_fcck_sim': 0, 'viavel_sim_fc3k_nao': 0,
                  'viavel_nao_fc3k_sim': 0, 'n_viaveis': 0, 'n_inviaveis': 0}
        if 'witness_C' in meta and not viavel(S, T, V, adj, r, meta['witness_C']):
            raise AssertionError(f'{name}: controle multicomponente não é viável')
        for k in range(len(V) + 1):
            for C in combinations(V, k):
                oracle = viavel(S, T, V, adj, r, C)
                decisions = {}
                for key, model, y in (('fcck', fcck, ycc),
                                      ('fc3', c3, yc3raw),
                                      ('fc3k', c3k, yc3)):
                    _fix_y(model, y, V, C)
                    decisions[key] = _status_is_feasible(model, key)
                    if oracle != decisions[key]:
                        counts[f'viavel_{"sim" if oracle else "nao"}_{key}_{"sim" if decisions[key] else "nao"}'] += 1
                counts['n_instalacoes'] += 1
                counts['n_viaveis' if oracle else 'n_inviaveis'] += 1
                if any(oracle != x for x in decisions.values()):
                    raise AssertionError(f'DIVERGÊNCIA {name} C={C} oracle={oracle} '
                                         f'modelos={decisions}. STOP: não medir LP.')
        # Este método verifica SOMENTE equivalência. Nenhum ObjVal LP é lido
        # antes da passagem completa por TODAS as instâncias.
        return {'instancia': name, 'n': len(V), 'm': len(S), **counts}
    finally:
        c3.dispose()
        c3k.dispose()
        fcck.dispose()


def measure_lp_after_validation(inst):
    """Somente chamar após TODA a bateria por instalação terminar sem falhas."""
    S, T, V, adj, A_r, r, meta = inst
    K, khash, _ = prepare_k(S, T, V, adj, A_r, r)
    zcc, _ = lp_fcc(S, T, V, A_r)
    from fcc_k import lp_fcc_plus_k
    from fc3 import lp_fc3_plus_k
    zcck, metacc = lp_fcc_plus_k(S, T, V, adj, A_r, r, K=K, k_hash=khash)
    zc3, metac3 = lp_fc3(S, T, V, A_r)
    zc3k, metac3k = lp_fc3_plus_k(S, T, V, adj, A_r, r, K=K, k_hash=khash)
    assert metacc['k_hash'] == metac3k['k_hash'] == khash
    if zc3 < zcc - EPS or zc3k < zcck - EPS:
        raise AssertionError(f'{meta["name"]}: dominância F-C3 violada: {zc3}<{zcc} '
                             f'ou {zc3k}<{zcck}')
    opt = opt_por_enumeracao(S, T, V, adj, r)
    if opt is None:
        raise AssertionError(f'{meta["name"]}: instância sem OPT; não interpretar LP')
    if any(z > opt + EPS for z in (zcc, zcck, zc3, zc3k)):
        raise AssertionError(f'{meta["name"]}: LP > OPT certificado={opt}')
    return {'instancia': meta['name'], 'n': len(V), 'm': len(S),
            'k_hash': khash, 'n_K': len(K), 'n_W': metac3['n_W'],
            'network_arcs': metac3k['n_network_arcs'], 'lp_fcc': zcc,
            'lp_fcc_k': zcck, 'lp_fc3': zc3, 'lp_fc3_k': zc3k,
            'opt_enum': opt, 'status': 'COMPUTATIONALLY VERIFIED'}


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _source_regressions():
    rows = []
    for factory in (make_source_g2, make_source_c5):
        S, T, V, adj, A_r, r, meta = factory()
        try:
            z, metadata = lp_fc3(S, T, V, A_r)
        except FC3SizeExceeded as exc:
            rows.append({'instancia': meta['name'], 'n': len(V), 'm': len(S),
                         'expected': meta['lp_fc3_expected'], 'measured': '',
                         'status': 'NOT MEASURED', 'reason': str(exc)})
            continue
        if abs(z - meta['lp_fc3_expected']) > EPS:
            raise AssertionError(f'SOURCE {meta["name"]}: LP={z}; '
                                 f'previsão={meta["lp_fc3_expected"]}')
        rows.append({'instancia': meta['name'], 'n': len(V), 'm': len(S),
                     'expected': meta['lp_fc3_expected'], 'measured': z,
                     'status': 'COMPUTATIONALLY VERIFIED', 'reason': ''})
    _write(OUT / 'n1-t3-source-regressoes.csv', rows)
    for row in rows:
        print('SOURCE', row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-regressions', action='store_true',
                        help='também checa §§8-9, sem ajustar os caps')
    args = parser.parse_args()
    factories = (make_StayPutIsolado, make_StayPut, make_Direct0,
                 make_TermRelay, make_TermRelayForced, make_CaminhoABC,
                 make_SharedTerminal, make_two_components, make_Tri)
    validation_rows, lp_rows = [], []
    instances = [factory() for factory in factories]
    for inst in instances:
        print('VALIDANDO', inst[6]['name'], 'n=', len(inst[2]), flush=True)
        validation_row = validate_instance(inst)
        validation_rows.append(validation_row)
        print('PASS', inst[6]['name'], validation_row['n_instalacoes'],
              'instalações; 0 discordâncias', flush=True)
    # Nenhum LP da N1-T3 é calculado ANTES da equivalência em toda a bateria.
    _write(OUT / 'n1-t3-validacao.csv', validation_rows)
    print('PASS: equivalência por instalação integral; começando LP', flush=True)
    for inst in instances:
        lp_row = measure_lp_after_validation(inst)
        lp_rows.append(lp_row)
        print('PASS LP', inst[6]['name'], 'dominância e OPT verificados', flush=True)
    _write(OUT / 'n1-t3-lp-invariantes.csv', lp_rows)
    print('PASS: invariantes LP; arquivos regeneráveis com PYTHONHASHSEED=0')
    if args.source_regressions:
        _source_regressions()


if __name__ == '__main__':
    main()
