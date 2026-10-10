# FC-04 — Validação da implementação (pré-homologação)

**Data:** 2026-10-10  
**Base:** FC-03 implementada; suíte FC-02/FC-03 previamente validada pelo usuário com Gurobi.  
**Estado:** IMPLEMENTADA / **HOMOLOGAÇÃO INTEGRADA PENDENTE**.

## Matriz de aceitação

| ID | Evidência implementada | Resultado local |
|---|---|---|
| AUDIT-01 | `fc_instances.py:114` recalcula SHA-256 bruto e de conteúdo normalizado, registra `MATCH` ou `NOT_DECLARED` | PASS (testes positivos/negativos) |
| AUDIT-02 | `fc_instances.py:114` aborta `INTEGRITY_ERROR` para qualquer hash declarado divergente | PASS |
| AUDIT-03 | `fc_instances.py:76,114` confere n, m, arestas/arcos, r, r_usado e cabeçalhos N/M; métricas não suportadas ficam `UNSUPPORTED` | PASS |
| AUDIT-04 | `fc_integrity.py:48,59,72`; `fc_reporting.py:252,296`; `run_comparison.py:72` inventariam código, entrada, saída, CSV, log e figuras antes do checksum final; fonte não pode mudar entre início e fim | PASS (smoke sem solver) |
| AUDIT-05 | `verify_comparison_artifacts.py:92` audita em modo somente leitura com caminhos relativos/absolutos, faltantes e adulterações | PASS (smoke e testes negativos) |
| AUDIT-06 | `fc_integrity.py:83`, auditor independente e protocolo: agrupamento por instância única; A `lp_fcc_k` e B `fcc_k` contempladas | PASS (9/10 histórico e casos de abstenção) |

## Testes realizados neste ambiente

1. `python -m unittest discover -s experiments/formulation-comparison -p 'test_fc04_*.py' -q`: **27 testes PASS**.
2. `python -m compileall -q experiments/formulation-comparison`: **PASS**.
3. Smoke real de manifesto usando instâncias e scripts locais, sem Gurobi: auditor retornou `(True, [])`; após adulterar `results.csv`, retornou `HASH_MISMATCH` (**PASS**).
4. `validate_spec.py --strict` e `validate_tasks.py --strict`: **0 erros, 0 avisos**.
5. CSV histórico `scalability-20261010T071119Z/results.csv`: **9/10 instâncias distintas com CAP** e **1/10 OPTIMAL**; não inferir nada para as outras instâncias.

## Pendências para homologação (não declarar PASS)

- Executar a **suíte integral com Gurobi real** no ambiente do projeto, pois `gurobipy` não está instalado aqui. Resultados anteriores da FC-03 não substituem esta regressão.
- Executar `python -m ruff check experiments/formulation-comparison`; Ruff não está instalado aqui.
- Rodar piloto FC-04 real (`--tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline --time-limit 120 --lp-time-limit 60 --plots`), verificar `manifest.sha256` com CLI do auditor e conferir `PAIR_VALID` em ambas as instâncias.
- Para aceitação de escalabilidade na versão nova, executar `--tier scalability` somente se o orçamento/cap tiver sido aprovado; o teste sobre o CSV histórico **não é uma nova execução**.
- Revisão independente dos artefatos completos e do manifesto feita no ambiente final. O checksum não é assinatura autenticada.

## Preservação

Nenhum arquivo ou gate congelado N1/N2 foi modificado. Os relatórios históricos sob `results/formulation-comparison/` foram usados apenas como leitura; execução real escreve em um novo diretório. A FC-04 não executa verificador racional e não muda `NOT_CERTIFIED`/`INCONCLUSIVE` da FC-03.
