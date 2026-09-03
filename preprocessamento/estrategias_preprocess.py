"""Executa subconjuntos controlados das regras de pré-processamento.

Este módulo não duplica as implementações das regras. Ele apenas orquestra as
funções já existentes em ``modelo_min_station_das_preprocess`` para permitir um
experimento de ablação: folhas, alcance e dominância podem ser avaliados
separadamente.
"""

import time

from ms_utils import construir_arcos_alcance

from .modelo_min_station_das_preprocess import (
    aplicar_dominancia_pred_succ,
    calcular_RS_RT,
    diagnosticar_assinatura_global_orig_dest,
    diagnosticar_equivalencia_pred_succ,
    diagnosticar_quase_dominancia,
    normalizar_arcos,
    pct_reducao,
    podar_folhas_sem_terminais,
    preprocessar_instancia,
    remover_arcos_forcados_zero,
    remover_arcos_irrelevantes_por_alcance,
    remover_candidatos_por_alcance,
)


SEM_PREPROCESSAMENTO = "sem_preprocessamento"
SOMENTE_FOLHAS = "somente_folhas"
SOMENTE_ALCANCE = "somente_alcance"
SOMENTE_DOMINANCIA = "somente_dominancia"
PREPROCESSAMENTO_COMPLETO = "com_preprocessamento"

ESTRATEGIAS_ISOLADAS = (
    SOMENTE_FOLHAS,
    SOMENTE_ALCANCE,
    SOMENTE_DOMINANCIA,
)

ESTRATEGIAS_TODAS = (
    SEM_PREPROCESSAMENTO,
    *ESTRATEGIAS_ISOLADAS,
    PREPROCESSAMENTO_COMPLETO,
)

CONFIGURACOES = {
    SEM_PREPROCESSAMENTO: {
        "folhas": False,
        "alcance": False,
        "dominancia": False,
    },
    SOMENTE_FOLHAS: {
        "folhas": True,
        "alcance": False,
        "dominancia": False,
    },
    SOMENTE_ALCANCE: {
        "folhas": False,
        "alcance": True,
        "dominancia": False,
    },
    SOMENTE_DOMINANCIA: {
        "folhas": False,
        "alcance": False,
        "dominancia": True,
    },
    PREPROCESSAMENTO_COMPLETO: {
        "folhas": True,
        "alcance": True,
        "dominancia": True,
    },
}


def configuracao_estrategia(estrategia: str) -> dict:
    try:
        return dict(CONFIGURACOES[estrategia])
    except KeyError as error:
        permitidas = ", ".join(ESTRATEGIAS_TODAS)
        raise ValueError(
            f"Estratégia desconhecida: {estrategia}. Use uma de: {permitidas}"
        ) from error


def _stats_diagnosticos_vazios() -> dict:
    return {
        "diag_eq_classes": "",
        "diag_eq_candidatos": "",
        "diag_eq_maior_classe": "",
        "diag_qdom_90": "",
        "diag_qdom_95": "",
        "diag_qdom_99": "",
        "diag_global_classes": "",
        "diag_global_candidatos": "",
        "diag_global_maior_classe": "",
    }


