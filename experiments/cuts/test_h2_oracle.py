"""Acceptance tests AS14-01..07: matching, budget, H2, cache, controls.

Assertions are driven by independently constructed physical microinstances and
independent_validator.viavel, not by introspection of implementation counters.
"""
from __future__ import annotations

import json
import random
import unittest
from dataclasses import replace
from itertools import combinations
from unittest.mock import patch

from independent_validator import viavel
from h2_oracle import (MatchingOracle, PhysicalInstance, Status, classify_h2)
from h2_oracle_schema import ViabilityResult


def make_instance(V, S, T, edges, r=1):
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def subsets(V):
    for k in range(len(V) + 1):
        yield from combinations(V, k)


def control_cases():
    return [
        make_instance('ust', 'us', 'st', [('u','s'),('s','t')]),
        make_instance('abc', 'a', 'c', [('a','b'),('b','c')]),
        make_instance('abcd', 'a', 'd', [('a','b'),('b','c'),('c','d')]),
        make_instance(('s1','s2','w','t1','t2'), ('s1','s2'), ('t1','t2'),
                      [('s1','w'),('s2','w'),('w','t1'),('w','t2')]),
        make_instance('st', 's', 't', []),
    ]


class JumpClock:
    """Deterministic monotonic clock: one controllable deadline crossing."""
    def __init__(self, jump_at=None, late=100.0):
        self.reads = 0
        self.jump_at = jump_at
        self.late = late

    def __call__(self):
        self.reads += 1
        return self.late if self.jump_at is not None and self.reads >= self.jump_at else 0.0


