# AS25.1 — Diagnóstico e otimização da separação FC-R — Specification

**Referências:** `specs/as-25-fcr-lp-pareado/` (campanha AS25), `docs/technical/plans/execucao/plano-fcr-as23-as27.md`, `docs/technical/reference/experimentos/as251-diagnostico-fcr.md` (diagnóstico). **Branch:** `novos_testes`. **Estado:** diagnóstico concluído; implementação e testes concluídos; campanha AS25.1 pré-registrada e **não executada**. **Pré-condição:** resultados AS25 (`results/benchmark/as25-fcr-lp-001`, `as25-fcr-ablation-001`) preservados sem alteração.

## Problem Statement

A AS25 terminou em `INVESTIGATE`: ganhos LP de FC-R sobre COMP+K pequenos (0,025%–0,417%) e custo de parede de 2,3× a 15,4× COMP+K. O diagnóstico mostrou que o custo vinha sobretudo de bookkeeping evitável (revalidação de `H` por região) e que a diferença da ablação MAPF é efeito de truncamento por rodadas, não defeito. A AS25.1 corrige o custo sem mudar as desigualdades e mede, em campanha nova e pré-registrada, se a política otimizada muda a decisão científica.

## Problemas comprovados (evidência do diagnóstico)

| ID | Problema | Evidência | Tipo |
|---|---|---|---|
| D1 | `choose_regions` chama `region_excess` por candidato, que chama `_graph` e revalida todos os arcos de `H`: O(\|V\|·\|A\| + \|A\|²) | cProfile MAPF: 12.822 chamadas a `_graph`, 99% do tempo do índice; `index-as25-vs-as251.json`: MAPF 28,2 s vs 0,12 s, CC3 170,2 s vs 0,35 s, planos idênticos | Complexidade algorítmica |
| D2 | `construct_row` revalida `H` e refaz a fronteira em O(\|A\|) por corte emitido | CC3: separação 0,8 s/rodada com 27 cortes (27.000 arcos) | Recomputação |
| D3 | Fronteiras de região são recalculadas a cada rodada, embora estáticas | Código `fcr_lp_policy.py:57-70` | Recomputação |
| D4 | Diferença MAPF 13,280 vs 13,2551 vem de truncamento por `max_rounds=6` em trajetórias não aninhadas | Sem teto de rodadas, ambas as políticas convergem para 13,280000 (16 e 37 rodadas) | Efeito esperado, não bug |
| D5 | Regiões maiores consomem rodadas sem ganho no fecho | Fecho singleton = fecho singleton+12 maiores em CC9 (27,082111) e MAPF (13,280000) | Seleção |
| D6 | Fecho da família declarada < 1% em CC9 (0,205%), MAPF (0,606%) e CC3 (0,000%); ≥ 1% só em BIP42 (+1,172% após 40 rodadas; 1% exige 13 rodadas, 2.506 linhas e 79 s de laço) | Diagnóstico de fecho, `results/benchmark/as251-diagnostico-001` | Limite da família, não da política |

## Goals

- [x] Reduzir o custo de preparação e separação FC-R sem alterar nenhuma linha emitida para a mesma sequência de pontos LP.
- [x] Adotar uma regra de seleção sustentada por medição, documentando as alternativas rejeitadas.
- [x] Pré-registrar campanha AS25.1 com braços que separam efeito de infraestrutura e efeito de seleção.
- [ ] Executar a campanha AS25.1 e classificar o resultado em A/B/C/D (pendente; execução no checkout do pesquisador após commit).

## Out of Scope

| Item | Razão |
|---|---|
| Novas famílias de cortes ou novas regiões | Restrição explícita da tarefa. |
| MIP / AS26 | Exige gate LP positivo e aprovação humana. |
| Alterar COMP, K, `fcr_rows.py`, `fcr_regions.py`, `fcr_separator.py`, `fcr_lp_policy.py`, runner AS25 | Código auditado da AS24/AS25 e comparabilidade histórica. |
| Alterar parâmetros Gurobi ou orçamento de 90 s | Comparabilidade com AS25. |
| Mudar gate AS25 retroativamente | Pré-registro histórico. |
| Grafos reservados (AS27) | Avaliação independente posterior. |
| Remover a censura de Vienna I056 e PUC W3C571 | Censura já em COMP/COMP+K; independe de FC-R. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Ordenação dos cortes | Manter ordem lexicográfica das regiões (AS25) | `deficit` melhorou CC9 (+0,005 p.p.), empatou MAPF e CC3 e piorou BIP42 (0,025% → 0,0007%) no orçamento AS25; sinal inconsistente | Sim, por evidência de diagnóstico |
| Regiões maiores | `larger_mode='escalate'`: examinar as 12 regiões maiores só quando nenhum singleton novo violar | D4/D5; MAPF 0,417% → 0,606% no mesmo orçamento; CC9/BIP42 iguais | Sim, por evidência de diagnóstico |
| Auditoria canônica por corte | Desligada na campanha; equivalência garantida por testes e por comparação de assinaturas entre braços AS25 e INFRA | Reativar custaria O(\|A\|) por corte (D2) | Sim |
| Instâncias de calibração | Mesmas seis de desenvolvimento da AS25 | Regra do projeto; calibração e confirmação no mesmo conjunto não generalizam (AS27) | Sim |
| Campanha real | Não executada nesta entrega | Proveniência exige commit limpo, e o projeto proíbe commit automático | Sim |
| Commits por tarefa (TLC) | Não realizados | `CLAUDE.md`: só commitar com pedido explícito; mensagem sugerida entregue | Sim |

