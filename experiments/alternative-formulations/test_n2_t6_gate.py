"""Regression and adversarial tests for the read-only N2-T6 scientific gate."""
from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import verify_n2_t6_gate as gate


FREEZE = json.loads(gate.FREEZE.read_text(encoding='utf-8'))


def make_rows():
    details = [
        ('1/1', '1/2', '2.0', '-1/2', '-1/2', '1.0', '1.0', '1'),
        ('6/1', '1/1', '7.0', '-5/1', '-5/1', '6.0', '6.0', '1'),
        ('11500000000000001/10000000000000000', '2/3', '',
         '-14500000000000003/30000000000000000', '', '1.1500000000000001', '1.0', '1'),
        ('8/1', '18/13', '', '-86/13', '', '8.0', '8.0', '2'),
    ]
    out = []
    for ctrl, (b0, lb, full, gain, rec, comp, core, rounded) in zip(
            FREEZE['instances'], details, strict=True):
        out.append({
            'name': ctrl['name'], 'family': ctrl['family'],
            'level': str(ctrl['level']), 'n': str(ctrl['n']), 'm': str(ctrl['m']),
            'r': str(ctrl['r']), 'instance_sha256': ctrl['instance_sha256'],
            'k_sha256': ctrl.get('k_sha256', '0' * 64),
            'freeze_sha256': gate.EXPECTED_FREEZE_SHA256,
            'path': 'B/F-CC+K ROOT_ONLY', 'seed': '42', 'threads': '4',
            'work_cap': '164.0', 'wall_cap_s': '1800.0',
            'b0_reference': b0, 'b0_comp_lp': comp, 'b0_core_ip': core,
            'b0_certificate_status': 'UNCERTIFIED', 'b0_certified_exact': '',
            'full_lp_historical': full, 'lp_status': 'CERTIFIED',
            'lp_lb_exact': lb, 'lb_continuous_exact': lb, 'lp_source': 'N1',
            'physical_status': 'CERTIFIED', 'physical_lb_exact': lb,
            'physical_integer_lb': rounded, 'g2_status': 'NOT_CONVERGED_CERTIFIED',
            'gain_over_b0_reference': gain, 'recovery_fraction_level1': rec,
            'stop_reason': 'NUMERICAL_STATIONARY', 'status': 'CERTIFIED_PHYSICAL_LB',
            'work_comp_lp': '0', 'work_core_ip': '0', 'work_master': '0.1',
            'work_pricing': '0.2', 'work_total': '0.3',
            'work_unmeasured_calls': '0', 'wall_total_s': '3.0',
            'pricing_calls': '1', 'n_curve_points': '1',
        })
    return out


def write_csv(path: Path, rows: list[dict]):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(root: Path):
    f = root / 'experiments/alternative-formulations/n2-t1-freeze.json'
    f.parent.mkdir(parents=True)
    shutil.copyfile(gate.FREEZE, f)
    results = root / 'results/alternative-formulations/n2-t5-prospectivo'
    results.mkdir(parents=True)
    rows = make_rows()
    write_csv(results / gate.CSV_NAME, rows)
    curve = []
    for row in rows:
        curve.append({'name': row['name'], 'iteration': '0',
                      'cumulative_work': '0.3', 'cumulative_wall_s': '2.5',
                      'lb_status': 'CERTIFIED', 'lb_exact': row['physical_lb_exact'],
                      'lb_source': 'N1', 'pricing_calls': '1',
                      'note': 'NUMERICAL_STATIONARY'})
    write_csv(results / gate.CURVE_NAME, curve)
    (results / gate.COSTS_NAME).write_text('# costs\n', encoding='utf-8')
    (results / gate.SVG_NAME).write_text('<svg></svg>\n', encoding='utf-8')
    expected = {filename: gate.sha256(results / filename)
                for filename in gate.EXPECTED_ARTIFACTS}
    manifest = {'task': 'N2-T5', 'status': 'MEASURED_PENDING_N2_T6',
                'freeze_sha256': gate.EXPECTED_FREEZE_SHA256,
                'instances_in_freeze_order': list(gate.EXPECTED_NAMES),
                'n_rows': 4, 'n_physical_certified': 4,
                'protocol': FREEZE['protocol'], 'scope': 'prospective, root only',
                'artifacts_sha256': expected}
    (results / gate.MANIFEST).write_text(json.dumps(manifest), encoding='utf-8')
    return results, expected


