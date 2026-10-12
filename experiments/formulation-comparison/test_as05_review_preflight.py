"""Testes da auditoria documental; testes de sucesso NÃO são homologação."""
import json
import tempfile
import unittest
from pathlib import Path
from as05_review_preflight import inspect

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'results/benchmark/as05-prospective-plan-v1.json'
EVIDENCE = ROOT / 'docs/technical/plans/execucao/as05-gate-evidence-REVISADO.json'


class TestReviewPreflight(unittest.TestCase):
    def test_frozen_plan_matches_original_digest(self):
        report = inspect(ROOT, PLAN, EVIDENCE)
        self.assertEqual(report['plan_digest'], '193a0fb1812c10e502d2e086d9dc2e1f857b724046955bbb0684ad99c038ef3b')

    def test_pending_template_stays_blocked(self):
        report = inspect(ROOT, PLAN, EVIDENCE)
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertTrue(any('AS04_NAO_HOMOLOGADA' in b for b in report['blockers']))

    def test_missing_evidence_refuses_approval(self):
        report = inspect(ROOT, PLAN, ROOT / 'arquivo-inexistente.json')
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertTrue(any('EVIDENCIA_AUSENTE' in b for b in report['blockers']))

    def test_fake_independent_reviewer_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'evidence.json'
            data = json.loads(EVIDENCE.read_text())
            data['reviewers']['as04'] = {'author':'mesma-pessoa','reviewer':'mesma-pessoa','evidence_path':'foo.md'}
            p.write_text(json.dumps(data))
            report = inspect(ROOT, PLAN, p)
            self.assertTrue(any('REVISOR_AS04_IGUAL_AO_AUTOR' in b for b in report['blockers']))

    def test_existing_placeholder_cannot_certify(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.md'
            path.write_text('parecer de teste')
            data = json.loads(EVIDENCE.read_text())
            data.update(as04_verdict='PASS', as02_evidence={'as01_verdict':'PASS',
                'as01_independent_reviewer':True,'physical_exhaustion_passed':True,
                'sec59_lp_passed':True,'math_counterexample':False,
                'as02_independent_reviewer':True})
            for feature in ('as01','as02','as04'):
                data['reviewers'][feature]={'author':'author','reviewer':'reviewer','evidence_path':str(path)}
            evidence = Path(tmp) / 'evidence.json'
            evidence.write_text(json.dumps(data))
            report = inspect(ROOT, PLAN, evidence)
            self.assertEqual(report['status'], 'DECLARATIONS_COMPLETE_UNVERIFIED')
            self.assertIn('não atestam independência',report['notes'][1])

if __name__ == '__main__':
    unittest.main()
