"""FC-05: testes independentes de prontidão, censura e auditoria de artefatos.

Não exigem Gurobi. Não abrem nem alteram dados históricos do repositório.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from fc_integrity import dump_json_bytes, sha256_file  # noqa: E402
from verify_comparison_pilot import (  # noqa: E402
    NOT_READY, READY, evaluate, gate_from_rows, publish_candidate,
)

HASH_INSTANCE = hashlib.sha256(b'fixture-instancia').hexdigest()
HASH_K = hashlib.sha256(b'fixture-K').hexdigest()
INSTANCES = ('hb-q4-ndir2-p1-k1-L2.txt', 'bp-nao-q2-B2-s0.txt')


def _row(name, arm, value, *, ub=2):
    is_lp = arm.startswith('lp_')
    return {
        'instance_name': name, 'instance_sha256': HASH_INSTANCE,
        'modality': 'A' if is_lp else 'B',
        'formulation': ('baseline' if arm in ('lp_base', 'lp_comp') else
                        'fcc_k' if arm == 'lp_fcc_k' else arm),
        'observations': f'{arm}; K=1' if is_lp else '',
        'status': 'OPTIMAL', 'solver_evidence': 'SOLVER_NUMERIC_OPTIMAL',
        'solver_numeric_status': 'OPTIMAL', 'model_complete': 'True',
        'evidence_schema': 'FC03-v1',
        'wall_total_s': '1.5', 'solver_runtime_s': '0.5', 'work': '0.1',
        'k_sha256': '' if arm == 'lp_base' else HASH_K,
        'n_K': '0' if arm == 'lp_base' else '1',
        'n_K_added': '1' if not is_lp else '',
        'k_validated': 'True' if not is_lp else '',
        'pair_status': 'PAIR_VALID' if not is_lp else '',
        'comparison_role': 'primary' if not is_lp else 'lp_control',
        'pair_instance_sha256': HASH_INSTANCE if not is_lp else '',
        'pair_k_sha256': HASH_K if not is_lp else '',
        'physically_validated': 'True' if not is_lp else '',
        'physical_feasible_ub': str(ub) if not is_lp else '',
        'physical_ub_provenance': 'INDEPENDENT_VALIDATOR:installed_cardinality' if not is_lp else '',
        'objective_primal': str(ub) if not is_lp else '',
        'solver_numeric_mip_incumbent': str(ub) if not is_lp else '',
        'solver_numeric_mip_lb': str(ub) if not is_lp else '',
        'solver_numeric_lp_objective': str(value) if is_lp else '',
        'rational_verification': 'NOT_CERTIFIED',
        'rational_verified_lb_exact': '', 'certified_gap_abs_exact': '',
        'certified_gap_rel_exact': '', 'certified_gap_status': 'INCONCLUSIVE',
    }


def _fixture():
    manifest = {
        'tier': 'pilot', 'modalities': ['A', 'B'],
        'formulations': ['comp_mip', 'fcc_k'],
        'config': {'lp_time_limit_s': 60, 'time_limit_s': 120},
        'instances': [{'nome': n, 'instance_sha256': HASH_INSTANCE,
                       'caminho': f'instances/{n}'} for n in INSTANCES],
        'errors': [],
    }
    rows = []
    for name, ub in zip(INSTANCES, (2, 7)):
        for arm, value in [('lp_base', 0.3), ('lp_comp', ub - 1),
                           ('lp_fcc_k', ub), ('comp_mip', ub), ('fcc_k', ub)]:
            rows.append(_row(name, arm, value, ub=ub))
    return rows, manifest


def _publish_temp(root, rows, manifest):
    root = Path(root)
    path = root / 'results/formulation-comparison/pilot-test'
    path.mkdir(parents=True)
    code = root / 'experiments/formulation-comparison/fake.py'
    code.parent.mkdir(parents=True)
    code.write_text('print("fixture")\n', encoding='utf-8')
    inputs = {}
    for name in INSTANCES:
        instance_path = root / 'instances' / name
        instance_path.parent.mkdir(parents=True, exist_ok=True)
        instance_path.write_bytes(b'fixture-instancia')
        inputs[instance_path.relative_to(root).as_posix()] = sha256_file(instance_path)
    results = path / 'results.csv'
    with results.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (path / 'run.log').write_text('fixture\n', encoding='utf-8')
    publish_candidate(path, rows, manifest)
    produced = sorted(p.relative_to(root).as_posix() for p in path.rglob('*') if p.is_file())
    stored = {
        **manifest,
        'artifact_schema': 'FC04-v1',
        'code_files_sha256': {code.relative_to(root).as_posix(): sha256_file(code)},
        'input_files_sha256': inputs,
        'generated_files_sha256': {name: sha256_file(root / name) for name in produced},
        'generated_files': produced,
    }
    manifest_bytes = dump_json_bytes(stored)
    (path / 'manifest.json').write_bytes(manifest_bytes)
    (path / 'manifest.sha256').write_text(
        f'{hashlib.sha256(manifest_bytes).hexdigest()}  manifest.json\n', encoding='ascii')
    return path


class PilotGateTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.manifest = _fixture()

    def check_rejected(self, code):
        result = gate_from_rows(self.rows, self.manifest)
        self.assertEqual(result['candidate_gate'], NOT_READY)
        self.assertIn(code, '\n'.join(str(x) for x in result['instances'] + result['global_reasons']))

    def test_pilot01_pilot04_ready_requires_all_five_arms_per_instance(self):
        result = gate_from_rows(self.rows, self.manifest)
        self.assertEqual(result['candidate_gate'], READY)
        self.assertEqual(result['summary']['selected_total'], 2)
        self.assertEqual(result['summary']['primary_pair_valid_total'], 2)
        self.assertFalse(result['automatic_extended_execution'])
        self.assertIn('not_superiority', result['interpretation'])

    def test_pilot01_must_use_two_preregistered_instances(self):
        self.rows = [r for r in self.rows if r['instance_name'] == INSTANCES[0]]
        self.manifest['instances'] = self.manifest['instances'][:1]
        self.check_rejected('PILOT_SELECTION_DIFFERS_FROM_PREREGISTRATION')

    def test_pilot01_budget_cannot_be_extended_to_one_hour(self):
        self.manifest['config']['time_limit_s'] = 3600
        self.check_rejected('PILOT_BUDGET_ABOVE_PREREGISTERED_CAP')

    def test_pilot01_missing_lp_modality_is_not_ready(self):
        self.manifest['modalities'] = ['B']
        self.check_rejected('INCOMPLETE_MODALITIES')

    def test_pilot01_missing_primary_mip_arm_is_not_ready(self):
        self.manifest['formulations'] = ['fcc_k']
        self.check_rejected('MISSING_PRIMARY_MIP_ARMS')

    def test_pilot01_budget_violation_rejected(self):
        self.rows[0]['wall_total_s'] = '65'
        self.check_rejected('GLOBAL_BUDGET_EXCEEDED')

    def test_pilot01_missing_solver_work_rejected(self):
        self.rows[0]['work'] = ''
        self.check_rejected('MISSING_COST_MEASUREMENT')

    def test_pilot01_invalid_solver_runtime_rejected(self):
        self.rows[0]['solver_runtime_s'] = '20'
        self.check_rejected('SOLVER_RUNTIME_GREATER_THAN_WALL')

    def test_pilot02_selection_denominator_kept_if_no_rows(self):
        self.rows = [r for r in self.rows if r['instance_name'] == INSTANCES[0]]
        result = gate_from_rows(self.rows, self.manifest)
        self.assertEqual(result['summary']['selected_total'], 2)
        self.assertEqual(result['summary']['not_ready_total'], 1)
        self.assertEqual(result['summary']['censored_or_missing_total'], 1)

    def test_pilot03_cap_exceeded_censored_in_denominator(self):
        self.rows[2]['status'] = 'CAP_EXCEEDED'
        self.rows[2]['solver_evidence'] = 'NOT_MEASURED'
        self.rows[2]['model_complete'] = 'False'
        self.check_rejected('CENSORED_OR_NOT_OPTIMAL')
        self.assertEqual(gate_from_rows(self.rows, self.manifest)
                         ['summary']['censored_or_missing_total'], 1)

    def test_pilot03_single_mip_timeout_is_censored(self):
        self.rows[3]['status'] = 'TIMEOUT_PREPARATION'
        self.check_rejected('CENSORED_OR_NOT_OPTIMAL')

    def test_pilot03_mismatched_k_sha_denies_pair(self):
        self.rows[4]['k_sha256'] = '0' * 64
        self.check_rejected('K_HASH_MISMATCH')

    def test_pilot03_mismatched_k_count_denies_pair(self):
        self.rows[4]['n_K'] = '2'
        self.check_rejected('K_COUNT_MISMATCH')

    def test_pilot03_k_not_fully_applied_denies_pair(self):
        self.rows[4]['n_K_added'] = '0'
        self.check_rejected('K_NOT_FULLY_APPLIED')

    def test_pilot03_bad_pair_flag_denies_pair(self):
        self.rows[4]['pair_status'] = 'PAIR_NOT_AVAILABLE'
        self.check_rejected('PAIR_NOT_VALID')

    def test_pilot03_bad_physical_incumbent_denies_pair(self):
        self.rows[4]['physically_validated'] = 'False'
        self.check_rejected('INVALID_PHYSICAL_WITNESS')

    def test_pilot03_pair_instance_hash_mismatch_denies_pair(self):
        self.rows[4]['pair_instance_sha256'] = 'f' * 64
        self.check_rejected('PAIR_IDENTITY_MISMATCH')

    def test_pilot05_solver_optimal_is_not_rational_certification(self):
        self.rows[4]['certified_gap_status'] = 'CERTIFIED'
        self.check_rejected('UNSUPPORTED_RATIONAL_CERTIFICATION')

    def test_pilot05_absent_rational_proof_is_explicit(self):
        self.rows[4]['rational_verification'] = 'RATIONAL_VERIFIED'
        self.check_rejected('INVALID_RATIONAL_EVIDENCE')

    def test_pilot05_numeric_lp_exceeds_physical_ub(self):
        self.rows[2]['solver_numeric_lp_objective'] = '99.0'
        self.check_rejected('LP_EXCEEDS_PHYSICAL_UB')

    def test_pilot06_duplicate_arm_and_unknown_instance_not_silent(self):
        self.rows.append(deepcopy(self.rows[4]))
        self.rows.append(_row('unexpected', 'fcc_k', 2))
        result = gate_from_rows(self.rows, self.manifest)
        self.assertEqual(result['candidate_gate'], NOT_READY)
        self.assertIn('ARM_COUNT', str(result))
        self.assertIn('UNEXPECTED_CSV_INSTANCES', str(result))

    def test_pilot06_optional_ablation_is_not_primary(self):
        self.manifest['formulations'].append('baseline')
        for name in INSTANCES:
            row = _row(name, 'baseline', 2, ub=2)
            row['comparison_role'] = 'ablation_no_k'
            row['pair_status'] = 'ABLATION_ONLY'
            self.rows.append(row)
        self.assertEqual(gate_from_rows(self.rows, self.manifest)['candidate_gate'], READY)

    def test_pilot06_optional_ablation_missing_row_rejected(self):
        self.manifest['formulations'].append('baseline')
        self.check_rejected('ABLATION_ARM_COUNT')


class FinalAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.rows, self.manifest = _fixture()
        self.run_dir = _publish_temp(self.root, self.rows, self.manifest)

    def test_pilot02_pilot04_full_sha_roundtrip_and_ready(self):
        outcome = evaluate(self.run_dir, root=self.root)
        self.assertEqual(outcome['status'], READY, outcome)
        self.assertEqual(outcome['artifact_audit'], 'PASS')
        self.assertFalse(outcome['rational_certification_claimed'])
        self.assertFalse(outcome['extended_run_triggered'])

    def test_pilot02_modified_csv_denies_readiness(self):
        with (self.run_dir / 'results.csv').open('a', encoding='utf-8') as f:
            f.write('\n')
        outcome = evaluate(self.run_dir, root=self.root)
        self.assertEqual(outcome['status'], NOT_READY)
        self.assertIn('HASH_MISMATCH', str(outcome))

    def test_pilot02_modified_source_denies_readiness(self):
        path = self.root / 'experiments/formulation-comparison/fake.py'
        path.write_text('changed\n', encoding='utf-8')
        outcome = evaluate(self.run_dir, root=self.root)
        self.assertEqual(outcome['status'], NOT_READY)
        self.assertIn('HASH_MISMATCH', str(outcome))

    def test_pilot02_modified_candidate_denies_readiness(self):
        path = self.run_dir / 'pilot_gate.json'
        gate = json.loads(path.read_text(encoding='utf-8'))
        gate['candidate_gate'] = NOT_READY
        path.write_text(json.dumps(gate), encoding='utf-8')
        outcome = evaluate(self.run_dir, root=self.root)
        self.assertEqual(outcome['status'], NOT_READY)
        self.assertIn('PUBLISHED_CANDIDATE_DOES_NOT_MATCH_CSV_AND_MANIFEST', outcome['problems'])

    def test_pilot03_no_manifest_denies_readiness(self):
        (self.run_dir / 'manifest.sha256').unlink()
        self.assertEqual(evaluate(self.run_dir, root=self.root)['status'], NOT_READY)

    def test_pilot02_publication_never_overwrites(self):
        with self.assertRaises(FileExistsError):
            publish_candidate(self.run_dir, self.rows, self.manifest)


if __name__ == '__main__':
    unittest.main()
