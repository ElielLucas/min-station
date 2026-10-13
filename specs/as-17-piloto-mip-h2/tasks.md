# AS17 — Piloto MIP de H2 na raiz sobre COMP+K — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **Este pacote contém apenas planejamento; nenhuma tarefa foi executada.**

**Spec:** `specs/as-17-piloto-mip-h2/spec.md`  
**Design:** `specs/as-17-piloto-mip-h2/design.md`  
**Status:** DRAFT  
**Precondition:** AS16 GO explícito

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-17-piloto-mip-h2/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-17-piloto-mip-h2/tasks.md` |
| Quick | `poetry run python -m unittest discover -s experiments -p 'test_*.py'` ou revisão independente de prova para tarefa documental |
| Full | Quick + `poetry run ruff check experiments/cuts` para código modificado + revisão dos ACs e da proveniência |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "test(as17): valida entrega atomica"` |

## Execution Plan

### Phase 1: Avaliação MIP

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Especificar política MIP de raiz e resultados censurados

**What:** Especificar política MIP de raiz e resultados censurados. Uma entrega verificável desta etapa.

**Where:** `docs/technical/plans/execucao/as17-preregistro-mip-h2.md`

**Depends on:** None

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS17-01, AS17-02

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Plano pareado, custos e modos de falha congelados.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Plano pareado, custos e modos de falha congelados.

**Gate:** quick — review matemático independente e registro em evidências

### T2: Implementar construção MIP com H2 pré-certificado

**What:** Implementar construção MIP com H2 pré-certificado. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/h2_root_mip.py`

**Depends on:** T1

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS17-03, AS17-04

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Integração sem mudar COMP+K, com teste de invariância inteira.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** integration — Integração sem mudar COMP+K, com teste de invariância inteira.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T3: Implementar execução MIP e validação física do UB

**What:** Implementar execução MIP e validação física do UB. Uma entrega verificável desta etapa.

**Where:** `experiments/cuts/run_h2_mip.py`

**Depends on:** T2

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS17-05, AS17-06

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Tempo total, status, UB física, LB, gap e nós rastreados.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** integration — Tempo total, status, UB física, LB, gap e nós rastreados.

**Gate:** quick — python -m unittest (suíte da etapa; confirmar nome após criação)

### T4: Analisar controle, regressões e replicações condicionais

**What:** Analisar controle, regressões e replicações condicionais. Uma entrega verificável desta etapa.

**Where:** `docs/technical/reference/experimentos/as17-resultado-mip-h2.md`

**Depends on:** T3

**Reuses:** recursos existentes indicados em `design.md`, após verificar contratos reais.

**Requirement:** AS17-07, AS17-08

**Tools:** Skill `/tlc-spec-driven`; arquivos locais; Python unittest; GitHub para consulta; Gurobi apenas se for exigido pela etapa.

**Done when:**

- [ ] Evidências, comparação root bounds e gate GO/STOP/INVESTIGATE.
- [ ] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [ ] Evidência associada a hash/commit é registrada e gate executado.
- [ ] Antes de commitar, atualizar `tasks.md` e rastreabilidade; commit **local** somente após autorização para Execute.

**Tests:** review — Evidências, comparação root bounds e gate GO/STOP/INVESTIGATE.

**Gate:** full — review matemático independente e registro em evidências


## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Task | Uma entrega principal | Status |
|---|---|---|
| T1 | `docs/technical/plans/execucao/as17-preregistro-mip-h2.md` | OK |
| T2 | `experiments/cuts/h2_root_mip.py` | OK |
| T3 | `experiments/cuts/run_h2_mip.py` | OK |
| T4 | `docs/technical/reference/experimentos/as17-resultado-mip-h2.md` | OK |

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
| T2 | Código/teste | integration | integration | OK — testar junto da entrega |
| T3 | Código/teste | integration | integration | OK — testar junto da entrega |
| T4 | Documento | review | review | OK — testar junto da entrega |

## Closing Verification

- [ ] Gate da spec e das tasks passou antes de aprovar Execute.
- [ ] Todas as tarefas tiveram teste/prova co-localizado à entrega e gate PASS.
- [ ] Verifier autor ≠ verificador registrou evidência por AC, incluindo discriminação comportamental em scratch seguro quando houver código.
- [ ] Gate científico: GO condicionado a benefício MIP replicável sem invalidar incumbentes; se H2 só melhora LP, registrar conclusão parcial e STOP para expansão da busca. Sem passagem automática para 3600s.
- [ ] Como este projeto mantém `specs/` em vez do padrão `.specs/features/` da skill, verificar compatibilidade de `validate_state.py` antes da execução; nunca declarar PASS de conclusão se o validador não suportar o layout ou sem `validation.md`.
