"""N2-T3/E4: integração N1/ENUM/N2 com oráculo de CG real mockado.

Rodável sem Gurobi: o controlador REAL é carregado com módulos de solver fakes
para exercitar especificamente prepare/accept/overrun/stop/compatibilidade.
Em instalação com Gurobi, o teste adicional da integração real usa a API CG.
"""

# ruff: noqa: E402  # Imports locais após bootstrap do diretório experimental.

from __future__ import annotations

import importlib.util
import sys
import unittest
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from n2_t3_cert_core import CERTIFIED, UNCERTIFIED, LP_SCOPE, canonical_k_hash
from n2_t3_cert_integration import (
    CertificationOptions,
    CertifiedCGResult,
    _CertificationRecorder,
    run_certified_column_generation,
)

V, S, T = (0, 1, 2), (0,), (2,)
H = MappingProxyType({0: frozenset({1}),
                      1: frozenset({0, 2}),
                      2: frozenset({1})})
CUT = frozenset({1})
K = (CUT,)
HASH = canonical_k_hash(K)
INITIAL_COLUMN = (frozenset(V), frozenset(S), frozenset(T))
SMALL_COLUMN = (frozenset({1}), frozenset(S), frozenset(T))


def fake_snapshot(revision=1, solve_id=1, good=True, *, k_hash=HASH):
    pi = {0: 3.0 if good else 0.0}
    mu = {0: 1.0 if good else 0.0,
          1: 1.0 if good else 0.0,
          2: 1.0 if good else 0.0}
    return SimpleNamespace(
        revision=revision, solve_id=solve_id, k_hash=k_hash,
        direct_rc=MappingProxyType({}),
        values=SimpleNamespace(pi=MappingProxyType(pi),
                               tau=MappingProxyType({2: 0.0}),
                               mu=MappingProxyType(mu),
                               kappa=MappingProxyType({CUT: 0.0})))


class FakeMaster:
    created = []
    fail_at = None
    bad_vector_at = None
    next_value = False

    def __init__(self, S, T, V, adj, A_r, r, *, K=None, k_hash=None):
        self.S, self.T, self.V = tuple(S), tuple(T), tuple(V)
        self.K = tuple(K or ())
        self.k_hash = canonical_k_hash(self.K)
        self.D = ()
        self.reach_graph = H
        self.columns = (INITIAL_COLUMN,)
        self.solve_id = 0
        self.revision = 1
        self.disposed = False
        self.__class__.created.append(self)

    def solve(self, *, params):
        self.solve_id += 1
        if self.solve_id == self.fail_at:
            return SimpleNamespace(status_name='TIME_LIMIT', error='interrupted',
                                   work=0.5, runtime=0.01, revision=self.revision,
                                   solve_id=self.solve_id, dual=None, objective_rmp=None)
        snapshot = fake_snapshot(self.revision, self.solve_id,
                                 good=(self.solve_id == 1 or not self.next_value),
                                 k_hash='bad' if self.solve_id == self.bad_vector_at else HASH)
        return SimpleNamespace(status_name='OPTIMAL', error=None,
                               work=0.5, runtime=0.01, revision=self.revision,
                               solve_id=self.solve_id, dual=snapshot,
                               objective_rmp=3.0 if self.solve_id == 1 else 1.0)

    def reduced_cost(self, column, *, snapshot):
        if snapshot.solve_id != self.solve_id:
            raise RuntimeError('snapshot obsoleto')
        if column != SMALL_COLUMN:
            raise ValueError('coluna inesperada')
        return -2.0

    def add_column(self, column):
        if column in self.columns:
            raise ValueError('duplicada')
        self.columns += (column,)
        self.revision += 1

    def dispose(self):
        self.disposed = True


