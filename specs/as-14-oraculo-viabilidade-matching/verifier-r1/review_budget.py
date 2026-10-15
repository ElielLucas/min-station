"""AS14 review: cooperative budget behaviour, indivisible operations and fake clocks."""
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
import os
sys.path.insert(0, os.environ.get('AS14_CUTS', str(ROOT / 'experiments/cuts')))

import h2_oracle  # noqa: E402
from h2_oracle import MatchingOracle, PhysicalInstance, Status, classify_h2  # noqa: E402


def chain():
    adj = {'a': [('b', 1)], 'b': [('a', 1), ('c', 1)], 'c': [('b', 1)]}
    return PhysicalInstance(('a', 'b', 'c'), ('a',), ('c',), adj, 1)


class CountingClock:
    def __init__(self, jump_at=None, jump=100.0):
        self.n = 0
        self.jump_at = jump_at
        self.jump = jump

    def __call__(self):
        self.n += 1
        if self.jump_at is not None and self.n >= self.jump_at:
            return self.jump
        return 0.0


class Budget(unittest.TestCase):
    def test_indivisible_reach_overshoot_is_unknown(self):
        orig = h2_oracle.destinos_alcancaveis

        def slow(*a):
            time.sleep(0.2)
            return orig(*a)
        with patch('h2_oracle.destinos_alcancaveis', side_effect=slow):
            t0 = time.monotonic()
            x = MatchingOracle().check(chain(), ('b',), budget_s=0.05)
            wall = time.monotonic() - t0
        self.assertGreaterEqual(wall, 0.2)          # the indivisible call was NOT preempted
        self.assertEqual(x.status, Status.UNKNOWN)  # but its result is discarded
        self.assertIsNone(x.matching_size)

    def test_indivisible_graph_build_overshoot_is_unknown(self):
        orig = h2_oracle._grafo_unitario

        def slow(*a):
            time.sleep(0.15)
            return orig(*a)
        with patch('h2_oracle._grafo_unitario', side_effect=slow):
            x = MatchingOracle().check(chain(), ('b',), budget_s=0.05)
        self.assertEqual(x.status, Status.UNKNOWN)

    def test_every_clock_crossing_point_yields_unknown_or_in_budget(self):
        # Find the number of clock reads of a successful fresh call, then make the clock jump
        # past the budget at each possible read. Any certified answer must report elapsed < budget.
        base = CountingClock()
        ok = MatchingOracle(clock=base).check(chain(), ('b',), budget_s=10)
        self.assertEqual(ok.status, Status.VIABLE)
        total = base.n
        for k in range(1, total + 1):
            x = MatchingOracle(clock=CountingClock(jump_at=k)).check(chain(), ('b',), budget_s=10)
            if x.status is not Status.UNKNOWN:
                self.assertLess(x.elapsed_wall_s, 10, f'certified over budget at read {k}/{total}')

    def test_cache_hit_crossing_point(self):
        # Same sweep on the cache-hit path (stored certificate is valid; checks reported elapsed).
        out = []
        for k in range(1, 8):
            clock = CountingClock()
            o = MatchingOracle(clock=clock)
            o.check(chain(), ('b',), budget_s=10)
            clock.n = 0
            clock.jump_at = k
            x = o.check(chain(), ('b',), budget_s=10)
            out.append((k, x.status.value, x.elapsed_wall_s, x.cache_hit))
        over = [row for row in out if row[1] != 'UNKNOWN' and row[2] >= 10]
        print('cache-hit sweep:', out)
        self.assertEqual(over, [], f'cache hit returned certificate with elapsed >= budget: {over}')

    def test_fingerprint_time_is_outside_budget(self):
        # Canonicalisation/fingerprint is computed before `begin`; measure whether it is charged.
        slow_fp = property(lambda self: (time.sleep(0.2), 'f' * 64)[1])
        with patch.object(PhysicalInstance, 'fingerprint', slow_fp):
            t0 = time.monotonic()
            x = MatchingOracle().check(chain(), ('b',), budget_s=0.05)
            wall = time.monotonic() - t0
        print(f'fingerprint sweep: status={x.status.value} wall={wall:.3f}s budget=0.05 '
              f'reported_elapsed={x.elapsed_wall_s:.4f}')
        # Not a false certificate (the matching is complete); record as a budget-accounting gap.
        self.assertIn(x.status, (Status.VIABLE, Status.UNKNOWN))

    def test_classify_h2_exhausted_budget_never_enters_bhat(self):
        adj = {v: [] for v in 'abcd'}
        for u, w in (('a', 'b'), ('b', 'c'), ('c', 'd')):
            adj[u].append((w, 1))
            adj[w].append((u, 1))
        i = PhysicalInstance(tuple('abcd'), ('a',), ('d',), adj, 1)
        for k in range(1, 200):
            c = classify_h2(MatchingOracle(clock=CountingClock(jump_at=k)), i, ('b', 'c'), budget_s=10)
            if c.state == 'CERTIFIED':
                for v in c.Bhat:
                    self.assertNotIn(v, c.unknown_candidates)
                self.assertTrue(set(c.Bhat) <= {'b', 'c'})
            self.assertIn(c.state, ('CERTIFIED', 'UNKNOWN'))

    def test_recursion_limit_large_m_is_unknown_not_infeasible(self):
        # Kuhn is recursive; long augmenting chains exceed Python's recursion limit.
        m = 1500
        S = tuple(range(m))
        T = tuple(range(m, 2 * m))
        adj = {v: [] for v in S + T}

        def e(u, w):
            adj[u].append((w, 1))
            adj[w].append((u, 1))
        # s_k -> {t_k, t_{k+1}} (k < m-1), s_{m-1} -> {t_0}: greedy takes t_k, the last origin
        # forces an augmenting path through every origin (depth ~ m).
        for k in range(m - 1):
            e(S[k], T[k])
            e(S[k], T[k + 1])
        e(S[m - 1], T[0])
        i = PhysicalInstance(S + T, S, T, adj, 1)
        x = MatchingOracle().check(i, ())
        print('large-m status:', x.status.value, x.reason)
        self.assertNotEqual(x.status, Status.INFEASIBLE)


if __name__ == '__main__':
    unittest.main(verbosity=2)
