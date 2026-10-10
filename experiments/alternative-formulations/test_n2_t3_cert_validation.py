"""Testes E5: H-K físico, U exato, G2, prova B0 e integração E4 revalidada."""
# ruff: noqa: E402
from __future__ import annotations

import unittest
from dataclasses import replace
from fractions import Fraction as F
from types import MappingProxyType, SimpleNamespace

from n2_t3_cert_core import (
    CERTIFIED, UNCERTIFIED, canonical_k_hash,
)
from n2_t3_cert_integration import (
    _CertificationRecorder, CertificationOptions,
)
from n2_t3_cert_validation import (
    G2_PASSED, G2_NOT_PROVED, PHYSICAL_SCOPE,
    RationalPrimalWitness, initial_primal_witness, validate_k_evidence,
    verify_primal_rational, check_g2, verify_baseline, finalize_verified_result,
    run_verified_column_generation,
)

V = (0, 1, 2)
S, T = (0,), (2,)
ADJ = {0: [(1, 1)], 1: [(0, 1), (2, 1)], 2: [(1, 1)]}
AR = ((0, 1), (1, 0), (1, 2), (2, 1))
K = (frozenset({1}),)
KH = canonical_k_hash(K)
Q0 = (frozenset(V), frozenset(S), frozenset(T))
QB = (frozenset({1}), frozenset(S), frozenset(T))


def context():
    return validate_k_evidence(S, T, V, ADJ, AR, 1, K, k_hash=KH)


def make_e4(ctx, *, pi=3., mu=1.):
    snapshot = SimpleNamespace(
        revision=1, solve_id=1, k_hash=KH,
        direct_rc=MappingProxyType({}),
        values=SimpleNamespace(pi={0: pi}, tau={2: 0.},
                               mu={0: mu, 1: mu, 2: mu}, kappa={K[0]: 0.}))
    master = SimpleNamespace(S=S, T=T, V=V, K=K, k_hash=KH, reach_graph=ctx.H)
    recorder = _CertificationRecorder(CertificationOptions(use_n2=False, instance_key=ctx.instance_digest))
    event = recorder.prepare(master, snapshot, iteration=0, remaining_time=None)
    recorder.accept(event)
    return recorder.finish(SimpleNamespace(rmp_objective=3., stop_reason='ITERATION_LIMIT'))


class KEvidenceTests(unittest.TestCase):
    def test_valid_cut_and_same_hash(self):
        ctx = context()
        self.assertEqual((ctx.validated_cuts, ctx.k_hash, ctx.D), (1, KH, ()))
        self.assertIn('assert_valid_cuts', ctx.justification)

    def test_empty_k_valid(self):
        ctx = validate_k_evidence(S, T, V, ADJ, AR, 1, ())
        self.assertEqual(ctx.validated_cuts, 0)
        self.assertNotEqual(ctx.k_hash, KH)

    def test_invalid_cut_rejected_by_existing_validator(self):
        with self.assertRaises(Exception):
            validate_k_evidence(S, T, V, ADJ, AR, 1, (frozenset({0}),))

    def test_hash_and_instance_changes_rejected(self):
        with self.assertRaises(ValueError):
            validate_k_evidence(S, T, V, ADJ, AR, 1, K, k_hash='bad')
        with self.assertRaises(ValueError):
            validate_k_evidence(S, T, V, ADJ, ((0, 1),), 1, K)
        with self.assertRaises(ValueError):
            validate_k_evidence(S, T, V, ADJ, AR, 2, K)

    def test_forged_context_is_rejected(self):
        ctx = context()
        with self.assertRaises(ValueError):
            verify_primal_rational(replace(ctx, k_hash='forged'), initial_primal_witness(ctx))
        with self.assertRaises(ValueError):
            verify_primal_rational(replace(ctx, H={0: set(), 1: set(), 2: set()}),
                                   initial_primal_witness(ctx))


