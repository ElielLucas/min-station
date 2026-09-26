"""Verificação E5 — Bloco C.6: validador is_valid_cut contra oráculo Gurobi."""
import sys
from pathlib import Path
ROOT = Path('/home/eliel/Documentos/eliel/Unicamp/min-station')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from itertools import combinations
from gurobipy import GRB
from baseline import construir_modelo_baseline
from cuts import is_valid_cut
import synthetic as syn


def check_oraculo(S, T, A_r, Z):
    """Fixa y=0 em Z, y=1 fora; INFEASIBLE ⟺ corte válido."""
    V = sorted(set(u for u, v in A_r) | set(v for u, v in A_r) | set(S) | set(T))
    modelo, y, f, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    for v in V:
        val = 0.0 if v in Z else 1.0
        y[v].lb = val
        y[v].ub = val
    modelo.update()
    modelo.optimize()
    return modelo.Status == GRB.INFEASIBLE


def testar(label, S, T, V, adj, A_r, r, tamanhos=(1, 2)):
    n_test = n_diverg = 0
    for size in tamanhos:
        for combo in combinations(V, size):
            Z = frozenset(combo)
            meu = is_valid_cut(S, T, A_r, Z)
            oraculo = check_oraculo(S, T, A_r, Z)
            n_test += 1
            if meu != oraculo:
                n_diverg += 1
                print(f'  DIVERGÊNCIA em {label}: Z={sorted(Z)}  is_valid_cut={meu}  oráculo={oraculo}')
    status = 'OK' if n_diverg == 0 else 'FALHOU'
    print(f'{label:<16} {n_test} testes, {n_diverg} divergências  [{status}]')
    return n_diverg


def main():
    print('=== Validador is_valid_cut vs oráculo Gurobi (singletons e pares) ===\n')
    total_diverg = 0
    for label, fn in [
        ('Direct0', syn.make_Direct0),
        ('TermRelay', syn.make_TermRelay),
        ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut),
        ('SharedTerminal', syn.make_SharedTerminal),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        total_diverg += testar(label, S, T, V, adj, A_r, r)

    print()
    print('=== Laço completo em y-space nos gabaritos (validate_cuts=True) ===\n')
    from yspace import solve_lp_cutting_plane
    for label, fn in [
        ('Direct0', syn.make_Direct0),
        ('TermRelay', syn.make_TermRelay),
        ('Sec59(L=7)', lambda: syn.make_Sec59(L=7, r=1)),
        ('F2(k=1)', lambda: syn.make_F2(k=1, L=3, r=1)),
        ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut),
        ('SharedTerminal', syn.make_SharedTerminal),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        try:
            res = solve_lp_cutting_plane(S, T, V, adj, A_r, r, max_rounds=30,
                                         time_per_stage=60, seed=42, threads=2,
                                         validate_cuts=True)
            print(f'{label:<16} stage_lp={res["stage_lp"]}  stage_cuts={res["stage_cuts"]}')
        except Exception as e:
            total_diverg += 1
            print(f'{label:<16} EXCEÇÃO: {type(e).__name__}: {e}')

    print()
    if total_diverg == 0:
        print('RESULTADO FINAL: 0 divergências — validador correto.')
    else:
        print(f'RESULTADO FINAL: {total_diverg} divergências — investigar.')


if __name__ == '__main__':
    main()
