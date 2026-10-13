# AS18 — HL condicional e síntese científica dos novos cortes — Specification

**Status:** RASCUNHO / NÃO EXECUTADA  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** AS13–AS17 concluídas; HL requer sinal estrutural adicional documentado em AS16/AS17  
**Local:** `specs/as-18-hl-condicional-e-sintese/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; **não é resultado executado**.

## Problem Statement

Mesmo quando H2 é válida, pode deixar combinações incompatíveis de dois ou mais relés sem representação. HL é uma extensão potencialmente mais forte, mas enumeração exponencial só é justificável onde houver residual estrutural e orçamento.

## Goals

- [ ] Autorizar HL apenas quando houver evidência de obstrução adicional não capturada por H2.
- [ ] Explorar primeiro cardinalidade três e suportes localizados pequenos, com certificação exata.
- [ ] Consolidar decisão científica H2/HL, inclusive resultados negativos, sem alegar melhoria não medida.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Sem gerador global HL, sem pressuposto de submodularidade e sem campanhas 3600s ou benchmark de avaliação automaticamente. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Ativação HL | Somente após gap residual e testemunha discriminante além de H2 | Custo exponencial demanda justificativa | Não — premissa de planejamento |
| Suportes | k≤10 inicialmente; mudança exigirá novo pré-registro | Até 1024 padrões por suporte antes de filtragem | Não — premissa de planejamento |
| Coeficientes | Racionais certificados e β exato; tratar UNKNOWN conservadoramente | Uma amostra de padrões não certifica corte global | Não — premissa de planejamento |
| Encerramento | Se H2 for STOP e não houver hipótese independente documentada, HL fica NOT_AUTHORIZED | Evita desvio por motivação sintética apenas | Não — premissa de planejamento |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Extensão condicional e fechamento

**User Story:** Como pesquisador do MIN-STATION, quero autorizar hl apenas quando houver evidência de obstrução adicional não capturada por h2 para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS18-01:** WHEN HL for solicitado THEN o gate SHALL exigir evidência documentada de padrão local não capturado pelos H2 disponíveis.
2. **AS18-02:** WHEN um suporte R for escolhido THEN o procedimento SHALL testar ν(V\R) antes da enumeração de padrões.
3. **AS18-03:** WHEN ν(V\R)=m THEN o procedimento SHALL rejeitar R como incapaz de gerar linha HL não trivial.
4. **AS18-04:** WHEN um corte HL for emitido THEN a certificação SHALL calcular β_R(α) sobre todos os padrões admitidos ou por oráculo exato equivalente.
5. **AS18-05:** IF existir padrão UNKNOWN THEN o procedimento SHALL tratá-lo conservadoramente como admissível ou se abster de emitir o corte.
6. **AS18-06:** WHEN coeficientes numéricos forem propostos THEN o procedimento SHALL racionalizá-los e recomputar β exatamente antes da adição.
7. **AS18-07:** WHEN o exemplo dos quatro relés for testado THEN a análise SHALL demonstrar os valores LP 2, 8/3 e 3 dos modelos K, K+H2 e K+H2+HL, ou registrar divergência.
8. **AS18-08:** WHEN HL produzir evidências válidas THEN a análise SHALL comparar ganho marginal, custo e redundância frente ao mesmo pool H2.
9. **AS18-09:** WHEN a linha de pesquisa for encerrada THEN a síntese SHALL discriminar prova, testemunha analítica, resultado LP/MIP, contribuição bibliográfica e casos não medidos.

**Independent Test:**

- Quatro relés: HL y(R0)≥3, ótima inteira três e violação do ponto H2 2/3.
- Complemento viável => Φ_R cubo binário => não há linha nova.
- Suporte k≤10: enumeração exaustiva de padrões e comparação com viabilidade física independente.
- α racionais e recomputação de β; UNKNOWN proposital não gera corte inseguro.
- HL jamais rodado quando gate NOT_AUTHORIZED; síntese conserva STOP e ausência de evidência.

## Edge Cases

- Quatro relés: HL y(R0)≥3, ótima inteira três e violação do ponto H2 2/3.
- Complemento viável => Φ_R cubo binário => não há linha nova.
- Suporte k≤10: enumeração exaustiva de padrões e comparação com viabilidade física independente.
- α racionais e recomputação de β; UNKNOWN proposital não gera corte inseguro.
- HL jamais rodado quando gate NOT_AUTHORIZED; síntese conserva STOP e ausência de evidência.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS18-01 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-02 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-03 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-04 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-05 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-06 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-07 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-08 | P1: Extensão condicional e fechamento | Tarefas | Pending |
| AS18-09 | P1: Extensão condicional e fechamento | Tarefas | Pending |

**Coverage:** 9 requisitos; 9 com critérios explícitos; todos pendentes de execução e evidência.

## Success Criteria

- [ ] Todas as exigências dos ACs são verificadas com testes derivados da spec, não espelhados do código.
- [ ] Gate: GO de HL apenas com melhoria marginal certificada e custo justificado; caso negativo registrar STOP. Síntese final obrigatória mesmo se HL não autorizado.
- [ ] Parecer independente (autor ≠ verificador) reporta evidência por requisito e falhas/abstenções.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS18-01:** WHEN HL for solicitado THEN o gate SHALL exigir evidência documentada de padrão local não capturado pelos H2 disponíveis.
- **AS18-02:** WHEN um suporte R for escolhido THEN o procedimento SHALL testar ν(V\R) antes da enumeração de padrões.
- **AS18-03:** WHEN ν(V\R)=m THEN o procedimento SHALL rejeitar R como incapaz de gerar linha HL não trivial.
- **AS18-04:** WHEN um corte HL for emitido THEN a certificação SHALL calcular β_R(α) sobre todos os padrões admitidos ou por oráculo exato equivalente.
- **AS18-05:** IF existir padrão UNKNOWN THEN o procedimento SHALL tratá-lo conservadoramente como admissível ou se abster de emitir o corte.
- **AS18-06:** WHEN coeficientes numéricos forem propostos THEN o procedimento SHALL racionalizá-los e recomputar β exatamente antes da adição.
- **AS18-07:** WHEN o exemplo dos quatro relés for testado THEN a análise SHALL demonstrar os valores LP 2, 8/3 e 3 dos modelos K, K+H2 e K+H2+HL, ou registrar divergência.
- **AS18-08:** WHEN HL produzir evidências válidas THEN a análise SHALL comparar ganho marginal, custo e redundância frente ao mesmo pool H2.
- **AS18-09:** WHEN a linha de pesquisa for encerrada THEN a síntese SHALL discriminar prova, testemunha analítica, resultado LP/MIP, contribuição bibliográfica e casos não medidos.

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
