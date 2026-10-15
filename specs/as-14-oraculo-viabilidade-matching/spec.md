# AS14 — Oráculo certificado de viabilidade para suportes H2/HL — Specification

**Status:** R1 STOP — 6 correções executadas localmente; nova revisão independente e Ruff pendentes  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** AS13 GO matemático (R3 PASS, informado pelo autor)  
**Local:** `specs/as-14-oraculo-viabilidade-matching/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; implementação e verificações locais AS14 registradas em `implementation-evidence.md`.

## Problem Statement

Os novos cortes dependem de testes de viabilidade com todas as estações fora de R disponíveis. Um oráculo parcial, caro ou semanticamente errado pode produzir cortes inválidos ou enviesar a avaliação.

## Goals

- [x] Reutilizar a verificação física existente e expor contrato de matching exato com resultado triestado.
- [x] Validar monotonicidade, classificação de suportes e certificados sob orçamento finito.
- [x] Medir custo de oráculo e manter cache/proveniência de entradas canônicas.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Nenhuma busca heurística de suportes, nenhuma ligação ao Gurobi e nenhuma medição de ganho MIP. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Oráculo primário | `independent_validator.destinos_alcancaveis` (bateria) + matching bipartido com certificado de Hall em `h2_oracle.py` | Reutiliza a verificação física real existente | Sim — verificado localmente |
| Resultados | VIABLE / INFEASIBLE / UNKNOWN; budget cooperativo verificado entre chamadas de alcance e operações de matching; timeout/erro => UNKNOWN | Nunca tratar ausência de prova como inviabilidade | Sim — testes unitários e mutantes locais |
| Cache | SHA-256 de V/E/S/T/r + conjunto canônico; só resultados certificados | Impede reutilização cruzada de casos | Sim — testes de isolamento e monotonicidade |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Infraestrutura de certificação

**User Story:** Como pesquisador do MIN-STATION, quero reutilizar a verificação física existente e expor contrato de matching exato com resultado triestado para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS14-01:** WHEN um conjunto permitido C for avaliado THEN o oráculo SHALL retornar VIABLE apenas se ν(C)=m tiver sido certificado.
2. **AS14-02:** WHEN ν(C)<m for demonstrado THEN o oráculo SHALL retornar INFEASIBLE com evidência da insuficiência de matching.
3. **AS14-03:** IF a chamada exceder orçamento ou falhar THEN o oráculo SHALL retornar UNKNOWN e SHALL proibir sua utilização como prova de inviabilidade.
4. **AS14-04:** WHEN um suporte R for examinado THEN o oráculo SHALL calcular o complemento V\R sobre a instância física correta.
5. **AS14-05:** WHEN um resultado for armazenado em cache THEN a chave SHALL incluir identidade da instância e representação canônica das estações permitidas.
6. **AS14-06:** WHEN a classificação parcial H2 for interrompida THEN somente vértices com INFEASIBLE certificado SHALL integrar B̂_R.
7. **AS14-07:** WHEN um conjunto C⊆C′ for usado no teste de regressão THEN uma resposta VIABLE para C SHALL impedir resposta INFEASIBLE para C′ na mesma instância.

**Independent Test:**

- Unitários de matching e permanência s=t, terminais usados como recarga, partilha ilimitada e cadeia de duas recargas.
- Exaustão em micrografos confrontando resultados com o `viavel` independente.
- Timeout/error injection: UNKNOWN jamais altera B̂_R nem emite certificado falso.
- Cache entre duas instâncias de mesmo tamanho mas grafos distintos; canonicidade de ordem.

## Edge Cases

- Unitários de matching e permanência s=t, terminais usados como recarga, partilha ilimitada e cadeia de duas recargas.
- Exaustão em micrografos confrontando resultados com o `viavel` independente.
- Timeout/error injection: UNKNOWN jamais altera B̂_R nem emite certificado falso.
- Cache entre duas instâncias de mesmo tamanho mas grafos distintos; canonicidade de ordem.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS14-01 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-02 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-03 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-04 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-05 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-06 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |
| AS14-07 | P1: Infraestrutura de certificação | Tarefas | Implemented; local tests PASS; independent review pending |

**Coverage:** 7 requisitos; 7 implementados e cobertos por testes locais; todos aguardam parecer independente de encerramento.

## Success Criteria

- [x] Testes derivados dos critérios, inclusive casos negativos independentes para terminais, budget com cache, identidade tipada e ambos os sentidos da monotonicidade; 41 testes locais e R09/R10/R23/R29/R30 detectados. As contagens isoladas não substituem cobertura qualitativa.
- [x] Pré-gate local: nenhuma divergência nas 742 máscaras auditadas; nenhum UNKNOWN promovido a INFEASIBLE. **Não constitui GO final sem parecer independente.**
- [ ] Revisor independente confirma as seis correções do parecer R1 (`validation.md §7`) e autoriza a conclusão — **R1 STOP / R2 PENDENTE**.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS14-01:** WHEN um conjunto permitido C for avaliado THEN o oráculo SHALL retornar VIABLE apenas se ν(C)=m tiver sido certificado.
- **AS14-02:** WHEN ν(C)<m for demonstrado THEN o oráculo SHALL retornar INFEASIBLE com evidência da insuficiência de matching.
- **AS14-03:** IF a chamada exceder orçamento ou falhar THEN o oráculo SHALL retornar UNKNOWN e SHALL proibir sua utilização como prova de inviabilidade.
- **AS14-04:** WHEN um suporte R for examinado THEN o oráculo SHALL calcular o complemento V\R sobre a instância física correta.
- **AS14-05:** WHEN um resultado for armazenado em cache THEN a chave SHALL incluir identidade da instância e representação canônica das estações permitidas.
- **AS14-06:** WHEN a classificação parcial H2 for interrompida THEN somente vértices com INFEASIBLE certificado SHALL integrar B̂_R.
- **AS14-07:** WHEN um conjunto C⊆C′ for usado no teste de regressão THEN uma resposta VIABLE para C SHALL impedir resposta INFEASIBLE para C′ na mesma instância.

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
