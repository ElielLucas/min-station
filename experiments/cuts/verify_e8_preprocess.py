"""
Verificação do pré-processamento experimental (preprocess.py): o OPT do
modelo compacto com as fixações (y=0 em mortos/dominados, y=1 em
obrigatórios) tem de ser igual ao OPT sem fixações.

Inclui TermRelayForced, contraexemplo da versão anterior de find_mandatory
(que testava só não terminais e levava o OPT de 1 para 2), e PathM1 (m=1,
em que um terminal não pode dominar).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
import synthetic as syn
from baseline import construir_modelo_baseline
from harness import load_instance
from preprocess import preprocess
from verify_e8_oracle import make_PathM1


def opt_compacto(S, T, V, A_r, fix0=(), fix1=(), tl=300):
    modelo, y, f, _, _ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.Params.TimeLimit = tl
    for var in modelo.getVars():
        if var.VarName.startswith('f['):
            var.vtype = GRB.CONTINUOUS
    for v in fix0:
        y[v].ub = 0
    for v in fix1:
        y[v].lb = 1
    modelo.update()
    modelo.optimize()
    if modelo.Status == GRB.OPTIMAL:
        return modelo.ObjVal
    return f'status={modelo.Status}'


def checar(label, S, T, V, adj, A_r):
    t0 = time.monotonic()
    pp = preprocess(S, T, V, adj, A_r)
    t_pp = time.monotonic() - t0
    sem = opt_compacto(S, T, V, A_r)
    com = opt_compacto(S, T, V, A_r, pp['fixados_0'], pp['fixados_1'])
    ok = sem == com and not isinstance(sem, str)
    print(f'{label:<34} OPT sem={sem} com={com} fix0={pp["n_removidos"]} '
          f'fix1={pp["n_obrigatorios"]} t_pp={t_pp:.1f}s [{"PASS" if ok else "FAIL"}]',
          flush=True)
    return ok


def main():
    ok = True
    for label, fn in [
        ('Direct0', syn.make_Direct0), ('TermRelay', syn.make_TermRelay),
        ('TermRelayForced', syn.make_TermRelayForced), ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut), ('SharedTerminal', syn.make_SharedTerminal),
        ('F1(2,2)', lambda: syn.make_F1(m=2, k=2, r=1)),
        ('F2(k=1)', lambda: syn.make_F2(k=1, L=3, r=1)),
        ('Sec59(L=7)', lambda: syn.make_Sec59(L=7, r=1)),
        ('PathM1', make_PathM1),
    ]:
        S, T, V, adj, A_r, r, meta = fn()
        ok &= checar(label, S, T, V, adj, A_r)

    for fname, R in [('Chicago_n400_m1130_st15.txt', 7)]:
        S, T, V, adj, A_r, r = load_instance(ROOT / 'instances' / fname, R=R)
        ok &= checar(fname, S, T, V, adj, A_r)

    print('\nRESULTADO FINAL:', 'todos PASS' if ok else 'há FAIL — investigar')
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
