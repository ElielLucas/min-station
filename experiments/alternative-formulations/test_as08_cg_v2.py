"""AS-08 CG v2: contagem exata de linhas, caps, pricing otimizado, seleção e prazos.

Regressões das correções pós-piloto 002. Nenhum teste altera B1–B4/K: todos
comparam contra o modelo compilado, a enumeração completa (T2a) ou um oráculo
Bellman-Ford independente do Dijkstra de produção.
"""
from __future__ import annotations

import importlib.util
import random
import sys
import time
import unittest
from fractions import Fraction
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FC_DIR = _PROJECT_ROOT / 'experiments' / 'formulation-comparison'
if str(_FC_DIR) not in sys.path:
    sys.path.insert(0, str(_FC_DIR))

from as02_model_a import Instance
from as02_solve import solve
from as08_b_exact import compile_b, enumerate_paths
from as08_column_generation import (CGConfig, SELECTIONS, compile_rmp, rmp_row_counts,
                                    b3_pairs_of, run_column_generation, select_columns,
                                    selection_order, verify_rational_certificate)
from as08_pricing import PricedPath, prepare_pricing, price_all, price_source
from run_as08_b_pilot import make_plan, validate_plan, verify, verify_progress, progress_record
from run_as08_t2a import FIXTURES, build_fixture

BACKEND = 'gurobi' if importlib.util.find_spec('gurobipy') else 'scipy-highs'


def bellman_ford(ins: Instance, source, pi, tau, gamma, mu):
    """Oráculo independente: menor passeio com custo nos vértices internos.

    Pesos >= 0, então o menor passeio que não reentra na origem tem o custo
    do menor caminho simples. Não compartilha código com as08_pricing.
    """
    zero = Fraction(0)
    dist = {source: zero}
    for _ in range(len(ins.V)):
        changed = False
        for u, v in ins.A_r:
            if u not in dist or v == source:
                continue
            cand = dist[u] + (zero if u == source else gamma.get((source, u), zero) + mu.get(u, zero))
            if v not in dist or cand < dist[v]:
                dist[v] = cand
                changed = True
        if not changed:
            break
    return {t: dist[t] - pi[source] - tau[t] for t in ins.T if t in dist}


def random_instance(rng, n=14, density=.25):
    V = tuple(f'v{i}' for i in range(n))
    k = rng.randint(2, 4)
    S = tuple(sorted(rng.sample(V, k)))
    T = tuple(sorted(rng.sample(V, k)))  # pode sobrepor S (caminho de comprimento zero)
    A = tuple(sorted((u, v) for u in V for v in V if u != v and rng.random() < density))
    return Instance(V, S, T, A, 1)


def random_duals(rng, ins, denominators=(1, 3, 7, 10)):
    q = lambda lo, hi: Fraction(rng.randint(lo, hi), rng.choice(denominators))
    pi = {s: q(-6, 12) for s in ins.S}
    tau = {t: q(-6, 12) for t in ins.T}
    gamma = {(s, v): q(0, 5) for s in ins.S for v in ins.V if v != s and rng.random() < .4}
    mu = {v: q(0, 4) for v in ins.V if rng.random() < .5}
    return pi, tau, gamma, mu


def fake(source, target, rc, path=None):
    return PricedPath(source, target, path or (source, target), rc)


