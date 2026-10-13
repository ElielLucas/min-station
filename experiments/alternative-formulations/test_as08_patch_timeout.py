"""AS08 hotfix: nomes compactos, progresso antes do timeout e integridade."""
from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# unittest discover with -s alternative-formulations does not add sibling directories.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FC_DIR = _PROJECT_ROOT / 'experiments' / 'formulation-comparison'
if str(_FC_DIR) not in sys.path:
    sys.path.insert(0, str(_FC_DIR))

from as02_model_a import Instance
from as08_column_generation import CGConfig, compile_rmp, run_column_generation
from fc_budget import BoundedOutcome, run_bounded
from run_as08_b_pilot import execute, make_plan, verify
from run_as08_t2a import FIXTURES, build_fixture


def _emit_then_sleep(ctx):
    ctx.phase('solve')
    ctx.progress({'schema':'AS08-CG-PROGRESS-v1','event':'RMP_SOLVED',
                  'elapsed_seconds':ctx.elapsed(),'iteration':1,
                  'rmp_objective_with_artificials':999.0,
                  'certified_global_lb':None})
    time.sleep(5)
    return 'unexpected'


class TestAS08Hotfix(unittest.TestCase):
    def test_long_paths_have_short_names_preserving_full_keys(self):
        n=142
        V=tuple(f'v{i:04}' for i in range(n))
        P=V
        self.assertGreater(len('x['+'/'.join(P)+']'),255)
        ins=Instance(V,(V[0],),(V[-1],),tuple(zip(V,V[1:])),1)
        compiled,_=compile_rmp(ins,[],[P])
        self.assertIn(('x',P),compiled.columns)
        self.assertEqual(compiled.variables[compiled.columns['x',P]].name,'x[0]')
        self.assertTrue(all(len(v.name)<255 for v in compiled.variables))
        self.assertEqual(len([k for k in compiled.columns if k[0]=='x']),1)

    def test_column_names_deterministic_under_shuffled_input(self):
        ins,_=build_fixture(FIXTURES[0])
        A=(('a','c'),('b','c'),('a','c','d'))
        first,_=compile_rmp(ins,[],A)
        second,_=compile_rmp(ins,[],reversed(A))
        self.assertEqual({k:first.variables[v].name for k,v in first.columns.items() if k[0]=='x'},
                         {k:second.variables[v].name for k,v in second.columns.items() if k[0]=='x'})

    def test_pricing_reports_progress_without_false_lb(self):
        ins,_=build_fixture(FIXTURES[0])
        events=[]
        result=run_column_generation(ins,config=CGConfig(seconds=10,iterations=20),
                                     progress=events.append)
        self.assertEqual(result['status'],'CONVERGED')
        self.assertEqual(events[0]['event'],'CG_STARTED')
        self.assertEqual(events[-1]['event'],'CG_FINISHED')
        self.assertTrue(any(x['event']=='RMP_SOLVED' for x in events))
        self.assertTrue(any(x['event']=='ITERATION_COMPLETE' for x in events))
        for event in events:
            self.assertNotIn('global_lower_bound',event)  # RMP não é LB
        self.assertIsNotNone(result['global_lower_bound'])

    def test_supervisor_keeps_progress_from_killed_worker(self):
        events=[]
        outcome=run_bounded(_emit_then_sleep,budget_s=2.5,on_progress=events.append)
        self.assertEqual(outcome.status,'TIMEOUT_SOLVER')
        self.assertIsNone(outcome.value)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['event'],'RMP_SOLVED')
        self.assertIsNone(events[0]['certified_global_lb'])

    def test_timeout_sidecar_and_manifest_integrity(self):
        root=Path(__file__).resolve().parents[2]
        plan=make_plan(root)

        def fake_bounded(func,row,workdir,arm,plan,budget_s,on_progress=None):
            if arm=='B_K':
                on_progress({'schema':'AS08-CG-PROGRESS-v1','event':'INPUT_READY',
                             'elapsed_seconds':1.0})
                on_progress({'schema':'AS08-CG-PROGRESS-v1','event':'RMP_SOLVED',
                             'iteration':1,'elapsed_seconds':4.0,
                             'rmp_objective_with_artificials':999.0,
                             'certified_global_lb':None})
                return BoundedOutcome('TIMEOUT_SOLVER',None,300.0,(('solve',299.0),),
                                      'Supervisão encerrou o worker')
            return BoundedOutcome('COMPLETED',
                      {'status':'OPTIMAL_NUMERIC','lp_numeric_value':1.0,
                       'global_lower_bound':None,'k_validated':True,
                       'K_sha256':'test-fixture','instance_sha256':row['sha256']},3.0,(('solve',2.0),),'')

        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            with patch('run_as08_b_pilot.run_bounded',fake_bounded):
                results=execute(plan,root,output)
            self.assertEqual(len(results),12)
            first=plan['cases'][0]['name']
            b=json.loads((output/f'{first}--B_K.json').read_text())
            self.assertEqual(b['status'],'TIMEOUT_SOLVER')
            self.assertIsNone(b['lp_numeric_value'])
            self.assertIsNone(b['global_lower_bound'])
            self.assertEqual(b['cg_progress_checkpoint']['events'],2)
            self.assertIsNone(b['cg_progress_checkpoint']['last_event']['certified_global_lb'])
            self.assertEqual(len(verify(output,root)),12)
            sidecar=output/f'{first}--B_K.cg-progress.json'
            payload=json.loads(sidecar.read_text())
            payload['events'][1]['rmp_objective_with_artificials']=1001.0
            sidecar.write_text(json.dumps(payload)+'\n')
            with self.assertRaisesRegex(ValueError,'manifest'):
                verify(output,root)


if __name__=='__main__':
    unittest.main()
