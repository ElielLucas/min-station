import csv
import time
import argparse
from pathlib import Path
from collections import defaultdict, deque, Counter

from gurobipy import Model, GRB, quicksum
from ms_utils import (
    ler_instancia,
    construir_adjacencia,
    construir_arcos_alcance,
    RegistSerieTemporal,
)


# =============================================================================
# Utilidades gerais
# =============================================================================

def chave_no(x):
    """Chave estável para ordenar vértices, mesmo se vierem como int/str."""
    return (str(type(x)), str(x))


def pct_reducao(antes, depois):
    if antes == 0:
        return 0.0
    return 100.0 * (antes - depois) / antes


def extrair_vizinho_peso(item):
    """
    Aceita formatos comuns de adjacência:
    - (v, peso)
    - [v, peso]
    - v
    """
    if isinstance(item, (tuple, list)):
        if len(item) >= 2:
            return item[0], item[1]
        if len(item) == 1:
            return item[0], 1
    return item, 1


def construir_adj_undirected_sets(adj):
    """Converte a adjacência ponderada para vizinhança não ponderada."""
    viz = defaultdict(set)
    for u, itens in adj.items():
        viz.setdefault(u, set())
        for item in itens:
            v, _ = extrair_vizinho_peso(item)
            viz[u].add(v)
            viz[v].add(u)
    return viz


def filtrar_adj_por_vertices(adj, vertices_keep):
    """Remove da adjacência ponderada os vértices fora de vertices_keep."""
    keep = set(vertices_keep)
    novo = {v: [] for v in keep}
    for u, itens in adj.items():
        if u not in keep:
            continue
        for item in itens:
            v, w = extrair_vizinho_peso(item)
            if v in keep:
                novo[u].append((v, w))
    return novo


def normalizar_arcos(arcos, vertices):
    """Remove loops, arcos fora de V e duplicatas."""
    V_set = set(vertices)
    vistos = set()
    saida = []
    loops = 0
    fora = 0
    duplicados = 0

    for u, v in arcos:
        if u == v:
            loops += 1
            continue
        if u not in V_set or v not in V_set:
            fora += 1
            continue
        a = (u, v)
        if a in vistos:
            duplicados += 1
            continue
        vistos.add(a)
        saida.append(a)

    return saida, {
        "loops": loops,
        "fora_de_V": fora,
        "duplicados": duplicados,
    }


def montar_sucessores_predecessores(V, arcos):
    succ = {v: set() for v in V}
    pred = {v: set() for v in V}

    for u, v in arcos:
        succ.setdefault(u, set()).add(v)
        pred.setdefault(v, set()).add(u)
        succ.setdefault(v, set())
        pred.setdefault(u, set())

    return succ, pred


def bfs_multi(fontes, adj_succ):
    visitado = set()
    fila = deque()

    for s in fontes:
        if s in adj_succ and s not in visitado:
            visitado.add(s)
            fila.append(s)

    while fila:
        u = fila.popleft()
        for v in adj_succ.get(u, ()):
            if v not in visitado:
                visitado.add(v)
                fila.append(v)

    return visitado


class PreprocessLogger:
    def __init__(self, nome_instancia, R, log_dir=None, ativo=True):
        self.nome_instancia = nome_instancia
        self.R = R
        self.log_dir = Path(log_dir) if log_dir else None
        self.ativo = ativo
        self.linhas = []

    def log(self, msg=""):
        if self.ativo:
            print(msg)
        self.linhas.append(str(msg))

    def sep(self, titulo=None):
        self.log("=" * 80)
        if titulo:
            self.log(titulo)
            self.log("=" * 80)

    def salvar(self):
        if not self.log_dir:
            return None

        self.log_dir.mkdir(parents=True, exist_ok=True)
        nome_seguro = str(self.nome_instancia).replace("/", "_").replace("\\", "_")
        r_seguro = str(self.R).replace(".", "p")
        caminho = self.log_dir / f"{nome_seguro}__R{r_seguro}__preprocess.log"
        caminho.write_text("\n".join(self.linhas) + "\n", encoding="utf-8")
        return caminho


# =============================================================================
# Pré-processamento no grafo original
# =============================================================================

