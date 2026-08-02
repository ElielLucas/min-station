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
OUTPUT_DIR = "outputs_cumulativo"

TIME_LIMIT = 3600
MIP_GAP = 0.0
EPS = 1e-6

DEFAULT_R = None

# Para testar uma instância específica:
# ONLY_FILE = "cc10-2p.txt"
ONLY_FILE = None

VERBOSE = True
GUROBI_LOG = True

# Se True, x, z e a são inteiras.
# Se False, x, z e a são contínuas.
# Para começar os testes, recomendo False, porque o modelo já tem y binário
# e o modelo expandido pode ficar muito grande.
FLUXO_INTEIRO = False

# Para evitar arquivos de solução gigantes.
MAX_SALTOS_SALVAR = 5000
MAX_RECARGAS_SALVAR = 5000
MAX_ABSORCOES_SALVAR = 5000


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

    if abs(r - round(r)) > EPS:
        raise ValueError(
            f"A autonomia r={r} da instância {nome} não é inteira. "
            f"A formulação cumulativa usa estados q=0,...,r."
        )

    r = int(round(r))

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
# PREPARAÇÃO DOS ARCOS DIRECIONADOS
# ============================================================

def peso_inteiro(peso, nome_instancia):
    if abs(peso - round(peso)) > EPS:
        raise ValueError(
            f"A formulação cumulativa exige pesos inteiros. "
            f"Foi encontrado peso {peso} na instância {nome_instancia}."
        )

    return int(round(peso))


def construir_arcos_direcionados(G, r, nome_instancia):
    """
    Cada aresta não direcionada {u,v} vira dois arcos:
        u -> v
        v -> u

    Apenas arcos com consumo <= r são mantidos.
    """
    arcos = []

    for u, v, dados in G.edges(data=True):
        peso = peso_inteiro(float(dados.get("weight", 1.0)), nome_instancia)

        if peso <= r:
            arcos.append((u, v, peso))
            arcos.append((v, u, peso))

    return arcos


# ============================================================
# MODELO CUMULATIVO
# ============================================================

def configurar_gurobi(modelo):
    modelo.Params.OutputFlag = 1 if GUROBI_LOG else 0
    modelo.Params.TimeLimit = TIME_LIMIT
    modelo.Params.MIPGap = MIP_GAP

    modelo.Params.MIPFocus = 1
    modelo.Params.Heuristics = 0.5
    modelo.Params.Cuts = 2
    modelo.Params.Presolve = 2
    modelo.Params.Symmetry = 2


def tipo_fluxo():
    if FLUXO_INTEIRO:
        return GRB.INTEGER
    return GRB.CONTINUOUS


