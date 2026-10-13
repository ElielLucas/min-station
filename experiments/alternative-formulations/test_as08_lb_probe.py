"""AS-08/LB — limites racionais antes de convergir; sem relaxar a auditoria."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FC=ROOT/'experiments/formulation-comparison'
if str(FC) not in sys.path:sys.path.insert(0,str(FC))
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))

from as02_solve import solve
from as08_b_exact import compile_b
from as08_column_generation import CGConfig,run_column_generation,verify_rational_certificate
from run_as08_t2a import FIXTURES,build_fixture
import run_as08_lb_probe as probe
from fc_budget import BoundedOutcome

FIXTURE=next(f for f in FIXTURES if f.name=='e1-b4-star')


class TestIntermediateCertificates(unittest.TestCase):
    def setUp(self):
        self.ins,self.K=build_fixture(FIXTURE)

    def config(self,**params):
        default=dict(backend='scipy-highs',seconds=12.0,iterations=30,
                     max_columns=1,per_round=1,
                     intermediate_cert_every=1,
                     intermediate_cert_budget_s=3.,
                     intermediate_cert_min_remaining_s=1.,
                     intermediate_cert_max_attempts=3)
        default.update(params)
        return CGConfig(**default)

    def test_censored_run_has_auditable_global_bound(self):
        events=[]
        res=run_column_generation(self.ins,self.K,config=self.config(),progress=events.append)
        self.assertEqual(res['status'],'CAP_EXCEEDED')
        self.assertIsNone(res.get('numeric_primal_dual_gap'))
        self.assertGreaterEqual(res['intermediate_cert_successes'],1)
        cert=res['global_lb_certificate']
        self.assertTrue(verify_rational_certificate(self.ins,self.K,cert))
        exact,_=compile_b(self.ins,self.K)
        optimum=solve(exact,backend='scipy-highs')
        self.assertEqual(optimum.status,'OPTIMAL')
        self.assertLessEqual(Fraction(cert['rational']),Fraction(str(optimum.objective))+Fraction('0.0000001'))
        self.assertTrue(any(e['event']=='INTERMEDIATE_CERT_IMPROVED' and
                            e.get('certificate')==cert for e in events))
        self.assertTrue(all('global_lower_bound' not in e or e['global_lower_bound'] is None
                            for e in res['iterations'] if e['iter']==0))

    def test_off_by_default_preserves_previous_behavior(self):
        base=self.config(intermediate_cert_every=0)
        e=[]
        res=run_column_generation(self.ins,self.K,config=base,progress=e.append)
        self.assertEqual(res['intermediate_cert_attempts'],0)
        self.assertFalse(any('INTERMEDIATE_CERT' in item['event'] for item in e))

    def test_partial_certificate_does_not_publish_lower_bound(self):
        import as08_column_generation as mod
        def stub(*args,**kwargs):
            return {'status':'CERTIFICATE_TIMEOUT','lower_bound':None,'rational':None}
        with patch.object(mod,'certified_bound',stub):
            r=run_column_generation(self.ins,self.K,config=self.config())
        self.assertIsNone(r['global_lower_bound'])
        self.assertIsNone(r['global_lb_certificate'])

    def test_invalid_options_rejected(self):
        with self.assertRaises(ValueError):
            self.config(intermediate_cert_every=1,rational_certificate=False).validate()
        with self.assertRaises(ValueError):
            self.config(intermediate_cert_budget_s=0).validate()
        with self.assertRaises(ValueError):
            self.config(intermediate_cert_max_attempts=-1).validate()

    def test_mutated_dual_fails_independent_verifier(self):
        r=run_column_generation(self.ins,self.K,config=self.config())
        forged=json.loads(json.dumps(r['global_lb_certificate']))
        forged['rational']='9000'
        with self.assertRaises(ValueError):
            verify_rational_certificate(self.ins,self.K,forged)


class TestProbePlan(unittest.TestCase):
    def test_plan_is_frozen_to_three_cases(self):
        p=probe.make_plan(ROOT)
        self.assertEqual(tuple(c['name'] for c in p['cases']),probe.SELECTED)
        self.assertEqual(len(p['cases']),3)
        self.assertIs(probe.validate_plan(p,ROOT),p)
        p=json.loads(json.dumps(p))
        p['cg']['intermediate_cert_every']=0
        with self.assertRaises(ValueError):
            probe.validate_plan(p,ROOT)

    def test_summary_does_not_claim_gain_without_dual(self):
        p=probe.make_plan(ROOT)
        c=p['cases'][0]
        u={'case':c,'arm':'U_K','status':'OPTIMAL_NUMERIC','lp_numeric_value':13.2,
           'K_sha256':'same','wall_total_s':1.}
        b={'case':c,'arm':'B_K','status':'CAP_EXCEEDED','lp_numeric_value':None,
           'global_lb_certificate':None,'K_sha256':'same','wall_total_s':5.}
        rows=[u,b]
        # analyze usa pares exatamente adjacentes e não altera LP quando censurado.
        # Acrescentar os outros pares no mesmo formato.
        for extra in p['cases'][1:]:
            rows.extend([{**u,'case':extra},{**b,'case':extra}])
        with tempfile.TemporaryDirectory() as tmp:
            report=probe.analyze(rows,Path(tmp),[])
            self.assertEqual(report['decision'],'INCONCLUSIVE_NO_MATERIAL_CERTIFIED_GAIN')
            self.assertTrue(all(x['b_lp_optimal'] is None for x in report['cases']))


    def test_two_independent_sources_trigger_only_exploratory_gate(self):
        p=probe.make_plan(ROOT)
        # Teste só da regra de análise; NÃO autentica certificados sintéticos.
        cases=p['cases']
        self.assertGreaterEqual(len(set(c['graph_source'] for c in cases)),2)
        rows=[]
        for c in cases:
            val=10.0
            rows.extend([
                {'case':c,'arm':'U_K','status':'OPTIMAL_NUMERIC',
                 'lp_numeric_value':val,'K_sha256':'matching-K','wall_total_s':1.0},
                {'case':c,'arm':'B_K','status':'CAP_EXCEEDED',
                 'lp_numeric_value':None,
                 'global_lb_certificate':{'status':'CERTIFIED_RATIONAL_DUAL','rational':'11'},
                 'K_sha256':'matching-K','wall_total_s':10.0},
            ])
        with tempfile.TemporaryDirectory() as td:
            report=probe.analyze(rows,Path(td),[c['name'] for c in cases])
            self.assertEqual(report['decision'],'EVIDENCE_FOR_CONTINUATION_EXPLORATORY')
            self.assertTrue(all(item['b_lp_optimal'] is None for item in report['cases']))
            self.assertTrue(all(item['material_gain_gt_1pct'] for item in report['cases']))

    def test_unaudited_certificate_cannot_enter_analysis(self):
        p=probe.make_plan(ROOT)
        rows=[]
        for c in p['cases']:
            rows.extend([
                {'case':c,'arm':'U_K','status':'OPTIMAL_NUMERIC',
                 'lp_numeric_value':10.0,'K_sha256':'same','wall_total_s':1.},
                {'case':c,'arm':'B_K','status':'TIMEOUT_SOLVER',
                 'lp_numeric_value':None,'K_sha256':'same','wall_total_s':10.,
                 'global_lb_certificate':{'status':'CERTIFIED_RATIONAL_DUAL',
                                          'rational':'1000000'}},
            ])
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'não auditado'):
                probe.analyze(rows,Path(td),[])



class TestTimeoutRecovery(unittest.TestCase):
    def test_supervisor_preserves_last_complete_certificate_not_rmp(self):
        plan=probe.make_plan(ROOT,backend='scipy-highs')
        c0=plan['cases'][0]
        ins,K=build_fixture(FIXTURE)
        small=run_column_generation(ins,K,config=CGConfig(
            backend='scipy-highs',seconds=10,per_round=1,max_columns=1,
            intermediate_cert_every=1,intermediate_cert_budget_s=3.,
            intermediate_cert_min_remaining_s=1.,intermediate_cert_max_attempts=2))
        cert=small['global_lb_certificate']
        self.assertIsNotNone(cert)

        def fake_bounded(worker, manifest_row, root, arm, local_plan, budget_s, on_progress=None):
            if arm=='U_K':
                return BoundedOutcome('COMPLETED',{
                    'status':'OPTIMAL_NUMERIC','lp_numeric_value':2.,
                    'k_validated':True,'K_sha256':'sample-K',
                    'instance_sha256':manifest_row['sha256'],
                    'global_lower_bound':None},0.2,())
            if on_progress:
                on_progress({'schema':'AS08-CG-PROGRESS-v1','event':'INPUT_READY',
                             'elapsed_seconds':0.,
                             'K_sha256':'sample-K','K_count':1,
                             'instance_sha256':manifest_row['sha256']})
                on_progress({'schema':'AS08-CG-PROGRESS-v1',
                             'event':'INTERMEDIATE_CERT_IMPROVED','elapsed_seconds':1.,
                             'iteration':2,'certificate':cert,
                             'certified_global_lb':float(Fraction(cert['rational'])),
                             'rmp_objective_with_artificials':9999.})
            return BoundedOutcome('TIMEOUT_SOLVER',None,10.,(),'worker killed')

        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            with patch.object(probe,'run_bounded',side_effect=fake_bounded):
                runs=probe.execute(plan,ROOT,out)
            b=next(x for x in runs if x['arm']=='B_K')
            self.assertEqual(b['status'],'TIMEOUT_SOLVER')
            self.assertIsNone(b.get('lp_numeric_value'))
            self.assertEqual(b['global_lower_bound'],float(Fraction(cert['rational'])))
            self.assertTrue(b['certified_lb_recovered_from_progress'])
            checkpoint=json.loads((out/probe._progress_name(c0)).read_text())
            self.assertEqual(checkpoint['latest_certificate'],cert)
            self.assertTrue(all('certificate' not in e for e in checkpoint['events']))
            self.assertEqual(len(probe.verify(out,ROOT)),6)
            # Nenhum certificado sintético pode passar pela auditoria real;
            # o teste do transporte não constitui aprovação científica.
            with self.assertRaises((ValueError,KeyError,AssertionError)):
                probe.audit_duals(runs,ROOT)
            frozen=out/'manifest.json'
            record_path=out/probe._progress_name(c0)
            obj=json.loads(record_path.read_text())
            obj['latest_certificate']['rational']='123456'
            record_path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                probe.verify(out,ROOT)


if __name__=='__main__':
    unittest.main()
