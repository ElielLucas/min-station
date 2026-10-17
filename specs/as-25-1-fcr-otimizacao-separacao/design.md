# AS25.1 — Design técnico: separação FC-R otimizada

**Spec:** `spec.md`. **Status:** implementado; campanha pré-registrada, não executada.

## Diagnóstico que orienta o design

Medições em `results/benchmark/as251-diagnostico-001/` (classe `DIAGNOSTIC_POST_HOC`, mesma máquina, Gurobi 12.0.3, parâmetros AS25). Os traços rodaram três a três em paralelo; tempos absolutos dos traços são indicativos. O índice foi medido isolado, com `tracemalloc` ligado (sobrecarga incluída nos dois índices). Valores AS25 conferidos em `results/benchmark/as25-fcr-*/rows.json`.

### Custo por etapa (AS25, braço `U_K_FCR`, rows.json)

| Caso | Total | K | Índice de regiões | Separação | Reotimização | Índice / total |
|---|---:|---:|---:|---:|---:|---:|
| PUC CC9 | 6,51 s | 0,79 | 4,00 | 0,30 | 0,50 | 61% |
| PUC BIP42 | 39,46 s | 16,98 | 18,86 | 0,73 | 1,15 | 48% |
| MAPF Room | 28,80 s | 0,33 | 25,91 | 0,89 | 0,13 | 90% |
| PUCN CC3 (ablação singleton) | 33,59 s | 4,67 | 17,21 | 3,76 | 2,79 | 51% |

Inserção de linhas e extração do ponto LP somam < 0,3 s em todos os casos. Pico de RSS observado ≤ 134 MB; FC-R acrescenta 6–23 MB sobre `U_K`. Memória não é gargalo.

### Causa do custo do índice (cProfile, MAPF, |V|=682, |A|=11.622)

`choose_regions` → `region_excess` → `_graph`, que revalida todos os arcos de `H` a cada chamada. Com 313 regiões maiores candidatas e 682 singletons, foram 12.822 revalidações e 1,49·10⁸ avaliações do gerador de validação: 99% do tempo do índice. A complexidade efetiva é O(|V|·|A| + |A|²). O mesmo `_graph` roda dentro de `construct_row` para cada corte emitido (O(|A|) por corte).

### Qualidade dos cortes

- Teto de 32 cortes por rodada atingido em todas as rodadas de CC9 e BIP42; em BIP42, 180 cortes violados por rodada ficam fora (`CUT_CAP`). O teto total de 128 encerra CC9/BIP42 em 4 rodadas.
- Deduplicação: 0 duplicatas em toda a AS25; a mesma região volta com `Q` diferente (assinatura nova), não repetida.
- Densidade: 9 nnz/linha (CC9), 19 (BIP42), 22 (MAPF), 27 (CC3).
- Degenerescência: muitas rodadas mudam só o fluxo. MAPF: rodadas 1–2 sem ganho; CC3: 29 rodadas até o fecho com ganho 0.

### Fecho da família declarada (sem tetos, até não haver violação)

| Caso | COMP+K | Fecho singletons | Fecho singletons + 12 maiores | Rodadas (single / +maiores) | Reotimização acumulada |
|---|---:|---:|---:|---:|---:|
| PUC CC9 | 27,026786 | 27,082111 (+0,205%) | 27,082111 (+0,205%) | 14 / 17 | 1,6 s / 1,8 s |
| MAPF Room | 13,200000 | 13,280000 (+0,606%) | 13,280000 (+0,606%) | 16 / 37 | 0,3 s / 0,5 s |
| PUCN CC3 | 16,933333 | 16,933333 (0%) | 16,933333 (0%) | 29 / 34 | 38,8 s / 31,6 s |
| PUC BIP42 | 31,706052 | 32,077607 (+1,172%) | 32,077607 (+1,172%) | 40 / 40 | 406 s / 385 s |

Fonte: `closure-*.json`. O fecho é limite superior do ganho de qualquer política restrita a essas regiões (com a mesma tolerância). Regiões maiores não alteram o fecho em nenhum dos quatro casos. Em CC9, MAPF e CC3 nenhuma política alcança 1%. Em BIP42, 1% é cruzado na rodada 13, com 2.506 linhas e 79,1 s acumulados de separação, inserção e reotimização, além de ~17 s de preparação de `K`: excede o orçamento de 90 s e o teto de 2× COMP+K (≈ 35 s). Vienna I056 e PUC W3C571 são censurados já em COMP e COMP+K na AS25.

### Ablação MAPF explicada

A partir do mesmo ponto inicial, a política com regiões maiores adiciona na rodada 1 um superconjunto dos cortes singleton (13 singletons + 12 maiores). Daí em diante os pontos LP diferem e as famílias adicionadas deixam de ser aninhadas. Com `max_rounds=6`, nenhuma das duas converge (5 e 13 violados na última rodada). Sem teto de rodadas, ambas chegam a 13,280000. Não há violação de monotonicidade nem defeito: é truncamento de trajetórias distintas. As regiões maiores consomem rodadas (rodadas 3–5 com objetivo parado em 13,247059) sem acrescentar ao fecho.

### Seleção: alternativas comparadas (orçamento AS25: 32/rodada, 128 total, 6 rodadas)

