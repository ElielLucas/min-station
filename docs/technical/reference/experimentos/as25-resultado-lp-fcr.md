# AS25 — Piloto LP pareado FC-R: estado de execução

**Status:** implementação do runner, analisador e pré-registro concluída; **campanha real Gurobi NÃO executada** nesta entrega.  
**Gate científico:** PENDING_REAL_LP_AND_INDEPENDENT_REVIEW.  
**Baseline:** `U`/`U_K` compilados sem alterar `compile_u`, `prepare_K` ou as famílias K.  
**Referência:** [`as25-preregistro-fcr-lp.md`](../../plans/execucao/as25-preregistro-fcr-lp.md).

## Evidência disponível

- 18 testes novos da AS25 verificam, entre outros, equivalência da separação indexada e a AS24 em seis pontos racionais, 24 linhas no dry-run, 12 linhas da ablação isolada, append-only, hashes, censuras, e gate conservador.
- No microteste de integração usando SciPy/HiGHS, seis rodadas de separação sobre uma solução ótima da testemunha sintética elevaram o bound de **1 para 1,175**; não se trata da campanha Gurobi real nem prova de ganho nas instâncias de desenvolvimento.
- A suíte geral da implementação contém 204 testes no snapshot examinado; este número **não** é um resultado Gurobi nem substitui execução independente no checkout do pesquisador.
- Não foram criados resultados em `results/benchmark/as25-fcr-lp-001/`, já que uma pasta com esse nome deve ser inédita antes da execução efetiva.

## Registro da campanha real (pendente)

Depois de executar o runner no checkout do pesquisador, registrar aqui os arquivos `manifest.json`, `rows.json` e `analysis.json`, número de pares ótimos, censuras, ganho LP por grafo bruto e custo de parede por braço. Conferir também `--ablation` (rodada separada) e o SHA do commit para proveniência.

**Não há autorização automática para AS26.** Mesmo um eventual `GO_CANDIDATE_REVIEW` dependerá de avaliação científica e revisão independente dos dados e do código.
