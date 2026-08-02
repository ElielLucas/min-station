import csv
import time
import argparse
from pathlib import Path

from gurobipy import Model, GRB, quicksum
from ms_utils import (
    ler_instancia,
    construir_adjacencia,
    construir_arcos_alcance,
    RegistSerieTemporal,
)


def construir_modelo_baseline(S, T, V, arcos, custos_estacao=None):
    """
    Constrói uma formulação PLI para o MIN-STATION original de Das.

    Nesta versão:
    - y[v] é criado para todo v em V;
    - a função objetivo minimiza estações em todo V;
    - origens têm balanço líquido de saída igual a 1;
    - destinos têm balanço líquido de entrada igual a 1;
    - demais vértices conservam fluxo;
    - a ativação é escrita separadamente para:
        * entrada em vértices que não são destinos;
        * entrada nos destinos;
        * saída de vértices que não são origens;
        * saída das origens.
    """
    S = list(S)
    T = list(T)
    V = list(V)

    S_set = set(S)
    T_set = set(T)
    V_set = set(V)

    if len(S) != len(T):
        raise ValueError(
            f"MIN-STATION exige |S| = |T|. Recebido |S|={len(S)} e |T|={len(T)}."
        )

    intersecao_ST = S_set & T_set
    if intersecao_ST:
        raise ValueError(
            "Esta formulação assume S e T disjuntos. "
            f"Vértices em ambos os conjuntos: {sorted(intersecao_ST)}"
        )

    faltando_S = S_set - V_set
    faltando_T = T_set - V_set

    if faltando_S:
        raise ValueError(f"Há origens fora de V: {sorted(faltando_S)}")

    if faltando_T:
        raise ValueError(f"Há destinos fora de V: {sorted(faltando_T)}")

    A = [
        (u, v)
        for (u, v) in arcos
        if u in V_set and v in V_set and u != v
    ]

    arcos_entrada = {n: [] for n in V}
    arcos_saida = {n: [] for n in V}

    for u, v in A:
        arcos_saida[u].append((u, v))
        arcos_entrada[v].append((u, v))

    m = len(S)

    if custos_estacao is None:
        custos_estacao = {v: 1.0 for v in V}
    else:
        for v in V:
            custos_estacao.setdefault(v, 1.0)

    modelo = Model("MIN-STATION-DAS")

    y = {
        v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]")
        for v in V
    }

    f = {
        (u, v): modelo.addVar(lb=0.0, vtype=GRB.INTEGER, name=f"f[{u},{v}]")
        for (u, v) in A
    }

    modelo.setObjective(
        quicksum(custos_estacao[v] * y[v] for v in V),
        GRB.MINIMIZE,
    )

    entrada = {
        v: quicksum(f[a] for a in arcos_entrada.get(v, []))
        for v in V
    }

    saida = {
        v: quicksum(f[a] for a in arcos_saida.get(v, []))
        for v in V
    }

    # Fluxo em fontes e sumidouros
    # Balanço nas origens: sai uma unidade líquida de fluxo.
    for s in S:
        modelo.addConstr(
            saida[s] - entrada[s] == 1,
            name=f"balanco_origem[{s}]",
        )

    # Balanço nos destinos: entra uma unidade líquida de fluxo.
    for t in T:
        modelo.addConstr(
            entrada[t] - saida[t] == 1,
            name=f"balanco_destino[{t}]",
        )

    # Conservação de fluxo nos demais vértices.
    for v in V:
        if v not in S_set and v not in T_set:
            modelo.addConstr(
                entrada[v] == saida[v],
                name=f"fluxo_cons[{v}]",
            )

    # Ativação por instalação
    # Entrada em vértices que não são destinos.
    for v in V:
        if v not in T_set:
            modelo.addConstr(
                entrada[v] <= m * y[v],
                name=f"ativa_entrada_nao_destino[{v}]",
            )

    # Entrada nos destinos.
    for t in T:
        modelo.addConstr(
            entrada[t] <= 1 + (m - 1) * y[t],
            name=f"ativa_entrada_destino[{t}]",
        )

    # Saída de vértices que não são origens.
    for v in V:
        if v not in S_set:
            modelo.addConstr(
                saida[v] <= m * y[v],
                name=f"ativa_saida_nao_origem[{v}]",
            )

    # Saída das origens.
    for s in S:
        modelo.addConstr(
            saida[s] <= 1 + (m - 1) * y[s],
            name=f"ativa_saida_origem[{s}]",
        )

    modelo.update()

    return modelo, y, f, len(A), len(V)


