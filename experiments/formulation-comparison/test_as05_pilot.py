"""AS-05: testes derivados de cada AC, contra adulteração e falha segura."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for folder in (ROOT,HERE,HERE.parent/'alternative-formulations'):
    if str(folder) not in sys.path:
        sys.path.insert(0,str(folder))

from as04_schema import ArmResult,SolverPolicy  # noqa: E402
from as04_compare import compare_case  # noqa: E402
from as05_protocol import make_plan,plan_digest,read_plan,sha256_file,validate_plan  # noqa: E402
from as05_gate import a4_selection,assess_gate,metrics_for_case  # noqa: E402
from as05_pilot import run_pilot,verify_pilot,verify_preconditions  # noqa: E402


def fixture():
    protocol=json.loads((ROOT/'results/benchmark/protocol.json').read_text(encoding='utf-8'))
    plan=make_plan(protocol,as00_sha256=sha256_file(ROOT/'results/benchmark/protocol.json'),
                   manifest_sha256=sha256_file(ROOT/'instances/manifest.csv'))
    return plan,protocol


def result_for(case, *, z=(2.,3.,3.3), statuses=None, walls=(1.,1.,1.4), seed=42,
               selected=('U','U_K','A2_K')):
    pol=SolverPolicy(seed=seed,threads=4,budget_s=90.,memory_limit_bytes=16*1024**3)
    records=[]
    for arm,value,wall in zip(('U','U_K','A2_K'),z,walls):
        status=statuses.get(arm,'OPTIMAL_NUMERIC') if statuses else 'OPTIMAL_NUMERIC'
        rec=ArmResult(case_name=case['manifest_name'],arm_id=arm,mode='LP',status=status,
                      instance_sha256=case['source_sha256'],structural_sha256='s-hash',
                      reference_k_sha256='k-hash',applied_k_sha256=None if arm=='U' else 'k-hash',
                      k_validated=True,solver_policy_sha256=pol.sha256,solver_policy=vars(pol).copy(),
                      model_complete=status=='OPTIMAL_NUMERIC',lp_opt_value=value,
                      wall_total_s=wall)
        if arm in selected:
            records.append(rec)
    return {'case_name':case['manifest_name'],'mode':'LP', 'arms':[x.to_dict() for x in records],
            'comparison':compare_case(records),'policy_sha256':pol.sha256,'schema':'AS04-COMPARISON-v1'}


def evidence():
    return {'as04_verdict':'PASS',
            'as02_evidence':{'as01_verdict':'PASS','as01_independent_reviewer':True,
                             'physical_exhaustion_passed':True,'sec59_lp_passed':True,
                             'math_counterexample':False,'as02_independent_reviewer':True},
            'reviewers':{x:{'author':'autor','reviewer':f'verificador-{x}',
                            'evidence_path':f'docs/review/{x}.md'} for x in ('as01','as02','as04')}}


class AS05Protocol(unittest.TestCase):
    def test_as05_01_exact_six_dev_and_three_arms(self):
        p,ref=fixture()
        self.assertEqual(len(p['pilot_cases']),6)
        self.assertEqual(p['main_arms'],['U','U_K','A2_K'])
        self.assertEqual({c['split'] for c in p['pilot_cases']},{'desenvolvimento'})
        validate_plan(p,ref,ROOT)

    def test_as05_01_frozen_as00_untouched(self):
        p,_=fixture()
        self.assertEqual(p['basis_protocol_sha256'],sha256_file(ROOT/'results/benchmark/protocol.json'))
        self.assertEqual(p['policy']['wall_budget_s_per_arm'],90)
        self.assertEqual(p['policy']['threads'],4)

    def test_as05_01_evaluation_case_rejected(self):
        p,ref=fixture()
        p['pilot_cases'][0]['name']='mapf-den312d-m50-f2-rho'
        with self.assertRaises(ValueError):validate_plan(p,ref,ROOT)

    def test_as05_01_input_sha_mutation_rejected(self):
        p,ref=fixture()
        p['pilot_cases'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):validate_plan(p,ref,ROOT)

    def test_as05_01_digest_order_independent(self):
        p,_=fixture()
        self.assertEqual(plan_digest(p),plan_digest(json.loads(json.dumps(p,sort_keys=True))))

    def test_as05_03_a4_disabled_default(self):
        p,_=fixture()
        c=p['pilot_cases'][0]
        metric=metrics_for_case(c,result_for(c),p['materiality_addendum'])
        self.assertEqual(a4_selection(c,metric,p),(False,'NOT_SELECTED_REASON:A4_DISABLED_IN_FROZEN_PLAN'))

    def test_as05_03_a4_trigger_only_if_gain(self):
        p,ref=fixture()
        p['a4']['policy']='ON_MATERIAL_A2_GAIN'
        validate_plan(p,ref,ROOT)
        c=p['pilot_cases'][0]
        yes=metrics_for_case(c,result_for(c),p['materiality_addendum'])
        no=metrics_for_case(c,result_for(c,z=(2.,3.,3.)),p['materiality_addendum'])
        self.assertTrue(a4_selection(c,yes,p)[0]);self.assertFalse(a4_selection(c,no,p)[0])

    def test_as05_03_nonnested_auto_forbidden_by_adapter(self):
        p,ref=fixture()
        p['a4']['policy']='PRESELECTED_HYPOTHESIS'
        with self.assertRaises(ValueError):validate_plan(p,ref,ROOT)
        p['a4']['preselected_case_hypotheses']={p['pilot_cases'][0]['name']:'Grafo estruturado com clusters distantes'}
        validate_plan(p,ref,ROOT)

    def test_as05_05_zero_or_nonfinite_threshold_rejected(self):
        p,ref=fixture()
        p['materiality_addendum']['relative_gain_min']=0
        with self.assertRaises(ValueError):validate_plan(p,ref,ROOT)
        p['materiality_addendum']['relative_gain_min']=float('nan')
        with self.assertRaises(ValueError):validate_plan(p,ref,ROOT)


class AS05Metrics(unittest.TestCase):
    def setUp(self):self.plan,_=fixture();self.rule=self.plan['materiality_addendum'];self.case=self.plan['pilot_cases'][0]

    def test_as05_04_two_deltas_are_separate(self):
        m=metrics_for_case(self.case,result_for(self.case),self.rule)
        self.assertAlmostEqual(m['contrasts']['K_EFFECT']['absolute'],1.0)
        self.assertAlmostEqual(m['contrasts']['A_EFFECT']['absolute'],.3)
        self.assertAlmostEqual(m['contrasts']['A_EFFECT']['relative'],.1)
        self.assertTrue(m['material_a_gain'])

    def test_as05_04_tolerance_blocks_tiny_gain(self):
        m=metrics_for_case(self.case,result_for(self.case,z=(2.,3.,3.+5e-7)),self.rule)
        self.assertFalse(m['material_a_gain'])

    def test_as05_04_false_claimed_delta_detected(self):
        r=result_for(self.case)
        r['comparison']['pairs'][1]['lp_delta']=12.0
        with self.assertRaises(ValueError):metrics_for_case(self.case,r,self.rule)

    def test_as05_05_interrupted_lp_is_censored(self):
        r=result_for(self.case,statuses={'A2_K':'TIME_LIMIT'})
        m=metrics_for_case(self.case,r,self.rule)
        self.assertIsNone(m['contrasts']['A_EFFECT']['absolute'])
        self.assertFalse(m['material_a_gain'])
        self.assertEqual(r['arms'][2]['lp_opt_value'],None)

    def test_as05_05_missing_arm_rejected(self):
        r=result_for(self.case)
        r['arms'].pop()
        with self.assertRaises(ValueError):metrics_for_case(self.case,r,self.rule)

    def test_as05_05_wrong_mode_rejected(self):
        r=result_for(self.case);r['mode']='MIP'
        with self.assertRaises(ValueError):metrics_for_case(self.case,r,self.rule)

    def test_as05_06_reproduction_only_with_seeds_43_44(self):
        from as05_gate import assess_reproduction
        base=result_for(self.case)
        reps=[result_for(self.case,seed=s,selected=('U_K','A2_K')) for s in (43,44)]
        observed=assess_reproduction(self.case,base,reps,self.rule,[42,43,44])
        self.assertEqual(observed['status'],'PASS')
        self.assertEqual(observed['verified_seeds'],[43,44])
        missing=assess_reproduction(self.case,base,reps[:1],self.rule,[42,43,44])
        self.assertEqual(missing['status'],'PENDING')

    def test_as05_06_reproduction_rejects_wrong_source_hash(self):
        from as05_gate import assess_reproduction
        base=result_for(self.case)
        reps=[result_for(self.case,seed=s,selected=('U_K','A2_K')) for s in (43,44)]
        reps[0]['arms'][0]['structural_sha256']='fake'
        with self.assertRaises(ValueError):
            assess_reproduction(self.case,base,reps,self.rule,[42,43,44])

    def test_as05_06_reproduction_rejects_partition_changed(self):
        from as05_gate import assess_reproduction
        base=result_for(self.case)
        base['arms'][2]['partition_sha256']='group42'
        reps=[result_for(self.case,seed=s,selected=('U_K','A2_K')) for s in (43,44)]
        reps[0]['arms'][1]['partition_sha256']='group43'
        reps[1]['arms'][1]['partition_sha256']='group42'
        with self.assertRaisesRegex(ValueError,'partição A2'):
            assess_reproduction(self.case,base,reps,self.rule,[42,43,44])

    def test_as05_06_not_promote_without_reproduction(self):
        metrics=[metrics_for_case(c,result_for(c),self.rule) for c in self.plan['pilot_cases']]
        self.assertEqual(assess_gate(metrics,self.plan)['verdict'],'INVESTIGATE')

    def test_as05_06_independent_raw_graphs_and_sources(self):
        metrics=[metrics_for_case(c,result_for(c),self.rule) for c in self.plan['pilot_cases']]
        for m in metrics:
            m['reproduction']={'status':'PASS','reason':'ganho reproduzido','verified_seeds':[43,44]}
        result=assess_gate(metrics,self.plan)
        self.assertEqual(result['verdict'],'GO')
        self.assertEqual(result['denominator_cases'],6)
        self.assertGreaterEqual(result['n_winning_sources'],2)

    def test_as05_06_only_puc_family_is_stop(self):
        metrics=[]
        for c in self.plan['pilot_cases']:
            m=metrics_for_case(c,result_for(c,z=(2.,3.,3.3) if c['graph_source']=='puc' else (2.,3.,3.)),self.rule)
            metrics.append(m)
        for m in metrics:
            if m['material_a_gain'] and m['wall_acceptable']:
                m['reproduction']={'status':'PASS','reason':'ganho reproduzido','verified_seeds':[43,44]}
        result=assess_gate(metrics,self.plan)
        self.assertEqual(result['verdict'],'STOP')
        self.assertEqual(result['n_winning_sources'],1)

    def test_as05_06_censored_is_investigate_not_stop_or_go(self):
        metrics=[metrics_for_case(c,result_for(c,statuses={'A2_K':'TIME_LIMIT'} if i==2 else None),self.rule)
                 for i,c in enumerate(self.plan['pilot_cases'])]
        result=assess_gate(metrics,self.plan)
        self.assertEqual(result['verdict'],'INVESTIGATE')
        self.assertEqual(result['censored_cases'],[self.plan['pilot_cases'][2]['name']])

    def test_as05_06_slow_wall_blocks_go(self):
        metrics=[metrics_for_case(c,result_for(c,walls=(1.,1.,3.5) if i==2 else (1.,1.,1.2)),self.rule)
                 for i,c in enumerate(self.plan['pilot_cases'])]
        self.assertEqual(assess_gate(metrics,self.plan)['verdict'],'STOP')

    def test_as05_06_two_mapf_seeds_count_once(self):
        metrics=[metrics_for_case(c,result_for(c),self.rule) for c in self.plan['pilot_cases']]
        # Injetar nome de variante para tentar inflar denominador: deve falhar.
        fake=copy.deepcopy(metrics[0]);fake['name']='mapf-room-copy'
        with self.assertRaises(ValueError):assess_gate(metrics[:-1]+[fake],self.plan)

    def test_as05_06_nondominance_is_investigate(self):
        metrics=[]
        for i,c in enumerate(self.plan['pilot_cases']):
            z=(2.,3.,2.5) if i==0 else (2.,3.,3.3)
            metrics.append(metrics_for_case(c,result_for(c,z=z),self.rule))
        self.assertEqual(assess_gate(metrics,self.plan)['verdict'],'INVESTIGATE')


class AS05Integration(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.t=Path(self.tmp.name)
    def _paths(self):
        p,_=fixture()
        planpath=self.t/'plan.json';planpath.write_text(json.dumps(p),encoding='utf-8')
        epath=self.t/'evidence.json';epath.write_text(json.dumps(evidence()),encoding='utf-8')
        return p,planpath,epath

    def test_as05_gate_blocks_absent_review(self):
        with self.assertRaises(RuntimeError):verify_preconditions({})
        e=evidence();e['as02_evidence']['as01_independent_reviewer']=False
        with self.assertRaises(RuntimeError):verify_preconditions(e)

    def test_as05_gate_blocks_same_author_and_reviewer(self):
        e=evidence();e['reviewers']['as01']['reviewer']='autor'
        with self.assertRaises(RuntimeError):verify_preconditions(e)

    def test_as05_pilot_6x3_report_integrity(self):
        plan,planpath,epath=self._paths()
        by_name={c['manifest_name']:c for c in plan['pilot_cases']}
        def case_runner(row,**kwargs):
            self.assertIn(kwargs['arm_ids'],(('U','U_K','A2_K'),('U_K','A2_K')))
            self.assertEqual(kwargs['policy'].budget_s,90)
            return result_for(by_name[row['nome']],seed=kwargs['policy'].seed,
                              selected=kwargs['arm_ids'])
        single=Mock(side_effect=RuntimeError('A4 não deveria rodar'))
        dst=self.t/'pilot-001'
        run_pilot(root=ROOT,plan_path=planpath,evidence_path=epath,output_dir=dst,
                  run_case_fn=case_runner,run_arm_fn=single)
        self.assertFalse(single.called)
        report=verify_pilot(dst)
        self.assertEqual(report['decision']['verdict'],'GO')
        self.assertEqual(len(report['cases']),6)
        self.assertEqual(len(list((dst/'cases').glob('*/arms.csv'))),6)
        with self.assertRaises(FileExistsError):
            run_pilot(root=ROOT,plan_path=planpath,evidence_path=epath,output_dir=dst,
                      run_case_fn=case_runner,run_arm_fn=single)

    def test_as05_no_solver_call_before_gate(self):
        p,pp,ep=self._paths();e=evidence();e['as04_verdict']='PENDING';ep.write_text(json.dumps(e))
        solver=Mock(side_effect=RuntimeError('DO_NOT_CALL'))
        with self.assertRaisesRegex(RuntimeError,'AS05_BLOCKED'):
            run_pilot(root=ROOT,plan_path=pp,evidence_path=ep,output_dir=self.t/'blocked',
                      run_case_fn=solver)
        self.assertFalse(solver.called)

    def test_as05_05_worker_exception_retains_all_cases(self):
        p,pp,ep=self._paths()
        dst=self.t/'pilot-worker-error'
        def fails(_row,**_kw):
            raise RuntimeError('backend indisponível')
        run_pilot(root=ROOT,plan_path=pp,evidence_path=ep,output_dir=dst,
                  run_case_fn=fails)
        report=verify_pilot(dst)
        self.assertEqual(report['decision']['verdict'],'INVESTIGATE')
        self.assertEqual(len(report['cases']),6)
        for c in report['cases']:
            self.assertEqual(set(c['arm_statuses'].values()),{'WORKER_ERROR'})
            data=json.loads((dst/'cases'/c['name']/'comparison.json').read_text())
            self.assertEqual(len(data['arms']),3)
            self.assertTrue(all(x['lp_opt_value'] is None for x in data['arms']))

    def test_as05_sensor_report_tampering(self):
        p,pp,ep=self._paths();index={c['manifest_name']:c for c in p['pilot_cases']}
        dst=self.t/'pilot-002'
        run_pilot(root=ROOT,plan_path=pp,evidence_path=ep,output_dir=dst,
                  run_case_fn=lambda row,**kwargs:result_for(index[row['nome']],seed=kwargs['policy'].seed,
                                                       selected=kwargs['arm_ids']))
        j=dst/'lp_gate.json';j.write_text(j.read_text().replace('"GO"','"STOP"'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'integridade'):
            verify_pilot(dst)


if __name__=='__main__':unittest.main()
