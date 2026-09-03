"""Testa separadores obrigatórios no pré-processamento do MIN-STATION.

O experimento executa duas variantes novas:

* ``somente_separadores``: mantém o grafo original e fixa as estações
  obrigatórias encontradas no grafo de alcance;
* ``folhas_separadores``: poda folhas não terminais antes de construir o grafo
  de alcance e, em seguida, fixa as estações obrigatórias.

Resultados anteriores de ``sem_preprocessamento`` e ``somente_folhas`` podem
ser incorporados com ``--reference-runs-csv``.
"""

from __future__ import annotations

import argparse
import math
import os
import platform
import socket
import time
from collections.abc import Mapping
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from ms_utils import (
    RegistSerieTemporal,
    construir_adjacencia,
    construir_arcos_alcance,
    ler_instancia,
)

from .experimento_estrategias import (
    STATUS_NAMES,
    choose_files,
    current_git_sha,
    default_experiment_id,
    file_sha256,
    make_run_id,
    model_attribute,
    safe_float,
    safe_int,
    utc_now_text,
)
from .modelo_min_station_das_preprocess import (
    PreprocessLogger,
    construir_modelo_baseline,
    normalizar_arcos,
    podar_folhas_sem_terminais,
)
from .resultados_preprocess import load_runs
from .resultados_separadores import (
    append_run_csv,
    existing_run_ids,
    save_run_json,
    write_comparison_csv,
)
from .separadores_obrigatorios import detectar_estacoes_obrigatorias


SOMENTE_SEPARADORES = "somente_separadores"
FOLHAS_SEPARADORES = "folhas_separadores"
ESTRATEGIAS = (SOMENTE_SEPARADORES, FOLHAS_SEPARADORES)


def _preprocessar(
    *,
    estrategia: str,
    nome_instancia: str,
    S,
    T,
    V,
    adj,
    R,
    logger,
):
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"Estratégia desconhecida: {estrategia}")

    usar_folhas = estrategia == FOLHAS_SEPARADORES
    inicio = time.monotonic()
    V0 = list(V)

    logger.sep(
        f"SEPARADORES OBRIGATÓRIOS | {nome_instancia} | "
        f"R={R} | {estrategia}"
    )
    logger.log(
        f"[Estratégia] folhas={usar_folhas} | separadores=True"
    )

    if usar_folhas:
        V1, adj1, stats_grafo = podar_folhas_sem_terminais(
            V0, adj, S, T, logger
        )
    else:
        V1 = V0
        adj1 = adj
        stats_grafo = {
            "grafo_folhas_removidas": 0,
            "grafo_grau2_diag": "",
            "grafo_preprocess_s": 0.0,
        }
        logger.log("[Grafo original] Poda de folhas não aplicada.")

    inicio_arcos = time.monotonic()
    arcos_brutos = construir_arcos_alcance(V1, adj1, R)
    arcos, normalizacao = normalizar_arcos(arcos_brutos, V1)
    tempo_arcos = time.monotonic() - inicio_arcos
    candidatos = set(V1)

    logger.log("[Construção A^R]")
    logger.log(
        f"  A^R normalizado={len(arcos)} | "
        f"loops={normalizacao['loops']} | "
        f"fora_de_V={normalizacao['fora_de_V']} | "
        f"duplicados={normalizacao['duplicados']} | "
        f"tempo={tempo_arcos:.3f}s"
    )

    inicio_separadores = time.monotonic()
    resultado = detectar_estacoes_obrigatorias(
        vertices=V1,
        arcos_alcance=arcos,
        origens=S,
        destinos=T,
        candidatos=candidatos,
    )
    tempo_separadores = time.monotonic() - inicio_separadores
    obrigatorias = set(resultado.estacoes_obrigatorias)

    logger.log("[Separadores obrigatórios]")
    logger.log(
        f"  componentes={resultado.componentes_originais} | "
        f"articulações={len(resultado.articulacoes)} | "
        "separadores_desbalanceados="
        f"{len(resultado.separadores_desbalanceados)} | "
        f"estações_obrigatórias={len(obrigatorias)} | "
        f"tempo={tempo_separadores:.3f}s"
    )
    if obrigatorias:
        amostra = sorted(map(str, obrigatorias))[:20]
        logger.log(f"  IDs obrigatórios (até 20): {', '.join(amostra)}")

    tempo_total = time.monotonic() - inicio
    stats = {
        "preprocess_aplicado": True,
        "preprocess_strategy": estrategia,
        "usa_folhas": usar_folhas,
        "usa_separadores": True,
        "N_nodes_pre": len(V1),
        "M_base_pre": sum(len(adj1.get(u, [])) for u in adj1),
        "A_R_bruto": len(arcos),
        "A_R_final": len(arcos),
        "candidatos_bruto": len(candidatos),
        "candidatos_final": len(candidatos),
        "candidatos_removidos_alcance": 0,
        "candidatos_removidos_dominancia": 0,
        "candidatos_removidos_total": 0,
        "arcos_removidos_irrelevantes": 0,
        "arcos_removidos_forcados_zero": 0,
        "A_R_removidos_total": 0,
        "preprocess_iteracoes": 1,
        "preprocess_s": tempo_total,
        "A_R_loops_descartados": normalizacao["loops"],
        "A_R_duplicados_descartados": normalizacao["duplicados"],
        "articulacoes_total": len(resultado.articulacoes),
        "separadores_desbalanceados_total": len(
            resultado.separadores_desbalanceados
        ),
        "estacoes_obrigatorias_total": len(obrigatorias),
        "estacoes_obrigatorias_ids": "|".join(
            sorted(map(str, obrigatorias))
        ),
        "componentes_alcance_total": resultado.componentes_originais,
        "componentes_desbalanceadas_total": (
            resultado.componentes_desbalanceadas_total
        ),
        "maior_desequilibrio": resultado.maior_desequilibrio,
        **stats_grafo,
    }

    logger.log(f"[Resumo] tempo_total_preprocessamento={tempo_total:.3f}s")
    return V1, arcos, candidatos, obrigatorias, stats


