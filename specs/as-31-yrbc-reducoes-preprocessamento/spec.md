# AS31 — Piloto pareado de reduções seguras

**Estado:** BLOQUEADA — requer G0+G1 PASS e pré-registro.
**Gate:** G2a — Relevância computacional da dominância.
**Dependências:** AS29/G0 PASS; AS30/G1 PASS; autorização explícita do pesquisador para campanha.
**Esforço estimado:** 2–3 dias + tempo Gurobi, incerteza média.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

As sondas do Astra fixaram 68,3% de candidatos em Vienna e 48,4% em MAPF Room, mas usaram uma seed, sem pré-registro. Reduções antigas do projeto tiveram resultados mistos. É necessário separar ganho de tamanho, raiz e MIP em uma comparação controlada, sem alterar a semântica física.

## Goals

- [ ] Medir R-dom isoladamente em instâncias principais de desenvolvimento e comparar ao pré-processamento histórico.
- [ ] Decidir GO/STOP sobre a redução com métricas objetivas e sem contaminação da partição reservada.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Y-RBC completo | Não combinar BF/BR ou heurísticas nesta etapa. |
| Selecionar casos por ganho visto | A política e os casos são congelados antes da execução. |
| Usar casos de avaliação | Preservar blind test AS35. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Cobertura | Somente partição desenvolvimento, com vários regimes; nenhum gráfico reservado nesta etapa | Separar desenvolvimento de avaliação. | Não — revisar antes de Execute |
| Orçamento | Usar WorkLimit da baseline em protocolo pareado; tempo guarda e três sementes pré-registradas | Comparabilidade e repetibilidade. | Não — revisar antes de Execute |
| Comparadores | COMP+K sem redução, COMP+K + R-dom, e histórico de pré-processamento quando compatível | Atribuir a melhora à redução nova. | Não — revisar antes de Execute |
| Status científico | Um ganho de LP raiz isolado não autoriza AS32 se houver regressão MIP sistemática | Priorizar algoritmo inteiro. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Executar reduções de maneira controlada

**User Story:** Como pesquisador, quero medir se reduzir a rede preserva o ótimo e diminui custo.

**Acceptance Criteria**

1. WHEN uma instância de desenvolvimento entrar na campanha THEN o runner SHALL registrar hash, fixações, arcos removidos, LP raiz, bound MIP e solução incumbente validada.
2. WHEN dois braços forem comparados THEN o protocolo SHALL manter seed, threads, WorkLimit, start, presolve e versão compatíveis.
3. IF o pré-registro ou hash divergirem THEN a execução SHALL abortar antes de gerar uma comparação qualificável.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Decidir G2a com censuras

**User Story:** Como pesquisador, quero tomar decisão sem escolher somente o caso favorável.

**Acceptance Criteria**

1. WHEN a campanha terminar THEN o analisador SHALL informar resultados pareados e censuras, sem converter timeout em ganho zero.
2. WHEN duas instâncias independentes apresentarem ganho relevante sem regressão sistemática THEN o parecer SHALL marcar GO_CANDIDATE_REVIEW, nunca autorização automática AS32.
3. IF não houver benefício MIP verificável e as reduções forem pequenas nos casos fora de PUC THEN o parecer SHALL recomendar STOP ou INCONCLUSIVE conforme a cobertura.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR31-01 | P1: Executar reduções de maneira controlada | Specify/Design/Tasks | Pending | T2, T4 |
| YR31-02 | P1: Executar reduções de maneira controlada | Specify/Design/Tasks | Pending | T2, T4 |
| YR31-03 | P1: Executar reduções de maneira controlada | Specify/Design/Tasks | Pending | T1, T4 |
| YR31-04 | P2: Decidir G2a com censuras | Specify/Design/Tasks | Pending | T3, T5 |
| YR31-05 | P2: Decidir G2a com censuras | Specify/Design/Tasks | Pending | T3, T5 |
| YR31-06 | P2: Decidir G2a com censuras | Specify/Design/Tasks | Pending | T3, T5 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G2a GO_CANDIDATE_REVIEW se ≥2 grafos brutos independentes apresentarem redução ≥50% no tempo de raiz sem piorar bound, OU melhora de tempo até OPT ≥2×, OU melhora inteira de LB/UB ≥1 estação, com evidência MIP e sem regressão grave em outros casos. STOP se não houver efeito de MIP e pouca redução útil fora de PUC; INCONCLUSIVE em censuras/variabilidade. Revisão humana autoriza AS32 somente após GO.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
