"""AS25 spec-backed tests: coverage, immutable four-arm protocol and conservative gate."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.cuts.fcr_lp_policy import IndexedFCR
from experiments.cuts.fcr_separator import scan
from experiments.cuts.verify_fcr_witness import build_system
from experiments.cuts import run_fcr_lp_as25 as runner
from experiments.cuts.analyze_fcr_lp_as25 import analyze


class AS25FCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system=build_system()
        cls.ins=cls.system['instance']
        cls.evidence=json.loads((runner.ROOT/'results/benchmark/as23-fcr-witness-001.json').read_text())
        cls.plan,cls.sha,cls.base=runner.load_plan()

    def test_fixed_region_Q_and_full_singletons_equivalent_to_AS24(self):
        model=self.system['compiled']
        for name in ('COMP_K','COMP_K_FCR','COMP_K_C8','COMP_K_C8_FCR',
                     'COMP_K_C6_C8','COMP_K_C6_C8_FCR'):
            vector=[Fraction(v) for v in self.evidence['cases'][name]['primal']]
            y={v:vector[model.columns['y',v]] for v in self.ins.V}
            f={(u,v):vector[model.columns['F',u,v]] for u,v in self.ins.A_r}
            for larger in (False,True):
                slow=scan(self.ins,y,f,include_larger=larger,max_larger=12,max_cuts=64,tolerance=1e-8)
                fast=IndexedFCR(self.ins,max_larger=12,include_larger=larger).separate(
                    y,f,max_cuts=64,tolerance=1e-8)
                self.assertEqual([r.signature for r in slow.cuts],[r.signature for r in fast['cuts']])
                self.assertEqual(slow.stats['singletons_checked'],fast['stats']['singletons_checked'])
                self.assertEqual(slow.stats['larger_checked'],fast['stats']['larger_checked'])
                self.assertEqual(slow.stats['violated'],fast['stats']['violated'])
                self.assertTrue(fast['stats']['singleton_complete'])
                self.assertEqual([r.terms for r in slow.cuts],[r.terms for r in fast['cuts']])

    def test_mutant_terminal_exclusion_independently_rejected_by_canonical_rows(self):
        from experiments.cuts.fcr_rows import construct_row
        with self.assertRaises(ValueError):
            construct_row(self.ins,('d1',),('e1',),'destination')
        with self.assertRaises(ValueError):
            construct_row(self.ins,('a1',),('c1',),'origin')

    def test_cap_does_not_silently_claim_global_completeness(self):
        evaluator=IndexedFCR(self.ins,max_larger=12)
        limited=evaluator.separate({}, {},max_cuts=0)
        self.assertTrue(limited['stats']['singleton_complete'])
        self.assertGreater(limited['stats']['capped'],0)
        self.assertNotEqual(limited['status'],'COMPLETE_DECLARED_FAMILY')
        timed=evaluator.separate({}, {},time_limit_s=0)
        self.assertEqual(timed['status'],'PARTIAL_SINGLETONS')
        self.assertFalse(timed['stats']['singleton_complete'])
        self.assertFalse(limited['stats']['global_region_separation'])

    def test_q_ties_and_approximate_fractions(self):
        index=IndexedFCR(self.ins,include_larger=False)
        point=index.separate({'x11':1/3},{('a1','x11'):1/3},max_cuts=99)
        events=[v for v in point['events'] if v['region']==['a1']]
        self.assertEqual(len(events),1)
        self.assertNotIn('x11',events[0].get('certificate',{}).get('q',[]))

    def test_load_plan_rejects_policy_and_case_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'modified.json'
            for change in ('budget','cases','fcr','gate','primary_arms'):
                value=copy.deepcopy(self.plan)
                if change=='budget':value['budget']['wall_seconds_per_arm']=900
                if change=='cases':value['cases'][0]['raw_graph_id']='fabricated'
                if change=='fcr':value['fcr']['max_larger']=900
                if change=='gate':value['gate']['minimum_relative_gain']=0
                if change=='primary_arms':value['primary_arms'].append('U_MIP')
                path.write_text(json.dumps(value))
                with self.subTest(change=change),self.assertRaises(ValueError):
                    runner.load_plan(path)

    def test_dry_run_all_24_rows_and_append_only(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'pilot'
            result=runner.execute(self.plan,self.sha,self.base,runner.ROOT,out,
                {c['name'] for c in self.plan['cases']},dry_run=True)
            self.assertEqual(result['arm_rows'],24)
            self.assertEqual(result['gate'],'INVESTIGATE')
            rows=json.loads((out/'rows.json').read_text())
            self.assertEqual(len(rows),24)
            self.assertEqual({r['status'] for r in rows},{'NOT_RUN'})
            self.assertEqual(len({(r['name'],r['arm_id']) for r in rows}),24)
            self.assertTrue((out/'manifest.json').is_file())
            self.assertTrue((out/'analysis.json').is_file())
            with self.assertRaises(FileExistsError):
                runner.execute(self.plan,self.sha,self.base,runner.ROOT,out,
                    {c['name'] for c in self.plan['cases']},dry_run=True)

    def test_dry_run_ablation_kept_outside_primary_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'ablation'
            result=runner.execute(self.plan,self.sha,self.base,runner.ROOT,out,
                 {c['name'] for c in self.plan['cases']},dry_run=True,ablation=True)
            self.assertEqual(result['gate'],'ABLATION_DESCRIPTIVE_ONLY')
            self.assertEqual(result['arm_rows'],12)
            self.assertEqual(json.loads((out/'manifest.json').read_text())['campaign'],'ABLATION')

    def make_rows(self,*,bounds=(10,12),costs=(8,12),status='OPTIMAL',complete=True):
        rows=[]
        for c in self.plan['cases']:
            for arm in runner.PRIMARY_ARMS:
                obj=(bounds[1] if arm=='U_K_FCR' else bounds[0])
                wall=(costs[1] if arm=='U_K_FCR' else costs[0])
                rows.append({'name':c['name'],'arm_id':arm,
                             'raw_graph_id':c['raw_graph_id'],
                             'instance_sha256':c['source_sha256'],
                             'status':status,'lp_objective':obj if status=='OPTIMAL' else None,
                             'elapsed_wall_s':wall,'fcr_added':4,
                             'singleton_complete_all_scans':complete,
                             'selected_heuristic_complete_all_scans':complete})
        manifest={'campaign':'PRIMARY','arms':list(runner.PRIMARY_ARMS),'mode':'LP',
                  'cases':[c['name'] for c in self.plan['cases']], 'plan_sha256':self.sha}
        return rows,manifest

    def test_conservative_positive_gate_is_review_only(self):
        rows,manifest=self.make_rows()
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'GO_CANDIDATE_REVIEW')
        self.assertEqual(result['qualified_raw_graph_count'],6)
        self.assertFalse(result['mip_automatically_authorized'])

    def test_nonoptimal_arm_is_censored_not_paired(self):
        rows,manifest=self.make_rows()
        rows[3]['status']='TIME_LIMIT';rows[3]['lp_objective']=None
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'INVESTIGATE')
        self.assertEqual(result['censored_arm_count'],1)
        self.assertFalse(result['cases'][0]['comparisons']['FC_R_marginal_over_K']['paired_optimal'])

    def test_flow_only_cut_does_not_count_as_improvement(self):
        rows,manifest=self.make_rows(bounds=(10,10))
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'STOP')
        self.assertTrue(result['cases'][0]['comparisons']['FC_R_marginal_over_K']['flow_only_zero_bound_gain'])

    def test_positive_gain_with_partial_region_coverage_cannot_go(self):
        rows,manifest=self.make_rows(complete=False)
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'INVESTIGATE')
        self.assertEqual(result['qualified_raw_graph_count'],0)

    def test_cut_cap_is_inconclusive_even_with_complete_region_scan(self):
        rows,manifest=self.make_rows()
        rows[3]['fcr_cut_cap_encountered']=True
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'INVESTIGATE')
        self.assertFalse(result['cases'][0]['counts_for_gate'])

    def test_cost_cap_blocks_GO_even_if_objective_gains(self):
        rows,manifest=self.make_rows(costs=(1,10))
        self.assertEqual(analyze(self.plan,manifest,rows)['gate'],'STOP')

    def test_zero_baseline_objective_has_undefined_relative_gain(self):
        rows,manifest=self.make_rows(bounds=(0,0))
        result=analyze(self.plan,manifest,rows)
        self.assertEqual(result['gate'],'STOP')
        self.assertIsNone(result['cases'][0]['comparisons']['FC_R_marginal_over_K']['relative_gain'])

    def test_identity_mismatch_duplicate_or_missing_rows_rejected(self):
        rows,manifest=self.make_rows()
        for corrupted in (rows[:-1],rows+[rows[0]],
                          [{**rows[0],'instance_sha256':'fake'}]+rows[1:]):
            with self.assertRaises(ValueError):analyze(self.plan,manifest,corrupted)

    def test_censored_or_partial_sample_cannot_go(self):
        rows,manifest=self.make_rows()
        manifest['cases']=[self.plan['cases'][0]['name']]
        rows=[r for r in rows if r['name']==manifest['cases'][0]]
        self.assertEqual(analyze(self.plan,manifest,rows)['gate'],'INVESTIGATE')
        manifest['mode']='DRY_RUN'
        self.assertEqual(analyze(self.plan,manifest,rows)['gate'],'INVESTIGATE')

    def test_minute_wall_budget_is_absolute_per_arm(self):
        self.assertEqual(self.plan['budget']['wall_seconds_per_arm'],90)
        self.assertEqual(self.plan['fcr']['max_rounds'],6)
        with patch.object(runner,'_work_arm', side_effect=TimeoutError('deadline')):
            class Pipe:
                def __init__(self):self.sent=[]
                def send(self,x):self.sent.append(x)
                def close(self):pass
            conn=Pipe()
            c=self.plan['cases'][0]
            runner._worker(conn,c,{},runner.ROOT,'U',{},self.plan['fcr'],0)
            self.assertEqual(conn.sent[0]['status'],'TIME_LIMIT')


if __name__=='__main__':unittest.main()

class AS25SolverBridgeTests(unittest.TestCase):
    """Integration through a different LP engine, no Gurobi license needed."""
    def test_synthetic_compiled_lp_reoptimizes_with_generated_rows(self):
        import time
        import numpy as np
        from scipy.optimize import linprog
        from scipy.sparse import lil_matrix
        from experiments.cuts.verify_fcr_witness import witness_instance
        from types import SimpleNamespace
        from experiments.cuts import run_fcr_lp_as25 as runner

        ins,adj,_,_=witness_instance()
        loaded=SimpleNamespace(V=ins.V,S=ins.S,T=ins.T,A_r=ins.A_r,r=ins.r,
                               adj=adj,instance_sha256='synthetic-as23')

        class Expr:
            def __init__(self, terms=None):self.terms=dict(terms or {})
            def __add__(self,other):
                d=dict(self.terms)
                if isinstance(other,Expr):
                    for k,v in other.terms.items():d[k]=d.get(k,0.)+v
                elif other!=0:raise TypeError(other)
                return Expr(d)
            __radd__=__add__
            def __ge__(self,rhs):return self.terms,float(rhs)
        class Var:
            def __init__(self,j):self.j=j;self.X=0.
            def __rmul__(self,c):return Expr({self.j:float(c)})
        class GP:
            @staticmethod
            def quicksum(items):return sum(items,Expr())
        class Model:
            def __init__(self,compiled):
                self.compiled=compiled;self.columns=[Var(j) for j in range(len(compiled.variables))]
                self.extra=[];self.NumConstrs=len(compiled.equations)
                self.NumNZs=sum(len(eq.terms) for eq in compiled.equations)
            def getVars(self):return self.columns
            def addConstr(self,row,name):
                terms,rhs=row;self.extra.append((terms,rhs));return row
            def update(self):
                self.NumConstrs=len(self.compiled.equations)+len(self.extra)
                self.NumNZs=sum(len(eq.terms) for eq in self.compiled.equations)+sum(len(x[0]) for x in self.extra)
        def fake_solver(compiled,policy,deadline):
            model=Model(compiled)
            return model,{key[1]:model.columns[j] for key,j in compiled.columns.items() if key[0]=='y'},GP
        def fake_optimize(model,gp,deadline,ycols):
            compiled=model.compiled
            # A certified optimum on a degenerate face that is known to
            # violate FC-R.  A generic LP solver may return a different
            # optimum with no violation, which would not test row insertion.
            if not model.extra:
                evidence=json.loads((runner.ROOT/'results/benchmark/as23-fcr-witness-001.json').read_text())
                primal=[float(Fraction(x)) for x in evidence['cases']['COMP_K']['primal']]
                for variable,value in zip(model.columns,primal):variable.X=value
                return {'status':'OPTIMAL','lp_objective':1.,
                        'y_star':{key:float(col.X) for key,col in ycols.items()},
                        'solver_wall_s':0.,'solver_runtime_s':0.,'solver_work':0.}

            n=len(compiled.variables)
            c=np.zeros(n)
            for j,value in compiled.objective.items():c[j]=float(value)
            inequalities=[];bounds=[];equalities=[];eq_bounds=[]
            for row in compiled.equations:
                coef=dict(row.terms);rhs=float(row.rhs)
                if row.sense=='==':equalities.append(coef);eq_bounds.append(rhs)
                elif row.sense=='>=':inequalities.append({j:-x for j,x in coef.items()});bounds.append(-rhs)
                else:inequalities.append(coef);bounds.append(rhs)
            for coef,rhs in model.extra:
                inequalities.append({j:-x for j,x in coef.items()});bounds.append(-rhs)
            def matrix(rows):
                mat=lil_matrix((len(rows),n))
                for i,row in enumerate(rows):
                    for j,v in row.items():mat[i,j]=v
                return mat.tocsr() if rows else None
            result=linprog(c,A_ub=matrix(inequalities),b_ub=bounds or None,
                 A_eq=matrix(equalities),b_eq=eq_bounds or None,
                 bounds=[(v.lb,None if not np.isfinite(v.ub) else v.ub) for v in compiled.variables],method='highs')
            if not result.success:return {'status':'UNKNOWN','lp_objective':None,'y_star':None}
            for v,x in zip(model.columns,result.x):v.X=float(x)
            return {'status':'OPTIMAL','lp_objective':float(result.fun),
                    'y_star':{key:float(col.X) for key,col in ycols.items()},
                    'solver_wall_s':0.,'solver_runtime_s':0.,'solver_work':0.}
        config={'max_variables':1000000,'max_larger':12,'max_rounds':6,
                'max_cuts_per_round':32,'max_cuts_total':128,'min_violation':1e-6,
                'max_separation_wall_s':12,'min_reopt_remaining_s':2}
        def run(arm):
            with patch.object(runner,'load_instance',return_value=loaded),\
                 patch.object(runner,'_solver',side_effect=fake_solver),\
                 patch.object(runner,'_optimize',side_effect=fake_optimize):
                return runner._work_arm({'source_sha256':'synthetic-as23'}, {},runner.ROOT,
                                        arm,{},config,time.monotonic()+90)
        base=run('U_K')
        strengthened=run('U_K_FCR')
        self.assertEqual(base['status'],'OPTIMAL')
        self.assertEqual(strengthened['status'],'OPTIMAL')
        self.assertAlmostEqual(base['lp_objective'],1.,places=6)
        # The separation policy need not find the four prechosen AS23 cuts.
        # It must, however, reoptimize valid added rows without weakening LP.
        self.assertGreater(strengthened['lp_objective'],1.+1e-5)
        self.assertGreater(strengthened['fcr_added'],0)
        self.assertTrue(strengthened['singleton_complete_all_scans'])
        self.assertGreater(strengthened['n_constraints_final'],base['n_constraints_initial'])
