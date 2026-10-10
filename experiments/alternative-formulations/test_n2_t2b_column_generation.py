"""Entrega 3: testes da geração de colunas na raiz, fora do corpus N2.

Requer Gurobi (não ignora testes se dependência/licença faltar). Execute:
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations \
    -p test_n2_t2b_column_generation.py -v
Instâncias minúsculas definidas aqui; não usa os 23 controles N1 (N2-T4).
A comparação com o LP F-CC+K completo (fcc_k.lp_fcc_plus_k) é regressão
numérica, não certificação.
"""
# E402: bootstrap experimental; E741: correspondência com q=(W,I,J).
# ruff: noqa: E402, E741
import dataclasses
import math
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import gurobipy as gp
from fcc_k import lp_fcc_plus_k
from ms_utils import construir_adjacencia, construir_arcos_alcance
from n2_t2b_master import RestrictedMaster
import n2_t2b_column_generation as cg
import n2_t2b_pricing as pr

TOL = 1e-6  # regressão numérica contra o LP completo; não é margem de certificado


def instance(V, edges, S, T, r=1):
    arcs = [(u, v, 1) for a, b in edges for u, v in ((a, b), (b, a))]
    adj = construir_adjacencia(arcs)
    return tuple(S), tuple(T), tuple(V), adj, construir_arcos_alcance(V, adj, r), r


def path(n, S, T, r=1):
    V = [chr(ord('a') + i) for i in range(n)]
    return instance(V, list(zip(V, V[1:])), S, T, r)


def q(W, I, J):
    return frozenset(W), frozenset(I), frozenset(J)


ABC = path(3, 'a', 'c')
K_ABC = [frozenset('b')]


def random_instance(rng):
    n = rng.randint(1, 7)
    V = [f'v{i}' for i in range(n)]
    edges = {(V[rng.randrange(i)], V[i]) for i in range(1, n)}
    for _ in range(rng.randint(0, n)):
        if n > 1:
            a, b = rng.sample(V, 2)
            if (b, a) not in edges:
                edges.add((a, b))
    m = rng.randint(1, min(3, n))
    return instance(V, sorted(edges), rng.sample(V, m), rng.sample(V, m), rng.choice([1, 2]))


class Spy:
    """Pricer que chama price() e permite alterar o resultado (dataclasses.replace)."""

    def __init__(self, transform=None):
        self.transform = transform
        self.calls = []

    def __call__(self, master, snapshot, **kwargs):
        current = master.extract_duals()
        self.calls.append(dict(snapshot=snapshot, is_current=snapshot is current,
                               solve_id=snapshot.solve_id, revision=snapshot.revision,
                               columns=master.columns, params=dict(kwargs['params'])))
        result = pr.price(master, snapshot, **kwargs)
        if self.transform is not None:
            result = self.transform(len(self.calls), master, snapshot, result)
        return result


def replace(result, **changes):
    return dataclasses.replace(result, **changes)


