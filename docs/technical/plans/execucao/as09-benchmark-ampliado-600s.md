# MIN-STATION — AS-09: benchmark ampliado 600 s (LP + MIP)

## Propósito e limites

Patch **incremental** para a branch `novos_testes`. Não edita o compilador COMP, o compilador C, os cortes K nem os resultados históricos. Amplia a AS-09 em 15 instâncias unitárias, com quatro braços por instância (**COMP, COMP+K, C, C+K**) e dois modos (**LP e MIP**). Total **120 execuções**, com teto **600 segundos por execução**, incluindo preparação, geração de alcance, geração e validação de K, construção, solver e validação física MIP. O pior caso puramente teórico é 20 horas, não uma previsão do tempo de execução.

**Classificação:** `EXPLORATORY_MIXED_SPLITS`. Inclui instâncias de desenvolvimento e de avaliação; **não ajuste decisões de formulação, parâmetros ou cortes usando resultados de avaliação**. Igualdade numérica LP em grafos reais **não substitui** a revisão formal pendente da equivalência de projeções LP entre C e COMP.

## Instâncias congeladas no plano

As seis anteriores são preservadas, literalmente:

1. `mapf-room-32-32-4-m10-f8`
2. `puc-bip42p-regiao-f2`
3. `puc-cc9-2p-seed-r1`
4. `puc-w3c571-seed-r1`
5. `pucn-cc3-10n-seed-r1`
6. `vienna-I056-regiao-f4`

Adicionadas:

7. `mapf-den312d-m50-f2-rho` (MAPF densa já investigada na AS-09)
8. `mapf-empty-32-32-m25-f4`
9. `mapf-maze-32-32-2-m10-f4`
10. `mapf-random-64-64-20-m100-f4`
11. `pace18-t2-061-regiao-f4` (PACE 2018)
12. `vienna-I052-regiao-f4`
13. `urb-apia-m10-f8` (rede urbana)
14. `b-b18-regiao-f2` (SteinLib B)
15. `i-i160-301-regiao-f2` (SteinLib I)

Todas as 15 foram conferidas contra o manifesto do ZIP fornecido, com `classe=principal`, grafo físico não direcionado unitário e autonomia inteira. Não inclui `lin23`/`lin37` nem amplia o domínio matemático de C para pesos não unitários.

## Instalar

Na raiz do projeto e com a branch `novos_testes` atualizada:

```bash
unzip -o ~/Downloads/min-station-AS09-benchmark-ampliado-600s.zip
```

O patch contém **somente arquivos novos**, sem substituição dos compiladores e benchmarks antigos:

- `experiments/alternative-formulations/run_as09_extended.py`
- `experiments/alternative-formulations/test_as09_extended.py`
- `docs/technical/plans/execucao/as09-benchmark-ampliado-600s.md`

## 1. Testar

```bash
PYTHONPATH=.:experiments/formulation-comparison poetry run python -m unittest discover \
  -s experiments/alternative-formulations -p 'test_as09_*.py' -v
```

Na versão analisada, foram aprovados **20 testes AS-09**, incluindo os **6 testes novos do benchmark ampliado**. Alguns testes de protocolo usam dados simulados e não são resultados de benchmark.

## 2. Criar o plano real (15 instâncias)

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --init-plan \
  --suite full \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --budget 600 \
  --max-variables 900000 \
  --max-constraints 350000 \
  --threads 4 \
  --mip-gap 0.0001 \
  --validation-reserve 45
```

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --check-plan --plan results/benchmark/as09-expanded-plan-600s-v1.json
```

`--init-plan` usa o manifesto atual e congela os hashes dos insumos e da implementação. Para iniciar outra campanha após mudar o código, gere **outro plano e uma nova pasta**. Os limites acima são de pré-montagem; ultrapassá-los marca `NOT_BUILT_SIZE`, **não** um resultado matemático negativo.

## 3. Executar primeiro LP (60 braços)

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --execute --mode LP \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001
```

Depois:

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --verify --mode LP \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001

PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --analyze --mode LP \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001
```

Resultados LP e análises parciais são guardados em `LP/`, `analysis-lp.md`, `analysis-lp.json`, `arms-lp.csv` e `pairs-lp.csv`.

