import os
import time
import csv
import networkx as nx
import gurobipy as gp
from gurobipy import GRB


# ============================================================
# CONFIGURAÇÕES SIMPLES
# ============================================================

INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs_benders"

TIME_LIMIT = 1200
MAX_ITER = 10000
EPS = 1e-6

DEFAULT_R = None

# Para testar uma instância específica:
# ONLY_FILE = "bip42p.txt"
ONLY_FILE = None

VERBOSE = True
GUROBI_LOG = False

# Limite de tempo para cada resolução do mestre.
# Antes estava 60; isso estava fazendo cada iteração demorar muito.
MASTER_TIME_LIMIT = 10

# Cortes iniciais ajudam, mas podem deixar o primeiro mestre pesado.
USAR_CORTES_INICIAIS = True

# Limita a quantidade de cortes iniciais.
# Antes estava 200; para bip42p isso deixou o mestre pesado.
MAX_CORTES_INICIAIS = 80


# ============================================================
# FUNÇÕES DE LEITURA DE INSTÂNCIA
# ============================================================

def limpar_linha(linha):
    linha = linha.strip()

    if not linha:
        return ""

    if linha.startswith("#") or linha.startswith("%") or linha.startswith("//"):
        return ""

    if linha.lower().startswith("c "):
        return ""

    for sep in ["#", "%", "//"]:
        if sep in linha:
            linha = linha.split(sep)[0].strip()

    return linha


def tokens_linha(linha):
    for ch in "{}[](),;:=\t":
        linha = linha.replace(ch, " ")
    return [t for t in linha.split() if t]


def eh_numero(txt):
    try:
        float(txt)
        return True
    except Exception:
        return False


def converter_no(txt):
    try:
        x = float(txt)
        if x.is_integer():
            return int(x)
        return txt
    except Exception:
        return txt


def converter_peso(txt):
    try:
        return float(txt)
    except Exception:
        return 1.0


def eh_label_conhecida(token):
    labels = {
        "p",
        "s", "source", "sources", "origem", "origens", "start", "starts",
        "t", "target", "targets", "destino", "destinos", "sink", "sinks",
        "r", "range", "autonomy", "autonomia", "battery", "capacidade",
        "e", "edge", "a", "arc", "aresta",
        "v", "vertex", "node", "no", "nó", "nodes", "vertices",
    }
    return token.lower() in labels


def coletar_lista_apos_linha(linhas_validas, indice_atual, quantidade):
    valores = []
    i = indice_atual + 1

    while i < len(linhas_validas) and len(valores) < quantidade:
        toks = tokens_linha(linhas_validas[i])

        if not toks:
            i += 1
            continue

        primeiro = toks[0].lower()

        if eh_label_conhecida(primeiro):
            break

        for tok in toks:
            if eh_numero(tok):
                valores.append(converter_no(tok))
                if len(valores) == quantidade:
                    break

        i += 1

    return valores, i


