"""Testes derivados de AS03-03/04: estimativa, abstenções e denominador."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from as02_model_a import Instance, compile_a
from as03_grouping import partition_two
from as03_planner import plan_a2, plan_a4
from as03_size import BuildBudget, decide_build, estimate_size


class TestAS03Size(unittest.TestCase):
    def setUp(self):
        self.case = Instance(('a','b','c','d','e','f'), ('a','b','c','d'),
                             ('c','d','e','f'),
                             (('a','e'),('e','b'),('b','f'),('f','a'),('d','c')),
                             1)
        self.k = (('a', 'b'), ('c',))
        self.grouping = partition_two(self.case)

    def test_as03_03_count_vars_exactly_including_overlap(self):
        estimate = estimate_size(self.case, self.grouping.blocks, k_cuts=self.k)
        n, k, a, m, h = 6, 2, 5, 4, 2
        self.assertEqual(estimate.variables, n + k * (a + n + m) + h)
        self.assertEqual(estimate.constraints, 3*k*n + m + n + len(self.k))
        compiled = compile_a(self.case, self.grouping.blocks, self.k, relax=True)
        self.assertEqual(estimate.variables, len(compiled.variables))
        self.assertEqual(estimate.constraints, len(compiled.equations))
        self.assertGreaterEqual(estimate.nonzeros_upper, compiled.n_nonzeros)

    def test_as03_03_four_group_count_matches_compiler(self):
        a4 = plan_a4(self.case, 'sample', plan_a2(self.case, 'sample'),
                     authorized_by_as05=True, k_cuts=self.k)
        estimate = a4.decision.estimate
        self.assertEqual(a4.decision.status, 'READY_FOR_BUILD')
        compiled = compile_a(self.case, a4.grouping.blocks, self.k, relax=True)
        self.assertEqual(len(compiled.variables), estimate.variables)
        self.assertEqual(len(compiled.equations), estimate.constraints)

    def test_as03_04_size_cap_retains_case_and_no_objective(self):
        arm = plan_a2(self.case, 'case-01', budget=BuildBudget(max_variables=1))
        record = arm.to_record()
        self.assertEqual(record['status'], 'NOT_BUILT_SIZE')
        self.assertEqual(record['case_name'], 'case-01')
        self.assertTrue(record['applicable'])
        self.assertIsNone(record['measured_lp'])
        self.assertIsNone(record['measured_mip'])

    def test_as03_04_memory_proxy_not_called_certified_limit(self):
        arm = plan_a2(self.case, 'case-01', budget=BuildBudget(max_memory_bytes=1))
        self.assertEqual(arm.decision.status, 'NOT_BUILT_MEMORY')
        self.assertIn('heuristic', arm.decision.estimate.memory_estimator)

    def test_as03_04_budget_requires_reserve(self):
        arm = plan_a2(self.case, 'case-01', budget=BuildBudget(
            remaining_seconds=0, minimum_build_reserve_seconds=10))
        self.assertEqual(arm.decision.status, 'NOT_BUILT_BUDGET')

    def test_as03_04_not_authorized_four_keeps_case(self):
        parent = plan_a2(self.case, 'case-01')
        a4 = plan_a4(self.case, 'case-01', parent)
        self.assertEqual(a4.decision.status, 'NOT_AUTHORIZED')
        self.assertTrue(a4.decision.applicable)
        self.assertIsNone(a4.grouping)

    def test_as03_04_not_applicable_a2_with_one_origin(self):
        small = Instance(('a','b'), ('a',), ('b',), (('a','b'),), 1)
        arm = plan_a2(small, 'one-origin')
        self.assertEqual(arm.decision.status, 'NOT_APPLICABLE')
        self.assertTrue(arm.decision.applicable)
        self.assertIsNone(arm.decision.measured_lp)

    def test_as03_04_not_applicable_a4_with_three_origins(self):
        small = Instance(('a','b','c'), ('a','b','c'), ('a','b','c'),
                         (('a','b'),('b','c')), 1)
        p = plan_a2(small, 'three-origins')
        arm = plan_a4(small, 'three-origins', p, authorized_by_as05=True)
        self.assertEqual(arm.decision.status, 'NOT_APPLICABLE')
        self.assertTrue(arm.decision.applicable)

    def test_as03_04_denominator_counts_censored_rows(self):
        cases = [plan_a2(self.case, f'case-{i}', budget=BuildBudget(max_variables=i))
                 for i in (0, 1, 100000)]
        self.assertEqual(len(cases), 3)
        self.assertEqual(sum(bool(a.decision.applicable) for a in cases), 3)
        self.assertEqual(sum(a.decision.status == 'READY_FOR_BUILD' for a in cases), 1)

    def test_as03_04_rejects_invalid_budget_inputs(self):
        for kwargs in ({'max_variables': -1}, {'max_memory_bytes': -1},
                       {'remaining_seconds': -1}, {'minimum_build_reserve_seconds': float('nan')}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    BuildBudget(**kwargs)

    def test_as03_05_json_record_has_hash_policy_seed(self):
        arm = plan_a2(self.case, 'case-01', policy='balanced', seed=5)
        rec = arm.to_record()
        self.assertEqual(rec['policy'], 'balanced')
        self.assertEqual(rec['seed'], 5)
        self.assertEqual(rec['partition_hash'], arm.grouping.partition_hash)
        self.assertEqual(len(rec['blocks']), 2)
        self.assertIsNone(rec['measured_lp'])

    def test_as03_05_case_name_does_not_change_partition(self):
        x = plan_a2(self.case, 'dev-example', seed=7)
        y = plan_a2(self.case, 'evaluation-other-name', seed=7)
        self.assertEqual(x.grouping.partition_hash, y.grouping.partition_hash)
        self.assertEqual(x.grouping.blocks, y.grouping.blocks)
        self.assertNotEqual(x.decision.case_name, y.decision.case_name)

    def test_sensor_size_mutation_rejected_by_count_comparison(self):
        estimate = estimate_size(self.case, self.grouping.blocks)
        defective = estimate.variables - 1
        self.assertNotEqual(defective, len(compile_a(self.case, self.grouping.blocks).variables))


if __name__ == '__main__':
    unittest.main()
