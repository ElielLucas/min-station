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


def adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida):
    S_set = set(S)
    T_set = set(T)

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


def adicionar_ativacao_entrada(modelo, S, T, V, entrada, y):
    T_set = set(T)
    m = len(S)

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


def adicionar_ativacao_saida(modelo, S, T, V, saida, y):
    S_set = set(S)
    m = len(S)

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


def construir_modelo_original_para_ub(S, T, V, A, arcos_entrada, arcos_saida):
    m = len(S)

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
        quicksum(y[v] for v in V),
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

    adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida)
    adicionar_ativacao_entrada(modelo, S, T, V, entrada, y)
    adicionar_ativacao_saida(modelo, S, T, V, saida, y)

    modelo.update()
    return modelo


def obter_ub_modelo_original(S, T, V, A, arcos_entrada, arcos_saida, tempo_limite_s, threads):
    if tempo_limite_s is None or tempo_limite_s <= 0:
        return {
            "UB": None,
            "LB_mip": None,
            "status_mip": None,
            "runtime_mip": 0.0,
            "solcount_mip": 0,
        }

    modelo = construir_modelo_original_para_ub(
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


def coeficientes_lagrangeanos_por_vertice(v, S_set, T_set, m, alpha, beta, relax_mode):
    """
    Retorna o coeficiente de y_v e a parte constante associada aos multiplicadores.

    Ativação de entrada:
        In_v - a_v - (m-a_v)y_v <= 0

    Ativação de saída:
        Out_v - b_v - (m-b_v)y_v <= 0
    """
    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}

    a_v = 1 if v in T_set else 0
    b_v = 1 if v in S_set else 0

    q_v = 1.0
    constante_v = 0.0

    if relax_in:
        q_v -= (m - a_v) * alpha[v]
        constante_v -= alpha[v] * a_v

    if relax_out:
        q_v -= (m - b_v) * beta[v]
        constante_v -= beta[v] * b_v

    return q_v, constante_v


def obter_obj_bound_seguro(modelo):
    try:
        valor = float(modelo.ObjBound)
        if math.isfinite(valor):
            return valor
    except Exception:
        pass

    return None


def obter_obj_val_seguro(modelo):
    try:
        valor = float(modelo.ObjVal)
        if math.isfinite(valor):
            return valor
    except Exception:
        pass

    return None


