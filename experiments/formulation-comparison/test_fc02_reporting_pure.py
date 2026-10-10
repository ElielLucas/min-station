"""FC-02: contrato de CSV verificável sem licença Gurobi."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fc_pairing import assess_primary_pair  # noqa: E402


class _LP:
    pass


class _MIP:
    pass


def _load_reporting_without_solver():
    dummy_core = types.ModuleType('fc_core')
    dummy_core.LPResult = _LP
    dummy_core.MIPResult = _MIP
    spec = importlib.util.spec_from_file_location('_fc02_reporting_pure', HERE / 'fc_reporting.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'fc_core': dummy_core}):
        spec.loader.exec_module(module)
    return module


def _result(formulation):
    r = _MIP()
    r.formulation = formulation
    r.status_name = 'OPTIMAL'
    r.instance_sha256 = 'digest-instancia'
    r.k_sha256 = None if formulation == 'baseline' else 'digest-K'
    r.n_K = 0 if formulation == 'baseline' else 2
    r.n_K_added = 0 if formulation == 'baseline' else 2
    r.k_validated = formulation != 'baseline'
    r.objective_ub = 2.0
    r.objective_lb = 2.0
    r.physically_validated = True
    r.physical_ub_status = 'UB_PHYSICAL_VALIDATED'
    r.time_s = 1.0
    r.solver_runtime_s = 0.1
    r.work = 0.5
    r.certification = 'CERTIFIED_MIP_OPTIMAL'
    r.gap_abs = 0.0
    r.gap_rel = 0.0
    r.time_to_first_feasible_s = 0.3
    r.time_to_best_s = 0.5
    r.time_to_proof_s = 1.0
    r.nodes = 5
    r.n_vars = 50
    r.n_cons = 70
    r.ru_maxrss_kb_before = 123
    r.ru_maxrss_kb_after = 124
    r.evolution = ()
    r.phase_wall_s = (('solve', 0.1),)
    r.stop_reason = 'OPTIMAL'
    r.reason = ''
    return r


class ReportPureTests(unittest.TestCase):
    def test_csv_has_primary_ablation_and_hash_integrity(self):
        rep = _load_reporting_without_solver()
        instance = types.SimpleNamespace(
            nome='test.txt', classe='estrutural', familia='HB', n=3,
            m_arestas=2, m=1, r=1.0, instance_sha256='digest-instancia',
        )
        comp = _result('comp_mip')
        fcc = _result('fcc_k')
        base = _result('baseline')
        pair = assess_primary_pair(instance, comp, fcc)
        self.assertEqual(pair.status, 'PAIR_VALID')
        rows, evo = rep.rows_for_instance(
            instance, {}, base, fcc, b_comp_mip=comp, pair=pair,
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual(evo, [])
        for row in rows:
            self.assertEqual(set(rep.RESULTS_FIELDS), set(row))
        by_name = {r['formulation']: r for r in rows}
        for label in ('comp_mip', 'fcc_k'):
            self.assertEqual(by_name[label]['comparison_role'], 'primary')
            self.assertEqual(by_name[label]['pair_status'], 'PAIR_VALID')
            self.assertEqual(by_name[label]['k_sha256'], 'digest-K')
            self.assertEqual(by_name[label]['pair_k_sha256'], 'digest-K')
        self.assertEqual(by_name['baseline']['comparison_role'], 'ablation_no_k')
        self.assertEqual(by_name['baseline']['pair_status'], 'ABLATION_ONLY')
        self.assertEqual(by_name['baseline']['k_sha256'], '')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'results.csv'
            rep.write_csv(path, rep.RESULTS_FIELDS, rows)
            import csv
            with path.open(newline='', encoding='utf-8') as f:
                persisted = list(csv.DictReader(f))
            self.assertEqual(len(persisted), 3)
            self.assertEqual(persisted[0]['pair_status'], 'PAIR_VALID')


if __name__ == '__main__':
    unittest.main()
