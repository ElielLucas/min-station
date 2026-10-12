"""AS-05-DIAG: discriminação de integridade, custos, cortes e escolhas de grupos."""
from __future__ import annotations

import json
import tempfile
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "experiments/alternative-formulations")]

from as02_model_a import Instance, compile_a, compile_u
from as02_solve import solve_scipy
from as04_arms import canonical_k, k_digest
from as04_schema import SolverPolicy
from as05_diag_core import (
    _contrast, _diag_worker, _overlap_partition, _timed_k,
    _verify_model_identity, grouping_blocks, make_diagnostic_plan,
    run_diagnostic_stage, validate_diagnostic_plan, verify_diagnostic_stage,
)
from as02_model_a import prepare_K
from experiments.cuts.synthetic import make_Sec59

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / 'results/benchmark/as05-pilot-owner-exploratory-001'


def toy():
    S, T, V, adj, arcs, r, _ = make_Sec59(L=7)
    ins = Instance(tuple(V), tuple(S), tuple(T), tuple(arcs), int(r))
    return ins, SimpleNamespace(adj=adj, V=V, S=S, T=T, r=r, A_r=arcs,
                                instance_sha256='source-sha')


class Context:
    def __init__(self):
        self.phases = []
    def phase(self, key):
        self.phases.append(key)
    def require_remaining(self):
        return 100


class TestAS05DiagnosticCuts(unittest.TestCase):
    def test_k_cached_has_exact_legacy_hash(self):
        ins, loaded = toy()
        cuts, evidence = _timed_k(ins, loaded, Context())
        old = canonical_k(ins, prepare_K(ins, loaded.adj, ins.r))
        self.assertEqual(cuts, old)
        self.assertEqual(evidence['k_sha256'], k_digest(ins, old))
        self.assertTrue(evidence['k_validated'])
        self.assertEqual(evidence['counts']['unique'], len(cuts))

    def test_cut_profile_has_all_families(self):
        ins, loaded = toy()
        ctx = Context()
        _, profile = _timed_k(ins, loaded, ctx)
        for key in ('neighborhoods_s', 'c1_s', 'c2_s', 'c4_dm_s',
                    'canonicalize_s', 'validation_cached_s'):
            self.assertIn(key, profile['phase_wall_s'])
            self.assertGreaterEqual(profile['phase_wall_s'][key], 0)
        self.assertIn('k_validation_cached', ctx.phases)

    def test_invalid_cut_still_rejected(self):
        ins, loaded = toy()
        with patch('as05_diag_core.generate_C1', return_value=[frozenset({'s1'})]), \
             patch('as05_diag_core.generate_C2', return_value=[]), \
             patch('as05_diag_core.generate_C4_DM', return_value=[]):
            # A validade não é desativada para ganhar desempenho.
            with self.assertRaises(Exception):
                _timed_k(ins, loaded, Context())

    def test_u_never_calls_k(self):
        ins, loaded = toy()
        ctx = Context()
        mock_solver = {'status':'OPTIMAL_NUMERIC', 'lp_opt_value': 2.0,
                       'solver_runtime_s': .01, 'solver_version': 'fake'}
        solver = {'seed': 42, 'threads': 1, 'memory_limit_bytes': None}
        with patch('as05_diag_core._load_timed', return_value=(loaded, 0.1, 0.1)), \
             patch('as05_diag_core._timed_k', side_effect=AssertionError('U pagou K')), \
             patch('as05_diag_core._optimize', return_value=mock_solver):
            row = _diag_worker(ctx, {'nome':'toy'}, str(ROOT), 'lp', 'U', None,
                               solver, 90, 1_000_000, 42)
        self.assertEqual(row['status'], 'OPTIMAL_NUMERIC')
        self.assertIsNone(row['reference_k_sha256'])
        self.assertFalse(row['k_prepared_for_this_arm'])
        self.assertNotIn('k_preparation', ctx.phases)

    def test_u_k_runs_cut_validation(self):
        _, loaded = toy()
        ctx = Context()
        solver = {'seed': 42, 'threads': 1, 'memory_limit_bytes': None}
        with patch('as05_diag_core._load_timed', return_value=(loaded, .1, .1)), \
             patch('as05_diag_core._optimize', return_value={
                 'status':'OPTIMAL_NUMERIC', 'lp_opt_value':3.0,
                 'solver_runtime_s': .01}):
            row = _diag_worker(ctx, {'nome':'toy'}, str(ROOT), 'lp', 'U_K', None,
                               solver, 90, 1_000_000, 42)
        self.assertTrue(row['k_prepared_for_this_arm'])
        self.assertTrue(row['k_validated'])
        self.assertIsNotNone(row['reference_k_sha256'])
        self.assertIn('k_validation_cached', ctx.phases)


