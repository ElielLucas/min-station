# AS25 — Piloto LP pareado FC-R versus COMP+K — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** T1–T4 implementadas e testadas; campanha Gurobi real (T5), relatório com resultados e revisão independente (T6) pendentes. **Branch de referência:** `novos_testes`. **Pré-condição:** AS24 `VALIDATED_WITH_MINOR_FINDINGS` e política FC-R congelada antes da campanha; não reutilizar grafos reservados.

## Problem Statement

Medir de forma preregistrada a contribuição marginal de FC-R em seis grafos de desenvolvimento com quatro braços e análise separada de regiões unitárias e maiores.

## Goals

- [x] Instrumentar para medir de forma preregistrada a contribuição marginal de FC-R em seis grafos de desenvolvimento com quatro braços e análise separada de regiões unitárias e maiores.
- [x] Implementar gate e evidências rastreáveis: `GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.

## Out of Scope

| Item | Razão |
|---|---|
| Atribuir ganho à testemunha sintética | Ela não constitui benchmark. |
| Rodar MIP | AS26 exige gate LP positivo e autorização. |
| Alterar K/C6/C8 | Comparabilidade com AS16–AS22 exige baseline intacto. |
| Generalização para os grafos reservados | AS27 posterior. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Comparadores | `COMP`, `COMP+K`, `COMP+FC-R`, `COMP+K+FC-R` em 6 grafos fixos | Isola efeito principal e marginal de FC-R. | Sim; congelada no AS25 JSON antes da campanha |
| Tempo | 90 s totais por braço incluindo preparação, separação e reotimização | Conserva interpretação do custo real das campanhas anteriores. | Sim; congelada no AS25 JSON antes da campanha |
| Ablacão | Usar quatro braços no piloto principal (24 registros) e executar a ablação singleton versus singleton+regiões maiores como rodada separada, com mesmo orçamento, policy ID e resultado próprio | Quantifica cobertura e contribuição extra das regiões maiores sem manipular orçamento. | Sim; congelada no AS25 JSON antes da campanha |
| Gate | Ganho ≥1% em ≥2 grafos brutos independentes e razão custo ≤2×, com censuras preservadas | Critério prospectivo do Astra, sujeito a revisão antes da primeira execução. | Sim; congelada no AS25 JSON antes da campanha |

**Open questions: none.** Política técnica congelada em `as25-preregistro-fcr-lp.json`; revisão independente continua sendo um gate obrigatório posterior, não uma decisão de parâmetros pendente.

## User Stories

### P1: Execução reproduzível

**User Story:** Como pesquisador, quero comparar LP FC-R em bases idênticas para evitar confusão experimental.

**Acceptance Criteria**

1. WHEN o runner iniciar THEN the sistema SHALL validar os seis IDs, hashes e origem bruta dos casos de desenvolvimento conforme preregistro.
2. WHEN cada caso for executado THEN the sistema SHALL produzir os quatro braços previstos e contabilizar 90 s totais por braço.
3. IF algum braço exceder o orçamento THEN the sistema SHALL persistir status censurado e métricas disponíveis sem inventar valor ótimo.

**Independent Test:** Dry run 24 braços com IDs/hashes, censura simulada e saída em diretório inédito.

### P1: Medir ganho marginal correto

**User Story:** Como pesquisador, quero avaliar se FC-R realmente melhora o limite para distinguir fluxo alterado de bound maior.

**Acceptance Criteria**

1. WHEN os dois LPs de uma comparação terminarem ótimos THEN the analisador SHALL calcular ganho absoluto e relativo do limite objetivo e razão de custo total.
2. WHEN não houver violação em todos os singletons THEN the analisador SHALL declarar ausência de violação apenas para essa subfamília no ponto testado.
3. WHEN um corte apenas modificar fluxos sem elevar o objetivo THEN the analisador SHALL classificar o caso como ganho LP zero.

**Independent Test:** Casos artificiais de bound invariável e de variação de flow com objetivo constante.

### P2: Decidir continuidade

**User Story:** Como pesquisador, quero obter gate científico auditável para não começar MIP prematuramente.

**Acceptance Criteria**

1. WHEN a campanha completa for analisada THEN the sistema SHALL contar grafos brutos independentes com ganho ≥1% e custo ≤2×.
2. IF não houver pares comparáveis suficientes THEN the sistema SHALL produzir `INVESTIGATE` com censuras explícitas, sem `GO` automático.
3. IF o gate técnico for satisfeito THEN the sistema SHALL produzir no máximo `GO_CANDIDATE_REVIEW`, exigindo decisão científica humana antes da AS26.

**Independent Test:** Gerar análise a partir de outputs congelados, sem redescobrir parâmetros pós-hoc.

## Edge Cases

- IF houver erro, censura ou evidência incompleta THEN the sistema SHALL registrar a razão e não atribuir resultado positivo à fase.
- IF a pré-condição não estiver satisfeita THEN the sistema SHALL bloquear a execução de AS25.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR25-01 | Execução reproduzível | T1 — plano congelado | Implemented; LP pending |
| FCR25-02 | Execução reproduzível | T2 — runner e dry-run | Implemented; LP pending |
| FCR25-03 | Execução reproduzível | T2 — timeout e censura | Implemented; LP pending |
| FCR25-04 | Medir ganho marginal correto | T4 — analisador | Implemented; LP pending |
| FCR25-05 | Medir ganho marginal correto | T3 — separador/ablação | Implemented; LP pending |
| FCR25-06 | Medir ganho marginal correto | T4 — flow-only | Implemented; LP pending |
| FCR25-07 | Decidir continuidade | T4 — raw graph ids | Implemented; LP pending |
| FCR25-08 | Decidir continuidade | T4 — censura | Implemented; LP pending |
| FCR25-09 | Decidir continuidade | T4 — gate review-only | Implemented; LP pending |

**Coverage:** 9 requisitos rastreáveis; código/testes das T1–T4 implementados; T5–T6 pendentes de Gurobi e revisão independente.

## Success Criteria

- [x] 24 linhas esperadas em dry-run, seis casos por quatro braços.
- [x] Instrumentação de números LP, tempo total e métricas por fase para os JSON; execução real pendente.
- [x] Gate reproduzível por script sem promoção automática a MIP.

## Dependências e gate

`GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.