def executar_para_R(
    nome_instancia,
    S,
    T,
    VI,
    V,
    adj,
    R,
    tempo_limite_s=1200,
    pasta_plots=None,
    plot_amostra_s=5.0,
    plot_escala_y="linear",
    plot_corte_ini_s=0.5,
    plot_teto_pct=99.0,
    plot_max_pontos=400,
    plot_mostrar_gap=True,
):
    t0 = time.monotonic()

    A = construir_arcos_alcance(V, adj, R)
    tam_AR = len(A)

    modelo, y, f, tam_AR, tam_candidatos = construir_modelo_baseline(
        S=S,
        T=T,
        V=V,
        arcos=A,
    )

    modelo.Params.TimeLimit = tempo_limite_s

    logger = RegistSerieTemporal(
        nome_instancia,
        R,
        pasta_plots,
        intervalo_amostra=plot_amostra_s,
        suffix="",
        titulo_tag="BASE_DAS",
    )

    def callback(m, where):
        try:
            if where == GRB.Callback.MIP:
                t = m.cbGet(GRB.Callback.RUNTIME)
                lb = m.cbGet(GRB.Callback.MIP_OBJBND)
                ub = m.cbGet(GRB.Callback.MIP_OBJBST)
                nos = int(m.cbGet(GRB.Callback.MIP_NODCNT))
                logger.talvez_adicionar(t, lb, ub, nos)

            elif where == GRB.Callback.MIPSOL:
                t = m.cbGet(GRB.Callback.RUNTIME)
                ub = m.cbGet(GRB.Callback.MIPSOL_OBJ)
                lb = m.cbGet(GRB.Callback.MIP_OBJBND)
                nos = int(m.cbGet(GRB.Callback.MIP_NODCNT))
                logger.talvez_adicionar(t, lb, ub, nos, forcar=True)

        except Exception:
            pass

    modelo.optimize(callback)

    t1 = time.monotonic()
    tempo = t1 - t0

    status = modelo.Status
    solcount = getattr(modelo, "SolCount", 0)

    LS = None
    LI = None
    gap = None

    bateu_limite = status == GRB.TIME_LIMIT

    if solcount > 0:
        try:
            LS = float(modelo.ObjVal)
        except Exception:
            LS = None

    try:
        LI = float(modelo.ObjBound)
    except Exception:
        LI = None

    try:
        if solcount > 0:
            gap = float(modelo.MIPGap)
    except Exception:
        gap = None

    n_vars = len(A) + tam_candidatos
    n_cons = 3 * len(V)

    try:
        nos_busca_final = int(getattr(modelo, "NodeCount", 0))

        logger.talvez_adicionar(
            tempo,
            LI if LI is not None else float("nan"),
            LS if LS is not None else float("nan"),
            nos_busca_final,
            forcar=True,
        )

        caminho_csv = logger.salvar_csv()
        caminho_png = logger.salvar_grafico(
            escala_y=plot_escala_y,
            corte_inicial_s=plot_corte_ini_s,
            teto_percentil=plot_teto_pct,
            mostrar_gap=plot_mostrar_gap,
            max_pontos=plot_max_pontos,
        )

        if caminho_csv:
            print(f"Série salva em: {caminho_csv}")

        if caminho_png:
            print(f"Gráfico salvo em: {caminho_png}")

    except Exception as e:
        print(f"Aviso ao salvar série/plot: {e}")

    linha = {
        "instance": nome_instancia,
        "R": R,
        "N_nodes": len(V),
        "M_base": sum(len(adj[u]) for u in adj),
        "A_R": tam_AR,
        "m": len(S),
        "VI": len(VI),
        "candidatos": tam_candidatos,
        "vars": n_vars,
        "cons": n_cons,
        "status": status,
        "solcount": solcount,
        "LI": LI,
        "LS": LS,
        "gap": gap,
        "runtime_s": tempo,
        "nodes": int(getattr(modelo, "NodeCount", 0)),
        "timelimit": bateu_limite,
        "feasible_like": (status == GRB.OPTIMAL) or (bateu_limite and solcount > 0),
    }

    return linha