@dataclass(frozen=True)
class FakePricing:
    outcome: str
    termination: str
    status_name: str
    column: tuple | None
    reduced_cost: float | None
    solver_bound: float | None = 99e30  # número propositalmente inútil para prova
    work: float = 0.2
    runtime: float = 0.01
    certification_status: str = UNCERTIFIED
    proves_no_negative_column: bool = False
    error: str | None = None


def fake_price(master, snapshot, **kwargs):
    if snapshot.solve_id == 1:
        return FakePricing('NEGATIVE_COLUMN', 'NUMERICALLY_OPTIMAL', 'OPTIMAL',
                           SMALL_COLUMN, -2.0)
    return FakePricing('NO_INCUMBENT', 'OTHER_LIMIT', 'TIME_LIMIT', None, None)


def installed_fake_controller():
    """Isola módulos só durante import para testar o controlador de produção."""
    gurobi = SimpleNamespace(gurobi=SimpleNamespace(version=lambda: (12, 0, 3)))
    pricing = SimpleNamespace(
        NEGATIVE_COLUMN='NEGATIVE_COLUMN', NO_INCUMBENT='NO_INCUMBENT',
        NONNEGATIVE_INCUMBENT='NONNEGATIVE_INCUMBENT',
        NUMERICALLY_OPTIMAL='NUMERICALLY_OPTIMAL', SOLVER_FAILURE='SOLVER_FAILURE',
        UNCERTIFIED=UNCERTIFIED, price=fake_price)
    libraries = {'gurobipy': gurobi,
                 'n2_t2b_master': SimpleNamespace(RestrictedMaster=FakeMaster),
                 'n2_t2b_pricing': pricing}
    path = HERE / 'n2_t2b_column_generation.py'
    module_name = '_n2_t2b_column_generation_e4_offline_test'
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, libraries | {module_name: mod}):
        spec.loader.exec_module(mod)
    return mod


def run_fake(options, **kwargs):
    mod = installed_fake_controller()
    with patch.dict(sys.modules, {'n2_t2b_column_generation': mod}):
        return run_certified_column_generation(S, T, V, {}, (), 1,
                                               K=K, options=options,
                                               pricer=fake_price, **kwargs)


