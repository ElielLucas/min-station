# AS06 — Piloto MIP pareado: COMP versus COMP+K — Specification

**Status:** IMPLEMENTAÇÃO LOCAL CONCLUÍDA · Gurobi real e revisão independente pendentes.  
**Prioridade:** P5 exploratória após AS-05.  
**Dependências:** AS-04 implementada; AS-05 LP fatorial íntegra (exploratória, gate científico pendente).  
**Local:** `specs/as-06-piloto-mip-pareado/`.

## Problem Statement

A melhoria LP de COMP+K não prova melhoria de gap MIP/tempo. Executar campanha pareada e auditável de resolução inteira sem prosseguir na busca de A2/A4. Manter COMP+K como referência experimental, não como candidato homologado.

## Goals

- [x] Infraestrutura de **seis pares** U (COMP) × U_K (COMP+K), seed 42, 300 s de wall total por braço.
- [x] A4_K apenas secundário em três casos predefinidos pelos resultados exploratórios AS05.
- [x] Medir gap MIP por UB física validada contra LB numérica do solver; curvas e custos, inclusive censura.
- [x] Gate que impede replicação automática quando não existe benefício em duas fontes independentes.
- [x] Implementar preparação condicional de 600 s, seeds 42/43/44 e mesmos seis pares.
- [ ] Rodar MIP real em ambiente Gurobi e obter evidência do gate.
- [ ] Verificação independente autor ≠ revisor; nenhuma homologação assumida.

## Out of Scope

- Campanha final 3600 s, instâncias de avaliação, seleção por instância e ajustes pós-hoc.
- Alterar o solver histórico, K, modelos AS-02/AS-05 ou resultados congelados.
- Criar heurísticas de warm start, formulações B/C ou certificado racional.

## Assumptions & Open Questions

| Decisão | Default | Justificativa | Confirmado? |
|---|---|---|---|
| Piloto principal | 6 casos × (U,U_K), 300 s, seed 42 | Isola ganho inteiro de K | Sim, implementado; execução pendente |
| Secundário | A4_K em MAPF, PUC w3c571, Vienna | Hipóteses exploratórias LP AS05 | Sim, sem promoção |
| Solver | Gurobi 4 threads; sem warm start; MIPGap=1e-4 | Mesma configuração por par | Implementado, execução real pendente |
| K | C1+C2+C4-DM, validador bitset-v2 | Preservar identidade e custo | Implementado |
| Replicação | 600 s; seeds 42,43,44; U/U_K nos 6 casos | Apenas após gate GO | Implementado, bloqueado até evidência |
| Benefício | ≥2 p.p. absolutos **ou** ≥25% relativos de redução do gap | Adendo AS06 exploratório | Implementado; não é AS00 |
| Não inferioridade | Nenhuma regressão de gap >1 p.p.; dois grafos e duas fontes | Evitar melhoria isolada | Implementado |

**Open questions: none** — não existem parâmetros pendentes para o piloto exploratório; validade científica independente continua pendente.

## User Stories

**User Story:** Como pesquisador, quero verificar se cortes K melhoram a busca MIP sob o mesmo wall total e com solução física comprovada.

### Acceptance Criteria

1. **AS06-01 — Pares:** WHEN o piloto roda THEN SHALL registrar U e U_K no mesmo caso/seed, e A4_K só nos três casos exploratórios predefinidos.
2. **AS06-02 — Orçamento:** WHEN um worker executa THEN SHALL pagar carregamento, alcance, K, build, solve e validação no único deadline 300/600 s; censura preservada.
3. **AS06-03 — Repetição:** IF o gate 300 s é GO THEN SHALL permitir plano imutável de 600 s com seeds 42,43,44 e seis pares; caso contrário SHALL recusar criação.
4. **AS06-04 — Evolução:** WHEN Gurobi oferece callbacks THEN SHALL registrar LB e incumbentes numéricos sem substituí-los por UB física; eventos ausentes permanecem ausentes, junto a nós/Work/tempos.
5. **AS06-05 — Validade física:** IF uma solução de estações é capturada THEN SHALL verificar no grafo original com oracle independente, rejeitar UB inválida e impedir gap fictício.
6. **AS06-06 — Promoção:** WHEN a análise é construída THEN SHALL exigir evidência comparável em pelo menos duas fontes e dois grafos independentes, sem regressões severas, preservando PENDING científico.
7. **AS06-07 — Negativo:** IF houver censura, ausência de UB ou falta de benefício THEN SHALL manter os seis casos, declarar INCONCLUSIVE/STOP e não abrir AS11 automaticamente.
8. **AS06-08 — Integridade:** WHEN checkpoint/relatório/análise é retomado ou verificado THEN SHALL conferir plano congelado, hashes, slots e vínculos fonte; shall rejeitar alteração/corrupção.

## Edge Cases

Gurobi indisponível, NO_INCUMBENT, falha física, callback perdido, K interrompido, build de A4 grande, memória, prazo vencido em validação e 1 fonte apenas. Numéricos não são certificados racionais. Eventual cardinalidade de S∩T preservada pelo validador físico existente.

## Requirement Traceability

| Requisito | Testes/evidência | Implementação |
|---|---|---|
| AS06-01 | fixed_slots_and_sources, full_campaign_integrity | `as06_mip.py`, `as06_reporting.py` |
| AS06-02 | budget_timeout_never_fabricates_bounds | `fc_budget.py` reutilizado |
| AS06-03 | replication_without_gate_refused; full_campaign_integrity_and_analysis | `make_plan`, `verify_analysis` |
| AS06-04 | testes de trace, verificador de valores finitos; Gurobi real pendente | `_solve_mip` |
| AS06-05 | invalid_incumbent_rejected; --audit-physical | `physical_trace`, `validate_physical_ub` |
| AS06-06 | gap_gate_requires_two_families | `stage_gate` |
| AS06-07 | gap_no_ub_not_zero, missing_solver_not_marked_optimal | `pair_result`, `validate_run` |
| AS06-08 | checkpoint_mutation, analysis_tamper | `verify_campaign`, `verify_analysis` |

## Success Criteria

- [x] Código e testes locais derivados de ACs.
- [x] Checkpoint e relatório append-only, sem reescrever AS-05.
- [x] Smoke MIP HiGHS pequeno prova integridade de compilação binária.
- [ ] Execução real com Gurobi e validação física dos incumbentes do piloto.
- [ ] Parecer matemático/código autor ≠ verificador; gate independente antes de homologação.

## Tests Derived from Acceptance Criteria

Os testes estão em `experiments/formulation-comparison/test_as06_mip.py`; a suíte não substitui a execução real nem a revisão independente.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entradas | Hash de AS05, plano, split, política, instance SHA, K SHA |
| Falhas/parciais | NO_INCUMBENT, timeouts, erro, validação falha permanecem no denominador |
| Idempotência | Checkpoints com sidecar SHA, resume íntegro, append-only |
| Concorrência | Worker spawn por braço e budget próprio; sem compartilhamento oculto |
| Ciclo dos dados | Report/CSV/manifest e análise vinculada ao relatório |
| Observabilidade | Wall fases, Work, nodes, peak RSS, callback MIP, gaps físicos |
| Estado / transições | screening 300 → gate GO → replication 600, ou STOP/INCONCLUSIVE |
| Auth | N/A, scripts locais |