class TestAS05DiagnosticGroupings(unittest.TestCase):
    def test_preselected_policies_are_deterministic(self):
        ins, _ = toy()
        for policy in ('balanced', 'reachability_degree', 'reachability_overlap'):
            first = grouping_blocks(ins, policy, 42)
            again = grouping_blocks(Instance(tuple(reversed(ins.V)),
                                              tuple(reversed(ins.S)),
                                              tuple(reversed(ins.T)),
                                              tuple(reversed(ins.A_r)), ins.r), policy, 42)
            self.assertEqual(first, again)
            self.assertEqual(set(first[0][0] + first[0][1]), set(ins.S))

    def test_overlap_no_empty_or_duplicate(self):
        ins, _ = toy()
        blocks = _overlap_partition(ins, 42)
        self.assertEqual(len(blocks), 2)
        self.assertTrue(all(blocks))
        self.assertEqual(set(blocks[0]).intersection(blocks[1]), set())

    def test_overlap_rejected_unknown_policy(self):
        ins, _ = toy()
        with self.assertRaises(ValueError):
            grouping_blocks(ins, 'lp-selected-best', 42)

    def test_partition_compiles_and_lp_dominates_u(self):
        ins, _ = toy()
        u = solve_scipy(compile_u(ins, relax=True))
        for policy in ('balanced', 'reachability_degree', 'reachability_overlap'):
            blocks, _ = grouping_blocks(ins, policy, 42)
            a = solve_scipy(compile_a(ins, blocks, relax=True))
            self.assertEqual(a.status, 'OPTIMAL')
            self.assertGreaterEqual(a.objective + 1e-6, u.objective)


class TestAS05DiagnosticIntegrity(unittest.TestCase):
    def test_plan_is_bound_to_original_report(self):
        plan = make_diagnostic_plan(ROOT, PILOT)
        self.assertEqual(plan, validate_diagnostic_plan(plan, ROOT))
        self.assertEqual(len(plan['cases']['censored']), 2)
        self.assertEqual(len(plan['cases']['grouping']), 4)
        self.assertEqual(plan['scientific_gate'], 'PENDING')
        changed = json.loads(json.dumps(plan))
        changed['budgets_seconds_per_arm']['censored'] += 1
        with self.assertRaises(ValueError):
            validate_diagnostic_plan(changed, ROOT)

    def test_censored_is_retained_without_forged_bound(self):
        policy = SolverPolicy(seed=42, threads=1, budget_s=90)
        left = {'case_name': 'toy', 'arm_id': 'U_K', 'status': 'OPTIMAL_NUMERIC',
                'model_complete': True, 'instance_sha256': 'inst',
                'structural_sha256': 'struct', 'reference_k_sha256': 'cut',
                'applied_k_sha256': 'cut', 'k_validated': True,
                'wall_total_s': 3., 'wall_phases_s': {}, 'lp_opt_value': 2.}
        right = {**left, 'arm_id': 'A2_K', 'status': 'TIMEOUT_SOLVER',
                 'model_complete': False, 'lp_opt_value': None}
        result = _contrast(left, right, policy, effect='A_EFFECT')
        self.assertNotEqual(result['status'], 'MATCHED_COMPLETE')
        self.assertIsNone(result['lp_delta'])

    def test_u_reference_reused_but_not_charged(self):
        policy = SolverPolicy(seed=42, threads=1, budget_s=90)
        left = {'case_name': 'toy', 'arm_id': 'U', 'status': 'OPTIMAL_NUMERIC',
                'model_complete': True, 'instance_sha256': 'inst',
                'structural_sha256': 'struct', 'reference_k_sha256': None,
                'applied_k_sha256': None, 'k_validated': False,
                'wall_total_s': 1., 'wall_phases_s': {}, 'lp_opt_value': 1.}
        right = {**left, 'arm_id': 'U_K', 'reference_k_sha256': 'cut',
                 'applied_k_sha256': 'cut', 'k_validated': True,
                 'wall_total_s': 2., 'lp_opt_value': 2.}
        result = _contrast(left, right, policy, effect='K_EFFECT')
        self.assertEqual(result['status'], 'MATCHED_COMPLETE')
        self.assertEqual(result['lp_delta'], 1)

    def test_different_k_hash_refuses_pair(self):
        policy = SolverPolicy(seed=42, threads=1, budget_s=90)
        left = {'case_name': 'toy', 'arm_id': 'U_K', 'status': 'OPTIMAL_NUMERIC',
                'model_complete': True, 'instance_sha256': 'inst',
                'structural_sha256': 'struct', 'reference_k_sha256': 'cut-a',
                'applied_k_sha256': 'cut-a', 'k_validated': True,
                'wall_total_s': 1., 'wall_phases_s': {}, 'lp_opt_value': 2.}
        right = {**left, 'arm_id': 'A2_K', 'reference_k_sha256': 'cut-b',
                 'applied_k_sha256': 'cut-b'}
        self.assertEqual(_contrast(left, right, policy, effect='A_EFFECT')['status'],
                         'INTEGRITY_ERROR')
        with self.assertRaises(ValueError):
            _verify_model_identity([left, right])

    def test_manifest_detects_result_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            plan = {'schema': 'test'}
            report = {'schema':'AS05-DIAG-RESULT-v1', 'stage':'cuts',
                      'scientific_gate':'PENDING', 'scientific_promotion':'NOT_AUTHORIZED',
                      'plan_sha256':'dummy', 'cases':[{'name':'c'}], 'expected_cases':['c']}
            (folder/'plan.json').write_text(json.dumps(plan))
            (folder/'report.json').write_text(json.dumps(report))
            (folder/'arms.csv').write_text('status\nTIMEOUT_PREPARATION\n')
            from as05_protocol import sha256_file
            from as05_diag_core import _write_json
            import hashlib
            report['plan_sha256'] = hashlib.sha256((folder/'plan.json').read_bytes()).hexdigest()
            (folder/'report.json').write_text(json.dumps(report))
            _write_json(folder/'manifest.json', {'schema':'AS05-DIAG-INTEGRITY-v1',
                'files': {n: sha256_file(folder/n) for n in ('plan.json', 'report.json', 'arms.csv')}})
            with self.assertRaises(ValueError):
                verify_diagnostic_stage(folder)
            report['scientific_promotion'] = 'GO'
            (folder/'report.json').write_text(json.dumps(report))
            with self.assertRaises(ValueError):
                verify_diagnostic_stage(folder)

    def test_previously_recorded_cases_never_modified(self):
        plan = make_diagnostic_plan(ROOT, PILOT)
        self.assertTrue(plan['censored_preserved_in_parent'])
        self.assertEqual(set(plan['cases']['censored']) & set(plan['cases']['grouping']), set())