def podar_folhas_sem_terminais(V, adj, S, T, logger):
    """
    Remove iterativamente folhas que não são origens nem destinos.

    Justificativa intuitiva:
    uma ramificação pendente sem terminal não é necessária para conectar S a T.
    Se uma estação dentro dessa ramificação fosse usada apenas para recarga,
    uma estação no ponto de entrada da ramificação é pelo menos tão boa.
    """
    t0 = time.monotonic()

    V_set = set(V)
    terminais = set(S) | set(T)
    viz = construir_adj_undirected_sets(adj)

    grau = {v: len(viz.get(v, set()) & V_set) for v in V_set}
    fila = deque(
        v for v in V_set
        if v not in terminais and grau.get(v, 0) <= 1
    )

    removidos = set()

    while fila:
        v = fila.popleft()
        if v in removidos or v in terminais:
            continue
        if grau.get(v, 0) > 1:
            continue

        removidos.add(v)

        for nb in list(viz.get(v, set())):
            if nb in removidos:
                continue
            if v in viz.get(nb, set()):
                viz[nb].remove(v)
                grau[nb] = max(0, grau.get(nb, 0) - 1)
                if nb not in terminais and grau[nb] <= 1:
                    fila.append(nb)

        grau[v] = 0

    V_novo = [v for v in V if v not in removidos]
    adj_novo = filtrar_adj_por_vertices(adj, V_novo)

    # Diagnóstico de grau 2 remanescente. Não aplicamos contração automaticamente.
    viz_novo = construir_adj_undirected_sets(adj_novo)
    grau2_nao_terminal = sum(
        1
        for v in V_novo
        if v not in terminais and len(viz_novo.get(v, set())) == 2
    )

    t1 = time.monotonic()

    logger.log("[Grafo original]")
    logger.log(
        f"  Poda iterativa de folhas sem terminais: "
        f"|V| {len(V)} -> {len(V_novo)} | removidos={len(removidos)} "
        f"({pct_reducao(len(V), len(V_novo)):.2f}%) | tempo={t1 - t0:.3f}s"
    )
    logger.log(
        f"  Contração de grau 2: não aplicada por segurança "
        f"(estações podem ser instaladas em todos os vértices). "
        f"Vértices grau-2 não terminais remanescentes={grau2_nao_terminal}"
    )

    return V_novo, adj_novo, {
        "grafo_folhas_removidas": len(removidos),
        "grafo_grau2_diag": grau2_nao_terminal,
        "grafo_preprocess_s": t1 - t0,
    }


# =============================================================================
# Pré-processamento no dígrafo de alcance A^R
# =============================================================================

def calcular_RS_RT(V, arcos, S, T):
    succ, pred = montar_sucessores_predecessores(V, arcos)
    RS = bfs_multi(S, succ)
    RT = bfs_multi(T, pred)
    return RS, RT, succ, pred


def remover_candidatos_por_alcance(V, candidatos, RS, RT, logger, label):
    antes = len(candidatos)
    relevantes = RS & RT

    fora_RS = {v for v in candidatos if v not in RS}
    fora_RT = {v for v in candidatos if v not in RT}
    removidos = {v for v in candidatos if v not in relevantes}

    candidatos_novo = set(candidatos) - removidos
    depois = len(candidatos_novo)

    logger.log(
        f"  [{label} | candidatos] "
        f"{antes} -> {depois} | removidos={len(removidos)} "
        f"({pct_reducao(antes, depois):.2f}%) | "
        f"fora_RS={len(fora_RS)} | fora_RT={len(fora_RT)}"
    )

    return candidatos_novo, removidos


def remover_arcos_irrelevantes_por_alcance(arcos, RS, RT, logger, label):
    antes = len(arcos)
    novos = []
    rem_tail = 0
    rem_head = 0
    rem_ambos = 0

    for u, v in arcos:
        ok_tail = u in RS
        ok_head = v in RT

        if ok_tail and ok_head:
            novos.append((u, v))
        else:
            if not ok_tail and not ok_head:
                rem_ambos += 1
            elif not ok_tail:
                rem_tail += 1
            else:
                rem_head += 1

    depois = len(novos)

    logger.log(
        f"  [{label} | arcos irrelevantes] "
        f"{antes} -> {depois} | removidos={antes - depois} "
        f"({pct_reducao(antes, depois):.2f}%) | "
        f"u_fora_RS={rem_tail} | v_fora_RT={rem_head} | ambos={rem_ambos}"
    )

    return novos, {
        "arcos_irrelevantes_removidos": antes - depois,
        "arcos_irrelevantes_u_fora_RS": rem_tail,
        "arcos_irrelevantes_v_fora_RT": rem_head,
        "arcos_irrelevantes_ambos": rem_ambos,
    }


def remover_arcos_forcados_zero(arcos, candidatos, S, T, logger, label):
    """
    Remove arcos cujo fluxo será necessariamente zero pela ativação.

    Com estações permitidas em S e T, NÃO é seguro remover automaticamente:
    - arcos que entram em S;
    - arcos que saem de T.

    A regra correta é:
    - um arco pode sair de u se u é candidato a estação OU u é origem;
    - um arco pode entrar em v se v é candidato a estação OU v é destino.

    Quando todos os vértices estão em candidatos, essa regra normalmente não remove nada
    no início. Ela pode remover arcos depois que algum candidato for eliminado por alcance
    ou dominância.
    """
    S_set = set(S)
    T_set = set(T)
    C = set(candidatos)

    antes = len(arcos)
    novos = []
    rem_saida = 0
    rem_entrada = 0
    rem_ambos = 0

    for u, v in arcos:
        pode_sair = (u in C) or (u in S_set)
        pode_entrar = (v in C) or (v in T_set)

        if pode_sair and pode_entrar:
            novos.append((u, v))
        else:
            if not pode_sair and not pode_entrar:
                rem_ambos += 1
            elif not pode_sair:
                rem_saida += 1
            else:
                rem_entrada += 1

    depois = len(novos)

    logger.log(
        f"  [{label} | arcos forçados a zero] "
        f"{antes} -> {depois} | removidos={antes - depois} "
        f"({pct_reducao(antes, depois):.2f}%) | "
        f"sem_saida_livre/estacao={rem_saida} | "
        f"sem_entrada_livre/estacao={rem_entrada} | ambos={rem_ambos}"
    )

    return novos, {
        "arcos_forcados_zero_removidos": antes - depois,
        "arcos_forcados_zero_saida": rem_saida,
        "arcos_forcados_zero_entrada": rem_entrada,
        "arcos_forcados_zero_ambos": rem_ambos,
    }


