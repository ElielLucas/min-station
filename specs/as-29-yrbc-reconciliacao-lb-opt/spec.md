# AS29 — Reconciliação de LB*, UB* e OPT

**Estado:** `AS29_COMPLETE` com limitações menores (Rev. 2, 18/10/2026). G0 pelo contrato vigente, sem emendas: `G0_CANDIDATE_PASS` (31/31 casos de desenvolvimento com UB física revalidada). **A aprovação do gate é do pesquisador.** Histórico: Rev. 0 (17/10) `G0_BLOCKED_EVIDENCE` com 8/31; Rev. 1 (17/10) `COMPLETE_WITH_LIMITATIONS`, emenda A1 proposta e depois não adotada; Rev. 2 (18/10) exportação posterior das instalações.
**Gate:** G0 — Fontes reconciliadas.
**Dependências:** AS28 encerrada; não depende de Y-RBC matematicamente válido.
**Esforço estimado:** 0,5–1 dia, incerteza baixa.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks → Execute → revisão independente (Rev. 1) → exportação posterior de instalações (Rev. 2) → Verifier.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

A linha de base reúne LP, limites MIP, ótimo de núcleo e incumbentes físicos sob orçamentos diferentes. Há divergências históricas, especialmente CC9 (OPT=31 reportado em AS06/AS09, enquanto a tabela de LB* da Spec A marca 30) e artefatos anteriores à correção de K. Sem proveniência rigorosa, comparar Y-RBC com o envelope pode induzir uma conclusão falsa.

## Goals

- [x] Produzir tabela fonte-a-fonte (31 desenvolvimento + 5 legados) com LB/UB/OPT e seu estado; as lacunas de UB física ficam explícitas.
- [x] Documentar regras de comparabilidade para AS31–AS35 sem usar resultados reservados. A **aprovação do protocolo científico** depende de revisão independente.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Reexecutar linha de base | Esta etapa é auditoria e reconciliação documental. *[Rev. 2: o pesquisador autorizou, em 18/10/2026, uma exportação posterior das instalações com a configuração da Spec A, em pasta nova e sem alterar `linha_base.csv`; não é reexecução da linha de base e está rotulada como evidência posterior.]* |
| Alterar os JSONs históricos | Evidências históricas devem permanecer imutáveis. |
| Divulgar instâncias reservadas | A partição de avaliação permanece isolada. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Convenção de nomes | COMP = U sem K; COMP+K = U+C1+C2+C4-DM | Evita confundir COMP histórico E7–E14 com convenção AS. | Aplicada nos CSVs (Rev. 1); confirmação do pesquisador pendente |
| Correção de registros | Publicar errata e tabela derivada; não sobrescrever resultados | Rastreabilidade das medições e de correções. | Aplicada; nenhuma fonte primária alterada (Rev. 1); confirmação do pesquisador pendente |
| Certificação | OPT numérico somente quando solução primal viável e bound coincidem nas tolerâncias documentadas | Status solver não é prova racional. | Aplicada: "solução primal viável" = instalação revalidada pelo oráculo independente (Rev. 1); confirmação do pesquisador pendente |
| Dados de avaliação | Usar só IDs e metadados necessários ao congelamento, sem ler resultados reservados | Prevenir vazamento experimental. | Aplicada: arquivos AS09 de avaliação filtrados antes da leitura; linhas de avaliação de `linha_base.csv` descartadas na carga (Rev. 1); confirmação do pesquisador pendente |

**Open questions: none** sobre os requisitos. Ficam com o pesquisador duas decisões de gate, não de especificação: aprovar o G0 e confirmar os defaults acima (ver Success Criteria).

## User Stories

### P1: Auditar envelope histórico

**User Story:** Como pesquisador, quero comparar limites independentes com proveniência para saber qual método efetivamente resolveu cada caso.

**Acceptance Criteria**

