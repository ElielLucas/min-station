# AS01 — Auditoria matemática da formulação A e errata T18 — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P1 · gate matemático obrigatório  
**Dependências:** AS00 (controle de instâncias pequenas)  
**Local:** `specs/as-01-formalizacao-matematica-a/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

A T18 implementada não domina a relaxação U como afirmado na documentação. O Astra propôs A, com fluxos por grupos de origens e ligação global, mas suas provas, relações de dominância e casos S∩T ainda requerem revisão independente.

## Goals

- [ ] Fixar a definição normativa completa de A, incluindo todas as variáveis, balanços e ativação global.
- [ ] Provar equivalência inteira, caso k=1, monotonicidade por refinamento e relações com COMP+K e F-CC+K, ou registrar lacunas e bloquear implementação.
- [ ] Documentar contraexemplo racional T18 e a distinção entre A unitária, B e proposta de cortes.

## Out of Scope

| Item | Motivo |
|---|---|
| Otimizações em benchmark grande | Matemática deve passar antes de benchmark. |
| Reparar ou substituir silenciosamente T18 histórica | Registrar errata separada, preservando código e evidência. |
| Alegar dominância estrita universal | O parecer prova ganho em um caso, não em todas as instâncias. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Fonte matemática | Segundo parecer Astra do commit e25b056, sujeito a auditoria independente | Recomendação ainda não aprovada como teorema final. | Pendente de execução |
| Partição | Blocos não vazios formam partição de S; destinos livres e |S|=|T|=m | Preserva anonimato e a semântica do problema. | Pendente de execução |
| Cortes K | C1+C2+C4-DM idênticos quando comparando modelos +K | Mantém as conclusões matemáticas e experimentais separadas. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS01-01 — Definição completa:** WHEN the mathematical dossier is finalized THEN it SHALL define A1–A7, domains, c_Bv, kappa_v, S∩T and zero-length paths without ambiguous conventions.
2. **AS01-02 — Exatidão inteira:** WHEN y is binary THEN the dossier SHALL prove physical feasibility if and only if A has a feasible extension for any partition of S.
3. **AS01-03 — Um grupo:** WHEN B={S} THEN the dossier SHALL establish equality of the projected LP optimum and U for arbitrary valid instances or mark the claim UNPROVEN.
4. **AS01-04 — Refinamento:** WHEN a partition refines another THEN the dossier SHALL derive LP non-weakening by an explicit projection, or mark the claim UNPROVEN.
5. **AS01-05 — Dominância:** WHEN relationships to F-CC, B, T18 and previous cuts are stated THEN the dossier SHALL distinguish proven implications, counterexamples and unresolved comparisons.
6. **AS01-06 — T18 errata:** WHEN the historical T18 dominance statement is cited THEN the dossier SHALL attach the star counterexample with rational LP values 1/2 and 1.
7. **AS01-07 — Verificador:** IF an independent reviewer finds an invalid counterexample or missing proof step THEN the gate SHALL remain FAIL and block AS02.

**Independent Test:** Conferência simbólica das equações.; Auditoria das duas implicações.; Checar casos com S∩T.; Revisão dos coeficientes c_Bv.; Não declarar ordem entre partições incomparáveis.; Reproduzir a testemunha racional.; Registro de ressalva vinculada ao AC..

## Edge Cases

**Gate obrigatório:** resultado `PASS` de um verificador independente das provas. O exemplo Sec59 constitui uma testemunha de ganho, não demonstra desempenho geral. Não promover A por simples contagem de variáveis.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS01-01 | Conferência simbólica das equações. | Tasks | Pending |
| AS01-02 | Auditoria das duas implicações. | Tasks | Pending |
| AS01-03 | Checar casos com S∩T. | Tasks | Pending |
| AS01-04 | Revisão dos coeficientes c_Bv. | Tasks | Pending |
| AS01-05 | Não declarar ordem entre partições incomparáveis. | Tasks | Pending |
| AS01-06 | Reproduzir a testemunha racional. | Tasks | Pending |
| AS01-07 | Registro de ressalva vinculada ao AC. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS01-01:** Conferência simbólica das equações.
- **AS01-02:** Auditoria das duas implicações.
- **AS01-03:** Checar casos com S∩T.
- **AS01-04:** Revisão dos coeficientes c_Bv.
- **AS01-05:** Não declarar ordem entre partições incomparáveis.
- **AS01-06:** Reproduzir a testemunha racional.
- **AS01-07:** Registro de ressalva vinculada ao AC.

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
