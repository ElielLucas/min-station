# AS27 — Tasks: Avaliação independente e generalização FC-R

**Status:** PLANEJADA; caixas abertas são trabalho futuro, não implementado.

**Design:** `specs/as-27-fcr-avaliacao-independente/design.md`. **Fonte:** `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

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
| Build | Após mudanças só documentais e antes de concluir fase | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-27-fcr-avaliacao-independente/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-27-fcr-avaliacao-independente/tasks.md` |

## Execution Plan

Fases sequenciais; dependências por tarefa exibidas no mapa abaixo.

### Phase 1: Preparação

### T1: Congelar protocolo e reserva
### T2: Implementar auditoria do split

### Phase 2: Verificação / núcleo

### T3: Executar validação independente

### Phase 3: Consolidação

### T4: Consolidar relatório científico

## Task Breakdown

### T1: Congelar protocolo e reserva

**What:** Identificar split, fonte, versão, orçamento, métricas e impossibilidade de tuning pós-hoc.
**Where:** `docs/technical/plans/execucao/as27-preregistro-fcr-avaliacao.md`
**Depends on:** None
**Requirement:** FCR27-01
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Identificar split, fonte, versão, orçamento, métricas e impossibilidade de tuning pós-hoc.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as27): congelar protocolo e reserva`

### T2: Implementar auditoria do split

**What:** Falhar sobre IDs brutos em comum, hash/política divergente ou ausência de gate; testes negativos.
**Where:** `experiments/cuts/verify_fcr_reserved_split.py`
**Depends on:** T1
**Requirement:** FCR27-02
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Falhar sobre IDs brutos em comum, hash/política divergente ou ausência de gate; testes negativos.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as27): implementar auditoria do split`

### T3: Executar validação independente

**What:** Criar outputs inéditos com todos os casos e censuras, executar somente autorizado.
**Where:** `results/benchmark/as27-fcr-independent-001/manifest.json`
**Depends on:** T2
**Requirement:** FCR27-03
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Criar outputs inéditos com todos os casos e censuras, executar somente autorizado.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** integration
**Gate:** full
**Commit:** `feat(as27): executar validação independente`

### T4: Consolidar relatório científico

**What:** Conclusão por família e global com incerteza, censura, custo e proveniência.
**Where:** `docs/technical/reference/experimentos/as27-avaliacao-independente-fcr.md`
**Depends on:** T3
**Requirement:** FCR27-04
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Conclusão por família e global com incerteza, censura, custo e proveniência.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as27): consolidar relatório científico`

## Phase Execution Map

```
T1 -> T2
T2 -> T3
T3 -> T4
```

## Task Granularity Check

Cada T entrega um artefato primário indicado em `Where`; testes co-localizados fazem parte da mesma tarefa quando seu código é modificado.

## Diagram-Definition Cross-Check

As setas intrafase dos diagramas refletem `Depends on`. Dependências cruzadas apontam apenas para fases anteriores.

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | `docs/technical/plans/execucao/as27-preregistro-fcr-avaliacao.md` | review | review | OK — planejado |
| T2 | `experiments/cuts/verify_fcr_reserved_split.py` | unit | unit | OK — planejado |
| T3 | `results/benchmark/as27-fcr-independent-001/manifest.json` | integration | integration | OK — planejado |
| T4 | `docs/technical/reference/experimentos/as27-avaliacao-independente-fcr.md` | review | review | OK — planejado |

## Gate de habilitação

**Etapa condicional e não autorizada; requer AS26 com aprovação e política congelada. Nenhum resultado reservado nesta entrega.**

**Importante:** este plano não contém tarefas marcadas como concluídas; validação estrutural do texto não equivale a testes de produto ou de FC-R.