def aplicar_dominancia_pred_succ(V, arcos, candidatos, logger, max_candidatos=8000, max_exemplos=10):
    """
    Remove candidato v se existir candidato u que domina v:
        Pred(v) ⊆ Pred(u)
        Succ(v) ⊆ Succ(u)

    Custo unitário: u não é pior que v.

    Em caso de equivalência exata, mantém o representante com menor chave estável.
    """
    t0 = time.monotonic()

    C = set(candidatos)
    n = len(C)

    if n > max_candidatos:
        logger.log(
            f"  [Dominância Pred/Succ] pulada: candidatos={n} > "
            f"limite={max_candidatos}. Ajuste --max-dominance-candidates se quiser rodar."
        )
        return C, set(), {
            "dominancia_pulada": True,
            "dominancia_removidos": 0,
            "dominancia_pares_testados": 0,
            "dominancia_s": 0.0,
        }

    succ, pred = montar_sucessores_predecessores(V, arcos)
    lista = sorted(C, key=chave_no)

    pred_c = {v: pred.get(v, set()) for v in lista}
    succ_c = {v: succ.get(v, set()) for v in lista}

    removidos = set()
    exemplos = []
    pares_testados = 0
    pares_dominantes = 0

    # Candidatos organizados por tamanho de vizinhança para reduzir testes.
    for v in lista:
        if v in removidos:
            continue

        Pv = pred_c[v]
        Sv = succ_c[v]
        chave_v = chave_no(v)

        for u in lista:
            if u == v or u in removidos:
                continue

            Pu = pred_c[u]
            Su = succ_c[u]

            if len(Pu) < len(Pv) or len(Su) < len(Sv):
                continue

            # Empate: se são equivalentes, só o menor representante domina.
            if len(Pu) == len(Pv) and len(Su) == len(Sv) and chave_no(u) > chave_v:
                continue

            pares_testados += 1

            if Pv.issubset(Pu) and Sv.issubset(Su):
                pares_dominantes += 1
                removidos.add(v)
                if len(exemplos) < max_exemplos:
                    exemplos.append((v, u, len(Pv), len(Pu), len(Sv), len(Su)))
                break

    C_novo = C - removidos
    t1 = time.monotonic()

    logger.log(
        f"  [Dominância Pred/Succ] "
        f"{len(C)} -> {len(C_novo)} | removidos={len(removidos)} "
        f"({pct_reducao(len(C), len(C_novo)):.2f}%) | "
        f"pares_testados={pares_testados} | pares_dominantes={pares_dominantes} | "
        f"tempo={t1 - t0:.3f}s"
    )

    if exemplos:
        logger.log("    Exemplos de dominância:")
        for v, u, pv, pu, sv, su in exemplos:
            logger.log(
                f"      v={v} dominado por u={u} | "
                f"|Pred(v)|={pv}, |Pred(u)|={pu}, "
                f"|Succ(v)|={sv}, |Succ(u)|={su}"
            )

    return C_novo, removidos, {
        "dominancia_pulada": False,
        "dominancia_removidos": len(removidos),
        "dominancia_pares_testados": pares_testados,
        "dominancia_pares_dominantes": pares_dominantes,
        "dominancia_s": t1 - t0,
    }


# =============================================================================
# Diagnósticos estruturais. Não removem nada.
# =============================================================================

def diagnosticar_equivalencia_pred_succ(V, arcos, candidatos, logger):
    t0 = time.monotonic()
    succ, pred = montar_sucessores_predecessores(V, arcos)

    classes = defaultdict(list)
    for v in candidatos:
        assinatura = (frozenset(pred.get(v, set())), frozenset(succ.get(v, set())))
        classes[assinatura].append(v)

    tamanhos = [len(vals) for vals in classes.values() if len(vals) > 1]
    qtd_classes = len(tamanhos)
    candidatos_em_classes = sum(tamanhos)
    maior = max(tamanhos) if tamanhos else 0
    t1 = time.monotonic()

    logger.log(
        f"[Diagnóstico | equivalência Pred/Succ] "
        f"classes_nao_unitarias={qtd_classes} | "
        f"candidatos_em_classes={candidatos_em_classes} | "
        f"maior_classe={maior} | tempo={t1 - t0:.3f}s"
    )

    return {
        "diag_eq_classes": qtd_classes,
        "diag_eq_candidatos": candidatos_em_classes,
        "diag_eq_maior_classe": maior,
        "diag_eq_s": t1 - t0,
    }


