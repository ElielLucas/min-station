# AS28 — Pré-registro LP de C3-cut (antes da campanha)

**Estado:** FROZEN BEFORE LP CAMPAIGN.
**Plano executável:** `as28-preregistro-c3-lp.json`. Não editar após a execução.
**Spec:** `specs/as-28-c3-cut-triagem-lp/`.
**Controles:** `U_K` × `U_K_C3`, somente relaxação linear, dois braços em cada uma das seis instâncias de desenvolvimento de AS25.1.

## Hipótese e possível refutação

Há uma hipótese de que cortes individuais por origem/destino adicionem informação LP material, não recuperada por COMP+K. Confirmar sinal exige pelo menos 1% de ganho LP em dois grafos brutos independentes, razão de tempo total até 2× e as varreduras **da amostra selecionada** completas; censuras não são sucesso. A política usa amostra fixa de oito terminais por lado, até duas rodadas e no máximo 32 cortes no braço. Se não mostrar ganho material, **encerrar essa política** e discutir formulações alternativas; não inferir a redundância de toda C3.

## Sem mudança retrospectiva

Não modificar benchmarks anteriores, resultados AS25/AS25.1, `cuts.py`, COMP, K, H2, HL ou FC-R. Não acessar a partição de avaliação. Não criar MIP. Não usar corte C3 no branched solver ou callback nesta etapa. A implementação desta etapa não reivindica uma família nova.

## Execução após commit e revisão da árvore

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
poetry run python experiments/cuts/run_c3_lp_as28.py \
  --dry-run --output-dir results/benchmark/as28-c3-dryrun-local-001
poetry run python experiments/cuts/run_c3_lp_as28.py \
  --output-dir results/benchmark/as28-c3-lp-001
poetry run python experiments/cuts/analyze_c3_lp_as28.py \
  --results-dir results/benchmark/as28-c3-lp-001
```

**Observação:** arquivos de saída são append-only; não repetir em diretório já existente. A comparação real deve ser executada em checkout limpo e Gurobi licenciado. O dry-run não constitui evidência LP.
