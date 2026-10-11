# AS07 — Contingência: cortes por origem e matching compartilhado — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** Draft — todas pendentes; execução NÃO iniciada.  
**Spec:** `specs/as-07-cortes-origem-matching/spec.md`  
**Design:** `specs/as-07-cortes-origem-matching/design.md`  
**Pré-condição externa:** AS01 auditado; AS05=STOP ou AS06=STOP/INVESTIGATE, após decisão escrita

## Test Coverage Matrix

| Camada | Testes exigidos | Resultado esperado |
|---|---|---|
| Matemática e documentos | review com contraexemplos e prova revisada por segundo responsável | Prova explícita ou `UNPROVEN` bloqueante |
| Núcleo/modelos | unit | Asserções diretas de cada AC; instalação pequena vs validador independente |
| Runner/integração | integration | Hash, estados censurados, budget e physical UB conforme spec |
| Dados/relatórios | unit/integration | Nenhuma linha desaparece; ausências não viram números |

## Gate Check Commands

| Gate | Comando / procedimento |
|---|---|
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-07-cortes-origem-matching/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-07-cortes-origem-matching/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` (focar suíte da feature assim que criada) |
| Full | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` + `python -m ruff check experiments/astra-study` nos arquivos criados; review matemático independente para provas |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Fechar prova e contrato dos cortes

**What:** Fechar prova e contrato dos cortes; evidenciar requisitos AS07-01,AS07-02,AS07-06.

**Where:** `docs/technical/reference/formulacoes/astra-cortes-origem.md` (proposto)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS07-01,AS07-02,AS07-06

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Redes s∩t e validade confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `redes S∩T e validade`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Implementar o separador max-flow

**What:** Implementar o separador max-flow; evidenciar requisitos AS07-03.

**Where:** `experiments/astra-study/as_origin_separator.py` (proposto)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS07-03

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Mínimo corte e desigualdade confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `mínimo corte e desigualdade`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Integrar separação limitada na raiz

**What:** Integrar separação limitada na raiz; evidenciar requisitos AS07-04.

**Where:** `experiments/astra-study/as_root_cuts.py` (proposto)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS07-04

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Parada preserva u_k confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `parada preserva U_K`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Avaliar benefício independente

**What:** Avaliar benefício independente; evidenciar requisitos AS07-05.

**Where:** `experiments/astra-study/as_cuts_gate.py` (proposto)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS07-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Ganho líquido predefinido confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `ganho líquido predefinido`; para review anexar prova/testemunha e parecer independente.

**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3 -> T4
```

**Cross-check:** a ordem explícita acima coincide com cada `Depends on`; nenhuma dependência aponta para fase posterior.

## Closing Verification

- [ ] Validadores estruturais de spec e tasks aprovados.
- [ ] Verificador independente produziu `validation.md` apenas após Execute, com PASS/FAIL por requisito, `file:line` e sensor de discriminação quando couber.
- [ ] Fechamento pelo validador de estado da skill quando o projeto adotar a estrutura `.specs/features/`; a estrutura corrente `specs/` mantém o padrão anterior sem migração silenciosa.
