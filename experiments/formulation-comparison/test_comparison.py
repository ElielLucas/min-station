"""Testes da comparação base × F-CC+K.

Requer Gurobi (não ignora testes se faltar; falha explicitamente). Execute:
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison \
    -p test_comparison.py -v

Reproduz, como regressão, os valores históricos congelados de N1-T5 para
`HB-q4-ndir2-p1` (`results/alternative-formulations/n1-t5-diagnostico.csv`):
`lp_base=1/3`, `lp_comp=1`, `lp_fcc_k=2`, `opt=2`. Não reexecuta N1/N2 nem
altera seus arquivos.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import fc_config as fcfg  # noqa: E402
import fc_core as fcore  # noqa: E402
import fc_instances as fi  # noqa: E402
import fc_reporting as rep  # noqa: E402
from fc_core import EvolutionTracker  # noqa: E402

HB_Q4_ROW = {
    'nome': 'hb-q4-ndir2-p1-k1-L2.txt',
    'caminho': 'instances/estrutural/hb/hb-q4-ndir2-p1-k1-L2.txt',
    'classe': 'estrutural', 'r': '1', 'sha256_conteudo': '', 'arestas_nao_dirigidas': '24',
    'n': '16',
}
BP_Q2_B2_ROW = {
    'nome': 'bp-nao-q2-B2-s0.txt', 'caminho': 'instances/estrutural/bp/bp-nao-q2-B2-s0.txt',
    'classe': 'estrutural', 'r': '1', 'sha256_conteudo': '', 'arestas_nao_dirigidas': '4', 'n': '16',
}

PILOT_CFG = fcfg.ExperimentConfig(time_limit_s=60.0, lp_time_limit_s=30.0)


class ConfigTests(unittest.TestCase):
    def test_rejects_invalid_values(self):
        for bad in (dict(threads=0), dict(time_limit_s=-1), dict(lp_time_limit_s=0),
                   dict(max_w=0), dict(checkpoints_s=(5.0, 1.0)), dict(modalities=('X',))):
            with self.assertRaises(ValueError):
                fcfg.ExperimentConfig(**bad)

    def test_as_dict_reproducible(self):
        cfg = fcfg.ExperimentConfig(threads=2, seed=7)
        self.assertEqual(cfg.as_dict(), fcfg.ExperimentConfig(threads=2, seed=7).as_dict())

    def test_environment_manifest_reports_real_versions(self):
        env = fcfg.environment_manifest()
        self.assertIn('python_version', env)
        self.assertIn('gurobi_available', env)


class EvolutionTrackerTests(unittest.TestCase):
    """Lógica de checkpoint testável sem Gurobi (item 8: coleta de métricas)."""

    def test_marks_crossed_once_not_interpolated(self):
        tracker = EvolutionTracker((1.0, 5.0, 10.0))
        tracker.on_periodic(0.5, lb=0.0, ub=None, nodes=0, work=0.0)
        self.assertEqual(tracker.points, [])
        tracker.on_periodic(1.2, lb=1.0, ub=5.0, nodes=2, work=0.1)
        self.assertEqual(len(tracker.points), 1)
        self.assertEqual(tracker.points[0].mark_s, 1.0)
        self.assertEqual(tracker.points[0].observed_time_s, 1.2)  # tempo real, não o marco
        tracker.on_periodic(12.0, lb=3.0, ub=3.0, nodes=9, work=1.0)
        self.assertEqual([p.mark_s for p in tracker.points], [1.0, 5.0, 10.0])
        tracker.on_periodic(20.0, lb=3.0, ub=3.0, nodes=9, work=2.0)
        self.assertEqual(len(tracker.points), 3)  # marcos não se repetem

    def test_incumbent_tracks_first_and_best_time(self):
        tracker = EvolutionTracker((1.0,))
        self.assertIsNone(tracker.first_feasible_time)
        tracker.on_incumbent(2.0, 10.0)
        self.assertEqual(tracker.first_feasible_time, 2.0)
        self.assertEqual(tracker.best_time, 2.0)
        tracker.on_incumbent(3.0, 10.0)  # mesmo valor: não é melhoria
        self.assertEqual(tracker.best_time, 2.0)
        tracker.on_incumbent(4.0, 4.0)  # melhora estrita
        self.assertEqual(tracker.best_time, 4.0)
        self.assertEqual(tracker.first_feasible_time, 2.0)  # não muda após o primeiro


class InstancePoolTests(unittest.TestCase):
    def test_tiers_are_disjoint_pilot_subset_of_main(self):
        pilot = {i.nome for i in fi.pool('pilot')}
        main = {i.nome for i in fi.pool('main')}
        scal = {i.nome for i in fi.pool('scalability')}
        self.assertTrue(pilot <= main)
        self.assertEqual(pilot & scal, set())

    def test_excluded_instances_never_selected(self):
        for tier in ('pilot', 'main', 'scalability'):
            names = {i.nome for i in fi.pool(tier)}
            self.assertFalse(names & fi.EXCLUDED_NAMES)

    def test_load_instance_identity_hash_matches_manifest(self):
        rows = {r['nome']: r for r in fi.load_manifest()}
        row = rows['hb-q4-ndir2-p1-k1-L2.txt']
        inst = fi.load_instance(row)
        self.assertEqual(inst.instance_sha256, row['sha256_conteudo'])
        self.assertEqual(inst.n, 16)
        self.assertEqual(inst.m, 6)

    def test_tractability_probe_matches_known_boundary(self):
        # hb-q4 (n=16) é conhecido tratável (N1); sc-gf2-k3 (n=21) é conhecido
        # acima do cap (nota de N1 em provas-fcc-fc3.md / Analise-consolidada).
        tratavel_inst = fi.load_instance(HB_Q4_ROW)
        ok, n_w, motivo = fi.tractability_probe(tratavel_inst, max_w=200000)
        self.assertTrue(ok, motivo)
        self.assertEqual(n_w, 9341)  # mesmo n_W_raw do congelamento N1-T5
        rows = {r['nome']: r for r in fi.load_manifest()}
        intratavel_inst = fi.load_instance(rows['sc-gf2-k3.txt'])
        ok, _n_w, motivo = fi.tractability_probe(intratavel_inst, max_w=200000, wall_guard_s=20)
        self.assertFalse(ok)
        self.assertIn('CAP_EXCEEDED', motivo)


class ModalityATests(unittest.TestCase):
    """Regressão contra os valores congelados de N1-T5 para HB-q4-ndir2-p1."""

    def test_reproduces_frozen_n1_values(self):
        inst = fi.load_instance(HB_Q4_ROW)
        results = fcore.run_modality_a(inst, PILOT_CFG)
        self.assertAlmostEqual(results['lp_base'].value, 1 / 3, places=7)
        self.assertAlmostEqual(results['lp_comp'].value, 1.0, places=7)
        self.assertAlmostEqual(results['lp_fcc_k'].value, 2.0, places=7)
        for r in results.values():
            if hasattr(r, 'certification'):
                self.assertEqual(r.certification, fcore.CERTIFIED_LP)
        # Monotonicidade exigida pela cadeia base <= COMP <= F-CC+K <= OPT (P2, N1).
        self.assertLessEqual(results['lp_base'].value, results['lp_comp'].value + 1e-9)
        self.assertLessEqual(results['lp_comp'].value, results['lp_fcc_k'].value + 1e-9)

    def test_cap_exceeded_is_explicit_never_zero(self):
        rows = {r['nome']: r for r in fi.load_manifest()}
        inst = fi.load_instance(rows['sc-gf2-k3.txt'])
        cfg = fcfg.ExperimentConfig(time_limit_s=60.0, lp_time_limit_s=30.0, max_w=200000)
        results = fcore.run_modality_a(inst, cfg)
        r = results['lp_fcc_k']
        self.assertEqual(r.certification, fcore.NOT_MEASURED_CAP_EXCEEDED)
        self.assertIsNone(r.value)  # nunca 0 nem um palpite


class ModalityBTests(unittest.TestCase):
    def test_baseline_and_fcc_k_agree_on_known_optimum_and_are_validated(self):
        inst = fi.load_instance(HB_Q4_ROW)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        rf = fcore.run_modality_b_fcc_k(inst, PILOT_CFG)
        self.assertEqual(rb.status_name, 'OPTIMAL')
        self.assertEqual(rf.status_name, 'OPTIMAL')
        self.assertAlmostEqual(rb.objective_ub, 2.0, places=7)
        self.assertAlmostEqual(rf.objective_ub, 2.0, places=7)
        self.assertEqual(rb.objective_ub, rb.objective_lb)  # otimalidade: UB=LB exatos
        self.assertEqual(rf.objective_ub, rf.objective_lb)
        self.assertEqual(rb.certification, fcore.CERTIFIED_MIP_OPTIMAL)
        self.assertEqual(rf.certification, fcore.CERTIFIED_MIP_OPTIMAL)
        self.assertTrue(rb.physically_validated)
        self.assertTrue(rf.physically_validated)
        self.assertEqual(rb.gap_abs, 0.0)
        self.assertEqual(rf.gap_abs, 0.0)

    def test_installed_set_identity_between_formulations_uses_same_instance(self):
        """Mesma instância (S,T,V,adj,r) para as duas formulações (item 1)."""
        inst = fi.load_instance(HB_Q4_ROW)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        rf = fcore.run_modality_b_fcc_k(inst, PILOT_CFG)
        # Ambas as soluções, obtidas de modelos diferentes sobre a MESMA
        # instância, devem ser fisicamente viáveis segundo o MESMO oráculo.
        self.assertTrue(fcore._validate(inst, set(rb.installed)))
        self.assertTrue(fcore._validate(inst, set(rf.installed)))

    def test_invalid_installation_is_rejected_by_oracle(self):
        inst = fi.load_instance(HB_Q4_ROW)
        self.assertFalse(fcore._validate(inst, set()))  # vazio não resolve esta instância

    def test_rmp_style_objective_is_never_produced_here(self):
        """Proibição explícita (item 4): nada nesta comparação usa RMP/geração
        de colunas da N2; os únicos valores possíveis são LP exato ou MIP
        completo. Nenhum MIPResult tem o rótulo UNCERTIFIED que a N2 usava
        para o objetivo do master restrito."""
        inst = fi.load_instance(HB_Q4_ROW)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        rf = fcore.run_modality_b_fcc_k(inst, PILOT_CFG)
        for r in (rb, rf):
            self.assertIn(r.certification, (fcore.CERTIFIED_MIP_OPTIMAL,
                                            fcore.CERTIFIED_MIP_BOUND,
                                            fcore.UNCERTIFIED_NO_INCUMBENT))
            self.assertNotEqual(r.certification, 'CERTIFIED')  # nunca o rótulo genérico
        import fc_core
        src = Path(fc_core.__file__).read_text(encoding='utf-8')
        self.assertNotIn('RestrictedMaster', src)
        self.assertNotIn('n2_t2b', src)

    def test_gap_calculation_and_percentage_safety(self):
        inst = fi.load_instance(HB_Q4_ROW)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        self.assertEqual(rb.gap_abs, rb.objective_ub - rb.objective_lb)
        if rb.objective_ub and rb.objective_ub > 1e-9:
            self.assertAlmostEqual(rb.gap_rel, rb.gap_abs / rb.objective_ub, places=9)

    def test_gap_rel_is_none_when_denominator_inadequate(self):
        from dataclasses import replace
        inst = fi.load_instance(HB_Q4_ROW)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        zero_ub = replace(rb, objective_ub=0.0, objective_lb=0.0, gap_abs=0.0, gap_rel=None)
        self.assertIsNone(zero_ub.gap_rel)  # 0/0 nunca vira um número fabricado

    def test_timeout_is_handled_without_fabricating_optimum(self):
        inst = fi.load_instance(HB_Q4_ROW)
        tight = fcfg.ExperimentConfig(time_limit_s=0.0001, lp_time_limit_s=1.0)
        r = fcore.run_modality_b_fcc_k(inst, tight)
        self.assertIn(r.status_name, ('TIME_LIMIT', 'OPTIMAL'))
        if r.status_name == 'TIME_LIMIT':
            self.assertIn(r.certification,
                          (fcore.CERTIFIED_MIP_BOUND, fcore.UNCERTIFIED_NO_INCUMBENT))
            self.assertIsNone(r.time_to_proof_s)  # sem prova, sem tempo de prova

    def test_budget_is_forwarded_and_not_exceeded_on_lp(self):
        inst = fi.load_instance(HB_Q4_ROW)
        cfg = fcfg.ExperimentConfig(time_limit_s=60.0, lp_time_limit_s=5.0)
        results = fcore.run_modality_a(inst, cfg)
        for key in ('lp_base', 'lp_comp'):
            self.assertLessEqual(results[key].time_s, 5.0 + 2.0)  # folga de overhead, não travou


class ReportingTests(unittest.TestCase):
    def test_csv_rows_and_evolution_are_generated_and_integral(self):
        inst = fi.load_instance(HB_Q4_ROW)
        a = fcore.run_modality_a(inst, PILOT_CFG)
        rb = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        rf = fcore.run_modality_b_fcc_k(inst, PILOT_CFG)
        rows, evolution = rep.rows_for_instance(inst, a, rb, rf)
        self.assertEqual(len(rows), 5)  # lp_base, lp_comp, lp_fcc_k, baseline, fcc_k
        for row in rows:
            for field in rep.RESULTS_FIELDS:
                self.assertIn(field, row)
        formulations = {row['formulation'] for row in rows}
        self.assertEqual(formulations, {'baseline', 'fcc_k'})
        self.assertTrue(evolution)
        for point in evolution:
            for field in rep.EVOLUTION_FIELDS:
                self.assertIn(field, point)

    def test_write_csv_does_not_overwrite_other_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = Path(tmp) / 'run1' / 'results.csv'
            p2 = Path(tmp) / 'run2' / 'results.csv'
            rep.write_csv(p1, ['a'], [{'a': 1}])
            rep.write_csv(p2, ['a'], [{'a': 2}])
            # read_text() traduz \r\n -> \n (newline universal); o que importa
            # é que cada arquivo tem só a própria linha, sem se misturar.
            self.assertEqual(p1.read_text(), 'a\n1\n')
            self.assertEqual(p2.read_text(), 'a\n2\n')

    def test_manifest_contains_commit_hashes_config_and_limitations(self):
        inst = fi.load_instance(HB_Q4_ROW)
        env = fcfg.environment_manifest()
        manifest = rep.reproducibility_manifest(ROOT, PILOT_CFG, [inst], env,
                                                commands=['cmd'], limitations=['lim'],
                                                generated_files=['x.csv'])
        self.assertIn('git', manifest)
        self.assertIn('commit', manifest['git'])
        self.assertEqual(manifest['config'], PILOT_CFG.as_dict())
        self.assertIn('baseline.py', manifest['reused_files_sha256'])
        self.assertIn('experiments/alternative-formulations/fcc_k.py',
                      manifest['reused_files_sha256'])
        self.assertEqual(manifest['instances'][0]['nome'], inst.nome)
        self.assertEqual(manifest['limitations'], ['lim'])


class ConfigReproducibilityEndToEndTest(unittest.TestCase):
    def test_same_config_same_instance_gives_same_optimum_twice(self):
        inst = fi.load_instance(HB_Q4_ROW)
        r1 = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        r2 = fcore.run_modality_b_baseline(inst, PILOT_CFG)
        self.assertEqual(r1.objective_ub, r2.objective_ub)
        self.assertEqual(r1.status_name, r2.status_name)


if __name__ == '__main__':
    unittest.main()
