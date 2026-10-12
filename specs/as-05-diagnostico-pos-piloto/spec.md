# AS05-DIAG — Diagnóstico de cortes K, censura e agrupamento — Specification

**Status:** implementação preparada, testes locais; **campanha diagnóstica Gurobi ainda não executada**  
**Prioridade:** P1 (investigação após `INVESTIGATE`)  
**Dependências:** AS-00 (benchmark), AS-02 (modelos), AS-03 (partições), AS-04 (comparador), AS-05 (piloto exploratório já executado)  
**Local:** `specs/as-05-diagnostico-pos-piloto/`

## Problem Statement

A execução exploratória AS-05 retornou `INVESTIGATE`. Quatro casos pareados não mostram ganho LP A2 material; `puc-w3c571-seed-r1` não concluiu a preparação dos cortes em 90 s; `vienna-I056-regiao-f4` teve A2 censurado. Além disso, o braço U pagava a preparação de K embora não o utilize. Precisamos identificar os custos reais e testar políticas determinísticas predefinidas, sem alterar o piloto original e sem vazar dados de avaliação.

## Goals

- [ ] Instrumentar geração e validação dos cortes K: vizinhanças, C1, C2, C4-DM, canonização e validação.
- [ ] Evitar reconstruções redundantes de N+/N− na validação, conservando exatamente os cortes e o verificador.
- [ ] Medir U sem preparar K; medir U+K e A2+K com K integralmente dentro de cada orçamento.
- [ ] Reensaiar os dois casos censurados em rodada **diagnóstica separada**, com teto de 300 s por braço.
- [ ] Comparar em quatro casos de desenvolvimento três políticas A2: `reachability_degree`, `balanced` e `reachability_overlap` (nova, somente exploratória) sob 90 s por braço.
- [ ] Emitir perfis, deltas, tempos e síntese com hashes, censuras e checkpoints retomáveis, **sem promover AS-06**.

## Out of Scope

| Item | Motivo |
|---|---|
| Alterar `results/benchmark/as05-pilot-owner-exploratory-001/` | Resultados originais congelados, inclusive censuras. |
| Executar casos de avaliação AS-00 | Evitar vazamento e seleção adaptativa. |
| Executar ou declarar revisão matemática independente | Continua pendente no protocolo científico. |
| Escolher automaticamente política ótima para campanha de avaliação | Seria escolha pós-observação sem novo pré-registro. |
| Implementar novas formulações B/C ou AS-06 | Fases distintas. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Orçamento diagnóstico nos censurados | 300 s por braço | Separa sondagem da campanha original de 90 s | Plano congelado antes da nova execução |
| Orçamento políticas no desenvolvimento | 90 s por braço | Pareabilidade interna com AS-05 | Plano congelado antes da nova execução |
| Preparação compartilhada de K entre braços | **Não**; +K paga K próprio; U não paga K | Evita dupla contagem e custo espúrio em U | Verificar por teste |
| Número de casos agrupamento | 4 completos na AS-05 | Hipótese exploratória pós-piloto, sem promoção | Seleção registrada por hash antes do solve |
| Classificação final | `POSTHOC_DIAGNOSTIC_DEVELOPMENT_ONLY` | Separar descoberta de confirmação | Fixa no esquema |

**Open questions: none** — novos diagnósticos exigem novo plano se as condições mudarem.

## User Stories

### P1: Diagnóstico reproduzível e auditável

**User Story:** Como pesquisador, quero identificar gargalos e limitações da formulação A de maneira reproduzível, sem perder as evidências do primeiro piloto.

**Acceptance Criteria:**

1. **AS05D-01 — Integridade:** WHEN um plano diagnóstico é criado THEN ele SHALL vincular os hashes do manifesto, relatório e plano AS-05 original e SHALL recusar alterações após o congelamento.
2. **AS05D-02 — Cortes:** WHEN K é calculado THEN o sistema SHALL medir C1/C2/C4-DM, canonização e validação separadamente, reutilizar N+/N− e preservar o hash do K legado.
3. **AS05D-03 — Ablação U:** WHEN U é executado THEN SHALL omitir totalmente a geração de K no braço e SHALL medir seu tempo total separadamente, com referência de K proveniente do U_K comparado.
4. **AS05D-04 — Casos censurados:** WHEN são reensaiados os dois casos originalmente censurados THEN SHALL executar U/U_K/A2_K sob supervisão de 300 s por braço, preservando censuras e objetivos ausentes.
5. **AS05D-05 — Agrupamento:** WHEN o diagnóstico de políticas roda THEN SHALL comparar A2 de `reachability_degree`, `balanced` e `reachability_overlap` com U_K no mesmo caso, seed e configuração; SHALL derivar grupos sem observar LP.
6. **AS05D-06 — Retomada:** IF a execução for interrompida THEN SHALL permitir `--resume` a partir de checkpoints inteiros e íntegros por braço, sem sobrescrever resultados anteriores nem aceitar artefatos adulterados.
7. **AS05D-07 — Análise:** WHEN os três estágios terminam THEN SHALL gerar JSON, CSV e Markdown com deltas, custos e censuras, sem inferir valor LP de timeouts nem autorizar automaticamente promoção científica.
8. **AS05D-08 — Independência:** IF existem hashes diferentes de K, instância, estrutura ou política do solver THEN SHALL recusar o contraste; resultados com K inválido não serão considerados completos.

