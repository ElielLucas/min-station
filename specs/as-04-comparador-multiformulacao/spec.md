# AS04 — Comparador justo U, U+K e formulações candidatas — Specification

**Status:** RASCUNHO · código de integração local preparado; gates pendentes  
**Prioridade:** P3 · infraestrutura obrigatória  
**Dependências:** AS00=PASS; AS01/AS02=PASS para executar A; reutilizar FC-01–FC-04  
**Local:** `specs/as-04-comparador-multiformulacao/`

> Esta spec traduz os pareceres Astra de 11/10/2026, auditados sobre a branch `novos_testes` no commit `e25b056`. Os pareceres descrevem hipóteses, não uma campanha nova. Os adaptadores e os testes foram preparados localmente; a integração Gurobi e os gates de revisão independente permanecem pendentes.

## Problem Statement

Comparar modelos em scripts separados sem orçamento, cortes, hashes, estados e medição alinhados introduz vieses; resultados LP, MIP e certificação racional não podem ser misturados.

## Goals

- [ ] Criar uma infraestrutura multiarmas reutilizável com contratos de input, K, solver e métricas compartilhados.
- [ ] Comparar explicitamente U sem K, U+K, A2+K e outras candidatas liberadas por gate, isolando efeito de K e efeito da formulação.
- [ ] Não falsificar LP ou bound de modelos incompletos ou interrompidos.

## Out of Scope

| Item | Motivo |
|---|---|
| Reimplementar FC-01 a FC-04 | Reusar instrumentos existentes e testar integração. |
| Declarar o núcleo inteiro como solução física | Controle de LB, não um braço de instalação viável. |
| Rodar F-CC parcial como se completa | Cap e status explícitos. |

## Assumptions & Open Questions

| Decisão / hipótese | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| IDs estáveis de braço | U; U_K; A2_K; A4_K; CUTS_K; B_K; C_K; FCC_K; CORE_IP | Elimina ambiguidade atual de COMP como U+K. | Pendente de execução |
| Comparações primárias | U vs U_K (efeito K); U_K vs A2_K (efeito A); A2_K vs A4_K (refinamento) | Pares interpretáveis com todos fatores restantes fixos. | Pendente de execução |
| Braços opcionais | F-CC+K apenas onde completa; B/C/cortes após seus próprios gates | Viés por escolha de casos deve ser reportado. | Pendente de execução |
| Relógio | Cada braço repete loading/alcance/K em processo supervisionado por FC-01 | Evita custo compartilhado não atribuído, mantém prazo ponta a ponta. | Implementado localmente; Gurobi pendente |

**Open questions: none** — defaults sujeitos aos gates; a política automática A2 não pode ser substituída após observar LP (Sec59 distingue partição automática e testemunha). Mudar uma premissa após observar avaliação exige nova versão e registro de desvio.

## User Stories

### P1: Resultado principal verificável

**User Story:** Como pesquisador do MIN-STATION, quero obter os entregáveis descritos nesta spec com entradas, restrições, status e evidências auditáveis para fundamentar uma decisão científica.

**Acceptance Criteria:**

1. **AS04-01 — Pares alinhados:** WHEN a matched experiment runs THEN the comparator SHALL enforce identical instance fingerprints and solver policy across all participating arms.
2. **AS04-02 — K comparável:** WHEN two +K arms are paired THEN the comparator SHALL enforce identical validated K hashes; the U ablation SHALL be explicitly labeled WITHOUT_K.
3. **AS04-03 — Separação de efeitos:** WHEN a result table is created THEN the reporter SHALL distinguish U vs U_K, U_K vs A2_K, and refinement or optional comparisons without treating them as one effect.
4. **AS04-04 — Resultados censurados:** IF an arm cannot be built, times out or runs out of memory THEN the comparator SHALL record the reason and full wall time without imputing missing objectives.
5. **AS04-05 — LP válido:** IF an LP does not reach proven numerical optimum or an admissible dual bound THEN the comparator SHALL not publish its primal objective as a valid global LP lower bound.
6. **AS04-06 — MIP físico:** WHEN a MIP incumbent is found THEN the comparator SHALL publish UB_PHYSICAL_VALIDATED only after an independent physical validation.
7. **AS04-07 — Custo completo:** WHEN runtime is reported THEN the reporter SHALL show input load, graph reachability, K, build, presolve/solver, validation, total wall, work, nodes and peak memory when observed.
8. **AS04-08 — Classes de evidência:** The output schema SHALL keep solver numeric bound, physical validated UB and independent rational certificate in distinct fields.
9. **AS04-09 — Núcleo e F-CC:** WHEN CORE_IP or incomplete FCC_K is presented THEN the comparator SHALL label core as lower-bound control and incomplete FCC_K as non-comparable for complete-model claims.

**Independent Test:** Alterar fingerprint invalida par.; K diferente bloqueia comparação.; Tabela efeito K / efeito A / efeito k.; Falhas aparecem no denominador.; Interrupção forçada.; Instalação inválida rejeitada.; Tempo de preparo não desaparece.; JSON com três evidências.; Sem bound de RMP restrito como global..

## Edge Cases

**Interpretação obrigatória:** `U` é o modelo agregado sem K (ablação). `U_K` é a formulação que os relatórios anteriores frequentemente chamam `COMP`. A comparação U vs U_K isola efeito K; U_K vs A2_K isola mudança de formulação.

## Requirement Traceability

| Requirement ID | Teste derivado do AC | Fase | Status |
|---|---|---|---|
| AS04-01 | Alterar fingerprint invalida par. | Tasks | Pending |
| AS04-02 | K diferente bloqueia comparação. | Tasks | Pending |
| AS04-03 | Tabela efeito K / efeito A / efeito k. | Tasks | Pending |
| AS04-04 | Falhas aparecem no denominador. | Tasks | Pending |
| AS04-05 | Interrupção forçada. | Tasks | Pending |
| AS04-06 | Instalação inválida rejeitada. | Tasks | Pending |
| AS04-07 | Tempo de preparo não desaparece. | Tasks | Pending |
| AS04-08 | JSON com três evidências. | Tasks | Pending |
| AS04-09 | Sem bound de RMP restrito como global. | Tasks | Pending |

## Success Criteria

- [ ] Cada critério de aceite possui teste que compara o resultado com o comportamento esperado da spec, e não com a implementação.
- [ ] Todos os casos negativos, abstenções e limites matemáticos definidos são preservados.
- [ ] O gate desta spec é evidenciado por artefatos e revisão autor ≠ verificador; na fase de execução há um commit local atômico por tarefa.
- [ ] Não há edição nem sobrescrita das evidências congeladas N1, N2 e FC.

## Tests Derived from Acceptance Criteria

- **AS04-01:** Alterar fingerprint invalida par.
- **AS04-02:** K diferente bloqueia comparação.
- **AS04-03:** Tabela efeito K / efeito A / efeito k.
- **AS04-04:** Falhas aparecem no denominador.
- **AS04-05:** Interrupção forçada.
- **AS04-06:** Instalação inválida rejeitada.
- **AS04-07:** Tempo de preparo não desaparece.
- **AS04-08:** JSON com três evidências.
- **AS04-09:** Sem bound de RMP restrito como global.

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
