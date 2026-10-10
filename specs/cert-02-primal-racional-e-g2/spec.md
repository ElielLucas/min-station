# CERT-02 — Testemunha primal racional e teste G2 — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P2  
**Pré-requisito:** CERT-01 (ao menos snapshots confiáveis)  
**Caminho:** `specs/cert-02-primal-racional-e-g2/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

A N2 usou no G2 uma testemunha primal trivial que instala todas as estações (U=16,16,26,23). Assim, mesmo um certificado melhor poderia continuar sem fechar o gap. Falta reconstruir racionalmente uma solução primal do master restrito final e verificar todas as suas restrições.

## Goals

- [ ] Reconstruir e validar testemunha primal racional próxima ao RMP final, quando matematicamente possível.
- [ ] Separar cota superior do LP completo de solução inteira física, testando G2 somente com provas compatíveis.

## Out of Scope

| Feature | Reason |
|---|---|
| Transformar solução primal fracionária em UB físico. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Declarar G2 só por estacionariedade numérica. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Substituir o Teorema L ou editar provas congeladas. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Reconstrução | Começar com `Fraction.from_float` do vetor primal; se resíduos inviabilizarem, usar ajuste racional verificado ou abster-se | Evita arredondamento silencioso que quebra igualdades. | Não — default explícito |
| Status | `RATIONAL_PRIMAL_VALID` apenas se TODAS R1–R4, K, limites/domínios e custo forem checados | Testemunha primal não deve depender de status do solver. | Não — default explícito |
| Prova de G2 | Requer LB global racional + U_LP racional + diferença exata <= 1e-6 | Sem prova de primais e bound, status fica inconclusivo. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Reconstrução primal exata

**User Story:** Como pesquisador, quero U LP verificável diferente do trivial.

**Por que P1:** Relevante para prova de convergência.

**Acceptance Criteria (EARS):**

1. **PRIM-01** — WHEN a final RMP solution is captured THEN the system SHALL reconstruct candidate y, lambda, d rational values with original column identifiers.
2. **PRIM-02** — WHEN candidate rational values are presented THEN the verifier SHALL check every R1–R4, K, nonnegativity and bounds on the complete retained column set.
3. **PRIM-03** — IF rational repair cannot satisfy the master exactly THEN the system SHALL emit `PRIMAL_ABSTAIN` and SHALL NOT report numerical ObjVal as U_LP certified.

**Teste independente:** Snapshot com S∩T retorna variáveis exatas.; Perturbar uma igualdade falha.; Arredondamento inviável..
### P1: G2 verificável

**User Story:** Como pesquisador, quero prova de gap LP se e somente se há duas evidências.

**Por que P1:** Impede falso sucesso.

**Acceptance Criteria (EARS):**

4. **PRIM-04** — WHEN a valid rational U_LP and certified global LB_CG share model identity THEN the verifier SHALL compute their exact rational gap and accept G2 only if it is at most 1/1000000.
5. **PRIM-05** — IF only a fractional primal is available THEN the system SHALL explicitly distinguish it from an integer feasible physical UB.

**Teste independente:** Casos 1/1000000 e > limite.; Conferir status distinto..

## Edge Cases

- RMP não contém coluna usada: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Repair inexato: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- K diferente: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- D com stay-put: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Gap perto 1e-6: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| PRIM-01 | P1: Reconstrução primal exata | Tasks | Pending |
| PRIM-02 | P1: Reconstrução primal exata | Tasks | Pending |
| PRIM-03 | P1: Reconstrução primal exata | Tasks | Pending |
| PRIM-04 | P1: G2 verificável | Tasks | Pending |
| PRIM-05 | P1: G2 verificável | Tasks | Pending |

**Coverage:** 5 total, 5 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Reconstruir e validar testemunha primal racional próxima ao RMP final, quando matematicamente possível.
- [ ] Separar cota superior do LP completo de solução inteira física, testando G2 somente com provas compatíveis.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **PRIM-01:** Snapshot com S∩T retorna variáveis exatas.
- **PRIM-02:** Perturbar uma igualdade falha.
- **PRIM-03:** Arredondamento inviável.
- **PRIM-04:** Casos 1/1000000 e > limite.
- **PRIM-05:** Conferir status distinto.

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
