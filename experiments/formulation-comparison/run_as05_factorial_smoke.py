"""Smoke sintético para os seis braços LP, sem produzir evidência de campanha."""
from __future__ import annotations

import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
for folder in (ROOT, HERE, HERE.parent/'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0,str(folder))

from as02_model_a import Instance  # noqa: E402
from as02_solve import solve_scipy  # noqa: E402
from as05_diag_core import _timed_k  # noqa: E402
from as05_factorial import ARMS, WITH_K, compile_factorial, partitions  # noqa: E402
from experiments.cuts.synthetic import make_F1  # noqa: E402


def main():
    from types import SimpleNamespace

    S,T,V,adj,arcs,r,_=make_F1(m=4,k=1)
    ins=Instance(tuple(V),tuple(S),tuple(T),tuple(arcs),int(r))
    loaded=SimpleNamespace(adj=adj)
    a2,a4=partitions(ins,policy='reachability_degree',seed=42)
    K,profile=_timed_k(ins,loaded,validator_method='bitset-v2')
    values={}
    for arm in ARMS:
        model=compile_factorial(ins,arm,cuts=K if arm in WITH_K else (),groups2=a2,groups4=a4)
        solved=solve_scipy(model,time_limit=20)
        if solved.status!='OPTIMAL' or solved.objective is None:
            raise AssertionError(f'Smoke falhou: {arm}: {solved.status}')
        values[arm]=solved.objective
        print(f'{arm}: LP={solved.objective:.9f} vars={len(model.variables)} rows={len(model.equations)}')
    for left,right in (('U','U_K'),('U','A2'),('A2','A4'),
                       ('U_K','A2_K'),('A2_K','A4_K'),('A2','A2_K'),('A4','A4_K')):
        if values[left]>values[right]+1e-6:
            raise AssertionError(f'Dominância violada: {left}->{right}')
    if a4.parent_hash!=a2.partition_hash:
        raise AssertionError('A4 não está ligada ao hash de A2')
    print(f'K validado: {profile["counts"]["unique"]} cortes')
    print('AS05_FACTORIAL_SMOKE_PASS (HiGHS sintético; não é experimento real)')


if __name__=='__main__':
    main()
