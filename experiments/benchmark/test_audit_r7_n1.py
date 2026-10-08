#!/usr/bin/env python3
"""Testes offline N1-T4 sem Gurobi."""
import unittest
from audit_r7_n1 import Reach, component_matching, matching_hall


class AuditR7Tests(unittest.TestCase):
    def test_hall_without_degree_zero(self):
        reach = {'s0': {'t0'}, 's1': {'t0'}}
        n, X, N, deficit = matching_hall(['s0', 's1'], reach)
        self.assertEqual(n, 1)
        self.assertEqual(set(X), {'s0', 's1'})
        self.assertEqual(N, ['t0'])
        self.assertEqual(deficit, 1)
        self.assertTrue(all(reach[s] for s in reach))

    def test_hall_with_zero_degree(self):
        n, X, N, deficit = matching_hall(['s0','s1'], {'s0':{'t0'},'s1':set()})
        self.assertEqual((n, deficit), (1,1))
        self.assertIn('s1', X)
        self.assertEqual(N, [])

    def test_permanence_without_stations(self):
        adj = {'s0': {'t0':1}, 't0': {'s0':1}}
        r = Reach(adj, 1)
        graph, comps = component_matching(['s0'], ['s0'], (), r)
        self.assertEqual(graph['s0'], {'s0'})
        self.assertEqual(comps, [])
        self.assertEqual(matching_hall(['s0'], graph)[0], 1)

    def test_components_independent(self):
        adj = {'s0': {'c':1}, 'c': {'s0':1,'t0':1},
               't0': {'c':1}, 's1': {'c2':1}, 'c2': {'s1':1,'t1':1}, 't1': {'c2':1}}
        r = Reach(adj, 1)
        graph, comps = component_matching(['s0','s1'], ['t0','t1'], {'c','c2'}, r)
        self.assertEqual(len(comps), 2)
        self.assertEqual(graph['s0'], {'t0'})
        self.assertEqual(graph['s1'], {'t1'})
        self.assertEqual(matching_hall(['s0','s1'], graph)[0], 2)


if __name__ == '__main__':
    unittest.main()
