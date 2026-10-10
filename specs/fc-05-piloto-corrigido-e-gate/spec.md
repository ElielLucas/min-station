# FC-05 — Piloto corrigido e Gate de prontidão — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** FC-01, FC-02, FC-03 e FC-04 aprovadas; CERT-01 não é dependência para comparação LP completa  
**Caminho:** `specs/fc-05-piloto-corrigido-e-gate/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

Os resultados exploratórios atuais (pilot/main/scalability) foram coletados antes da correção do orçamento global, da escolha do controle COMP inteiro e da terminologia de evidência. É necessária uma rodada nova, curta, preservando os arquivos antigos, para testar a comparação justa e decidir se vale uma hora.

## Goals

- [ ] Executar comparação curta reprodutível em instâncias de controle e documentar correção física, completude e custos totais.
- [ ] Emitir Gate explícito `READY_FOR_EXTENDED` ou `NOT_READY` com evidências; nenhuma hora de execução automática.

## Out of Scope

| Feature | Reason |
|---|---|
| Reabrir N2 ou sobrescrever seus resultados. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Garantir ganho da F-CC+K. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Afirmar generalização para benchmark-v1 inteiro. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Orçamento inicial | 60s LP e 120s MIP por braço com budget global, não somar em um único TimeLimit por lote | Custo curto e diagnóstico. | Não — default explícito |
| Primeiras instâncias | HB q4 e BP não q2 B2; expandir a casos estruturais já enumeráveis | Casos com LP histórico e custos observados. | Não — default explícito |
| Gate de progressão | Pronto só se evidência consistente, sem divergência física/hash e comparabilidade íntegra | Ausência de problemas não implica ganho algorítmico. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Execução de piloto controlado

**User Story:** Como pesquisador, quero validar o protocolo antes de gastar horas.

**Por que P1:** Evita custo de experimentos inválidos.

**Acceptance Criteria (EARS):**

1. **PILOT-01** — WHEN a pilot starts THEN the executor SHALL execute comparable LP/MIP arms for the same instance/K with complete end-to-end time records.
2. **PILOT-02** — WHEN pilot results are finalized THEN the reporter SHALL preserve the previous results and create a new timestamped directory with checksummed files.
3. **PILOT-03** — IF a paired arm has invalid physical solution, mismatched K or incomplete enumeration THEN the gate SHALL mark that paired comparison `NOT_READY` with reason.
4. **PILOT-04** — IF budget, integrity and proof-semantics checks pass on all preselected pilot pairs THEN the gate SHALL report `READY_FOR_EXTENDED` without claiming relative performance superiority.

**Teste independente:** Comparar SHA, n_K e wall.; Diretório novo e antigo intacto.; Instância adulterada ou cap.; Gates executados e sem claim de ganho..
### P1: Resultados pareados honestos

**User Story:** Como pesquisador, quero números interpretáveis e abstenções explícitas.

**Por que P1:** Permite planejar 1 hora sem exagerar.

**Acceptance Criteria (EARS):**

5. **PILOT-05** — WHEN reporting a LP comparison THEN the report SHALL distinguish numeric Gurobi LP optimal values from rational proof objects and preserve missing data as missing.
6. **PILOT-06** — IF a single instance is not comparable within the cap THEN the report SHALL retain its row as censored or not measured and SHALL NOT drop it from denominators silently.

**Teste independente:** Status 3 eixos.; Cap mantém linha..

## Edge Cases

- Erro de certificado: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Cap no único braço: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Timeout durante enumeração: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- MIP ótimo mas UB inválido: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Novo output path colide: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| PILOT-01 | P1: Execução de piloto controlado | Tasks | Pending |
| PILOT-02 | P1: Execução de piloto controlado | Tasks | Pending |
| PILOT-03 | P1: Execução de piloto controlado | Tasks | Pending |
| PILOT-04 | P1: Execução de piloto controlado | Tasks | Pending |
| PILOT-05 | P1: Resultados pareados honestos | Tasks | Pending |
| PILOT-06 | P1: Resultados pareados honestos | Tasks | Pending |

**Coverage:** 6 total, 6 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Executar comparação curta reprodutível em instâncias de controle e documentar correção física, completude e custos totais.
- [ ] Emitir Gate explícito `READY_FOR_EXTENDED` ou `NOT_READY` com evidências; nenhuma hora de execução automática.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **PILOT-01:** Comparar SHA, n_K e wall.
- **PILOT-02:** Diretório novo e antigo intacto.
- **PILOT-03:** Instância adulterada ou cap.
- **PILOT-04:** Gates executados e sem claim de ganho.
- **PILOT-05:** Status 3 eixos.
- **PILOT-06:** Cap mantém linha.

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
