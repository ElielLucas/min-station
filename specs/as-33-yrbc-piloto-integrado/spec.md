# AS33 — Piloto integrado com callbacks e telemetria

**Estado:** BLOQUEADA — G2b GO + revisão independente.
**Gate:** G3 — Integração estável.
**Dependências:** AS32/G2b GO aprovado; validação matemática AS30 continua válida.
**Esforço estimado:** 1–2 semanas, alta incerteza.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

Uma triagem de potencial não garante robustez do algoritmo em execução inteira completa. O piloto deve tornar Y-RBC reprodutível, medível e seguro, com mecanismos de cortes no callback e ablações de tempo e memória.

## Goals

- [ ] Implementar integração sustentada de callbacks e métricas por estágio com abortos seguros.
- [ ] Comprovar reprodutibilidade e validade de todas as incumbentes relatadas em lote de desenvolvimento.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Avaliação reservada | É exclusiva AS35. |
| Otimizar para cada instância depois de observar o desempenho | Política deve ser global e pré-registrada. |
| Alterar conceito de viabilidade do Das | Oráculo segue a mesma semântica do modelo. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Estabilidade | Callbacks devem respeitar WorkLimit e timeout externo, inclusive tempo gasto em Python | Evitar repetir estouro de prazo E7. | Não — revisar antes de Execute |
| Telemetry | Registrar tempo callback, max-flow, presolve, extração, cortes, LP de raiz, nós, RSS | Permitir identificar gargalos sem inferência intuitiva. | Não — revisar antes de Execute |
| Discriminação | Ablar componentes separadamente, sem misturar ganhos | Entender o que realmente melhora. | Não — revisar antes de Execute |
| G3 | É gate de robustez, não confirmação final de ganho científico | Resultados de AS34 decidirão competição. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Instrumentar uma versão robusta

**User Story:** Como pesquisador, quero executar Y-RBC com limites estáveis e rastreabilidade.

**Acceptance Criteria**

1. WHEN o solver encerrar THEN o registro SHALL conter hash, commit, seed, work/tempo, status, LB, UB validada, nós e breakdown dos callbacks.
2. IF um callback exceder orçamento ou falhar THEN o executor SHALL registrar censura/erro seguro e SHALL nunca promover incumbente sem validação.
3. WHEN diferentes modalidades de cortes estiverem ativas THEN os logs SHALL identificar BF, BR, K, reduções e heurística separadamente.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Conferir qualidade e degradações

**User Story:** Como pesquisador, quero saber se a implementação estabilizada reproduz o protótipo correto.

**Acceptance Criteria**

1. WHEN G3 for auditado THEN o verificador independente SHALL executar testes de microinstâncias e comparar incumbentes com oráculo físico.
2. WHEN o piloto for repetido em sementes fixas THEN a classificação SHALL registrar dispersão de tempo, bound e variância sem eliminar censuras.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR33-01 | P1: Instrumentar uma versão robusta | Specify/Design/Tasks | Pending | T1, T2 |
| YR33-02 | P1: Instrumentar uma versão robusta | Specify/Design/Tasks | Pending | T2, T3 |
| YR33-03 | P1: Instrumentar uma versão robusta | Specify/Design/Tasks | Pending | T1, T3 |
| YR33-04 | P2: Conferir qualidade e degradações | Specify/Design/Tasks | Pending | T3, T4 |
| YR33-05 | P2: Conferir qualidade e degradações | Specify/Design/Tasks | Pending | T4 |

**Coverage:** 5 critérios rastreados; implementação e validação pendentes.

## Success Criteria

- [ ] G3 PASS somente com zero incumbente fisicamente inválida, zero corte errado, saída reproduzível e trace completo para todos os casos concluídos; tempo callback conhecido e guardas auditadas. G3 BLOCKED com falha de corretude ou registros incompletos; resultado computacional ruim é STOP científico, não bug encoberto.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
