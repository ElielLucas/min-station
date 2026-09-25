# Experimento de estratégias isoladas

Coloque estes três arquivos dentro da pasta `preprocessamento/` do projeto:

- `experimento_estrategias.py`
- `estrategias_preprocess.py`
- `resultados_estrategias.py`

Eles reutilizam, sem substituir, os arquivos já existentes:

- `modelo_min_station_das_preprocess.py`
- `resultados_preprocess.py`

## Execução comparável ao experimento de 1200 segundos

Execute na raiz do repositório:

```bash
PYTHONHASHSEED=0 poetry run python -u -m preprocessamento.experimento_estrategias \
  --inputs-dir ./instancias \
  --experiment-id artigo_estrategias_isoladas_1200 \
  --reference-runs-csv ./experimentos_preprocess/artigo_preprocess_1200/runs.csv \
  --time-limit 1200 \
  --budget-mode total \
  --threads 12 \
  --seeds 0 \
  2>&1 | tee "logs/artigo_estrategias_isoladas_1200_$(date +%Y%m%d_%H%M%S).txt"
```

Por padrão, o comando executa apenas:

1. `somente_folhas`;
2. `somente_alcance`;
3. `somente_dominancia`.

O baseline e o pré-processamento completo não são reexecutados. Eles são lidos
do CSV informado em `--reference-runs-csv` e incorporados ao comparativo.

## Arquivos de saída

Na pasta `experimentos_preprocess/artigo_estrategias_isoladas_1200/` serão
criados:

- `runs.csv`: uma linha por execução isolada, com todas as métricas já usadas;
- `comparison_strategies.csv`: uma linha por instância, seed e estratégia,
  sempre comparada ao baseline;
- JSON, logs do Gurobi, logs de pré-processamento, séries temporais e gráficos.

No comparativo, confira especialmente:

- `config_compatible`: mesmo limite, modo de orçamento, threads, seed e arquivo
  de instância do baseline;
- `environment_compatible`: mesma versão do Gurobi, máquina e plataforma;
- `same_git_sha`: informação adicional de rastreabilidade; pode ser falsa se os
  novos scripts tiverem sido commitados depois do experimento anterior.

## Retomar após interrupção

Repita o mesmo comando com o mesmo `--experiment-id`. Os `run_id` já presentes
em `runs.csv` serão ignorados. Use `--rerun` somente quando quiser executar tudo
novamente.

## Executar uma seleção específica

```bash
PYTHONHASHSEED=0 poetry run python -u -m preprocessamento.experimento_estrategias \
  --inputs-dir ./instancias \
  --experiment-id teste_folhas_alcance_300 \
  --strategies somente_folhas somente_alcance \
  --time-limit 300 \
  --budget-mode total \
  --threads 12 \
  --seeds 0
```

As opções adicionais `sem_preprocessamento` e `com_preprocessamento` também são
aceitas em `--strategies`, mas não fazem parte do padrão porque seus resultados
já existem.
