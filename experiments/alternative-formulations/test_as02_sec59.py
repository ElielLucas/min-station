"""AS02-05: regressão LP numérica Sec59(L=7), com K congelado C1+C2+C4-DM."""
import importlib.util
import unittest

from as02_model_a import Instance, compile_a, compile_u, prepare_K
from as02_solve import solve
from experiments.cuts.synthetic import make_Sec59

BACKEND = 'gurobi' if importlib.util.find_spec('gurobipy') else 'scipy-highs'


class TestAS02Sec59(unittest.TestCase):
    def test_as02_05_sec59_lp_control_and_grouped(self):
        S, T, V, adj, ar, r, _ = make_Sec59(L=7, r=1)
        instance = Instance(tuple(V), tuple(S), tuple(T), tuple(ar), r)
        K = prepare_K(instance, adj, r)
        self.assertGreater(len(K), 0)
        u = solve(compile_u(instance, K, relax=True), backend=BACKEND)
        a = solve(compile_a(instance, (('s1','s2'),('s3',)), K, relax=True), backend=BACKEND)
        self.assertEqual(u.status, 'OPTIMAL')
        self.assertEqual(a.status, 'OPTIMAL')
        self.assertAlmostEqual(u.objective, 11/3, delta=1e-6)
        self.assertAlmostEqual(a.objective, 9/2, delta=1e-6)
        self.assertLess(u.objective, a.objective)
        one = solve(compile_a(instance, (S,), K, relax=True), backend=BACKEND)
        self.assertAlmostEqual(one.objective, u.objective, delta=1e-6)


if __name__ == '__main__':
    unittest.main()
