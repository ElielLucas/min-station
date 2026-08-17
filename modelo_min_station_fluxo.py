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

def construir_modelo_baseline(S, T, VI, arcos, custos_estacao=None):
    """Constrói o modelo MIN-STATION (baseline) sobre o dígrafo de alcance A^R."""
    S = list(S); T = list(T); VI = list(VI)
    nos = set(S) | set(T) | set(VI)
    A = [(u, v) for (u, v) in arcos if (u in nos and v in nos and u != v)]

    arcos_entrada = {n: [] for n in nos}
    arcos_saida   = {n: [] for n in nos}
    for (u, v) in A:
        arcos_saida[u].append((u, v))
        arcos_entrada[v].append((u, v))

    m = len(S)
    if custos_estacao is None:
        custos_estacao = {v: 1.0 for v in VI}
    else:
        for v in VI:
            custos_estacao.setdefault(v, 1.0)

    modelo = Model("MIN-STATION")

    y = {v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]") for v in VI}
    f = {(u, v): modelo.addVar(lb=0.0, vtype=GRB.INTEGER, name=f"f[{u},{v}]") for (u, v) in A}

    modelo.setObjective(quicksum(custos_estacao[v] * y[v] for v in VI), GRB.MINIMIZE)

    for s in S:
        modelo.addConstr(quicksum(f[a] for a in arcos_entrada.get(s, [])) == 0, name=f"in_S[{s}]")
        modelo.addConstr(quicksum(f[a] for a in arcos_saida.get(s, []))   == 1, name=f"out_S[{s}]")
    for t in T:
        modelo.addConstr(quicksum(f[a] for a in arcos_entrada.get(t, [])) == 1, name=f"in_T[{t}]")
        modelo.addConstr(quicksum(f[a] for a in arcos_saida.get(t, []))   == 0, name=f"out_T[{t}]")
    for v in VI:
        modelo.addConstr(quicksum(f[a] for a in arcos_entrada.get(v, [])) ==
                         quicksum(f[a] for a in arcos_saida.get(v, [])),    name=f"fluxo_cons[{v}]")
        modelo.addConstr(quicksum(f[a] for a in arcos_entrada.get(v, [])) <= m * y[v], name=f"ativa_in[{v}]")

    modelo.update()
    return modelo, y, f, len(A), len(VI)

