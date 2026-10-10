"""N2-T4: testes offline de identidade/critério e smoke com Gurobi quando disponível."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

# ruff: noqa: E402
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_n2_t4 as r


class ManifestTests(unittest.TestCase):
    def test_exact_23_eligible_one_missing_reference(self):
        controls = r.build_manifest(verify_hashes=False)
        self.assertEqual((len(controls), sum(not x.excluded for x in controls)), (24, 23))
        self.assertEqual([c.name for c in controls if c.excluded], ['SC-GF2-k3'])
        self.assertEqual((len([x for x in controls if x.source == 'T5']),
                          len([x for x in controls if x.source == 'T6'])), (18, 6))
        self.assertEqual(len({c.id for c in controls}), 24)
        self.assertEqual(controls[-1].reference, F(0))
        self.assertIsNone(next(x for x in controls if x.excluded).reference)

    def test_complete_frozen_source_hashes(self):
        self.assertEqual(sum(not x.excluded for x in r.build_manifest()), 23)

    def test_archived_values_stay_exact_decimal(self):
        self.assertEqual(r._reference_fraction('1.5'), F(3, 2))
        self.assertEqual(r._reference_fraction('0'), F(0))
        self.assertEqual(r._reference_fraction('2.500000'), F(5, 2))
        for bad in ('', 'NaN', 'Inf', 'fail', 'NOT MEASURED'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                r._reference_fraction(bad)

    def test_frozen_t5_values_match_csv(self):
        manifest = r.build_manifest(verify_hashes=False)
        freeze = r._read_json(r.FREEZE_T5)
        for case, frozen in zip(manifest[:18], freeze['instances']):
            self.assertEqual(case.name, frozen['nome'])
            self.assertEqual(case.k_hash, frozen['k_hash'])
            self.assertEqual(case.instance_hash, frozen['data_sha256'])

    def test_t6_both_variants_same_family_and_distinct_instances(self):
        controls = r.build_manifest(verify_hashes=False)[18:]
        self.assertEqual(len(controls), 6)
        for before, after in zip(controls[::2], controls[1::2]):
            self.assertTrue(before.name.endswith('-obstruction'))
            self.assertTrue(after.name.endswith('-control'))
            self.assertNotEqual(before.instance_hash, after.instance_hash)

    def test_mutated_historical_lp_is_rejected(self):
        rows = r._read_csv(r.N1_T5)
        mutated = [dict(x) for x in rows]
        mutated[0]['lp_fcc_k'] = ''
        original = r._read_csv
        with patch.object(r, '_read_csv', side_effect=lambda path: (
                mutated if path == r.N1_T5 else original(path))):
            with self.assertRaises(ValueError):
                r.build_manifest(verify_hashes=False)

    def test_t6_unapproved_reference_is_rejected(self):
        original = r._read_csv
        rows = original(r.N1_T6)
        rows[0]['pair_status'] = 'EXCLUDED'
        with patch.object(r, '_read_csv', side_effect=lambda path: (
                rows if path == r.N1_T6 else original(path))):
            with self.assertRaises(ValueError):
                r.build_manifest(verify_hashes=False)

    def test_archive_hashes_are_verified_when_full_source_available(self):
        freeze6 = r._read_json(r.FREEZE_T6)
        digest = hashlib.sha256(r.N1_T5.read_bytes()).hexdigest()
        self.assertEqual(freeze6['gate_t5']['source_hashes'][
            'results/alternative-formulations/n1-t5-diagnostico.csv'], digest)
        self.assertEqual(r._read_json(r.N1_PAIRS)['freeze_hash'],
                         hashlib.sha256(r.FREEZE_T6.read_bytes()).hexdigest())
        # O build completo checa TODOS os hashes do projeto local.


class ClassifierTests(unittest.TestCase):
    def check(self, ref=F(3, 2), status='CERTIFIED', lb=F(1),
              g2='NOT_CONVERGED_CERTIFIED', upper=None,
              stop='', z=None, reflects=False):
        return r.classify(ref, status=status, lb=lb, g2_status=g2, upper=upper,
                          stop_reason=stop, rmp_objective=z,
                          reflects_all_columns=reflects)

    def test_certified_incomplete_pricing_below_reference_passes(self):
        status, text = self.check(lb=F(1, 2), stop='TIME_LIMIT')
        self.assertEqual(status, r.PASS_LB)
        self.assertIn('LB rigoroso', text)

    def test_no_certified_bound_is_failure(self):
        for status, lb in [('UNCERTIFIED', None), ('UNCERTIFIED', F(1)),
                           ('CERTIFIED', None)]:
            with self.subTest(status=status, lb=lb):
                self.assertEqual(self.check(status=status, lb=lb)[0], r.FAIL)

    def test_lb_above_lp_tolerance_fails(self):
        self.assertEqual(self.check(lb=F(3, 2) + F(2, 1_000_000))[0], r.FAIL)
        self.assertEqual(self.check(lb=F(3, 2) + r.EPS)[0], r.PASS_LB)

    def test_g2_requires_verified_upper_and_reference_agreement(self):
        self.assertEqual(self.check(g2=r.G2_PASSED, lb=F(3, 2), upper=F(3, 2))[0],
                         r.PASS_G2)
        self.assertEqual(self.check(g2=r.G2_PASSED, lb=F(3, 2), upper=None)[0],
                         r.FAIL)
        self.assertEqual(self.check(g2=r.G2_PASSED, lb=F(1), upper=F(1))[0], r.FAIL)
        self.assertEqual(self.check(g2=r.G2_PASSED, lb=F(3, 2), upper=F(2))[0], r.FAIL)

    def test_numeric_stationarity_does_not_mean_g2(self):
        self.assertEqual(self.check(stop='NUMERICAL_STATIONARY', z=1.5,
                                    reflects=True)[0], r.PASS_NUMERIC)
        self.assertEqual(self.check(stop='NUMERICAL_STATIONARY', z=1.4,
                                    reflects=True)[0], r.FAIL)
        self.assertEqual(self.check(stop='NUMERICAL_STATIONARY', z=1.5,
                                    reflects=False)[0], r.FAIL)
        self.assertEqual(self.check(stop='NUMERICAL_STATIONARY', z=float('nan'),
                                    reflects=True)[0], r.FAIL)

    def test_no_direct_matching_zero_reference(self):
        self.assertEqual(self.check(ref=F(0), lb=F(0))[0], r.PASS_LB)
        self.assertEqual(self.check(ref=F(0), lb=F(1))[0], r.FAIL)


class OutputAndFlowTests(unittest.TestCase):
    def test_csv_has_immutable_reference_and_justification_fields(self):
        cases = r.build_manifest(verify_hashes=False)
        output = r._csv_bytes([dict(r._initial_row(cases[0]), comparison=r.PASS_LB,
                                    justification='racional verificado')])
        record = list(csv.DictReader(output.decode('utf-8').splitlines()))[0]
        self.assertEqual(record['reference_lp_fcc_k'], '0.0')
        self.assertEqual(record['comparison'], r.PASS_LB)
        self.assertEqual(record['justification'], 'racional verificado')
        self.assertIn('rmp_objective_diagnostic', record)

    def test_output_create_only_and_manifest_digest(self):
        cases = r.build_manifest(verify_hashes=False)
        rows = [dict(r._initial_row(cases[0]), comparison=r.PASS_LB)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            csv_path, meta_path = r._output(path, rows, cases, config={'case': 1},
                                            result='FAIL_BLOCK_N2_T5')
            original = csv_path.read_bytes()
            meta = json.loads(meta_path.read_text())
            self.assertEqual(meta['csv_sha256'], hashlib.sha256(original).hexdigest())
            self.assertEqual(meta['expected_eligible'], 23)
            self.assertEqual(meta['status'], 'FAIL_BLOCK_N2_T5')
            with self.assertRaises(FileExistsError):
                r._output(path, rows, cases, config={}, result='PASS')
            self.assertEqual(csv_path.read_bytes(), original)

    def test_run_stops_at_first_failed_case(self):
        cases = r.build_manifest(verify_hashes=False)
        old_t5 = sys.modules.get('run_n1_t5')
        old_t6 = sys.modules.get('run_n1_t6')
        stub_t5 = types.ModuleType('run_n1_t5')
        stub_t5.corpus = lambda: []
        stub_t6 = types.ModuleType('run_n1_t6')
        stub_t6.read_pairs = lambda: {'pairs': []}
        sys.modules['run_n1_t5'] = stub_t5
        sys.modules['run_n1_t6'] = stub_t6
        visited = []

        def fail_first(case, *_args, **_kwargs):
            visited.append(case.id)
            return {'comparison': r.FAIL, 'justification': 'controle falhou'}

        try:
            with tempfile.TemporaryDirectory() as tmp:
                with patch.object(r, '_rebuild_case', return_value=None), patch.object(
                        r, '_evaluate_case', side_effect=fail_first):
                    self.assertFalse(r._run(cases, run_dir=Path(tmp), time_limit=10,
                                            work_limit=None, max_iterations=2, enum_cap=9))
                self.assertEqual(len(visited), 1)
                data = json.loads((Path(tmp) / 'n2-t4-regressao-manifest.json').read_text())
                self.assertEqual(data['status'], 'FAIL_BLOCK_N2_T5')
                self.assertEqual(data['eligible_checked'], 1)
        finally:
            if old_t5 is None:
                sys.modules.pop('run_n1_t5', None)
            else:
                sys.modules['run_n1_t5'] = old_t5
            if old_t6 is None:
                sys.modules.pop('run_n1_t6', None)
            else:
                sys.modules['run_n1_t6'] = old_t6

    def test_run_full_pass_is_only_after_23_evaluations(self):
        cases = r.build_manifest(verify_hashes=False)
        stubs = {'run_n1_t5': types.ModuleType('run_n1_t5'),
                 'run_n1_t6': types.ModuleType('run_n1_t6')}
        stubs['run_n1_t5'].corpus = lambda: []
        stubs['run_n1_t6'].read_pairs = lambda: {'pairs': []}
        seen = []

        def evaluate(case, *_args, **_kwargs):
            seen.append(case.id)
            return {'comparison': r.PASS_LB, 'justification': 'certificado'}

        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(sys.modules, stubs), patch.object(
                    r, '_rebuild_case', return_value=None), patch.object(
                    r, '_evaluate_case', side_effect=evaluate):
                self.assertTrue(r._run(cases, run_dir=Path(tmp), time_limit=10,
                                       work_limit=None, max_iterations=2, enum_cap=9))
            self.assertEqual(len(seen), 23)
            meta = json.loads((Path(tmp) / 'n2-t4-regressao-manifest.json').read_text())
            self.assertEqual((meta['status'], meta['passed'], meta['eligible_checked']),
                             ('PASS', 23, 23))
            with (Path(tmp) / 'n2-t4-regressao.csv').open(encoding='utf-8', newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 24)
            self.assertEqual(sum(x['comparison'] == r.EXCLUDED for x in rows), 1)


class DisconnectedDomainExceptionTests(unittest.TestCase):
    """Direct0 é exceção documental, NÃO uma execução da CG em G desconexo."""

    @staticmethod
    def sample():
        case = r.build_manifest(verify_hashes=False)[0]
        S, T = ('s1', 's2'), ('t1', 't2')
        V = S + T
        adj = {'s1': (('t1', 1),), 't1': (('s1', 1),),
               's2': (('t2', 1),), 't2': (('s2', 1),)}
        A_r = (('s1', 't1'), ('t1', 's1'), ('s2', 't2'), ('t2', 's2'))
        k_hash = hashlib.sha256(b'[]').hexdigest()
        return case, (S, T, V, adj, A_r, 1, (), k_hash)

    def test_direct0_exact_zero_is_explicit_not_cg_or_g2(self):
        case, data = self.sample()
        row = r._evaluate_case(case, data, time_limit=40.0, work_limit=None,
                               max_iterations=20, enum_cap=2048)
        self.assertEqual(row['comparison'], r.PASS_DIRECT_ZERO)
        self.assertEqual(row['proof_method'], 'EXACT_DIRECT_MATCHING_ZERO_NO_CG')
        self.assertEqual((row['lp_certification_status'], row['lp_lb_exact']),
                         ('CERTIFIED', '0/1'))
        self.assertEqual((row['iterations'], row['pricing_calls']), (0, 0))
        self.assertNotEqual(row['g2_status'], r.G2_PASSED)
        self.assertEqual(json.loads(row['direct_matching']),
                         [['s1', 't1'], ['s2', 't2']])
        self.assertIn('NÃO houve CG/E5', row['justification'])

    def test_mutations_are_rejected_without_fallback(self):
        case, data = self.sample()
        S, T, V, adj, arcs, autonomy, cuts, kh = data
        altered = [
            (S, T, V, adj, arcs[:-1], autonomy, cuts, kh),
            (S, T, V, adj, arcs, autonomy, (frozenset(('s1',)),), kh),
            (S, T, V, adj, arcs, autonomy, cuts, '0' * 64),
            (S, T, V, {**adj, 's2': ()}, arcs, autonomy, cuts, kh),
        ]
        for bad in altered:
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                r._exact_direct_zero_exception(case, bad)
        from dataclasses import replace
        with self.assertRaises(ValueError):
            r._exact_direct_zero_exception(replace(case, reference_raw='1'), data)
        with self.assertRaises(ValueError):
            r._exact_direct_zero_exception(replace(case, instance_hash='0'*64), data)

    def test_only_exact_frozen_control_uses_exception(self):
        case, data = self.sample()
        from dataclasses import replace
        self.assertIsNone(r._exact_direct_zero_exception(replace(case, id='T5:other'), data))

    def test_exception_is_recorded_but_cannot_automatically_release_n2_t5(self):
        cases = r.build_manifest(verify_hashes=False)
        stubs = {'run_n1_t5': types.ModuleType('run_n1_t5'),
                 'run_n1_t6': types.ModuleType('run_n1_t6')}
        stubs['run_n1_t5'].corpus = lambda: []
        stubs['run_n1_t6'].read_pairs = lambda: {'pairs': []}
        seen = []
        def evaluate(case, *_args, **_kwargs):
            seen.append(case.id)
            if case.id == 'T5:Direct0':
                return {'comparison': r.PASS_DIRECT_ZERO, 'justification': 'prova direta'}
            return {'comparison': r.PASS_LB, 'justification': 'prova CG E5'}
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(sys.modules, stubs), patch.object(
                    r, '_rebuild_case', return_value=None), patch.object(
                    r, '_evaluate_case', side_effect=evaluate):
                self.assertFalse(r._run(cases, run_dir=Path(tmp), time_limit=10,
                                        work_limit=None, max_iterations=2, enum_cap=9))
            meta = json.loads((Path(tmp) / 'n2-t4-regressao-manifest.json').read_text())
            self.assertEqual(meta['passed'], 23)
            self.assertEqual(meta['eligible_checked'], 23)
            self.assertEqual(meta['exact_domain_exceptions'], ['T5:Direct0'])
            self.assertEqual(meta['cg_evaluated'], 22)
            self.assertEqual(meta['status'], 'SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5')
            self.assertEqual(len(seen), 23)


@unittest.skipUnless(importlib.util.find_spec('gurobipy') is not None,
                     'Gurobi indisponível no ambiente de teste')
class GurobiSmokeTests(unittest.TestCase):
    def test_rebuild_real_n1_direct_zero_and_compare(self):
        from run_n1_t5 import corpus
        from run_n1_t6 import read_pairs
        case = r.build_manifest(verify_hashes=False)[0]
        data = r._rebuild_case(case, {x['nome']: x for x in corpus()},
                               {graph['name']: graph for pair in read_pairs()['pairs']
                                for graph in pair['graphs']})
        result = r._evaluate_case(case, data, time_limit=40.0, work_limit=None,
                                  max_iterations=20, enum_cap=2048)
        self.assertEqual(result['comparison'], r.PASS_DIRECT_ZERO)
        self.assertEqual(result['proof_method'], 'EXACT_DIRECT_MATCHING_ZERO_NO_CG')
        self.assertEqual(result['lp_certification_status'], r.CERTIFIED)

    def test_rebuild_real_n1_t6_control_and_compare(self):
        from run_n1_t5 import corpus
        from run_n1_t6 import read_pairs
        case = next(c for c in r.build_manifest(verify_hashes=False)
                    if c.id == 'T6:T6-F2-01-control')
        data = r._rebuild_case(case, {x['nome']: x for x in corpus()},
                               {graph['name']: graph for pair in read_pairs()['pairs']
                                for graph in pair['graphs']})
        result = r._evaluate_case(case, data, time_limit=40.0, work_limit=None,
                                  max_iterations=20, enum_cap=2048)
        self.assertIn(result['comparison'], (r.PASS_G2, r.PASS_NUMERIC, r.PASS_LB))
        self.assertEqual(result['lp_certification_status'], r.CERTIFIED)


if __name__ == '__main__':
    unittest.main()
