# AS34 — Comparação confirmatória entre algoritmos exatos

**Estado:** BLOQUEADA — G3 PASS e política congelada.
**Gate:** G4 — Competitividade reproduzida.
**Dependências:** AS33/G3 PASS e autorização científica explícita para campanha maior.
**Esforço estimado:** 1 semana + computação, alta incerteza.
**Método:** `/tlc-spec-driven` — Specify → Design → Tasks; Execute NÃO iniciado.
**Semântica:** MIN-STATION de Das; estações em todo `V`, autonomia comum e `S∩T` permitido.

## Problem Statement

Uma melhora em poucas instâncias de desenvolvimento pode desaparecer com seeds diferentes e limites de trabalho mais longos. A comparação confirmatória precisa determinar se Y-RBC é competitivo com COMP+K, núcleo e BC-y/CBI sem misturar resultados não comparáveis.

## Goals

- [ ] Comparar sob mesmo orçamento e dados, com três sementes e matriz de casos de desenvolvimento pré-registrada.
- [ ] Escolher uma versão congelada de Y-RBC apenas se houver ganho suficientemente robusto para justificar avaliação reservada.

## Out of Scope

| Não fazer | Justificativa |
|---|---|
| Usar partição avaliação | Somente AS35. |
| Ajustar políticas a cada instância do teste confirmatório | Seria exploração pós-hoc, não confirmação. |
| Declarar solução ótima sem bound válido | Status e prova devem corresponder à instância física. |

## Assumptions & Open Questions

| Premissa / decisão | Chosen default | Rationale | Confirmed? |
|---|---|---|---|---|
| Campanha | WorkLimit/TimeLimit/threads/seed iguais entre braços; comparar 600s só quando factível | Alinhamento com análise histórica e orçamento disponível. | Não — revisar antes de Execute |
| Braços | COMP original, COMP+K, núcleo IP, BC-y/CBI e Y-RBC | Medir envelope e ganhos incrementais. | Não — revisar antes de Execute |
| Mérito | Performance objetiva: bounds inteiros, UB, gap, tempo até prova, robustez | Não fazer ganho LP puro decidir MIP. | Não — revisar antes de Execute |
| Reserva | É separada e só aberta depois da decisão G4 | Generalização genuína. | Não — revisar antes de Execute |

**Open questions: none — defaults acima estão registrados e dependem de revisão/aprovação, não de execução tácita.**

## User Stories

### P1: Executar comparação justa

**User Story:** Como pesquisador, quero uma evidência reprodutível de competitividade.

**Acceptance Criteria**

1. WHEN um braço rodar THEN a campanha SHALL usar orçamento, seed, versão do solver e definição física comparáveis aos demais braços.
2. WHEN o núcleo reportar incumbente THEN o relatório SHALL tratá-la somente como limite de cobertura, salvo validação física independente.
3. IF um braço encerrar por limite THEN o analisador SHALL conservar a censura e o melhor bound válido, sem concluir pior desempenho por falta de ótimo.

**Independent Test:** demonstrar os critérios de P1 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

### P2: Escolher se existe contribuição

**User Story:** Como pesquisador, quero decidir se Y-RBC merece avaliação independente.

**Acceptance Criteria**

1. WHEN G4 for calculado THEN o relatório SHALL apresentar ganhos por caso, razões de tempo apenas para pares comparáveis e intervalo de variância entre seeds.
2. IF a vantagem for só em uma instância ou baseada em sonda pós-hoc THEN o gate SHALL recomendar STOP/INCONCLUSIVE, não liberar AS35.
3. WHEN houver sinal sólido no conjunto de desenvolvimento THEN a política SHALL ser congelada e revisada antes de abrir dados reservados.

**Independent Test:** demonstrar os critérios de P2 pelos arquivos de evidência e verificações previstas nas tarefas, sem inferir sucesso de implementação não executada.

## Edge Cases

- **Dados incompletos:** status INCONCLUSIVE/BLOCKED; não estimar números faltantes.
- **Terminal em S∩T:** zero deslocamento é permitido, trânsito de terceiros depende de estação.
- **Censura/limite de trabalho:** jamais converter em ganho zero ou resultado ótimo.
- **Fonte histórica divergente:** registrar conflito antes de comparar.

## Requirement Traceability

| Requirement ID | Story | Phase | Status | Tasks |
|---|---|---|---|---|
| YR34-01 | P1: Executar comparação justa | Specify/Design/Tasks | Pending | T1, T2 |
| YR34-02 | P1: Executar comparação justa | Specify/Design/Tasks | Pending | T2 |
| YR34-03 | P1: Executar comparação justa | Specify/Design/Tasks | Pending | T1, T2 |
| YR34-04 | P2: Escolher se existe contribuição | Specify/Design/Tasks | Pending | T3, T4 |
| YR34-05 | P2: Escolher se existe contribuição | Specify/Design/Tasks | Pending | T3, T4 |
| YR34-06 | P2: Escolher se existe contribuição | Specify/Design/Tasks | Pending | T3, T4 |

**Coverage:** 6 critérios rastreados, 6 mapeados a tarefas; implementação e validação pendentes.

## Success Criteria

- [ ] G4 GO: vantagem estatística/operacional consistente em ≥2 grafos brutos independentes e ≥2 sementes por caso, sem invalidez física, sem regressão grave no conjunto e com ganhos relevantes no LB, UB, gap ou tempo; thresholds operacionais deverão ser congelados numericamente no pré-registro antes do solve. STOP se não houver melhoria robusta ou houver custo superior sem benefício; INCONCLUSIVE se censuras dominarem.
- [ ] Revisor independente confirma evidências por requisito; nenhum `validation.md` será criado antes de validação efetiva.
- [ ] Não alterar histórico AS25–AS28, não liberar AS26, não acessar instâncias reservadas antes de AS35.

## Fontes e escopo

- `docs/technical/reference/tecnico/parecer-astra-pos-as28-yrbc.md` — hipótese externa sob revisão.
- `docs/technical/plans/execucao/plano-yrbc-as29-as35.md` — dependências e gates.
- `RESEARCH.md`, `CLAUDE.md`, `docs/context-ai/base-formulation.md` — semântica do problema.
- Specs anteriores e JSONs experimentais permanecem fontes primárias do que já foi executado.

> **Não iniciado:** todos os checkboxes de aceite ficam desmarcados. Aprovar a spec não implica autorização de benchmark, push ou uso da partição reservada.