1. WHEN um resultado histórico for incluído THEN o relatório SHALL registrar instância/hash, método, versão, parâmetros, seed, orçamento, status, bound e incumbente validada.
2. WHEN o envelope for calculado THEN o pipeline SHALL considerar LB da cobertura como limite válido e SHALL excluir sua solução inteira de qualquer UB físico sem validação no MIN-STATION.
3. IF dois documentos divergirem THEN o relatório SHALL exibir os valores lado a lado, a evidência primária e o estado de reconciliação, sem apagar a divergência.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Corrigir a régua de decisão

**User Story:** Como pesquisador, quero comparar limites LP, limites MIP e ótimo físico sem misturá-los.

**Acceptance Criteria**

1. WHEN CC9 constar como aberta na linha de base THEN a errata SHALL registrar os certificados numéricos AS06/AS09 para OPT=31 e a distinção entre LB* histórico=30 e ótimo posterior=31.
2. WHEN campanhas posteriores forem preparadas THEN a matriz SHALL usar a mesma definição de instância e orçamento pareado com métricas separadas para LP, LB MIP e UB físico.
3. IF uma evidência vier de artefato pré-correção de K THEN a matriz SHALL marcá-la não comparável até reprodução ou justificativa específica.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR29-01 | P1: Auditar envelope histórico | Execute | Verified (Rev. 1) | T1 |
| YR29-02 | P1: Auditar envelope histórico | Execute | Verified (Rev. 1) — oráculo reexecutado, C/C_K inadmissível | T2 |
| YR29-03 | P1: Auditar envelope histórico | Execute | Verified (Rev. 1) | T3 |
| YR29-04 | P2: Corrigir a régua de decisão | Execute | Verified (Rev. 1) | T3 |
| YR29-05 | P2: Corrigir a régua de decisão | Execute | Documented; regras de uso em `as29-envelope-lb-opt.md` §6–§7 | T4 |
| YR29-06 | P2: Corrigir a régua de decisão | Execute | Verified — artefatos pré-correção de K (E9/E10) excluídos do envelope | T4 |

**Coverage:** 6 critérios rastreados e cobertos por `test_reconcile_as29.py` ou pelos relatórios; detalhes em `validation.md`.

## Evidência de execução

**Rev. 0 (17/10/2026, autor da implementação):** 11 testes PASS; 260 linhas de proveniência; 8/31 UBs físicas *reportadas*; `G0_BLOCKED_EVIDENCE`. As UBs não tinham sido revalidadas pelo oráculo.

**Rev. 1 (17/10/2026, revisão independente):**

- `reconcile_as29.py` reexecuta o oráculo independente em 67/67 instalações arquivadas (0 rejeições), exclui do LB os braços `C`/`C_K` (formulação sem prova), acrescenta LP U/U_K do AS09, separa `OPT_NUMERIC_PHYSICAL` (3) de `OPT_NUMERIC_SOLVER_ONLY` (15), detecta LB > UB entre fontes (0 casos) e lê seed/threads/orçamento de planos com hash conferido.
- Após o primeiro Verifier (FAIL por lacunas de contrato): limites do manifesto lado a lado (E-29-11), estado `INCOMPLETE` que bloqueia, plano AS06 conferido contra manifesto/`report.json`, `source_versioned_in`/`cuts_scope`, e G0 de volta ao contrato vigente com a emenda separada.
- `test_reconcile_as29.py`: 31 testes PASS. O sensor reproduzível é o do Verifier, registrado em `validation.md`; o sensor do autor (12/12 mortos) não deixou artefato. Na iteração 2, as lacunas N11/N12 (lado UB da flag) e N10 (`cuts_scope`) receberam testes.
- 292 linhas de proveniência, 36 casos. Os valores de LB\*, LB histórico e UB física por caso não mudaram em relação à Rev. 0. A conferência foi feita na sessão, antes de sobrescrever os CSVs da Rev. 0, que não eram versionados; não há artefato da Rev. 0.
- Nenhuma execução de Gurobi, nenhuma instalação reconstruída a partir do valor objetivo e nenhuma alteração em `results/` (na Rev. 1).

**Rev. 2 (18/10/2026, exportação posterior autorizada pelo pesquisador):**