def executar_para_R(nome_instancia, 
                    S, 
                    T, 
                    VI, 
                    V, 
                    adj, 
                    R,
                    tempo_limite_s=1200,
                    pasta_plots = None,
                    plot_amostra_s=5.0,
                    plot_escala_y="linear",
                    plot_corte_ini_s=0.5,
                    plot_teto_pct=99.0,
                    plot_max_pontos=400,
                    plot_mostrar_gap=True):
    
    t0 = time.monotonic()

    A = construir_arcos_alcance(V, adj, R)
    tam_AR = len(A)

    modelo, y, f, tam_AR, tam_VI = construir_modelo_baseline(S=S, T=T, VI=VI, arcos=A)
    modelo.Params.TimeLimit = tempo_limite_s

    logger = RegistSerieTemporal(
        nome_instancia, R, pasta_plots,
        intervalo_amostra=plot_amostra_s,
        suffix="", titulo_tag="BASE"
    )

    def callback(m, where):
        try:
            if where == GRB.Callback.MIP:
                t   = m.cbGet(GRB.Callback.RUNTIME)
                lb  = m.cbGet(GRB.Callback.MIP_OBJBND)
                ub  = m.cbGet(GRB.Callback.MIP_OBJBST)
                nos = int(m.cbGet(GRB.Callback.MIP_NODCNT))
                logger.talvez_adicionar(t, lb, ub, nos)
            elif where == GRB.Callback.MIPSOL:
                t   = m.cbGet(GRB.Callback.RUNTIME)
                ub  = m.cbGet(GRB.Callback.MIPSOL_OBJ)
                lb  = m.cbGet(GRB.Callback.MIP_OBJBND)
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
    bateu_limite = (status == GRB.TIME_LIMIT)

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

    n_vars = modelo.NumVars
    n_cons = modelo.NumConstrs

    try:
        nos_busca_final = int(getattr(modelo, "NodeCount", 0))

        logger.talvez_adicionar(tempo, LI if LI is not None else float("nan"),
                                LS if LS is not None else float("nan"),
                                nos_busca_final, forcar=True)
        
        caminho_csv = logger.salvar_csv()
        caminho_png = logger.salvar_grafico(
            escala_y=plot_escala_y,
            corte_inicial_s=plot_corte_ini_s,
            teto_percentil=plot_teto_pct,
            mostrar_gap=plot_mostrar_gap,
            max_pontos=plot_max_pontos,
        )
        if caminho_csv: print(f"Série salva em: {caminho_csv}")
        if caminho_png: print(f"Gráfico salvo em: {caminho_png}")

    except Exception as e:
        print(f"Aviso ao salvar série/plot: {e}")

    linha = {
        "instance": nome_instancia,
        "R": R,
        "N_nodes": len(V),
        "M_base": sum(len(adj[u]) for u in adj),
        "A_R": tam_AR,
        "m": len(S),
        "VI": tam_VI,
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


def varrer_R_e_coletar(caminho_instancia,
                       tempo_limite_s,
                       pasta_plots,
                       plot_amostra_s,
                       plot_escala_y,
                       plot_corte_ini_s,
                       plot_teto_pct,
                       plot_max_pontos,
                       plot_mostrar_gap):
    
    nome = caminho_instancia.name

    try:
        dados = ler_instancia(str(caminho_instancia))
    except Exception as e:
        print(f"[{nome}] ERRO no parsing: {e}")
        return []

    S, T, VI, V, E_w, R0 = dados["S"], dados["T"], dados["VI"], dados["V"], dados["E"], dados["R"]
    adj = construir_adjacencia(E_w)

    linhas = []
    R_atual = float(R0)

    while True:
        print(f"\n[{nome}] ===== R = {R_atual} =====")

        linha = executar_para_R(
            nome_instancia=nome, 
            S=S, 
            T=T, 
            VI=VI, 
            V=V, 
            adj=adj, 
            R=R_atual,
            tempo_limite_s=tempo_limite_s,
            pasta_plots=pasta_plots,
            plot_amostra_s=plot_amostra_s,
            plot_escala_y=plot_escala_y,
            plot_corte_ini_s=plot_corte_ini_s,
            plot_teto_pct=plot_teto_pct,
            plot_max_pontos=plot_max_pontos,
            plot_mostrar_gap=plot_mostrar_gap,
        )
        linhas.append(linha)

        if (linha["status"] == GRB.INFEASIBLE) or (linha["A_R"] == 0) or (R_atual <= 0):
            break

        R_atual -= 1.0

    return linhas


CSV_HEADER = [
    "instance","R","N_nodes","M_base","A_R","m","VI","vars","cons",
    "status","solcount","LI","LS","gap","runtime_s","nodes","timelimit"
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
        description="Solver MIN-STATION (dirigido) — varre R decrescendo, salva resultados e gera gráficos LB/UBxtempo."
    )
    ap.add_argument("--inputs-dir", type=str, default="./inputs",
                    help="Pasta de instâncias. Padrão: ./inputs")
    ap.add_argument("--csv-out", type=str, default="results_min_station.csv",
                    help="CSV de saída (append). Padrão: results_min_station.csv")
    ap.add_argument("--time-limit", type=int, default=1200,
                    help="Tempo máximo por execução (s). Padrão: 1200 (20 min)")
    ap.add_argument("--plots-dir", type=str, default="plots",
                    help="Salvar PNG e CSV da série temporal aqui.")
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
        print("\n" + "="*80)
        print(f"Arquivo: {p.name}")
        print("="*80)
        linhas = varrer_R_e_coletar(
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