## 4. Executar MIP (60 braços)

**Recomendação:** iniciar MIP apenas depois de verificar LP e conferir RAM disponível. O limite de 600 s é de tempo **wall**, não de memória. MIP reserva até 45 s do orçamento para validação de incumbentes pelo oráculo físico independente do projeto.

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --execute --mode MIP \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001
```

Se uma execução parar e restarem arquivos:

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --execute --mode MIP --resume \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001
```

`--resume` **não reexecuta nem sobrescreve** braços com arquivos já gerados, inclusive `TIME_LIMIT`, `NOT_BUILT_SIZE` ou `TIMEOUT_SOLVER`. Novas condições experimentais exigem outro plano/diretório.

## 5. Verificar e comparar LP + MIP

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --verify --mode ALL \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001

PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --analyze --mode ALL \
  --plan results/benchmark/as09-expanded-plan-600s-v1.json \
  --output-dir results/benchmark/as09-expanded-600s-001
```

Arquivos finais:

- `results/benchmark/as09-expanded-600s-001/analysis-all.md` — tabelas e comparações pareadas;
- `analysis-all.json` — dados analíticos estruturados;
- `arms-all.csv` — todos os braços, com status, LP/UB/LB/gap, tempo, tamanho, RSS, nós, primeira UB;
- `pairs-all.csv` — pares COMP×C, separados por modo e presença de K, com economias de tempo, memória, variáveis, coeficientes não nulos e diferença de gap;
- `LP/manifest.json` e `MIP/manifest.json` — hashes de integridade;
- `LP/<instancia>--<braco>.json` e `MIP/<instancia>--<braco>.json` — detalhes e fases de cada execução.

**LP:** só há valor reportado em `OPTIMAL_NUMERIC`. Timeouts, ausência de montagem e erros permanecem censurados.

**MIP:** o limite inferior `mip_numeric_bound` é dado pelo Gurobi (numérico); o limite superior publicado é o objetivo de uma instalação validada pelo **oráculo físico independente**. O `validated_mip_gap` é calculado como `max(0, (UB_fisico - LB_numerico)/max(1, |UB_fisico|))`, e só existe quando **ambos** estão disponíveis. A métrica `time_to_first_validated_ub_solver_s` só é apresentada se um evento correspondente foi observado. O tempo total inclui a preparação; portanto, não é igual ao tempo do solver.

Se o Gurobi atinge seu `TimeLimit` mas devolve um resultado MIP com bound e incumbente validada, esses valores são preservados com status `TIME_LIMIT`. Se o supervisor precisa matar o processo, é publicado `TIMEOUT_SOLVER` **sem inventar UB, LB ou gap**.

## 6. Smoke opcional de protocolo (2 instâncias)

Para validar a sequência operacional antes da campanha longa, use `--suite smoke` em um plano e saída **separados**:

```bash
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --init-plan --suite smoke --budget 600 \
  --plan results/benchmark/as09-expanded-smoke-plan-v1.json

PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_extended.py \
  --execute --mode LP \
  --plan results/benchmark/as09-expanded-smoke-plan-v1.json \
  --output-dir results/benchmark/as09-expanded-smoke-001
```

Esse smoke não substitui a campanha maior, não produz prova LP e não contém comparações MIP até executar `--mode MIP`.

## Notas importantes

1. Esta campanha contém explicitamente instâncias de **avaliação** (além das seis de desenvolvimento). Trate a campanha como uma inspeção exploratória de generalização, não como o conjunto final de teste cego para homologação.
2. A equivalência LP das projeções e a relação entre os problemas MIP precisam de **prova formal independente** antes de reivindicações científicas gerais.
3. O script reutiliza `_solve_mip` da AS-06 para validar incumbentes; não modifica o Gurobi, não cria cortes dinâmicos e não implementa warm start.
4. O ambiente usado na preparação do patch **não tem Gurobi**. Foram executados testes unitários, integridade e validação do carregamento das 15 instâncias, mas a campanha real de 600 segundos deve ser executada no computador com licença Gurobi.
5. Experimentos em uma única seed são exploratórios. Se houver ganhos promissores, planeje replicações pré-registradas com múltiplas seeds, na mesma máquina, antes de discutir significância ou ganhos estatisticamente estáveis.
