"""AS02-06: gate bloqueia campanhas se matemática ou revisão estiver pendente."""
import unittest
from as02_validation_gate import GateEvidence, assess, require_hard_campaign_authorization


class TestAS02Gate(unittest.TestCase):
    def test_as02_06_fail_closed_without_as01_review(self):
        evidence = GateEvidence(physical_exhaustion_passed=True, sec59_lp_passed=True)
        self.assertEqual(assess(evidence), 'AS01_REVIEW_PENDING')
        with self.assertRaisesRegex(RuntimeError, 'AS01_REVIEW_PENDING'):
            require_hard_campaign_authorization(evidence)

    def test_as02_06_counterexample_overrides_all_positive_fields(self):
        evidence = GateEvidence('PASS', True, True, True, True, True)
        self.assertEqual(assess(evidence), 'MATH_GATE_FAIL')
        with self.assertRaisesRegex(RuntimeError, 'MATH_GATE_FAIL'):
            require_hard_campaign_authorization(evidence)

    def test_as02_06_independent_review_and_tests_required(self):
        self.assertEqual(assess(GateEvidence('PASS', True, True, True, False, False)),
                         'AS02_REVIEW_PENDING')
        self.assertEqual(assess(GateEvidence('PASS', True, False, True, False, True)),
                         'AS02_VALIDATION_FAIL')
        good = GateEvidence('PASS', True, True, True, False, True)
        self.assertEqual(assess(good), 'PASS')
        require_hard_campaign_authorization(good)


if __name__ == '__main__':
    unittest.main()