def resolver_subproblema_lagrangeano(
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    alpha,
    beta,
    relax_mode,
    fluxo_inteiro,
    subproblem_time_limit,
    threads,
    usar_tiebreak=True,
    tiebreak_tol=1e-7,
):
    """Resolve o subproblema lagrangeano."""
    
    if relax_mode not in {"all", "in", "out"}:
        raise ValueError(f"relax_mode inválido: {relax_mode}")

    t_sub0 = time.monotonic()

    S_set = set(S)
    T_set = set(T)
    m = len(S)

    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}

    modelo = Model(f"LR-SUBPROBLEM-{relax_mode}")
    modelo.Params.OutputFlag = 0

    if subproblem_time_limit is not None and subproblem_time_limit > 0:
        modelo.Params.TimeLimit = subproblem_time_limit

    if threads is not None and threads > 0:
        modelo.Params.Threads = threads

    vtype_fluxo = GRB.INTEGER if fluxo_inteiro else GRB.CONTINUOUS

    y = {
        v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]")
        for v in V
    }

    f = {
        (u, v): modelo.addVar(
            lb=0.0,
            ub=m,
            vtype=vtype_fluxo,
            name=f"f[{u},{v}]",
        )
        for (u, v) in A
    }

    entrada = {
        v: quicksum(f[a] for a in arcos_entrada.get(v, []))
        for v in V
    }

    saida = {
        v: quicksum(f[a] for a in arcos_saida.get(v, []))
        for v in V
    }

    objetivo_fluxo = quicksum(
        (
            (alpha[v] if relax_in else 0.0)
            +
            (beta[u] if relax_out else 0.0)
        ) * f[(u, v)]
        for (u, v) in A
    )

    objetivo_y = quicksum(
        coeficientes_lagrangeanos_por_vertice(
            v=v,
            S_set=S_set,
            T_set=T_set,
            m=m,
            alpha=alpha,
            beta=beta,
            relax_mode=relax_mode,
        )[0] * y[v]
        for v in V
    )

    constante = sum(
        coeficientes_lagrangeanos_por_vertice(
            v=v,
            S_set=S_set,
            T_set=T_set,
            m=m,
            alpha=alpha,
            beta=beta,
            relax_mode=relax_mode,
        )[1]
        for v in V
    )

    objetivo_lagrangeano = objetivo_fluxo + objetivo_y + constante
    fluxo_total = quicksum(f[a] for a in A)

    modelo.setObjective(
        objetivo_lagrangeano,
        GRB.MINIMIZE,
    )

    adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida)

    if not relax_in:
        adicionar_ativacao_entrada(modelo, S, T, V, entrada, y)

    if not relax_out:
        adicionar_ativacao_saida(modelo, S, T, V, saida, y)

    modelo.optimize()

    status_1 = modelo.Status
    status_1_nome = nome_status_gurobi(status_1)
    solcount_1 = int(getattr(modelo, "SolCount", 0))

    obj_bound = obter_obj_bound_seguro(modelo)
    L_incumbente = obter_obj_val_seguro(modelo) if solcount_1 > 0 else None

    if status_1 == GRB.OPTIMAL:
        L_bound_certificado = L_incumbente
        subgradiente_valido = True
    else:
        L_bound_certificado = obj_bound
        subgradiente_valido = False

    if solcount_1 == 0:
        return {
            "status": status_1_nome,
            "status_lagrangeano": status_1_nome,
            "status_tiebreak": "",
            "tem_solucao": False,
            "subgradiente_valido": False,
            "L": L_incumbente,
            "L_incumbente_subproblema": L_incumbente,
            "L_bound_certificado": L_bound_certificado,
            "obj_bound": obj_bound,
            "fluxo_total_tiebreak": None,
            "runtime": time.monotonic() - t_sub0,
            "y": None,
            "f": None,
            "entrada": None,
            "saida": None,
            "num_y_1": None,
        }

    status_final_nome = status_1_nome
    status_tiebreak_nome = ""
    fluxo_total_tiebreak = None

    if usar_tiebreak and status_1 == GRB.OPTIMAL:
        modelo.addConstr(
            objetivo_lagrangeano <= L_incumbente + tiebreak_tol,
            name="fixa_obj_lagrangeano_para_tiebreak",
        )

        modelo.setObjective(
            fluxo_total,
            GRB.MINIMIZE,
        )

        modelo.optimize()

        status_2 = modelo.Status
        status_tiebreak_nome = nome_status_gurobi(status_2)
        solcount_2 = int(getattr(modelo, "SolCount", 0))

        if status_2 == GRB.OPTIMAL or solcount_2 > 0:
            status_final_nome = status_tiebreak_nome
            try:
                fluxo_total_tiebreak = float(modelo.ObjVal)
            except Exception:
                fluxo_total_tiebreak = None
        else:
            status_final_nome = f"{status_1_nome};TIEBREAK_{status_tiebreak_nome}"

    y_val = {v: float(y[v].X) for v in V}
    f_val = {a: float(f[a].X) for a in A}

    entrada_val = {
        v: sum(f_val[a] for a in arcos_entrada.get(v, []))
        for v in V
    }

    saida_val = {
        v: sum(f_val[a] for a in arcos_saida.get(v, []))
        for v in V
    }

    return {
        "status": status_final_nome,
        "status_lagrangeano": status_1_nome,
        "status_tiebreak": status_tiebreak_nome,
        "tem_solucao": True,
        "subgradiente_valido": subgradiente_valido,
        "L": L_incumbente,
        "L_incumbente_subproblema": L_incumbente,
        "L_bound_certificado": L_bound_certificado,
        "obj_bound": obj_bound,
        "fluxo_total_tiebreak": fluxo_total_tiebreak,
        "runtime": time.monotonic() - t_sub0,
        "y": y_val,
        "f": f_val,
        "entrada": entrada_val,
        "saida": saida_val,
        "num_y_1": int(sum(1 for v in V if y_val[v] > 0.5)),
    }


