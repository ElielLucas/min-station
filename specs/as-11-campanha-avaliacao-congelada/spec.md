# AS11 — Campanha final condicionada de até 3.600 s — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P5 · somente com promoção  
**Dependências:** AS06=GO, ou ramo condicional com gate aprovado; AS00 protocolo congelado  
**Local:** `specs/as-11-campanha-avaliacao-congelada/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Uma campanha longa sem benefício em desenvolvimento desperdiça recursos e expõe o estudo a cherry-picking. A avaliação deve testar generalização de políticas congeladas e relatar todas as falhas.

## Goals

- [ ] Congelar modelo vencedor, parâmetros, seleção de 8–12 instâncias de avaliação e métricas antes da execução.
- [ ] Executar no máximo 3.600 s ponta a ponta por braço/semente, com rastreabilidade de entradas e validação física.
- [ ] Relatar aplicabilidade e ganhos pareados, inclusive timeouts, OOM e diferenças entre famílias.

## Out of Scope

| Item | Motivo |
|---|---|
| Trocar instâncias após ver resultados | Proibido no estudo confirmatório. |
| Exigir F-CC explícita para admitir caso | Viés da FC-06. |
| Declarar prova racional por status OPTIMAL | Distinção de AS04. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Número | Cerca de 8–12 casos estratificados, escolhidos antes da execução | Parecer Astra. | Pendente de execução |
| Tempo | 3.600 s por braço/seed incluindo preparação e validação | Orçamento ponta a ponta. | Pendente de execução |
| Repetição | Seeds congeladas no pré-registro e orçamento total estimado antes de lançar | Evita consumir dezenas de horas sem justificar. | Pendente de execução |
| Se não houve promoção | Registrar `CAMPAIGN_NOT_AUTHORIZED` e encerrar com resultado negativo em AS12 | Não há obrigação de rodar 3.600 s. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS11-01 — Gate:** IF no candidate has a documented promotion PASS THEN the campaign SHALL not start and SHALL emit CAMPAIGN_NOT_AUTHORIZED.
2. **AS11-02 — Freeze:** WHEN the evaluation starts THEN the runner SHALL verify hashes for cases, policies, code revision, K and solver configuration against preregistered values.
3. **AS11-03 — Cobertura:** WHEN a planned arm ends THEN the result set SHALL include all selected cases and classify solve, timeout, memory, build-failure or validation-failure outcomes.
4. **AS11-04 — Tempo:** WHEN a timed run executes THEN the supervisor SHALL enforce and report the 3600 s total budget including preprocessing, building, solving and validation.
5. **AS11-05 — Comparação:** WHEN results are summarized THEN the reporter SHALL provide paired per-family LB, validated UB, gap, runtime-to-target, memory and solved-rate metrics with censored outcomes visible.
6. **AS11-06 — Independência:** WHEN related MAPF maps occur across splits THEN the synthesis SHALL flag them as non-independent evidence and SHALL not count them as separate families.
7. **AS11-07 — Certificação:** The report SHALL distinguish numerical Gurobi statuses from independent rational certificates and shall not present incomplete RMP as global bound.

**Independent Test:** Executar controle com gate FAIL.; Tamper bloqueia.; Nenhuma linha some.; Timeout antes do solver.; Não promediar apenas casos resolvidos.; Map m10/m25.; Campo de certificado independente..

## Edge Cases

Se nenhum candidato passar, **não executar** campanha longa. `CAMPAIGN_NOT_AUTHORIZED` é um resultado legítimo de planejamento, não ausência de pesquisa.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS11-01 | Executar controle com gate FAIL. | Tasks | Pending |
| AS11-02 | Tamper bloqueia. | Tasks | Pending |
| AS11-03 | Nenhuma linha some. | Tasks | Pending |
| AS11-04 | Timeout antes do solver. | Tasks | Pending |
| AS11-05 | Não promediar apenas casos resolvidos. | Tasks | Pending |
| AS11-06 | Map m10/m25. | Tasks | Pending |
| AS11-07 | Campo de certificado independente. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS11-01:** Executar controle com gate FAIL.
- **AS11-02:** Tamper bloqueia.
- **AS11-03:** Nenhuma linha some.
- **AS11-04:** Timeout antes do solver.
- **AS11-05:** Não promediar apenas casos resolvidos.
- **AS11-06:** Map m10/m25.
- **AS11-07:** Campo de certificado independente.

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
