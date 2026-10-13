# AS13 — Fundamentação matemática e validação independente H2/HL — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **Este pacote contém apenas planejamento; nenhuma tarefa foi executada.**

**Spec:** `specs/as-13-fundamentacao-h2-hl/spec.md`  
**Design:** `specs/as-13-fundamentacao-h2-hl/design.md`  
**Status:** DRAFT  
**Precondition:** Nenhuma; início da linha H2/HL

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-13-fundamentacao-h2-hl/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-13-fundamentacao-h2-hl/tasks.md` |
| Quick | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` ou revisão independente de prova para tarefa documental |
| Full | Quick + `poetry run ruff check experiments/cuts` para código modificado + revisão dos ACs e da proveniência |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "test(as13): valida entrega atomica"` |

## Execution Plan

### Phase 1: Fundamentação

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Consolidar as definições formais e as hipóteses físicas

**What:** Consolidar as definições formais e as hipóteses físicas. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/formulacoes/as13-cortes-h2-hl-fundamentos.md`

**Depends on:** None

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS13-01

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Revisão das equações e contraexemplos com parecer independente.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Revisão das equações e contraexemplos com parecer independente.

**Gate:** quick — review matemático independente e registro em evidências

### T2: Documentar H2 e validar prova em todas as classes de vértices

**What:** Documentar H2 e validar prova em todas as classes de vértices. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/formulacoes/as13-prova-h2.md`

**Depends on:** T1

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS13-02, AS13-03

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Prova por casos e testes exaustivos manuais referenciados.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Prova por casos e testes exaustivos manuais referenciados.

**Gate:** quick — review matemático independente e registro em evidências

### T3: Documentar HL e relação de força com H2 e K

**What:** Documentar HL e relação de força com H2 e K. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/formulacoes/as13-prova-hl.md`

**Depends on:** T2

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS13-04, AS13-05

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Prova de projeção, caso complemento viável e custos de enumeração.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Prova de projeção, caso complemento viável e custos de enumeração.

**Gate:** quick — review matemático independente e registro em evidências

### T4: Certificar testemunhas e emitir gate matemático

**What:** Certificar testemunhas e emitir gate matemático. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/experimentos/as13-testemunhas-e-gate.md`

**Depends on:** T3

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS13-06, AS13-07

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Tabelas reproduzíveis com testes de independência e GO/STOP.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Tabelas reproduzíveis com testes de independência e GO/STOP.

**Gate:** full — review matemático independente e registro em evidências


## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Task | Uma entrega principal | Status |
|---|---|---|
| T1 | `docs/technical/reference/formulacoes/as13-cortes-h2-hl-fundamentos.md` | OK |
| T2 | `docs/technical/reference/formulacoes/as13-prova-h2.md` | OK |
| T3 | `docs/technical/reference/formulacoes/as13-prova-hl.md` | OK |
| T4 | `docs/technical/reference/experimentos/as13-testemunhas-e-gate.md` | OK |

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
| T2 | Documento | review | review | OK — testar junto da entrega |
| T3 | Documento | review | review | OK — testar junto da entrega |
| T4 | Documento | review | review | OK — testar junto da entrega |

## Closing Verification

- [ ] Gate da spec e das tasks passou antes de aprovar Execute.
- [ ] Todas as tarefas tiveram teste/prova co-localizado à entrega e gate PASS.
- [ ] Verifier autor ≠ verificador registrou evidência por AC, incluindo discriminação comportamental em scratch seguro quando houver código.
- [ ] Gate científico: GO apenas se validade de H2 e HL estiver documentada sem lacunas bloqueantes e todas as testemunhas reproduzidas; caso contrário STOP/UNPROVEN com evidência.
- [ ] Como este projeto mantém `specs/` em vez do padrão `.specs/features/` da skill, verificar compatibilidade de `validate_state.py` antes da execução; nunca declarar PASS de conclusão se o validador não suportar o layout ou sem `validation.md`.