def _eh_variavel_gurobi(value) -> bool:
    return isinstance(value, gp.Var)


def _localizar_variaveis_estacao(
    saidas_modelo: tuple,
    candidatos: set,
    obrigatorias: set,
) -> Mapping:
    """Localiza o mapa y[v] sem depender da posição exata no retorno."""
    if not obrigatorias:
        return {}

    candidatas = []
    for item in saidas_modelo[1:]:
        if not isinstance(item, Mapping):
            continue
        chaves = set(item.keys())
        if not obrigatorias.issubset(chaves):
            continue
        valores = [item[vertice] for vertice in obrigatorias]
        if not all(_eh_variavel_gurobi(valor) for valor in valores):
            continue
        cobertura = len(chaves & candidatos)
        candidatas.append((cobertura, item))

    if not candidatas:
        raise RuntimeError(
            "Não foi possível localizar o dicionário das variáveis y[v] "
            "retornado por construir_modelo_baseline. Verifique a interface "
            "da função antes de executar o experimento."
        )

    candidatas.sort(key=lambda item: item[0], reverse=True)
    return candidatas[0][1]


def _fixar_estacoes_obrigatorias(
    modelo: gp.Model,
    saidas_modelo: tuple,
    candidatos: set,
    obrigatorias: set,
) -> int:
    variaveis_estacao = _localizar_variaveis_estacao(
        saidas_modelo, candidatos, obrigatorias
    )
    for vertice in obrigatorias:
        variavel = variaveis_estacao[vertice]
        variavel.LB = 1.0
        variavel.UB = 1.0
    modelo.update()
    return len(obrigatorias)


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
    git_sha: str,
) -> dict:
    instance = instance_path.name
    radius = int(float(data["R"]))
    run_id = make_run_id(experiment_id, instance, radius, seed, variant)
    S, T, VI, V = data["S"], data["T"], data["VI"], data["V"]
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
    V_model, reachability_arcs, station_candidates, mandatory, prep_stats = (
        _preprocessar(
            estrategia=variant,
            nome_instancia=instance,
            S=S,
            T=T,
            V=V,
            adj=adjacency,
            R=radius,
            logger=preprocess_logger,
        )
    )
    preprocess_wall_s = time.monotonic() - preprocess_start
    preprocess_log_path = preprocess_logger.salvar()

    build_start = time.monotonic()
    model_outputs = construir_modelo_baseline(
        S=S,
        T=T,
        V=V_model,
        arcos=reachability_arcs,
        candidatos_estacao=station_candidates,
    )
    if not isinstance(model_outputs, tuple) or not model_outputs:
        raise RuntimeError("construir_modelo_baseline deve retornar uma tupla")
    model = model_outputs[0]
    fixed_count = _fixar_estacoes_obrigatorias(
        model,
        model_outputs,
        station_candidates,
        mandatory,
    )
    model_build_s = time.monotonic() - build_start

    elapsed_before_solver = time.monotonic() - total_start
    solver_time_limit_s = (
        max(0.0, time_limit_s - elapsed_before_solver)
        if budget_mode == "total"
        else time_limit_s
    )

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
                lower = callback_model.cbGet(GRB.Callback.MIP_OBJBND)
                upper = callback_model.cbGet(GRB.Callback.MIP_OBJBST)
                nodes = int(callback_model.cbGet(GRB.Callback.MIP_NODCNT))
                series.talvez_adicionar(runtime, lower, upper, nodes)
            elif where == GRB.Callback.MIPSOL:
                runtime = callback_model.cbGet(GRB.Callback.RUNTIME)
                upper = callback_model.cbGet(GRB.Callback.MIPSOL_OBJ)
                lower = callback_model.cbGet(GRB.Callback.MIP_OBJBND)
                nodes = int(callback_model.cbGet(GRB.Callback.MIP_NODCNT))
                series.talvez_adicionar(
                    runtime, lower, upper, nodes, forcar=True
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
        "M_base_pre": prep_stats["M_base_pre"],
        "A_R_bruto": prep_stats["A_R_bruto"],
        "A_R_final": len(reachability_arcs),
        "m": len(S),
        "candidatos_bruto": prep_stats["candidatos_bruto"],
        "candidatos_final": len(station_candidates),
        "grafo_folhas_removidas": prep_stats["grafo_folhas_removidas"],
        "grafo_grau2_diag": prep_stats.get("grafo_grau2_diag", ""),
        "candidatos_removidos_alcance": 0,
        "candidatos_removidos_dominancia": 0,
        "candidatos_removidos_total": 0,
        "arcos_removidos_irrelevantes": 0,
        "arcos_removidos_forcados_zero": 0,
        "A_R_removidos_total": 0,
        "preprocess_iteracoes": 1,
        "preprocess_s": prep_stats["preprocess_s"],
        "solver_s": solver_s,
        "diag_eq_classes": "",
        "diag_eq_candidatos": "",
        "diag_eq_maior_classe": "",
        "diag_qdom_90": "",
        "diag_qdom_95": "",
        "diag_qdom_99": "",
        "diag_global_classes": "",
        "diag_global_candidatos": "",
        "diag_global_maior_classe": "",
        "usa_folhas": prep_stats["usa_folhas"],
        "usa_separadores": True,
        "articulacoes_total": prep_stats["articulacoes_total"],
        "separadores_desbalanceados_total": prep_stats[
            "separadores_desbalanceados_total"
        ],
        "estacoes_obrigatorias_total": prep_stats[
            "estacoes_obrigatorias_total"
        ],
        "estacoes_obrigatorias_ids": prep_stats[
            "estacoes_obrigatorias_ids"
        ],
        "componentes_alcance_total": prep_stats[
            "componentes_alcance_total"
        ],
        "componentes_desbalanceadas_total": prep_stats[
            "componentes_desbalanceadas_total"
        ],
        "maior_desequilibrio": prep_stats["maior_desequilibrio"],
        "station_vars_fixed_one": fixed_count,
        "vars": safe_int(model_attribute(model, "NumVars", 0)) or 0,
        "cons": safe_int(model_attribute(model, "NumConstrs", 0)) or 0,
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
        "feasible_like": status == GRB.OPTIMAL
        or (is_time_limit and solcount > 0),
        "preprocess_wall_s": preprocess_wall_s,
        "model_build_s": model_build_s,
        "solver_log_path": str(solver_log_path),
        "preprocess_log_path": str(preprocess_log_path or ""),
        "timeseries_csv_path": str(timeseries_csv_path or ""),
        "plot_png_path": str(plot_png_path or ""),
        "simplex_iterations": safe_float(model_attribute(model, "IterCount")),
        "barrier_iterations": safe_float(
            model_attribute(model, "BarIterCount")
        ),
        "work_units": safe_float(model_attribute(model, "Work")),
        "model_nonzeros": safe_int(model_attribute(model, "NumNZs", 0)) or 0,
        "model_fingerprint": safe_int(
            model_attribute(model, "Fingerprint")
        ),
        "candidatos_removidos_total_global": len(V)
        - len(station_candidates),
        "erro": "",
    }
    return row


