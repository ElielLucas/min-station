# FC-06 — Campanha pareada de até 3.600 segundos (condicional) — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P2/condicional  
**Pré-requisito:** FC-05 `READY_FOR_EXTENDED` e seleção de instâncias documentada; CERT-01/CERT-02 são complementares, não substituem a comparação inteira  
**Caminho:** `specs/fc-06-campanha-3600s-condicional/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

O prazo de uma hora não deve ser aplicado aos modelos atuais sem correções nem em instâncias triviais. A formulação completa F-CC+K sofre estouro do cap em muitas instâncias e a campanha deve ser amostrada previamente, com dados censurados preservados.

## Goals

- [ ] Definir e executar campanha prospectiva pareada somente após Gate operacional, com até 3600s de wall por braço e registro de seeds.
- [ ] Analisar escalabilidade e força do LP separadamente do desempenho inteiro, sem imputar resultados de instâncias que não couberam.

## Out of Scope

| Feature | Reason |
|---|---|
| Branch-and-price ou extensão de N2. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Forçar execução de 3600s em casos já provados ótimos em segundos. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Publicar conclusão global com seis instâncias selecionadas após observar resultados. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Prontidão | Dependência formal de FC-05 READY_FOR_EXTENDED; se não houver instâncias não triviais, somente documentar insuficiência | Evita horas sem valor informativo. | Não — default explícito |
| Seeds | 42, 43 e 44 nas repetições da campanha longa quando justificado | Diminui dependência de ordem e seed. | Não — default explícito |
| Orçamento | 3600s parede incluindo preparação específica do braço, enumeração, construção, solver e validação | Comparação ponta a ponta justa. | Não — default explícito |
| Agregação | Agrupar por grafo de origem e separar grupos correlatos | Não declarar independência de instâncias do mesmo grafo. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P2: Pré-registro e execução controlada

**User Story:** Como pesquisador, quero evidência válida do custo de ambos os métodos em casos suficientemente difíceis.

**Por que P2:** Condicional à correção e ao piloto.

**Acceptance Criteria (EARS):**

1. **HOUR-01** — IF the operational pilot gate is not `READY_FOR_EXTENDED` THEN the campaign executor SHALL refuse to start any 3600-second experiment.
2. **HOUR-02** — WHEN an eligible campaign starts THEN the executor SHALL freeze the instance selection, hashes, machine, software, seed list and primary metrics before the first long run.
3. **HOUR-03** — WHEN a formulation is executed THEN the executor SHALL enforce the same 3600-second total wall cap for preparation, enumeration, solve and validation.
4. **HOUR-04** — IF F-CC+K exceeds enumeration cap THEN the campaign SHALL preserve a censored outcome without replacing it by RMP N2 or a zero.

**Teste independente:** Gate falso bloqueia.; Manifesto criado antes de solver.; Mock worker long aborta.; CAP e linha mantida..
### P2: Análise estatística sem viés

**User Story:** Como pesquisador, quero avaliar evidências positivas e negativas sem escolher apenas casos resolvidos.

**Por que P2:** Adequado à dissertação.

**Acceptance Criteria (EARS):**

5. **HOUR-05** — WHEN reporting paired outcomes THEN the reporter SHALL include timeouts, cap failures and unsolved cases in denominators and group outcomes by origin graph.
6. **HOUR-06** — WHEN a scientific conclusion is emitted THEN the report SHALL distinguish LP strength, numeric MIP performance and independently certified evidence, with no universal superiority claim from a limited sample.

**Teste independente:** CSV contém unsolved e grouped.; Auditoria de relatório e schema..

## Edge Cases

- Gate não pronto: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Sem instância difícil elegível: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Cap em F-CC+K: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Timeout de worker: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Repetições mesmo grafo: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| HOUR-01 | P2: Pré-registro e execução controlada | Tasks | Pending |
| HOUR-02 | P2: Pré-registro e execução controlada | Tasks | Pending |
| HOUR-03 | P2: Pré-registro e execução controlada | Tasks | Pending |
| HOUR-04 | P2: Pré-registro e execução controlada | Tasks | Pending |
| HOUR-05 | P2: Análise estatística sem viés | Tasks | Pending |
| HOUR-06 | P2: Análise estatística sem viés | Tasks | Pending |

**Coverage:** 6 total, 6 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Definir e executar campanha prospectiva pareada somente após Gate operacional, com até 3600s de wall por braço e registro de seeds.
- [ ] Analisar escalabilidade e força do LP separadamente do desempenho inteiro, sem imputar resultados de instâncias que não couberam.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **HOUR-01:** Gate falso bloqueia.
- **HOUR-02:** Manifesto criado antes de solver.
- **HOUR-03:** Mock worker long aborta.
- **HOUR-04:** CAP e linha mantida.
- **HOUR-05:** CSV contém unsolved e grouped.
- **HOUR-06:** Auditoria de relatório e schema.

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