class FrozenGateRuleTests(unittest.TestCase):
    def test_negative_gains_issue_fail_not_missing_proof(self):
        report = gate.scientific_decision(make_rows(), FREEZE)
        self.assertEqual(report['decision'], 'N2 FAIL')
        self.assertEqual(len(report['measured']), 4)
        self.assertEqual(len(report['blocking_reasons']), 6)

    def test_50_percent_recovery_independently(self):
        rows = make_rows()
        self.assertEqual((Fraction(rows[0]['physical_lb_exact']) -
                          Fraction(rows[0]['b0_reference'])) /
                         (Fraction(rows[0]['full_lp_historical']) -
                          Fraction(rows[0]['b0_reference'])), Fraction(-1, 2))
        self.assertEqual((Fraction(rows[1]['physical_lb_exact']) -
                          Fraction(rows[1]['b0_reference'])) /
                         (Fraction(rows[1]['full_lp_historical']) -
                          Fraction(rows[1]['b0_reference'])), Fraction(-5))

    def test_forged_gain_rejected(self):
        rows = make_rows()
        rows[0]['gain_over_b0_reference'] = '10/1'
        with self.assertRaisesRegex(gate.AuditError, 'ganho'):
            gate.scientific_decision(rows, FREEZE)

    def test_forged_integer_rounding_rejected(self):
        rows = make_rows()
        rows[3]['physical_integer_lb'] = '9'
        with self.assertRaisesRegex(gate.AuditError, 'arredondamento'):
            gate.scientific_decision(rows, FREEZE)

    def test_weak_lb_not_replaced_by_numeric_rmp(self):
        rows = make_rows()
        rows[0]['rmp_obj_numeric_diagnostic'] = '99.0'
        report = gate.scientific_decision(rows, FREEZE)
        self.assertEqual(report['decision'], 'N2 FAIL')

    def test_tampered_frozen_case_rejected(self):
        rows = make_rows()
        rows[2]['instance_sha256'] = 'f' * 64
        with self.assertRaisesRegex(gate.AuditError, 'instância'):
            gate.scientific_decision(rows, FREEZE)

    def test_missing_full_lp_remains_missing_level_two(self):
        rows = make_rows()
        rows[2]['full_lp_historical'] = '3.0'
        with self.assertRaisesRegex(gate.AuditError, 'indevidamente imputados'):
            gate.scientific_decision(rows, FREEZE)


class ArtifactAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.results, self.expected = make_fixture(self.root)

    def test_full_fixture_issues_fail_with_verified_bytes(self):
        report = gate.audit(self.root, expected_artifacts=self.expected)
        self.assertEqual(report['decision'], 'N2 FAIL')
        self.assertEqual(report['audit_status'],
                         'VERIFIED_ARTIFACT_BYTES_AND_TABULAR_INVARIANTS')

    def test_one_byte_changed_in_curve_rejected(self):
        p = self.results / gate.CURVE_NAME
        p.write_bytes(p.read_bytes() + b'\n')
        with self.assertRaisesRegex(gate.AuditError, 'bytes'):
            gate.audit(self.root, expected_artifacts=self.expected)

    def test_tampered_manifest_digest_rejected(self):
        p = self.results / gate.MANIFEST
        data = json.loads(p.read_text())
        data['artifacts_sha256'][gate.CSV_NAME] = '0' * 64
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(gate.AuditError, 'âncora'):
            gate.audit(self.root, expected_artifacts=self.expected)

    def test_modified_freeze_refused(self):
        p = self.root / 'experiments/alternative-formulations/n2-t1-freeze.json'
        p.write_bytes(p.read_bytes() + b'\n')
        with self.assertRaisesRegex(gate.AuditError, 'freeze'):
            gate.audit(self.root, expected_artifacts=self.expected)

    def test_monotonic_lb_enforced(self):
        rows = make_rows()
        curves = [
            {'name': row['name'], 'iteration': '0', 'cumulative_work': '0.1',
             'cumulative_wall_s': '1.0', 'lb_status': 'CERTIFIED',
             'lb_exact': row['physical_lb_exact'], 'lb_source': 'N1',
             'pricing_calls': '1', 'note': 'NUMERICAL_STATIONARY'}
            for row in rows
        ]
        curves[0]['lb_exact'] = '100/1'
        with self.assertRaisesRegex(gate.AuditError, 'diferente'):
            gate.validate_curves(curves, rows)

    def test_missing_artifact_rejected(self):
        (self.results / gate.SVG_NAME).unlink()
        with self.assertRaises(FileNotFoundError):
            gate.audit(self.root, expected_artifacts=self.expected)


if __name__ == '__main__':
    unittest.main()
