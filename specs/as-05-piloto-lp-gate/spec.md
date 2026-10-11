# AS05 — Piloto LP de A e gate de promoção — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P4 · obrigatório  
**Dependências:** AS00,AS01,AS02,AS03,AS04=PASS  
**Local:** `specs/as-05-piloto-lp-gate/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Ganho em Sec59 não garante melhoria em instâncias difíceis. Um piloto LP barato deve mostrar se dois grupos trazem limite inferior superior ao U+K e se o custo adicional compensa.

## Goals

- [ ] Realizar matriz de seis instâncias de desenvolvimento em braços U, U_K, A2_K, CORE_IP quando aplicável.
- [ ] Testar A4_K somente sob gatilho predefinido, mantendo partições aninhadas.
- [ ] Emitir decisão reproduzível GO/STOP/INVESTIGATE sem campanha longa automática.

## Out of Scope

| Item | Motivo |
|---|---|
| Ajustar política em avaliação | Vazamento. |
| Usar F-CC incompleta como controle LP | Não fornece LP da formulação inteira completa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Janela de diagnóstico | 60–90 s totais por braço (valor fixado no pré-registro AS00) | Parecer recomenda triagem curta. | Pendente de execução |
| Tolerância | 1e-6 para comparações LP numéricas concluídas | Ganho dentro da tolerância não é evidência de melhora. | Pendente de execução |
| Gatilho quatro grupos | A2 mostra ganho em caso relevante ou há hipótese escrita de fraqueza por agrupamento | Evita expandir k mecanicamente. | Pendente de execução |
| Critério materialidade | Fixar antes da execução valores numéricos de ganho relativo, custo e regressão máxima no protocolo AS00 | Astra não impôs limiar numérico universal; não inventar posterior. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS05-01 — Matriz LP:** WHEN the pilot is run THEN it SHALL attempt U, U_K and A2_K on all six preregistered development instances and CORE_IP as an auxiliary bound when supported.
2. **AS05-02 — F-CC controle:** WHERE a tiny control case admits complete FCC_K enumeration the pilot SHALL compare its LP without counting it as a mandatory arm of difficult instances.
3. **AS05-03 — Quatro grupos:** IF the preregistered refinement trigger is absent THEN the pilot SHALL skip A4_K with an explicit NOT_SELECTED_REASON.
4. **AS05-04 — Qualidade:** WHEN comparable LP optima are available THEN the report SHALL compute gain of U_K over U and gain of A2_K over U_K separately.
5. **AS05-05 — Interrupções:** IF a model is not built or its LP is interrupted THEN the report SHALL retain the row with a censored status and no fabricated LP optimum.
6. **AS05-06 — Decisão:** WHEN all development outcomes are collected THEN the gate SHALL issue GO only if pre-registered materiality criteria hold on at least two independent graph families, otherwise STOP or INVESTIGATE with reasons.

**Independent Test:** 6 × 3 entradas presentes.; Enumeração incompleta classificada.; Sem A4 por padrão.; Cálculos e tolerância.; Caso grande permanece.; Duas seeds no mesmo mapa não contam duas famílias..

## Edge Cases

O piloto LP é discriminante: ganho apenas em Sec59 não autoriza campanha MIP. Uma LP interrompida sem bound apropriado não recebe o rótulo de `z_LP` ótimo.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS05-01 | 6 × 3 entradas presentes. | Tasks | Pending |
| AS05-02 | Enumeração incompleta classificada. | Tasks | Pending |
| AS05-03 | Sem A4 por padrão. | Tasks | Pending |
| AS05-04 | Cálculos e tolerância. | Tasks | Pending |
| AS05-05 | Caso grande permanece. | Tasks | Pending |
| AS05-06 | Duas seeds no mesmo mapa não contam duas famílias. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS05-01:** 6 × 3 entradas presentes.
- **AS05-02:** Enumeração incompleta classificada.
- **AS05-03:** Sem A4 por padrão.
- **AS05-04:** Cálculos e tolerância.
- **AS05-05:** Caso grande permanece.
- **AS05-06:** Duas seeds no mesmo mapa não contam duas famílias.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entradas | Critérios EARS cobrem domínios, partições, fingerprints e status conforme escopo. |
| Falhas externas e parciais | Distinção de erro, orçamento, solver, OOM, falta de dados e abstenção; não inferir resultado. |
| Retry e idempotência | Artefatos novos, hashes e política de não sobrescrever evidência congelada. |
| Concorrência / ordenação | Pré-registro de seeds, parâmetros e ordem/família de comparações. |
| Ciclo dos dados | Resultado append-only e rastro de proveniência. |
| Observabilidade | Métricas/evidências por caso e estágio, conforme os ACs. |
| Auth e rate limit | N/A: scripts científicos locais sem API autenticada. |
| Estado / transições | Gates PASS / FAIL / STOP / INVESTIGATE / NOT_AUTHORIZED, quando aplicável. |
