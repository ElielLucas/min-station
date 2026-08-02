import argparse
import ast
import csv
import heapq
import json
import math
import re
import time
from pathlib import Path
from ms_utils import ler_instancia as _ler_instancia_ms
from ms_utils import construir_arcos_alcance as _construir_arcos_ms
from ms_utils import construir_adjacencia as _construir_adjacencia_ms
from gurobipy import GRB, Model, quicksum


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


def valor_objetivo_seguro(modelo):
    try:
        valor = float(modelo.ObjVal)
        if math.isfinite(valor):
            return valor
    except Exception:
        return None
    return None


def bound_objetivo_seguro(modelo):
    try:
        valor = float(modelo.ObjBound)
        if math.isfinite(valor):
            return valor
    except Exception:
        return None
    return None


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
        writer = csv.DictWriter(f, fieldnames=header)
        if primeira:
            writer.writeheader()
        for linha in linhas:
            writer.writerow({campo: linha.get(campo, "") for campo in header})


def remover_arquivo_se_existir(caminho):
    if caminho.exists():
        caminho.unlink()


def norma2_valores(valores):
    return sum((float(x) * float(x) for x in valores))


def _normalizar_lista_valores(valor):
    if valor is None:
        return []
    if isinstance(valor, set):
        return list(valor)
    if isinstance(valor, tuple):
        return list(valor)
    if isinstance(valor, list):
        return valor
    return [valor]


def _parse_valor_textual(texto):
    texto = texto.strip().rstrip(";")
    try:
        return ast.literal_eval(texto)
    except Exception:
        pass
    partes = re.split("[\\s,]+", texto.strip())
    partes = [p for p in partes if p]
    valores = []
    for p in partes:
        try:
            if "." in p:
                valores.append(float(p))
            else:
                valores.append(int(p))
        except ValueError:
            valores.append(p)
    return valores


def _ler_instancia_json_ou_txt(caminho):
    path = Path(caminho)
    texto = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not texto:
        raise ValueError(f"Arquivo vazio: {caminho}")
    if texto[0] in "[{":
        dados = json.loads(texto)
        if isinstance(dados, list):
            raise ValueError(
                "O arquivo JSON contém uma lista. Esperado um objeto com chaves S, T, VI, V, E, R."
            )
        return dados
    dados = {}
    padrao = re.compile("^\\s*([A-Za-z_][A-Za-z0-9_]*)\\s*[:=]\\s*(.*?)\\s*$")
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = padrao.match(linha)
        if not m:
            continue
        chave = m.group(1).strip()
        valor_txt = m.group(2).strip()
        dados[chave] = _parse_valor_textual(valor_txt)
    aliases = {
        "sources": "S",
        "origens": "S",
        "destinations": "T",
        "destinos": "T",
        "vertices_intermediarios": "VI",
        "vertices": "V",
        "edges": "E",
        "arestas": "E",
        "range": "R",
        "r": "R",
    }
    for antigo, novo in aliases.items():
        if antigo in dados and novo not in dados:
            dados[novo] = dados[antigo]
    obrigatorias = {"S", "T", "E", "R"}
    faltantes = obrigatorias - set(dados)
    if faltantes:
        raise ValueError(
            f"Não consegui identificar as chaves obrigatórias {sorted(faltantes)} em {caminho}. Use ms_utils.py no mesmo diretório ou informe arquivo com S, T, E, R."
        )
    if "V" not in dados:
        vertices = set(_normalizar_lista_valores(dados.get("S"))) | set(
            _normalizar_lista_valores(dados.get("T"))
        )
        for e in _normalizar_lista_valores(dados["E"]):
            if len(e) >= 2:
                vertices.add(e[0])
                vertices.add(e[1])
        dados["V"] = list(vertices)
    if "VI" not in dados:
        S_set = set(_normalizar_lista_valores(dados["S"]))
        T_set = set(_normalizar_lista_valores(dados["T"]))
        dados["VI"] = [
            v
            for v in _normalizar_lista_valores(dados["V"])
            if v not in S_set and v not in T_set
        ]
    return dados


def ler_instancia(caminho):
    try:
        return _ler_instancia_ms(caminho)
    except Exception:
        return _ler_instancia_json_ou_txt(caminho)


def construir_adjacencia(E_w):
    try:
        return _construir_adjacencia_ms(E_w)
    except Exception:
        pass
    adj = {}
    for e in E_w:
        if isinstance(e, dict):
            u = e.get("u", e.get("origem", e.get("from")))
            v = e.get("v", e.get("destino", e.get("to")))
            w = e.get("w", e.get("peso", e.get("weight", 1.0)))
        else:
            if len(e) < 2:
                continue
            u = e[0]
            v = e[1]
            w = e[2] if len(e) >= 3 else 1.0
        adj.setdefault(u, []).append((v, float(w)))
        adj.setdefault(v, [])
    return adj


def construir_arcos_alcance(V, adj, R):
    try:
        return _construir_arcos_ms(V, adj, R)
    except Exception:
        pass
    V_lista = list(V)
    R_float = float(R)
    arcos = []
    for origem in V_lista:
        dist = {v: float("inf") for v in V_lista}
        dist[origem] = 0.0
        heap = [(0.0, str(origem), origem)]
        while heap:
            d_atual, _ordem, u = heapq.heappop(heap)
            if d_atual > dist[u] + 1e-12:
                continue
            if d_atual > R_float + 1e-12:
                continue
            for v, peso in adj.get(u, []):
                nd = d_atual + float(peso)
                if nd + 1e-12 < dist.get(v, float("inf")) and nd <= R_float + 1e-12:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, str(v), v))
        for destino, d in dist.items():
            if destino != origem and math.isfinite(d) and (d <= R_float + 1e-12):
                arcos.append((origem, destino))
    return arcos


