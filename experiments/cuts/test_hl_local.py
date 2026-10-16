"""AS19 behavioral and negative testing for independent bounded HL pilot."""
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h2_oracle import MatchingOracle, PhysicalInstance
from h2_oracle_schema import Status
from hl_local import HLOptions, separate_hl
from verify_as13_foundations import k4, reach_arcs, k_cuts, solve_comp_lp, h2_for_support
from independent_validator import viavel


class TestHLLocal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.W = k4()
        cls.physical = PhysicalInstance.from_tuple(cls.raw)
        cls.S, cls.T, cls.V, cls.adj, cls.r = cls.raw
        cls.y = {v: (2. / 3. if v in cls.W else 0.) for v in cls.V}
        cls.options = HLOptions(max_support_size=4, max_oracle_calls=40,
                                total_budget_s=30, per_support_budget_s=15)

    def evaluate(self, **kwargs):
        return separate_hl(self.physical, self.y, supports=[self.W],
                           options=self.options, **kwargs)

    def test_four_relay_exact_cut_and_h2_residual(self):
        result = self.evaluate()
        self.assertEqual(result.status, 'CUTS_FOUND')
        self.assertEqual(len(result.cuts), 1)
        cut = result.cuts[0]
        self.assertEqual(cut.rhs, Fraction(3))
        self.assertEqual(dict(cut.coefficients), {v: Fraction(1) for v in self.W})
        self.assertAlmostEqual(cut.violation, 1 / 3)
        self.assertEqual(result.records[0]['patterns_examined'], 16)
        self.assertEqual(result.oracle_calls, 16)  # complement + remaining 15 patterns
        for installed_size in range(len(self.V) + 1):
            for subset in combinations(self.V, installed_size):
                if viavel(self.S, self.T, self.V, self.adj, self.r, subset):
                    self.assertGreaterEqual(sum(v in subset for v in self.W), cut.rhs)

    def test_comp_k_h2_hl_lp_hierarchy_from_actual_models(self):
        arcs = reach_arcs(self.V, self.adj, self.r)
        K = k_cuts(self.S, self.T, self.V, self.adj, self.r, arcs)
        base, y, _ = solve_comp_lp(self.S, self.T, self.V, arcs, K)
        self.assertAlmostEqual(base, 2)
        self.assertTrue(all(abs(y[v] - 0.5) < 1e-7 for v in self.W))
        h2 = []
        for missing in self.W:
            row = h2_for_support(self.S, self.T, self.V, self.adj, self.r,
                                 [v for v in self.W if v != missing])
            self.assertIsNotNone(row)
            h2.append(row[:2])
        middle, fractional, _ = solve_comp_lp(self.S, self.T, self.V, arcs, K, more=h2)
        self.assertAlmostEqual(middle, 8 / 3)
        cut = self.evaluate().cuts[0]
        best, _, _ = solve_comp_lp(self.S, self.T, self.V, arcs, K,
                                   more=[*h2, (dict(cut.coefficients), cut.rhs)])
        self.assertAlmostEqual(best, 3)
        self.assertAlmostEqual(sum(fractional[v] for v in self.W), 8 / 3)

    def test_viable_complement_short_circuits_no_enumeration(self):
        y = {v: 0 for v in self.V}
        out = separate_hl(self.physical, y, supports=[(self.W[0],)], options=self.options)
        self.assertEqual(out.cuts, ())
        self.assertEqual(out.oracle_calls, 1)
        self.assertEqual(out.records[0]['reason'], 'COMPLEMENT_VIABLE')

    def test_unknown_pattern_always_abstains(self):
        class UnknownOracle(MatchingOracle):
            def check(self, instance, allowed_stations, budget_s=None):
                result = super().check(instance, allowed_stations, budget_s=budget_s)
                if frozenset(allowed_stations) == frozenset(set(instance.V) - set(self_W) | {self_W[0]}):
                    return replace(result, status=Status.UNKNOWN, matching_size=None,
                                   witness=(), hall_origins=(), hall_destinations=(), reason='INJECTED')
                return result
        self_W = self.W
        out = self.evaluate(oracle=UnknownOracle())
        self.assertFalse(out.cuts)
        self.assertEqual(out.records[0]['status'], 'ABSTAIN')
        self.assertLess(out.records[0]['patterns_examined'], 16)

    def test_budget_limits_abstain_instead_of_weak_certificate(self):
        from dataclasses import replace
        options = replace(self.options, max_oracle_calls=3)
        out = separate_hl(self.physical, self.y, supports=[self.W], options=options)
        self.assertEqual(out.cuts, ())
        self.assertEqual(out.oracle_calls, 3)
        self.assertEqual(out.records[0]['reason'], 'UNKNOWN_OR_INCOMPLETE_PATTERN')
        zero = separate_hl(self.physical, self.y, supports=[self.W],
                           options=replace(self.options, total_budget_s=0))
        self.assertEqual(zero.cuts, ())
        self.assertEqual(zero.status, 'PARTIAL_BUDGET')

    def test_support_cap_and_validation(self):
        out = separate_hl(self.physical, self.y, supports=[self.W],
                          options=replace(self.options, max_support_size=3))
        self.assertEqual(out.oracle_calls, 0)
        self.assertEqual(out.records[0]['status'], 'SKIPPED_SIZE')
        with self.assertRaises(ValueError):
            self.evaluate(alpha={v: 1 for v in self.W[:-1]})
        with self.assertRaises(ValueError):
            self.evaluate(alpha={v: -1 for v in self.W})
        with self.assertRaises(ValueError):
            self.evaluate(alpha={v: float('nan') for v in self.W})
        with self.assertRaises(ValueError):
            separate_hl(self.physical, self.y, supports=[('unknown',)], options=self.options)
        with self.assertRaises(ValueError):
            HLOptions(max_support_size=0)

    def test_rationalization_and_beta_are_exact(self):
        alpha = {v: (0.5 if v == self.W[0] else 1) for v in self.W}
        out = self.evaluate(alpha=alpha)
        cut, = out.cuts
        self.assertEqual(dict(cut.coefficients)[self.W[0]], Fraction(1, 2))
        self.assertEqual(cut.rhs, Fraction(5, 2))
        self.assertAlmostEqual(cut.violation, 1 / 6)

    def test_hash_stability_and_append_only(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first.cuts[0].cut_hash, second.cuts[0].cut_hash)
        self.assertEqual(first.cuts[0].certificate_sha256, second.cuts[0].certificate_sha256)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'pilot.json'
            first.save_new(path)
            with self.assertRaises(FileExistsError):
                second.save_new(path)

    def test_no_cut_for_already_integral_solution(self):
        y = {v: float(v in self.W[:3]) for v in self.V}
        out = separate_hl(self.physical, y, supports=[self.W], options=self.options)
        self.assertFalse(out.cuts)
        self.assertEqual(out.records[0]['status'], 'NOT_VIOLATED')


if __name__ == '__main__':
    unittest.main()
