"""AS22 mathematical, solver, budget, provenance, and real compiler regression tests."""
import copy
import json
import math
import tempfile
import time
import unittest
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from h2_oracle import MatchingOracle,PhysicalInstance
from h2_oracle_schema import Status
from hl_polyhedral import PolyOptions,separate_hl_poly,_find_rational_cut
from hl_poly_supports import select_poly_supports
from run_hl_poly_micro import alternative_paths_fixture,run as micro_run
from run_hl_lp_as22 import load_plan, execute, _work_arm, ROOT
from verify_as13_foundations import k4,reach_arcs,k_cuts,solve_comp_lp


class PolySeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physical,cls.y,cls.support=alternative_paths_fixture()
        cls.opts=PolyOptions(max_support_size=3,max_supports=1,
                    max_oracle_calls=25,total_budget_s=30,per_support_budget_s=25)

    def test_nonuniform_valid_certified_cut_not_cardinality(self):
        report=separate_hl_poly(self.physical,self.y,supports=[self.support],options=self.opts)
        self.assertEqual(report.status,'CUTS_FOUND')
        self.assertEqual(len(report.cuts),1)
        self.assertTrue(report.records[0]['classification_complete'])
        self.assertEqual(report.records[0]['patterns_total'],8)
        self.assertEqual(report.records[0]['patterns_examined']+report.records[0]['patterns_inferred'],8)
        cut=report.cuts[0]
        self.assertGreater(cut.violation,0.15)
        self.assertNotEqual(len({a for _,a in cut.coefficients}),1)
        self.assertGreaterEqual(sum(self.y[v] for v in self.support),1.)
        F=set(self.physical.V)-set(self.support)
        # An independent exact rational check across ALL physical patterns.
        for size in range(4):
            for A in combinations(self.support,size):
                res=MatchingOracle().check(self.physical,F|set(A))
                if res.status==Status.VIABLE:
                    lhs=sum((a for v,a in cut.coefficients if v in A),Fraction(0))
                    self.assertGreaterEqual(lhs,cut.rhs)

    def test_hash_determinism_and_append_only(self):
        a=separate_hl_poly(self.physical,self.y,supports=[self.support],options=self.opts)
        b=separate_hl_poly(self.physical,self.y,supports=[tuple(reversed(self.support))],options=self.opts)
        self.assertEqual(a.cuts[0].certificate_sha256,b.cuts[0].certificate_sha256)
        self.assertEqual(a.cuts[0].cut_hash,b.cuts[0].cut_hash)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'one.json'
            a.save_new(p)
            with self.assertRaises(FileExistsError):b.save_new(p)

    def test_unknown_or_quota_does_not_emit_invalid_cut(self):
        class UnknownOracle(MatchingOracle):
            def check(self,instance,allowed_stations,budget_s=None):
                r=super().check(instance,allowed_stations,budget_s=budget_s)
                return replace(r,status=Status.UNKNOWN,matching_size=None,
                    witness=(),hall_origins=(),hall_destinations=(),reason='INJECTED')
        for settings,engine in [({},UnknownOracle()),
                 ({'max_oracle_calls':2},None),
                 ({'max_patterns_per_support':7},None),
                 ({'per_support_budget_s':0},None),
                 ({'max_support_size':2},None)]:
            p=separate_hl_poly(self.physical,self.y,supports=[self.support],
                             options=replace(self.opts,**settings),oracle=engine)
            self.assertEqual(len(p.cuts),0)
            self.assertEqual(p.status,'PARTIAL_BUDGET')

    def test_zero_violation_no_cut_if_lp_is_integral_viable(self):
        y={v:0. for v in self.physical.V};y['a']=1.
        r=separate_hl_poly(self.physical,y,supports=[self.support],options=self.opts)
        self.assertEqual(r.status,'NO_CUTS')
        self.assertTrue(r.records[0]['classification_complete'])

    def test_rationalization_requires_exact_positive_gap(self):
        R=('a','b','c')
        viable=[1,6,3,5,7]  # a OR (b,c) upward closed
        # Numeric margin but max_denominator=1 can lose certain facets;
        # regardless, returned beta must be EXACT for every viable pattern.
        for denom in (1,2,8,128):
            candidate,reason=_find_rational_cut(R,self.y,viable,
                          max_denominator=denom,min_violation=1e-6)
            if candidate:
                alpha,beta,gap=candidate
                self.assertTrue(all(a>=0 for a in alpha))
                self.assertEqual(beta,min(sum((alpha[i] for i in range(3)
                      if mask&(1<<i)),Fraction(0)) for mask in viable))
                self.assertGreater(gap,1e-6)

    def test_bad_inputs_are_rejected(self):
        with self.assertRaises(ValueError):PolyOptions(max_denominator=0)
        with self.assertRaises(ValueError):PolyOptions(total_budget_s=float('nan'))
        with self.assertRaises(ValueError):separate_hl_poly(self.physical,
            {**self.y,'a':float('nan')},supports=[self.support])
        with self.assertRaises(ValueError):separate_hl_poly(self.physical,
            self.y,supports=[('a','unknown')])