class ColumnGenerationTests(unittest.TestCase):
    def assert_uncertified(self, result):
        self.assertEqual(result.certification_status, pr.UNCERTIFIED)
        self.assertNotEqual(result.convergence_status, 'CERTIFIED')
        self.assertIn(result.stop_reason, cg.STOP_REASONS)
        self.assertEqual(result.scope, 'ROOT_CG_NUMERICAL_ONLY')
        names = {f.name.lower() for f in dataclasses.fields(result)}
        names |= {f.name.lower() for f in dataclasses.fields(cg.IterationRecord)}
        self.assertFalse(any('lb' in n.split('_') or 'lower' in n for n in names))

    # ── 8.1 caminho a–b–c ────────────────────────────────────────────────

    def test_path_abc_reaches_one(self):
        result = cg.run_column_generation(*ABC, K=K_ABC)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertEqual(result.convergence_status, cg.NUMERIC_UNCERTIFIED)
        self.assertAlmostEqual(result.history[0].rmp_objective, 3.0, places=7)
        self.assertAlmostEqual(result.rmp_objective, 1.0, places=7)
        self.assertTrue(result.objective_reflects_all_columns)
        self.assertEqual(result.columns[0], q('abc', 'a', 'c'))
        added = [h.column_added for h in result.history if h.column_added]
        self.assertEqual(len(added), result.columns_added)
        # Qualquer coluna ótima serve; toda solução de valor 1 usa só a estação b.
        self.assertTrue(any(W == {'b'} for W, _I, _J in result.columns))
        self.assertTrue(all(I == {'a'} and J == {'c'} for _W, I, J in added))
        self.assertEqual(result.n_K, 1)

    # ── 8.2 LP completo ──────────────────────────────────────────────────

    def test_stationary_value_matches_full_fcc_k_lp(self):
        rng = random.Random(20261009)
        compared = 0
        for case in range(30):
            data = random_instance(rng)
            result = cg.run_column_generation(*data)
            self.assert_uncertified(result)
            if result.stop_reason != cg.NUMERICAL_STATIONARY:
                continue
            full, meta = lp_fcc_plus_k(*data)
            with self.subTest(case=case, V=data[2], S=data[0], T=data[1], r=data[5]):
                self.assertEqual(result.k_hash, meta['k_hash'])
                self.assertLessEqual(abs(result.rmp_objective - full), TOL)
                compared += 1
        self.assertGreaterEqual(compared, 25)

    # ── 8.3 integridade do ciclo ─────────────────────────────────────────

    def test_cycle_integrity_and_current_snapshots(self):
        data = path(5, 'ab', 'de')
        spy = Spy()
        with patch.object(pr, 'price_vector', side_effect=AssertionError('price_vector usado')):
            result = cg.run_column_generation(*data, pricer=spy)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertTrue(all(c['is_current'] for c in spy.calls))
        ids = [c['solve_id'] for c in spy.calls]
        self.assertEqual(ids, sorted(set(ids)))  # um snapshot novo por chamada
        self.assertEqual(result.columns[0], q('abcde', 'ab', 'de'))
        for call, rec in zip(spy.calls, result.history):
            self.assertEqual((call['solve_id'], call['revision']),
                             (rec.master_solve_id, rec.master_revision))
            self.assertEqual(rec.master_status, 'OPTIMAL')
            if rec.column_added:
                self.assertNotIn(rec.column_added, call['columns'])
                self.assertEqual(rec.columns_after, rec.columns_before + 1)
                self.assertLess(rec.candidate_reduced_cost, -result.settings['entry_tolerance'])
        objs = [h.rmp_objective for h in result.history]
        self.assertTrue(all(b <= a + 1e-7 for a, b in zip(objs, objs[1:])))
        self.assertEqual(len(result.columns), 1 + result.columns_added)
        self.assertEqual(result.pricing_calls, len(spy.calls))
        full, _ = lp_fcc_plus_k(*data)
        self.assertLessEqual(abs(result.rmp_objective - full), TOL)

    def test_degenerate_negative_column_is_not_an_error(self):
        # Sob o dual de Q_R={(V,S,T)}, ({b,c},{a},{d}) tem rc<0 mas z_R fica em 5.
        data = path(5, 'ab', 'de')
        forced = q('bc', 'a', 'd')

        def first_forced(n, master, snapshot, result):
            if n > 1:
                return result
            rc = master.reduced_cost(forced, snapshot=snapshot)
            self.assertLess(rc, -1e-7)
            return replace(result, outcome=pr.NEGATIVE_COLUMN, column=forced, reduced_cost=rc)

        result = cg.run_column_generation(*data, pricer=Spy(first_forced))
        self.assert_uncertified(result)
        self.assertTrue(result.history[1].degenerate_step)
        self.assertAlmostEqual(result.history[1].objective_decrease, 0.0, places=7)
        self.assertGreaterEqual(result.degenerate_steps, 1)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        full, _ = lp_fcc_plus_k(*data)
        self.assertLessEqual(abs(result.rmp_objective - full), TOL)

    # ── 8.4 interrupções e falhas ────────────────────────────────────────

    def test_interrupted_pricing_with_negative_column_is_used(self):
        def interrupted(n, master, snapshot, result):
            if result.outcome == pr.NEGATIVE_COLUMN:
                return replace(result, termination=pr.OTHER_LIMIT, status_name='SOLUTION_LIMIT')
            return result

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(interrupted))
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertIn('interrompido', result.history[0].note)
        self.assertAlmostEqual(result.rmp_objective, 1.0, places=7)

    def test_interrupted_pricing_without_incumbent(self):
        def no_time(master, snapshot, **kwargs):
            kwargs['params'] = dict(kwargs['params'], TimeLimit=0.0)
            return pr.price(master, snapshot, **kwargs)

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=no_time)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.PRICING_INCOMPLETE)
        self.assertEqual(result.history[-1].pricing_outcome, pr.NO_INCUMBENT)
        self.assertEqual(result.convergence_status, cg.NOT_CONVERGED)

    def test_nonnegative_interrupted_pricing_is_not_stationary(self):
        # ObjBoundC forjado "provando" ausência de coluna negativa é ignorado.
        def weak(n, master, snapshot, result):
            return replace(result, outcome=pr.NONNEGATIVE_INCUMBENT, termination=pr.OTHER_LIMIT,
                           status_name='NODE_LIMIT', column=None, reduced_cost=None,
                           solver_bound=1e9)

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(weak))
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.PRICING_INCOMPLETE)
        self.assertEqual(result.history[-1].pricing_solver_bound, 1e9)

    def test_solver_bound_never_blocks_a_negative_column(self):
        def bound(n, master, snapshot, result):
            return replace(result, solver_bound=1e9)

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(bound))
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertAlmostEqual(result.rmp_objective, 1.0, places=7)

    def test_master_interrupted_without_dual(self):
        first = cg.run_column_generation(*ABC, K=K_ABC,
                                         master_params={'IterationLimit': 0, 'Presolve': 0})
        self.assert_uncertified(first)
        self.assertEqual(first.stop_reason, cg.MASTER_FAILURE)
        self.assertIsNone(first.rmp_objective)
        self.assertEqual(first.pricing_calls, 0)
        self.assertEqual(first.history[0].master_status, 'ITERATION_LIMIT')
        # Interrupção na reotimização: z_R anterior preservado, mas desatualizado.
        later = cg.run_column_generation(*ABC, K=K_ABC, master_params={'IterationLimit': 0})
        self.assertEqual(later.stop_reason, cg.MASTER_FAILURE)
        self.assertEqual([h.master_status for h in later.history], ['OPTIMAL', 'ITERATION_LIMIT'])
        self.assertAlmostEqual(later.rmp_objective, 3.0, places=7)
        self.assertFalse(later.objective_reflects_all_columns)
        # Limite por chamada (não global) não vira TIME_LIMIT/WORK_LIMIT global.
        for params in ({'TimeLimit': 0.0}, {'WorkLimit': 0.0}):
            local = cg.run_column_generation(*ABC, K=K_ABC, master_params=params)
            self.assertEqual(local.stop_reason, cg.MASTER_FAILURE)

    def test_duplicate_negative_column_stops_without_loop(self):
        initial = q('abc', 'a', 'c')

        def duplicate(n, master, snapshot, result):
            return replace(result, outcome=pr.NEGATIVE_COLUMN, column=initial,
                           reduced_cost=master.reduced_cost(initial, snapshot=snapshot))

        spy = Spy(duplicate)
        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=spy)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.DUPLICATE_COLUMN)
        self.assertEqual(len(spy.calls), 1)
        self.assertEqual(result.columns, (initial,))

    def test_invalid_column_is_rejected_before_insertion(self):
        def invalid(n, master, snapshot, result):
            return replace(result, column=q('ac', 'a', 'c'))  # desconexo em H

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(invalid))
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)
        self.assertEqual(result.columns_added, 0)
        self.assertEqual(len(result.columns), 1)

    def test_inconsistent_reduced_cost_is_rejected(self):
        def shifted(n, master, snapshot, result):
            return replace(result, reduced_cost=result.reduced_cost - 0.5)

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(shifted))
        self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)
        self.assertIn('inconsistente', result.message)
        self.assertEqual(result.columns_added, 0)

    def test_pricing_failure_statuses(self):
        def failing(master, snapshot, **kwargs):
            with patch.object(gp.Model, 'optimize', side_effect=gp.GurobiError(10001, 'x')):
                return pr.price(master, snapshot, **kwargs)

        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=failing)
        self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)
        self.assertEqual(result.history[-1].pricing_outcome, pr.SOLVER_ERROR)
        forged = Spy(lambda n, m, s, r: replace(r, certification_status='CERTIFIED'))
        result = cg.run_column_generation(*ABC, K=K_ABC, pricer=forged)
        self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)
        self.assertEqual(result.certification_status, pr.UNCERTIFIED)

    def test_master_solver_failure(self):
        with patch.object(gp.Model, 'optimize', side_effect=gp.GurobiError(10009, 'x')):
            result = cg.run_column_generation(*ABC, K=K_ABC)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.MASTER_FAILURE)
        self.assertIn('10009', result.message)

    def test_iteration_limit(self):
        zero = cg.run_column_generation(*ABC, K=K_ABC, max_iterations=0)
        self.assertEqual(zero.stop_reason, cg.ITERATION_LIMIT)
        self.assertEqual(zero.pricing_calls, 0)
        self.assertAlmostEqual(zero.rmp_objective, 3.0, places=7)
        one = cg.run_column_generation(*ABC, K=K_ABC, max_iterations=1)
        self.assert_uncertified(one)
        self.assertEqual(one.stop_reason, cg.ITERATION_LIMIT)
        self.assertEqual(one.pricing_calls, 1)
        self.assertTrue(one.objective_reflects_all_columns)  # master reotimizado
        self.assertAlmostEqual(one.rmp_objective, 1.0, places=7)

    def test_global_work_limit_is_forwarded_and_enforced(self):
        spy = Spy()
        result = cg.run_column_generation(*path(5, 'ab', 'de'), work_limit=164.0, pricer=spy)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        used = 0.0
        for rec in result.history:
            self.assertLessEqual(rec.master_cost.forwarded_limits['WorkLimit'], 164.0 - used + 1e-12)
            used += rec.master_cost.work
            if rec.pricing_cost:
                self.assertLessEqual(rec.pricing_cost.forwarded_limits['WorkLimit'],
                                     164.0 - used + 1e-12)
                used += rec.pricing_cost.work
            self.assertAlmostEqual(rec.cumulative_work, used, places=12)
        self.assertAlmostEqual(result.total_work, used, places=12)
        # Per-call menor que o global: o global não é "binding".
        small = cg.run_column_generation(*ABC, K=K_ABC, work_limit=164.0,
                                         pricing_params={'WorkLimit': 1.0})
        self.assertEqual(small.history[0].pricing_cost.forwarded_limits['WorkLimit'], 1.0)
        self.assertEqual(small.history[0].pricing_cost.global_binding, frozenset())
        expensive = Spy(lambda n, m, s, r: replace(r, work=1e6))
        result = cg.run_column_generation(*ABC, K=K_ABC, work_limit=100.0, pricer=expensive)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.WORK_LIMIT)
        self.assertEqual(len(expensive.calls), 1)
        # Coluna obtida além do orçamento não é inserida; z_R segue atual.
        self.assertEqual(result.columns_added, 0)
        self.assertTrue(result.objective_reflects_all_columns)
        self.assertEqual(cg.run_column_generation(*ABC, K=K_ABC, work_limit=0.0).stop_reason,
                         cg.WORK_LIMIT)

    def test_work_overrun_is_never_stationary(self):
        # Regressão: pricing OPTIMAL sem coluna negativa, mas além do orçamento.
        def overrun_on_second(n, master, snapshot, result):
            return replace(result, work=1e6) if n == 2 else result

        spy = Spy(overrun_on_second)
        result = cg.run_column_generation(*ABC, K=K_ABC, work_limit=100.0, pricer=spy)
        self.assert_uncertified(result)
        last = result.history[-1]
        self.assertEqual(last.pricing_termination, pr.NUMERICALLY_OPTIMAL)
        self.assertEqual(last.pricing_outcome, pr.NONNEGATIVE_INCUMBENT)
        self.assertEqual(result.stop_reason, cg.WORK_LIMIT)
        self.assertEqual(last.decision, cg.WORK_LIMIT)
        self.assertEqual(result.convergence_status, cg.NOT_CONVERGED)
        self.assertGreater(result.total_work, 100.0)  # consumo efetivo registrado
        self.assertAlmostEqual(last.cumulative_work, result.total_work, places=12)
        self.assertIn('ultrapassado', result.message)
        # Sem orçamento, o mesmo Work alto não interfere: estacionário.
        free = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(overrun_on_second))
        self.assertEqual(free.stop_reason, cg.NUMERICAL_STATIONARY)

    def test_master_work_overrun_stops_before_pricing(self):
        original = RestrictedMaster.solve

        def expensive_solve(self, **kwargs):
            return replace(original(self, **kwargs), work=1e6)

        spy = Spy()
        with patch.object(RestrictedMaster, 'solve', expensive_solve):
            result = cg.run_column_generation(*ABC, K=K_ABC, work_limit=100.0, pricer=spy)
        self.assertEqual(result.stop_reason, cg.WORK_LIMIT)
        self.assertEqual(spy.calls, [])
        self.assertEqual(result.history[0].master_status, 'OPTIMAL')

    def test_rc_agreement_tolerance_and_nonfinite_rc(self):
        for bad in (math.nan, math.inf, -1e-9):
            with self.assertRaises(ValueError):
                cg.run_column_generation(*ABC, K=K_ABC, rc_agreement_tolerance=bad)
        for value in (math.nan, math.inf, -math.inf):
            forged = Spy(lambda n, m, s, r, v=value: replace(r, reduced_cost=v))
            with self.subTest(reduced_cost=value):
                result = cg.run_column_generation(*ABC, K=K_ABC, pricer=forged)
                self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)
                self.assertIn('inconsistente', result.message)
                self.assertEqual(result.columns_added, 0)
        # Divergência acima de uma tolerância maior que zero continua rejeitada.
        shifted = Spy(lambda n, m, s, r: replace(r, reduced_cost=r.reduced_cost - 1e-3))
        result = cg.run_column_generation(*ABC, K=K_ABC, rc_agreement_tolerance=1e-4,
                                          pricer=shifted)
        self.assertEqual(result.stop_reason, cg.PRICING_FAILURE)

    def test_negative_work_is_invalid_and_not_discounted(self):
        negative = Spy(lambda n, m, s, r: replace(r, work=-5.0))
        free = cg.run_column_generation(*ABC, K=K_ABC, pricer=negative)
        self.assertEqual(free.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertIsNone(free.total_work)
        self.assertEqual(free.unmeasured_work_calls, free.pricing_calls)
        masters = sum(h.master_cost.work for h in free.history)
        self.assertAlmostEqual(free.measured_work, masters, places=12)  # -5 não descontado
        self.assertGreaterEqual(free.measured_work, 0.0)
        self.assertIsNone(free.history[0].pricing_cost.work)
        self.assertEqual(free.history[0].pricing_cost.raw_work, -5.0)
        budgeted = cg.run_column_generation(*ABC, K=K_ABC, work_limit=164.0,
                                            pricer=Spy(lambda n, m, s, r: replace(r, work=-5.0)))
        self.assertEqual(budgeted.stop_reason, cg.WORK_UNMEASURED)
        self.assertIn('inválido', budgeted.message)
        original = RestrictedMaster.solve

        def negative_master(self, **kwargs):
            return replace(original(self, **kwargs), work=-1.0)

        with patch.object(RestrictedMaster, 'solve', negative_master):
            result = cg.run_column_generation(*ABC, K=K_ABC, work_limit=164.0)
        self.assertEqual(result.stop_reason, cg.WORK_UNMEASURED)
        self.assertEqual(result.measured_work, 0.0)

    def test_time_overrun_after_last_pricing_is_not_stationary(self):
        # Regressão: o segundo pricing (o que seria NUMERICAL_STATIONARY) só
        # "enxerga" o relógio estourado depois de concluído (overhead fora do
        # solver); o controlador deve reavaliar o tempo global antes de
        # decidir, mesmo após o último subsolve.
        calls = []

        def counting(master, snapshot, **kwargs):
            calls.append(1)
            return pr.price(master, snapshot, **kwargs)

        def fake_clock():
            return 1000.0 if len(calls) >= 2 else 0.0

        result = cg.run_column_generation(*ABC, K=K_ABC, time_limit=10.0,
                                          pricer=counting, clock=fake_clock)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.TIME_LIMIT)
        self.assertNotEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result.pricing_calls, 2)
        self.assertEqual(result.convergence_status, cg.NOT_CONVERGED)
        self.assertIn('ultrapassado', result.message)
        # Sem orçamento de tempo, o mesmo salto de relógio não interfere.
        calls_free = []

        def counting_free(master, snapshot, **kwargs):
            calls_free.append(1)
            return pr.price(master, snapshot, **kwargs)

        def fake_clock_free():
            return 1000.0 if len(calls_free) >= 2 else 0.0

        free = cg.run_column_generation(*ABC, K=K_ABC, pricer=counting_free,
                                        clock=fake_clock_free)
        self.assertEqual(free.stop_reason, cg.NUMERICAL_STATIONARY)

    def test_global_time_limit(self):
        ticks = iter(range(0, 10**6, 10))
        result = cg.run_column_generation(*ABC, K=K_ABC, time_limit=25.0,
                                          clock=lambda: float(next(ticks)))
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.TIME_LIMIT)
        for rec in result.history:
            self.assertLessEqual(rec.master_cost.forwarded_limits['TimeLimit'], 25.0)

    def test_unmeasured_work_on_last_pricing_is_not_stationary(self):
        # Regressão: a segunda chamada (a que seria NUMERICAL_STATIONARY)
        # retorna Work ausente; com work_limit ativo isso não pode encerrar
        # como estacionário, mesmo sendo o último subsolve do laço.
        def unmeasured_last(n, master, snapshot, result):
            return replace(result, work=None) if n == 2 else result

        spy = Spy(unmeasured_last)
        result = cg.run_column_generation(*ABC, K=K_ABC, work_limit=164.0, pricer=spy)
        self.assert_uncertified(result)
        self.assertEqual(result.stop_reason, cg.WORK_UNMEASURED)
        self.assertNotEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertEqual(len(spy.calls), 2)
        self.assertEqual(result.pricing_calls, 2)
        self.assertEqual(result.columns_added, 1)  # a 1a coluna (rc=-2) já havia sido inserida
        self.assertIsNone(result.total_work)
        self.assertIn('último pricing', result.message)
        # Sem orçamento de Work, o mesmo caso continua estacionário.
        free = cg.run_column_generation(*ABC, K=K_ABC, pricer=Spy(unmeasured_last))
        self.assertEqual(free.stop_reason, cg.NUMERICAL_STATIONARY)

    def test_unmeasured_work_is_explicit(self):
        unmeasured = Spy(lambda n, m, s, r: replace(r, work=None))
        free = cg.run_column_generation(*ABC, K=K_ABC, pricer=unmeasured)
        self.assertEqual(free.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertIsNone(free.total_work)
        self.assertGreaterEqual(free.unmeasured_work_calls, 1)
        self.assertTrue(math.isfinite(free.measured_work))
        self.assertIsNone(free.history[0].pricing_cost.work)
        self.assertIsNone(free.history[0].cumulative_work)
        budgeted = cg.run_column_generation(*ABC, K=K_ABC, work_limit=164.0,
                                            pricer=Spy(lambda n, m, s, r: replace(r, work=None)))
        self.assertEqual(budgeted.stop_reason, cg.WORK_UNMEASURED)

    # ── 8.5 certificação e recursos ──────────────────────────────────────

    def test_stationary_is_numeric_only(self):
        result = cg.run_column_generation(*ABC, K=K_ABC)
        self.assertEqual(result.stop_reason, cg.NUMERICAL_STATIONARY)
        self.assertEqual(result.convergence_status, cg.NUMERIC_UNCERTIFIED)
        self.assertEqual(result.certification_status, pr.UNCERTIFIED)
        self.assertIsNotNone(result.history[-1].pricing_solver_bound)  # registrado, não usado

    def test_master_is_disposed_on_exception_and_inputs_validated(self):
        disposed = []
        original = RestrictedMaster.dispose

        def spy_dispose(self):
            disposed.append(True)
            original(self)

        def boom(master, snapshot, **kwargs):
            raise RuntimeError('falha inesperada')

        with patch.object(RestrictedMaster, 'dispose', spy_dispose):
            with self.assertRaises(RuntimeError):
                cg.run_column_generation(*ABC, K=K_ABC, pricer=boom)
        self.assertTrue(disposed)
        for bad in ({'max_iterations': -1}, {'work_limit': math.nan},
                    {'time_limit': -1.0}, {'entry_tolerance': -1e-9}):
            with self.assertRaises(ValueError):
                cg.run_column_generation(*ABC, K=K_ABC, **bad)
        with self.assertRaises(ValueError):
            cg.run_column_generation(*ABC, K=K_ABC, master_params={'LogFile': 'x.log'})

    def test_no_n2_result_files_are_written(self):
        cg.run_column_generation(*ABC, K=K_ABC)
        results_dir = ROOT / 'results' / 'alternative-formulations'
        self.assertFalse(any(p.name.startswith('n2-') for p in results_dir.iterdir()))


if __name__ == '__main__':
    unittest.main()
