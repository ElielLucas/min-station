# AS28 — Evidência de validação local

**Status atual (17/10/2026):** `REAL_LP_EXECUTED_NO_SIGNAL_BOUNDED_POLICY`. **Histórico:** `READY_FOR_GUROBI_REVIEW` era o status da validação local anterior à campanha.
**Snapshot de origem:** `min-station(20261017-175756).zip`, branch de trabalho indicada pelo usuário: `novos_testes`.

## Matemática e código

- 9 testes novos em `test_as28_c3_screen.py`: passaram. Incluem BFS independente e enumeração de instalações fisicamente viáveis (`independent_validator.viavel`) em 24 micrografos aleatórios conectados, com `r=1,2`, origens/destinos possivelmente coincidentes, além de testes dirigidos.
- Suíte completa `python -m unittest discover -s experiments/cuts -p 'test_*.py' -q`: **253 testes OK, 2 pulados**, após extrair do ZIP de origem os JSONs históricos necessários aos testes AS18, AS23–AS25. Os dois skips são dependências ausentes de Gurobi neste ambiente.
- O `cuts.py` histórico não foi modificado; o wrapper confere adicionalmente que cada suporte intercepta todos os caminhos do terminal selecionado até o conjunto de terminais oposto.

## Protocolo

- `python experiments/cuts/run_c3_lp_as28.py --dry-run --output-dir /mnt/data/as28-c3-dryrun-test` → `NOT_EXECUTED_DRY_RUN`; 6 casos, 12 braços; nenhum LP resolvido.
- O dry-run usa os seis casos e suas SHA-256 da AS25.1, com validação de manifesto e código congelado.
- A campanha **não foi executada**, pois a instalação de Gurobi não está disponível neste ambiente.

## Limitações da validação anterior à campanha

- Os testes validam a matemática de cada corte topologicamente certificado, não o desempenho de LP real nem sua força marginal.
- A seleção é limitada a até oito terminais por lado e duas rodadas. Mesmo `NO_SIGNAL_BOUNDED_POLICY` não significa redundância global de C3.
- O separador histórico Edmonds–Karp pode extrapolar a janela soft de 12 s em uma chamada indivisível; o processo aplica timeout hard de 90 s por braço.
- Sem Parecer Opus independente, sem resultados AS28 reais, sem aprovação para AS26.

## Evidência adicionada após a campanha Gurobi (17/10/2026)

O pesquisador informou execução local de `253` testes (`OK`) com Gurobi ativo e a campanha real `results/benchmark/as28-c3-lp-001/`. Inspeção posterior dos JSONs do ZIP recebido confirmou `rows=12`, `paired_optimal=4`, `qualified_raw_graphs=[]`, duas censuras (`Vienna` e `W3C571`) e classificação `NO_SIGNAL_BOUNDED_POLICY`. Todos os seis hashes de módulos em `manifest.json` correspondem aos arquivos do ZIP. Manifesto declara commit `6f9e6e1e60e41876d916ca10fc82dd0aed43c275` e árvore rastreada sem modificações.

As varreduras da amostra selecionada foram concluídas nos quatro pares ótimos, não o universo C3. Apenas BIP42 apresentou ganho próximo de 1% (0,9282%; cinco cortes); seu teto inteiro passou numericamente de 32 para 33, **abaixo de LB*=35 já obtido pela linha de base histórica**. Nenhum dos quatro limites inteiros de C3 superou o LB* correspondente.

Ver `docs/technical/reference/experimentos/as28-resultado-lp-c3.md` para tabela, tempos, integridade, censuras e recomendação STOP. **Não há autorização automática de MIP/AS26.** Revisão independente ou decisão final do pesquisador ainda pendentes.
