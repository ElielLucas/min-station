# AS16 — Evidências locais da implementação

**Estado:** implementação, testes automatizados e campanha Gurobi executadas; análise documental realizada; revisão humana independente não comprovada.

## Cobertura por requisito

| Requisito | Entrega | Evidência local | Estado |
|---|---|---|---|
| AS16-01 | Plano JSON com seis fontes, hashes, raw_graph_id, seeds, solver e orçamento | `test_six_frozen_raw_distinct_and_valid_source`, `test_changed_source_or_cut_version_fails_closed` | Implementado; campanha executada |
| AS16-02 | Preparação de K paga inclusive em `U_H2` | `test_h2_without_k_pays_k_preparation` | Implementado |
| AS16-03 | Objetivo LP inicial/final, ganhos, tempo total e fases separadas | `run_h2_lp.py`, `analyze_h2_lp.py`, casos artificiais | Implementado; medição real registrada com censuras |
| AS16-04 | Quatro braços com mesmo plano e deadline por processo | `ARMS`, `run_arm()`, `test_expired_budget_never_solves` | Implementado; Gurobi executado |
| AS16-05 | Censura TIME_LIMIT/UNKNOWN/ERROR/OOM e não imputação de objetivo | `test_missing_result_is_censored_and_investigate`, `test_unknown_oom_and_error_are_never_optimal`, `test_untrusted_censored_value_is_rejected` | Implementado |
| AS16-06 | Distinção candidatos/certificados/violados/aceitos/redundantes/não testados | `test_distinct_status_counters_and_unexamined` | Implementado |
| AS16-07 | Mesmo pool H2 instalado nos dois controles fixos | `pool_for_case()`, `test_fixed_pool_applies_same_cut_even_when_not_violated` | Implementado; 10 controles ótimos e 2 NOT_RUN |
| AS16-08 | Gate GO/STOP/INVESTIGATE e proveniência independente por grafo bruto | `test_gate_go_requires_two_independent_raw_graphs_and_paid_gain`, `test_gate_stop_on_no_gain`, `test_same_pool_controls_mandatory` | Implementado; gate real INVESTIGATE e decisão de pesquisa STOP |

## Comandos efetivamente verificados nesta entrega

```text
python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
Ran 106 tests — OK

python .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-16-piloto-lp-h2/spec.md
0 errors, 0 warnings (validado antes da alteração apenas de status)

python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-16-piloto-lp-h2/tasks.md
0 errors, 0 warnings (validado antes da alteração apenas de status)

python -m compileall -q experiments/cuts/run_h2_lp.py experiments/cuts/analyze_h2_lp.py experiments/cuts/test_as16_lp.py
OK
```

A ferramenta `ruff` e `gurobipy` **não estavam disponíveis** neste ambiente. Não se reporta lint como aprovado, nem resultado LP otimizado. Testes artificiais do gate não são resultados de benchmark. A verificação matemática AS13–AS15 já contida no projeto foi executada como regressão automatizada, mas **não substitui parecer de pessoa independente**.

## Campanha numérica realizada pelo executor (15/10/2026)

- Comando: `poetry run python experiments/cuts/run_h2_lp.py --output-dir results/benchmark/as16-lp-h2-001`.
- Gurobi com licença acadêmica conforme saída reportada pelo executor; `manifest.json` indica Gurobi disponível, 4 threads, seed 42, 90 segundos/arm, commit de origem `03431cf8cceafa20de354a160008c8fb84d4b54e`.
- 36 registros: 6 casos × (4 braços + 2 controles). Cinco braços principais `TIME_LIMIT` (quatro em PUC W3C571 e U+H2 em Vienna); dois controles `NOT_RUN` em PUC W3C571.
- O analisador retorna **`INVESTIGATE`**, não `STOP`: exige amostra e controles completos. A decisão de pesquisa **STOP para H2 nesta linha** decorre de **0/5 ganhos marginais ótimos sobre U+K** e da impossibilidade de atingir o limiar de dois grafos com um sexto grafo restante.
- Mesmo pool: não houve ganho adicional sobre U+K nos cinco controles completos; controles são post hoc.
- Execução da suíte relatada pelo executor: `Ran 106 tests in 4.886s` / `OK`. Este pacote de documentação não altera a implementação do runner, dos testes ou do analisador.
- Artefatos auditáveis: `results/benchmark/as16-lp-h2-001/manifest.json`, `rows.json`, `analysis.json`, cinco `*-pool.json`; relatório numérico em `docs/technical/reference/experimentos/as16-resultado-lp-h2.md`.

## Fechamento e ressalvas

1. **Etapa experimental encerrada por decisão de priorização**: H2 não será promovido nem ampliado neste protocolo; manter os artefatos e resultado de gate inalterados.
2. **Revisão científica independente** por pessoa diferente do autor continua sem evidência; não alegar que esse aceite formal foi obtido.
3. Não concluir dominância universal de K sobre H2, significância estatística dos tempos ou melhoria MIP.
4. Para reabrir H2, exigir hipótese e protocolo novos, sem alterar retroativamente o pré-registro ou os resultados desta campanha.