def diagnosticar_quase_dominancia(V, arcos, candidatos, logger, max_candidatos=2500):
    t0 = time.monotonic()
    C = sorted(set(candidatos), key=chave_no)
    n = len(C)

    if n > max_candidatos:
        logger.log(
            f"[Diagnóstico | quase-dominância] pulado: candidatos={n} > "
            f"limite={max_candidatos}. Ajuste --diag-quase-dom-max-candidatos se quiser rodar."
        )
        return {
            "diag_qdom_pulado": True,
            "diag_qdom_90": "",
            "diag_qdom_95": "",
            "diag_qdom_99": "",
            "diag_qdom_s": 0.0,
        }

    succ, pred = montar_sucessores_predecessores(V, arcos)
    pred_c = {v: pred.get(v, set()) for v in C}
    succ_c = {v: succ.get(v, set()) for v in C}

    cont = {0.90: 0, 0.95: 0, 0.99: 0}
    pares = 0

    for i, v in enumerate(C):
        Pv = pred_c[v]
        Sv = succ_c[v]
        denom_p = max(1, len(Pv))
        denom_s = max(1, len(Sv))

        for u in C:
            if u == v:
                continue

            Pu = pred_c[u]
            Su = succ_c[u]

            # Só consideramos u como candidato a "quase dominador" se ele tiver
            # pelo menos tantas possibilidades locais quanto v.
            if len(Pu) < len(Pv) or len(Su) < len(Sv):
                continue

            pares += 1

            cov_p = len(Pv & Pu) / denom_p
            cov_s = len(Sv & Su) / denom_s
            cov = min(cov_p, cov_s)

            for thr in cont:
                if cov >= thr:
                    cont[thr] += 1

    t1 = time.monotonic()

    logger.log(
        f"[Diagnóstico | quase-dominância] "
        f"pares_avaliados={pares} | >=90%={cont[0.90]} | "
        f">=95%={cont[0.95]} | >=99%={cont[0.99]} | tempo={t1 - t0:.3f}s"
    )

    return {
        "diag_qdom_pulado": False,
        "diag_qdom_90": cont[0.90],
        "diag_qdom_95": cont[0.95],
        "diag_qdom_99": cont[0.99],
        "diag_qdom_s": t1 - t0,
    }


def calcular_bits_alcance(fontes, adj_succ, V):
    bits = {v: 0 for v in V}

    for idx, s in enumerate(fontes):
        if s not in adj_succ:
            continue

        bit = 1 << idx
        visitado = set([s])
        fila = deque([s])

        while fila:
            u = fila.popleft()
            bits[u] |= bit
            for v in adj_succ.get(u, ()):
                if v not in visitado:
                    visitado.add(v)
                    fila.append(v)

    return bits


def diagnosticar_assinatura_global_orig_dest(V, arcos, candidatos, S, T, logger, max_terminais_total=2048):
    t0 = time.monotonic()

    total_terminais = len(S) + len(T)
    if total_terminais > max_terminais_total:
        logger.log(
            f"[Diagnóstico | assinatura global Orig/Dest] pulado: "
            f"|S|+|T|={total_terminais} > limite={max_terminais_total}. "
            f"Ajuste --diag-global-max-terminais se quiser rodar."
        )
        return {
            "diag_global_pulado": True,
            "diag_global_classes": "",
            "diag_global_candidatos": "",
            "diag_global_maior_classe": "",
            "diag_global_s": 0.0,
        }

    succ, pred = montar_sucessores_predecessores(V, arcos)

    orig_bits = calcular_bits_alcance(list(S), succ, V)
    dest_bits = calcular_bits_alcance(list(T), pred, V)

    classes = defaultdict(list)
    for v in candidatos:
        classes[(orig_bits.get(v, 0), dest_bits.get(v, 0))].append(v)

    tamanhos = [len(vals) for vals in classes.values() if len(vals) > 1]
    qtd_classes = len(tamanhos)
    candidatos_em_classes = sum(tamanhos)
    maior = max(tamanhos) if tamanhos else 0
    t1 = time.monotonic()

    logger.log(
        f"[Diagnóstico | assinatura global Orig/Dest] "
        f"classes_nao_unitarias={qtd_classes} | "
        f"candidatos_em_classes={candidatos_em_classes} | "
        f"maior_classe={maior} | tempo={t1 - t0:.3f}s"
    )

    return {
        "diag_global_pulado": False,
        "diag_global_classes": qtd_classes,
        "diag_global_candidatos": candidatos_em_classes,
        "diag_global_maior_classe": maior,
        "diag_global_s": t1 - t0,
    }


