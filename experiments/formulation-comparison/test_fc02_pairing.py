"""FC-02: testes puros de integridade do par, sem dependência do Gurobi."""
from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fc_pairing import assess_primary_pair  # noqa: E402


@dataclass(frozen=True)
class FakeInstance:
    instance_sha256: str = 'bytes-reais'


@dataclass(frozen=True)
class FakeResult:
    status_name: str = 'OPTIMAL'
    instance_sha256: str = 'bytes-reais'
    k_sha256: str = 'hash-K'
    n_K: int = 2
    n_K_added: int = 2
    k_validated: bool = True
    objective_ub: float | None = 2.0
    physically_validated: bool | None = True
    reason: str = ''


class PairContractTests(unittest.TestCase):
    def setUp(self):
        self.inst = FakeInstance()
        self.comp = FakeResult()
        self.fcc = FakeResult()

    def check(self, want, comp=None, fcc=None):
        p = assess_primary_pair(self.inst,
                                self.comp if comp is None else comp,
                                self.fcc if fcc is None else fcc)
        self.assertEqual(p.status, want, p)
        return p

    def test_both_complete_identical_hash_validated_witness(self):
        p = self.check('PAIR_VALID')
        self.assertEqual(p.instance_sha256, 'bytes-reais')
        self.assertEqual(p.k_sha256, 'hash-K')

    def test_empty_k_set_still_has_canonical_digest_and_is_comparable(self):
        self.check('PAIR_VALID', replace(self.comp, n_K=0, n_K_added=0),
                   replace(self.fcc, n_K=0, n_K_added=0))

    def test_divergent_instance_hash_refuses_pair(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, instance_sha256='adulterado'))

    def test_missing_instance_hash_refuses_pair(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, instance_sha256=None))

    def test_divergent_k_hash_refuses_pair(self):
        self.check('INTEGRITY_ERROR', fcc=replace(self.fcc, k_sha256='adulterado'))

    def test_absent_k_hash_refuses_pair(self):
        self.check('INTEGRITY_ERROR', fcc=replace(self.fcc, k_sha256=None))

    def test_incorrect_number_of_added_cuts_refuses_pair(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, n_K_added=1))

    def test_unvalidated_k_refuses_pair(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, k_validated=False))

    def test_mismatched_k_counts_refuses_pair(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, n_K=3, n_K_added=3))

    def test_invalid_physical_witness_refuses_pair(self):
        self.check('INVALID_PHYSICAL_WITNESS', replace(self.comp, physically_validated=False))

    def test_missing_independent_validator_refuses_pair(self):
        self.check('INVALID_PHYSICAL_WITNESS', replace(self.comp, physically_validated=None))

    def test_no_incumbent_does_not_assert_physical_ub(self):
        self.check('PAIR_VALID', replace(self.comp, objective_ub=None,
                                         physically_validated=None, status_name='TIME_LIMIT'))

    def test_unknown_solver_status_is_not_comparable(self):
        self.check('PAIR_NOT_AVAILABLE', replace(self.comp, status_name='STATUS_99'))

    def test_cap_exceeded_is_not_comparable_or_a_fake_bound(self):
        self.check('PAIR_NOT_AVAILABLE', fcc=replace(self.fcc, status_name='CAP_EXCEEDED',
                                                     objective_ub=None, n_K=None,
                                                     k_sha256=None))

    def test_timeout_without_result_is_not_comparable(self):
        self.check('PAIR_NOT_AVAILABLE', replace(self.comp, status_name='TIMEOUT_PREPARATION',
                                                 objective_ub=None))

    def test_worker_error_is_not_comparable(self):
        self.check('PAIR_NOT_AVAILABLE', replace(self.comp, status_name='WORKER_ERROR'))

    def test_invalid_k_fails_closed_as_integrity_error(self):
        self.check('INTEGRITY_ERROR', replace(self.comp, status_name='WORKER_ERROR',
                                             reason='ValueError: INTEGRITY_ERROR: invalid K'))

    def test_one_unexecuted_arm_is_not_comparable(self):
        self.assertEqual(assess_primary_pair(self.inst, None, self.fcc).status,
                         'PAIR_NOT_AVAILABLE')
        self.assertEqual(assess_primary_pair(self.inst, self.comp, None).status,
                         'PAIR_NOT_AVAILABLE')


if __name__ == '__main__':
    unittest.main()