class PrimalTests(unittest.TestCase):
    def test_initial_seed_is_exact_upper_n(self):
        ctx = context()
        upper = verify_primal_rational(ctx, initial_primal_witness(ctx))
        self.assertEqual(upper.u_exact, F(3))
        self.assertEqual(upper.status, CERTIFIED)

    def test_single_station_witness_is_exact_upper_one(self):
        ctx = context()
        upper = verify_primal_rational(ctx, RationalPrimalWitness(
            {0: F(0), 1: F(1), 2: F(0)}, {QB: F(1)}, {}))
        self.assertEqual(upper.u_exact, F(1))

    def test_r1_r2_r3_k_bounds_exact(self):
        ctx = context()
        good = initial_primal_witness(ctx)
        cases = [
            RationalPrimalWitness({0: F(1), 1: F(1), 2: F(0)}, good.lam, good.d),
            RationalPrimalWitness({0: F(1), 1: F(1), 2: F(1, 2)}, good.lam, good.d),
            RationalPrimalWitness({0: F(1), 1: F(0), 2: F(1)}, good.lam, good.d),
            RationalPrimalWitness(good.y, {Q0: F(1, 2)}, good.d),
            RationalPrimalWitness({0: F(-1), 1: F(1), 2: F(1)}, good.lam, good.d),
            RationalPrimalWitness(good.y, {(frozenset({0,2}), frozenset(S), frozenset(T)): F(1)}, good.d),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                verify_primal_rational(ctx, case)

    def test_shared_terminal_direct_pair_exact(self):
        v = (0,)
        ctx = validate_k_evidence((0,), (0,), v, {}, (), 1, ())
        witness = RationalPrimalWitness({0: F(0)}, {}, {(0, 0): F(1)})
        upper = verify_primal_rational(ctx, witness)
        self.assertEqual(upper.u_exact, F(0))

    def test_floor_rational_and_forged_upper(self):
        ctx = context()
        result = make_e4(ctx)
        cert = result.best_certificate
        one = verify_primal_rational(ctx, RationalPrimalWitness(
            {0: F(0), 1: F(1), 2: F(0)}, {QB: F(1)}, {}))
        self.assertTrue(check_g2(ctx, one, cert, instance_key=ctx.instance_digest, evidence=result))
        self.assertFalse(check_g2(ctx, replace(one, u_exact=F(0)), cert, instance_key=ctx.instance_digest, evidence=result))
        self.assertFalse(check_g2(ctx, one, cert, instance_key='other', evidence=result))
        self.assertFalse(check_g2(ctx, one, None, instance_key=ctx.instance_digest, evidence=result))


class BaselineTests(unittest.TestCase):
    def test_b0_validity_checked_separately(self):
        ctx = context()
        self.assertEqual(verify_baseline(ctx, 1).status, CERTIFIED)
        bad = verify_baseline(ctx, 2)
        self.assertEqual(bad.status, UNCERTIFIED)
        self.assertIn('contraprova', bad.justification)

    def test_core_interrupted_only_incumbent_refused(self):
        ctx = context()
        proof = verify_baseline(ctx, 1, source='CORE_IP', solver_status='INTERRUPTED')
        self.assertEqual(proof.status, UNCERTIFIED)
        self.assertIsNone(proof.b0_exact)

    def test_large_instance_abstains(self):
        ctx = context()
        proof = verify_baseline(ctx, 1, max_vertices=2)
        self.assertEqual(proof.status, UNCERTIFIED)

    def test_b0_does_not_depend_on_lp_lb(self):
        ctx = context()
        proof = verify_baseline(ctx, 1, source='COMP_LP')
        self.assertEqual(proof.status, CERTIFIED)
        self.assertEqual(proof.b0_exact, F(1))

    def test_example_b0_two_certified_by_independent_physical_search(self):
        # Um par de robôs com trajetos separados e sem matching direto.
        v = tuple(range(7))
        s, t = (0, 1), (5, 6)
        adj = {x: [(y, 1) for y in (x - 1, x + 1) if y in v] for x in v}
        arcs = tuple((a, b) for a in v for b in v if abs(a - b) == 1)
        ctx = validate_k_evidence(s, t, v, adj, arcs, 1, ())
        p = verify_baseline(ctx, 2)
        self.assertEqual(p.status, CERTIFIED)
        self.assertEqual(p.b0_exact, F(2))


class EndToEndTests(unittest.TestCase):
    def test_reaudit_real_source_e1_and_physical_promote(self):
        ctx = context()
        e4 = make_e4(ctx)
        final = finalize_verified_result(e4, ctx, primal=RationalPrimalWitness(
            {0: F(0), 1: F(1), 2: F(0)}, {QB: F(1)}, {}),
            baseline=verify_baseline(ctx, 1))
        self.assertEqual((final.lp_status, final.physical_status), (CERTIFIED, CERTIFIED))
        self.assertEqual((final.lp_lb_exact, final.physical_integer_lb), (F(1), 1))
        self.assertEqual(final.convergence_status, G2_PASSED)
        self.assertEqual(final.scope, PHYSICAL_SCOPE)
        self.assertEqual(final.b0_exact, F(1))
        self.assertNotIn('ObjBound', final.as_dict())
        self.assertEqual(final.as_dict()['physical_lb_floor_12dp'], '1.000000000000')
        self.assertEqual(final.as_dict()['rmp_objective_diagnostic'], 3.)

    def test_initial_upper_nonconvergence_and_absent_b0(self):
        ctx = context()
        final = finalize_verified_result(make_e4(ctx), ctx,
                                         primal=initial_primal_witness(ctx))
        self.assertEqual(final.convergence_status, G2_NOT_PROVED)
        self.assertIsNone(final.b0_exact)

    def test_other_instance_and_forged_dual_or_bound_no_physical_certificate(self):
        ctx = context()
        e4 = make_e4(ctx)
        wrong = replace(e4.certification_history[0], instance_key='other')
        falsified = replace(e4, certification_history=(wrong,))
        output = finalize_verified_result(falsified, ctx)
        self.assertEqual(output.physical_status, UNCERTIFIED)
        event = e4.certification_history[0]
        attempt = replace(event.attempts[0], bound=replace(event.attempts[0].bound, ell=F(1000)))
        output = finalize_verified_result(replace(e4, certification_history=(
            replace(event, attempts=(attempt,)),)), ctx)
        self.assertEqual(output.physical_status, UNCERTIFIED)

    def test_invalid_k_cannot_be_hidden_by_lp_certificate(self):
        ctx = context()
        e4 = make_e4(ctx)
        with self.assertRaises(ValueError):
            finalize_verified_result(e4, replace(ctx, K=(frozenset({0}),)))

    def test_b0_independent_even_when_g2_missing(self):
        ctx = context()
        final = finalize_verified_result(make_e4(ctx), ctx,
                                         baseline=verify_baseline(ctx, 1))
        self.assertEqual(final.physical_status, CERTIFIED)
        self.assertEqual(final.b0_exact, F(1))
        self.assertEqual(final.convergence_status, G2_NOT_PROVED)

    def test_fake_certificate_cannot_pass_g2_without_replay(self):
        ctx = context()
        result = make_e4(ctx)
        good = verify_primal_rational(ctx, RationalPrimalWitness(
            {0: F(0), 1: F(1), 2: F(0)}, {QB: F(1)}, {}))
        fake = replace(result.best_certificate, winning_branch='FORGED')
        self.assertFalse(check_g2(ctx, good, fake, instance_key=ctx.instance_digest,
                                  evidence=result))
        self.assertFalse(check_g2(ctx, good, result.best_certificate,
                                  instance_key=ctx.instance_digest))

    def test_context_of_other_origin_terminal_is_not_accepted(self):
        ctx = context()
        result = make_e4(ctx)
        ctx2 = validate_k_evidence((0,), (1,), V, ADJ, AR, 1, ())
        output = finalize_verified_result(result, ctx2)
        self.assertEqual(output.physical_status, UNCERTIFIED)

    def test_global_time_zero_refuses_before_start(self):
        with self.assertRaises(TimeoutError):
            run_verified_column_generation(S, T, V, ADJ, AR, 1, K=K,
                                           options=CertificationOptions(use_n2=False),
                                           time_limit=0)

    def test_real_gurobi_pipeline_when_available(self):
        try:
            import gurobipy  # noqa: F401
        except ImportError:
            self.skipTest('Gurobi indisponível; executar no venv do pesquisador')
        result = run_verified_column_generation(S, T, V, ADJ, AR, 1,
                                                 K=K, k_hash=KH,
                                                 options=CertificationOptions(use_n2=False),
                                                 max_iterations=2)
        self.assertEqual(result.physical_status, CERTIFIED)
        self.assertEqual(result.lp_lb_exact, F(1))
        self.assertEqual(result.primal_upper.u_exact, F(3))
        self.assertEqual(result.b0_exact, None)


if __name__ == '__main__':
    unittest.main()