class TestOptimizedPricing(unittest.TestCase):
    def test_exact_matches_independent_bellman_ford(self):
        rng = random.Random(20261012)
        for _ in range(40):
            ins = random_instance(rng)
            pi, tau, gamma, mu = random_duals(rng, ins)
            priced = price_all(ins, pi, tau, gamma, mu, exact=True)
            arcs = set(ins.A_r)
            for s in ins.S:
                expected = bellman_ford(ins, s, pi, tau, gamma, mu)
                got = {p.target: p for p in priced[s]}
                self.assertEqual(set(got), set(expected))
                for t, p in got.items():
                    self.assertIsInstance(p.reduced_cost, Fraction)
                    self.assertEqual(p.reduced_cost, expected[t])
                    path = p.path
                    self.assertEqual((path[0], path[-1]), (s, t))
                    self.assertEqual(len(set(path)), len(path))
                    self.assertNotIn(s, path[1:])
                    self.assertTrue(all(a in arcs for a in zip(path, path[1:])))
                    cost = sum((gamma.get((s, v), 0) + mu.get(v, 0) for v in path[1:-1]),
                               Fraction(0)) - pi[s] - tau[t]
                    self.assertEqual(cost, p.reduced_cost)

    def test_float_mode_agrees_with_exact(self):
        rng = random.Random(7)
        for _ in range(20):
            ins = random_instance(rng)
            pi, tau, gamma, mu = random_duals(rng, ins)
            exact = price_all(ins, pi, tau, gamma, mu, exact=True)
            flt = price_all(ins, {k: float(v) for k, v in pi.items()},
                            {k: float(v) for k, v in tau.items()},
                            {k: float(v) for k, v in gamma.items()},
                            {k: float(v) for k, v in mu.items()})
            for s in ins.S:
                a = {p.target: p.reduced_cost for p in exact[s]}
                b = {p.target: p.reduced_cost for p in flt[s]}
                self.assertEqual(set(a), set(b))
                for t in a:
                    self.assertAlmostEqual(float(a[t]), b[t], places=9)

    def test_decimal_float_duals_scaled_exactly(self):
        # Duais vindos do solver: Fraction(str(float)) com denominadores 10^k.
        rng = random.Random(3)
        ins = random_instance(rng, n=12, density=.35)
        conv = lambda x: Fraction(str(x))
        pi = {s: conv(rng.uniform(-3, 9)) for s in ins.S}
        tau = {t: conv(rng.uniform(-3, 9)) for t in ins.T}
        gamma = {(s, v): conv(rng.uniform(0, 1)) for s in ins.S for v in ins.V if v != s}
        mu = {v: conv(rng.uniform(0, 1) / 3) for v in ins.V}
        priced = price_all(ins, pi, tau, gamma, mu, exact=True)
        for s in ins.S:
            self.assertEqual({p.target: p.reduced_cost for p in priced[s]},
                             bellman_ford(ins, s, pi, tau, gamma, mu))

    def test_prepared_graph_reuse_is_identical(self):
        rng = random.Random(11)
        ins = random_instance(rng)
        pi, tau, gamma, mu = random_duals(rng, ins)
        graph = prepare_pricing(ins)
        with_graph = price_all(ins, pi, tau, gamma, mu, exact=True, graph=graph)
        self.assertEqual(with_graph, price_all(ins, pi, tau, gamma, mu, exact=True))
        for s in ins.S:
            self.assertEqual(price_source(ins, s, pi, tau, gamma, mu, exact=True, graph=graph),
                             with_graph[s])

    def test_overlap_zero_length_path_kept(self):
        ins, _ = build_fixture(next(f for f in FIXTURES if f.name == 'overlap-triangle'))
        priced = price_all(ins, {s: 0 for s in ins.S}, {t: 0 for t in ins.T}, {}, {}, exact=True)
        self.assertIn(('b',), [p.path for p in priced['b']])