def resolver_cumulativo(instancia):
    nome = instancia["nome"]
    G = instancia["G"]
    S = instancia["S"]
    T = instancia["T"]
    r = instancia["r"]

    vertices = list(G.nodes())
    S_set = set(S)
    T_set = set(T)
    m = len(S)

    inicio = time.time()

    if VERBOSE:
        print()
        print("=" * 70)
        print(f"Instância: {nome}")
        print(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()} r={r}")
        print(f"|S|={len(S)} |T|={len(T)}")
        print("Construindo arcos direcionados do grafo original...")

    arcos = construir_arcos_direcionados(G, r, nome)

    if VERBOSE:
        print(f"|A dirigido|={len(arcos)}")
        print("Criando modelo cumulativo...")

    modelo = gp.Model(f"cumulativo_{nome}")
    configurar_gurobi(modelo)

    fluxo_vtype = tipo_fluxo()

    # ------------------------------------------------------------
    # Variáveis y_v
    # ------------------------------------------------------------
    y = {}

    for v in vertices:
        y[v] = modelo.addVar(
            vtype=GRB.BINARY,
            name=f"y_{v}"
        )

    # ------------------------------------------------------------
    # Variáveis x_{ij}^q
    #
    # x[(i,j,q)] = fluxo que sai de i para j com consumo q,
    # chegando em j com consumo q + c_ij.
    # ------------------------------------------------------------
    x = {}

    saida_estado = {}
    entrada_estado = {}

    total_x = 0

    for i, j, consumo in arcos:
        for q in range(0, r - consumo + 1):
            var = modelo.addVar(
                lb=0.0,
                ub=float(m),
                vtype=fluxo_vtype,
                name=f"x_{i}_{j}_{q}"
            )

            x[(i, j, q)] = var

            saida_estado.setdefault((i, q), []).append(var)
            entrada_estado.setdefault((j, q + consumo), []).append(var)

            total_x += 1

    # ------------------------------------------------------------
    # Variáveis z_v^q
    #
    # z[(v,q)] = fluxo que recarrega em v após chegar com consumo q.
    # Depois da recarga, o fluxo volta ao estado (v,0).
    # ------------------------------------------------------------
    z = {}
    recarga_saida_estado = {}
    recarga_entrada_zero = {}

    total_z = 0

    for v in vertices:
        for q in range(1, r + 1):
            var = modelo.addVar(
                lb=0.0,
                ub=float(m),
                vtype=fluxo_vtype,
                name=f"z_{v}_{q}"
            )

            z[(v, q)] = var
            recarga_saida_estado[(v, q)] = var
            recarga_entrada_zero.setdefault(v, []).append(var)

            total_z += 1

    # ------------------------------------------------------------
    # Variáveis a_t^q
    #
    # a[(t,q)] = fluxo absorvido no destino t com consumo q.
    # ------------------------------------------------------------
    a = {}

    total_a = 0

    for t in T:
        for q in range(0, r + 1):
            var = modelo.addVar(
                lb=0.0,
                ub=1.0,
                vtype=fluxo_vtype,
                name=f"a_{t}_{q}"
            )

            a[(t, q)] = var
            total_a += 1

    modelo.update()

    if VERBOSE:
        print(f"Variáveis y: {len(y)}")
        print(f"Variáveis x: {total_x}")
        print(f"Variáveis z: {total_z}")
        print(f"Variáveis a: {total_a}")
        print("Adicionando função objetivo...")

    modelo.setObjective(
        gp.quicksum(y[v] for v in vertices),
        GRB.MINIMIZE
    )

    # ------------------------------------------------------------
    # Atendimento dos destinos
    # sum_q a_t^q = 1
    # ------------------------------------------------------------
    if VERBOSE:
        print("Adicionando restrições de atendimento dos destinos...")

    for t in T:
        modelo.addConstr(
            gp.quicksum(a[(t, q)] for q in range(0, r + 1)) == 1,
            name=f"atende_destino_{t}"
        )

    # ------------------------------------------------------------
    # Conservação de fluxo nos estados (v,q)
    # ------------------------------------------------------------
    if VERBOSE:
        print("Adicionando restrições de conservação nos estados...")

    total_conservacao = 0

    for v in vertices:
        recargas_para_zero = recarga_entrada_zero.get(v, [])

        for q in range(0, r + 1):
            termos_saida = []

            if (v, q) in saida_estado:
                termos_saida.extend(saida_estado[(v, q)])

            if q > 0 and (v, q) in recarga_saida_estado:
                termos_saida.append(recarga_saida_estado[(v, q)])

            if v in T_set and (v, q) in a:
                termos_saida.append(a[(v, q)])

            termos_entrada = []

            if (v, q) in entrada_estado:
                termos_entrada.extend(entrada_estado[(v, q)])

            if q == 0:
                termos_entrada.extend(recargas_para_zero)

            supply = 0.0

            if v in S_set and q == 0:
                supply = 1.0

            modelo.addConstr(
                gp.quicksum(termos_saida)
                ==
                gp.quicksum(termos_entrada) + supply,
                name=f"conserva_{v}_{q}"
            )

            total_conservacao += 1

    # ------------------------------------------------------------
    # Ativação da recarga
    # z_v^q <= |S| y_v
    # ------------------------------------------------------------
    if VERBOSE:
        print("Adicionando restrições de ativação da recarga...")

    total_ativacao = 0

    for v in vertices:
        for q in range(1, r + 1):
            modelo.addConstr(
                z[(v, q)] <= m * y[v],
                name=f"ativa_recarga_{v}_{q}"
            )
            total_ativacao += 1

    if VERBOSE:
        print(f"Restrições de atendimento: {len(T)}")
        print(f"Restrições de conservação: {total_conservacao}")
        print(f"Restrições de ativação: {total_ativacao}")
        print("Otimizando...")

    modelo.optimize()

    tempo_total = time.time() - inicio

    status = interpretar_status_gurobi(modelo.Status)

    estacoes = []
    saltos_usados = []
    recargas_usadas = []
    absorcoes = []

    objetivo = None
    gap = None
    bound = None

    if modelo.SolCount > 0:
        objetivo = modelo.ObjVal
        bound = modelo.ObjBound

        if abs(modelo.ObjVal) > EPS:
            gap = abs(modelo.ObjVal - modelo.ObjBound) / abs(modelo.ObjVal)
        else:
            gap = 0.0

        estacoes = [
            v for v in vertices
            if y[v].X > 0.5
        ]

        for (i, j, q), var in x.items():
            if var.X > EPS:
                saltos_usados.append((i, j, q, var.X))

        for (v, q), var in z.items():
            if var.X > EPS:
                recargas_usadas.append((v, q, var.X))

        for (t, q), var in a.items():
            if var.X > EPS:
                absorcoes.append((t, q, var.X))

    return {
        "nome": nome,
        "status": status,
        "objetivo": objetivo,
        "bound": bound,
        "gap": gap,
        "estacoes": estacoes,
        "saltos_usados": saltos_usados,
        "recargas_usadas": recargas_usadas,
        "absorcoes": absorcoes,
        "tempo": tempo_total,
        "r": r,
        "m": m,
        "n_vertices": G.number_of_nodes(),
        "n_arestas": G.number_of_edges(),
        "n_arcos_dirigidos": len(arcos),
        "n_var_y": len(y),
        "n_var_x": total_x,
        "n_var_z": total_z,
        "n_var_a": total_a,
        "n_conservacao": total_conservacao,
        "n_ativacao": total_ativacao,
    }


