# AS06 — Piloto MIP pareado: COMP × COMP+K — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Executar cada tarefa com a skill `/tlc-spec-driven` existente em `.claude/skills/tlc-spec-driven/`: testes derivados de AC, gates antes de commit, **um commit local atômico por tarefa**, sem push/deploy, e verificador independente após última tarefa (autor ≠ verificador), incluindo sensor de discriminação quando houver código.

**Status:** T1–T4 implementadas e testadas na cópia fornecida; pendente Gurobi real, commits atômicos no repositório do responsável e verificador independente.  
**Spec:** `specs/as-06-piloto-mip-pareado/spec.md`  
**Design:** `specs/as-06-piloto-mip-pareado/design.md`  
**Pré-condição externa:** AS05 fatorial exploratória concluída, **gate científico PENDING**; AS04 implementada. Execução aqui somente exploratória autorizada pelo responsável.

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
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-06-piloto-mip-pareado/spec.md` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-06-piloto-mip-pareado/tasks.md` |
| Quick | `PYTHONHASHSEED=0 PYTHONPATH=. python -m unittest discover -s experiments/formulation-comparison -p 'test_as06_mip.py' -v` |
| Full | `PYTHONHASHSEED=0 PYTHONPATH=. python -m unittest discover -s experiments/formulation-comparison -p 'test_as0*.py' -v` + Ruff nos novos módulos (se instalado); revisão matemática independente posterior |
| Commit | `python3 .claude/skills/tlc-spec-driven/scripts/check_commit.py --message "feat(astra): implementa tarefa atômica"` |

## Execution Plan

### Phase 1: Preparação e entregas atômicas

```
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Implementar agenda pareada e seeds

**What:** Implementar agenda pareada e seeds; evidenciar requisitos AS06-01,AS06-03.

**Where:** `experiments/formulation-comparison/as06_mip.py` (implementado; CLI adjacente)

**Depends on:** None

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS06-01,AS06-03

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [x] 300 e 600 condicional confirmado por testes de integração sem Gurobi.
- [x] Regressões e casos negativos locais passam; validação Gurobi real permanece pendente.
- [ ] Commit atômico será feito pelo responsável após aplicação no Git; esta entrega é um ZIP sem histórico Git.

**Tests:** integration — verificar esperado `300 e 600 condicional`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T2: Capturar curvas e censura

**What:** Capturar curvas e censura; evidenciar requisitos AS06-04.

**Where:** `experiments/formulation-comparison/as06_mip.py::_solve_mip` (implementado)

**Depends on:** T1

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS06-04

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [x] Captura numérica instrumentada e verificação estrutural; ensaio Gurobi real pendente.
- [x] Regressões e casos negativos locais passam; validação Gurobi real permanece pendente.
- [ ] Commit atômico será feito pelo responsável após aplicação no Git; esta entrega é um ZIP sem histórico Git.

**Tests:** integration — verificar esperado `LB/UB ao longo do tempo`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T3: Conectar validador de incumbentes

**What:** Conectar validador de incumbentes; evidenciar requisitos AS06-05.

**Where:** `experiments/formulation-comparison/as06_mip.py::physical_trace` (implementado)

**Depends on:** T2

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS06-05

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [x] Rejeitar incumbente adulterado em teste com validador físico independente.
- [x] Regressões e casos negativos locais passam; validação Gurobi real permanece pendente.
- [ ] Commit atômico será feito pelo responsável após aplicação no Git; esta entrega é um ZIP sem histórico Git.

**Tests:** integration — verificar esperado `rejeitar incumbente adulterado`; para review anexar prova/testemunha e parecer independente.

**Gate:** quick

### T4: Emitir decisão e negativos

**What:** Emitir decisão e negativos; evidenciar requisitos AS06-02,AS06-06,AS06-07.

**Where:** `experiments/formulation-comparison/as06_reporting.py` (implementado)

**Depends on:** T3

**Reuses:** infraestrutura citada no design, quando compatível.

**Requirement:** AS06-02,AS06-06,AS06-07

**Tools:** Skill `/tlc-spec-driven`; repositório local; Gurobi somente nas tarefas de integração que o exigirem.

**Done when:**

- [x] Duas fontes de grafo, timeouts e gate STOP/GO testados.
- [x] Regressões e casos negativos locais passam; validação Gurobi real permanece pendente.
- [ ] Commit atômico será feito pelo responsável após aplicação no Git; esta entrega é um ZIP sem histórico Git.

**Tests:** integration — verificar esperado `duas famílias e timeouts`; para review anexar prova/testemunha e parecer independente.

**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3 -> T4
```

**Cross-check:** a ordem explícita acima coincide com cada `Depends on`; nenhuma dependência aponta para fase posterior.

## Closing Verification

- [x] Validadores estruturais de spec e tasks aprovados (ver resultado da execução local).
- [ ] Verificador independente autor ≠ verificador: pendente; não criar parecer fictício nem alegar homologação.
- [ ] Fechamento pelo validador de estado da skill quando o projeto adotar a estrutura `.specs/features/`; a estrutura corrente `specs/` mantém o padrão anterior sem migração silenciosa.
