# AS32 — Protótipo Y-RBC e teste do envelope inteiro

**Estado:** BLOQUEADA — G2a GO + autorização humana.
**Gate:** G2b — Potencial frente ao envelope.
**Dependências:** AS29 PASS; AS30 PASS; AS31 GO aprovado; gate da arquitetura aprovado.
**Esforço estimado:** 4–7 dias, alta incerteza.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

BC-y/CBI antigos já mostraram alto custo de callbacks, fraca incumbente inicial e perda para COMP no regime de redes TNTP. Y-RBC deve demonstrar mecanismo novo e vantagem em instâncias principais do problema de Das sem apenas renomear os callbacks anteriores.

## Goals

- [ ] Protótipo mínimo e exato em y-space com K, BF em MIPNODE, BR em MIPSOL e oráculo/primal fiscalizados.
- [ ] Comparar sob orçamento equivalente com núcleo IP, COMP+K MIP e BC-y/CBI anterior, incluindo ablações para atribuição.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Campanha ampliada | AS33 só com G2b aprovado. |
| Prometer LP superior ao COMP+K | A projeção BF completa apenas recupera a LP de COMP com K. |
| Alterar o oráculo físico | Reutilizar e testar equivalência, não trocar a definição do problema. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Integridade MIPSOL | Todo incumbente candidato é validado antes de aceito; timeout em callback não pode pular verificação | A corretude vem antes do desempenho. | Não — revisar antes de Execute |
| Modo de separação | BF separado por mincut de N(y) com rede restrita certificada; BR como lazy em y inteiro | Mecanismos já existentes no repositório. | Não — revisar antes de Execute |
| Heurística primal | Partir de candidatos pequenos de cobertura e reparar; validar sempre o matching | Evitar start de V com milhares de estações. | Não — revisar antes de Execute |
| Avaliação | Comparar métricas pareadas por budget e seed, com ablação e censuras | Não exigir recuperar todo envelope histórico de seeds diferentes. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Construir protótipo correto

**User Story:** Como pesquisador, quero executar um mestre sem fluxo explícito que aceite somente instalações reais.

**Acceptance Criteria**

1. WHEN MIPSOL apresentar candidato inteiro THEN o callback SHALL validar o conjunto no oráculo exato e SHALL emitir BR se inviável, antes de devolver o controle.
2. WHEN MIPNODE apresentar ponto fracionário elegível THEN o separador SHALL emitir somente BF com certificado de corte finito e violação acima da tolerância.
3. IF o certificado BF/BR falhar ou houver budget esgotado THEN o protótipo SHALL abster-se/terminar de maneira segura sem declarar solução inviável como válida.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Comparar contra o envelope

**User Story:** Como pesquisador, quero saber se Y-RBC realmente supera uma abordagem existente sob mesmas condições.

**Acceptance Criteria**

1. WHEN a campanha exploratória rodar THEN o comparador SHALL incluir K IP, COMP+K MIP, BC-y/CBI legado e os braços de ablação, sem tratar incumbente do núcleo como solução física.
2. WHEN um start de solução for fornecido THEN o programa SHALL aceitá-lo somente após validação física do conjunto C.
3. IF o protótipo ficar abaixo do envelope pareado em vários casos ou gastar mais de metade do tempo em callback THEN o gate SHALL recomendar STOP.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR32-01 | P1: Construir protótipo correto | Specify/Design/Tasks | Pending | T1, T2 |
| YR32-02 | P1: Construir protótipo correto | Specify/Design/Tasks | Pending | T1, T2 |
| YR32-03 | P1: Construir protótipo correto | Specify/Design/Tasks | Pending | T1, T2 |
| YR32-04 | P2: Comparar contra o envelope | Specify/Design/Tasks | Pending | T4 |
| YR32-05 | P2: Comparar contra o envelope | Specify/Design/Tasks | Pending | T3, T4 |
| YR32-06 | P2: Comparar contra o envelope | Specify/Design/Tasks | Pending | T5 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G2b GO_CANDIDATE_REVIEW: ao menos 2 grafos brutos independentes com melhoria verificável em bound/UB/tempo frente ao melhor comparador PAREADO, nenhum erro de viabilidade, callback medianamente <50% do tempo e cobertura suficiente; exigir não regressão em ≥4/6 comparáveis como critério secundário, não teto absoluto de LB* de outra execução. STOP se custo de callback >50% sistematicamente, nenhum ganho e retrocesso em ≥3 casos; INCONCLUSIVE se tempo/variância impedirem atribuição.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
