# AS16 — Piloto LP pareado COMP, K e H2 — Specification

**Status:** EXPERIMENTO EXECUTADO / DOCUMENTAÇÃO DE ENCERRAMENTO (gate automático `INVESTIGATE`; decisão de pesquisa `STOP`)  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** AS13–AS15 GO  
**Local:** `specs/as-16-piloto-lp-h2/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; **não é resultado executado**.

## Problem Statement

H2 pode fortalecer formalmente o relaxamento em casos sintéticos, mas não sabemos se os suportes úteis aparecem em instâncias difíceis ou se o custo de separação compensa o ganho no bound.

## Goals

- [x] Pré-registrar seis instâncias de desenvolvimento do AS-00 e quatro braços comparáveis.
- [x] Medir ganho líquido de LP com separação e custos totais explicitados (com censuras preservadas).
- [x] Registrar gate automático `INVESTIGATE` e decisão de pesquisa `STOP`, com evidência por grafo bruto e ressalvas.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Não utilizar Formulação C, não executar MIP e não alterar conjunto de avaliação congelada. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Braços | U, U+K, U+H2, U+K+H2 | Isola efeito de H2 e interação com K | Não — premissa de planejamento |
| Tempo | 90s totais por braço LP, com orçamento interno para separação | Preserva regra AS-00; ajustes precisam de novo plano | Não — premissa de planejamento |
| Triagem GO | Ganho LP objetivo >=1% em pelo menos dois grafos brutos independentes e ganho não anulado pelo custo em pelo menos um | Threshold pré-registrado exploratório, sujeito a revisão antes de rodar | Não — premissa de planejamento |
| Resultado negativo | STOP e relatório completo inclusive censuras/UNKNOWN | Evita avançar automaticamente a MIP | Não — premissa de planejamento |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Avaliação LP

**User Story:** Como pesquisador do MIN-STATION, quero pré-registrar seis instâncias de desenvolvimento do as-00 e quatro braços comparáveis para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS16-01:** WHEN o plano experimental for congelado THEN o runner SHALL registrar instâncias, SHA, versões dos cortes, seeds, threads, orçamento e parâmetros Gurobi.
2. **AS16-02:** WHEN um braço U+H2 usar K apenas para orientar suportes THEN o runner SHALL contabilizar o custo de preparar K mesmo sem adicionar K ao modelo.
3. **AS16-03:** WHEN o LP for resolvido THEN o relatório SHALL separar ganho absoluto/relativo, tempo de alcance, K, seleção, certificação, reotimização e tempo total.
4. **AS16-04:** WHEN dois braços forem comparados THEN a análise SHALL usar as mesmas instâncias, política de solver e orçamento total, isolando o fator H2.
5. **AS16-05:** WHEN um LP atingir limite, memória ou estado desconhecido THEN a análise SHALL preservar a censura e SHALL impedir tratá-la como objetivo ótimo.
6. **AS16-06:** WHEN forem avaliados cortes H2 THEN o relatório SHALL distinguir candidatos, certificados, violados, aceitos, redundantes e não testados.
7. **AS16-07:** WHEN um ganho de H2 for atribuído THEN a análise SHALL incluir controle de mesmo pool de cortes para distinguir efeito algébrico do processo de separação.
8. **AS16-08:** WHEN o piloto terminar THEN o gate SHALL emitir GO, STOP ou INVESTIGATE com critério quantitativo e origem independente explícitos.

**Independent Test:**

- Smoke com duas instâncias; controle de hash, limite de tempo e relatórios de 4 braços.
- Run replay com mesmo plano gera mesmas identidades de braços e não sobrescreve artefatos.
- Injeção de TIME_LIMIT, OOM, UNKNOWN e separação sem corte; relatório preserva linhas.
- Comparação same-pool vs sob demanda; checagem de ganho matemático e custo total.

## Edge Cases

- Smoke com duas instâncias; controle de hash, limite de tempo e relatórios de 4 braços.
- Run replay com mesmo plano gera mesmas identidades de braços e não sobrescreve artefatos.
- Injeção de TIME_LIMIT, OOM, UNKNOWN e separação sem corte; relatório preserva linhas.
- Comparação same-pool vs sob demanda; checagem de ganho matemático e custo total.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS16-01 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-02 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-03 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-04 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-05 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-06 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-07 | P1: Avaliação LP | Tarefas | Evidence recorded |
| AS16-08 | P1: Avaliação LP | Tarefas | Evidence recorded |

**Coverage:** 8 requisitos; 8 com critérios explícitos; execução e evidências registradas em `validation.md`. Revisão humana independente continua sem comprovação.

## Success Criteria

- [ ] Todas as exigências dos ACs são verificadas com testes derivados da spec, não espelhados do código.
- [ ] Gate: GO somente com ≥1% de melhoria de LB em ≥2 grafos brutos independentes e evidência de custo líquido aceitável em ≥1; senão STOP; INVESTIGATE por erros/censura inconclusiva.
- [ ] Parecer independente (autor ≠ verificador) reporta evidência por requisito e falhas/abstenções.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS16-01:** WHEN o plano experimental for congelado THEN o runner SHALL registrar instâncias, SHA, versões dos cortes, seeds, threads, orçamento e parâmetros Gurobi.
- **AS16-02:** WHEN um braço U+H2 usar K apenas para orientar suportes THEN o runner SHALL contabilizar o custo de preparar K mesmo sem adicionar K ao modelo.
- **AS16-03:** WHEN o LP for resolvido THEN o relatório SHALL separar ganho absoluto/relativo, tempo de alcance, K, seleção, certificação, reotimização e tempo total.
- **AS16-04:** WHEN dois braços forem comparados THEN a análise SHALL usar as mesmas instâncias, política de solver e orçamento total, isolando o fator H2.
- **AS16-05:** WHEN um LP atingir limite, memória ou estado desconhecido THEN a análise SHALL preservar a censura e SHALL impedir tratá-la como objetivo ótimo.
- **AS16-06:** WHEN forem avaliados cortes H2 THEN o relatório SHALL distinguir candidatos, certificados, violados, aceitos, redundantes e não testados.
- **AS16-07:** WHEN um ganho de H2 for atribuído THEN a análise SHALL incluir controle de mesmo pool de cortes para distinguir efeito algébrico do processo de separação.
- **AS16-08:** WHEN o piloto terminar THEN o gate SHALL emitir GO, STOP ou INVESTIGATE com critério quantitativo e origem independente explícitos.

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

## Fechamento experimental (15/10/2026)

A campanha real produziu 36 linhas. O gate automatizado foi `INVESTIGATE` devido a TIME_LIMIT/NOT_RUN. A comparação U+K → U+K+H2 teve ganho zero nos cinco grafos com ambos ótimos; é impossível atingir o mínimo de dois grafos com ganho na amostra fixa restante. Decisão de pesquisa: `STOP` para novas rodadas/priorização de H2 neste protocolo, **sem adulterar o gate**, sem promover H2 e sem alegar revisão independente concluída. Detalhes e tempos em `docs/technical/reference/experimentos/as16-resultado-lp-h2.md`.
