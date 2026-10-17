# AS25.1 — Diagnóstico e otimização da separação FC-R

**Veredito:** o custo da AS25 vinha de bookkeeping evitável e foi removido sem mudar nenhuma linha FC-R. A diferença da ablação MAPF é truncamento, não defeito. Mesmo com o separador otimizado, o fecho da família declarada fica abaixo de 1% em três dos quatro casos com LP ótimo, e em BIP42 o 1% custa ≈ 5,6× COMP+K. Pelo diagnóstico, a classe esperada da AS25.1 é **B**: ganho de eficiência real, ganho LP insuficiente, AS26 continua bloqueada. A campanha de confirmação está pré-registrada e **não foi executada**.

**Spec:** `specs/as-25-1-fcr-otimizacao-separacao/`. **Evidência:** `results/benchmark/as251-diagnostico-001/` (classe `DIAGNOSTIC_POST_HOC`, fora de qualquer gate). **Escopo:** problema de Das, baseline COMP+K inalterado, seis casos de desenvolvimento da AS25, somente LP.

## 1. Fontes conferidas

- AS25 principal e ablação: `results/benchmark/as25-fcr-lp-001/rows.json`, `as25-fcr-ablation-001/rows.json`. Os hashes de código no manifesto AS25 coincidem com os arquivos atuais de `fcr_*.py` e do runner AS25.
- **Divergência documental:** `docs/technical/reference/experimentos/as25-resultado-lp-fcr.md`, `specs/as-25-fcr-lp-pareado/{spec,validation}.md` e `plano-fcr-as23-as27.md` ainda dizem que a campanha AS25 não foi executada, mas os três diretórios de resultado existem (gate `INVESTIGATE`). Esta entrega não reescreve esses documentos históricos; a reconciliação fica para o pesquisador.

## 2. Gargalos confirmados

| Etapa | Evidência | Causa | Prioridade |
|---|---|---|---|
| Índice de regiões | 48–90% da parede do braço `U_K_FCR` (AS25); CC3 com regiões maiores: 170 s, acima dos 90 s | `region_excess` → `_graph` revalida todos os arcos de `H` por região: O(\|V\|·\|A\| + \|A\|²). cProfile MAPF: 12.822 revalidações, 99% do tempo | 1 |
| Montagem das linhas | CC3: ~0,9 s/rodada de separação com 27.000 arcos | `construct_row` revalida `H` e refaz a fronteira, O(\|A\|) por corte | 2 |
| Fronteiras entre rodadas | Código `fcr_lp_policy.py:57-70` | Fronteira estática recalculada a cada rodada | 3 |
| Reotimização LP | BIP42 sem tetos: 0,6 s → 17 s por rodada; 385–406 s no fecho | Custo do solver com milhares de linhas densas e degenerescência | Não é do separador |
| Inserção, extração do ponto, memória | < 0,3 s; RSS ≤ 134 MB | — | Não é gargalo |

Índice isolado (`index-as25-vs-as251.json`, com `tracemalloc` nos dois):

| Caso | \|V\| | \|A(H)\| | AS25 singletons | AS25.1 singletons | AS25 +maiores | AS25.1 +maiores | Plano igual |
|---|---:|---:|---:|---:|---:|---:|---|
| PUC CC9 | 512 | 4.608 | 0,89 s | 0,022 s | 4,65 s | 0,071 s | sim |
| PUC BIP42 | 1.200 | 7.964 | 3,62 s | 0,086 s | 22,32 s | 0,191 s | sim |
| PUCN CC3 | 1.000 | 27.000 | 12,12 s | 0,120 s | 170,17 s | 0,346 s | sim |
| MAPF Room | 682 | 11.622 | 2,89 s | 0,044 s | 28,22 s | 0,124 s | sim |
| Vienna I056 | 1.991 | 381.600 | — | 2,31 s | — | 4,94 s | — |
| PUC W3C571 | 3.997 | 20.556 | — | 0,24 s | — | 3,30 s | — |

## 3. Qualidade dos cortes

- Teto de 32/rodada ativo em todas as rodadas de CC9 e BIP42; em BIP42, 167–180 linhas violadas por rodada ficam fora. O teto de 128 encerra CC9 e BIP42 em 4 rodadas.
- Duplicatas: 0 em toda a AS25. A mesma região volta com outro `Q`.
- Densidade média: 9 (CC9), 19 (BIP42), 22 (MAPF) e 27 (CC3) não zeros por linha.
- Degenerescência: várias rodadas só mudam o fluxo. CC3 roda 29 rodadas até o fecho com ganho 0. MAPF tem duas rodadas iniciais sem ganho.
- Mais cortes não implicam mais limite: em BIP42 a ordenação por violação adicionou linhas com déficit maior e terminou com ganho menor (0,0007% contra 0,025%).

## 4. Ablação MAPF