if __name__ == '__main__':
    unittest.main()


class TestAS05DiagnosticPipeline(unittest.TestCase):
    def _fake_runner(self, row, *, kind, arm, group_policy, **_):
        case = row['nome']
        basis = {'case_name': case, 'kind': kind, 'arm_id': arm,
                 'grouping_policy': group_policy, 'status': 'OPTIMAL_NUMERIC',
                 'instance_sha256': 'source-'+case, 'structural_sha256': 'graph-'+case,
                 'reference_k_sha256': None if arm == 'U' else 'valid-k-'+case,
                 'applied_k_sha256': None if arm == 'U' else 'valid-k-'+case,
                 'model_complete': True, 'k_validated': arm != 'U',
                 'k_prepared_for_this_arm': arm != 'U', 'wall_total_s': 2.,
                 'wall_phases_s': {'k_c2': 0.4} if arm != 'U' else {'model_build':0.4},
                 'solver_runtime_s': 1., 'lp_opt_value': 1.0 if arm == 'U' else 2.0,
                 'partition_sha256': ('partition-'+str(group_policy)) if arm == 'A2_K' else None}
        if kind == 'cuts':
            return {'case_name':case, 'kind':kind,'arm_id':None,
                    'grouping_policy':None,'status':'PROFILED',
                    'wall_total_s': 3., 'wall_phases_s':{'k_c2':1.},
                    'cut_profile': {'counts':{'unique':10},'k_sha256':'hash'}}
        return basis

    def test_stage_files_verify_and_is_append_only(self):
        plan_path = ROOT/'results/benchmark/as05-diagnostic-plan-v1.json'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'cuts'
            path = run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                        stage='cuts', output_dir=output,
                                        run_one=self._fake_runner)
            self.assertTrue(path.is_file())
            result = verify_diagnostic_stage(output)
            self.assertEqual(len(result['cases']), 2)
            self.assertEqual(len(list((output/'checkpoints').rglob('arm-*.json'))), 2)
            with self.assertRaises(FileExistsError):
                run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                     stage='cuts', output_dir=output,
                                     run_one=self._fake_runner)

    def test_censored_and_grouping_full_pipeline(self):
        plan_path = ROOT/'results/benchmark/as05-diagnostic-plan-v1.json'
        with tempfile.TemporaryDirectory() as tmp:
            for stage, n_cases, n_arms in [('censored', 2, 3), ('grouping', 4, 4)]:
                output = Path(tmp)/stage
                run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                     stage=stage, output_dir=output,
                                     run_one=self._fake_runner)
                report = verify_diagnostic_stage(output)
                self.assertEqual(len(report['cases']), n_cases)
                self.assertTrue(all(len(c['runs'])==n_arms for c in report['cases']))
                self.assertTrue(all(c['contrasts'] for c in report['cases']))
                self.assertEqual(report['scientific_gate'], 'PENDING')

    def test_resume_uses_existing_checkpoints_without_repeat(self):
        plan_path = ROOT/'results/benchmark/as05-diagnostic-plan-v1.json'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'cuts'
            output.mkdir()
            (output/'plan.json').write_bytes(plan_path.read_bytes())
            from as05_diag_core import _read_or_run_checkpoint
            item = make_diagnostic_plan(ROOT, PILOT)['cases']['cuts'][0]
            item_run = self._fake_runner({'nome':item}, kind='cuts', arm=None, group_policy=None)
            _read_or_run_checkpoint(output, item, 0, ('cuts',None,None), lambda:item_run, resume=False)
            calls=[]
            def runner(row, **kwargs):
                calls.append(row['nome'])
                return self._fake_runner(row, **kwargs)
            run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                 stage='cuts', output_dir=output, run_one=runner, resume=True)
            self.assertEqual(len(calls), 1)
            self.assertEqual(len(verify_diagnostic_stage(output)['cases']), 2)

    def test_corrupted_checkpoint_blocks_resume(self):
        from as05_diag_core import _read_or_run_checkpoint
        plan_path = ROOT/'results/benchmark/as05-diagnostic-plan-v1.json'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'cuts'
            output.mkdir()
            (output/'plan.json').write_bytes(plan_path.read_bytes())
            item = make_diagnostic_plan(ROOT, PILOT)['cases']['cuts'][0]
            _read_or_run_checkpoint(output, item, 0, ('cuts', None, None),
                                    lambda:self._fake_runner({'nome':item}, kind='cuts', arm=None,
                                                             group_policy=None), resume=False)
            checkpoint = output/'checkpoints'/item/'arm-00.json'
            checkpoint.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'adulterado'):
                run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                     stage='cuts', output_dir=output,
                                     run_one=self._fake_runner, resume=True)


