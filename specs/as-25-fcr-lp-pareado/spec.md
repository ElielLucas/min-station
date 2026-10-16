# AS25 — Piloto LP pareado FC-R versus COMP+K — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** somente planejado, não implementado nem validado. **Branch de referência:** `novos_testes`. **Pré-condição:** AS24 `VALIDATED` e política FC-R congelada antes da campanha; não reutilizar grafos reservados.

## Problem Statement

Medir de forma preregistrada a contribuição marginal de FC-R em seis grafos de desenvolvimento com quatro braços e análise separada de regiões unitárias e maiores.

## Goals

- [ ] Medir de forma preregistrada a contribuição marginal de FC-R em seis grafos de desenvolvimento com quatro braços e análise separada de regiões unitárias e maiores.
- [ ] Gate e evidências rastreáveis: `GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.

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
| Comparadores | `COMP`, `COMP+K`, `COMP+FC-R`, `COMP+K+FC-R` em 6 grafos fixos | Isola efeito principal e marginal de FC-R. | Não; premissa de planejamento |
| Tempo | 90 s totais por braço incluindo preparação, separação e reotimização | Conserva interpretação do custo real das campanhas anteriores. | Não; premissa de planejamento |
| Ablacão | Usar quatro braços no piloto principal (24 registros) e executar a ablação singleton versus singleton+regiões maiores como rodada separada, com mesmo orçamento, policy ID e resultado próprio | Quantifica cobertura e contribuição extra das regiões maiores sem manipular orçamento. | Não; premissa de planejamento |
| Gate | Ganho ≥1% em ≥2 grafos brutos independentes e razão custo ≤2×, com censuras preservadas | Critério prospectivo do Astra, sujeito a revisão antes da primeira execução. | Não; premissa de planejamento |

**Open questions:** none — as escolhas não confirmadas são premissas explícitas acima; antes da execução, revalidar alterações de escopo e gates.

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
| FCR25-01 | Execução reproduzível | Tasks | Pending |
| FCR25-02 | Execução reproduzível | Tasks | Pending |
| FCR25-03 | Execução reproduzível | Tasks | Pending |
| FCR25-04 | Medir ganho marginal correto | Tasks | Pending |
| FCR25-05 | Medir ganho marginal correto | Tasks | Pending |
| FCR25-06 | Medir ganho marginal correto | Tasks | Pending |
| FCR25-07 | Decidir continuidade | Tasks | Pending |
| FCR25-08 | Decidir continuidade | Tasks | Pending |
| FCR25-09 | Decidir continuidade | Tasks | Pending |

**Coverage:** 9 requisitos rastreáveis; tarefas detalhadas em `tasks.md`; 0 implementados.

## Success Criteria

- [ ] 24 linhas esperadas em dry-run, seis casos por quatro braços.
- [ ] Números LP, tempo total e métricas por fase diretamente atribuíveis aos JSON gerados.
- [ ] Gate reproduzível por script sem promoção automática a MIP.

## Dependências e gate

`GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.
