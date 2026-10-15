"""Acceptance-derived AS16 tests: preregistration, timing, censor, pool, gate."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import analyze_h2_lp as an
import run_h2_lp as run


class Preregister(unittest.TestCase):
    def test_six_frozen_raw_distinct_and_valid_source(self):
        plan, sha = run.load_plan()
        self.assertEqual(len(sha), 64)
        self.assertEqual(len({c['raw_graph_id'] for c in plan['cases']}), 6)
        self.assertEqual(len(run.validate_sources(plan)), 149)  # entire manifest, only six used
        self.assertEqual(plan['budget']['wall_seconds_per_arm'], 90)

    def test_changed_source_or_cut_version_fails_closed(self):
        plan, _ = run.load_plan()
        altered = deepcopy(plan)
        altered['source_versions']['experiments/cuts/h2_separator.py'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'componente congelado'):
            run.validate_sources(altered)
        altered = deepcopy(plan)
        altered['cases'][0]['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'bytes alterados'):
            run.validate_sources(altered)

    def test_output_is_append_only_and_dry_run_has_all_rows(self):
        plan, sha = run.load_plan()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'run'
            selected = {c['name'] for c in plan['cases'][:2]}
            report = run.execute(plan, sha, run.ROOT, target, selected, dry_run=True)
            self.assertEqual(report['gate'], 'INVESTIGATE')
            self.assertEqual(report['arm_rows'], 12)
            rows = json.loads((target / 'rows.json').read_text())
            self.assertEqual({r['status'] for r in rows}, {'NOT_RUN'})
            with self.assertRaises(FileExistsError):
                run.execute(plan, sha, run.ROOT, target, selected, dry_run=True)


class ArtificialResults(unittest.TestCase):
    def setUp(self):
        self.plan, sha = run.load_plan()
        self.manifest = {'plan_sha256': sha,
                         'cases': [c['name'] for c in self.plan['cases']]}
        self.rows = []
        for case in self.plan['cases']:
            for arm in (*an.ONLINE, *an.FIXED):
                # U+K stronger than U; online H2 improves U+K by 2%.
                obj = {'U': 10., 'U_K': 10.1, 'U_H2': 10.15,
                       'U_K_H2': 10.302, 'U_FIXED_H2': 10.15,
                       'U_K_FIXED_H2': 10.302}[arm]
                self.rows.append({'name': case['name'], 'raw_graph_id': case['raw_graph_id'],
                                  'instance_sha256': case['source_sha256'], 'arm_id': arm,
                                  'lp_objective': obj, 'status': 'OPTIMAL',
                                  'elapsed_wall_s': 1.3 if arm.endswith('H2') else 1.0})

    def test_gate_go_requires_two_independent_raw_graphs_and_paid_gain(self):
        report = an.analyze(self.plan, self.manifest, self.rows)
        self.assertEqual(report['gate'], 'GO')
        self.assertEqual(report['independent_raw_graphs_with_gain'], 6)
        self.assertEqual(report['independent_raw_graphs_with_paid_gain'], 6)

    def test_gate_stop_on_no_gain(self):
        for row in self.rows:
            if row['arm_id'] == 'U_K_H2':
                row['lp_objective'] = 10.1
        self.assertEqual(an.analyze(self.plan, self.manifest, self.rows)['gate'], 'STOP')

    def test_missing_result_is_censored_and_investigate(self):
        self.rows[0]['status'] = 'TIME_LIMIT'
        self.rows[0]['lp_objective'] = None
        report = an.analyze(self.plan, self.manifest, self.rows)
        self.assertEqual(report['gate'], 'INVESTIGATE')
        affected = next(x for x in report['comparisons'] if x['name'] == self.rows[0]['name'])
        self.assertIsNone(affected['U_to_U_K']['absolute_gain'])

    def test_unknown_oom_and_error_are_never_optimal(self):
        for status in ('TIME_LIMIT', 'ERROR', 'UNKNOWN', 'NOT_MEASURED_MEMORY'):
            rows = deepcopy(self.rows)
            rows[2]['status'] = status
            rows[2]['lp_objective'] = None
            self.assertEqual(an.analyze(self.plan, self.manifest, rows)['gate'], 'INVESTIGATE')

    def test_no_silent_data_tamper(self):
        self.rows[0]['instance_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            an.analyze(self.plan, self.manifest, self.rows)

    def test_untrusted_censored_value_is_rejected(self):
        self.rows[0]['status'] = 'TIME_LIMIT'
        with self.assertRaisesRegex(ValueError, 'censored objective'):
            an.analyze(self.plan, self.manifest, self.rows)

    def test_same_pool_controls_mandatory(self):
        self.rows[-1]['status'] = 'NOT_RUN'
        self.rows[-1]['lp_objective'] = None
        self.assertEqual(an.analyze(self.plan, self.manifest, self.rows)['gate'], 'INVESTIGATE')

    def test_strength_not_divide_by_zero(self):
        a = {'status': 'OPTIMAL', 'lp_objective': 0.}
        b = {'status': 'OPTIMAL', 'lp_objective': 1.}
        self.assertEqual(an.strength(a, b)['absolute_gain'], 1.)


class H2Accounting(unittest.TestCase):
    def test_distinct_status_counters_and_unexamined(self):
        report = {'supports_proposed': 8, 'supports_examined': 6,
                  'records': [{'status': x, 'unexamined_candidates': ['v1', 'v2'] if x == 'EMITTED' else []} for x in (
                      'EMITTED', 'DEGENERATE_COVER', 'DUPLICATE',
                      'NOT_VIOLATED', 'UNKNOWN_COMPLEMENT', 'NO_CUT')],
                  'cuts': [{'unexamined_candidates': ['v1', 'v2']}],
                  'status': 'CUTS_FOUND'}
        val = an.cut_accounting({'separation': report, 'h2_accepted': 1,
                                  'h2_redundant': 0})
        self.assertEqual(val['proposed'], 8)
        self.assertEqual(val['certified_complements'], 4)
        self.assertEqual(val['violated'], 3)
        self.assertEqual(val['not_tested'], 4)
        self.assertEqual(val['accepted'], 1)

    def test_h2_without_k_pays_k_preparation(self):
        # Mock IO/solver; genuine AS14 physical object is still constructed.
        loaded = SimpleNamespace(V=('a', 'b'), S=('a',), T=('b',), r=1,
            A_r=(('a', 'b'), ('b', 'a')),
            adj={'a': [('b', 1.0)], 'b': [('a', 1.0)]}, instance_sha256='a'*64)
        case = {'name': 'fake', 'source_sha256': 'a'*64}
        fake_model = SimpleNamespace(NumVars=4, NumConstrs=3)
        fake_compiled = SimpleNamespace(variables=[1, 2])
        config = {'max_variables': 100, 'separator_budget_s': 2.,
                  'max_supports': 1, 'max_pairs': 0, 'max_oracle_calls': 2,
                  'max_candidates_per_support': 2, 'max_cuts': 1,
                  'min_violation': 1e-7, 'per_support_budget_s': 1.}
        first = {'status': 'OPTIMAL', 'lp_objective': 0.4,
                 'y_star': {'a': 0.2, 'b': 0.2}, 'solver_wall_s': 0.01}
        fake_report = SimpleNamespace(to_dict=lambda: {'status': 'NO_CUT',
                            'records': [], 'cuts': [], 'supports_proposed': 1}, cuts=())
        with patch.object(run, 'load_instance', return_value=loaded), \
             patch.object(run, 'prepare_K', return_value=[frozenset(('a',))]) as k, \
             patch.object(run, 'compile_u', return_value=fake_compiled) as compiler, \
             patch.object(run, '_solver', return_value=(fake_model, {}, None)), \
             patch.object(run, '_optimize', return_value=first), \
             patch.object(run, 'separate_h2', return_value=fake_report), \
             patch.object(run, 'select_supports', return_value=()):
            out = run._work_arm(case, {}, run.ROOT, 'U_H2', {}, config,
                                run.time.monotonic() + 5.)
        self.assertEqual(out['status'], 'OPTIMAL')
        self.assertEqual(out['applied_k_count'], 0)
        self.assertEqual(out['prepared_k_count'], 1)
        self.assertIn('k_preparation_s', out['timings'])
        compiler.assert_called_once()
        self.assertEqual(compiler.call_args.kwargs, {'relax': True})
        self.assertEqual(compiler.call_args.args[1], ())
        k.assert_called_once()


    def test_fixed_pool_applies_same_cut_even_when_not_violated(self):
        loaded = SimpleNamespace(V=('a', 'b'), S=('a',), T=('b',), r=1,
            A_r=(('a', 'b'), ('b', 'a')),
            adj={'a': [('b', 1.)], 'b': [('a', 1.)]}, instance_sha256='a' * 64)
        from h2_oracle import PhysicalInstance
        fingerprint = PhysicalInstance(('a','b'),('a',),('b',),
            {'a': [('b', 1)], 'b': [('a', 1)]},1).fingerprint
        case = {'name': 'fake', 'source_sha256': 'a' * 64}
        cut = {'instance_sha256': fingerprint, 'rhs': 2,
               'cut_hash': 'f' * 64, 'coefficients': [['a', 2], ['b', 2]]}
        pool = {'instance_sha256': fingerprint, 'cuts': [cut]}
        config = {'max_variables': 10, 'min_violation': 1e-7}
        optimum = {'status': 'OPTIMAL', 'lp_objective': 2.,
                   'y_star': {'a': 0.6, 'b': 0.6}}
        model = SimpleNamespace(NumVars=2, NumConstrs=2, update=lambda: None)
        with patch.object(run, 'load_instance', return_value=loaded), \
             patch.object(run, 'prepare_K', return_value=[]), \
             patch.object(run, 'compile_u', return_value=SimpleNamespace(variables=[1,2])), \
             patch.object(run, '_solver', return_value=(model, {}, None)), \
             patch.object(run, '_optimize', return_value=optimum), \
             patch.object(run, '_add_cut') as inserted:
            result = run._work_arm(case, {}, run.ROOT, 'U_FIXED_H2', {}, config,
                                   run.time.monotonic() + 3, pool=pool)
        self.assertEqual(result['h2_redundant'], 1)
        self.assertEqual(result['h2_accepted'], 1)
        inserted.assert_called_once()

    def test_expired_budget_never_solves(self):
        with self.assertRaises(TimeoutError):
            run._work_arm({}, {}, run.ROOT, 'U', {}, {},
                          run.time.monotonic() - 0.1)


if __name__ == '__main__':
    unittest.main()
