# AS-04 — Validação local do autor (NÃO substitui verificador independente)

**Data:** 2026-10-11. **Status final:** `PENDING`.

| Critério | Evidência implementada | Resultado local |
|---|---|---|
| AS04-01 | `as04_compare.assess_pair`, hash da instância, A_r e política | Testes de mutação aprovados |
| AS04-02 | `as04_arms.canonical_k`, `k_digest`, U rotulada WITHOUT_K | Testes de K divergente e mutação aprovados |
| AS04-03 | `K_EFFECT`, `A_EFFECT`, `REFINEMENT_EFFECT` | Teste de três pares aprovado |
| AS04-04 | `ArmResult` com censura, worker supervisionado FC-01, relatório com denominador fixo | Testes de timeout/memória e linha censurada aprovados; worker Gurobi pendente |
| AS04-05 | LP só publica primal como `lp_opt_value` em OPTIMAL completo | Teste de interrupção e ausência de bound aprovado |
| AS04-06 | Validação independente via `independent_validator.viavel` | Teste real de instalação inválida e válida aprovado; Gurobi pendente |
| AS04-07 | Loading+alcance+K+construção+solve+validação no budget FC-01; campos de tempo, Work, nós, pico memória | Testes de campos aprovados; mensuração com Gurobi pendente |
| AS04-08 | MIP numeric bound, UB física, racional em colunas independentes | Teste de evidência e recusa de prova inventada aprovado |
| AS04-09 | FCC incompleta e CORE não promovidos a modelo físico completo | Testes de classificações aprovados |

**Smoke HiGHS:** `U=7/3`, `U_K=11/3`, `A2_K` automático `=11/3`; testemunha matemática com partição específica `=9/2`. A discrepância A2 reflete escolha estrutural, não reparametrização pós-hoc.

**Testes:** 30/30 testes AS-04 aprovados; 10/10 AS-02 e 27/27 AS-03 passaram em regressão local. O smoke real do executor sem Gurobi gerou `SOLVER_ERROR` e `NOT_AUTHORIZED` mantendo todas as linhas, sem imputação.

**Pendências:** Ruff não disponível neste ambiente; Gurobi também não; não há prova independente AS-01/AS-02 homologada no ZIP; auditoria AS-04 autor≠verificador, commits locais e validação na branch original pendentes. Não publicar resultados LP/MIP de múltiplas instâncias como se fossem AS-05.