class AS14OracleTests(unittest.TestCase):
    def test_as14_01_origin_terminal_without_station_does_not_recharge(self):
        # a-m-b-n-c with b-q: b is an origin/terminal, but must not recharge
        # unless b is installed. Both expectations are independent of viavel.
        V = ('a', 'm', 'b', 'n', 'c', 'q')
        edges = [('a', 'm'), ('m', 'b'), ('b', 'n'), ('n', 'c'), ('b', 'q')]
        i = make_instance(V, ('a', 'b'), ('c', 'q'), edges, r=2)
        without = MatchingOracle().check(i, ())
        self.assertEqual(without.status, Status.INFEASIBLE)
        self.assertEqual(without.matching_size, 1)
        self.assertEqual(without.hall_origins, ('a',))
        self.assertEqual(without.hall_destinations, ())
        with_station = MatchingOracle().check(i, ('b',))
        self.assertEqual(with_station.status, Status.VIABLE)
        self.assertEqual(with_station.matching_size, 2)

    def test_as14_01_destination_terminal_without_station_does_not_recharge(self):
        # a-m-t1-n-t2; u-t1; r=2. Reaching t2 via terminal t1 requires
        # an actual station at t1 (not automatic charging at destinations).
        V = ('a', 'm', 't1', 'n', 't2', 'u')
        edges = [('a', 'm'), ('m', 't1'), ('t1', 'n'), ('n', 't2'), ('u', 't1')]
        i = make_instance(V, ('a', 'u'), ('t1', 't2'), edges, r=2)
        without = MatchingOracle().check(i, ())
        self.assertEqual(without.status, Status.INFEASIBLE)
        self.assertEqual(without.matching_size, 1)
        self.assertEqual(MatchingOracle().check(i, ('t1',)).status, Status.VIABLE)

    def test_as14_01_zero_robots_certificate(self):
        i = make_instance('a', (), (), ())
        x = MatchingOracle().check(i, ())
        self.assertEqual((x.status, x.matching_size, x.witness), (Status.VIABLE, 0, ()))

    def test_as14_01_station_free_direct_path(self):
        i = make_instance('st', 's', 't', [('s','t')])
        x = MatchingOracle().check(i, ())
        self.assertEqual(x.status, Status.VIABLE)
        self.assertEqual(x.witness, (('s', 't'),))
        self.assertEqual(x.matching_size, 1)

    def test_as14_01_anonymous_matching_not_fixed_pairing(self):
        i = make_instance(('s1','s2','t1','t2'), ('s1','s2'), ('t1','t2'),
                          [('s1','t2'),('s2','t1')])
        x = MatchingOracle().check(i, ())
        self.assertEqual(x.status, Status.VIABLE)
        self.assertEqual(set(x.witness), {('s1','t2'),('s2','t1')})

    def test_as14_01_zero_length_stay_in_s_intersection_t(self):
        i = make_instance(('x','y'), ('x',), ('x',), [('x','y')], r=0)
        self.assertEqual(MatchingOracle().check(i, ()).witness, (('x','x'),))

    def test_as14_01_nonterminal_relay_requires_installed_station(self):
        i = make_instance('abcd', 'a', 'd', [('a','b'),('b','c'),('c','d')])
        self.assertEqual(MatchingOracle().check(i, ('b','c')).status, Status.VIABLE)
        self.assertEqual(MatchingOracle().check(i, ('b',)).status, Status.INFEASIBLE)

    def test_as14_01_share_station_without_capacity(self):
        i = control_cases()[3]
        x = MatchingOracle().check(i, ('w',))
        self.assertEqual((x.status, x.matching_size), (Status.VIABLE, 2))

    def test_as14_01_no_station_needed_if_autonomy_sufficient(self):
        i = make_instance('abcd','a','d',[('a','b'),('b','c'),('c','d')],r=3)
        self.assertEqual(MatchingOracle().check(i, ()).status, Status.VIABLE)

    def test_as14_02_infeasible_has_replayable_hall_witness(self):
        i = make_instance(('s1','s2','t1','t2'), ('s1','s2'),('t1','t2'),
                          [('s1','t1'),('s2','t1')])
        x = MatchingOracle().check(i, ())
        self.assertEqual(x.status, Status.INFEASIBLE)
        self.assertEqual(x.matching_size, 1)
        self.assertEqual(set(x.hall_origins), {'s1','s2'})
        self.assertEqual(set(x.hall_destinations), {'t1'})
        data = x.to_dict()['hall_certificate']
        self.assertEqual(data['deficiency'], 1)

    def test_as14_02_unreachable_is_infeasible(self):
        x = MatchingOracle().check(control_cases()[-1], ())
        self.assertEqual((x.status, x.matching_size), (Status.INFEASIBLE, 0))
        self.assertEqual(x.hall_origins, ('s',))
        self.assertEqual(x.hall_destinations, ())

    def test_as14_03_zero_budget_always_unknown(self):
        i = control_cases()[1]
        self.assertEqual(MatchingOracle().check(i, ('b',), budget_s=0).status, Status.UNKNOWN)

    def test_as14_03_timeout_after_reachability_yields_unknown(self):
        i = control_cases()[1]
        oracle = MatchingOracle()
        with patch('h2_oracle.destinos_alcancaveis', side_effect=lambda *args: self._timeout_reach(*args)):
            x = oracle.check(i, (), budget_s=0.01)
        self.assertEqual(x.status, Status.UNKNOWN)
        self.assertIsNone(x.matching_size)
        self.assertNotIn('hall_certificate', x.to_dict())
        self.assertEqual(len(oracle.cache), 0)

    @staticmethod
    def _timeout_reach(*args):
        import time
        time.sleep(0.02)
        return set()

    def test_as14_03_reach_exception_is_unknown_not_infeasible(self):
        i = control_cases()[1]
        with patch('h2_oracle.destinos_alcancaveis', side_effect=RuntimeError('broken')):
            x = MatchingOracle().check(i, ('b',))
        self.assertEqual(x.status, Status.UNKNOWN)
        self.assertTrue(x.reason.startswith('ORACLE_ERROR:'))

    def test_as14_03_matching_exception_is_unknown(self):
        i = control_cases()[1]
        with patch('h2_oracle._max_matching_with_hall', side_effect=RuntimeError):
            x = MatchingOracle().check(i, ('b',))
        self.assertEqual(x.status, Status.UNKNOWN)
        self.assertIsNone(x.matching_size)

    def test_as14_03_unknown_not_cached_even_if_retried(self):
        i = control_cases()[1]
        oracle = MatchingOracle()
        with patch('h2_oracle.destinos_alcancaveis', side_effect=RuntimeError):
            self.assertEqual(oracle.check(i, ('b',)).status, Status.UNKNOWN)
        self.assertEqual(oracle.check(i, ('b',)).status, Status.VIABLE)
        self.assertEqual(len(oracle.cache), 1)
        self.assertEqual(oracle.physical_computations, 2)

    def test_as14_03_unknown_rejected_as_false_certificate(self):
        i = control_cases()[1]
        x = MatchingOracle().check(i, (), budget_s=0)
        with self.assertRaises(ValueError):
            replace(x, status=Status.INFEASIBLE, matching_size=0)

    def test_as14_03_budget_crossings_include_final_probe_and_cache_hit(self):
        # Sweep every read of a deterministic clock for both the fresh and
        # cached paths. R23 (remove the final probe) must be killed here.
        i = control_cases()[1]
        stations = ('b',)
        budget = 10.0
        fresh_clock = JumpClock()
        fresh_result = MatchingOracle(clock=fresh_clock).check(i, stations, budget_s=budget)
        self.assertEqual(fresh_result.status, Status.VIABLE)
        for jump in range(1, fresh_clock.reads + 1):
            candidate = MatchingOracle(clock=JumpClock(jump_at=jump)).check(
                i, stations, budget_s=budget)
            if candidate.status is not Status.UNKNOWN:
                self.assertLess(candidate.elapsed_wall_s, budget, ('fresh', jump))
            else:
                self.assertIsNone(candidate.matching_size)

        # Cache is populated without an artificial deadline; then the clock is
        # reset so each cache hit is independently tested at each read.
        warm = MatchingOracle(clock=JumpClock())
        warm.check(i, stations, budget_s=budget)
        cached_clock = JumpClock()
        warm.clock = cached_clock
        cached_result = warm.check(i, stations, budget_s=budget)
        self.assertTrue(cached_result.cache_hit)
        self.assertEqual(cached_result.status, Status.VIABLE)
        for jump in range(1, cached_clock.reads + 1):
            oracle = MatchingOracle(clock=JumpClock())
            oracle.check(i, stations, budget_s=budget)
            oracle.clock = JumpClock(jump_at=jump)
            candidate = oracle.check(i, stations, budget_s=budget)
            if candidate.status is not Status.UNKNOWN:
                self.assertTrue(candidate.cache_hit)
                self.assertLess(candidate.elapsed_wall_s, budget, ('cache', jump))
            else:
                self.assertIsNone(candidate.matching_size)
                self.assertEqual(candidate.reason, 'TIME_BUDGET_EXCEEDED')

    def test_as14_03_final_probe_rejects_certificate_when_clock_crosses(self):
        # Force the clock to cross the deadline *after* building the certified
        # result but *before* the final probe. This must fail under mutant R23.
        from h2_oracle import ViabilityResult as original_result

        i = control_cases()[1]
        for preload_cache in (False, True):
            with self.subTest(cache_hit=preload_cache):
                clock = JumpClock()
                oracle = MatchingOracle(clock=clock)
                if preload_cache:
                    self.assertEqual(oracle.check(i, ('b',), budget_s=10).status,
                                     Status.VIABLE)
                clock.reads = 0
                clock.jump_at = None

                def create_result(*args, **kwargs):
                    certificate = original_result(*args, **kwargs)
                    if certificate.status is Status.VIABLE:
                        # Only the next clock observation reveals the overrun.
                        clock.jump_at = clock.reads + 1
                    return certificate

                with patch('h2_oracle.ViabilityResult', side_effect=create_result):
                    answer = oracle.check(i, ('b',), budget_s=10)
                self.assertEqual(answer.status, Status.UNKNOWN)
                self.assertEqual(answer.reason, 'TIME_BUDGET_EXCEEDED')
                self.assertIsNone(answer.matching_size)

    def test_as14_04_complement_on_actual_physical_V(self):
        i = control_cases()[1]
        c = classify_h2(MatchingOracle(), i, {'b'})
        self.assertEqual(c.support, ('b',))
        self.assertEqual(c.complement, ('a','c'))
        self.assertEqual((c.state,c.rhs), ('CERTIFIED',2))
        self.assertEqual(c.coefficients, (('b',2),))

    def test_as14_04_complement_viable_is_not_cut(self):
        i = control_cases()[1]
        x = classify_h2(MatchingOracle(), i, {'a'})
        # Removing a leaves {b,c} available; both stations are not needed.
        self.assertEqual(x.state, 'NO_CUT')
        self.assertEqual(classify_h2(MatchingOracle(), i, ()).state, 'NO_CUT')

    def test_as14_04_full_complement_viable_is_no_cut(self):
        i = control_cases()[1]
        self.assertEqual(classify_h2(MatchingOracle(), i, ()).state, 'NO_CUT')

    def test_as14_05_same_graph_reordered_has_same_hash_and_key(self):
        a = make_instance('abc','a','c',[('a','b'),('b','c')])
        b = make_instance('cba','a','c',[('c','b'),('b','a')])
        self.assertEqual(a.fingerprint, b.fingerprint)
        oracle = MatchingOracle()
        first = oracle.check(a, ('c','b'))
        second = oracle.check(b, ('b','c'))
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertTrue(second.cache_hit)
        self.assertEqual(oracle.physical_computations, 1)

    def test_as14_05_graphs_same_size_do_not_collide(self):
        a = make_instance('abc','a','c',[('a','b'),('b','c')])
        b = make_instance('abc','a','c',[('a','b')])
        self.assertNotEqual(a.fingerprint,b.fingerprint)
        oracle = MatchingOracle()
        self.assertEqual(oracle.check(a, ('b',)).status, Status.VIABLE)
        self.assertEqual(oracle.check(b, ('b',)).status, Status.INFEASIBLE)
        self.assertEqual(oracle.physical_computations, 2)

    def test_as14_05_int_and_str_vertices_never_share_fingerprint_or_cache(self):
        # R29: dropping vertex type would make [1,2] and ['1','2'] collide,
        # allowing a cached VIABLE certificate to certify an infeasible graph.
        V = (1, 2, '1', '2')
        a = make_instance(V, (1,), (2,), [(1, 2)])
        b = make_instance(V, (1,), (2,), [('1', '2')])
        self.assertNotEqual(a.fingerprint, b.fingerprint)
        oracle = MatchingOracle()
        self.assertEqual(oracle.check(a, ()).status, Status.VIABLE)
        second = oracle.check(b, ())
        self.assertEqual(second.status, Status.INFEASIBLE)
        self.assertFalse(second.cache_hit)
        self.assertEqual(oracle.physical_computations, 2)

    def test_as15_entry_t_only_change_cannot_reuse_viable_cache(self):
        # Opus R2/N08: identical graph, S and r, but T changes only.
        # r=0 and s=t yields VIABLE with no edges; T=(1,) is INFEASIBLE.
        # Dropping T from the fingerprint would reuse a false VIABLE cache hit.
        source = make_instance((0, 1), (0,), (0,), [], r=0)
        target = make_instance((0, 1), (0,), (1,), [], r=0)
        self.assertEqual(source.V, target.V)
        self.assertEqual(source.S, target.S)
        self.assertEqual(source.adj, target.adj)
        self.assertEqual(source.r, target.r)
        self.assertNotEqual(source.T, target.T)

        oracle = MatchingOracle()
        viable = oracle.check(source, ())
        self.assertEqual(viable.status, Status.VIABLE)
        self.assertFalse(viable.cache_hit)
        infeasible = oracle.check(target, ())
        self.assertEqual(infeasible.status, Status.INFEASIBLE)
        self.assertFalse(infeasible.cache_hit)
        self.assertEqual(oracle.physical_computations, 2)
        self.assertNotEqual(source.fingerprint, target.fingerprint)
        self.assertNotEqual(viable.instance_sha256, infeasible.instance_sha256)

    def test_as14_05_input_mutation_cannot_change_instance_identity(self):
        adj = {'a':[('b',1)], 'b':[('a',1),('c',1)], 'c':[('b',1)]}
        i = PhysicalInstance(('a','b','c'), ('a',), ('c',), adj, 1)
        before = i.fingerprint
        adj['a'].clear()
        adj['b'].clear()
        self.assertEqual(before, i.fingerprint)
        self.assertEqual(MatchingOracle().check(i, ('b',)).status, Status.VIABLE)

    def test_as14_05_bool_vertex_does_not_alias_integer(self):
        i = make_instance((1,2), (1,), (2,), [(1,2)])
        with self.assertRaises(ValueError):
            MatchingOracle().check(i, (True,))

    def test_as14_05_same_graph_different_r_and_terminals(self):
        a = make_instance('abc','a','c',[('a','b'),('b','c')], r=1)
        b = make_instance('abc','a','c',[('a','b'),('b','c')], r=2)
        c = make_instance('abc','b','c',[('a','b'),('b','c')], r=1)
        d = make_instance('abc','a','b',[('a','b'),('b','c')], r=1)
        # d changes T only; the previous test checked r and S, but not T.
        self.assertEqual(len({a.fingerprint,b.fingerprint,c.fingerprint,
                              d.fingerprint}), 4)

    def test_as14_05_deterministic_json_and_station_order(self):
        i = control_cases()[1]
        oracle = MatchingOracle()
        first = oracle.check(i, ('b','a'))
        payload = first.to_json()
        self.assertEqual(payload, json.dumps(json.loads(payload),ensure_ascii=False,
                                              sort_keys=True,separators=(',',':')))
        self.assertEqual(first.allowed_stations, ('a','b'))

    def test_as14_05_invalid_graph_or_stations_fail_before_cache(self):
        with self.assertRaises(ValueError):
            PhysicalInstance(('a','b'),('a',),('b',), {'a':[('b',1)],'b':[]},1)
        with self.assertRaises(ValueError):
            make_instance('ab','a','b', [('a','b')],r=-1)
        with self.assertRaises(ValueError):
            MatchingOracle().check(control_cases()[1], ('absent',))

    def test_as14_06_unknown_complement_does_not_emit_cut(self):
        i = control_cases()[1]
        c = classify_h2(MatchingOracle(), i, {'b'}, budget_s=0)
        self.assertEqual(c.state, 'UNKNOWN')
        self.assertIsNone(c.rhs)
        self.assertEqual(c.Bhat, ())

    def test_as14_06_only_certified_infeasible_additions_enter_bhat(self):
        i = control_cases()[2]  # chain a-b-c-d, r=1; needs b and c
        oracle = MatchingOracle()
        c = classify_h2(oracle, i, {'b','c'})
        self.assertEqual(c.state, 'CERTIFIED')
        self.assertEqual(c.Bhat, ('b','c'))
        self.assertEqual(c.coefficients,(('b',1),('c',1)))
        self.assertEqual(c.rhs,2)

    def test_as14_06_partial_candidates_unknown_get_coef_two(self):
        i = control_cases()[2]
        c = classify_h2(MatchingOracle(), i, {'b','c'}, candidates={'b'})
        self.assertEqual(c.Bhat, ('b',))
        self.assertEqual(c.coefficients,(('b',1),('c',2)))

    def test_as14_06_candidate_exception_does_not_enter_bhat(self):
        i = control_cases()[2]
        oracle = MatchingOracle()
        from h2_oracle import destinos_alcancaveis as original
        calls = [0]
        def injected(*args):
            calls[0] += 1
            if calls[0] >= 2:  # after complement call; with only one origin
                raise RuntimeError('candidate not certified')
            return original(*args)
        with patch('h2_oracle.destinos_alcancaveis', side_effect=injected):
            c = classify_h2(oracle, i, {'b','c'})
        self.assertEqual(c.state, 'CERTIFIED')
        self.assertEqual(c.Bhat, ())
        self.assertEqual(c.coefficients, (('b',2),('c',2)))
        self.assertEqual(c.unknown_candidates,('b','c'))

    def test_as14_07_cached_monotonic_conflicts_fail_closed(self):
        i = control_cases()[1]
        oracle = MatchingOracle()
        valid = oracle.check(i, ('b',))
        self.assertEqual(valid.status, Status.VIABLE)
        impossible = ViabilityResult(status=Status.INFEASIBLE,
                                     instance_sha256=i.fingerprint, allowed_stations=('a','b'),
                                     robot_count=1, matching_size=0,elapsed_wall_s=0,budget_s=None,
                                     calls=2,fingerprint='synthetic',hall_origins=('a',),
                                     hall_destinations=())
        with self.assertRaises(AssertionError):
            oracle.cache.put(impossible)

    def test_as14_07_cached_infeasible_superset_rejects_viable_subset(self):
        # The reverse fail-closed branch is essential: INFEASIBLE(C') must
        # conflict with VIABLE(C) whenever C is a subset of C'. Kills R30.
        i = control_cases()[1]
        oracle = MatchingOracle()
        cached_impossible = ViabilityResult(
            status=Status.INFEASIBLE, instance_sha256=i.fingerprint,
            allowed_stations=('a', 'b'), robot_count=1, matching_size=0,
            elapsed_wall_s=0, budget_s=None, calls=1, fingerprint='synthetic',
            hall_origins=('a',), hall_destinations=())
        oracle.cache.put(cached_impossible)
        valid_subset = MatchingOracle().check(i, ('b',))
        self.assertEqual(valid_subset.status, Status.VIABLE)
        with self.assertRaisesRegex(AssertionError, 'monotonicity'):
            oracle.cache.put(valid_subset)

    def test_as14_07_all_ordered_pairs_of_subsets_are_monotone(self):
        for i in control_cases():
            oracle = MatchingOracle()
            results = {frozenset(C): oracle.check(i, C).status for C in subsets(i.V)}
            self.assertEqual(len(results), 2 ** len(i.V))
            for a, a_status in results.items():
                if a_status is not Status.VIABLE:
                    continue
                for b, b_status in results.items():
                    if a <= b:
                        self.assertNotEqual(b_status, Status.INFEASIBLE)

    def test_as14_independent_battery_oracle_exhaustive_controls(self):
        checked = 0
        both = set()
        for i in control_cases():
            oracle = MatchingOracle()
            for C in subsets(i.V):
                got = oracle.check(i, C)
                expected = viavel(i.S,i.T,i.V,i.adj,i.r,C)
                self.assertEqual(got.status is Status.VIABLE, expected, (i,C))
                self.assertNotEqual(got.status,Status.UNKNOWN)
                both.add(got.status)
                checked += 1
        self.assertEqual(checked, sum(2 ** len(i.V) for i in control_cases()))
        self.assertEqual(both, {Status.VIABLE, Status.INFEASIBLE})

    def test_as14_independent_oracle_random_small_graphs(self):
        rng = random.Random(1407)
        for n in range(2,6):
            V = tuple(f'v{x}' for x in range(n))
            for _ in range(8):
                edges = [(V[a],V[b]) for a,b in combinations(range(n),2) if rng.getrandbits(1)]
                selected = rng.sample(V, rng.randint(1,n))
                m = rng.randint(1,len(selected))
                S = tuple(selected[:m])
                T = tuple(rng.sample(V,m))
                i = make_instance(V,S,T,edges,rng.randint(0,3))
                oracle = MatchingOracle()
                for C in subsets(V):
                    x = oracle.check(i,C)
                    self.assertNotEqual(x.status,Status.UNKNOWN)
                    self.assertEqual(x.status is Status.VIABLE, viavel(i.S,i.T,i.V,i.adj,i.r,C))

    def test_as14_h2_cuts_valid_on_every_physical_installation(self):
        for i in control_cases():
            oracle = MatchingOracle()
            physical = [set(C) for C in subsets(i.V) if viavel(i.S,i.T,i.V,i.adj,i.r,C)]
            for R in subsets(i.V):
                classification = classify_h2(oracle, i, R)
                if classification.state != 'CERTIFIED':
                    continue
                for C in physical:
                    self.assertGreaterEqual(sum(c for v,c in classification.coefficients if v in C),2)

    def test_as14_metrics_record_calls_and_cache_hits(self):
        i = control_cases()[1]
        oracle = MatchingOracle()
        oracle.check(i, ('b',))
        oracle.check(i, ('b',))
        metrics = oracle.metrics()
        self.assertEqual(metrics['calls'],2)
        self.assertEqual(metrics['physical_computations'],1)
        self.assertEqual(metrics['cache_hits'],1)
        self.assertGreaterEqual(metrics['total_elapsed_wall_s'],0)


if __name__ == '__main__':
    unittest.main()
