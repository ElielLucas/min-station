"""Testes AS04 derivados dos ACs: integridade, censura, K e validação física."""
from __future__ import annotations

import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from as04_schema import ArmResult, SolverPolicy, digest
from as04_compare import assess_pair, compare_case
from as04_reporting import publish_run, verify_run, flatten_arm
from as04_runner import validate_physical_ub, run_arm
from as04_arms import Instance, compile_arm, canonical_k, k_digest
from experiments.cuts.synthetic import make_Direct0, make_Sec59


POLICY = SolverPolicy(seed=11, threads=1, budget_s=5)
KREF = digest((('x',),))


def row(arm='U_K', *, mode='LP', status='OPTIMAL_NUMERIC', **fields):
    r = dict(case_name='toy', arm_id=arm, mode=mode, status=status,
             instance_sha256='case-sha', structural_sha256='ar-sha',
             reference_k_sha256=KREF,
             applied_k_sha256=None if arm == 'U' else KREF,
             k_validated=True, solver_policy_sha256=POLICY.sha256,
             solver_policy=asdict(POLICY), model_complete=True,
             lp_opt_value=2.0 if mode == 'LP' else None,
             wall_total_s=3.0,
             wall_phases_s={'preparation': .5, 'k_preparation': .3,
                            'model_build': .4, 'solve': 1.0, 'validation': .1},
             mip_numeric_bound=1.0 if mode == 'MIP' else None,
             mip_numeric_incumbent=2.0 if mode == 'MIP' else None,
             physical_validated_ub=2 if mode == 'MIP' else None,
             installed=('a', 'b') if mode == 'MIP' else None)
    r.update(fields)
    return ArmResult(**r)


