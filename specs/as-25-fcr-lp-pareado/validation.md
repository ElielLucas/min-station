# AS25 — Validação da implementação pré-experimental

**Status:** `PENDING_REAL_LP_AND_INDEPENDENT_REVIEW`. **Não é PASS formal TLC da AS25 completa.**  
**Escopo entregue:** T1–T4 (protocolo, runner, separação/ablação e análise).  
**Pendências:** T5 campanha real, T6 resultados/gate revisados por verificador distinto do autor, commits/proveniência no checkout do pesquisador.

| Requisito | Evidência | Situação |
|---|---|---|
| FCR25-01 (identidade/hashes) | `experiments/cuts/run_fcr_lp_as25.py:52`; reuso de `validate_sources` e AS16 | PASS local |
| FCR25-02 (24 braços/90 s) | `experiments/cuts/run_fcr_lp_as25.py:224`; `experiments/cuts/test_as25_fcr_lp.py` (`test_dry_run_all_24_rows_and_append_only`) | PASS dry-run; LP real pendente |
| FCR25-03 (censura) | `experiments/cuts/run_fcr_lp_as25.py:205`; testes de TIME_LIMIT e statuses | PASS local; LP real pendente |
| FCR25-04 (ganho objetivo) | `experiments/cuts/analyze_fcr_lp_as25.py:23` e testes `test_flow_only_cut_does_not_count_as_improvement` | PASS artificial |
| FCR25-05 (cobertura e ablação) | `experiments/cuts/fcr_lp_policy.py:32` e `test_fixed_region_Q_and_full_singletons_equivalent_to_AS24` | PASS microcasos; LP real pendente |
| FCR25-06 (fluxo sem bound) | `experiments/cuts/analyze_fcr_lp_as25.py:32` | PASS artificial |
| FCR25-07 (raw_graph_id) | `experiments/cuts/analyze_fcr_lp_as25.py:48` | PASS artificial |
| FCR25-08 (censuras) | `experiments/cuts/analyze_fcr_lp_as25.py:93` | PASS artificial |
| FCR25-09 (human review/MIP) | `experiments/cuts/analyze_fcr_lp_as25.py:126` | PASS artificial |

**Reprodutibilidade:** protocolo `docs/technical/plans/execucao/as25-preregistro-fcr-lp.json`, com seis fontes SHA-256 da AS16. Dry-run gera `manifest.json`, `rows.json`, `analysis.json` em diretório inédito, sem Gurobi. Nem esses dados nem os certificados da AS23 devem ser reportados como campanha real.

**Limites:** nenhuma instância real Gurobi foi resolvida nesta implementação; otimização LP real e ganho de FC-R permanecem perguntas em aberto. AS24 `VALIDATED_WITH_MINOR_FINDINGS` foi documentada; achados menores detalhados do Claude não estão disponíveis. Nenhum commit foi feito nesta entrega.