def preprocessar_instancia(
    nome_instancia,
    S,
    T,
    V,
    adj,
    R,
    logger,
    aplicar_preprocess=True,
    max_iters=10,
    max_dominance_candidates=8000,
    diag_quase_dom_max_candidatos=2500,
    diag_global_max_terminais=2048,
):
    t_pre0 = time.monotonic()
    stats = {}

    logger.sep(f"PREPROCESSAMENTO | {nome_instancia} | R={R}")

    V0 = list(V)
    adj0 = adj
    candidatos0 = set(V0)

    M_base0 = sum(len(adj0.get(u, [])) for u in adj0)

    logger.log(
        f"[Inicial] |V|={len(V0)} | |S|={len(S)} | |T|={len(T)} | "
        f"candidatos_iniciais={len(candidatos0)} | M_base={M_base0}"
    )
    logger.log(
        "[Observação] Estações permitidas em todos os vértices, inclusive origens e destinos."
    )
    logger.log(
        "[Observação] Por isso, arcos entrando em S ou saindo de T NÃO são removidos automaticamente."
    )

    if not aplicar_preprocess:
        A_bruto = construir_arcos_alcance(V0, adj0, R)
        A, norm = normalizar_arcos(A_bruto, V0)
        stats.update({
            "preprocess_aplicado": False,
            "preprocess_iteracoes": 0,
            "N_nodes_pre": len(V0),
            "M_base_pre": M_base0,
            "A_R_bruto": len(A),
            "A_R_final": len(A),
            "candidatos_bruto": len(candidatos0),
            "candidatos_final": len(candidatos0),
            "candidatos_removidos_alcance": 0,
            "candidatos_removidos_dominancia": 0,
            "arcos_removidos_irrelevantes": 0,
            "arcos_removidos_forcados_zero": 0,
            "grafo_folhas_removidas": 0,
            "grafo_grau2_diag": "",
            "preprocess_s": time.monotonic() - t_pre0,
        })
        return V0, adj0, A, candidatos0, stats

    # 1) Grafo original: poda de ramos pendentes sem terminais.
    V1, adj1, st_grafo = podar_folhas_sem_terminais(V0, adj0, S, T, logger)
    stats.update(st_grafo)

    candidatos = set(V1)

    # 2) Construção de A^R.
    t_ar0 = time.monotonic()
    A_bruto = construir_arcos_alcance(V1, adj1, R)
    A, norm = normalizar_arcos(A_bruto, V1)
    t_ar1 = time.monotonic()

    logger.log("[Construção A^R]")
    logger.log(
        f"  A^R bruto normalizado: {len(A)} | "
        f"loops_descartados={norm['loops']} | fora_de_V={norm['fora_de_V']} | "
        f"duplicados={norm['duplicados']} | tempo={t_ar1 - t_ar0:.3f}s"
    )

    stats.update({
        "preprocess_aplicado": True,
        "N_nodes_pre": len(V1),
        "M_base_pre": sum(len(adj1.get(u, [])) for u in adj1),
        "A_R_bruto": len(A),
        "candidatos_bruto": len(candidatos),
        "candidatos_removidos_alcance": 0,
        "candidatos_removidos_dominancia": 0,
        "arcos_removidos_irrelevantes": 0,
        "arcos_removidos_forcados_zero": 0,
        "A_R_loops_descartados": norm["loops"],
        "A_R_duplicados_descartados": norm["duplicados"],
    })

    # 3) Regra geral de arcos forçados a zero.
    A, st_zero_ini = remover_arcos_forcados_zero(
        A, candidatos, S, T, logger, "Inicial"
    )
    stats["arcos_removidos_forcados_zero"] += st_zero_ini["arcos_forcados_zero_removidos"]

    # 4) Iterações: alcance -> arcos irrelevantes -> dominância -> arcos forçados.
    iteracoes = 0

    for it in range(1, max_iters + 1):
        iteracoes = it
        logger.log("")
        logger.log(f"[Iteração {it}]")

        cand_inicio = len(candidatos)
        arcos_inicio = len(A)

        t_it0 = time.monotonic()

        RS, RT, _, _ = calcular_RS_RT(V1, A, S, T)

        candidatos, rem_alc = remover_candidatos_por_alcance(
            V1, candidatos, RS, RT, logger, f"Iteração {it} - Alcance"
        )
        stats["candidatos_removidos_alcance"] += len(rem_alc)

        A, st_arcos = remover_arcos_irrelevantes_por_alcance(
            A, RS, RT, logger, f"Iteração {it} - Alcance"
        )
        stats["arcos_removidos_irrelevantes"] += st_arcos["arcos_irrelevantes_removidos"]

        A, st_zero = remover_arcos_forcados_zero(
            A, candidatos, S, T, logger, f"Iteração {it} - pós-alcance"
        )
        stats["arcos_removidos_forcados_zero"] += st_zero["arcos_forcados_zero_removidos"]

        candidatos, rem_dom, st_dom = aplicar_dominancia_pred_succ(
            V1,
            A,
            candidatos,
            logger,
            max_candidatos=max_dominance_candidates,
        )
        stats["candidatos_removidos_dominancia"] += len(rem_dom)

        A, st_zero2 = remover_arcos_forcados_zero(
            A, candidatos, S, T, logger, f"Iteração {it} - pós-dominância"
        )
        stats["arcos_removidos_forcados_zero"] += st_zero2["arcos_forcados_zero_removidos"]

        # Uma nova filtragem de alcance após dominância fica naturalmente para a próxima iteração.
        t_it1 = time.monotonic()

        cand_fim = len(candidatos)
        arcos_fim = len(A)

        logger.log(
            f"  [Resumo iteração {it}] "
            f"candidatos {cand_inicio} -> {cand_fim} | "
            f"A^R {arcos_inicio} -> {arcos_fim} | "
            f"tempo={t_it1 - t_it0:.3f}s"
        )

        if cand_inicio == cand_fim and arcos_inicio == arcos_fim:
            logger.log(f"  [Estabilização] Nenhuma redução na iteração {it}.")
            break

    # 5) Diagnósticos finais. Não removem nada.
    logger.log("")
    logger.log("[Diagnósticos finais sem remoção]")
    st_eq = diagnosticar_equivalencia_pred_succ(V1, A, candidatos, logger)
    st_qdom = diagnosticar_quase_dominancia(
        V1, A, candidatos, logger, max_candidatos=diag_quase_dom_max_candidatos
    )
    st_global = diagnosticar_assinatura_global_orig_dest(
        V1, A, candidatos, S, T, logger, max_terminais_total=diag_global_max_terminais
    )

    stats.update(st_eq)
    stats.update(st_qdom)
    stats.update(st_global)

    t_pre1 = time.monotonic()

    stats.update({
        "preprocess_iteracoes": iteracoes,
        "A_R_final": len(A),
        "candidatos_final": len(candidatos),
        "candidatos_removidos_total": stats["candidatos_bruto"] - len(candidatos),
        "A_R_removidos_total": stats["A_R_bruto"] - len(A),
        "preprocess_s": t_pre1 - t_pre0,
    })

    logger.log("")
    logger.log("[Resumo final do pré-processamento]")
    logger.log(
        f"  |V| original -> pré: {len(V0)} -> {len(V1)} | "
        f"removidos_grafo={len(V0) - len(V1)}"
    )
    logger.log(
        f"  candidatos: {stats['candidatos_bruto']} -> {len(candidatos)} | "
        f"removidos={stats['candidatos_removidos_total']} "
        f"({pct_reducao(stats['candidatos_bruto'], len(candidatos)):.2f}%)"
    )
    logger.log(
        f"  A^R: {stats['A_R_bruto']} -> {len(A)} | "
        f"removidos={stats['A_R_removidos_total']} "
        f"({pct_reducao(stats['A_R_bruto'], len(A)):.2f}%)"
    )
    logger.log(f"  tempo_total_preprocessamento={stats['preprocess_s']:.3f}s")

    return V1, adj1, A, candidatos, stats


