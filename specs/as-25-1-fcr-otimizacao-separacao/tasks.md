# AS25.1 — Tasks: Diagnóstico e otimização da separação FC-R

## Execution Protocol (MANDATORY -- do not skip)

Implementar com a skill `tlc-spec-driven` (fluxo Execute e Critical Rules). Testes derivam dos ACs de `spec.md`. Gate verde antes de concluir cada tarefa. **Desvio registrado:** `CLAUDE.md` proíbe commit automático; cada tarefa termina com gate verde e mensagem de commit sugerida, sem commit. Após a última tarefa, verificador independente obrigatório.

**Design:** `specs/as-25-1-fcr-otimizacao-separacao/design.md`
**Status:** In Progress

---

## Test Coverage Matrix

> Gerada a partir de `CLAUDE.md`, `docs/context-ai/code-guidelines.md`, `experiments/cuts/test_as24_fcr.py`, `experiments/cuts/test_as25_fcr_lp.py` e do padrão `unittest` com Poetry.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
|---|---|---|---|---|
| Separação FC-R (domínio matemático) | unit | 1:1 com ACs FCR251-01..12; edge cases `S∩T`, `r>1`, saldo 2, circulações | `experiments/cuts/test_as251_fcr.py` | `poetry run python -m unittest experiments.cuts.test_as251_fcr -q` |
| Diagnóstico, runner, persistência | integration | Modos, rótulo pós-hoc, plano congelado, braços, censura, append-only, registro por rodada | `experiments/cuts/test_as251_fcr.py` | `poetry run python -m unittest experiments.cuts.test_as251_fcr -q` |
| Analisador | unit | Gate AS25, equivalência INFRA, A/B/C/D, flow-only, sem MIP | `experiments/cuts/test_as251_fcr.py` | `poetry run python -m unittest experiments.cuts.test_as251_fcr -q` |
| Pré-registro e relatórios | none | Conferência por `load_plan` (testada em T5) e revisão humana | `docs/technical/**` | build gate |

## Gate Check Commands

| Gate Level | When to Use | Command |
|---|---|---|
| Quick | Tarefas com testes unitários | `poetry run python -m unittest experiments.cuts.test_as251_fcr -q` |
| Full | Runner/analisador | `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` |
| Build | Fim de fase ou tarefa documental | Full + `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-25-1-fcr-otimizacao-separacao/spec.md` + `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-25-1-fcr-otimizacao-separacao/tasks.md` |

---

## Execution Plan

### Phase 1: Separador

```
T1 → T2
```

### Phase 2: Evidência e protocolo

```
T3 → T4
```

### Phase 3: Campanha

```
T5 → T6 → T7
```

---

## Task Breakdown

### T1: Índice e linhas AS25.1 equivalentes

**What**: `fast_region_plan`, `CachedRegion` e `FastIndexedFCR` (ordem lexicográfica, maiores sempre) com linhas iguais às canônicas.
**Where**: `experiments/cuts/fcr_lp_policy_as251.py`
**Depends on**: None
**Reuses**: `fcr_rows.FCRRow`, `fcr_rows._graph`, `fcr_regions.RegionPlan`
**Requirement**: FCR251-01, FCR251-02, FCR251-03, FCR251-04, FCR251-05, FCR251-06, FCR251-07

**Tools**:

- MCP: NONE
- Skill: `integer-programming-techniques`

**Done when**:

- [x] Plano igual a `choose_regions` na testemunha e em 40 microinstâncias aleatórias
- [x] Linhas iguais a `construct_row` para todo `(L,Q)` emitido
- [x] Saída igual a `IndexedFCR` nos seis pontos racionais AS23
- [x] Q igual ao ótimo exaustivo nas duas direções
- [x] Gate quick verde

**Tests**: unit
**Gate**: quick

---

### T2: Seleção singleton-primeiro

**What**: `larger_mode='escalate'`, status `COMPLETE_SINGLETONS_LARGER_DEFERRED` e opção diagnóstica `selection='deficit'`.
**Where**: `experiments/cuts/fcr_lp_policy_as251.py` (modify)
**Depends on**: T1
**Reuses**: contadores de `IndexedFCR`
**Requirement**: FCR251-08, FCR251-09, FCR251-10, FCR251-11, FCR251-12

**Tools**:

- MCP: NONE
- Skill: `cutting-planes-valid-inequalities`

**Done when**:

- [x] Regiões maiores não examinadas quando há singleton novo violado
- [x] Regiões maiores todas examinadas quando nenhum singleton novo viola
- [x] Duplicatas e tolerância classificadas conforme spec
- [x] Gate quick verde