- `experiments/benchmark/export_as29_installations.py` resolveu os 23 casos de desenvolvimento sem instalação, em `U` e `U_K`, com a configuração da Spec A (seed 42, `WorkLimit=164`, 4 threads, Gurobi 12.0.3): 46 solves, 27 `OPTIMAL_NUMERIC` e 19 `WORK_LIMIT`. Saída em `results/benchmark/as29-physical-ub-001/` (nova pasta, sidecar SHA-256 por arquivo); nenhuma fonte existente foi alterada.
- As 46 instalações passaram no oráculo independente e as 46 linhas reproduzem a linha de base de seed 42 (mesmo `mip_obj`, `mip_bound` dentro de 0,01).
- O auditor agora lê essa fonte: 338 linhas de proveniência, 113 instalações revalidadas (0 rejeições), 31/31 casos de desenvolvimento com UB física (18 `OPT_NUMERIC_PHYSICAL`, 13 `OPEN_PHYSICAL_UB`), gate `G0_CANDIDATE_PASS`.
- `test_reconcile_as29.py`: 34 testes PASS (inclui reprodução da linha de base, adulteração de sidecar da exportação e gate real).
- Limite declarado: nos casos D/A de 3 seeds só a seed 42 foi reexecutada; em 4 casos a UB física é maior do que o menor objetivo numérico da Spec A (outra seed, sem instalação).

## Success Criteria

- [x] **G0 PASS (critério vigente, texto original, sem emendas) — condições atendidas na Rev. 2:** 100% dos casos de desenvolvimento usados nos futuros gates com hash, LB fonte, UB fisicamente validado e classe de status; divergências explicitamente abertas ou resolvidas; CC9 contextualizada. 31/31 casos com UB física; o auditor emite `G0_CANDIDATE_PASS`. *Candidato: a aprovação do gate cabe ao pesquisador (plano §6).*
- [x] **Emenda A1: não adotada e sem efeito.** Proposta na Rev. 1, depois dos resultados, para o caso em que as instalações não fossem obtidas. A Rev. 2 obteve as instalações; o critério original foi atendido sem mudança. O texto da emenda e os argumentos contra ficam abaixo, por registro.
- [ ] Revisor independente confirma evidências por requisito: ver o veredito mais recente em `validation.md`.
- [x] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35. *[Rev. 1: texto original restaurado; a Rev. 0 o tinha trocado por "não utilizar resultados reservados" sem registro. Nenhum arquivo de instância `avaliacao` é aberto; o auditor lê `linha_base.csv` inteiro e descarta as linhas de avaliação na carga, sem usá-las.]*

### Emenda A1 do critério G0 — registro histórico (não adotada)

- **Revisão:** proposta na Rev. 1, 17/10/2026, **posterior** aos resultados da Rev. 0. Não foi adotada; o critério segue o texto original.
- **Motivação:** (1) o texto do critério e o do plano qualificam o requisito com "casos usados nos/que entram nos futuros gates", e esse conjunto só é fixado no pré-registro da AS31; (2) "Reexecutar linha de base" está fora de escopo, e `linha_base.csv` nunca guardou vetores de instalação, de modo que a leitura "31/31" era inalcançável dentro da etapa; (3) a UB numérica do solver só é usada onde um erro é conservador, e toda alegação nova do Y-RBC já exige incumbente validada pelo protocolo da própria campanha.
- **Evidência:** `as29-envelope-lb-opt.md` §4–§6; `as29-erratas-e-incompatibilidades.md` E-29-08 a E-29-10.
- **O que não mudou:** nenhum caso sem instalação foi promovido a UB física; o critério original permanece não atendido.
- **Contra a emenda (registrado):** é um afrouxamento posterior aos resultados; os 8 casos abertos sem UB física são D/A, justamente onde AS31/AS32 alegariam ganho de UB; e as obrigações transferidas precisam ser escritas na spec da AS31 antes de valerem.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> Aprovar a spec ou a recomendação G0 não autoriza benchmark, push ou uso da partição reservada.