def parse_args():
    parser = argparse.ArgumentParser(
        description="Testa separadores obrigatórios no MIN-STATION."
    )
    parser.add_argument("--inputs-dir", default="./instancias")
    parser.add_argument("--output-dir", default="./experimentos_preprocess")
    parser.add_argument("--experiment-id", default=None)
    parser.add_argument("--instances", nargs="*", default=None)
    parser.add_argument(
        "--strategies",
        nargs="+",
        choices=ESTRATEGIAS,
        default=list(ESTRATEGIAS),
    )
    parser.add_argument(
        "--reference-runs-csv",
        action="append",
        default=[],
        help="runs.csv anterior. Pode ser informado mais de uma vez.",
    )
    parser.add_argument(
        "--only-reference-instances",
        action="store_true",
        help="Executa apenas instâncias presentes nos CSVs de referência.",
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[0])
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--time-limit", type=float, default=3600.0)
    parser.add_argument(
        "--budget-mode", choices=("total", "solver"), default="total"
    )
    parser.add_argument("--plot-sample", type=float, default=10.0)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--rerun", action="store_true")
    return parser.parse_args()


def _reference_keys(paths: list[Path]) -> set[tuple[str, str, str]]:
    keys = set()
    for path in paths:
        for row in load_runs(path):
            if row.get("variant") != "sem_preprocessamento":
                continue
            keys.add(
                (
                    row.get("instance", ""),
                    row.get("R", ""),
                    row.get("seed", ""),
                )
            )
    return keys


