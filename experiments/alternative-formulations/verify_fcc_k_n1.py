#!/usr/bin/env python3
"""N1-T3: testar F-CC+K para toda instalação de pequenas instâncias.

Requer Gurobi; aborta ao primeiro desacordo com viavel, antes de medir LP.
Não altera a bateria histórica de verify_fcc.py.
"""
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(ROOT))

from independent_validator import viavel
from fcc_k import fcc_plus_k_y_feasible
from synthetic import (make_CaminhoABC, make_Direct0, make_SharedTerminal,
                       make_StayPut, make_StayPutIsolado, make_TermRelay)


def verify_instance(fab):
    S, T, V, adj, A_r, r, meta = fab()
    truth_true_model_false = truth_false_model_true = 0
    n = 0
    for k in range(len(V)+1):
        for C in combinations(V, k):
            oracle = viavel(S, T, V, adj, r, C)
            model = fcc_plus_k_y_feasible(S, T, V, adj, A_r, r, C)
            n += 1
            truth_true_model_false += int(oracle and not model)
            truth_false_model_true += int(model and not oracle)
            if model != oracle:
                print(f'DIVERGÊNCIA {meta["name"]} C={C} viavel={oracle} fcc+K={model}')
                raise AssertionError('Interrompido antes da medição LP')
    print(f'{meta["name"]}: {n} instalações; divergência viavel→modelo={truth_true_model_false}; '
          f'modelo→viavel={truth_false_model_true}')
    return n


def main():
    total = 0
    for fab in (make_Direct0, make_TermRelay, make_StayPut,
                make_StayPutIsolado, make_CaminhoABC, make_SharedTerminal):
        total += verify_instance(fab)
    print('PASS F-CC+K; instalações verificadas:', total)


if __name__ == '__main__':
    main()
