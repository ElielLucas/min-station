"""Protocol tests are independent of Gurobi availability and source execution."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fc_budget import BoundedOutcome
from run_as09_pilot import (ROOT, ARMS, CASES, analyze, digest, execute,
                            make_plan, validate_plan, verify)


class TestAS09Pilot(unittest.TestCase):
    def test_plan_freezes_inputs_arms_and_implementation(self):
        plan=make_plan(ROOT)
        self.assertEqual(plan['arms'],list(ARMS))
        self.assertEqual(tuple(c['case'] for c in plan['cases']),CASES)
        self.assertEqual(plan['math_gate'],'PROOF_REVIEW_REQUIRED')
        self.assertEqual(len(plan['implementation_sha256']),4)
        self.assertEqual(plan['budget_seconds_per_arm'],300)
        self.assertEqual(validate_plan(plan,ROOT),plan)
        wrong=json.loads(json.dumps(plan))
        wrong['cases'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):validate_plan(wrong,ROOT)
        wrong=json.loads(json.dumps(plan))
        wrong['solver']['seed']=999
        with self.assertRaises(ValueError):validate_plan(wrong,ROOT)

    def test_censored_results_never_publish_lp_and_artifacts_are_immutable(self):
        plan=make_plan(ROOT)
        def fake_supervisor(_func,row,_root,arm,_plan,*,budget_s):
            if arm in ('U','U_K'):
                result={'status':'OPTIMAL_NUMERIC','lp_numeric_value':10.0,
                        'instance_sha256':row['sha256'],'model_complete':True,
                        'n_variables':20,'n_constraints':10,'K_sha256':'hash' if arm.endswith('_K') else None,
                        'K_validated':arm.endswith('_K')}
            else:
                result={'status':'NOT_BUILT_SIZE','lp_numeric_value':None}
            return BoundedOutcome('COMPLETED',result,1.0,tuple())
        with tempfile.TemporaryDirectory() as td,patch('run_as09_pilot.run_bounded',side_effect=fake_supervisor):
            folder=Path(td)/'pilot'
            result=execute(plan,ROOT,folder)
            self.assertEqual(len(result),12)
            decision=analyze(folder,ROOT)
            self.assertEqual(decision,'INVESTIGATE_CENSORED')
            with self.assertRaises(FileExistsError):execute(plan,ROOT,folder)
            raw=json.loads((folder/f'{CASES[0]}--C_K.json').read_text())
            raw['lp_numeric_value']=99
            (folder/f'{CASES[0]}--C_K.json').write_text(json.dumps(raw))
            with self.assertRaises(ValueError):verify(folder,ROOT)

    def test_equal_numeric_lp_never_promotes_without_proof(self):
        plan=make_plan(ROOT)
        def fake_supervisor(_func,row,_root,arm,_plan,*,budget_s):
            is_c=arm.startswith('C')
            return BoundedOutcome('COMPLETED',
               {'status':'OPTIMAL_NUMERIC','lp_numeric_value':10.0,
                'instance_sha256':row['sha256'],'model_complete':True,
                'n_variables':10 if is_c else 100,
                'n_constraints':15 if is_c else 10,
                'n_nonzeros':30 if is_c else 100,
                'peak_rss_kb':100 if is_c else 200,
                'K_sha256':'hash' if arm.endswith('_K') else None,
                'K_validated':arm.endswith('_K')},
               .5 if is_c else 2.0,tuple())
        with tempfile.TemporaryDirectory() as td,patch('run_as09_pilot.run_bounded',side_effect=fake_supervisor):
            folder=Path(td)/'pilot';execute(plan,ROOT,folder)
            self.assertEqual(analyze(folder,ROOT),'PROMISING_EXPLORATORY_PROOF_REVIEW_PENDING')
            analysis=json.loads((folder/'analysis.json').read_text())
            self.assertEqual(analysis['math_gate'],'PROOF_REVIEW_REQUIRED')
            self.assertTrue(all(r['LP_equal_numeric'] for r in analysis['rows']))

if __name__=='__main__': unittest.main()