# =============================================================================
# Modelo PLI
# =============================================================================

def construir_modelo_baseline(S, T, V, arcos, candidatos_estacao=None, custos_estacao=None):
    S = list(S)
    T = list(T)
    V = list(V)

    S_set = set(S)
    T_set = set(T)
    V_set = set(V)

    if candidatos_estacao is None:
        candidatos_estacao = set(V)
    else:
        candidatos_estacao = set(candidatos_estacao)

    if len(S) != len(T):
        raise ValueError(
            f"MIN-STATION exige |S| = |T|. Recebido |S|={len(S)} e |T|={len(T)}."
        )

    faltando_S = S_set - V_set
    faltando_T = T_set - V_set

    if faltando_S:
        raise ValueError(f"Há origens fora de V: {sorted(faltando_S)}")

    if faltando_T:
        raise ValueError(f"Há destinos fora de V: {sorted(faltando_T)}")

    candidatos_fora = candidatos_estacao - V_set
    if candidatos_fora:
        raise ValueError(f"Há candidatos fora de V: {sorted(candidatos_fora)}")

    A = [(u, v) for (u, v) in arcos if u in V_set and v in V_set and u != v]

    arcos_entrada = {n: [] for n in V}
    arcos_saida = {n: [] for n in V}

    for u, v in A:
        arcos_saida[u].append((u, v))
        arcos_entrada[v].append((u, v))

    m = len(S)

    if custos_estacao is None:
        custos_estacao = {v: 1.0 for v in candidatos_estacao}
    else:
        for v in candidatos_estacao:
            custos_estacao.setdefault(v, 1.0)

    modelo = Model("MIN-STATION-DAS-PREPROCESS")

    y = {
        v: modelo.addVar(vtype=GRB.BINARY, name=f"y[{v}]")
        for v in candidatos_estacao
    }

    f = {
        (u, v): modelo.addVar(lb=0.0, vtype=GRB.INTEGER, name=f"f[{u},{v}]")
        for (u, v) in A
    }

    modelo.setObjective(
        quicksum(custos_estacao[v] * y[v] for v in candidatos_estacao),
        GRB.MINIMIZE,
    )

    for v in V:
        entrada_v = quicksum(f[a] for a in arcos_entrada.get(v, []))
        saida_v = quicksum(f[a] for a in arcos_saida.get(v, []))

        balanco = (1 if v in S_set else 0) - (1 if v in T_set else 0)

        modelo.addConstr(
            saida_v - entrada_v == balanco,
            name=f"balanco[{v}]",
        )

        entrada_livre = 1 if v in T_set else 0
        saida_livre = 1 if v in S_set else 0

        if v in candidatos_estacao:
            yv = y[v]

            modelo.addConstr(
                entrada_v <= entrada_livre + (m - entrada_livre) * yv,
                name=f"ativa_entrada[{v}]",
            )

            modelo.addConstr(
                saida_v <= saida_livre + (m - saida_livre) * yv,
                name=f"ativa_saida[{v}]",
            )
        else:
            modelo.addConstr(
                entrada_v <= entrada_livre,
                name=f"ativa_entrada_fix0[{v}]",
            )

            modelo.addConstr(
                saida_v <= saida_livre,
                name=f"ativa_saida_fix0[{v}]",
            )

    modelo.update()
    return modelo, y, f, len(A), len(candidatos_estacao)


