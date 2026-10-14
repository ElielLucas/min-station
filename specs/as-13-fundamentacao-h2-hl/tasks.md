# AS13 — Fundamentação matemática e validação independente H2/HL — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Ativar a skill `/tlc-spec-driven` (`.claude/skills/tlc-spec-driven/SKILL.md`) ao executar. Um commit local por tarefa após gate PASS; não efetuar commits nem push sem a aprovação explícita do usuário e respeitar `CLAUDE.md`. Após a última tarefa, Verifier independente, discriminação quando houver código e relatório de evidências. **T1–T4 possuem artefatos, testes e parecer independente R3 `PASS`; não houve commits desta entrega. Quatro mutantes residuais precisam ser fechados antes da AS15.**

**Spec:** `specs/as-13-fundamentacao-h2-hl/spec.md`  
**Design:** `specs/as-13-fundamentacao-h2-hl/design.md`  
**Status:** **CONCLUÍDO — AS13 PASS / GO AS14 (Opus R3)**; quatro mutantes residuais pendentes antes da AS15
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

- [x] Revisão **externa** das equações e contraexemplos: Opus R3 aprovou AS13-01 a AS13-07, conforme `validation.md`.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência associada ao HEAD e blobs da fonte registrada; gate técnico executado (sem commit).
- [x] Atualizados `tasks.md` e rastreabilidade; **nenhum commit criado** (projeto exige autorização explícita).

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

- [x] Prova por casos e testes exaustivos referenciados.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência associada ao HEAD e blobs da fonte registrada; gate técnico executado (sem commit).
- [x] Atualizados `tasks.md` e rastreabilidade; **nenhum commit criado** (projeto exige autorização explícita).

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

- [x] Prova de projeção, caso complemento viável e custos de enumeração.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência associada ao HEAD e blobs da fonte registrada; gate técnico executado (sem commit).
- [x] Atualizados `tasks.md` e rastreabilidade; **nenhum commit criado** (projeto exige autorização explícita).

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

- [x] Tabelas reproduzíveis e registro do gate científico final `PASS`, conforme revisor independente R3.
- [x] Testes regressivos derivados dos ACs e casos negativos aplicáveis passam sem enfraquecimento.
- [x] Evidência associada ao HEAD e blobs da fonte registrada; gate técnico executado (sem commit).
- [x] Atualizados `tasks.md` e rastreabilidade; **nenhum commit criado** (projeto exige autorização explícita).

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

- [x] Validação estrutural de `spec.md` e `tasks.md` executada no fechamento documental; registrar os comandos e saída no checkout.
- [x] Tarefas T1–T4 receberam documento e testes próprios; gate técnico local passou.
- [x] Verifier Opus R3 (autor ≠ verificador) aprovou AS13-01 a AS13-07; registrou 15/19 mutantes mortos e 4 residuais a tratar antes da AS15.
- [x] Gate científico AS13 **PASS / GO AS14** por parecer externo R3; **AS15 condicionada** à correção dos quatro mutantes residuais e às dependências da AS14.
- [x] O relatório independente `specs/as-13-fundamentacao-h2-hl/validation.md` existe no checkout do verificador e recebeu a seção R3 `PASS` (conforme parecer informado); o layout `specs/` diverge do caminho padrão de `validate_state.py`, portanto o status se apoia no parecer e no gate aplicável ao projeto, sem alegar execução do `validate_state.py`.

## Pendência de qualidade antes da AS15 (não bloqueia AS14)

- [ ] Adicionar testes adversariais que detectem remoção da checagem de validade H2 completa.
- [ ] Adicionar testes adversariais que detectem remoção da checagem de validade H2 parcial.
- [ ] Adicionar testes adversariais que detectem remoção da checagem da identidade de projeção HL.
- [ ] Rastrear e eliminar o quarto mutante residual registrado na seção R3 de `validation.md`, sem presumir seu comportamento a partir deste resumo.

**Gate:** antes de AS15, executar novamente o sensor independente sobre os quatro mutantes residuais e registrar a evidência em uma etapa apropriada de AS14/AS15, preservando R1–R3.
