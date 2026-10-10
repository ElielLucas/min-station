"""FC-01: testes independentes do deadline/worker SEM dependência de Gurobi.

Executar: python -m unittest discover -s experiments/formulation-comparison
             -p test_fc01_budget.py -v
"""
from __future__ import annotations

import math
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fc_budget import BudgetExpired, WallBudget, run_bounded  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def _quick_job(ctx):
    ctx.phase('k_preparation')
    ctx.phase('model_build')
    ctx.phase('solve')
    ctx.require_remaining()
    ctx.phase('validation')
    return {'lp': 2}


def _slow_preparation(ctx):
    ctx.phase('k_preparation')
    ctx.phase('model_build')
    time.sleep(5.0)  # não verifica ctx.remaining() de propósito
    ctx.phase('solve')
    raise AssertionError('Solver NÃO pode iniciar após timeout de montagem')


def _slow_solver(ctx):
    ctx.phase('model_build')
    ctx.phase('solve')
    time.sleep(5.0)
    return {'objective': 11.0}


def _slow_validation(ctx):
    ctx.phase('solve')
    ctx.phase('validation')
    time.sleep(5.0)
    return {'validated': True}


def _raises_error(ctx):
    ctx.phase('model_build')
    raise ValueError('falha proposital de montagem')


class GurobiError(Exception):
    pass


def _no_solver_license(ctx):
    ctx.phase('model_build')
    raise GurobiError('License expired')


def _raises_cap(ctx):
    class CapExceeded(Exception):
        pass
    ctx.phase('model_build')
    time.sleep(0.05)
    raise CapExceeded('cap máximo: 1')


class WallBudgetTests(unittest.TestCase):
    def test_remaining_is_absolute_and_not_reset(self):
        clock = FakeClock()
        b = WallBudget(60.0, clock=clock)
        self.assertEqual(b.remaining(), 60.0)
        clock.now = 155.0
        self.assertEqual(b.remaining(), 5.0)
        clock.now = 161.0
        self.assertEqual(b.remaining(), 0.0)
        with self.assertRaises(BudgetExpired):
            b.require_remaining()

    def test_rejects_nonpositive_nan_infinity(self):
        for value in (0, -1, float('nan'), math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                WallBudget(value)


class SupervisorTests(unittest.TestCase):
    def test_success_reports_phases_without_solver_requirement(self):
        r = run_bounded(_quick_job, budget_s=3.0)
        self.assertEqual(r.status, 'COMPLETED', r.reason)
        self.assertEqual(r.value, {'lp': 2})
        self.assertGreater(r.wall_total_s, 0.0)
        phases = dict(r.phase_wall_s)
        self.assertIn('model_build', phases)
        self.assertIn('solve', phases)
        self.assertIn('validation', phases)
        self.assertAlmostEqual(sum(phases.values()), r.wall_total_s, delta=0.1)

    def test_preparation_timeout_kills_worker_and_no_objective(self):
        r = run_bounded(_slow_preparation, budget_s=2.0)
        self.assertEqual(r.status, 'TIMEOUT_PREPARATION', r.reason)
        self.assertIsNone(r.value)
        self.assertIn('Prazo', r.reason)
        self.assertGreater(r.wall_total_s, 0.0)

    def test_solver_timeout_discards_partial_value(self):
        r = run_bounded(_slow_solver, budget_s=2.0)
        self.assertEqual(r.status, 'TIMEOUT_SOLVER', r.reason)
        self.assertIsNone(r.value)
        self.assertGreater(dict(r.phase_wall_s)['solve'], 0.0)

    def test_validation_time_counts_against_deadline(self):
        r = run_bounded(_slow_validation, budget_s=2.0)
        self.assertEqual(r.status, 'TIMEOUT_VALIDATION', r.reason)
        self.assertIsNone(r.value)

    def test_failure_has_diagnostic_and_no_result(self):
        r = run_bounded(_raises_error, budget_s=3.0)
        self.assertEqual(r.status, 'WORKER_ERROR')
        self.assertIn('falha proposital', r.reason)
        self.assertIsNone(r.value)

    def test_cap_has_measurable_cost_and_no_result(self):
        r = run_bounded(_raises_cap, budget_s=3.0)
        self.assertEqual(r.status, 'CAP_EXCEEDED', r.reason)
        self.assertIn('cap máximo', r.reason)
        self.assertIsNone(r.value)
        self.assertGreater(r.wall_total_s, 0.0)
        self.assertGreater(dict(r.phase_wall_s).get('model_build', 0.0), 0.0)

    def test_missing_solver_license_is_explicit(self):
        r = run_bounded(_no_solver_license, budget_s=3.0)
        self.assertEqual(r.status, 'SOLVER_UNAVAILABLE')
        self.assertIsNone(r.value)
        self.assertIn('License expired', r.reason)

    def test_deadline_expired_in_worker_before_solve(self):
        r = run_bounded(_quick_job, budget_s=0.000001)
        self.assertEqual(r.status, 'TIMEOUT_PREPARATION')
        self.assertIsNone(r.value)


if __name__ == '__main__':
    unittest.main()