def preparar_estrutura_rede(S, T, V, arcos):
    S_lista = list(S)
    T_lista = list(T)
    V_lista = list(V)
    S_set = set(S_lista)
    T_set = set(T_lista)
    V_set = set(V_lista)
    if len(S_lista) != len(T_lista):
        raise ValueError(
            f"MIN-STATION exige |S| = |T|. Recebido |S|={len(S_lista)} e |T|={len(T_lista)}."
        )
    faltando_s = S_set - V_set
    faltando_t = T_set - V_set
    if faltando_s:
        raise ValueError(f"Há origens fora de V: {sorted(map(str, faltando_s))}")
    if faltando_t:
        raise ValueError(f"Há destinos fora de V: {sorted(map(str, faltando_t))}")
    vistos = set()
    A = []
    for u, v in arcos:
        if u == v:
            continue
        if u not in V_set or v not in V_set:
            continue
        if (u, v) in vistos:
            continue
        vistos.add((u, v))
        A.append((u, v))
    arcos_entrada = {v: [] for v in V_lista}
    arcos_saida = {v: [] for v in V_lista}
    for u, v in A:
        arcos_saida.setdefault(u, []).append((u, v))
        arcos_entrada.setdefault(v, []).append((u, v))
        arcos_entrada.setdefault(u, arcos_entrada.get(u, []))
        arcos_saida.setdefault(v, arcos_saida.get(v, []))
    return (S_lista, T_lista, V_lista, A, arcos_entrada, arcos_saida)


def adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida):
    S_set = set(S)
    T_set = set(T)
    for s in S:
        modelo.addConstr(saida[s] - entrada[s] == 1, name=f"balanco_origem[{s}]")
    for t in T:
        modelo.addConstr(entrada[t] - saida[t] == 1, name=f"balanco_destino[{t}]")
    for v in V:
        if v not in S_set and v not in T_set:
            modelo.addConstr(entrada[v] == saida[v], name=f"fluxo_cons[{v}]")


def adicionar_ativacao_entrada(modelo, S, T, V, entrada, y):
    T_set = set(T)
    m = len(S)
    for v in V:
        a_v = 1 if v in T_set else 0
        modelo.addConstr(
            entrada[v] <= a_v + (m - a_v) * y[v], name=f"ativa_entrada[{v}]"
        )


def adicionar_ativacao_saida(modelo, S, T, V, saida, y):
    S_set = set(S)
    m = len(S)
    for v in V:
        b_v = 1 if v in S_set else 0
        modelo.addConstr(saida[v] <= b_v + (m - b_v) * y[v], name=f"ativa_saida[{v}]")


def coeficientes_lagrangeanos_por_vertice(
    v, S_set, T_set, m, lambda_in, lambda_out, relax_mode
):
    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}
    a_v = 1 if v in T_set else 0
    b_v = 1 if v in S_set else 0
    coef_y = 1.0
    constante = 0.0
    if relax_in:
        lam = lambda_in[v]
        coef_y -= (m - a_v) * lam
        constante -= a_v * lam
    if relax_out:
        lam = lambda_out[v]
        coef_y -= (m - b_v) * lam
        constante -= b_v * lam
    return (coef_y, constante)


def construir_modelo_original_para_ub(
    S, T, V, A, arcos_entrada, arcos_saida, fluxo_inteiro=True
):
    m = len(S)
    modelo = Model("MIN-STATION-ORIGINAL-UB")
    modelo.Params.OutputFlag = 0
    y = {v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]") for v in V}
    tipo_f = GRB.INTEGER if fluxo_inteiro else GRB.CONTINUOUS
    f = {
        (u, v): modelo.addVar(lb=0.0, ub=m, vtype=tipo_f, name=f"f[{u},{v}]")
        for u, v in A
    }
    entrada = {v: quicksum((f[a] for a in arcos_entrada.get(v, []))) for v in V}
    saida = {v: quicksum((f[a] for a in arcos_saida.get(v, []))) for v in V}
    modelo.setObjective(quicksum((y[v] for v in V)), GRB.MINIMIZE)
    adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida)
    adicionar_ativacao_entrada(modelo, S, T, V, entrada, y)
    adicionar_ativacao_saida(modelo, S, T, V, saida, y)
    modelo.update()
    return modelo


def obter_ub_modelo_original(
    S, T, V, A, arcos_entrada, arcos_saida, tempo_limite_s, threads, fluxo_inteiro
):
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
        fluxo_inteiro=fluxo_inteiro,
    )
    modelo.Params.TimeLimit = tempo_limite_s
    if threads is not None and threads > 0:
        modelo.Params.Threads = threads
    t0 = time.monotonic()
    modelo.optimize()
    runtime = time.monotonic() - t0
    solcount = int(getattr(modelo, "SolCount", 0))
    return {
        "UB": valor_objetivo_seguro(modelo) if solcount > 0 else None,
        "LB_mip": bound_objetivo_seguro(modelo),
        "status_mip": nome_status_gurobi(modelo.Status),
        "runtime_mip": runtime,
        "solcount_mip": solcount,
    }


