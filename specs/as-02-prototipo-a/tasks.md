# AS02 — Protótipo da formulação A e validação exaustiva — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** implementação local preparada e testada; tarefas não concluídas segundo o `/tlc-spec-driven` por falta de commits atômicos e verificação independente.  
**Spec:** `specs/as-02-prototipo-a/spec.md`  
**Design:** `specs/as-02-prototipo-a/design.md`  
**Pré-condição externa:** AS01=PASS

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-02-prototipo-a/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-02-prototipo-a/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as02*.py' -v` (focar suíte da feature assim que criada) |
| Full | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as02*.py' -v` + `python -m ruff check experiments/alternative-formulations/as02*.py experiments/alternative-formulations/test_as02*.py experiments/alternative-formulations/run_as02_smoke.py` nos arquivos criados; review matemático independente para provas |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Implementar construtor A com validação de partição

**What:** Implementar construtor A com validação de partição; evidenciar requisitos AS02-01,AS02-02.

**Where:** `experiments/alternative-formulations/as02_model_a.py` (proposto)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS02-01,AS02-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Domínios e a1–a7 confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `domínios e A1–A7`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Construir verificador de instalações pequenas

**What:** Construir verificador de instalações pequenas; evidenciar requisitos AS02-03,AS02-04.

**Where:** `experiments/alternative-formulations/test_as02_model_a.py` (proposto)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS02-03,AS02-04

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Enumeração e casos s∩t confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `enumeração e casos S∩T`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Adicionar regressão LP Sec59

**What:** Adicionar regressão LP Sec59; evidenciar requisitos AS02-05.

**Where:** `experiments/alternative-formulations/test_as02_sec59.py` (proposto)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS02-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] 9/2 e 11/3 reproduzidos confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `9/2 e 11/3 reproduzidos`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Implementar gate físico/matemático

**What:** Implementar gate físico/matemático; evidenciar requisitos AS02-06.

**Where:** `experiments/alternative-formulations/as02_validation_gate.py` (proposto)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS02-06

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Caso adverso bloqueia piloto confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `caso adverso bloqueia piloto`; para review anexar prova/testemunha e parecer independente.

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

## Verificação local e pendências

A suíte AS02 foi executada com HiGHS/SciPy na cópia isolada (ver `validation-local.md`). Os checkboxes não foram marcados: o contrato exige Gurobi no checkout real, aprovação formal AS01, um commit por tarefa e verificador independente autor ≠ verificador. Não declarar AS02=PASS antes desses gates.