def calcular_subgradientes(S, T, V, entrada, saida, y, relax_mode):
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}

    g_in = {}
    g_out = {}

    if relax_in:
        for v in V:
            a_v = 1 if v in T_set else 0
            g_in[v] = entrada[v] - a_v - (m - a_v) * y[v]

    if relax_out:
        for v in V:
            b_v = 1 if v in S_set else 0
            g_out[v] = saida[v] - b_v - (m - b_v) * y[v]

    norma2 = sum(valor * valor for valor in g_in.values()) + sum(
        valor * valor for valor in g_out.values()
    )

    norma = math.sqrt(norma2)

    max_g_in = max(g_in.values()) if g_in else ""
    max_g_out = max(g_out.values()) if g_out else ""

    soma_viol_pos = sum(max(0.0, valor) for valor in g_in.values()) + sum(
        max(0.0, valor) for valor in g_out.values()
    )

    return {
        "g_in": g_in,
        "g_out": g_out,
        "norma2": norma2,
        "norma": norma,
        "max_g_in": max_g_in,
        "max_g_out": max_g_out,
        "soma_viol_pos": soma_viol_pos,
    }


def calcular_passo(iteracao, regra, pi_atual, UB, L_referencia, norma2, theta0):
    if norma2 <= 1e-18:
        return 0.0

    if regra == "polyak" and UB is not None and L_referencia is not None and UB > L_referencia:
        return pi_atual * (UB - L_referencia) / norma2

    return theta0 / math.sqrt(max(1, iteracao))


