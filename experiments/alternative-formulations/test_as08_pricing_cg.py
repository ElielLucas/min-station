"""AS-08 T2b/T3/T4: validações e sensores de discriminação.

HiGHS/SciPy roda localmente; Gurobi é testável no ambiente do autor.
"""
from __future__ import annotations

import importlib.util
import json
import random
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from as02_model_a import Instance, compile_u, compile_a
from as02_solve import solve
from as08_b_exact import compile_b, enumerate_paths
from as08_pricing import price_all, price_source
from as08_column_generation import (CGConfig, certified_bound, compile_rmp,
                                    run_column_generation, _solve, verify_rational_certificate)
from run_as08_t2a import FIXTURES, build_fixture
from run_as08_b_pilot import make_plan, validate_plan, analyze, verify, digest, json_write, sha

BACKEND = 'gurobi' if importlib.util.find_spec('gurobipy') else 'scipy-highs'


class TestAS08Pricing(unittest.TestCase):
    def test_pricing_exact_against_every_enumerated_path(self):
        rng=random.Random(20261012)
        for fixture in FIXTURES:
            ins,_=build_fixture(fixture)
            paths=enumerate_paths(ins)
            for _ in range(12):
                pi={s:Fraction(rng.randrange(-6,7),3) for s in ins.S}
                tau={t:Fraction(rng.randrange(-6,7),3) for t in ins.T}
                gamma={(s,v):Fraction(rng.randrange(0,7),4) for s in ins.S
                       for v in ins.V if v!=s}
                mu={v:Fraction(rng.randrange(0,7),4) for v in ins.V}
                priced=price_all(ins,pi,tau,gamma,mu,exact=True)
                for s in ins.S:
                    for t in ins.T:
                        expected=[]
                        for p in paths.by_source[s]:
                            if p[-1]==t:
                                expected.append((sum((gamma.get((s,v),0)+mu.get(v,0)
                                                     for v in p[1:-1]),Fraction(0))
                                                 -pi[s]-tau[t],p))
                        got=[p for p in priced[s] if p.target==t]
                        if not expected:
                            self.assertEqual(got,[])
                        else:
                            self.assertEqual(len(got),1)
                            self.assertEqual(got[0].reduced_cost,min(k for k,_ in expected))
                            self.assertIn(got[0].path,paths.by_source[s])

    def test_overlap_zero_path_and_intermediate_destinations(self):
        ins,_=build_fixture(next(f for f in FIXTURES if f.name=='e5-origin-destination-swap'))
        pi={s:0 for s in ins.S}; tau={t:0 for t in ins.T}
        results=price_source(ins,'v',pi,tau,{}, {},exact=True)
        self.assertIn(('v',),[p.path for p in results])
        self.assertIn(('v','b'),[p.path for p in results])
        ins,_=build_fixture(next(f for f in FIXTURES if f.name=='e1-b4-star'))
        priced=price_source(ins,'a',{s:0 for s in ins.S},{t:0 for t in ins.T},{}, {'c':1},exact=True)
        self.assertEqual(next(p.path for p in priced if p.target=='d'),('a','c','d'))
        self.assertEqual(next(p.reduced_cost for p in priced if p.target=='d'),1)

    def test_negative_or_non_finite_costs_refused(self):
        ins,_=build_fixture(FIXTURES[0])
        pi={s:0 for s in ins.S};tau={t:0 for t in ins.T}
        for bad in (-.001,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                price_source(ins,'a',pi,tau,{('a','c'):bad},{})
        with self.assertRaises(ValueError):
            price_source(ins,'a',{},tau,{}, {})
        with self.assertRaises(ValueError):
            price_source(ins,'a',pi,tau,{('fake','c'):1},{})

    def test_reachable_and_unreachable(self):
        ins,_=build_fixture(next(f for f in FIXTURES if f.name=='infeasible-components'))
        priced=price_all(ins,{s:0 for s in ins.S},{t:0 for t in ins.T},{},{})
        self.assertEqual(priced['a'],())
        self.assertEqual(priced['b'],())


class TestAS08ColumnGeneration(unittest.TestCase):
    def conf(self, **updates):
        cfg={**CGConfig(backend=BACKEND,seconds=15,iterations=100).__dict__,**updates}
        return CGConfig(**cfg)

    def test_ten_fixtures_full_master_equality(self):
        for fixture in FIXTURES:
            ins,_=build_fixture(fixture)
            result=run_column_generation(ins,config=self.conf())
            enumerated,_=compile_b(ins)
            exact=solve(enumerated,backend=BACKEND)
            if exact.status=='OPTIMAL':
                self.assertEqual(result['status'],'CONVERGED',fixture.name)
                self.assertIsNotNone(result['global_lower_bound'])
                self.assertAlmostEqual(result['global_lower_bound'],exact.objective,places=5)
                self.assertAlmostEqual(result['feasible_lp_upper_bound'],exact.objective,places=5)
                self.assertEqual(result['global_lb_certificate']['status'],'CERTIFIED_RATIONAL_DUAL')
                self.assertGreaterEqual(len(result['iterations']),2)
            else:
                self.assertIsNone(result['global_lower_bound'])
                self.assertNotEqual(result['status'],'CONVERGED')

    def test_k_also_matches_exact(self):
        ins,_=build_fixture(FIXTURES[2])
        K=[{'x'},{'a','b'}]
        r=run_column_generation(ins,K,config=self.conf())
        b,_=compile_b(ins,K)
        o=solve(b,backend=BACKEND)
        self.assertEqual(r['status'],'CONVERGED')
        self.assertAlmostEqual(r['global_lower_bound'],o.objective,places=5)

    def test_mutant_no_negative_col_does_not_certify(self):
        ins,_=build_fixture(FIXTURES[0])
        r=run_column_generation(ins,config=self.conf(iterations=1))
        self.assertEqual(r['status'],'ITERATION_LIMIT')
        self.assertIsNone(r['global_lower_bound'])
        self.assertNotEqual(r['rmp_objective'],r['global_lower_bound'])
        r=run_column_generation(ins,config=self.conf(max_columns=1))
        self.assertEqual(r['status'],'CAP_EXCEEDED')
        self.assertIsNone(r['global_lower_bound'])
        r=run_column_generation(ins,config=self.conf(rational_certificate=False))
        self.assertEqual(r['status'],'NO_GLOBAL_LB_CERTIFICATE_DISABLED')
        self.assertIsNone(r['global_lower_bound'])

    def test_rmp_artificials_not_confused_with_master_feasibility(self):
        ins,_=build_fixture(FIXTURES[0])
        master,_=compile_rmp(ins,[],[])
        sol=_solve(master,ins,[],self.conf(),seconds=5)
        self.assertEqual(sol.status,'OPTIMAL')
        self.assertGreater(sol.artificial_sum,0)
        self.assertGreater(sol.objective,len(ins.V))
        # The dual can be repaired to bound full B even if initial RMP is infeasible.
        cert=certified_bound(ins,[],sol)
        self.assertEqual(cert['status'],'CERTIFIED_RATIONAL_DUAL')
        self.assertLessEqual(cert['lower_bound'],1)

    def test_mutant_missing_b4_fails_witness(self):
        ins,_=build_fixture(FIXTURES[0])
        b,_=compile_b(ins,global_links=False)
        self.assertLess(solve(b,backend=BACKEND).objective,1)
        cg=run_column_generation(ins,config=self.conf())
        self.assertAlmostEqual(cg['global_lower_bound'],1,places=5)

    def test_random_graphs_match_enumeration_and_u_dominance(self):
        rng=random.Random(1863)
        for case in range(18):
            V=tuple(str(v) for v in range(5))
            S=tuple(sorted(rng.sample(V,2)))
            T=tuple(sorted(rng.sample(V,2)))
            E=tuple((u,v) for i,u in enumerate(V) for v in V[i+1:] if rng.random()<.42)
            Ar=tuple(sorted([(u,v) for u,v in E]+[(v,u) for u,v in E]))
            ins=Instance(V,S,T,Ar,1)
            enumerated,_=compile_b(ins)
            b=solve(enumerated,backend=BACKEND)
            r=run_column_generation(ins,config=self.conf())
            if b.status=='OPTIMAL':
                self.assertEqual(r['status'],'CONVERGED',case)
                self.assertAlmostEqual(r['global_lower_bound'],b.objective,places=5)
                u=solve(compile_u(ins,relax=True),backend=BACKEND)
                self.assertGreaterEqual(r['global_lower_bound']+1e-6,u.objective)
            else:
                self.assertNotEqual(r['status'],'CONVERGED')

    def test_invalid_column_and_config(self):
        ins,_=build_fixture(FIXTURES[0])
        with self.assertRaises(ValueError):
            compile_rmp(ins,[],[('a','d')])
        with self.assertRaises(ValueError):
            compile_rmp(ins,[],[('a','c','a')])
        with self.assertRaises(ValueError):
            self.conf(tolerance=2).validate()
        with self.assertRaises(ValueError):
            self.conf(seconds=-1).validate()


    def test_rational_certificate_independent_recheck_and_mutation(self):
        ins,_=build_fixture(FIXTURES[0])
        r=run_column_generation(ins,config=self.conf())
        import copy
        certificate=r['global_lb_certificate']
        self.assertTrue(verify_rational_certificate(ins,[],certificate))
        corrupted=copy.deepcopy(certificate)
        corrupted['rational']='0/1'
        with self.assertRaises(ValueError):
            verify_rational_certificate(ins,[],corrupted)
        corrupted=copy.deepcopy(certificate)
        corrupted['duals']['pi'][ins.S[0]]='-999'
        with self.assertRaises(ValueError):
            verify_rational_certificate(ins,[],corrupted)

    def test_artifact_manifest_catches_tampering(self):
        root=Path(__file__).resolve().parents[2]
        plan=make_plan(root)
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            json_write(out/'plan.json',plan)
            filenames={}
            for case in plan['cases']:
                for arm in plan['arms']:
                    name=f"{case['name']}--{arm}.json"
                    payload={'schema':'AS08-B-PILOT-RESULT-v1','plan_sha256':digest(plan),
                             'case':case,'arm':arm,'status':'TIME_LIMIT',
                             'lp_numeric_value':None,'global_lower_bound':None,
                             'wall_total_s':1.0}
                    json_write(out/name,payload)
                    filenames[name]=sha(out/name)
            json_write(out/'manifest.json',{'schema':'AS08-B-PILOT-MANIFEST-v1',
                                           'plan_sha256':digest(plan),'files':filenames})
            self.assertEqual(len(verify(out,root)),12)
            path=out/next(iter(filenames))
            path.write_text(path.read_text().replace('TIME_LIMIT','OPTIMAL_NUMERIC'))
            with self.assertRaises(ValueError):
                verify(out,root)

    def test_plan_freeze_and_analysis_censor(self):
        root=Path(__file__).resolve().parents[2]
        plan=make_plan(root,budget=240,backend='scipy-highs')
        self.assertEqual(len(plan['cases']),6)
        validate_plan(plan,root)
        plan['classification']='FALSIFIED'
        with self.assertRaises(ValueError):
            validate_plan(plan,root)
        pairs=[]
        plan=make_plan(root)
        for case in plan['cases']:
            for arm in ('U_K','B_K'):
                pairs.append({'case':case,'arm':arm,'status':'TIME_LIMIT',
                              'lp_numeric_value':None,'global_lower_bound':None,'wall_total_s':300.0})
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            report=analyze(pairs,out)
            self.assertEqual(report['decision'],'INVESTIGATE_CENSORED')
            self.assertTrue(all(x['decision']=='CENSORED' for x in report['pairs']))


if __name__=='__main__':
    unittest.main()
