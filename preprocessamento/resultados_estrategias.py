"""Persistência e comparação para o experimento de estratégias isoladas."""

import csv
from collections import defaultdict
from pathlib import Path

from .resultados_preprocess import (
    COMPARISON_METRICS,
    _difference,
    _pct_reduction,
    _speedup,
    append_run_csv,
    existing_run_ids,
    load_runs,
    save_run_json,
)


ORDEM_ESTRATEGIAS = {
    "sem_preprocessamento": 0,
    "somente_folhas": 1,
    "somente_alcance": 2,
    "somente_dominancia": 3,
    "com_preprocessamento": 4,
}


def _mesmo_numero(a, b) -> bool:
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def _config_compativel(baseline: dict, strategy: dict) -> bool:
    if not baseline or not strategy:
        return False
    return (
        baseline.get("budget_mode") == strategy.get("budget_mode")
        and _mesmo_numero(
            baseline.get("time_limit_s"), strategy.get("time_limit_s")
        )
        and str(baseline.get("threads")) == str(strategy.get("threads"))
        and str(baseline.get("seed")) == str(strategy.get("seed"))
        and baseline.get("instance_sha256") == strategy.get("instance_sha256")
    )


def _ambiente_compativel(baseline: dict, strategy: dict) -> bool:
    if not baseline or not strategy:
        return False
    return (
        baseline.get("gurobi_version") == strategy.get("gurobi_version")
        and baseline.get("hostname") == strategy.get("hostname")
        and baseline.get("platform") == strategy.get("platform")
    )


def write_strategy_comparison_csv(
    *,
    runs_csv: Path,
    comparison_csv: Path,
    experiment_id: str,
    reference_runs_csvs=(),
) -> None:
    """Cria uma linha por instância/seed/estratégia contra o baseline.

    Os CSVs de referência permitem reaproveitar as execuções anteriores de
    ``sem_preprocessamento`` e ``com_preprocessamento``. As execuções do
    experimento atual têm precedência se existir duplicidade.
    """
    current_rows = [
        row
        for row in load_runs(runs_csv)
        if row.get("experiment_id") == experiment_id
    ]

    reference_rows = []
    for path in reference_runs_csvs:
        reference_rows.extend(load_runs(Path(path)))

    def key_of(row):
        return (
            row.get("instance", ""),
            row.get("R", ""),
            row.get("seed", ""),
        )

    current_keys = {key_of(row) for row in current_rows}
    groups = defaultdict(dict)

    for row in reference_rows:
        key = key_of(row)
        if key in current_keys:
            groups[key][row.get("variant", "")] = row

    for row in current_rows:
        groups[key_of(row)][row.get("variant", "")] = row

    identity_fields = [
        "comparison_experiment_id",
        "source_experiment_id",
        "baseline_source_experiment_id",
        "instance",
        "R",
        "seed",
        "strategy",
        "baseline_available",
        "config_compatible",
        "environment_compatible",
        "same_git_sha",
        "budget_mode",
        "time_limit_s",
        "threads",
        "git_sha",
        "instance_sha256",
    ]
    paired_fields = [
        f"{prefix}_{metric}"
        for prefix in ("baseline", "strategy")
        for metric in COMPARISON_METRICS
    ]
    delta_fields = [
        "reducao_nodes_grafo_pct",
        "reducao_candidatos_pct",
        "reducao_arcos_A_R_pct",
        "reducao_vars_pct",
        "reducao_cons_pct",
        "reducao_nonzeros_pct",
        "delta_LI",
        "melhoria_LS",
        "delta_gap_pp",
        "delta_nodes",
        "delta_simplex_iterations",
        "delta_work_units",
        "speedup_runtime",
        "speedup_solver",
    ]
    fields = identity_fields + paired_fields + delta_fields

    output_rows = []
    for (instance, radius, seed), variants in sorted(groups.items()):
        baseline = variants.get("sem_preprocessamento", {})
        ordered_variants = sorted(
            variants.items(),
            key=lambda item: (
                ORDEM_ESTRATEGIAS.get(item[0], 99),
                item[0],
            ),
        )

        for strategy_name, strategy in ordered_variants:
            out = {
                "comparison_experiment_id": experiment_id,
                "source_experiment_id": strategy.get("experiment_id", ""),
                "baseline_source_experiment_id": baseline.get(
                    "experiment_id", ""
                ),
                "instance": instance,
                "R": radius,
                "seed": seed,
                "strategy": strategy_name,
                "baseline_available": bool(baseline),
                "config_compatible": _config_compativel(
                    baseline, strategy
                ),
                "environment_compatible": _ambiente_compativel(
                    baseline, strategy
                ),
                "same_git_sha": bool(baseline)
                and baseline.get("git_sha") == strategy.get("git_sha"),
                "budget_mode": strategy.get("budget_mode", ""),
                "time_limit_s": strategy.get("time_limit_s", ""),
                "threads": strategy.get("threads", ""),
                "git_sha": strategy.get("git_sha", ""),
                "instance_sha256": strategy.get("instance_sha256", ""),
            }

            for prefix, row in (
                ("baseline", baseline),
                ("strategy", strategy),
            ):
                for metric in COMPARISON_METRICS:
                    out[f"{prefix}_{metric}"] = row.get(metric, "")

            out.update(
                {
                    "reducao_nodes_grafo_pct": _pct_reduction(
                        baseline.get("N_nodes_pre"),
                        strategy.get("N_nodes_pre"),
                    ),
                    "reducao_candidatos_pct": _pct_reduction(
                        baseline.get("candidatos_final"),
                        strategy.get("candidatos_final"),
                    ),
                    "reducao_arcos_A_R_pct": _pct_reduction(
                        baseline.get("A_R_final"),
                        strategy.get("A_R_final"),
                    ),
                    "reducao_vars_pct": _pct_reduction(
                        baseline.get("vars"), strategy.get("vars")
                    ),
                    "reducao_cons_pct": _pct_reduction(
                        baseline.get("cons"), strategy.get("cons")
                    ),
                    "reducao_nonzeros_pct": _pct_reduction(
                        baseline.get("model_nonzeros"),
                        strategy.get("model_nonzeros"),
                    ),
                    "delta_LI": _difference(
                        strategy.get("LI"), baseline.get("LI")
                    ),
                    "melhoria_LS": _difference(
                        baseline.get("LS"), strategy.get("LS")
                    ),
                    "delta_gap_pp": _difference(
                        strategy.get("gap_pct"), baseline.get("gap_pct")
                    ),
                    "delta_nodes": _difference(
                        strategy.get("nodes"), baseline.get("nodes")
                    ),
                    "delta_simplex_iterations": _difference(
                        strategy.get("simplex_iterations"),
                        baseline.get("simplex_iterations"),
                    ),
                    "delta_work_units": _difference(
                        strategy.get("work_units"),
                        baseline.get("work_units"),
                    ),
                    "speedup_runtime": _speedup(
                        baseline.get("runtime_s"),
                        strategy.get("runtime_s"),
                    ),
                    "speedup_solver": _speedup(
                        baseline.get("solver_s"),
                        strategy.get("solver_s"),
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
