# F3 — LP da F-CC em instâncias pequenas

**Data:** 2026-10-06
**Pré-registro:** `experiments/alternative-formulations/pre-registro-f3.md` (escrito antes desta medição)
**CSV:** `results/alternative-formulations/f3-fcc.csv`
**Solver:** Gurobi 12, `Seed=42`, `Threads=1`, `Method=2` no LP da F-CC
**Forma:** F-CC separada (`λ_W,α,β`), P7 `PROVEN`. F-C3 não medida (`OPEN`).

## Resultado

A F-C3 não entra. A F-CC foi medida na forma separada por enumeração de `W` conexos em `H`, com caps `n_max=21` e `max_W=200000`.

P2: em toda linha `ok`, `lp_fcc >= lp_base` (tolerância `1e-6`). P1/P7: `verify_fcc.py` passou.

## Tabela (valores do CSV)

| Instância | tipo | n | LP base | LP+C1+C2+C4 | núcleo | LP F-CC | OPT | fonte | Γ |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| Direct0 | gadget | 4 | 0 | 0 | 0 | 0 | 0 | enum | 0 |
| TermRelay | gadget | 4 | 1 | 1 | 1 | 1 | 1 | enum | 0 |
| TermRelayForced | gadget | 5 | 1 | 1 | 1 | 1 | 1 | enum | 0 |
| StayPut | gadget | 2 | 0 | 0 | 0 | 0 | 0 | enum | 0 |
| StayPutIsolado | gadget | 1 | 0 | 0 | 0 | 0 | 0 | enum | 0 |
| SharedTerminal | gadget | 5 | 0,5 | 1 | 1 | 0,5 | 1 | enum | 0 |
| CaminhoABC | gadget | 3 | 0 | 0 | 0 | 0 | 0 | enum | 0 |
| Tri | tri | 9 | 1 | 1,5 | 2 | 1,5 | 2 | enum | 0 |
| F1(m=2,k=2) | f1 | 13 | 5 | 9 | 9 | 9 | 9 | enum | 0 |
| F2(k=1,L=3) | f2 | 7 | 1/3 | 1 | 1 | 1 | 1 | enum | 0 |
| Sec59(L=7) | sec59 | 13 | 7/3 | 11/3 | 2 | 4,5 | 7 | enum | 5 |
| HB-q4-ndir2-p1 | hb | 16 | 1/3 | 1 | 1 | 2 | 2 | enum | 1 |
| HB-q5-ndir2-p1 | hb | 21 | 0,375 | 1,083 | 1 | 3 | 3 | mip_base | 2 |
| BP-nao-[3,1]-q2 | bp-nao | 16 | 3 | 6 | 6 | 7 | 7 | enum | 1 |
| TR-k2-L5-r2 | tr | 18 | 3 | 3 | 3 | 3 | 3 | mip_base | 0 |
| SC-GF2-k3 | sc-gf2 | 21 | 1 | 1,75 | 3 | — | 3 | mip_base | 0 |

O núcleo é o IP só em `y` com C1+C2+C4-DM. Em Sec59 esse IP vale 2, abaixo do LP com fluxo+cortes (11/3): o núcleo não contém o fluxo, portanto pode ficar abaixo do LP da base cortada. Isso não é inconsistência do CSV. `Γ = OPT − núcleo` segue a definição pré-registrada.

## Tipos com Γ > 0 (medido)

| Tipo | Instâncias | max(LP cortes, núcleo) | LP F-CC | Γ | fracção de Γ fechada |
|---|---|---:|---:|---:|---:|
| hb | q=4 | 1 | 2 | 1 | 100% |
| hb | q=5 | 1,083 | 3 | 2 | 95,8% |
| bp-nao | [3,1] | 6 | 7 | 1 | 100% |
| sec59 | L=7 | 3,667 | 4,5 | 5 | 16,7% |

A análise de planejamento previa **ausência** de ganho em BP-"não". A medição mostra ganho de 1 estação no LP, até o OPT. Isso é facto computacional neste caso; não vira teorema.

## Controle negativo SC-GF2(k=3)

`|W|` enumerado atingiu `max_W+1`. F-CC **não** foi resolvida. LP set-cover = 1,75 = LP base+C1+C2+C4. Núcleo = OPT = 3, `Γ=0`. Sem valor F-CC, não há ganho em SC a investigar.

P9 permanece `HYPOTHESIS` (igualdade F-CC = LP set-cover não medida neste k).

## Alegações P11

Famílias 20/15 vértices e `1,5g`/`2g`: não reconstruídas. Sem comparação.

## Exclusões

Além de SC-GF2-k3 (`max_W`), o pré-registro já listava instâncias com `n>21` e as famílias F-C3/aranhas sem definição.

## O que estes números não dizem

Força de relaxação, não tempo nem nós. SharedTerminal tem F-CC = LP base (0,5) abaixo de C1+C2+C4 (1): a F-CC **não** domina os cortes estáticos em todo o conjunto, só é comparada ao `max` na regra GF1.
