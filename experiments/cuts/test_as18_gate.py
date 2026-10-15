"""Regressões AS18 derivadas das regras pré-registradas de transição."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from verify_as18_gate import InvalidEvidence, evaluate


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results/benchmark/as16-lp-h2-001"


class GateAS18Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        for name in ("manifest.json", "rows.json", "analysis.json"):
            (self.folder / name).write_bytes((SOURCE / name).read_bytes())

    def change(self, name, edit):
        p = self.folder / name
        obj = json.loads(p.read_text())
        edit(obj)
        p.write_text(json.dumps(obj))

    def test_stop_without_reclassifying_automatic_investigate(self):
        a = evaluate(self.folder)
        self.assertEqual(a["as16_automatic_gate"], "INVESTIGATE")
        self.assertEqual(a["as16_research_decision"], "STOP")
        self.assertEqual(a["as17_mip_gate"], "NOT_AUTHORIZED")
        self.assertEqual(a["as18_hl_gate"], "NOT_AUTHORIZED")
        self.assertEqual(a["comparison"]["comparable_graphs"], 5)
        self.assertEqual(a["comparison"]["maximum_possible_graphs_with_gain"], 1)

    def test_missing_comparison_cannot_count_as_gain(self):
        a = evaluate(self.folder)
        censored = [c for c in a["cases"] if c["status"] == "NOT_COMPARABLE"]
        self.assertEqual(len(censored), 1)
        self.assertIsNone(censored[0]["relative_gain"])

    def test_detects_duplicate_arm(self):
        self.change("rows.json", lambda rows: rows.append(copy.deepcopy(rows[0])))
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_detects_inconsistent_pairwise_objective(self):
        def mutate(rows):
            for row in rows:
                if row["arm_id"] == "U_K_H2" and row["status"] == "OPTIMAL":
                    row["lp_objective"] += 1
                    break
        self.change("rows.json", mutate)
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_detects_changed_raw_graph_across_arms(self):
        self.change("rows.json", lambda rows: rows[0].update(raw_graph_id="inventado"))
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_detects_fake_independent_graphs(self):
        def mutate(rows):
            for row in rows:
                if row["name"] == "puc-bip42p-regiao-f2":
                    row["raw_graph_id"] = "puc:cc9-2p"
        self.change("rows.json", mutate)
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_detects_modified_gate_counter(self):
        self.change("analysis.json", lambda d: d.update(independent_raw_graphs_with_gain=2))
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_missing_source_fails_closed(self):
        (self.folder / "rows.json").unlink()
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)

    def test_censored_case_cannot_be_silently_marked_optimal(self):
        def mutate(rows):
            for row in rows:
                if row["name"] == "puc-w3c571-seed-r1" and row["arm_id"] == "U_K_H2":
                    row["status"] = "OPTIMAL"
                    break
        self.change("rows.json", mutate)
        with self.assertRaises(InvalidEvidence):
            evaluate(self.folder)


if __name__ == "__main__":
    unittest.main()
