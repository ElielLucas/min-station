"""N2-T3/E1: regressões puras e oráculo de força-bruta independente (sem Gurobi).

Nenhum teste chama as funções L1/TopK do módulo para calcular o esperado.
A extensão H-K e a certificação física do MIN-STATION ficam na E5.
"""

import itertools
import math
import random
import sys
import unittest
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

from n2_t3_cert_core import (
    CERTIFIED, UNCERTIFIED, GlobalPricingBound, analytical_bound_n1,
    canonical_k_hash, conservative_integer_bound, evaluate_theorem_l,
    floor_export, floor_float, rationalize_snapshot, _integer_rounding_formula,
)


def fixture(*, V=(0, 1, 2), S=(0,), T=(2,), K=(), pi=None,
            tau=None, mu=None, kappa=None, instance='trial-1',
            revision=1, solve_id=1, D=None):
    """Snapshot com a mesma forma pública do tipo real, sem depender de Gurobi."""
    K = tuple(frozenset(z) for z in K)
    K = tuple(sorted(set(K), key=lambda z: tuple(sorted(z))))
    pi = pi if pi is not None else {s: 0.0 for s in S}
    tau = tau if tau is not None else {t: 0.0 for t in T}
    mu = mu if mu is not None else {v: 0.0 for v in V}
    kappa = kappa if kappa is not None else {z: 0.0 for z in K}
    snap = SimpleNamespace(
        values=SimpleNamespace(pi=pi, tau=tau, mu=mu, kappa=kappa),
        k_hash=canonical_k_hash(K), revision=revision, solve_id=solve_id,
        direct_rc={pair: 0.0 for pair in (() if D is None else D)},
    )
    dual = rationalize_snapshot(snap, instance, S, T, V, K)
    return dual, (() if D is None else D)


def rc_star_bruteforce(S, T, V, H, pi, tau, mu):
    """Independente de N1/TopK: enumera W/I/J e calcula cada custo."""
    best = None
    for mask in range(1, 1 << len(V)):
        W = {v for i, v in enumerate(V) if mask & (1 << i)}
        reached = {next(iter(W))}
        frontier = list(reached)
        while frontier:
            u = frontier.pop()
            for w in W & H[u] - reached:
                reached.add(w)
                frontier.append(w)
        if reached != W:
            continue
        B = set(W)
        for v in W:
            B.update(H[v])
        S_W = tuple(s for s in S if s in B)
        T_W = tuple(t for t in T if t in B)
        for k in range(1, min(len(S_W), len(T_W)) + 1):
            for origins in itertools.combinations(S_W, k):
                for destinations in itertools.combinations(T_W, k):
                    rc = sum((mu[v] for v in W), F(0))
                    rc -= sum((pi[s] for s in origins), F(0))
                    rc -= sum((tau[t] for t in destinations), F(0))
                    if best is None or rc < best:
                        best = rc
    if best is None:
        raise AssertionError('grafo/terminais do caso não produziram colunas')
    return best


