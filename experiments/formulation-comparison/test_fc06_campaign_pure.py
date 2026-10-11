"""FC-06: testes independentes HOUR-01...HOUR-06, sem Gurobi."""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import fc06_campaign as c
import fc06_reporting as reporting
import run_extended_comparison as runner
import verify_extended_campaign as verifier

DIGEST = 'a' * 64
KHASH = 'b' * 64
MAIN = 'hb-q5-ndir2-p1-k1-L2.txt'
ORIGIN = 'test:synthetic-root'


def sample_screen(name=MAIN, *, status_comp='OPTIMAL', status_fcc='TIME_LIMIT',
                  wall_comp='0.9', wall_fcc='120'):
    return [{
        'instance_name': name, 'modality': 'B', 'formulation': form,
        'instance_sha256': DIGEST, 'k_sha256': KHASH, 'pair_status': 'PAIR_VALID',
        'model_complete': 'True', 'k_validated': 'True', 'n_K': '5', 'n_K_added': '5',
        'status': status, 'wall_total_s': wall,
    } for form, status, wall in (
        ('comp_mip', status_comp, wall_comp), ('fcc_k', status_fcc, wall_fcc))]


def selected():
    return [{'instance': MAIN, 'instance_sha256': DIGEST, 'k_sha256': KHASH,
             'input_path': 'instances/structural.txt',
             'origin_graph': ORIGIN, 'familia': 'hb', 'eligibility': 'UNRESOLVED_COMPLETE_MODEL'}]


def prereg(*, include_lp=True):
    entries = selected()
    return {'schema': c.SCHEMA, 'pilot_gate': 'READY_FOR_EXTENDED',
            'selected': entries, 'seeds': list(c.SEEDS),
            'include_lp': include_lp, 'mip_wall_cap_s': 3600.0,
            'lp_wall_cap_s': 600.0,
            'plan': c.make_plan(entries, include_lp=include_lp),
            'code_files_sha256': {'code.py': DIGEST}}


def numeric_row(p, *, status='OPTIMAL', pair_status='PAIR_VALID'):
    data = {**p,
            'instance_name': p['instance'], 'instance_sha256': DIGEST,
            'origin_graph': p['origin_graph'], 'plan_order': p['order'],
            'status': status, 'stop_reason': status,
            'solver_evidence': ('SOLVER_NUMERIC_OPTIMAL' if status == 'OPTIMAL'
                                else 'SOLVER_NUMERIC_BOUND_ONLY'),
            'rational_verification': 'NOT_CERTIFIED',
            'certified_gap_status': 'INCONCLUSIVE',
            'solver_numeric_lp_objective': '2',
            'solver_numeric_mip_lb': '2', 'solver_numeric_mip_incumbent': '2',
            'physical_feasible_ub': '2', 'physically_validated': 'True',
            'model_complete': 'True', 'k_validated': 'True',
            'k_sha256': KHASH, 'pair_status': pair_status,
            'wall_total_s': '4.5', 'solver_runtime_s': '1.1', 'work': '1.6'}
    return data


