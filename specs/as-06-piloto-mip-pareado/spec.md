# AS06 — Piloto MIP 300/600 s com seeds e controles — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P5 · condicional ao LP  
**Dependências:** AS05=GO; AS04=PASS  
**Local:** `specs/as-06-piloto-mip-pareado/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

LP mais forte pode gerar MIP mais lento. É necessário medir ganho líquido em resolução inteira, com tempo de construção, busca e validação física comparáveis.

## Goals

- [ ] Comparar de modo pareado U_K contra A2_K (e A4_K quando aprovada), preservando U como ablação.
- [ ] Reproduzir resultados com 300 s/seed 42 e, havendo sinal, 600 s/seeds 42,43,44.
- [ ] Decidir de forma auditável qual candidato pode entrar na campanha final.

## Out of Scope

| Item | Motivo |
|---|---|
| 3600 s por instância sem gate | AS11. |
| Ajustar novos parâmetros durante avaliação | Protocolo congelado. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Etapa 1 | 300 s totais por braço/instância, seed 42 | Primeiro piloto proposto pelo Astra. | Pendente de execução |
| Etapa 2 | 600 s totais por braço/instância, seeds 42,43,44 | Somente quando 300 s indicar utilidade. | Pendente de execução |
| Warm start | Política idêntica aos braços; identidade e tempo cobrados | Não atribuir vantagem de UB a método desigual. | Pendente de execução |
| Medidas de desempenho | Best LB e UB ao longo do tempo, gap, primeira incumbente, nós, Work, memória e total wall | Distinguir força LP da dinâmica MIP. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS06-01 — Pares:** WHEN the MIP pilot runs THEN it SHALL execute U_K and each promoted A arm on the identical preregistered instance and solver configuration.
2. **AS06-02 — Orçamento:** WHEN an arm starts THEN its supervisor SHALL charge all allocated preparation, build, solver and validation time against the declared 300/600 s budget.
3. **AS06-03 — Repetição:** IF a 300 s pair meets the preregistered advance rule THEN the pilot SHALL run the matching 600 s pairs with seeds 42,43,44.
4. **AS06-04 — Evolução:** WHEN a Gurobi trace is available THEN the reporter SHALL record time-to-first validated UB, time-to-best UB, LB time series, nodes and Work without inventing missing events.
5. **AS06-05 — Validade física:** IF an incumbent fails the independent validator THEN the runner SHALL reject its UB as physical and flag validation failure.
6. **AS06-06 — Promoção:** WHEN outcomes are complete THEN the decision SHALL require reproducible benefit in at least two independent graph families and no concealed severe regressions before promotion.
7. **AS06-07 — Negativo:** IF the candidate provides no useful gain over U_K and CORE_IP THEN the pilot SHALL preserve negative evidence and route to the conditional decision branch without opening AS11 automatically.

**Independent Test:** Hash e parâmetros coincidem.; Timeout de construção não vira ausência do caso.; Controle de seeds e saltos.; Curvas monotônicas coerentes.; Perturbar y do incumbente.; Gate baseado em famílias, não linhas.; Gate STOP preservado..

## Edge Cases

Não usar apenas média de instâncias resolvidas; contabilizar regressões, timeouts, OOM e custo pré-solver. Candidatos precisam superar controles em pelo menos duas famílias de grafos independentes.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS06-01 | Hash e parâmetros coincidem. | Tasks | Pending |
| AS06-02 | Timeout de construção não vira ausência do caso. | Tasks | Pending |
| AS06-03 | Controle de seeds e saltos. | Tasks | Pending |
| AS06-04 | Curvas monotônicas coerentes. | Tasks | Pending |
| AS06-05 | Perturbar y do incumbente. | Tasks | Pending |
| AS06-06 | Gate baseado em famílias, não linhas. | Tasks | Pending |
| AS06-07 | Gate STOP preservado. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS06-01:** Hash e parâmetros coincidem.
- **AS06-02:** Timeout de construção não vira ausência do caso.
- **AS06-03:** Controle de seeds e saltos.
- **AS06-04:** Curvas monotônicas coerentes.
- **AS06-05:** Perturbar y do incumbente.
- **AS06-06:** Gate baseado em famílias, não linhas.
- **AS06-07:** Gate STOP preservado.

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
