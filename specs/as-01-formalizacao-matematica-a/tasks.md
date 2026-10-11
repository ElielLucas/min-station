# AS01 — Auditoria matemática da formulação A e errata T18 — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** Artefatos T1–T4 preparados e testados localmente; T5 e commits locais pendentes. Esta entrega não cumpre ainda o gate completo.  
**Spec:** `specs/as-01-formalizacao-matematica-a/spec.md`  
**Design:** `specs/as-01-formalizacao-matematica-a/design.md`  
**Pré-condição externa:** AS00 (controle de instâncias pequenas)

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-01-formalizacao-matematica-a/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-01-formalizacao-matematica-a/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as01*.py' -v` |
| Full | `PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as01*.py' -v` + `python3 -m ruff check experiments/alternative-formulations/test_as01_rational.py` + revisão matemática independente (autor ≠ revisor) |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4 -> T5
```

## Task Breakdown

### T1: Escrever definição normativa A1–A7

**What:** Escrever definição normativa A1–A7; evidenciar requisitos AS01-01.

**Where:** `docs/technical/reference/formulacoes/formulacao-a-grupos-origens.md` (preparado)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS01-01

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Definições sem lacunas confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `definições sem lacunas`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Provar a equivalência física inteira

**What:** Provar a equivalência física inteira; evidenciar requisitos AS01-02.

**Where:** `docs/technical/reference/formulacoes/provas-formulacao-a.md` (preparado)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS01-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Ambas direções e terminais confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `ambas direções e terminais`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Revisar hierarquia LP e relações

**What:** Revisar hierarquia LP e relações; evidenciar requisitos AS01-03,AS01-04,AS01-05.

**Where:** `docs/technical/reference/formulacoes/relacoes-lp-formulacao-a.md` (preparado)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS01-03,AS01-04,AS01-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Contraexemplos e projeções confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `contraexemplos e projeções`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Registrar errata T18 e testemunhas

**What:** Registrar errata T18 e testemunhas; evidenciar requisitos AS01-06.

**Where:** `docs/technical/reference/analise-estrutural/errata-desagregacao-por-origem-t18.md` (preparado)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS01-06

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Aritmética racional do contraexemplo confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `aritmética racional do contraexemplo`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T5: Emitir parecer independente do gate

**What:** Emitir parecer independente do gate; evidenciar requisitos AS01-07.

**Where:** `specs/as-01-formalizacao-matematica-a/validation.md` (pendente de parecer independente)

**Depends on:** T4

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS01-07

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Pass ou fail motivado confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** review — verificar esperado `PASS ou FAIL motivado`; para review anexar prova/testemunha e parecer independente.

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
