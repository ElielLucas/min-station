"""
Verifica OPT = 0 ⟺ r ≥ λ* (instance_features.lambda_estrela) nos gabaritos de
synthetic.py, variando r de 1 até λ*+1 e resolvendo o baseline para cada r.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments' / 'cuts'))
sys.path.insert(0, str(ROOT / 'src' / 'converters'))

from gurobipy import GRB
import synthetic as syn
from baseline import construir_modelo_baseline
from ms_utils import construir_arcos_alcance
from instance_features import lambda_estrela


def opt(S, T, V, adj, r):
    A_r = construir_arcos_alcance(V, adj, r)
    modelo, *_ = construir_modelo_baseline(S, T, V, A_r)
    modelo.Params.OutputFlag = 0
    modelo.optimize()
    return modelo.ObjVal if modelo.Status == GRB.OPTIMAL else None


def main():
    falhas = 0
    casos = 0
    for label, fn in [
        ('Direct0', syn.make_Direct0), ('TermRelay', syn.make_TermRelay),
        ('TermRelayForced', syn.make_TermRelayForced), ('Tri', syn.make_Tri),
        ('StayPut', syn.make_StayPut), ('SharedTerminal', syn.make_SharedTerminal),
        ('F1(2,2)', lambda: syn.make_F1(m=2, k=2, r=1)),
        ('F2(k=1)', lambda: syn.make_F2(k=1, L=3, r=1)),
        ('Sec59(L=7)', lambda: syn.make_Sec59(L=7, r=1)),
    ]:
        S, T, V, adj, _, _, _ = fn()
        lam = lambda_estrela(S, T, adj)
        linha = []
        for r in range(1, int(lam) + 2):
            o = opt(S, T, V, adj, r)
            ok = (o == 0) == (r >= lam)
            casos += 1
            falhas += not ok
            linha.append(f'r={r}:OPT={o}{"" if ok else "!"}')
        print(f'{label:<16} λ*={lam}  ' + '  '.join(linha))
    print(f'\n{casos} casos, {falhas} falhas')
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()
