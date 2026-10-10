"""N2-T3 E3: testes racionais, sem tratar o solver como prova matemática.

Oráculos independentes: enumeração de Q no teste E2 e verificação direta das
restrições P0--P5 com soluções de fluxo construídas por árvores geradoras.
"""

import random
import sys
import unittest
from collections import deque
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

from n2_t3_cert_box import (
    BOX_SOURCE,
    BoxAbstention,
    build_rational_pricing_lp,
    certify_box_bound,
    evaluate_box_theorem_l,
    propose_lp_multipliers,
)
from n2_t3_cert_core import (
    CERTIFIED,
    LP_SCOPE,
    UNCERTIFIED,
    GlobalPricingBound,
    analytical_bound_n1,
    evaluate_theorem_l,
)
from n2_t3_cert_enum import enumerate_global_bound, evaluate_enum_theorem_l
from test_n2_t3_cert_enum import brute_force, make_dual


def path_graph(n):
    H = {v: set() for v in range(n)}
    for v in range(n - 1):
        H[v].add(v + 1)
        H[v + 1].add(v)
    return H


def connected_graph(rng, n):
    H = path_graph(n)
    for u in range(n):
        for v in range(u + 2, n):
            if rng.random() < 0.45:
                H[u].add(v)
                H[v].add(u)
    return H


def build_case(n=3, *, H=None, S=None, T=None, pi=None, tau=None, mu=None, K=()):
    H = path_graph(n) if H is None else H
    S = (0,) if S is None else S
    T = (n - 1,) if T is None else T
    dual, D = make_dual(H, S, T, pi=pi, tau=tau, mu=mu, K=K)
    return dual, D, H, build_rational_pricing_lp(dual, H)


def feasible_witness(dual, H, lp, W, origins, destinations):
    """Constrói exatamente o fluxo P3--P5 para um W conexo (independente)."""
    W = frozenset(W)
    root = min(W)
    parent = {root: None}
    queue = deque([root])
    while queue:
        u = queue.popleft()
        for v in H[u] & W:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    if set(parent) != set(W):
        raise ValueError('W precisa ser conexo')
    size = {v: 1 for v in W}
    for v in reversed(tuple(parent)):
        if parent[v] is not None:
            size[parent[v]] += size[v]
    w = {var: F(0) for var in lp.variables}
    for v in W:
        w['x', v] = F(1)
    for s in origins:
        w['a', s] = F(1)
    for t in destinations:
        w['b', t] = F(1)
    w['rho', root] = F(1)
    w['g', root] = F(len(W))
    for v in W:
        if parent[v] is not None:
            w['f', parent[v], v] = F(size[v])
    return w


def direct_check(lp, w):
    """Checa independentemente domínio, igualdades e desigualdades originais."""
    if set(w) != set(lp.variables):
        return False
    if any(w[v] < 0 or w[v] > lp.upper[v] for v in lp.variables):
        return False
    for row in lp.equalities:
        if sum((w[v] * c for v, c in row.coefficients.items()), F(0)) != row.rhs:
            return False
    for row in lp.inequalities:
        if sum((w[v] * c for v, c in row.coefficients.items()), F(0)) < row.rhs:
            return False
    return True


