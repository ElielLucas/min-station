"""N2-T1: testes sem Gurobi e sem medições novas."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('run_n2_t1', HERE / 'run_n2_t1.py')
t1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1)


class N2T1Offline(unittest.TestCase):
    def test_path_and_budget_are_frozen(self):
        self.assertEqual(t1.EXPECTED_DECISION, 'PROMOTE FCC + EXISTING CUTS')
        self.assertEqual(t1.REFERENCE_WORK, 164.0)
        self.assertEqual({x[1] for x in t1.LEVEL_ONE}, {'hb', 'bp-nao'})
        self.assertEqual({x[1] for x in t1.LEVEL_TWO}, {'hb', 'bp-nao'})
        self.assertEqual(len(t1.LEVEL_TWO), 2)

    def test_level_two_is_above_n1_cap_and_deterministic(self):
        for name, family, factory, params in t1.LEVEL_TWO:
            a = t1.level_two_instance(factory, params)
            b = t1.level_two_instance(factory, params)
            self.assertGreater(len(a['V']), 21, name)
            self.assertEqual(a['data_sha256_n2'], b['data_sha256_n2'])
            self.assertEqual(len(a['S']), len(a['T']))
            self.assertEqual(a['r'], 1)
            self.assertEqual(len(a['A_r']), len(set(map(tuple, a['A_r']))))

    def test_n1_gate_refuses_activation_without_evidence(self):
        with patch.object(t1, 'activation', side_effect=RuntimeError('N1 não auditada')):
            with self.assertRaisesRegex(RuntimeError, 'N1 não auditada'):
                t1.generate_data()

    def test_no_freeze_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path(tmp) / 'freeze.json'
            previous.write_text('do not touch')
            with patch.object(t1, 'FREEZE', previous), patch.object(t1, 'PREREG', Path(tmp) / 'pre.md'):
                with self.assertRaisesRegex(RuntimeError, 'já congelada'):
                    t1.freeze()
            self.assertEqual(previous.read_text(), 'do not touch')

    def test_no_results_before_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'n2-experimental.csv').write_text('measured')
            with patch.object(t1, 'RESULTS', p):
                with self.assertRaisesRegex(RuntimeError, 'Já há evidência'):
                    t1.ensure_no_n2_results()

    def test_document_states_no_uncertified_lb(self):
        data = {'frozen_at_utc': '2026-10-09T00:00:00+00:00',
                'instances': [{'name':'HB', 'family':'hb','level':1,'n':16,'m':6,
                               'B0_reference':1.0,'full_lp_reference':2.0}],
                'protocol': {'WorkLimit_total':164.0,'threads':4,'seed':42,'wall_guard_seconds':1800},
                'small_regressions': [{'name':'HB'}], 'runner_sha256':'abcd'}
        doc = t1.render(data).decode()
        self.assertIn('não** LB certificado', doc)
        self.assertIn('UNCERTIFIED', doc)
        self.assertIn('≥50%', doc)

    def test_prereg_selection_uses_n1_not_new_results(self):
        # Somente verifica dados históricos se presentes; nunca chama solver.
        if not (t1.RESULTS / 'n1-t5-diagnostico.csv').exists():
            self.skipTest('Repositório N1 indisponível')
        rows = t1.assemble()
        self.assertEqual(len(rows), 4)
        self.assertEqual({r['level'] for r in rows}, {1, 2})
        self.assertEqual({r['family'] for r in rows}, {'hb', 'bp-nao'})
        self.assertTrue(all(r['full_lp_reference'] is None for r in rows if r['level'] == 2))
        self.assertTrue(all(r['full_lp_reference'] > r['B0_reference'] for r in rows if r['level'] == 1))


if __name__ == '__main__':
    unittest.main()
