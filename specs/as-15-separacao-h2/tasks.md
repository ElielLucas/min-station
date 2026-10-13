# AS15 — Geração, seleção e certificação de cortes H2 — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **Este pacote contém apenas planejamento; nenhuma tarefa foi executada.**

**Spec:** `specs/as-15-separacao-h2/spec.md`  
**Design:** `specs/as-15-separacao-h2/design.md`  
**Status:** DRAFT  
**Precondition:** AS13 GO e AS14 GO

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-15-separacao-h2/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-15-separacao-h2/tasks.md` |
| Quick | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` ou revisão independente de prova para tarefa documental |
| Full | Quick + `poetry run ruff check experiments/cuts` para código modificado + revisão dos ACs e da proveniência |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "test(as15): valida entrega atomica"` |

## Execution Plan

### Phase 1: Separador H2

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Representar e certificar a desigualdade H2

**What:** Representar e certificar a desigualdade H2. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_cut.py`

**Depends on:** None

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS15-01, AS15-02

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Coefficients/rhs de H2 e validade por enumeração independente.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Coefficients/rhs de H2 e validade por enumeração independente.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T2: Implementar seleção determinística de suportes

**What:** Implementar seleção determinística de suportes. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_supports.py`

**Depends on:** T1

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS15-03, AS15-04

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Suportes relevantes com deduplicação, tamanho/calls limitados.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Suportes relevantes com deduplicação, tamanho/calls limitados.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T3: Implementar separador orçamentado de H2

**What:** Implementar separador orçamentado de H2. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_separator.py`

**Depends on:** T2

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS15-05, AS15-06

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Certificações, violação, UNKNOWN e sem emissão indevida.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Certificações, violação, UNKNOWN e sem emissão indevida.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T4: Adicionar controle exaustivo e diagnóstico do separador

**What:** Adicionar controle exaustivo e diagnóstico do separador. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/test_h2_separator.py`

**Depends on:** T3

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS15-07, AS15-08

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Validar precisão e medir recall em grafos pequenos.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** unit — Validar precisão e medir recall em grafos pequenos.

**Gate:** full — python -m unittest (suíte da etapa; confirmar nome após criação)


## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Task | Uma entrega principal | Status |
|---|---|---|
| T1 | `experiments/cuts/h2_cut.py` | OK |
| T2 | `experiments/cuts/h2_supports.py` | OK |
| T3 | `experiments/cuts/h2_separator.py` | OK |
| T4 | `experiments/cuts/test_h2_separator.py` | OK |

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
| T1 | Código/teste | unit | unit | OK — testar junto da entrega |
| T2 | Código/teste | unit | unit | OK — testar junto da entrega |
| T3 | Código/teste | unit | unit | OK — testar junto da entrega |
| T4 | Código/teste | unit | unit | OK — testar junto da entrega |

## Closing Verification

- [ ] Gate da spec e das tasks passou antes de aprovar Execute.
- [ ] Todas as tarefas tiveram teste/prova co-localizado à entrega e gate PASS.
- [ ] Verifier autor ≠ verificador registrou evidência por AC, incluindo discriminação comportamental em scratch seguro quando houver código.
- [ ] Gate científico: GO se HB e casos negativos passarem, todo corte emitido for comprovadamente válido nas microinstâncias e ao menos um corte não redundante for encontrado com custo registrado; não exigir ganho de benchmark ainda.
- [ ] Como este projeto mantém `specs/` em vez do padrão `.specs/features/` da skill, verificar compatibilidade de `validate_state.py` antes da execução; nunca declarar PASS de conclusão se o validador não suportar o layout ou sem `validation.md`.