**Open questions:** none — decisões registradas acima.

## User Stories

### P1: Separação equivalente e mais barata ⭐ MVP

**User Story:** Como pesquisador, quero o mesmo separador FC-R com custo menor, para que o custo medido reflita a família de cortes e não o bookkeeping.

**Why P1:** D1–D3 dominam o custo da AS25.

**Acceptance Criteria:**

1. The `fast_region_plan` SHALL return a `RegionPlan` equal to `choose_regions` for the same instance, `max_larger` and `include_larger`.
2. The `FastIndexedFCR` SHALL emit, for every examined region `L` and chosen `Q`, a row equal (direção, `L`, `Q`, demanda, termos, rhs) to `construct_row(instance, L, Q, direction)`.
3. WHEN `selection='lexicographic'` and `larger_mode='always'` THEN `FastIndexedFCR.separate` SHALL return the same cut signatures, row terms and counters (`examined`, `violated`, `emitted`, `capped`, `duplicates`, `singletons_checked`, `larger_checked`) as `IndexedFCR.separate` for the same point.
4. The `FastIndexedFCR` SHALL choose, for each examined `L`, a `Q` whose left-hand side equals the minimum over all subsets of the eligible frontier (exhaustive enumeration), in both directions.
5. WHEN `separate` is called repeatedly on the same index with different points THEN each result SHALL equal the result of a freshly built index on that point.
6. IF the time limit expires before all singletons are examined THEN the separator SHALL report `PARTIAL_SINGLETONS` and `singleton_complete=False`.
7. IF the cut cap is reached THEN the separator SHALL report `CUT_CAP_REACHED` with `capped > 0` and keep `global_region_separation=False`.

**Independent Test:** Comparar `FastIndexedFCR` com AS24/AS25 na testemunha AS23 e em microinstâncias aleatórias com `S∩T`, `r=2`, saldo regional 2 e circulações.

### P1: Seleção singleton-primeiro ⭐ MVP

**User Story:** Como pesquisador, quero que as regiões maiores não consumam rodadas enquanto singletons ainda violam, porque o diagnóstico mostrou que isso só atrasa o ganho.

**Why P1:** D4/D5.

**Acceptance Criteria:**

1. WHERE `larger_mode='escalate'`, WHEN at least one new singleton row is violated THEN the separator SHALL examine no larger region and SHALL report `larger_deferred=True`.
2. WHERE `larger_mode='escalate'`, WHEN no new singleton row is violated THEN the separator SHALL examine every selected larger region.
3. WHERE `larger_mode='escalate'`, WHEN larger regions are deferred and the cap is not reached THEN the separator SHALL report status `COMPLETE_SINGLETONS_LARGER_DEFERRED`.
4. IF a violated row's signature is in `exclude_signatures` THEN the separator SHALL mark it `DUPLICATE` and SHALL not emit it.
5. WHEN a row's deficit is less than or equal to `tolerance` THEN the separator SHALL classify it `NO_VIOLATION_IN_FIXED_REGION`.

**Independent Test:** Pontos construídos com e sem violação singleton na testemunha AS23.

### P2: Diagnóstico reprodutível

**User Story:** Como pesquisador, quero reproduzir os números do diagnóstico, para não depender de logs efêmeros.

**Acceptance Criteria:**

1. WHEN the diagnostic script runs in `index` mode THEN it SHALL record AS25 and AS25.1 index build time and plan equality per case.
2. WHEN the diagnostic script runs in `trace` mode THEN it SHALL record LP objective, violated, emitted, nnz, separation, insertion and reoptimization time per round.
3. The diagnostic outputs SHALL carry `evidence_class='DIAGNOSTIC_POST_HOC'` and SHALL not enter any gate.

### P2: Campanha AS25.1 pré-registrada

