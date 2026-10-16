# AS26 — Tasks: Piloto MIP condicional de FC-R

**Status:** PLANEJADA; caixas abertas são trabalho futuro, não implementado.

**Design:** `specs/as-26-fcr-mip-condicional/design.md`. **Fonte:** `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

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
| Build | Após mudanças só documentais e antes de concluir fase | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-26-fcr-mip-condicional/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-26-fcr-mip-condicional/tasks.md` |

## Execution Plan

Fases sequenciais; dependências por tarefa exibidas no mapa abaixo.

### Phase 1: Preparação

### T1: Congelar autorização e métricas
### T2: Implementar guard de execução MIP

### Phase 2: Verificação / núcleo

### T3: Registrar telemetria de raiz e árvore
### T4: Executar comparação MIP controlada

### Phase 3: Consolidação

### T5: Publicar avaliação MIP

## Task Breakdown

### T1: Congelar autorização e métricas

**What:** Registrar quem aprovou, evidência AS25, orçamento, controles, root cuts e critérios antes do primeiro run.
**Where:** `docs/technical/plans/execucao/as26-preregistro-fcr-mip.md`
**Depends on:** None
**Requirement:** FCR26-01
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Registrar quem aprovou, evidência AS25, orçamento, controles, root cuts e critérios antes do primeiro run.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as26): congelar autorização e métricas`

### T2: Implementar guard de execução MIP

**What:** Bloquear sem aprovação, validar identidade de instância e parâmetros; testes negativos e de status.
**Where:** `experiments/cuts/run_fcr_mip_as26.py`
**Depends on:** T1
**Requirement:** FCR26-02
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Bloquear sem aprovação, validar identidade de instância e parâmetros; testes negativos e de status.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** integration
**Gate:** full
**Commit:** `feat(as26): implementar guard de execução mip`

### T3: Registrar telemetria de raiz e árvore

**What:** Coletar bound raiz, cuts nativos, nós, incumbente física, gap e tempos sem estimar campos ausentes; testes.
**Where:** `experiments/cuts/fcr_mip_metrics.py`
**Depends on:** T2
**Requirement:** FCR26-03
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Coletar bound raiz, cuts nativos, nós, incumbente física, gap e tempos sem estimar campos ausentes; testes.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as26): registrar telemetria de raiz e árvore`

### T4: Executar comparação MIP controlada

**What:** Preservar raw IDs/hashes e saídas append-only com braço controle, respeitando timeouts e licença.
**Where:** `results/benchmark/as26-fcr-mip-001/manifest.json`
**Depends on:** T3
**Requirement:** FCR26-04
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Preservar raw IDs/hashes e saídas append-only com braço controle, respeitando timeouts e licença.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** integration
**Gate:** full
**Commit:** `feat(as26): executar comparação mip controlada`

### T5: Publicar avaliação MIP

**What:** Distinguir ganho em raiz, melhora dual/tempo e custo, com veredito científico sem esconder perdas.
**Where:** `docs/technical/reference/experimentos/as26-resultado-mip-fcr.md`
**Depends on:** T4
**Requirement:** FCR26-05
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Distinguir ganho em raiz, melhora dual/tempo e custo, com veredito científico sem esconder perdas.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as26): publicar avaliação mip`

## Phase Execution Map

```
T1 -> T2
T2 -> T3
T3 -> T4
T4 -> T5
```

## Task Granularity Check

Cada T entrega um artefato primário indicado em `Where`; testes co-localizados fazem parte da mesma tarefa quando seu código é modificado.

## Diagram-Definition Cross-Check

As setas intrafase dos diagramas refletem `Depends on`. Dependências cruzadas apontam apenas para fases anteriores.

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | `docs/technical/plans/execucao/as26-preregistro-fcr-mip.md` | review | review | OK — planejado |
| T2 | `experiments/cuts/run_fcr_mip_as26.py` | integration | integration | OK — planejado |
| T3 | `experiments/cuts/fcr_mip_metrics.py` | unit | unit | OK — planejado |
| T4 | `results/benchmark/as26-fcr-mip-001/manifest.json` | integration | integration | OK — planejado |
| T5 | `docs/technical/reference/experimentos/as26-resultado-mip-fcr.md` | review | review | OK — planejado |

## Gate de habilitação

**Somente executar se AS25 tiver sido analisada com decisão científica humana formal; nenhum `GO_CANDIDATE_REVIEW` é autorização automática. Status inicial `BLOCKED_BY_GATE`.**

**Importante:** este plano não contém tarefas marcadas como concluídas; validação estrutural do texto não equivale a testes de produto ou de FC-R.
