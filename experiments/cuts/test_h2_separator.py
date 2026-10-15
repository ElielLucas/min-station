"""AS15 acceptance tests: independent physical truth, HB LP and negative cases."""
from __future__ import annotations

import json
import math
import random
import tempfile
import unittest
from dataclasses import replace
from itertools import combinations
from pathlib import Path

from h2_cut import H2Cut
from h2_oracle import MatchingOracle, PhysicalInstance
from h2_oracle_schema import Status, order_vertices
from h2_separator import SeparatorOptions, separate_h2
from h2_supports import select_supports
from independent_validator import viavel


def physical(V, S, T, edges, r=1):
    adj = {v: [] for v in V}
    for a, b in edges:
        adj[a].append((b, 1))
        adj[b].append((a, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def all_subsets(V):
    for k in range(len(V) + 1):
        yield from combinations(V, k)


def battery_viable(i, stations):
    return viavel(i.S, i.T, i.V, i.adj, i.r, stations)


def physical_h2(i, R):
    """Exact physical definition, NOT calling the oracle under test."""
    F = set(i.V) - set(R)
    if battery_viable(i, F):
        return None
    bhat = {v for v in R if not battery_viable(i, F | {v})}
    return {v: (1 if v in bhat else 2) for v in R}


class AS15SeparatorTests(unittest.TestCase):
    def setUp(self):
        self.path = physical('abc', 'a', 'c', [('a', 'b'), ('b', 'c')])
        self.y = {'a': .4, 'b': .2, 'c': .4}
        self.no_budget = SeparatorOptions(total_budget_s=None,
                                          per_support_budget_s=None,
                                          max_supports=128, max_cuts=128)

    def test_as15_01_viable_complement_never_emits_h2(self):
        # R={a}: F={b,c}; b is installed and is sufficient.
        r = separate_h2(self.path, {'a': 0., 'b': 1., 'c': 0.},
                        proposed_supports=[('a',)], options=self.no_budget)
        self.assertEqual(r.cuts, ())
        self.assertEqual(r.records[0]['status'], 'NO_CUT')
        self.assertEqual(r.records[0]['reason'], 'COMPLEMENT_VIABLE')

    def test_as15_02_03_exact_bhat_coefficients_rhs_and_physical_validity(self):
        r = separate_h2(self.path, self.y, proposed_supports=[('a','b','c')],
                        options=self.no_budget)
        self.assertEqual(len(r.cuts), 1)
        cut = r.cuts[0]
        self.assertEqual(cut.bhat, ('a', 'c'))
        self.assertEqual(cut.coefficients, (('a', 1), ('b', 2), ('c', 1)))
        self.assertEqual(cut.rhs, 2)
        self.assertAlmostEqual(cut.violation, .8)
        self.assertEqual(len(cut.certificate_hashes), 3)  # complement + two Bhat witnesses
        for stations in all_subsets(self.path.V):
            if battery_viable(self.path, stations):
                self.assertGreaterEqual(sum(coef for v, coef in cut.coefficients if v in stations), 2)

    def test_as15_02_partial_classification_is_conservative(self):
        # Only 'a' may be examined; both 'b' and 'c' remain coefficient 2.
        opt = replace(self.no_budget, max_candidates_per_support=1)
        r = separate_h2(self.path, {'a': 0.7, 'b': 0.1, 'c': 0.2},
                        proposed_supports=[self.path.V], options=opt)
        cut, = r.cuts
        self.assertEqual(cut.coefficients, (('a', 1), ('b', 2), ('c', 2)))
        self.assertEqual(cut.unexamined_candidates, ('b','c'))
        self.assertEqual(cut.unknown_candidates, ())

    def test_as15_04_strict_violation_threshold(self):
        # The exact H2 row for V is y_a + 2*y_b + y_c >= 2.
        y = {'a': 0.5, 'b': 0.5, 'c': 0.5}
        for tol in (0., 1e-7, 1.):
            r = separate_h2(self.path, y, proposed_supports=[self.path.V],
                            options=replace(self.no_budget, min_violation=tol))
            self.assertEqual(r.cuts, ())
            self.assertEqual(r.records[0]['status'], 'NOT_VIOLATED')
        violated = separate_h2(self.path, self.y, proposed_supports=[self.path.V],
                               options=replace(self.no_budget, min_violation=.799999))
        self.assertEqual(len(violated.cuts), 1)
        not_violated = separate_h2(self.path, self.y, proposed_supports=[self.path.V],
                                  options=replace(self.no_budget, min_violation=.8))
        self.assertEqual(not_violated.cuts, ())

    def test_as15_04_exact_violation_tolerance_boundary(self):
        # y_a=.5, y_b=.5, y_c=0 gives exact violation .5.
        y = {'a': .5, 'b': .5, 'c': 0.}
        report = separate_h2(self.path, y, proposed_supports=[self.path.V],
                             options=replace(self.no_budget, min_violation=.5))
        self.assertEqual(report.cuts, ())
        self.assertEqual(report.records[0]['status'], 'NOT_VIOLATED')

    def test_as15_05_mass_boundary_two(self):
        y = {'a': 1., 'b': 1., 'c': 0.}
        result = separate_h2(self.path, y, proposed_supports=[self.path.V],
                             options=self.no_budget)
        self.assertEqual(result.oracle_calls, 0)
        self.assertEqual(result.records[0]['status'], 'FILTERED_MASS')

    def test_as15_05_mass_ge_two_prevents_any_oracle_calls(self):
        result = separate_h2(self.path, {'a': 1., 'b': 1., 'c': 1.},
                             proposed_supports=[self.path.V], options=self.no_budget)
        self.assertEqual(result.oracle_calls, 0)
        self.assertEqual(result.records[0]['status'], 'FILTERED_MASS')

    def test_as15_06_unknown_complement_abstains(self):
        r = separate_h2(self.path, self.y, proposed_supports=[self.path.V],
                        options=replace(self.no_budget, per_support_budget_s=0))
        self.assertEqual(r.cuts, ())
        self.assertEqual(r.records[0]['status'], 'UNKNOWN_COMPLEMENT')

    def test_as15_06_unknown_candidate_never_enters_bhat(self):
        class UncertainMatching(MatchingOracle):
            def check(self, instance, allowed_stations, budget_s=None):
                r = super().check(instance, allowed_stations, budget_s=budget_s)
                if frozenset(allowed_stations) == {'a'}:
                    return replace(r, status=Status.UNKNOWN, matching_size=None,
                                   witness=(), hall_origins=(), hall_destinations=(),
                                   reason='FORCED_UNKNOWN')
                return r

        r = separate_h2(self.path, self.y, oracle=UncertainMatching(),
                        proposed_supports=[self.path.V], options=self.no_budget)
        cut, = r.cuts
        self.assertEqual(cut.unknown_candidates, ('a',))
        self.assertNotIn('a', cut.bhat)
        self.assertEqual(dict(cut.coefficients)['a'], 2)
        for stations in all_subsets(self.path.V):
            if battery_viable(self.path, stations):
                self.assertGreaterEqual(sum(coef for v, coef in cut.coefficients if v in stations), 2)

    def test_as15_06_budget_limits_unknowns_and_global_calls(self):
        r = separate_h2(self.path, self.y, proposed_supports=[self.path.V],
                        options=replace(self.no_budget, max_oracle_calls=2))
        self.assertEqual(r.oracle_calls, 2)
        self.assertEqual(len(r.cuts), 1)
        self.assertEqual(len(r.cuts[0].unexamined_candidates), 2)
        no_calls = separate_h2(self.path, self.y, proposed_supports=[self.path.V],
                               options=replace(self.no_budget, max_oracle_calls=0))
        self.assertEqual(no_calls.oracle_calls, 0)
        self.assertEqual(no_calls.status, 'BUDGET_EXHAUSTED')
        self.assertEqual(no_calls.cuts, ())

    def test_as15_07_report_hash_reproducibility_and_append_only(self):
        opt = self.no_budget
        first = separate_h2(self.path, self.y, proposed_supports=[self.path.V], options=opt)
        second = separate_h2(self.path, self.y, proposed_supports=[self.path.V], options=opt)
        a, = first.cuts
        b, = second.cuts
        self.assertEqual((a.cut_hash, a.certificate_sha256, a.certificate_hashes),
                         (b.cut_hash, b.certificate_sha256, b.certificate_hashes))
        data = first.to_dict()
        self.assertEqual(data['stage'], 'AS15')
        self.assertEqual(data['instance_sha256'], self.path.fingerprint)
        self.assertEqual(data['cuts'][0]['certificate_sha256'], a.certificate_sha256)
        self.assertEqual(data['cuts'][0]['violation'], a.violation)
        self.assertEqual(data['cuts'][0]['oracle_calls'], a.oracle_calls)
        self.assertIn('elapsed_wall_s', data['cuts'][0])
        self.assertNotIn('source_commit', data)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'as15-result.json'
            first.save_new(path)
            self.assertEqual(json.loads(path.read_text())['cuts_emitted'], 1)
            with self.assertRaises(FileExistsError):
                second.save_new(path)

    def test_as15_07_all_input_orders_deduplicated_deterministically(self):
        options = self.no_budget
        inputs = [('b','a','c'), ('c','b','a'), ('a','b','c')]
        a = separate_h2(self.path, self.y, proposed_supports=inputs, options=options)
        b = separate_h2(self.path, dict(reversed(list(self.y.items()))),
                        proposed_supports=list(reversed(inputs)), options=options)
        self.assertEqual(len(a.records), 1)
        self.assertEqual(a.cuts[0].cut_hash, b.cuts[0].cut_hash)
        self.assertEqual(a.cuts[0].certificate_sha256, b.cuts[0].certificate_sha256)

    def test_as15_07_instance_T_changes_cannot_contaminate_certificate_cache(self):
        # Two physically distinct problems: same V, S, edges, r; only T differs.
        edges = [('a','b'),('b','c'),('c','d')]
        near = physical('abcd', 'a', 'c', edges, r=2)
        far = physical('abcd', 'a', 'd', edges, r=2)
        y = dict.fromkeys('abcd', .1)
        shared = MatchingOracle()
        near_result = separate_h2(near, y, oracle=shared,
                                  proposed_supports=[near.V], options=self.no_budget)
        far_result = separate_h2(far, y, oracle=shared,
                                 proposed_supports=[far.V], options=self.no_budget)
        self.assertNotEqual(near.fingerprint, far.fingerprint)
        self.assertEqual(near_result.records[0]['status'], 'NO_CUT')
        self.assertEqual(far_result.records[0]['status'], 'EMITTED')
        self.assertEqual(far_result.cuts[0].instance_sha256, far.fingerprint)

    def test_as15_large_support_selection_is_bounded_without_global_enumeration(self):
        V = tuple(range(40))
        y = dict.fromkeys(V, .025)
        proposals = select_supports(V, y, k_supports=[(v,) for v in V],
                                    max_supports=5, max_pairs=3)
        self.assertEqual(len(proposals), 5)
        self.assertEqual(proposals[0].support, V)

    def test_as15_08_minimal_cover_degenerates_without_novelty(self):
        r = separate_h2(self.path, {'a': 0., 'b': 0.2, 'c': 0.},
                        proposed_supports=[('b',)], options=self.no_budget)
        self.assertEqual(r.cuts, ())
        self.assertEqual(r.records[0]['status'], 'DEGENERATE_COVER')
        self.assertTrue(r.records[0]['minimal_cover_certified'])
        self.assertEqual(r.to_dict()['degenerate_supports'], 1)
        self.assertEqual(r.to_dict()['nondegenerate_cuts'], 0)

    def test_as15_invalid_inputs_closed_before_certification(self):
        for bad in ({'a': 0., 'b': math.nan, 'c': 0.},
                    {'a': -0.1, 'b': 0., 'c': 0.},
                    {'a': 0., 'b': 0.},
                    {'a': True, 'b': 0., 'c': 0.}):
            with self.assertRaises(ValueError):
                separate_h2(self.path, bad, options=self.no_budget)
        with self.assertRaises(ValueError):
            separate_h2(self.path, self.y, proposed_supports=[('z',)], options=self.no_budget)
        with self.assertRaises(ValueError):
            SeparatorOptions(min_violation=-1)
        with self.assertRaises(ValueError):
            H2Cut(instance_sha256='0'*64, support=('a',), bhat=('a',),
                  coefficients=(('a', 2),), certificate_sha256='0'*64,
                  certificate_hashes=('0'*64,), violation=1., lhs_at_lp=1.,
                  oracle_calls=1, elapsed_wall_s=0.)

    def test_as15_heuristic_bounded_deterministic_and_source_agnostic(self):
        y = {'a': .2, 'b': .4, 'c': .2}
        r1 = select_supports('abc', y, k_supports=[('b',), ('a','c')],
                             hall_supports=[('a','b')], max_supports=4)
        r2 = select_supports('cba', y, k_supports=[('c','a'), ('b',)],
                             hall_supports=[('b','a')], max_supports=4)
        self.assertEqual(r1, r2)
        self.assertEqual(len(r1), 4)
        self.assertEqual(r1[0].support, ('a', 'b', 'c'))
        self.assertTrue(all(set(s.support) <= set('abc') for s in r1))
        bounded = select_supports('abc', y, k_supports=[('b',)],
                                  max_supports=4, max_support_size=2)
        self.assertTrue(all(len(x.support) <= 2 for x in bounded))

    def test_as15_precision_and_recall_vs_exhaustive_microinstances(self):
        cases = [
            self.path,
            physical('abcd', 'a', 'd', [('a','b'), ('b','c'), ('c','d')]),
            physical(('s1','s2','w','t1','t2'), ('s1','s2'), ('t1','t2'),
                     [('s1','w'), ('s2','w'), ('w','t1'), ('w','t2')]),
        ]
        rng = random.Random(1515)
        total_true_violated = total_heur_hits = total_emitted = 0
        for i in cases:
            for trial in range(3):
                y = {v: rng.uniform(.05,.45) for v in i.V}
                exact = {}
                for R in all_subsets(i.V):
                    coeff = physical_h2(i, R)
                    if coeff is None or not any(c == 1 for c in coeff.values()):
                        continue
                    violation = 2 - sum(coeff[v] * y[v] for v in R)
                    if violation > 1e-7:
                        exact[order_vertices(R)] = coeff
                all_R = list(all_subsets(i.V))
                exhaustive = separate_h2(i, y, proposed_supports=all_R,
                                         options=self.no_budget)
                heuristic = separate_h2(i, y, options=self.no_budget)
                for result in (exhaustive, heuristic):
                    for cut in result.cuts:
                        total_emitted += 1
                        self.assertIn(cut.support, exact)
                        self.assertEqual(dict(cut.coefficients), exact[cut.support])
                        self.assertGreater(cut.violation, 1e-7)
                        for C in all_subsets(i.V):
                            if battery_viable(i, C):
                                self.assertGreaterEqual(
                                    sum(coef for v, coef in cut.coefficients if v in C), 2)
                self.assertEqual({c.support for c in exhaustive.cuts}, set(exact))
                total_true_violated += len(exact)
                total_heur_hits += len({c.support for c in heuristic.cuts} & set(exact))
        self.assertGreater(total_true_violated, 0)
        self.assertGreater(total_emitted, 0)
        precision = 1.  # every emitted cut was compared with physical truth above
        recall = total_heur_hits / total_true_violated
        self.assertEqual(precision, 1.)
        self.assertGreaterEqual(recall, 0.)
        self.assertLessEqual(recall, 1.)

    def test_as15_hb_nonredundant_cut_closes_comp_k_lp_gap(self):
        # HB is the AS13 witness: COMP+K LP=1; H2 y(V)>=2 raises LP to 2.
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for module in (root / 'structural', root / 'alternative-formulations'):
            if str(module) not in sys.path:
                sys.path.insert(0, str(module))
        from hb import construir
        from verify_as13_foundations import k_cuts, reach_arcs, solve_comp_lp

        S, T, V, adj, _, r, _ = construir(4, 2, 1)
        i = PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)
        arcs = reach_arcs(V, adj, r)
        K = k_cuts(S, T, V, adj, r, arcs)
        base, lp_y, _ = solve_comp_lp(S, T, V, arcs, K)
        self.assertAlmostEqual(base, 1., places=7)
        result = separate_h2(i, lp_y, k_supports=K, options=self.no_budget)
        full = next(c for c in result.cuts if set(c.support) == set(V))
        self.assertTrue(all(coef == 1 for _, coef in full.coefficients))
        self.assertEqual(full.rhs, 2)
        self.assertAlmostEqual(full.violation, 1., places=7)
        strengthened, _, _ = solve_comp_lp(S, T, V, arcs, K,
                                            [(dict(full.coefficients), full.rhs)])
        self.assertAlmostEqual(strengthened, 2., places=7)
        self.assertGreater(strengthened, base + 0.9)


if __name__ == '__main__':
    unittest.main()