class RationalMatrixTests(unittest.TestCase):
    def test_single_vertex_no_arcs_all_bounds_and_rows(self):
        dual, _, H, lp = build_case(n=1, S=(0,), T=(0,))
        self.assertEqual(len(lp.variables), 5)
        self.assertEqual(len(lp.equalities), 3)
        self.assertEqual(len(lp.inequalities), 5)
        self.assertNotIn(('f', 0, 0), lp.upper)
        self.assertEqual(lp.upper['g', 0], F(1))
        self.assertEqual(set(lp.upper.values()), {F(1)})
        w = feasible_witness(dual, H, lp, {0}, {0}, {0})
        self.assertTrue(direct_check(lp, w))

    def test_p0_objective_signs_and_variable_box(self):
        _, _, _, lp = build_case(3, pi={0: F(2, 3)}, tau={2: F(-7, 2)},
                                   mu={0: F(1, 2), 1: F(3, 4), 2: F(5, 3)})
        self.assertEqual(lp.objective['x', 1], F(3, 4))
        self.assertEqual(lp.objective['a', 0], F(-2, 3))
        self.assertEqual(lp.objective['b', 2], F(7, 2))
        self.assertEqual(lp.objective['rho', 0], F(0))
        self.assertEqual(lp.objective['f', 1, 2], F(0))
        self.assertEqual(lp.upper['g', 1], F(3))
        self.assertEqual(lp.upper['f', 1, 2], F(2))
        for kind in ('x', 'a', 'b', 'rho'):
            self.assertEqual({u for key, u in lp.upper.items() if key[0] == kind}, {F(1)})

    def test_row_count_ids_complete_and_signs(self):
        _, _, H, lp = build_case(n=3)
        arcs = sum(len(v) for v in H.values())
        self.assertEqual(len(lp.variables), 3 * 3 + 2 + arcs)
        self.assertEqual(len(lp.equalities), 3 + 2)
        self.assertEqual(len(lp.inequalities), 2 + 1 + 2 * 3 + 2 * arcs)
        rows = {row.name: row for row in lp.equalities + lp.inequalities}
        self.assertEqual(len(rows), len(lp.equalities) + len(lp.inequalities))
        self.assertEqual(rows['P1a', 0].coefficients,
                         {('x', 0): F(1), ('x', 1): F(1), ('a', 0): F(-1)})
        self.assertEqual(rows['P1b', 2].coefficients,
                         {('x', 1): F(1), ('x', 2): F(1), ('b', 2): F(-1)})
        self.assertEqual(rows['P2min',].rhs, F(1))
        self.assertEqual(rows['P3root',].rhs, F(1))
        self.assertEqual(rows['P3g', 1].coefficients,
                         {('rho', 1): F(3), ('g', 1): F(-1)})
        self.assertEqual(rows['P4', 1].coefficients,
                         {('g', 1): F(1), ('x', 1): F(-1), ('f', 0, 1): F(1),
                          ('f', 2, 1): F(1), ('f', 1, 0): F(-1), ('f', 1, 2): F(-1)})
        self.assertEqual(rows['P5u', 0, 1].coefficients,
                         {('x', 0): F(2), ('f', 0, 1): F(-1)})
        self.assertEqual(rows['P5w', 0, 1].coefficients,
                         {('x', 1): F(2), ('f', 0, 1): F(-1)})
        self.assertEqual(rows['P2bal',].coefficients,
                         {('a', 0): F(1), ('b', 2): F(-1)})
        self.assertEqual(rows['P3rx', 0].coefficients,
                         {('x', 0): F(1), ('rho', 0): F(-1)})

    def test_p0_p5_exact_feasible_patterns_including_terminal_outside_w(self):
        for n in range(1, 7):
            H = path_graph(n)
            dual, _, _, lp = build_case(n, H=H, S=(0,), T=(n-1,))
            for width in range(1, n + 1):
                W = set(range(width))
                if 0 not in set(W).union(*(H[v] for v in W)):
                    continue
                if n - 1 not in set(W).union(*(H[v] for v in W)):
                    continue
                w = feasible_witness(dual, H, lp, W, {0}, {n-1})
                self.assertTrue(direct_check(lp, w), (n, width))

    def test_witness_invalid_balancing_and_flow_detected(self):
        dual, _, H, lp = build_case(n=4, S=(0,), T=(3,))
        w = feasible_witness(dual, H, lp, set(range(4)), {0}, {3})
        self.assertTrue(direct_check(lp, w))
        wrong = dict(w)
        wrong['a', 0] = F(0)
        self.assertFalse(direct_check(lp, wrong))
        wrong = dict(w)
        wrong['f', 1, 2] = F(0)
        self.assertFalse(direct_check(lp, wrong))
        wrong = dict(w)
        wrong['g', 0] = F(100)
        self.assertFalse(direct_check(lp, wrong))

    def test_immutable_maps_and_digest_repeatability(self):
        dual, _, H, lp = build_case()
        self.assertEqual(lp, build_rational_pricing_lp(dual, H))
        self.assertEqual(lp.lp_digest, build_rational_pricing_lp(dual, H).lp_digest)
        with self.assertRaises(TypeError):
            lp.objective['x', 0] = F(999)
        with self.assertRaises(TypeError):
            lp.equalities[0].coefficients['x', 0] = F(999)

    def test_gurobi_pricing_p0_p5_matrix_parity_when_available(self):
        """No ambiente com Gurobi, confronta CADA linha com o pricing real.

        Não usa o status/ObjBound do solver como prova; apenas confere a
        transcrição simbólica P0--P5 antes de certificar pelo N2 racional.
        """
        try:
            from n2_t2b_pricing import build_pricing_model
        except ImportError as exc:
            if exc.name in ('gurobipy', 'n2_t2b_pricing'):
                return  # a E3 é independente do solver; rodar no ambiente do usuário
            raise
        for n in (1, 2, 3, 4):
            H = path_graph(n)
            dual, _, _, lp = build_case(n, H=H, S=(0,), T=(n - 1,),
                                        pi={0: F(3, 2)}, tau={n-1: F(-1, 4)},
                                        mu={v: F(v + 1, 3) for v in H})
            master = SimpleNamespace(V=dual.V, S=dual.S, T=dual.T,
                                     reach_graph=H)
            values = SimpleNamespace(pi=dual.pi, tau=dual.tau, mu=dual.mu)
            md, _, _, _ = build_pricing_model(master, values)
            try:
                def varname(var):
                    return f'{var[0]}[{",".join(map(str, var[1:]))}]'

                self.assertEqual({v.VarName for v in md.getVars()},
                                 {varname(v) for v in lp.variables})
                for var in lp.variables:
                    real = md.getVarByName(varname(var))
                    self.assertAlmostEqual(real.Obj, float(lp.objective[var]), places=12)
                    if var[0] in ('x', 'a', 'b', 'rho'):
                        self.assertEqual(real.VType, 'B')
                    else:
                        self.assertEqual(real.VType, 'C')

                def row_name(row):
                    return (row.name[0] if len(row.name) == 1 else
                            f'{row.name[0]}[{",".join(map(str, row.name[1:]))}]')

                rows = lp.equalities + lp.inequalities
                self.assertEqual({c.ConstrName for c in md.getConstrs()},
                                 {row_name(r) for r in rows})
                for row in rows:
                    actual = md.getConstrByName(row_name(row))
                    sign = -1 if actual.Sense == '<' else 1
                    self.assertEqual(actual.Sense == '=', row in lp.equalities)
                    expr = md.getRow(actual)
                    coefficients = {}
                    for j in range(expr.size()):
                        key = expr.getVar(j).VarName
                        coefficients[key] = coefficients.get(key, 0) + sign * expr.getCoeff(j)
                    self.assertEqual(
                        {key: value for key, value in coefficients.items() if value != 0},
                        {varname(var): float(value)
                         for var, value in row.coefficients.items()},
                        row.name,
                    )
                    self.assertEqual(sign * actual.RHS, float(row.rhs), row.name)
            finally:
                md.dispose()

    def test_graph_validation_not_just_direct_pairs(self):
        H = path_graph(4)
        dual, _, _, lp = build_case(4, H=H, S=(0,), T=(3,))
        H2 = {v: set(neighbors) for v, neighbors in H.items()}
        H2[1].add(3)
        H2[3].add(1)
        # D continua vazio em ambas as topologias.
        self.assertEqual(dual.D, ())
        self.assertNotEqual(lp.graph_digest, build_rational_pricing_lp(dual, H2).graph_digest)
        self.assertIsInstance(certify_box_bound(dual, H2, lp), BoxAbstention)
        with self.assertRaises(ValueError):
            build_rational_pricing_lp(dual, {0: set(), 1: set(), 2: set(), 3: set()})


