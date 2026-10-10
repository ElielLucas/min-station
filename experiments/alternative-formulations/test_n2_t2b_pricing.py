"""Entrega 2: testes do oráculo de pricing P0--P5, fora do corpus N2.

Requer Gurobi (não ignora testes se dependência/licença faltar). Execute:
PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations \
    -p test_n2_t2b_pricing.py -v
O controle principal compara o MIP com a enumeração independente de Q em
Python puro (test_n2_t2b_controles_matematicos.alcance/colunas, BFS próprio,
sem fcc.py). Não é benchmark nem certificação de limites inferiores.
"""
# E402: bootstrap experimental; E741: correspondência com q=(W,I,J).
# ruff: noqa: E402, E741
import math
import random
import sys
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from fcc import grafo_H
from ms_utils import construir_adjacencia, construir_arcos_alcance
from n2_t2b_master import RestrictedMaster, StaleDualError, numerical_dual
import n2_t2b_pricing as pr
from test_n2_t2b_controles_matematicos import alcance, colunas

TOL = 1e-6  # comparação numérica MIP x enumeração (floats); não é margem de certificado


def instance(V, edges, S, T, r=1):
    arcs = [(u, v, 1) for a, b in edges for u, v in ((a, b), (b, a))]
    adj = construir_adjacencia(arcs)
    return tuple(S), tuple(T), tuple(V), adj, construir_arcos_alcance(V, adj, r), r


def enumerated(data, values):
    """Q por enumeração independente e o custo reduzido de cada coluna."""
    S, T, V, _adj, _A_r, r = data
    edges = sorted({tuple(sorted((u, w))) for u, nbrs in _adj.items() for w, _c in nbrs})
    neigh, _D = alcance(list(V), edges, r)
    Q = colunas(list(S), list(T), list(V), neigh)
    costs = {q: math.fsum([values.mu[v] for v in q[0]] + [-values.pi[s] for s in q[1]]
                          + [-values.tau[t] for t in q[2]]) for q in Q}
    return Q, costs


def random_instance(rng, n_max=6):
    n = rng.randint(1, n_max)
    V = [f'v{i}' for i in range(n)]
    edges = {(V[rng.randrange(i)], V[i]) for i in range(1, n)}
    for _ in range(rng.randint(0, n)):
        if n > 1:
            a, b = rng.sample(V, 2)
            if (b, a) not in edges:
                edges.add((a, b))
    m = rng.randint(1, min(3, n))
    return instance(V, sorted(edges), rng.sample(V, m), rng.sample(V, m), rng.choice([1, 1, 2]))


def path(n, S, T, r=1):
    V = [chr(ord('a') + i) for i in range(n)]
    return instance(V, list(zip(V, V[1:])), S, T, r)


