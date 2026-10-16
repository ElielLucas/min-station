# AS20 — Pré-registro do LP HL independente

**Criado em 15/10/2026 antes de qualquer execução numérica real AS20.**

O arquivo canônico `as20-preregistro-hl-lp.json` congela os seis grafos brutos de desenvolvimento da AS16 e os SHA256 de suas fontes, sem tocar instâncias de avaliação. A proposta HL decorre da construção AS13 e da certificação K4 AS19, não de GO de H2 (AS16/AS18).

## Comparação

- `U_K`: LP de `compile_u` + todos cortes K congelados.
- `U_K_HL`: mesmo LP + separação física HL uma rodada sobre o `y*` de `COMP+K`; resolve novamente se emitir cortes.
- Todos os tempos incluem carregamento, preparação K, construção, solves, seleção de suportes, enumeração e imposição. **90 segundos de parede por braço**, subprocessos separados, mesmos parâmetros Gurobi AS16.
- Suporte até 10, até 3 propostas, até 24 pares de K elegíveis, orçamento do oráculo até 24s total e 12s/suporte, 2200 consultas; no máximo 3 cortes unitários.
- Ordenação pré-fixada sem busca adaptativa em instâncias de avaliação. Suportes acima de 10 são excluídos inteiros, nunca truncados; falta de suporte e orçamento parcial são registrados.

## Gate

- `GO_CANDIDATE_REVIEW`: pelo menos dois grafos brutos independentes com aumento ≥1% do limite LP e tempo total HL/K ≤2, com todos seis casos executados. **Não** autoriza MIP.
- `NO_GAIN_IN_BOUNDED_SCREEN`: seis pares ótimos, triagem local completa, sem dois grafos favoráveis. **Não** descarta HL em geral.
- `INVESTIGATE`: qualquer insuficiência de cobertura, censura, subset ou falha de certificação.

Não executar repetições, alterar limites ou trocar coeficientes após observar resultados sem novo protocolo versionado.

## Execução reprodutível

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
poetry run python experiments/cuts/run_hl_lp.py --output-dir results/benchmark/as20-hl-lp-dry-001 --dry-run
poetry run python experiments/cuts/run_hl_lp.py --output-dir results/benchmark/as20-hl-lp-001
```

### Smoke menor (não gera conclusão de gate)

```bash
poetry run python experiments/cuts/run_hl_lp.py \
  --output-dir results/benchmark/as20-hl-lp-smoke-001 \
  --cases puc-cc9-2p-seed-r1
```

Saídas `manifest.json`, `rows.json` e `analysis.json` são append-only em diretório inédito; usar outro nome em novas execuções.
