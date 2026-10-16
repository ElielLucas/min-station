# AS23 — Tasks: Revisão matemática independente de FC-R

**Status:** PLANEJADA; caixas abertas são trabalho futuro, não implementado.

**Design:** `specs/as-23-fcr-revisao-matematica/design.md`. **Fonte:** `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

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
| Build | Após mudanças só documentais e antes de concluir fase | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-23-fcr-revisao-matematica/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-23-fcr-revisao-matematica/tasks.md` |

## Execution Plan

Fases sequenciais; dependências por tarefa exibidas no mapa abaixo.

### Phase 1: Preparação

### T1: Reconstruir instância HB ampliada
### T2: Verificar prova e condições de FC-R

### Phase 2: Verificação / núcleo

### T3: Reproduzir os certificados racionais
### T4: Conferir separação ótima em Q para L fixo

### Phase 3: Consolidação

### T5: Publicar parecer e gate AS23

## Task Breakdown

### T1: Reconstruir instância HB ampliada

**What:** Gerar explicitamente grafo físico, H, S, T, r, relés e verificar os quatro K gerados; não codificar objetivos como suposições.
**Where:** `experiments/cuts/verify_fcr_witness.py`
**Depends on:** None
**Requirement:** FCR23-04
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Gerar explicitamente grafo físico, H, S, T, r, relés e verificar os quatro K gerados; não codificar objetivos como suposições.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as23): reconstruir instância hb ampliada`

### T2: Verificar prova e condições de FC-R

**What:** Formalizar validade origens/destinos para todo COMP inteiro; contraexemplos de Q com terminais; caso com circulação.
**Where:** `docs/technical/reference/tecnico/as23-prova-fcr.md`
**Depends on:** T1
**Requirement:** FCR23-01
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Formalizar validade origens/destinos para todo COMP inteiro; contraexemplos de Q com terminais; caso com circulação.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** proof
**Gate:** build
**Commit:** `docs(as23): verificar prova e condições de fc-r`

### T3: Reproduzir os certificados racionais

**What:** Cobrir pontos COMP+K, C6/C8, violação FC-R e combinações lineares; usar Fraction para comparar igualdades.
**Where:** `experiments/cuts/test_as23_fcr_witness.py`
**Depends on:** T1, T2
**Requirement:** FCR23-05
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Cobrir pontos COMP+K, C6/C8, violação FC-R e combinações lineares; usar Fraction para comparar igualdades.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as23): reproduzir os certificados racionais`

### T4: Conferir separação ótima em Q para L fixo

**What:** Deduzir regra de sinal e comparar em casos pequenos com enumeração exaustiva, incluindo empates e FC-R-T.
**Where:** `experiments/cuts/test_as23_fcr_q_selection.py`
**Depends on:** T2
**Requirement:** FCR23-02
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Deduzir regra de sinal e comparar em casos pequenos com enumeração exaustiva, incluindo empates e FC-R-T.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as23): conferir separação ótima em q para l fixo`

### T5: Publicar parecer e gate AS23

**What:** Citar linhas/certificados, conferir literatura, registrar VALIDATED ou BLOCKED; não promover sem revisor independente.
**Where:** `docs/technical/reference/experimentos/as23-validacao-fcr.md`
**Depends on:** T3, T4
**Requirement:** FCR23-06
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [ ] Citar linhas/certificados, conferir literatura, registrar VALIDATED ou BLOCKED; não promover sem revisor independente.
- [ ] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [ ] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as23): publicar parecer e gate as23`

## Phase Execution Map

```
T1 -> T2
T1 -> T3
T2 -> T3
T2 -> T4
T3 -> T5
T4 -> T5
```

## Task Granularity Check

Cada T entrega um artefato primário indicado em `Where`; testes co-localizados fazem parte da mesma tarefa quando seu código é modificado.

## Diagram-Definition Cross-Check

As setas intrafase dos diagramas refletem `Depends on`. Dependências cruzadas apontam apenas para fases anteriores.

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | `experiments/cuts/verify_fcr_witness.py` | unit | unit | OK — planejado |
| T2 | `docs/technical/reference/tecnico/as23-prova-fcr.md` | proof | proof | OK — planejado |
| T3 | `experiments/cuts/test_as23_fcr_witness.py` | unit | unit | OK — planejado |
| T4 | `experiments/cuts/test_as23_fcr_q_selection.py` | unit | unit | OK — planejado |
| T5 | `docs/technical/reference/experimentos/as23-validacao-fcr.md` | review | review | OK — planejado |

## Gate de habilitação

**Gate `VALIDATED` somente se duas provas, testemunha física e racional independente, relação C6/C8 e verificação bibliográfica forem documentadas sem divergência bloqueante. `BLOCKED` em caso contrário.**

**Importante:** este plano não contém tarefas marcadas como concluídas; validação estrutural do texto não equivale a testes de produto ou de FC-R.
