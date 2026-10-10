# FC-03 — Relatório de verificação da implementação

**Data:** 2026-10-10  
**Estado:** IMPLEMENTADA PARA TESTE; HOMOLOGAÇÃO INTEGRADA PENDENTE  
**Base:** arquivos completos da entrega FC-02 já validados pelo usuário (58 testes + piloto de Gurobi, antes das mudanças FC-03).  
**Preservação:** sem alteração de N1/N2, certificadores E5, `baseline.py`, `harness.py`, `fcc.py`, `fcc_k.py` ou resultados históricos.

> A elaboração deste relatório não substitui a revisão por verificador independente do autor. A suíte real com Gurobi e o Ruff precisam ser executados no ambiente do projeto.

## Evidência técnica disponível

| Requisito | Evidência de implementação | Testes de aceitação |
|---|---|---|
| PROOF-01 | `fc_core.py` marca LP completo ótimo com `solver_evidence=SOLVER_NUMERIC_OPTIMAL`, `certification=NOT_CERTIFIED`, `rational_evidence=None`; CSV separa `solver_numeric_lp_objective` de racional | `test_proof01_optimal_lp_is_only_numeric`, `test_optimal_numeric_lp_csv_without_proof` |
| PROOF-02 | `fc_evidence.safe_solver_bound` registra `ObjBound` apenas com `model_complete=True` e estado válido; status numérico explícito | `test_proof02_complete_mip_timelimit_can_show_numeric_lb`, `test_proof02_no_incumbent_still_numeric_bound_only` |
| PROOF-03 | `fc_evidence.safe_solver_bound` rejeita formulação de pricing/RMP e modelo incompleto; `CAP_EXCEEDED` não publica bound | `test_proof03_restricted_rmp_never_global_bound`, `test_proof03_truncated_fcc_never_global_bound`, `test_proof03_objboundc_pricing_is_not_bound`, `test_proof03_cap_is_not_fake_zero` |
| PROOF-04 | `fc_evidence.physical_upper_bound` só publica cardinalidade inteira após validação física independente; CSV separa proveniência | `test_proof04_validated_cardinality_is_exact_ub`, `test_proof04_invalid_ub_refused`, `test_complete_mip_csv_separates_three_evidence_axes` |
| PROOF-05 | `fc_evidence.certified_gap` requer LB racional independente mais UB físico da mesma instância; sem eles publica `INCONCLUSIVE` | `test_proof05_no_lb_no_gap_even_with_ub`, `test_proof05_mismatched_instance_proof_refused`, `test_proof05_zero_ub_relative_gap_abstains`, `test_proof05_verified_lb_without_physical_validation_stays_inconclusive` |
| PROOF-06 | `RationalClaim`, `VerificationReceipt`, `accept_independent_proof` validam arquivo SHA, id, contexto e valor Fraction; API opt-in sem chamada automática no runner | `test_proof06_independent_receipt_preserves_exact_fraction`, `test_proof06_opt_in_attachment_and_certified_gap`, `test_proof06_no_verifier_fails`, `test_proof06_rejected_receipt_fails`, `test_proof06_mismatched_receipt_fails`, `test_proof06_modified_artifact_fails`, `test_proof06_restricted_model_does_not_accept_external_attestation`, `test_proof06_verified_proof_reported_only_with_matching_identity` |

## Comandos e resultados efetivamente observados neste ambiente

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s /mnt/data/fc03_staging/experiments/formulation-comparison \
  -p 'test_fc0*.py' -q
# Ran 54 tests ... OK

python -m py_compile /mnt/data/fc03_delivery/experiments/formulation-comparison/*.py
# PASS

python .claude/skills/tlc-spec-driven/scripts/validate_spec.py \
  specs/fc-03-semantica-evidencia-numerica/spec.md --strict
# 0 errors, 0 warnings

python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py \
  specs/fc-03-semantica-evidencia-numerica/tasks.md --strict
# 0 errors, 0 warnings
```

**Resultados:** 10 testes FC-01 + 19 FC-02 + 25 FC-03 = **54/54 PASS** (sem Gurobi). Compilação de todos os `.py` alterados: PASS. Validadores estruturais: PASS. Os testes FC-02 foram reaproveitados da entrega anterior, com os arquivos FC-03 sobrepostos.

**Não executado neste ambiente:** suíte completa `test_*.py` (necessita Gurobi), piloto real e `ruff` (pacotes indisponíveis). **Nenhuma conclusão de aceite integrado** é inferida dessas pendências.

## Pontos de atenção científicos

- `model_context_sha256` é digest da **identidade do contexto**, não da matriz completa ou de cada restrição. A identidade é necessária, não suficiente, para provar matematicamente o modelo.
- O `verifier` no teste é um *test double*, nunca uma prova matemática real. O executor padrão não aciona o verificador racional; por isso, todas as saídas normais mantêm `rational_verification=NOT_CERTIFIED` e `certified_gap_status=INCONCLUSIVE`.
- `PAIR_VALID` permanece evidência de integridade da comparação e validação física das incumbentes, não evidência racional de ótimo inteiro.
- As colunas `evolution.csv:lb/ub` representam amostras do solver e estão marcadas como numéricas, não certificadas.
- Nenhum CSV histórico é reescrito ou migrado automaticamente.

## Aceite integrado que falta no ambiente do usuário

```bash
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline \
  --time-limit 120 --lp-time-limit 60
```

Verificar as duas instâncias com `PAIR_VALID`, comparar resultados numéricos com o piloto FC-02, e inspecionar `results.csv`/`manifest.json` para checar `FC03-v1`, `NOT_CERTIFIED`, `INCONCLUSIVE`, `physical_feasible_ub`, `solver_numeric_*` e ausência de valores certificados sem verificador.