def ler_instancia(caminho):
    nome = os.path.basename(caminho)

    G = nx.Graph()
    S = []
    T = []
    r = DEFAULT_R

    n_vertices_declarado = None

    labels_origem = {"s", "source", "sources", "origem", "origens", "start", "starts"}
    labels_destino = {"t", "target", "targets", "destino", "destinos", "sink", "sinks"}
    labels_r = {"r", "range", "autonomy", "autonomia", "battery", "capacidade"}
    labels_aresta = {"e", "edge", "a", "arc", "aresta"}
    labels_no = {"v", "vertex", "node", "no", "nó", "nodes", "vertices"}

    linhas_validas = []

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = limpar_linha(linha)
            if linha:
                linhas_validas.append(linha)

    i = 0

    while i < len(linhas_validas):
        linha = linhas_validas[i]
        toks = tokens_linha(linha)

        if not toks:
            i += 1
            continue

        label = toks[0].lower()

        if label == "p":
            nums = [float(t) for t in toks[1:] if eh_numero(t)]

            if len(nums) >= 1:
                n_vertices_declarado = int(nums[0])

            if len(nums) >= 3 and r is None:
                r = nums[2]

            i += 1
            continue

        if label in labels_r:
            nums = [float(t) for t in toks[1:] if eh_numero(t)]

            if nums:
                r = nums[0]

            i += 1
            continue

        if label in labels_origem:
            valores = [converter_no(t) for t in toks[1:] if eh_numero(t)]

            if len(valores) == 0:
                i += 1
                continue

            if (
                len(valores) >= 2
                and isinstance(valores[0], int)
                and valores[0] == len(valores) - 1
            ):
                S.extend(valores[1:])
                i += 1
                continue

            if len(valores) == 1 and isinstance(valores[0], int) and valores[0] > 0:
                quantidade = valores[0]
                coletados, novo_i = coletar_lista_apos_linha(
                    linhas_validas,
                    i,
                    quantidade
                )

                if len(coletados) == quantidade:
                    S.extend(coletados)
                    i = novo_i
                    continue

                S.extend(valores)
                i += 1
                continue

            S.extend(valores)
            i += 1
            continue

        if label in labels_destino:
            valores = [converter_no(t) for t in toks[1:] if eh_numero(t)]

            if len(valores) == 0:
                i += 1
                continue

            if (
                len(valores) >= 2
                and isinstance(valores[0], int)
                and valores[0] == len(valores) - 1
            ):
                T.extend(valores[1:])
                i += 1
                continue

            if len(valores) == 1 and isinstance(valores[0], int) and valores[0] > 0:
                quantidade = valores[0]
                coletados, novo_i = coletar_lista_apos_linha(
                    linhas_validas,
                    i,
                    quantidade
                )

                if len(coletados) == quantidade:
                    T.extend(coletados)
                    i = novo_i
                    continue

                T.extend(valores)
                i += 1
                continue

            T.extend(valores)
            i += 1
            continue

        if label in labels_no:
            for tok in toks[1:]:
                if eh_numero(tok):
                    G.add_node(converter_no(tok))

            i += 1
            continue

        if label in labels_aresta:
            if len(toks) >= 3:
                u = converter_no(toks[1])
                v = converter_no(toks[2])
                peso = 1.0

                if len(toks) >= 4 and eh_numero(toks[3]):
                    peso = converter_peso(toks[3])

                if u != v:
                    G.add_edge(u, v, weight=peso)

            i += 1
            continue

        if len(toks) >= 2 and eh_numero(toks[0]) and eh_numero(toks[1]):
            u = converter_no(toks[0])
            v = converter_no(toks[1])
            peso = 1.0

            if len(toks) >= 3 and eh_numero(toks[2]):
                peso = converter_peso(toks[2])

            if u != v:
                G.add_edge(u, v, weight=peso)

            i += 1
            continue

        i += 1

    if n_vertices_declarado is not None:
        if any(isinstance(v, int) and v == 0 for v in G.nodes()):
            inicio = 0
            fim = n_vertices_declarado - 1
        else:
            inicio = 1
            fim = n_vertices_declarado

        for v in range(inicio, fim + 1):
            G.add_node(v)

    S = list(dict.fromkeys(S))
    T = list(dict.fromkeys(T))

    for v in S:
        G.add_node(v)

    for v in T:
        G.add_node(v)

    if r is None:
        raise ValueError(
            f"A instância {nome} não informou r. "
            f"Defina DEFAULT_R no início do código."
        )

    if len(S) == 0:
        raise ValueError(f"A instância {nome} não possui conjunto de origens S.")

    if len(T) == 0:
        raise ValueError(f"A instância {nome} não possui conjunto de destinos T.")

    if len(S) != len(T):
        raise ValueError(
            f"A instância {nome} tem |S|={len(S)} e |T|={len(T)}. "
            f"O MIN-STATION exige |S|=|T|."
        )

    if not nx.is_connected(G):
        raise ValueError(f"A instância {nome} não é conexa.")

    if VERBOSE:
        print(f"S lido em {nome}: {S[:20]}")
        print(f"T lido em {nome}: {T[:20]}")

    return {
        "nome": nome,
        "G": G,
        "S": S,
        "T": T,
        "r": r,
    }


# ============================================================
# DÍGRAFO DE ALCANCE
# ============================================================

def construir_digrafo_alcance(G, r):
    A = []

    for u in G.nodes():
        distancias = nx.single_source_dijkstra_path_length(
            G,
            u,
            cutoff=r,
            weight="weight"
        )

        for v, dist in distancias.items():
            if u != v and dist <= r + EPS:
                A.append((u, v))

    return A


# ============================================================
# REDE DE FLUXO DO SUBPROBLEMA
# ============================================================

