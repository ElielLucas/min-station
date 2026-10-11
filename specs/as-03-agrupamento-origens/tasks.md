# AS03 — Políticas reprodutíveis de agrupamento e limites de tamanho — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** código e testes locais preparados; integração, commits atômicos e verificação independente pendentes.  
**Spec:** `specs/as-03-agrupamento-origens/spec.md`  
**Design:** `specs/as-03-agrupamento-origens/design.md`  
**Pré-condição externa:** AS02=PASS; AS00 pré-registro

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-03-agrupamento-origens/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-03-agrupamento-origens/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as03*.py' -v` |
| Full | `PYTHONHASHSEED=0 python3 -m unittest discover -s experiments/alternative-formulations -p 'test_as03*.py' -v` + `PYTHONPATH=. python3 experiments/alternative-formulations/run_as03_smoke.py` + `python3 -m ruff check experiments/alternative-formulations/as03_*.py experiments/alternative-formulations/test_as03*.py experiments/alternative-formulations/run_as03_smoke.py`; revisão independente |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(as03): implementa tarefa atomica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3
```

## Task Breakdown

### T1: Codificar política determinística de dois grupos

**What:** Codificar política determinística de dois grupos; evidenciar requisitos AS03-01,AS03-05.

**Where:** `experiments/alternative-formulations/as03_grouping.py` (criado no pacote)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS03-01,AS03-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Ordem de entrada indiferente confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `ordem de entrada indiferente`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Codificar refinamento aninhado de quatro grupos

**What:** Codificar refinamento aninhado de quatro grupos; evidenciar requisitos AS03-02.

**Where:** `experiments/alternative-formulations/as03_grouping.py` (`refine_four`)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS03-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Aninhamento e casos m<4 confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `aninhamento e casos m<4`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Implementar estimativa de tamanho e abstenção

**What:** Implementar estimativa de tamanho e abstenção; evidenciar requisitos AS03-03,AS03-04.

**Where:** `experiments/alternative-formulations/as03_size.py` (integração no planner descrita no design)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS03-03,AS03-04

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Cap baixo e registro de exclusão confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `cap baixo e registro de exclusão`; para review anexar prova/testemunha e parecer independente.

**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3
```

**Cross-check:** a ordem explícita acima coincide com cada `Depends on`; nenhuma dependência aponta para fase posterior.

## Evidências de pacote (não substituem gates do checkout)

- Testes e smoke executados em cópia isolada com o compilador da AS02.
- `AS03-01/02/03/04/05` têm testes automáticos; review externo e commits originais pendentes.
- Nenhuma otimização no benchmark D/A foi autorizada.

## Closing Verification

- [ ] Validadores estruturais de spec e tasks aprovados.
- [ ] Verificador independente produziu `validation.md` apenas após Execute, com PASS/FAIL por requisito, `file:line` e sensor de discriminação quando couber.
- [ ] Fechamento pelo validador de estado da skill quando o projeto adotar a estrutura `.specs/features/`; a estrutura corrente `specs/` mantém o padrão anterior sem migração silenciosa.
