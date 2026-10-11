# AS12 — Síntese científica e encerramento reproduzível — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** Draft — todas pendentes; execução NÃO iniciada.  
**Spec:** `specs/as-12-sintese-decisao-cientifica/spec.md`  
**Design:** `specs/as-12-sintese-decisao-cientifica/design.md`  
**Pré-condição externa:** AS05 e AS06, quando habilitada; AS07–AS11 se executadas ou dispensadas por gate

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-12-sintese-decisao-cientifica/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-12-sintese-decisao-cientifica/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` (focar suíte da feature assim que criada) |
| Full | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` + `python -m ruff check experiments/astra-study` nos arquivos criados; review matemático independente para provas |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3
```

## Task Breakdown

### T1: Consolidar matriz rastreável

**What:** Consolidar matriz rastreável; evidenciar requisitos AS12-01,AS12-02.

**Where:** `experiments/astra-study/as_synthesis.py` (proposto)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS12-01,AS12-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Tipos de evidência confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `tipos de evidência`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Reconciliar decisões e freezes

**What:** Reconciliar decisões e freezes; evidenciar requisitos AS12-03,AS12-05.

**Where:** `docs/technical/plans/astra-decisoes.md` (proposto)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS12-03,AS12-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] N2 fail preservado confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `N2 FAIL preservado`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Publicar parecer e limitações

**What:** Publicar parecer e limitações; evidenciar requisitos AS12-04,AS12-06.

**Where:** `docs/technical/reference/astra-sintese-cientifica.md` (proposto)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS12-04,AS12-06

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Claims auditáveis confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `claims auditáveis`; para review anexar prova/testemunha e parecer independente.

**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3
```

**Cross-check:** a ordem explícita acima coincide com cada `Depends on`; nenhuma dependência aponta para fase posterior.

## Closing Verification

- [ ] Validadores estruturais de spec e tasks aprovados.
- [ ] Verificador independente produziu `validation.md` apenas após Execute, com PASS/FAIL por requisito, `file:line` e sensor de discriminação quando couber.
- [ ] Fechamento pelo validador de estado da skill quando o projeto adotar a estrutura `.specs/features/`; a estrutura corrente `specs/` mantém o padrão anterior sem migração silenciosa.