def base_coef_entrada(v, S_set, T_set, m):
    if v in T_set:
        base = 1.0
    else:
        base = 0.0

    coef = m - base
    return base, coef


def base_coef_saida(v, S_set, T_set, m):
    if v in S_set:
        base = 1.0
    else:
        base = 0.0

    coef = m - base
    return base, coef


def montar_rede_fluxo(vertices, A, S, T, y_barra):
    m = len(S)

    S_set = set(S)
    T_set = set(T)

    SS = ("__super__", "source")
    TT = ("__super__", "sink")

    N = nx.DiGraph()

    for v in vertices:
        yv = y_barra.get(v, 0.0)

        base_in, coef_in = base_coef_entrada(v, S_set, T_set, m)
        cap_in = base_in + coef_in * yv

        base_out, coef_out = base_coef_saida(v, S_set, T_set, m)
        cap_out = base_out + coef_out * yv

        N.add_edge(
            ("ent", v),
            ("meio", v),
            capacity=cap_in,
            tipo="entrada",
            vertice=v,
        )

        N.add_edge(
            ("meio", v),
            ("sai", v),
            capacity=cap_out,
            tipo="saida",
            vertice=v,
        )

    for s in S:
        N.add_edge(
            SS,
            ("meio", s),
            capacity=1.0,
            tipo="fonte",
        )

    for t in T:
        N.add_edge(
            ("meio", t),
            TT,
            capacity=1.0,
            tipo="sumidouro",
        )

    for u, v in A:
        N.add_edge(
            ("sai", u),
            ("ent", v),
            capacity=float(m),
            tipo="alcance",
        )

    return N, SS, TT


def calcular_corte_benders(vertices, A, S, T, y_barra):
    m = len(S)

    S_set = set(S)
    T_set = set(T)

    N, SS, TT = montar_rede_fluxo(vertices, A, S, T, y_barra)

    valor_corte, particao = nx.minimum_cut(N, SS, TT, capacity="capacity")
    lado_ss, lado_tt = particao

    constante = 0.0
    coeficientes = {}

    for a, b, dados in N.edges(data=True):
        if a in lado_ss and b in lado_tt:
            tipo = dados.get("tipo")

            if tipo == "entrada":
                v = dados["vertice"]
                base, coef = base_coef_entrada(v, S_set, T_set, m)

                constante += base

                if abs(coef) > EPS:
                    coeficientes[v] = coeficientes.get(v, 0.0) + coef

            elif tipo == "saida":
                v = dados["vertice"]
                base, coef = base_coef_saida(v, S_set, T_set, m)

                constante += base

                if abs(coef) > EPS:
                    coeficientes[v] = coeficientes.get(v, 0.0) + coef

            else:
                constante += dados["capacity"]

    return valor_corte, constante, coeficientes


def calcular_fluxo_final(vertices, A, S, T, y_barra):
    N, SS, TT = montar_rede_fluxo(vertices, A, S, T, y_barra)

    valor, fluxo = nx.maximum_flow(
        N,
        SS,
        TT,
        capacity="capacity"
    )

    saltos_usados = []

    for u, v in A:
        a = ("sai", u)
        b = ("ent", v)

        if a in fluxo and b in fluxo[a]:
            val = fluxo[a][b]

            if val > EPS:
                saltos_usados.append((u, v, val))

    return valor, saltos_usados


# ============================================================
# CORTES INICIAIS
# ============================================================

def adicionar_cortes_iniciais(mestre, y, vertices, A, S, T):
    S_set = set(S)
    T_set = set(T)

    saida = {v: set() for v in vertices}
    entrada = {v: set() for v in vertices}

    for u, v in A:
        saida.setdefault(u, set()).add(v)
        entrada.setdefault(v, set()).add(u)

    qtd_cortes = 0

    for s in S:
        if MAX_CORTES_INICIAIS is not None and qtd_cortes >= MAX_CORTES_INICIAIS:
            break

        alcanca_destino_direto = any(v in T_set for v in saida.get(s, set()))

        if not alcanca_destino_direto:
            candidatos = [
                v for v in saida.get(s, set())
                if v in y
            ]

            if candidatos:
                mestre.addConstr(
                    gp.quicksum(y[v] for v in candidatos) >= 1,
                    name=f"corte_inicial_origem_{s}"
                )
                qtd_cortes += 1

    for t in T:
        if MAX_CORTES_INICIAIS is not None and qtd_cortes >= MAX_CORTES_INICIAIS:
            break

        recebe_origem_direto = any(u in S_set for u in entrada.get(t, set()))

        if not recebe_origem_direto:
            candidatos = [
                u for u in entrada.get(t, set())
                if u in y
            ]

            if candidatos:
                mestre.addConstr(
                    gp.quicksum(y[u] for u in candidatos) >= 1,
                    name=f"corte_inicial_destino_{t}"
                )
                qtd_cortes += 1

    mestre.update()

    if VERBOSE:
        print(f"Cortes iniciais adicionados: {qtd_cortes}")