class PricingTests(unittest.TestCase):
    def master(self, data):
        master = RestrictedMaster(*data)
        self.addCleanup(master.dispose)
        return master

    def vector(self, master, pi=None, tau=None, mu=None, kappa=None):
        return numerical_dual(master.S, master.T, master.V, master.K,
                              pi=pi or dict.fromkeys(master.S, 0.0),
                              tau=tau or dict.fromkeys(master.T, 0.0),
                              mu=mu or dict.fromkeys(master.V, 0.0),
                              kappa=kappa or dict.fromkeys(master.K, 0.0))

    def assert_matches_enumeration(self, data, master, result, values):
        Q, costs = enumerated(data, values)
        best = min(costs.values())
        self.assertEqual(result.termination, pr.NUMERICALLY_OPTIMAL, result.error)
        self.assertIn(result.outcome, (pr.NEGATIVE_COLUMN, pr.NONNEGATIVE_INCUMBENT))
        self.assertIn(result.column, set(Q))  # admissível segundo a enumeração independente
        self.assertAlmostEqual(result.reduced_cost, costs[result.column], delta=1e-12)
        self.assertAlmostEqual(result.reduced_cost, best, delta=TOL)
        self.assertLessEqual(result.objective_mismatch, result.mismatch_tolerance)
        self.assertEqual(result.outcome == pr.NEGATIVE_COLUMN,
                         result.reduced_cost < -result.entry_tolerance)
        self.assertEqual(result.certification_status, pr.UNCERTIFIED)
        self.assertFalse(result.proves_no_negative_column)
        return best, {q for q, c in costs.items() if abs(c - best) <= TOL}

    # ── 7.1 enumeração completa ──────────────────────────────────────────

    def test_random_vectors_match_full_enumeration(self):
        rng = random.Random(20261009)
        for case in range(60):
            data = random_instance(rng)
            master = self.master(data)
            values = self.vector(
                master,
                pi={s: rng.choice([-2, -1, -0.5, 0, 0.5, 1, 2, 3]) for s in master.S},
                tau={t: rng.choice([-2, -1, 0, 0.25, 1, 2]) for t in master.T},
                mu={v: rng.choice([-0.5, 0, 0, 0.5, 1, 2]) for v in master.V},
                kappa={Z: rng.choice([0, 0.5, 1]) for Z in master.K},
            )
            with self.subTest(case=case, V=master.V, S=master.S, T=master.T):
                self.assert_matches_enumeration(data, master, pr.price_vector(master, values), values)

    def test_master_snapshots_match_full_enumeration(self):
        rng = random.Random(7)
        checked = 0
        for case in range(25):
            data = random_instance(rng)
            master = self.master(data)
            Q, _ = enumerated(data, self.vector(master))
            for column in rng.sample(Q, min(3, len(Q))):
                if column not in master.columns:
                    master.add_column(column)
            result = master.solve()
            self.assertIsNotNone(result.dual, result.error)
            with self.subTest(case=case):
                priced = pr.price(master, result.dual)
                self.assert_matches_enumeration(data, master, priced, result.dual.values)
                self.assertEqual((priced.revision, priced.solve_id),
                                 (result.dual.revision, result.dual.solve_id))
                self.assertEqual(priced.dual_source, 'MASTER_SNAPSHOT')
                checked += 1
        self.assertEqual(checked, 25)

    # ── 7.2 casos matemáticos ────────────────────────────────────────────

    def test_connectivity_only_in_H(self):
        # a..g, r=2: único W ótimo é {c,e}, conexo em H e desconexo em G.
        data = path(7, ['a'], ['g'], r=2)
        master = self.master(data)
        mu = {v: 5.0 for v in master.V} | {'c': 1.0, 'e': 1.0}
        values = self.vector(master, pi={'a': 10.0}, mu=mu)
        result = pr.price_vector(master, values)
        best, argmin = self.assert_matches_enumeration(data, master, result, values)
        self.assertEqual(argmin, {(frozenset('ce'), frozenset('a'), frozenset('g'))})
        self.assertEqual(result.column[0], frozenset('ce'))
        self.assertAlmostEqual(best, -8.0)

    def test_disconnected_W_in_H_is_never_returned(self):
        # Sem P3--P5, {a,e} (custo 0) venceria; com P3--P5 o ótimo usa o caminho.
        data = path(5, ['a', 'e'], ['a', 'e'])
        master = self.master(data)
        mu = {'a': 0.0, 'b': 1.0, 'c': 1.0, 'd': 1.0, 'e': 0.0}
        values = self.vector(master, pi={'a': 1.0, 'e': 1.0}, tau={'a': 1.0, 'e': 1.0}, mu=mu)
        result = pr.price_vector(master, values)
        self.assert_matches_enumeration(data, master, result, values)
        H = master.reach_graph
        W = result.column[0]
        self.assertTrue(len(W) == 1 or all(H[v] & W for v in W))
        with patch.object(pr, '_add_connectivity', lambda *args: None):
            broken = pr.price_vector(master, values)
        self.assertEqual(broken.outcome, pr.INVALID_INCUMBENT)  # validação barra o defeito
        self.assertIsNone(broken.column)

    def test_shared_terminals_S_equals_T_and_independent_roles(self):
        data = instance(('a', 'b', 'c'), (('a', 'b'), ('b', 'c')), ('a', 'c'), ('a', 'c'))
        master = self.master(data)
        values = self.vector(master, pi={'a': 2.0, 'c': -1.0}, tau={'a': -1.0, 'c': 2.0},
                             mu={'a': 0.0, 'b': 0.5, 'c': 0.0})
        result = pr.price_vector(master, values)
        _, argmin = self.assert_matches_enumeration(data, master, result, values)
        # Melhor: origem a e destino c (sem matching fixo, I≠J permitido).
        self.assertTrue(all(q[1] == {'a'} and q[2] == {'c'} for q in argmin))
        self.assertAlmostEqual(result.reduced_cost, -3.5)
        # Mesmo vértice nos dois papéis.
        values = self.vector(master, pi={'a': 2.0, 'c': -5.0}, tau={'a': 2.0, 'c': -5.0},
                             mu={'a': 0.25, 'b': 3.0, 'c': 3.0})
        result = pr.price_vector(master, values)
        self.assert_matches_enumeration(data, master, result, values)
        self.assertEqual(result.column, (frozenset('a'), frozenset('a'), frozenset('a')))

    def test_terminal_as_station(self):
        # TermRelay: s2 só alcança t2 por t1; a estação ótima é o destino t1.
        data = instance(('s1', 's2', 't1', 't2'), (('s1', 't1'), ('s2', 't1'), ('t1', 't2')),
                        ('s1', 's2'), ('t1', 't2'))
        master = self.master(data)
        values = self.vector(master, pi={'s1': 0.0, 's2': 2.0}, tau={'t1': 0.0, 't2': 1.0},
                             mu=dict.fromkeys(master.V, 1.0))
        result = pr.price_vector(master, values)
        _, argmin = self.assert_matches_enumeration(data, master, result, values)
        self.assertIn('t1', result.column[0])
        self.assertTrue(all('t1' in q[0] for q in argmin))

    def test_single_vertex_instance(self):
        data = instance(('a',), (), ('a',), ('a',))
        master = self.master(data)
        for pi in (3.0, 0.0, -2.0):
            values = self.vector(master, pi={'a': pi}, mu={'a': 1.0})
            result = pr.price_vector(master, values)
            self.assert_matches_enumeration(data, master, result, values)
            self.assertEqual(result.column, (frozenset('a'),) * 3)
            self.assertAlmostEqual(result.reduced_cost, 1.0 - pi)

    def test_negative_zero_and_positive_reduced_costs(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        mu = dict.fromkeys(master.V, 1.0)
        for pi, expected, outcome in ((3.0, -2.0, pr.NEGATIVE_COLUMN),
                                      (1.0, 0.0, pr.NONNEGATIVE_INCUMBENT),
                                      (-1.0, 2.0, pr.NONNEGATIVE_INCUMBENT)):
            values = self.vector(master, pi={'a': pi}, mu=mu)
            result = pr.price_vector(master, values)
            self.assert_matches_enumeration(data, master, result, values)
            self.assertAlmostEqual(result.reduced_cost, expected)
            self.assertEqual(result.outcome, outcome)
            self.assertFalse(result.proves_no_negative_column)

    def test_multiple_optima_and_degenerate_vectors(self):
        data = instance(('a', 'b', 'c', 'd'), (('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'a')),
                        ('a', 'b'), ('c', 'd'))
        master = self.master(data)
        zero = self.vector(master)
        result = pr.price_vector(master, zero)
        _, argmin = self.assert_matches_enumeration(data, master, result, zero)
        self.assertGreater(len(argmin), 1)
        self.assertIn(result.column, argmin)  # não depende de qual ótimo foi escolhido
        tie = self.vector(master, pi={'a': 1.0, 'b': 1.0}, tau={'c': 1.0, 'd': 1.0},
                          mu=dict.fromkeys(master.V, 1.0))
        result = pr.price_vector(master, tie)
        _, argmin = self.assert_matches_enumeration(data, master, result, tie)
        self.assertGreater(len(argmin), 1)
        self.assertIn(result.column, argmin)

    def test_balance_forces_negative_prize_when_needed(self):
        # Todo τ é negativo; |I|=|J|>=1 obriga a pagar ao menos um (k=1 vale -1, k=2 vale -2).
        data = path(3, ['a', 'b'], ['c', 'b'])
        master = self.master(data)
        values = self.vector(master, pi={'a': 5.0, 'b': 5.0}, tau={'c': -4.0, 'b': -4.0},
                             mu=dict.fromkeys(master.V, 0.0))
        result = pr.price_vector(master, values)
        self.assert_matches_enumeration(data, master, result, values)
        W, I, J = result.column
        self.assertEqual(len(I), len(J))
        self.assertGreaterEqual(len(I), 1)
        self.assertAlmostEqual(result.reduced_cost, -2.0)

    # ── 7.3 robustez ─────────────────────────────────────────────────────

    def test_snapshot_compatibility_is_enforced(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        first = master.solve().dual
        pr.price(master, first)
        master.add_column((frozenset('b'), frozenset('a'), frozenset('c')))
        with self.assertRaises(StaleDualError):
            pr.price(master, first)  # revisão nova, sem dual corrente
        second = master.solve().dual
        with self.assertRaises(StaleDualError):
            pr.price(master, first)  # dual de iteração anterior
        other = self.master(data)
        other.solve()
        with self.assertRaises(StaleDualError):
            pr.price(other, second)  # dual de outro master
        with self.assertRaises(pr.PricingInputError):
            pr.price(master, None)
        self.assertEqual(pr.price(master, second).dual_source, 'MASTER_SNAPSHOT')

    def test_missing_nonfinite_and_wrong_ids_are_rejected(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        good = self.vector(master)
        bad_values = [
            good.__class__(MappingProxyType({}), good.tau, good.mu, good.kappa, good.eta, good.L),
            good.__class__(MappingProxyType({'z': 0.0}), good.tau, good.mu, good.kappa,
                           good.eta, good.L),
            good.__class__(good.pi, MappingProxyType({'c': float('nan')}), good.mu, good.kappa,
                           good.eta, good.L),
            good.__class__(good.pi, good.tau, MappingProxyType(dict(good.mu) | {'b': math.inf}),
                           good.kappa, good.eta, good.L),
            good.__class__(good.pi, good.tau, good.mu, MappingProxyType({}), good.eta, good.L)
            if master.K else None,
        ]
        for values in filter(None, bad_values):
            with self.assertRaises(pr.PricingInputError):
                pr.price_vector(master, values)
        with self.assertRaises(pr.PricingInputError):
            pr.price_vector(master, {'pi': {}, 'tau': {}, 'mu': {}})
        other = self.master(path(3, ['a'], ['b']))
        with self.assertRaises(pr.PricingInputError):
            pr.price_vector(other, good)  # índices de outra instância
        with self.assertRaises(pr.PricingInputError):
            pr.price_vector(master, good, params={'Method': 1})
        with self.assertRaises(pr.PricingInputError):
            pr.price_vector(master, good, entry_tolerance=-1.0)

    def grid(self):
        V = [f'{i}{j}' for i in range(4) for j in range(4)]
        edges = [(f'{i}{j}', f'{i + 1}{j}') for i in range(3) for j in range(4)]
        edges += [(f'{i}{j}', f'{i}{j + 1}') for i in range(4) for j in range(3)]
        return instance(V, edges, ('00', '03', '30', '33'), ('11', '12', '21', '22'))

    def test_interrupted_with_incumbent_is_usable_but_proves_nothing(self):
        master = self.master(self.grid())
        snapshot = master.solve().dual
        full = pr.price(master, snapshot)
        self.assertEqual(full.outcome, pr.NEGATIVE_COLUMN)
        cut = pr.price(master, snapshot, params={'SolutionLimit': 1})
        self.assertEqual(cut.termination, pr.OTHER_LIMIT)
        self.assertEqual(cut.status_name, 'SOLUTION_LIMIT')
        self.assertGreaterEqual(cut.solution_count, 1)
        self.assertIsNotNone(cut.column)
        master.validate_column(cut.column)
        self.assertAlmostEqual(cut.reduced_cost, snapshot.values.column_rc(cut.column))
        # Sem coluna negativa no incumbente, ainda assim existe coluna negativa.
        if cut.outcome == pr.NONNEGATIVE_INCUMBENT:
            self.assertLess(full.reduced_cost, -cut.entry_tolerance)
        self.assertFalse(cut.proves_no_negative_column)
        self.assertEqual(cut.certification_status, pr.UNCERTIFIED)

    def test_interrupted_without_incumbent(self):
        master = self.master(self.grid())
        snapshot = master.solve().dual
        result = pr.price(master, snapshot, params={'TimeLimit': 0.0})
        self.assertEqual(result.termination, pr.TIME_LIMIT)
        self.assertEqual(result.outcome, pr.NO_INCUMBENT)
        self.assertIsNone(result.column)
        self.assertIsNone(result.reduced_cost)
        self.assertFalse(result.proves_no_negative_column)

    def test_objective_mismatch_is_detected(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        values = self.vector(master, pi={'a': 3.0}, mu=dict.fromkeys(master.V, 1.0))
        original = pr._objective_coefficients

        def shifted(m, v):
            cx, ca, cb = original(m, v)
            return {k: c + 0.25 for k, c in cx.items()}, ca, cb

        with patch.object(pr, '_objective_coefficients', shifted):
            result = pr.price_vector(master, values)
        self.assertEqual(result.outcome, pr.OBJECTIVE_MISMATCH)
        self.assertIsNone(result.column)
        self.assertGreater(result.objective_mismatch, result.mismatch_tolerance)

    def test_nonintegral_incumbent_is_rejected(self):
        # Coluna combinatoriamente válida (x,a,b intactos), mas uma binária
        # (rho) fracionária: a integralidade sozinha deve barrar o incumbente.
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        values = self.vector(master, pi={'a': 3.0}, mu=dict.fromkeys(master.V, 1.0))
        accepted = pr.price_vector(master, values)
        self.assertEqual(accepted.outcome, pr.NEGATIVE_COLUMN)
        self.assertLessEqual(accepted.max_integrality_violation, pr.INTEGRALITY_TOLERANCE)
        original = pr._binary_values
        for perturbed in (0.3, 10 * pr.INTEGRALITY_TOLERANCE, math.nan):
            def fractional(md, eps=perturbed):
                vals = list(original(md))
                vals[-1] = abs(vals[-1] - eps) if math.isfinite(eps) else eps
                return vals
            with self.subTest(perturbed=perturbed), \
                    patch.object(pr, '_binary_values', fractional):
                result = pr.price_vector(master, values)
                self.assertEqual(result.outcome, pr.INVALID_INCUMBENT)
                self.assertIsNone(result.column)
                self.assertIsNone(result.reduced_cost)
                self.assertGreater(result.max_integrality_violation, pr.INTEGRALITY_TOLERANCE)
                self.assertIn('não inteiro', result.error)
                self.assertEqual(result.termination, pr.NUMERICALLY_OPTIMAL)
                self.assertEqual(result.certification_status, pr.UNCERTIFIED)
        # Violação abaixo da tolerância continua aceita.
        def tiny(md):
            vals = list(original(md))
            vals[-1] = abs(vals[-1] - pr.INTEGRALITY_TOLERANCE / 10)
            return vals
        with patch.object(pr, '_binary_values', tiny):
            self.assertEqual(pr.price_vector(master, values).outcome, pr.NEGATIVE_COLUMN)

    def test_optimal_is_never_certified_and_bound_is_diagnostic(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        result = pr.price_vector(master, self.vector(master, mu=dict.fromkeys(master.V, 1.0)))
        self.assertEqual(result.termination, pr.NUMERICALLY_OPTIMAL)
        self.assertEqual(result.outcome, pr.NONNEGATIVE_INCUMBENT)
        self.assertEqual(result.certification_status, pr.UNCERTIFIED)
        self.assertFalse(result.proves_no_negative_column)
        self.assertEqual(result.pricing_label, 'heuristic')
        self.assertEqual(result.scope, 'PRICING_NUMERICAL_ONLY')
        self.assertIsNotNone(result.solver_bound)  # registrado, não usado como ℓ
        self.assertFalse(any('LB' in name for name in result.__dataclass_fields__))

    def test_solver_error_is_explicit(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        values = self.vector(master)
        with patch.object(pr.gp.Model, 'optimize', side_effect=pr.gp.GurobiError(10001, 'falha')):
            result = pr.price_vector(master, values)
        self.assertEqual(result.outcome, pr.SOLVER_ERROR)
        self.assertEqual(result.termination, pr.SOLVER_FAILURE)
        self.assertIsNone(result.column)
        self.assertIn('10001', result.error)

    def test_pricing_does_not_modify_master_or_write_files(self):
        data = path(3, ['a'], ['c'])
        master = self.master(data)
        snapshot = master.solve().dual
        before = (master.columns, dict(master.metadata))
        result = pr.price(master, snapshot)
        self.assertEqual(result.outcome, pr.NEGATIVE_COLUMN)
        self.assertEqual((master.columns, dict(master.metadata)), before)
        self.assertIs(master.extract_duals(), snapshot)  # snapshot continua corrente
        results_dir = ROOT / 'results' / 'alternative-formulations'
        self.assertFalse(any(p.name.startswith('n2-') for p in results_dir.iterdir()))

    def test_reach_graph_is_read_only_and_equals_fcc_H(self):
        data = path(5, ['a'], ['e'], r=2)
        master = self.master(data)
        H = master.reach_graph
        self.assertEqual({v: set(n) for v, n in H.items()}, grafo_H(master.V, data[4]))
        with self.assertRaises(TypeError):
            H['a'] = frozenset()
        self.assertIsInstance(H['a'], frozenset)


if __name__ == '__main__':
    unittest.main()