class SelectionTests(unittest.TestCase):
    def test_interaction_gets_reserved_slot(self):
        V=tuple(range(7));y={v:.5 for v in V}
        Ks=[(0,1),(1,2),(3,4)]
        rows,meta=select_poly_supports(V,y,k_supports=Ks,
                 max_support_size=3,max_supports=2,min_interaction_slots=1)
        self.assertEqual(len(rows),2)
        self.assertEqual(meta['interaction_slots_filled'],1)
        self.assertTrue(meta['selected_kinds'][0].startswith('K_'))
        self.assertEqual(meta['selected_kinds'][0],'K_UNION')
        self.assertEqual((rows,meta),select_poly_supports(V,y,k_supports=Ks[::-1],
                 max_support_size=3,max_supports=2,min_interaction_slots=1))

    def test_large_k_projection_never_claims_validity(self):
        V=tuple(range(15));y={v:.1 for v in V}
        rows,meta=select_poly_supports(V,y,k_supports=[tuple(range(12)),tuple(range(3,15))],
                      max_support_size=7,max_supports=4,min_interaction_slots=1)
        self.assertTrue(rows)
        self.assertTrue(all(len(r)<=7 for r in rows))
        self.assertTrue(meta['selection_is_not_certification'])


class IntegrationTests(unittest.TestCase):
    def test_comp_k_real_compiler_k4_gains_with_certified_cut(self):
        raw,W=k4();S,T,V,adj,r=raw
        arcs=reach_arcs(V,adj,r);K=k_cuts(S,T,V,adj,r,arcs)
        loaded=SimpleNamespace(S=S,T=T,V=V,adj=adj,A_r=arcs,r=r,
                                instance_sha256='K4-AS22-SYNTHETIC')
        class Var:
            def __init__(self,v):self.v=v
            def __rmul__(self,n):return self.v,float(n)
        class Expr:
            def __init__(self,terms):self.terms=dict(terms)
            def __ge__(self,rhs):return self.terms,float(rhs)
        class GP:
            @staticmethod
            def quicksum(terms):return Expr(terms)
        class Model:
            def __init__(self):self.more=[];self.NumConstrs=30
            def addConstr(self,row,name):self.more.append(row);self.NumConstrs+=1
            def update(self):pass
        def builder(compiled,policy,deadline):return Model(),{v:Var(v) for v in V},GP
        def solve(model,gp,deadline,ycols):
            obj,y,_=solve_comp_lp(S,T,V,arcs,K,more=model.more)
            return {'status':'OPTIMAL','lp_objective':obj,'y_star':y}
        cfg={'max_variables':1000000,'max_support_size':4,'max_supports':4,
             'max_pairs':64,'max_k_seeds':48,'min_interaction_slots':2,
             'max_oracle_calls':100,'max_patterns_per_support':20,
             'max_denominator':128,'total_budget_s':24,'per_support_budget_s':8,
             'min_violation':1e-6,'max_cuts':3}
        with (patch('run_hl_lp_as22.load_instance',return_value=loaded),
              patch('run_hl_lp_as22.prepare_K',return_value=K),
              patch('run_hl_lp_as22._solver',side_effect=builder),
              patch('run_hl_lp_as22._optimize',side_effect=solve)):
            b=_work_arm({'source_sha256':'K4-AS22-SYNTHETIC'},{},ROOT,
                             'U_K',{},cfg,time.monotonic()+60)
            h=_work_arm({'source_sha256':'K4-AS22-SYNTHETIC'},{},ROOT,
                             'U_K_HL',{},cfg,time.monotonic()+60)
        self.assertAlmostEqual(b['lp_objective'],2.)
        self.assertAlmostEqual(h['lp_objective'],3.)
        self.assertGreater(h['hl_accepted'],0)
        self.assertEqual(h['separation']['stage'],'AS22')
        self.assertIn('K_UNION',h['selection']['selected_kinds'])

    def test_micro_has_both_independent_witnesses(self):
        d=micro_run()
        self.assertAlmostEqual(d['k4']['baseline_comp_k_lp'],2)
        self.assertAlmostEqual(d['k4']['strengthened_comp_k_hl_lp'],3)
        self.assertGreater(d['nonuniform_fixture']['general_cut']['violation'],0)


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan,cls.sha,cls.source=load_plan()

    def test_freeze_and_source_provenance(self):
        self.assertEqual(len(self.plan['cases']),6)
        self.assertEqual(len({c['raw_graph_id'] for c in self.plan['cases']}),6)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'mutated.json'
            q=copy.deepcopy(self.plan);q['hl']['max_denominator']=999
            p.write_text(json.dumps(q))
            with self.assertRaises(ValueError):load_plan(p)
            q=copy.deepcopy(self.plan);q['cases'].pop()
            p.write_text(json.dumps(q))
            with self.assertRaises(ValueError):load_plan(p)

    def test_dryrun_is_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'one'
            result=execute(self.plan,self.sha,self.source,ROOT,out,
                      {c['name'] for c in self.plan['cases']},dry_run=True)
            self.assertEqual(result['gate'],'NOT_EXECUTED')
            self.assertEqual(result['stage'],'AS22')
            self.assertEqual(result['arm_rows'],12)
            with self.assertRaises(FileExistsError):
                execute(self.plan,self.sha,self.source,ROOT,out,
                      {c['name'] for c in self.plan['cases']},dry_run=True)


if __name__=='__main__':unittest.main()