class TestAS04Schema(unittest.TestCase):
    def test_as04_01_fingerprint_change_refuses_pair(self):
        self.assertEqual(assess_pair(row('U'), row('U_K', instance_sha256='other'),
                                     effect='K_EFFECT').status, 'INTEGRITY_ERROR')

    def test_as04_01_ar_hash_change_refuses_pair(self):
        self.assertEqual(assess_pair(row('U'), row('U_K', structural_sha256='other'),
                                     effect='K_EFFECT').status, 'INTEGRITY_ERROR')

    def test_as04_01_solver_seed_difference_refuses_pair(self):
        other = SolverPolicy(seed=99, budget_s=5)
        self.assertEqual(assess_pair(row('U'), row('U_K', solver_policy_sha256=other.sha256,
                                     solver_policy=asdict(other)), effect='K_EFFECT').status,
                         'INTEGRITY_ERROR')

    def test_as04_01_policy_payload_mutation_detected(self):
        self.assertEqual(assess_pair(row('U'), row('U_K', solver_policy={'seed': 99}),
                                     effect='K_EFFECT').status, 'INTEGRITY_ERROR')

    def test_as04_02_unequal_k_rejects_two_plus_k_arms(self):
        self.assertEqual(assess_pair(row('U_K'), row('A2_K', applied_k_sha256='tampered'),
                                     effect='A_EFFECT').status, 'INTEGRITY_ERROR')

    def test_as04_02_ablation_is_without_k(self):
        with self.assertRaises(ValueError):
            row('U', applied_k_sha256=KREF)
        self.assertEqual(assess_pair(row('U'), row('U_K'), effect='K_EFFECT').status,
                         'MATCHED_COMPLETE')

    def test_as04_02_invalid_k_is_not_comparable(self):
        self.assertEqual(assess_pair(row('U'), row('U_K', k_validated=False,
                                                     model_complete=False),
                                     effect='K_EFFECT').status, 'NOT_COMPARABLE')

    def test_as04_03_three_effects_reported_separately(self):
        data = compare_case([row('U', lp_opt_value=1), row('U_K', lp_opt_value=2),
                             row('A2_K', lp_opt_value=3), row('A4_K', lp_opt_value=3)])
        self.assertEqual([x['effect'] for x in data['pairs']],
                         ['K_EFFECT', 'A_EFFECT', 'REFINEMENT_EFFECT'])
        self.assertEqual([x['lp_delta'] for x in data['pairs']], [1, 1, 0])

    def test_as04_03_nonmatched_modes_forbidden(self):
        self.assertEqual(assess_pair(row('U'), row('U_K', mode='MIP'),
                                     effect='K_EFFECT').status, 'INTEGRITY_ERROR')

    def test_as04_04_timeout_stays_in_denominator(self):
        censored = row('A2_K', status='TIMEOUT_SOLVER', model_complete=False)
        self.assertIsNone(censored.lp_opt_value)
        data = compare_case([row('U_K'), censored])
        self.assertEqual(data['pairs'][1]['status'], 'NOT_COMPARABLE')
        self.assertEqual(data['observed_arm_count'], 2)

    def test_as04_04_memory_failure_no_objective(self):
        invalid = row('U_K', status='MEMORY_LIMIT', model_complete=False, lp_opt_value=88)
        self.assertIsNone(invalid.lp_opt_value)
        self.assertIsNone(invalid.mip_numeric_bound)

    def test_as04_05_lp_timeout_primal_not_global_lb(self):
        invalid = row('U_K', status='TIME_LIMIT', lp_opt_value=7.0, lp_dual_bound=9.0)
        self.assertIsNone(invalid.lp_opt_value)
        self.assertIsNone(invalid.lp_dual_bound)

    def test_as04_05_lp_optimal_numerical_only(self):
        result = row('U_K')
        self.assertEqual(result.lp_opt_value, 2)
        self.assertEqual(result.evidence_class, 'SOLVER_NUMERIC_LP_OPTIMAL')
        self.assertIsNone(result.rational_verified_lb_exact)

    def test_as04_06_invalid_ub_requires_matching_installation(self):
        with self.assertRaises(ValueError):
            row('U_K', mode='MIP', physical_validated_ub=5)

    def test_as04_06_actual_independent_oracle_rejects_invalid(self):
        S, T, V, adj, _ar, r, _meta = make_Sec59(L=7)
        inst = SimpleNamespace(S=S, T=T, V=V, adj=adj, r=r)
        self.assertIsNone(validate_physical_ub(inst, ('w1',)))
        self.assertEqual(validate_physical_ub(inst, ('w1','w2','w3','w4','w5','w6','w7')), 7)

    def test_as04_07_phase_fields_are_not_imputed(self):
        result = row('U_K', wall_phases_s={'preparation': .6,
                                            'k_preparation': .5, 'model_build': .4,
                                            'solve': 1., 'validation': .2,
                                            'supervisor_shutdown': .3},
                     wall_total_s=4.5)
        flat = flatten_arm(result.to_dict())
        self.assertEqual(flat['wall_input_reachability_s'], .6)
        self.assertEqual(flat['wall_k_preparation_s'], .5)
        self.assertEqual(flat['wall_total_s'], 4.5)
        self.assertIsNone(flat['presolve_wall_s'])
        self.assertGreater(flat['wall_total_s'], sum(result.wall_phases_s.values()))

    def test_as04_08_numeric_physical_and_rational_separate(self):
        result = row('U_K', mode='MIP')
        payload = result.to_dict()
        self.assertEqual(payload['mip_numeric_bound'], 1)
        self.assertEqual(payload['physical_validated_ub'], 2)
        self.assertEqual(payload['rational_certification'], 'NOT_CERTIFIED')
        self.assertIsNone(payload['rational_verified_lb_exact'])

    def test_as04_08_fake_rational_proof_rejected(self):
        with self.assertRaises(ValueError):
            row('U_K', rational_verified_lb_exact='3/2')

    def test_as04_09_restricted_fcc_not_complete_lb(self):
        model = row('FCC_K', mode='LP', model_complete=False, lp_opt_value=999)
        self.assertIsNone(model.lp_opt_value)
        self.assertEqual(model.comparison_role, 'physical_model')

    def test_as04_09_core_not_physical_solution(self):
        with self.assertRaises(ValueError):
            row('CORE_IP', mode='MIP')
        result = row('CORE_IP', mode='LP', model_complete=False, status='NOT_AUTHORIZED',
                     applied_k_sha256=None)
        self.assertEqual(result.comparison_role, 'lower_bound_control_only')

    def test_as04_02_canonical_cuts_hash_independent_of_order(self):
        inst = Instance(('a','b','c'), ('a',), ('c',), (('a','b'),('b','c')), 1)
        self.assertEqual(k_digest(inst, [('b','a'), ('c',)]),
                         k_digest(inst, [('c',), ('a','b'), ('a','b')]))
        with self.assertRaises(ValueError):
            canonical_k(inst, [('a', 'a')])

    def test_as04_03_reuses_as02_model_not_reimplementation(self):
        inst = Instance.from_synthetic(make_Direct0())
        a, _ = compile_arm('U', inst, (), mode='LP')
        b, _ = compile_arm('U_K', inst, (), mode='LP')
        self.assertEqual(len(a.variables), len(b.variables))
        self.assertFalse(any(eq.name.startswith('A6') for eq in a.equations))
        with self.assertRaises(NotImplementedError):
            compile_arm('FCC_K', inst, (), mode='LP')

    def test_as04_gate_blocks_a_before_independent_review(self):
        result = run_arm({'nome':'dummy'}, root=Path('/does-not-exist'),
                         arm_id='A2_K', mode='LP', policy=POLICY)
        self.assertEqual(result.status, 'NOT_AUTHORIZED')
        self.assertIsNone(result.lp_opt_value)

    def test_as04_optional_arms_fail_closed(self):
        result = run_arm({'nome':'dummy'}, root=Path('/does-not-exist'),
                         arm_id='FCC_K', mode='LP', policy=POLICY)
        self.assertEqual(result.status, 'NOT_AUTHORIZED')

    def test_as04_07_policy_rejects_different_warm_start(self):
        with self.assertRaises(ValueError):
            SolverPolicy(warm_start='from other arm')

    def test_as04_04_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            SolverPolicy(budget_s=0)


