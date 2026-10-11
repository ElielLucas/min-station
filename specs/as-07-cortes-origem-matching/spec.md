# AS07 — Contingência: cortes por origem e matching compartilhado — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** Condicional · concorrente do primeiro parecer  
**Dependências:** AS01 auditado; AS05=STOP ou AS06=STOP/INVESTIGATE, após decisão escrita  
**Local:** `specs/as-07-cortes-origem-matching/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Se a desagregação por grupos não entregar benefício líquido, a alternativa de manter U_K com cortes separados por fluxo máximo pode recuperar informação de origem/destino sem materializar k fluxos.

## Goals

- [ ] Formalizar o modelo auxiliar de matching e fluxo unitário com S∩T.
- [ ] Demonstrar validade física de todos os cortes e verificar um caso de ganho LP estrito ou justificar hipótese discriminante.
- [ ] Testar separação limitada na raiz com capacidade de parar e manter U_K inteiro exato.

## Out of Scope

| Item | Motivo |
|---|---|
| Implementar cortes em toda árvore de início | Astra sugere raiz antes de callbacks. |
| Tratar subset U⊂S como extensão completa | Declaração de origem selecionada obrigatória. |
| Retomar N2/branch-and-price | Outra linha de pesquisa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Ativação | Somente se AS05/AS06 rejeitar A ou o custo for excessivo | Evita desenvolver dois motores sem evidência. | Pendente de execução |
| Rede auxiliar | Uma origem por vez, nós divididos, capacidade y no trânsito e p_st na absorção final | Capacidade das estações não é compartilhada globalmente entre robôs. | Pendente de execução |
| Preservação | Manter integralmente U_K e gerar cortes válidos na raiz sob limite fixo | Parada antecipada continua MIP completo válido. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS07-01 — Pareamento:** WHEN the extension uses a subset U of origins THEN it SHALL impose sum_t p_st=1 and sum_{s∈U}p_st≤1 while leaving destination assignment free.
2. **AS07-02 — Rede especial:** WHEN a terminal is used for transit rather than final arrival THEN the auxiliary network SHALL charge its station transit arc; zero-length stay SHALL be permitted when s∈T.
3. **AS07-03 — Separação:** WHEN the current fractional solution violates a unit-source min-cut THEN the separator SHALL generate a valid cut sum_{v∈Z} y_v + sum_{t∈J}p_st≥1.
4. **AS07-04 — Preservação:** IF the separation budget ends THEN the solver SHALL continue with the intact U_K MIP and SHALL never infer F-CC completeness.
5. **AS07-05 — Promoção:** IF no independent strict LP benefit beyond U_K is found or separation cost exceeds materiality limits THEN the branch SHALL stop without executing a full campaign.
6. **AS07-06 — Dominação:** WHEN a theoretical dominance claim is published THEN it SHALL identify any unproven strictness or missing proof of projection to F-CC.

**Independent Test:** Feasibility contra casos anônimos.; Testes de S∩T.; Comparar mincut e corte manual.; Parar em zero rodadas.; Gate negativo registra custo.; Parecer matemático independente..

## Edge Cases

A proposta anterior permanece concorrente, **não** método simultâneo obrigatório. Redes de origem têm capacidade `y_v` separadamente, nunca capacidade consumida em conjunto por todos os robôs.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS07-01 | Feasibility contra casos anônimos. | Tasks | Pending |
| AS07-02 | Testes de S∩T. | Tasks | Pending |
| AS07-03 | Comparar mincut e corte manual. | Tasks | Pending |
| AS07-04 | Parar em zero rodadas. | Tasks | Pending |
| AS07-05 | Gate negativo registra custo. | Tasks | Pending |
| AS07-06 | Parecer matemático independente. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS07-01:** Feasibility contra casos anônimos.
- **AS07-02:** Testes de S∩T.
- **AS07-03:** Comparar mincut e corte manual.
- **AS07-04:** Parar em zero rodadas.
- **AS07-05:** Gate negativo registra custo.
- **AS07-06:** Parecer matemático independente.

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
