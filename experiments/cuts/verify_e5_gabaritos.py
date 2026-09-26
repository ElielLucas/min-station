"""Verificação E5 — Bloco B.4 e B.5.1: gabaritos pós-variante U e regressão de equivalência."""
import sys
from pathlib import Path
ROOT = Path('/home/eliel/Documentos/eliel/Unicamp/min-station')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))

from gurobipy import GRB
from baseline import construir_modelo_baseline
import synthetic as syn


def resolver(nome, S, T, V, adj, A_r, r, meta):
    modelo, y, f, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.optimize()
    status = modelo.Status
    if status == GRB.OPTIMAL:
        obj = modelo.ObjVal
    elif status == GRB.INFEASIBLE:
        obj = None
    else:
        obj = f'status={status}'
    esperado = meta.get('OPT')
    ok = (obj == esperado) if isinstance(obj, (int, float)) else False
    tag = 'PASS' if ok else ('INFEASIBLE' if status == GRB.INFEASIBLE else 'FAIL')
    print(f'{nome:<20} OPT esperado={esperado}  obtido={obj}  status={status}  {tag}')
    return status, obj


def main():
    print('=== Gabaritos existentes (regressão pós-variante-U) ===')
    for label, fn, kwargs in [
        ('F1(2,2)', syn.make_F1, dict(m=2, k=2, r=1)),
        ('F1(2,3)', syn.make_F1, dict(m=2, k=3, r=1)),
        ('F2(k=1)', syn.make_F2, dict(k=1, L=3, r=1)),
        ('Tri', syn.make_Tri, dict(r=1)),
        ('Sec59(L=7)', syn.make_Sec59, dict(L=7, r=1)),
    ]:
        S, T, V, adj, A_r, r, meta = fn(**kwargs)
        resolver(label, S, T, V, adj, A_r, r, meta)

    print()
    print('=== Gabaritos novos: validade de cortes (C.1) ===')
    for label, fn in [('Direct0', syn.make_Direct0), ('TermRelay', syn.make_TermRelay)]:
        S, T, V, adj, A_r, r, meta = fn()
        resolver(label, S, T, V, adj, A_r, r, meta)

    print()
    print('=== Gabaritos novos: variante U / S∩T (B.4) ===')
    for label, fn in [('StayPut', syn.make_StayPut), ('SharedTerminal', syn.make_SharedTerminal)]:
        S, T, V, adj, A_r, r, meta = fn()
        print(f'  S={S} T={T} S∩T={set(S) & set(T)}')
        resolver(label, S, T, V, adj, A_r, r, meta)


if __name__ == '__main__':
    main()
