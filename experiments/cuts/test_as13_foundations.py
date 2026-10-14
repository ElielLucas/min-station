"""Regression tests derived from AS13 acceptance criteria (no Gurobi)."""
from __future__ import annotations

import unittest
from unittest.mock import patch
import verify_as13_foundations as as13
from itertools import combinations

from verify_as13_foundations import (
    from_edges, k4, h2_for_support, k_cuts, reach_arcs,
    reach_matching_oracle, verify,
    physical_optimum_by_cardinality, verify_k4_exhaustive_physical,
)
from independent_validator import viavel
from hb import construir as construir_hb


class AS13Foundations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = verify()

    def test_as13_01_shared_terminal_can_stay_without_station(self):
        case = from_edges(('s',),('s',),('s',),(),1)
        S,T,V,adj,r = case
        self.assertTrue(viavel(S,T,V,adj,r,()))
        self.assertTrue(reach_matching_oracle(S,T,V,reach_arcs(V,adj,r),()))

    def test_as13_01_terminal_relay_must_be_installed_if_needed(self):
        case = from_edges(('s','t','u'),('s',),('u',),(('s','t'),('t','u')),1)
        S,T,V,adj,r = case
        self.assertFalse(viavel(S,T,V,adj,r,()))
        self.assertTrue(viavel(S,T,V,adj,r,('t',)))
        self.assertFalse(reach_matching_oracle(S,T,V,reach_arcs(V,adj,r),()))
        self.assertTrue(reach_matching_oracle(S,T,V,reach_arcs(V,adj,r),('t',)))

    def test_as13_01_two_consecutive_stations_needed(self):
        case=from_edges(('s','a','b','t'),('s',),('t',),(('s','a'),('a','b'),('b','t')),1)
        S,T,V,adj,r = case
        self.assertFalse(viavel(S,T,V,adj,r,('a',)))
        self.assertFalse(viavel(S,T,V,adj,r,('b',)))
        self.assertTrue(viavel(S,T,V,adj,r,('a','b')))

    def test_as13_01_one_relay_services_two_robots(self):
        S,T,V,adj,r=from_edges(('s1','s2','w','t1','t2'),('s1','s2'),('t1','t2'),
                                    (('s1','w'),('s2','w'),('w','t1'),('w','t2')),1)
        self.assertTrue(viavel(S,T,V,adj,r,('w',)))

    def test_as13_02_h2_requires_invalid_complement(self):
        S,T,V,adj,r=from_edges(('s','a','t'),('s',),('t',),(('s','a'),('a','t')),1)
        self.assertIsNone(h2_for_support(S,T,V,adj,r,('s',)))
        coefs,rhs,B=h2_for_support(S,T,V,adj,r,('a',))
        self.assertEqual((coefs,rhs,B),({'a':2},2,set()))
        # F = {s,t} is infeasible; installing a suffices; H2 degenerates to y_a>=1.

    def test_as13_02_empty_support_is_not_certified(self):
        S,T,V,adj,r=from_edges(('s','a','t'),('s',),('t',),(('s','a'),('a','t')),1)
        self.assertIsNone(h2_for_support(S,T,V,adj,r,()))

    def test_as13_04_hl_with_viable_complement_is_full_cube(self):
        S,T,V,adj,r=from_edges(('s','a','t'),('s',),('t',),(('s','a'),('a','t')),1)
        R={'s'}
        F=set(V)-R
        self.assertTrue(viavel(S,T,V,adj,r,F))
        for pattern in (set(),{'s'}):
            self.assertTrue(viavel(S,T,V,adj,r,F|pattern))

    def test_as13_03_full_and_partial_classification(self):
        S,T,V,adj,edges,r,_ = construir_hb(4,2,1)
        coefs,rhs,B=h2_for_support(S,T,V,adj,r,V)
        self.assertEqual(rhs,2)
        self.assertEqual(len(B),16)
        self.assertTrue(all(coef==1 for coef in coefs.values()))
        coefs2,rhs2,B2=h2_for_support(S,T,V,adj,r,V,partial_insufficient={'x0_0'})
        self.assertEqual(rhs2,2)
        self.assertEqual(B2,{'x0_0'})
        self.assertTrue(all(c==2 for v,c in coefs2.items() if v!='x0_0'))
        self.assertGreaterEqual(sum(coefs2.get(v,0) for v in ('x0_0','x0_1')),2)

    def test_as13_04_hl_projection_k4(self):
        (S,T,V,adj,r),W=k4()
        R=set(W); F=set(V)-R
        patterns=[]
        for k in range(5):
            for combo in combinations(W,k):
                if viavel(S,T,V,adj,r,F|set(combo)):
                    patterns.append(set(combo))
        self.assertEqual(len(patterns),5) # 4 triples and the full set
        self.assertEqual(min(map(len,patterns)),3)
        self.assertEqual(set(map(frozenset,patterns)),set(map(frozenset,[set(W)] + [set(t) for t in combinations(W,3)])))

    def test_as13_05_hb_exact_expected_LP_and_IP(self):
        self.assertEqual(self.evidence['HB']['lp_COMP_K'],1)
        self.assertEqual(self.evidence['HB']['lp_COMP_K_H2'],2)
        self.assertEqual(self.evidence['HB']['ip_phys_opt'],2)
        self.assertEqual(self.evidence['HB']['K_count'],4)

    def test_as13_05_k4_hierarchy_exact_expected_values(self):
        self.assertEqual(self.evidence['K4']['lp_COMP_K'],2)
        self.assertAlmostEqual(self.evidence['K4']['lp_COMP_K_H2'],8/3)
        self.assertEqual(self.evidence['K4']['lp_COMP_K_H2_HL'],3)
        self.assertEqual(self.evidence['K4']['ip_phys_opt'],3)

    def test_as13_05_every_k4_installation_checked(self):
        self.assertEqual(self.evidence['K4']['battery_station_subsets_checked'],65536)
        self.assertEqual(self.evidence['K4']['H2_supports_nontrivial_checked'],45056)

    def test_as13_05_ip_is_computed_from_physical_oracle(self):
        # Directly challenge the two distinct optima, not a cached JSON value.
        direct = from_edges(('s','t'),('s',),('t',),(('s','t'),),1)
        S,T,V,adj,r = direct
        zero = physical_optimum_by_cardinality(S,T,V,adj,r)
        self.assertEqual(zero['optimum'], 0)
        self.assertEqual(zero['witness'], [])
        two = from_edges(('s','a','b','t'),('s',),('t',),
                         (('s','a'),('a','b'),('b','t')),1)
        S,T,V,adj,r=two
        result=physical_optimum_by_cardinality(S,T,V,adj,r)
        self.assertEqual(result['optimum'], 2)
        self.assertTrue(viavel(S,T,V,adj,r,result['witness']))
        self.assertGreater(result['station_subsets_checked'], 1)

    def test_as13_05_verify_cannot_ignore_corrupted_hb_optimum(self):
        # Mutating the physical optimum oracle at the call site must invalidate
        # the whole certificate, not merely change an unused helper function.
        bad={'optimum': 0, 'witness': [], 'station_subsets_checked': 1}
        with patch.object(as13, 'physical_optimum_by_cardinality', return_value=bad):
            with self.assertRaises(AssertionError):
                as13.verify()

    def test_as13_05_verify_cannot_ignore_corrupted_k4_exhaustive(self):
        # An author cannot replace K4's 65536 checks with an innocent-looking
        # field containing a literal 65536 and still pass this test.
        bad={'optimum': 1, 'witness': [], 'station_subsets_checked': 1}
        with patch.object(as13, 'verify_k4_exhaustive_physical', return_value=bad):
            with self.assertRaises(AssertionError):
                as13.verify()

    def test_as13_05_k4_exhaustive_rejects_one_false_positive(self):
        # Flip physical feasibility for exactly one mask. An enumeration that
        # trusts only a literal '65536' or avoids the oracle must fail here.
        instance, W = k4()
        S,T,V,adj,r=instance
        real_oracle=as13.viavel
        def wrong_on_empty(*args, **kwargs):
            if not args[5]:
                return True
            return real_oracle(*args, **kwargs)
        with patch.object(as13, 'viavel', side_effect=wrong_on_empty):
            with self.assertRaisesRegex(AssertionError, 'K4 physical mismatch'):
                verify_k4_exhaustive_physical(instance, W)

    def test_as13_05_k4_exhaustive_rejects_one_false_negative(self):
        # Non-initial mask: ensures the scan reaches feasible full selections.
        instance, W=k4()
        real_oracle=as13.viavel
        selected=frozenset(W[:3])
        def wrong_on_triple(*args, **kwargs):
            if frozenset(args[5]) == selected:
                return False
            return real_oracle(*args, **kwargs)
        with patch.object(as13, 'viavel', side_effect=wrong_on_triple):
            with self.assertRaisesRegex(AssertionError, 'K4 physical mismatch'):
                verify_k4_exhaustive_physical(instance, W)

    def test_as13_05_hb_ip_not_literal(self):
        S,T,V,adj,edges,r,_ = construir_hb(4,2,1)
        result = physical_optimum_by_cardinality(S,T,V,adj,r)
        self.assertEqual(result['optimum'], 2)
        self.assertEqual(len(result['witness']), result['optimum'])
        self.assertTrue(viavel(S,T,V,adj,r,result['witness']))

    def test_as13_07_k4_cg_rounding_from_real_materialized_K(self):
        (S,T,V,adj,r),W=k4()
        K=k_cuts(S,T,V,adj,r,reach_arcs(V,adj,r))
        for missing in W:
            triple=set(W)-{missing}
            actual={frozenset(Z) for Z in K if set(Z)<=triple}
            expected={frozenset(pair) for pair in combinations(sorted(triple),2)}
            self.assertEqual(actual, expected)
            # Pair-covering sum: 2*y(triple)>=3, hence integer y(triple)>=2.
            for k in range(4):
                for selected in combinations(sorted(triple),k):
                    if all(set(selected)&set(Z) for Z in actual):
                        self.assertGreaterEqual(len(selected),2)
        self.assertAlmostEqual(self.evidence['K4']['lp_COMP_K_plus_CG_triples'], 8/3)
        self.assertTrue(self.evidence['K4']['CG_triples_exactly_H2_triples_on_K4'])

    def test_as13_installation_gate_passes_only_when_proofs_present(self):
        import tempfile
        from pathlib import Path
        from verify_as13_delivery import check_installation
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(check_installation(root)['errors'], [])
        with tempfile.TemporaryDirectory() as missing:
            report = check_installation(Path(missing))
            self.assertEqual(report['status'], 'FAIL_MISSING_DELIVERABLES')
            self.assertEqual(len(report['errors']), report['required_file_count'])

    def test_as13_06_07_hb_integer_K_not_physical(self):
        S,T,V,adj,edges,r,_=construir_hb(4,2,1)
        K=k_cuts(S,T,V,adj,r,reach_arcs(V,adj,r))
        C={'x0_0'}
        self.assertTrue(all(C & set(Z) for Z in K))
        self.assertFalse(viavel(S,T,V,adj,r,C))

    # R2: each formerly-surviving mutation has an executable *outcome* test.
    # These tests challenge the relevant loop, not merely a counter copied
    # from the witness report.

    def test_as13_r2_oracle_hb_k4_rejects_one_false_classification(self):
        original = as13.viavel
        hb_origins = tuple(construir_hb(4, 2, 1)[0])

        def flipped(*args, **kwargs):
            if tuple(args[0]) == hb_origins and not args[5]:
                return not original(*args, **kwargs)
            return original(*args, **kwargs)

        with patch.object(as13, 'viavel', side_effect=flipped):
            with self.assertRaisesRegex(AssertionError, 'oracle mismatch'):
                as13.check_oracle_agreement_hb_k4()
        self.assertEqual(
            as13.check_oracle_agreement_hb_k4()['station_subsets_compared'],
            674)

    def test_as13_r2_control_oracle_rejects_one_false_classification(self):
        controls = as13.small_controls()
        original = as13.viavel

        def flipped(*args, **kwargs):
            if tuple(args[0]) == ('a',) and not args[5]:
                return not original(*args, **kwargs)
            return original(*args, **kwargs)

        with patch.object(as13, 'viavel', side_effect=flipped):
            with self.assertRaisesRegex(AssertionError, 'oracle mismatch'):
                as13.check_oracle_agreement_controls(controls)
        self.assertEqual(
            as13.check_oracle_agreement_controls(controls),
            {'battery_vs_reach_cases': 68, 'cases': 5})

    def test_as13_r2_exhaustive_cuts_rejects_one_false_classification(self):
        controls = as13.small_controls()
        original = as13.viavel

        def flipped(*args, **kwargs):
            if tuple(args[0]) == ('a',) and not args[5]:
                return not original(*args, **kwargs)
            return original(*args, **kwargs)

        with patch.object(as13, 'viavel', side_effect=flipped):
            with self.assertRaisesRegex(AssertionError, 'oracle mismatch'):
                as13.check_exhaustive_small_cuts(controls)
        summary = as13.check_exhaustive_small_cuts(controls)
        self.assertEqual(summary['H2_nontrivial_supports'], 32)
        self.assertEqual(summary['HL_nontrivial_supports'], 32)
        self.assertGreater(summary['HL_positive_beta_supports'], 0)
        self.assertEqual(summary['globally_infeasible_controls'], 1)

    def test_as13_r2_k4_all_h2_supports_reject_one_false_classification(self):
        instance, W = k4()
        V = instance[2]
        ix = {v: i for i, v in enumerate(V)}
        wbits = sum(1 << ix[w] for w in W)
        # Structurally derived control table; the full physical table is
        # independently computed by verify_k4_exhaustive_physical in verify().
        physical_predictions = [
            (mask & wbits).bit_count() >= 3
            for mask in range(1 << len(V))
        ]
        # Flip exactly one outcome, not the number of iterations.
        physical_predictions[0] = True
        with self.assertRaisesRegex(AssertionError, 'K4 H2 classification mismatch'):
            as13.check_all_h2_at_k4_fractional(
                instance, W, mask_viability=physical_predictions)
        physical_predictions[0] = False
        self.assertEqual(
            as13.check_all_h2_at_k4_fractional(
                instance, W, mask_viability=physical_predictions),
            (45056, 16384))
        self.assertEqual(self.evidence['K4']['H2_supports_tight_at_fractional_point'], 16384)

    def test_as13_r2_hl_beta_is_positive_and_checked_independently(self):
        case = as13.small_controls()[1]  # a-b-c, r=1, b must be installed
        S, T, V, adj, r = case
        R = {'b'}
        F = set(V) - R
        patterns = [P for P in (set(), {'b'}) if viavel(S, T, V, adj, r, F | P)]
        self.assertEqual(patterns, [{'b'}])
        self.assertEqual(as13.hl_beta_from_patterns(patterns, {'b': 1}), 1)
        # The entire exhaustive verifier must reject beta=0, even if it is
        # silently substituted in the previously uncovered inner HL loop.
        with patch.object(as13, 'hl_beta_from_patterns', return_value=0):
            with self.assertRaisesRegex(AssertionError, 'HL beta differs'):
                as13.check_exhaustive_small_cuts(as13.small_controls())
        self.assertGreater(self.evidence['exhaustive_small_cuts']['HL_positive_beta_supports'], 0)

    def test_as13_r2_globally_infeasible_control(self):
        S, T, V, adj, r = as13.small_controls()[-1]
        arcs = reach_arcs(V, adj, r)
        self.assertFalse(viavel(S, T, V, adj, r, V))
        self.assertFalse(reach_matching_oracle(S, T, V, arcs, V))
        # All choices are infeasible, so R=empty has an empty H2 LHS:
        # mathematically valid vacuously but a global-infeasibility signal,
        # not a normal row to be injected by a future separator.
        self.assertEqual(h2_for_support(S,T,V,adj,r,()), ({},2,set()))
        phi_empty = [P for P in (set(),) if viavel(S,T,V,adj,r,set(V)|P)]
        self.assertEqual(phi_empty, [])
        with self.assertRaisesRegex(ValueError, 'Phi_R is empty'):
            as13.hl_beta_from_patterns(phi_empty, {})
        self.assertEqual(self.evidence['exhaustive_small_cuts']['globally_infeasible_controls'], 1)


if __name__ == '__main__':
    unittest.main()
