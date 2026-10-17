"""AS28 — auditoria de C3-cut e protocolo de triagem independente de Gurobi."""
from __future__ import annotations

import itertools
import random
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from independent_validator import viavel
from experiments.cuts.c3_cut_screen_as28 import (
    _one_terminal, _hits_all_paths, screen_c3, select_terminals,
)
from experiments.cuts.analyze_c3_lp_as28 import analyze


def small_graphs():
    rng = random.Random(2803)
    for _ in range(24):
        n = rng.randint(4, 7)
        V = [f'v{i}' for i in range(n)]
        E = {(min(V[j], V[j-1]), max(V[j], V[j-1])) for j in range(1, n)}
        E |= {tuple(sorted(rng.sample(V, 2))) for _ in range(n)}
        m = rng.randint(1, min(3, n))
        S, T = rng.sample(V, m), rng.sample(V, m)
        adj = {v: [] for v in V}
        for u, v in E:
            adj[u].append((v, 1))
            adj[v].append((u, 1))
        r = rng.choice((1, 2))
        arcs = set()
        for s in V:
            frontier = {s}
            seen = {s}
            for _ in range(r):
                nxt = {v for u in frontier for v, _ in adj[u]}-seen
                seen |= nxt
                frontier = nxt
            arcs |= {(s, v) for v in seen if v != s}
        y = {v: rng.choice((0., .2, .33, .5, .8, 1.)) for v in V}
        yield V, S, T, adj, r, tuple(sorted(arcs)), y


class C3ScreenMathTests(unittest.TestCase):
    def test_known_path_violation(self):
        arcs = (('s', 'a'), ('a', 's'), ('a', 't'), ('t', 'a'))
        result = _one_terminal('s', ('t',), arcs, {'a': .25}, 'origin', 1e-6)
        self.assertEqual(result['status'], 'VIOLATED')
        self.assertEqual(result['cut'], ('a',))
        self.assertAlmostEqual(result['lhs'], .25)

    def test_direct_arc_no_c3(self):
        self.assertEqual(_one_terminal('s', ('t',), [('s', 't')], {}, 'origin', 1e-6)['status'],
                         'NO_VIOLATION')

    def test_source_intersects_dest_stays_free(self):
        self.assertEqual(_one_terminal('a', ('a',), (), {}, 'origin', 1e-6)['status'],
                         'NO_VIOLATION')

    def test_dest_symmetry(self):
        arcs = [('s', 'a'), ('a', 's'), ('a', 't'), ('t', 'a')]
        result = _one_terminal('t', ('s',), arcs, {'a': .1}, 'destination', 1e-6)
        self.assertEqual(result['cut'], ('a',))

    def test_invalid_topology_rejected(self):
        self.assertFalse(_hits_all_paths('s', {'t'}, [('s','t')], {'a'}))
        self.assertTrue(_hits_all_paths('s', {'t'}, [('s','a'), ('a','t')], {'a'}))

    def test_selection_deterministic_and_bounded(self):
        S = [str(i) for i in range(21)]
        self.assertEqual(select_terminals(S,'x','origin',8), select_terminals(S[::-1],'x','origin',8))
        self.assertEqual(len(select_terminals(S,'x','origin',8)),8)
        with self.assertRaises(ValueError):
            select_terminals(S, 'x','origin',-1)

    def test_exhaustive_cut_validity_against_independent_physical_oracle(self):
        checked = 0
        for V,S,T,adj,r,arcs,y in small_graphs():
            for side, origins, targets in (('origin',S,T),('destination',T,S)):
                for root in origins:
                    result = _one_terminal(root, targets, arcs, y, side, 1e-6)
                    if result['status'] != 'VIOLATED':
                        continue
                    checked += 1
                    cut = set(result['cut'])
                    # Verifica TODOS os conjuntos fisicamente viaveis do microcaso,
                    # usando BFS de bateria + matching, sem chamar o maxflow C3.
                    for bits in itertools.product((0,1), repeat=len(V)):
                        C = {v for v, enabled in zip(V,bits) if enabled}
                        if viavel(S,T,V,adj,r,C):
                            self.assertTrue(C & cut, (V,S,T,r,side,root,cut,C))
        self.assertGreater(checked, 0)

    def test_scan_budget_not_global_closure(self):
        result = screen_c3(['s'],['t'], [('s','a'),('a','t')], {'a':0.1},
                           case_name='mini',sources_per_side=1,max_seconds=10.)
        self.assertEqual(result['status'],'COMPLETE_SELECTED')
        self.assertFalse(result['global_c3_closed'])
        self.assertGreaterEqual(result['emitted'],1)
        partial = screen_c3(['s'],['t'], [('s','a'),('a','t')], {'a':0.1},
                            case_name='mini', sources_per_side=1,max_seconds=0.)
        self.assertEqual(partial['status'],'PARTIAL_TIME_BUDGET')

    def test_no_signal_gate_is_not_global_stop(self):
        from copy import deepcopy
        cases=[{'name': f'c{i}','raw_graph_id':f'g{i}'} for i in range(4)]
        plan={'cases':cases,'arms':['U_K','U_K_C3'],
              'gate':{'minimum_relative_gain':.01,'minimum_independent_raw_graphs':2,
                      'maximum_cost_multiple':2,'min_paired_optimal':4}}
        rows=[]
        for case in cases:
            for arm in plan['arms']:
                rows.append({'name':case['name'],'arm_id':arm,'status':'OPTIMAL',
                            'lp_objective':5. if arm=='U_K' else 5.001,
                            'elapsed_wall_s':1. if arm=='U_K' else 1.2,
                            'complete_selected_all_scans':True,'cut_cap_reached':False,
                            'n_c3_cuts':1})
        summary=analyze(plan,{'mode':'LP','cases':[c['name'] for c in cases]},rows)
        self.assertEqual(summary['classification'],'NO_SIGNAL_BOUNDED_POLICY')
        self.assertFalse(summary['mip_automatically_authorized'])
        rows[1]['lp_objective']=5.5
        rows[3]['lp_objective']=5.5
        summary=analyze(plan,{'mode':'LP','cases':[c['name'] for c in cases]},rows)
        self.assertEqual(summary['classification'],'PROMISING_FOR_INDEPENDENT_REVIEW')


if __name__ == '__main__':
    unittest.main()
