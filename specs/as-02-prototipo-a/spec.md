# AS02 — Protótipo da formulação A e validação exaustiva — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P2 · obrigatório  
**Dependências:** AS01=PASS  
**Local:** `specs/as-02-prototipo-a/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

Ainda não existe implementação experimental validada de A. Antes de um piloto difícil, uma implementação mínima deve provar que não exclui instalações fisicamente viáveis nem aceita soluções fisicamente impossíveis.

## Goals

- [ ] Implementar A como modelo MIP completo com y binário e variáveis auxiliares contínuas.
- [ ] Validar pequena escala por enumeração física independente e testes adversos.
- [ ] Reproduzir Sec59 LP e a hierarquia com tolerâncias declaradas.

## Out of Scope

| Item | Motivo |
|---|---|
| Heurística de seleção avançada de grupos | AS03. |
| Instâncias grandes e tuning de solver | AS05/AS06. |
| Reescrever baseline.py ou T18 | Implementação nova, isolada. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Caminho de código | `experiments/astra-study/` novo; nomes de arquivo propostos | Evita alterar modelos históricos. | Pendente de execução |
| Tolerância LP | 1e-6 para comparação numérica; testemunha racional separada | Compatível com controles anteriores sem confundir certificação. | Pendente de execução |
| Núcleo do modelo | Somente y binário; f,g,p,h contínuos | Preserva a formulação A descrita pelo Astra. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS02-01 — Modelo exato:** WHEN A is built with a valid partition THEN the builder SHALL create A1–A7 using the same graph, S, T, r and K as the requested case.
2. **AS02-02 — Partição inválida:** IF groups overlap, omit an origin or are empty THEN the builder SHALL reject the request before creating a model.
3. **AS02-03 — Oráculo físico:** WHEN a tiny installation subset is evaluated THEN the test suite SHALL agree with `independent_validator.viavel` for every considered y assignment.
4. **AS02-04 — Terminais especiais:** WHEN S∩T, staying, terminal transit or terminal station occurs THEN the model SHALL preserve the independently validated physical result.
5. **AS02-05 — Ganho Sec59:** WHEN the frozen Sec59 two-group configuration is solved as LP THEN the runner SHALL reproduce 9/2 within 1e-6 and COMP+K 11/3 within 1e-6.
6. **AS02-06 — Falha matemática:** IF any counterexample invalidates an AC of AS01 THEN the pipeline SHALL block all hard-instance campaigns with status `MATH_GATE_FAIL`.

**Independent Test:** Inspeção automática de domínio e linhas.; Testar casos inválidos.; Enumerar C⊆V para n pequeno.; Testes de quatro famílias adversas.; LPs e testemunha racional auditada.; Teste negativo e nenhum resultado publicado como válido..

## Edge Cases

**Gate obrigatório:** correspondência exaustiva com o validador físico em todos os pequenos casos. Implementações inválidas não devem ser corrigidas com exceções ad hoc para uma única instância.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS02-01 | Inspeção automática de domínio e linhas. | Tasks | Pending |
| AS02-02 | Testar casos inválidos. | Tasks | Pending |
| AS02-03 | Enumerar C⊆V para n pequeno. | Tasks | Pending |
| AS02-04 | Testes de quatro famílias adversas. | Tasks | Pending |
| AS02-05 | LPs e testemunha racional auditada. | Tasks | Pending |
| AS02-06 | Teste negativo e nenhum resultado publicado como válido. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS02-01:** Inspeção automática de domínio e linhas.
- **AS02-02:** Testar casos inválidos.
- **AS02-03:** Enumerar C⊆V para n pequeno.
- **AS02-04:** Testes de quatro famílias adversas.
- **AS02-05:** LPs e testemunha racional auditada.
- **AS02-06:** Teste negativo e nenhum resultado publicado como válido.

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