class RationalVectorTests(unittest.TestCase):
    def test_float_binary_ratio_and_projection(self):
        dual, _ = fixture(V=(0, 1), S=(0,), T=(1,),
                          pi={0: 0.1}, tau={1: -0.2},
                          mu={0: -0.0001, 1: 0.3})
        self.assertEqual(dual.pi[0], F.from_float(0.1))
        self.assertNotEqual(dual.pi[0], F(1, 10))
        self.assertEqual(dual.tau[1], F.from_float(-0.2))
        self.assertEqual(dual.mu[0], F(0))
        self.assertEqual(dual.mu[1], F.from_float(0.3))

    def test_negative_kappa_projection_recomputes_eta(self):
        K = (frozenset({1}),)
        dual, D = fixture(K=K, pi={0: 2.0}, tau={2: 0.0},
                          mu={0: 0.0, 1: 2.0, 2: 0.0},
                          kappa={K[0]: -2.0}, D=())
        self.assertEqual(dual.kappa[K[0]], 0)
        bound = analytical_bound_n1(dual)
        cert = evaluate_theorem_l(dual, bound, D)
        self.assertEqual((bound.ell, cert.l_exact, cert.lb_exact),
                         (F(-2), F(1), F(1, 3)))

    def test_nan_inf_rejected_in_all_components(self):
        for name in ('pi', 'tau', 'mu', 'kappa'):
            for val in (float('nan'), math.inf, -math.inf):
                with self.subTest(name=name, val=val):
                    K = (frozenset({1}),)
                    data = {'pi': {0: 0.0}, 'tau': {2: 0.0},
                            'mu': {0: 0.0, 1: 0.0, 2: 0.0},
                            'kappa': {K[0]: 0.0}}
                    data[name][next(iter(data[name]))] = val
                    with self.assertRaises(ValueError):
                        fixture(K=K, **data)

    def test_indices_missing_extra_and_duplicate(self):
        bad = [dict(pi={0: 1.0, 3: 1.0}),
               dict(mu={0: 1.0, 1: 1.0}),
               dict(S=(0, 0))]
        for params in bad:
            with self.subTest(params=params), self.assertRaises(ValueError):
                fixture(**params)

    def test_snapshot_hash_mismatch_and_missing(self):
        dual, _ = fixture()
        self.assertEqual(len(dual.k_hash), 64)
        from n2_t3_cert_core import rationalize_snapshot
        s = SimpleNamespace(values=SimpleNamespace(pi={0: 0.}, tau={2: 0.},
                                                     mu={0: 0., 1: 0., 2: 0.},
                                                     kappa={}),
                            revision=1, solve_id=1, k_hash='bad', direct_rc={})
        with self.assertRaises(ValueError):
            rationalize_snapshot(s, 'trial-1', (0,), (2,), (0, 1, 2), ())
        with self.assertRaises(ValueError):
            rationalize_snapshot(None, 'trial-1', (0,), (2,), (0, 1, 2), ())

    def test_digest_deterministic_and_bound_to_instance_k_iteration_and_coefficients(self):
        a, _ = fixture()
        b, _ = fixture()
        self.assertEqual(a.vector_digest, b.vector_digest)
        changes = [fixture(instance='other')[0], fixture(revision=2)[0],
                   fixture(solve_id=2)[0],
                   fixture(mu={0: 0.0, 1: 0.0, 2: 1.0})[0],
                   fixture(K=(frozenset({0}),),
                           kappa={frozenset({0}): 0.0})[0]]
        for other in changes:
            self.assertNotEqual(a.vector_digest, other.vector_digest)

    def test_dual_maps_are_immutable(self):
        dual, _ = fixture()
        with self.assertRaises(TypeError):
            dual.mu[0] = F(2)
        with self.assertRaises(Exception):
            dual.solve_id = 2

    def test_tampered_dual_digest_is_rejected(self):
        from dataclasses import replace
        from types import MappingProxyType
        dual, _ = fixture()
        corrupted = replace(dual, mu=MappingProxyType({0: F(3), 1: F(0), 2: F(0)}))
        with self.assertRaises(ValueError):
            analytical_bound_n1(corrupted)


