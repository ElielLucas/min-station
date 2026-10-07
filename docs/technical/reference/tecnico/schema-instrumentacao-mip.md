# Instrumentação do MIP

`measure_mip` (`experiments/cuts/harness.py`) devolve, além dos campos já usados pelos runners:

| Campo | Origem | Custo |
|---|---|---|
| `node_count` | `NodeCount` depois de `optimize` | nenhum callback |
| `work` | atributo `Work` | nenhum callback |
| `time_modelo_s` | construção do modelo e dos cortes, fora do `optimize` | relógio local |
| `time_mip_s` | `optimize` | relógio local |
| `time_to_proof_s` | igual a `time_mip_s` quando o status é ótimo; senão ausente | não distingue prova de busca por si só |
| `time_to_first_incumbent_s` | primeiro `MIPSOL` | callback só de leitura |
| `time_to_best_incumbent_s` | último `MIPSOL` que melhorou o valor | mesmo callback |

`coletar_incumbente` é `False` por padrão. Com o padrão, os dois tempos de incumbente ficam vazios e o `optimize` não recebe callback, para não alterar a busca dos experimentos já publicados. `measure_lp` e `measure_root` não recebem esse callback: medem LP ou raiz em volume alto e não têm incumbente inteiro.

Não há estágio separado de heurística primal nem de pré-processamento dentro de `measure_mip`. Esses tempos não são inventados. O CBI (`solve_cbi`) já devolve o esquema usado no E12: `iterations`, `oracle_calls`, `n_cuts_total`, `n_z_cuts`, `master_time_s`, `oracle_time_s`, `node_count`. Esse retorno não foi substituído.

Exemplo populado, `verify_t9_instrumentacao.py`, caso `CaminhoABC`, um incumbente, status ótimo: o tempo do primeiro incumbente é igual ao do melhor, e os dois são menores ou iguais a `time_mip_s`. `TermRelay` repete o mesmo padrão com objetivo 1.

## O que cada runner grava

Varredura dos `run_e*.py` em 2026-10-03. Nenhum foi reexecutado.

| Runner | Grava `node_count` | Grava tempos de incumbente |
|---|---|---|
| `experiments/benchmark/run_e12.py` | sim, coluna do CSV | não |
| `run_e0`, `run_e1`, `run_e1prime`, `run_e2`, `run_e4`, `run_e6`, `run_e7`, `run_e8` | não | não |
| `run_e9`, `run_e10`, `run_e10b`, `run_e13`, `run_e14` | não | não |

`NodeCount` já estava no retorno de `measure_mip` antes desta instrumentação. Os tempos de incumbente são novos e só entram no CSV de um runner que passar `coletar_incumbente=True` e gravar os campos. Um `run_e*.py` novo faz isso; os históricos não foram alterados.
