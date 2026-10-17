# AS29 — Reconciliação de LB*, UB* e OPT

**Estado:** DRAFT — primeira etapa elegível para aprovação documental, ainda não executada.
**Gate:** G0 — Fontes reconciliadas.
**Dependências:** AS28 encerrada; não depende de Y-RBC matematicamente válido.
**Esforço estimado:** 0,5–1 dia, incerteza baixa.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

A linha de base reúne LP, limites MIP, ótimo de núcleo e incumbentes físicos sob orçamentos diferentes. Há divergências históricas, especialmente CC9 (OPT=31 reportado em AS06/AS09, enquanto a tabela de LB* da Spec A marca 30) e artefatos anteriores à correção de K. Sem proveniência rigorosa, comparar Y-RBC com o envelope pode induzir uma conclusão falsa.

## Goals

- [ ] Produzir uma tabela fonte-a-fonte de LB/UB/OPT e estado para casos de desenvolvimento, sem inferir certificado racional de um status numérico do Gurobi.
- [ ] Definir protocolo de comparabilidade para AS31–AS35 sem abrir a partição de avaliação.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Reexecutar linha de base | Esta etapa é auditoria e reconciliação documental. |
| Alterar os JSONs históricos | Evidências históricas devem permanecer imutáveis. |
| Divulgar instâncias reservadas | A partição de avaliação permanece isolada. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Convenção de nomes | COMP = U sem K; COMP+K = U+C1+C2+C4-DM | Evita confundir COMP histórico E7–E14 com convenção AS. | Não — revisar antes de Execute |
| Correção de registros | Publicar errata e tabela derivada; não sobrescrever resultados | Rastreabilidade das medições e de correções. | Não — revisar antes de Execute |
| Certificação | OPT numérico somente quando solução primal viável e bound coincidem nas tolerâncias documentadas | Status solver não é prova racional. | Não — revisar antes de Execute |
| Dados de avaliação | Usar só IDs e metadados necessários ao congelamento, sem ler resultados reservados | Prevenir vazamento experimental. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

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
| YR29-01 | P1: Auditar envelope histórico | Specify/Design/Tasks | Pending | T1 |
| YR29-02 | P1: Auditar envelope histórico | Specify/Design/Tasks | Pending | T2 |
| YR29-03 | P1: Auditar envelope histórico | Specify/Design/Tasks | Pending | T3 |
| YR29-04 | P2: Corrigir a régua de decisão | Specify/Design/Tasks | Pending | T3 |
| YR29-05 | P2: Corrigir a régua de decisão | Specify/Design/Tasks | Pending | T4 |
| YR29-06 | P2: Corrigir a régua de decisão | Specify/Design/Tasks | Pending | T4 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G0 PASS: 100% dos casos de desenvolvimento usados nos futuros gates com hash, LB fonte, UB fisicamente validado e classe de status; divergências explicitamente abertas ou resolvidas; CC9 contextualizada. G0 BLOCKED se não houver rastro de proveniência suficiente.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
