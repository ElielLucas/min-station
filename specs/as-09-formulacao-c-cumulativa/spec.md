# AS09 — Contingência: formulação C de estados de bateria — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** Condicional · alcance denso  
**Dependências:** AS01; AS03 tamanho de A_r; gate justificado  
**Local:** `specs/as-09-formulacao-c-cumulativa/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Grafos MAPF e Vienna podem produzir A_r denso. A versão cumulativa histórica possui ativação por nível que não controla a soma das recargas; uma versão com ativação total poderia ter menor representação.

## Goals

- [ ] Corrigir o contrato de recarga cumulativa sem alterar o problema de robôs anônimos.
- [ ] Verificar projeção de LP equivalente a U/COMP antes de reivindicar economia de representação.
- [ ] Testar representação em alcance denso, incluindo custo de K que ainda depende do grafo de alcance.

## Out of Scope

| Item | Motivo |
|---|---|
| Prometer limite LP superior ao COMP | Astra propõe equivalência, não reforço. |
| Omitir construção de A_r exigida pelos cortes K | Custo global continua contado. |
| Reativar cumulativa histórica sem correção de ativação | Contraexemplo mostrou insuficiência. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Gatilho | A_r denso, 2r|E| significativamente menor que |A_r| e custo de A observado | Justificativa quantitativa antes do código. | Pendente de execução |
| Consumo | Arestas de G custo unitário; r inteiro; estados q=0,...,r | Semântica do MIN-STATION atual. | Pendente de execução |
| Objetivo | Comparar memória/tempo, não força teórica LP | Uma falha de prova de equivalência interrompe afirmação de dominância. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS09-01 — Estados:** WHEN C is specified THEN it SHALL model movement F^q, recharge z^q and destination absorption e^q on original G with q=0..r.
2. **AS09-02 — Ativação corrigida:** WHEN recharge variables are created THEN C SHALL enforce sum_{q=1}^r z_v^q≤κ_v y_v instead of only independent per-level activation.
3. **AS09-03 — Terminais:** WHEN S∩T occurs THEN C SHALL represent staying, free initial departure, final absorption and paid intermediate recharge correctly.
4. **AS09-04 — Equivalência:** WHEN C is compared with U without K THEN the reviewer SHALL verify LP y-projection equivalence or mark the property UNPROVEN.
5. **AS09-05 — Custo completo:** WHEN C is benchmarked with K THEN the experiment SHALL include any necessary reachability/K preparation and report actual nvars, constraints, memory and wall time.
6. **AS09-06 — Gate:** IF no representation-size advantage survives full pipeline cost THEN the branch SHALL close without opening MIP campaign.

**Independent Test:** Estados de bateria enumerados.; Estrela T18 elimina LP espúrio.; Contraexemplo a-v-b.; Duas projeções, exemplos.; Não esconder A_r.; Abstenções e negativos..

## Edge Cases

C é reserva para custo de representação em alcance denso. A relação LP com U deve ser comprovada; não confundir possíveis ganhos por tamanho com força de relaxação.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS09-01 | Estados de bateria enumerados. | Tasks | Pending |
| AS09-02 | Estrela T18 elimina LP espúrio. | Tasks | Pending |
| AS09-03 | Contraexemplo a-v-b. | Tasks | Pending |
| AS09-04 | Duas projeções, exemplos. | Tasks | Pending |
| AS09-05 | Não esconder A_r. | Tasks | Pending |
| AS09-06 | Abstenções e negativos. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS09-01:** Estados de bateria enumerados.
- **AS09-02:** Estrela T18 elimina LP espúrio.
- **AS09-03:** Contraexemplo a-v-b.
- **AS09-04:** Duas projeções, exemplos.
- **AS09-05:** Não esconder A_r.
- **AS09-06:** Abstenções e negativos.

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
