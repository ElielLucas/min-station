"""
Executa uma comparação pareada do MIN-STATION com e sem pré-processamento.

Cada execução é salva imediatamente em JSON e no CSV detalhado. O CSV
comparativo é reconstruído após cada execução concluída, portanto uma
interrupção não elimina os resultados já obtidos.
"""

import argparse
import hashlib
import math
import os
import platform
import re
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from preprocessamento.modelo_min_station_das_preprocess import (
    PreprocessLogger,
    construir_modelo_baseline,
    preprocessar_instancia,
)
from ms_utils import RegistSerieTemporal, construir_adjacencia, ler_instancia
from .resultados_preprocess import (
    append_run_csv,
    existing_run_ids,
    save_run_json,
    write_comparison_csv,
)


VARIANT_SEM = "sem_preprocessamento"
VARIANT_COM = "com_preprocessamento"


STATUS_NAMES = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INPROGRESS: "INPROGRESS",
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT",
    GRB.WORK_LIMIT: "WORK_LIMIT",
    GRB.MEM_LIMIT: "MEM_LIMIT",
}


def utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_experiment_id() -> str:
    return datetime.now().strftime("preprocess_%Y%m%d_%H%M%S")


def safe_name(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_.")
    return result or "run"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def current_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def safe_float(value):
    try:
        result = float(value)
    except (TypeError, ValueError, AttributeError):
        return None
    return result if math.isfinite(result) else None


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError, AttributeError):
        return None


def model_attribute(model, name, default=None):
    try:
        return getattr(model, name)
    except (AttributeError, gp.GurobiError):
        return default


def make_run_id(
    experiment_id: str,
    instance: str,
    radius,
    seed: int,
    variant: str,
) -> str:
    parts = [experiment_id, Path(instance).stem, f"R{radius}", f"seed{seed}", variant]
    return "__".join(safe_name(part) for part in parts)


def choose_files(inputs_dir: Path, selected: list[str] | None) -> list[Path]:
    files = sorted(path for path in inputs_dir.glob("*.txt") if path.is_file())
    if not selected:
        return files

    wanted = {Path(name).name for name in selected}
    chosen = [path for path in files if path.name in wanted]
    missing = sorted(wanted - {path.name for path in chosen})
    if missing:
        raise FileNotFoundError(
            "Instância(s) não encontrada(s) em "
            f"{inputs_dir}: {', '.join(missing)}"
        )
    return chosen


def variants_from_args(value: str, order: str) -> list[str]:
    if value == "sem":
        return [VARIANT_SEM]
    if value == "com":
        return [VARIANT_COM]
    if order == "com_primeiro":
        return [VARIANT_COM, VARIANT_SEM]
    return [VARIANT_SEM, VARIANT_COM]


