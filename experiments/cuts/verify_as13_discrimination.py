#!/usr/bin/env python3
"""AS13 discrimination sensor: nine in-memory faults; no source files changed.

The test suite must reject the four original faults plus R2's five
mutation families N2-N5/N7: skipped exhaustive H2/HL loops, skipped oracle
comparisons, a fabricated K4 H2 count, and beta forced to zero. This is
not independent review.
"""
import json
from unittest.mock import patch

import test_as13_foundations as tests


def must_kill(test_method, patch_target, replacement, label):
    with patch.object(tests, patch_target, replacement):
        try:
            getattr(tests.AS13Foundations(test_method), test_method)()
        except AssertionError:
            return label
    raise AssertionError(f'Surviving mutant: {label}')



def must_kill_as13(test_method, target, replacement, label):
    """A baseline test must PASS and fail when the verifier is made inert.

    This prevents counting an unrelated preexisting failure as a killed mutant.
    """
    case = tests.AS13Foundations(test_method)
    getattr(case, test_method)()  # unmutated baseline
    with patch.object(tests.as13, target, replacement):
        try:
            getattr(tests.AS13Foundations(test_method), test_method)()
        except AssertionError:
            return label
    raise AssertionError(f'Surviving mutant: {label}')

def check_sensor():
    killed = []
    tests.AS13Foundations.setUpClass()
    original = tests.h2_for_support

    def inflated_h2(*args, **kwargs):
        output = original(*args, **kwargs)
        if output is None:
            return None
        coefs, rhs, B = output
        return coefs, rhs + 1, B

    killed.append(must_kill('test_as13_03_full_and_partial_classification',
                            'h2_for_support', inflated_h2, 'H2_RHS_2_TO_3'))
    killed.append(must_kill('test_as13_01_shared_terminal_can_stay_without_station',
                            'reach_matching_oracle', lambda *a, **k: False,
                            'ZERO_LENGTH_STAY_SUPPRESSED'))
    killed.append(must_kill('test_as13_05_ip_is_computed_from_physical_oracle',
                            'physical_optimum_by_cardinality',
                            lambda *a, **k: {'optimum': 2, 'witness': [],
                                             'station_subsets_checked': 0},
                            'IP_OPTIMUM_HARDCODED_2'))
    killed.append(must_kill('test_as13_05_k4_exhaustive_rejects_one_false_positive',
                            'verify_k4_exhaustive_physical',
                            lambda *a, **k: {'optimum': 3, 'witness': [],
                                             'station_subsets_checked': 65536},
                            'K4_ENUMERATION_SKIPPED_WITH_LITERAL_COUNTER'))
    # Exact Opus R2 blind spots: each replacement supplies the same plausible
    # summary that previously let a disabled internal loop survive.
    killed.append(must_kill_as13(
        'test_as13_r2_exhaustive_cuts_rejects_one_false_classification',
        'check_exhaustive_small_cuts',
        lambda *a, **k: {'H2_nontrivial_supports': 32,
                          'HL_nontrivial_supports': 32,
                          'HL_positive_beta_supports': 4,
                          'globally_infeasible_controls': 1},
        'N2_EXHAUSTIVE_H2_HL_LOOP_SKIPPED'))
    killed.append(must_kill_as13(
        'test_as13_r2_oracle_hb_k4_rejects_one_false_classification',
        'check_oracle_agreement_hb_k4',
        lambda *a, **k: {'station_subsets_compared': 674},
        'N3_HB_K4_ORACLE_LOOP_SKIPPED'))
    killed.append(must_kill_as13(
        'test_as13_r2_control_oracle_rejects_one_false_classification',
        'check_oracle_agreement_controls',
        lambda *a, **k: {'battery_vs_reach_cases': 68, 'cases': 5},
        'N4_CONTROL_ORACLE_LOOP_SKIPPED'))
    killed.append(must_kill_as13(
        'test_as13_r2_k4_all_h2_supports_reject_one_false_classification',
        'check_all_h2_at_k4_fractional',
        lambda *a, **k: (45056, 16384),
        'N5_K4_H2_SUPPORTS_REPLACED_BY_LITERALS'))
    killed.append(must_kill_as13(
        'test_as13_r2_hl_beta_is_positive_and_checked_independently',
        'hl_beta_from_patterns',
        lambda *a, **k: 0,
        'N7_HL_BETA_FORCED_TO_ZERO'))
    return {'schema': 'AS13-DISCRIMINATION-v3',
            'faults_injected': len(killed), 'killed': len(killed),
            'survived': 0, 'fault_names': killed,
            'workspace_modified': False}


if __name__ == '__main__':
    print(json.dumps(check_sensor(), indent=2, sort_keys=True))