def construir_modelo_relaxacao_linear(S, T, V, A, arcos_entrada, arcos_saida):
    m = len(S)
    modelo = Model("MIN-STATION-ORIGINAL-LP-RELAXATION")
    modelo.Params.OutputFlag = 0
    y = {
        v: modelo.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name=f"y_lp[{v}]")
        for v in V
    }
    f = {
        (u, v): modelo.addVar(lb=0.0, ub=m, vtype=GRB.CONTINUOUS, name=f"f_lp[{u},{v}]")
        for u, v in A
    }
    entrada = {v: quicksum((f[a] for a in arcos_entrada.get(v, []))) for v in V}
    saida = {v: quicksum((f[a] for a in arcos_saida.get(v, []))) for v in V}
    modelo.setObjective(quicksum((y[v] for v in V)), GRB.MINIMIZE)
    adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida)
    adicionar_ativacao_entrada(modelo, S, T, V, entrada, y)
    adicionar_ativacao_saida(modelo, S, T, V, saida, y)
    modelo.update()
    return modelo


def resolver_relaxacao_linear(
    S, T, V, A, arcos_entrada, arcos_saida, tempo_limite_s, threads
):
    modelo = construir_modelo_relaxacao_linear(
        S=S, T=T, V=V, A=A, arcos_entrada=arcos_entrada, arcos_saida=arcos_saida
    )
    if tempo_limite_s is not None and tempo_limite_s > 0:
        modelo.Params.TimeLimit = tempo_limite_s
    if threads is not None and threads > 0:
        modelo.Params.Threads = threads
    t0 = time.monotonic()
    modelo.optimize()
    runtime = time.monotonic() - t0
    status_nome = nome_status_gurobi(modelo.Status)
    lb_linear = valor_objetivo_seguro(modelo)
    obj_bound = bound_objetivo_seguro(modelo)
    return {
        "LB_relax_linear": lb_linear,
        "LB_relax_linear_bound": obj_bound,
        "status_relax_linear": status_nome,
        "runtime_relax_linear_s": runtime,
    }


def _float_ou_none(valor):
    if valor in (None, ""):
        return None
    try:
        valor_float = float(valor)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(valor_float):
        return None
    return valor_float


def enriquecer_resumo_com_comparacao_lp(resumo, info_lp):
    lb_lp = _float_ou_none(info_lp.get("LB_relax_linear"))
    lb_lr = _float_ou_none(resumo.get("melhor_LB_certificado"))
    ub = _float_ou_none(resumo.get("UB_final"))
    melhoria_abs = None
    melhoria_pct = None
    classificacao = "NA"
    if lb_lp is not None and lb_lr is not None:
        melhoria_abs = lb_lr - lb_lp
        denom = max(1.0, abs(lb_lp))
        melhoria_pct = 100.0 * melhoria_abs / denom
        if melhoria_abs > 1e-07:
            classificacao = "LR_melhor_que_LP"
        elif melhoria_abs < -1e-07:
            classificacao = "LR_pior_que_LP"
        else:
            classificacao = "LR_igual_LP"
    gap_lp = gap_percentual(ub, lb_lp)
    gap_lr = gap_percentual(ub, lb_lr)
    reducao_gap = None
    if gap_lp is not None and gap_lr is not None:
        reducao_gap = gap_lp - gap_lr
    resumo.update(
        {
            "LB_relax_linear": "" if lb_lp is None else lb_lp,
            "LB_relax_linear_bound": ""
            if info_lp.get("LB_relax_linear_bound") is None
            else info_lp.get("LB_relax_linear_bound"),
            "status_relax_linear": info_lp.get("status_relax_linear", ""),
            "runtime_relax_linear_s": info_lp.get("runtime_relax_linear_s", ""),
            "melhoria_LR_menos_LP_abs": "" if melhoria_abs is None else melhoria_abs,
            "melhoria_LR_menos_LP_pct_sobre_LP": ""
            if melhoria_pct is None
            else melhoria_pct,
            "classificacao_LR_vs_LP": classificacao,
            "gap_relax_linear_pct": "" if gap_lp is None else gap_lp,
            "gap_lagrangeano_pct": "" if gap_lr is None else gap_lr,
            "reducao_gap_LP_menos_LR_pontos_pct": ""
            if reducao_gap is None
            else reducao_gap,
        }
    )
    return resumo