def executar_lagrangeano_instancia(
    nome_instancia,
    S,
    T,
    VI,
    V,
    adj,
    R,
    relax_mode,
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
    usar_tiebreak,
    tiebreak_tol,
    atualizar_com_subproblema_nao_otimo,
):
    t_total0 = time.monotonic()

    A_original = construir_arcos_alcance(V, adj, R)

    S, T, V, A, arcos_entrada, arcos_saida = preparar_estrutura_rede(
        S=S,
        T=T,
        V=V,
        arcos=A_original,
    )

    print(
        f"[{nome_instancia}] modo={relax_mode} "
        f"|V|={len(V)} |A_r|={len(A)} |S|=|T|={len(S)} R={R}"
    )

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
            "O passo Polyak será substituído por passo decrescente."
        )
    else:
        print(f"[{nome_instancia}] UB inicial = {UB}")

    alpha = {v: float(alpha_init) for v in V}
    beta = {v: float(beta_init) for v in V}

    pi_atual = float(pi_inicial)
    melhor_LB_certificado = -float("inf")
    melhor_iter = None
    sem_melhora = 0

    linhas_iter = []

    for k in range(1, max_iters + 1):
        t_iter0 = time.monotonic()

        sub = resolver_subproblema_lagrangeano(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            alpha=alpha,
            beta=beta,
            relax_mode=relax_mode,
            fluxo_inteiro=fluxo_inteiro,
            subproblem_time_limit=subproblem_time_limit,
            threads=threads,
            usar_tiebreak=usar_tiebreak,
            tiebreak_tol=tiebreak_tol,
        )

        L_incumbente = sub["L_incumbente_subproblema"]
        L_bound_certificado = sub["L_bound_certificado"]

        if L_bound_certificado is not None and L_bound_certificado > melhor_LB_certificado + tol_melhoria:
            melhor_LB_certificado = L_bound_certificado
            melhor_iter = k
            sem_melhora = 0
        else:
            sem_melhora += 1

        if sem_melhora >= stall_limit:
            pi_atual = max(pi_min, pi_atual * pi_decay)
            sem_melhora = 0

        if not sub["tem_solucao"]:
            gap_lag = gap_percentual(
                UB,
                None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado,
            )

            linha = {
                "instance": nome_instancia,
                "R": R,
                "relax_mode": relax_mode,
                "iter": k,
                "status_subproblema": sub["status"],
                "status_lagrangeano": sub["status_lagrangeano"],
                "status_tiebreak": sub["status_tiebreak"],
                "subgradiente_valido": sub["subgradiente_valido"],
                "L_incumbente_subproblema": "" if L_incumbente is None else L_incumbente,
                "L_bound_certificado": "" if L_bound_certificado is None else L_bound_certificado,
                "melhor_LB_certificado": "" if melhor_LB_certificado == -float("inf") else melhor_LB_certificado,
                "UB": "" if UB is None else UB,
                "gap_lagrangeano_certificado_pct": "" if gap_lag is None else gap_lag,
                "norma_subgrad": "",
                "theta": "",
                "pi": pi_atual,
                "num_y_1": "",
                "max_g_in": "",
                "max_g_out": "",
                "soma_viol_pos": "",
                "fluxo_total_tiebreak": "",
                "runtime_subproblema_s": sub["runtime"],
                "runtime_iter_s": time.monotonic() - t_iter0,
                "runtime_total_s": time.monotonic() - t_total0,
            }
            linhas_iter.append(linha)
            print(f"[{nome_instancia}] Subproblema sem solução na iteração {k}: {sub['status']}")
            break

        subgrad = calcular_subgradientes(
            S=S,
            T=T,
            V=V,
            entrada=sub["entrada"],
            saida=sub["saida"],
            y=sub["y"],
            relax_mode=relax_mode,
        )

        norma2 = subgrad["norma2"]
        norma = subgrad["norma"]

        L_referencia_passo = L_bound_certificado
        theta = calcular_passo(
            iteracao=k,
            regra=step_rule,
            pi_atual=pi_atual,
            UB=UB,
            L_referencia=L_referencia_passo,
            norma2=norma2,
            theta0=theta0,
        )

        gap_lag = gap_percentual(
            UB,
            None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado,
        )

        linha = {
            "instance": nome_instancia,
            "R": R,
            "relax_mode": relax_mode,
            "iter": k,
            "status_subproblema": sub["status"],
            "status_lagrangeano": sub["status_lagrangeano"],
            "status_tiebreak": sub["status_tiebreak"],
            "subgradiente_valido": sub["subgradiente_valido"],
            "L_incumbente_subproblema": "" if L_incumbente is None else L_incumbente,
            "L_bound_certificado": "" if L_bound_certificado is None else L_bound_certificado,
            "melhor_LB_certificado": melhor_LB_certificado,
            "UB": "" if UB is None else UB,
            "gap_lagrangeano_certificado_pct": "" if gap_lag is None else gap_lag,
            "norma_subgrad": norma,
            "theta": theta,
            "pi": pi_atual,
            "num_y_1": sub["num_y_1"],
            "max_g_in": subgrad["max_g_in"],
            "max_g_out": subgrad["max_g_out"],
            "soma_viol_pos": subgrad["soma_viol_pos"],
            "fluxo_total_tiebreak": "" if sub["fluxo_total_tiebreak"] is None else sub["fluxo_total_tiebreak"],
            "runtime_subproblema_s": sub["runtime"],
            "runtime_iter_s": time.monotonic() - t_iter0,
            "runtime_total_s": time.monotonic() - t_total0,
        }
        linhas_iter.append(linha)

        if k == 1 or k % 10 == 0 or k == max_iters:
            gap_txt = "NA" if gap_lag is None else f"{gap_lag:.2f}%"
            print(
                f"[{nome_instancia}] modo={relax_mode} it={k:04d} "
                f"L_inc={L_incumbente if L_incumbente is not None else 'NA'} "
                f"L_cert={L_bound_certificado if L_bound_certificado is not None else 'NA'} "
                f"bestLB_cert={melhor_LB_certificado if melhor_LB_certificado != -float('inf') else 'NA'} "
                f"UB={UB if UB is not None else 'NA'} gap_cert={gap_txt} "
                f"||g||={norma:.4f} theta={theta:.6g} pi={pi_atual:.4f} "
                f"status={sub['status']}"
            )

        if sub["status_lagrangeano"] != "OPTIMAL":
            print(
                f"[{nome_instancia}] Aviso: subproblema lagrangeano com status "
                f"{sub['status_lagrangeano']}. "
                f"Usando ObjBound={L_bound_certificado} como LB certificado; "
                "subgradiente da incumbente é heurístico."
            )

        if norma <= tol_norma:
            print(f"[{nome_instancia}] Parou por norma do subgradiente <= {tol_norma}.")
            break

        if theta <= 1e-18:
            print(f"[{nome_instancia}] Parou por passo praticamente zero.")
            break

        if sub["subgradiente_valido"] or atualizar_com_subproblema_nao_otimo:
            if relax_mode in {"all", "in"}:
                for v, g in subgrad["g_in"].items():
                    alpha[v] = max(0.0, alpha[v] + theta * g)

            if relax_mode in {"all", "out"}:
                for v, g in subgrad["g_out"].items():
                    beta[v] = max(0.0, beta[v] + theta * g)
        else:
            print(
                f"[{nome_instancia}] Parou porque o subproblema não foi ótimo "
                "e --nao-atualizar-com-subproblema-nao-otimo está ativo."
            )
            break

    runtime_total = time.monotonic() - t_total0

    melhor_LB_saida = "" if melhor_LB_certificado == -float("inf") else melhor_LB_certificado

    resumo = {
        "instance": nome_instancia,
        "R": R,
        "relax_mode": relax_mode,
        "N_nodes": len(V),
        "A_R": len(A),
        "m": len(S),
        "VI": len(VI),
        "max_iters": max_iters,
        "iters_executadas": len(linhas_iter),
        "melhor_LB_certificado": melhor_LB_saida,
        "melhor_iter": "" if melhor_iter is None else melhor_iter,
        "UB": "" if UB is None else UB,
        "gap_lagrangeano_certificado_pct": ""
        if gap_percentual(UB, None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado) is None
        else gap_percentual(UB, melhor_LB_certificado),
        "status_mip_ub": info_ub["status_mip"],
        "LB_mip_ub": "" if info_ub["LB_mip"] is None else info_ub["LB_mip"],
        "runtime_mip_ub_s": info_ub["runtime_mip"],
        "solcount_mip_ub": info_ub["solcount_mip"],
        "runtime_total_s": runtime_total,
        "step_rule": step_rule,
        "pi_inicial": pi_inicial,
        "pi_final": pi_atual,
        "fluxo_inteiro": fluxo_inteiro,
        "tiebreak": usar_tiebreak,
        "atualizar_com_subproblema_nao_otimo": atualizar_com_subproblema_nao_otimo,
    }

    return resumo, linhas_iter


