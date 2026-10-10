# CERT-01 — Piloto controlado dos oráculos de pricing — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** Independente das FC-01–04; antes de CERT-02 e da campanha longa  
**Caminho:** `specs/cert-01-piloto-comparacao-pricing/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

A N2 prospectiva publicou somente limites de fonte N1: N2-box foi alimentado com multiplicadores nulos, ENUM ficou desabilitado e o resultado MIP de pricing não constitui sozinho prova global racional. Falta comparação dos oráculos para o MESMO vetor dual e cobertura completa documentada.

## Goals

- [ ] Comparar N1, N2-box zero, N2-box com multiplicadores não nulos e ENUM quando completo para vetores duais idênticos.
- [ ] Demonstrar matematicamente cada limite e separar força do oráculo de estacionariedade numérica do CG.

## Out of Scope

| Feature | Reason |
|---|---|
| Editar o Gate N2 FAIL ou reabrir o pré-registro. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Tratar MIP pricing ObjBoundC como certificado racional. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Afirmar que ENUM truncado fornece um bound global. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Vetores de entrada | Capturar snapshots racionais imutáveis do próprio CG, com identidade de instância/K | Permite avaliação pareada sem duas trajetórias duais diferentes. | Não — default explícito |
| Multiplicadores | `propose_lp_multipliers` apenas propõe; `certify_box_bound` verifica coeficientes racionais | Otimização numérica dos multiplicadores não é prova. | Não — default explícito |
| ENUM cap | Contar W conexos e declarar cobertura completa somente sob enumeração exaustiva | Evita chamar prefixo truncado de exato. | Não — default explícito |
| Conjunto inicial | HB q4 e BP q2 16 vértices; casos maiores após medição exploratória | Ambos têm números históricos de W e baixo custo relativo. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Avaliação pareada de limites

**User Story:** Como pesquisador, quero medir a perda entre oráculos sem misturar pontos duais diferentes.

**Por que P1:** Diagnóstico central do parecer.

**Acceptance Criteria (EARS):**

1. **ORCL-01** — WHEN a rational dual snapshot is selected THEN the diagnostic SHALL evaluate N1 and N2-box zero on precisely the same dual and instance/K identity.
2. **ORCL-02** — WHEN optimized numeric multipliers are proposed THEN the diagnostic SHALL validate them through rational `certify_box_bound` before publishing `ell_N2_OPT`.
3. **ORCL-03** — WHEN ENUM covers all connected W and all admissible terminal choices THEN the diagnostic SHALL report the exact rational global pricing optimum with a coverage witness.
4. **ORCL-04** — IF ENUM is interrupted, capped or memory-limited THEN the diagnostic SHALL mark `ENUM_INCOMPLETE` without publishing its sampled minimum as global lower bound.

**Teste independente:** Mesmo digest de dual e K em todas linhas.; Proposta inválida rejeitada; proposta válida verificável.; Grafito mínimo força bruta confere exacto.; Cap=total ou incompleto..
### P1: Interpretar perda na certificação

**User Story:** Como pesquisador, quero separar o preço mínimo global do LB físico derivado.

**Por que P1:** Transforma resultado em hipótese testável.

**Acceptance Criteria (EARS):**

5. **ORCL-05** — WHEN an oracle returns a proved global ell THEN the diagnostic SHALL evaluate Theorem L using the same rational dual and record ell, L, delta and LB separately.
6. **ORCL-06** — IF an oracle is abstained THEN the diagnostic SHALL leave its derived LB absent rather than substituting zero or RMP.
7. **ORCL-07** — WHEN results are reported THEN the diagnostic SHALL distinguish the best proved pricing bound from MIP numeric pricing objective and RMP numeric objective.

**Teste independente:** Frações reproduzíveis.; Sem prova não gera LP LB.; CSV campos distintos..

## Edge Cases

- Theta/nu não finitos: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Nu negativo: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- ENUM atingiu cap: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Dual de outra K: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Solver SciPy indisponível: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| ORCL-01 | P1: Avaliação pareada de limites | Tasks | Pending |
| ORCL-02 | P1: Avaliação pareada de limites | Tasks | Pending |
| ORCL-03 | P1: Avaliação pareada de limites | Tasks | Pending |
| ORCL-04 | P1: Avaliação pareada de limites | Tasks | Pending |
| ORCL-05 | P1: Interpretar perda na certificação | Tasks | Pending |
| ORCL-06 | P1: Interpretar perda na certificação | Tasks | Pending |
| ORCL-07 | P1: Interpretar perda na certificação | Tasks | Pending |

**Coverage:** 7 total, 7 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Comparar N1, N2-box zero, N2-box com multiplicadores não nulos e ENUM quando completo para vetores duais idênticos.
- [ ] Demonstrar matematicamente cada limite e separar força do oráculo de estacionariedade numérica do CG.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **ORCL-01:** Mesmo digest de dual e K em todas linhas.
- **ORCL-02:** Proposta inválida rejeitada; proposta válida verificável.
- **ORCL-03:** Grafito mínimo força bruta confere exacto.
- **ORCL-04:** Cap=total ou incompleto.
- **ORCL-05:** Frações reproduzíveis.
- **ORCL-06:** Sem prova não gera LP LB.
- **ORCL-07:** CSV campos distintos.

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
