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


def nome_status_gurobi(status):
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


def append_csv(linhas, caminho_csv, header):
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    primeira = not caminho_csv.exists()

    with caminho_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)

        if primeira:
            w.writeheader()

        for linha in linhas:
            w.writerow({k: linha.get(k, "") for k in header})


def norma2_vetor(x):
    return sum(valor * valor for valor in x)


def norma_vetor(x):
    return math.sqrt(norma2_vetor(x))


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
        UB = obter_obj_val_seguro(modelo)

    LB_mip = obter_obj_bound_seguro(modelo)

    return {
        "UB": UB,
        "LB_mip": LB_mip,
        "status_mip": nome_status_gurobi(modelo.Status),
        "runtime_mip": runtime,
        "solcount_mip": solcount,
    }



def construir_modelo_relaxacao_linear(S, T, V, A, arcos_entrada, arcos_saida):
    m = len(S)

    modelo = Model("MIN-STATION-LP-ORIGINAL")
    modelo.Params.OutputFlag = 0

    y = {
        v: modelo.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name=f"y[{v}]")
        for v in V
    }

    f = {
        (u, v): modelo.addVar(lb=0.0, ub=m, vtype=GRB.CONTINUOUS, name=f"f[{u},{v}]")
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


def resolver_relaxacao_linear_original(
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    lp_time_limit=0.0,
    threads=None,
    output_lp=False,
    tempo_limite_global=None,
):
    t0 = time.monotonic()

    modelo = construir_modelo_relaxacao_linear(
        S=S,
        T=T,
        V=V,
        A=A,
        arcos_entrada=arcos_entrada,
        arcos_saida=arcos_saida,
    )

    modelo.Params.OutputFlag = 1 if output_lp else 0

    if lp_time_limit is not None and lp_time_limit > 0:
        modelo.Params.TimeLimit = lp_time_limit

    if threads is not None and threads > 0:
        modelo.Params.Threads = threads

    modelo.optimize()

    obj_val = obter_obj_val_seguro(modelo)
    obj_bound = obter_obj_bound_seguro(modelo)
    runtime = time.monotonic() - t0

    return {
        "LB_LP_original": obj_val if modelo.SolCount > 0 else None,
        "bound_LP_original": obj_bound,
        "status_LP_original": nome_status_gurobi(modelo.Status),
        "runtime_LP_original_s": runtime,
        "vars_LP_original": modelo.NumVars,
        "constrs_LP_original": modelo.NumConstrs,
        "solcount_LP_original": modelo.SolCount,
    }


def classificar_bundle_vs_lp(lb_bundle, lb_lp, tol=1e-6):
    if lb_bundle is None or lb_lp is None:
        return "comparacao_indisponivel"

    if lb_bundle > lb_lp + tol:
        return "LR_Bundle_melhor_que_LP_original"

    if lb_lp > lb_bundle + tol:
        return "LR_Bundle_pior_que_LP_original"

    return "LR_Bundle_igual_LP_original"


def coeficientes_lagrangeanos_por_vertice(v, S_set, T_set, m, alpha, beta, relax_mode):
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
    output_subproblema=False,
):
    if relax_mode not in {"all", "in", "out"}:
        raise ValueError(f"relax_mode inválido: {relax_mode}")

    t_sub0 = time.monotonic()

    S_set = set(S)
    T_set = set(T)
    m = len(S)

    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}

    modelo = Model(f"LR-SUBPROBLEM-{relax_mode}")
    modelo.Params.OutputFlag = 1 if output_subproblema else 0

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
            fluxo_total_tiebreak = obter_obj_val_seguro(modelo)
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