class TestAS04Reporting(unittest.TestCase):
    def test_as04_04_report_retains_censored_arm(self):
        policy = POLICY
        items = [row('U'), row('U_K'), row('A2_K', status='NOT_BUILT_SIZE',
                                            model_complete=False)]
        data = dict(schema='AS04-COMPARISON-v1', case_name='toy', mode='LP',
                    policy_sha256=policy.sha256, arms=[r.to_dict() for r in items],
                    comparison=compare_case(items))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run'
            publish_run(data, path, expected_arms=('U','U_K','A2_K'))
            self.assertTrue(verify_run(path))
            with (path/'arms.csv').open(encoding='utf-8') as fh:
                self.assertEqual(len(fh.readlines()), 4)
            with self.assertRaises(FileExistsError):
                publish_run(data, path, expected_arms=('U','U_K','A2_K'))
            (path/'arms.csv').write_text('MUTATION')
            with self.assertRaises(ValueError):
                verify_run(path)

    def test_as04_04_report_refuses_dropped_arm(self):
        items = [row('U'), row('U_K')]
        data = dict(schema='AS04-COMPARISON-v1', case_name='toy', mode='LP',
                    policy_sha256=POLICY.sha256, arms=[r.to_dict() for r in items],
                    comparison=compare_case(items))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                publish_run(data, Path(directory)/'run',
                            expected_arms=('U','U_K','A2_K'))

    def test_as04_sensor_remove_k_from_u_k_detected(self):
        with self.assertRaises(ValueError):
            row('U_K', applied_k_sha256=None)
        pair = assess_pair(row('U'), row('U_K', applied_k_sha256='mutated-K'),
                           effect='K_EFFECT')
        self.assertEqual(pair.status, 'INTEGRITY_ERROR')


if __name__ == '__main__':
    unittest.main()


def _simulated_slow_preparation(ctx):
    """Fixture no top-level para spawn real FC-01, sem solver."""
    import time
    ctx.phase('preparation')
    time.sleep(1.5)
    return {'should_not_be_published': 42}


class TestAS04Budget(unittest.TestCase):
    def test_as04_07_preparation_is_inside_real_supervised_budget(self):
        from fc_budget import run_bounded
        outcome = run_bounded(_simulated_slow_preparation, budget_s=.4)
        self.assertEqual(outcome.status, 'TIMEOUT_PREPARATION')
        self.assertIsNone(outcome.value)
        self.assertGreater(outcome.wall_total_s, 0)
        self.assertTrue(outcome.wall_total_s < 2)
