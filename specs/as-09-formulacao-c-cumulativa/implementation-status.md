# AS-09 — Estado após protótipo inicial

| Tarefa | Estado | Evidência | Pendência |
|---|---|---|---|
| T1: especificação C e equivalência LP | `PROOF_REVIEW_REQUIRED` | `docs/technical/reference/formulacoes/as09-c-cumulativa-projecao.md` + amostras numéricas C/U | Revisão matemática independente da decomposição U↔C |
| T2: compilador cumulativo corrigido | `IMPLEMENTED_EXPLORATORY` | `experiments/alternative-formulations/as09_model_c.py` e testes `test_as09_model_c.py` | Validação Gurobi local e ampliação de fixtures reais |
| T3: custo completo | `RUNNER_IMPLEMENTED_NOT_EXECUTED_GUROBI` | `run_as09_screen.py` e `run_as09_pilot.py`; protocolo pareado U/C com e sem K, 300s/braço, hashes, wall e RSS | Executar no ambiente com Gurobi, analisar censuras e métricas reais |
| T4: gate custo-benefício | `PRE_REGISTERED_NOT_AUTHORIZED` | `analyze()` do piloto aplica gate exploratório e bloqueia promoção sem revisão matemática | Depende T1 revisão independente e T3 medição completa |

A AS-09 é independente da AS-08. Nenhuma saída histórica de AS-08/FC/N1/N2 deve ser modificada. Os arquivos fornecidos são um patch de trabalho; não são commits no repositório do usuário.
