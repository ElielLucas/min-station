"""Tests AS09 expanded benchmark protocol without requiring Gurobi."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
for p in (str(HERE),str(ROOT),str(ROOT/'experiments/formulation-comparison')):
    if p not in sys.path:
        sys.path.insert(0,p)

from fc_budget import BoundedOutcome
from run_as09_extended import (ARMS, MODES, FULL_CASES, PRIOR_SIX, ROOT,
    analyze, canonical_hash, execute, make_plan, selected_cases, validate_plan, verify)


def fake_bounded(_fn, row, _root, mode, arm, plan, *, budget_s):
    is_c = arm.startswith('C')
    base = {'instance_sha256':row['sha256'],'model_complete':True,
            'K_sha256':'same-K' if arm.endswith('_K') else None,
            'K_validated':arm.endswith('_K'), 'n_variables':50 if is_c else 100,
            'n_constraints':70 if is_c else 20,'n_nonzeros':150 if is_c else 250,
            'peak_rss_kb': 100*1024 if is_c else 200*1024,
            'solver_runtime_s':1.0 if is_c else 1.5}
    if mode == 'LP':
        base.update(status='OPTIMAL_NUMERIC',lp_numeric_value=5.0)
    else:
        base.update(status='TIME_LIMIT',lp_numeric_value=None,
                    physical_validated_ub=12, mip_numeric_incumbent=12,
                    mip_numeric_bound=10.0, validated_mip_gap=(12-10)/12,
                    nodes=50, time_to_first_validated_ub_solver_s=0.5)
    return BoundedOutcome('COMPLETED',base,1.0 if is_c else 2.0,tuple())


class TestAS09Extended(unittest.TestCase):
    def test_full_suite_retains_original_six_plus_distinct_expansion(self):
        self.assertEqual(len(FULL_CASES),15)
        self.assertEqual(FULL_CASES[:6],PRIOR_SIX)
        self.assertEqual(len(set(FULL_CASES)),15)
        rows = selected_cases(ROOT,'full')
        self.assertEqual(len(rows),15)
        self.assertGreaterEqual(len(set(r['source_family'] for r in rows)),5)
        self.assertTrue(all(r['r']>=1 and len(r['source_sha256'])==64 for r in rows))

    def test_plan_freeze_both_modes_caps_and_budget(self):
        p=make_plan(ROOT)
        self.assertEqual(p['budget_seconds_per_arm'],600)
        self.assertEqual(p['modes'],['LP','MIP'])
        self.assertEqual(p['arms'],list(ARMS))
        self.assertEqual(validate_plan(p,ROOT),p)
        q=json.loads(json.dumps(p));q['solver']['seed']=43
        with self.assertRaises(ValueError):validate_plan(q,ROOT)
        q=json.loads(json.dumps(p));q['cases'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):validate_plan(q,ROOT)
        with self.assertRaises(ValueError):make_plan(ROOT,budget=1)

    def test_lp_and_mip_append_only_verifiable_and_analysis(self):
        p=make_plan(ROOT,suite='smoke')
        with tempfile.TemporaryDirectory() as tmp, patch('run_as09_extended.run_bounded',side_effect=fake_bounded):
            out=Path(tmp)/'campaign'
            self.assertEqual(len(execute(p,ROOT,out,mode='LP')),8)
            self.assertEqual(len(execute(p,ROOT,out,mode='MIP')),8)
            self.assertEqual(len(verify(p,ROOT,out,mode='LP')),8)
            self.assertEqual(len(verify(p,ROOT,out,mode='MIP')),8)
            self.assertIn('EXPLORATORY',analyze(p,ROOT,out,mode='ALL'))
            analysis=json.loads((out/'analysis-all.json').read_text())
            self.assertEqual(len(analysis['rows']),16)
            self.assertEqual(analysis['math_gate'],'PROOF_REVIEW_REQUIRED')
            self.assertTrue(all(r['mip_gap_validated'] is not None for r in analysis['rows'] if r['mode']=='MIP'))
            with self.assertRaises(FileExistsError):execute(p,ROOT,out,mode='MIP')
            self.assertEqual(len(execute(p,ROOT,out,mode='MIP',resume=True)),8)
            fp=out/'LP'/f'{p["cases"][0]["case"]}--C.json'
            fp.write_bytes(fp.read_bytes()+b' ')
            with self.assertRaises(ValueError):verify(p,ROOT,out,mode='LP')

    def test_censor_never_publishes_fake_metrics(self):
        p=make_plan(ROOT,suite='smoke')
        def censored(_fn,row,_root,mode,arm,plan,*,budget_s):
            return BoundedOutcome('TIMEOUT_SOLVER',None,600.0,(('solve',599.),),'worker killed')
        with tempfile.TemporaryDirectory() as tmp, patch('run_as09_extended.run_bounded',side_effect=censored):
            out=Path(tmp)/'campaign'
            execute(p,ROOT,out,mode='MIP')
            res=verify(p,ROOT,out,mode='MIP')
            self.assertTrue(all(r.get('validated_mip_gap') is None and
                                r.get('mip_numeric_bound') is None and
                                r.get('physical_validated_ub') is None for r in res.values()))
            self.assertEqual(analyze(p,ROOT,out,mode='MIP'),'EXPLORATORY_WITH_CENSORED_ARMS')
            with self.assertRaises(FileNotFoundError):analyze(p,ROOT,out,mode='ALL')

    def test_mip_gap_verification_rejects_forged_gap(self):
        p=make_plan(ROOT,suite='smoke')
        with tempfile.TemporaryDirectory() as tmp, patch('run_as09_extended.run_bounded',side_effect=fake_bounded):
            out=Path(tmp)/'campaign';execute(p,ROOT,out,mode='MIP')
            filename=f'{p["cases"][0]["case"]}--U.json'
            fp=out/'MIP'/filename
            res=json.loads(fp.read_text());res['validated_mip_gap']=0.0
            fp.write_text(json.dumps(res))
            # Hash check already detects tampering.
            with self.assertRaises(ValueError):verify(p,ROOT,out,mode='MIP')

    def test_no_same_source_with_different_cut_hash(self):
        p=make_plan(ROOT,suite='smoke')
        def different(_fn,row,_root,mode,arm,plan,*,budget_s):
            outcome=fake_bounded(_fn,row,_root,mode,arm,plan,budget_s=budget_s)
            outcome.value['K_sha256'] = ('wrong' if arm=='C_K' else outcome.value['K_sha256'])
            return outcome
        with tempfile.TemporaryDirectory() as tmp,patch('run_as09_extended.run_bounded',side_effect=different):
            with self.assertRaises(ValueError):execute(p,ROOT,Path(tmp)/'campaign',mode='LP')

if __name__=='__main__':unittest.main()
