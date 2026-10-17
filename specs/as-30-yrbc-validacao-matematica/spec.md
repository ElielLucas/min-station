# AS30 — Auditoria matemática das reduções e do Y-RBC

**Estado:** DRAFT — bloqueada até AS29/G0 PASS, ainda não executada.
**Gate:** G1 — Correção provada e microvalidada.
**Dependências:** AS29/G0 PASS; código experimental NÃO liberado.
**Esforço estimado:** 2–4 dias, incerteza média.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

A construção Y-RBC apoia-se em três afirmações matemáticas ainda não auditadas independentemente: dominância de vizinhanças fechadas em H, projeção do fluxo por BF e validade de BR, inclusive quando S∩T não é vazio. Uma redução incorreta pode excluir o ótimo e invalidar toda a futura campanha.

## Goals

- [ ] Provar ou refutar R-dom, BF e BR na semântica original de Das e em todos os casos de terminais.
- [ ] Estabelecer casos-testemunha e oráculos independentes que detectem exclusão de um ótimo ou de instalação fisicamente viável.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Benchmarks reais | G1 é matemático; performance é G2a/G2b. |
| Integrar callbacks no solver | A arquitetura só será autorizada após prova e gates. |
| Assumir que uma família domina outra | Qualquer inclusão poliédrica precisa de prova específica. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Grafo e alcance | G não direcionado, H=G^r simétrico, autonomia comum | A prova R-dom não pode ser generalizada automaticamente a extensões dirigidas. | Não — revisar antes de Execute |
| Dominância simultânea | Aplicar cadeia estrita/ordem total entre gêmeos e provar solução sobrevivente | Evitar fixar os dois representantes da mesma classe. | Não — revisar antes de Execute |
| Semântica de terminais | Extremos gratuitos, trânsito exige estação; S∩T admite caminho vazio | Evita erro em cortes de max-flow e poda de arcos. | Não — revisar antes de Execute |
| Capacidade da rede | Usar κ_v da implementação validada para cada papel do vértice | κ é capacidade técnica do fluxo, não capacidade física. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Demonstrar a correção de fixações

**User Story:** Como pesquisador, quero fixar instalações dominadas sem perder o ótimo físico.

**Acceptance Criteria**

1. WHEN R-dom fixar um vértice THEN a prova SHALL construir transformação de qualquer ótimo para outro ótimo que não o utiliza.
2. WHEN vizinhanças fechadas forem iguais THEN o desempate SHALL preservar um representante e SHALL evitar ciclos de substituição.
3. IF um vértice fixado pertencer a S ou T THEN a construção SHALL preservar seu uso como origem/destino gratuito sem permitir trânsito grátis.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Validar projeção e oráculo

**User Story:** Como pesquisador, quero comprovar que BF/BR não excluem soluções físicas válidas.

**Acceptance Criteria**

1. WHEN um BF for gerado a partir de um corte finito de N(y) THEN o certificado SHALL indicar Z, κ, c0, deficiência e validade sob S∩T.
2. WHEN um BR for gerado THEN o verificador SHALL provar que V\Z é inviável e que o suporte da instalação incumbente violada não intersecta Z.
3. IF qualquer microinstância n≤5 contradisser a prova THEN o gate G1 SHALL ser BLOCKED e a redução/corte SHALL ser rejeitado.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR30-01 | P1: Demonstrar a correção de fixações | Specify/Design/Tasks | Pending | T1, T4 |
| YR30-02 | P1: Demonstrar a correção de fixações | Specify/Design/Tasks | Pending | T1, T4 |
| YR30-03 | P1: Demonstrar a correção de fixações | Specify/Design/Tasks | Pending | T1, T4 |
| YR30-04 | P2: Validar projeção e oráculo | Specify/Design/Tasks | Pending | T2, T4 |
| YR30-05 | P2: Validar projeção e oráculo | Specify/Design/Tasks | Pending | T2, T4 |
| YR30-06 | P2: Validar projeção e oráculo | Specify/Design/Tasks | Pending | T3, T4 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G1 PASS apenas se nenhuma instalação física válida excluída, nenhum ótimo perdido na bateria exaustiva, prova R-dom e BF/BR completas com S∩T, validação independente e testes anti-mutação. Qualquer contraexemplo ou prova incompleta => G1 BLOCKED; não executar AS31.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
