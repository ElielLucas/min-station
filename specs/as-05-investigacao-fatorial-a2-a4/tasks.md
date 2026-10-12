# AS05-FAC — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Usar `/tlc-spec-driven`; preservar AS00, AS05 e AS05-DIAG-v1/v2; sem commits automáticos. A nova campanha é exploratória, com K exato e plano imutável antes dos solves.

**Status:** código implementado e validado localmente; execução real Gurobi pendente.  
**Spec:** `specs/as-05-investigacao-fatorial-a2-a4/spec.md`  
**Design:** `specs/as-05-investigacao-fatorial-a2-a4/design.md`

## Test Coverage Matrix

| Camada | Testes | Resultado exigido |
|---|---|---|
| Plano | 6 casos dev, 6 braços, policy fixa, SHA originais | Intacto |
| Álgebra | Compiladores AS02, A6 nos +K, A4 refinamento | Equivalência de construção |
| Worker | Sem K não calcula cortes; timeout/cap sem objetivo | Falha segura |
| Supervisor | 300 s por braço e 16 GiB virtual sob `RLIMIT_AS` | Sem solve fora de controle |
| Integridade | 36 linhas, 9 contrastes, SHA, checkpoint/resume | Reprodução auditável |
| Smoke | Seis LPs sintéticos HiGHS | Dominância numérica |

## Gate Check Commands

| Gate | Comando / procedimento |
|---|---|
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-05-investigacao-fatorial-a2-a4/spec.md --strict` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-05-investigacao-fatorial-a2-a4/tasks.md --strict` |
| Quick | `PYTHONPATH=. poetry run python -m unittest discover -s experiments/formulation-comparison -p 'test_as05_factorial.py' -v` |
| Smoke | `PYTHONPATH=. poetry run python experiments/formulation-comparison/run_as05_factorial_smoke.py` |
| Ruff | `poetry run python -m ruff check experiments/formulation-comparison/as05_factorial.py experiments/formulation-comparison/run_as05_factorial.py experiments/formulation-comparison/run_as05_factorial_smoke.py experiments/formulation-comparison/test_as05_factorial.py` |
| Regressão | Quick + AS04, AS05, AS02, AS03 |

## Execution Plan

```
T1 plano -> T2 modelos e política -> T3 executor e supervisor -> T4 integridade -> T5 análise
```

## Task Breakdown

### T1: Congelar o protocolo de desenvolvimento

**What:** Vincular 6 casos de AS00 e fontes por SHA; registrar todos 6 braços, budgets, seed, política e K.  
**Where:** `as05_factorial.py`.  
**Depends on:** None.  
**Requirement:** FAC-01.  
**Done when:**

- [x] Plano criado de modo determinístico e verificado antes dos solves.
- [x] Alterações no plano/fonte são rejeitadas.
- [ ] Revalidado no ambiente do pesquisador.

**Tests:** `test_six_dev_arms_and_fixed_policy`, `test_mutation_rejected`.  
**Gate:** quick

### T2: Compilação justa dos seis braços

**What:** Montar com/sem cortes K, aninhamento A2→A4, tamanho e memória pré-construção.  
**Where:** `as05_factorial.py`.  
**Depends on:** T1.  
**Requirement:** FAC-02, FAC-03, FAC-04, FAC-05.  
**Done when:**

- [x] Seis sistemas corretamente compilados, sem K nos braços controle.
- [x] A4 possui pai A2 e preserva partição em braços com/sem K.
- [x] Cenários com A4 não aplicável permanecem como linha censurada.

**Tests:** `TestFactorialMathematics`, smoke sintético.  
**Gate:** quick + smoke

### T3: Executar sob supervisão e preservar checkpoints

**What:** Worker FC-01 por braço, orçamentos, medição por fase, status e retomada segura.  
**Where:** `run_as05_factorial.py`.  
**Depends on:** T2.  
**Requirement:** FAC-05, FAC-06.  
**Done when:**

- [x] Retomada parcial simulada sem refazer braços concluídos.
- [x] Corrupção de checkpoint detectada.
- [ ] Execução Gurobi de todos seis casos.

**Tests:** `test_resume_only_unfinished`, `test_reject_corrupted_checkpoint_on_resume`.  
**Gate:** quick

### T4: Integridade de pares/relatórios

**What:** Conferir SHA de fontes e K, partições e LPs, emitir 36 linhas e CSV.  
**Where:** `as05_factorial.py`.  
**Depends on:** T3.  
**Requirement:** FAC-06, FAC-07, FAC-08.  
**Done when:**

- [x] Comparações reconhecem apenas pares ótimos LP completos.
- [x] Rastreabilidade por checkpoint/manifesto protegida.

**Tests:** `TestFactorialReports`.  
**Gate:** quick

### T5: Consolidar e interpretar

**What:** Análise fatorial por caso, deltas, custos, tamanhos e interação.  
**Where:** `as05_factorial.py`.  
**Depends on:** T4.  
**Requirement:** FAC-07, FAC-08.  
**Done when:**

- [x] Estrutura de relatório e decisão exploratória implementadas.
- [ ] Interpretar resultados reais sem promoção científica.

**Tests:** `test_analysis_is_exploratory_and_append_only`.  
**Gate:** full
