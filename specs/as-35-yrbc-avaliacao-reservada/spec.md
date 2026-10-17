# AS35 — Avaliação independente congelada de Y-RBC

**Estado:** BLOQUEADA — G4 GO e freeze verificado.
**Gate:** G5 — Generalização fora de desenvolvimento.
**Dependências:** AS34/G4 GO aprovado; freeze commit + hash + política + critérios.
**Esforço estimado:** 1 semana + computação, alta incerteza.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

O histórico de cortes foi construído em poucos grafos de desenvolvimento. A contribuição só pode ser generalizada depois de testar política integralmente congelada em instâncias de avaliação não utilizadas para seleção/ajuste.

## Goals

- [ ] Avaliar generalização de Y-RBC em partição reservada sem usar resultados para retuning.
- [ ] Produzir relatório auditável de ganho/risco e delimitação por classe de instância, inclusive censuras.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Alterar parâmetros após resultado reservado | Configuraria vazamento do conjunto de avaliação. |
| Reabrir FC-R/C3 ou AS26 por resultado de Y-RBC | São programas distintos e gates separados. |
| Declarar superioridade universal | Conclusões apenas na amostra e configurações efetivas. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Freeze | Commit, hashes, dependências, solver e protocolo assinados antes da primeira instância reservada | Evitar vazamento. | Não — revisar antes de Execute |
| Cobertura | Toda a partição elegível congelada, com orçamento igual ao comparador | Não filtrar a posteriori. | Não — revisar antes de Execute |
| Revisão | Verificador separado da implementação confirma integridade e estatísticas | Evidência independente. | Não — revisar antes de Execute |
| Falhas | Se houver incidente de integridade, parar e relatar; nova campanha é separada | Preservar valor confirmatório. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Avaliar sem vazamento

**User Story:** Como pesquisador, quero testar a política numa partição não utilizada para desenvolver Y-RBC.

**Acceptance Criteria**

1. WHEN AS35 iniciar THEN o executor SHALL verificar freeze de commit, hash do protocolo, lista de instâncias e parâmetros antes de ler resultados da partição reservada.
2. WHEN a avaliação ocorrer THEN o comparador SHALL executar os braços aprovados sobre todas as instâncias elegíveis com budgets iguais.
3. IF houver mudança após abertura da reserva THEN o relatório SHALL declarar a avaliação comprometida e SHALL impedir promoção automática de ganho.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Publicar a evidência definitiva

**User Story:** Como pesquisador, quero determinar se o algoritmo melhora consistentemente a solução exata.

**Acceptance Criteria**

1. WHEN a campanha terminar THEN o relatório SHALL expor bounds, incumbentes validadas, gaps, tempos, nós, custos e censuras por classe e por instância.
2. WHEN o verificador revisar os resultados THEN ele SHALL conferir a validade física, hashes e decisão GO/STOP e SHALL separar inferência matemática de ganho computacional.
3. IF a generalização falhar THEN o relatório SHALL recomendar encerrar/limitar o escopo e preservar resultados negativos completos.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR35-01 | P1: Avaliar sem vazamento | Specify/Design/Tasks | Pending | T1, T2 |
| YR35-02 | P1: Avaliar sem vazamento | Specify/Design/Tasks | Pending | T2, T3 |
| YR35-03 | P1: Avaliar sem vazamento | Specify/Design/Tasks | Pending | T1, T2, T3 |
| YR35-04 | P2: Publicar a evidência definitiva | Specify/Design/Tasks | Pending | T4 |
| YR35-05 | P2: Publicar a evidência definitiva | Specify/Design/Tasks | Pending | T4 |
| YR35-06 | P2: Publicar a evidência definitiva | Specify/Design/Tasks | Pending | T4 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G5 PASS técnico: 100% dos resultados rastreáveis ao freeze e 100% das incumbentes declaradas fisicamente válidas; verificação independente concluída. GO científico apenas com evidência robusta em reserva, sem omissões e com comparação justa. Caso contrário STOP, INCONCLUSIVE ou INVALIDATED (vazamento), nunca retuning silencioso.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
