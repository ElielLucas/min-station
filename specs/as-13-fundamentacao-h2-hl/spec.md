# AS13 — Fundamentação matemática e validação independente H2/HL — Specification

**Status:** RASCUNHO / NÃO EXECUTADA  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** Nenhuma; início da linha H2/HL  
**Local:** `specs/as-13-fundamentacao-h2-hl/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; **não é resultado executado**.

## Problem Statement

Antes de desenvolver novos cortes, é necessário fechar as hipóteses sobre a viabilidade física anônima, verificar a prova de H2 e a interpretação de HL como projeção, e evitar repetir cortes anteriormente estudados.

## Goals

- [ ] Formalizar os contratos matemáticos de H2 e HL sem alterar COMP+K.
- [ ] Revisar independentemente as provas, com tratamento de S∩T e estações em V.
- [ ] Produzir testemunhas reproduzíveis de fortalecimento e controles negativos.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Sem implementação de separador, sem novas campanhas LP/MIP e sem Formulação C. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Base de viabilidade | ν(C)=m no bipartido entre cópias de S e T, construído com arcos de alcance por estações em C | Fundamenta os dois cortes; validar contra o verificador físico independente | Não — premissa de planejamento |
| Prova do ganho | Exemplos HB e quatro relés são testemunhas analíticas a auditar, não resultados computacionais | Evita converter dedução do parecer em medição | Não — premissa de planejamento |
| Originalidade | Nenhuma alegação de novidade poliédrica geral para coeficientes 0,1,2 ou cascos locais | Literatura antecedente reconhecida | Não — premissa de planejamento |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Fundamentação

**User Story:** Como pesquisador do MIN-STATION, quero formalizar os contratos matemáticos de h2 e hl sem alterar comp+k para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS13-01:** WHEN um conjunto C for classificado como fisicamente viável THEN o verificador matemático SHALL obter ν(C)=m sob a semântica anônima original.
2. **AS13-02:** WHEN H2 for derivado de um suporte R THEN a demonstração SHALL usar F=V\R, ν(F)<m e B_R={v∈R:ν(F∪{v})<m}.
3. **AS13-03:** WHEN uma escolha individual v∈B_R for classificada THEN a prova SHALL justificar coeficiente 1 em y_v e coeficiente 2 nos demais vértices de R.
4. **AS13-04:** WHEN HL for formalizado THEN a documentação SHALL provar Φ_R como projeção exata das instalações inteiras viáveis sobre R.
5. **AS13-05:** WHEN as testemunhas HB e quatro relés forem auditadas THEN o relatório SHALL separar satisfação de K, viabilidade física, ótimo LP e ótimo IP.
6. **AS13-06:** IF um contraexemplo ou hipótese não demonstrada for encontrado THEN a etapa SHALL registrar UNPROVEN e bloquear a implementação dependente.
7. **AS13-07:** WHEN o parecer de novidade for registrado THEN ele SHALL identificar o que já decorre de K, C6, CBI, CG/zero-half e de limites globais conhecidos.

**Independent Test:**

- Enumerar todas as instalações em grafos pequenos e confrontar ν(C) com verificador independente, inclusive S∩T.
- Checar prova da H2 para R=∅, R=V, complemento viável, suportes minimais e classificação parcial.
- Reconstruir HB e K4 de quatro relés, obter objetivos LP com precisão e verificar alegações de estrita força.
- Verificar controle com único relé central que atende múltiplos robôs e s-a-b-t com r=1.

## Edge Cases

- Enumerar todas as instalações em grafos pequenos e confrontar ν(C) com verificador independente, inclusive S∩T.
- Checar prova da H2 para R=∅, R=V, complemento viável, suportes minimais e classificação parcial.
- Reconstruir HB e K4 de quatro relés, obter objetivos LP com precisão e verificar alegações de estrita força.
- Verificar controle com único relé central que atende múltiplos robôs e s-a-b-t com r=1.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS13-01 | P1: Fundamentação | Tarefas | Pending |
| AS13-02 | P1: Fundamentação | Tarefas | Pending |
| AS13-03 | P1: Fundamentação | Tarefas | Pending |
| AS13-04 | P1: Fundamentação | Tarefas | Pending |
| AS13-05 | P1: Fundamentação | Tarefas | Pending |
| AS13-06 | P1: Fundamentação | Tarefas | Pending |
| AS13-07 | P1: Fundamentação | Tarefas | Pending |

**Coverage:** 7 requisitos; 7 com critérios explícitos; todos pendentes de execução e evidência.

## Success Criteria

- [ ] Todas as exigências dos ACs são verificadas com testes derivados da spec, não espelhados do código.
- [ ] Gate: GO apenas se validade de H2 e HL estiver documentada sem lacunas bloqueantes e todas as testemunhas reproduzidas; caso contrário STOP/UNPROVEN com evidência.
- [ ] Parecer independente (autor ≠ verificador) reporta evidência por requisito e falhas/abstenções.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS13-01:** WHEN um conjunto C for classificado como fisicamente viável THEN o verificador matemático SHALL obter ν(C)=m sob a semântica anônima original.
- **AS13-02:** WHEN H2 for derivado de um suporte R THEN a demonstração SHALL usar F=V\R, ν(F)<m e B_R={v∈R:ν(F∪{v})<m}.
- **AS13-03:** WHEN uma escolha individual v∈B_R for classificada THEN a prova SHALL justificar coeficiente 1 em y_v e coeficiente 2 nos demais vértices de R.
- **AS13-04:** WHEN HL for formalizado THEN a documentação SHALL provar Φ_R como projeção exata das instalações inteiras viáveis sobre R.
- **AS13-05:** WHEN as testemunhas HB e quatro relés forem auditadas THEN o relatório SHALL separar satisfação de K, viabilidade física, ótimo LP e ótimo IP.
- **AS13-06:** IF um contraexemplo ou hipótese não demonstrada for encontrado THEN a etapa SHALL registrar UNPROVEN e bloquear a implementação dependente.
- **AS13-07:** WHEN o parecer de novidade for registrado THEN ele SHALL identificar o que já decorre de K, C6, CBI, CG/zero-half e de limites globais conhecidos.

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
