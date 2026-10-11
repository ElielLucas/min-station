# AS00 — Escopo, benchmark difícil e pré-registro — Specification

**Status:** RASCUNHO · não implementada nesta entrega  
**Prioridade:** P0 · obrigatório  
**Dependências:** Pareceres Astra; manifesto benchmark-v1  
**Local:** `specs/as-00-benchmark-e-pre-registro/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses e verificações pontuais; **não são** uma campanha nova, e nenhuma tarefa abaixo foi executada.

## Problem Statement

O universo da FC-06 foi restrito por instâncias enumeráveis na F-CC explícita; isso excluiu casos difíceis antes da comparação. Os registros históricos também misturam nomes legados e normalizados e não asseguram independência entre variantes do mesmo mapa.

## Goals

- [ ] Fixar um universo de desenvolvimento e avaliação selecionado pela dificuldade do problema, não pela enumerabilidade F-CC.
- [ ] Registrar identidade, proveniência, estratos, orçamento e política de progressão antes de observar resultados novos.

## Out of Scope

| Item | Motivo |
|---|---|
| Reabrir FC-06 ou alterar freezes legados | Fazer novo protocolo auditável sem modificar evidências anteriores. |
| Procurar apenas instâncias artificiais com timeout | Seleção deve responder a hipóteses explícitas. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Partição inicial | 31 casos D/A do benchmark-v1: 14 desenvolvimento e 17 avaliação; revalidar manifesto do snapshot | Universo identificado no parecer, mas deve ser confrontado com o ZIP. | Pendente de execução |
| Piloto de desenvolvimento | puc-cc9-2p-seed-r1; puc-bip42p-regiao-f2; pucn-cc3-10n-seed-r1; mapf-room-32-32-4-m10-f8; vienna-I056-regiao-f4; puc-w3c571-seed-r1 | Seis instâncias de propriedades variadas recomendadas pelo Astra. | Pendente de execução |
| Identidade independente | Hash de G, S, T, r e A_r; family_id do grafo bruto/mapa/cenário | Nomes e quantidade de robôs não garantem independência. | Pendente de execução |
| Seleção final | Estratificar e congelar cerca de 8–12 casos de avaliação antes do teste final | Evita cherry-picking; selecionador registra ausência de estrato elegível. | Pendente de execução |

**Open questions: none** — os defaults são premissas explícitas sujeitas aos gates anteriores; mudar qualquer uma depois de observar a avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS00-01 — Manifesto auditável:** WHEN a case is registered THEN the protocol SHALL store source file, normalized name, graph-family ID, n, m, r, graph hash, S/T hashes and A_r hash.
2. **AS00-02 — Sem viés por enumerabilidade:** IF explicit F-CC construction fails THEN the protocol SHALL retain the case in the applicability denominator with a classified outcome.
3. **AS00-03 — Independência:** WHEN a development case shares a raw MAPF map/scenario with evaluation THEN the protocol SHALL flag the evaluation case as related and exclude it from claims of independent validation.
4. **AS00-04 — Pré-registro:** WHEN an experiment is authorized THEN the protocol SHALL persist its case set, seeds, arm IDs, resource budget, hypothesis and promotion thresholds before running any arm.
5. **AS00-05 — Preservação:** The protocol SHALL create new result paths and SHALL never overwrite historical N1/N2/FC artifacts.

**Independent Test:** Auditar dois aliases equivalentes e um par não equivalente.; Cap excedido não remove caso.; MAPF room m10/m25 são relacionados.; Manifesto imutável e digest verificável.; Verificar ausência de alterações no legado..

## Edge Cases

A ordem do estudo é: corrigir universo e pré-registro → provar A → validar protótipo → comparar controles → pilotos → ramificação condicionada → avaliação. A inexistência de nova evidência nunca autoriza alterar resultados históricos.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS00-01 | Auditar dois aliases equivalentes e um par não equivalente. | Tasks | Pending |
| AS00-02 | Cap excedido não remove caso. | Tasks | Pending |
| AS00-03 | MAPF room m10/m25 são relacionados. | Tasks | Pending |
| AS00-04 | Manifesto imutável e digest verificável. | Tasks | Pending |
| AS00-05 | Verificar ausência de alterações no legado. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS00-01:** Auditar dois aliases equivalentes e um par não equivalente.
- **AS00-02:** Cap excedido não remove caso.
- **AS00-03:** MAPF room m10/m25 são relacionados.
- **AS00-04:** Manifesto imutável e digest verificável.
- **AS00-05:** Verificar ausência de alterações no legado.

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
