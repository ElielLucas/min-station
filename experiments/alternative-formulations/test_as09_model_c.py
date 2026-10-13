"""AS09 initial verification: explicit C rows, physical witness, LP projections.

Numerical samples do NOT replace the pending analytic U<->C y-fiber proof.
"""
import itertools
import random
import unittest

from as02_model_a import Instance, compile_u
from as02_solve import solve
from as09_model_c import compile_c, dimension_estimate, prepare_physical_graph
from experiments.cuts.independent_validator import viavel

BACKEND = 'scipy-highs'


def sample(edges, S, T, r):
    V = tuple(sorted(set(S) | set(T) | {v for uv in edges for v in uv}))
    adj = {v: [] for v in V}
    for u, v in edges:
        adj[u].append((v, 1))
        adj[v].append((u, 1))
    reach = []
    for s in V:
        seen = {s}
        front = {s}
        for _ in range(r):
            front = {n for v in front for n, _ in adj[v]} - seen
            seen.update(front)
        reach.extend((s, t) for t in sorted(seen - {s}))
    return Instance(V, tuple(S), tuple(T), tuple(sorted(reach)), r), adj


class TestAS09C(unittest.TestCase):
    def test_dimensions_and_levels(self):
        inst, adj = sample([('a','b'),('b','c')], ('a',), ('c',), 2)
        pg = prepare_physical_graph(inst, adj)
        C = compile_c(inst, adj, K=[('b',)], relax=True)
        d = dimension_estimate(inst, pg, 1)
        self.assertEqual(len(C.variables), d['n_variables'])
        self.assertEqual(len(C.equations), d['n_constraints'])
        self.assertEqual(C.families, {'C1': 9, 'C2': 1, 'C3': 3, 'K': 1})
        self.assertEqual(d['n_movement_variables'], 8)
        self.assertEqual(d['n_recharge_variables'], 6)
        self.assertFalse(any(v.binary for v in C.variables))
        M = compile_c(inst, adj, relax=False)
        self.assertEqual(sum(v.binary for v in M.variables), len(inst.V))

    def test_validation_refuses_weighted_or_directed(self):
        inst, adj = sample([('a','b')], ('a',), ('b',), 1)
        with self.assertRaisesRegex(ValueError, 'unitário'):
            compile_c(inst, {'a': [('b', 2)], 'b': [('a', 2)]})
        with self.assertRaisesRegex(ValueError, 'não direcionado'):
            compile_c(inst, {'a': [('b', 1)], 'b': []})
        with self.assertRaises(ValueError):
            compile_c(inst, {'a': [('b', 1), ('b', 1)], 'b': [('a', 1)]})

    def test_a_v_b_requires_station_for_r1(self):
        inst, adj = sample([('a','v'),('v','b')], ('a',), ('b',), 1)
        C = compile_c(inst, adj)
        self.assertAlmostEqual(solve(C, backend=BACKEND).objective, 1)
        for y in ({'a':0,'v':0,'b':0}, {'a':0,'v':1,'b':0}):
            actual = solve(C, fixed_y=y, backend=BACKEND)
            self.assertEqual(actual.status == 'OPTIMAL', bool(y['v']))

    def test_overlap_zero_length_and_destination_transit(self):
        inst, adj = sample([('a','b'),('b','c')], ('a','b'), ('b','c'), 1)
        C = compile_c(inst, adj)
        self.assertAlmostEqual(solve(C, backend=BACKEND).objective, 0)
        # a->b and b->c can be paired without installing at b.
        self.assertEqual(solve(C, fixed_y={'a':0,'b':0,'c':0}, backend=BACKEND).status,'OPTIMAL')
        stay, ad = sample([], ('v',), ('v',), 1)
        self.assertAlmostEqual(solve(compile_c(stay, ad), backend=BACKEND).objective, 0)

    def test_c3_is_cumulative_not_per_level(self):
        inst, adj = sample([('a','c'),('c','b')], ('a','b'), ('a','b'), 2)
        C = compile_c(inst, adj)
        row = next(r for r in C.equations if r.name == 'C3[c]')
        coeffs = {key: dict(row.terms).get(j, 0) for key,j in C.columns.items() if key[0] in ('y','z') and key[1]=='c'}
        self.assertEqual(coeffs[('z','c',1)], 1)
        self.assertEqual(coeffs[('z','c',2)], 1)
        self.assertEqual(coeffs[('y','c')], -2)
        # y=.5, z1=z2=1 passes *individual* zq <= m*y but fails total z1+z2 <=m*y.
        self.assertGreater(1+1 - 2*.5, 0)

    def test_t18_terminal_star_rejects_half_station(self):
        # S={a,b}, T={c,d}, G: a-c, b-c, c-d; r=1.
        # The only compatible two routes are a->c and b->c->d,
        # so station c must be fully active, even in the LP.
        inst, adj = sample([('a','c'),('b','c'),('c','d')], ('a','b'), ('c','d'), 1)
        C = compile_c(inst, adj, relax=True)
        U = compile_u(inst, relax=True)
        self.assertAlmostEqual(solve(C,backend=BACKEND).objective,1.0)
        self.assertAlmostEqual(solve(U,backend=BACKEND).objective,1.0)
        self.assertEqual(solve(C, fixed_y={'a':0,'b':0,'c':.5,'d':0}, backend=BACKEND).status,
                         'INFEASIBLE')

    def test_every_binary_installation_against_physical_oracle(self):
        cases = [
            ('line', [('a','v'),('v','b')], ('a',), ('b',), 1),
            ('overlap', [('a','b'),('b','c')], ('a','b'), ('b','c'), 1),
            ('hub', [('c',str(i)) for i in range(4)], ('0','1'), ('2','3'), 2),
            ('cycle', [('a','b'),('b','c'),('c','d'),('d','a')], ('a','c'), ('b','d'), 2),
        ]
        verified = 0
        for label, edges, S, T, r in cases:
            inst, adj = sample(edges, S, T, r)
            C = compile_c(inst, adj)
            for bits in itertools.product([0, 1], repeat=len(inst.V)):
                y = dict(zip(inst.V, bits))
                result = solve(C, fixed_y=y, backend=BACKEND)
                expected = viavel(S, T, inst.V, adj, r, set(v for v in inst.V if y[v]))
                with self.subTest(case=label, y=y):
                    self.assertEqual(result.status in ('OPTIMAL','INFEASIBLE'), True)
                    self.assertEqual(result.status=='OPTIMAL', expected)
                verified+=1
        self.assertGreater(verified,35)

    def test_lp_opt_and_fixed_fibers_against_u_numerical(self):
        rng = random.Random(9026)
        checks = 0
        for k in range(28):
            n = rng.randint(3, 6)
            vertices = [str(i) for i in range(n)]
            edges = {(str(i-1),str(i)) for i in range(1,n)}
            edges |= {(str(i),str(j)) for i in range(n) for j in range(i+2,n) if rng.random() < .27}
            m = rng.randint(1, min(3,n))
            S = tuple(rng.sample(vertices, m))
            T = tuple(rng.sample(vertices, m))
            r = rng.randint(1,3)
            inst,adj = sample(sorted(edges),S,T,r)
            C,U = compile_c(inst,adj),compile_u(inst,relax=True)
            got_c,got_u = solve(C,backend=BACKEND),solve(U,backend=BACKEND)
            with self.subTest(case=k, S=S, T=T, r=r):
                self.assertEqual(got_c.status, got_u.status)
                if got_c.status=='OPTIMAL':
                    self.assertAlmostEqual(got_c.objective,got_u.objective,places=6)
            # Numeric fiber equality sampled at fractional station vectors.
            for _ in range(4):
                y = {v:rng.choice((0,.25,.5,.75,1)) for v in inst.V}
                fixed_c, fixed_u = solve(C, fixed_y=y,backend=BACKEND),solve(U,fixed_y=y,backend=BACKEND)
                with self.subTest(case=k,y=y):
                    self.assertEqual(fixed_c.status, fixed_u.status)
                checks+=1
        self.assertEqual(checks,112)

if __name__=='__main__':
    unittest.main()
