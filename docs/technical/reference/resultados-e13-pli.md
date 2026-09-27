# Resultados E13 — primal × dual em MAPF/Vienna via ênfase do solver

**Data:** 2026-09-27
**Formulação:** baseline, variante U (`baseline.py`), dígrafo de alcance, fluxo contínuo, cortes
C1+C2+C4 (C4-DM corrigido — ver [`correcao-c4-dm.md`](correcao-c4-dm.md))
**Ambiente:** Gurobi 12.0.3, Python 3.12, seed 42, 4 threads, 2 fatias por fase (nunca 3 — satura a
máquina de 12 núcleos, ver cabeçalho de `run_e13.py`)
**Plano:** passo 1 do §7 de [`resultados-e9-e10-pli.md`](resultados-e9-e10-pli.md)
**Dados:** `results/benchmark/e13_base_fatia{1,2}.csv`, `e13_longo_fatia{1,2}.csv`
**Tabelas:** geradas por `experiments/benchmark/tabela_e13.py` a partir dos CSVs (nenhum número
copiado à mão)

Todas as 13 instâncias são D/A de MAPF e Vienna do benchmark-v1, compatíveis com o problema de Das
(classe `principal`).

## 1. Pergunta

O E10 e o E10b usaram construtores primais em Python (reverse-delete, H3, reparo do núcleo) como
instrumento para saber se o gap de MAPF/Vienna sob o COMP padrão é primal ou dual, e nenhum dos dois
respondeu — os três construtores devolvem soluções piores que o próprio incumbente do Gurobi
(resultados-e9-e10-pli.md §3.1 item 4, §4.1 item 4). Aqui o instrumento passa a ser o solver: roda o
COMP com `MIPFocus=1` (ênfase primal) e observa quanto o incumbente se move, comparado ao COMP padrão
no mesmo TL.

Braços, todos com C1+C2+C4:

- `controle` — COMP padrão, TL 600 s (referência medida com o C4-DM corrigido)
- `focus600` — `MIPFocus=1`, TL 600 s (mesmo orçamento, ênfase primal)
- `focus1800` — `MIPFocus=1`, TL 1800 s (TL triplicado, só nas que `focus600` não fechou)

Critério pré-registrado sobre Δ_UB (queda relativa do UB contra o `controle`):

- gap primal: Δ_UB ≥ 5% em ≥ 7 das 13;
- gap dual: Δ_UB < 1% em ≥ 9 das 13, **mesmo com TL triplicado**;
- qualquer outro desfecho é inconclusivo.

Os dois ramos comparam contra o incumbente do próprio solver, nunca contra o OPT, que é desconhecido
nestas 13 — são evidência para priorizar o próximo experimento, não prova.

## 2. Resultado

| Instância | Família | m | LB ctrl | UB ctrl | LB focus | UB focus | Δ_UB | UB 1800 s | Δ_UB 1800 | manifesto |
|---|---|---|---|---|---|---|---|---|---|---|
| `mapf-random-32-32-10-m50-f8` | mapf | 50 | 54 | 74 | 49 | 68 | +8,1% | 70 | +5,4% | **difere** |
| `mapf-room-32-32-4-m10-f8` | mapf | 10 | 16 | 18 | 15 | 18 | +0,0% | 18 | +0,0% | bate |
| `mapf-room-32-32-4-m25-f4-rho` | mapf | 25 | 17 | 19 | 15 | 19 | +0,0% | 19 | +0,0% | **difere** |
| `mapf-random-32-32-10-m25-f4` | mapf | 25 | 15 | 21 | 13 | 21 | +0,0% | 20 | +4,8% | **difere** |
| `mapf-empty-32-32-m25-f4` | mapf | 25 | 13 | 18 | 13 | 18 | +0,0% | 18 | +0,0% | **difere** |
| `mapf-random-64-64-20-m100-f4` | mapf | 100 | 41 | 68 | 41 | 68 | +0,0% | 63 | +7,4% | **difere** |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | mapf | 50 | 81 | 126 | 80 | 126 | +0,0% | 117 | +7,1% | bate |
| `mapf-den312d-m25-f4` | mapf | 25 | 17 | 17 | 15 | 17 | +0,0% | 17 | +0,0% | **difere** |
| `mapf-den312d-m50-f2-rho` | mapf | 50 | 4 | 9 | 4 | 9 | +0,0% | 9 | +0,0% | bate |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | mapf | 25 | 28 | 49 | 29 | 48 | +2,0% | 42 | +14,3% | **difere** |
| `vienna-I056-regiao-f4` | vienna | 25 | 9 | 12 | 9 | 11 | +8,3% | 11 | +8,3% | bate |
| `vienna-I065-intercalado-f2` | vienna | 72 | 16 | 21 | 16 | 20 | +4,8% | 19 | +9,5% | **difere** |
| `vienna-I065-regiao-f4` | vienna | 72 | 14 | 20 | 14 | 20 | +0,0% | 17 | +15,0% | **difere** |

