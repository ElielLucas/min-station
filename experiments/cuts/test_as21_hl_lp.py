"""AS21 negative guards, certificate semantics and real COMP+K integration."""
import copy
import json
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from h2_oracle import PhysicalInstance, MatchingOracle
from h2_oracle_schema import Status
from hl_layered import LayeredOptions, separate_hl_layered
from hl_structural import select_structural_supports
from run_hl_lp_as21 import (load_plan, execute, _work_arm, ROOT)
from analyze_hl_lp_as21 import analyze, compare_as20
from verify_as13_foundations import k4, reach_arcs, k_cuts, solve_comp_lp


class LayeredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.W = k4()
        cls.S, cls.T, cls.V, cls.adj, cls.r = cls.raw
        cls.physical = PhysicalInstance.from_tuple(cls.raw)
        cls.y = {v: (.5 if v in cls.W else 0.) for v in cls.V}
        cls.options = LayeredOptions(max_support_size=4, max_supports=1,
                         max_oracle_calls=50, total_budget_s=25, per_support_budget_s=20)

    def test_exact_lower_layers_K4_11_not_16(self):
        result = separate_hl_layered(self.physical, self.y, supports=[self.W], options=self.options)
        self.assertEqual(result.status, 'CUTS_FOUND')
        self.assertEqual(len(result.cuts), 1)
        self.assertEqual(str(result.cuts[0].rhs), '3')
        self.assertEqual(result.oracle_calls, 11)
        self.assertEqual(result.records[0]['patterns_required'], 11)
        self.assertEqual(result.records[0]['full_patterns'], 16)
        self.assertEqual(result.records[0]['patterns_proven_infeasible'], 11)
        self.assertEqual(result.records[0]['method'], 'LOWER_LAYERS_INFEASIBLE')

    def test_certificate_stable_under_support_permutation_and_cache(self):
        a = separate_hl_layered(self.physical,self.y,supports=[self.W],options=self.options)
        b = separate_hl_layered(self.physical,self.y,supports=[self.W[::-1]],options=self.options)
        self.assertEqual(a.cuts[0].certificate_sha256,b.cuts[0].certificate_sha256)
        self.assertEqual(a.cuts[0].cut_hash,b.cuts[0].cut_hash)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'evidence.json'
            a.save_new(path)
            with self.assertRaises(FileExistsError): b.save_new(path)

    def test_witness_below_target_prevents_cut(self):
        # With all relays already available outside R, complement is viable.
        y = {v: 0. for v in self.V}
        result = separate_hl_layered(self.physical,y,supports=[(self.W[0],)],options=self.options)
        self.assertEqual(result.cuts, ())
        self.assertEqual(result.records[0]['status'],'NO_CUT_WITNESS')
        self.assertEqual(result.oracle_calls,1)

    def test_unknown_never_proves_infeasibility(self):
        class UnknownOracle(MatchingOracle):
            def check(self, instance, allowed_stations, budget_s=None):
                ans=super().check(instance,allowed_stations,budget_s=budget_s)
                return replace(ans, status=Status.UNKNOWN, matching_size=None,
                               witness=(), hall_origins=(), hall_destinations=(),reason='INJECTED')
        ans=separate_hl_layered(self.physical,self.y,supports=[self.W],options=self.options,oracle=UnknownOracle())
        self.assertFalse(ans.cuts)
        self.assertEqual(ans.status,'PARTIAL_BUDGET')
        self.assertEqual(ans.records[0]['reason'],'UNKNOWN_PHYSICAL_ORACLE')

    def test_budget_and_pattern_cap_abstain(self):
        for changes, status in [({'max_oracle_calls': 3},'ABSTAIN'),
                                ({'max_patterns_per_support': 10},'SKIPPED_PATTERN_CAP'),
                                ({'max_rhs': 2},'SKIPPED_RHS_CAP'),
                                ({'total_budget_s': 0},None)]:
            options=replace(self.options,**changes)
            ans=separate_hl_layered(self.physical,self.y,supports=[self.W],options=options)
            self.assertFalse(ans.cuts)
            self.assertEqual(ans.status,'PARTIAL_BUDGET')
            if status: self.assertEqual(ans.records[0]['status'],status)

    def test_no_global_enumeration_and_validation(self):
        with self.assertRaises(ValueError):
            separate_hl_layered(self.physical,self.y,supports=[('missing',)],options=self.options)
        with self.assertRaises(ValueError):
            separate_hl_layered(self.physical,{**self.y, self.W[0]: float('nan')},
                                supports=[self.W],options=self.options)
        with self.assertRaises(ValueError): LayeredOptions(max_rhs=0)
        with self.assertRaises(ValueError): LayeredOptions(max_oracle_calls=-1)


