"""Testa a via exploratoria autorizada pelo responsavel e o bloqueio cientifico."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
for location in (HERE, ROOT, ROOT / 'experiments/formulation-comparison',
                 ROOT / 'experiments/alternative-formulations'):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from as05_owner_authorization import verify_owner_authorization  # noqa: E402
from as05_protocol import make_plan, plan_digest, sha256_file  # noqa: E402
from as05_pilot import run_pilot, verify_pilot, verify_preconditions  # noqa: E402
from test_as05_pilot import result_for  # noqa: E402


def _plan():
    protocol = json.loads((ROOT / 'results/benchmark/protocol.json').read_text(encoding='utf-8'))
    return make_plan(protocol,
                     as00_sha256=sha256_file(ROOT / 'results/benchmark/protocol.json'),
                     manifest_sha256=sha256_file(ROOT / 'instances/manifest.csv'))


def _owner_auth(plan):
    return {'schema': 'AS05-OWNER-AUTHORIZATION-v1',
            'authorization_type': 'OWNER_APPROVED_EXPLORATORY',
            'authorized_by_owner': True,
            'scope': 'AS05_DEVELOPMENT_LP_ONLY',
            'independent_review_claimed': False,
            'plan_sha256': plan_digest(plan),
            'basis': 'Autorizacao expressa do responsavel'}


class TestAS05OwnerAuthorization(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.plan = _plan()
        self.plan_path = self.folder / 'plan.json'
        self.plan_path.write_text(json.dumps(self.plan), encoding='utf-8')
        self.auth_path = self.folder / 'owner.json'
        self.auth_path.write_text(json.dumps(_owner_auth(self.plan)), encoding='utf-8')
        self.pending_path = self.folder / 'pending.json'
        self.pending_path.write_text(json.dumps({
            'as04_verdict': 'PENDING',
            'as02_evidence': {'as01_verdict': 'PENDING',
                              'as01_independent_reviewer': False,
                              'physical_exhaustion_passed': False,
                              'sec59_lp_passed': False,
                              'math_counterexample': False,
                              'as02_independent_reviewer': False},
            'reviewers': {name: {'author': '', 'reviewer': '', 'evidence_path': ''}
                          for name in ('as01', 'as02', 'as04')}
        }), encoding='utf-8')

    def test_strict_gate_still_blocks(self):
        with self.assertRaisesRegex(RuntimeError, 'AS04 nao homologada|AS04 não homologada'):
            verify_preconditions(json.loads(self.pending_path.read_text()))
        called = Mock(side_effect=AssertionError('solver nao pode ser chamado'))
        with self.assertRaisesRegex(RuntimeError, 'AS05_BLOCKED'):
            run_pilot(root=ROOT, plan_path=self.plan_path, evidence_path=self.pending_path,
                      output_dir=self.folder/'strict', run_case_fn=called)
        called.assert_not_called()

    def test_owner_mode_6x3_and_no_scientific_go(self):
        by_name = {c['manifest_name']: c for c in self.plan['pilot_cases']}
        calls = []

        def runner(row, **kw):
            self.assertTrue(kw['owner_exploratory'])
            self.assertEqual(kw['mode'], 'LP')
            self.assertEqual(kw['grouping_seed'], self.plan['policy']['grouping_seed'])
            calls.append(kw['arm_ids'])
            return result_for(by_name[row['nome']], seed=kw['policy'].seed,
                              selected=kw['arm_ids'])

        dest = self.folder/'owner-run'
        run_pilot(root=ROOT, plan_path=self.plan_path, evidence_path=self.pending_path,
                  output_dir=dest, owner_authorization_path=self.auth_path,
                  run_case_fn=runner, run_arm_fn=Mock(side_effect=RuntimeError('A4 OFF')))
        report = verify_pilot(dest)
        self.assertEqual(report['execution_class'], 'OWNER_AUTHORIZED_EXPLORATORY')
        self.assertEqual(report['scientific_homologation'], 'PENDING')
        self.assertEqual(report['screening_decision']['verdict'], 'GO')
        self.assertEqual(report['decision']['verdict'], 'INVESTIGATE')
        self.assertEqual(len(report['cases']), 6)
        self.assertEqual(len(list((dest/'cases').glob('*/arms.csv'))), 6)
        self.assertEqual(len([c for c in calls if c == ('U', 'U_K', 'A2_K')]), 6)
        self.assertEqual(report['owner_authorization_sha256'], sha256_file(dest/'owner-authorization.json'))

    def test_refuse_modified_hash_or_false_independent_review(self):
        for field, value in [('plan_sha256', '0'*64), ('independent_review_claimed', True),
                             ('scope', 'AS06_MIP'), ('authorized_by_owner', False)]:
            with self.subTest(field=field):
                a = copy.deepcopy(_owner_auth(self.plan))
                a[field] = value
                with self.assertRaisesRegex(RuntimeError, 'AS05_OWNER_BLOCKED'):
                    verify_owner_authorization(a, self.plan)

    def test_no_solver_when_owner_auth_is_invalid(self):
        a = _owner_auth(self.plan)
        a['authorization_type'] = 'FAKE'
        self.auth_path.write_text(json.dumps(a))
        called = Mock(side_effect=AssertionError('NAO EXECUTAR'))
        with self.assertRaisesRegex(RuntimeError, 'AS05_OWNER_BLOCKED'):
            run_pilot(root=ROOT, plan_path=self.plan_path, evidence_path=self.pending_path,
                      output_dir=self.folder/'invalid', owner_authorization_path=self.auth_path,
                      run_case_fn=called)
        called.assert_not_called()
        self.assertFalse((self.folder/'invalid').exists())

    def test_owner_auth_is_bound_to_canonical_plan(self):
        self.assertEqual(plan_digest(self.plan),
                         '193a0fb1812c10e502d2e086d9dc2e1f857b724046955bbb0684ad99c038ef3b')
        verify_owner_authorization(_owner_auth(self.plan), self.plan)


if __name__ == '__main__':
    unittest.main()
