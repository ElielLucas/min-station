"""AS-08/T2a: controles que discriminam B correta de versões defeituosas."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from as02_model_a import Instance, compile_a, compile_u
from as02_solve import solve
from as08_b_exact import PathEnumerationLimit, check_b_system, compile_b, enumerate_paths
from run_as08_t2a import (FIXTURES, build_fixture, run_case, verify, write_results,
                          y_vectors, VERSION)

BACKEND = 'gurobi' if importlib.util.find_spec('gurobipy') else 'scipy-highs'


class TestAS08T2a(unittest.TestCase):
    def get(self, name):
        f = next(f for f in FIXTURES if f.name == name)
        return build_fixture(f)

    def test_as08_01_s_t_overlap_has_zero_path(self):
        ins, _ = self.get('e5-origin-destination-swap')
        paths = enumerate_paths(ins)
        self.assertIn(('v',), paths.by_source['v'])
        self.assertIn(('v', 'b'), paths.by_source['v'])
        self.assertIn(('a', 'v'), paths.by_source['a'])
        self.assertEqual(len(paths.by_source), 2)

    def test_as08_01_destinations_are_allowed_internal(self):
        ins, _ = self.get('e1-b4-star')
        paths = enumerate_paths(ins)
        self.assertIn(('a', 'c', 'd'), paths.by_source['a'])
        self.assertIn('c', ins.T)

    def test_as08_01_cycle_removed_and_no_duplicate_paths(self):
        ins, _ = self.get('overlap-triangle')
        paths = enumerate_paths(ins)
        for s in ins.S:
            self.assertEqual(len(set(paths.by_source[s])), len(paths.by_source[s]))
            for p in paths.by_source[s]:
                self.assertEqual(len(set(p)), len(p))

    def test_as08_01_unreachable_origin_zero_columns(self):
        ins, _ = self.get('infeasible-components')
        paths = enumerate_paths(ins)
        self.assertEqual(paths.count, 0)
        b, _ = compile_b(ins, relax=True)
        self.assertEqual(solve(b, backend=BACKEND).status, 'INFEASIBLE')

    def test_as08_01_enumeration_limit_refuses_incomplete_model(self):
        ins, _ = self.get('e1-b4-star')
        with self.assertRaises(PathEnumerationLimit):
            compile_b(ins, max_paths=1)
        with self.assertRaises(PathEnumerationLimit):
            compile_b(ins, max_vertices=2)
        with self.assertRaises(ValueError):
            enumerate_paths(ins, max_paths=0)

    def test_as08_02_rows_correct_and_types(self):
        ins, _ = self.get('e1-b4-star')
        c, paths = compile_b(ins, K=[{'c'}], relax=False)
        self.assertEqual(c.families['B1'], len(ins.S))
        self.assertEqual(c.families['B2'], len(ins.T))
        self.assertEqual(c.families['B3'], len(ins.S) * (len(ins.V)-1))
        self.assertEqual(c.families['B4'], 2)  # c,d are T not S
        self.assertEqual(c.families['BK'], 1)
        self.assertEqual(len([v for v in c.variables if v.binary]), len(ins.V))
        self.assertEqual(len([v for v in c.variables if v.name.startswith('x[')]), paths.count)
        self.assertEqual(len(c.objective), len(ins.V))
        lp, _ = compile_b(ins, relax=True)
        self.assertTrue(all(not v.binary for v in lp.variables))
        self.assertEqual(set(c.columns), set(lp.columns))

    def test_as08_02_b4_is_necessary_without_k_mutation_sensor(self):
        ins, _ = self.get('e1-b4-star')
        b, _ = compile_b(ins)
        mutant, _ = compile_b(ins, global_links=False)
        good = solve(b, backend=BACKEND)
        bad = solve(mutant, backend=BACKEND)
        self.assertEqual(good.status, 'OPTIMAL')
        self.assertEqual(bad.status, 'OPTIMAL')
        self.assertAlmostEqual(good.objective, 1.0, places=6)
        self.assertAlmostEqual(bad.objective, 0.5, places=6)

    def test_as08_02_explicit_fractional_witness_rejected_by_b4(self):
        ins, _ = self.get('e1-b4-star')
        b, paths = compile_b(ins)
        x = {(s, p): 0. for s in ins.S for p in paths.by_source[s]}
        for s in ins.S:
            x[s, (s, 'c')] = 0.5
            x[s, (s, 'c', 'd')] = 0.5
        y = {v: (0.5 if v == 'c' else 0.) for v in ins.V}
        result = check_b_system(b, ins, paths, y, x)
        self.assertFalse(result['feasible'])
        self.assertEqual(result['violated_rows'], ['B4[c]'])
        mutant, _ = compile_b(ins, global_links=False)
        self.assertTrue(check_b_system(mutant, ins, paths, y, x)['feasible'])

    def test_as08_02_b4_redundant_when_all_destinations_are_origins(self):
        ins, _ = self.get('e4-stay-only')
        b, _ = compile_b(ins)
        self.assertNotIn('B4', b.families)
        self.assertEqual(solve(b, backend=BACKEND).objective, 0.)

    def test_as08_03_lp_b_a_objective_and_u_dominance(self):
        for f in FIXTURES:
            ins, _ = build_fixture(f)
            b, _ = compile_b(ins)
            a = compile_a(ins, ((s,) for s in ins.S), relax=True)
            u = compile_u(ins, relax=True)
            ob, oa, ou = [solve(c, backend=BACKEND) for c in (b,a,u)]
            with self.subTest(f=f.name):
                self.assertEqual(ob.status, oa.status)
                if ob.status == 'OPTIMAL':
                    self.assertAlmostEqual(ob.objective, oa.objective, delta=1e-6)
                    self.assertLessEqual(ou.objective, ob.objective + 1e-6)
                else:
                    self.assertEqual(ob.status, 'INFEASIBLE')

    def test_as08_03_specific_y_fibers_and_physical(self):
        for name in ('e1-b4-star', 'e4-stay-only', 'e5-origin-destination-swap',
                     'infeasible-components', 'autonomy-two'):
            f = next(f for f in FIXTURES if f.name == name)
            row = run_case(f, backend=BACKEND, seconds=10, max_vertices=9,
                           max_paths=20000, fractionals=15, seed=42)
            with self.subTest(name=name):
                self.assertEqual(row['status'], 'PASS', row.get('counterexamples'))
                for mode in ('no_k', 'with_k'):
                    self.assertEqual(row['checks'][mode]['fixed_y_binary'], 2**len(row['instance']['V']))
                    self.assertGreater(row['checks'][mode]['fixed_y_fractional'], 0)
                    self.assertEqual(row['checks'][mode]['mip_optimum']['status'],
                                     'OPTIMAL' if row['checks'][mode]['physical_optimum'] is not None
                                     else 'INFEASIBLE')

    def test_as08_03_known_witnesses(self):
        for name, b_expected, u_expected in (
            ('e1-b4-star', 1., 1.),
            ('e2-disaggregated-hub', 1., .5),
            ('e3-lp-gap', .5, .5),
        ):
            ins, _ = self.get(name)
            b, _ = compile_b(ins)
            u = compile_u(ins, relax=True)
            with self.subTest(name=name):
                self.assertAlmostEqual(solve(b, backend=BACKEND).objective, b_expected)
                self.assertAlmostEqual(solve(u, backend=BACKEND).objective, u_expected)

    def test_as08_03_determinism(self):
        ins, _ = self.get('e1-b4-star')
        self.assertEqual(enumerate_paths(ins), enumerate_paths(ins))
        self.assertEqual(y_vectors(ins.V, max_fractional=9, seed=42),
                         y_vectors(ins.V, max_fractional=9, seed=42))

    def test_as08_03_validation_invalid_y_rejected(self):
        ins, _ = self.get('e4-stay-only')
        b, paths = compile_b(ins)
        with self.assertRaises(ValueError):
            check_b_system(b, ins, paths, {}, {})
        with self.assertRaises(ValueError):
            check_b_system(b, ins, paths, {v: 0. for v in ins.V}, {})

    def test_as08_03_result_integrity_and_no_overwrite(self):
        cases = [{'name': f.name, 'status': 'PASS'} for f in FIXTURES]
        payload = {'schema': VERSION, 'backend': BACKEND, 'cases': cases,
                   'decision': 'PASS_EXPLORATORY'}
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'evidence'
            write_results(output, payload)
            self.assertEqual(verify(output)['decision'], 'PASS_EXPLORATORY')
            with self.assertRaises(FileExistsError):
                write_results(output, payload)
            path = output / 'results.json'
            path.write_text(path.read_text() + ' ', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                verify(output)

    def test_as08_03_incomplete_never_passes(self):
        f = next(f for f in FIXTURES if f.name == 'e1-b4-star')
        row = run_case(f, backend=BACKEND, seconds=10, max_vertices=9,
                       max_paths=1, fractionals=4, seed=42)
        self.assertEqual(row['status'], 'INCOMPLETE')
        self.assertEqual(row['reason'], 'PATH_ENUM_LIMIT')


if __name__ == '__main__':
    unittest.main()