class TheoremLTests(unittest.TestCase):
    def test_path_abc_D_empty_L_and_N1(self):
        Z = frozenset({1})
        dual, D = fixture(pi={0: 3.0}, tau={2: 0.0},
                          mu={0: 1.0, 1: 1.0, 2: 1.0},
                          K=(Z,), kappa={Z: 0.0}, D=())
        bound = analytical_bound_n1(dual)
        result = evaluate_theorem_l(dual, bound, D)
        self.assertEqual(bound.ell, F(-2))
        self.assertEqual((result.l_exact, result.delta_exact, result.lb_exact),
                         (F(3), F(0), F(1)))
        self.assertEqual(result.status, CERTIFIED)
        self.assertEqual(result.scope, 'FULL_FCC_K_LP_ONLY')
        self.assertIn('NÃO verificados', result.justification)

    def test_permanence_negative_delta_guard(self):
        E = F(1, 1_000_000)
        # Usamos Fraction direto: nenhum arredondamento do epsilon decimal.
        dual, D = fixture(V=('a', 'b'), S=('a',), T=('a',),
                          pi={'a': F(1)}, tau={'a': F(0)},
                          mu={'a': F(1) - E / 2, 'b': F(1)},
                          D=(('a', 'a'),))
        bound = analytical_bound_n1(dual)
        result = evaluate_theorem_l(dual, bound, D)
        self.assertEqual(bound.ell, -E / 2)
        self.assertEqual((result.l_exact, result.delta_exact, result.lb_exact),
                         (F(1), F(-1), F(0)))
        self.assertLess(result.lb_exact, result.l_exact - E)

    def test_eta_positive_vanishes_false_lb(self):
        dual, _ = fixture(pi={0: 2.0}, tau={2: 0.0},
                          mu={0: 0.0, 1: 2.0, 2: 0.0})
        # eta[1]=1, portanto L=1 (sem eta incorretamente seria L=2).
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual(res.l_exact, F(1))

    def test_ratio_branch_can_dominate_mass(self):
        # m=1, L=5/4, ell=-1/2, delta=0:
        # max(0, 3/4, 5/6) = 5/6 => RATIO.
        dual, _ = fixture(pi={0: F(5, 4)}, tau={2: F(0)},
                          mu={0: F(3, 4), 1: F(3, 4), 2: F(3, 4)})
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual(res.winning_branch, 'RATIO')
        self.assertEqual(res.lb_exact, F(5, 6))

    def test_zero_multiplier_not_gap_certificate(self):
        dual, _ = fixture()
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual((res.l_exact, res.lb_exact), (F(0), F(0)))
        self.assertIsNone(getattr(res, 'convergence_status', None))

    def test_invalid_direct_pairs_and_wrong_m(self):
        dual, _ = fixture()
        bound = analytical_bound_n1(dual)
        with self.assertRaises(ValueError):
            evaluate_theorem_l(dual, bound, ((0, 5),))
        with self.assertRaises(ValueError):
            evaluate_theorem_l(dual, bound, (), m=2)

    def test_manual_ell_and_gurobi_bound_not_certifiable(self):
        dual, _ = fixture(pi={0: 3.0})
        for suspicious in (0.0, F(0), {'ObjBoundC': 0.0}, 10):
            with self.subTest(suspicious=suspicious):
                result = evaluate_theorem_l(dual, suspicious, ())
                self.assertEqual(result.status, UNCERTIFIED)
                self.assertIsNone(result.lb_exact)
                with self.assertRaises(ValueError):
                    floor_export(result)

    def test_forged_evidence_and_large_ell_rejected(self):
        dual, _ = fixture(pi={0: 3.0})
        actual = analytical_bound_n1(dual)
        candidates = [
            GlobalPricingBound(F(0), 'N1', dual.vector_digest, actual.evidence),
            GlobalPricingBound(actual.ell, 'N1', dual.vector_digest, {'verified': True}),
            GlobalPricingBound(actual.ell, 'ENUM', dual.vector_digest, actual.evidence),
            GlobalPricingBound(actual.ell, 'MIP_OPT', dual.vector_digest, actual.evidence),
        ]
        for forged in candidates:
            self.assertEqual(evaluate_theorem_l(dual, forged, ()).status, UNCERTIFIED)

    def test_old_iteration_bound_rejected(self):
        old, D = fixture(pi={0: 3.0})
        new, _ = fixture(pi={0: 3.0}, revision=2)
        result = evaluate_theorem_l(new, analytical_bound_n1(old), D)
        self.assertEqual(result.status, UNCERTIFIED)
        self.assertIsNone(result.lb_exact)

    def test_fraction_output_and_downward_decimal_export(self):
        # ell=0; mu=1/3, pi=1/4, tau=0 => L=1/4; delta=0;
        # LB=1/4. Ainda assim o decimal não é aproximado para cima.
        dual, _ = fixture(V=(0,), S=(0,), T=(0,),
                          mu={0: F(1, 3)}, pi={0: F(1, 4)},
                          tau={0: F(0)})
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual(res.lb_exact, F(1, 4))
        self.assertEqual(floor_export(res, 2), Decimal('0.25'))
        self.assertEqual(_integer_rounding_formula(res.lb_exact), 1)
        with self.assertRaisesRegex(RuntimeError, 'H-K'):
            conservative_integer_bound(res)

    def test_export_nonterminating_rational_floor(self):
        dual, _ = fixture(V=(0,), S=(0,), T=(0,),
                          mu={0: F(1, 3)}, pi={0: F(1, 3)},
                          tau={0: F(0)})
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual(res.lb_exact, F(1, 3))
        floor = floor_export(res, 12)
        self.assertEqual(floor, Decimal('0.333333333333'))
        self.assertLessEqual(F(floor), res.lb_exact)
        self.assertLessEqual(F.from_float(floor_float(res)), res.lb_exact)

    def test_integer_rounding_epsilon_exact(self):
        # LB=1-1/(2e6), ceil(LB-1e-6)=1; não arredondar LB antes.
        dual, _ = fixture(pi={0: F(1) - F(1, 2_000_000)},
                          tau={2: F(0)},
                          mu={0: F(1), 1: F(1), 2: F(1)})
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertEqual(res.lb_exact, F(1) - F(1, 2_000_000))
        self.assertEqual(_integer_rounding_formula(res.lb_exact), 1)
        with self.assertRaisesRegex(RuntimeError, 'H-K'):
            conservative_integer_bound(res)

    def test_integer_formula_not_valid_lb_for_fractional_lp(self):
        self.assertEqual(_integer_rounding_formula(F(3, 2)), 2)
        self.assertGreater(_integer_rounding_formula(F(3, 2)), F(3, 2))

    def test_direct_pairs_incomplete_are_refused(self):
        dual, _ = fixture(V=(0,), S=(0,), T=(0,), D=((0, 0),))
        valid = analytical_bound_n1(dual)
        result = evaluate_theorem_l(dual, valid, ())
        self.assertEqual(result.status, UNCERTIFIED)
        self.assertIsNone(result.lb_exact)

    def test_floor_float_near_float_boundary(self):
        dual, _ = fixture(V=(0,), S=(0,), T=(0,),
                          pi={0: F(1, 10)}, mu={0: F(1)}, tau={0: F(0)})
        res = evaluate_theorem_l(dual, analytical_bound_n1(dual), ())
        self.assertLessEqual(F.from_float(floor_float(res)), res.lb_exact)
        self.assertEqual(floor_export(res, 1), Decimal('0.1'))