def adicionar_corte_inicial_global(mestre, y, vertices):
    mestre.addConstr(
        gp.quicksum(y[v] for v in vertices) >= 1,
        name="corte_inicial_global"
    )
    mestre.update()

    if VERBOSE:
        print("Corte inicial global adicionado: sum(y) >= 1")


# ============================================================
# BENDERS ITERATIVO
# ============================================================

def remover_origem_destino_iguais(S, T):
    S2 = list(S)
    T2 = list(T)

    comuns = set(S2).intersection(set(T2))

    for v in comuns:
        if v in S2 and v in T2:
            S2.remove(v)
            T2.remove(v)

    return S2, T2, comuns


def configurar_gurobi(mestre):
    mestre.Params.OutputFlag = 1 if GUROBI_LOG else 0

    # Foco em achar boas soluções incumbentes mais rápido.
    mestre.Params.MIPFocus = 1
    mestre.Params.Heuristics = 0.5

    # Cortes e presolve do Gurobi.
    mestre.Params.Cuts = 2
    mestre.Params.Presolve = 2
    mestre.Params.Symmetry = 2


def resolver_benders(instancia):
    nome = instancia["nome"]
    G = instancia["G"]
    S_original = instancia["S"]
    T_original = instancia["T"]
    r = instancia["r"]

    S, T, comuns = remover_origem_destino_iguais(S_original, T_original)

    vertices = list(G.nodes())
    m = len(S)

    inicio = time.time()

    if VERBOSE:
        print()
        print("=" * 70)
        print(f"Instância: {nome}")
        print(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()} r={r}")
        print(f"|S| original={len(S_original)} |T| original={len(T_original)}")

        if comuns:
            print(f"Vértices em S ∩ T já satisfeitos sem movimento: {len(comuns)}")

        print(f"|S| roteado={len(S)} |T| roteado={len(T)}")

    if m == 0:
        return {
            "nome": nome,
            "status": "OTIMA",
            "objetivo": 0,
            "melhor_viavel": 0,
            "estacoes": [],
            "saltos_usados": [],
            "iteracoes": 0,
            "tempo": time.time() - inicio,
            "r": r,
            "n_vertices": G.number_of_nodes(),
            "n_arestas": G.number_of_edges(),
            "n_arcos_alcance": 0,
            "m": 0,
        }

    if VERBOSE:
        print("Construindo dígrafo de alcance...")

    A = construir_digrafo_alcance(G, r)

    if VERBOSE:
        print(f"|A_r|={len(A)}")

    # Testa se existe solução com todas as estações abertas.
    y_tudo_aberto = {v: 1.0 for v in vertices}
    fluxo_full, _, _ = calcular_corte_benders(vertices, A, S, T, y_tudo_aberto)

    if fluxo_full < m - EPS:
        if VERBOSE:
            print("Mesmo com todas as estações abertas, o fluxo máximo é menor que |S|.")
            print(f"Fluxo máximo com tudo aberto: {fluxo_full}, necessário: {m}")

        return {
            "nome": nome,
            "status": "INVIAVEL",
            "objetivo": None,
            "melhor_viavel": None,
            "estacoes": [],
            "saltos_usados": [],
            "iteracoes": 0,
            "tempo": time.time() - inicio,
            "r": r,
            "n_vertices": G.number_of_nodes(),
            "n_arestas": G.number_of_edges(),
            "n_arcos_alcance": len(A),
            "m": m,
        }

    mestre = gp.Model(f"benders_{nome}")
    configurar_gurobi(mestre)

    y = {}

    for v in vertices:
        nome_var = f"y_{str(v)}"
        y[v] = mestre.addVar(vtype=GRB.BINARY, name=nome_var)

    mestre.setObjective(gp.quicksum(y[v] for v in vertices), GRB.MINIMIZE)
    mestre.update()

    if USAR_CORTES_INICIAIS:
        adicionar_cortes_iniciais(mestre, y, vertices, A, S, T)
    else:
        adicionar_corte_inicial_global(mestre, y, vertices)

    iteracao = 0
    status_final = "NAO_RESOLVIDO"

    estacoes = []
    saltos_usados = []

    melhor_viavel_obj = None
    melhor_viavel_estacoes = []
    melhor_viavel_saltos = []

    ultimo_obj_impresso = None
    melhor_fluxo_visto = -1

    while iteracao < MAX_ITER:
        tempo_passado = time.time() - inicio
        tempo_restante = TIME_LIMIT - tempo_passado

        if tempo_restante <= 0:
            status_final = "TIME_LIMIT"
            break

        mestre.Params.TimeLimit = min(tempo_restante, MASTER_TIME_LIMIT)
        mestre.optimize()

        if mestre.Status == GRB.INFEASIBLE:
            status_final = "INVIAVEL"
            break

        if mestre.SolCount == 0:
            status_final = "SEM_SOLUCAO_MESTRE"
            break

        master_foi_otimo = mestre.Status == GRB.OPTIMAL

        y_barra = {v: y[v].X for v in vertices}

        valor_corte, constante, coeficientes = calcular_corte_benders(
            vertices,
            A,
            S,
            T,
            y_barra
        )

        obj_atual = sum(1 for v in vertices if y_barra[v] > 0.5)

        if valor_corte > melhor_fluxo_visto:
            melhor_fluxo_visto = valor_corte

        deve_imprimir = (
            iteracao % 10 == 0
            or ultimo_obj_impresso != obj_atual
            or valor_corte >= m - EPS
        )

        if VERBOSE and deve_imprimir:
            status_mestre = "OPT" if master_foi_otimo else f"STATUS_{mestre.Status}"
            print(
                f"Iteração {iteracao:04d} | "
                f"mestre={obj_atual} | "
                f"fluxo/max-cut={valor_corte:.6f} | "
                f"melhor_fluxo={melhor_fluxo_visto:.6f} | "
                f"cortes={iteracao} | "
                f"mestre_status={status_mestre}"
            )
            ultimo_obj_impresso = obj_atual

        if valor_corte >= m - EPS:
            estacoes_candidatas = [v for v in vertices if y_barra[v] > 0.5]

            _, saltos_candidatos = calcular_fluxo_final(
                vertices,
                A,
                S,
                T,
                y_barra
            )

            if (
                melhor_viavel_obj is None
                or len(estacoes_candidatas) < melhor_viavel_obj
            ):
                melhor_viavel_obj = len(estacoes_candidatas)
                melhor_viavel_estacoes = estacoes_candidatas
                melhor_viavel_saltos = saltos_candidatos

            if master_foi_otimo:
                estacoes = estacoes_candidatas
                saltos_usados = saltos_candidatos
                status_final = "OTIMA"
                break

            estacoes = melhor_viavel_estacoes
            saltos_usados = melhor_viavel_saltos
            status_final = "VIAVEL_NAO_PROVADO"
            break

        expr = constante

        for v, coef in coeficientes.items():
            expr += coef * y[v]

        mestre.addConstr(expr >= m, name=f"corte_benders_{iteracao}")
        mestre.update()

        iteracao += 1

    tempo_total = time.time() - inicio

    if status_final == "OTIMA":
        objetivo = len(estacoes)
    elif melhor_viavel_obj is not None:
        objetivo = melhor_viavel_obj
        estacoes = melhor_viavel_estacoes
        saltos_usados = melhor_viavel_saltos

        if status_final in {"NAO_RESOLVIDO", "TIME_LIMIT"}:
            status_final = "VIAVEL_NAO_PROVADO"
    elif mestre.SolCount > 0:
        objetivo = None
        estacoes = [v for v in vertices if y[v].X > 0.5]
    else:
        objetivo = None

    return {
        "nome": nome,
        "status": status_final,
        "objetivo": objetivo,
        "melhor_viavel": melhor_viavel_obj,
        "estacoes": estacoes,
        "saltos_usados": saltos_usados,
        "iteracoes": iteracao,
        "tempo": tempo_total,
        "r": r,
        "n_vertices": G.number_of_nodes(),
        "n_arestas": G.number_of_edges(),
        "n_arcos_alcance": len(A),
        "m": m,
    }