Instâncias: 13; com Δ_UB medido: 13; com fase longo (1800 s): 13; fecharam em 600 s: 0.

## 3. Veredito

- Δ_UB ≥ 5% (queda apreciável): **7** de 13 (critério de gap primal: ≥ 7)
- Δ_UB < 1% (UB parado, mesmo com TL triplicado): **5** de 13 (critério de gap dual: ≥ 9)

**GAP PRIMAL.** O incumbente do B&B padrão estava longe do que o próprio solver alcança com ênfase
primal. O passo 3 do §7 de resultados-e9-e10 (E11, C4 mochila com δ≥2), condicionado a este passo
indicar gap dual, não é acionado.

Três leituras importantes sobre a solidez deste veredito:

1. **É um resultado de borda, não folgado.** O critério exige ≥ 7 e saiu exatamente 7. A oitava
   candidata, `mapf-random-32-32-10-m25-f4`, ficou em Δ_UB = 4,8% na fase longa — a 0,2 ponto
   percentual do limiar.
2. **A fase longa inverteu o sinal da fase base, e por isso era obrigatória.** Em 600 s (fase
   `base`), 2/13 batiam ≥ 5% e 9/13 ficavam <1% — sinalizava gap dual. Sete instâncias que tinham UB
   parado em 600 s se moveram sob 1800 s, incluindo as duas maiores quedas de todo o experimento:
   `vienna-I065-regiao-f4` (UB 20→17, +15,0%) e `mapf-warehouse-10-20-10-2-1-m25-f4` (UB 49→42,
   +14,3%). Declarar o veredito só com a fase base — como o texto gerado por `tabela_e13.py` chegou
   a fazer antes de ser corrigido nesta sessão — teria registrado a conclusão oposta à correta. É
   exatamente por isso que o critério foi pré-registrado com "mesmo com TL triplicado".
3. **UB parado em 600 s não é por si evidência de gap dual.** É o espelho da correção já feita em
   resultados-e9-e10-pli.md §4.1 item 5 (um MIP start melhor não move o LB porque age sobre o
   incumbente, não porque o gap seja dual): aqui, um UB parado em 600 s não é evidência de gap dual
   se o solver não teve tempo de explorar — é preciso o TL maior para saber se o incumbente já
   estava perto do teto do solver ou só não tinha tido chance de se mover.

Os dois ramos comparam contra o incumbente, nunca contra o OPT, que é desconhecido nestas instâncias
— é evidência para priorizar o próximo experimento, não prova.

### 3.1 Gap residual

Saída de `residual()` em `experiments/benchmark/tabela_e13.py`. LB_melhor é o maior LB dos três
braços e UB_melhor é o menor UB; a queda primal é `(UB_controle − UB_melhor)/UB_controle` e o gap
residual é `(UB_melhor − LB_melhor)/UB_melhor`.

