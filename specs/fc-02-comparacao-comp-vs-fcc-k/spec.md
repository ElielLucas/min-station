# FC-02 — Comparação inteira controlada COMP × F-CC+K — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** FC-01 (medição confiável)  
**Caminho:** `specs/fc-02-comparacao-comp-vs-fcc-k/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

O braço inteiro atual compara `baseline` sem os cortes K com `fcc_k` com K. Essa diferença mistura efeito da formulação com efeito dos cortes. O protocolo prevê COMP como controle principal mas o runner inteiro não o executa.

## Goals

- [ ] Introduzir braço inteiro COMP com fluxo contínuo e y binário, usando os mesmos K e mesma instância da F-CC+K.
- [ ] Separar baseline sem K como ablação e manter controle LP base/COMP/F-CC+K.

## Out of Scope

| Feature | Reason |
|---|---|
| Trocar a formulação base congelada no repositório. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Comparar o núcleo IP como solução física. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Usar o master restrito da N2 como MIP completo. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Controle principal | COMP MIP = variante U com fluxo contínuo, y binário e os K do experimento | Replica o COMP validado no projeto sem uma restrição inteira desnecessária. | Não — default explícito |
| Ablation | `baseline` sem K será braço secundário claramente rotulado | Permite isolar contribuição de K e da formulação. | Não — default explícito |
| Cap da F-CC+K | Abster-se sem imputar valores quando enumeração completa não cabe | Evita comparação contra modelo incompleto. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Equidade das formulações inteiras

**User Story:** Como pesquisador, quero comparar duas formulações completas do mesmo problema com K idêntico.

**Por que P1:** Fundamento da conclusão de desempenho.

**Acceptance Criteria (EARS):**

1. **PAIR-01** — WHEN a comparison pair is constructed THEN the executor SHALL use the identical instance hash and K hash for COMP MIP and F-CC+K MIP.
2. **PAIR-02** — WHEN the COMP MIP is built THEN the executor SHALL require binary y and continuous flow f with the same valid cuts K applied to F-CC+K.
3. **PAIR-03** — WHEN the main integer comparison runs THEN the executor SHALL label COMP MIP versus F-CC+K MIP as the primary pair and baseline without K as an ablation.
4. **PAIR-04** — IF F-CC+K enumeration is incomplete THEN the executor SHALL report `NOT_MEASURED_CAP_EXCEEDED` for that arm without reporting a global integer lower bound from its restricted model.

**Teste independente:** Par de modelos com hashes idênticos.; Inspecionar vtypes e restrições.; CSV distinto primary/ablation.; Cap muito baixo..
### P1: Soluções e cortes verificáveis

**User Story:** Como pesquisador, quero comprovar que ganho numérico não vem de solução inválida.

**Por que P1:** Evita falsos positivos.

**Acceptance Criteria (EARS):**

5. **PAIR-05** — WHEN an integer incumbent is found THEN the executor SHALL independently validate the installed station set and physical matching before publishing `UB_PHYSICAL_VALIDATED`.
6. **PAIR-06** — IF K validation fails or its hash differs between arms THEN the executor SHALL refuse to publish the paired comparison as valid.

**Teste independente:** Instalação boa/ruim testada.; Corte adulterado recusa..

## Edge Cases

- S∩T: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- K vazio: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Cap de enumeração: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- COMP incumbente inválido: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Desigualdade de hashes: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| PAIR-01 | P1: Equidade das formulações inteiras | Tasks | Pending |
| PAIR-02 | P1: Equidade das formulações inteiras | Tasks | Pending |
| PAIR-03 | P1: Equidade das formulações inteiras | Tasks | Pending |
| PAIR-04 | P1: Equidade das formulações inteiras | Tasks | Pending |
| PAIR-05 | P1: Soluções e cortes verificáveis | Tasks | Pending |
| PAIR-06 | P1: Soluções e cortes verificáveis | Tasks | Pending |

**Coverage:** 6 total, 6 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Introduzir braço inteiro COMP com fluxo contínuo e y binário, usando os mesmos K e mesma instância da F-CC+K.
- [ ] Separar baseline sem K como ablação e manter controle LP base/COMP/F-CC+K.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **PAIR-01:** Par de modelos com hashes idênticos.
- **PAIR-02:** Inspecionar vtypes e restrições.
- **PAIR-03:** CSV distinto primary/ablation.
- **PAIR-04:** Cap muito baixo.
- **PAIR-05:** Instalação boa/ruim testada.
- **PAIR-06:** Corte adulterado recusa.

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