class EligibilityTests(unittest.TestCase):
    def test_hour01_gate_false_cannot_validate(self):
        r = prereg()
        r['pilot_gate'] = 'NOT_READY'
        with self.assertRaisesRegex(ValueError, 'gate'):
            c.validate_prereg(r)

    def test_hour01_empty_candidates_stop(self):
        r = prereg()
        r['selected'] = []
        with self.assertRaisesRegex(ValueError, 'instâncias informativas'):
            c.validate_prereg(r)

    def test_hour02_full_mip_screening_can_be_eligible_if_unresolved(self):
        ok, mode, ev = c.pair_screening(sample_screen(), MAIN, DIGEST)
        self.assertTrue(ok)
        self.assertEqual(mode, 'UNRESOLVED_COMPLETE_MODEL')
        self.assertEqual(ev['k_sha256'], KHASH)

    def test_hour02_resolved_trivial_refused_even_with_justification(self):
        rows = sample_screen(status_fcc='OPTIMAL', wall_fcc='2')
        allowed, *_ = c.pair_screening(rows, MAIN, DIGEST,
                                       justification='x' * 100)
        self.assertFalse(allowed)

    def test_hour02_resolved_without_justification_refused(self):
        rows = sample_screen(status_fcc='OPTIMAL', wall_fcc='50')
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])
        self.assertTrue(c.pair_screening(rows, MAIN, DIGEST, justification='x' * 100)[0])

    def test_hour04_cap_is_not_eligible(self):
        rows = sample_screen(status_fcc='CAP_EXCEEDED')
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])

    def test_hour02_k_and_instance_hash_mismatch_refused(self):
        rows = sample_screen()
        rows[0]['k_sha256'] = 'c' * 64
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])
        rows = sample_screen()
        rows[0]['instance_sha256'] = 'c' * 64
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])

    def test_hour02_k_added_count_and_model_complete_checked(self):
        rows = sample_screen()
        rows[0]['n_K_added'] = '4'
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])
        rows = sample_screen()
        rows[1]['model_complete'] = 'False'
        self.assertFalse(c.pair_screening(rows, MAIN, DIGEST)[0])

    def test_hour02_duplicate_screening_refused(self):
        rows = sample_screen()
        self.assertFalse(c.pair_screening(rows + rows[:1], MAIN, DIGEST)[0])

    def test_hour02_prereg_plan_cannot_be_mutated(self):
        r = prereg()
        c.validate_prereg(r)
        r['plan'][0]['wall_budget_s'] = 9999
        with self.assertRaisesRegex(ValueError, 'plano'):
            c.validate_prereg(r)

    def test_hour03_budget_and_seed_order_exact(self):
        plan = c.make_plan(selected())
        self.assertEqual(len(plan), 9)
        self.assertEqual([x['formulation'] for x in plan[:3]], list(c.LP_ARMS))
        self.assertEqual([x['formulation'] for x in plan[3:]],
                         ['comp_mip', 'fcc_k', 'fcc_k', 'comp_mip', 'comp_mip', 'fcc_k'])
        self.assertTrue(all(x['wall_budget_s'] == 3600 for x in plan[3:]))
        self.assertTrue(all(x['wall_budget_s'] == 600 for x in plan[:3]))

    def test_hour03_no_3600_runs_automatically(self):
        with self.assertRaisesRegex(ValueError, 'confirm-long-run'):
            runner.execute('/tmp/unimportant', confirm_long_run=False)

    def test_hour05_origin_group_not_seed_independent(self):
        plan = c.make_plan(selected(), include_lp=False)
        rows = [numeric_row(p) for p in plan]
        rows[1]['status'] = 'CAP_EXCEEDED'
        rows[1]['pair_status'] = 'PAIR_NOT_AVAILABLE'
        groups = c.grouped_counts(rows, plan)
        self.assertEqual(groups[ORIGIN]['planned_arms'], 6)
        self.assertEqual(groups[ORIGIN]['censored_arms'], 1)
        self.assertEqual(groups[ORIGIN]['pair_not_valid_repetitions'], 1)
        self.assertEqual(groups[ORIGIN]['pair_valid_repetitions'], 2)

    def test_hour05_missing_arm_counts_as_censored(self):
        plan = c.make_plan(selected(), include_lp=False)
        groups = c.grouped_counts([], plan)
        self.assertEqual(groups[ORIGIN]['censored_arms'], 6)
        self.assertEqual(groups[ORIGIN]['pair_not_valid_repetitions'], 3)

    def test_hour05_report_separates_lp_and_mip(self):
        p = prereg()
        rows = [numeric_row(x) for x in p['plan']]
        summary = reporting.summary(rows, p)
        self.assertEqual(summary['planned_mip_pairs_total'], 3)
        self.assertEqual(len(summary['lp_strength_observations']), 1)
        self.assertFalse(summary['universal_superiority_claimed'])
        self.assertFalse(summary['any_rational_certification_claimed'])

    def test_hour06_report_preserves_missing_denominator_and_rational_absence(self):
        p = prereg(include_lp=False)
        rows = [numeric_row(x) for x in p['plan'][:2]]
        data = reporting.summary(rows, p)
        self.assertEqual(data['planned_arms_total'], 6)
        self.assertEqual(data['censored_or_missing_arms_total'], 4)
        self.assertEqual(data['comparable_mip_pairs_total'], 1)
        self.assertTrue(all(x['rational_verification'] == 'NOT_CERTIFIED'
                            for x in data['mip_pair_outcomes']))