**Independent Test:** K reproduzido com mesmo SHA; corte inválido rejeitado; U sem `prepare_K`; hashes divergentes rejeitados; partições independentes da ordem das entradas; checkpoint adulterado recusado; testes end-to-end com runners artificiais; análise exploratória sem `GO`.

## Edge Cases

- Timeout em `k_c1`, `k_c2`, `k_c4_dm` ou `k_validation_cached` classificado como `TIMEOUT_PREPARATION`, não `TIMEOUT_SOLVER`.
- Ausência de Gurobi registrada como erro/abstenção, sem inventar objetivo LP.
- Resultado LP de solver interrompido nunca é tratado como ótimo numérico.
- Se as duas instâncias censuradas persistirem, análise permanece inconclusiva para esses contrastes; linha não desaparece.
- Se novo hash de K diferir do original, recusar comparação; não corrigir os dados silenciosamente.
- Caso sem dois grupos não é elegível à política A2.

## Requirement Traceability

| Requirement ID | Teste derivado | Fase | Status |
|---|---|---|---|
| AS05D-01 | `test_plan_is_bound_to_original_report` | Teste unitário | PASS local |
| AS05D-02 | `test_k_cached_has_exact_legacy_hash` | Teste unitário | PASS local |
| AS05D-03 | `test_u_never_calls_k` | Teste unitário | PASS local |
| AS05D-04 | `test_censored_and_grouping_full_pipeline` | Integração mock | PASS local; Gurobi pendente |
| AS05D-05 | `test_preselected_policies_are_deterministic` | Teste unitário | PASS local |
| AS05D-06 | `test_resume_uses_existing_checkpoints_without_repeat` | Integração mock | PASS local |
| AS05D-07 | `test_complete_analysis_exploratory_no_promotion` | Integração mock | PASS local |
| AS05D-08 | `test_different_k_hash_refuses_pair` | Teste unitário | PASS local |

## Success Criteria

- [x] As políticas e os budgets estão congelados num plano adicional; AS-00 e AS-05 não são alterados.
- [x] Código independente do adaptador AS-04 original, com testes negativos e manifesto próprio.
- [x] Checkpoints com SHA por braço, execução append-only e consolidação verificável.
- [ ] Executar diagnósticos reais Gurobi e validar manifestos/resultados.
- [ ] Revisão independente de código/evidência para conclusão científica.

## Tests Derived from Acceptance Criteria

- **AS05D-01:** Mutação de orçamento, origem ou SHA rejeitada.
- **AS05D-02:** Cortes e SHA coincidem com `prepare_K` original; verificador inválido falha.
- **AS05D-03:** Mock de `_timed_k` que lança exceção não é chamado por U.
- **AS05D-04:** Dois casos e três braços são mantidos; resultado interrompido sem LP.
- **AS05D-05:** Três políticas determinísticas e independentes de solver.
- **AS05D-06:** Interrupção retoma apenas slots faltantes; hash alterado impede retomada.
- **AS05D-07:** Os três estágios são exigidos para produzir análise; relatório continua exploratório.
- **AS05D-08:** Hash distinto entre U_K/A2_K invalida contraste.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entradas | SHA do piloto e manifesto; plano idêntico ao prospectivo criado; casos permitidos enumerados. |
| Falhas e parciais | Abstenções explícitas, deadline global por braço com spawn, sem LP fictício. |
| Retry e idempotência | Checkpoints por braço; `--resume` somente com hashes; saída final imutável. |
| Concorrência | FC-01 por processo isolado, execução serial reproduzível. |
| Observabilidade | C1/C2/C4-DM, validação, solver, tempo por braço, variável e SHA. |
| Auth | N/A: CLI científica offline; resultados exploratórios autorizados pelo proprietário. |
| Estados | PROFILED / OPTIMAL_NUMERIC / TIMEOUT_PREPARATION / TIMEOUT_SOLVER / NOT_COMPARABLE. |