class TestExactRowCount(unittest.TestCase):
    def shared_instance(self):
        chain = tuple(f'c{i}' for i in range(8))
        V = ('a', 'b', *chain, 't1', 't2')
        arcs = {('a', 'c0'), ('b', 'c0'), (chain[-1], 't1'), (chain[-1], 't2')}
        arcs |= set(zip(chain, chain[1:]))
        ins = Instance(V, ('a', 'b'), ('t1', 't2'), tuple(sorted(arcs)), 1)
        columns = [(s, *chain, t) for s in ('a', 'b') for t in ('t1', 't2')]
        return ins, columns

    def test_shared_b3_pairs_counted_once(self):
        ins, columns = self.shared_instance()
        pairs = set().union(*(b3_pairs_of(p) for p in columns))
        counts = rmp_row_counts(ins, (), pairs)
        compiled, _ = compile_rmp(ins, (), columns)
        self.assertEqual(counts['B3'], 16)  # 2 origens × 8 vértices internos
        self.assertEqual(counts['total'], len(compiled.equations))
        self.assertEqual(counts['B3'], compiled.families['B3'])
        legacy = 2*len(ins.S) + len(ins.T) + sum(len(p)-2 for p in columns)
        self.assertGreater(legacy, counts['total'])  # superestimativa do piloto 002

    def test_random_column_sets_match_compiled_model(self):
        rng = random.Random(5)
        for fixture in FIXTURES:
            ins, _ = build_fixture(fixture)
            paths = [p for group in enumerate_paths(ins).by_source.values() for p in group]
            for _ in range(5):
                cols = rng.sample(paths, rng.randint(0, len(paths))) if paths else []
                K = [{v} for v in rng.sample(ins.V, min(2, len(ins.V)))]
                compiled, Kc = compile_rmp(ins, K, cols)
                pairs = set().union(set(), *(b3_pairs_of(p) for p in cols))
                counts = rmp_row_counts(ins, Kc, pairs)
                self.assertEqual(counts['total'], len(compiled.equations), fixture.name)
                for family in ('B1', 'B2', 'B3', 'B4', 'BK'):
                    self.assertEqual(counts[family], compiled.families.get(family, 0))

    def test_compile_with_graph_is_identical(self):
        ins, columns = self.shared_instance()
        a, _ = compile_rmp(ins, [{'c3'}], columns)
        b, _ = compile_rmp(ins, [{'c3'}], columns, graph=prepare_pricing(ins))
        self.assertEqual(a.equations, b.equations)
        self.assertEqual(a.variables, b.variables)
        with self.assertRaises(ValueError):
            compile_rmp(ins, (), [('a', 'c1')], graph=prepare_pricing(ins))


class TestCapacityLimits(unittest.TestCase):
    def conf(self, **updates):
        return CGConfig(**{**CGConfig(backend=BACKEND, seconds=30, iterations=100).__dict__, **updates})

    def test_shared_pairs_do_not_trigger_false_row_cap(self):
        ins, _ = TestExactRowCount().shared_instance()
        free = run_column_generation(ins, config=self.conf())
        self.assertEqual(free['status'], 'CONVERGED')
        needed = max(it['rows'] for it in free['iterations'])
        # Exatamente as linhas necessárias bastam (a estimativa antiga recusaria).
        tight = run_column_generation(ins, config=self.conf(max_rows=needed))
        self.assertEqual(tight['status'], 'CONVERGED')
        self.assertAlmostEqual(tight['global_lower_bound'], free['global_lower_bound'], places=6)

    def test_row_cap_reached_is_reported_with_values(self):
        ins, _ = TestExactRowCount().shared_instance()
        base = rmp_row_counts(ins, (), set())['total']
        r = run_column_generation(ins, config=self.conf(max_rows=base+3))
        self.assertEqual(r['status'], 'CAP_EXCEEDED')
        self.assertEqual(r['stop_detail']['limit'], 'max_rows')
        self.assertEqual(r['stop_detail']['configured'], base+3)
        self.assertLessEqual(r['stop_detail']['observed'], base+3)
        self.assertTrue(all(it['rows'] <= base+3 for it in r['iterations']))
        self.assertIsNone(r['global_lower_bound'])
        r = run_column_generation(ins, config=self.conf(max_rows=base-1))
        self.assertEqual((r['status'], r['stop_detail']['limit'], r['n_iterations']),
                         ('CAP_EXCEEDED', 'max_rows', 0))

    def test_column_cap_reached_is_reported_with_values(self):
        ins, _ = build_fixture(FIXTURES[0])
        r = run_column_generation(ins, config=self.conf(max_columns=1))
        self.assertEqual(r['status'], 'CAP_EXCEEDED')
        self.assertEqual(r['columns'], 1)
        self.assertEqual(r['stop_detail'], {**r['stop_detail'], 'limit': 'max_columns',
                                            'observed': 1, 'configured': 1})
        self.assertIsNone(r['global_lower_bound'])


