# AS25.1 — Pré-registro da campanha LP de confirmação FC-R

**Arquivo congelado:** [`as251-preregistro-fcr-lp.json`](as251-preregistro-fcr-lp.json). O runner `experiments/cuts/run_fcr_lp_as251.py` recusa qualquer divergência.
**Spec:** `specs/as-25-1-fcr-otimizacao-separacao/spec.md`.
**Estado:** congelado antes de qualquer execução da campanha AS25.1. O diagnóstico pós-hoc (`results/benchmark/as251-diagnostico-001`) motivou a política e **não entra no gate**.

## O que é preservado da AS25

- Os mesmos seis casos de desenvolvimento, com os mesmos SHA-256 e `raw_graph_id` (herdados do pré-registro AS25, cujo SHA-256 fica gravado no JSON).
- Os mesmos parâmetros Gurobi (`Method=1`, `Threads=4`, `Seed=42`, tolerâncias 1e-6, `MemLimit` 16 GiB).
- Orçamento total de 90 s de parede por braço, em processo próprio, incluindo leitura, `K`, índice, separação e reotimizações.
- Mesma política numérica FC-R: 12 regiões maiores no máximo, 6 rodadas, 32 cortes por rodada, 128 no total, violação mínima 1e-6, 12 s de separação por rodada, 2 s mínimos para reotimizar.
- O gate AS25 é recalculado sem alteração, apenas como referência.

## Braços

| Braço | Separador | Ordem | Regiões maiores |
|---|---|---|---|
| `U_K` | — | — | — |
| `U_K_FCR_AS25` | `IndexedFCR` (AS25, linhas canônicas) | lexicográfica | sempre |
| `U_K_FCR_INFRA` | `FastIndexedFCR` | lexicográfica | sempre |
| `U_K_FCR_AS251` | `FastIndexedFCR` | lexicográfica | só quando nenhum singleton novo viola |

`U_K_FCR_INFRA` isola o efeito de infraestrutura: deve emitir as mesmas linhas, rodada a rodada, que `U_K_FCR_AS25`. `U_K_FCR_AS251` acrescenta a nova seleção.

## Registro por braço e rodada

Tempos de leitura, `K`, construção do modelo, LP base, índice de regiões, extração do ponto, separação, inserção e reotimização. Por rodada: status do separador, contadores, linhas e nnz adicionados, digests SHA-256 das assinaturas e dos termos, objetivo LP após a reotimização. RSS de pico.

## Classificação AS25.1 (critério adicional, fixado agora)

Ganho e custo são medidos em `U_K_FCR_AS251` contra `U_K`; pares só entre braços `OPTIMAL`.

- **A** — em ≥ 2 grafos brutos: ganho ≥ 1%, custo ≤ 2×, objetivo não decrescente, cobertura completa (singletons completos em toda varredura; maiores completas ou adiadas; sem teto de cortes).
- **C** — não A, e ganho ≥ 1% em ≥ 2 grafos brutos sem considerar custo e cobertura.
- **B** — não A nem C, e eficiência demonstrada: em ≥ 1 caso com `U_K`, `U_K_FCR_AS25` e `U_K_FCR_INFRA` ótimos, INFRA equivalente à AS25 em todos esses casos, e mediana de `1 − overhead_INFRA/overhead_AS25` ≥ 0,5 (`overhead = parede do braço − parede de U_K`).
- **D** — caso contrário.

Equivalência INFRA: digests de assinatura e de termos iguais em todas as rodadas e diferença de objetivo ≤ 1e-6·max(1,|obj|). Casos em que `U_K_FCR_AS25` é censurado e INFRA termina são listados como resgatados, fora da mediana.

## Expectativa declarada antes da execução

Pelo diagnóstico pós-hoc, o fecho da família declarada fica abaixo de 1% em CC9, MAPF e CC3, e Vienna I056 e PUC W3C571 são censurados já em `U_K`. A classe A é, portanto, inalcançável nesta amostra; o resultado esperado é **B**. Este registro existe para que a campanha confirme ou refute essa expectativa, não para mudá-la depois.

## Limites

Somente desenvolvimento, somente LP, sem MIP, sem grafos reservados, sem alterar COMP, K ou o código AS24/AS25. Calibração e confirmação usam as mesmas seis instâncias; generalização exige AS27. Nenhuma classe autoriza AS26 automaticamente.

## Execução

```bash
poetry run python experiments/cuts/run_fcr_lp_as251.py --output-dir /tmp/as251-dry --dry-run
poetry run python experiments/cuts/run_fcr_lp_as251.py --output-dir results/benchmark/as251-fcr-lp-001
poetry run python experiments/cuts/analyze_fcr_lp_as251.py --results-dir results/benchmark/as251-fcr-lp-001
```

Executar após commit do código, para que `source_has_tracked_modifications` seja `false`.
