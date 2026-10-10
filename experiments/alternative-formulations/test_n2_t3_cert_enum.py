"""N2-T3/E2: ENUM exato, cobertura e recusa conservadora de provas forjadas.

Oráculo independente: força bruta de 2^n-1 subconjuntos, todos os I/J de
mesma cardinalidade, com teste DFS de conexidade. Não usa ENUM nem TopK.
"""

import itertools
import random
import sys
import unittest
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

from n2_t3_cert_core import (
    CERTIFIED,
    UNCERTIFIED,
    GlobalPricingBound,
    analytical_bound_n1,
    canonical_k_hash,
    evaluate_theorem_l,
    rationalize_snapshot,
)
from n2_t3_cert_enum import (
    EnumAbstention,
    enumerate_global_bound,
    evaluate_enum_theorem_l,
    graph_digest,
)


def make_dual(H, S, T, *, pi=None, tau=None, mu=None, K=(),
              instance='enum-instance', revision=1, solve_id=1):
    V = tuple(sorted(H))
    S, T = tuple(sorted(S)), tuple(sorted(T))
    K = tuple(sorted((frozenset(z) for z in K), key=lambda z: tuple(sorted(z))))
    D = tuple((s, t) for s in S for t in T if s == t or t in H[s])
    snap = SimpleNamespace(
        values=SimpleNamespace(
            pi={s: 0.0 for s in S} if pi is None else pi,
            tau={t: 0.0 for t in T} if tau is None else tau,
            mu={v: 0.0 for v in V} if mu is None else mu,
            kappa={z: 0.0 for z in K}),
        direct_rc={pair: 0.0 for pair in D},
        k_hash=canonical_k_hash(K), revision=revision, solve_id=solve_id,
    )
    return rationalize_snapshot(snap, instance, S, T, V, K), D


def brute_force(dual, H):
    """Todos W,I,J: não chama código do ENUM nem função TopK."""
    V = dual.V
    best = None
    n_connected = 0
    n_eligible = 0
    for mask in range(1, 1 << len(V)):
        W = {v for index, v in enumerate(V) if mask & (1 << index)}
        discovered = {min(W)}
        stack = [min(W)]
        while stack:
            u = stack.pop()
            for v in W.intersection(H[u]).difference(discovered):
                discovered.add(v)
                stack.append(v)
        if discovered != W:
            continue
        n_connected += 1
        closed = W.union(*(H[v] for v in W))
        origins = [s for s in dual.S if s in closed]
        destinations = [t for t in dual.T if t in closed]
        if not origins or not destinations:
            continue
        n_eligible += 1
        for k in range(1, min(len(origins), len(destinations)) + 1):
            for selected_origins in itertools.combinations(origins, k):
                for selected_destinations in itertools.combinations(destinations, k):
                    value = sum((dual.mu[v] for v in W), F(0))
                    value -= sum((dual.pi[s] for s in selected_origins), F(0))
                    value -= sum((dual.tau[t] for t in selected_destinations), F(0))
                    if best is None or value < best:
                        best = value
    return best, n_connected, n_eligible


