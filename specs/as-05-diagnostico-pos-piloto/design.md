# AS05-DIAG — Diagnóstico pós-piloto — Design

**Status:** implementado localmente; aguardando testes reais Gurobi.
**Spec:** `specs/as-05-diagnostico-pos-piloto/spec.md`

## Design Constraints

Preservar o fluxo científico, a formulação U e A2 da AS02, famílias C1/C2/C4-DM e todas as evidências históricas. Nenhuma reexecução altera `as05-pilot-owner-exploratory-001` ou `as05-prospective-plan-v1.json`.

## Proposed Architecture and Contracts

- `experiments/formulation-comparison/as05_diag_core.py`: plano derivado do piloto original, worker FC-01, K instrumentado, compilação pelo AS02, agrupamento alternativo estrutural, checagem de identidade, comparação de LP, checkpoints SHA e relatório por estágio.
- `experiments/formulation-comparison/run_as05_diagnostics.py`: CLI de `--init-plan`, `--check-plan`, `--stage cuts|censored|grouping`, `--resume` e `--verify`.
- `experiments/formulation-comparison/as05_diag_analysis.py` + `run_as05_diag_analysis.py`: consolidação de três estágios sem solves adicionais.
- `experiments/formulation-comparison/test_as05_diag.py`: testes puros, SciPy pequeno e integração artificial sem Gurobi.
- `experiments/formulation-comparison/fc_budget.py`: identificar subfases `k_*` como preparação mesmo no timeout.
- `results/benchmark/as05-diagnostic-plan-v1.json`: adendo pós-piloto imutável, vinculado aos hashes reais da AS-05.

## Experimental Arms

| Estágio | Casos | Braços | Budget |
|---|---|---|---|
| cuts | `puc-w3c571-seed-r1`, `vienna-I056-regiao-f4` | somente C1/C2/C4-DM e validação | 300 s/caso |
| censored | mesmos 2 | U, U_K, A2_K (grau) | 300 s/braço |
| grouping | os 4 completados na AS05 | U_K, A2_K@reachability_degree, @balanced, @reachability_overlap | 90 s/braço |

`reachability_overlap` é um **novo controle exploratório**, não uma política normativa AS03: escolhe duas âncoras estruturalmente distintas pela Jaccard dos vizinhos de alcance e divide a ordenação em grupos balanceados. Não consulta valor LP nem usa dados de avaliação.

## Regras de tempo/custo

- U não prepara cortes. O hash de K de referência é associado no relatório após executar U_K; **não é tempo de execução de U**.
- U_K e A2_K preparam e validam K no próprio processo e orçamento. O perfil de K não é cobrado duas vezes no mesmo braço: cortes são gerados uma vez e validados com N+/N− já calculadas.
- C1/C2/C4-DM e verificação não podem ser pulados, mesmo quando demorados.
- `solver_runtime_s` é métrica reportada pelo Gurobi; não confundir com `wall_total_s`, que inclui spawn, carga, K, construção, solve e validação.
- Após timeout/erro, preservar status e tempos de fases enviados pelo supervisor; `lp_opt_value=None`.
- Comparações LP precisam de mesma identidade estrutural, seed, K e configuração; se falhar, marcar `INTEGRITY_ERROR` ou `NOT_COMPARABLE`.

## Artifacts and Traceability

O relatório de cada estágio grava `checkpoints/{case}/arm-NN.json`, seu `.sha256`, `report.json`, `arms.csv`, `plan.json`, `manifest.json`. `--resume` recusa arquivo com SHA divergente. Consolidação grava `diagnostic_analysis.json`, `.md`, `grouping.csv`, manifesto. O plano e o relatório de origem são referenciados por SHA.

## Threats to Validity

Diagnóstico é posterior aos resultados do piloto: **não reinterpreta o gate original**. `reachability_overlap` e a seleção dos quatro casos são hipóteses de desenvolvimento, não resultados de avaliação independentes. Um ganho localizado pode exigir repetição em seeds e grafos de outra origem, em novo protocolo, antes de promoção da formulação A. K continua aguardando homologação matemática independente.

## Exit Gate

Implementação: testes AS05-DIAG e regressões AS04/AS05/FC-01, compilação, specs válidas. Experimentos: três estágios reais concluídos e relatórios verificados. Ciência: verificador humano independente (não fornecido por este pacote).