| Política (`trace-*.json`) | CC9 | MAPF | BIP42 | CC3 |
|---|---:|---:|---:|---:|
| `as25` (lexicográfica, maiores sempre) | +0,109% | +0,417% | +0,025% | 0% |
| `infra` (mesma política, índice AS25.1) | +0,109% | +0,417% | +0,025% | 0% |
| `deficit`, maiores sempre | +0,114% | +0,417% | +0,0007% | 0% |
| `deficit_escalate` | +0,123% | +0,606% | 0,000% | 0% |
| `as251` (lexicográfica, singleton-primeiro) | +0,109% | +0,606% | +0,025% | 0% |
| `singleton` (só singletons) | +0,109% | +0,606% | +0,025% | 0% |

Um protótipo de rascunho também testou eficácia (`deficit`/norma euclidiana da linha): resultado idêntico a `deficit` em CC9 e MAPF; não foi mantido no código.

Decisão: manter ordem lexicográfica e adotar singleton-primeiro. A ordenação por violação não tem sinal consistente; o escalonamento nunca piorou e recupera o fecho em MAPF.

## Architecture Overview

```
run_fcr_lp_as251.py ──> FastIndexedFCR (fcr_lp_policy_as251.py)
        │                    ├── fast_region_plan  (== fcr_regions.choose_regions)
        │                    ├── CachedRegion.frontier (estático entre rodadas)
        │                    └── _row  (== fcr_rows.construct_row; audit opcional)
        ├──> IndexedFCR (AS25, inalterado) para o braço U_K_FCR_AS25
        └──> analyze_fcr_lp_as251.py ──> gate AS25 + classificação A/B/C/D
diagnose_fcr_as251.py ──> results/benchmark/as251-diagnostico-001 (pós-hoc)
```

## Code Reuse Analysis

| Artefato | Reuso |
|---|---|
| `fcr_rows.FCRRow`, `_graph`, `construct_row` | Tipo de linha, validação única de `H`, auditoria |
| `fcr_regions.RegionPlan` | Mesmo contrato de plano |
| `fcr_lp_policy.IndexedFCR` | Braço AS25 e oráculo de equivalência |
| `run_fcr_lp_as25._point`, `_add_fcr`, `_usage_mb` | Extração do ponto e inserção canônica |
| `run_h2_lp` helpers (`_solver`, `_optimize`, `_phase`, `validate_sources`, ...) | Mesmo LP e mesmo orçamento |
| `analyze_fcr_lp_as25._pair` | Mesmo pareamento e flag flow-only |

## Components

| Componente | Local | Contrato |
|---|---|---|
| Índice AS25.1 | `experiments/cuts/fcr_lp_policy_as251.py` | `FastIndexedFCR(instance, max_larger, include_larger, selection, larger_mode, audit_rows)`; `separate(...)` com o mesmo retorno de `IndexedFCR` mais `larger_deferred`, `nnz`, `selection_rank` |
| Diagnóstico | `experiments/cuts/diagnose_fcr_as251.py` | Modos `index` e `trace`; JSON `DIAGNOSTIC_POST_HOC` |
| Pré-registro | `docs/technical/plans/execucao/as251-preregistro-fcr-lp.{json,md}` | Casos/hashes AS25, solver, 90 s, política, braços, regra A/B/C/D |
| Runner | `experiments/cuts/run_fcr_lp_as251.py` | 4 braços × 6 casos, processo por braço, registro por rodada |
| Analisador | `experiments/cuts/analyze_fcr_lp_as251.py` | Gate AS25 verbatim + equivalência INFRA + A/B/C/D |
| Testes | `experiments/cuts/test_as251_fcr.py` | Equivalência, Q exato, escalonamento, runner, analisador |

## Braços

| Braço | Índice | Ordem | Regiões maiores | Papel |
|---|---|---|---|---|
| `U_K` | — | — | — | Referência |
| `U_K_FCR_AS25` | `IndexedFCR` | lexicográfica | sempre | Política original AS25 |
| `U_K_FCR_INFRA` | `FastIndexedFCR` | lexicográfica | sempre | Só infraestrutura; deve repetir linhas e objetivo AS25 |
| `U_K_FCR_AS251` | `FastIndexedFCR` | lexicográfica | singleton-primeiro | Infraestrutura + nova seleção |

## Riscos para a validade matemática

| Risco | Mitigação |
|---|---|
| Linha diferente da canônica | `audit_rows` em testes; digest de termos por rodada comparado entre `U_K_FCR_AS25` e `U_K_FCR_INFRA` na campanha |
| Cache obsoleto entre rodadas | Cache contém só estrutura de `H` (imutável); valores de `y`/`f` lidos a cada chamada; teste de chamadas repetidas |
| Plano de regiões diferente | Teste de igualdade com `choose_regions` em testemunha e instâncias aleatórias |
| Escalonamento declarar cobertura falsa | Status `COMPLETE_SINGLETONS_LARGER_DEFERRED`; `larger_checked` conta só o examinado; `global_region_separation=False` sempre |
| Tolerância float | Mesma aritmética e mesma tolerância 1e-6 da AS25 |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Não editar código AS24/AS25 | Novo módulo | Hashes das campanhas históricas e auditoria AS24 preservados |
| Auditoria por corte na campanha | Desligada | Custo O(\|A\|) por corte (D2); equivalência verificada por digest |
| Teto de rodadas | Mantido em 6 | Comparabilidade com AS25; o efeito do teto fica documentado (D4) |
| Sem alterar `Method`/parâmetros Gurobi | Mantidos | Reotimização em BIP42 é custo do solver, não do separador |
