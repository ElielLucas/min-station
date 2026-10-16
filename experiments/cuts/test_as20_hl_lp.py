"""AS20 — independent HL real-development screen contracts and guards."""
import copy
import json
import tempfile
import time
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch

from analyze_hl_lp import analyze
from hl_local import HLOptions, separate_hl
from hl_supports import select_hl_supports
from run_hl_lp import (load_plan, execute, _add_hl_cut, _work_arm, PLAN_FILE,
                       SCHEMA, ARMS, ROOT)
from h2_oracle import PhysicalInstance
from verify_as13_foundations import k4, k_cuts, reach_arcs, solve_comp_lp


class SelectionTests(unittest.TestCase):
    def test_k4_union_first_certifies_stronger_than_K(self):
        raw, W = k4()
        S, T, V, adj, r = raw
        A = reach_arcs(V, adj, r)
        K = k_cuts(S, T, V, adj, r, A)
        base, y, _ = solve_comp_lp(S, T, V, A, K)
        self.assertAlmostEqual(base, 2)
        supports, meta = select_hl_supports(V, y, k_supports=K,
                                            max_support_size=4, max_supports=3)
        self.assertEqual(supports[0], tuple(W))
        self.assertEqual(meta['selected_support_sizes'][0], 4)
        report = separate_hl(PhysicalInstance.from_tuple(raw), y,
                             supports=supports[:1], options=HLOptions(max_support_size=4))
        self.assertEqual(len(report.cuts), 1)
        self.assertEqual(str(report.cuts[0].rhs), '3')
        strengthened, _, _ = solve_comp_lp(S, T, V, A, K,
              more=[(dict(report.cuts[0].coefficients), report.cuts[0].rhs)])
        self.assertAlmostEqual(strengthened, 3)

    def test_no_truncation_of_large_k(self):
        result, meta = select_hl_supports(('a','b','c','d'),
            {'a':.5,'b':.5,'c':.5,'d':.5}, k_supports=[('a','b','c','d')],
            max_support_size=3)
        self.assertEqual(result, ())
        self.assertTrue(meta['no_eligible_support'])
        self.assertEqual(meta['k_excluded_by_size'], 1)

    def test_deterministic_and_no_dedup_errors(self):
        args = dict(vertices=('a','b','c','d'),
                    y_star=dict(zip('abcd',(.5,.5,.5,.5))),
                    max_support_size=4, max_supports=4)
        k1=[('a','b'), ('b','c'), ('c','d'), ('a','d')]
        s1, m1 = select_hl_supports(k_supports=k1, **args)
        s2, m2 = select_hl_supports(k_supports=list(reversed(k1)), **args)
        self.assertEqual((s1,m1),(s2,m2))
        self.assertTrue(all(len(s) == len(set(s)) for s in s1))

    def test_rejects_invalid_support_and_y(self):
        with self.assertRaises(ValueError):
            select_hl_supports(('a','b'), {'a':.5,'b':.5}, k_supports=[('a','c')])
        with self.assertRaises(ValueError):
            select_hl_supports(('a','b'), {'a':.5,'b':float('nan')}, k_supports=[])
        with self.assertRaises(ValueError):
            select_hl_supports(('a','b'), {'a':.5,'b':.5}, k_supports=[], max_pairs=-1)


