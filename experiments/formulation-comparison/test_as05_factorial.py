"""AS05-FAC: experimentos fatorial exploratórios, falha segura e auditabilidade."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT, HERE.parent/'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from as02_model_a import Instance  # noqa: E402
from as05_factorial import (  # noqa: E402
    ARMS, WITH_K, _factorial_worker, analyze_experiment,
    compile_factorial, make_plan, partitions, run_experiment,
    validate_plan, verify_case, verify_experiment,
)
from experiments.cuts.synthetic import make_F1  # noqa: E402


def toy(m=4):
    S,T,V,adj,arcs,r,_ = make_F1(m=m,k=1)
    return Instance(tuple(V),tuple(S),tuple(T),tuple(arcs),r), SimpleNamespace(
        adj=adj, V=V,S=S,T=T,A_r=arcs,r=r,instance_sha256='toy-sha')


class Context:
    def __init__(self):
        self.phases=[]
    def phase(self,x):
        self.phases.append(x)
    def remaining(self):
        return 200
    def require_remaining(self):
        return 200


class TestFactorialMathematics(unittest.TestCase):
    def test_six_compilers_exactly_use_k_where_expected(self):
        instance,_ = toy()
        a2,a4 = partitions(instance,policy='reachability_degree',seed=42)
        cuts = (('h',),)
        for arm in ARMS:
            model = compile_factorial(instance,arm,
                cuts=cuts if arm in WITH_K else (),groups2=a2,groups4=a4)
            self.assertEqual(model.families.get('A6',0),int(arm in WITH_K),arm)
            self.assertEqual(all(not x.binary for x in model.variables),True)
            self.assertEqual(len(model.variables),len(set(model.columns.values())))
        self.assertEqual(a4.parent_hash,a2.partition_hash)

    def test_same_partition_without_and_with_k(self):
        instance,_=toy()
        a2,a4=partitions(instance,policy='reachability_degree',seed=42)
        self.assertEqual(a2.partition_hash,partitions(instance,policy='reachability_degree',seed=42)[0].partition_hash)
        self.assertEqual(a4.partition_hash,partitions(instance,policy='reachability_degree',seed=42)[1].partition_hash)
        # +K adiciona apenas A6, sem alteração no número de variáveis.
        for left,right,g in [('A2','A2_K',a2),('A4','A4_K',a4)]:
            x=compile_factorial(instance,left,groups2=a2,groups4=a4)
            y=compile_factorial(instance,right,cuts=(('h',),),groups2=a2,groups4=a4)
            self.assertEqual(len(x.variables),len(y.variables))
            self.assertEqual(len(y.equations),len(x.equations)+1)

    def test_cannot_inject_k_into_without_k(self):
        instance,_=toy()
        a2,a4=partitions(instance,policy='balanced',seed=42)
        for arm in ('U','A2','A4'):
            with self.assertRaises(ValueError):
                compile_factorial(instance,arm,cuts=(('h',),),groups2=a2,groups4=a4)

    def test_nonnested_a4_rejected(self):
        instance,_=toy()
        a2,a4=partitions(instance,policy='balanced',seed=42)
        broken=SimpleNamespace(parent_hash='wrong',blocks=a4.blocks)
        with self.assertRaises(ValueError):
            compile_factorial(instance,'A4',groups2=a2,groups4=broken)

    def test_A2_applicable_with_three_origins_but_A4_not(self):
        _,loaded=toy(m=3)
        plan=make_plan(ROOT)
        row={'nome':'toy.txt'}
        def loader(_row,_root):return loaded,0.0,0.0
        with patch('as05_factorial._load_timed',side_effect=loader), \
             patch('as05_factorial._optimize',return_value={'status':'OPTIMAL_NUMERIC','lp_opt_value':1.0,
                 'solver_runtime_s':0.1,'n_variables':42,'n_constraints':66,'n_nonzeros':99}), \
             patch('as05_factorial.resource.setrlimit'):
            a2=_factorial_worker(Context(),row,str(ROOT),'A2',plan)
            a4=_factorial_worker(Context(),row,str(ROOT),'A4',plan)
        self.assertEqual(a2['status'],'OPTIMAL_NUMERIC')
        self.assertEqual(a4['status'],'NOT_APPLICABLE')
        self.assertIsNone(a4['lp_opt_value'] if 'lp_opt_value' in a4 else None)

    def test_u_does_not_compute_k_nor_assign_it(self):
        _,loaded=toy()
        plan=make_plan(ROOT)
        with patch('as05_factorial._load_timed',return_value=(loaded,.1,.1)), \
             patch('as05_factorial._timed_k',side_effect=AssertionError('K proibido')), \
             patch('as05_factorial.resource.setrlimit'), \
             patch('as05_factorial._optimize',return_value={'status':'OPTIMAL_NUMERIC',
                 'lp_opt_value':1.,'solver_runtime_s':.1,'n_variables':10,'n_constraints':10,'n_nonzeros':10}):
            for arm in ('U','A2','A4'):
                rec=_factorial_worker(Context(),{'nome':'toy.txt'},str(ROOT),arm,plan)
                self.assertEqual(rec['status'],'OPTIMAL_NUMERIC',arm)
                self.assertFalse(rec['k_prepared_for_this_arm'],arm)
                self.assertIsNone(rec['applied_k_sha256'],arm)

    def test_six_workers_reuse_k_and_nesting_without_gurobi(self):
        _,loaded=toy()
        plan=make_plan(ROOT)
        call_count=[]
        def fake_solve(compiled,_mode,_policy,_ctx):
            call_count.append(len(compiled.variables))
            return {'status':'OPTIMAL_NUMERIC','lp_opt_value':1.,
                    'solver_runtime_s':.01,'n_variables':len(compiled.variables),
                    'n_constraints':len(compiled.equations),'n_nonzeros':compiled.n_nonzeros}
        rows={}
        with patch('as05_factorial._load_timed',return_value=(loaded,.01,.01)), \
             patch('as05_factorial.resource.setrlimit'), \
             patch('as05_factorial._optimize',side_effect=fake_solve):
            for arm in ARMS:
                rows[arm]=_factorial_worker(Context(),{'nome':'toy.txt'},str(ROOT),arm,plan)
        self.assertEqual(len(call_count),6)
        for arm in ARMS:
            self.assertEqual(rows[arm]['status'],'OPTIMAL_NUMERIC')
            self.assertEqual(rows[arm]['k_prepared_for_this_arm'],arm in WITH_K)
            self.assertEqual(bool(rows[arm]['reference_k_sha256']),arm in WITH_K)
        self.assertEqual(len({rows[k]['reference_k_sha256'] for k in WITH_K}),1)
        self.assertEqual(rows['A2']['partition_sha256'],rows['A2_K']['partition_sha256'])
        self.assertEqual(rows['A4']['partition_sha256'],rows['A4_K']['partition_sha256'])
        self.assertEqual(rows['A4']['a4_parent_sha256'],rows['A2']['partition_sha256'])

    def test_size_filter_abstains_before_k_and_solver(self):
        _,loaded=toy()
        plan=make_plan(ROOT)
        plan['limits']['max_variables']=100
        with patch('as05_factorial._load_timed',return_value=(loaded,.01,.01)), \
             patch('as05_factorial.resource.setrlimit'), \
             patch('as05_factorial._timed_k',side_effect=AssertionError('K indevido')), \
             patch('as05_factorial._optimize',side_effect=AssertionError('solver indevido')):
            result=_factorial_worker(Context(),{'nome':'toy.txt'},str(ROOT),'A4_K',plan)
        self.assertEqual(result['status'],'NOT_BUILT_SIZE')
        self.assertIsNone(result.get('lp_opt_value'))
        self.assertFalse(result['k_prepared_for_this_arm'])

    def test_lp_monotonicity_small_HiGHS_optional(self):
        try:
            from as02_solve import solve_scipy
        except ImportError:
            self.skipTest('SciPy opcional indisponível')
        instance,_=toy()
        a2,a4=partitions(instance,policy='reachability_degree',seed=42)
        values={}
        for arm in ('U','A2','A4'):
            result=solve_scipy(compile_factorial(instance,arm,groups2=a2,groups4=a4),time_limit=15)
            self.assertEqual(result.status,'OPTIMAL')
            values[arm]=result.objective
        self.assertLessEqual(values['U'],values['A2']+1e-7)
        self.assertLessEqual(values['A2'],values['A4']+1e-7)


class TestFactorialPlan(unittest.TestCase):
    def test_six_dev_arms_and_fixed_policy(self):
        p=make_plan(ROOT)
        self.assertEqual(len(p['cases']),6)
        self.assertEqual(p['arms'],list(ARMS))
        self.assertEqual(p['grouping']['policy'],'reachability_degree')
        self.assertEqual(p['scientific_promotion'],'NOT_AUTHORIZED')
        self.assertEqual(validate_plan(p,ROOT),p)

    def test_mutation_rejected(self):
        plan=make_plan(ROOT)
        for field,new in [('budget_seconds_per_arm',301),('grouping',{'policy':'balanced'})]:
            bad=copy.deepcopy(plan)
            bad[field]=new
            with self.assertRaises(ValueError):
                validate_plan(bad,ROOT)


def mock_record(row,*,root,arm,plan):
    values={'U':1.,'U_K':2.,'A2':1.3,'A2_K':2.2,'A4':1.5,'A4_K':2.4}
    id=row['nome'].removesuffix('.txt')
    hash_k=plan['k_policy']['expected_previous_hashes'].get(id,'mock_k')
    return {'case_name':row['nome'],'arm_id':arm,'status':'OPTIMAL_NUMERIC',
            'grouping_policy':plan['grouping']['policy'] if arm in ('A2','A2_K','A4','A4_K') else None,
            'model_complete':True,'lp_opt_value':values[arm],
            'instance_sha256':row['sha256'],'structural_sha256':'struct_'+id,
            'wall_total_s':1.,'solver_runtime_s':.1,
            'n_variables':100,'n_constraints':200,'n_nonzeros':300,
            'k_prepared_for_this_arm':arm in WITH_K,'k_validated':arm in WITH_K,
            'applied_k_sha256':hash_k if arm in WITH_K else None,
            'reference_k_sha256':hash_k if arm in WITH_K else None,
            'partition_sha256':('parent' if arm in ('A2','A2_K') else 'child'
                                if arm in ('A4','A4_K') else None),
            'a2_partition_sha256':'parent' if arm in ('A2','A2_K','A4','A4_K') else None,
            'a4_partition_sha256':'child' if arm in ('A2','A2_K','A4','A4_K') else None,
            'a4_parent_sha256':'parent' if arm in ('A2','A2_K','A4','A4_K') else None}


class TestFactorialReports(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.output=Path(self.t.name)/'run'
        self.plan=ROOT/'results/benchmark/as05-factorial-plan-v1.json'

    def run_mock(self,runner=mock_record):
        run_experiment(root=ROOT,plan_path=self.plan,output_dir=self.output,runner=runner)
        return verify_experiment(self.output)

    def test_all_36_rows_and_8_contrasts(self):
        report=self.run_mock()
        self.assertEqual(len(report['cases']),6)
        self.assertTrue(all(len(c['runs'])==6 for c in report['cases']))
        self.assertTrue(all(set(c['contrasts'])==set(__import__('as05_factorial').PAIRS) for c in report['cases']))
        self.assertEqual(report['scientific_gate'],'PENDING')
        self.assertEqual(report['scientific_promotion'],'NOT_AUTHORIZED')
        self.assertTrue((self.output/'manifest.json').is_file())

    def test_analysis_is_exploratory_and_append_only(self):
        self.run_mock()
        path=analyze_experiment(self.output,self.output/'analysis')
        content=json.loads((path.parent/'analysis.json').read_text())
        self.assertEqual(content['recommendation'],'PROMISING_EXPLORATORY_REPLICATION_REQUIRED')
        self.assertEqual(content['effects']['REFINEMENT_WITH_K']['n_comparable'],6)
        with self.assertRaises(FileExistsError):
            analyze_experiment(self.output,self.output/'analysis')

    def test_reject_drop_arm_in_report(self):
        report=self.run_mock()
        report['cases'][0]['runs'].pop()
        with self.assertRaises(ValueError):
            verify_case(report['cases'][0],make_plan(ROOT))

    def test_reject_k_hash_mismatch(self):
        report=self.run_mock()
        case=copy.deepcopy(report['cases'][0])
        case['runs'][3]['reference_k_sha256']='bad'
        with self.assertRaises(ValueError):
            verify_case(case,make_plan(ROOT))

    def test_reject_changing_a4_parent(self):
        report=self.run_mock()
        case=copy.deepcopy(report['cases'][0])
        case['runs'][4]['a4_parent_sha256']='new_parent'
        with self.assertRaises(ValueError):
            verify_case(case,make_plan(ROOT))

    def test_reject_censored_lp_value(self):
        report=self.run_mock()
        case=copy.deepcopy(report['cases'][0])
        case['runs'][4]['status']='TIMEOUT_SOLVER'
        case['runs'][4]['model_complete']=False
        with self.assertRaises(ValueError):
            verify_case(case,make_plan(ROOT))

    def test_detect_file_tampering(self):
        self.run_mock()
        path=self.output/'arms.csv'
        path.write_text(path.read_text()+'tampered\n')
        with self.assertRaises(ValueError):
            verify_experiment(self.output)

    def test_resume_only_unfinished(self):
        seen=[]
        def flaky(row,*,root,arm,plan):
            seen.append((row['nome'],arm))
            if len(seen)==4:
                raise RuntimeError('interrupção simulada')
            return mock_record(row,root=root,arm=arm,plan=plan)
        with self.assertRaises(RuntimeError):
            run_experiment(root=ROOT,plan_path=self.plan,output_dir=self.output,runner=flaky)
        self.assertEqual(len(seen),4)
        def done(row,*,root,arm,plan):
            seen.append((row['nome'],arm))
            return mock_record(row,root=root,arm=arm,plan=plan)
        run_experiment(root=ROOT,plan_path=self.plan,output_dir=self.output,
                       runner=done,resume=True)
        self.assertEqual(len(seen),37)
        self.assertEqual(len(verify_experiment(self.output)['cases']),6)

    def test_reject_corrupted_checkpoint_on_resume(self):
        def crash(row,*,root,arm,plan):
            if arm=='U_K':raise RuntimeError('erro artificial')
            return mock_record(row,root=root,arm=arm,plan=plan)
        with self.assertRaises(RuntimeError):
            run_experiment(root=ROOT,plan_path=self.plan,output_dir=self.output,runner=crash)
        checkpoint=next((self.output/'checkpoints').rglob('arm-00.json'))
        checkpoint.write_text(checkpoint.read_text()+' ')
        with self.assertRaises(ValueError):
            run_experiment(root=ROOT,plan_path=self.plan,output_dir=self.output,
                           runner=mock_record,resume=True)

    def test_verifier_rejects_changing_report_without_updating_manifest(self):
        self.run_mock()
        obj=json.loads((self.output/'report.json').read_text())
        obj['cases'][0]['runs'][0]['lp_opt_value']=900
        (self.output/'report.json').write_text(json.dumps(obj))
        with self.assertRaises(ValueError):
            verify_experiment(self.output)


if __name__=='__main__':
    unittest.main()
