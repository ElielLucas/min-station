# AS05-DIAG — Adendo de implementação v2 (não altera spec original)

## Objetivo

Corrigir a falta de `grouping_policy` de `A2_K` na etapa `censored` e substituir o gargalo de validação K por um algoritmo **exato**, preservando os geradores e os cortes, o modelo matemático, a autorização exploratória, os orçamentos e os registros originais. Executar novo reensaio separado; não promover o gate científico automaticamente.

## Requisitos

- **D2-01:** plano v2 imutável vinculado ao plano e aos três manifestos v1; duas instâncias originais; nenhuma instância de avaliação nova.
- **D2-02:** política `reachability_degree` explicitamente no braço A2+K; seed original; nunca trocar por política selecionada após observar LP.
- **D2-03:** todos os cortes K devem passar verificação de validade exata, sem alterar hashes, famílias ou modelos; sentinela histórica adicional.
- **D2-04:** método legado permanece default da v1, método `bitset-v2` é específico da v2 e constará em plano, checkpoints e evidências.
- **D2-05:** nenhum timeout gera LB LP; nenhum WORKER_ERROR desaparece; relatório retém os seis braços dos dois casos.
- **D2-06:** retomada só de checkpoints íntegros e saída em diretórios novos.
- **D2-07:** análise combina novo diagnóstico de cortes/censurados e apenas a *proveniência* do agrupamento v1, sem apagar os resultados exploratórios históricos ou liberar a AS06.

## Evidências e validação

- `experiments/formulation-comparison/test_as05_diag_retest_v2.py`: comparação diferencial exaustiva com `is_valid_cut`, testes de matching/Hall, mutação, SHA, erro de política, plan freeze, pipeline 2×3, saída imutável e integridade.
- `results/benchmark/as05-diagnostic-retest-plan-v2.json`: plano prospectivo dos solves v2.
- `docs/technical/plans/execucao/as05-reteste-v2-validacao-k.md`: discussão técnica e limitações.

## Status

Implementação e `cuts` reais na máquina de preparação verificados; **solves LP v2 com Gurobi ainda não executados**; gate científico continua `PENDING`.
