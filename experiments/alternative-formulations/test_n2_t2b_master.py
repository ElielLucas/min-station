"""Entrega 1: testes determinísticos do master/dual, fora do corpus N2.

Requer Gurobi (não ignora testes se dependência/licença faltar). Execute:
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations \
    -p test_n2_t2b_master.py -v
Não é benchmark nem certificação de limites inferiores.
"""
# E402: bootstrap experimental; E741: correspondência com q=(W,I,J).
# ruff: noqa: E402, E741
import itertools
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from gurobipy import GRB
from fcc import B_de, grafo_H
from fcc_k import build_fcc_plus_k, prepare_k
from ms_utils import construir_adjacencia, construir_arcos_alcance
from n2_t2b_master import (
    DuplicateColumnError, RestrictedMaster, StaleDualError, numerical_dual,
)


def instance(V=('a', 'b', 'c'), edges=(('a', 'b'), ('b', 'c')),
             S=('a',), T=('c',), r=1):
    arcs = [(u, v, 1) for u, v in edges for u, v in ((u, v), (v, u))]
    adj = construir_adjacencia(arcs)
    return S, T, V, adj, construir_arcos_alcance(V, adj, r), r


def q(W, I=('a',), J=('c',)):
    return frozenset(W), frozenset(I), frozenset(J)


def tiny_columns(data):
    """Força bruta só dos fixtures n<=5; não usa a validação do novo master."""
    S, T, V, _adj, A_r, _r = data
    H = grafo_H(V, A_r)
    for size in range(1, len(V) + 1):
        for chosen in itertools.combinations(V, size):
            W = frozenset(chosen)
            seen, stack = {chosen[0]}, [chosen[0]]
            while stack:
                for v in H[stack.pop()] & W - seen:
                    seen.add(v)
                    stack.append(v)
            if seen != W:
                continue
            BW = B_de(W, H)
            for k in range(1, min(len(set(S) & BW), len(set(T) & BW)) + 1):
                for I in itertools.combinations(sorted(set(S) & BW), k):
                    for J in itertools.combinations(sorted(set(T) & BW), k):
                        yield q(W, I, J)


