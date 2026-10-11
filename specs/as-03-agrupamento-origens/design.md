# AS03 — Políticas reprodutíveis de agrupamento e limites de tamanho — Design

**Status:** protótipo produzido e testado localmente; homologação independente pendente.  
**Spec:** `specs/as-03-agrupamento-origens/spec.md`

## Design Constraints

- Reutilizar `experiments/alternative-formulations/as02_model_a.py` sem modificá-lo; `compile_a(instance, blocks, K)` é o contrato de referência para contagem exata de variáveis.
- Manter a semântica original MIN-STATION; A2/A4 alteram apenas a partição de origens, não o pareamento anônimo nem as restrições do modelo.
- Preservar artefatos, freezes e conclusões legadas N1/N2/FC (`N2 FAIL` não muda).
- Nunca otimizar uma partição usando informação de LP, MIP, avaliação ou bounds; política não é tuning sobre holdout.
- Manter o caminho consolidado do projeto em `experiments/alternative-formulations/`, sem criar `astra-study`.
- Não declarar AS02/AS01 formalmente PASS sem revisão independente dos seus gates.

## Proposed Architecture and Contracts

### 1. `as03_grouping.py` — Partições estruturais

- `partition_two(instance, policy='reachability_degree', seed=0) -> Grouping`: divide `S` em dois blocos com cobertura exata, não vazios e balanceados por cardinalidade.
- Política `reachability_degree`: ordenação baseada em graus de alcance e adjacência entre origens, desempate SHA-256 (não usa `hash()` do Python); fallback `balanced` se descritores empatados.
- Política `balanced`: controle determinístico apenas por rótulo de origem.
- `refine_four(instance, groups2, authorized=True) -> Grouping`: divide cada bloco pai em dois e verifica aninhamento, integridade de hash da partição pai e igualdade de instância. Sem autorização explícita lança erro. Para `m < 4` ou bloco pai unitário gera `NotApplicable`.
- `is_nested(groups2, groups4)`: predicado independente da política.
- `Grouping`: `blocks`, `policy`, `seed`, `instance_hash`, `partition_hash`, `parent_hash`.
- Identidade da partição inclui `POLICY_VERSION='AS03-GROUPING-V1'`, parâmetros, instância canônica e vínculo ao pai.

### 2. `as03_size.py` — Estimador sem solver

- `estimate_size(instance, blocks, k_cuts=()) -> SizeEstimate` calcula **exatamente** `n+k(a+n+m)+|S∩T|` variáveis e `3kn+m+n+|K|` linhas para `compile_a` da AS-02.
- Limite superior conservador para não zeros: `2ka+2km+5kn+n+2h+Σ|Z|`. Se a geração dos K ainda não ocorreu, a previsão é apenas do modelo sem esses cortes, e deve ser rotulada como tal pelo chamador.
- `memory_proxy_bytes`: `4 * (192*variables + 128*constraints + 32*nonzeros_upper)`, **heurística**, não limite garantido de RAM ou RSS.
- `BuildBudget`: caps independentes de variáveis/linhas/não zeros/proxy de memória, tempo remanescente/reserva mínima.
- `decide_build`: classifica `READY_FOR_BUILD`, `NOT_BUILT_SIZE`, `NOT_BUILT_MEMORY`, `NOT_BUILT_BUDGET`, `NOT_APPLICABLE` sem medir LP/MIP, sem zero imputado e sem suprimir linha de caso.

### 3. `as03_planner.py` — Contrato para AS-04

- `plan_a2(instance, case_name, policy, seed, budget, k_cuts) -> PlannedArm` produz partição + decisão.
- `plan_a4(instance, case_name, parent, authorized_by_as05, policy, seed, budget, k_cuts)` sempre depende da A2 existente e exige liberação AS-05 explícita; antes disso retorna `NOT_AUTHORIZED`.
- `.to_record()` serializa parâmetros, hashes e estimativas em JSON sem resultado de solver, mantendo o caso e o `arm_id` compatíveis com AS-00 (`A2_PLUS_K`, `A4_PLUS_K`).
- O nome do caso é usado apenas para rastreabilidade e não afeta o agrupamento.

### 4. Integração e testes

- `run_as03_smoke.py` exercita os contratos com um exemplo sintético e compara estimativas com `compile_a`; usa liberação fictícia de A4 apenas para validar estrutura.
- `test_as03_grouping.py` cobre AS03-01/02/05 (ordem de entrada, refinamento, casos negativos, sem vazamento).
- `test_as03_size.py` cobre AS03-03/04 (fórmula exata, cortes, caps, ausência de medições, sensor de discriminação).
- Documento canônico `docs/technical/plans/execucao/as03-politicas-agrupamento.md` registra políticas, status, limitações, parâmetros default e regras de progressão.

## Dependencies and Reuse

- **Pré-condições de fechamento:** AS00 pré-registro conferido; AS01 prova independente; AS02 gates independentes aprovados.
- **Reutilização imediata:** `as02_model_a.Instance` e `compile_a`, sem alterar os modelos.
- **Fase seguinte:** AS04 integrará estes registros ao comparador; AS05 decidirá com evidência de desenvolvimento se A4 merece execução, e nunca liberará A4 com base nos resultados do conjunto de avaliação.

## Threats to Validity

- `READY_FOR_BUILD` é filtro estimado e **não** atestado de que o modelo cabe em memória.
- Formulações A4 só dominam A2 em LP quando as partições são refinamentos aninhados; duas partições arbitrárias de k=4/k=2 não garantem essa relação.
- Uma política melhor em Sec59 ou em testes sintéticos não justifica adotá-la nas instâncias de avaliação.
- A seleção `reachability_degree` é hipótese heurística simples, não uma estratégia otimizada ou empiricamente vencedora.
- A relação de dependência AS01/AS02 impede liberação científica do piloto mesmo com todos os testes desta feature passando.

## Exit Gate

A feature somente pode ser marcada como concluída após testes derivados dos ACs no checkout real, execução do linter, revisão independente com `validation.md`, gates de AS01/AS02 e commits locais atômicos por tarefa. O pacote não contém `validation.md` assinado e não executa o estudo de benchmark.