def main():
    args = parse_args()
    experiment_id = args.experiment_id or default_experiment_id()
    experiment_dir = Path(args.output_dir) / experiment_id
    runs_csv = experiment_dir / "runs.csv"
    comparison_csv = experiment_dir / "comparison_separadores.csv"
    json_dir = experiment_dir / "runs_json"

    reference_paths = [Path(path) for path in args.reference_runs_csv]
    missing = [str(path) for path in reference_paths if not path.is_file()]
    if missing:
        raise SystemExit("CSV(s) não encontrado(s): " + ", ".join(missing))

    files = choose_files(Path(args.inputs_dir), args.instances)
    reference_keys = _reference_keys(reference_paths)
    if args.only_reference_instances:
        if not reference_paths:
            raise SystemExit(
                "--only-reference-instances exige --reference-runs-csv"
            )
        nomes = {key[0] for key in reference_keys}
        files = [path for path in files if path.name in nomes]

    if not files:
        raise SystemExit("Nenhuma instância selecionada para execução")

    if os.environ.get("PYTHONHASHSEED") is None:
        print("[aviso] Defina PYTHONHASHSEED=0 para reprodutibilidade.")

    git_sha = current_git_sha()
    completed = existing_run_ids(runs_csv)
    variants = list(dict.fromkeys(args.strategies))

    print(f"Experimento: {experiment_id}")
    print(f"Instâncias candidatas: {len(files)}")
    print(f"Estratégias: {', '.join(variants)}")
    print(f"Seeds: {args.seeds}")
    print(f"Limite: {args.time_limit}s | modo={args.budget_mode}")

    for instance_path in files:
        try:
            data = ler_instancia(str(instance_path))
        except Exception as error:
            print(f"[{instance_path.name}] erro de leitura: {error}")
            continue

        radius = int(float(data["R"]))
        for seed in args.seeds:
            key = (instance_path.name, str(radius), str(seed))
            if args.only_reference_instances and key not in reference_keys:
                print(
                    f"[skip] baseline ausente para "
                    f"{instance_path.name}, R={radius}, seed={seed}"
                )
                continue

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
                    f"{instance_path.name} | R={radius} | "
                    f"seed={seed} | {variant}"
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
                        git_sha=git_sha,
                    )
                except Exception as error:
                    print(f"[erro] {run_id}: {error}")
                    continue

                save_run_json(row, json_dir)
                append_run_csv(row, runs_csv)
                completed.add(run_id)
                write_comparison_csv(
                    runs_csv=runs_csv,
                    comparison_csv=comparison_csv,
                    experiment_id=experiment_id,
                    reference_runs_csvs=reference_paths,
                )
                print(
                    f"[ok] obrigatórias={row['estacoes_obrigatorias_total']} | "
                    f"status={row['status_name']} | LI={row['LI']} | "
                    f"LS={row['LS']} | gap={row['gap_pct']}% | "
                    f"runtime={row['runtime_s']:.2f}s"
                )

    write_comparison_csv(
        runs_csv=runs_csv,
        comparison_csv=comparison_csv,
        experiment_id=experiment_id,
        reference_runs_csvs=reference_paths,
    )
    print(f"CSV detalhado: {runs_csv}")
    print(f"CSV comparativo: {comparison_csv}")


if __name__ == "__main__":
    main()
