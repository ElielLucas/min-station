"""AS00: testes derivados dos cinco critérios de aceite (sem solver)."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments' / 'benchmark'))
from as00_families import raw_family_keys  # noqa: E402
from as00_preregister import make_protocol, write_preregistration  # noqa: E402
from as00_protocol import (PILOT, build_universe, fingerprint_case,
                         manifest_rows, retain_outcome)  # noqa: E402


class TestAS00(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.universe = build_universe(ROOT)
        cls.cases = {c['name']: c for c in cls.universe['cases']}
        cls.manifest = {r['nome']: r for r in manifest_rows(ROOT)}

    def test_as00_01_identidade_completa_do_manifesto(self):
        # Cada campo é requerido para auditoria e não pode virar uma string vazia.
        self.assertEqual(len(self.cases), 31)
        self.assertEqual(self.universe['counts'], {'desenvolvimento': 14, 'avaliacao': 17})
        for c in self.cases.values():
            for key in ('source_file', 'source_sha256', 'graph_hash', 'S_hash',
                        'T_hash', 'A_r_hash', 'raw_graph_id', 'family_id',
                        'reach_equivalence_id'):
                self.assertTrue(c[key], (c['name'], key))
            self.assertEqual(len(c['graph_hash']), 64)
            self.assertEqual(len(c['A_r_hash']), 64)
            self.assertGreater(c['n'], 0)
            self.assertGreater(c['m'], 0)
            self.assertGreater(c['r'], 0)

    def test_as00_01_equivalencia_entre_aliases_e_nao_equivalencia(self):
        a = fingerprint_case(self.manifest['hc9u.txt'], ROOT, {})
        b = fingerprint_case(self.manifest['puc-hc9u-seed-r1.txt'], ROOT, {})
        c = fingerprint_case(self.manifest['hc10p.txt'], ROOT, {})
        d = fingerprint_case(self.manifest['puc-hc10p-seed-r1.txt'], ROOT, {})
        legacy_cc = fingerprint_case(self.manifest['cc12-2u.txt'], ROOT, {})
        new_cc = fingerprint_case(self.manifest['puc-cc12-2u-seed-r1.txt'], ROOT, {})
        self.assertEqual(a['reach_equivalence_id'], b['reach_equivalence_id'])
        self.assertEqual(c['reach_equivalence_id'], d['reach_equivalence_id'])
        self.assertNotEqual(legacy_cc['reach_equivalence_id'], new_cc['reach_equivalence_id'])
        self.assertNotEqual(a['source_sha256'], b['source_sha256'])

    def test_as00_01_integridade_rejeita_hash_de_arquivo_incorreto(self):
        row = dict(self.manifest['puc-cc9-2p-seed-r1.txt'])
        row['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR'):
            fingerprint_case(row, ROOT, {})

    def test_as00_01_rejeita_alcance_incoerente_do_manifesto(self):
        row = dict(self.manifest['puc-cc9-2p-seed-r1.txt'])
        row['n_arcos_alcance'] = '1'
        with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR: n_arcos_alcance'):
            fingerprint_case(row, ROOT, {})

    def test_as00_02_cap_nao_apaga_instancia(self):
        count = len(self.universe['cases'])
        after = retain_outcome(self.universe['cases'], 'puc-w3c571-seed-r1',
                               'NOT_MEASURED_CAP')
        self.assertEqual(len(after), count)
        self.assertEqual(next(c['outcome'] for c in after
                              if c['name'] == 'puc-w3c571-seed-r1'), 'NOT_MEASURED_CAP')
        self.assertTrue(next(c['comparison_eligible'] for c in after
                             if c['name'] == 'puc-w3c571-seed-r1'))
        self.assertEqual(len([c for c in after if c['outcome'] == 'NOT_RUN']), count - 1)

    def test_as00_02_memoria_e_erro_nao_imputam_zero(self):
        for status in ('NOT_MEASURED_INPUT', 'NOT_MEASURED_MEMORY',
                       'NOT_MEASURED_BUDGET', 'ERROR'):
            after = retain_outcome(self.universe['cases'], PILOT[0], status)
            self.assertEqual(len(after), 31)
            self.assertEqual(next(c for c in after if c['name'] == PILOT[0])['outcome'], status)
        with self.assertRaisesRegex(ValueError, 'status não reconhecido'):
            retain_outcome(self.universe['cases'], PILOT[0], '0')

    def test_as00_03_mapf_room_m10_e_m25_sao_relacionados(self):
        dev = self.cases['mapf-room-32-32-4-m10-f8']
        eva = self.cases['mapf-room-32-32-4-m25-f4-rho']
        self.assertEqual(dev['family_id'], eva['family_id'])
        self.assertEqual(dev['raw_graph_id'], eva['raw_graph_id'])
        self.assertEqual(dev['split'], 'desenvolvimento')
        self.assertEqual(eva['split'], 'avaliacao')
        self.assertEqual(eva['independence'], 'RELATED_SCENARIO')
        self.assertIn(dev['name'], eva['related_development'])

    def test_as00_03_sem_proveniencia_nao_declara_independencia(self):
        fake_mapf = {'nome': 'mapf-fake.txt', 'caminho': 'instances/benchmark-v1/mapf/mapf-fake.txt',
                     'instancia_original': 'example.map'}
        with self.assertRaisesRegex(ValueError, 'Proveniência MAPF insuficiente'):
            raw_family_keys(fake_mapf, {})

    def test_as00_04_piloto_e_bracos_congelados(self):
        protocol = make_protocol(self.universe)
        self.assertEqual(set(protocol['pilot_cases']), set(PILOT))
        self.assertTrue(all(self.cases[n]['split'] == 'desenvolvimento' for n in PILOT))
        self.assertEqual(protocol['mandatory_initial_arms'],
                         ['U_NO_K', 'U_PLUS_K', 'A2_PLUS_K'])
        self.assertEqual(protocol['seeds']['reproducibility'], [42, 43, 44])
        self.assertEqual(protocol['budget']['mip_pilot_seconds_per_arm'], [300, 600])
        self.assertEqual(protocol['budget']['final_wall_seconds_per_arm'], 3600)
        self.assertEqual(protocol['promotion']['minimum_independent_raw_graphs_with_reproducible_gain'], 2)
        self.assertFalse(protocol['execution_authorized'])

    def test_as00_04_selecao_final_congelada_10_grafos_independentes(self):
        protocol = make_protocol(self.universe)
        chosen = protocol['final_evaluation_cases']
        self.assertEqual(len(chosen), 10)
        self.assertEqual(len({self.cases[n]['raw_graph_id'] for n in chosen}), 10)
        self.assertTrue(all(self.cases[n]['independence'] == 'INDEPENDENT_RAW_SOURCE'
                            for n in chosen))
        self.assertEqual(len(protocol['evaluation_support_cases']), 7)
        self.assertNotIn('mapf-room-32-32-4-m25-f4-rho', chosen)

    def test_as00_04_preregistro_digest_e_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'as00-v1'
            write_preregistration(self.universe, output)
            raw = (output / 'protocol.json').read_bytes()
            expected = hashlib.sha256(raw).hexdigest()
            self.assertEqual(expected, (output / 'protocol.sha256').read_text().split()[0])
            payload = json.loads(raw)
            self.assertEqual(payload['counts'], {'desenvolvimento': 14, 'avaliacao': 17})
            self.assertIn(expected, (output / 'pre_register.md').read_text())
            with self.assertRaises(FileExistsError):
                write_preregistration(self.universe, output)
            self.assertEqual((output / 'protocol.json').read_bytes(), raw)

    def test_as00_05_artefatos_n1_n2_fc_preservados(self):
        historic = [ROOT / 'results/formulation-comparison/main-20261011T005611Z/results.csv',
                    ROOT / 'results/alternative-formulations/n2-t5-prospectivo/n2-t5-manifest.json',
                    ROOT / 'instances/manifest.csv']
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in historic]
        with tempfile.TemporaryDirectory() as td:
            write_preregistration(self.universe, Path(td) / 'new-as00')
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in historic])

    def test_as00_01_caso_retirado_e_rejeitado(self):
        # O snapshot acordado tem 31 D/A, e falta silenciosa não é aceitável.
        from unittest.mock import patch
        with patch('as00_protocol.manifest_rows', return_value=[r for r in manifest_rows(ROOT)
                    if r['nome'] != 'puc-w3c571-seed-r1.txt']):
            with self.assertRaisesRegex(ValueError, 'universo D/A diverge'):
                build_universe(ROOT)


if __name__ == '__main__':
    unittest.main()