# ============================================================
# SAÍDA DOS RESULTADOS
# ============================================================

def salvar_solucao(resultado):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nome_base = os.path.splitext(resultado["nome"])[0]
    caminho = os.path.join(OUTPUT_DIR, f"{nome_base}_solucao_benders.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"Instância: {resultado['nome']}\n")
        f.write(f"Status: {resultado['status']}\n")
        f.write(f"Objetivo: {resultado['objetivo']}\n")
        f.write(f"Melhor viável: {resultado['melhor_viavel']}\n")
        f.write(f"Tempo: {resultado['tempo']:.4f} s\n")
        f.write(f"Iterações de Benders: {resultado['iteracoes']}\n")
        f.write(f"r: {resultado['r']}\n")
        f.write(f"|V|: {resultado['n_vertices']}\n")
        f.write(f"|E|: {resultado['n_arestas']}\n")
        f.write(f"|A_r|: {resultado['n_arcos_alcance']}\n")
        f.write(f"|S| roteado: {resultado['m']}\n")
        f.write("\n")

        f.write("Estações abertas:\n")
        for v in sorted(resultado["estacoes"], key=lambda x: str(x)):
            f.write(f"{v}\n")

        f.write("\nSaltos usados no fluxo final:\n")
        for u, v, val in resultado["saltos_usados"]:
            f.write(f"{u} -> {v} : {val}\n")

    return caminho


def salvar_resumo(resultados):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    caminho = os.path.join(OUTPUT_DIR, "resumo_benders.csv")

    campos = [
        "instancia",
        "status",
        "objetivo",
        "melhor_viavel",
        "tempo",
        "iteracoes",
        "r",
        "m",
        "n_vertices",
        "n_arestas",
        "n_arcos_alcance",
    ]

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        for r in resultados:
            writer.writerow({
                "instancia": r["nome"],
                "status": r["status"],
                "objetivo": r["objetivo"],
                "melhor_viavel": r["melhor_viavel"],
                "tempo": f"{r['tempo']:.4f}",
                "iteracoes": r["iteracoes"],
                "r": r["r"],
                "m": r["m"],
                "n_vertices": r["n_vertices"],
                "n_arestas": r["n_arestas"],
                "n_arcos_alcance": r["n_arcos_alcance"],
            })

    return caminho


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_DIR):
        print(f"A pasta de entrada não existe: {INPUT_DIR}")
        return

    arquivos = [
        arq for arq in os.listdir(INPUT_DIR)
        if arq.lower().endswith(".txt")
    ]

    arquivos.sort()

    if ONLY_FILE is not None:
        arquivos = [arq for arq in arquivos if arq == ONLY_FILE]

    if not arquivos:
        print(f"Nenhum arquivo .txt encontrado em {INPUT_DIR}.")
        return

    resultados = []

    for arq in arquivos:
        caminho = os.path.join(INPUT_DIR, arq)

        try:
            instancia = ler_instancia(caminho)
            resultado = resolver_benders(instancia)
            resultados.append(resultado)

            caminho_sol = salvar_solucao(resultado)

            print()
            print(f"Resultado salvo em: {caminho_sol}")
            print(
                f"{resultado['nome']} | "
                f"status={resultado['status']} | "
                f"obj={resultado['objetivo']} | "
                f"melhor_viavel={resultado['melhor_viavel']} | "
                f"tempo={resultado['tempo']:.2f}s | "
                f"iter={resultado['iteracoes']}"
            )

        except Exception as e:
            print()
            print("=" * 70)
            print(f"Erro ao processar {arq}:")
            print(e)

            resultados.append({
                "nome": arq,
                "status": "ERRO",
                "objetivo": None,
                "melhor_viavel": None,
                "estacoes": [],
                "saltos_usados": [],
                "iteracoes": 0,
                "tempo": 0.0,
                "r": None,
                "n_vertices": None,
                "n_arestas": None,
                "n_arcos_alcance": None,
                "m": None,
            })

    caminho_resumo = salvar_resumo(resultados)

    print()
    print("=" * 70)
    print(f"Resumo salvo em: {caminho_resumo}")


if __name__ == "__main__":
    main()