ITER_HEADER = [
    "instance",
    "R",
    "relax_mode",
    "iter",
    "status_subproblema",
    "status_lagrangeano",
    "status_tiebreak",
    "subgradiente_valido",
    "L_incumbente_subproblema",
    "L_bound_certificado",
    "melhor_LB_certificado",
    "UB",
    "gap_lagrangeano_certificado_pct",
    "norma_subgrad",
    "theta",
    "pi",
    "num_y_1",
    "max_g_in",
    "max_g_out",
    "soma_viol_pos",
    "fluxo_total_tiebreak",
    "runtime_subproblema_s",
    "runtime_iter_s",
    "runtime_total_s",
]

RESUMO_HEADER = [
    "instance",
    "R",
    "relax_mode",
    "N_nodes",
    "A_R",
    "m",
    "VI",
    "max_iters",
    "iters_executadas",
    "melhor_LB_certificado",
    "melhor_iter",
    "UB",
    "gap_lagrangeano_certificado_pct",
    "status_mip_ub",
    "LB_mip_ub",
    "runtime_mip_ub_s",
    "solcount_mip_ub",
    "runtime_total_s",
    "step_rule",
    "pi_inicial",
    "pi_final",
    "fluxo_inteiro",
    "tiebreak",
    "atualizar_com_subproblema_nao_otimo",
]


