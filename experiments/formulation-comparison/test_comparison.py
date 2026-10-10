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
import hashlib
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
from fc_pairing import assess_primary_pair  # noqa: E402

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


class ModuleIsolationTests(unittest.TestCase):
    """Evita importar fc_* antigos de alternative-formulations por engano."""

    def test_modules_come_from_formulation_comparison(self):
        for module in (fcfg, fcore, fi, rep):
            with self.subTest(module=module.__name__):
                self.assertEqual(Path(module.__file__).resolve().parent, HERE,
                                 f'Módulo sombreado: {module.__name__} em {module.__file__}')


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
        self.assertEqual(inst.instance_sha256, row['sha256'])
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
                self.assertIsNotNone(r.solver_runtime_s)
                self.assertIsNotNone(r.work)
                self.assertGreaterEqual(r.time_s + 0.01, r.solver_runtime_s)
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
        self.assertGreater(r.time_s, 0.0)
        self.assertEqual(r.status, 'CAP_EXCEEDED')


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
        self.assertGreater(rb.time_s, 0.0)
        self.assertGreater(rf.time_s, 0.0)
        self.assertTrue(dict(rf.phase_wall_s).get('model_build', 0.0) > 0.0)
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
        self.assertIn(r.status_name, ('TIMEOUT_PREPARATION', 'TIMEOUT_SOLVER',
                                      'TIMEOUT_VALIDATION', 'TIME_LIMIT', 'OPTIMAL'))
        if r.status_name.startswith('TIMEOUT_'):
            self.assertIsNone(r.objective_ub)
            self.assertIsNone(r.objective_lb)
            self.assertIsNone(r.time_to_proof_s)
        if r.status_name == 'TIME_LIMIT':
            self.assertIn(r.certification,
                          (fcore.CERTIFIED_MIP_BOUND, fcore.UNCERTIFIED_NO_INCUMBENT))
            self.assertIsNone(r.time_to_proof_s)  # sem prova, sem tempo de prova

    def test_budget_is_forwarded_and_not_exceeded_on_lp(self):
        inst = fi.load_instance(HB_Q4_ROW)
        cfg = fcfg.ExperimentConfig(time_limit_s=60.0, lp_time_limit_s=5.0)
        results = fcore.run_modality_a(inst, cfg)
        for key in ('lp_base', 'lp_comp', 'lp_fcc_k'):
            self.assertLessEqual(results[key].time_s, 5.0 + 2.0)
            self.assertEqual(results[key].time_s, results[key].time_s)
            self.assertTrue(results[key].phase_wall_s)


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


class FC02GurobiIntegrationTests(unittest.TestCase):
    """FC-02: exigem Gurobi real e verificam modelos, hashes e cortes reais."""

    @classmethod
    def setUpClass(cls):
        cls.inst = fi.load_instance(HB_Q4_ROW)
        cls.comp = fcore.run_modality_b_comp(cls.inst, PILOT_CFG)
        cls.fcc = fcore.run_modality_b_fcc_k(cls.inst, PILOT_CFG)

    def test_comp_mip_and_fcc_k_are_complete_and_same_k(self):
        pair = assess_primary_pair(self.inst, self.comp, self.fcc)
        self.assertEqual(pair.status, 'PAIR_VALID', pair.reason)
        self.assertTrue(self.comp.k_validated)
        self.assertTrue(self.fcc.k_validated)
        self.assertEqual(self.comp.n_K, self.comp.n_K_added)
        self.assertEqual(self.fcc.n_K, self.fcc.n_K_added)
        self.assertEqual(self.comp.k_sha256, self.fcc.k_sha256)
        self.assertEqual(self.comp.instance_sha256, self.inst.instance_sha256)
        self.assertEqual(self.fcc.instance_sha256, self.inst.instance_sha256)
        self.assertEqual(self.comp.status_name, 'OPTIMAL')
        self.assertEqual(self.fcc.status_name, 'OPTIMAL')
        self.assertAlmostEqual(self.comp.objective_ub, 2.0, places=7)
        self.assertAlmostEqual(self.fcc.objective_ub, 2.0, places=7)
        self.assertEqual(self.comp.physical_ub_status, 'UB_PHYSICAL_VALIDATED')
        self.assertEqual(self.fcc.physical_ub_status, 'UB_PHYSICAL_VALIDATED')

    def test_comp_structural_binary_y_continuous_f(self):
        from harness import _make_mip
        from gurobipy import GRB
        cuts, k_hash = fcore._k_for(self.inst)
        model, y, f, n_added = _make_mip(
            self.inst.S, self.inst.T, self.inst.V, self.inst.A_r, 'cont', cuts,
        )
        try:
            self.assertTrue(all(var.VType == GRB.BINARY for var in y.values()))
            self.assertTrue(all(var.VType == GRB.CONTINUOUS for var in f.values()))
            self.assertEqual(n_added, len(cuts))
            self.assertEqual(k_hash, self.comp.k_sha256)
        finally:
            model.dispose()

    def test_report_primary_pair_and_no_k_ablation(self):
        rb = fcore.run_modality_b_baseline(self.inst, PILOT_CFG)
        pair = assess_primary_pair(self.inst, self.comp, self.fcc)
        rows, evolution = rep.rows_for_instance(
            self.inst, {}, rb, self.fcc, b_comp_mip=self.comp, pair=pair,
        )
        self.assertEqual(len(rows), 3)
        mapped = {r['formulation']: r for r in rows}
        self.assertEqual(mapped['comp_mip']['comparison_role'], 'primary')
        self.assertEqual(mapped['fcc_k']['comparison_role'], 'primary')
        self.assertEqual(mapped['baseline']['comparison_role'], 'ablation_no_k')
        self.assertEqual(mapped['baseline']['pair_status'], 'ABLATION_ONLY')
        for f in ('comp_mip', 'fcc_k'):
            self.assertEqual(mapped[f]['pair_status'], 'PAIR_VALID')
            self.assertEqual(mapped[f]['pair_k_sha256'], pair.k_sha256)
            self.assertEqual(mapped[f]['physical_ub_status'], 'UB_PHYSICAL_VALIDATED')
        self.assertEqual(mapped['baseline']['k_sha256'], '')
        self.assertEqual(len(evolution), sum(len(x.evolution)
                         for x in (self.comp, self.fcc, rb)))

    def test_cap_fcc_mip_never_becomes_paired(self):
        tight = fcfg.ExperimentConfig(time_limit_s=20.0, max_w=1)
        capped = fcore.run_modality_b_fcc_k(self.inst, tight)
        self.assertEqual(capped.status_name, 'CAP_EXCEEDED', capped.reason)
        self.assertEqual(capped.certification, fcore.NOT_MEASURED_CAP_EXCEEDED)
        self.assertIsNone(capped.objective_lb)
        self.assertIsNone(capped.objective_ub)
        self.assertNotEqual(assess_primary_pair(self.inst, self.comp, capped).status,
                            'PAIR_VALID')

    def test_manifest_hash_is_verified_from_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            orig = ROOT / HB_Q4_ROW['caminho']
            copied = Path(temp) / 'copy.txt'
            copied.write_bytes(orig.read_bytes())
            row = dict(HB_Q4_ROW, caminho='copy.txt', sha256='0' * 64)
            with self.assertRaisesRegex(ValueError, 'INTEGRITY_ERROR'):
                fi.load_instance(row, root=Path(temp))
            row['sha256'] = hashlib.sha256(copied.read_bytes()).hexdigest()
            good = fi.load_instance(row, root=Path(temp))
            self.assertEqual(good.instance_sha256, row['sha256'])