# =============================================================================
# Execução
# =============================================================================

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
    aplicar_preprocess=True,
    preprocess_log_dir="preprocess_logs",
    max_preprocess_iters=10,
    max_dominance_candidates=8000,
    diag_quase_dom_max_candidatos=2500,
    diag_global_max_terminais=2048,
):
    t0 = time.monotonic()

    logger_pre = PreprocessLogger(
        nome_instancia=nome_instancia,
        R=R,
        log_dir=preprocess_log_dir,
        ativo=True,
    )

    V_pre, adj_pre, A, candidatos_estacao, prep_stats = preprocessar_instancia(
        nome_instancia=nome_instancia,
        S=S,
        T=T,
        V=V,
        adj=adj,
        R=R,
        logger=logger_pre,
        aplicar_preprocess=aplicar_preprocess,
        max_iters=max_preprocess_iters,
        max_dominance_candidates=max_dominance_candidates,
        diag_quase_dom_max_candidatos=diag_quase_dom_max_candidatos,
        diag_global_max_terminais=diag_global_max_terminais,
    )

    caminho_log_pre = logger_pre.salvar()
    if caminho_log_pre:
        print(f"Log de pré-processamento salvo em: {caminho_log_pre}")

    modelo, y, f, tam_AR, tam_candidatos = construir_modelo_baseline(
        S=S,
        T=T,
        V=V_pre,
        arcos=A,
        candidatos_estacao=candidatos_estacao,
    )

    modelo.Params.TimeLimit = tempo_limite_s

    logger = RegistSerieTemporal(
        nome_instancia,
        R,
        pasta_plots,
        intervalo_amostra=plot_amostra_s,
        suffix="",
        titulo_tag="BASE_DAS_PREPROCESS",
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
    tempo_total = t1 - t0
    tempo_solver = tempo_total - float(prep_stats.get("preprocess_s", 0.0))

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
    n_cons = 3 * len(V_pre)

    try:
        nos_busca_final = int(getattr(modelo, "NodeCount", 0))

        logger.talvez_adicionar(
            tempo_total,
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

        "N_nodes_original": len(V),
        "M_base_original": sum(len(adj[u]) for u in adj),
        "VI_original": len(VI),

        "N_nodes_pre": len(V_pre),
        "M_base_pre": prep_stats.get("M_base_pre", ""),
        "A_R_bruto": prep_stats.get("A_R_bruto", tam_AR),
        "A_R_final": tam_AR,

        "m": len(S),
        "candidatos_bruto": prep_stats.get("candidatos_bruto", len(V)),
        "candidatos_final": tam_candidatos,

        "grafo_folhas_removidas": prep_stats.get("grafo_folhas_removidas", 0),
        "grafo_grau2_diag": prep_stats.get("grafo_grau2_diag", ""),

        "candidatos_removidos_alcance": prep_stats.get("candidatos_removidos_alcance", 0),
        "candidatos_removidos_dominancia": prep_stats.get("candidatos_removidos_dominancia", 0),
        "candidatos_removidos_total": prep_stats.get("candidatos_removidos_total", 0),

        "arcos_removidos_irrelevantes": prep_stats.get("arcos_removidos_irrelevantes", 0),
        "arcos_removidos_forcados_zero": prep_stats.get("arcos_removidos_forcados_zero", 0),
        "A_R_removidos_total": prep_stats.get("A_R_removidos_total", 0),

        "preprocess_iteracoes": prep_stats.get("preprocess_iteracoes", 0),
        "preprocess_s": prep_stats.get("preprocess_s", 0.0),
        "solver_s": tempo_solver,

        "diag_eq_classes": prep_stats.get("diag_eq_classes", ""),
        "diag_eq_candidatos": prep_stats.get("diag_eq_candidatos", ""),
        "diag_eq_maior_classe": prep_stats.get("diag_eq_maior_classe", ""),

        "diag_qdom_90": prep_stats.get("diag_qdom_90", ""),
        "diag_qdom_95": prep_stats.get("diag_qdom_95", ""),
        "diag_qdom_99": prep_stats.get("diag_qdom_99", ""),

        "diag_global_classes": prep_stats.get("diag_global_classes", ""),
        "diag_global_candidatos": prep_stats.get("diag_global_candidatos", ""),
        "diag_global_maior_classe": prep_stats.get("diag_global_maior_classe", ""),

        "vars": n_vars,
        "cons": n_cons,
        "status": status,
        "solcount": solcount,
        "LI": LI,
        "LS": LS,
        "gap": gap,
        "runtime_s": tempo_total,
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
    aplicar_preprocess,
    preprocess_log_dir,
    max_preprocess_iters,
    max_dominance_candidates,
    diag_quase_dom_max_candidatos,
    diag_global_max_terminais,
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
        aplicar_preprocess=aplicar_preprocess,
        preprocess_log_dir=preprocess_log_dir,
        max_preprocess_iters=max_preprocess_iters,
        max_dominance_candidates=max_dominance_candidates,
        diag_quase_dom_max_candidatos=diag_quase_dom_max_candidatos,
        diag_global_max_terminais=diag_global_max_terminais,
    )

    return [linha]


CSV_HEADER = [
    "instance",
    "R",

    "N_nodes_original",
    "M_base_original",
    "VI_original",

    "N_nodes_pre",
    "M_base_pre",
    "A_R_bruto",
    "A_R_final",

    "m",
    "candidatos_bruto",
    "candidatos_final",

    "grafo_folhas_removidas",
    "grafo_grau2_diag",

    "candidatos_removidos_alcance",
    "candidatos_removidos_dominancia",
    "candidatos_removidos_total",

    "arcos_removidos_irrelevantes",
    "arcos_removidos_forcados_zero",
    "A_R_removidos_total",

    "preprocess_iteracoes",
    "preprocess_s",
    "solver_s",

    "diag_eq_classes",
    "diag_eq_candidatos",
    "diag_eq_maior_classe",

    "diag_qdom_90",
    "diag_qdom_95",
    "diag_qdom_99",

    "diag_global_classes",
    "diag_global_candidatos",
    "diag_global_maior_classe",

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

    caminho_csv.parent.mkdir(parents=True, exist_ok=True) if caminho_csv.parent != Path(".") else None

    with caminho_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)

        if primeira:
            w.writeheader()

        for r in linhas:
            w.writerow({k: r.get(k, "") for k in CSV_HEADER})


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Solver MIN-STATION original de Das sobre dígrafo de alcance, "
            "com pré-processamento iterativo e logs detalhados."
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
        default="results_min_station_das_preprocess.csv",
        help="CSV de saída append. Padrão: results_min_station_das_preprocess.csv",
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

    ap.add_argument(
        "--sem-preprocess",
        action="store_true",
        help="Desativa o pré-processamento e roda a formulação diretamente.",
    )

    ap.add_argument(
        "--preprocess-log-dir",
        type=str,
        default="preprocess_logs",
        help="Pasta para salvar logs detalhados de pré-processamento. Padrão: preprocess_logs.",
    )

    ap.add_argument(
        "--max-preprocess-iters",
        type=int,
        default=10,
        help="Número máximo de iterações do pré-processamento. Padrão: 10.",
    )

    ap.add_argument(
        "--max-dominance-candidates",
        type=int,
        default=8000,
        help=(
            "Limite de candidatos para rodar dominância Pred/Succ exata. "
            "Acima disso, a etapa é pulada para evitar custo quadrático. Padrão: 8000."
        ),
    )

    ap.add_argument(
        "--diag-quase-dom-max-candidatos",
        type=int,
        default=2500,
        help=(
            "Limite de candidatos para diagnóstico de quase-dominância. "
            "Acima disso, o diagnóstico é pulado. Padrão: 2500."
        ),
    )

    ap.add_argument(
        "--diag-global-max-terminais",
        type=int,
        default=2048,
        help=(
            "Limite para |S|+|T| no diagnóstico de assinatura global Orig/Dest. "
            "Acima disso, o diagnóstico é pulado. Padrão: 2048."
        ),
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
            aplicar_preprocess=not args.sem_preprocess,
            preprocess_log_dir=args.preprocess_log_dir,
            max_preprocess_iters=args.max_preprocess_iters,
            max_dominance_candidates=args.max_dominance_candidates,
            diag_quase_dom_max_candidatos=args.diag_quase_dom_max_candidatos,
            diag_global_max_terminais=args.diag_global_max_terminais,
        )

        write_csv(linhas, caminho_csv)
        total += len(linhas)

    print(f"\n[ok] {total} linha(s) salvas em {caminho_csv}")


if __name__ == "__main__":
    main()