class N1GlobalValidityTests(unittest.TestCase):
    def test_negative_topk_keeps_first_pair(self):
        dual, _ = fixture(V=(0, 1), S=(0, 1), T=(0, 1),
                          pi={0: -1.0, 1: -2.0}, tau={0: -3.0, 1: -4.0},
                          mu={0: 0.0, 1: 0.0})
        b = analytical_bound_n1(dual)
        self.assertEqual(b.ell, F(4))  # best k=1: -1-3=-4
        self.assertEqual(b.evidence['best_k'], 1)

    def test_n1_k2_dominates_k1(self):
        dual, _ = fixture(V=(0, 1), S=(0, 1), T=(0, 1),
                          pi={0: 2.0, 1: 1.0}, tau={0: 3.0, 1: 2.0})
        b = analytical_bound_n1(dual)
        self.assertEqual((b.ell, b.evidence['best_k']), (F(-8), 2))

    def test_single_vertex_shared_terminal(self):
        dual, D = fixture(V=(0,), S=(0,), T=(0,),
                          pi={0: 1.0}, tau={0: 2.0}, mu={0: 3.0},
                          D=((0, 0),))
        b = analytical_bound_n1(dual)
        self.assertEqual(b.ell, F(0))
        result = evaluate_theorem_l(dual, b, D)
        self.assertEqual(result.delta_exact, -F(3))
        self.assertEqual(result.lb_exact, F(0))

    def test_n1_is_global_lower_bound_independent_random_enumeration(self):
        rng = random.Random(20261010)
        tested = 0
        for n in range(1, 6):
            V = tuple(range(n))
            for _ in range(14):
                # Grafo em H conectado; árvore caminho, mais arestas aleatórias.
                H = {v: set() for v in V}
                for v in range(1, n):
                    H[v - 1].add(v)
                    H[v].add(v - 1)
                for u in V:
                    for v in V:
                        if u < v and rng.random() < 0.25:
                            H[u].add(v)
                            H[v].add(u)
                m = rng.randint(1, min(2, n))
                S = tuple(sorted(rng.sample(V, m)))
                T = tuple(sorted(rng.sample(V, m)))
                pi = {s: F(rng.randint(-5, 7), 3) for s in S}
                tau = {t: F(rng.randint(-4, 6), 5) for t in T}
                mu = {v: F(rng.randint(0, 8), 4) for v in V}
                dual, _ = fixture(V=V, S=S, T=T, pi=pi, tau=tau, mu=mu)
                lower = analytical_bound_n1(dual)
                exact = rc_star_bruteforce(S, T, V, H, dual.pi, dual.tau, dual.mu)
                self.assertLessEqual(lower.ell, exact,
                                     (n, S, T, lower.ell, exact))
                tested += 1
        self.assertEqual(tested, 70)


if __name__ == '__main__':
    unittest.main()