class SourcePreflightTests(unittest.TestCase):
    def test_hour01_pilot_not_ready_refuses_before_selection(self):
        with mock.patch.object(runner, 'evaluate_pilot', return_value={
            'status': 'NOT_READY', 'problems': ['tampered']}):
            with self.assertRaisesRegex(ValueError, 'FC05_GATE_NOT_READY'):
                runner._pilot_preflight(runner.ROOT)

    def test_hour01_screening_unaudited_refused(self):
        with mock.patch.object(runner, 'audit_artifacts', return_value=(False, ['bad'])):
            with self.assertRaisesRegex(ValueError, 'SCREENING_ARTIFACT_AUDIT_FAILED'):
                runner._screening_preflight(runner.ROOT)

    def test_hour02_source_not_inside_repo_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                runner._in_repo_dir(Path(d))

    def test_hour02_out_dir_must_be_new_extended_and_not_existing(self):
        with self.assertRaises(ValueError):
            runner._safe_out_dir(runner.EXTENDED_ROOT / 'pilot-new')

    def test_hour02_prepare_explicit_not_eligible_creates_no_prereg(self):
        with tempfile.TemporaryDirectory(dir=runner.EXTENDED_ROOT, prefix='extended-test-parent-') as parent:
            path = Path(parent) / 'extended-refusal'
            with (mock.patch.object(runner, '_pilot_preflight', return_value={'status': runner.READY}),
                  mock.patch.object(runner, '_screening_preflight', return_value=({}, []))):
                result = runner.prepare(
                    pilot_run=runner.ROOT / 'results/formulation-comparison/pilot-20261011T002026Z',
                    screening_run=runner.ROOT / 'results/formulation-comparison/main-20261010T071251Z',
                    run_dir=path)
            self.assertEqual(result['status'], 'NOT_ELIGIBLE')
            self.assertFalse((path / 'preregistration.json').exists())
            self.assertEqual(json.loads((path / 'eligibility_report.json').read_text())['status'],
                             'NOT_ELIGIBLE')

    def test_hour02_prepare_and_execute_preflight_sealed_without_solver(self):
        real = {x.nome: x for x in runner.fi.pool('main')}[MAIN]
        rows = sample_screen()
        for row in rows:
            row['instance_sha256'] = real.instance_sha256
        with tempfile.TemporaryDirectory(dir=runner.EXTENDED_ROOT, prefix='extended-test-parent-') as parent:
            path = Path(parent) / 'extended-sealed'
            fake_pilot = runner.ROOT / 'results/formulation-comparison/pilot-20261011T002026Z'
            fake_screen = runner.ROOT / 'results/formulation-comparison/main-20261010T071251Z'
            with (mock.patch.object(runner, '_pilot_preflight', return_value={'status': runner.READY}),
                  mock.patch.object(runner, '_screening_preflight', return_value=({'tier': 'main'}, rows))):
                a = runner.prepare(pilot_run=fake_pilot, screening_run=fake_screen,
                                   run_dir=path, requested=(MAIN,))
                self.assertEqual(a['status'], 'PRE_REGISTERED')
                before, _ = runner.preflight_execute(path)
                self.assertEqual(len(before['plan']), 9)
                with (path / 'plan.csv').open('a', encoding='utf-8') as stream:
                    stream.write('garbage\n')
                with self.assertRaisesRegex(ValueError, 'plan.csv'):
                    runner.preflight_execute(path)