class BoxProofTests(unittest.TestCase):
    def test_zero_multipliers_exact_formula(self):
        dual, D, H, lp = build_case(3, pi={0: F(5, 3)}, tau={2: F(-1, 2)},
                                    mu={0: F(1, 2), 1: F(2, 3), 2: F(1, 4)})
        result = certify_box_bound(dual, H, lp)
        self.assertIsInstance(result, GlobalPricingBound)
        self.assertEqual(result.source, BOX_SOURCE)
        self.assertEqual(result.ell, F(-5, 3))
        self.assertEqual(result.evidence['constant'], F(0))
        self.assertEqual(result.evidence['box_contribution'], F(-5, 3))
        cert = evaluate_box_theorem_l(dual, H, lp, result, D)
        self.assertEqual((cert.status, cert.scope, cert.source),
                         (CERTIFIED, LP_SCOPE, BOX_SOURCE))
        self.assertEqual(cert.ell_exact, result.ell)
        self.assertEqual(evaluate_theorem_l(dual, result, D).status, UNCERTIFIED)

    def test_theta_unrestricted_positive_and_negative(self):
        dual, _, H, lp = build_case()
        theta = {row.name: F(i - 2, 3) for i, row in enumerate(lp.equalities)}
        bound = certify_box_bound(dual, H, lp, theta=theta)
        self.assertEqual(dict(bound.evidence['theta']), theta)
        self.assertEqual(type(bound.ell), F)

    def test_negative_nu_projected_and_evidence_recorded(self):
        dual, D, H, lp = build_case()
        nu = {row.name: F(-i - 1, 7) for i, row in enumerate(lp.inequalities)}
        candidate = certify_box_bound(dual, H, lp, nu=nu)
        self.assertTrue(all(x == 0 for _, x in candidate.evidence['nu']))
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, candidate, D).status,
                         CERTIFIED)

    def test_fractional_coefficients_and_all_variables_proved(self):
        dual, D, H, lp = build_case(3, pi={0: F(2, 3)}, tau={2: F(3, 7)},
                                    mu={0: F(4, 11), 1: F(6, 13), 2: F(2, 9)},
                                    K=(frozenset({1}),))
        theta = {row.name: F(i + 1, 37) for i, row in enumerate(lp.equalities)}
        nu = {row.name: F(i + 1, 43) for i, row in enumerate(lp.inequalities)}
        result = certify_box_bound(dual, H, lp, theta, nu)
        self.assertIsInstance(result.ell, F)
        self.assertIsInstance(result.evidence['constant'], F)
        self.assertIsInstance(result.evidence['box_contribution'], F)
        cert = evaluate_box_theorem_l(dual, H, lp, result, D)
        self.assertEqual(cert.status, CERTIFIED)
        self.assertIsInstance(cert.lb_exact, F)
        self.assertEqual(cert.vector_digest, dual.vector_digest)
        self.assertEqual(cert.k_hash, dual.k_hash)
        self.assertEqual(cert.justification.count('H-K'), 1)

    def test_n2_not_mistaken_for_min_station_or_g2(self):
        dual, D, H, lp = build_case()
        cert = evaluate_box_theorem_l(dual, H, lp,
                                       certify_box_bound(dual, H, lp), D)
        self.assertNotIn('MIN-STATION', cert.scope)
        self.assertEqual(cert.scope, LP_SCOPE)
        self.assertEqual(cert.source, BOX_SOURCE)
        self.assertFalse(hasattr(cert, 'converged'))

    def test_forged_global_bound_and_ell_rejected(self):
        dual, D, H, lp = build_case()
        correct = certify_box_bound(dual, H, lp)
        forged = replace(correct, ell=correct.ell + 1)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, forged, D).status,
                         UNCERTIFIED)
        data = dict(correct.evidence)
        data['method'] = 'ObjBoundC'
        forged = replace(correct, evidence=MappingProxyType(data))
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, forged, D).status,
                         UNCERTIFIED)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, 123.45, D).status,
                         UNCERTIFIED)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp,
                         GlobalPricingBound(F(999), 'N2', dual.vector_digest, {}), D).status,
                         UNCERTIFIED)

    def test_matrix_tamper_even_if_digest_forged(self):
        dual, D, H, lp = build_case()
        good = certify_box_bound(dual, H, lp)
        bad_objective = MappingProxyType({**lp.objective, ('a', 0): F(-1000)})
        tampered = replace(lp, objective=bad_objective)
        self.assertIsInstance(certify_box_bound(dual, H, tampered), BoxAbstention)
        self.assertEqual(evaluate_box_theorem_l(dual, H, tampered, good, D).status,
                         UNCERTIFIED)
        row = lp.inequalities[0]
        modified_row = replace(row, rhs=F(-10))
        tampered = replace(lp, inequalities=(modified_row,) + lp.inequalities[1:])
        self.assertIsInstance(certify_box_bound(dual, H, tampered), BoxAbstention)
        tampered = replace(lp, upper=MappingProxyType({**lp.upper, ('g', 0): F(10_000)}))
        self.assertIsInstance(certify_box_bound(dual, H, tampered), BoxAbstention)
        tampered = replace(lp, equalities=lp.equalities[1:])
        self.assertIsInstance(certify_box_bound(dual, H, tampered), BoxAbstention)
        tampered = replace(lp, lp_digest='nonsense')
        self.assertIsInstance(certify_box_bound(dual, H, tampered), BoxAbstention)

    def test_other_vector_revision_and_bad_direct_pairs(self):
        dual, _, H, lp = build_case()
        good = certify_box_bound(dual, H, lp)
        modified_dual, D2 = make_dual(H, (0,), (2,), revision=99)
        self.assertEqual(evaluate_box_theorem_l(modified_dual, H, lp, good, D2).status,
                         UNCERTIFIED)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, good, ((0, 2),)).status,
                         UNCERTIFIED)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, good, None).status,
                         UNCERTIFIED)

    def test_forged_multipliers_or_evidence_rejected(self):
        dual, D, H, lp = build_case()
        bound = certify_box_bound(dual, H, lp)
        data = dict(bound.evidence)
        data['theta'] = ((('P4', 0), F(10)),)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp,
                         replace(bound, evidence=data), D).status, UNCERTIFIED)
        data = dict(bound.evidence)
        data['nu'] = tuple((row.name, F(-1)) for row in lp.inequalities)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp,
                         replace(bound, evidence=data), D).status, UNCERTIFIED)
        data = dict(bound.evidence)
        data['graph_digest'] = 'forged'
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp,
                         replace(bound, evidence=data), D).status, UNCERTIFIED)

    def test_reject_wrong_theta_nu_indices_nan_inf_objbound(self):
        dual, _, H, lp = build_case()
        bad = {row.name: F(0) for row in lp.equalities[1:]}
        with self.assertRaises(ValueError):
            certify_box_bound(dual, H, lp, theta=bad)
        for bad_value in (float('nan'), float('inf'), float('-inf'), True):
            theta = {row.name: F(0) for row in lp.equalities}
            theta[lp.equalities[0].name] = bad_value
            with self.assertRaises(ValueError):
                certify_box_bound(dual, H, lp, theta=theta)
        with self.assertRaises(ValueError):
            certify_box_bound(dual, H, lp, nu={('ObjBoundC',): 42.0})

    def test_float_dual_mult_converted_exactly(self):
        dual, D, H, lp = build_case()
        theta = {row.name: -0.1 for row in lp.equalities}
        nu = {row.name: 0.2 for row in lp.inequalities}
        bound = certify_box_bound(dual, H, lp, theta, nu)
        self.assertEqual(dict(bound.evidence['theta'])[lp.equalities[0].name],
                         F.from_float(-0.1))
        self.assertEqual(dict(bound.evidence['nu'])[lp.inequalities[0].name],
                         F.from_float(0.2))
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, bound, D).status, CERTIFIED)

    def test_zero_nu_with_theta_different_from_optimal_still_valid(self):
        dual, _, H, lp = build_case(n=3, pi={0: F(4)}, tau={2: F(1)})
        theta = {row.name: F(-200) for row in lp.equalities}
        bound = certify_box_bound(dual, H, lp, theta=theta)
        true_min, _, _ = brute_force(dual, H)
        self.assertLessEqual(bound.ell, true_min)

    def test_random_exact_n2_less_than_true_cstar_100_graphs(self):
        rng = random.Random(20261010)
        for i in range(100):
            n = rng.randrange(1, 7)
            H = connected_graph(rng, n)
            s = (rng.randrange(n),)
            t = (rng.randrange(n),)
            pi = {s[0]: F(rng.randint(-6, 7), rng.randint(1, 5))}
            tau = {t[0]: F(rng.randint(-5, 6), rng.randint(1, 6))}
            mu = {v: F(rng.randrange(0, 6), rng.randint(1, 7)) for v in H}
            dual, D, _, lp = build_case(n, H=H, S=s, T=t, pi=pi, tau=tau, mu=mu)
            true_min, _, _ = brute_force(dual, H)
            for mode in (0, 1, 2):
                theta = {row.name: F(rng.randint(-6, 6), rng.randint(1, 7))
                         for row in lp.equalities} if mode else None
                nu = {row.name: F(rng.randint(-5, 7), rng.randint(1, 9))
                      for row in lp.inequalities} if mode == 2 else None
                bound = certify_box_bound(dual, H, lp, theta, nu)
                self.assertLessEqual(bound.ell, true_min, (i, n, mode))
                self.assertEqual(evaluate_box_theorem_l(dual, H, lp,
                                 bound, D).status, CERTIFIED)

    def test_n1_enum_n2_separate_sources_and_values(self):
        dual, D, H, lp = build_case(n=3, pi={0: F(4)}, tau={2: F(1)},
                                    mu={0: F(1), 1: F(1), 2: F(2)})
        n1 = analytical_bound_n1(dual)
        enum = enumerate_global_bound(dual, H, cap=10)
        box = certify_box_bound(dual, H, lp)
        self.assertEqual(evaluate_theorem_l(dual, n1, D).source, 'N1')
        self.assertEqual(evaluate_enum_theorem_l(dual, enum, D, H, 10).source, 'ENUM')
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, box, D).source, 'N2')
        self.assertLessEqual(box.ell, enum.ell)
        self.assertLessEqual(n1.ell, enum.ell)


