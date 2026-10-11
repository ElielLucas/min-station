# AS04 — Comparador justo U, U+K e formulações candidatas — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** Implementação local preparada sem commits; revisão independente e execução Gurobi pendentes.  
**Spec:** `specs/as-04-comparador-multiformulacao/spec.md`  
**Design:** `specs/as-04-comparador-multiformulacao/design.md`  
**Pré-condição externa:** AS00=PASS; AS02=PASS para A; reusar FC-01–FC-04

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-04-comparador-multiformulacao/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-04-comparador-multiformulacao/tasks.md` |
| Quick | `PYTHONHASHSEED=0 PYTHONPATH=. python3 -m unittest discover -s experiments/formulation-comparison -p 'test_as04*.py' -v` |
| Full | `PYTHONHASHSEED=0 PYTHONPATH=. python3 -m unittest discover -s experiments/formulation-comparison -p 'test_as04*.py' -v` + `PYTHONPATH=. python3 experiments/formulation-comparison/run_as04_smoke.py` + `python3 -m ruff check experiments/formulation-comparison/as04*.py experiments/formulation-comparison/test_as04*.py experiments/formulation-comparison/run_as04*.py`; Gurobi no checkout real + verificador independente |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(as04): implementa tarefa atomica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4 -> T5
```

## Task Breakdown

### T1: Criar registro e estados multiarmas

**What:** Criar registro e estados multiarmas; evidenciar requisitos AS04-04,AS04-08.

**Where:** `experiments/formulation-comparison/as04_schema.py` (proposto)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS04-04,AS04-08

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Campos completos e status censurado confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `campos completos e status censurado`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Criar adapters U/U+K/A

**What:** Criar adapters U/U+K/A; evidenciar requisitos AS04-02,AS04-03,AS04-09.

**Where:** `experiments/formulation-comparison/as04_arms.py` (proposto)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS04-02,AS04-03,AS04-09

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Modelos alinhados e tipos confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `modelos alinhados e tipos`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Integrar pareamento e hashes

**What:** Integrar pareamento e hashes; evidenciar requisitos AS04-01,AS04-02.

**Where:** `experiments/formulation-comparison/as04_compare.py` (proposto)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS04-01,AS04-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Hash divergente rejeita confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `hash divergente rejeita`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Integrar orçamento e mensuração

**What:** Integrar orçamento e mensuração; evidenciar requisitos AS04-07.

**Where:** `experiments/formulation-comparison/as04_runner.py` (proposto)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS04-07

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Loading antes do modelo cobrado confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `loading antes do modelo cobrado`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T5: Implementar publicação e verificação

**What:** Implementar publicação e verificação; evidenciar requisitos AS04-05,AS04-06,AS04-08.

**Where:** `experiments/formulation-comparison/as04_reporting.py` (proposto)

**Depends on:** T4

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS04-05,AS04-06,AS04-08

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Lp incompleto não vira lb confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `LP incompleto não vira LB`; para review anexar prova/testemunha e parecer independente.

**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3 -> T4 -> T5
```

**Cross-check:** a ordem explícita acima coincide com cada `Depends on`; nenhuma dependência aponta para fase posterior.

## Closing Verification

- [ ] Validadores estruturais de spec e tasks aprovados.
- [ ] Verificador independente produziu `validation.md` apenas após Execute, com PASS/FAIL por requisito, `file:line` e sensor de discriminação quando couber.
- [ ] Fechamento pelo validador de estado da skill quando o projeto adotar a estrutura `.specs/features/`; a estrutura corrente `specs/` mantém o padrão anterior sem migração silenciosa.