Reproduzida exatamente (13,280000 vs 13,255072). Mesmo ponto inicial, mesmos parâmetros. Na rodada 1 a política com regiões maiores adiciona os mesmos 13 singletons mais 12 pares; a partir daí os pontos LP diferem e as famílias deixam de ser aninhadas. Com 6 rodadas nenhuma converge. Sem teto, singletons convergem em 16 rodadas e singletons+maiores em 37, ambos em **13,280000**. Não há bug: a monotonicidade vale no fecho e foi observada. As regiões maiores gastam rodadas (objetivo parado em 13,247059 nas rodadas 3–5) sem elevar o fecho.

## 5. Fecho da família declarada

| Caso | COMP+K | Fecho singletons | Fecho +12 maiores |
|---|---:|---:|---:|
| PUC CC9 | 27,026786 | +0,205% | +0,205% |
| MAPF Room | 13,200000 | +0,606% | +0,606% |
| PUCN CC3 | 16,933333 | 0% | 0% |
| PUC BIP42 | 31,706052 | +1,172% | +1,172% |

Em BIP42, 1% é cruzado na rodada 13 com 2.506 linhas e 79,1 s de laço de cortes, além de ~17 s de `K`. Vienna I056 e PUC W3C571 são censurados já em COMP e COMP+K. Logo, com 90 s e custo ≤ 2×, nenhum grafo bruto desta amostra atinge o gate AS25, e no máximo um atinge 1% sem limite de custo.

## 6. Seleção: alternativas e decisão

Ver tabela completa em `specs/as-25-1-fcr-otimizacao-separacao/design.md`. Resumo no orçamento AS25 (32/rodada, 128, 6 rodadas):

- `deficit` (ordenar por violação): +0,005 p.p. em CC9, empate em MAPF e CC3, −0,024 p.p. em BIP42. Rejeitado: sinal inconsistente.
- Singleton-primeiro (`escalate`): igual à AS25 em CC9, BIP42 e CC3; MAPF 0,417% → 0,606% (= fecho). Adotado.
- Densidade, custo de inserção e diversidade estrutural não foram usados como critério: inserção custa < 0,1 s e a densidade não separou políticas melhores. Ganho observado entre rodadas não foi usado porque a degenerescência produz rodadas de ganho zero seguidas de ganho positivo (MAPF, rodadas 1–3).

## 7. Implementação

- `experiments/cuts/fcr_lp_policy_as251.py`: `fast_region_plan` (mesmo `RegionPlan` em O(\|V\| + \|A\| log \|A\|)), fronteiras em cache, montagem de linha a partir da fronteira, `audit_rows` opcional contra `construct_row`, `larger_mode='escalate'` com status `COMPLETE_SINGLETONS_LARGER_DEFERRED`, `selection='deficit'` só para diagnóstico.
- `experiments/cuts/diagnose_fcr_as251.py`: reproduz índice, traços e fechos.
- `experiments/cuts/run_fcr_lp_as251.py` e `analyze_fcr_lp_as251.py`: campanha de 4 braços e classificação A/B/C/D.
- Nenhum arquivo AS24/AS25, COMP ou K foi alterado.

## 8. O que foi efetivamente validado

- 40 testes novos e suíte completa `experiments/cuts`: **244/244** (204 anteriores + 40). Verificador independente: 24/24 mutantes mortos, `validation.md` PASS.
- Equivalência matemática: plano igual a `choose_regions` e linhas iguais a `construct_row` na testemunha AS23 e em 40 microinstâncias aleatórias (com `S∩T`, `r=2`, saldo regional 2, circulações); `Q` igual ao ótimo por enumeração exaustiva; mesma saída de `IndexedFCR` com tetos 0, 2 e 64.
- Equivalência em instâncias reais: digests de termos e assinaturas iguais em todas as rodadas entre `as25` e `infra` em CC9, MAPF, BIP42 e CC3, com objetivo final idêntico.
- Smoke do runner (CC9, MAPF, CC3; diretório temporário, código não commitado, três diagnósticos rodando em paralelo; **não arquivado e não é campanha**): CC9 10,04 s → 3,88 s; MAPF 43,82 s → 2,79 s; CC3 de `TIME_LIMIT` para 12,68 s. Objetivos e rodadas INFRA idênticos aos AS25.

Não validado: campanha AS25.1 completa; fecho com regiões maiores de tamanho > 2; desempenho em grafos reservados.

## 9. Próximo passo

1. Commit do código e da documentação (mensagem sugerida na entrega).
2. Campanha: `poetry run python experiments/cuts/run_fcr_lp_as251.py --output-dir results/benchmark/as251-fcr-lp-001`.
3. Se a classe for B ou D, encerrar a otimização de FC-R como estratégia LP, preservando a contribuição matemática da AS23. Uma alternativa residual justificável seria limitada a BIP42 (gestão de linhas frouxas), mas não altera o gate, que exige dois grafos.