class TestSelection(unittest.TestCase):
    def tie_candidates(self, n=4):
        S = [f's{i}' for i in range(n)]
        T = [f't{i}' for i in range(n)]
        return {s: [fake(s, t, -20.0) for t in T] for s in S}

    def take(self, kept, strategy, limit):
        selected, _, _ = select_columns(selection_order(kept, strategy), limit=limit,
                                        row_room=10**9, b3_pairs=set())
        return selected

    def test_tie_global_concentrates_matching_balances(self):
        # Reproduz a 1ª iteração do piloto: todos os pares com o mesmo custo.
        kept = self.tie_candidates()
        g = self.take(kept, 'global', 4)
        self.assertEqual({p.source for p in g}, {'s0'})
        ps = self.take(kept, 'per_source', 4)
        self.assertEqual({p.source for p in ps}, {'s0', 's1', 's2', 's3'})
        self.assertEqual({p.target for p in ps}, {'t0'})
        m = self.take(kept, 'matching', 4)
        self.assertEqual({p.source for p in m}, {'s0', 's1', 's2', 's3'})
        self.assertEqual({p.target for p in m}, {'t0', 't1', 't2', 't3'})

    def test_matching_continues_with_later_passes(self):
        kept = self.tie_candidates(3)
        m = self.take(kept, 'matching', 9)
        self.assertEqual(len(m), 9)
        self.assertEqual(len({(p.source, p.target) for p in m}), 9)
        first = m[:3]
        self.assertEqual(len({p.source for p in first}), 3)
        self.assertEqual(len({p.target for p in first}), 3)

    def test_deterministic_under_shuffled_input(self):
        rng = random.Random(1)
        base = {f's{i}': sorted((fake(f's{i}', f't{j}', float(rng.randint(-5, -1)))
                                 for j in range(5)), key=lambda p: (p.reduced_cost, p.target))
                for i in range(6)}
        for strategy in SELECTIONS:
            reference = [(p.source, p.target) for p in self.take(base, strategy, 7)]
            for _ in range(5):
                items = list(base.items())
                rng.shuffle(items)
                again = [(p.source, p.target) for p in self.take(dict(items), strategy, 7)]
                self.assertEqual(reference, again, strategy)

    def test_origins_without_candidates_are_skipped(self):
        kept = {'s0': [fake('s0', 't0', -3.0), fake('s0', 't1', -2.0)],
                's2': [fake('s2', 't1', -1.0)]}
        for strategy in SELECTIONS:
            chosen = self.take(kept, strategy, 10)
            self.assertEqual(len(chosen), 3, strategy)
            self.assertEqual({p.source for p in chosen}, {'s0', 's2'})

    def test_row_room_blocks_only_columns_with_new_pairs(self):
        kept = {'a': [fake('a', 't', -9.0, ('a', 'x', 't')),
                      fake('a', 'u', -8.0, ('a', 'y', 'u')),
                      fake('a', 'w', -7.0, ('a', 'w'))]}
        chosen, new, blocked = select_columns(selection_order(kept, 'global'), limit=5,
                                              row_room=0, b3_pairs={('a', 'x')})
        self.assertEqual([p.path for p in chosen], [('a', 'x', 't'), ('a', 'w')])
        self.assertEqual((new, blocked), (set(), 1))


class TestCertificatesAllStrategies(unittest.TestCase):
    def test_every_strategy_certifies_the_enumerated_lp(self):
        for strategy in SELECTIONS:
            config = CGConfig(backend=BACKEND, seconds=15, iterations=100, selection=strategy)
            for fixture in FIXTURES:
                ins, _ = build_fixture(fixture)
                exact = solve(compile_b(ins)[0], backend=BACKEND)
                r = run_column_generation(ins, config=config)
                if exact.status != 'OPTIMAL':
                    self.assertIsNone(r['global_lower_bound'])
                    continue
                self.assertEqual(r['status'], 'CONVERGED', (strategy, fixture.name))
                self.assertAlmostEqual(r['global_lower_bound'], exact.objective, places=5)
                self.assertTrue(verify_rational_certificate(ins, [], r['global_lb_certificate']))

    def test_random_graphs_with_k_every_strategy(self):
        rng = random.Random(1863)
        for case in range(8):
            ins = random_instance(rng, n=7, density=.35)
            K = [set(rng.sample(ins.V, 2))]
            exact = solve(compile_b(ins, K)[0], backend=BACKEND)
            for strategy in SELECTIONS:
                r = run_column_generation(ins, K, config=CGConfig(
                    backend=BACKEND, seconds=15, iterations=100, selection=strategy))
                if exact.status == 'OPTIMAL':
                    self.assertEqual(r['status'], 'CONVERGED', (case, strategy))
                    self.assertAlmostEqual(r['global_lower_bound'], exact.objective, places=5)
                    self.assertTrue(verify_rational_certificate(ins, K, r['global_lb_certificate']))
                else:
                    self.assertNotEqual(r['status'], 'CONVERGED')


