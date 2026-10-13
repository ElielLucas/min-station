# AS18 — HL condicional e síntese científica dos novos cortes — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **Este pacote contém apenas planejamento; nenhuma tarefa foi executada.**

**Spec:** `specs/as-18-hl-condicional-e-sintese/spec.md`  
**Design:** `specs/as-18-hl-condicional-e-sintese/design.md`  
**Status:** DRAFT  
**Precondition:** AS13–AS17 concluídas; HL requer sinal estrutural adicional documentado em AS16/AS17

## Test Coverage Matrix

> Fonte: `CLAUDE.md`, `pyproject.toml` e testes existentes `experiments/`; confirmar padrões de suite no checkout usado.

| Camada | Tipo obrigatório | Expectativa | Local | Como executar |
|---|---|---|---|---|
| Prova e documentação | review | Conferência independente de cada afirmação e contraexemplos | `docs/technical/` | Parecer documentado e revisado |
| Oráculo / separação / modelo | unit | Todas as ramificações e casos negativos derivados dos ACs | `experiments/cuts/test_*.py` (proposto) | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` |
| Execução/experimentos/relatório | integration | Budget, idempotência, formato, falha, ganho e censura | `experiments/` (nomes a confirmar) | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` |

## Gate Check Commands

| Gate | Comando / processo |
|---|---|
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-18-hl-condicional-e-sintese/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-18-hl-condicional-e-sintese/tasks.md` |
| Quick | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` ou revisão independente de prova para tarefa documental |
| Full | Quick + `poetry run ruff check experiments/cuts` para código modificado + revisão dos ACs e da proveniência |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "test(as18): valida entrega atomica"` |

## Execution Plan

### Phase 1: Extensão condicional e fechamento

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Formalizar autorização e política local de HL

**What:** Formalizar autorização e política local de HL. Uma entrega verificável desta etapa.

**Where:** `docs/technical/plans/execucao/as18-gate-hl.md`

**Depends on:** None

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS18-01, AS18-02

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Decisão documentada antes de enumerar padrões.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Decisão documentada antes de enumerar padrões.

**Gate:** quick — review matemático independente e registro em evidências

### T2: Implementar enumeração local e β exato

**What:** Implementar enumeração local e β exato. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/hl_local.py`

**Depends on:** T1

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS18-03, AS18-04

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Padrões totais/UNKNOWN conservador e certificados racionais.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Padrões totais/UNKNOWN conservador e certificados racionais.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T3: Implementar microteste e triagem incremental LP

**What:** Implementar microteste e triagem incremental LP. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/test_hl_local.py`

**Depends on:** T2

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS18-05, AS18-06

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Hierarquia K–H2–HL reproduzida e margem de custo medida.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Hierarquia K–H2–HL reproduzida e margem de custo medida.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T4: Publicar síntese científica e próxima decisão

**What:** Publicar síntese científica e próxima decisão. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/experimentos/as18-sintese-h2-hl.md`

**Depends on:** T3

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS18-07, AS18-08, AS18-09

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Resultados próprios, limites e literatura diferenciados, incluindo STOP.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Resultados próprios, limites e literatura diferenciados, incluindo STOP.

**Gate:** full — review matemático independente e registro em evidências


## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Task | Uma entrega principal | Status |
|---|---|---|
| T1 | `docs/technical/plans/execucao/as18-gate-hl.md` | OK |
| T2 | `experiments/cuts/hl_local.py` | OK |
| T3 | `experiments/cuts/test_hl_local.py` | OK |
| T4 | `docs/technical/reference/experimentos/as18-sintese-h2-hl.md` | OK |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
|---|---|---|---|
| T1 | None | None | OK — consistente |
| T2 | T1 | T1 | OK — consistente |
| T3 | T2 | T2 | OK — consistente |
| T4 | T3 | T3 | OK — consistente |

## Test Co-location Validation

| Task | Camada | Matrix Requires | Task Says | Status |
|---|---|---|---|---|
| T1 | Documento | review | review | OK — testar junto da entrega |
| T2 | Código/teste | unit | unit | OK — testar junto da entrega |
| T3 | Código/teste | unit | unit | OK — testar junto da entrega |
| T4 | Documento | review | review | OK — testar junto da entrega |

## Closing Verification

- [ ] Gate da spec e das tasks passou antes de aprovar Execute.
- [ ] Todas as tarefas tiveram teste/prova co-localizado à entrega e gate PASS.
- [ ] Verifier autor ≠ verificador registrou evidência por AC, incluindo discriminação comportamental em scratch seguro quando houver código.
- [ ] Gate científico: GO de HL apenas com melhoria marginal certificada e custo justificado; caso negativo registrar STOP. Síntese final obrigatória mesmo se HL não autorizado.
- [ ] Como este projeto mantém `specs/` em vez do padrão `.specs/features/` da skill, verificar compatibilidade de `validate_state.py` antes da execução; nunca declarar PASS de conclusão se o validador não suportar o layout ou sem `validation.md`.