class CertificationRecorderTests(unittest.TestCase):
    def setUp(self):
        FakeMaster.created.clear()
        FakeMaster.fail_at = None
        FakeMaster.bad_vector_at = None
        FakeMaster.next_value = False

    def test_n1_n2_and_enum_both_verified_and_lp_only(self):
        master = FakeMaster(S, T, V, {}, (), 1, K=K)
        snap = fake_snapshot()
        recorder = _CertificationRecorder(CertificationOptions(enum_cap=100))
        event = recorder.prepare(master, snap, iteration=0, remaining_time=None)
        self.assertEqual({a.source for a in event.attempts}, {'N1', 'ENUM', 'N2'})
        self.assertTrue(all(a.status == CERTIFIED for a in event.attempts))
        self.assertEqual(event.best_certificate.lb_exact, F(1))
        self.assertEqual(event.best_certificate.scope, LP_SCOPE)
        for attempt in event.attempts:
            self.assertIsNotNone(attempt.bound)
            self.assertIsNotNone(attempt.verification)
            self.assertEqual(attempt.bound.vector_digest, event.vector_digest)
        recorder.accept(event)
        result = recorder.finish(SimpleNamespace(certification_status=UNCERTIFIED,
                                                  rmp_objective=3.0))
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertEqual(result.lb_exact, F(1))
        self.assertEqual(result.scope, LP_SCOPE)
        self.assertEqual(result.convergence_status, 'NOT_CHECKED_G2')
        self.assertEqual(result.base_result.certification_status, UNCERTIFIED)
        self.assertNotEqual(result.base_result.certification_status, CERTIFIED)

    def test_enum_cap_exactly_total_abstains_n1_survives(self):
        # 3-vertex path H: 6 nonempty connected subsets.
        master = FakeMaster(S, T, V, {}, (), 1, K=K)
        recorder = _CertificationRecorder(CertificationOptions(enum_cap=6))
        event = recorder.prepare(master, fake_snapshot(), iteration=0, remaining_time=None)
        info = {a.source: a for a in event.attempts}
        self.assertEqual(info['ENUM'].status, UNCERTIFIED)
        self.assertIn('cap', info['ENUM'].reason)
        self.assertEqual(info['N1'].status, CERTIFIED)
        self.assertEqual(event.best_certificate.lb_exact, F(1))

    def test_last_certified_survives_weaker_next_snapshot(self):
        FakeMaster.next_value = True
        result = run_fake(CertificationOptions(enum_cap=100))
        self.assertIsInstance(result, CertifiedCGResult)
        self.assertEqual(result.base_result.stop_reason, 'PRICING_INCOMPLETE')
        self.assertEqual(result.base_result.columns_added, 1)
        self.assertEqual(len(result.certification_history), 2)
        self.assertEqual(result.best_certificate.solve_id, 1)
        self.assertEqual(result.lb_exact, F(1))
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertTrue(FakeMaster.created[-1].disposed)
        self.assertEqual(result.base_result.certification_status, UNCERTIFIED)
        self.assertEqual(result.base_result.rmp_objective, 1.0)

    def test_master_interrupted_preserves_previous(self):
        FakeMaster.fail_at = 2
        result = run_fake(CertificationOptions(use_n2=False))
        self.assertEqual(result.base_result.stop_reason, 'MASTER_FAILURE')
        self.assertEqual(result.lb_exact, F(1))
        self.assertEqual(len(result.certification_history), 1)

    def test_no_valid_snapshot_before_failure_has_no_certificate(self):
        FakeMaster.fail_at = 1
        result = run_fake(CertificationOptions())
        self.assertIsNone(result.lb_exact)
        self.assertEqual(result.certification_status, UNCERTIFIED)
        self.assertTrue(result.justification)
        self.assertFalse(result.certification_history)

    def test_invalid_vector_abstains_then_valid_iteration(self):
        FakeMaster.bad_vector_at = 1
        result = run_fake(CertificationOptions(enum_cap=100))
        self.assertEqual(result.certification_history[0].attempts[0].source, 'VECTOR')
        self.assertEqual(result.certification_history[0].attempts[0].status, UNCERTIFIED)
        self.assertIsNotNone(result.certification_history[1].best_certificate.lb_exact)
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertEqual(result.best_certificate.solve_id, 2)

    def test_max_iterations_zero_keeps_first_cert_without_pricing(self):
        result = run_fake(CertificationOptions(enum_cap=None, use_n2=False),
                          max_iterations=0)
        self.assertEqual(result.base_result.stop_reason, 'ITERATION_LIMIT')
        self.assertEqual(result.base_result.pricing_calls, 0)
        self.assertEqual(result.lb_exact, F(1))

    def test_n2_box_zero_no_extra_numeric_solver(self):
        master = FakeMaster(S, T, V, {}, (), 1, K=K)
        options = CertificationOptions(use_n1=False, use_n2=True, enum_cap=None)
        recorder = _CertificationRecorder(options)
        event = recorder.prepare(master, fake_snapshot(), iteration=0, remaining_time=None)
        self.assertEqual(len(event.attempts), 1)
        self.assertEqual(event.attempts[0].source, 'N2')
        self.assertEqual(event.attempts[0].status, CERTIFIED)
        self.assertTrue(all(v == F(0) for _, v in event.attempts[0].bound.evidence['theta']))
        self.assertTrue(all(v == F(0) for _, v in event.attempts[0].bound.evidence['nu']))

    def test_malformed_configuration_fails_before_run(self):
        for options in (
            {'enum_cap': -1}, {'enum_cap': True}, {'max_enum_vertices': 0},
            {'max_n2_vertices': False}, {'use_n1': 1}, {'instance_key': ''},
            {'use_n1': False, 'use_n2': False, 'enum_cap': None},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                CertificationOptions(**options)
        with self.assertRaises(ValueError):
            run_fake(CertificationOptions(), certification_hook=object())

    def test_large_instance_circuit_breakers_are_abstentions(self):
        master = FakeMaster(S, T, V, {}, (), 1, K=K)
        recorder = _CertificationRecorder(CertificationOptions(
            use_n1=False, enum_cap=100, max_enum_vertices=2,
            max_n2_vertices=2))
        event = recorder.prepare(master, fake_snapshot(), iteration=0, remaining_time=None)
        self.assertEqual([a.status for a in event.attempts], [UNCERTIFIED, UNCERTIFIED])
        self.assertIsNone(event.best_certificate)

    def test_time_available_zero_skips_all_proofs(self):
        master = FakeMaster(S, T, V, {}, (), 1, K=K)
        recorder = _CertificationRecorder(CertificationOptions(enum_cap=50))
        event = recorder.prepare(master, fake_snapshot(), iteration=0, remaining_time=0)
        self.assertTrue(all(a.status == UNCERTIFIED for a in event.attempts))
        self.assertIsNone(event.best_certificate)

    def test_legacy_unmodified_return_type_and_status(self):
        mod = installed_fake_controller()
        result = mod.run_column_generation(S, T, V, {}, (), 1, K=K,
                                            pricer=fake_price)
        self.assertEqual(type(result).__name__, 'ColumnGenerationResult')
        self.assertEqual(result.certification_status, UNCERTIFIED)
        self.assertEqual(result.scope, 'ROOT_CG_NUMERICAL_ONLY')
        self.assertFalse(hasattr(result, 'lb_exact'))
        self.assertTrue(FakeMaster.created[-1].disposed)
        self.assertEqual(result.stop_reason, 'PRICING_INCOMPLETE')

    def test_work_budget_stops_before_second_snapshot_and_keeps_prior_proof(self):
        result = run_fake(CertificationOptions(enum_cap=100), work_limit=1.0)
        # first master=0.5 + pricing=0.2, second master=0.5 => overrun
        self.assertEqual(result.base_result.stop_reason, 'WORK_LIMIT')
        self.assertEqual(len(result.certification_history), 1)
        self.assertEqual(result.lb_exact, F(1))

    def test_time_budget_overrun_during_prepare_discards_new_certificate(self):
        class SimClock:
            now = 0.0
            def __call__(self):
                return self.now
        clock = SimClock()
        orig = _CertificationRecorder.prepare

        def slow_prepare(self, *args, **kwargs):
            event = orig(self, *args, **kwargs)
            clock.now = 20.0
            return event
        with patch.object(_CertificationRecorder, 'prepare', slow_prepare):
            result = run_fake(CertificationOptions(), clock=clock, time_limit=5.0)
        self.assertEqual(result.base_result.stop_reason, 'TIME_LIMIT')
        self.assertIsNone(result.lb_exact)
        self.assertFalse(result.certification_history)

    def test_history_contains_no_gurobi_objects_and_has_distinct_ids(self):
        result = run_fake(CertificationOptions(enum_cap=100))
        digest0, digest1 = [e.vector_digest for e in result.certification_history]
        self.assertNotEqual(digest0, digest1)
        self.assertEqual([e.solve_id for e in result.certification_history], [1, 2])
        self.assertTrue(all(not hasattr(e, '_model') for e in result.certification_history))
        with self.assertRaises(Exception):
            result.certification_history[0].iteration = 8

    def test_change_h_or_k_between_iterations_abstains_preserves_previous(self):
        mod = installed_fake_controller()
        def alter(master, snapshot, **kwargs):
            if snapshot.solve_id == 1:
                master.reach_graph = MappingProxyType({
                    0: frozenset({1, 2}),
                    1: frozenset({0, 2}),
                    2: frozenset({0, 1}),
                })
                # Enquanto primeiro pricing é executado, H é alterado:
                # segunda prova NÃO pode reaproveitar a identidade anterior.
            return fake_price(master, snapshot, **kwargs)
        with patch.dict(sys.modules, {'n2_t2b_column_generation': mod}):
            result = run_certified_column_generation(
                S, T, V, {}, (), 1, K=K, pricer=alter,
                options=CertificationOptions())
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertEqual(result.lb_exact, F(1))
        self.assertEqual(len(result.certification_history), 2)
        second = result.certification_history[1]
        self.assertIsNone(second.best_certificate)
        self.assertEqual(second.attempts[0].source, 'IDENTITY')
        self.assertEqual(second.attempts[0].status, UNCERTIFIED)
        self.assertEqual(result.best_certificate.solve_id, 1)

    def test_unmeasured_work_during_later_master_preserves_prior(self):
        orig = FakeMaster.solve
        def missing(self, **kwargs):
            r = orig(self, **kwargs)
            if self.solve_id == 2:
                r.work = float('nan')
            return r
        with patch.object(FakeMaster, 'solve', missing):
            result = run_fake(CertificationOptions(), work_limit=10.0)
        self.assertEqual(result.base_result.stop_reason, 'WORK_UNMEASURED')
        self.assertEqual(len(result.certification_history), 1)
        self.assertEqual(result.lb_exact, F(1))
        self.assertIsNone(result.base_result.total_work)

    def test_same_snapshot_is_required_prior_to_add_column(self):
        observed = []
        mod = installed_fake_controller()
        class Recorder:
            def prepare(self, master, snapshot, **kwargs):
                observed.append(('prepare', master.revision, snapshot.revision))
                return object()
            def accept(self, event):
                observed.append(('accept', FakeMaster.created[-1].revision, None))
        mod.run_column_generation(S, T, V, {}, (), 1, K=K, pricer=fake_price,
                                  certification_hook=Recorder())
        self.assertEqual(observed[:2], [('prepare', 1, 1), ('accept', 1, None)])
        self.assertEqual(observed[2:4], [('prepare', 2, 2), ('accept', 2, None)])


@unittest.skipUnless(importlib.util.find_spec('gurobipy'), 'Gurobi indisponível')
class RealGurobiIntegrationTests(unittest.TestCase):
    """Contraprova da integração real: habilitada automaticamente no venv."""

    def test_real_root_cg_returns_lp_certificate_without_changing_legacy(self):
        from test_n2_t2b_column_generation import ABC, K_ABC
        result = run_certified_column_generation(
            *ABC, K=K_ABC,
            options=CertificationOptions(enum_cap=100, use_n2=True))
        self.assertEqual(result.base_result.stop_reason, 'NUMERICAL_STATIONARY')
        self.assertEqual(result.base_result.certification_status, UNCERTIFIED)
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertEqual(result.scope, LP_SCOPE)
        self.assertEqual(result.lb_exact, F(1))
        self.assertEqual(result.convergence_status, 'NOT_CHECKED_G2')
        self.assertGreaterEqual(len(result.certification_history), 2)
        self.assertTrue(any(a.source == 'ENUM' and a.status == CERTIFIED
                            for event in result.certification_history
                            for a in event.attempts))

    def test_real_root_cg_with_first_snapshot_only(self):
        from test_n2_t2b_column_generation import ABC, K_ABC
        result = run_certified_column_generation(
            *ABC, K=K_ABC, max_iterations=0,
            options=CertificationOptions(use_n1=True, use_n2=False))
        self.assertEqual(result.base_result.stop_reason, 'ITERATION_LIMIT')
        self.assertEqual(result.base_result.pricing_calls, 0)
        self.assertEqual(len(result.certification_history), 1)
        self.assertEqual(result.certification_status, CERTIFIED)
        self.assertIsNotNone(result.lb_exact)


if __name__ == '__main__':
    unittest.main()
