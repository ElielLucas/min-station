import csv
import json
import math
from collections import defaultdict
from pathlib import Path


LEGACY_FIELDS = [
    "instance",
    "R",
    "N_nodes_original",
    "M_base_original",
    "VI_original",
    "N_nodes_pre",
    "M_base_pre",
    "A_R_bruto",
    "A_R_final",
    "m",
    "candidatos_bruto",
    "candidatos_final",
    "grafo_folhas_removidas",
    "grafo_grau2_diag",
    "candidatos_removidos_alcance",
    "candidatos_removidos_dominancia",
    "candidatos_removidos_total",
    "arcos_removidos_irrelevantes",
    "arcos_removidos_forcados_zero",
    "A_R_removidos_total",
    "preprocess_iteracoes",
    "preprocess_s",
    "solver_s",
    "diag_eq_classes",
    "diag_eq_candidatos",
    "diag_eq_maior_classe",
    "diag_qdom_90",
    "diag_qdom_95",
    "diag_qdom_99",
    "diag_global_classes",
    "diag_global_candidatos",
    "diag_global_maior_classe",
    "vars",
    "cons",
    "status",
    "solcount",
    "LI",
    "LS",
    "gap",
    "runtime_s",
    "nodes",
    "timelimit",
    "feasible_like",
]


METADATA_FIELDS = [
    "experiment_id",
    "run_id",
    "timestamp_utc",
    "variant",
    "seed",
    "threads",
    "python_hash_seed",
    "budget_mode",
    "time_limit_s",
    "solver_time_limit_s",
    "git_sha",
    "instance_sha256",
    "gurobi_version",
    "hostname",
    "platform",
]


EXTRA_RESULT_FIELDS = [
    "status_name",
    "gap_pct",
    "preprocess_wall_s",
    "model_build_s",
    "solver_log_path",
    "preprocess_log_path",
    "timeseries_csv_path",
    "plot_png_path",
    "simplex_iterations",
    "barrier_iterations",
    "work_units",
    "model_nonzeros",
    "model_fingerprint",
    "candidatos_removidos_total_global",
    "erro",
]


RUN_FIELDS = METADATA_FIELDS + LEGACY_FIELDS + EXTRA_RESULT_FIELDS


COMPARISON_METRICS = [
    "N_nodes_pre",
    "M_base_pre",
    "A_R_bruto",
    "A_R_final",
    "candidatos_bruto",
    "candidatos_final",
    "grafo_folhas_removidas",
    "candidatos_removidos_alcance",
    "candidatos_removidos_dominancia",
    "candidatos_removidos_total",
    "candidatos_removidos_total_global",
    "arcos_removidos_irrelevantes",
    "arcos_removidos_forcados_zero",
    "A_R_removidos_total",
    "preprocess_iteracoes",
    "preprocess_s",
    "model_build_s",
    "solver_s",
    "runtime_s",
    "vars",
    "cons",
    "model_nonzeros",
    "status",
    "status_name",
    "solcount",
    "LI",
    "LS",
    "gap",
    "gap_pct",
    "nodes",
    "simplex_iterations",
    "barrier_iterations",
    "work_units",
    "timelimit",
    "feasible_like",
]


def append_run_csv(row: dict, csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    first = not csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=RUN_FIELDS,
            extrasaction="ignore",
        )
        if first:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in RUN_FIELDS})
        file.flush()