def resolver_subproblema_lagrangeano(
    S,
    T,
    V,
    A,
    arcos_entrada,
    arcos_saida,
    lambda_in,
    lambda_out,
    relax_mode,
    fluxo_inteiro,
    subproblem_time_limit,
    threads,
    usar_tiebreak,
    tiebreak_tol,
):
    if relax_mode not in {"all", "in", "out"}:
        raise ValueError(f"relax_mode inválido: {relax_mode}")
    t0 = time.monotonic()
    S_set = set(S)
    T_set = set(T)
    m = len(S)
    relax_in = relax_mode in {"all", "in"}
    relax_out = relax_mode in {"all", "out"}
    modelo = Model(f"LR-ORIGINAL-{relax_mode}")
    modelo.Params.OutputFlag = 0
    if subproblem_time_limit is not None and subproblem_time_limit > 0:
        modelo.Params.TimeLimit = subproblem_time_limit
    if threads is not None and threads > 0:
        modelo.Params.Threads = threads
    tipo_f = GRB.INTEGER if fluxo_inteiro else GRB.CONTINUOUS
    y = {v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]") for v in V}
    f = {
        (u, v): modelo.addVar(lb=0.0, ub=m, vtype=tipo_f, name=f"f[{u},{v}]")
        for u, v in A
    }
    entrada = {v: quicksum((f[a] for a in arcos_entrada.get(v, []))) for v in V}
    saida = {v: quicksum((f[a] for a in arcos_saida.get(v, []))) for v in V}
    objetivo_fluxo = quicksum(
        (
            (
                (lambda_in[v] if relax_in else 0.0)
                + (lambda_out[u] if relax_out else 0.0)
            )
            * f[u, v]
            for u, v in A
        )
    )
    objetivo_y = quicksum(
        (
            coeficientes_lagrangeanos_por_vertice(
                v=v,
                S_set=S_set,
                T_set=T_set,
                m=m,
                lambda_in=lambda_in,
                lambda_out=lambda_out,
                relax_mode=relax_mode,
            )[0]
            * y[v]
            for v in V
        )
    )
    constante = sum(
        (
            coeficientes_lagrangeanos_por_vertice(
                v=v,
                S_set=S_set,
                T_set=T_set,
                m=m,
                lambda_in=lambda_in,
                lambda_out=lambda_out,
                relax_mode=relax_mode,
            )[1]
            for v in V
        )
    )
    objetivo_lagrangeano = objetivo_fluxo + objetivo_y + constante
    modelo.setObjective(objetivo_lagrangeano, GRB.MINIMIZE)

    adicionar_restricoes_fluxo(modelo, S, T, V, entrada, saida)

    if not relax_in:
        adicionar_ativacao_entrada(modelo, S, T, V, entrada, y)
    if not relax_out:
        adicionar_ativacao_saida(modelo, S, T, V, saida, y)

    modelo.optimize()

    status_1 = modelo.Status
    status_1_nome = nome_status_gurobi(status_1)
    solcount_1 = int(getattr(modelo, "SolCount", 0))
    obj_bound = bound_objetivo_seguro(modelo)
    L_incumbente = valor_objetivo_seguro(modelo) if solcount_1 > 0 else None

    if status_1 == GRB.OPTIMAL:
        L_certificado = L_incumbente
        subgradiente_valido = True
    else:
        L_certificado = obj_bound
        subgradiente_valido = False

    if solcount_1 == 0:
        return {
            "tem_solucao": False,
            "status": status_1_nome,
            "status_lagrangeano": status_1_nome,
            "status_tiebreak": "",
            "subgradiente_valido": False,
            "L_incumbente": L_incumbente,
            "L_certificado": L_certificado,
            "obj_bound": obj_bound,
            "runtime": time.monotonic() - t0,
            "y": None,
            "f": None,
            "entrada": None,
            "saida": None,
            "num_y_1": None,
            "fluxo_total_tiebreak": None,
            "UB_heuristico_reparo": None,
        }

    status_final_nome = status_1_nome
    status_tiebreak_nome = ""
    fluxo_total_tiebreak = None
    if usar_tiebreak and status_1 == GRB.OPTIMAL and (L_incumbente is not None):
        modelo.addConstr(
            objetivo_lagrangeano <= L_incumbente + tiebreak_tol,
            name="fixa_obj_lagrangeano_para_tiebreak",
        )
        fluxo_total = quicksum((f[a] for a in A))
        modelo.setObjective(fluxo_total, GRB.MINIMIZE)
        modelo.optimize()
        status_2_nome = nome_status_gurobi(modelo.Status)
        status_tiebreak_nome = status_2_nome
        if int(getattr(modelo, "SolCount", 0)) > 0:
            status_final_nome = status_2_nome
            fluxo_total_tiebreak = valor_objetivo_seguro(modelo)
        else:
            status_final_nome = f"{status_1_nome};TIEBREAK_{status_2_nome}"
    y_val = {v: float(y[v].X) for v in V}
    f_val = {a: float(f[a].X) for a in A}
    entrada_val = {v: sum((f_val[a] for a in arcos_entrada.get(v, []))) for v in V}
    saida_val = {v: sum((f_val[a] for a in arcos_saida.get(v, []))) for v in V}
    ub_reparo = calcular_ub_reparo_fluxo(
        S=S, T=T, V=V, entrada=entrada_val, saida=saida_val
    )
    return {
        "tem_solucao": True,
        "status": status_final_nome,
        "status_lagrangeano": status_1_nome,
        "status_tiebreak": status_tiebreak_nome,
        "subgradiente_valido": subgradiente_valido,
        "L_incumbente": L_incumbente,
        "L_certificado": L_certificado,
        "obj_bound": obj_bound,
        "runtime": time.monotonic() - t0,
        "y": y_val,
        "f": f_val,
        "entrada": entrada_val,
        "saida": saida_val,
        "num_y_1": int(sum((1 for v in V if y_val[v] > 0.5))),
        "fluxo_total_tiebreak": fluxo_total_tiebreak,
        "UB_heuristico_reparo": ub_reparo,
    }


def calcular_ub_reparo_fluxo(S, T, V, entrada, saida, tol=1e-07):
    S_set = set(S)
    T_set = set(T)
    abertos = 0
    for v in V:
        a_v = 1 if v in T_set else 0
        b_v = 1 if v in S_set else 0
        precisa_por_entrada = entrada[v] > a_v + tol
        precisa_por_saida = saida[v] > b_v + tol
        if precisa_por_entrada or precisa_por_saida:
            abertos += 1
    return float(abertos)


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
    norma2 = norma2_valores(g_in.values()) + norma2_valores(g_out.values())
    norma = math.sqrt(norma2)
    return {
        "g_in": g_in,
        "g_out": g_out,
        "norma2": norma2,
        "norma": norma,
        "max_g_in": "" if not g_in else max(g_in.values()),
        "min_g_in": "" if not g_in else min(g_in.values()),
        "max_g_out": "" if not g_out else max(g_out.values()),
        "min_g_out": "" if not g_out else min(g_out.values()),
        "soma_viol_pos": sum((max(0.0, x) for x in g_in.values()))
        + sum((max(0.0, x) for x in g_out.values())),
    }