def executar_arquivo(caminho_instancia: Path, args):
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
    print(f"Modo de relaxação: {args.relax_mode}")
    print(f"Tiebreak menor fluxo: {not args.sem_tiebreak}")
    print(
        "Atualizar com subproblema não ótimo: "
        f"{not args.nao_atualizar_com_subproblema_nao_otimo}"
    )
    print("=" * 80)

    resumo, linhas_iter = executar_lagrangeano_instancia(
        nome_instancia=nome,
        S=S,
        T=T,
        VI=VI,
        V=V,
        adj=adj,
        R=R_instancia,
        relax_mode=args.relax_mode,
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
        usar_tiebreak=not args.sem_tiebreak,
        tiebreak_tol=args.tiebreak_tol,
        atualizar_com_subproblema_nao_otimo=not args.nao_atualizar_com_subproblema_nao_otimo,
    )

    return resumo, linhas_iter


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Relaxação lagrangeana para o MIN-STATION original de Das. "
            "Registra separadamente incumbente do subproblema e bound certificado."
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
        "--relax-mode",
        type=str,
        choices=["all", "in", "out"],
        default="all",
        help=(
            "Modo de relaxação: "
            "all relaxa entrada e saída; "
            "in relaxa só entrada; "
            "out relaxa só saída."
        ),
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
        help="UB manual. Recomendo usar quando executar uma única instância.",
    )

    ap.add_argument(
        "--ub-time-limit",
        type=float,
        default=60.0,
        help="Tempo para rodar o modelo original e obter UB. Use 0 para não calcular UB.",
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
        default=0.01,
        help="Parâmetro pi do passo de Polyak. Padrão: 0.01",
    )

    ap.add_argument(
        "--pi-decay",
        type=float,
        default=0.7,
        help="Fator de redução de pi após estagnação. Padrão: 0.7",
    )

    ap.add_argument(
        "--pi-min",
        type=float,
        default=0.001,
        help="Menor valor permitido para pi. Padrão: 0.001",
    )

    ap.add_argument(
        "--stall-limit",
        type=int,
        default=100,
        help="Iterações sem melhora antes de reduzir pi. Padrão: 100",
    )

    ap.add_argument(
        "--theta0",
        type=float,
        default=0.0001,
        help="Passo inicial para regra decrescente. Padrão: 0.0001",
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
        help="Tolerância para considerar melhora no LB certificado. Padrão: 1e-6",
    )

    ap.add_argument(
        "--subproblem-time-limit",
        type=float,
        default=0.0,
        help=(
            "Tempo limite para cada subproblema. "
            "0 significa sem limite. Para bound lagrangeano exato, deixe 0."
        ),
    )

    ap.add_argument(
        "--fluxo-inteiro",
        action="store_true",
        help="Usa f inteiro no subproblema. Por padrão usa fluxo contínuo.",
    )

    ap.add_argument(
        "--threads",
        type=int,
        default=0,
        help="Número de threads do Gurobi. 0 usa padrão do Gurobi.",
    )

    ap.add_argument(
        "--sem-tiebreak",
        action="store_true",
        help="Desativa o desempate por menor fluxo total.",
    )

    ap.add_argument(
        "--tiebreak-tol",
        type=float,
        default=1e-7,
        help="Tolerância para fixar o valor ótimo lagrangeano no desempate. Padrão: 1e-7.",
    )

    ap.add_argument(
        "--nao-atualizar-com-subproblema-nao-otimo",
        action="store_true",
        help=(
            "Se ativo, para a execução quando o subproblema não é ótimo. "
            "Por padrão, continua usando ObjBound como LB certificado e a incumbente "
            "apenas para atualização heurística dos multiplicadores."
        ),
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

    caminho_iter = out_dir / f"lagrangeano_{args.relax_mode}_iteracoes.csv"
    caminho_resumo = out_dir / f"lagrangeano_{args.relax_mode}_resumo.csv"

    print(f"{len(arquivos)} arquivo(s) encontrado(s) em {pasta}")
    print(f"Modo de relaxação: {args.relax_mode}")
    print(f"Tiebreak menor fluxo: {not args.sem_tiebreak}")
    print(
        "Atualizar com subproblema não ótimo: "
        f"{not args.nao_atualizar_com_subproblema_nao_otimo}"
    )
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