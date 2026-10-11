# AS-02 — Evidências locais de desenvolvimento (não é verificação independente)

**Data:** 2026-10-11.  
**Ambiente:** Python 3.13.5, SciPy 1.17.0 / HiGHS, sem `gurobipy` e sem `ruff`.  
**Estado:** **IMPLEMENTAÇÃO LOCAL TESTADA, GATE FINAL PENDENTE**.

## Evidências

| Requisito | Evidência | Resultado local |
|---|---|---|
| AS02-01 | `as02_model_a.py::compile_a`, `test_as02_model_a.py::test_as02_01_rows_domains_and_constraints` | Passou: A1–A7, domínios, variáveis auxiliares contínuas, contagem |
| AS02-02 | `test_as02_model_a.py::test_as02_02_invalid_partitions_rejected` | Passou, inclusive rejeição de origem duplicada dentro de bloco |
| AS02-03 | `test_as02_model_a.py::test_as02_03_04_all_installations_agree_with_independent_physical_oracle` | Passou: todos C⊆V das 7 instâncias × 2 particionamentos, confrontados com `independent_validator.viavel` |
| AS02-04 | `test_as02_model_a.py::test_as02_04_integer_objective_matches_exhaustive_physical_optimum` | Passou: OPT MIP numérico vs ótimo por enumeração física; permanência/terminais incluídos |
| AS02-05 | `test_as02_sec59.py::test_as02_05_sec59_lp_control_and_grouped` | Passou: U+K=11/3, A2+K=9/2, A1grupo+K=11/3, tolerância 1e−6 |
| AS02-06 | `test_as02_validation_gate.py` | Passou: MATH_GATE_FAIL, AS01_REVIEW_PENDING, AS02_REVIEW_PENDING, AS02_VALIDATION_FAIL e autorização completa simulada |
| Sensor | `test_as02_model_a.py::test_as02_sensor_removed_global_a5_is_detected` | Passou: mutilação de A5 faz LP cair de 1 para 1/2 |

## Testes locais

- `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_as02*.py' -v`: **10 testes OK** após correção do defeito de grupo duplicado.
- `validate_spec.py`: **0 erros, 0 avisos**.
- `validate_tasks.py`: **0 erros, 0 avisos**.
- Sintaxe Python: todos os scripts novos compilam.

## Pendências bloqueantes

- **AS-01:** última evidência disponível (`specs/as-01-formalizacao-matematica-a/validation.md` do pacote anterior) registra `PENDING` por falta de parecer independente. Não presumir alteração deste status no checkout do usuário.
- **Gurobi:** não instalado neste ambiente; `build_A` e `run_as02_smoke.py` não executados com Gurobi aqui. A versão do usuário precisa rodar ambos e os testes.
- **Ruff:** não instalado aqui, lint não verificado.
- **Verificador independente:** não executado (este documento é registro do próprio autor, não o `validation.md` formal).
- **Commits:** nenhum commit executado na branch do usuário; as tarefas não foram marcadas como concluídas.
- **Sem campanhas grandes:** nenhum resultado experimental de AS-05/AS-06/AS-11 foi produzido, nem qualquer arquivo histórico em `results/` foi alterado.

**Veredito:** PENDING. O protótipo está preparado para integração e revisão, mas não para proclamar equivalência geral provada ou promoção de uma nova formulação.