def execute_variant(
    *,
    experiment_id: str,
    instance_path: Path,
    data: dict,
    variant: str,
    seed: int,
    threads: int,
    time_limit_s: float,
    budget_mode: str,
    experiment_dir: Path,
    save_plots: bool,
    plot_sample_s: float,
    max_preprocess_iters: int,
    max_dominance_candidates: int,
    with_diagnostics: bool,
    git_sha: str,
) -> dict:
    instance = instance_path.name
    radius = int(float(data["R"]))
    run_id = make_run_id(experiment_id, instance, radius, seed, variant)
    use_preprocess = variant == VARIANT_COM

    S = data["S"]
    T = data["T"]
    VI = data["VI"]
    V = data["V"]
    adjacency = construir_adjacencia(data["E"])

    variant_dir = experiment_dir / variant
    preprocess_log_dir = variant_dir / "preprocess_logs"
    solver_log_dir = variant_dir / "solver_logs"
    timeseries_dir = variant_dir / "timeseries"
    plots_dir = variant_dir / "plots"
    solver_log_dir.mkdir(parents=True, exist_ok=True)
    timeseries_dir.mkdir(parents=True, exist_ok=True)
    if save_plots:
        plots_dir.mkdir(parents=True, exist_ok=True)

    solver_log_path = solver_log_dir / f"{run_id}.log"
    total_start = time.monotonic()

    preprocess_logger = PreprocessLogger(
        nome_instancia=instance,
        R=radius,
        log_dir=preprocess_log_dir,
        ativo=True,
    )

    preprocess_start = time.monotonic()
    V_model, _, reachability_arcs, station_candidates, prep_stats = (
        preprocessar_instancia(
            nome_instancia=instance,
            S=S,
            T=T,
            V=V,
            adj=adjacency,
            R=radius,
            logger=preprocess_logger,
            aplicar_preprocess=use_preprocess,
            max_iters=max_preprocess_iters,
            max_dominance_candidates=max_dominance_candidates,
            diag_quase_dom_max_candidatos=2500 if with_diagnostics else 0,
            diag_global_max_terminais=2048 if with_diagnostics else 0,
        )
    )
    preprocess_wall_s = time.monotonic() - preprocess_start
    preprocess_log_path = preprocess_logger.salvar()

    build_start = time.monotonic()
    model, _, _, _, _ = construir_modelo_baseline(
        S=S,
        T=T,
        V=V_model,
        arcos=reachability_arcs,
        candidatos_estacao=station_candidates,
    )
    model_build_s = time.monotonic() - build_start

    elapsed_before_solver = time.monotonic() - total_start
    if budget_mode == "total":
        solver_time_limit_s = max(0.0, time_limit_s - elapsed_before_solver)
    else:
        solver_time_limit_s = time_limit_s

    model.Params.TimeLimit = solver_time_limit_s
    model.Params.Seed = seed
    if threads > 0:
        model.Params.Threads = threads
    model.Params.LogFile = str(solver_log_path)

    series = RegistSerieTemporal(
        instance,
        radius,
        timeseries_dir,
        intervalo_amostra=plot_sample_s,
        suffix=f"__seed{seed}__{variant}",
        titulo_tag=variant.upper(),
    )

    def callback(callback_model, where):
        try:
            if where == GRB.Callback.MIP:
                runtime = callback_model.cbGet(GRB.Callback.RUNTIME)
                lower_bound = callback_model.cbGet(GRB.Callback.MIP_OBJBND)
                upper_bound = callback_model.cbGet(GRB.Callback.MIP_OBJBST)
                nodes = int(callback_model.cbGet(GRB.Callback.MIP_NODCNT))
                series.talvez_adicionar(runtime, lower_bound, upper_bound, nodes)
            elif where == GRB.Callback.MIPSOL:
                runtime = callback_model.cbGet(GRB.Callback.RUNTIME)
                upper_bound = callback_model.cbGet(GRB.Callback.MIPSOL_OBJ)
                lower_bound = callback_model.cbGet(GRB.Callback.MIP_OBJBND)
                nodes = int(callback_model.cbGet(GRB.Callback.MIP_NODCNT))
                series.talvez_adicionar(
                    runtime,
                    lower_bound,
                    upper_bound,
                    nodes,
                    forcar=True,
                )
        except gp.GurobiError:
            pass

    model.optimize(callback)
    runtime_s = time.monotonic() - total_start

    status = safe_int(model_attribute(model, "Status"))
    solcount = safe_int(model_attribute(model, "SolCount", 0)) or 0
    lower_bound = safe_float(model_attribute(model, "ObjBound"))
    upper_bound = (
        safe_float(model_attribute(model, "ObjVal")) if solcount > 0 else None
    )
    gap = safe_float(model_attribute(model, "MIPGap")) if solcount > 0 else None
    solver_s = safe_float(model_attribute(model, "Runtime"))
    nodes = safe_int(model_attribute(model, "NodeCount", 0)) or 0

    series.talvez_adicionar(
        solver_s or 0.0,
        lower_bound if lower_bound is not None else float("nan"),
        upper_bound if upper_bound is not None else float("nan"),
        nodes,
        forcar=True,
    )
    timeseries_csv_path = series.salvar_csv()
    plot_png_path = None
    if save_plots:
        original_output_dir = series.pasta_saida
        series.pasta_saida = plots_dir
        plot_png_path = series.salvar_grafico(
            escala_y="symlog",
            corte_inicial_s=0.5,
            teto_percentil=99.0,
            mostrar_gap=True,
            max_pontos=400,
        )
        series.pasta_saida = original_output_dir

    is_time_limit = status == GRB.TIME_LIMIT
    model_vars = safe_int(model_attribute(model, "NumVars", 0)) or 0
    model_cons = safe_int(model_attribute(model, "NumConstrs", 0)) or 0
    model_nonzeros = safe_int(model_attribute(model, "NumNZs", 0)) or 0

    row = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "timestamp_utc": utc_now_text(),
        "variant": variant,
        "seed": seed,
        "threads": threads if threads > 0 else "auto",
        "python_hash_seed": os.environ.get("PYTHONHASHSEED", ""),
        "budget_mode": budget_mode,
        "time_limit_s": time_limit_s,
        "solver_time_limit_s": solver_time_limit_s,
        "git_sha": git_sha,
        "instance_sha256": file_sha256(instance_path),
        "gurobi_version": ".".join(map(str, gp.gurobi.version())),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "instance": instance,
        "R": radius,
        "N_nodes_original": len(V),
        "M_base_original": sum(len(adjacency.get(node, [])) for node in V),
        "VI_original": len(VI),
        "N_nodes_pre": len(V_model),
        "M_base_pre": prep_stats.get("M_base_pre", ""),
        "A_R_bruto": prep_stats.get("A_R_bruto", len(reachability_arcs)),
        "A_R_final": len(reachability_arcs),
        "m": len(S),
        "candidatos_bruto": prep_stats.get("candidatos_bruto", len(V)),
        "candidatos_final": len(station_candidates),
        "grafo_folhas_removidas": prep_stats.get("grafo_folhas_removidas", 0),
        "grafo_grau2_diag": prep_stats.get("grafo_grau2_diag", ""),
        "candidatos_removidos_alcance": prep_stats.get(
            "candidatos_removidos_alcance", 0
        ),
        "candidatos_removidos_dominancia": prep_stats.get(
            "candidatos_removidos_dominancia", 0
        ),
        "candidatos_removidos_total": prep_stats.get(
            "candidatos_removidos_total", 0
        ),
        "arcos_removidos_irrelevantes": prep_stats.get(
            "arcos_removidos_irrelevantes", 0
        ),
        "arcos_removidos_forcados_zero": prep_stats.get(
            "arcos_removidos_forcados_zero", 0
        ),
        "A_R_removidos_total": prep_stats.get("A_R_removidos_total", 0),
        "preprocess_iteracoes": prep_stats.get("preprocess_iteracoes", 0),
        "preprocess_s": prep_stats.get("preprocess_s", preprocess_wall_s),
        "solver_s": solver_s,
        "diag_eq_classes": prep_stats.get("diag_eq_classes", ""),
        "diag_eq_candidatos": prep_stats.get("diag_eq_candidatos", ""),
        "diag_eq_maior_classe": prep_stats.get("diag_eq_maior_classe", ""),
        "diag_qdom_90": prep_stats.get("diag_qdom_90", ""),
        "diag_qdom_95": prep_stats.get("diag_qdom_95", ""),
        "diag_qdom_99": prep_stats.get("diag_qdom_99", ""),
        "diag_global_classes": prep_stats.get("diag_global_classes", ""),
        "diag_global_candidatos": prep_stats.get("diag_global_candidatos", ""),
        "diag_global_maior_classe": prep_stats.get(
            "diag_global_maior_classe", ""
        ),
        "vars": model_vars,
        "cons": model_cons,
        "status": status,
        "status_name": STATUS_NAMES.get(status, f"STATUS_{status}"),
        "solcount": solcount,
        "LI": lower_bound,
        "LS": upper_bound,
        "gap": gap,
        "gap_pct": 100.0 * gap if gap is not None else None,
        "runtime_s": runtime_s,
        "nodes": nodes,
        "timelimit": is_time_limit,
        "feasible_like": status == GRB.OPTIMAL or (is_time_limit and solcount > 0),
        "preprocess_wall_s": preprocess_wall_s,
        "model_build_s": model_build_s,
        "solver_log_path": str(solver_log_path),
        "preprocess_log_path": str(preprocess_log_path or ""),
        "timeseries_csv_path": str(timeseries_csv_path or ""),
        "plot_png_path": str(plot_png_path or ""),
        "simplex_iterations": safe_float(model_attribute(model, "IterCount")),
        "barrier_iterations": safe_float(model_attribute(model, "BarIterCount")),
        "work_units": safe_float(model_attribute(model, "Work")),
        "model_nonzeros": model_nonzeros,
        "model_fingerprint": safe_int(model_attribute(model, "Fingerprint")),
        "candidatos_removidos_total_global": len(V) - len(station_candidates),
        "erro": "",
    }
    return row


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compara o modelo MIN-STATION com e sem pré-processamento."
    )
    parser.add_argument("--inputs-dir", default="./instancias")
    parser.add_argument("--output-dir", default="./experimentos_preprocess")
    parser.add_argument("--experiment-id", default=None)
    parser.add_argument("--instances", nargs="*", default=None)
    parser.add_argument(
        "--variants",
        choices=("both", "sem", "com"),
        default="both",
    )
    parser.add_argument(
        "--order",
        choices=("sem_primeiro", "com_primeiro"),
        default="sem_primeiro",
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[0])
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--time-limit", type=float, default=3600.0)
    parser.add_argument(
        "--budget-mode",
        choices=("total", "solver"),
        default="total",
        help=(
            "total: o pré-processamento e a construção consomem o limite; "
            "solver: cada variante recebe o limite completo no Gurobi."
        ),
    )
    parser.add_argument("--max-preprocess-iters", type=int, default=10)
    parser.add_argument("--max-dominance-candidates", type=int, default=8000)
    parser.add_argument(
        "--with-diagnostics",
        action="store_true",
        help="Executa também os diagnósticos exploratórios de quase-dominância.",
    )
    parser.add_argument("--plot-sample", type=float, default=10.0)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Executa novamente mesmo quando o run_id já existe no CSV.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    experiment_id = args.experiment_id or default_experiment_id()
    inputs_dir = Path(args.inputs_dir)
    experiment_dir = Path(args.output_dir) / experiment_id
    runs_csv = experiment_dir / "runs.csv"
    comparison_csv = experiment_dir / "comparison.csv"
    json_dir = experiment_dir / "runs_json"

    files = choose_files(inputs_dir, args.instances)
    if not files:
        raise SystemExit(f"Nenhuma instância .txt encontrada em {inputs_dir}")

    python_hash_seed = os.environ.get("PYTHONHASHSEED")
    if python_hash_seed is None:
        print(
            "[aviso] PYTHONHASHSEED não foi definido. Para maior reprodutibilidade, "
            "execute com PYTHONHASHSEED=0."
        )

    variants = variants_from_args(args.variants, args.order)
    git_sha = current_git_sha()
    completed = existing_run_ids(runs_csv)

    print(f"Experimento: {experiment_id}")
    print(f"Instâncias: {len(files)}")
    print(f"Variantes: {', '.join(variants)}")
    print(f"Seeds: {args.seeds}")
    print(f"Limite: {args.time_limit}s | modo={args.budget_mode}")
    print(f"Resultados: {experiment_dir}")

    for instance_path in files:
        try:
            data = ler_instancia(str(instance_path))
        except Exception as error:
            print(f"[{instance_path.name}] erro de leitura: {error}")
            continue

        radius = int(float(data["R"]))
        for seed in args.seeds:
            for variant in variants:
                run_id = make_run_id(
                    experiment_id,
                    instance_path.name,
                    radius,
                    seed,
                    variant,
                )
                if run_id in completed and not args.rerun:
                    print(f"[skip] {run_id} já está salvo")
                    continue

                print("=" * 80)
                print(
                    f"{instance_path.name} | R={radius} | seed={seed} | {variant}"
                )
                print("=" * 80)

                try:
                    row = execute_variant(
                        experiment_id=experiment_id,
                        instance_path=instance_path,
                        data=data,
                        variant=variant,
                        seed=seed,
                        threads=args.threads,
                        time_limit_s=args.time_limit,
                        budget_mode=args.budget_mode,
                        experiment_dir=experiment_dir,
                        save_plots=not args.no_plots,
                        plot_sample_s=args.plot_sample,
                        max_preprocess_iters=args.max_preprocess_iters,
                        max_dominance_candidates=args.max_dominance_candidates,
                        with_diagnostics=args.with_diagnostics,
                        git_sha=git_sha,
                    )
                except Exception as error:
                    print(f"[erro] {run_id}: {error}")
                    continue

                save_run_json(row, json_dir)
                append_run_csv(row, runs_csv)
                completed.add(run_id)
                write_comparison_csv(
                    runs_csv,
                    comparison_csv,
                    experiment_id,
                )
                print(
                    f"[ok] status={row['status_name']} | LI={row['LI']} | "
                    f"LS={row['LS']} | gap={row['gap_pct']}% | "
                    f"runtime={row['runtime_s']:.2f}s"
                )

    write_comparison_csv(runs_csv, comparison_csv, experiment_id)
    print(f"CSV detalhado: {runs_csv}")
    print(f"CSV comparativo: {comparison_csv}")


if __name__ == "__main__":
    main()