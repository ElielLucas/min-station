# FC-03 — Semântica de limites, certificados e convergência — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** FC-02; pode evoluir em paralelo com FC-04 após a interface estabilizada  
**Caminho:** `specs/fc-03-semantica-evidencia-numerica/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

No comparativo, `GRB.OPTIMAL` e `ObjBound` recebem rótulos `CERTIFIED_LP`, `CERTIFIED_MIP_BOUND` ou `CERTIFIED_MIP_OPTIMAL`. O método fornece evidência numérica do Gurobi, mas não reconstrói prova racional independente equivalente à E5 da N2. Os rótulos podem induzir interpretação científica incorreta.

## Goals

- [ ] Distinguir status numérico do solver, certificado racional independente e validação física do UB.
- [ ] Garantir que comparação e gap usam apenas bounds apropriados, identificando a fonte e o grau de prova.

## Out of Scope

| Feature | Reason |
|---|---|
| Reconstruir prova racional genérica de branch-and-bound de Gurobi. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Chamar `ObjBoundC` de certificado racional. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Afirmar força teórica estrita com base apenas em floats de solver. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Rotulagem | `SOLVER_NUMERIC_OPTIMAL`, `SOLVER_NUMERIC_BOUND`, `RATIONAL_VERIFIED`, `NOT_CERTIFIED` são eixos distintos | Força clareza sem descartar resultados numéricos legítimos. | Não — default explícito |
| Bounds inteiros | `ObjBound` de um MIP completo pode constar como limite numérico de solver, nunca prova racional independente | É evidência computacional sob tolerâncias, não proof object. | Não — default explícito |
| Infeasibilidade | Sem solução e sem prova publicada => `UNKNOWN`/abstenção apropriada | Evita UB=0 e suposições de factibilidade. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Status científicos inequívocos

**User Story:** Como pesquisador, quero saber de onde vem cada limite.

**Por que P1:** Evita falsa certificação.

**Acceptance Criteria (EARS):**

1. **PROOF-01** — WHEN a full LP returns `GRB.OPTIMAL` THEN the executor SHALL publish `SOLVER_NUMERIC_OPTIMAL` and SHALL NOT report `RATIONAL_VERIFIED` without an independent verifier record.
2. **PROOF-02** — WHEN a complete MIP returns an `ObjBound` THEN the executor SHALL record it as a numeric solver bound with its solver status and model-completeness flag.
3. **PROOF-03** — IF the model is restricted or enumeration is truncated THEN the executor SHALL prohibit using its MIP bound as a global MIN-STATION lower bound.
4. **PROOF-04** — WHEN an incumbent has passed independent physical validation THEN the executor SHALL publish its cost as a physical feasible UB with provenance.

**Teste independente:** Mock GRB.OPTIMAL não libera prova racional.; MIP completo intermitente.; RMP incompleto.; Incumbente válido..
### P1: Gap e abstenção seguros

**User Story:** Como pesquisador, quero evitar porcentagens e gaps enganosos.

**Por que P1:** Distingue resultado inconclusivo.

**Acceptance Criteria (EARS):**

5. **PROOF-05** — IF the published UB or comparable LB is absent THEN the executor SHALL leave certified gap fields empty and record `INCONCLUSIVE`.
6. **PROOF-06** — WHEN a rational verifier succeeds THEN the executor SHALL store proof identifier, checked model identity and exact rational value separately from floating-point fields.

**Teste independente:** Sem incumbent ou sem LB.; Mock prova íntegra..

## Edge Cases

- LP ótimo apenas numeric: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- TIME_LIMIT sem incumbente: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- F-CC+K truncada: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- UB inválido: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- ObjBoundC pricing: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| PROOF-01 | P1: Status científicos inequívocos | Tasks | Pending |
| PROOF-02 | P1: Status científicos inequívocos | Tasks | Pending |
| PROOF-03 | P1: Status científicos inequívocos | Tasks | Pending |
| PROOF-04 | P1: Status científicos inequívocos | Tasks | Pending |
| PROOF-05 | P1: Gap e abstenção seguros | Tasks | Pending |
| PROOF-06 | P1: Gap e abstenção seguros | Tasks | Pending |

**Coverage:** 6 total, 6 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Distinguir status numérico do solver, certificado racional independente e validação física do UB.
- [ ] Garantir que comparação e gap usam apenas bounds apropriados, identificando a fonte e o grau de prova.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **PROOF-01:** Mock GRB.OPTIMAL não libera prova racional.
- **PROOF-02:** MIP completo intermitente.
- **PROOF-03:** RMP incompleto.
- **PROOF-04:** Incumbente válido.
- **PROOF-05:** Sem incumbent ou sem LB.
- **PROOF-06:** Mock prova íntegra.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entrada | ACs verificam limites, hashes, domínio e status válidos, conforme o escopo. |
| Falha parcial/externa | Timeout, cap, erro Gurobi, falta de licença ou abstenção permanecem estados explícitos. |
| Retry/idempotência | Novos diretórios, sem sobrescrever resultados anteriores. |
| Concorrência/ordenação | Determinismo de seed e controle de orçamento por braço; não presumir threads com relógio compartilhado. |
| Ciclo de dados | Artefatos append-only e digests de arquivos publicados. |
| Observabilidade | CSV/JSON com status, fonte da evidência, wall, Work e justificativa. |
| Autenticação/rate limit | N/A: execução local de scripts de pesquisa, sem API autenticada. |
| Estado/transições | Quando aplicável: indisponível/numérico/verificado/abstenção, com regras explícitas nos ACs. |