class MasterTests(unittest.TestCase):
    def master(self, data=None, **kwargs):
        master = RestrictedMaster(*(data or instance()), **kwargs)
        self.addCleanup(master.dispose)
        return master

    def assert_optimal(self, result, objective):
        self.assertEqual(result.status, GRB.OPTIMAL, result.error)
        self.assertIsNone(result.error)
        self.assertIsNotNone(result.dual)
        self.assertAlmostEqual(result.objective_rmp, objective, places=7)
        self.assertLessEqual(result.dual.checks.max_rc_error, 1e-7)
        self.assertLessEqual(result.dual.checks.duality_gap, 1e-7)
        self.assertLessEqual(result.dual.checks.max_dual_violation, 1e-7)

    def test_path_rmp_three_then_one_is_not_a_lower_bound(self):
        master = self.master()
        self.assertEqual(master.D, ())
        self.assertEqual(master.K, (frozenset({'b'}),))
        self.assertEqual(master.columns, (q('abc'),))
        self.assert_optimal(master.solve(), 3)
        self.assertLess(master.reduced_cost(q('b')), 0)
        old = master.extract_duals()
        master.add_column(q('b'))
        with self.assertRaises(StaleDualError):
            master.reduced_cost(q('b'), snapshot=old)
        with self.assertRaises(RuntimeError):
            master.extract_duals()
        result = master.solve()
        self.assert_optimal(result, 1)
        self.assertEqual(result.scope, 'RMP_NUMERICAL_ONLY')
        self.assertFalse(hasattr(result, 'LB_CG'))
        self.assertFalse(hasattr(result, 'certified'))

    def test_eta_positive_without_relying_on_solver_degeneracy(self):
        vec = numerical_dual(
            ('a',), ('c',), ('a', 'b', 'c'), (),
            pi={'a': 2}, tau={'c': 0}, mu={'a': 0, 'b': 2, 'c': 0}, kappa={},
        )
        self.assertEqual(dict(vec.eta), {'a': 0, 'b': 1, 'c': 0})
        self.assertEqual(vec.L, 1)
        self.assertEqual(vec.column_rc(q('b')), 0)
        self.assertEqual(vec.column_rc(q('abc')), 0)
        # K também contribui a eta; não duplicar a penalização do UB.
        Z = frozenset({'b'})
        vec2 = numerical_dual(
            ('a',), ('c',), ('a', 'b', 'c'), (Z,),
            pi={'a': 2}, tau={'c': 0}, mu={'a': 0, 'b': 2, 'c': 0}, kappa={Z: 3},
        )
        self.assertEqual(vec2.eta['b'], 4)
        self.assertEqual(vec2.L, 1)

    def test_stay_and_independent_terminal_roles(self):
        master = self.master(instance(('a',), (), ('a',), ('a',)))
        self.assertEqual(master.D, (('a', 'a'),))
        self.assert_optimal(master.solve(), 0)
        self.assertEqual(master.primal_values()['d'][('a', 'a')], 1)
        overlap = self.master(instance(S=('a', 'b'), T=('b', 'c')))
        overlap.add_column(q('b', ('a',), ('b',)))
        overlap.add_column(q('b', ('b',), ('c',)))
        self.assertIn(('b', 'b'), overlap.D)
        self.assert_optimal(overlap.solve(), 0)

    def test_bounds_senses_and_column_coefficients(self):
        master = self.master()
        model = master._model  # inspeção da montagem, sem mudar o modelo
        self.assertEqual(model.ModelSense, GRB.MINIMIZE)
        self.assertEqual(model.IsMIP, 0)
        for var in model.getVars():
            self.assertEqual(var.VType, GRB.CONTINUOUS)
            self.assertEqual(var.LB, 0)
            is_y = var.VarName.startswith('y[')
            if is_y:
                self.assertEqual(var.UB, 1)
            else:
                self.assertTrue(math.isinf(var.UB) and var.UB > 0)
            self.assertEqual(var.Obj, 1 if is_y else 0)
        master.add_column(q('b'))
        model.update()
        lam = master._lam[q('b')]
        self.assertEqual(model.getCoeff(master._r1['a'], lam), 1)
        self.assertEqual(model.getCoeff(master._r2['c'], lam), 1)
        for v in master.V:
            self.assertEqual(model.getCoeff(master._r3[v], lam), int(v == 'b'))
            self.assertEqual(master._r3[v].Sense, '<')
        for row in master._k_rows.values():
            self.assertEqual(model.getCoeff(row, lam), 0)
            self.assertEqual(row.Sense, '>')
        direct = self.master(instance(('a', 'b'), (('a', 'b'),), ('a',), ('b',)))
        self.assertTrue(math.isinf(direct._d['a', 'b'].UB)
                        and direct._d['a', 'b'].UB > 0)

    def test_invalid_columns_and_duplicates_do_not_mutate_state(self):
        master = self.master()
        first = master.solve()
        invalid = [q(''), q('ac'), q('b', (), ()), q('b', (), ('c',)),
                   q('b', ('a',), ()), q('a'), q('b', ('c',), ('c',)),
                   q('b', ('a',), ('a',)), q('x'), ('b', 'a'), (None, (), ())]
        for column in invalid:
            with self.subTest(column=column), self.assertRaises(ValueError):
                master.add_column(column)
            self.assertEqual(master.columns, (q('abc'),))
            self.assertIs(master.extract_duals(), first.dual)
        with self.assertRaises(DuplicateColumnError):
            master.add_column((['c', 'b', 'a'], ['a'], ['c']))
        two = self.master(instance(S=('a', 'b'), T=('b', 'c')))
        with self.assertRaises(ValueError):
            two.add_column(q('b', ('a', 'b'), ('c',)))

    def test_connectivity_is_in_H_and_terminals_can_be_stations(self):
        data = instance(tuple('abcde'), tuple(zip('abcd', 'bcde')), r=2,
                        S=('a',), T=('e',))
        master = self.master(data)
        # {b,d} é desconexo em G, mas conexo em G^2 e atende a/e.
        master.add_column(q('bd', ('a',), ('e',)))
        self.assertEqual(master.validate_column(q('bc', ('a',), ('e',))),
                         q('bc', ('a',), ('e',)))
        terminal = self.master(instance(S=('a', 'b'), T=('b', 'c')))
        terminal.add_column(q('b', ('a', 'b'), ('b', 'c')))
        self.assertIn(q('b', ('a', 'b'), ('b', 'c')), terminal.columns)

    def test_k_hash_and_supplied_k_are_preserved(self):
        data = instance()
        K, digest, _ = prepare_k(*data)
        with patch('n2_t2b_master.prepare_k', side_effect=AssertionError('regenerou K')):
            master = self.master(data, K=list(reversed(K)), k_hash=digest)
        self.assertEqual(master.k_hash, digest)
        self.assertEqual(master.K, tuple(K))
        self.assertEqual(master.metadata['n_K'], len(K))
        self.assertEqual(master.metadata['n_K_added'], len(K))
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.master(data, K=K, k_hash='0' * 64)
        with self.assertRaises(ValueError):
            self.master(data, K=[frozenset({'unknown'})])
        with self.assertRaises(ValueError):
            self.master(data, K=[frozenset()])
        # Corte combinatoriamente inválido: instalar b evita {a}.
        with self.assertRaises(RuntimeError):
            self.master(data, K=[frozenset({'a'})])

    def test_row_duals_and_rc_are_mapped_without_sign_loss(self):
        master = self.master()
        master.add_column(q('ab'))
        self.assert_optimal(master.solve(), 2)
        vec = master.extract_duals().values
        self.assertEqual(vec.pi['a'], master._r1['a'].Pi)
        self.assertEqual(vec.tau['c'], master._r2['c'].Pi)
        for v in master.V:
            self.assertEqual(vec.mu[v], -master._r3[v].Pi)
            self.assertGreaterEqual(vec.mu[v], -1e-7)
        for Z in master.K:
            self.assertEqual(vec.kappa[Z], master._k_rows[Z].Pi)
            self.assertGreaterEqual(vec.kappa[Z], -1e-7)
        for column, var in master._lam.items():
            self.assertAlmostEqual(master.reduced_cost(column), var.RC, places=7)
        direct = self.master(instance(S=('a', 'b'), T=('b', 'c')))
        self.assert_optimal(direct.solve(), 0)
        for pair, var in direct._d.items():
            self.assertAlmostEqual(direct.extract_duals().values.direct_rc(pair), var.RC,
                                   places=7)

    def test_degenerate_extension_does_not_require_strict_improvement(self):
        master = self.master()
        master.add_column(q('b'))
        before = master.solve()
        self.assert_optimal(before, 1)
        master.add_column(q('ab'))
        after = master.solve()
        self.assert_optimal(after, 1)
        self.assertLessEqual(after.objective_rmp, before.objective_rmp + 1e-7)
        # Um dual ótimo válido pode dar rc negativo sem ganho imediato.
        K = (frozenset({'b'}),)
        other = self.master()
        other.add_column(q('ab'))
        self.assert_optimal(other.solve(), 2)
        # Usar o dual de custo 2 para Q_R={V,{a,b}}; {b,c} custa -1,
        # mas K + R3 mantêm z_R=2 após a inclusão (colunas se sobrepõem em b).
        vec = numerical_dual(('a',), ('c',), tuple('abc'), K,
                             pi={'a': 2}, tau={'c': 0},
                             mu={'a': 1, 'b': 1, 'c': 0}, kappa={K[0]: 0})
        self.assertEqual(vec.L, 2)
        self.assertEqual(vec.column_rc(q('bc')), -1)
        other.add_column(q('bc'))
        self.assert_optimal(other.solve(), 2)

    def test_snapshot_is_immutable_and_cannot_cross_solve_or_master(self):
        master = self.master()
        old = master.solve().dual
        with self.assertRaises(TypeError):
            old.values.mu['a'] = 100
        master.solve()
        with self.assertRaises(StaleDualError):
            master.reduced_cost(q('b'), snapshot=old)
        another = self.master()
        another.solve()
        with self.assertRaises(StaleDualError):
            another.reduced_cost(q('b'), snapshot=master.extract_duals())

    def test_nonoptimal_status_has_no_duals_or_objective_and_can_resume(self):
        master = self.master()
        with self.assertRaises(RuntimeError):
            master.extract_duals()
        result = master.solve(params={'TimeLimit': 0, 'Presolve': 0})
        self.assertEqual(result.status, GRB.TIME_LIMIT)
        self.assertEqual(result.status_name, 'TIME_LIMIT')
        self.assertIsNone(result.dual)
        self.assertIsNone(result.objective_rmp)
        with self.assertRaises(RuntimeError):
            master.extract_duals()
        self.assert_optimal(master.solve(), 3)  # limite anterior não vaza

    def test_bad_graphs_and_inconsistent_reachability_are_rejected(self):
        data = instance()
        S, T, V, adj, A_r, r = data
        bad = [(S, T, V, adj, A_r[:-1], r),
               (S, T, V, adj, A_r, 0), (S, (), V, adj, A_r, r),
               (('x',), T, V, adj, A_r, r),
               (S, T, V, {'a': [('b', 1)], 'b': [('c', 1)]}, A_r, r)]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.master(args)

    def test_nonfinite_duals_and_missing_indices_are_rejected(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ValueError):
                numerical_dual(('a',), ('c',), tuple('abc'), (),
                               pi={'a': value}, tau={'c': 0},
                               mu=dict.fromkeys('abc', 0), kappa={})
        with self.assertRaises(ValueError):
            numerical_dual(('a',), ('c',), tuple('abc'), (),
                           pi={}, tau={'c': 0}, mu=dict.fromkeys('abc', 0), kappa={})

    def test_no_output_files_and_solver_failure_is_explicit(self):
        import gurobipy as gp
        master = self.master()
        master.solve()
        with patch.object(gp.Model, 'optimize', side_effect=gp.GurobiError(10009, 'test')):
            result = master.solve()
        self.assertIsNone(result.dual)
        self.assertEqual(result.status_name, 'SOLVER_ERROR')
        self.assertIn('10009', result.error)
        with self.assertRaises(RuntimeError):
            master.extract_duals()
        # Nem LogFile nem outras saídas de solver são aceitas pela API.
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):
                master.solve(params={'LogFile': str(Path(path) / 'n2.log')})
            self.assertEqual(list(Path(path).iterdir()), [])
        self.assert_optimal(master.solve(), 3)

    def test_full_tiny_master_matches_existing_fcc_plus_k(self):
        fixtures = [instance(),
                    instance(tuple('abcd'), tuple(zip('abc', 'bcd')), ('a',), ('d',)),
                    instance(S=('a', 'b'), T=('b', 'c')),
                    instance(tuple('abcde'), (('a', 'c'), ('b', 'c'), ('c', 'd'),
                                             ('c', 'e')), ('a', 'b'), ('d', 'e')),
                    instance(tuple('abcde'), tuple(zip('abcde', 'bcdea')),
                             ('a', 'c'), ('c', 'e'), 2)]
        for data in fixtures:
            with self.subTest(data=data):
                K, digest, _ = prepare_k(*data)
                master = self.master(data, K=K, k_hash=digest)
                for column in tiny_columns(data):
                    if column not in master.columns:
                        master.add_column(column)
                ref, _y, _extra, meta = build_fcc_plus_k(*data, K=K, k_hash=digest)
                try:
                    ref.Params.Threads = 1
                    ref.Params.Seed = 42
                    ref.optimize()
                    self.assertEqual(ref.Status, GRB.OPTIMAL)
                    self.assert_optimal(master.solve(), ref.ObjVal)
                    self.assertEqual(master.k_hash, meta['k_hash'])
                finally:
                    ref.dispose()


if __name__ == '__main__':
    unittest.main()
