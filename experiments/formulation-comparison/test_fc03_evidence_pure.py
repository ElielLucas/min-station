"""FC-03 acceptance tests, independent of Gurobi. Run with unittest discovery."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fc_evidence as ev  # noqa: E402


@dataclass(frozen=True)
class FakeMIP:
    formulation: str = 'comp_mip'
    status_name: str = 'OPTIMAL'
    objective_ub: float | None = 2.0
    objective_lb: float | None = 2.0
    physically_validated: bool | None = True
    physical_ub_status: str = 'UB_PHYSICAL_VALIDATED'
    installed: tuple = ('u', 'v')
    model_complete: bool = True
    instance_sha256: str = 'instance-A'
    model_context_sha256: str = 'context-A'
    rational_evidence: object | None = None
    certification: str = ev.NOT_CERTIFIED


@dataclass(frozen=True)
class FakeLP:
    formulation: str = 'lp_fcc_k'
    status: str = 'OPTIMAL'
    value: float | None = 2.0
    model_complete: bool = True
    rational_evidence: object | None = None


def _claim(folder: Path):
    proof = folder / 'proof.json'
    proof.write_text('{"proof":"independent-example"}', encoding='utf-8')
    return ev.RationalClaim(
        numerator=3, denominator=2,
        proof_path=str(proof), proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest(),
        proof_id='cert-example-001', model_context_sha256='context-A',
        instance_sha256='instance-A',
    )


def _verifier(claim):
    # This is a TEST DOUBLE, NOT a mathematical verifier or production proof.
    return ev.VerificationReceipt(True, 'independent-test-verifier', claim.proof_sha256,
                                  claim.model_context_sha256, claim.instance_sha256,
                                  claim.numerator, claim.denominator, claim.scope)


class EvidenceClassificationTests(unittest.TestCase):
    def test_proof01_optimal_lp_is_only_numeric(self):
        lp = FakeLP()
        self.assertEqual(ev.solver_classification(lp.status, model_complete=True),
                         ev.SOLVER_NUMERIC_OPTIMAL)
        self.assertIsNone(getattr(lp, 'rational_evidence'))

    def test_proof02_complete_mip_timelimit_can_show_numeric_lb(self):
        r = replace(FakeMIP(), status_name='TIME_LIMIT', objective_lb=1.1)
        self.assertEqual(ev.safe_solver_bound(r), 1.1)
        self.assertEqual(ev.solver_classification('TIME_LIMIT', model_complete=True,
                                                  numeric_bound=1.1), ev.SOLVER_NUMERIC_BOUND)

    def test_proof02_no_incumbent_still_numeric_bound_only(self):
        r = replace(FakeMIP(), status_name='TIME_LIMIT', objective_ub=None,
                    physically_validated=None, objective_lb=1.0)
        self.assertEqual(ev.safe_solver_bound(r), 1.0)
        self.assertIsNone(ev.physical_upper_bound(r))
        self.assertEqual(ev.certified_gap(r, instance_sha256='instance-A')[0], ev.INCONCLUSIVE)

    def test_proof03_restricted_rmp_never_global_bound(self):
        self.assertIsNone(ev.safe_solver_bound(replace(FakeMIP(), formulation='rmp',
                                                       objective_lb=10.0)))

    def test_proof03_truncated_fcc_never_global_bound(self):
        self.assertIsNone(ev.safe_solver_bound(replace(FakeMIP(), model_complete=False)))

    def test_proof03_objboundc_pricing_is_not_bound(self):
        self.assertIsNone(ev.safe_solver_bound(replace(FakeMIP(), formulation='pricing')))

    def test_proof03_cap_is_not_fake_zero(self):
        r = replace(FakeMIP(), status_name='CAP_EXCEEDED', objective_lb=0.0)
        self.assertIsNone(ev.safe_solver_bound(r))
        self.assertEqual(ev.solver_classification('CAP_EXCEEDED', model_complete=False),
                         ev.NOT_MEASURED)

    def test_proof04_validated_cardinality_is_exact_ub(self):
        self.assertEqual(ev.physical_upper_bound(FakeMIP()), 2)

    def test_proof04_invalid_ub_refused(self):
        r = FakeMIP()
        for bad in (replace(r, physically_validated=False),
                    replace(r, physically_validated=None),
                    replace(r, objective_ub=3.0),
                    replace(r, installed=('u', 'u'))):
            with self.subTest(bad=bad):
                self.assertIsNone(ev.physical_upper_bound(bad))

    def test_proof05_no_lb_no_gap_even_with_ub(self):
        status, gap, rel = ev.certified_gap(FakeMIP(), instance_sha256='instance-A')
        self.assertEqual((status, gap, rel), (ev.INCONCLUSIVE, None, None))

    def test_proof05_zero_ub_relative_gap_abstains(self):
        r = replace(FakeMIP(), objective_ub=0.0, installed=(),
                    rational_evidence=ev.VerifiedRationalEvidence(Fraction(0), 'p', 'sha', 'v',
                                                                  'context-A', 'instance-A',
                                                                  ev.PHYSICAL_GLOBAL_LB))
        status, abs_gap, rel = ev.certified_gap(r, instance_sha256='instance-A')
        self.assertEqual((status, abs_gap, rel), (ev.CERTIFIED_GAP_AVAILABLE, Fraction(0), None))

    def test_proof05_mismatched_instance_proof_refused(self):
        proof = ev.VerifiedRationalEvidence(Fraction(1), 'p', 'sha', 'v', 'context-A',
                                            'instance-B', ev.PHYSICAL_GLOBAL_LB)
        self.assertIsNone(ev.checked_rational_lb(replace(FakeMIP(), rational_evidence=proof),
                                                  instance_sha256='instance-A'))

    def test_proof06_independent_receipt_preserves_exact_fraction(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            evd = ev.accept_independent_proof(
                claim, expected_model_context_sha256='context-A',
                expected_instance_sha256='instance-A', verifier=_verifier)
            self.assertEqual(evd.value, Fraction(3, 2))
            self.assertEqual(evd.proof_id, 'cert-example-001')
            self.assertEqual(evd.verifier_id, 'independent-test-verifier')
            self.assertEqual(evd.model_context_sha256, 'context-A')
            self.assertEqual(evd.proof_sha256, claim.proof_sha256)

    def test_proof06_opt_in_attachment_and_certified_gap(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            result = ev.attach_independent_proof(FakeMIP(), claim, verifier=_verifier)
            self.assertEqual(result.certification, ev.RATIONAL_VERIFIED)
            status, gap, relative = ev.certified_gap(result, instance_sha256='instance-A')
            self.assertEqual((status, gap, relative),
                             (ev.CERTIFIED_GAP_AVAILABLE, Fraction(1, 2), Fraction(1, 4)))

    def test_proof05_verified_lb_without_physical_validation_stays_inconclusive(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            valid = ev.attach_independent_proof(FakeMIP(), claim, verifier=_verifier)
            invalid = replace(valid, physically_validated=False,
                              physical_ub_status='INVALID_PHYSICAL_WITNESS')
            self.assertEqual(ev.certified_gap(invalid, instance_sha256='instance-A'),
                             (ev.INCONCLUSIVE, None, None))

    def test_proof06_verified_proof_reported_only_with_matching_identity(self):
        with tempfile.TemporaryDirectory() as d:
            valid = ev.attach_independent_proof(FakeMIP(), _claim(Path(d)), verifier=_verifier)
            self.assertEqual(ev.exact_text(ev.checked_rational_lb(
                valid, instance_sha256='instance-A')), '3/2')
            self.assertIsNone(ev.checked_rational_lb(
                replace(valid, model_context_sha256='other'), instance_sha256='instance-A'))

    def test_proof06_no_verifier_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ev.accept_independent_proof(_claim(Path(d)),
                    expected_model_context_sha256='context-A',
                    expected_instance_sha256='instance-A', verifier=None)

    def test_proof06_rejected_receipt_fails(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            with self.assertRaises(ValueError):
                ev.attach_independent_proof(FakeMIP(), claim,
                    verifier=lambda c: replace(_verifier(c), accepted=False))

    def test_proof06_mismatched_receipt_fails(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            with self.assertRaises(ValueError):
                ev.attach_independent_proof(FakeMIP(), claim,
                    verifier=lambda c: replace(_verifier(c), model_context_sha256='other'))

    def test_proof06_modified_artifact_fails(self):
        with tempfile.TemporaryDirectory() as d:
            claim = _claim(Path(d))
            Path(claim.proof_path).write_text('modified', encoding='utf-8')
            with self.assertRaises(ValueError):
                ev.attach_independent_proof(FakeMIP(), claim, verifier=_verifier)

    def test_proof06_restricted_model_does_not_accept_external_attestation(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ev.attach_independent_proof(replace(FakeMIP(), model_complete=False),
                                            _claim(Path(d)), verifier=_verifier)

    def test_context_digest_deterministic_and_distinguishes_k(self):
        params = dict(instance_sha256='a', formulation='fcc_k', modality='B',
                      k_sha256='k1', model_complete=True)
        self.assertEqual(ev.context_digest(**params), ev.context_digest(**params))
        self.assertNotEqual(ev.context_digest(**params),
                            ev.context_digest(**{**params, 'k_sha256': 'k2'}))


class ReportingTests(unittest.TestCase):
    def _reporter(self):
        class LP:
            pass
        class MIP:
            pass
        dummy = types.ModuleType('fc_core')
        dummy.LPResult = LP
        dummy.MIPResult = MIP
        spec = importlib.util.spec_from_file_location('_fc03_reporting', HERE / 'fc_reporting.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'fc_core': dummy}):
            spec.loader.exec_module(module)
        return module, LP, MIP

    def test_optimal_numeric_lp_csv_without_proof(self):
        rep, LP, _ = self._reporter()
        r = LP()
        r.formulation, r.status, r.value = 'lp_comp', 'OPTIMAL', 3.125
        r.model_complete = True
        r.time_s, r.work, r.solver_runtime_s = 1.0, 0.01, 0.1
        r.phase_wall_s, r.stop_reason = (), 'OPTIMAL'
        r.n_vars, r.n_cons, r.n_K, r.k_sha256, r.reason = 3, 5, 0, None, ''
        r.rational_evidence = None
        inst = types.SimpleNamespace(nome='i', classe='c', familia='f', n=3, m_arestas=2,
                         m=1, r=1, instance_sha256='sha')
        row = rep._lp_row(inst, r)
        self.assertEqual(row['solver_evidence'], ev.SOLVER_NUMERIC_OPTIMAL)
        self.assertEqual(row['solver_numeric_lp_objective'], 3.125)
        self.assertEqual(row['rational_verification'], ev.NOT_CERTIFIED)
        self.assertEqual(row['certified_gap_status'], ev.INCONCLUSIVE)
        self.assertEqual(row['lb_best'], '')
        self.assertEqual(row['certification'], ev.NOT_CERTIFIED)
        self.assertEqual(set(row), set(rep.RESULTS_FIELDS))

    def test_complete_mip_csv_separates_three_evidence_axes(self):
        rep, _, MIP = self._reporter()
        r = MIP()
        r.__dict__.update(FakeMIP().__dict__)
        r.time_s, r.solver_runtime_s, r.work = 1.0, 0.1, 0.01
        r.phase_wall_s, r.stop_reason = (), 'OPTIMAL'
        r.n_vars, r.n_cons, r.n_K, r.n_K_added, r.k_sha256 = 3, 5, 0, 0, 'k'
        r.k_validated, r.reason = True, ''
        r.gap_abs, r.gap_rel = 0.0, 0.0
        r.nodes, r.ru_maxrss_kb_before, r.ru_maxrss_kb_after = 0, 1, 2
        r.time_to_first_feasible_s = 0.2
        r.time_to_best_s = 0.3
        r.time_to_proof_s = 0.5
        r.evolution = ()
        inst = types.SimpleNamespace(nome='i', classe='c', familia='f', n=3, m_arestas=2,
                         m=1, r=1, instance_sha256='instance-A')
        row = rep._mip_row(inst, r)
        self.assertEqual(row['solver_numeric_mip_lb'], 2.0)
        self.assertEqual(row['physical_feasible_ub'], 2)
        self.assertEqual(row['rational_verification'], ev.NOT_CERTIFIED)
        self.assertEqual(row['certified_gap_abs_exact'], '')
        self.assertEqual(row['certified_gap_status'], ev.INCONCLUSIVE)
        self.assertEqual(row['optimality_proven'], '')
        self.assertTrue(row['solver_optimality_reported'])
        self.assertEqual(row['solver_time_to_optimal_s'], 0.5)
        self.assertEqual(set(row), set(rep.RESULTS_FIELDS))

    def test_numeric_bound_unavailable_when_incomplete_or_pricing(self):
        rep, _, MIP = self._reporter()
        # No solver required: direct core evidence must fail closed.
        for formulation in ('rmp', 'pricing', 'fcc_k'):
            complete = formulation != 'fcc_k'
            r = replace(FakeMIP(), formulation=formulation, model_complete=complete)
            self.assertIsNone(ev.safe_solver_bound(r))


if __name__ == '__main__':
    unittest.main()
