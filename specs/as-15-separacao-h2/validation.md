# AS15 — Registro de validação

## Execução local (15/10/2026) — **NÃO É PARECER INDEPENDENTE**

**Veredito:** `LOCAL_PASS / INDEPENDENT_REVIEW_PENDING`.

| AC | Evidência principal | Veredito local |
|---|---|---|
| AS15-01 | `test_h2_separator.py::test_as15_01_viable_complement_never_emits_h2` | PASS |
| AS15-02 | `test_as15_02_03_exact_bhat_coefficients_rhs_and_physical_validity`, `test_as15_06_unknown_candidate_never_enters_bhat` | PASS |
| AS15-03 | `test_as15_02_03_exact_bhat_coefficients_rhs_and_physical_validity` | PASS |
| AS15-04 | `test_as15_04_strict_violation_threshold`, `test_as15_04_exact_violation_tolerance_boundary` | PASS |
| AS15-05 | `test_as15_05_mass_ge_two_prevents_any_oracle_calls`, `test_as15_05_mass_boundary_two` | PASS |
| AS15-06 | `test_as15_06_unknown_complement_abstains`, `test_as15_06_budget_limits_unknowns_and_global_calls`, `test_as15_06_unknown_candidate_never_enters_bhat` | PASS |
| AS15-07 | `test_as15_07_report_hash_reproducibility_and_append_only`, `test_as15_07_all_input_orders_deduplicated_deterministically`, `test_as15_07_instance_T_changes_cannot_contaminate_certificate_cache` | PASS |
| AS15-08 | `test_as15_08_minimal_cover_degenerates_without_novelty` | PASS |

**Teste de validade física e controle não redundante:** `verify_as15_separation.py`, com detalhes em `as15-local-audit.json`: HB 1→2; 91 linhas verificadas, 0 invalidade; recall heurístico 8/83. **Discriminação:** 7/7 mutantes mortos, detalhes em `as15-local-mutations.json`.

**Portões não satisfeitos:** Ruff não rodado no ambiente de preparação; código não associado a commit real; parecer de revisor independente não realizado. **AS15 permanece sem aprovação final**. Um revisor distinto deve preservar esta seção e adicionar sua própria R1, com mutações próprias e evidências por AC. Não promover AS16 automaticamente.
