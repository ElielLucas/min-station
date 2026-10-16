# AS25 — Tasks: Piloto LP pareado FC-R versus COMP+K

**Status:** PLANEJADA; caixas abertas são trabalho futuro, não implementado.

**Design:** `specs/as-25-fcr-lp-pareado/design.md`. **Fonte:** `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

## Execution Protocol (MANDATORY -- do not skip)

Usar `/tlc-spec-driven` em toda tarefa. Critérios de aceite derivados de `spec.md`; teste deve testar requisito, não espelhar implementação. Cada tarefa concluída exige testes/gate e commit atômico local apenas quando explicitamente autorizado; após a última tarefa, verificador independente obrigatório com evidências `file:line`. Nenhum `git push` ou MIP automático.

## Test Coverage Matrix

> Gerada a partir de `CLAUDE.md`, dos testes `experiments/cuts/test_as22_hl_poly.py`, dos runners AS20–AS22 e do padrão `unittest` executado com Poetry. Proposta: confirmar antes da execução.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
|---|---|---|---|---|
| Prova/relatório de pesquisa | review | Conferência independente de todas as afirmações e links de evidência | `docs/technical/**` | Revisão humana e verificador independente |
| Separação/validação matemática | unit | Cobrir todas as condições e casos limite dos ACs, inclusive contraexemplos | `experiments/cuts/test_as2*_*.py` | `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` |
| Runner, integração de solver, persistência | integration | Dry-run, statuses, censura, hashes, append-only e pares | `experiments/cuts/test_as2*_*.py` | `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` |
| Dados de execução/manifesto | review | Schema, proveniência, análise e hashes reproduzíveis | `results/benchmark/**` | Conferência por parser e revisão humana |

## Gate Check Commands

| Gate Level | When to Use | Command |
|---|---|---|
| Quick | Depois de implementação e testes unitários | `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` |
| Full | Depois de mudanças de integração ou runner | `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` e validações funcionais preregistradas |
| Build | Após mudanças só documentais e antes de concluir fase | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-25-fcr-lp-pareado/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-25-fcr-lp-pareado/tasks.md` |

## Execution Plan

Fases sequenciais; dependências por tarefa exibidas no mapa abaixo.

### Phase 1: Preparação

### T1: Congelar protocolo experimental
### T2: Implementar runner LP pareado

### Phase 2: Verificação / núcleo

### T3: Instrumentar separação/ablação
### T4: Construir analisador conservador

### Phase 3: Consolidação

### T5: Executar campanha Gurobi real
### T6: Publicar relatório e gate

## Task Breakdown

### T1: Congelar protocolo experimental

**What:** Registrar seis grafos brutos, hashes, 4 braços, 90 s de parede, ablação, gate e critérios de censura.
**Where:** `docs/technical/plans/execucao/as25-preregistro-fcr-lp.md`
**Depends on:** None
**Requirement:** FCR25-01
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Registrar seis grafos brutos, hashes, 4 braços, 90 s de parede, ablação, gate e critérios de censura.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as25): congelar protocolo experimental`

### T2: Implementar runner LP pareado

**What:** Dry-run 24 linhas, parâmetro do solver consistente, append-only, custos de fase e testes de timeout/sem licença co-localizados.
**Where:** `experiments/cuts/run_fcr_lp_as25.py`
**Depends on:** T1
**Requirement:** FCR25-02
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Dry-run 24 linhas, parâmetro do solver consistente, append-only, custos de fase e testes de timeout/sem licença co-localizados.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** integration
**Gate:** full
**Commit:** `feat(as25): implementar runner lp pareado`

### T3: Instrumentar separação/ablação

**What:** Registrar singleton completo versus região maior selecionada e métricas de violação, candidatos, NNZ, tempo e memória com testes.
**Where:** `experiments/cuts/fcr_lp_policy.py`
**Depends on:** T2
**Requirement:** FCR25-03
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Registrar singleton completo versus região maior selecionada e métricas de violação, candidatos, NNZ, tempo e memória com testes.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as25): instrumentar separação/ablação`

### T4: Construir analisador conservador

**What:** Contar raw_graph_id, censura, ganho absoluto/relativo, razão custo, não promover automaticamente a MIP; testes por braços fictícios.
**Where:** `experiments/cuts/analyze_fcr_lp_as25.py`
**Depends on:** T3
**Requirement:** FCR25-04
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Contar raw_graph_id, censura, ganho absoluto/relativo, razão custo, não promover automaticamente a MIP; testes por braços fictícios.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** full
**Commit:** `feat(as25): construir analisador conservador`

### T5: Executar campanha Gurobi real

**What:** Criar manifesto e resultados novos imutáveis, 24 braços reais se disponíveis, status explícito em todos.
**Where:** `results/benchmark/as25-fcr-lp-001/manifest.json`
**Depends on:** T4
**Requirement:** FCR25-05
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Criar manifesto e resultados novos imutáveis, 24 braços reais se disponíveis, status explícito em todos.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** integration
**Gate:** full
**Commit:** `feat(as25): executar campanha gurobi real`

### T6: Publicar relatório e gate

**What:** Documentar ablações, ganhos, tempos, censuras e gate; solicitar revisão humana se GO_CANDIDATE_REVIEW.
**Where:** `docs/technical/reference/experimentos/as25-resultado-lp-fcr.md`
**Depends on:** T5
**Requirement:** FCR25-06
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Documentar ablações, ganhos, tempos, censuras e gate; solicitar revisão humana se GO_CANDIDATE_REVIEW.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as25): publicar relatório e gate`

## Phase Execution Map

```
T1 -> T2
T2 -> T3
T3 -> T4
T4 -> T5
T5 -> T6
```

## Task Granularity Check

Cada T entrega um artefato primário indicado em `Where`; testes co-localizados fazem parte da mesma tarefa quando seu código é modificado.

## Diagram-Definition Cross-Check

As setas intrafase dos diagramas refletem `Depends on`. Dependências cruzadas apontam apenas para fases anteriores.

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | `docs/technical/plans/execucao/as25-preregistro-fcr-lp.md` | review | review | OK — planejado |
| T2 | `experiments/cuts/run_fcr_lp_as25.py` | integration | integration | OK — planejado |
| T3 | `experiments/cuts/fcr_lp_policy.py` | unit | unit | OK — planejado |
| T4 | `experiments/cuts/analyze_fcr_lp_as25.py` | unit | unit | OK — planejado |
| T5 | `results/benchmark/as25-fcr-lp-001/manifest.json` | integration | integration | OK — planejado |
| T6 | `docs/technical/reference/experimentos/as25-resultado-lp-fcr.md` | review | review | OK — planejado |

## Gate de habilitação

**`GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.**

**Importante:** este plano não contém tarefas marcadas como concluídas; validação estrutural do texto não equivale a testes de produto ou de FC-R.
