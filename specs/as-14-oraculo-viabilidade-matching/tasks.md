# AS14 — Oráculo certificado de viabilidade para suportes H2/HL — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **T1–T4 implementadas e testadas localmente; nenhum commit efetuado; parecer independente ainda pendente.**

**Spec:** `specs/as-14-oraculo-viabilidade-matching/spec.md`  
**Design:** `specs/as-14-oraculo-viabilidade-matching/design.md`  
**Status:** R1 STOP — CORREÇÕES LOCAIS APLICADAS; LINT E REVERIFICAÇÃO INDEPENDENTE PENDENTES  
**Precondition:** AS13 GO matemático (R3 PASS, informado pelo autor)

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-14-oraculo-viabilidade-matching/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-14-oraculo-viabilidade-matching/tasks.md` |
| Quick | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` ou revisão independente de prova para tarefa documental |
| Full | Quick + `poetry run ruff check experiments/cuts` para código modificado + revisão dos ACs e da proveniência |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "test(as14): valida entrega atomica"` |

## Execution Plan

### Phase 1: Infraestrutura de certificação

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Definir tipos triestado e formato de evidência

**What:** Definir tipos triestado e formato de evidência. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_oracle_schema.py`

**Depends on:** None

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS14-01

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [x] Serialização determinística e contrato VIABLE/INFEASIBLE/UNKNOWN.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência de execução local, SHA de instância e gate técnico documentados em `implementation-evidence.md`; `source_commit` é `null` quando executado de ZIP (sem `.git`).
- [x] Rastreabilidade e `tasks.md` atualizadas; **sem commit**, conforme `CLAUDE.md`.

**Tests:** unit — Serialização determinística e contrato VIABLE/INFEASIBLE/UNKNOWN.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T2: Implementar adaptador do oráculo físico de matching

**What:** Implementar adaptador do oráculo físico de matching. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_oracle.py`

**Depends on:** T1

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS14-02, AS14-03

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [x] Correspondência 1:1 com validador independente em microinstâncias.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência de execução local, SHA de instância e gate técnico documentados em `implementation-evidence.md`; `source_commit` é `null` quando executado de ZIP (sem `.git`).
- [x] Rastreabilidade e `tasks.md` atualizadas; **sem commit**, conforme `CLAUDE.md`.

**Tests:** unit — Correspondência 1:1 com validador independente em microinstâncias.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T3: Adicionar cache canônico e orçamento por chamada

**What:** Adicionar cache canônico e orçamento por chamada. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_oracle_cache.py`

**Depends on:** T2

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS14-04, AS14-05

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [x] Teste de colisão entre instâncias e injeção de timeout.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência de execução local, SHA de instância e gate técnico documentados em `implementation-evidence.md`; `source_commit` é `null` quando executado de ZIP (sem `.git`).
- [x] Rastreabilidade e `tasks.md` atualizadas; **sem commit**, conforme `CLAUDE.md`.

**Tests:** unit — Teste de colisão entre instâncias e injeção de timeout.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T4: Fechar regressão exaustiva e profiling do oráculo

**What:** Fechar regressão exaustiva e profiling do oráculo. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/test_h2_oracle.py`

**Depends on:** T3

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS14-06, AS14-07

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [x] Casos físicos, S∩T, falsos negativos e custos por ν.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência de execução local, SHA de instância e gate técnico documentados em `implementation-evidence.md`; `source_commit` é `null` quando executado de ZIP (sem `.git`).
- [x] Rastreabilidade e `tasks.md` atualizadas; **sem commit**, conforme `CLAUDE.md`.

**Tests:** unit — Casos físicos, S∩T, falsos negativos e custos por ν.

**Gate:** full — python -m unittest (suíte da etapa; confirmar nome após criação)


## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Task | Uma entrega principal | Status |
|---|---|---|
| T1 | `experiments/cuts/h2_oracle_schema.py` | OK |
| T2 | `experiments/cuts/h2_oracle.py` | OK |
| T3 | `experiments/cuts/h2_oracle_cache.py` | OK |
| T4 | `experiments/cuts/test_h2_oracle.py` | OK |

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

- [x] Gate estrutural de spec e tasks: 0 erros, 0 avisos.
- [ ] T1–T4: 41 testes AS14, 27 testes AS13, cinco mutantes R1 detectados e auditoria independente local passam; gate técnico Full depende de Ruff no checkout do usuário, seguido do parecer R2.
- [ ] Verifier autor ≠ verificador registrou evidência por AC — **aguardando revisão independente; sensor próprio 7/7 não substitui essa revisão**.
- [ ] Gate científico final: **R1 STOP / R2 PENDING**; manter AS15 bloqueada; além desta etapa restam quatro mutantes residuais da AS13 antes da AS15.
- [ ] Como este projeto mantém `specs/` em vez do padrão `.specs/features/` da skill, verificar compatibilidade de `validate_state.py` antes da execução; nunca declarar PASS de conclusão se o validador não suportar o layout ou sem `validation.md`.
