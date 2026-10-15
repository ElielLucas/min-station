# AS17 — Piloto MIP de H2 na raiz sobre COMP+K — Specification

**Status:** NOT_AUTHORIZED — bloqueada pelo gate AS16; NÃO EXECUTADA  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** AS16 GO explícito  
**Local:** `specs/as-17-piloto-mip-h2/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; **não é resultado executado**.

## Problem Statement

Aumento de limite LP não garante melhora da busca inteira. É necessário medir H2 na raiz sobre COMP+K com custo completo e validar incumbentes físicos, sem contaminar o solver por mudanças simultâneas.

## Goals

- [ ] Avaliar COMP+K versus COMP+K+H2 na raiz com orçamento total e solver iguais.
- [ ] Registrar limites, incumbentes físicos, gap, nós, memória e evolução do bound após cortes do solver.
- [ ] Autorizar replicação 600s/seeds somente com sinal robusto e auditar regressões.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Sem separação em toda árvore na primeira campanha, sem C, sem 3600s antes de decisão formal e sem alterar freezes. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Piloto | 300s totais por braço nos seis casos de desenvolvimento | Conforme AS-00, sem campanha grande prematura | Não — premissa de planejamento |
| Injeção de cortes | Estática na raiz antes da busca MIP, com mesmos parâmetros Gurobi | Evita callback complexo antecipado | Não — premissa de planejamento |
| Replicação | 600s e seeds 42/43/44 apenas com indícios replicáveis | Previne extrapolação de 1 seed | Não — premissa de planejamento |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Avaliação MIP

**User Story:** Como pesquisador do MIN-STATION, quero avaliar comp+k versus comp+k+h2 na raiz com orçamento total e solver iguais para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS17-01:** WHEN H2 for ativado THEN o modelo MIP SHALL manter todas as restrições de COMP+K e apenas acrescentar linhas H2 certificadas.
2. **AS17-02:** WHEN um orçamento de 300s for aplicado THEN o tempo total SHALL incluir preparação, K, oráculo, separação, resolução e validação física.
3. **AS17-03:** WHEN uma incumbente for reportada THEN o relatório SHALL computar UB apenas se a solução inteira for fisicamente validada.
4. **AS17-04:** WHEN o solver encerrar THEN o relatório SHALL preservar status, LB, UB validada, gap, tempo, nós, memória e primeira incumbente, com censura explícita.
5. **AS17-05:** WHEN H2 apresentar ganho no LP puro THEN a análise SHALL verificar separadamente se o ganho persiste depois dos cortes automáticos na raiz.
6. **AS17-06:** IF H2 falhar, expirar orçamento ou exceder memória THEN o runner SHALL manter a semântica intacta de COMP+K e registrar falha ou abstenção sem inventar bound.
7. **AS17-07:** WHEN evidência favorável justificar replicação THEN o protocolo SHALL repetir com seeds 42, 43 e 44 e 600s, mantendo braços pareados.
8. **AS17-08:** WHEN a etapa terminar THEN o relatório SHALL atribuir GO, STOP ou INVESTIGATE com todas as regressões e resultados censurados.

**Independent Test:**

- Build de MIP COMP+K sem H2 deve coincidir com controle histórico nas microinstâncias.
- H2 raiz em HB não altera conjunto de soluções inteiras viáveis; ótimo preservado.
- Simular VALIDATION_FAIL e TIME_LIMIT; nenhuma UB não validada entra no gap.
- Zero cortes e orçamento de separação esgotado não devem excluir soluções viáveis.
- Comparação de root bound antes/depois de cuts nativos do solver com etiquetas corretas.

## Edge Cases

- Build de MIP COMP+K sem H2 deve coincidir com controle histórico nas microinstâncias.
- H2 raiz em HB não altera conjunto de soluções inteiras viáveis; ótimo preservado.
- Simular VALIDATION_FAIL e TIME_LIMIT; nenhuma UB não validada entra no gap.
- Zero cortes e orçamento de separação esgotado não devem excluir soluções viáveis.
- Comparação de root bound antes/depois de cuts nativos do solver com etiquetas corretas.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS17-01 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-02 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-03 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-04 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-05 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-06 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-07 | P1: Avaliação MIP | Tarefas | Pending |
| AS17-08 | P1: Avaliação MIP | Tarefas | Pending |

**Coverage:** 8 requisitos; 8 com critérios explícitos; todos pendentes de execução e evidência.

## Success Criteria

- [ ] Todas as exigências dos ACs são verificadas com testes derivados da spec, não espelhados do código.
- [ ] Gate: GO condicionado a benefício MIP replicável sem invalidar incumbentes; se H2 só melhora LP, registrar conclusão parcial e STOP para expansão da busca. Sem passagem automática para 3600s.
- [ ] Parecer independente (autor ≠ verificador) reporta evidência por requisito e falhas/abstenções.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS17-01:** WHEN H2 for ativado THEN o modelo MIP SHALL manter todas as restrições de COMP+K e apenas acrescentar linhas H2 certificadas.
- **AS17-02:** WHEN um orçamento de 300s for aplicado THEN o tempo total SHALL incluir preparação, K, oráculo, separação, resolução e validação física.
- **AS17-03:** WHEN uma incumbente for reportada THEN o relatório SHALL computar UB apenas se a solução inteira for fisicamente validada.
- **AS17-04:** WHEN o solver encerrar THEN o relatório SHALL preservar status, LB, UB validada, gap, tempo, nós, memória e primeira incumbente, com censura explícita.
- **AS17-05:** WHEN H2 apresentar ganho no LP puro THEN a análise SHALL verificar separadamente se o ganho persiste depois dos cortes automáticos na raiz.
- **AS17-06:** IF H2 falhar, expirar orçamento ou exceder memória THEN o runner SHALL manter a semântica intacta de COMP+K e registrar falha ou abstenção sem inventar bound.
- **AS17-07:** WHEN evidência favorável justificar replicação THEN o protocolo SHALL repetir com seeds 42, 43 e 44 e 600s, mantendo braços pareados.
- **AS17-08:** WHEN a etapa terminar THEN o relatório SHALL atribuir GO, STOP ou INVESTIGATE com todas as regressões e resultados censurados.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entradas | Instância física, S/T/r, vértices permitidos, parâmetros e suportes dentro do domínio da etapa. |
| Falhas parciais | UNKNOWN/timeouts/erros não equivalem a prova de viabilidade ou inviabilidade; censura explícita. |
| Idempotência | Hash de instância, cortes em ordem canônica e artefatos de saída imutáveis/novos. |
| Concorrência | Ordem estável de chamadas, seeds e configuração explícitas; nunca depender do hash seed. |
| Ciclo de dados | Resultados append-only e jamais sobrescrever N1/N2/FC nem freezes antigos. |
| Observabilidade | Contadores de chamadas, tempo, fingerprint, status e evidência de gate. |
| Autenticação | N/A: experimentação local sem serviço de autenticação próprio. |
| Integridade de estados | Gate GO/STOP/INVESTIGATE/UNPROVEN/NOT_AUTHORIZED rastreável. |

## Scientific Invariants

COMP (U) e COMP+K (U_K) com variáveis binárias de instalação em V, fluxo contínuo, autonomia comum inteira, grafo físico principal não direcionado e unitário, robôs anônimos, S∩T permitido, sem capacidade nas estações.

- A desigualdade só é considerada válida com prova matemática e/ou certificado conservador; testes numéricos não substituem demonstração.
- Preservar distinção entre prova, witness analítico, ótimo LP, bound MIP e UB validada.
- Nenhuma afirmação de contribuição inédita sem revisão bibliográfica específica.

## Encaminhamento após AS16 (15/10/2026)

A AS16 foi encerrada por decisão científica `STOP`, com gate automático `INVESTIGATE` preservado. Como esta spec requer **GO explícito**, o piloto MIP H2 **não está autorizado** e permanece sem implementação/experimentos. Todos os critérios AS17-01 a AS17-08 estão **não verificados**, não concluídos. Evidência em `validation.md` e na síntese `docs/technical/reference/experimentos/as18-sintese-h2-hl.md`. Reabertura exige novo protocolo, não reaproveitamento retroativo de AS16.
