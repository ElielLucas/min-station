"""Smoke test Gurobi AS-02 para o checkout local, sem gerar resultados históricos.

Uso (na raiz): python3 experiments/alternative-formulations/run_as02_smoke.py
"""
from math import isclose

from as02_model_a import Instance, build_A, compile_u, prepare_K
from as02_solve import solve_gurobi
from experiments.cuts.synthetic import make_Sec59


def main():
    from gurobipy import GRB

    S, T, V, adj, arcs, r, _ = make_Sec59(L=7, r=1)
    instance = Instance(tuple(V), tuple(S), tuple(T), tuple(arcs), r)
    K = prepare_K(instance, adj, r)
    model, vars_by_key, meta = build_A(instance, (('s1', 's2'), ('s3',)), K, relax=True)
    model.Params.Threads = 1
    model.Params.Seed = 0
    model.Params.TimeLimit = 60
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f'AS02 A2+K não ótima: status={model.Status}')
    control = solve_gurobi(compile_u(instance, K, relax=True), threads=1)
    if control.status != 'OPTIMAL':
        raise RuntimeError(f'AS02 U+K não ótima: {control.status}')
    print(f'Sec59 | U+K LP={control.objective:.9f} | A2+K LP={model.ObjVal:.9f}')
    print(f'Gurobi | {meta} | y={len([key for key in vars_by_key if key[0] == "y"])}')
    if not (isclose(control.objective, 11/3, abs_tol=1e-6) and
            isclose(model.ObjVal, 9/2, abs_tol=1e-6)):
        raise AssertionError('Regressão LP Sec59 falhou')
    print('AS02_SMOKE_PASS (numérico, não é revisão matemática independente)')


if __name__ == '__main__':
    main()
