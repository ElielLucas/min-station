# FC-01 — Registro de implementação e validação

**Estado:** IMPLEMENTADA PARA REVISÃO — ACEITE INTEGRADO PENDENTE.

**Base:** `min-station(20261010-171720).zip`, branch informada `novos_testes`.
**Spec:** `specs/fc-01-orcamento-global-e-tempos/spec.md`.
**Escopo exclusivo:** relógio global, subprocesso supervisionado, medição por fase e falhas; sem mexer em N1/N2, cortes matemáticos, benchmarks ou resultados congelados.

## Rastreabilidade dos critérios

| ID | Evidência de implementação | Verificação neste ambiente | Verificação ainda necessária |
|---|---|---|---|
| TIME-01 | `fc_core._lp_job`, `fc_core.run_modality_a`, `fc_budget.WallBudget` | `test_remaining_is_absolute_and_not_reset`, `test_success_reports_phases_without_solver_requirement` | LP completo com Gurobi |
| TIME-02 | `fc_core._mip_job`, `_run_mip_bounded`, `_solve_mip_with_evolution` | `test_validation_time_counts_against_deadline`, `test_solver_timeout_discards_partial_value` | MIP completo com Gurobi |
| TIME-03 | `fc_budget.run_bounded` com subprocesso spawn/terminate/kill | `test_preparation_timeout_kills_worker_and_no_objective` | Enumeração real prolongada |
| TIME-04 | `WallBudget.require_remaining`, `_solver_time_limit` | `test_deadline_expired_in_worker_before_solve` | Instrumentar mock/fake solver integrado |
| TIME-05 | `_lp_failed`, `_failed_mip` e medição do supervisor | `test_cap_has_measurable_cost_and_no_result` | `sc-gf2-k3` com `max_w` baixo |
| TIME-06 | `LPResult`/`MIPResult`, `fc_reporting._wall_fields`, `RESULTS_FIELDS` | `test_success_reports_phases_without_solver_requirement` e compilação | CSV efetivo, medir Runtime/Work Gurobi |
| TIME-07 | `fc_budget._worker_entry`, `_failed_mip`, `_lp_failed`, logs runner | `test_failure_has_diagnostic_and_no_result`, `test_missing_solver_license_is_explicit` | Falha real de licença/solver se possível |

## Comandos efetivamente executados

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p test_fc01_budget.py -v
# 10 testes: OK

python -m compileall -q experiments/formulation-comparison
# OK

python .claude/skills/tlc-spec-driven/scripts/validate_spec.py \
  specs/fc-01-orcamento-global-e-tempos/spec.md --strict
# 0 errors / 0 warnings

python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py \
  specs/fc-01-orcamento-global-e-tempos/tasks.md --strict
# 0 errors / 0 warnings
```

## Bloqueios e próximos gates

- **Gurobi (`gurobipy`) não estava instalado no ambiente de desenvolvimento.** A suíte original `test_comparison.py` e o piloto LP/MIP não foram executados aqui. Não são considerados PASS.
- **Ruff não estava instalado no ambiente de desenvolvimento.** `python -m ruff check` está pendente; somente compilação sintática foi verificada.
- **Verifier independente (autor ≠ verificador) ainda não executado.** O aceite final requer revisão independente do código e evidência dos testes com Gurobi.
- Resultados antigos não foram reescritos. O novo formato CSV possui colunas adicionais; testes de ponta a ponta devem usar novos diretórios.
- O `ObjVal` ou `ObjBound` numérico do Gurobi não foi promovido a prova racional; isso pertence à **FC-03**.
- A comparação de modelo inteiro **COMP × F-CC+K com K idêntico** pertence à **FC-02**.

## Aceite no ambiente local

Executar na raiz do repositório com Gurobi licenciado:

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --time-limit 120 --lp-time-limit 60
```

Após executar, verificar em `results.csv` que: `time_s=wall_total_s`, Work não é confundido com segundos, `solver_runtime_s` é separado, tempos por fase não somam mais do que o wall total (tolerância de relógio) e um `CAP_EXCEEDED` ou `TIMEOUT_*` não apresenta valor artificial. 