**User Story:** Como pesquisador, quero separar o efeito de infraestrutura do efeito da seleção, para atribuir corretamente qualquer mudança.

**Acceptance Criteria:**

1. WHEN the runner starts THEN it SHALL reject a plan whose cases, hashes, solver parameters, 90 s budget, FC-R policy, arms or gate differ from the frozen AS25.1 plan.
2. The runner SHALL execute arms `U_K`, `U_K_FCR_AS25`, `U_K_FCR_INFRA`, `U_K_FCR_AS251` per case, each in its own process with a 90 s total wall budget.
3. The runner SHALL record per round: LP objective, rows added, nnz added, cut signature digest, separation, insertion and reoptimization time.
4. IF an arm exceeds its budget THEN the runner SHALL persist a censored status without an LP objective.
5. IF the output directory exists THEN the runner SHALL refuse to write.

### P2: Análise e decisão

**User Story:** Como pesquisador, quero uma classificação A/B/C/D fixada antes da execução.

**Acceptance Criteria:**

1. The analyzer SHALL evaluate the unchanged AS25 gate (≥1% LP gain over `U_K` in ≥2 independent raw graphs, cost ≤2×) on arm `U_K_FCR_AS251`.
2. The analyzer SHALL mark `infra_equivalent=True` for a case only WHEN `U_K_FCR_INFRA` and `U_K_FCR_AS25` are both OPTIMAL with identical per-round signature digests.
3. The analyzer SHALL classify the outcome as A, B, C or D using the rule frozen in the preregistration.
4. WHEN a paired comparison has added rows but objective gain ≤ 1e-7 THEN the analyzer SHALL flag it `flow_only_zero_bound_gain` and SHALL count zero gain.
5. The analyzer SHALL report `mip_automatically_authorized=False`.

## Edge Cases

- IF `selection` or `larger_mode` is unknown THEN the constructor SHALL raise `ValueError`.
- IF `y` or `f` uses a vertex or arc outside `H` THEN `separate` SHALL raise `ValueError`.
- WHEN a vertex is in `S∩T` THEN it SHALL not generate a singleton region and SHALL stay exempt from `Q` in the corresponding direction.
- WHEN `r > 1` THEN frontiers SHALL use arcs of `H`, not physical edges.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR251-01 | P1 Separação: plano igual | T1 | Implemented |
| FCR251-02 | P1 Separação: linha canônica | T1 | Implemented |
| FCR251-03 | P1 Separação: igualdade com AS25 | T1 | Implemented |
| FCR251-04 | P1 Separação: Q exato | T1 | Implemented |
| FCR251-05 | P1 Separação: cache | T1 | Implemented |
| FCR251-06 | P1 Separação: tempo parcial | T1 | Implemented |
| FCR251-07 | P1 Separação: teto | T1 | Implemented |
| FCR251-08 | P1 Seleção: adiamento | T2 | Implemented |
| FCR251-09 | P1 Seleção: escalonamento | T2 | Implemented |
| FCR251-10 | P1 Seleção: status | T2 | Implemented |
| FCR251-11 | P1 Seleção: duplicatas | T2 | Implemented |
| FCR251-12 | P1 Seleção: tolerância | T2 | Implemented |
| FCR251-13 | P2 Diagnóstico: índice | T3 | Implemented |
| FCR251-14 | P2 Diagnóstico: trajetória | T3 | Implemented |
| FCR251-15 | P2 Diagnóstico: rótulo | T3 | Implemented |
| FCR251-16 | P2 Campanha: plano congelado | T4, T5 | Implemented |
| FCR251-17 | P2 Campanha: braços | T5 | Implemented |
| FCR251-18 | P2 Campanha: registro por rodada | T5 | Implemented |
| FCR251-19 | P2 Campanha: censura | T5 | Implemented |
| FCR251-20 | P2 Campanha: append-only | T5 | Implemented |
| FCR251-21 | P2 Análise: gate AS25 | T6 | Implemented |
| FCR251-22 | P2 Análise: equivalência INFRA | T6 | Implemented |
| FCR251-23 | P2 Análise: A/B/C/D | T6 | Implemented |
| FCR251-24 | P2 Análise: flow-only | T6 | Implemented |
| FCR251-25 | P2 Análise: sem MIP | T6 | Implemented |

**Coverage:** 25 requisitos, 25 mapeados para tarefas.

## Success Criteria

- [x] Planos e linhas idênticos aos da AS24/AS25 em todos os testes de equivalência.
- [x] Índice AS25.1 ≥ 10× mais rápido que o AS25 nos quatro casos com LP ótimo (medido: 65× a 492×).
- [ ] Campanha AS25.1 executada e classificada (pendente).