# Schema independent audit fixtures. This tests output CONTENT, not merely
# replaying the publication-side summary algorithm.
class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dir = self.root / 'run'
        self.dir.mkdir()
        self.p = prereg(include_lp=False)
        self.rows = [numeric_row(x) for x in self.p['plan']]
        self._write()

    def _write(self):
        payload = c.canonical_bytes(self.p)
        (self.dir / 'preregistration.json').write_bytes(payload)
        (self.dir / 'preregistration.sha256').write_text(
            __import__('hashlib').sha256(payload).hexdigest() + '  preregistration.json\n')
        with (self.dir / 'plan.csv').open('w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(self.p['plan'][0]))
            writer.writeheader()
            writer.writerows(self.p['plan'])
        with (self.dir / 'results.csv').open('w', encoding='utf-8', newline='') as file:
            columns = list(dict.fromkeys(k for row in self.rows for k in row))
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(self.rows)
        report = reporting.summary(self.rows, self.p)
        (self.dir / 'campaign_report.json').write_text(json.dumps(report))
        manifest = {'tier': 'extended', 'fc06_schema': 'FC06-run-v1',
                    'preregistration_sha256': __import__('hashlib').sha256(payload).hexdigest(),
                    'code_files_sha256': self.p['code_files_sha256'],
                    'input_files_sha256': {'instances/structural.txt': DIGEST},
                    'planned_arm_count': len(self.p['plan']),
                    'reported_arm_count': len(self.rows),
                    'rational_verifier_executed': False, 'superiority_claimed': False}
        (self.dir / 'manifest.json').write_text(json.dumps(manifest))
        events = [{'event': 'START', 'preregistration_sha256':
                   __import__('hashlib').sha256(payload).hexdigest()}]
        events += [{'event': 'ARM_FINISHED', 'formulation': x['formulation']}
                   for x in self.p['plan']]
        (self.dir / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events) + '\n')

    def audit(self):
        with (mock.patch.object(verifier, 'verify_fc04', return_value=(True, [])),
              mock.patch.object(verifier, '_source_integrity')):
            return verifier.verify(self.dir, root=self.root)

    def test_hour06_independent_audit_pass(self):
        r = self.audit()
        self.assertEqual(r['status'], 'PASS', r['problems'])
        self.assertEqual(r['comparable_pairs'], 3)

    def test_hour06_audit_rejects_modified_prereg(self):
        file = self.dir / 'preregistration.json'
        file.write_bytes(file.read_bytes() + b' ')
        self.assertEqual(self.audit()['status'], 'INTEGRITY_FAIL')

    def test_hour06_audit_rejects_false_valid_pair(self):
        self.rows[0]['k_sha256'] = 'c' * 64
        self._write()
        self.assertIn('FALSE_VALID_PAIR', '\n'.join(self.audit()['problems']))

    def test_hour06_audit_rejects_fake_rational_proof(self):
        self.rows[0]['rational_verification'] = 'RATIONAL_VERIFIED'
        self._write()
        self.assertIn('RATIONAL_CERTIFICATION_UNSUPPORTED', '\n'.join(self.audit()['problems']))

    def test_hour05_audit_rejects_dropped_censored_arm(self):
        self.rows.pop()
        self._write()
        self.assertIn('PLANNED_ARM_NOT_RECORDED', '\n'.join(self.audit()['problems']))

    def test_hour05_audit_accepts_censored_arm_if_present(self):
        self.rows[0]['status'] = 'CAP_EXCEEDED'
        self.rows[0]['pair_status'] = 'PAIR_NOT_AVAILABLE'
        self.rows[1]['pair_status'] = 'PAIR_NOT_AVAILABLE'
        self.rows[0]['solver_evidence'] = 'NOT_MEASURED'
        self.rows[0]['solver_numeric_mip_lb'] = ''
        self.rows[0]['solver_numeric_mip_incumbent'] = ''
        self.rows[0]['physical_feasible_ub'] = ''
        self.rows[0]['physically_validated'] = ''
        self._write()
        r = self.audit()
        self.assertEqual(r['status'], 'PASS', r['problems'])
        self.assertEqual(r['comparable_pairs'], 2)

    def test_hour03_audit_rejects_wall_cap_violation(self):
        self.rows[0]['wall_total_s'] = '3605'
        self._write()
        self.assertIn('BUDGET_VIOLATION', '\n'.join(self.audit()['problems']))

    def test_hour02_audit_rejects_plan_modified(self):
        file = self.dir / 'plan.csv'
        file.write_text(file.read_text() + '\n')
        # Extra blank lines are ignored by csv.DictReader: change an actual row.
        text = file.read_text()
        file.write_text(text.replace('comp_mip', 'baseline', 1))
        self.assertIn('PLAN_CSV_DIFFERS', '\n'.join(self.audit()['problems']))