class LPSuggestionTests(unittest.TestCase):
    def test_scipy_suggestion_is_only_numeric_candidate(self):
        try:
            import scipy  # noqa: F401
        except ImportError:
            return  # sem SciPy, o módulo exato continua independente
        dual, D, H, lp = build_case(3, pi={0: F(3)}, tau={2: F(2)})
        theta, nu = propose_lp_multipliers(lp)
        self.assertEqual(set(theta), {row.name for row in lp.equalities})
        self.assertEqual(set(nu), {row.name for row in lp.inequalities})
        self.assertTrue(all(v >= 0 for v in nu.values()))
        bound = certify_box_bound(dual, H, lp, theta, nu)
        self.assertEqual(evaluate_box_theorem_l(dual, H, lp, bound, D).status,
                         CERTIFIED)
        true_min, _, _ = brute_force(dual, H)
        self.assertLessEqual(bound.ell, true_min)

    def test_scipy_lp_bound_sanity_multiple_graphs(self):
        try:
            import scipy  # noqa: F401
        except ImportError:
            return
        for n in (1, 2, 3, 4):
            H = path_graph(n)
            dual, D, _, lp = build_case(n, H=H, S=(0,), T=(n-1,),
                                        pi={0: F(2)}, tau={n-1: F(1)},
                                        mu={v: F(1) for v in H})
            theta, nu = propose_lp_multipliers(lp)
            bound = certify_box_bound(dual, H, lp, theta, nu)
            self.assertEqual(evaluate_box_theorem_l(dual, H, lp, bound, D).status,
                             CERTIFIED)
            true_min, _, _ = brute_force(dual, H)
            self.assertLessEqual(bound.ell, true_min)


if __name__ == '__main__':
    unittest.main()
