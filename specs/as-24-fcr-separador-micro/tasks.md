# AS24 — Tasks: Separador FC-R e microvalidação

**Status:** T1–T5 concluídas; revisão independente favorável (`APPROVED_WITH_MINOR_FINDINGS`); commit final e atualização de proveniência pendentes no checkout do pesquisador.

**Design:** `specs/as-24-fcr-separador-micro/design.md`. **Fonte:** `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

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
| Build | Após mudanças só documentais e antes de concluir fase | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-24-fcr-separador-micro/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-24-fcr-separador-micro/tasks.md` |

## Execution Plan

Fases sequenciais; dependências por tarefa exibidas no mapa abaixo.

### Phase 1: Preparação

### T1: Criar representação canônica de FC-R
### T2: Separar Q ótimo para L fixo

### Phase 2: Verificação / núcleo

### T3: Selecionar regiões unitárias e estruturais
### T4: Construir teste de enumeração independente

### Phase 3: Consolidação

### T5: Publicar relatório de microvalidação

## Task Breakdown

### T1: Criar representação canônica de FC-R

**What:** Termos de fluxo e y com orientação e saldo; rejeitar Q proibido e fornecer assinatura determinística.
**Where:** `experiments/cuts/fcr_rows.py`
**Depends on:** None
**Requirement:** FCR24-03
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [x] Termos de fluxo e y com orientação e saldo; rejeitar Q proibido e fornecer assinatura determinística.
- [x] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [x] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as24): criar representação canônica de fc-r`

### T2: Separar Q ótimo para L fixo

**What:** Implementar ambas as orientações, fórmula fechada Q*, empates, tolerâncias e deduplicação com testes co-localizados.
**Where:** `experiments/cuts/fcr_separator.py`
**Depends on:** T1
**Requirement:** FCR24-01
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [x] Implementar ambas as orientações, fórmula fechada Q*, empates, tolerâncias e deduplicação com testes co-localizados.
- [x] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [x] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as24): separar q ótimo para l fixo`

### T3: Selecionar regiões unitárias e estruturais

**What:** Exaurir singletons elegíveis; heurística limitada para L maiores com cobertura e abstenção explícita.
**Where:** `experiments/cuts/fcr_regions.py`
**Depends on:** T2
**Requirement:** FCR24-02
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [x] Exaurir singletons elegíveis; heurística limitada para L maiores com cobertura e abstenção explícita.
- [x] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [x] Gate `quick` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** quick
**Commit:** `feat(as24): selecionar regiões unitárias e estruturais`

### T4: Construir teste de enumeração independente

**What:** Verificar Q por força bruta em L pequeno e validade para todos os y binários/fluxos construídos; cobrir S=T, interseção, ciclos, r>1 e K fechado.
**Where:** `experiments/cuts/test_as24_fcr.py`
**Depends on:** T3
**Requirement:** FCR24-04
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [x] Verificar Q por força bruta em L pequeno e validade para todos os y binários/fluxos construídos; cobrir S=T, interseção, ciclos, r>1 e K fechado.
- [x] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [x] Gate `full` aprovado e suíte existente sem redução de testes.

**Tests:** unit
**Gate:** full
**Commit:** `feat(as24): construir teste de enumeração independente`

### T5: Publicar relatório de microvalidação

**What:** Registrar contagens, regiões verificadas, limite de enumeração e gate VALIDATED/BLOCKED antes de AS25.
**Where:** `docs/technical/reference/experimentos/as24-validacao-separador-fcr.md`
**Depends on:** T4
**Requirement:** FCR24-05
**Reuses:** baseline COMP+K e referência `docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md`.

**Done when:**

- [x] Registrar contagens, regiões verificadas, limite de enumeração e gate VALIDATED/BLOCKED antes de AS25.
- [x] Evidência identificável por arquivo/linha, com divergências e abstenções explícitas.
- [x] Gate `build` aprovado e suíte existente sem redução de testes.

**Tests:** review
**Gate:** build
**Commit:** `docs(as24): publicar relatório de microvalidação`

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
| T1 | `experiments/cuts/fcr_rows.py` | unit | unit | OK — implementado |
| T2 | `experiments/cuts/fcr_separator.py` | unit | unit | OK — implementado |
| T3 | `experiments/cuts/fcr_regions.py` | unit | unit | OK — implementado |
| T4 | `experiments/cuts/test_as24_fcr.py` | unit | unit | OK — implementado |
| T5 | `docs/technical/reference/experimentos/as24-validacao-separador-fcr.md` | review | review | OK — implementado |

## Gate de habilitação

**Separador não emite corte inválido; decisão `VALIDATED` depende de concordância exata na escolha de Q em microcasos, cobertura total declarada dos singletons e testes adversariais completos.**

**Importante:** as tarefas de implementação e microtestes têm evidências locais. A revisão independente do Claude foi comunicada pelo pesquisador como `APPROVED_WITH_MINOR_FINDINGS`; os achados menores não foram individualizados e continuam em acompanhamento. Consulte `validation.md`.

## Evidências de execução

- `experiments/cuts/test_as24_fcr.py`: seleção exata de Q nas duas direções e para saldo 1/2, validade contra minimização adversarial de fluxo, S=T, interseção, terminais, compartilhamento, alcance r>1, censura, limite de cortes e determinismo.
- `results/benchmark/as24-fcr-micro-001.json`: seis pontos LP sintéticos certificados na AS23, exames unitários e ablação de regiões maiores.
- `docs/technical/reference/experimentos/as24-validacao-separador-fcr.md`: resultados de teste e escopo do gate.
- **Ação restante:** aplicar/commitar o pacote no checkout do pesquisador e regenerar o JSON com `source_commit` definitivo; obter o relatório detalhado do Claude apenas para acompanhar os achados menores, sem bloquear a AS25.