class ConfigSubgradienteOriginal:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def calcular_tamanho_passo(
    iteracao, regra, alpha_atual, ub, lb_referencia, norma2_g, theta0
):
    if norma2_g <= 1e-18:
        return 0.0
    if (
        regra == "polyak"
        and ub is not None
        and (lb_referencia is not None)
        and (ub > lb_referencia)
    ):
        return alpha_atual * (ub - lb_referencia) / norma2_g
    if regra == "harmonic":
        return theta0 / max(1, iteracao)
    if regra == "sqrt":
        return theta0 / math.sqrt(max(1, iteracao))
    if regra == "constant":
        return theta0
    return theta0 / math.sqrt(max(1, iteracao))


def projetar_lambda(valor, lambda_max):
    valor = max(0.0, valor)
    if lambda_max is not None:
        valor = min(valor, lambda_max)
    return valor


def executar_subgradiente_original(
    nome_instancia, S, T, VI, V, A, arcos_entrada, arcos_saida, config
):
    t_total0 = time.monotonic()
    lambda_in = {v: float(config.lambda_in_init) for v in V}
    lambda_out = {v: float(config.lambda_out_init) for v in V}
    info_ub = {
        "UB": config.ub_inicial,
        "LB_mip": None,
        "status_mip": "UB_MANUAL" if config.ub_inicial is not None else None,
        "runtime_mip": 0.0,
        "solcount_mip": 1 if config.ub_inicial is not None else 0,
    }
    if (
        config.ub_inicial is None
        and config.ub_time_limit is not None
        and (config.ub_time_limit > 0)
    ):
        print(
            f"[{nome_instancia}] Calculando UB pelo modelo original por {config.ub_time_limit}s..."
        )
        info_ub = obter_ub_modelo_original(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            tempo_limite_s=config.ub_time_limit,
            threads=config.threads,
            fluxo_inteiro=True,
        )
    UB = info_ub["UB"]
    melhor_LB = -float("inf")
    melhor_iter_LB = None
    melhor_UB_heur = None
    melhor_iter_UB = None
    alpha_atual = float(config.alpha_inicial)
    sem_melhora = 0
    linhas = []
    for k in range(1, config.max_iters + 1):
        if config.tempo_limite_global is not None and config.tempo_limite_global > 0:
            if time.monotonic() - t_total0 >= config.tempo_limite_global:
                print(
                    f"[{nome_instancia}] Parou por tempo limite global de {config.tempo_limite_global}s."
                )
                break
        t_iter0 = time.monotonic()
        sub = resolver_subproblema_lagrangeano(
            S=S,
            T=T,
            V=V,
            A=A,
            arcos_entrada=arcos_entrada,
            arcos_saida=arcos_saida,
            lambda_in=lambda_in,
            lambda_out=lambda_out,
            relax_mode=config.relax_mode,
            fluxo_inteiro=config.fluxo_inteiro,
            subproblem_time_limit=config.subproblem_time_limit,
            threads=config.threads,
            usar_tiebreak=config.usar_tiebreak,
            tiebreak_tol=config.tiebreak_tol,
        )
        L_inc = sub["L_incumbente"]
        L_cert = sub["L_certificado"]
        melhorou = False
        if L_cert is not None and L_cert > melhor_LB + config.tol_melhoria:
            melhor_LB = float(L_cert)
            melhor_iter_LB = k
            sem_melhora = 0
            melhorou = True
        else:
            sem_melhora += 1
        
        ub_heur = sub.get("UB_heuristico_reparo")
        if config.usar_ub_heuristico and ub_heur is not None:
            if melhor_UB_heur is None or ub_heur < melhor_UB_heur:
                melhor_UB_heur = float(ub_heur)
                melhor_iter_UB = k
            if UB is None or ub_heur < UB:
                UB = float(ub_heur)
        
        alpha_reduzido = 0
        if sem_melhora >= config.stall_limit:
            novo_alpha = max(config.alpha_min, alpha_atual * config.alpha_decay)
            if novo_alpha < alpha_atual - 1e-18:
                alpha_reduzido = 1
            alpha_atual = novo_alpha
            sem_melhora = 0
        
        if not sub["tem_solucao"]:
            gap = gap_percentual(UB, None if melhor_LB == -float("inf") else melhor_LB)
            linha = {
                "instance": nome_instancia,
                "method": "original_subgradient",
                "relax_mode": config.relax_mode,
                "iter": k,
                "status_subproblema": sub["status"],
                "status_lagrangeano": sub["status_lagrangeano"],
                "status_tiebreak": sub["status_tiebreak"],
                "subgradiente_valido": sub["subgradiente_valido"],
                "L_incumbente_subproblema": "" if L_inc is None else L_inc,
                "L_bound_certificado": "" if L_cert is None else L_cert,
                "melhor_LB_certificado": ""
                if melhor_LB == -float("inf")
                else melhor_LB,
                "melhor_iter_LB": "" if melhor_iter_LB is None else melhor_iter_LB,
                "UB": "" if UB is None else UB,
                "UB_heuristico_reparo": "" if ub_heur is None else ub_heur,
                "melhor_UB_heuristico": ""
                if melhor_UB_heur is None
                else melhor_UB_heur,
                "melhor_iter_UB_heuristico": ""
                if melhor_iter_UB is None
                else melhor_iter_UB,
                "gap_pct": "" if gap is None else gap,
                "alpha": alpha_atual,
                "alpha_reduzido": alpha_reduzido,
                "theta": "",
                "step_rule": config.step_rule,
                "norma_subgrad": "",
                "norma_passo": "",
                "sem_melhoria": sem_melhora,
                "num_y_1_oracle": "",
                "max_g_in": "",
                "min_g_in": "",
                "max_g_out": "",
                "min_g_out": "",
                "soma_viol_pos": "",
                "fluxo_total_tiebreak": "",
                "runtime_subproblema_s": sub["runtime"],
                "runtime_iter_s": time.monotonic() - t_iter0,
                "runtime_total_s": time.monotonic() - t_total0,
            }
            linhas.append(linha)
            print(
                f"[{nome_instancia}] Subproblema sem solução na iteração {k}: {sub['status']}"
            )
            break
        subgrad = calcular_subgradientes(
            S=S,
            T=T,
            V=V,
            entrada=sub["entrada"],
            saida=sub["saida"],
            y=sub["y"],
            relax_mode=config.relax_mode,
        )
        norma2 = float(subgrad["norma2"])
        norma = float(subgrad["norma"])
        L_ref_passo = L_inc if L_inc is not None else L_cert
        theta = calcular_tamanho_passo(
            iteracao=k,
            regra=config.step_rule,
            alpha_atual=alpha_atual,
            ub=UB,
            lb_referencia=L_ref_passo,
            norma2_g=norma2,
            theta0=config.theta0,
        )
        norma_passo2 = 0.0
        pode_atualizar = (
            sub["subgradiente_valido"] or config.atualizar_com_subproblema_nao_otimo
        )
        if pode_atualizar:
            if config.relax_mode in {"all", "in"}:
                for v, g in subgrad["g_in"].items():
                    antigo = lambda_in[v]
                    novo = projetar_lambda(antigo + theta * g, config.lambda_max)
                    lambda_in[v] = novo
                    norma_passo2 += (novo - antigo) ** 2
            if config.relax_mode in {"all", "out"}:
                for v, g in subgrad["g_out"].items():
                    antigo = lambda_out[v]
                    novo = projetar_lambda(antigo + theta * g, config.lambda_max)
                    lambda_out[v] = novo
                    norma_passo2 += (novo - antigo) ** 2
        else:
            print(
                f"[{nome_instancia}] Parou porque o subproblema não foi ótimo e a atualização com subproblema não ótimo está desativada."
            )
        
        norma_passo = math.sqrt(norma_passo2)
        gap = gap_percentual(UB, None if melhor_LB == -float("inf") else melhor_LB)
        runtime_iter = time.monotonic() - t_iter0
        runtime_total = time.monotonic() - t_total0
        linha = {
            "instance": nome_instancia,
            "method": "original_subgradient",
            "relax_mode": config.relax_mode,
            "iter": k,
            "status_subproblema": sub["status"],
            "status_lagrangeano": sub["status_lagrangeano"],
            "status_tiebreak": sub["status_tiebreak"],
            "subgradiente_valido": sub["subgradiente_valido"],
            "L_incumbente_subproblema": "" if L_inc is None else L_inc,
            "L_bound_certificado": "" if L_cert is None else L_cert,
            "melhor_LB_certificado": "" if melhor_LB == -float("inf") else melhor_LB,
            "melhor_iter_LB": "" if melhor_iter_LB is None else melhor_iter_LB,
            "UB": "" if UB is None else UB,
            "UB_heuristico_reparo": "" if ub_heur is None else ub_heur,
            "melhor_UB_heuristico": "" if melhor_UB_heur is None else melhor_UB_heur,
            "melhor_iter_UB_heuristico": ""
            if melhor_iter_UB is None
            else melhor_iter_UB,
            "gap_pct": "" if gap is None else gap,
            "alpha": alpha_atual,
            "alpha_reduzido": alpha_reduzido,
            "theta": theta,
            "step_rule": config.step_rule,
            "norma_subgrad": norma,
            "norma_passo": norma_passo,
            "sem_melhoria": sem_melhora,
            "num_y_1_oracle": sub["num_y_1"],
            "max_g_in": subgrad["max_g_in"],
            "min_g_in": subgrad["min_g_in"],
            "max_g_out": subgrad["max_g_out"],
            "min_g_out": subgrad["min_g_out"],
            "soma_viol_pos": subgrad["soma_viol_pos"],
            "fluxo_total_tiebreak": ""
            if sub["fluxo_total_tiebreak"] is None
            else sub["fluxo_total_tiebreak"],
            "runtime_subproblema_s": sub["runtime"],
            "runtime_iter_s": runtime_iter,
            "runtime_total_s": runtime_total,
        }
        linhas.append(linha)
        deve_printar = (
            k == 1
            or k == config.max_iters
            or (config.print_every > 0 and k % config.print_every == 0)
            or melhorou
            or alpha_reduzido
        )
        if deve_printar:
            gap_txt = "NA" if gap is None else f"{gap:.2f}%"
            print(
                f"[{nome_instancia}] original-{config.relax_mode} it={k:05d} L_inc={(L_inc if L_inc is not None else 'NA')} L_cert={(L_cert if L_cert is not None else 'NA')} bestLB={(melhor_LB if melhor_LB != -float('inf') else 'NA')} UB={(UB if UB is not None else 'NA')} gap={gap_txt} UB_heur={(ub_heur if ub_heur is not None else 'NA')} ||g||={norma:.6g} theta={theta:.6g} alpha={alpha_atual:.6g} step={norma_passo:.6g} status={sub['status']}"
            )
        if not pode_atualizar:
            break
        if config.parar_por_convergencia and norma <= config.tol_norma:
            print(
                f"[{nome_instancia}] Parou por norma do subgradiente <= {config.tol_norma}."
            )
            break
        if config.parar_por_convergencia and theta <= 1e-18:
            print(f"[{nome_instancia}] Parou por passo praticamente zero.")
            break
        if config.parar_por_convergencia and alpha_atual <= config.alpha_stop:
            print(f"[{nome_instancia}] Parou por alpha <= {config.alpha_stop}.")
            break
    
    melhor_lb_final = None if melhor_LB == -float("inf") else melhor_LB

    resumo = {
        "instance": nome_instancia,
        "method": "original_subgradient",
        "relax_mode": config.relax_mode,
        "N_nodes": len(V),
        "A_R": len(A),
        "m": len(S),
        "VI": len(VI),
        "multiplicadores": len(V)
        * (
            (1 if config.relax_mode in {"all", "in"} else 0)
            + (1 if config.relax_mode in {"all", "out"} else 0)
        ),
        "max_iters": config.max_iters,
        "iters_executadas": len(linhas),
        "melhor_LB_certificado": "" if melhor_lb_final is None else melhor_lb_final,
        "melhor_iter_LB": "" if melhor_iter_LB is None else melhor_iter_LB,
        "UB_final": "" if UB is None else UB,
        "melhor_UB_heuristico": "" if melhor_UB_heur is None else melhor_UB_heur,
        "melhor_iter_UB_heuristico": "" if melhor_iter_UB is None else melhor_iter_UB,
        "gap_pct": ""
        if gap_percentual(UB, melhor_lb_final) is None
        else gap_percentual(UB, melhor_lb_final),
        "status_mip_ub": info_ub["status_mip"],
        "LB_mip_ub": "" if info_ub["LB_mip"] is None else info_ub["LB_mip"],
        "runtime_mip_ub_s": info_ub["runtime_mip"],
        "solcount_mip_ub": info_ub["solcount_mip"],
        "alpha_final": alpha_atual,
        "runtime_total_s": time.monotonic() - t_total0,
        "step_rule": config.step_rule,
        "fluxo_inteiro": config.fluxo_inteiro,
        "tiebreak": config.usar_tiebreak,
        "atualizar_com_subproblema_nao_otimo": config.atualizar_com_subproblema_nao_otimo,
        "observacao": "relaxacao_lagrangeana_original_agregada_subgradiente_polyak",
    }
    return (resumo, linhas)