class EnumExactnessTests(unittest.TestCase):
    def test_single_vertex_shared_terminal_and_zero_arcs(self):
        H = {0: set()}
        dual, D = make_dual(H, (0,), (0,), pi={0: 0.5},
                            tau={0: -1.0}, mu={0: 2.0})
        bound = enumerate_global_bound(dual, H, cap=2)
        self.assertIsInstance(bound, GlobalPricingBound)
        self.assertEqual(bound.ell, F(5, 2))
        self.assertEqual(bound.evidence['visited_connected_w'], 1)
        self.assertEqual(bound.evidence['eligible_w'], 1)
        self.assertEqual(bound.evidence['witness_origins'], (0,))
        self.assertEqual(bound.evidence['witness_destinations'], (0,))
        cert = evaluate_enum_theorem_l(dual, bound, D, H, cap=2)
        self.assertEqual((cert.status, cert.source), (CERTIFIED, 'ENUM'))
        self.assertEqual(cert.ell_exact, F(5, 2))
        self.assertIsNotNone(cert.lb_exact)
        self.assertEqual(evaluate_theorem_l(dual, bound, D).status, UNCERTIFIED)

    def test_nonzero_K_eta_and_exact_nonbinary_fraction(self):
        H = {0: {1}, 1: {0, 2}, 2: {1}}
        cut = frozenset({1})
        dual, D = make_dual(H, (0,), (2,),
                            pi={0: F(2, 3)}, tau={2: F(-1, 7)},
                            mu={0: F(1, 3), 1: F(5, 2), 2: F(1, 4)},
                            K=(cut,))
        expected, total, eligible = brute_force(dual, H)
        bound = enumerate_global_bound(dual, H, total + 1)
        self.assertEqual(bound.ell, expected)
        self.assertEqual(bound.evidence['eligible_w'], eligible)
        self.assertEqual(evaluate_enum_theorem_l(dual, bound, D, H,
                                                  total + 1).status, CERTIFIED)

    def test_graph_path_against_full_Q(self):
        H = {0: {1}, 1: {0, 2}, 2: {1}}
        dual, D = make_dual(H, (0,), (2,), pi={0: 3.0},
                            tau={2: 0.0}, mu={0: 1.0, 1: 1.0, 2: 1.0})
        bound = enumerate_global_bound(dual, H, cap=7)
        self.assertEqual(bound.ell, F(-2))
        self.assertEqual(bound.evidence['visited_connected_w'], 6)
        self.assertEqual(bound.evidence['eligible_w'], 4)
        self.assertEqual((bound.evidence['witness_w'], bound.evidence['witness_k']), ((1,), 1))
        cert = evaluate_enum_theorem_l(dual, bound, D, H, cap=7)
        self.assertEqual(cert.lb_exact, F(1))
        self.assertEqual(cert.status, CERTIFIED)
        n1 = analytical_bound_n1(dual)
        self.assertLessEqual(n1.ell, bound.ell)

    def test_dense_and_sparse_graphs_and_topk_with_negative_values(self):
        for complete in (True, False):
            n = 5
            H = {v: {u for u in range(n) if u != v and
                      (complete or abs(u - v) == 1)} for v in range(n)}
            dual, _ = make_dual(H, (0, 2, 4), (0, 1, 3),
                                pi={0: 3.0, 2: -2.0, 4: 1.0},
                                tau={0: -1.0, 1: 0.5, 3: 2.0},
                                mu={0: 0.0, 1: 0.5, 2: 1.0, 3: 0.0, 4: 2.0})
            expected, count, eligible = brute_force(dual, H)
            actual = enumerate_global_bound(dual, H, cap=count + 1)
            self.assertEqual(actual.ell, expected)
            self.assertEqual((actual.evidence['visited_connected_w'],
                              actual.evidence['eligible_w']), (count, eligible))

    def test_random_exact_cstar_120_graphs_n_up_to_6(self):
        rng = random.Random(102010)
        compared = 0
        for _ in range(120):
            n = rng.randint(1, 6)
            H = {v: set() for v in range(n)}
            for v in range(1, n):
                u = rng.randrange(v)
                H[u].add(v)
                H[v].add(u)
            for u in range(n):
                for v in range(u + 1, n):
                    if rng.random() < 0.3:
                        H[u].add(v)
                        H[v].add(u)
            m = rng.randint(1, n)
            S = tuple(sorted(rng.sample(range(n), m)))
            T = tuple(sorted(rng.sample(range(n), m)))
            pi = {s: rng.choice((-3.0, -0.5, 0.0, 1.5, 4.0)) for s in S}
            tau = {t: rng.choice((-2.0, -0.5, 0.0, 2.0, 3.5)) for t in T}
            mu = {v: rng.choice((-2.0, 0.0, 0.25, 1.0, 2.5)) for v in H}
            dual, D = make_dual(H, S, T, pi=pi, tau=tau, mu=mu)
            expected, total, eligible = brute_force(dual, H)
            with self.subTest(n=n, S=S, T=T, H=H):
                bound = enumerate_global_bound(dual, H, cap=total + 1)
                self.assertIsInstance(bound, GlobalPricingBound)
                self.assertEqual(bound.ell, expected)
                self.assertEqual(bound.evidence['visited_connected_w'], total)
                self.assertEqual(bound.evidence['eligible_w'], eligible)
                self.assertEqual(evaluate_enum_theorem_l(dual, bound, D, H, total + 1).status,
                                 CERTIFIED)
            compared += 1
        self.assertEqual(compared, 120)


