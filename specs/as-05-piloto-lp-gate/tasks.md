# AS05 — Piloto LP de A e gate de promoção — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** Código e testes estruturais preparados; tarefas de execução/homologação continuam pendentes.  
**Spec:** `specs/as-05-piloto-lp-gate/spec.md`  
**Design:** `specs/as-05-piloto-lp-gate/design.md`  
**Pré-condição externa:** AS00,AS01,AS02,AS03,AS04=PASS

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-05-piloto-lp-gate/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-05-piloto-lp-gate/tasks.md` |
| Quick | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` (focar suíte da feature assim que criada) |
| Full | `PYTHONHASHSEED=0 python -m unittest discover -s experiments -p 'test_as_*.py' -v` + `python3 -m ruff check experiments/formulation-comparison/as05*.py experiments/formulation-comparison/run_as05*.py experiments/formulation-comparison/as04_runner.py`; review matemático independente para provas |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Codificar executor LP com seis instâncias

**What:** Codificar executor LP com seis instâncias; evidenciar requisitos AS05-01,AS05-05.

**Where:** `experiments/formulation-comparison/as05_pilot.py` (implementado localmente)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS05-01,AS05-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] 6 × braços e falhas confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `6 × braços e falhas`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Calcular deltas LP separados

**What:** Calcular deltas LP separados; evidenciar requisitos AS05-04.

**Where:** `experiments/formulation-comparison/as05_gate.py` (implementado localmente)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS05-04

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] K vs u, a vs k confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `K vs U, A vs K`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Implementar gatilho A4 aninhado

**What:** Implementar gatilho A4 aninhado; evidenciar requisitos AS05-03.

**Where:** `experiments/formulation-comparison/as05_gate.py` (usa AS03 existente)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS05-03

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Skip e gatilho reproduzíveis confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** unit — verificar esperado `skip e gatilho reproduzíveis`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Publicar gate de promoção

**What:** Publicar gate de promoção; evidenciar requisitos AS05-06,AS05-02.

**Where:** `experiments/formulation-comparison/as05_gate.py` (implementado localmente)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS05-06,AS05-02

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [ ] Duas famílias e limiares confirmado por teste independente.
- [ ] Regressões e casos negativos definidos pelos ACs passam no gate; nenhum teste existente é enfraquecido.
- [ ] `tasks.md` e rastreabilidade atualizados antes de commit atômico local.

**Tests:** integration — verificar esperado `duas famílias e limiares`; para review anexar prova/testemunha e parecer independente.

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

## Evidências da implementação local — pendentes de homologação

- Testes AS05 `test_as05_pilot.py` aprovados localmente; **não substituem revisão independente**.
- Regressões AS04 e AS03 executadas localmente após alterar `grouping_seed` opcional.
- `--init-plan`/`--check-plan`: executáveis sem solver; `run_as05_smoke.py` somente cenário artificial.
- Dependências científicas anteriores **não são automaticamente PASS**: AS01/AS02 requerem revisão matemática, AS04 ainda depende de homologação e validação real Gurobi.
- T1–T4 têm código preparado, mas suas checklists **continuam abertas** até os gates completos e commits locais atômicos no repositório do usuário.
- Os controles CORE_IP/FCC não implementados permanecem abstenção transparente; jamais preencher seus resultados com zero.
