#!/usr/bin/env python3
"""Testes offline N1-T3 (sem Gurobi). Não certificam LP/equivalência."""
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for path in (str(HERE), str(ROOT), str(ROOT / 'experiments' / 'cuts')):
    if path not in sys.path:
        sys.path.insert(0, path)

from fc3 import bound_network_arcs, stage_arcs, _validate_inputs
from independent_validator import viavel
from source_controls_fc3_n1 import make_source_c5, make_source_g2, make_two_components


class FC3OfflineTests(unittest.TestCase):
    def test_arcs_complete(self):
        # 8 arcos não uso, 27 arcos uso (inclui 8 com R=∅)
        arcs = list(stage_arcs(7))
        self.assertEqual(len(arcs), 35)
        self.assertEqual(sum(not a[3] for a in arcs), 8)
        self.assertEqual(sum(a[3] for a in arcs), 27)
        self.assertEqual(sum(a[3] and a[1] == 0 for a in arcs), 8)
        self.assertTrue(all((b & r) == 0 and dest == b | r for b, r, dest, _ in arcs))
        self.assertEqual(len(set(arcs)), len(arcs))

    def test_eligibility(self):
        for mask in range(8):
            arcs = list(stage_arcs(mask))
            self.assertEqual(sum(not x[3] for x in arcs), 8)
            self.assertTrue(all((r & ~mask) == 0 for _, r, _, use in arcs if use))

    def test_bound(self):
        self.assertEqual(bound_network_arcs(2, 100), 0)
        self.assertEqual(bound_network_arcs(3, 1), 86)
        self.assertEqual(bound_network_arcs(5, 0), 160)

    def test_source_counts_and_connectivity(self):
        for fab, n, m in ((make_source_g2, 20, 7), (make_source_c5, 15, 5)):
            S, T, V, adj, _, _, _ = fab()
            self.assertEqual((len(V), len(S), len(T)), (n, m, m))
            self.assertTrue(set(S).isdisjoint(T))
            _validate_inputs(S, T, V)
            seen, stack = {V[0]}, [V[0]]
            while stack:
                u = stack.pop()
                for v, _ in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            self.assertEqual(seen, set(V))

    def test_two_components_true_feasible(self):
        S, T, V, adj, _, r, meta = make_two_components()
        C = meta['witness_C']
        self.assertTrue(viavel(S, T, V, adj, r, C))
        self.assertEqual(len(C), 2)
        self.assertNotIn('y', [v for v, _ in adj[C[0]]])
        self.assertNotIn('x', [v for v, _ in adj[C[1]]])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            _validate_inputs(['a'], [], ['a'])
        with self.assertRaises(ValueError):
            _validate_inputs(['a'], ['b'], ['a'])
        with self.assertRaises(ValueError):
            _validate_inputs(['a'], ['a'], ['a', 'a'])


if __name__ == '__main__':
    unittest.main()