ITER_HEADER = [
    "instance",
    "method",
    "relax_mode",
    "iter",
    "status_subproblema",
    "status_lagrangeano",
    "status_tiebreak",
    "subgradiente_valido",
    "L_incumbente_subproblema",
    "L_bound_certificado",
    "melhor_LB_certificado",
    "melhor_iter_LB",
    "UB",
    "UB_heuristico_reparo",
    "melhor_UB_heuristico",
    "melhor_iter_UB_heuristico",
    "gap_pct",
    "alpha",
    "alpha_reduzido",
    "theta",
    "step_rule",
    "norma_subgrad",
    "norma_passo",
    "sem_melhoria",
    "num_y_1_oracle",
    "max_g_in",
    "min_g_in",
    "max_g_out",
    "min_g_out",
    "soma_viol_pos",
    "fluxo_total_tiebreak",
    "runtime_subproblema_s",
    "runtime_iter_s",
    "runtime_total_s",
]
RESUMO_HEADER = [
    "instance",
    "method",
    "relax_mode",
    "N_nodes",
    "A_R",
    "m",
    "VI",
    "multiplicadores",
    "max_iters",
    "iters_executadas",
    "melhor_LB_certificado",
    "melhor_iter_LB",
    "UB_final",
    "melhor_UB_heuristico",
    "melhor_iter_UB_heuristico",
    "gap_pct",
    "LB_relax_linear",
    "LB_relax_linear_bound",
    "status_relax_linear",
    "runtime_relax_linear_s",
    "melhoria_LR_menos_LP_abs",
    "melhoria_LR_menos_LP_pct_sobre_LP",
    "classificacao_LR_vs_LP",
    "gap_relax_linear_pct",
    "gap_lagrangeano_pct",
    "reducao_gap_LP_menos_LR_pontos_pct",
    "status_mip_ub",
    "LB_mip_ub",
    "runtime_mip_ub_s",
    "solcount_mip_ub",
    "alpha_final",
    "runtime_total_s",
    "step_rule",
    "fluxo_inteiro",
    "tiebreak",
    "atualizar_com_subproblema_nao_otimo",
    "observacao",
]