def save_run_json(row: dict, json_dir: Path) -> Path:
    json_dir.mkdir(parents=True, exist_ok=True)
    path = json_dir / f"{row['run_id']}.json"
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(row, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(path)
    return path


def load_runs(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    with csv_path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def existing_run_ids(csv_path: Path) -> set[str]:
    return {
        row.get("run_id", "")
        for row in load_runs(csv_path)
        if row.get("run_id")
    }


def _number(value):
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _pct_reduction(before, after):
    before_num = _number(before)
    after_num = _number(after)
    if before_num in (None, 0) or after_num is None:
        return ""
    return 100.0 * (before_num - after_num) / before_num


def _difference(after, before):
    after_num = _number(after)
    before_num = _number(before)
    if after_num is None or before_num is None:
        return ""
    return after_num - before_num


def _speedup(before, after):
    before_num = _number(before)
    after_num = _number(after)
    if before_num is None or after_num in (None, 0):
        return ""
    return before_num / after_num


def write_comparison_csv(
    runs_csv: Path,
    comparison_csv: Path,
    experiment_id: str,
) -> None:
    rows = [
        row
        for row in load_runs(runs_csv)
        if row.get("experiment_id") == experiment_id
    ]

    groups = defaultdict(dict)
    for row in rows:
        key = (
            row.get("instance", ""),
            row.get("R", ""),
            row.get("seed", ""),
        )
        groups[key][row.get("variant", "")] = row

    identity_fields = [
        "experiment_id",
        "instance",
        "R",
        "seed",
        "pair_complete",
        "budget_mode",
        "time_limit_s",
        "threads",
        "git_sha",
        "instance_sha256",
    ]
    paired_fields = [
        f"{prefix}_{metric}"
        for prefix in ("sem", "com")
        for metric in COMPARISON_METRICS
    ]
    delta_fields = [
        "reducao_nodes_grafo_pct",
        "reducao_candidatos_pct",
        "reducao_arcos_A_R_pct",
        "reducao_vars_pct",
        "reducao_cons_pct",
        "delta_LI",
        "melhoria_LS",
        "delta_gap_pp",
        "delta_nodes",
        "speedup_runtime",
        "speedup_solver",
    ]
    fields = identity_fields + paired_fields + delta_fields

    output_rows = []
    for (instance, radius, seed), variants in sorted(groups.items()):
        baseline = variants.get("sem_preprocessamento", {})
        preprocess = variants.get("com_preprocessamento", {})
        reference = baseline or preprocess

        out = {
            "experiment_id": experiment_id,
            "instance": instance,
            "R": radius,
            "seed": seed,
            "pair_complete": bool(baseline and preprocess),
            "budget_mode": reference.get("budget_mode", ""),
            "time_limit_s": reference.get("time_limit_s", ""),
            "threads": reference.get("threads", ""),
            "git_sha": reference.get("git_sha", ""),
            "instance_sha256": reference.get("instance_sha256", ""),
        }

        for prefix, row in (("sem", baseline), ("com", preprocess)):
            for metric in COMPARISON_METRICS:
                out[f"{prefix}_{metric}"] = row.get(metric, "")

        out.update(
            {
                "reducao_nodes_grafo_pct": _pct_reduction(
                    baseline.get("N_nodes_pre"), preprocess.get("N_nodes_pre")
                ),
                "reducao_candidatos_pct": _pct_reduction(
                    baseline.get("candidatos_final"),
                    preprocess.get("candidatos_final"),
                ),
                "reducao_arcos_A_R_pct": _pct_reduction(
                    baseline.get("A_R_final"), preprocess.get("A_R_final")
                ),
                "reducao_vars_pct": _pct_reduction(
                    baseline.get("vars"), preprocess.get("vars")
                ),
                "reducao_cons_pct": _pct_reduction(
                    baseline.get("cons"), preprocess.get("cons")
                ),
                "delta_LI": _difference(
                    preprocess.get("LI"), baseline.get("LI")
                ),
                "melhoria_LS": _difference(
                    baseline.get("LS"), preprocess.get("LS")
                ),
                "delta_gap_pp": _difference(
                    preprocess.get("gap_pct"), baseline.get("gap_pct")
                ),
                "delta_nodes": _difference(
                    preprocess.get("nodes"), baseline.get("nodes")
                ),
                "speedup_runtime": _speedup(
                    baseline.get("runtime_s"), preprocess.get("runtime_s")
                ),
                "speedup_solver": _speedup(
                    baseline.get("solver_s"), preprocess.get("solver_s")
                ),
            }
        )
        output_rows.append(out)

    comparison_csv.parent.mkdir(parents=True, exist_ok=True)
    temp_path = comparison_csv.with_suffix(".csv.tmp")
    with temp_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    temp_path.replace(comparison_csv)
