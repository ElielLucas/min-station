# AS03 — Políticas reprodutíveis de agrupamento e limites de tamanho — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P3 · obrigatório  
**Dependências:** AS02=PASS; AS00 pré-registro  
**Local:** `specs/as-03-agrupamento-origens/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

A pode tornar-se cara se os grupos crescerem em número ou se A_r for denso. A escolha dos grupos influencia os limites LP e pode induzir overfitting se for ajustada nas instâncias de avaliação.

## Goals

- [ ] Definir políticas determinísticas de partição em dois grupos e refinamento opcional em quatro.
- [ ] Pré-estimar representação e interromper uma construção inviável sem excluir o caso do universo.

## Out of Scope

| Item | Motivo |
|---|---|
| Otimizar agrupamento com conhecimento do ótimo ou resultado de avaliação | Vazamento experimental. |
| Criar centenas de grupos por padrão | Contraria o objetivo da investigação. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Política inicial | Uma divisão determinística por características estruturais pré-registradas e fallback balanceado | Hipótese computacional; não há política vencedora demonstrada. | Pendente de execução |
| Quatro grupos | Somente refinamento dos dois blocos existentes e mediante gatilho AS05 | Preserva a relação LP não-decrescente. | Pendente de execução |
| Estado de abstenção | `NOT_BUILT_SIZE`, `NOT_BUILT_MEMORY`, `NOT_BUILT_BUDGET` | Não atribuir a falhas um resultado LP. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS03-01 — Determinismo:** WHEN the same instance and grouping policy are requested THEN the grouper SHALL produce identical origin blocks and partition hash independently of input order.
2. **AS03-02 — Refinamento:** WHEN four groups are generated from the two-group policy THEN each four-group block SHALL be a subset of exactly one two-group block.
3. **AS03-03 — Orçamento estimado:** WHEN a partition is proposed THEN the predictor SHALL estimate n+k(a+n+m)+|S∩T| variables before building A.
4. **AS03-04 — Falha controlada:** IF the prospective size or memory budget is exceeded THEN the planner SHALL classify the arm without excluding the instance from comparisons of applicability.
5. **AS03-05 — Sem vazamento:** The grouper SHALL use only instance structure and pre-registered policy parameters, not LP optimum, MIP bound or evaluation-arm outcome.

**Independent Test:** Reordenar S não altera output.; Validação de aninhamento.; Conferir contagem com m e a sintéticos.; Teste com orçamento artificial baixo.; Inspecionar entradas e assinaturas..

## Edge Cases

Escolhas de agrupamento devem ser fundamentadas estruturalmente; políticas distintas podem produzir LPs sem ordem total. Não afirmar que todo `k=4` domina todo `k=2` sem relação de refinamento.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS03-01 | Reordenar S não altera output. | Tasks | Pending |
| AS03-02 | Validação de aninhamento. | Tasks | Pending |
| AS03-03 | Conferir contagem com m e a sintéticos. | Tasks | Pending |
| AS03-04 | Teste com orçamento artificial baixo. | Tasks | Pending |
| AS03-05 | Inspecionar entradas e assinaturas. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS03-01:** Reordenar S não altera output.
- **AS03-02:** Validação de aninhamento.
- **AS03-03:** Conferir contagem com m e a sintéticos.
- **AS03-04:** Teste com orçamento artificial baixo.
- **AS03-05:** Inspecionar entradas e assinaturas.

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
