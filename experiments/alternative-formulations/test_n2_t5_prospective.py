"""N2-T5: contratos prospectivos, integridade da N1/N2-T4 e contabilidade.

Sem Gurobi: testes puros. A execução experimental real acontece via `run`.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

# Diretório de experimentos é intencionalmente importável sem pacote Python.
# ruff: noqa: E402
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_n2_t5 as m


class FrozenContractTests(unittest.TestCase):
    def setUp(self):
        with open(m.FREEZE, encoding='utf8') as f:
            self.freeze = json.load(f)

    def test_exact_four_by_two_by_two(self):
        plan = m.check_freeze(full=False)
        self.assertEqual(tuple(x['name'] for x in plan['instances']), m.EXPECTED_NAMES)
        self.assertEqual({(x['family'], x['level']) for x in plan['instances']},
                         {('hb', 1), ('hb', 2), ('bp-nao', 1), ('bp-nao', 2)})

    def test_freeze_rejects_mutated_budget(self):
        altered = json.loads(json.dumps(self.freeze))
        altered['protocol']['WorkLimit_total'] = 328.0
        with patch.object(m, '_read', return_value=altered):
            with self.assertRaisesRegex(ValueError, 'protocolo'):
                m.check_freeze(full=False)

    def test_freeze_rejects_mutated_identity(self):
        altered = json.loads(json.dumps(self.freeze))
        altered['instances'][2]['name'] = 'synthetic-after-results'
        with patch.object(m, '_read', return_value=altered):
            with self.assertRaisesRegex(ValueError, 'instâncias'):
                m.check_freeze(full=False)

    def test_no_historical_full_lp_fabricated_for_level2(self):
        altered = json.loads(json.dumps(self.freeze))
        altered['instances'][2]['full_lp_reference'] = 12
        with patch.object(m, '_read', return_value=altered):
            with self.assertRaisesRegex(ValueError, 'fabricadas'):
                m.check_freeze(full=False)

    def test_wrong_or_missing_hashseed_rejected(self):
        with patch.dict(os.environ, {'PYTHONHASHSEED': '1'}):
            with self.assertRaisesRegex(RuntimeError, 'PYTHONHASHSEED'):
                m.check_freeze(full=False)

    def test_integer_rational_roundtrip_and_missing_value(self):
        self.assertIsNone(m._reference(None))
        self.assertEqual(m._reference(0.5), Fraction(1, 2))
        self.assertEqual(m._ratio(Fraction(7, 3)), '7/3')
        self.assertEqual(m._ratio(None), '')
        with self.assertRaises(TypeError):
            m._ratio(2.5)


class T4GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = Path(self.tmp.name)
        self.gate = p / 'gate.md'
        self.csv = p / 'regression.csv'
        self.manifest = p / 'manifest.json'
        self.freeze = p / 'n2-t1-freeze.json'
        self.freeze.write_bytes(b'fixed-freeze')
        self.gate.write_text('APROVADO_COM_EXCECAO_DE_DOMINIO_DIRECT0\n'
                             'ACEITA_COM_EXCECAO_FORMAL\nLIBERAR N2-T5', encoding='utf8')
        rows = [{'id': 'T5:Direct0',
                 'comparison': 'PASS_DIRECT_ZERO_EXACT_OUTSIDE_CONNECTED_DOMAIN',
                 'lp_lb_exact': '0/1', 'lp_certification_status': m.CERTIFIED}]
        rows += [{'id': f'T5:fake-{i}', 'comparison': 'PASS_CERTIFIED_LB_LE_FULL_LP',
                  'lp_lb_exact': '1/1', 'lp_certification_status': m.CERTIFIED}
                 for i in range(22)]
        rows.append({'id': 'T5:SC-GF2-k3', 'comparison': 'EXCLUDED_NO_FULL_LP_REFERENCE',
                     'lp_lb_exact': '', 'lp_certification_status': ''})
        self.rows = rows
        self.csv.write_bytes(m._csv_bytes(rows, ('id', 'comparison', 'lp_lb_exact',
                                                  'lp_certification_status')))
        self.contents = {
            'task': 'N2-T4', 'status': 'SCOPE_EXCEPTION_REVIEW_BLOCK_N2_T5',
            'expected_eligible': 23, 'eligible_checked': 23,
            'passed': 23, 'cg_evaluated': 22, 'failures': [],
            'exact_domain_exceptions': ['T5:Direct0'],
            'excluded': ['T5:SC-GF2-k3'],
            'csv_sha256': m._sha(self.csv),
            'n2_t1_sha256': m._sha(self.freeze), 'n1_sources_sha256': {},
        }
        self._save()

    def _save(self):
        self.manifest.write_text(json.dumps(self.contents), encoding='utf8')

    def _verify(self):
        with patch.multiple(m, T4_GATE=self.gate, T4_MANIFEST=self.manifest,
                            T4_REPORT=self.csv, FREEZE=self.freeze):
            return m.check_t4_gate()

    def test_accepted_exception_and_22_cg_pass(self):
        result = self._verify()
        self.assertEqual(result['counts'], {'cg': 22, 'direct': 1, 'excluded': 1})

    def test_tampered_csv_rejected(self):
        self.csv.write_bytes(self.csv.read_bytes() + b'corrupt')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self._verify()

    def test_fake_change_to_manifest_gate_status_rejected(self):
        self.contents['status'] = 'PASS_N2_T5'
        self._save()
        with self.assertRaisesRegex(ValueError, 'status original'):
            self._verify()

    def test_21_cg_pass_not_enough(self):
        self.contents['cg_evaluated'] = 21
        self._save()
        with self.assertRaisesRegex(ValueError, 'cg_evaluated'):
            self._verify()

    def test_missing_human_approval_rejected(self):
        self.gate.write_text('sem aprovação', encoding='utf8')
        with self.assertRaisesRegex(ValueError, 'decisão humana'):
            self._verify()

    def test_different_n2_t1_freeze_rejected(self):
        self.contents['n2_t1_sha256'] = '0' * 64
        self._save()
        with self.assertRaisesRegex(ValueError, 'pré-registro'):
            self._verify()

    def test_forged_exception_proof_rejected(self):
        self.rows[0]['lp_lb_exact'] = '1/1'
        self.csv.write_bytes(m._csv_bytes(self.rows, ('id', 'comparison', 'lp_lb_exact',
                                                      'lp_certification_status')))
        self.contents['csv_sha256'] = m._sha(self.csv)
        self._save()
        with self.assertRaisesRegex(ValueError, 'Direct0'):
            self._verify()


class LedgerTests(unittest.TestCase):
    def test_work_cumulative_not_restarted_between_solves(self):
        b = m.Budget(164.0, 1800, clock=lambda: 0.0)
        b.add('comp_lp', 50.0)
        b.add('core_ip', 40.0)
        self.assertEqual(b.remaining(), 74.0)
        b.add('cg', 74.0)
        self.assertEqual(b.remaining(), 0.0)
        with self.assertRaises(TimeoutError):
            b.ensure()

    def test_any_solver_overrun_discarded(self):
        b = m.Budget(164, 1800, clock=lambda: 0)
        b.add('comp_lp', 160)
        with self.assertRaisesRegex(TimeoutError, 'excedeu'):
            b.add('core_ip', 4.1)
        self.assertAlmostEqual(b.work_items['core_ip'], 4.1)

    def test_unmeasured_work_never_imputed(self):
        b = m.Budget(164, 1800, clock=lambda: 0)
        for value in (float('nan'), float('inf'), -1, None):
            with self.assertRaises(RuntimeError):
                b.add('pricing', value)
        self.assertEqual(b.unmeasured, 4)
        with self.assertRaises(RuntimeError):
            b.ensure()

    def test_wall_guard_counts_python(self):
        times = iter([0, 1801])
        b = m.Budget(164, 1800, clock=lambda: next(times))
        with self.assertRaises(TimeoutError):
            b.ensure()

    def test_accounting_exact_four_phases(self):
        row = dict(work_comp_lp=12., work_core_ip=13., work_master=14.,
                   work_pricing=15., work_total=54.,
                   wall_assembly_s=1., wall_reach_s=0., wall_k_s=2.,
                   wall_comp_lp_s=3., wall_core_ip_s=4., wall_cg_s=5.,
                   wall_postcheck_s=6., wall_other_s=7., wall_total_s=28.,
                   physical_status=m.UNCERTIFIED)
        m.validate_accounting(row)
        row['work_total'] = 53
        with self.assertRaisesRegex(ValueError, 'Work total'):
            m.validate_accounting(row)

    def test_no_fake_gain_with_b0_missing(self):
        with self.assertRaisesRegex(ValueError, 'ganho sem B0'):
            m.validate_accounting({'b0_reference': '', 'gain_over_b0_reference': '0/1'})

    def test_no_certified_status_without_exact_value(self):
        with self.assertRaisesRegex(ValueError, 'status CERTIFIED'):
            m.validate_accounting({'lp_status': m.CERTIFIED, 'lp_lb_exact': ''})
        with self.assertRaisesRegex(ValueError, 'limite físico'):
            m.validate_accounting({'physical_status': m.CERTIFIED, 'physical_lb_exact': ''})

    def test_abstention_preserves_partial_work(self):
        b = m.Budget(164, 1800, clock=lambda: 0)
        b.add('comp_lp', 13)
        b.add('core_ip', 18)
        error = m.MeasuredAbstention(ValueError('failed'), b, {})
        row = m._failed_row({'name': 'HB-q6-ndir2-p1', 'family': 'hb',
                             'level': 2, 'n': 26, 'm': 10, 'r': 1,
                             'instance_sha256': 'hash'}, 'freeze', error, 15)
        self.assertEqual(row['work_comp_lp'], 13)
        self.assertEqual(row['work_core_ip'], 18)
        self.assertEqual(row['work_total'], '')
        self.assertEqual(row['physical_status'], m.UNCERTIFIED)


class OutputTests(unittest.TestCase):
    def test_csv_schema_preserves_empty(self):
        blob = m._csv_bytes([{'name': 'HB-q6-ndir2-p1', 'b0_reference': ''}], m.FIELDS)
        record = list(csv.DictReader(io.StringIO(blob.decode())))[0]
        self.assertEqual(record['b0_reference'], '')
        self.assertEqual(record['name'], 'HB-q6-ndir2-p1')

    def test_create_only_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'n2t5'
            paths = m._write_new(target, [{'name': m.EXPECTED_NAMES[0]}], [],
                                 {'task': 'N2-T5'}, 'cost report')
            self.assertEqual(len(paths), 5)
            manifest = json.loads((target / 'n2-t5-manifest.json').read_text())
            for name, digest in manifest['artifacts_sha256'].items():
                self.assertEqual(m._sha(target / name), digest)
            with self.assertRaises(FileExistsError):
                m._write_new(target, [], [], {}, '')

    def test_svg_contains_only_certified_points(self):
        curve = [{'name': m.EXPECTED_NAMES[0], 'lb_status': m.CERTIFIED,
                  'lb_exact': '3/2', 'cumulative_work': 2.0}]
        svg = m._curve_svg(curve, [{'name': m.EXPECTED_NAMES[0],
                                   'b0_reference': '1/1'}]).decode()
        self.assertIn('<svg', svg)
        self.assertIn('N2-T5', svg)
        self.assertIn('1/1', svg)
        self.assertEqual(svg.count('<circle'), 1)

    def test_only_four_frozen_rows_not_adaptive(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = {'instances': [{'name': n, 'family': ('hb' if i % 2 == 0 else 'bp-nao'),
                                   'level': 1 if i < 2 else 2}
                                  for i, n in enumerate(m.EXPECTED_NAMES)],
                    'protocol': {'WorkLimit_total': 164}}
            def evaluator(case, *, freeze_hash):
                return ({'name': case['name'], 'family': case['family'],
                         'level': case['level'], 'status': 'CERTIFIED_PHYSICAL_LB',
                         'physical_status': m.CERTIFIED,
                         'physical_lb_exact': '1/1', 'b0_reference': '0/1',
                         'work_total': 2, 'work_comp_lp': 0, 'work_core_ip': 0,
                         'work_master': 1, 'work_pricing': 1}, [])
            with patch.object(m, 'check_freeze', return_value=plan):
                result = m.run_all(Path(tmp) / 'out', evaluator=evaluator,
                                   preflight=lambda: {'freeze_sha256': 'digest',
                                                      't4': {'csv_sha256': 'digest'}})
            self.assertEqual(result, 0)
            with (Path(tmp) / 'out' / 'n2-t5-medicoes.csv').open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual([r['name'] for r in rows], list(m.EXPECTED_NAMES))
            manifest = json.loads((Path(tmp) / 'out' / 'n2-t5-manifest.json').read_text())
            self.assertEqual(manifest['status'], 'MEASURED_PENDING_N2_T6')

    def test_execution_failure_produces_abstention_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = {'instances': [{'name': n, 'family': 'hb' if i % 2 == 0 else 'bp-nao',
                                   'level': 1 if i < 2 else 2, 'n': 5, 'm': 2, 'r': 1,
                                   'instance_sha256': 'x'}
                                  for i, n in enumerate(m.EXPECTED_NAMES)],
                    'protocol': {'WorkLimit_total': 164}}
            def failure(case, *, freeze_hash):
                raise RuntimeError('solver failed')
            with patch.object(m, 'check_freeze', return_value=plan):
                ret = m.run_all(Path(tmp) / 'out', evaluator=failure,
                                preflight=lambda: {'freeze_sha256': 'freeze',
                                                   't4': {'csv_sha256': 'digest'}})
            self.assertEqual(ret, 2)
            with (Path(tmp) / 'out' / 'n2-t5-medicoes.csv').open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(r['status'] == 'ABSTAINED_INCOMPLETE' for r in rows))
            self.assertTrue(all(r['b0_reference'] == '' and r['physical_lb_exact'] == ''
                                for r in rows))


class RealPipelineContractTests(unittest.TestCase):
    def _run_fake(self, level, *, cg_work=0.5, comp_work=0.2, core_work=0.3):
        case = {'name': m.EXPECTED_NAMES[level-1], 'family': 'hb', 'level': level,
                'n': 16, 'm': 2, 'r': 1, 'instance_sha256': 'hash',
                'B0_reference': 1.0 if level == 1 else None,
                'full_lp_reference': 2.0 if level == 1 else None,
                'expected_positive_increment': 1.0 if level == 1 else None}
        b0 = SimpleNamespace(status=m.UNCERTIFIED)
        record = SimpleNamespace(master_cost=SimpleNamespace(work=cg_work * 0.4, runtime=0.01),
                                 pricing_cost=SimpleNamespace(work=cg_work * 0.6, runtime=0.01),
                                 candidate_reduced_cost=None, pricing_solver_bound=None)
        base = SimpleNamespace(total_work=cg_work, unmeasured_work_calls=0, history=(record,),
                               stop_reason='ITERATION_LIMIT', rmp_objective=1.0,
                               pricing_calls=0, columns_added=0, columns=(),
                               iterations=0, wall_time=0.01)
        final = SimpleNamespace(numerical_result=base, lp_status=m.CERTIFIED,
                                lp_lb_exact=Fraction(1), lp_source='N1',
                                physical_status=m.CERTIFIED,
                                physical_lb_exact=Fraction(1), physical_integer_lb=1,
                                primal_upper=None, convergence_status='NOT_PROVED',
                                audit_warnings=(), validation_wall=0.0,
                                justification='verified by E5', audit_history=(),
                                baseline=b0)
        class Options:
            def __init__(self, **kw):
                self.kw = kw
        observed = {}
        def cg(*args, **kwargs):
            observed['remaining'] = kwargs['work_limit']
            observed['threads'] = kwargs['master_params']['Threads']
            observed['seed'] = kwargs['pricing_params']['Seed']
            return final
        def solve(kind, data, K, budget, **kwargs):
            work = comp_work if kind == 'comp_lp' else core_work
            budget.add(kind, work)
            return {'objective': 1.0 if kind == 'comp_lp' else 0.0,
                    'status': 'OPTIMAL_NUMERIC'}
        files = {
            'n2_t3_cert_integration': SimpleNamespace(CertificationOptions=Options),
            'n2_t3_cert_validation': SimpleNamespace(run_verified_column_generation=cg),
            'run_n2_t1': SimpleNamespace(prior_rows=lambda: (
                {case['name']: {'B0': '1', 'lp_comp': '1', 'core_ip': '1',
                                'lp_fcc_k': '2'}}, {})),
        }
        with patch.dict(sys.modules, files), \
             patch.object(m, '_load_instance', return_value=((0,), (0,), (0,),
                                                               {0: ()}, (), 1)), \
             patch.object(m, '_verify_reach', return_value=0), \
             patch.object(m, '_prepare_k', return_value=([], 'khash', {})), \
             patch.object(m, '_solver_once', side_effect=solve), \
             patch.object(m, '_make_curve', return_value=[]):
            row, curve = m.run_one(case, freeze_hash='sha')
        return row, curve, observed

    def test_level_one_reuses_archived_reference_without_baseline_solve(self):
        row, _, observed = self._run_fake(1)
        self.assertEqual(observed['remaining'], 164.0)
        self.assertEqual(row['work_total'], 0.5)
        self.assertEqual(row['b0_reference'], '1/1')
        self.assertEqual(row['b0_reference_status'], 'N1_FROZEN_REFERENCE')
        self.assertEqual(row['b0_comp_lp'], 1.0)
        self.assertEqual(row['status'], 'CERTIFIED_PHYSICAL_LB')
        self.assertEqual(observed['threads'], 4)
        self.assertEqual(observed['seed'], 42)

    def test_level_two_debits_baselines_from_same_work_cap(self):
        # O caso estruturado desconhecido deve medir COMP e core antes do CG.
        row, _, observed = self._run_fake(2)
        self.assertAlmostEqual(observed['remaining'], 163.5)
        self.assertAlmostEqual(row['work_total'], 1.0)
        self.assertEqual(row['work_comp_lp'], 0.2)
        self.assertEqual(row['work_core_ip'], 0.3)
        self.assertEqual(row['b0_reference_status'], 'OPTIMAL_NUMERIC_NOT_E5_CERTIFIED')
        self.assertEqual(row['b0_certificate_status'], m.UNCERTIFIED)

    def test_level_two_budget_overrun_never_publishes_new_lb(self):
        with self.assertRaises(m.MeasuredAbstention):
            self._run_fake(2, cg_work=164)

    def test_status_without_physical_proof_must_abstain(self):
        row, _, _ = self._run_fake(1)
        self.assertEqual(row['physical_status'], m.CERTIFIED)
        self.assertNotEqual(row['g2_status'], 'CONVERGED_CERTIFIED')



if __name__ == '__main__':
    unittest.main()
