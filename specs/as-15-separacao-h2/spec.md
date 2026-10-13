# AS15 — Geração, seleção e certificação de cortes H2 — Specification

**Status:** RASCUNHO / NÃO EXECUTADA  
**Branch de referência:** `novos_testes` (verificar HEAD antes de Execute)  
**Dependências externas:** AS13 GO e AS14 GO  
**Local:** `specs/as-15-separacao-h2/`  
**Fonte da hipótese:** parecer Astra recebido em 13/10/2026; **não é resultado executado**.

## Problem Statement

A validade de H2 não fornece, por si só, um mecanismo para encontrar suportes úteis. É necessário selecionar R, certificar coeficientes e avaliar violação sem custo explosivo.

## Goals

- [ ] Construir H2 certificados em y com suporte e coeficientes reproduzíveis.
- [ ] Experimentar seleção heurística de suportes usando massa fracionária, K e obstruções de Hall.
- [ ] Registrar cobertura de separação, custo, redundância e casos de degeneração.

## Out of Scope

| Item | Motivo |
|---|---|
| Formulação C e C+K | Suspensas por decisão do usuário durante esta linha de cortes. |
| Alterar COMP+K, K existente, N1/N2/FC ou resultados congelados | Preservar controle e proveniência. |
| Sem callbacks MIP e sem HL; nenhuma enumeração global de suportes para instâncias grandes. | Delimitação específica desta etapa. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Gerador | H2 estático a partir de soluções LP correntes com orçamento máximo por instância | Reduz risco antes de callbacks | Não — premissa de planejamento |
| Suportes | Uniões pequenas de K/Hall e suporte fracionário são hipóteses a comparar com controles | Não presumir completude heurística | Não — premissa de planejamento |
| Ordenação | Conjuntos, chamadas e cortes ordenados deterministicamente | Garantir rastreabilidade e testes pareados | Não — premissa de planejamento |

**Open questions:** none — nenhuma sem default. As premissas operacionais devem ser aceitas antes da execução; alterar threshold, fonte ou orçamento após resultados requer plano versionado.

## User Stories

### P1: Pesquisa verificável — Separador H2

**User Story:** Como pesquisador do MIN-STATION, quero construir h2 certificados em y com suporte e coeficientes reproduzíveis para produzir uma decisão cientificamente auditável.

**Acceptance Criteria:**

1. **AS15-01:** WHEN ν(V\R)=m THEN o separador SHALL rejeitar R sem emitir H2.
2. **AS15-02:** WHEN ν(V\R)<m THEN o separador SHALL emitir H2 apenas com membros de B_R certificados INFEASIBLE.
3. **AS15-03:** WHEN o separador produzir a linha THEN ela SHALL usar coeficiente 1 em B̂_R, coeficiente 2 em R\B̂_R e lado direito 2.
4. **AS15-04:** WHEN o LP corrente for y* THEN o separador SHALL aceitar uma linha apenas se a violação superar a tolerância pré-registrada.
5. **AS15-05:** IF y*(R)≥2 THEN o separador SHALL descartar R antes de classificar escolhas individuais.
6. **AS15-06:** IF qualquer teste essencial retornar UNKNOWN THEN o separador SHALL abster-se da afirmação não certificada e registrar a razão.
7. **AS15-07:** WHEN o conjunto de cortes for exportado THEN o relatório SHALL conter suporte, coeficientes, hash de certificado, violação, chamadas e tempo.
8. **AS15-08:** WHEN um suporte minimal de cobertura degenerar em y(R)≥1 THEN a análise SHALL marcar a degeneração e não contá-la como novidade adicional.

**Independent Test:**

- Em HB, obter H2 y(V)≥2 e demonstrar violação do ponto de custo 1.
- Em R com complemento viável, nenhum H2; em suportes minimais, degeneração.
- Sob timeout parcial, a linha com B̂_R permanece válida e todos os UNKNOWN têm coeficiente 2.
- Comparar busca heurística a enumeração de R em microinstâncias: precisão 100%; recall reportado sem exigir completude.
- Testar deduplicação, ordem estável, filtros e tolerância numérica fixada.

## Edge Cases

- Em HB, obter H2 y(V)≥2 e demonstrar violação do ponto de custo 1.
- Em R com complemento viável, nenhum H2; em suportes minimais, degeneração.
- Sob timeout parcial, a linha com B̂_R permanece válida e todos os UNKNOWN têm coeficiente 2.
- Comparar busca heurística a enumeração de R em microinstâncias: precisão 100%; recall reportado sem exigir completude.
- Testar deduplicação, ordem estável, filtros e tolerância numérica fixada.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS15-01 | P1: Separador H2 | Tarefas | Pending |
| AS15-02 | P1: Separador H2 | Tarefas | Pending |
| AS15-03 | P1: Separador H2 | Tarefas | Pending |
| AS15-04 | P1: Separador H2 | Tarefas | Pending |
| AS15-05 | P1: Separador H2 | Tarefas | Pending |
| AS15-06 | P1: Separador H2 | Tarefas | Pending |
| AS15-07 | P1: Separador H2 | Tarefas | Pending |
| AS15-08 | P1: Separador H2 | Tarefas | Pending |

**Coverage:** 8 requisitos; 8 com critérios explícitos; todos pendentes de execução e evidência.

## Success Criteria

- [ ] Todas as exigências dos ACs são verificadas com testes derivados da spec, não espelhados do código.
- [ ] Gate: GO se HB e casos negativos passarem, todo corte emitido for comprovadamente válido nas microinstâncias e ao menos um corte não redundante for encontrado com custo registrado; não exigir ganho de benchmark ainda.
- [ ] Parecer independente (autor ≠ verificador) reporta evidência por requisito e falhas/abstenções.
- [ ] Nenhuma campanha ou mudança no baseline é declarada concluída somente porque a documentação foi produzida.

## Tests Derived from Acceptance Criteria

- **AS15-01:** WHEN ν(V\R)=m THEN o separador SHALL rejeitar R sem emitir H2.
- **AS15-02:** WHEN ν(V\R)<m THEN o separador SHALL emitir H2 apenas com membros de B_R certificados INFEASIBLE.
- **AS15-03:** WHEN o separador produzir a linha THEN ela SHALL usar coeficiente 1 em B̂_R, coeficiente 2 em R\B̂_R e lado direito 2.
- **AS15-04:** WHEN o LP corrente for y* THEN o separador SHALL aceitar uma linha apenas se a violação superar a tolerância pré-registrada.
- **AS15-05:** IF y*(R)≥2 THEN o separador SHALL descartar R antes de classificar escolhas individuais.
- **AS15-06:** IF qualquer teste essencial retornar UNKNOWN THEN o separador SHALL abster-se da afirmação não certificada e registrar a razão.
- **AS15-07:** WHEN o conjunto de cortes for exportado THEN o relatório SHALL conter suporte, coeficientes, hash de certificado, violação, chamadas e tempo.
- **AS15-08:** WHEN um suporte minimal de cobertura degenerar em y(R)≥1 THEN a análise SHALL marcar a degeneração e não contá-la como novidade adicional.

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