class IndexadorMultiplicadores:
    def __init__(self, V, relax_mode):
        self.V = list(V)
        self.relax_mode = relax_mode
        self.chaves = []

        if relax_mode in {"all", "in"}:
            for v in self.V:
                self.chaves.append(("alpha", v))

        if relax_mode in {"all", "out"}:
            for v in self.V:
                self.chaves.append(("beta", v))

        self.n = len(self.chaves)

    def vetor_inicial(self, alpha_init, beta_init):
        x = []
        for tipo, _v in self.chaves:
            if tipo == "alpha":
                x.append(float(alpha_init))
            else:
                x.append(float(beta_init))
        return x

    def vetor_para_dicts(self, x):
        alpha = {v: 0.0 for v in self.V}
        beta = {v: 0.0 for v in self.V}

        for i, (tipo, v) in enumerate(self.chaves):
            if tipo == "alpha":
                alpha[v] = float(x[i])
            else:
                beta[v] = float(x[i])

        return alpha, beta

    def subgradiente_para_vetor(self, subgrad):
        g = []

        for tipo, v in self.chaves:
            if tipo == "alpha":
                g.append(float(subgrad["g_in"].get(v, 0.0)))
            else:
                g.append(float(subgrad["g_out"].get(v, 0.0)))

        return g

    def norma_lambdas(self, x):
        return norma_vetor(x)



def avaliar_oraculo_bundle(
    lambdas,
    indexador,
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    relax_mode,
    fluxo_inteiro,
    subproblem_time_limit,
    threads,
    usar_tiebreak,
    tiebreak_tol,
    output_subproblema,
    permitir_oraculo_inexato,
):
    alpha, beta = indexador.vetor_para_dicts(lambdas)

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
        output_subproblema=output_subproblema,
    )

    q_inc = sub["L_incumbente_subproblema"]
    q_cert = sub["L_bound_certificado"]

    if not sub["tem_solucao"]:
        return {
            "ok_para_corte": False,
            "sub": sub,
            "q_usado": None,
            "phi_usado": None,
            "g_dual": None,
            "h_phi": None,
            "norma_subgrad": None,
            "max_g_in": "",
            "max_g_out": "",
            "soma_viol_pos": "",
            "motivo": "sem_solucao_primal_no_subproblema",
        }

    subgrad = calcular_subgradientes(
        S=S,
        T=T,
        V=V,
        entrada=sub["entrada"],
        saida=sub["saida"],
        y=sub["y"],
        relax_mode=relax_mode,
    )

    g_dual = indexador.subgradiente_para_vetor(subgrad)

    if sub["subgradiente_valido"]:
        q_usado = q_inc
        corte_exato = True
        ok_para_corte = True
    else:
        q_usado = q_inc
        corte_exato = False
        ok_para_corte = bool(permitir_oraculo_inexato and q_inc is not None)

    phi_usado = None if q_usado is None else -q_usado
    h_phi = None if g_dual is None else [-valor for valor in g_dual]

    return {
        "ok_para_corte": ok_para_corte,
        "corte_exato": corte_exato,
        "sub": sub,
        "q_usado": q_usado,
        "phi_usado": phi_usado,
        "q_incumbente": q_inc,
        "q_certificado": q_cert,
        "g_dual": g_dual,
        "h_phi": h_phi,
        "norma_subgrad": subgrad["norma"],
        "max_g_in": subgrad["max_g_in"],
        "max_g_out": subgrad["max_g_out"],
        "soma_viol_pos": subgrad["soma_viol_pos"],
        "motivo": "",
    }



def resolver_mestre_bundle(
    cortes,
    centro,
    mu,
    master_time_limit,
    threads,
    output_master=False,
):
    if not cortes:
        raise ValueError("O mestre bundle precisa de pelo menos um corte.")

    n = len(centro)

    modelo = Model("PROXIMAL-BUNDLE-MASTER")
    modelo.Params.OutputFlag = 1 if output_master else 0

    if master_time_limit is not None and master_time_limit > 0:
        modelo.Params.TimeLimit = master_time_limit

    if threads is not None and threads > 0:
        modelo.Params.Threads = threads

    x = {
        i: modelo.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"lambda[{i}]")
        for i in range(n)
    }

    z = modelo.addVar(lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name="z_modelo")

    for corte in cortes:
        modelo.addConstr(
            z >= corte["phi"]
            + quicksum(
                corte["h"][i] * (x[i] - corte["lambda"][i])
                for i in range(n)
            ),
            name=f"corte[{corte['id']}]",
        )

    termo_prox = 0.5 * mu * quicksum(
        (x[i] - centro[i]) * (x[i] - centro[i])
        for i in range(n)
    )

    modelo.setObjective(z + termo_prox, GRB.MINIMIZE)
    modelo.optimize()

    status = nome_status_gurobi(modelo.Status)
    solcount = int(getattr(modelo, "SolCount", 0))

    if modelo.Status != GRB.OPTIMAL and solcount == 0:
        return {
            "tem_solucao": False,
            "status": status,
            "lambda_trial": None,
            "z_modelo_trial": None,
            "obj_mestre": None,
            "runtime": float(getattr(modelo, "Runtime", 0.0)),
        }

    lambda_trial = [float(x[i].X) for i in range(n)]
    z_modelo_trial = float(z.X)
    obj_mestre = obter_obj_val_seguro(modelo)

    return {
        "tem_solucao": True,
        "status": status,
        "lambda_trial": lambda_trial,
        "z_modelo_trial": z_modelo_trial,
        "obj_mestre": obj_mestre,
        "runtime": float(getattr(modelo, "Runtime", 0.0)),
    }


