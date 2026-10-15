"""AS14 review: hand-derived physical microinstances (expected values derived by hand, not by code)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
import os
sys.path.insert(0, os.environ.get('AS14_CUTS', str(ROOT / 'experiments/cuts')))
sys.path.insert(0, str(Path(__file__).parent))

from h2_oracle import MatchingOracle, PhysicalInstance, Status, classify_h2  # noqa: E402

V_, I_ = Status.VIABLE, Status.INFEASIBLE


def inst(V, S, T, edges, r):
    adj = {v: [] for v in V}
    for u, w in edges:
        adj[u].append((w, 1))
        adj[w].append((u, 1))
    return PhysicalInstance(tuple(V), tuple(S), tuple(T), adj, r)


def path(names):
    return [(names[k], names[k + 1]) for k in range(len(names) - 1)]


class Micro(unittest.TestCase):
    def st(self, i, C):
        return MatchingOracle().check(i, C)

    def test_sxt_robot_must_leave_its_own_target(self):
        # s - x - t, S={s,x}, T={x,t}, r=1: only s->x and x->t work (s->t needs 2 steps).
        i = inst('sxt', ('s', 'x'), ('x', 't'), path('sxt'), 1)
        x = self.st(i, ())
        self.assertEqual(x.status, V_)
        self.assertEqual(set(x.witness), {('s', 'x'), ('x', 't')})

    def test_sxt_stay_not_double_counted(self):
        # x in S∩T, second robot y far away: T={x,z} where z unreachable for anyone without station.
        # x stays (or goes); y must reach z: path y-a-z (2 steps), r=1.
        i = inst(('x', 'y', 'a', 'z'), ('x', 'y'), ('x', 'z'), [('y', 'a'), ('a', 'z')], 1)
        self.assertEqual(self.st(i, ()).status, I_)
        self.assertEqual(self.st(i, ('a',)).status, V_)
        bad = self.st(i, ())
        self.assertEqual(bad.matching_size, 1)

    def test_terminal_without_station_does_not_recharge(self):
        # a-m-b-n-c and b-q, S={a,b}, T={c,q}, r=2. b is an origin (terminal) but has no station.
        # a reaches nothing in T without a station at b (dist(a,q)=3, dist(a,c)=4).
        V = ('a', 'm', 'b', 'n', 'c', 'q')
        E = path(('a', 'm', 'b', 'n', 'c')) + [('b', 'q')]
        i = inst(V, ('a', 'b'), ('c', 'q'), E, 2)
        x = self.st(i, ())
        self.assertEqual(x.status, I_)
        self.assertEqual(x.hall_origins, ('a',))
        self.assertEqual(x.hall_destinations, ())
        self.assertEqual(self.st(i, ('b',)).status, V_)  # terminal used as station

    def test_destination_without_station_does_not_recharge(self):
        # a-m-t1-n-t2, S={a, z}, T={t1? no}: robot from a passes through t1 (destination of nobody
        # else reachable) to t2. S={a,u}, T={t1,t2}; u adjacent to t1 only. r=2.
        V = ('a', 'm', 't1', 'n', 't2', 'u')
        E = path(('a', 'm', 't1', 'n', 't2')) + [('u', 't1')]
        i = inst(V, ('a', 'u'), ('t1', 't2'), E, 2)
        # a reaches t1 (2); t2 is at distance 4 from a and 3 from u -> no one reaches t2.
        self.assertEqual(self.st(i, ()).status, I_)
        self.assertEqual(self.st(i, ('t1',)).status, V_)

    def test_two_recharges_chain(self):
        names = 'abcdefg'  # path length 6, r=2: a->c->e->g
        i = inst(names, ('a',), ('g',), path(names), 2)
        self.assertEqual(self.st(i, ('c', 'e')).status, V_)
        self.assertEqual(self.st(i, ('c',)).status, I_)
        self.assertEqual(self.st(i, ('e',)).status, I_)
        self.assertEqual(self.st(i, ('b', 'd', 'f')).status, V_)
        self.assertEqual(self.st(i, ('b', 'e')).status, I_)  # b->e is 3 > 2

    def test_unlimited_sharing_three_robots_one_station(self):
        V = ('s1', 's2', 's3', 'w', 't1', 't2', 't3')
        E = [(s, 'w') for s in ('s1', 's2', 's3')] + [('w', t) for t in ('t1', 't2', 't3')]
        i = inst(V, ('s1', 's2', 's3'), ('t1', 't2', 't3'), E, 1)
        self.assertEqual(self.st(i, ()).status, I_)
        x = self.st(i, ('w',))
        self.assertEqual((x.status, x.matching_size), (V_, 3))

    def test_kuhn_requires_augmentation(self):
        # s1 reaches {t1,t2}, s2 reaches {t1}. Greedy in sorted order picks s1->t1 and fails.
        V = ('s1', 's2', 't1', 't2')
        i = inst(V, ('s1', 's2'), ('t1', 't2'), [('s1', 't1'), ('s1', 't2'), ('s2', 't1')], 1)
        x = self.st(i, ())
        self.assertEqual(x.status, V_)
        self.assertEqual(set(x.witness), {('s1', 't2'), ('s2', 't1')})

    def test_hall_needs_alternating_expansion(self):
        # s1->{t1}, s2->{t1,t2}, s3->{t2}; t3 isolated. nu=2, minimal violator needs all three.
        V = ('s1', 's2', 's3', 't1', 't2', 't3')
        E = [('s1', 't1'), ('s2', 't1'), ('s2', 't2'), ('s3', 't2')]
        i = inst(V, ('s1', 's2', 's3'), ('t1', 't2', 't3'), E, 1)
        x = self.st(i, ())
        self.assertEqual((x.status, x.matching_size), (I_, 2))
        self.assertEqual(set(x.hall_origins), {'s1', 's2', 's3'})
        self.assertEqual(set(x.hall_destinations), {'t1', 't2'})

    def test_station_at_origin_is_harmless_and_counted(self):
        # starting battery is full regardless; station at s itself adds nothing.
        i = inst('sab', ('s',), ('b',), path('sab'), 1)
        self.assertEqual(self.st(i, ('s',)).status, I_)
        self.assertEqual(self.st(i, ('a',)).status, V_)

    def test_station_at_destination_relays_other_robot(self):
        # s1 - t1 - t2, s2 adjacent t1... s1 must reach t2 via t1 station; s2 takes t1.
        V = ('s1', 't1', 't2', 's2')
        E = [('s1', 't1'), ('t1', 't2'), ('s2', 't1')]
        i = inst(V, ('s1', 's2'), ('t1', 't2'), E, 1)
        self.assertEqual(self.st(i, ()).status, I_)
        self.assertEqual(self.st(i, ('t1',)).status, V_)

    def test_h2_on_two_recharge_chain(self):
        names = 'abcdefg'
        i = inst(names, ('a',), ('g',), path(names), 2)
        # R={c,d,e}: F={a,b,f,g} infeasible. F+{c}: a->c, c->e? e not station -> c->g dist 4 no. INF.
        # F+{d}: a->? b(1),c(2) ; b is station: b->d(2) d station -> f(2) station -> g. VIABLE.
        # F+{e}: a->b->d? d not station; b->c/d; f station reached from d? no. a->b, b reaches up to d;
        #        e at dist 3 from b -> INF.
        c = classify_h2(MatchingOracle(), i, ('c', 'd', 'e'))
        self.assertEqual(c.state, 'CERTIFIED')
        self.assertEqual(set(c.Bhat), {'c', 'e'})
        self.assertEqual(dict(c.coefficients), {'c': 1, 'd': 2, 'e': 1})
        self.assertEqual(c.complement, ('a', 'b', 'f', 'g'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