def executar_arquivo(caminho_instancia, args):
    nome = caminho_instancia.name
    try:
        dados = ler_instancia(str(caminho_instancia))
    except Exception as exc:
        print(f"[{nome}] ERRO no parsing: {exc}")
        return (None, [])
    
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
                u, v = (e[0], e[1])
            vertices.add(u)
            vertices.add(v)
        V = list(vertices)
    
    adj = construir_adjacencia(E_w)
    R_instancia = int(float(R0))
    A_original = construir_arcos_alcance(V, adj, R_instancia)
    S, T, V, A, arcos_entrada, arcos_saida = preparar_estrutura_rede(
        S, T, V, A_original
    )

    config = ConfigSubgradienteOriginal(
        relax_mode=args.relax_mode,
        max_iters=args.max_iters,
        ub_inicial=args.ub,
        ub_time_limit=None,
        usar_ub_heuristico=True,
        step_rule=args.step_rule,
        alpha_inicial=args.alpha,
        alpha_decay=args.alpha_decay,
        alpha_min=args.alpha_min,
        alpha_stop=args.alpha_stop,
        stall_limit=150,
        theta0=0.01,
        lambda_in_init=args.lambda_in_init,
        lambda_out_init=args.lambda_out_init,
        lambda_max=None,
        tol_norma=args.tol_norma,
        tol_melhoria=args.tol_melhoria,
        subproblem_time_limit=None,
        fluxo_inteiro=False,
        threads=None,
        usar_tiebreak=True,
        tiebreak_tol=1e-07,
        atualizar_com_subproblema_nao_otimo=True,
        tempo_limite_global=args.tempo_limite_global,
        parar_por_convergencia=False,
        print_every=args.print_every,
    )

    multiplicadores = len(V) * (
        (1 if args.relax_mode in {"all", "in"} else 0)
        + (1 if args.relax_mode in {"all", "out"} else 0)
    )
    print("\n" + "=" * 80)
    print(f"Arquivo: {nome}")
    print(f"R original: {R_instancia}")
    print("Relaxação: original/agregada, sem caminhos")
    print(f"Modo de relaxação: {args.relax_mode}")
    print("Método dual: subgradiente projetado")
    print(f"|V|={len(V)} |A_r|={len(A)} |S|=|T|={len(S)} |VI|={len(VI)}")
    print(f"Multiplicadores: {multiplicadores}")
    print("Fluxo inteiro no oracle: False")
    print(f"UB inicial: {(args.ub if args.ub is not None else 'NA')}")
    print(f"Regra de passo: {args.step_rule}")
    print(f"alpha inicial: {args.alpha}")
    print("Tiebreak menor fluxo: True")
    print("=" * 80)
    print(f"[{nome}] Resolvendo relaxação linear do modelo original/agregado...")
    info_lp = resolver_relaxacao_linear(
        S=S,
        T=T,
        V=V,
        A=A,
        arcos_entrada=arcos_entrada,
        arcos_saida=arcos_saida,
        tempo_limite_s=None,
        threads=None,
    )
    print(
        f"[{nome}] LP status={info_lp['status_relax_linear']} LB_LP={info_lp['LB_relax_linear']} runtime={info_lp['runtime_relax_linear_s']:.3f}s"
    )

    resumo, linhas = executar_subgradiente_original(
        nome_instancia=nome,
        S=S,
        T=T,
        VI=list(VI),
        V=V,
        A=A,
        arcos_entrada=arcos_entrada,
        arcos_saida=arcos_saida,
        config=config,
    )

    for linha in linhas:
        linha["R"] = R_instancia

    resumo["R"] = R_instancia

    resumo = enriquecer_resumo_com_comparacao_lp(resumo, info_lp)
    print(
        f"[{nome}] Comparação final: LB_LP={resumo.get('LB_relax_linear', 'NA')} | LB_LR={resumo.get('melhor_LB_certificado', 'NA')} | melhoria={resumo.get('melhoria_LR_menos_LP_abs', 'NA')} | classe={resumo.get('classificacao_LR_vs_LP', 'NA')}"
    )
    return (resumo, linhas)


