"""AS25.1 spec-backed tests: cheaper FC-R index must not change any row.

Oracles are independent of the AS25.1 module: the audited AS24 constructor,
the AS25 indexed separator and an exhaustive enumeration of Q written here.
"""
import itertools
import json
import random
import unittest
from collections import deque
from fractions import Fraction as F

from experiments.cuts.fcr_lp_policy import IndexedFCR
from experiments.cuts.fcr_lp_policy_as251 import FastIndexedFCR, fast_region_plan
from experiments.cuts.fcr_regions import choose_regions
from experiments.cuts.fcr_rows import construct_row
from experiments.cuts.verify_fcr_witness import build_system
from experiments.cuts import run_fcr_lp_as25 as as25_runner
from as02_model_a import Instance


def reach_instance(V, S, T, edges, r):
    """H on a unit graph: arcs (u,v), u != v, with BFS distance <= r."""
    adj = {v: set() for v in V}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    arcs = []
    for s in V:
        dist = {s: 0}
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u]+1
                    queue.append(w)
        arcs += [(s, v) for v, d in dist.items() if 0 < d <= r]
    return Instance(tuple(V), tuple(S), tuple(T), tuple(sorted(arcs)), r)


def random_instance(rng):
    n = rng.randint(6, 9)
    V = [f'v{i}' for i in range(n)]
    edges = {(V[i], V[rng.randrange(i)]) for i in range(1, n)}
    edges |= {tuple(rng.sample(V, 2)) for _ in range(rng.randint(0, n))}
    m = rng.randint(2, n//2)
    S = rng.sample(V, m)
    # Force S∩T in about half the cases and same-sign pairs (regional excess 2).
    T = rng.sample(V, m) if rng.random() < 0.5 else S[:1]+rng.sample([v for v in V if v not in S], m-1)
    return reach_instance(V, S, T, edges, rng.choice((1, 2)))


def random_point(rng, ins):
    y = {v: F(rng.randint(0, 6), 6) for v in ins.V if rng.random() < 0.7}
    f = {a: F(rng.randint(0, 8), 4) for a in ins.A_r if rng.random() < 0.5}
    # Adversarial circulation: flow around a directed triangle/2-cycle of H.
    u, v = rng.choice(ins.A_r)
    if (v, u) in set(ins.A_r):
        f[u, v] = f.get((u, v), 0)+F(3, 2)
        f[v, u] = f.get((v, u), 0)+F(3, 2)
    return y, f


def exhaustive_min_lhs(ins, L, direction, y, f):
    """Independent oracle: min over all Q of the FC-R left-hand side."""
    R = set(L)
    signed = len(R & set(ins.S))-len(R & set(ins.T))
    demand = signed if direction == 'origin' else -signed
    if direction == 'origin':
        arcs = [(u, v) for u, v in ins.A_r if u in R and v not in R]
        ext = lambda a: a[1]
        exempt = set(ins.T)
    else:
        arcs = [(u, v) for u, v in ins.A_r if v in R and u not in R]
        ext = lambda a: a[0]
        exempt = set(ins.S)
    possible = sorted({ext(a) for a in arcs}-exempt)
    best = None
    for k in range(len(possible)+1):
        for Q in itertools.combinations(possible, k):
            lhs = (sum((f.get(a, 0) for a in arcs if ext(a) not in Q), F(0)) +
                   demand*sum((y.get(v, 0) for v in Q), F(0)))
            best = lhs if best is None or lhs < best else best
    return demand, best


def witness_points(system):
    evidence = json.loads((as25_runner.ROOT/'results/benchmark/as23-fcr-witness-001.json').read_text())
    model, ins = system['compiled'], system['instance']
    for name, case in sorted(evidence['cases'].items()):
        vector = [F(v) for v in case['primal']]
        yield name, ({v: vector[model.columns['y', v]] for v in ins.V},
                     {(u, v): vector[model.columns['F', u, v]] for u, v in ins.A_r})


COUNTERS = ('examined', 'violated', 'emitted', 'capped', 'duplicates',
            'singletons_checked', 'larger_checked', 'no_violation')


class AS251SeparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = build_system()
        cls.ins = cls.system['instance']
        cls.points = list(witness_points(cls.system))
        rng = random.Random(251)
        cls.random_cases = []
        for _ in range(40):
            ins = random_instance(rng)
            cls.random_cases.append((ins, [random_point(rng, ins) for _ in range(3)]))

    def assertSameSeparation(self, slow, fast):
        self.assertEqual([c.signature for c in slow['cuts']], [c.signature for c in fast['cuts']])
        self.assertEqual([c.terms for c in slow['cuts']], [c.terms for c in fast['cuts']])
        self.assertEqual(slow['status'], fast['status'])
        for key in COUNTERS:
            self.assertEqual(slow['stats'][key], fast['stats'][key], key)

    # FCR251-01
    def test_region_plan_equals_as24_choose_regions(self):
        cases = [self.ins]+[ins for ins, _ in self.random_cases]
        for ins in cases:
            for cap, larger in ((0, True), (3, True), (12, True), (12, False)):
                with self.subTest(V=len(ins.V), cap=cap, larger=larger):
                    self.assertEqual(choose_regions(ins, max_larger=cap, include_larger=larger),
                                     fast_region_plan(ins, max_larger=cap, include_larger=larger))
        self.assertGreater(sum(len(fast_region_plan(ins).larger) > 0 for ins in cases), 20)

    # FCR251-02 (audit_rows also raises on any mismatch)
    def test_every_emitted_row_equals_canonical_constructor(self):
        for ins, points in [(self.ins, [p for _, p in self.points])]+self.random_cases:
            index = FastIndexedFCR(ins, max_larger=12, audit_rows=True)
            for y, f in points+[({}, {})]:
                for row in index.separate(y, f, max_cuts=10**6, tolerance=1e-9)['cuts']:
                    self.assertEqual(row, construct_row(ins, row.region, row.q, row.direction))

    def test_row_for_every_q_subset_of_witness_regions_equals_canonical(self):
        index = FastIndexedFCR(self.ins, max_larger=12)
        for region in index.regions:
            eligible = sorted({ext for _, ext, ok in region.frontier if ok})
            for Q in itertools.islice(itertools.chain.from_iterable(
                    itertools.combinations(eligible, k) for k in range(3)), 40):
                self.assertEqual(index._row(region, Q),
                                 construct_row(self.ins, region.vertices, Q, region.direction))

    # FCR251-03 and AC 13 of the task: same regions + same order => same output as AS25
    def test_lexicographic_always_equals_as25_indexed_separator(self):
        for ins, points in [(self.ins, [p for _, p in self.points])]+self.random_cases:
            for larger in (False, True):
                slow = IndexedFCR(ins, max_larger=12, include_larger=larger)
                fast = FastIndexedFCR(ins, max_larger=12, include_larger=larger)
                for y, f in points:
                    for cap in (0, 2, 64):
                        first = slow.separate(y, f, max_cuts=cap, tolerance=1e-8)
                        self.assertSameSeparation(first, fast.separate(y, f, max_cuts=cap, tolerance=1e-8))
                        seen = {c.signature for c in first['cuts']}
                        self.assertSameSeparation(
                            slow.separate(y, f, max_cuts=cap, tolerance=1e-8, exclude_signatures=seen),
                            fast.separate(y, f, max_cuts=cap, tolerance=1e-8, exclude_signatures=seen))

    # FCR251-04: exact Q, FC-R and FC-R-T, S∩T, r=2, demand 2, circulations
    def test_q_is_exhaustive_optimum_for_every_examined_region(self):
        directions, demands, overlap, radius = set(), set(), False, set()
        for ins, points in [(self.ins, [p for _, p in self.points])]+self.random_cases:
            index = FastIndexedFCR(ins, max_larger=12)
            overlap |= bool(set(ins.S) & set(ins.T))
            radius.add(ins.r)
            for y, f in points:
                for region in index.regions:
                    Q, deficit = index._evaluate(region, y, f)
                    demand, best = exhaustive_min_lhs(ins, region.vertices, region.direction, y, f)
                    self.assertEqual(demand, region.demand)
                    self.assertAlmostEqual(deficit, float(demand-best), places=9)
                    directions.add(region.direction)
                    demands.add(region.demand)
        self.assertEqual(directions, {'origin', 'destination'})
        self.assertIn(2, demands)
        self.assertTrue(overlap)
        self.assertEqual(radius, {1, 2})

    def test_overlap_vertex_is_not_a_singleton_and_is_never_in_q(self):
        ins = reach_instance(('s', 'x', 'w', 't'), ('s', 'x'), ('x', 't'),
                             [('s', 'x'), ('x', 'w'), ('w', 't'), ('s', 'w')], 1)
        index = FastIndexedFCR(ins, max_larger=12)
        self.assertNotIn(('x',), [r.vertices for r in index.regions])
        # x ∈ T is exempt from Q of origin s although it carries all the flow.
        result = index.separate({}, {('s', 'x'): 0.5}, max_cuts=99)
        s_rows = [c for c in result['cuts'] if c.region == ('s',)]
        self.assertEqual(len(s_rows), 1)
        self.assertNotIn('x', s_rows[0].q)
        self.assertIn((('F', 's', 'x'), 1), s_rows[0].terms)

    def test_radius_two_frontier_uses_reachability_arcs(self):
        ins = reach_instance(('s', 'a', 'b', 't'), ('s',), ('t',), [('s', 'a'), ('a', 'b'), ('b', 't')], 2)
        index = FastIndexedFCR(ins, max_larger=0)
        s_region = [r for r in index.regions if r.vertices == ('s',)][0]
        self.assertEqual(sorted(a for a, _, _ in s_region.frontier), [('s', 'a'), ('s', 'b')])

    # FCR251-05
    def test_reused_index_has_no_stale_state(self):
        for ins, points in self.random_cases[:15]:
            index = FastIndexedFCR(ins, max_larger=12)
            for y, f in points+list(reversed(points)):
                reused = index.separate(y, f, max_cuts=3)
                fresh = FastIndexedFCR(ins, max_larger=12).separate(y, f, max_cuts=3)
                self.assertSameSeparation(fresh, reused)
                self.assertEqual(fresh['events'], reused['events'])

    # FCR251-06
    def test_time_limit_during_singletons_is_partial(self):
        result = FastIndexedFCR(self.ins, max_larger=12).separate({}, {}, time_limit_s=0)
        self.assertEqual(result['status'], 'PARTIAL_SINGLETONS')
        self.assertFalse(result['stats']['singleton_complete'])
        self.assertEqual(result['stats']['reason'], 'TIME_LIMIT')

    # FCR251-07
    def test_cut_cap_is_reported_without_global_claim(self):
        result = FastIndexedFCR(self.ins, max_larger=12).separate({}, {}, max_cuts=1)
        self.assertEqual(result['status'], 'CUT_CAP_REACHED')
        self.assertEqual(len(result['cuts']), 1)
        self.assertGreater(result['stats']['capped'], 0)
        self.assertFalse(result['stats']['global_region_separation'])

    # FCR251-08
    def test_escalate_defers_larger_regions_while_a_singleton_is_violated(self):
        index = FastIndexedFCR(self.ins, max_larger=12, larger_mode='escalate')
        self.assertGreater(len(index.plan.larger), 0)
        result = index.separate({}, {}, max_cuts=10**6)
        self.assertTrue(result['stats']['larger_deferred'])
        self.assertEqual(result['stats']['larger_checked'], 0)
        self.assertEqual({c.region for c in result['cuts']}, set(index.plan.singletons))
        self.assertEqual(result['stats']['singletons_checked'], len(index.plan.singletons))

    # FCR251-09
    def test_escalate_examines_every_larger_region_without_new_singleton_violation(self):
        index = FastIndexedFCR(self.ins, max_larger=12, larger_mode='escalate')
        singles = {c.signature for c in index.separate({}, {}, max_cuts=10**6)['cuts']}
        result = index.separate({}, {}, max_cuts=10**6, exclude_signatures=singles)
        self.assertFalse(result['stats']['larger_deferred'])
        self.assertEqual(result['stats']['larger_checked'], len(index.plan.larger))
        self.assertEqual({c.region for c in result['cuts']}, set(index.plan.larger))
        self.assertEqual(result['stats']['duplicates'], len(singles))

    # FCR251-10
    def test_escalate_status_when_larger_deferred(self):
        index = FastIndexedFCR(self.ins, max_larger=12, larger_mode='escalate')
        self.assertEqual(index.separate({}, {}, max_cuts=10**6)['status'],
                         'COMPLETE_SINGLETONS_LARGER_DEFERRED')
        self.assertEqual(index.separate({}, {}, max_cuts=1)['status'], 'CUT_CAP_REACHED')

    # FCR251-11
    def test_excluded_signature_is_duplicate_and_not_emitted(self):
        index = FastIndexedFCR(self.ins, max_larger=0)
        first = index.separate({}, {}, max_cuts=10**6)['cuts'][0]
        again = index.separate({}, {}, max_cuts=10**6, exclude_signatures={first.signature})
        self.assertNotIn(first.signature, [c.signature for c in again['cuts']])
        event = [e for e in again['events'] if tuple(e['region']) == first.region][0]
        self.assertEqual(event['decision'], 'DUPLICATE')
        self.assertEqual(again['stats']['duplicates'], 1)

    # FCR251-12
    def test_deficit_equal_to_tolerance_is_not_a_violation(self):
        ins = reach_instance(('s', 'a', 't'), ('s',), ('t',), [('s', 'a'), ('a', 't')], 1)
        index = FastIndexedFCR(ins, max_larger=0)
        def s_event(flow):
            out = index.separate({'a': 1.0}, {('s', 'a'): flow}, max_cuts=9, tolerance=0.25)
            return [e for e in out['events'] if e['region'] == ['s']][0]
        at = s_event(0.75)
        self.assertEqual(at['deficit'], 0.25)
        self.assertEqual(at['decision'], 'NO_VIOLATION_IN_FIXED_REGION')
        above = s_event(0.74)
        self.assertGreater(above['deficit'], 0.25)
        self.assertEqual(above['decision'], 'ADDED')

    def test_deficit_selection_ranks_by_violation_without_changing_rows(self):
        y, f = self.points[0][1]
        lex = FastIndexedFCR(self.ins, max_larger=12).separate(y, f, max_cuts=10**6, tolerance=1e-8)
        ranked = FastIndexedFCR(self.ins, max_larger=12, selection='deficit').separate(
            y, f, max_cuts=10**6, tolerance=1e-8)
        self.assertEqual(sorted(c.signature for c in lex['cuts']), sorted(c.signature for c in ranked['cuts']))
        added = sorted((e for e in ranked['events'] if e['decision'] == 'ADDED'), key=lambda e: e['selection_rank'])
        self.assertEqual([e['deficit'] for e in added], sorted((e['deficit'] for e in added), reverse=True))

    def test_invalid_options_and_points_are_rejected(self):
        with self.assertRaises(ValueError):
            FastIndexedFCR(self.ins, selection='random')
        with self.assertRaises(ValueError):
            FastIndexedFCR(self.ins, larger_mode='never')
        index = FastIndexedFCR(self.ins)
        for y, f in (({'ghost': 0.5}, {}), ({}, {('a1', 'a2'): 1.0}), ({}, {self.ins.A_r[0]: float('nan')})):
            with self.subTest(y=y, f=f), self.assertRaises(ValueError):
                index.separate(y, f)


class AS251DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = build_system()

    # FCR251-13
    def test_index_report_times_both_indexes_and_checks_plan_equality(self):
        from experiments.cuts.diagnose_fcr_as251 import index_report
        report = index_report(self.system['instance'])
        self.assertEqual([r['include_larger'] for r in report['index']], [False, True])
        for row in report['index']:
            self.assertTrue(row['plan_equal'])
            self.assertTrue(row['regions_equal'])
            self.assertGreaterEqual(row['as25_index_s'], 0)
            self.assertGreaterEqual(row['as251_index_s'], 0)
        self.assertEqual(report['n_arcs_H'], len(self.system['instance'].A_r))

    # FCR251-14
    def test_trace_records_objective_and_costs_per_round(self):
        try:
            import gurobipy  # noqa: F401
        except ImportError:
            self.skipTest('Gurobi unavailable: trace mode needs the AS25 LP solver')
        from experiments.cuts.diagnose_fcr_as251 import trace
        plan = as25_runner.load_plan()[0]
        index = FastIndexedFCR(self.system['instance'], max_larger=12)
        result = trace(self.system['instance'], self.system['compiled'], plan['solver_parameters'],
                       index, per_round=1000, total=1000, rounds=50)
        self.assertEqual(result['status'], 'OPTIMAL')
        self.assertTrue(result['converged_no_violation'])
        last = result['rounds'][-1]
        self.assertEqual(last['emitted'], 0)
        objectives = [r['objective'] for r in result['rounds'][:-1]]
        self.assertTrue(all(b >= a-1e-7 for a, b in zip([result['base_objective']]+objectives, objectives)))
        self.assertAlmostEqual(result['final_objective'], objectives[-1])
        self.assertGreater(result['final_objective'], result['base_objective']+1e-6)
        for key in ('separation_s', 'insertion_s', 'reoptimization_s', 'nnz', 'terms_digest'):
            self.assertIn(key, result['rounds'][0])

    # FCR251-15
    def test_outputs_are_labelled_post_hoc_and_outside_gate(self):
        from experiments.cuts.diagnose_fcr_as251 import _header
        header = _header('index')
        self.assertEqual(header['evidence_class'], 'DIAGNOSTIC_POST_HOC')
        self.assertFalse(header['enters_gate'])


def _has_gurobi():
    try:
        import gurobipy  # noqa: F401
        return True
    except ImportError:
        return False


class AS251RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from experiments.cuts import run_fcr_lp_as251 as runner
        cls.runner = runner
        cls.plan, cls.sha, cls.base = runner.load_plan()

    # FCR251-16
    def test_plan_reuses_as25_cases_solver_budget_and_policy(self):
        as25 = as25_runner.load_plan()[0]
        for key in ('cases', 'solver_parameters', 'budget', 'fcr'):
            self.assertEqual(self.plan[key], as25[key])
        self.assertEqual(self.plan['budget'], {'wall_seconds_per_arm': 90})
        self.assertEqual(self.plan['as25_reference_gate'], as25['gate'])

    def test_load_plan_rejects_mutations(self):
        import copy
        import tempfile
        from pathlib import Path
        mutations = {
            'budget': lambda p: p['budget'].update(wall_seconds_per_arm=900),
            'case': lambda p: p['cases'][0].update(raw_graph_id='fabricated'),
            'fcr': lambda p: p['fcr'].update(max_rounds=60),
            'solver': lambda p: p['solver_parameters'].update(Method=2),
            'gate': lambda p: p['as25_reference_gate'].update(minimum_relative_gain=0),
            'arms': lambda p: p['arms'].append('U_K_MIP'),
            'policy': lambda p: p['arm_policies']['U_K_FCR_AS251'].update(selection='deficit'),
            'classification': lambda p: p['classification'].update(efficiency_minimum_median_overhead_reduction=0.1),
            'mip': lambda p: p.update(mip_automatically_authorized=True),
            'as25_hash': lambda p: p.update(as25_plan_sha256='0'*64),
            'as16_hash': lambda p: p.update(as16_plan_sha256='0'*64),
            'source_hash': lambda p: p['cases'][1].update(source_sha256='0'*64),
            'constraints': lambda p: p['constraints'].remove('no MIP'),
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'plan.json'
            for name, mutate in mutations.items():
                plan = copy.deepcopy(self.plan)
                mutate(plan)
                path.write_text(json.dumps(plan))
                with self.subTest(name), self.assertRaises(ValueError):
                    self.runner.load_plan(path)

    # FCR251-17, FCR251-20
    def test_dry_run_has_24_rows_four_arms_and_is_append_only(self):
        import tempfile
        from pathlib import Path
        names = {c['name'] for c in self.plan['cases']}
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'as251'
            result = self.runner.execute(self.plan, self.sha, self.base, self.runner.ROOT, out, names, dry_run=True)
            rows = json.loads((out/'rows.json').read_text())
            self.assertEqual(len(rows), 24)
            self.assertEqual({(r['name'], r['arm_id']) for r in rows},
                             {(n, a) for n in names for a in self.runner.ARMS})
            self.assertEqual(result['classification'], 'NOT_CLASSIFIED_DRY_RUN')
            self.assertEqual(json.loads((out/'manifest.json').read_text())['arms'], list(self.runner.ARMS))
            with self.assertRaises(FileExistsError):
                self.runner.execute(self.plan, self.sha, self.base, self.runner.ROOT, out, names, dry_run=True)

    # FCR251-19
    def test_timeout_is_persisted_as_censored_without_objective(self):
        from unittest.mock import patch

        class Pipe:
            sent = []
            def send(self, x): self.sent.append(x)
            def close(self): pass
        with patch.object(self.runner, '_work_arm', side_effect=TimeoutError('deadline')):
            conn = Pipe()
            self.runner._worker(conn, self.plan['cases'][0], {}, self.runner.ROOT, 'U_K_FCR_AS251',
                                {}, self.plan['fcr'], 0)
        self.assertEqual(conn.sent[0]['status'], 'TIME_LIMIT')
        self.assertNotIn('lp_objective', conn.sent[0])

    def _witness_arm(self, arm):
        import time
        from types import SimpleNamespace
        from unittest.mock import patch
        from experiments.cuts.verify_fcr_witness import witness_instance
        ins, adj, _, _ = witness_instance()
        loaded = SimpleNamespace(V=ins.V, S=ins.S, T=ins.T, A_r=ins.A_r, r=ins.r, adj=adj,
                                 instance_sha256='synthetic-as23')
        with patch.object(self.runner, 'load_instance', return_value=loaded):
            return self.runner._work_arm({'source_sha256': 'synthetic-as23'}, {}, self.runner.ROOT, arm,
                                         self.plan['solver_parameters'], self.plan['fcr'], time.monotonic()+90)

    # FCR251-18 and task AC 13/14 on a real LP: infra arm repeats AS25 rows and objective
    @unittest.skipUnless(_has_gurobi(), 'Gurobi unavailable: real LP arm')
    def test_witness_lp_round_records_and_infra_equals_as25(self):
        as25 = self._witness_arm('U_K_FCR_AS25')
        infra = self._witness_arm('U_K_FCR_INFRA')
        candidate = self._witness_arm('U_K_FCR_AS251')
        for record in (as25, infra, candidate):
            self.assertEqual(record['status'], 'OPTIMAL')
            self.assertGreater(record['lp_objective'], record['base_lp_objective']+1e-6)
            first = record['fcr_rounds'][0]
            for key in ('objective_after', 'signature_digest', 'terms_digest', 'nnz', 'emitted'):
                self.assertIn(key, first)
            self.assertEqual(first['objective_after'] is not None, first['emitted'] > 0)
            for key in ('fcr_region_index_s', 'fcr_separation_s', 'fcr_insertion_s', 'lp_reoptimization_s'):
                self.assertIn(key, record['timings'])
        self.assertEqual([r['signature_digest'] for r in as25['fcr_rounds']],
                         [r['signature_digest'] for r in infra['fcr_rounds']])
        self.assertEqual([r['terms_digest'] for r in as25['fcr_rounds']],
                         [r['terms_digest'] for r in infra['fcr_rounds']])
        self.assertAlmostEqual(as25['lp_objective'], infra['lp_objective'], places=9)
        self.assertEqual(sum(r['emitted_larger'] for r in candidate['fcr_rounds'][:1]), 0)
        # FCR251-23: deferred larger regions count as covered, never as complete larger scans
        self.assertTrue(candidate['fcr_rounds'][0]['stats']['larger_deferred'])
        self.assertEqual(candidate['fcr_rounds'][0]['stats']['larger_checked'], 0)
        self.assertTrue(candidate['larger_complete_or_deferred_all_scans'])
        self.assertTrue(as25['larger_complete_or_deferred_all_scans'])

    # FCR251-17, FCR251-19: own process and hard wall deadline
    def test_run_arm_enforces_total_wall_budget_in_child_process(self):
        import copy
        plan = copy.deepcopy(self.plan)
        plan['budget']['wall_seconds_per_arm'] = 1
        case = [c for c in plan['cases'] if c['name'] == 'vienna-I056-regiao-f4'][0]
        rows = self.runner.validate_sources(self.base, self.runner.ROOT)
        result = self.runner.run_arm(case, rows[case['name']], self.runner.ROOT, 'U_K_FCR_AS251', plan)
        self.assertEqual(result['status'], 'TIME_LIMIT')
        self.assertIsNone(result.get('lp_objective'))
        self.assertLess(result['elapsed_wall_s'], 5)
        self.assertEqual(result['arm_id'], 'U_K_FCR_AS251')


class AS251AnalyzerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from experiments.cuts import run_fcr_lp_as251 as runner
        from experiments.cuts.analyze_fcr_lp_as251 import analyze
        cls.runner, cls.analyze = runner, staticmethod(analyze)
        cls.plan = runner.load_plan()[0]

    def make_rows(self, *, objective=None, wall=None, status=None, rounds=None, complete=True):
        objective = {'U_K': 10., 'U_K_FCR_AS25': 10.05, 'U_K_FCR_INFRA': 10.05, 'U_K_FCR_AS251': 10.2,
                     **(objective or {})}
        wall = {'U_K': 2., 'U_K_FCR_AS25': 12., 'U_K_FCR_INFRA': 3., 'U_K_FCR_AS251': 3., **(wall or {})}
        status = status or {}
        rounds = rounds or {}
        default_rounds = [{'signature_digest': 's1', 'terms_digest': 't1', 'objective_after': 10.05}]
        rows = []
        for case in self.plan['cases']:
            for arm in self.runner.ARMS:
                state = status.get(arm, 'OPTIMAL')
                rows.append({'name': case['name'], 'arm_id': arm, 'raw_graph_id': case['raw_graph_id'],
                             'instance_sha256': case['source_sha256'], 'status': state,
                             'lp_objective': objective[arm] if state == 'OPTIMAL' else None,
                             'elapsed_wall_s': wall[arm], 'fcr_added': 0 if arm == 'U_K' else 5,
                             'fcr_rounds': [] if arm == 'U_K' else rounds.get(arm, default_rounds),
                             'singleton_complete_all_scans': complete,
                             'larger_complete_or_deferred_all_scans': complete})
        manifest = {'mode': 'LP', 'arms': list(self.runner.ARMS),
                    'cases': [c['name'] for c in self.plan['cases']], 'plan_sha256': 'x'}
        return manifest, rows

    # FCR251-21, FCR251-23 (class A)
    def test_class_A_needs_gain_cost_and_coverage(self):
        result = self.analyze(self.plan, *self.make_rows())
        self.assertEqual(result['classification'], 'A')
        self.assertEqual(result['as25_reference_gate'], 'GO_CANDIDATE_REVIEW')
        self.assertEqual(len(result['qualified_raw_graph_ids']), 6)

    # FCR251-23 (class C): gain >= 1% but cost > 2x
    def test_class_C_when_gain_exists_but_cost_is_excessive(self):
        result = self.analyze(self.plan, *self.make_rows(wall={'U_K_FCR_AS251': 4.1}))
        self.assertEqual(result['classification'], 'C')
        self.assertEqual(result['as25_reference_gate'], 'STOP')

    # FCR251-23 (class B) and FCR251-22
    def test_class_B_when_infra_is_equivalent_and_cheaper_but_gain_small(self):
        result = self.analyze(self.plan, *self.make_rows(objective={'U_K_FCR_AS251': 10.05}))
        self.assertEqual(result['classification'], 'B')
        self.assertTrue(result['efficiency']['holds'])
        self.assertAlmostEqual(result['efficiency']['median_overhead_reduction'], 0.9)
        self.assertTrue(all(c['infra_equivalent'] for c in result['cases']))

    # FCR251-22, FCR251-23 (class D): different rows break equivalence
    def test_class_D_when_infra_rows_differ_from_as25(self):
        other = [{'signature_digest': 's1', 'terms_digest': 'DIFFERENT', 'objective_after': 10.05}]
        result = self.analyze(self.plan, *self.make_rows(objective={'U_K_FCR_AS251': 10.05},
                                                         rounds={'U_K_FCR_INFRA': other}))
        self.assertEqual(result['classification'], 'D')
        self.assertFalse(result['efficiency']['holds'])
        self.assertFalse(result['cases'][0]['infra_equivalent'])

    def test_class_D_when_infra_is_not_cheaper(self):
        result = self.analyze(self.plan, *self.make_rows(objective={'U_K_FCR_AS251': 10.05},
                                                         wall={'U_K_FCR_INFRA': 8.}))
        self.assertAlmostEqual(result['efficiency']['median_overhead_reduction'], 0.4)
        self.assertEqual(result['classification'], 'D')

    # FCR251-24
    def test_flow_only_rows_count_as_zero_gain(self):
        result = self.analyze(self.plan, *self.make_rows(objective={'U_K_FCR_AS251': 10.}))
        marginal = result['cases'][0]['as251_vs_U_K']
        self.assertTrue(marginal['flow_only_zero_bound_gain'])
        self.assertEqual(marginal['absolute_gain'], 0.)
        self.assertEqual(result['gain_at_least_1pct_raw_graph_ids'], [])

    def test_censored_candidate_is_not_paired_and_blocks_reference_gate(self):
        result = self.analyze(self.plan, *self.make_rows(status={'U_K_FCR_AS251': 'TIME_LIMIT'},
                                                         objective={'U_K_FCR_AS251': 10.05}))
        self.assertFalse(result['cases'][0]['as251_vs_U_K']['paired_optimal'])
        self.assertEqual(result['as25_reference_gate'], 'INVESTIGATE')
        self.assertEqual(result['censored_arm_count'], 6)

    def test_rescued_case_is_reported_outside_the_median(self):
        manifest, rows = self.make_rows(objective={'U_K_FCR_AS251': 10.05})
        rows[1].update(status='TIME_LIMIT', lp_objective=None)  # first case, U_K_FCR_AS25
        result = self.analyze(self.plan, manifest, rows)
        self.assertEqual(result['efficiency']['rescued_cases'], [self.plan['cases'][0]['name']])
        self.assertEqual(result['efficiency']['infra_compared_cases'], 5)

    def test_partial_coverage_blocks_class_A(self):
        result = self.analyze(self.plan, *self.make_rows(complete=False))
        self.assertNotEqual(result['classification'], 'A')
        self.assertEqual(result['as25_reference_gate'], 'INVESTIGATE')

    # FCR251-25
    def test_no_class_authorizes_mip(self):
        for kwargs in ({}, {'objective': {'U_K_FCR_AS251': 10.}}):
            self.assertFalse(self.analyze(self.plan, *self.make_rows(**kwargs))['mip_automatically_authorized'])

    # FCR251-22: signature digest, every round and objective tolerance all matter
    def test_infra_equivalence_requires_signatures_all_rounds_and_objective(self):
        two = [{'signature_digest': 's1', 'terms_digest': 't1', 'objective_after': 10.},
               {'signature_digest': 's2', 'terms_digest': 't2', 'objective_after': 10.05}]
        variants = {
            'signature': ({'U_K_FCR_INFRA': [{'signature_digest': 'OTHER', 'terms_digest': 't1',
                                              'objective_after': 10.05}]}, {}),
            'second_round': ({'U_K_FCR_AS25': two, 'U_K_FCR_INFRA': [two[0], {**two[1], 'terms_digest': 'X'}]}, {}),
            'objective': ({}, {'U_K_FCR_INFRA': 10.05+1e-4}),
        }
        for name, (rounds, objective) in variants.items():
            with self.subTest(name):
                result = self.analyze(self.plan, *self.make_rows(
                    rounds=rounds, objective={'U_K_FCR_AS251': 10.05, **objective}))
                self.assertFalse(result['cases'][0]['infra_equivalent'])
                self.assertEqual(result['classification'], 'D')
        same = self.analyze(self.plan, *self.make_rows(rounds={'U_K_FCR_AS25': two, 'U_K_FCR_INFRA': two},
                                                       objective={'U_K_FCR_AS251': 10.05, 'U_K_FCR_INFRA': 10.05+1e-6}))
        self.assertTrue(same['cases'][0]['infra_equivalent'])

    # FCR251-21, FCR251-23: exact thresholds (gain 1%, cost 2.0x) qualify
    def test_exact_gain_and_cost_thresholds_qualify_for_A(self):
        result = self.analyze(self.plan, *self.make_rows(
            objective={'U_K': 100., 'U_K_FCR_AS25': 100., 'U_K_FCR_INFRA': 100., 'U_K_FCR_AS251': 101.},
            wall={'U_K_FCR_AS251': 4.}))
        self.assertEqual(result['cases'][0]['as251_vs_U_K']['cost_multiple'], 2.0)
        self.assertEqual(result['classification'], 'A')
        below = self.analyze(self.plan, *self.make_rows(
            objective={'U_K': 100., 'U_K_FCR_AS25': 100., 'U_K_FCR_INFRA': 100., 'U_K_FCR_AS251': 100.99}))
        self.assertNotIn(below['classification'], ('A', 'C'))

    # FCR251-23: a cut cap on the candidate arm blocks A even with gain and cost
    def test_cut_cap_blocks_A_but_keeps_C(self):
        manifest, rows = self.make_rows()
        for row in rows:
            if row['arm_id'] == 'U_K_FCR_AS251':
                row['fcr_cut_cap_encountered'] = True
        result = self.analyze(self.plan, manifest, rows)
        self.assertEqual(result['classification'], 'C')
        self.assertEqual(result['qualified_raw_graph_ids'], [])

    def test_corrupted_rows_are_rejected(self):
        manifest, rows = self.make_rows()
        for bad in (rows[:-1], rows+[rows[0]], [{**rows[0], 'instance_sha256': 'fake'}]+rows[1:]):
            with self.assertRaises(ValueError):
                self.analyze(self.plan, manifest, bad)


if __name__ == '__main__':
    unittest.main()