def interpretar_status_gurobi(status):
    if status == GRB.OPTIMAL:
        return "OTIMA"

    if status == GRB.TIME_LIMIT:
        return "TIME_LIMIT"

    if status == GRB.INFEASIBLE:
        return "INVIAVEL"

    if status == GRB.UNBOUNDED:
        return "ILIMITADA"

    if status == GRB.INF_OR_UNBD:
        return "INVIAVEL_OU_ILIMITADA"

    if status == GRB.INTERRUPTED:
        return "INTERROMPIDA"

    return f"STATUS_{status}"


# ============================================================
# SAÍDA DOS RESULTADOS
# ============================================================

def salvar_solucao(resultado):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nome_base = os.path.splitext(resultado["nome"])[0]
    caminho = os.path.join(OUTPUT_DIR, f"{nome_base}_solucao_cumulativo.txt")

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"Instância: {resultado['nome']}\n")
        f.write(f"Status: {resultado['status']}\n")
        f.write(f"Objetivo: {resultado['objetivo']}\n")
        f.write(f"Bound: {resultado['bound']}\n")
        f.write(f"Gap: {resultado['gap']}\n")
        f.write(f"Tempo: {resultado['tempo']:.4f} s\n")
        f.write(f"r: {resultado['r']}\n")
        f.write(f"|S|: {resultado['m']}\n")
        f.write(f"|V|: {resultado['n_vertices']}\n")
        f.write(f"|E|: {resultado['n_arestas']}\n")
        f.write(f"|A dirigido|: {resultado['n_arcos_dirigidos']}\n")
        f.write(f"Variáveis y: {resultado['n_var_y']}\n")
        f.write(f"Variáveis x: {resultado['n_var_x']}\n")
        f.write(f"Variáveis z: {resultado['n_var_z']}\n")
        f.write(f"Variáveis a: {resultado['n_var_a']}\n")
        f.write(f"Restrições conservação: {resultado['n_conservacao']}\n")
        f.write(f"Restrições ativação: {resultado['n_ativacao']}\n")
        f.write("\n")

        f.write("Estações abertas:\n")
        for v in sorted(resultado["estacoes"], key=lambda item: str(item)):
            f.write(f"{v}\n")

        f.write("\nSaltos usados no fluxo acumulado:\n")
        qtd_saltos = 0
        for i, j, q, val in resultado["saltos_usados"]:
            if qtd_saltos >= MAX_SALTOS_SALVAR:
                f.write("...\n")
                f.write(
                    f"Saída truncada. Total de saltos usados: "
                    f"{len(resultado['saltos_usados'])}\n"
                )
                break

            f.write(f"{i} -> {j} | consumo_saida={q} | fluxo={val}\n")
            qtd_saltos += 1

        f.write("\nRecargas usadas:\n")
        qtd_recargas = 0
        for v, q, val in resultado["recargas_usadas"]:
            if qtd_recargas >= MAX_RECARGAS_SALVAR:
                f.write("...\n")
                f.write(
                    f"Saída truncada. Total de recargas usadas: "
                    f"{len(resultado['recargas_usadas'])}\n"
                )
                break

            f.write(f"v={v} | consumo_antes_recarga={q} | fluxo={val}\n")
            qtd_recargas += 1

        f.write("\nAbsorções nos destinos:\n")
        qtd_absorcoes = 0
        for t, q, val in resultado["absorcoes"]:
            if qtd_absorcoes >= MAX_ABSORCOES_SALVAR:
                f.write("...\n")
                f.write(
                    f"Saída truncada. Total de absorções: "
                    f"{len(resultado['absorcoes'])}\n"
                )
                break

            f.write(f"t={t} | consumo_chegada={q} | fluxo={val}\n")
            qtd_absorcoes += 1

    return caminho