def executar_instancia_e_coletar(
    caminho_instancia,
    tempo_limite_s,
    pasta_plots,
    plot_amostra_s,
    plot_escala_y,
    plot_corte_ini_s,
    plot_teto_pct,
    plot_max_pontos,
    plot_mostrar_gap,
):
    nome = caminho_instancia.name

    try:
        dados = ler_instancia(str(caminho_instancia))
    except Exception as e:
        print(f"[{nome}] ERRO no parsing: {e}")
        return []

    S = dados["S"]
    T = dados["T"]
    VI = dados["VI"]
    V = dados["V"]
    E_w = dados["E"]
    R0 = dados["R"]

    adj = construir_adjacencia(E_w)

    R_instancia = int(float(R0))

    print(f"\n[{nome}] ===== R = {R_instancia} =====")

    linha = executar_para_R(
        nome_instancia=nome,
        S=S,
        T=T,
        VI=VI,
        V=V,
        adj=adj,
        R=R_instancia,
        tempo_limite_s=tempo_limite_s,
        pasta_plots=pasta_plots,
        plot_amostra_s=plot_amostra_s,
        plot_escala_y=plot_escala_y,
        plot_corte_ini_s=plot_corte_ini_s,
        plot_teto_pct=plot_teto_pct,
        plot_max_pontos=plot_max_pontos,
        plot_mostrar_gap=plot_mostrar_gap,
    )

    return [linha]


CSV_HEADER = [
    "instance",
    "R",
    "N_nodes",
    "M_base",
    "A_R",
    "m",
    "VI",
    "candidatos",
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
]


def write_csv(linhas: list[dict], caminho_csv: Path) -> None:
    primeira = not caminho_csv.exists()

    with caminho_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)

        if primeira:
            w.writeheader()

        for r in linhas:
            w.writerow({k: r.get(k, "") for k in CSV_HEADER})


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Solver MIN-STATION original de Das sobre dígrafo de alcance. "
            "Executa somente o R original de cada instância, salva resultados "
            "e gera gráficos LB/UB x tempo."
        )
    )

    ap.add_argument(
        "--inputs-dir",
        type=str,
        default="./inputs",
        help="Pasta de instâncias. Padrão: ./inputs",
    )

    ap.add_argument(
        "--csv-out",
        type=str,
        default="results_min_station_das.csv",
        help="CSV de saída append. Padrão: results_min_station_das.csv",
    )

    ap.add_argument(
        "--time-limit",
        type=int,
        default=1200,
        help="Tempo máximo por execução em segundos. Padrão: 1200.",
    )

    ap.add_argument(
        "--plots-dir",
        type=str,
        default="plots",
        help="Pasta para salvar PNG e CSV da série temporal.",
    )

    args = ap.parse_args()

    pasta = Path(args.inputs_dir)
    arquivos = sorted([p for p in pasta.glob("*.txt") if p.is_file()])

    if not arquivos:
        print(f"Nenhum .txt em {pasta}.")
        return

    pasta_plots = Path(args.plots_dir) if args.plots_dir else None

    print(f"{len(arquivos)} arquivo(s) encontrados em {pasta}")

    total = 0
    caminho_csv = Path(args.csv_out)

    for p in arquivos:
        print("\n" + "=" * 80)
        print(f"Arquivo: {p.name}")
        print("=" * 80)

        linhas = executar_instancia_e_coletar(
            p,
            tempo_limite_s=args.time_limit,
            pasta_plots=pasta_plots,
            plot_amostra_s=10,
            plot_escala_y="symlog",
            plot_corte_ini_s=0.5,
            plot_teto_pct=99,
            plot_max_pontos=400,
            plot_mostrar_gap=True,
        )

        write_csv(linhas, caminho_csv)
        total += len(linhas)

    print(f"\n[ok] {total} linha(s) salvas em {caminho_csv}")


if __name__ == "__main__":
    main()