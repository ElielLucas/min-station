# AS12 — Síntese científica e encerramento reproduzível — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** Encerramento obrigatório  
**Dependências:** AS05 e AS06, quando habilitada; AS07–AS11 se executadas ou dispensadas por gate  
**Local:** `specs/as-12-sintese-decisao-cientifica/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

A pesquisa precisa preservar resultados positivos e negativos, evitar afirmar superioridade não medida e relacionar força LP, aplicabilidade e performance ao controle U_K e ao núcleo.

## Goals

- [ ] Produzir síntese com matriz de formulações e rastreabilidade das afirmações ao tipo de evidência.
- [ ] Documentar as limitações e a escolha final ou ausência de ganho sem reabrir N2 FAIL.
- [ ] Fornecer artefatos suficientes para reprodução e discussão acadêmica.

## Out of Scope

| Item | Motivo |
|---|---|
| Reescrever experimentos ou alterar freeze de N1/N2/FC | Resultados anteriores permanecem auditáveis. |
| Afirmar novidade de multicommodity, Benders ou fluxo máximo em geral | Contribuição deve ser específica ao MIN-STATION. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Escopo de comparação | U; U_K; A2/A4; candidatos opcionais liberados por gate; FCC_K pequeno; núcleo IP | Não fabricar medições ausentes. | Pendente de execução |
| Tipo de conclusão | Separar contribuição matemática, algorítmica e experimental | Possível resultado negativo ainda é cientificamente relevante. | Pendente de execução |
| Literatura | Referências de Das (2026), desagregação parcial, regenerator e modelos de caminhos devem ser verificadas antes do manuscrito | Parecer menciona precedentes que não devem ser confundidos com inovação própria. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS12-01 — Matriz de evidência:** WHEN the final report is compiled THEN it SHALL label every comparison as theoretical proof, rational witness, numeric LP, numeric MIP, physical UB validation or not measured.
2. **AS12-02 — Relações:** WHEN a formulation is ranked THEN the report SHALL separate theoretical LP dominance, measured performance and applicability.
3. **AS12-03 — Resultados negativos:** IF A or conditional alternatives fail a gate THEN the report SHALL preserve their stopping reason and measured evidence without rewriting outcomes.
4. **AS12-04 — Reprodutibilidade:** WHEN an experimental claim is cited THEN the report SHALL provide source commit/hash, instance hash, K hash, script, parameters, budget and result artifact identity.
5. **AS12-05 — Escopo:** The conclusion SHALL state that N2 FAIL remains unchanged, F-CC explicit is a small-case control and no unrun branch has measured evidence.
6. **AS12-06 — Análise crítica:** WHEN a purported gain is reported THEN the synthesis SHALL compare it against U_K and CORE_IP where available and note independent graph-family count.

**Independent Test:** Auditar amostra por fonte.; Tabela com dimensões distintas.; Gates STOP constam da linha do tempo.; Proveniência verificável.; Não atribuir vitória hipotética.; Ganho do núcleo não atribuído a A..

## Edge Cases

A síntese deve preservar o caráter prospectivo em relação aos novos métodos, mas reconhecer que as instâncias de avaliação já possuem resultados históricos conhecidos.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS12-01 | Auditar amostra por fonte. | Tasks | Pending |
| AS12-02 | Tabela com dimensões distintas. | Tasks | Pending |
| AS12-03 | Gates STOP constam da linha do tempo. | Tasks | Pending |
| AS12-04 | Proveniência verificável. | Tasks | Pending |
| AS12-05 | Não atribuir vitória hipotética. | Tasks | Pending |
| AS12-06 | Ganho do núcleo não atribuído a A. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS12-01:** Auditar amostra por fonte.
- **AS12-02:** Tabela com dimensões distintas.
- **AS12-03:** Gates STOP constam da linha do tempo.
- **AS12-04:** Proveniência verificável.
- **AS12-05:** Não atribuir vitória hipotética.
- **AS12-06:** Ganho do núcleo não atribuído a A.

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
