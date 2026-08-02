import csv
import math
import time
import argparse
from pathlib import Path

from gurobipy import Model, GRB, quicksum

from ms_utils import (
    ler_instancia,
    construir_adjacencia,
    construir_arcos_alcance,
)


def nome_status_gurobi(status: int) -> str:
    nomes = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
    }
    return nomes.get(status, str(status))


def gap_percentual(ub, lb):
    if ub is None or lb is None:
        return None

    if abs(ub) <= 1e-12:
        return 0.0 if abs(ub - lb) <= 1e-12 else None

    return 100.0 * max(0.0, ub - lb) / abs(ub)


def append_csv(linhas: list[dict], caminho_csv: Path, header: list[str]) -> None:
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    primeira = not caminho_csv.exists()

    with caminho_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)

        if primeira:
            w.writeheader()

        for linha in linhas:
            w.writerow({k: linha.get(k, "") for k in header})


def preparar_estrutura_rede(S, T, V, arcos):
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
            f"Vértices em ambos os conjuntos: {sorted(map(str, intersecao_ST))}"
        )

    faltando_S = S_set - V_set
    faltando_T = T_set - V_set

    if faltando_S:
        raise ValueError(f"Há origens fora de V: {sorted(map(str, faltando_S))}")

    if faltando_T:
        raise ValueError(f"Há destinos fora de V: {sorted(map(str, faltando_T))}")

    A = []
    vistos = set()

    for u, v in arcos:
        if u in V_set and v in V_set and u != v and (u, v) not in vistos:
            A.append((u, v))
            vistos.add((u, v))

    arcos_entrada = {v: [] for v in V}
    arcos_saida = {v: [] for v in V}

    for u, v in A:
        arcos_saida[u].append((u, v))
        arcos_entrada[v].append((u, v))

    return S, T, V, A, arcos_entrada, arcos_saida