def main():
    args = argparse.Namespace(
        inputs_dir="./inputs",
        out_dir="results_original_subgradient_static",
        relax_mode="all",
        max_iters=2000,
        tempo_limite_global=3600.0,
        print_every=10,
        ub=42.0,
        step_rule="polyak",
        alpha=2.0,
        alpha_decay=0.7,
        alpha_min=0.0001,
        alpha_stop=1e-05,
        lambda_in_init=0.0,
        lambda_out_init=0.0,
        tol_norma=1e-06,
        tol_melhoria=1e-08,
    )
    pasta = Path(args.inputs_dir)
    arquivos = sorted((p for p in pasta.glob("*.txt") if p.is_file()))

    if not arquivos:
        print(f"Nenhum .txt encontrado em {pasta}.")
        return
    
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    caminho_iter = out_dir / f"original_{args.relax_mode}_subgradient_iteracoes.csv"
    caminho_resumo = out_dir / f"original_{args.relax_mode}_subgradient_resumo.csv"
    remover_arquivo_se_existir(caminho_iter)
    remover_arquivo_se_existir(caminho_resumo)
    print(f"{len(arquivos)} arquivo(s) encontrado(s) em {pasta}")
    print("Relaxação: original/agregada, sem caminhos")
    print(f"Modo de relaxação: {args.relax_mode}")
    print("Método dual: subgradiente projetado")
    print("Parâmetros: definidos estaticamente no script")
    print("Comparação LP x LR: True")
    print(f"Regra de passo: {args.step_rule}")
    print(f"alpha={args.alpha} alpha_decay={args.alpha_decay} stall_limit=150")
    print(
        f"UB={args.ub} max_iters={args.max_iters} tempo_limite_global={args.tempo_limite_global}"
    )
    print(f"CSV de iterações: {caminho_iter}")
    print(f"CSV de resumo: {caminho_resumo}")
    total = 0
    for caminho in arquivos:
        resumo, linhas = executar_arquivo(caminho, args)
        if linhas:
            append_csv(linhas, caminho_iter, ["R"] + ITER_HEADER)
        if resumo is not None:
            append_csv([resumo], caminho_resumo, ["R"] + RESUMO_HEADER)
            total += 1
    print(f"\n[ok] {total} instância(s) processada(s).")
    print(f"[ok] Iterações salvas em: {caminho_iter}")
    print(f"[ok] Resumo salvo em: {caminho_resumo}")


if __name__ == "__main__":
    main()