def podar_cortes(cortes, max_cortes, id_corte_centro):
    if max_cortes is None or max_cortes <= 0:
        return cortes

    if len(cortes) <= max_cortes:
        return cortes

    corte_centro = None
    demais = []

    for corte in cortes:
        if corte["id"] == id_corte_centro:
            corte_centro = corte
        else:
            demais.append(corte)

    # Mantém os cortes mais recentes e protege o corte do centro atual.
    espaco_para_demais = max_cortes - (1 if corte_centro is not None else 0)
    demais = demais[-max(0, espaco_para_demais):]

    if corte_centro is not None:
        return [corte_centro] + demais

    return demais[-max_cortes:]


ITER_HEADER = [
    "instance",
    "R",
    "relax_mode",
    "iter",
    "tipo_passo",
    "status_mestre",
    "status_subproblema",
    "status_lagrangeano",
    "status_tiebreak",
    "corte_exato",
    "q_centro",
    "q_trial_usado",
    "q_trial_incumbente",
    "q_trial_certificado",
    "melhor_LB_certificado",
    "UB",
    "gap_certificado_pct",
    "phi_centro",
    "phi_trial_usado",
    "z_modelo_trial",
    "pred_decrease",
    "actual_decrease",
    "norma_subgrad",
    "norma_passo",
    "mu",
    "num_cortes",
    "num_y_1",
    "max_g_in",
    "max_g_out",
    "soma_viol_pos",
    "fluxo_total_tiebreak",
    "runtime_mestre_s",
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
    "LB_relax_linear_original",
    "status_LP_original",
    "runtime_LP_original_s",
    "vars_LP_original",
    "constrs_LP_original",
    "max_iters",
    "iters_executadas",
    "melhor_LB_certificado",
    "melhor_iter_certificado",
    "q_melhor_centro",
    "UB",
    "gap_certificado_pct",
    "melhoria_Bundle_menos_LP_abs",
    "melhoria_Bundle_menos_LP_pct_sobre_LP",
    "classificacao_Bundle_vs_LP_original",
    "gap_LP_original_pct",
    "reducao_gap_LP_menos_Bundle_pontos_pct",
    "status_mip_ub",
    "LB_mip_ub",
    "runtime_mip_ub_s",
    "solcount_mip_ub",
    "runtime_total_s",
    "mu_final",
    "num_cortes_final",
    "fluxo_inteiro",
    "tiebreak",
    "permitir_oraculo_inexato",
]