**Tests**: unit
**Gate**: quick

---

### T3: Script de diagnóstico reprodutível

**What**: Script com modos `index` (tempo e igualdade de plano AS25 vs AS25.1) e `trace` (objetivo e custos por rodada, com ou sem tetos).
**Where**: `experiments/cuts/diagnose_fcr_as251.py`
**Depends on**: None
**Reuses**: helpers de `run_fcr_lp_as25.py` e `run_h2_lp.py`
**Requirement**: FCR251-13, FCR251-14, FCR251-15

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Saída JSON com `evidence_class='DIAGNOSTIC_POST_HOC'`
- [x] Teste de integração do modo `index` na testemunha sem Gurobi
- [x] Evidência gravada em `results/benchmark/as251-diagnostico-001/`
- [x] Gate full verde

**Tests**: integration
**Gate**: full

---

### T4: Pré-registro AS25.1

**What**: JSON e Markdown congelando casos/hashes AS25, solver, 90 s, política FC-R, braços e regra A/B/C/D.
**Where**: `docs/technical/plans/execucao/as251-preregistro-fcr-lp.json`
**Depends on**: T3
**Reuses**: `as25-preregistro-fcr-lp.json`
**Requirement**: FCR251-16

**Tools**:

- MCP: NONE
- Skill: `algorithm-benchmarking-statistics`

**Done when**:

- [x] Casos, hashes e parâmetros Gurobi idênticos à AS25
- [x] Regra A/B/C/D escrita antes de qualquer execução da campanha
- [x] Markdown companheiro `as251-preregistro-fcr-lp.md`
- [x] Gate build verde

**Tests**: none
**Gate**: build

---

### T5: Runner AS25.1

**What**: Runner de quatro braços com processo por braço, 90 s, registro por rodada e digests de linhas.
**Where**: `experiments/cuts/run_fcr_lp_as251.py`
**Depends on**: None
**Reuses**: `run_fcr_lp_as25._point`, `_add_fcr`, `_usage_mb`; helpers `run_h2_lp`
**Requirement**: FCR251-16, FCR251-17, FCR251-18, FCR251-19, FCR251-20

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `load_plan` rejeita mutações de casos, orçamento, política, braços e gate
- [x] Dry-run produz 24 linhas e recusa diretório existente
- [x] Braço sintético registra objetivo e digests por rodada
- [x] Gate full verde

**Tests**: integration
**Gate**: full

---

### T6: Analisador AS25.1

**What**: Gate AS25 verbatim, equivalência INFRA por digest, classificação A/B/C/D.
**Where**: `experiments/cuts/analyze_fcr_lp_as251.py`
**Depends on**: T5
**Reuses**: `analyze_fcr_lp_as25._pair`
**Requirement**: FCR251-21, FCR251-22, FCR251-23, FCR251-24, FCR251-25

**Tools**:

- MCP: NONE
- Skill: `algorithm-benchmarking-statistics`

**Done when**:

- [x] Cada classe A/B/C/D produzida por um conjunto de linhas sintéticas
- [x] Digest divergente impede `infra_equivalent`
- [x] Flow-only conta ganho zero
- [x] Gate full verde

**Tests**: unit
**Gate**: full

---

### T7: Relatório técnico e científico

**What**: Relatório do diagnóstico e do estado AS25.1, com divergências documentais e comandos.
**Where**: `docs/technical/reference/experimentos/as251-diagnostico-fcr.md`
**Depends on**: T6
**Reuses**: `as25-resultado-lp-fcr.md`
**Requirement**: FCR251-15

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Números conferidos contra JSON
- [x] Pendências e limites explícitos
- [x] Gate build verde

**Tests**: none
**Gate**: build

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3

Phase 1:  T1 ------→ T2
Phase 2:  T3 ------→ T4
Phase 3:  T5 ------→ T6 ------→ T7
```

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
|---|---|---|---|
| T1 | None | início | ✅ |
| T2 | T1 | T1 → T2 | ✅ |
| T3 | None | início da fase 2 | ✅ |
| T4 | T3 | T3 → T4 | ✅ |
| T5 | None | início da fase 3 | ✅ |
| T6 | T5 | T5 → T6 | ✅ |
| T7 | T6 | T6 → T7 | ✅ |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | Separação FC-R | unit | unit | ✅ |
| T2 | Separação FC-R | unit | unit | ✅ |
| T3 | Diagnóstico | integration | integration | ✅ |
| T4 | Pré-registro | none | none | ✅ |
| T5 | Runner | integration | integration | ✅ |
| T6 | Analisador | unit | unit | ✅ |
| T7 | Relatório | none | none | ✅ |
