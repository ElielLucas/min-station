# FC-01 — Orçamento global e medição ponta a ponta — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** Nenhuma; primeira correção do comparativo  
**Caminho:** `specs/fc-01-orcamento-global-e-tempos/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

O comparativo atual configura TimeLimit no MIP depois da montagem e chama `lp_fcc_plus_k` sem encaminhar o `lp_time_limit_s`. Enumeração, montagem, tentativa abortada por cap e validação ficam fora do orçamento prometido. Assim, tempo de solver e tempo total não são comparáveis.

## Goals

- [ ] Respeitar tetos de parede globais por execução de LP/MIP, incluindo preparação específica do braço, enumeração, montagem, solver e validação.
- [ ] Registrar custo por fase, motivo de parada e trabalho Gurobi de forma reproduzível.

## Out of Scope

| Feature | Reason |
|---|---|
| Alterar o teto de 164 Work congelado da N2. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Otimizar a enumeração ou melhorar a formulação. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Executar a bateria principal de uma hora. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Relógio | `time.monotonic()` para limite de parede; Work permanece métrica separada | Impede equiparar unidades Work e segundos. | Não — default explícito |
| Interrupção de preparação Python | Isolar execução em processo controlável ou mecanismo equivalente que realmente interrompa enumeração Python | `TimeLimit` do solver não interrompe código Python já rodando. | Não — default explícito |
| Contagem de tempo | O tempo do braço inclui K e preparação específica daquele braço; preparação compartilhada é registrada separadamente | Evita duplicar custo e permite comparação ponta a ponta. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Prazo global LP e MIP

**User Story:** Como pesquisador, quero que um braço nunca ultrapasse silenciosamente o orçamento de parede para poder comparar algoritmos.

**Por que P1:** Prioritário para qualquer medição de tempo.

**Acceptance Criteria (EARS):**

1. **TIME-01** — WHEN a modalidade A inicia THEN the executor SHALL iniciar o relógio global antes da preparação específica do braço e transmitir apenas o tempo restante ao solver.
2. **TIME-02** — WHEN a modalidade B inicia THEN the executor SHALL contabilizar enumeração, construção, otimização e validação no mesmo orçamento configurado por braço.
3. **TIME-03** — IF the global deadline expires during Python enumeration or model assembly THEN the executor SHALL encerrar o braço com status `TIMEOUT_PREPARATION` e sem valor LP/IP fabricado.
4. **TIME-04** — IF the deadline expires before optimize THEN the executor SHALL abstain from starting a Gurobi solve and SHALL record the elapsed wall time.

**Teste independente:** Começar no relógio simulado e afirmar tempo restante.; Preparação artificial de 80s e budget 60s não inicia solve.; Worker demorado ultrapassa deadline e retorna timeout.; Mock deadline expirado e `optimize` proibido..
### P1: Medição de custo e exceções

**User Story:** Como pesquisador, quero medições completas inclusive em falhas para evitar viés de sobrevivência.

**Por que P1:** É pré-condição dos relatórios.

**Acceptance Criteria (EARS):**

5. **TIME-05** — WHEN an enumeration cap is exceeded THEN the executor SHALL record positive observed preparation wall time and `NOT_MEASURED_CAP_EXCEEDED` instead of reporting duration zero.
6. **TIME-06** — WHEN a solve ends THEN the executor SHALL record total wall, phase durations, solver Runtime and solver Work in distinct fields.
7. **TIME-07** — IF a solver or worker fails THEN the executor SHALL preserve a nonempty diagnostic and an explicit failure status without emitting an objective as valid.

**Teste independente:** Cap mínimo acionado após relógio avançar.; Assert monotonia e não duplicação das fases.; Exception stub imprime causa e sem LB..

## Edge Cases

- Orçamento menor que preparação: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Cap atingido durante geração de W: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Solver sem licença: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Timeout sem incumbent: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Tempo de validação pós-solver: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| TIME-01 | P1: Prazo global LP e MIP | Tasks | Pending |
| TIME-02 | P1: Prazo global LP e MIP | Tasks | Pending |
| TIME-03 | P1: Prazo global LP e MIP | Tasks | Pending |
| TIME-04 | P1: Prazo global LP e MIP | Tasks | Pending |
| TIME-05 | P1: Medição de custo e exceções | Tasks | Pending |
| TIME-06 | P1: Medição de custo e exceções | Tasks | Pending |
| TIME-07 | P1: Medição de custo e exceções | Tasks | Pending |

**Coverage:** 7 total, 7 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Respeitar tetos de parede globais por execução de LP/MIP, incluindo preparação específica do braço, enumeração, montagem, solver e validação.
- [ ] Registrar custo por fase, motivo de parada e trabalho Gurobi de forma reproduzível.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **TIME-01:** Começar no relógio simulado e afirmar tempo restante.
- **TIME-02:** Preparação artificial de 80s e budget 60s não inicia solve.
- **TIME-03:** Worker demorado ultrapassa deadline e retorna timeout.
- **TIME-04:** Mock deadline expirado e `optimize` proibido.
- **TIME-05:** Cap mínimo acionado após relógio avançar.
- **TIME-06:** Assert monotonia e não duplicação das fases.
- **TIME-07:** Exception stub imprime causa e sem LB.

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