| Instância | LB_melhor | UB_melhor | queda primal | gap residual | residual > queda |
|---|---|---|---|---|---|
| `mapf-random-32-32-10-m50-f8` | 54 | 68 | +8,1% | +20,6% | sim |
| `mapf-room-32-32-4-m10-f8` | 16 | 18 | +0,0% | +11,1% | sim |
| `mapf-room-32-32-4-m25-f4-rho` | 17 | 19 | +0,0% | +10,5% | sim |
| `mapf-random-32-32-10-m25-f4` | 15 | 20 | +4,8% | +25,0% | sim |
| `mapf-empty-32-32-m25-f4` | 13 | 18 | +0,0% | +27,8% | sim |
| `mapf-random-64-64-20-m100-f4` | 41 | 63 | +7,4% | +34,9% | sim |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | 81 | 117 | +7,1% | +30,8% | sim |
| `mapf-den312d-m25-f4` | 17 | 17 | +0,0% | +0,0% | não |
| `mapf-den312d-m50-f2-rho` | 5 | 9 | +0,0% | +44,4% | sim |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | 29 | 42 | +14,3% | +31,0% | sim |
| `vienna-I056-regiao-f4` | 9 | 11 | +8,3% | +18,2% | sim |
| `vienna-I065-intercalado-f2` | 17 | 19 | +9,5% | +10,5% | sim |
| `vienna-I065-regiao-f4` | 14 | 17 | +15,0% | +17,6% | sim |

Não resolvidas: 12; residual > queda primal: **12**.

O veredito da §3 prioriza o próximo experimento, mas não atribui o residual. Mesmo com o melhor UB
encontrado, o gap continua entre 10,5% e 44,4% e supera a queda primal nas 12 instâncias não
resolvidas (`warehouse-m50`: 81/117, 30,8% residual contra 7,1% de queda; `random-64`: 41/63, 34,9%
contra 7,4%). Sem OPT não dá para dizer se esse residual está no LB ou no UB. O E13 provou que o UB
não estava saturado. Não provou que o LB está bom.

## 4. Leitura por família

O sinal não é uniforme por família. Das 7 instâncias com Δ_UB ≥ 5%, 5 são MAPF e 2 são Vienna; das 5
com Δ_UB < 1%, 4 são MAPF e 1 é Vienna. Não há uma família que seja só primal ou só dual — a MAPF
`den312d-m25-f4` já sai do controle no ótimo provado (LB=UB=17) e a MAPF `warehouse-m25` cai 14,3%
sob ênfase primal e TL maior. A leitura correta é por instância, não por família.

## 5. Divergência com o manifesto

9 das 13 instâncias no braço `controle` divergiram do manifesto (`instances/manifest.csv`):

| Instância | LB manifesto | LB controle | UB manifesto | UB controle |
|---|---|---|---|---|
| `mapf-random-32-32-10-m50-f8` | 54 | 54 | 71 | 74 |
| `mapf-room-32-32-4-m25-f4-rho` | 16 | 17 | 19 | 19 |
| `mapf-empty-32-32-m25-f4` | 13 | 13 | 19 | 18 |
| `vienna-I065-regiao-f4` | 14 | 14 | 19 | 20 |
| `mapf-random-32-32-10-m25-f4` | 14 | 15 | 21 | 21 |
| `mapf-random-64-64-20-m100-f4` | 41 | 41 | 67 | 68 |
| `mapf-den312d-m25-f4` | 15 | 17 | 17 | 17 |
| `vienna-I065-intercalado-f2` | 16 | 16 | 20 | 21 |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | 29 | 28 | 53 | 49 |

Isto não é ruído de execução: a correção de `generate_C4_DM` (correcao-c4-dm.md) tornou a geração de
cortes determinística, e essa ordenação mudou o caminho do B&B sob time limit em quase todas as
instâncias, não só nas 2 que tiveram a família de cortes alterada em si. Uma delas mudou de classe —
`mapf-den312d-m25-f4` era A com LB 15 no manifesto e agora fecha ao ótimo provado em 17. Os números
do manifesto atual não são reproduzíveis com o código corrigido; isso reforça, sem decidir aqui, a
necessidade de regerar o benchmark-v1 com o gerador de cortes corrigido.

## 6. Consequência para a agenda

O passo 3 do §7 de resultados-e9-e10-pli.md ("E11 — C4 na versão mochila com δ≥2, só se o passo 1
indicar gap dual em MAPF/Vienna") tinha o E11 como prioridade **condicionada** a um veredito de gap
dual. O veredito saiu primal — o gatilho não ocorreu. Isto não decide o que vem a seguir; fica
registrado para quando a agenda for retomada.