def executar_bundle_instancia(
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
    alpha_init,
    beta_init,
    subproblem_time_limit,
    master_time_limit,
    fluxo_inteiro,
    threads,
    usar_tiebreak,
    tiebreak_tol,
    mu_inicial,
    mu_min,
    mu_max,
    mu_serious_factor,
    mu_null_factor,
    serious_fraction,
    tol_pred,
    tol_passo,
    max_cortes,
    permitir_oraculo_inexato,
    output_subproblema,
    output_master,
    comparar_lp_original=True,
    lp_time_limit=0.0,
    output_lp=False,
    tempo_limite_global=None,
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

    info_lp = {
        "LB_LP_original": None,
        "bound_LP_original": None,
        "status_LP_original": "NAO_EXECUTADO",
        "runtime_LP_original_s": 0.0,
        "vars_LP_original": "",
        "constrs_LP_original": "",
        "solcount_LP_original": 0,
    }

    if comparar_lp_original:
        print(f"[{nome_instancia}] Resolvendo relaxação linear da formulação original/agregada...")
        info_lp = resolver_relaxacao_linear_original(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            lp_time_limit=lp_time_limit,
            threads=threads,
            output_lp=output_lp,
        )
        print(
            f"[{nome_instancia}] LP-original status={info_lp['status_LP_original']} "
            f"LB_LP={info_lp['LB_LP_original']} "
            f"runtime={info_lp['runtime_LP_original_s']:.3f}s "
            f"vars={info_lp['vars_LP_original']} constrs={info_lp['constrs_LP_original']}"
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
        print(f"[{nome_instancia}] Aviso: nenhum UB disponível para cálculo de gap.")
    else:
        print(f"[{nome_instancia}] UB inicial = {UB}")

    indexador = IndexadorMultiplicadores(V=V, relax_mode=relax_mode)

    if indexador.n == 0:
        raise ValueError(f"Sem multiplicadores para relax_mode={relax_mode}")

    centro = indexador.vetor_inicial(alpha_init=alpha_init, beta_init=beta_init)

    cortes = []
    proximo_id_corte = 1

    melhor_LB_certificado = -float("inf")
    melhor_iter_certificado = None

    mu = float(mu_inicial)

    # Avaliação inicial no centro.
    avaliacao_centro = avaliar_oraculo_bundle(
        lambdas=centro,
        indexador=indexador,
        S=S,
        T=T,
        V=V,
        A=A,
        arcos_entrada=arcos_entrada,
        arcos_saida=arcos_saida,
        relax_mode=relax_mode,
        fluxo_inteiro=fluxo_inteiro,
        subproblem_time_limit=subproblem_time_limit,
        threads=threads,
        usar_tiebreak=usar_tiebreak,
        tiebreak_tol=tiebreak_tol,
        output_subproblema=output_subproblema,
        permitir_oraculo_inexato=permitir_oraculo_inexato,
    )

    if avaliacao_centro["q_certificado"] is not None:
        melhor_LB_certificado = avaliacao_centro["q_certificado"]
        melhor_iter_certificado = 0

    if not avaliacao_centro["ok_para_corte"]:
        print(
            f"[{nome_instancia}] Não foi possível criar corte inicial. "
            f"Status={avaliacao_centro['sub']['status']}; "
            f"q_cert={avaliacao_centro['q_certificado']}."
        )
        return {
            "instance": nome_instancia,
            "R": R,
            "relax_mode": relax_mode,
            "N_nodes": len(V),
            "A_R": len(A),
            "m": len(S),
            "VI": len(VI),
            "LB_relax_linear_original": "" if info_lp["LB_LP_original"] is None else info_lp["LB_LP_original"],
            "status_LP_original": info_lp["status_LP_original"],
            "runtime_LP_original_s": info_lp["runtime_LP_original_s"],
            "vars_LP_original": info_lp["vars_LP_original"],
            "constrs_LP_original": info_lp["constrs_LP_original"],
            "max_iters": max_iters,
            "iters_executadas": 0,
            "melhor_LB_certificado": ""
            if melhor_LB_certificado == -float("inf")
            else melhor_LB_certificado,
            "melhor_iter_certificado": ""
            if melhor_iter_certificado is None
            else melhor_iter_certificado,
            "q_melhor_centro": "",
            "UB": "" if UB is None else UB,
            "gap_certificado_pct": "",
            "melhoria_Bundle_menos_LP_abs": "",
            "melhoria_Bundle_menos_LP_pct_sobre_LP": "",
            "classificacao_Bundle_vs_LP_original": classificar_bundle_vs_lp(None, info_lp["LB_LP_original"]),
            "gap_LP_original_pct": "",
            "reducao_gap_LP_menos_Bundle_pontos_pct": "",
            "status_mip_ub": info_ub["status_mip"],
            "LB_mip_ub": "" if info_ub["LB_mip"] is None else info_ub["LB_mip"],
            "runtime_mip_ub_s": info_ub["runtime_mip"],
            "solcount_mip_ub": info_ub["solcount_mip"],
            "runtime_total_s": time.monotonic() - t_total0,
            "mu_final": mu,
            "num_cortes_final": len(cortes),
            "fluxo_inteiro": fluxo_inteiro,
            "tiebreak": usar_tiebreak,
            "permitir_oraculo_inexato": permitir_oraculo_inexato,
        }, []

    phi_centro = avaliacao_centro["phi_usado"]
    q_centro = avaliacao_centro["q_usado"]

    corte_centro = {
        "id": proximo_id_corte,
        "lambda": list(centro),
        "phi": avaliacao_centro["phi_usado"],
        "h": avaliacao_centro["h_phi"],
        "exato": avaliacao_centro["corte_exato"],
    }
    proximo_id_corte += 1
    cortes.append(corte_centro)
    id_corte_centro = corte_centro["id"]

    linhas_iter = []

    for k in range(1, max_iters + 1):
        t_iter0 = time.monotonic()

        if tempo_limite_global is not None and tempo_limite_global > 0:
            if time.monotonic() - t_total0 >= tempo_limite_global:
                print(f"[{nome_instancia}] Tempo limite global atingido antes da iteração {k}.")
                break

        mestre = resolver_mestre_bundle(
            cortes=cortes,
            centro=centro,
            mu=mu,
            master_time_limit=master_time_limit,
            threads=threads,
            output_master=output_master,
        )

        if not mestre["tem_solucao"]:
            print(f"[{nome_instancia}] Mestre bundle sem solução na iteração {k}: {mestre['status']}")
            break

        trial = mestre["lambda_trial"]

        pred_decrease = phi_centro - mestre["z_modelo_trial"]
        if pred_decrease < 0 and pred_decrease > -1e-8:
            pred_decrease = 0.0

        passo = [trial[i] - centro[i] for i in range(indexador.n)]
        norma_passo = norma_vetor(passo)

        avaliacao_trial = avaliar_oraculo_bundle(
            lambdas=trial,
            indexador=indexador,
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            relax_mode=relax_mode,
            fluxo_inteiro=fluxo_inteiro,
            subproblem_time_limit=subproblem_time_limit,
            threads=threads,
            usar_tiebreak=usar_tiebreak,
            tiebreak_tol=tiebreak_tol,
            output_subproblema=output_subproblema,
            permitir_oraculo_inexato=permitir_oraculo_inexato,
        )

        sub = avaliacao_trial["sub"]

        q_trial_cert = avaliacao_trial["q_certificado"]
        if q_trial_cert is not None and q_trial_cert > melhor_LB_certificado:
            melhor_LB_certificado = q_trial_cert
            melhor_iter_certificado = k

        if not avaliacao_trial["ok_para_corte"]:
            gap_cert = gap_percentual(
                UB,
                None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado,
            )

            linha = {
                "instance": nome_instancia,
                "R": R,
                "relax_mode": relax_mode,
                "iter": k,
                "tipo_passo": "sem_corte",
                "status_mestre": mestre["status"],
                "status_subproblema": sub["status"],
                "status_lagrangeano": sub["status_lagrangeano"],
                "status_tiebreak": sub["status_tiebreak"],
                "corte_exato": False,
                "q_centro": q_centro,
                "q_trial_usado": "",
                "q_trial_incumbente": ""
                if avaliacao_trial.get("q_incumbente") is None
                else avaliacao_trial.get("q_incumbente"),
                "q_trial_certificado": ""
                if q_trial_cert is None
                else q_trial_cert,
                "melhor_LB_certificado": ""
                if melhor_LB_certificado == -float("inf")
                else melhor_LB_certificado,
                "UB": "" if UB is None else UB,
                "gap_certificado_pct": "" if gap_cert is None else gap_cert,
                "phi_centro": phi_centro,
                "phi_trial_usado": "",
                "z_modelo_trial": mestre["z_modelo_trial"],
                "pred_decrease": pred_decrease,
                "actual_decrease": "",
                "norma_subgrad": "",
                "norma_passo": norma_passo,
                "mu": mu,
                "num_cortes": len(cortes),
                "num_y_1": "",
                "max_g_in": "",
                "max_g_out": "",
                "soma_viol_pos": "",
                "fluxo_total_tiebreak": "",
                "runtime_mestre_s": mestre["runtime"],
                "runtime_subproblema_s": sub["runtime"],
                "runtime_iter_s": time.monotonic() - t_iter0,
                "runtime_total_s": time.monotonic() - t_total0,
            }
            linhas_iter.append(linha)

            print(
                f"[{nome_instancia}] it={k:04d} sem corte válido. "
                f"status_sub={sub['status']}; q_cert={q_trial_cert}."
            )
            break

        phi_trial = avaliacao_trial["phi_usado"]
        q_trial = avaliacao_trial["q_usado"]

        actual_decrease = phi_centro - phi_trial

        serious = False
        if pred_decrease <= tol_pred:
            tipo_passo = "parada_pred"
        elif norma_passo <= tol_passo:
            tipo_passo = "parada_passo"
        elif phi_trial <= phi_centro - serious_fraction * pred_decrease:
            serious = True
            tipo_passo = "serious"
        else:
            tipo_passo = "null"

        novo_corte = {
            "id": proximo_id_corte,
            "lambda": list(trial),
            "phi": phi_trial,
            "h": avaliacao_trial["h_phi"],
            "exato": avaliacao_trial["corte_exato"],
        }
        proximo_id_corte += 1
        cortes.append(novo_corte)

        if serious:
            centro = list(trial)
            phi_centro = phi_trial
            q_centro = q_trial
            id_corte_centro = novo_corte["id"]
            mu = max(mu_min, mu * mu_serious_factor)
        else:
            mu = min(mu_max, mu * mu_null_factor)

        cortes = podar_cortes(
            cortes=cortes,
            max_cortes=max_cortes,
            id_corte_centro=id_corte_centro,
        )

        gap_cert = gap_percentual(
            UB,
            None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado,
        )

        linha = {
            "instance": nome_instancia,
            "R": R,
            "relax_mode": relax_mode,
            "iter": k,
            "tipo_passo": tipo_passo,
            "status_mestre": mestre["status"],
            "status_subproblema": sub["status"],
            "status_lagrangeano": sub["status_lagrangeano"],
            "status_tiebreak": sub["status_tiebreak"],
            "corte_exato": avaliacao_trial["corte_exato"],
            "q_centro": q_centro,
            "q_trial_usado": q_trial,
            "q_trial_incumbente": ""
            if avaliacao_trial.get("q_incumbente") is None
            else avaliacao_trial.get("q_incumbente"),
            "q_trial_certificado": ""
            if q_trial_cert is None
            else q_trial_cert,
            "melhor_LB_certificado": ""
            if melhor_LB_certificado == -float("inf")
            else melhor_LB_certificado,
            "UB": "" if UB is None else UB,
            "gap_certificado_pct": "" if gap_cert is None else gap_cert,
            "phi_centro": phi_centro,
            "phi_trial_usado": phi_trial,
            "z_modelo_trial": mestre["z_modelo_trial"],
            "pred_decrease": pred_decrease,
            "actual_decrease": actual_decrease,
            "norma_subgrad": avaliacao_trial["norma_subgrad"],
            "norma_passo": norma_passo,
            "mu": mu,
            "num_cortes": len(cortes),
            "num_y_1": sub["num_y_1"],
            "max_g_in": avaliacao_trial["max_g_in"],
            "max_g_out": avaliacao_trial["max_g_out"],
            "soma_viol_pos": avaliacao_trial["soma_viol_pos"],
            "fluxo_total_tiebreak": ""
            if sub["fluxo_total_tiebreak"] is None
            else sub["fluxo_total_tiebreak"],
            "runtime_mestre_s": mestre["runtime"],
            "runtime_subproblema_s": sub["runtime"],
            "runtime_iter_s": time.monotonic() - t_iter0,
            "runtime_total_s": time.monotonic() - t_total0,
        }
        linhas_iter.append(linha)

        if k == 1 or k % 10 == 0 or k == max_iters or tipo_passo.startswith("parada"):
            gap_txt = "NA" if gap_cert is None else f"{gap_cert:.2f}%"
            print(
                f"[{nome_instancia}] it={k:04d} {tipo_passo} "
                f"q_trial={q_trial:.6g} q_cert={q_trial_cert if q_trial_cert is not None else 'NA'} "
                f"bestLB_cert={melhor_LB_certificado if melhor_LB_certificado != -float('inf') else 'NA'} "
                f"UB={UB if UB is not None else 'NA'} gap_cert={gap_txt} "
                f"pred={pred_decrease:.6g} act={actual_decrease:.6g} "
                f"||step||={norma_passo:.6g} mu={mu:.6g} "
                f"status_sub={sub['status']}"
            )

        if sub["status_lagrangeano"] != "OPTIMAL":
            print(
                f"[{nome_instancia}] Aviso: subproblema com status {sub['status_lagrangeano']}. "
                f"q_cert={q_trial_cert}. "
                "Corte/subgradiente só é exato se status_lagrangeano=OPTIMAL."
            )

        if tipo_passo in {"parada_pred", "parada_passo"}:
            break

    runtime_total = time.monotonic() - t_total0

    lb_bundle_num = None if melhor_LB_certificado == -float("inf") else melhor_LB_certificado
    lb_lp_num = info_lp["LB_LP_original"]

    melhor_LB_saida = "" if lb_bundle_num is None else lb_bundle_num
    gap_saida = gap_percentual(UB, lb_bundle_num)
    gap_lp = gap_percentual(UB, lb_lp_num)

    if lb_bundle_num is not None and lb_lp_num is not None:
        melhoria_abs = lb_bundle_num - lb_lp_num
        melhoria_pct = "" if abs(lb_lp_num) <= 1e-12 else 100.0 * melhoria_abs / abs(lb_lp_num)
    else:
        melhoria_abs = ""
        melhoria_pct = ""

    if gap_lp is not None and gap_saida is not None:
        reducao_gap = gap_lp - gap_saida
    else:
        reducao_gap = ""

    classificacao = classificar_bundle_vs_lp(lb_bundle_num, lb_lp_num)

    resumo = {
        "instance": nome_instancia,
        "R": R,
        "relax_mode": relax_mode,
        "N_nodes": len(V),
        "A_R": len(A),
        "m": len(S),
        "VI": len(VI),
        "LB_relax_linear_original": "" if lb_lp_num is None else lb_lp_num,
        "status_LP_original": info_lp["status_LP_original"],
        "runtime_LP_original_s": info_lp["runtime_LP_original_s"],
        "vars_LP_original": info_lp["vars_LP_original"],
        "constrs_LP_original": info_lp["constrs_LP_original"],
        "max_iters": max_iters,
        "iters_executadas": len(linhas_iter),
        "melhor_LB_certificado": melhor_LB_saida,
        "melhor_iter_certificado": ""
        if melhor_iter_certificado is None
        else melhor_iter_certificado,
        "q_melhor_centro": q_centro,
        "UB": "" if UB is None else UB,
        "gap_certificado_pct": "" if gap_saida is None else gap_saida,
        "melhoria_Bundle_menos_LP_abs": melhoria_abs,
        "melhoria_Bundle_menos_LP_pct_sobre_LP": melhoria_pct,
        "classificacao_Bundle_vs_LP_original": classificacao,
        "gap_LP_original_pct": "" if gap_lp is None else gap_lp,
        "reducao_gap_LP_menos_Bundle_pontos_pct": reducao_gap,
        "status_mip_ub": info_ub["status_mip"],
        "LB_mip_ub": "" if info_ub["LB_mip"] is None else info_ub["LB_mip"],
        "runtime_mip_ub_s": info_ub["runtime_mip"],
        "solcount_mip_ub": info_ub["solcount_mip"],
        "runtime_total_s": runtime_total,
        "mu_final": mu,
        "num_cortes_final": len(cortes),
        "fluxo_inteiro": fluxo_inteiro,
        "tiebreak": usar_tiebreak,
        "permitir_oraculo_inexato": permitir_oraculo_inexato,
    }

    return resumo, linhas_iter



def executar_arquivo(caminho_instancia, args):
    nome = caminho_instancia.name

    try:
        dados = ler_instancia(str(caminho_instancia))
    except Exception as exc:
        print(f"[{nome}] ERRO no parsing: {exc}")
        return None, []

    S = dados["S"]
    T = dados["T"]
    VI = dados.get("VI", [])
    V = dados.get("V")
    E_w = dados["E"]
    R0 = dados["R"]

    if V is None:
        vertices = set(S) | set(T) | set(VI)
        for e in E_w:
            if isinstance(e, dict):
                u = e.get("u", e.get("origem", e.get("from")))
                v = e.get("v", e.get("destino", e.get("to")))
            else:
                u = e[0]
                v = e[1]
            vertices.add(u)
            vertices.add(v)
        V = list(vertices)

    adj = construir_adjacencia(E_w)
    R_instancia = int(float(R0))

    print("\n" + "=" * 80)
    print(f"Arquivo: {nome}")
    print(f"R original: {R_instancia}")
    print("Relaxação: original/agregada, sem caminhos")
    print(f"Modo de relaxação: {args.relax_mode}")
    print("Método dual: proximal bundle")
    print("Comparação LP original x LR-Bundle: True")
    print("Tiebreak menor fluxo: True")
    print("Permitir oracle inexato: False")
    print("Fluxo inteiro no oracle: False")
    print(f"UB inicial: {args.ub if args.ub is not None else 'NA'}")
    print(f"mu inicial: {args.mu}")
    print(f"max_cortes: {args.max_cortes}")
    print("=" * 80)

    resumo, linhas_iter = executar_bundle_instancia(
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
        ub_time_limit=None,
        alpha_init=args.alpha_init,
        beta_init=args.beta_init,
        subproblem_time_limit=None,
        master_time_limit=None,
        fluxo_inteiro=False,
        threads=None,
        usar_tiebreak=True,
        tiebreak_tol=1e-7,
        mu_inicial=args.mu,
        mu_min=1e-6,
        mu_max=1e6,
        mu_serious_factor=0.7,
        mu_null_factor=2.0,
        serious_fraction=0.1,
        tol_pred=args.tol_pred,
        tol_passo=args.tol_passo,
        max_cortes=args.max_cortes,
        permitir_oraculo_inexato=False,
        output_subproblema=False,
        output_master=False,
        comparar_lp_original=True,
        lp_time_limit=None,
        output_lp=False,
        tempo_limite_global=args.tempo_limite_global,
    )

    return resumo, linhas_iter


def main():
    args = argparse.Namespace(
        inputs_dir="./inputs",
        out_dir="results_original_bundle_static",

        relax_mode="all",

        max_iters=500,
        tempo_limite_global=3600.0,

        # Upper bound usado no cálculo do gap e na avaliação do desempenho.
        ub=42.0,

        # Multiplicadores lagrangeanos iniciais.
        alpha_init=0.0,
        beta_init=0.0,

        # Peso proximal inicial do bundle.
        # O mestre resolve: min z + (mu/2)*||lambda - centro||².
        mu=1.0,

        # Número máximo de cortes mantidos no mestre bundle.
        max_cortes=200,

        # Tolerâncias de parada do bundle.
        tol_pred=1e-5,
        tol_passo=1e-7,
    )

    pasta = Path(args.inputs_dir)
    arquivos = sorted(p for p in pasta.glob("*.txt") if p.is_file())

    if not arquivos:
        print(f"Nenhum .txt encontrado em {pasta}.")
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    caminho_iter = out_dir / f"original_{args.relax_mode}_bundle_iteracoes.csv"
    caminho_resumo = out_dir / f"original_{args.relax_mode}_bundle_resumo.csv"

    for caminho_csv in (caminho_iter, caminho_resumo):
        if caminho_csv.exists():
            caminho_csv.unlink()

    print(f"{len(arquivos)} arquivo(s) encontrado(s) em {pasta}")
    print("Relaxação: original/agregada, sem caminhos")
    print(f"Modo de relaxação: {args.relax_mode}")
    print("Método dual: proximal bundle")
    print("Parâmetros: definidos estaticamente no script")
    print("Comparação LP original x LR-Bundle: True")
    print("Tiebreak menor fluxo: True")
    print("Permitir oracle inexato: False")
    print(
        f"UB={args.ub} max_iters={args.max_iters} "
        f"tempo_limite_global={args.tempo_limite_global}"
    )
    print(f"mu={args.mu} max_cortes={args.max_cortes}")
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