class IntegrationTests(unittest.TestCase):
    def test_real_compiler_and_lp_reoptimization_without_gurobi_k4(self):
        # Integration of AS20 arm control flow, actual COMP+K compiler, physical
        # oracle and real LP (SciPy/HiGHS). Stub only Gurobi adapter.
        raw, W = k4()
        S, T, V, adj, r = raw
        arcs = reach_arcs(V, adj, r)
        loaded = SimpleNamespace(S=S,T=T,V=V,adj=adj,A_r=arcs,r=r,
                                 instance_sha256='K4-SYNTHETIC-ONLY')
        K = k_cuts(S,T,V,adj,r,arcs)

        class Var:
            def __init__(self, vertex): self.vertex = vertex
            def __rmul__(self, value): return self.vertex, float(value)
        class Expr:
            def __init__(self, terms): self.terms = dict(terms)
            def __ge__(self, rhs): return self.terms, float(rhs)
        class GP:
            @staticmethod
            def quicksum(terms): return Expr(terms)
        class Model:
            def __init__(self): self.more=[];self.NumConstrs=42
            def addConstr(self, row, name):
                self.more.append(row)
                self.NumConstrs += 1
            def update(self): pass
        def build(compiled,policy,deadline):
            return Model(), {v:Var(v) for v in V}, GP
        def optimize(model,gp,deadline,ycols):
            fun, y, _ = solve_comp_lp(S,T,V,arcs,K,more=model.more)
            return dict(status='OPTIMAL',lp_objective=fun,y_star=y,
                        solver_wall_s=0.,solver_runtime_s=0.,solver_work=0.)

        cfg=dict(max_variables=1000000,max_support_size=4,max_supports=3,
                 max_pairs=24,max_oracle_calls=300,total_budget_s=15,
                 per_support_budget_s=10,min_violation=1e-7,max_cuts=3)
        case={'source_sha256':'K4-SYNTHETIC-ONLY'}
        with (patch('run_hl_lp.load_instance',return_value=loaded),
              patch('run_hl_lp.prepare_K',return_value=K),
              patch('run_hl_lp._solver',side_effect=build),
              patch('run_hl_lp._optimize',side_effect=optimize)):
            base = _work_arm(case, {}, ROOT,'U_K',{},cfg,time.monotonic()+30)
            improved = _work_arm(case,{},ROOT,'U_K_HL',{},cfg,time.monotonic()+30)
        self.assertEqual(base['status'],'OPTIMAL')
        self.assertEqual(improved['status'],'OPTIMAL')
        self.assertAlmostEqual(base['lp_objective'],2)
        self.assertAlmostEqual(improved['lp_objective'],3)
        self.assertGreaterEqual(improved['hl_accepted'],1)
        self.assertTrue(improved['cuts'][0]['certificate_sha256'])
        self.assertEqual(improved['selection']['policy'],
                         'AS20_K_SMALL_AND_UNIONS_V1')


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.sha, cls.source = load_plan()

    def test_plan_frozen_and_six_independent_graphs(self):
        self.assertEqual(len(self.plan['cases']),6)
        self.assertEqual(len(set(c['raw_graph_id'] for c in self.plan['cases'])),6)
        self.assertEqual(tuple(self.plan['arms']), ARMS)
        self.assertEqual(self.plan['budget']['wall_seconds_per_arm'],90)

    def test_plan_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            plan = copy.deepcopy(self.plan)
            plan['hl']['max_support_size'] = 20
            name = Path(td)/'mutant.json';name.write_text(json.dumps(plan))
            with self.assertRaises(ValueError): load_plan(name)
            plan['hl']['max_support_size'] = 10
            plan['cases'].append(plan['cases'][0]);name.write_text(json.dumps(plan))
            with self.assertRaises(ValueError): load_plan(name)
            plan = copy.deepcopy(self.plan)
            plan['as16_plan_sha256'] = 'x'*64
            name.write_text(json.dumps(plan))
            with self.assertRaises(ValueError): load_plan(name)

    def test_dry_run_real_provenance_and_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'dry'
            report = execute(self.plan, self.sha, self.source, ROOT, out,
                    {self.plan['cases'][0]['name']}, dry_run=True)
            self.assertEqual(report['gate'], 'NOT_EXECUTED')
            self.assertEqual(report['arm_rows'], 2)
            self.assertEqual(len(json.loads((out/'rows.json').read_text())),2)
            with self.assertRaises(FileExistsError):
                execute(self.plan, self.sha, self.source, ROOT, out,
                        {self.plan['cases'][0]['name']}, dry_run=True)
            with self.assertRaises(ValueError):
                execute(self.plan, self.sha, self.source, ROOT, Path(td)/'bad',
                        {'evaluation-forbidden'}, dry_run=True)


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.sha, _ = load_plan()

    def _rows(self, names=None):
        names = names or [c['name'] for c in self.plan['cases']]
        cases = {c['name']: c for c in self.plan['cases']}
        out=[]
        for n in names:
            for arm in ARMS:
                out.append(dict(name=n, arm_id=arm, instance_sha256=cases[n]['source_sha256'],
                                raw_graph_id=cases[n]['raw_graph_id'], status='OPTIMAL',
                                lp_objective=10., elapsed_wall_s=10.,
                                hl_accepted=0, selection={'selected_count':1,'no_eligible_support':False},
                                separation={'status':'NO_CUTS','records':[{'status':'NOT_VIOLATED'}]}))
        return out

    def test_no_gain_requires_complete_conclusive_campaign(self):
        rows=self._rows()
        ans=analyze(self.plan,dict(mode='LP',cases=[c['name'] for c in self.plan['cases']]),rows)
        self.assertEqual(ans['gate'],'NO_GAIN_IN_BOUNDED_SCREEN')
        rows[1]['selection']={'selected_count':0,'no_eligible_support':True}
        self.assertEqual(analyze(self.plan,dict(mode='LP',cases=[c['name'] for c in self.plan['cases']]),rows)['gate'],'INVESTIGATE')

    def test_gains_require_two_independent_graphs_with_acceptable_cost(self):
        rows=self._rows()
        names=[c['name'] for c in self.plan['cases']]
        for n in names[:2]:
            next(r for r in rows if r['name']==n and r['arm_id']=='U_K_HL')['lp_objective']=10.5
        ans=analyze(self.plan,dict(mode='LP',cases=names),rows)
        self.assertEqual(ans['gate'],'GO_CANDIDATE_REVIEW')
        row=next(r for r in rows if r['name']==names[0] and r['arm_id']=='U_K_HL')
        row['elapsed_wall_s']=25.
        self.assertEqual(analyze(self.plan,dict(mode='LP',cases=names),rows)['gate'],'NO_GAIN_IN_BOUNDED_SCREEN')

    def test_censored_subset_unknown_and_duplicate_are_not_scientific_failure(self):
        names=[c['name'] for c in self.plan['cases']][:2]
        rows=self._rows(names)
        manifest=dict(mode='LP',cases=names)
        self.assertEqual(analyze(self.plan,manifest,rows)['gate'],'INVESTIGATE')
        rows[1]['status']='TIME_LIMIT'
        self.assertFalse(analyze(self.plan,manifest,rows)['cases'][0]['paired_optimal'])
        with self.assertRaises(ValueError):analyze(self.plan,manifest,rows+[rows[0]])
        rows=self._rows(names)
        rows[0]['instance_sha256']='wrong'
        with self.assertRaises(ValueError):analyze(self.plan,manifest,rows)

    def test_dry_run_never_produces_gain(self):
        names=[c['name'] for c in self.plan['cases']]
        self.assertEqual(analyze(self.plan,dict(mode='DRY_RUN',cases=names),
                                 self._rows())['gate'], 'NOT_EXECUTED')


if __name__=='__main__':
    unittest.main()
