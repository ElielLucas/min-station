"""AS02-01..04: testes de AC com oráculo físico externo ao fluxo agregado."""
import importlib.util
import itertools
import unittest

from as02_model_a import Instance, compile_a, prepare_K
from as02_solve import solve
from experiments.cuts.independent_validator import viavel

BACKEND = 'gurobi' if importlib.util.find_spec('gurobipy') else 'scipy-highs'


def tiny_graph(edges, S, T, r=1):
    V = tuple(sorted(set(itertools.chain.from_iterable(edges)) | set(S) | set(T)))
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    # Grafo de alcance derivado do G original: não depende de A ou da U.
    reach = []
    for s in V:
        frontier, visited = {s}, {s}
        for _ in range(r):
            next_frontier = set().union(*(set(x for x, _ in adj[v]) for v in frontier))
            visited |= next_frontier
            frontier = next_frontier
        for t in sorted(visited - {s}):
            reach.append((s, t))
    return Instance(V, tuple(S), tuple(T), tuple(sorted(reach)), r), adj


class TestAS02Model(unittest.TestCase):
    def test_as02_01_rows_domains_and_constraints(self):
        instance, _ = tiny_graph([('a', 'c'), ('b', 'c'), ('c', 'd')], ('a', 'b'), ('c', 'd'))
        groups = (('a',), ('b',))
        K = (frozenset({'c'}),)
        model = compile_a(instance, groups, K)
        n, k, arcs, m = len(instance.V), len(groups), len(instance.A_r), len(instance.S)
        self.assertEqual(model.families,
                         {'A6': 1, 'A1': n*k, 'A2': n*k, 'A4': n*k, 'A3': m, 'A5': n})
        self.assertEqual(len(model.variables), n + k*arcs + k*n + k*m)
        self.assertEqual(sum(v.binary for v in model.variables), n)
        self.assertEqual(len([v for v in model.variables if v.name.startswith('h[')]), 0)
        self.assertEqual(set(model.objective), {model.columns['y', v] for v in instance.V})
        self.assertEqual(model.equations[0].sense, '>=')
        self.assertEqual(model.equations[0].rhs, 1)
        self.assertEqual(sum(v.binary for v in compile_a(instance, groups, relax=True).variables), 0)
        # Inclusão de um ponto S∩T adiciona h somente ao bloco que contém a origem.
        same, _ = tiny_graph([('a', 'b'), ('b', 'c')], ('a', 'b'), ('b', 'c'))
        with_stay = compile_a(same, (('a',), ('b',)))
        self.assertEqual(sum(v.name.startswith('h[') for v in with_stay.variables), 1)
        self.assertEqual(sum(v.name.startswith('p[') for v in with_stay.variables), 4)

    def test_as02_02_invalid_partitions_rejected(self):
        instance, _ = tiny_graph([('a', 'b'), ('b', 'c')], ('a', 'b'), ('b', 'c'))
        for invalid in ([], [()], [('a',)], [('a',), ('a', 'b')], [('a', 'b'), ('c',)],
                        [('a', 'a'), ('b',)]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compile_a(instance, invalid)
        with self.assertRaises(ValueError):
            compile_a(instance, [('a',), ('b',)], (frozenset({'unknown'}),))
        with self.assertRaises(ValueError):
            compile_a(Instance(('a', 'b'), ('a', 'a'), ('b', 'a'), (('a', 'b'),), 1), [('a',)])

    def test_as02_03_04_all_installations_agree_with_independent_physical_oracle(self):
        fixtures = [
            ('line-swap', [('a','b'),('b','c'),('c','d')], ('a','d'), ('b','c'), 1),
            ('line-relay', [('a','b'),('b','c'),('c','d')], ('a','b'), ('b','d'), 1),
            ('cycle', [('a','b'),('b','c'),('c','d'),('d','a')], ('a','c'), ('b','d'), 1),
            ('triangle-overlap', [('a','b'),('a','c'),('b','c')], ('a','b'), ('b','c'), 1),
            ('stay-only', [], ('v',), ('v',), 1),
            ('terminal-hub', [('v','p1'),('v','p2'),('v','p3'),('v','p4')],
             ('v','p1','p2'), ('v','p3','p4'), 1),
            ('longer-autonomy', [('a','b'),('b','c'),('c','d')], ('a','d'), ('b','c'), 2),
        ]
        checked = 0
        for label, edges, S, T, r in fixtures:
            instance, adj = tiny_graph(edges, S, T, r)
            groupsets = [[instance.S], [(s,) for s in instance.S]]
            for groups in groupsets:
                compiled = compile_a(instance, groups, relax=True)
                for bits in itertools.product((0, 1), repeat=len(instance.V)):
                    assignment = dict(zip(instance.V, bits))
                    C = {v for v, used in assignment.items() if used}
                    expected = viavel(S, T, instance.V, adj, r, C)
                    outcome = solve(compiled, fixed_y=assignment, backend=BACKEND)
                    with self.subTest(graph=label, groups=groups, stations=sorted(C)):
                        self.assertIn(outcome.status, {'OPTIMAL', 'INFEASIBLE'})
                        self.assertEqual(outcome.status == 'OPTIMAL', expected)
                    checked += 1
        self.assertGreaterEqual(checked, 200)

    def test_as02_03_k_cuts_do_not_exclude_physical_installations(self):
        instance, adj = tiny_graph([('a', 'b'), ('b', 'c'), ('c', 'd')],
                                   ('a', 'b'), ('c', 'd'))
        K = prepare_K(instance, adj, 1)
        model = compile_a(instance, (instance.S,), K, relax=True)
        for bits in itertools.product((0, 1), repeat=len(instance.V)):
            assignment = dict(zip(instance.V, bits))
            physical = viavel(instance.S, instance.T, instance.V, adj, 1,
                              {v for v, b in assignment.items() if b})
            outcome = solve(model, fixed_y=assignment, backend=BACKEND)
            self.assertEqual(outcome.status == 'OPTIMAL', physical)

    def test_as02_sensor_removed_global_a5_is_detected(self):
        # O sensor confirma que o teste distingue A da T18 defeituosa:
        # sem A5 o LP da estrela cai de 1 para 1/2, testemunha adversa AS01.
        instance, _ = tiny_graph([('a','c'),('b','c'),('c','d')],
                                  ('a','b'), ('c','d'))
        correct = compile_a(instance, (('a',), ('b',)), relax=True)
        mutant = compile_a(instance, (('a',), ('b',)), relax=True)
        mutant.equations = [eq for eq in mutant.equations if not eq.name.startswith('A5[')]
        good = solve(correct, backend=BACKEND)
        bad = solve(mutant, backend=BACKEND)
        self.assertEqual(good.status, 'OPTIMAL')
        self.assertEqual(bad.status, 'OPTIMAL')
        self.assertAlmostEqual(good.objective, 1, delta=1e-6)
        self.assertAlmostEqual(bad.objective, 0.5, delta=1e-6)
        self.assertGreater(good.objective, bad.objective)

    def test_as02_04_integer_objective_matches_exhaustive_physical_optimum(self):
        fixtures = [
            ([('a','b'),('b','c'),('c','d')],('a','d'),('c','b'),1),
            ([('v','p1'),('v','p2'),('v','p3'),('v','p4')],('v','p1','p2'),('v','p3','p4'),1),
            ([('a','b'),('b','c')],('a','b'),('b','c'),1),
        ]
        for edges, S, T, r in fixtures:
            instance, adj = tiny_graph(edges, S, T, r)
            feasible = [sum(bits) for bits in itertools.product((0,1), repeat=len(instance.V))
                        if viavel(S,T,instance.V,adj,r,
                                  {v for v,b in zip(instance.V,bits) if b})]
            physical_opt = min(feasible) if feasible else None
            for groups in ((instance.S,), tuple((s,) for s in instance.S)):
                result = solve(compile_a(instance, groups, relax=False), backend=BACKEND)
                self.assertEqual(result.status, 'OPTIMAL' if feasible else 'INFEASIBLE')
                self.assertEqual(result.objective, physical_opt)


if __name__ == '__main__':
    unittest.main()