class EndToEndWithoutGurobiTests(unittest.TestCase):
    """Executa runner, relatórios, manifest e auditoria reais com solver simulado."""

    def test_hour01_to_hour06_fake_solver_full_publication_and_audit(self):
        import hashlib
        import sys
        import types
        from fc_integrity import source_inventory, input_inventory, generated_inventory
        inst = {i.nome: i for i in runner.fi.pool('main')}[MAIN]
        selections = [{**selected()[0], 'instance_sha256': inst.instance_sha256,
                       'instance_content_sha256': inst.instance_content_sha256,
                       'input_path': inst.caminho}]
        p = {**prereg(), 'selected': selections,
             'plan': c.make_plan(selections), 'code_files_sha256': source_inventory(runner.ROOT),
             'config': runner.fcfg.ExperimentConfig().as_dict(),
             'pilot_run': 'results/formulation-comparison/pilot-20261011T002026Z',
             'screening_run': 'results/formulation-comparison/main-20261010T071251Z'}

        def lp_func(_inst, cfg):
            return {f: types.SimpleNamespace(formulation=f, status='OPTIMAL',
                                             solver_runtime_s=0.25, work=0.1)
                    for f in c.LP_ARMS}

        def mip_func(arm):
            def fn(_inst, cfg):
                return types.SimpleNamespace(
                    formulation=arm, status_name='OPTIMAL', instance_sha256=inst.instance_sha256,
                    k_sha256=KHASH, k_validated=True, n_K=5, n_K_added=5,
                    objective_ub=3.0, physically_validated=True,
                    solver_runtime_s=0.5, work=0.25, seed=cfg.seed)
            return fn

        def fake_lp_row(instance, result):
            return {'instance_name': instance.nome, 'modality': 'A',
                    'formulation': result.formulation, 'status': result.status,
                    'solver_evidence': 'SOLVER_NUMERIC_OPTIMAL',
                    'rational_verification': 'NOT_CERTIFIED',
                    'certified_gap_status': 'INCONCLUSIVE',
                    'solver_numeric_lp_objective': 2.0, 'wall_total_s': .9,
                    'solver_runtime_s': result.solver_runtime_s, 'work': result.work}

        def fake_mip_row(instance, result, pair):
            return {'instance_name': instance.nome, 'instance_sha256': inst.instance_sha256,
                    'modality': 'B', 'formulation': result.formulation,
                    'status': result.status_name, 'solver_evidence': 'SOLVER_NUMERIC_OPTIMAL',
                    'rational_verification': 'NOT_CERTIFIED',
                    'certified_gap_status': 'INCONCLUSIVE',
                    'model_complete': True, 'k_sha256': result.k_sha256,
                    'k_validated': True, 'physically_validated': True,
                    'physical_feasible_ub': 3, 'solver_numeric_mip_incumbent': 3,
                    'solver_numeric_mip_lb': 3, 'wall_total_s': 1.2,
                    'solver_runtime_s': result.solver_runtime_s, 'work': result.work,
                    'pair_status': pair.status}

        fields = list(dict.fromkeys(('instance_name', 'instance_sha256', 'modality',
                   'formulation', 'status', 'solver_evidence', 'rational_verification',
                   'certified_gap_status', 'solver_numeric_lp_objective',
                   'model_complete', 'k_sha256', 'k_validated', 'physically_validated',
                   'physical_feasible_ub', 'solver_numeric_mip_incumbent',
                   'solver_numeric_mip_lb', 'wall_total_s', 'solver_runtime_s', 'work',
                   'pair_status')))

        def fake_manifest(root, cfg, instances, environment, commands, limitations,
                          generated, strict_generated=False):
            return {'artifact_schema': 'FC04-v1',
                    'code_files_sha256': source_inventory(root),
                    'input_files_sha256': input_inventory(root, instances),
                    'generated_files_sha256': generated_inventory(root, generated),
                    'generated_files': generated,
                    'instances': [{'nome': i.nome, 'instance_sha256': i.instance_sha256,
                                   'caminho': i.caminho} for i in instances],
                    'environment': environment, 'config': cfg.as_dict(),
                    'commands': commands, 'limitations': limitations}

        def fake_finalize(path, manifest):
            payload = c.canonical_bytes(manifest)
            Path(path).write_bytes(payload)
            Path(path).with_suffix('.sha256').write_text(
                hashlib.sha256(payload).hexdigest() + '  manifest.json\n')

        fake_core = types.SimpleNamespace(
            run_modality_a=lp_func, run_modality_b_comp=mip_func('comp_mip'),
            run_modality_b_fcc_k=mip_func('fcc_k'))
        fake_report = types.SimpleNamespace(
            _lp_row=fake_lp_row, _mip_row=fake_mip_row,
            RESULTS_FIELDS=fields, reproducibility_manifest=fake_manifest,
            finalize_manifest=fake_finalize)
        with tempfile.TemporaryDirectory(dir=runner.EXTENDED_ROOT,
                                         prefix='extended-test-parent-') as parent:
            path = Path(parent) / 'extended-synthetic'
            path.mkdir()
            body = c.canonical_bytes(p)
            (path / 'preregistration.json').write_bytes(body)
            (path / 'preregistration.sha256').write_text(
                hashlib.sha256(body).hexdigest() + '  preregistration.json\n')
            (path / 'eligibility_report.json').write_text(json.dumps({
                'status': 'ELIGIBLE', 'selected': selections, 'excluded': []}))
            with (path / 'plan.csv').open('w', encoding='utf-8', newline='') as file:
                w = csv.DictWriter(file, fieldnames=list(p['plan'][0]))
                w.writeheader()
                w.writerows(p['plan'])
            with (mock.patch.dict(sys.modules, {'fc_core': fake_core, 'fc_reporting': fake_report}),
                  mock.patch.object(runner, 'preflight_execute', return_value=(p, {MAIN: inst})),
                  mock.patch.object(verifier, '_source_integrity')):
                output = runner.execute(path, confirm_long_run=True, check_license=False)
            self.assertEqual(output['status'], 'PASS', output['problems'])
            results = c.csv_rows(path / 'results.csv')
            self.assertEqual(len(results), 9)
            self.assertEqual({r['formulation'] for r in results if r['modality'] == 'A'},
                             set(c.LP_ARMS))
            self.assertEqual({r['seed'] for r in results if r['modality'] == 'B'},
                             {'42', '43', '44'})
            self.assertTrue(all(r['rational_verification'] == 'NOT_CERTIFIED' for r in results))
            with mock.patch.object(verifier, '_source_integrity'):
                audit = verifier.verify(path, root=runner.ROOT)
            self.assertEqual(audit['status'], 'PASS', audit['problems'])


if __name__ == '__main__':
    unittest.main()