def construir_modelo_original_para_ub(S, T, V, A, arcos_entrada, arcos_saida, custos_estacao=None):
    """
    Modelo original completo, usado apenas para obter um limitante superior (UB).
    É a mesma formulação base com ativação explícita.
    """
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    if custos_estacao is None:
        custos_estacao = {v: 1.0 for v in V}
    else:
        for v in V:
            custos_estacao.setdefault(v, 1.0)

    modelo = Model("MIN-STATION-DAS-UB")
    modelo.Params.OutputFlag = 0

    y = {
        v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]")
        for v in V
    }

    f = {
        (u, v): modelo.addVar(lb=0.0, ub=m, vtype=GRB.INTEGER, name=f"f[{u},{v}]")
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

    for s in S:
        modelo.addConstr(
            saida[s] - entrada[s] == 1,
            name=f"balanco_origem[{s}]",
        )

    for t in T:
        modelo.addConstr(
            entrada[t] - saida[t] == 1,
            name=f"balanco_destino[{t}]",
        )

    for v in V:
        if v not in S_set and v not in T_set:
            modelo.addConstr(
                entrada[v] == saida[v],
                name=f"fluxo_cons[{v}]",
            )

    for v in V:
        if v not in T_set:
            modelo.addConstr(
                entrada[v] <= m * y[v],
                name=f"ativa_entrada_nao_destino[{v}]",
            )

    for t in T:
        modelo.addConstr(
            entrada[t] <= 1 + (m - 1) * y[t],
            name=f"ativa_entrada_destino[{t}]",
        )

    for v in V:
        if v not in S_set:
            modelo.addConstr(
                saida[v] <= m * y[v],
                name=f"ativa_saida_nao_origem[{v}]",
            )

    for s in S:
        modelo.addConstr(
            saida[s] <= 1 + (m - 1) * y[s],
            name=f"ativa_saida_origem[{s}]",
        )

    modelo.update()
    return modelo, y, f


def obter_ub_modelo_original(
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    tempo_limite_s,
    threads=None,
):
    if tempo_limite_s is None or tempo_limite_s <= 0:
        return {
            "UB": None,
            "LB_mip": None,
            "status_mip": None,
            "runtime_mip": 0.0,
            "solcount_mip": 0,
        }

    modelo, y, f = construir_modelo_original_para_ub(
        S=S,
        T=T,
        V=V,
        A=A,
        arcos_entrada=arcos_entrada,
        arcos_saida=arcos_saida,
    )

    modelo.Params.TimeLimit = tempo_limite_s

    if threads is not None and threads > 0:
        modelo.Params.Threads = threads

    t0 = time.monotonic()
    modelo.optimize()
    runtime = time.monotonic() - t0

    solcount = int(getattr(modelo, "SolCount", 0))

    UB = None
    LB_mip = None

    if solcount > 0:
        try:
            UB = float(modelo.ObjVal)
        except Exception:
            UB = None

    try:
        LB_mip = float(modelo.ObjBound)
    except Exception:
        LB_mip = None

    return {
        "UB": UB,
        "LB_mip": LB_mip,
        "status_mip": nome_status_gurobi(modelo.Status),
        "runtime_mip": runtime,
        "solcount_mip": solcount,
    }


def resolver_fluxo_lagrangeano(
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    alpha,
    beta,
    fluxo_inteiro=False,
    tempo_limite_s=0,
    threads=None,
):
    """
    Resolve o subproblema de fluxo da relaxação lagrangeana.

    Custos dos arcos:
        c_uv = beta[u] + alpha[v]

    Mantém apenas:
    - balanço nas origens;
    - balanço nos destinos;
    - conservação nos demais vértices;
    - domínio do fluxo.
    """
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    modelo = Model("LR-FLUXO")
    modelo.Params.OutputFlag = 0

    if tempo_limite_s is not None and tempo_limite_s > 0:
        modelo.Params.TimeLimit = tempo_limite_s

    if threads is not None and threads > 0:
        modelo.Params.Threads = threads

    vtype_fluxo = GRB.INTEGER if fluxo_inteiro else GRB.CONTINUOUS

    f = {
        (u, v): modelo.addVar(
            lb=0.0,
            ub=m,
            vtype=vtype_fluxo,
            name=f"f[{u},{v}]",
        )
        for (u, v) in A
    }

    custo_arco = {
        (u, v): beta[u] + alpha[v]
        for (u, v) in A
    }

    modelo.setObjective(
        quicksum(custo_arco[a] * f[a] for a in A),
        GRB.MINIMIZE,
    )

    entrada_expr = {
        v: quicksum(f[a] for a in arcos_entrada.get(v, []))
        for v in V
    }

    saida_expr = {
        v: quicksum(f[a] for a in arcos_saida.get(v, []))
        for v in V
    }

    for s in S:
        modelo.addConstr(
            saida_expr[s] - entrada_expr[s] == 1,
            name=f"balanco_origem[{s}]",
        )

    for t in T:
        modelo.addConstr(
            entrada_expr[t] - saida_expr[t] == 1,
            name=f"balanco_destino[{t}]",
        )

    for v in V:
        if v not in S_set and v not in T_set:
            modelo.addConstr(
                entrada_expr[v] == saida_expr[v],
                name=f"fluxo_cons[{v}]",
            )

    modelo.optimize()

    status = modelo.Status
    solcount = int(getattr(modelo, "SolCount", 0))

    if status != GRB.OPTIMAL and solcount == 0:
        return {
            "status": nome_status_gurobi(status),
            "tem_solucao": False,
            "runtime": float(getattr(modelo, "Runtime", 0.0)),
            "flow_cost": None,
            "f": None,
            "entrada": None,
            "saida": None,
        }

    f_val = {
        a: float(f[a].X)
        for a in A
    }

    entrada = {
        v: sum(f_val[a] for a in arcos_entrada.get(v, []))
        for v in V
    }

    saida = {
        v: sum(f_val[a] for a in arcos_saida.get(v, []))
        for v in V
    }

    return {
        "status": nome_status_gurobi(status),
        "tem_solucao": True,
        "runtime": float(getattr(modelo, "Runtime", 0.0)),
        "flow_cost": float(modelo.ObjVal),
        "f": f_val,
        "entrada": entrada,
        "saida": saida,
    }


def calcular_y_separavel(V, S, T, alpha, beta):
    """
    Resolve a parte separável em y da relaxação.

    q_v = 1 - (M-a_v) alpha_v - (M-b_v) beta_v

    y_v = 1 se q_v < 0; caso contrário, y_v = 0.
    """
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    y = {}
    q = {}

    for v in V:
        a_v = 1 if v in T_set else 0
        b_v = 1 if v in S_set else 0

        q_v = 1.0 - (m - a_v) * alpha[v] - (m - b_v) * beta[v]
        q[v] = q_v
        y[v] = 1.0 if q_v < -1e-12 else 0.0

    y_part = sum(q[v] * y[v] for v in V)

    return y, q, y_part


def avaliar_lagrangeano(S, T, V, entrada, saida, y, alpha, beta, flow_cost, y_part):
    """
    Calcula:
    - valor lagrangeano;
    - subgradientes das restrições relaxadas.
    """
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    constante = 0.0
    g_in = {}
    g_out = {}

    for v in V:
        a_v = 1 if v in T_set else 0
        b_v = 1 if v in S_set else 0

        constante -= alpha[v] * a_v
        constante -= beta[v] * b_v

        g_in[v] = entrada[v] - a_v - (m - a_v) * y[v]
        g_out[v] = saida[v] - b_v - (m - b_v) * y[v]

    valor_lagrangeano = flow_cost + y_part + constante

    norma2 = (
        sum(g_in[v] ** 2 for v in V)
        + sum(g_out[v] ** 2 for v in V)
    )

    norma = math.sqrt(norma2)

    max_g_in = max(g_in.values()) if g_in else 0.0
    max_g_out = max(g_out.values()) if g_out else 0.0

    soma_viol_pos = (
        sum(max(0.0, g_in[v]) for v in V)
        + sum(max(0.0, g_out[v]) for v in V)
    )

    return {
        "L": valor_lagrangeano,
        "constante": constante,
        "g_in": g_in,
        "g_out": g_out,
        "norma": norma,
        "norma2": norma2,
        "max_g_in": max_g_in,
        "max_g_out": max_g_out,
        "soma_viol_pos": soma_viol_pos,
    }


def calcular_passo(
    iteracao,
    regra,
    pi_atual,
    UB,
    L_atual,
    norma2,
    theta0,
):
    if norma2 <= 1e-18:
        return 0.0

    if regra == "polyak" and UB is not None and UB > L_atual:
        return pi_atual * (UB - L_atual) / norma2

    return theta0 / math.sqrt(max(1, iteracao))


def executar_lagrangeano_instancia(
    nome_instancia,
    S,
    T,
    VI,
    V,
    adj,
    R,
    max_iters,
    UB_manual,
    ub_time_limit,
    step_rule,
    pi_inicial,
    pi_decay,
    pi_min,
    stall_limit,
    theta0,
    alpha_init,
    beta_init,
    tol_norma,
    tol_melhoria,
    subproblem_time_limit,
    fluxo_inteiro,
    threads,
):
    t_total0 = time.monotonic()

    A_original = construir_arcos_alcance(V, adj, R)

    S, T, V, A, arcos_entrada, arcos_saida = preparar_estrutura_rede(
        S=S,
        T=T,
        V=V,
        arcos=A_original,
    )

    print(f"[{nome_instancia}] |V|={len(V)} |A_r|={len(A)} |S|=|T|={len(S)} R={R}")

    info_ub = {
        "UB": UB_manual,
        "LB_mip": None,
        "status_mip": "UB_MANUAL" if UB_manual is not None else None,
        "runtime_mip": 0.0,
        "solcount_mip": 1 if UB_manual is not None else 0,
    }

    if UB_manual is None and ub_time_limit is not None and ub_time_limit > 0:
        print(f"[{nome_instancia}] Calculando UB pelo modelo original por {ub_time_limit}s...")
        info_ub = obter_ub_modelo_original(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            tempo_limite_s=ub_time_limit,
            threads=threads,
        )

    UB = info_ub["UB"]

    if UB is None:
        print(
            f"[{nome_instancia}] Aviso: nenhum UB disponível. "
            f"O passo Polyak será substituído por passo decrescente."
        )
    else:
        print(f"[{nome_instancia}] UB inicial = {UB}")

    alpha = {v: float(alpha_init) for v in V}
    beta = {v: float(beta_init) for v in V}

    pi_atual = float(pi_inicial)
    melhor_LB = -float("inf")
    melhor_iter = None
    sem_melhora = 0

    linhas_iter = []

    for k in range(1, max_iters + 1):
        t_iter0 = time.monotonic()

        fluxo = resolver_fluxo_lagrangeano(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            alpha=alpha,
            beta=beta,
            fluxo_inteiro=fluxo_inteiro,
            tempo_limite_s=subproblem_time_limit,
            threads=threads,
        )

        if not fluxo["tem_solucao"]:
            linha = {
                "instance": nome_instancia,
                "R": R,
                "iter": k,
                "status_subproblema": fluxo["status"],
                "L_atual": "",
                "melhor_LB": "" if melhor_LB == -float("inf") else melhor_LB,
                "UB": "" if UB is None else UB,
                "gap_lagrangeano_pct": "",
                "norma_subgrad": "",
                "theta": "",
                "pi": pi_atual,
                "flow_cost": "",
                "y_part": "",
                "constante": "",
                "num_y_1": "",
                "max_g_in": "",
                "max_g_out": "",
                "soma_viol_pos": "",
                "runtime_iter_s": time.monotonic() - t_iter0,
                "runtime_total_s": time.monotonic() - t_total0,
            }
            linhas_iter.append(linha)
            print(f"[{nome_instancia}] Subproblema sem solução na iteração {k}: {fluxo['status']}")
            break

        y, q, y_part = calcular_y_separavel(
            V=V,
            S=S,
            T=T,
            alpha=alpha,
            beta=beta,
        )

        avaliacao = avaliar_lagrangeano(
            S=S,
            T=T,
            V=V,
            entrada=fluxo["entrada"],
            saida=fluxo["saida"],
            y=y,
            alpha=alpha,
            beta=beta,
            flow_cost=fluxo["flow_cost"],
            y_part=y_part,
        )

        L_atual = avaliacao["L"]
        norma2 = avaliacao["norma2"]
        norma = avaliacao["norma"]

        if L_atual > melhor_LB + tol_melhoria:
            melhor_LB = L_atual
            melhor_iter = k
            sem_melhora = 0
        else:
            sem_melhora += 1

        if sem_melhora >= stall_limit:
            pi_atual = max(pi_min, pi_atual * pi_decay)
            sem_melhora = 0

        theta = calcular_passo(
            iteracao=k,
            regra=step_rule,
            pi_atual=pi_atual,
            UB=UB,
            L_atual=L_atual,
            norma2=norma2,
            theta0=theta0,
        )

        gap_lag = gap_percentual(UB, melhor_LB)

        linha = {
            "instance": nome_instancia,
            "R": R,
            "iter": k,
            "status_subproblema": fluxo["status"],
            "L_atual": L_atual,
            "melhor_LB": melhor_LB,
            "UB": "" if UB is None else UB,
            "gap_lagrangeano_pct": "" if gap_lag is None else gap_lag,
            "norma_subgrad": norma,
            "theta": theta,
            "pi": pi_atual,
            "flow_cost": fluxo["flow_cost"],
            "y_part": y_part,
            "constante": avaliacao["constante"],
            "num_y_1": int(sum(1 for v in V if y[v] > 0.5)),
            "max_g_in": avaliacao["max_g_in"],
            "max_g_out": avaliacao["max_g_out"],
            "soma_viol_pos": avaliacao["soma_viol_pos"],
            "runtime_iter_s": time.monotonic() - t_iter0,
            "runtime_total_s": time.monotonic() - t_total0,
        }
        linhas_iter.append(linha)

        if k == 1 or k % 10 == 0 or k == max_iters:
            gap_txt = "NA" if gap_lag is None else f"{gap_lag:.2f}%"
            print(
                f"[{nome_instancia}] it={k:04d} "
                f"L={L_atual:.4f} bestLB={melhor_LB:.4f} "
                f"UB={UB if UB is not None else 'NA'} gap={gap_txt} "
                f"||g||={norma:.4f} theta={theta:.6g} pi={pi_atual:.4f}"
            )

        if norma <= tol_norma:
            print(f"[{nome_instancia}] Parou por norma do subgradiente <= {tol_norma}.")
            break

        if theta <= 1e-18:
            print(f"[{nome_instancia}] Parou por passo praticamente zero.")
            break

        g_in = avaliacao["g_in"]
        g_out = avaliacao["g_out"]

        for v in V:
            alpha[v] = max(0.0, alpha[v] + theta * g_in[v])
            beta[v] = max(0.0, beta[v] + theta * g_out[v])

    runtime_total = time.monotonic() - t_total0

    resumo = {
        "instance": nome_instancia,
        "R": R,
        "N_nodes": len(V),
        "A_R": len(A),
        "m": len(S),
        "VI": len(VI),
        "max_iters": max_iters,
        "iters_executadas": len(linhas_iter),
        "melhor_LB_lagrangeano": "" if melhor_LB == -float("inf") else melhor_LB,
        "melhor_iter": "" if melhor_iter is None else melhor_iter,
        "UB": "" if UB is None else UB,
        "gap_lagrangeano_pct": "" if gap_percentual(UB, melhor_LB) is None else gap_percentual(UB, melhor_LB),
        "status_mip_ub": info_ub["status_mip"],
        "LB_mip_ub": "" if info_ub["LB_mip"] is None else info_ub["LB_mip"],
        "runtime_mip_ub_s": info_ub["runtime_mip"],
        "solcount_mip_ub": info_ub["solcount_mip"],
        "runtime_total_s": runtime_total,
        "step_rule": step_rule,
        "pi_inicial": pi_inicial,
        "pi_final": pi_atual,
        "fluxo_inteiro": fluxo_inteiro,
    }

    return resumo, linhas_iter


ITER_HEADER = [
    "instance",
    "R",
    "iter",
    "status_subproblema",
    "L_atual",
    "melhor_LB",
    "UB",
    "gap_lagrangeano_pct",
    "norma_subgrad",
    "theta",
    "pi",
    "flow_cost",
    "y_part",
    "constante",
    "num_y_1",
    "max_g_in",
    "max_g_out",
    "soma_viol_pos",
    "runtime_iter_s",
    "runtime_total_s",
]

RESUMO_HEADER = [
    "instance",
    "R",
    "N_nodes",
    "A_R",
    "m",
    "VI",
    "max_iters",
    "iters_executadas",
    "melhor_LB_lagrangeano",
    "melhor_iter",
    "UB",
    "gap_lagrangeano_pct",
    "status_mip_ub",
    "LB_mip_ub",
    "runtime_mip_ub_s",
    "solcount_mip_ub",
    "runtime_total_s",
    "step_rule",
    "pi_inicial",
    "pi_final",
    "fluxo_inteiro",
]


def executar_arquivo(
    caminho_instancia: Path,
    args,
):
    nome = caminho_instancia.name

    try:
        dados = ler_instancia(str(caminho_instancia))
    except Exception as e:
        print(f"[{nome}] ERRO no parsing: {e}")
        return None, []

    S = dados["S"]
    T = dados["T"]
    VI = dados["VI"]
    V = dados["V"]
    E_w = dados["E"]
    R0 = dados["R"]

    adj = construir_adjacencia(E_w)
    R_instancia = int(float(R0))

    print("\n" + "=" * 80)
    print(f"Arquivo: {nome}")
    print(f"R original: {R_instancia}")
    print("=" * 80)

    resumo, linhas_iter = executar_lagrangeano_instancia(
        nome_instancia=nome,
        S=S,
        T=T,
        VI=VI,
        V=V,
        adj=adj,
        R=R_instancia,
        max_iters=args.max_iters,
        UB_manual=args.ub,
        ub_time_limit=args.ub_time_limit,
        step_rule=args.step_rule,
        pi_inicial=args.pi,
        pi_decay=args.pi_decay,
        pi_min=args.pi_min,
        stall_limit=args.stall_limit,
        theta0=args.theta0,
        alpha_init=args.alpha_init,
        beta_init=args.beta_init,
        tol_norma=args.tol_norma,
        tol_melhoria=args.tol_melhoria,
        subproblem_time_limit=args.subproblem_time_limit,
        fluxo_inteiro=args.fluxo_inteiro,
        threads=args.threads,
    )

    return resumo, linhas_iter


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Relaxação lagrangeana para o MIN-STATION original de Das. "
            "Relaxa as restrições de ativação e resolve o dual por subgradiente."
        )
    )

    ap.add_argument(
        "--inputs-dir",
        type=str,
        default="./inputs",
        help="Pasta com instâncias .txt. Padrão: ./inputs",
    )

    ap.add_argument(
        "--out-dir",
        type=str,
        default="results_lagrangeano",
        help="Pasta de saída dos CSVs. Padrão: results_lagrangeano",
    )

    ap.add_argument(
        "--max-iters",
        type=int,
        default=200,
        help="Número máximo de iterações do subgradiente. Padrão: 200",
    )

    ap.add_argument(
        "--ub",
        type=float,
        default=None,
        help="UB manual. Recomendo usar apenas quando executar uma única instância.",
    )

    ap.add_argument(
        "--ub-time-limit",
        type=float,
        default=60.0,
        help=(
            "Tempo para rodar o modelo original e obter UB. "
            "Use 0 para não calcular UB. Padrão: 60."
        ),
    )

    ap.add_argument(
        "--step-rule",
        type=str,
        choices=["polyak", "diminishing"],
        default="polyak",
        help="Regra de passo. Padrão: polyak.",
    )

    ap.add_argument(
        "--pi",
        type=float,
        default=1.8,
        help="Parâmetro pi do passo de Polyak. Padrão: 1.8",
    )

    ap.add_argument(
        "--pi-decay",
        type=float,
        default=0.5,
        help="Fator de redução de pi após estagnação. Padrão: 0.5",
    )

    ap.add_argument(
        "--pi-min",
        type=float,
        default=0.05,
        help="Menor valor permitido para pi. Padrão: 0.05",
    )

    ap.add_argument(
        "--stall-limit",
        type=int,
        default=20,
        help="Iterações sem melhora antes de reduzir pi. Padrão: 20",
    )

    ap.add_argument(
        "--theta0",
        type=float,
        default=1.0,
        help="Passo inicial para regra decrescente. Padrão: 1.0",
    )

    ap.add_argument(
        "--alpha-init",
        type=float,
        default=0.0,
        help="Valor inicial dos multiplicadores alpha. Padrão: 0.",
    )

    ap.add_argument(
        "--beta-init",
        type=float,
        default=0.0,
        help="Valor inicial dos multiplicadores beta. Padrão: 0.",
    )

    ap.add_argument(
        "--tol-norma",
        type=float,
        default=1e-6,
        help="Tolerância para norma do subgradiente. Padrão: 1e-6",
    )

    ap.add_argument(
        "--tol-melhoria",
        type=float,
        default=1e-6,
        help="Tolerância para considerar melhora no LB. Padrão: 1e-6",
    )

    ap.add_argument(
        "--subproblem-time-limit",
        type=float,
        default=0.0,
        help="Tempo limite para cada subproblema de fluxo. 0 significa sem limite.",
    )

    ap.add_argument(
        "--fluxo-inteiro",
        action="store_true",
        help=(
            "Usa f inteiro no subproblema. Por padrão usa fluxo contínuo, "
            "aproveitando a estrutura de fluxo."
        ),
    )

    ap.add_argument(
        "--threads",
        type=int,
        default=0,
        help="Número de threads do Gurobi. 0 usa padrão do Gurobi.",
    )

    args = ap.parse_args()

    if args.threads <= 0:
        args.threads = None

    pasta = Path(args.inputs_dir)
    arquivos = sorted([p for p in pasta.glob("*.txt") if p.is_file()])

    if not arquivos:
        print(f"Nenhum .txt encontrado em {pasta}.")
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    caminho_iter = out_dir / "lagrangeano_iteracoes.csv"
    caminho_resumo = out_dir / "lagrangeano_resumo.csv"

    print(f"{len(arquivos)} arquivo(s) encontrado(s) em {pasta}")
    print(f"CSV de iterações: {caminho_iter}")
    print(f"CSV de resumo: {caminho_resumo}")

    total_instancias = 0

    for caminho in arquivos:
        resumo, linhas_iter = executar_arquivo(caminho, args)

        if linhas_iter:
            append_csv(linhas_iter, caminho_iter, ITER_HEADER)

        if resumo is not None:
            append_csv([resumo], caminho_resumo, RESUMO_HEADER)
            total_instancias += 1

    print(f"\n[ok] {total_instancias} instância(s) processada(s).")
    print(f"[ok] Iterações salvas em: {caminho_iter}")
    print(f"[ok] Resumo salvo em: {caminho_resumo}")


if __name__ == "__main__":
    main()