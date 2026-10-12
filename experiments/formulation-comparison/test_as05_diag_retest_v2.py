"""AS05 DIAG V2: matching exato, integridade histórica, política A2 e reensaio."""
from __future__ import annotations

import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'experiments/alternative-formulations'))

from as02_model_a import Instance
from as04_arms import canonical_k, k_digest
from as05_diag_core import _diag_worker, _timed_k
from as05_diag_cut_fast import ExactCutValidator
from as05_diag_retest_v2 import (
    A2_POLICY, K_VALIDATOR, VIENNA_K_SHA256, W3C_K_SHA256, _verify_k_prior,
    make_retest_plan, validate_retest_plan, run_retest_stage,
    verify_retest_stage, analyze_retest,
)
from experiments.cuts.cuts import CorteInvalido, is_valid_cut
from experiments.cuts.synthetic import make_Sec59


def toy():
    S, T, V, adj, arcs, r, _ = make_Sec59(L=7)
    instance = Instance(tuple(V), tuple(S), tuple(T), tuple(arcs), int(r))
    return instance, SimpleNamespace(adj=adj, V=V, S=S, T=T, r=r, A_r=arcs,
                                     instance_sha256='sha-toy')


class Context:
    def __init__(self):
        self.phases = []
    def phase(self, name):
        self.phases.append(name)
    def require_remaining(self):
        return 100


class TestFastValidator(unittest.TestCase):
    def test_exhaustive_cuts_directed_overlaps_vs_original(self):
        rng = random.Random(20261012)
        checks = 0
        for n in (3, 4, 5, 6):
            V = [f'v{i}' for i in range(n)]
            for trial in range(20):
                m = rng.randrange(1, n + 1)
                S = rng.sample(V, m)
                T = rng.sample(V, m)
                A_r = [(u, v) for u in V for v in V if u != v and rng.random() < .38]
                fast = ExactCutValidator(S, T, A_r)
                for bits in range(1 << n):
                    Z = frozenset(V[i] for i in range(n) if bits >> i & 1)
                    self.assertEqual(fast.valid(Z), is_valid_cut(S, T, A_r, Z),
                                     (n, trial, S, T, Z))
                    checks += 1
        self.assertGreaterEqual(checks, 2000)

    def test_hall_deficiency_without_isolated_terminal(self):
        S = ['a','b','c']
        T = ['x','y','z']
        A_r = [('a','x'),('b','x'),('c','y'),('c','z')]
        fast = ExactCutValidator(S, T, A_r)
        self.assertTrue(fast.valid([]))
        self.assertTrue(is_valid_cut(S, T, A_r, []))

    def test_valid_and_invalid_cuts_cannot_be_skipped(self):
        instance, loaded = toy()
        fast = ExactCutValidator(instance.S, instance.T, instance.A_r)
        with self.assertRaises(CorteInvalido):
            fast.check_all([frozenset({'s1'})], origem='MUTATION')
        self.assertFalse(fast.valid({'s1'}))

    def test_fast_K_same_generator_and_sha(self):
        instance, loaded = toy()
        legacy, old = _timed_k(instance, loaded, Context())
        fast, new = _timed_k(instance, loaded, Context(), validator_method=K_VALIDATOR)
        self.assertEqual(fast, legacy)
        self.assertEqual(new['k_sha256'], old['k_sha256'])
        self.assertEqual(new['counts'], old['counts'])
        self.assertIn('validation_bitset_v2_s', new['phase_wall_s'])
        self.assertTrue(new['k_validated'])

    def test_fast_K_invalid_cut_still_raises(self):
        instance, loaded = toy()
        with patch('as05_diag_core.generate_C1', return_value=[frozenset({'s1'})]), \
             patch('as05_diag_core.generate_C2', return_value=[]), \
             patch('as05_diag_core.generate_C4_DM', return_value=[]):
            with self.assertRaises(CorteInvalido):
                _timed_k(instance, loaded, Context(), validator_method=K_VALIDATOR)

    def test_legacy_default_unmodified(self):
        instance, loaded = toy()
        _, result = _timed_k(instance, loaded, Context())
        self.assertEqual(result['validator_method'], 'legacy')
        self.assertIn('validation_cached_s', result['phase_wall_s'])
        self.assertNotIn('validation_bitset_v2_s', result['phase_wall_s'])