def preprocessar_instancia_estrategia(
    *,
    estrategia,
    nome_instancia,
    S,
    T,
    V,
    adj,
    R,
    logger,
    max_iters=10,
    max_dominance_candidates=8000,
    executar_diagnosticos=False,
    diag_quase_dom_max_candidatos=2500,
    diag_global_max_terminais=2048,
):
    """Aplica exatamente a estratégia indicada e retorna a interface original.

    ``sem_preprocessamento`` e ``com_preprocessamento`` são delegados à função
    original. Assim, se forem solicitados, continuam reproduzindo os dois
    tratamentos usados no experimento anterior.
    """
    config = configuracao_estrategia(estrategia)

    if estrategia in (SEM_PREPROCESSAMENTO, PREPROCESSAMENTO_COMPLETO):
        resultado = preprocessar_instancia(
            nome_instancia=nome_instancia,
            S=S,
            T=T,
            V=V,
            adj=adj,
            R=R,
            logger=logger,
            aplicar_preprocess=estrategia == PREPROCESSAMENTO_COMPLETO,
            max_iters=max_iters,
            max_dominance_candidates=max_dominance_candidates,
            diag_quase_dom_max_candidatos=(
                diag_quase_dom_max_candidatos if executar_diagnosticos else 0
            ),
            diag_global_max_terminais=(
                diag_global_max_terminais if executar_diagnosticos else 0
            ),
        )
        resultado[-1].update(
            {
                "preprocess_strategy": estrategia,
                "usa_folhas": config["folhas"],
                "usa_alcance": config["alcance"],
                "usa_dominancia": config["dominancia"],
            }
        )
        return resultado

    if max_iters < 1:
        raise ValueError("max_iters deve ser pelo menos 1")

    t_pre0 = time.monotonic()
    V0 = list(V)
    adj0 = adj
    M_base0 = sum(len(adj0.get(u, [])) for u in adj0)

    logger.sep(
        f"PREPROCESSAMENTO ISOLADO | {nome_instancia} | "
        f"R={R} | {estrategia}"
    )
    logger.log(
        f"[Estratégia] folhas={config['folhas']} | "
        f"alcance={config['alcance']} | dominância={config['dominancia']}"
    )
    logger.log(
        f"[Inicial] |V|={len(V0)} | |S|={len(S)} | |T|={len(T)} | "
        f"candidatos_iniciais={len(V0)} | M_base={M_base0}"
    )

    if config["folhas"]:
        V1, adj1, st_grafo = podar_folhas_sem_terminais(
            V0, adj0, S, T, logger
        )
    else:
        V1 = V0
        adj1 = adj0
        st_grafo = {
            "grafo_folhas_removidas": 0,
            "grafo_grau2_diag": "",
            "grafo_preprocess_s": 0.0,
        }
        logger.log("[Grafo original] Poda de folhas não aplicada.")

    candidatos = set(V1)

    t_ar0 = time.monotonic()
    A_bruto = construir_arcos_alcance(V1, adj1, R)
    A, norm = normalizar_arcos(A_bruto, V1)
    t_ar1 = time.monotonic()

    logger.log("[Construção A^R]")
    logger.log(
        f"  A^R bruto normalizado: {len(A)} | "
        f"loops_descartados={norm['loops']} | "
        f"fora_de_V={norm['fora_de_V']} | "
        f"duplicados={norm['duplicados']} | tempo={t_ar1 - t_ar0:.3f}s"
    )

    stats = {
        "preprocess_aplicado": True,
        "preprocess_strategy": estrategia,
        "usa_folhas": config["folhas"],
        "usa_alcance": config["alcance"],
        "usa_dominancia": config["dominancia"],
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
        **st_grafo,
        **_stats_diagnosticos_vazios(),
    }

    iteracoes = 0
    if config["alcance"] or config["dominancia"]:
        for it in range(1, max_iters + 1):
            iteracoes = it
            cand_inicio = len(candidatos)
            arcos_inicio = len(A)
            t_it0 = time.monotonic()

            logger.log("")
            logger.log(f"[Iteração {it}]")

            if config["alcance"]:
                RS, RT, _, _ = calcular_RS_RT(V1, A, S, T)
                candidatos, rem_alc = remover_candidatos_por_alcance(
                    V1,
                    candidatos,
                    RS,
                    RT,
                    logger,
                    f"Iteração {it} - Alcance",
                )
                stats["candidatos_removidos_alcance"] += len(rem_alc)

                A, st_arcos = remover_arcos_irrelevantes_por_alcance(
                    A, RS, RT, logger, f"Iteração {it} - Alcance"
                )
                stats["arcos_removidos_irrelevantes"] += st_arcos[
                    "arcos_irrelevantes_removidos"
                ]

                A, st_zero = remover_arcos_forcados_zero(
                    A,
                    candidatos,
                    S,
                    T,
                    logger,
                    f"Iteração {it} - pós-alcance",
                )
                stats["arcos_removidos_forcados_zero"] += st_zero[
                    "arcos_forcados_zero_removidos"
                ]

            if config["dominancia"]:
                candidatos, rem_dom, _ = aplicar_dominancia_pred_succ(
                    V1,
                    A,
                    candidatos,
                    logger,
                    max_candidatos=max_dominance_candidates,
                )
                stats["candidatos_removidos_dominancia"] += len(rem_dom)

                A, st_zero = remover_arcos_forcados_zero(
                    A,
                    candidatos,
                    S,
                    T,
                    logger,
                    f"Iteração {it} - pós-dominância",
                )
                stats["arcos_removidos_forcados_zero"] += st_zero[
                    "arcos_forcados_zero_removidos"
                ]

            cand_fim = len(candidatos)
            arcos_fim = len(A)
            logger.log(
                f"  [Resumo iteração {it}] candidatos {cand_inicio} -> "
                f"{cand_fim} | A^R {arcos_inicio} -> {arcos_fim} | "
                f"tempo={time.monotonic() - t_it0:.3f}s"
            )

            if cand_inicio == cand_fim and arcos_inicio == arcos_fim:
                logger.log(
                    f"  [Estabilização] Nenhuma redução na iteração {it}."
                )
                break

    if executar_diagnosticos:
        logger.log("")
        logger.log("[Diagnósticos finais sem remoção]")
        stats.update(
            diagnosticar_equivalencia_pred_succ(
                V1, A, candidatos, logger
            )
        )
        stats.update(
            diagnosticar_quase_dominancia(
                V1,
                A,
                candidatos,
                logger,
                max_candidatos=diag_quase_dom_max_candidatos,
            )
        )
        stats.update(
            diagnosticar_assinatura_global_orig_dest(
                V1,
                A,
                candidatos,
                S,
                T,
                logger,
                max_terminais_total=diag_global_max_terminais,
            )
        )

    stats.update(
        {
            "preprocess_iteracoes": iteracoes,
            "A_R_final": len(A),
            "candidatos_final": len(candidatos),
            "candidatos_removidos_total": (
                stats["candidatos_bruto"] - len(candidatos)
            ),
            "A_R_removidos_total": stats["A_R_bruto"] - len(A),
            "preprocess_s": time.monotonic() - t_pre0,
        }
    )

    logger.log("")
    logger.log("[Resumo final do pré-processamento isolado]")
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
