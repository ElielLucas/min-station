#!/usr/bin/env python3
"""AS22 synthetic certificates: nonuniform-facet witness and real COMP+K K4.

Does not measure real benchmarks, authorize MIP or replace LP Gurobi trials.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_oracle import PhysicalInstance
from h2_oracle_schema import canonical_json
from hl_polyhedral import PolyOptions, separate_hl_poly
from verify_as13_foundations import k4, reach_arcs, k_cuts, solve_comp_lp


def alternative_paths_fixture():
    """r=1: s-a-t or s-b-c-t; feasible patterns a OR (b AND c)."""
    V = ('s','t','a','b','c')
    edges=(('s','a'),('a','t'),('s','b'),('b','c'),('c','t'))
    adj={v:[] for v in V}
    for u,v in edges:
        adj[u].append((v,1))
        adj[v].append((u,1))
    physical=PhysicalInstance(V,('s',),('t',),adj,1)
    y={v:0. for v in V}
    y.update(a=.1,b=.5,c=.5)
    return physical,y,('a','b','c')


def run():
    physical, y, support=alternative_paths_fixture()
    alternate=separate_hl_poly(physical,y,supports=[support],
                      options=PolyOptions(max_support_size=3,max_supports=1))
    assert len(alternate.cuts)==1, alternate.to_dict()
    cut=alternate.cuts[0]
    assert len(set(cut.coefficients[i][1] for i in range(3)))>1
    # No violated uniform-cardinality inequality: min feasible cardinality
    # is 1, whereas the LP support sum is 1.1.
    assert sum(y[v] for v in support)>=1.

    raw,W=k4()
    S,T,V,adj,r=raw
    arcs=reach_arcs(V,adj,r)
    K=k_cuts(S,T,V,adj,r,arcs)
    baseline,lp_point,_=solve_comp_lp(S,T,V,arcs,K)
    k4_report=separate_hl_poly(PhysicalInstance.from_tuple(raw),lp_point,
              supports=[W],options=PolyOptions(max_support_size=4,max_supports=1))
    assert len(k4_report.cuts)==1,k4_report.to_dict()
    cut_k4=k4_report.cuts[0]
    strengthened,_,_=solve_comp_lp(S,T,V,arcs,K,
                               more=[(dict(cut_k4.coefficients),cut_k4.rhs)])
    assert abs(baseline-2.)<1e-7 and abs(strengthened-3.)<1e-7
    return {'schema_version':'AS22-HL-MICRO-v1','stage':'AS22',
        'synthetic_only':True,'not_real_comp_k_gain_evidence':True,
        'nonuniform_fixture':{
            'statement':'viable iff a OR (b AND c); cardinality not violated',
            'lp_point_on_support':{v:y[v] for v in support},
            'lp_mass':sum(y[v] for v in support),
            'minimum_feasible_cardinality':1,
            'general_cut':cut.to_dict(),
            'separation':alternate.to_dict()},
        'k4':{'baseline_comp_k_lp':baseline,'strengthened_comp_k_hl_lp':strengthened,
              'cut':cut_k4.to_dict(),'separation':k4_report.to_dict()},
        'solver_for_k4':'scipy.optimize.linprog(method=highs)',
        'scientific_note':'synthetic verification only; no empirical assertion about real benchmark gain'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as out:
        out.write(canonical_json(result)+'\n')
    print(json.dumps({'status':'CERTIFIED_SYNTHETIC_ONLY',
          'k4_lp':[result['k4']['baseline_comp_k_lp'],result['k4']['strengthened_comp_k_hl_lp']],
          'nonuniform_cut':result['nonuniform_fixture']['general_cut']['coefficients'],
          'output':str(args.output)},ensure_ascii=False))

if __name__=='__main__':main()