class TestAS05DiagnosticAnalysis(unittest.TestCase):
    def test_complete_analysis_exploratory_no_promotion(self):
        from as05_diag_analysis import build_analysis
        suite = TestAS05DiagnosticPipeline()
        plan_path = ROOT/'results/benchmark/as05-diagnostic-plan-v1.json'
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            stages = {}
            for stage in ('cuts', 'censored', 'grouping'):
                stages[stage] = folder/stage
                run_diagnostic_stage(root=ROOT, plan_path=plan_path,
                                     stage=stage, output_dir=stages[stage],
                                     run_one=suite._fake_runner)
            outfile = build_analysis(root=ROOT, plan_path=plan_path,
                                     stage_folders=stages, output_dir=folder/'analysis')
            report = json.loads(outfile.read_text(encoding='utf-8'))
            self.assertEqual(report['scientific_promotion'], 'NOT_AUTHORIZED')
            self.assertEqual(len(report['grouping']), 12)
            self.assertEqual(len(report['cuts']), 2)
            self.assertEqual(len(report['censored_retries']), 2)
            self.assertIn(report['recommendation'],
                          ('A2_NO_MATERIAL_LP_ADVANTAGE_IN_DEVELOPMENT',
                           'FOLLOW_UP_REPLICATION_REQUIRED', 'INVESTIGATE_FURTHER'))
            with self.assertRaises(FileExistsError):
                build_analysis(root=ROOT, plan_path=plan_path, stage_folders=stages,
                               output_dir=folder/'analysis')

    def test_budget_timeout_in_k_stage_is_preparation(self):
        from fc_budget import _timeout_status
        self.assertEqual(_timeout_status('k_c2'), 'TIMEOUT_PREPARATION')
        self.assertEqual(_timeout_status('k_validation_cached'), 'TIMEOUT_PREPARATION')
        self.assertEqual(_timeout_status('solve'), 'TIMEOUT_SOLVER')
