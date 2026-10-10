# FC-04 — Identidade de instâncias, integridade e relatórios — Specification

**Status:** RASCUNHO (não implementada)  
**Prioridade:** P1  
**Pré-requisito:** FC-01, FC-02 e FC-03 (schema final)  
**Caminho:** `specs/fc-04-integridade-manifesto-e-relatorios/`  

**Base de leitura:** ZIP `min-station(20261010-171720).zip` (branch informada `novos_testes`) e parecer do Astra colado em 2026-10-10. São referências para especificação, não evidência de implementação das novas tarefas.
**Preservação:** fase N2 encerrada `N2 FAIL`; não modificar congelamentos, Gates, resultados N1/N2 ou originais em `results/formulation-comparison/`.
**Norma científica:** RMP restrito ≠ LB físico; `GRB.OPTIMAL` é prova numérica do solver sob tolerâncias, não por si certificado racional independente.

## Problem Statement

O loader aceita `sha256_conteudo` do manifesto sem verificar que os bytes carregados correspondem ao hash. A proveniência registra alguns arquivos reutilizados, mas não todos os scripts do executor nem os digests dos resultados. Relatos de escalabilidade exageram o alcance da sondagem e há inconsistência de contagens.

## Goals

- [ ] Rejeitar instâncias divergentes e registrar hashes dos bytes efetivamente usados.
- [ ] Gerar manifesto auditável de código, entradas, configuração e saídas, com conclusões proporcionais à evidência.

## Out of Scope

| Feature | Reason |
|---|---|
| Reescrever resultados históricos sem registro de alteração. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Afirmar inviabilidade das 75 instâncias principais a partir de três sondagens. | Fora da mudança delimitada, preserva evidência e separação de estudos. |
| Introduzir download de dados externos. | Fora da mudança delimitada, preserva evidência e separação de estudos. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| SHA do manifesto | Recomputar bytes e comparar quando SHA esperado existir | Hash sem verificação não dá integridade. | Não — default explícito |
| Versionamento artefatos | Outputs novos em diretórios novos; arquivos antigos preservados | Permite comparação histórica e atualização controlada. | Não — default explícito |
| Números de escalabilidade | Relatar contagens a partir das linhas efetivamente medidas, deixando universo não sondado explícito | Evita generalização indevida. | Não — default explícito |

**Open questions:** none blocking — os defaults acima são hipóteses explícitas e deverão ser revisados em Execute se entrarem em conflito com provas do repositório.

## User Stories

### P1: Instâncias verificadas

**User Story:** Como pesquisador, quero garantir que ambos os braços usam os mesmos dados físicos.

**Por que P1:** Base de qualquer comparação.

**Acceptance Criteria (EARS):**

1. **AUDIT-01** — WHEN an instance is loaded THEN the loader SHALL compute SHA-256 from the actual file bytes and SHALL compare it to `sha256_conteudo` when supplied.
2. **AUDIT-02** — IF the expected SHA differs from actual bytes THEN the loader SHALL reject the instance with a nonempty mismatch diagnostic before optimization.
3. **AUDIT-03** — WHEN the manifest lists graph metadata THEN the loader SHALL check parsed dimensions and problem parameters against the declared metadata or record an explicit unsupported-field exception.

**Teste independente:** Modificar um byte do caso e checar falha.; Checksum incorreto.; m,n,r divergentes..
### P1: Manifesto e relato auditáveis

**User Story:** Como pesquisador, quero reconstruir de qual código e execução cada número veio.

**Por que P1:** Rastreabilidade da dissertação.

**Acceptance Criteria (EARS):**

4. **AUDIT-04** — WHEN a result directory is finalized THEN the manifest SHALL include hashes of the executor modules, relevant model sources, raw instances, result CSVs and final plot artifacts.
5. **AUDIT-05** — IF a measured file changes after finalization THEN the read-only audit SHALL report integrity failure instead of silently accepting the modified artifact.
6. **AUDIT-06** — WHEN scalability statistics are published THEN the report SHALL compute measured cap totals from the actual CSV rows and SHALL identify untested instances as untested.

**Teste independente:** Verificar hashes byte a byte.; Alterar um byte e rodar checker.; 9/10 esperado no dataset atual; sem 75/75..

## Edge Cases

- Hash ausente: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Hash divergente: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Metadado n incorreto: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Arquivo pós-run alterado: cobrir com teste de borda/abstenção segundo os ACs desta feature.
- Report parcial CAP: cobrir com teste de borda/abstenção segundo os ACs desta feature.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AUDIT-01 | P1: Instâncias verificadas | Tasks | Pending |
| AUDIT-02 | P1: Instâncias verificadas | Tasks | Pending |
| AUDIT-03 | P1: Instâncias verificadas | Tasks | Pending |
| AUDIT-04 | P1: Manifesto e relato auditáveis | Tasks | Pending |
| AUDIT-05 | P1: Manifesto e relato auditáveis | Tasks | Pending |
| AUDIT-06 | P1: Manifesto e relato auditáveis | Tasks | Pending |

**Coverage:** 6 total, 6 planejados em tasks; 0 não mapeados. Nenhum verificado.

## Success Criteria

- [ ] Rejeitar instâncias divergentes e registrar hashes dos bytes efetivamente usados.
- [ ] Gerar manifesto auditável de código, entradas, configuração e saídas, com conclusões proporcionais à evidência.
- [ ] Todos os ACs estão cobertos por testes independentes, com falhas negativas e Ruff sem erro.
- [ ] Evidência dos testes e dos arquivos realmente executados está registrada por Verifier distinto do autor.

## Tests Derived from Acceptance Criteria

- **AUDIT-01:** Modificar um byte do caso e checar falha.
- **AUDIT-02:** Checksum incorreto.
- **AUDIT-03:** m,n,r divergentes.
- **AUDIT-04:** Verificar hashes byte a byte.
- **AUDIT-05:** Alterar um byte e rodar checker.
- **AUDIT-06:** 9/10 esperado no dataset atual; sem 75/75.

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
