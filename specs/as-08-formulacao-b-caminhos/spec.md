# AS08 — Contingência: formulação B por caminhos e pricing — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** Condicional · apenas se k elevado  
**Dependências:** AS01; AS05/AS06 evidenciam que A exige muitos grupos  
**Local:** `specs/as-08-formulacao-b-caminhos/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

A totalmente desagregada exige muitos fluxos em A_r. B representa a mesma família poliedral por caminhos implícitos, mas precisa de pricing, master e limite global correto.

## Goals

- [ ] Formalizar B1–B4 incluindo caminhos de comprimento zero, destinos intermediários e ativação global.
- [ ] Provar a projeção B = A com grupos unitários.
- [ ] Testar pricing por caminhos mínimos, distinguir UB válido de LB global e explorar certificador racional condicionado.

## Out of Scope

| Item | Motivo |
|---|---|
| Tratar B como fonte independente de relaxação em relação a A unitária | Mesma projeção no argumento Astra. |
| Resolver branch-and-price | Exige nova arquitetura e gates não aprovados. |
| Abrir B sem diagnóstico sobre número de grupos | Escopo estritamente condicional. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Gatilho | AS05/AS06 registra necessidade de k alto com custo de construir A | Só então B é alternativa de representação. | Pendente de execução |
| Pricing | Custos de vértices internos não negativos; caminho mínimo no alcance H | Distinto de pricing por configuração conectada N2. | Pendente de execução |
| Bound | RMP objetivo sozinho nunca publicado como LB global | Necessidade de pricing e correção dual por origem. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS08-01 — Caminhos:** WHEN B is defined THEN it SHALL include all simple H-paths s→t and length-zero path s=t, without preset OD pairing.
2. **AS08-02 — Ligações:** WHEN B is constructed THEN it SHALL impose origin/destination unit cover, per-origin internal activation ≤y_v and global internal activation ≤κ_v y_v.
3. **AS08-03 — Projeção:** WHEN B is compared to singleton A THEN the dossier SHALL prove equal y-projected LP feasible regions or explicitly flag gap UNPROVEN.
4. **AS08-04 — Pricing:** WHEN duals are supplied THEN the oracle SHALL return a globally shortest reduced-cost path or a sound lower bound under declared arithmetic.
5. **AS08-05 — Bound global:** IF columns are incomplete THEN the reporter SHALL not use restricted-master objective as a global lower bound; it SHALL require a valid dual correction/certification.
6. **AS08-06 — Gate:** IF B cannot demonstrate benefit net of pricing and link-row costs THEN the branch SHALL stop and retain U_K as fallback.

**Independent Test:** Enumerador pequeno com S∩T.; B1–B4 + K checados.; Testar pequenas grafos.; Comparar com enumeração de caminhos.; Pricing omitido gera `NO_GLOBAL_LB`. ; Desempenho não inferido por LP teórico..

## Edge Cases

B é uma alternativa de **representação implícita da versão totalmente desagregada**, não uma família independente de força. Custo reduzido e certificação dual são hipóteses matemáticas a revisar.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS08-01 | Enumerador pequeno com S∩T. | Tasks | Pending |
| AS08-02 | B1–B4 + K checados. | Tasks | Pending |
| AS08-03 | Testar pequenas grafos. | Tasks | Pending |
| AS08-04 | Comparar com enumeração de caminhos. | Tasks | Pending |
| AS08-05 | Pricing omitido gera `NO_GLOBAL_LB`.  | Tasks | Pending |
| AS08-06 | Desempenho não inferido por LP teórico. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS08-01:** Enumerador pequeno com S∩T.
- **AS08-02:** B1–B4 + K checados.
- **AS08-03:** Testar pequenas grafos.
- **AS08-04:** Comparar com enumeração de caminhos.
- **AS08-05:** Pricing omitido gera `NO_GLOBAL_LB`. 
- **AS08-06:** Desempenho não inferido por LP teórico.

## Implicit-Requirement Sweep

| Dimensão | Resolução |
|---|---|
| Validação de entradas | Critérios EARS cobrem domínios, partições, fingerprints e status conforme escopo. |
| Falhas externas e parciais | Distinção de erro, orçamento, solver, OOM, falta de dados e abstenção; não inferir resultado. |
| Retry e idempotência | Artefatos novos, hashes e política de não sobrescrever evidência congelada. |
| Concorrência / ordenação | Pré-registro de seeds, parâmetros e ordem/família de comparações. |
| Ciclo dos dados | Resultado append-only e rastro de proveniência. |
| Observabilidade | Métricas/evidências por caso e estágio, conforme os ACs. |
| Auth e rate limit | N/A: scripts científicos locais sem API autenticada. |
| Estado / transições | Gates PASS / FAIL / STOP / INVESTIGATE / NOT_AUTHORIZED, quando aplicável. |
