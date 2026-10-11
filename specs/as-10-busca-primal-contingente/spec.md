# AS10 — Contingência: busca primal controlada no compacto — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** Condicional · secundária  
**Dependências:** AS06 sem ganho dual; decisão científica registrada  
**Local:** `specs/as-10-busca-primal-contingente/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Se todas as alternativas de fortalecer LB forem caras, pode haver valor em melhorar UB físico com busca local limitada, mas o bound de um subproblema restrito não é LB global.

## Goals

- [ ] Implementar pesquisa primal limitada sobre instalações, mantendo U_K como solucionador principal.
- [ ] Comparar políticas de incumbentes com orçamento idêntico e validação física independente.

## Out of Scope

| Item | Motivo |
|---|---|
| Reinterpretar LB de vizinhança como bound global | Matematicamente inválido. |
| Repetir E10/E13 sem controle e declaração de alterações | Campanhas históricas já sugerem confusões. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Ativação | Somente após STOP claro de AS06 e revisão do E13 | Não competir com a linha principal. | Pendente de execução |
| Uso dos incumbentes | Warm starts idênticos quando se mede efeito de formulação; modo primal separado para medir ganho de UB | Evita confusão causal. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS10-01 — Candidatos:** WHEN a neighborhood search returns a station set THEN the runner SHALL validate its physical feasibility before declaring any UB.
2. **AS10-02 — Isolamento:** WHEN primal search is assessed THEN the protocol SHALL distinguish its standalone effect from gains attributed to A or U_K.
3. **AS10-03 — Bound inválido:** IF a restricted subproblem produces an internal bound THEN the reporter SHALL label it LOCAL_ONLY and SHALL not publish it as a global MIN-STATION LB.
4. **AS10-04 — Tempo:** WHEN the primal phase is enabled THEN its construction and validation time SHALL count against the preregistered global budget.
5. **AS10-05 — Parada:** IF no reproducible UB improvement is found THEN the branch SHALL stop without expanding search arbitrarily.

**Independent Test:** Solução inviável descartada.; Matriz com/sem primal igual.; Teste status LOCAL_ONLY.; Budget incluindo overhead.; Dois grafos independentes..

## Edge Cases

O ganho de UB é avaliado em experimento separado. Um lower bound calculado em subproblema restrito não é limite inferior global do MIN-STATION.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS10-01 | Solução inviável descartada. | Tasks | Pending |
| AS10-02 | Matriz com/sem primal igual. | Tasks | Pending |
| AS10-03 | Teste status LOCAL_ONLY. | Tasks | Pending |
| AS10-04 | Budget incluindo overhead. | Tasks | Pending |
| AS10-05 | Dois grafos independentes. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS10-01:** Solução inviável descartada.
- **AS10-02:** Matriz com/sem primal igual.
- **AS10-03:** Teste status LOCAL_ONLY.
- **AS10-04:** Budget incluindo overhead.
- **AS10-05:** Dois grafos independentes.

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
