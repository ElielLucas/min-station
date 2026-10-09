"""Testes N1-T5 sem Gurobi: evidencias, métricas e comparação F3."""
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).with_name('run_n1_t5.py')
spec = importlib.util.spec_from_file_location('run_n1_t5', PATH)
t5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t5)


class N1T5OfflineTests(unittest.TestCase):
    def test_corpus_fixed(self):
        self.assertEqual(len(t5.NAMES), 18)
        self.assertEqual(t5.NAMES[-2:], ('SOURCE-g2','SOURCE-C5'))

    def test_prior_t3_evidence(self):
        status = t5.require_t3()
        self.assertTrue(status['validation_sha256'])
        self.assertTrue(status['source_sha256'])

    def test_f3_self_comparison(self):
        rows = t5.read_csv(t5.F3)
        self.assertEqual(len(rows), 16)
        for r in rows:
            self.assertIsNone(t5.equivalent_f3(r,r))

    def test_f3_tolerance_and_status(self):
        a = {'nome':'A','lp_fcc':'2.0','status':'ok'}
        b = {'nome':'A','lp_fcc':'2.0000005','status':'ok'}
        self.assertIsNone(t5.equivalent_f3(a,b))
        b['lp_fcc'] = '2.0001'
        self.assertIsNotNone(t5.equivalent_f3(a,b))
        b['lp_fcc'] = '2.0'
        b['status'] = 'excluida'
        self.assertIsNotNone(t5.equivalent_f3(a,b))

    def test_sharedterminal_negative_not_clipped(self):
        row = dict(opt=1.0,lp_comp=1.0,core_ip=1.0,
                   lp_fcc=.5,lp_fcc_k=1.,lp_fc3=.5,lp_fc3_k=1.)
        t5.compute_metrics(row)
        self.assertAlmostEqual(row['delta_fcc'], -0.5)
        self.assertEqual(row['gamma'],0.0)
        self.assertNotIn('rho_fcc',row)
        self.assertEqual(row['delta_trio'],0.0)

    def test_incremental_and_residual_fraction(self):
        row = dict(opt=7.,lp_comp=3.,core_ip=2.,lp_fcc=4.5,
                   lp_fcc_k=5.,lp_fc3=5.,lp_fc3_k=5.5)
        t5.compute_metrics(row)
        self.assertEqual(row['B0'],3.)
        self.assertEqual(row['gamma'],5.)
        self.assertEqual(row['delta_fcc_k'],2.)
        self.assertEqual(row['delta_trio'],.5)
        self.assertEqual(row['delta_trio_raw'],.5)
        self.assertEqual(row['rho_fc3_k'],(5.5-3.)/4.)
        self.assertEqual(row['rho_fcc_historico'],(4.5-3.)/5.)

    def test_missing_values_do_not_become_zero(self):
        row = dict(opt=3.,lp_comp=1.,core_ip=2.,lp_fcc='',
                   lp_fcc_k='',lp_fc3='',lp_fc3_k='')
        t5.compute_metrics(row)
        self.assertNotIn('delta_fcc',row)
        self.assertNotIn('delta_trio',row)


if __name__ == '__main__':
    unittest.main()
