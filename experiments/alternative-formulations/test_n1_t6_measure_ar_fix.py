"""Testes offline do adaptador de A_r sem Gurobi e sem gravar artefatos."""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_n1_t6_measure_ar_fix as fix


class TestMeasureArFix(unittest.TestCase):
    def test_listas_json_viram_tuplas_sem_mutacao(self):
        graph = {'name':'g', 'graph_hash':'sha-original', 'A_r':[['s1','a'],['a','t1']]}
        clone = fix.normalize_arcs_for_solver(graph)
        self.assertEqual(clone['A_r'], [('s1','a'),('a','t1')])
        self.assertEqual(graph['A_r'], [['s1','a'],['a','t1']])
        self.assertEqual(clone['graph_hash'], graph['graph_hash'])
        self.assertIsNot(clone, graph)
        self.assertEqual({*clone['A_r']}, {('s1','a'),('a','t1')})

    def test_arco_invalido_falha(self):
        with self.assertRaises(ValueError):
            fix.normalize_arcs_for_solver({'A_r':[['s1']]})

    def test_sem_hashseed_recusa(self):
        with patch.dict(os.environ, {'PYTHONHASHSEED':'1'}):
            with self.assertRaises(RuntimeError):
                fix.measure()

    def test_runner_original_e_restaurado(self):
        original = fix.t6.measure_one
        graph = {'A_r':[['s1','a']], 'graph_hash':'hash'}
        observations = []
        def fake_runner():
            observations.append(fix.t6.measure_one(graph, {}, 'CERTIFIED'))
        def fake_measure_one(g, *args):
            return g['A_r']
        with patch.dict(os.environ, {'PYTHONHASHSEED':'0'}), \
             patch.object(fix.t6, 'checked_certificates', return_value=(None,None)), \
             patch.object(fix.t6, 'measure_one', fake_measure_one), \
             patch.object(fix.t6, 'measure', fake_runner):
            fix.measure()
            self.assertIs(fix.t6.measure_one, fake_measure_one)
        self.assertEqual(observations, [[('s1','a')]])
        self.assertIs(fix.t6.measure_one, original)


if __name__ == '__main__':
    unittest.main()
