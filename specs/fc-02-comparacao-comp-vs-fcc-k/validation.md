# FC-02 — Registro de validação da implementação

**Estado:** IMPLEMENTADA PARA HOMOLOGAÇÃO LOCAL — **não aprovada**.
**Dependência:** FC-01 (usuário reportou 34/34 testes PASS e piloto integrado com 0 falhas em 2026-10-10).
**Não reinterpreta:** N2-T6 (`N2 FAIL`) ou relatórios históricos.

## Evidência executada nesta entrega

| Gate | Comando / verificação | Resultado |
|---|---|---|
| Contrato puro | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_fc02_*.py' -v` | **19/19 PASS** (sem Gurobi) |
| Regressão FC-01 | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_fc01_budget.py' -q` | **10/10 PASS** (sem Gurobi) |
| Sintaxe | `python -m compileall -q experiments/formulation-comparison` | **PASS** |
| Spec estrutural | `validate_spec.py specs/fc-02-comparacao-comp-vs-fcc-k/spec.md --strict` | 0 erros, 0 avisos |
| Tasks estrutural | `validate_tasks.py specs/fc-02-comparacao-comp-vs-fcc-k/tasks.md --strict` | 0 erros, 0 avisos |
| Ruff | `python -m ruff check experiments/formulation-comparison` | **PENDENTE** (Ruff indisponível no ambiente de autoria) |
| Integração Gurobi | `python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v` | **PENDENTE** (Gurobi indisponível no ambiente de autoria) |
| Piloto FC-02 | `run_comparison.py --tier pilot --modalities A,B` | **PENDENTE**, obrigatório no ambiente do usuário |

## Matriz PAIR-01 … PAIR-06

| AC | Evidência de implementação | Teste de aceite |
|---|---|---|
| PAIR-01 | `fc_instances.load_instance`; `fc_core._mip_job`; `fc_pairing.assess_primary_pair` | `test_fc02_pairing.test_divergent_*`; `FC02GurobiIntegrationTests.test_comp_mip_and_fcc_k_are_complete_and_same_k`; teste de hash de manifesto |
| PAIR-02 | `fc_core._mip_job` (`_make_mip(..., 'cont', K)` e tipos verificados) | `FC02GurobiIntegrationTests.test_comp_structural_binary_y_continuous_f` **pendente** |
| PAIR-03 | `run_comparison.run`, `--formulations`; `fc_reporting._mip_row` | `test_fc02_reporting_pure`; `FC02GurobiIntegrationTests.test_report_primary_pair_and_no_k_ablation` **pendente** |
| PAIR-04 | `fc_core._failed_mip`; `fc_pairing` bloqueia par incompleto | `test_fc02_pairing.test_cap_exceeded_*`; `FC02GurobiIntegrationTests.test_cap_fcc_mip_never_becomes_paired` **pendente** |
| PAIR-05 | `fc_core._validate` usando `independent_validator.viavel`; `physical_ub_status` | `test_fc02_pairing.test_invalid_physical_witness_refuses_pair`; teste de integração do ótimo **pendente** |
| PAIR-06 | `fc_core._k_for`: valida K e SHA canônico; `fc_pairing` rejeita divergência | `test_fc02_pairing.test_invalid_k_*`, `test_divergent_k_hash_*`; integração real **pendente** |

**Nota de ciência:** as labels `CERTIFIED_*` herdadas da FC-01 ainda são status **numéricos do solver**. A FC-03 realizará a distinção formal entre evidência numérica e certificação racional. `PAIR_VALID` significa integridade do par, **não** prova racional da igualdade dos valores.

## Comandos finais de homologação

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline \
  --time-limit 120 --lp-time-limit 60
```

**Gate de aceitação:** todos os testes e Ruff verdes; no CSV das duas instâncias, `comp_mip` e `fcc_k` com `comparison_role=primary`, hashes K idênticos, `pair_status=PAIR_VALID`, incumbentes validadas; `baseline` presente só com `comparison_role=ablation_no_k`. Nenhuma alteração aos resultados anteriores.

**Verifier independente:** pendente; a autoria não deve simular nem assinar parecer independente.