def salvar_resumo(resultados):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    caminho = os.path.join(OUTPUT_DIR, "resumo_cumulativo.csv")

    campos = [
        "instancia",
        "status",
        "objetivo",
        "bound",
        "gap",
        "tempo",
        "r",
        "m",
        "n_vertices",
        "n_arestas",
        "n_arcos_dirigidos",
        "n_var_y",
        "n_var_x",
        "n_var_z",
        "n_var_a",
        "n_conservacao",
        "n_ativacao",
    ]

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        for r in resultados:
            writer.writerow({
                "instancia": r["nome"],
                "status": r["status"],
                "objetivo": r["objetivo"],
                "bound": r["bound"],
                "gap": r["gap"],
                "tempo": f"{r['tempo']:.4f}",
                "r": r["r"],
                "m": r["m"],
                "n_vertices": r["n_vertices"],
                "n_arestas": r["n_arestas"],
                "n_arcos_dirigidos": r["n_arcos_dirigidos"],
                "n_var_y": r["n_var_y"],
                "n_var_x": r["n_var_x"],
                "n_var_z": r["n_var_z"],
                "n_var_a": r["n_var_a"],
                "n_conservacao": r["n_conservacao"],
                "n_ativacao": r["n_ativacao"],
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
            resultado = resolver_cumulativo(instancia)
            resultados.append(resultado)

            caminho_solucao = salvar_solucao(resultado)

            print()
            print(f"Resultado salvo em: {caminho_solucao}")
            print(
                f"{resultado['nome']} | "
                f"status={resultado['status']} | "
                f"obj={resultado['objetivo']} | "
                f"bound={resultado['bound']} | "
                f"gap={resultado['gap']} | "
                f"tempo={resultado['tempo']:.2f}s"
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
                "bound": None,
                "gap": None,
                "estacoes": [],
                "saltos_usados": [],
                "recargas_usadas": [],
                "absorcoes": [],
                "tempo": 0.0,
                "r": None,
                "m": None,
                "n_vertices": None,
                "n_arestas": None,
                "n_arcos_dirigidos": None,
                "n_var_y": None,
                "n_var_x": None,
                "n_var_z": None,
                "n_var_a": None,
                "n_conservacao": None,
                "n_ativacao": None,
            })

    caminho_resumo = salvar_resumo(resultados)

    print()
    print("=" * 70)
    print(f"Resumo salvo em: {caminho_resumo}")


if __name__ == "__main__":
    main()