class TestRetestV2Plan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = make_retest_plan(ROOT)

    def test_plan_pins_real_source_and_explicit_policy(self):
        self.assertEqual(self.plan['K_validator'], K_VALIDATOR)
        self.assertEqual([x['arm'] for x in self.plan['arms']['censored']], ['U','U_K','A2_K'])
        self.assertEqual(self.plan['arms']['censored'][-1]['grouping_policy'], A2_POLICY)
        self.assertEqual(self.plan, validate_retest_plan(self.plan, ROOT))
        self.assertEqual(self.plan['expected_k_sha256']['vienna-I056-regiao-f4'], VIENNA_K_SHA256)
        self.assertEqual(len(self.plan['cases']['censored']), 2)
        self.assertEqual(self.plan['scientific_gate'], 'PENDING')

    def test_plan_rejects_policy_or_budget_mutation(self):
        altered = json.loads(json.dumps(self.plan))
        altered['arms']['censored'][2]['grouping_policy'] = 'reachability_overlap'
        with self.assertRaises(ValueError):
            validate_retest_plan(altered, ROOT)
        altered = json.loads(json.dumps(self.plan))
        altered['budgets_seconds_per_arm']['censored'] = 600
        with self.assertRaises(ValueError):
            validate_retest_plan(altered, ROOT)

    def test_K_sha_must_match_prior_vienna(self):
        with self.assertRaises(ValueError):
            _verify_k_prior('vienna-I056-regiao-f4', {
                'status':'PROFILED', 'cut_profile':{'k_sha256':'mutated'}}, self.plan)
        _verify_k_prior('vienna-I056-regiao-f4', {
            'status':'PROFILED', 'cut_profile':{'k_sha256':VIENNA_K_SHA256}}, self.plan)

    def test_explicit_policy_reaches_model_compiler(self):
        instance, loaded = toy()
        with patch('as05_diag_core._load_timed', return_value=(loaded, .01, .02)), \
             patch('as05_diag_core._optimize', return_value={
                 'status':'OPTIMAL_NUMERIC', 'lp_opt_value':3.0,
                 'solver_runtime_s': .01}):
            result = _diag_worker(Context(), {'nome':'toy'}, str(ROOT), 'lp',
                                  'A2_K', A2_POLICY,
                                  {'seed':42,'threads':1,'memory_limit_bytes':None},
                                  90, 1_000_000, 42, validator_method=K_VALIDATOR)
        self.assertEqual(result['status'], 'OPTIMAL_NUMERIC')
        self.assertEqual(result['cut_profile']['validator_method'], K_VALIDATOR)
        self.assertIsNotNone(result['partition_sha256'])

    def test_no_policy_fails_closed_even_with_fast_validator(self):
        instance, loaded = toy()
        with patch('as05_diag_core._load_timed', return_value=(loaded, 0, 0)):
            with self.assertRaisesRegex(ValueError, 'política não autorizada'):
                _diag_worker(Context(), {'nome':'toy'}, str(ROOT), 'lp',
                             'A2_K', None,
                             {'seed':42,'threads':1,'memory_limit_bytes':None},
                             90, 1_000_000, 42, validator_method=K_VALIDATOR)


class TestRetestV2Pipeline(unittest.TestCase):
    def _fake_run_one(self, row, *, kind, arm, group_policy, **_):
        name = row['nome'].removesuffix('.txt')
        k = (VIENNA_K_SHA256 if name.startswith('vienna') else W3C_K_SHA256)
        result = {'case_name': row['nome'], 'kind':kind, 'arm_id':arm,
                  'grouping_policy':group_policy, 'status':'PROFILED' if kind=='cuts' else 'OPTIMAL_NUMERIC',
                  'reason':'', 'wall_total_s':1.0, 'wall_phases_s':{'solve': .3},
                  'cut_profile':{'counts':{'unique':101}, 'k_sha256':k,
                                 'phase_wall_s':{'validation_bitset_v2_s':.2}},
                  'reference_k_sha256':None if arm=='U' else k,
                  'applied_k_sha256':None if arm=='U' else k,
                  'k_validated':arm!='U', 'instance_sha256':f'instance-{name}',
                  'structural_sha256':f'structural-{name}',
                  'model_complete':True, 'lp_opt_value':2 if arm=='U' else 3 if arm=='U_K' else 3.05,
                  'solver_runtime_s':.3, 'solver_version':'test',
                  'partition_sha256':'A2-partition' if arm=='A2_K' else None}
        return result

    def test_complete_two_stage_pipeline_and_append_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan_path = root/'plan.json'
            plan_path.write_text(json.dumps(make_retest_plan(ROOT)), encoding='utf-8')
            out = root/'result'
            for stage in ('cuts','censored'):
                target = out/stage
                run_retest_stage(root=ROOT, plan_path=plan_path, stage=stage,
                                 output_dir=target, run_one=self._fake_run_one)
                report = verify_retest_stage(target)
                self.assertEqual(len(report['cases']), 2)
                self.assertEqual(report['scientific_promotion'], 'NOT_AUTHORIZED')
                with self.assertRaises(FileExistsError):
                    run_retest_stage(root=ROOT, plan_path=plan_path, stage=stage,
                                     output_dir=target, run_one=self._fake_run_one)
            report = verify_retest_stage(out/'censored')
            for case in report['cases']:
                self.assertEqual(case['runs'][2]['grouping_policy'], A2_POLICY)
                self.assertEqual(case['contrasts']['A_EFFECT']['status'], 'MATCHED_COMPLETE')
            output = analyze_retest(root=ROOT, plan_path=plan_path,
                                    results_dir=out, output_dir=out/'analysis')
            self.assertTrue(output.exists())
            analysis = json.loads(output.read_text())
            self.assertEqual(analysis['recommendation'],
                             'RETEST_COMPLETE_EXPLORATORY_NO_AUTOMATIC_PROMOTION')
            self.assertEqual(analysis['scientific_gate'], 'PENDING')
            # Mutação após executar deve ser recusada.
            checkpoint = next((out/'censored'/'checkpoints').rglob('arm-*.json'))
            checkpoint.write_text(checkpoint.read_text()+'\n')
            with self.assertRaises(ValueError):
                verify_retest_stage(out/'censored')

    def test_worker_error_remains_censored_not_fake_LP(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan_path = root/'plan.json'
            plan_path.write_text(json.dumps(make_retest_plan(ROOT)), encoding='utf-8')
            def fake(row, *, arm, **kw):
                if arm == 'A2_K':
                    result = self._fake_run_one(row, arm=arm, **kw)
                    result.update(status='WORKER_ERROR', lp_opt_value=None, model_complete=False)
                    return result
                return self._fake_run_one(row, arm=arm, **kw)
            target = root/'censored'
            run_retest_stage(root=ROOT, plan_path=plan_path, stage='censored',
                             output_dir=target, run_one=fake)
            report = verify_retest_stage(target)
            self.assertTrue(all(c['contrasts']['A_EFFECT']['lp_delta'] is None for c in report['cases']))
            self.assertTrue(all(c['runs'][2]['status']=='WORKER_ERROR' for c in report['cases']))


if __name__ == '__main__':
    unittest.main()