class TestDeadlinesAndCheckpoints(unittest.TestCase):
    def run_with_sleep(self, on_event, seconds=1.0):
        ins, _ = build_fixture(FIXTURES[1])  # duas origens
        events = []

        def progress(event):
            events.append(event)
            if event['event'] == on_event and event.get('iteration') == 1:
                time.sleep(seconds + .2)
        r = run_column_generation(ins, config=CGConfig(backend=BACKEND, seconds=seconds),
                                  progress=progress)
        return r, events

    def test_deadline_inside_pricing_stops_cleanly(self):
        r, events = self.run_with_sleep('PRICING')
        self.assertEqual(r['status'], 'TIME_LIMIT')
        self.assertEqual(r['stop_detail']['stage'], 'PRICING')
        self.assertLess(r['stop_detail']['origins_processed'], 2)
        self.assertIn('PRICING_INTERRUPTED', [e['event'] for e in events])
        self.assertIsNone(r['global_lower_bound'])
        self.assertEqual(events[-1]['event'], 'CG_FINISHED')

    def test_deadline_after_rmp_reports_stage(self):
        r, _ = self.run_with_sleep('SOLVING_RMP')
        self.assertEqual(r['status'], 'TIME_LIMIT')
        self.assertIn(r['stop_detail']['stage'], ('SOLVING_RMP', 'BUILD_RMP'))
        self.assertIsNone(r['global_lower_bound'])

    def test_progress_events_fit_checkpoint_schema(self):
        ins, _ = build_fixture(FIXTURES[2])
        events = []
        r = run_column_generation(ins, config=CGConfig(backend=BACKEND, seconds=15,
                                                       progress_interval_s=1e-9),
                                  progress=events.append)
        self.assertEqual(r['status'], 'CONVERGED')
        names = [e['event'] for e in events]
        self.assertIn('PRICING_PROGRESS', names)
        root = Path(__file__).resolve().parents[2]
        plan = make_plan(root)
        record = progress_record(plan, plan['cases'][0], 'B_K')
        record['events'] = events
        self.assertTrue(verify_progress(record, plan, plan['cases'][0], 'B_K'))
        for e in events:
            self.assertNotIn('global_lower_bound', e)
        for it in r['iterations']:
            for key in ('build_s', 'solve_s', 'pricing_s', 'origins_processed',
                        'negative_candidate_count', 'artificial_sum'):
                self.assertIn(key, it)
        self.assertIn('NUNCA limite inferior global', r['bound_semantics'])


class TestPlanCompatibility(unittest.TestCase):
    root = Path(__file__).resolve().parents[2]

    def test_v1_plan_verifies_but_cannot_execute(self):
        legacy = make_plan(self.root, schema='AS08-B-PILOT-PLAN-v1')
        self.assertNotIn('selection', legacy['cg'])
        validate_plan(legacy, self.root, allow_legacy=True)
        with self.assertRaises(ValueError):
            validate_plan(legacy, self.root)
        plan = make_plan(self.root)
        self.assertEqual(plan['schema'], 'AS08-B-PILOT-PLAN-v2')
        self.assertIn(plan['cg']['selection'], SELECTIONS)
        validate_plan(plan, self.root)

    def test_previous_pilot_artifacts_still_verify(self):
        for name in ('as08-b-pilot-001', 'as08-b-pilot-002'):
            folder = self.root / 'results' / 'benchmark' / name
            if not (folder / 'manifest.json').exists():
                self.skipTest(f'{name} ausente')
            self.assertEqual(len(verify(folder, self.root)), 12)


if __name__ == '__main__':
    unittest.main()