class SelectionTests(unittest.TestCase):
    def test_k4_interaction_preserved(self):
        raw, W=k4(); S,T,V,adj,r=raw
        arcs=reach_arcs(V,adj,r); K=k_cuts(S,T,V,adj,r,arcs)
        _,y,_=solve_comp_lp(S,T,V,arcs,K)
        supports,meta=select_structural_supports(V,y,k_supports=K,
                        max_support_size=4,max_supports=3)
        self.assertEqual(supports[0],tuple(W))
        self.assertEqual(meta['selected_kinds'][0],'K_UNION')

    def test_large_K_projection_explicitly_not_certificate(self):
        V=tuple(range(20)); y={v:.1 for v in V}
        sets=[tuple(range(0,15)),tuple(range(5,20))]
        a,da=select_structural_supports(V,y,k_supports=sets,max_support_size=10,max_supports=3)
        b,db=select_structural_supports(V,y,k_supports=list(reversed(sets)),max_support_size=10,max_supports=3)
        self.assertEqual((a,da),(b,db))
        self.assertTrue(a)
        self.assertTrue(all(len(s)<=10 for s in a))
        self.assertIn('K_PAIR_PROJECTION', da['selected_kinds'])
        self.assertTrue(da['projection_requires_independent_oracle_certification'])
        self.assertEqual(da['k_eligible_count'],0)
        with self.assertRaises(ValueError):
            select_structural_supports(V,{**y,0:float('nan')},k_supports=sets)
        with self.assertRaises(ValueError):
            select_structural_supports(V,y,k_supports=[tuple(range(21))])


class IntegrationTests(unittest.TestCase):
    def test_comp_k_real_compiler_k4_gains_only_after_certificate(self):
        raw, W=k4(); S,T,V,adj,r=raw
        arcs=reach_arcs(V,adj,r); K=k_cuts(S,T,V,adj,r,arcs)
        loaded=SimpleNamespace(S=S,T=T,V=V,adj=adj,A_r=arcs,r=r,
                               instance_sha256='K4-AS21-SYNTHETIC')
        class Var:
            def __init__(self,v):self.v=v
            def __rmul__(self,n):return self.v,float(n)
        class Expr:
            def __init__(self,terms):self.terms=dict(terms)
            def __ge__(self,rhs):return self.terms,float(rhs)
        class GP:
            @staticmethod
            def quicksum(terms): return Expr(terms)
        class Model:
            def __init__(self): self.more=[];self.NumConstrs=30
            def addConstr(self,row,name):self.more.append(row);self.NumConstrs+=1
            def update(self):pass
        def builder(compiled,policy,deadline):return Model(),{v:Var(v) for v in V},GP
        def solve(model,gp,deadline,ycols):
            fun,y,_=solve_comp_lp(S,T,V,arcs,K,more=model.more)
            return dict(status='OPTIMAL',lp_objective=fun,y_star=y)
        cfg=dict(max_variables=1000000,max_support_size=4,max_supports=4,
                 max_pairs=32,max_k_seeds=48,max_oracle_calls=100,
                 max_patterns_per_support=100,max_rhs=3,total_budget_s=20,
                 per_support_budget_s=10,min_violation=1e-7,max_cuts=3)
        with (patch('run_hl_lp_as21.load_instance',return_value=loaded),
              patch('run_hl_lp_as21.prepare_K',return_value=K),
              patch('run_hl_lp_as21._solver',side_effect=builder),
              patch('run_hl_lp_as21._optimize',side_effect=solve)):
            base=_work_arm({'source_sha256':'K4-AS21-SYNTHETIC'},{},ROOT,
                           'U_K',{},cfg,time.monotonic()+30)
            new=_work_arm({'source_sha256':'K4-AS21-SYNTHETIC'},{},ROOT,
                          'U_K_HL',{},cfg,time.monotonic()+30)
        self.assertEqual(base['status'],new['status'])
        self.assertAlmostEqual(base['lp_objective'],2)
        self.assertAlmostEqual(new['lp_objective'],3)
        self.assertGreaterEqual(new['hl_accepted'],1)
        self.assertEqual(new['separation']['stage'],'AS21')
        self.assertEqual(new['separation']['records'][0]['patterns_examined'],11)


class PlanAndAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan,cls.sha,cls.source=load_plan()

    def test_plan_freeze_and_mutations(self):
        self.assertEqual(len(self.plan['cases']),6)
        self.assertEqual(len(set(c['raw_graph_id'] for c in self.plan['cases'])),6)
        self.assertEqual(self.plan['hl']['max_rhs'],3)
        with tempfile.TemporaryDirectory() as td:
            temp=Path(td)/'changed.json'; x=copy.deepcopy(self.plan)
            x['hl']['max_rhs']=7; temp.write_text(json.dumps(x))
            with self.assertRaises(ValueError):load_plan(temp)
            x=copy.deepcopy(self.plan);x['cases'].pop();temp.write_text(json.dumps(x))
            with self.assertRaises(ValueError):load_plan(temp)

    def test_dryrun_append_only_no_solver(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'as21'
            a=execute(self.plan,self.sha,self.source,ROOT,out,
                      {c['name'] for c in self.plan['cases']},dry_run=True)
            self.assertEqual(a['gate'],'NOT_EXECUTED')
            self.assertEqual(a['stage'],'AS21')
            self.assertEqual(a['arm_rows'],12)
            with self.assertRaises(FileExistsError):
                execute(self.plan,self.sha,self.source,ROOT,out,
                        {c['name'] for c in self.plan['cases']},dry_run=True)

    def test_cross_run_comparison_does_not_claim_gain(self):
        r={'name':'test','raw_graph_id':'same','cuts_certified':0,'oracle_calls':2,
           'marginal_gain':0,'k_hl_elapsed_wall_s':3.,'screen_incomplete':False}
        comp=compare_as20({'cases':[r]}, {'cases':[dict(r,oracle_calls=1)]})
        self.assertEqual(len(comp['cases']),1)
        self.assertIn('descriptive',comp['scope'])
        self.assertEqual(comp['cases'][0]['as21_oracle_calls'],1)


if __name__=='__main__':unittest.main()
