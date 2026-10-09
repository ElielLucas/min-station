"""Testes N1-T6 sem Gurobi. Nao gera pares antes do freeze."""
import importlib.util
import unittest
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('run_n1_t6', HERE / 'run_n1_t6.py')
import sys
sys.path.insert(0, str(HERE))
t6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t6)


class T6Offline(unittest.TestCase):
    def test_protocol_is_bounded_and_no_random_search(self):
        self.assertGreater(len(t6.RECIPES), 0)
        self.assertLessEqual(len(t6.RECIPES), 12)
        self.assertEqual(len({r['id'] for r in t6.RECIPES}), len(t6.RECIPES))
        self.assertEqual({r['family'] for r in t6.RECIPES}, {'tri','f2','sec59'})
        for recipe in t6.RECIPES:
            self.assertNotEqual(set(recipe['remove']), set(recipe['add']))
            self.assertTrue(recipe['obstruction'])
            self.assertTrue(recipe['change'])

    def test_t5_gate_actually_fires(self):
        gate = t6.validate_previous()
        self.assertTrue(gate['triggered'])
        self.assertEqual(gate['families'], ['sec59'])
        self.assertEqual(gate['n_distinct'], 1)

    def test_existing_evidence_not_modified_by_module(self):
        from run_n1_t5 import OUT, FREEZE, WITNESSES
        self.assertEqual(len(t6.read_csv(OUT)), 18)
        self.assertTrue(FREEZE.exists())
        self.assertEqual(t6.load(WITNESSES)['state'],'COMPUTATIONALLY VERIFIED')

    def test_graphs_only_after_freeze(self):
        if not t6.FREEZE.exists():
            self.skipTest('N1-T6 ainda nao congelada: nao gerar grafos antes do freeze')
        t6.checked_freeze()
        for recipe in t6.RECIPES:
            a, b = t6.build_pair(recipe)
            t6.pair_structure({'recipe': recipe,'graphs':[a,b]})
            self.assertLessEqual(len(a['V']),10)
            self.assertEqual((len(a['S']),len(a['T']),a['r']), (3,3,1))
            self.assertEqual((a['V'],a['S'],a['T'],a['r']),
                             (b['V'],b['S'],b['T'],b['r']))
            self.assertEqual(len(a['edges']),len(b['edges']))

    def test_certificates_only_after_generation(self):
        if not t6.CERT.exists():
            self.skipTest('Aguardando gerar/certificar pares')
        pairs, cert = t6.checked_certificates()
        self.assertEqual(len(pairs['pairs']),len(t6.RECIPES))
        self.assertEqual(len(cert['pairs']),len(t6.RECIPES))
        for p in cert['pairs']:
            for v in p['variants']:
                if v['status']=='CERTIFIED':
                    self.assertIsInstance(v['opt'], int)
                    self.assertIsNotNone(v['C_star'])

    def test_atomic_checkpoint_preserves_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            original=t6.MEASURED
            try:
                t6.MEASURED=Path(temp) / 'checkpoint.csv'
                row={k:'' for k in t6.FIELDS}
                row.update(name='T6-TRI-01-obstruction', pair_id='T6-TRI-01',
                           graph_hash='testhash',pair_status='CERTIFIED',opt=2)
                t6.write_checkpoint([row])
                saved=t6.read_csv(t6.MEASURED)
                self.assertEqual(len(saved),1)
                self.assertEqual(saved[0]['opt'],'2')
                self.assertFalse(t6.MEASURED.with_suffix('.csv.tmp').exists())
            finally:
                t6.MEASURED=original

    def test_report_only_with_all_rows(self):
        if not t6.MEASURED.exists():
            self.skipTest('Ainda sem resultados de LP')
        rows = t6.read_csv(t6.MEASURED)
        self.assertLessEqual(len(rows), 2*len(t6.RECIPES))
        self.assertEqual([r['name'] for r in rows],
                         [x for recipe in t6.RECIPES for x in
                          (recipe['id']+'-obstruction',recipe['id']+'-control')][:len(rows)])


if __name__ == '__main__':
    unittest.main()