class EnumCoverageTests(unittest.TestCase):
    def setUp(self):
        self.H = {0: {1}, 1: {0, 2}, 2: {1}}
        self.dual, self.D = make_dual(self.H, (0,), (2,), pi={0: 3.0},
                                      tau={2: 0.0}, mu={0: 1.0, 1: 1.0, 2: 1.0})

    def test_cap_zero_one_partial_exact_and_plus_one(self):
        total = 6
        for cap in (0, 1, 2, 5, 6):
            with self.subTest(cap=cap):
                result = enumerate_global_bound(self.dual, self.H, cap)
                self.assertIsInstance(result, EnumAbstention)
                self.assertIsNone(result.ell)
                self.assertEqual(result.status, UNCERTIFIED)
                self.assertTrue(result.truncated)
                self.assertEqual(result.visited_connected_w, min(total, cap))
                self.assertEqual(evaluate_enum_theorem_l(self.dual, result, self.D,
                                                          self.H, cap).status, UNCERTIFIED)
        good = enumerate_global_bound(self.dual, self.H, total + 1)
        self.assertIsInstance(good, GlobalPricingBound)
        self.assertFalse(good.evidence['truncated'])
        self.assertEqual(good.evidence['cap'], 7)

    def test_dense_graph_exact_cap(self):
        H = {i: set(range(4)) - {i} for i in range(4)}
        dual, _ = make_dual(H, (0, 1), (2, 3))
        self.assertIsInstance(enumerate_global_bound(dual, H, 15), EnumAbstention)
        self.assertIsInstance(enumerate_global_bound(dual, H, 16), GlobalPricingBound)

    def test_interruption_via_callback(self):
        calls = [0]
        def stop():
            calls[0] += 1
            return calls[0] > 4
        result = enumerate_global_bound(self.dual, self.H, 20, interrupt_requested=stop)
        self.assertIsInstance(result, EnumAbstention)
        self.assertIsNone(result.ell)
        self.assertIn('interrupção', result.reason)
        full = enumerate_global_bound(self.dual, self.H, 20)
        self.assertEqual(full.ell, F(-2))

    def test_callback_raises_interrupted_error(self):
        def signal():
            raise InterruptedError('solicitação externa')
        result = enumerate_global_bound(self.dual, self.H, 20,
                                        interrupt_requested=signal)
        self.assertIsInstance(result, EnumAbstention)
        self.assertIsNone(result.ell)

    def test_interruption_via_zero_time_budget(self):
        res = enumerate_global_bound(self.dual, self.H, 20, time_limit_seconds=0)
        self.assertIsInstance(res, EnumAbstention)
        self.assertIsNone(res.ell)

    def test_invalid_limits_rejected(self):
        for cap in (-1, 1.5, True, None):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                enumerate_global_bound(self.dual, self.H, cap)
        for limit in (-1, float('inf'), float('nan'), True):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                enumerate_global_bound(self.dual, self.H, 20, time_limit_seconds=limit)


class EnumEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.H = {0: {1}, 1: {0, 2}, 2: {1}}
        self.dual, self.D = make_dual(self.H, (0,), (2,), pi={0: 3.0},
                                      tau={2: 0.0}, mu={0: 1.0, 1: 1.0, 2: 1.0})
        self.bound = enumerate_global_bound(self.dual, self.H, 7)

    def test_graph_validation_rejects_disconnected_directed_loops_and_outside(self):
        invalid = [{0: set(), 1: set(), 2: set()},
                   {0: {1}, 1: {0}, 2: {0}},
                   {0: {0, 1}, 1: {0, 2}, 2: {1}},
                   {0: {1, 3}, 1: {0, 2}, 2: {1}},
                   {0: {1}, 1: {0}, 2: {1}}]
        for H in invalid:
            with self.subTest(H=H), self.assertRaises(ValueError):
                enumerate_global_bound(self.dual, H, 7)

    def test_mismatch_direct_pairs_with_graph(self):
        # Mesma S/T e H diferente: D fornecido pelo master deixa de conferir.
        H_bad = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
        with self.assertRaises(ValueError):
            enumerate_global_bound(self.dual, H_bad, cap=20)

    def test_changed_graph_same_direct_pairs_cannot_reuse_evidence(self):
        # S={0}, T={3}: alterar H pode preservar D=∅ e ainda invalidar a prova.
        H4 = {0: {1}, 1: {0, 2}, 2: {1, 3}, 3: {2}}
        dual, D = make_dual(H4, (0,), (3,), pi={0: 3.0},
                            tau={3: 0.0}, mu={0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0})
        original = enumerate_global_bound(dual, H4, 12)
        H_changed = {0: {1}, 1: {0, 2, 3}, 2: {1, 3}, 3: {1, 2}}
        self.assertEqual(D, ())
        self.assertEqual(evaluate_enum_theorem_l(dual, original, D,
                                                  H_changed, 12).status, UNCERTIFIED)

    def test_hash_determinism_and_graph_different(self):
        self.assertEqual(graph_digest(self.H, self.dual.V),
                         graph_digest({2: {1}, 0: {1}, 1: {2, 0}}, self.dual.V))
        changed = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
        self.assertNotEqual(graph_digest(self.H, self.dual.V),
                            graph_digest(changed, self.dual.V))
        self.assertEqual(self.bound.evidence['graph_digest'],
                         graph_digest(self.H, self.dual.V))

    def test_forged_ell_and_evidence_rejected(self):
        fake_high = replace(self.bound, ell=self.bound.ell + F(100))
        fake_low = replace(self.bound, ell=self.bound.ell - F(100))
        for candidate in (fake_high, fake_low):
            self.assertEqual(evaluate_enum_theorem_l(self.dual, candidate, self.D,
                                                      self.H, 7).status, UNCERTIFIED)
        evidence = dict(self.bound.evidence)
        evidence['truncated'] = True
        fake_evidence = replace(self.bound, evidence=MappingProxyType(evidence))
        self.assertEqual(evaluate_enum_theorem_l(self.dual, fake_evidence, self.D,
                                                  self.H, 7).status, UNCERTIFIED)

    def test_other_vector_or_revision_rejected(self):
        other, D = make_dual(self.H, (0,), (2,), pi={0: 4.0},
                             tau={2: 0.0}, mu={0: 1.0, 1: 1.0, 2: 1.0}, solve_id=2)
        self.assertEqual(evaluate_enum_theorem_l(other, self.bound, D,
                                                  self.H, 7).status, UNCERTIFIED)

    def test_wrong_D_and_wrong_cap_rejected(self):
        self.assertEqual(evaluate_enum_theorem_l(self.dual, self.bound,
                                                  ((0, 2),), self.H, 7).status, UNCERTIFIED)
        self.assertEqual(evaluate_enum_theorem_l(self.dual, self.bound,
                                                  None, self.H, 7).status, UNCERTIFIED)
        self.assertEqual(evaluate_enum_theorem_l(self.dual, self.bound,
                                                  self.D, self.H, 6).status, UNCERTIFIED)
        self.assertEqual(evaluate_enum_theorem_l(self.dual, self.bound,
                                                  self.D, self.H, 8).status, UNCERTIFIED)

    def test_output_immutability_and_scope(self):
        with self.assertRaises(TypeError):
            self.bound.evidence['witness_rc'] = F(5)
        cert = evaluate_enum_theorem_l(self.dual, self.bound, self.D,
                                        self.H, 7)
        self.assertEqual(cert.status, CERTIFIED)
        self.assertEqual(cert.scope, 'FULL_FCC_K_LP_ONLY')
        self.assertNotIn('MIN-STATION CERTIFIED', cert.justification)

    def test_objboundc_cannot_replace_enum_proof(self):
        fake = SimpleNamespace(ObjBoundC=1.0, status='OPTIMAL')
        cert = evaluate_enum_theorem_l(self.dual, fake, self.D, self.H, 7)
        self.assertEqual(cert.status, UNCERTIFIED)


if __name__ == '__main__':
    unittest.main()
