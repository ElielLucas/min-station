"""FC-04: testes independentes do Gurobi e do solver.

Provas negativas de adulteração de instância, manifesto, código e relatório,
mais regressão contra o CSV histórico de escalabilidade sem modificá-lo.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import fc_instances as instances  # noqa: E402
from fc_integrity import (  # noqa: E402
    dump_json_bytes, generated_inventory, measured_scalability, relative_inside,
    scalability_from_csv, sha256_file,
)
from verify_comparison_artifacts import verify  # noqa: E402


class InstanceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = next(r for r in instances.load_manifest()
                       if r['nome'] == 'hb-q4-ndir2-p1-k1-L2.txt')

    def _fixture(self, tmp):
        root = Path(tmp)
        source = ROOT / self.row['caminho']
        dest = root / self.row['caminho']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
        return root, dest, dict(self.row)

    def test_audit01_real_pilot_manifest_recomputes_two_distinct_digests(self):
        inst = instances.load_instance(self.row)
        self.assertEqual(inst.instance_sha256, self.row['sha256'])
        self.assertEqual(inst.metadata_checks['sha256']['status'], 'MATCH')
        self.assertEqual(inst.metadata_checks['sha256_conteudo']['status'], 'MATCH')
        self.assertNotEqual(inst.instance_sha256, inst.instance_content_sha256)

    def test_audit01_missing_hash_is_explicit_and_actual_bytes_still_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, path, row = self._fixture(tmp)
            row['sha256'] = ''
            row['sha256_conteudo'] = ''
            value = instances.load_instance(row, root)
            self.assertEqual(value.instance_sha256, sha256_file(path))
            self.assertEqual(value.metadata_checks['sha256']['status'], 'NOT_DECLARED')

    def test_audit02_rejects_modified_bytes_even_if_instance_parser_accepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, path, row = self._fixture(tmp)
            path.write_bytes(path.read_bytes() + b'\n# injected\n')
            with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR.*sha256'):
                instances.load_instance(row, root)

    def test_audit02_rejects_modified_normalized_content_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _path, row = self._fixture(tmp)
            row['sha256_conteudo'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR.*sha256_conteudo'):
                instances.load_instance(row, root)

    def test_audit03_rejects_all_supported_metadata_mismatch(self):
        for field, fake in [('n', '17'), ('m', '7'), ('r_usado', '2'),
                            ('r_arquivo', '2'), ('arestas_nao_dirigidas', '25'),
                            ('arcos_arquivo', '47')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root, _path, row = self._fixture(tmp)
                row[field] = fake
                with self.assertRaisesRegex(ValueError, f'INTEGRITY_ERROR.*{field}'):
                    instances.load_instance(row, root)

    def test_audit03_m_from_source_header_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, path, row = self._fixture(tmp)
            changed = path.read_bytes().replace(b'M 48', b'M 47', 1)
            path.write_bytes(changed)
            row['sha256'] = hashlib.sha256(changed).hexdigest()
            row['sha256_conteudo'] = ''
            with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR.*M do arquivo'):
                instances.load_instance(row, root)

    def test_audit03_current_selected_pools_preserve_dimensions(self):
        for tier, expected in [('pilot', 2), ('main', 6), ('scalability', 10)]:
            with self.subTest(tier=tier):
                pool = instances.pool(tier)
                self.assertEqual(len(pool), expected)
                for inst in pool:
                    self.assertEqual(inst.metadata_checks['n']['status'], 'MATCH')
                    self.assertEqual(inst.metadata_checks['m']['status'], 'MATCH')
                    self.assertEqual(inst.metadata_checks['r']['status'], 'MATCH')

    def test_audit03_unsupported_metrics_are_labeled_not_silently_validated(self):
        inst = instances.load_instance(self.row)
        self.assertTrue(any(x['status'] == 'UNSUPPORTED'
                            for x in inst.metadata_checks.values()))


class ScalabilityTests(unittest.TestCase):
    def test_audit06_historical_csv_is_nine_of_ten_unique_instances(self):
        csv_path = ROOT / 'results/formulation-comparison/scalability-20261010T071119Z/results.csv'
        if not csv_path.exists():
            self.skipTest('CSV histórico não está incluído nesta cópia do repositório')
        results = scalability_from_csv(csv_path, expected_instances=instances.SCALABILITY_NAMES)
        self.assertEqual(results['tested_total'], 10)
        self.assertEqual(results['cap_exceeded_total'], 9)
        self.assertEqual(results['optimal_numeric_total'], 1)
        self.assertEqual(results['not_tested_total'], 0)
        self.assertTrue(results['not_evidence_about_unselected_instances'])

    def test_audit06_two_modalities_are_not_double_counted(self):
        rows = [dict(instance_name='a', formulation='fcc_k', modality=x, status='CAP_EXCEEDED')
                for x in ('A', 'B')]
        result = measured_scalability(rows, expected_instances=('a', 'b', 'c'))
        self.assertEqual(result['cap_exceeded_total'], 1)
        self.assertEqual(result['tested_total'], 1)
        self.assertEqual(result['not_tested_total'], 2)

    def test_audit06_mixed_case_is_inconclusive(self):
        rows = [dict(instance_name='a', formulation='fcc_k', status=x)
                for x in ('CAP_EXCEEDED', 'OPTIMAL')]
        result = measured_scalability(rows)
        self.assertEqual(result['cap_exceeded_total'], 0)
        self.assertEqual(result['inconclusive_total'], 1)

    def test_audit06_lp_only_is_measured_not_silently_unobserved(self):
        rows = [dict(instance_name='a', formulation='lp_fcc_k', modality='A',
                     status='NOT_MEASURED_CAP_EXCEEDED')]
        summary = measured_scalability(rows, expected_instances=('a', 'b'))
        self.assertEqual(summary['tested_total'], 1)
        self.assertEqual(summary['cap_exceeded_total'], 1)
        self.assertEqual(summary['not_tested_total'], 1)

    def test_audit06_conflicting_lp_and_mip_do_not_count_as_cap(self):
        rows = [dict(instance_name='a', formulation=f, status=s)
                for f, s in [('lp_fcc_k', 'CAP_EXCEEDED'),
                             ('fcc_k', 'OPTIMAL')]]
        summary = measured_scalability(rows, expected_instances=('a',))
        self.assertEqual(summary['cap_exceeded_total'], 0)
        self.assertEqual(summary['inconclusive_total'], 1)

    def test_audit06_no_fcc_observation_is_not_tested(self):
        rows = [dict(instance_name='a', formulation='comp_mip', status='OPTIMAL')]
        result = measured_scalability(rows, expected_instances=('a',))
        self.assertEqual(result['not_tested_total'], 1)

    def test_audit06_extra_instance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'não declaradas'):
            measured_scalability([dict(instance_name='x', formulation='fcc_k', status='OPTIMAL')],
                                 expected_instances=('a',))


class AuditVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_dir = self.root / 'results/formulation-comparison/try'
        self.run_dir.mkdir(parents=True)
        (self.root / 'code.py').write_text('print(1)\n', encoding='utf-8')
        (self.root / 'instance.txt').write_text('instance data\n', encoding='utf-8')
        (self.run_dir / 'results.csv').write_text(
            'instance_name,formulation,status\na,fcc_k,CAP_EXCEEDED\n', encoding='utf-8')
        (self.run_dir / 'evolution.csv').write_text('instance_name\n', encoding='utf-8')
        (self.run_dir / 'run.log').write_text('run\n', encoding='utf-8')
        self.source = self.root / 'code.py'
        self.input = self.root / 'instance.txt'
        self.outputs = [self.run_dir / f for f in ('results.csv', 'evolution.csv', 'run.log')]
        self.manifest = self._manifest()
        self._publish()

    def _manifest(self):
        return {
            'artifact_schema': 'FC04-v1', 'tier': 'pilot',
            'code_files_sha256': {'code.py': sha256_file(self.source)},
            'input_files_sha256': {'instance.txt': sha256_file(self.input)},
            'generated_files_sha256': generated_inventory(self.root, self.outputs),
            'generated_files': [f.relative_to(self.root).as_posix() for f in self.outputs],
            'instances': [{'nome': 'a', 'caminho': 'instance.txt',
                           'instance_sha256': sha256_file(self.input)}],
        }

    def _publish(self):
        encoded = dump_json_bytes(self.manifest)
        (self.run_dir / 'manifest.json').write_bytes(encoded)
        (self.run_dir / 'manifest.sha256').write_text(
            hashlib.sha256(encoded).hexdigest() + '  manifest.json\n', encoding='ascii')

    def test_audit04_audit05_all_bytes_roundtrip_pass(self):
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertTrue(ok, issues)

    def test_audit05_relative_run_path_passes(self):
        relative = self.run_dir.relative_to(self.root)
        # Executar a verificação a partir do diretório raiz, como no README.
        import os
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            ok, issues = verify(relative, root=self.root)
        finally:
            os.chdir(previous)
        self.assertTrue(ok, issues)

    def test_audit05_modified_csv_detected(self):
        (self.run_dir / 'results.csv').write_text('tampered\n', encoding='utf-8')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('HASH_MISMATCH', ' '.join(issues))

    def test_audit05_modified_source_detected(self):
        self.source.write_text('print(2)\n', encoding='utf-8')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('code_files', ' '.join(issues))

    def test_audit05_modified_input_detected(self):
        self.input.write_text('changed\n', encoding='utf-8')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('input_files', ' '.join(issues))

    def test_audit05_missing_generated_csv_detected(self):
        (self.run_dir / 'results.csv').unlink()
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('MISSING_OR_OUTSIDE', ' '.join(issues))

    def test_audit05_truncated_manifest_detected(self):
        (self.run_dir / 'manifest.json').write_text('{', encoding='utf-8')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('INVALID_MANIFEST', ' '.join(issues))

    def test_audit05_manifest_checksum_mismatch_detected(self):
        with (self.run_dir / 'manifest.json').open('ab') as fh:
            fh.write(b' ')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('MANIFEST_CHECKSUM_MISMATCH', issues)

    def test_audit05_untracked_postfinalization_plot_detected(self):
        (self.run_dir / 'plot.png').write_bytes(b'fake plot')
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('UNTRACKED_OUTPUTS', ' '.join(issues))

    def test_audit05_path_traversal_detected(self):
        self.manifest['generated_files_sha256']['../../secret.txt'] = '0' * 64
        self.manifest['generated_files'].append('../../secret.txt')
        self._publish()
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('INVALID_PATH', ' '.join(issues))

    def test_audit06_summary_recomputed_by_independent_verifier(self):
        self.manifest['tier'] = 'scalability'
        summary = measured_scalability(
            [{'instance_name': 'a', 'formulation': 'fcc_k', 'status': 'CAP_EXCEEDED'}],
            expected_instances=('a',))
        summary_path = self.run_dir / 'scalability_summary.json'
        summary_path.write_bytes(dump_json_bytes(summary))
        self.outputs.append(summary_path)
        self.manifest['generated_files_sha256'] = generated_inventory(self.root, self.outputs)
        self.manifest['generated_files'] = [f.relative_to(self.root).as_posix()
                                            for f in self.outputs]
        self._publish()
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertTrue(ok, issues)
        summary['cap_exceeded_total'] = 2
        summary_path.write_bytes(dump_json_bytes(summary))
        # Mesmo que se atualize a lista de hashes, a contagem tem verificação semântica.
        self.manifest['generated_files_sha256'] = generated_inventory(self.root, self.outputs)
        self._publish()
        ok, issues = verify(self.run_dir, root=self.root)
        self.assertFalse(ok)
        self.assertIn('SCALABILITY_COUNT_MISMATCH: cap_exceeded_total', issues)

    def test_audit04_rejects_file_outside_root(self):
        with tempfile.TemporaryDirectory() as out:
            outside = Path(out) / 'a.txt'
            outside.write_text('x')
            with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR'):
                relative_inside(self.root, outside)


if __name__ == '__main__':
    unittest.main()
