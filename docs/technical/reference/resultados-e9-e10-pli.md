# Resultados E9 e E10 — diagnóstico de raiz e primal construtivo no benchmark-v1

**Data:** 2026-09-26
**Formulação:** baseline, variante U (`baseline.py`), dígrafo de alcance, fluxo contínuo
**Ambiente:** Gurobi 12.0.3, Python 3.12, seed 42; commit `d384ceb` + alterações desta rodada
**Plano:** `docs/technical/plans/plano-pos-e8-adiado.md` (repriorização e situação após E9/E10)
**Dados:** `results/benchmark/e9_raiz_fatia{1,2,3}.csv`, `e10_primal_fatia{1,2}.csv`,
`e10b_construcao_fatia*.csv`, `e10b_comp_fatia*.csv`
**Tabelas:** geradas por `experiments/benchmark/tabela_e9_e10.py` a partir dos CSVs (nenhum número
copiado à mão)

Todas as instâncias são do benchmark-v1, compatíveis com o problema de Das (classe `principal`).

## 1. Perguntas

- **E9:** nas 30 instâncias difíceis (classes D/A do protocolo de dificuldade), quanto do limite
  vem da relaxação linear, de cada família de cortes estáticos e do IP do núcleo de cobertura?
- **E10:** um construtor primal que parte de C = ∅ (H3) supera o reverse-delete atual, que parte de
  C = V, e o UB do COMP após 600 s?
- **E10b:** reparando a solução do núcleo em vez de construir do zero, o UB cai abaixo do COMP? Isso
  diria se o gap de MAPF/Vienna é primal ou dual.

## 2. E9 — diagnóstico de raiz

`run_e9.py`: 30 D/A + 8 F de regressão (a de menor \|A_r\| de cada família com F). Configurações:
(a) z_LP; (b) +C1; (c) +C1+C2; (d) +C1+C2+C4, o controle, igual ao protocolo; (g) IP do núcleo
(C1+C2+C4, y binário, sem fluxo, TL 60 s, 4 threads); L_bot (`bounds_r6.py`). LPs com TL 300 s;
quando o LP não fecha, o bound fica vazio (nunca o ObjVal parcial). LB e UB do COMP vêm do
protocolo de dificuldade (600 s, sem start).

Fora do escopo, por decisão registrada no cabeçalho do script: (e) C3 exato e os itens de R6 além
de L_bot. O C3 precisaria de um oráculo fracionário restrito a S∪T∪supp(y\*), que não existe;
`check_C3_violations` monta a rede sobre todo A_r por origem e por rodada, e o próprio z_LP já não
fecha em 300 s em `vienna-I065-regiao-f4` (\|A_r\| = 790 mil).

| Instância | Classe | m | z_LP | +C1 | +C1+C2 | controle | núcleo LB (60 s) | L_bot | LB COMP | UB COMP |
|---|---|---|---|---|---|---|---|---|---|---|
| `mapf-maze-32-32-2-m10-f4` | F | 10 | 1,1 | 5,2 | 5,2 | 5,4 | 5 | 3 | 7 | 7 |
| `pace18-t2-001-regiao-f2` | F | 12 | 0,5 | 2,2 | 2,2 | 2,2 | 2 | 1 | 3 | 3 |
| `puc-w23c23-intercalado-f2-rho` | F | 276 | 0,9 | 123,0 | 123,0 | 123,0 | 128 | 1 | 128 | 128 |
| `pucn-cc6-2n-seed-r1` | F | 6 | 1,3 | 4,1 | 4,1 | 4,1 | 4 | 2 | 6 | 6 |
| `b-b12-intercalado-f2` | F | 19 | 0,4 | 7,0 | 7,0 | 7,0 | 7 | 1 | 7 | 7 |
| `i-i080-301-regiao-f2` | F | 10 | 0,9 | 5,0 | 5,0 | 5,0 | 5 | 1 | 5 | 5 |
| `lin-lin03-regiao-f4` | F | 4 | 2,0 | 4,5 | 5,5 | 5,5 | 5 | 3 | 7 | 7 |
| `urb-apia-m10-f8` | F | 10 | 6,5 | 8,0 | 8,0 | 8,0 | 8 | 7 | 8 | 8 |
| `mapf-den312d-m25-f4` | A | 25 | 1,0 | 10,5 | 13,2 | 13,2 | 13 | 3 | 15 | 17 |
| `mapf-den312d-m50-f2-rho` | A | 50 | 0,3 | 3,2 | 3,2 | 5,2 | 5 | 1 | 6 | 9 |
| `mapf-empty-32-32-m25-f4` | A | 25 | 1,0 | 11,2 | 11,2 | 11,3 | 11 | 3 | 13 | 19 |
| `mapf-random-32-32-10-m25-f4` | A | 25 | 1,3 | 10,8 | 11,2 | 12,6 | 13 | 3 | 14 | 21 |
| `mapf-random-32-32-10-m50-f8` | A | 50 | 2,6 | 35,8 | 42,2 | 43,2 | 43 | 6 | 54 | 71 |
| `mapf-random-64-64-20-m100-f4` | A | 100 | 1,0 | 34,3 | 35,2 | 37,6 | 39 | 3 | 41 | 67 |
| `mapf-room-32-32-4-m10-f8` | A | 10 | 2,4 | 9,2 | 13,2 | 13,2 | 13 | 6 | 16 | 18 |
| `mapf-room-32-32-4-m25-f4-rho` | A | 25 | 0,9 | 12,1 | 13,0 | 14,0 | 14 | 3 | 16 | 20 |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | A | 25 | 1,8 | 23,4 | 27,0 | 27,6 | 28 | 3 | 29 | 53 |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | A | 50 | 3,0 | 58,2 | 77,8 | 78,6 | 79 | 7 | 81 | 126 |
| `pace18-t2-141-regiao-f4` | A | 19 | 2,4 | 8,2 | 8,4 | 8,4 | 8 | 3 | 10 | 12 |
| `puc-bip42p-regiao-f2` | A | 100 | 1,0 | 31,7 | 31,7 | 31,7 | 35 (TL) | 1 | 33 | 43 |
| `puc-bip42p-seed-r1` | A | 100 | 1,0 | 31,7 | 31,7 | 31,7 | 35 (TL) | 1 | 33 | 43 |
| `puc-cc10-2u-seed-r1` | D | 67 | 1,1 | 51,0 | 51,0 | 52,0 | 52 | 2 | 53 | 58 |
| `puc-cc11-2u-seed-r1` | D | 122 | 1,0 | 92,0 | 92,0 | 92,0 | 92 | 2 | 92 | 102 |
| `puc-cc12-2u-seed-r1` | A | 236 | 0,9 | 162,5 | 162,5 | 163,5 | 164 | 2 | 165 | 200 |
| `puc-cc9-2p-seed-r1` | D | 32 | 1,2 | 27,0 | 27,0 | 27,0 | 27 | 2 | 30 | 31 |
| `puc-hc10p-seed-r1` | A | 256 | 1,0 | 51,2 | 51,2 | 51,2 | 54 (TL) | 1 | 52 | 81 |
| `puc-hc11p-seed-r1` | A | 512 | 1,0 | 93,1 | 93,1 | 93,1 | 97 (TL) | 1 | 95 | 156 |
| `puc-hc12p-seed-r1` | A | 1024 | 1,0 | 170,7 | 170,7 | 170,7 | 171 (TL) | 1 | 171 | — |
| `puc-hc9u-regiao-f4` | D | 128 | 1,5 | 28,7 | 31,2 | 31,2 | 36 | 3 | 36 | 39 |
| `puc-hc9u-seed-r1` | A | 128 | 1,0 | 28,4 | 28,4 | 28,4 | 32 | 1 | 32 | 41 |
| `puc-w23c23-seed-r1` | A | 276 | 1,1 | 132,3 | 133,3 | 133,3 | 139 (TL) | 3 | 141 | 158 |
| `puc-w3c571-seed-r1` | A | 1142 | 10,4 | 432,9 | 432,9 | 432,9 | 571 | 25 | 665 | 1139 |
| `pucn-cc3-10n-seed-r1` | A | 25 | 1,2 | 16,9 | 16,9 | 16,9 | 18 | 2 | 17 | 26 |
| `pucn-cc7-3n-regiao-f2` | A | 111 | 0,3 | 8,2 | 8,2 | 8,5 | 10 | 1 | 9 | 13 |
| `pucn-cc7-3n-seed-r1` | A | 111 | 0,8 | 65,0 | 65,0 | 65,3 | 66 | 2 | 68 | 80 |
| `vienna-I056-regiao-f4` | A | 25 | 2,4 | 8,4 | 8,5 | 8,5 | 9 | 3 | 9 | 12 |
| `vienna-I065-intercalado-f2` | A | 72 | 0,3 | 15,5 | 15,5 | 15,5 | 16 | 1 | 16 | 20 |
| `vienna-I065-regiao-f4` | A | 72 | — | 13,0 | — | 13,0 | 13 | 3 | 14 | 19 |

Por família (só D/A): mediana de controle/LB_COMP e de núcleo/LB_COMP; núcleo > LB_COMP conta as instâncias em que o núcleo supera o B&B de 600 s.

| Família | D/A | controle / LB COMP | núcleo / LB COMP | núcleo > LB COMP |
|---|---|---|---|---|
| `mapf` | 10 | 0,88 | 0,87 | 0 |
| `pace2018` | 1 | 0,84 | 0,80 | 0 |
| `puc` | 13 | 0,96 | 1,00 | 4 |
| `pucn` | 3 | 0,96 | 1,06 | 2 |
| `vienna` | 3 | 0,94 | 1,00 | 0 |

### 2.1 Leitura

1. **z_LP ≈ 1 em todas** (0,3 a 10), como prevê o Teorema 2: sem cortes, o LP enxerga só δ/m de
   cada corte. Nada de novo, mas confirmado nas famílias que nunca tinham sido medidas.
2. **C1 faz quase todo o trabalho.** C2 (bandas) soma bem em MAPF, onde o alcance é longo
   (warehouse-m50: 58,2 → 77,8; room-m10: 9,2 → 13,2); em PUC as bandas coincidem com C1. C4-DM
   soma pouco em todas.
3. **L_bot é dominado pela raiz com cortes em todas as instâncias** (1 a 25, contra 2,2 a 433 no controle). Os
   demais itens de R6 (bandas por atribuição, empacotamento) não valem implementação.
4. **Em PUC/PUCN o núcleo inteiro pesa, e supera o B&B do compacto.** Em 6 instâncias o IP do
   núcleo (60 s) dá LB maior que o COMP após 600 s: bip42p-regiao e bip42p-seed (35 vs. 33),
   hc10p (54 vs. 52), hc11p (97 vs. 95), pucn-cc3-10n (18 vs. 17), pucn-cc7-3n-regiao (10 vs. 9);
   empata em hc9u-seed e hc12p. Em w3c571 o núcleo sobe de 433 (raiz) para 571, mas o COMP chega a
   665 — ali o acoplamento de fluxo pesa mesmo em PUC.
   **Margem estreita, e o valor do núcleo não é reprodutível bit a bit** (§6, último item): as
   margens são de 1 a 2 estações. Só `pucn-cc3-10n` foi verificada estável (18 em 6 execuções
   independentes); as quatro de `puc` pararam por TL, onde o bound já depende do caminho do B&B.
   A leitura qualitativa — o núcleo é competitivo em PUC/PUCN e não em MAPF/Vienna — se sustenta;
   os valores individuais carregam ±1.
5. **Em MAPF e Vienna é o contrário:** o núcleo fica no nível da raiz com cortes e abaixo do LB do
   COMP (MAPF: mediana 0,87 do LB do COMP; nenhuma instância acima). O B&B do compacto acrescenta
   algo que o núcleo de cobertura não tem.
6. **Nas F de regressão o núcleo fica abaixo do ótimo** em 4 de 8 (maze 5 vs. 7, pace-001 2 vs. 3,
   pucn-cc6-2n 4 vs. 6, lin03 5 vs. 7): a solução do núcleo é inviável no problema real, como já
   visto em hc9u no E3.

## 3. E10 — primal construtivo

`run_e10.py`: nas 30 D/A, reverse-delete com busca local (`build_primal_solution`, o start do E8)
contra H3 + busca local (`build_primal_h3`), mesmo orçamento de 60 s e mesma seed. Rodou em paralelo
ao E9, com a CPU disputada.

| Instância | n | m | reverse-delete | H3 | UB COMP |
|---|---|---|---|---|---|
| `puc-cc9-2p-seed-r1` | 512 | 32 | 59 | 101 | 31 |
| `puc-hc9u-seed-r1` | 512 | 128 | 254 | 84 | 41 |
| `puc-hc9u-regiao-f4` | 512 | 128 | 243 | — (não terminou) | 39 |
| `puc-w23c23-seed-r1` | 1081 | 276 | 1039 | — (não terminou) | 158 |
| `pace18-t2-141-regiao-f4` | 294 | 19 | 21 | 22 | 12 |
| `puc-bip42p-seed-r1` | 1200 | 100 | 1086 | 92 | 43 |
| `puc-bip42p-regiao-f2` | 1200 | 100 | 1064 | 82 | 43 |
| `mapf-random-32-32-10-m50-f8` | 922 | 50 | 622 | — (não terminou) | 71 |
| `puc-cc10-2u-seed-r1` | 1024 | 67 | 886 | — (não terminou) | 58 |
| `puc-hc10p-seed-r1` | 1024 | 256 | 1003 | — (não terminou) | 81 |
| `mapf-room-32-32-4-m10-f8` | 682 | 10 | 29 | — (não terminou) | 18 |
| `mapf-room-32-32-4-m25-f4-rho` | 682 | 25 | 400 | — (não terminou) | 20 |
| `puc-w3c571-seed-r1` | 3997 | 1142 | 3995 | — (não terminou) | 1139 |
| `puc-cc11-2u-seed-r1` | 2048 | 122 | 2028 | — (não terminou) | 102 |
| `puc-hc11p-seed-r1` | 2048 | 512 | 2043 | — (não terminou) | 156 |
| `pucn-cc3-10n-seed-r1` | 1000 | 25 | 914 | 70 | 26 |
| `mapf-random-32-32-10-m25-f4` | 922 | 25 | 751 | — (não terminou) | 21 |
| `pucn-cc7-3n-seed-r1` | 2187 | 111 | 2163 | — (não terminou) | 80 |
| `mapf-empty-32-32-m25-f4` | 1024 | 25 | 902 | — (não terminou) | 19 |
| `puc-cc12-2u-seed-r1` | 4096 | 236 | 4091 | — (não terminou) | 200 |
| `puc-hc12p-seed-r1` | 4096 | 1024 | 4095 | — (não terminou) | — |
| `mapf-random-64-64-20-m100-f4` | 3270 | 100 | 3259 | — (não terminou) | 67 |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | 5699 | 50 | 5686 | — (não terminou) | 126 |
| `pucn-cc7-3n-regiao-f2` | 2187 | 111 | 2183 | — (não terminou) | 13 |
| `mapf-den312d-m25-f4` | 2445 | 25 | 2429 | — (não terminou) | 17 |
| `vienna-I056-regiao-f4` | 1991 | 25 | 1985 | — (não terminou) | 12 |
| `vienna-I065-intercalado-f2` | 3898 | 72 | 3893 | — (não terminou) | 20 |
| `mapf-den312d-m50-f2-rho` | 2445 | 50 | 2438 | — (não terminou) | 9 |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | 5699 | 25 | 5693 | — (não terminou) | 53 |
| `vienna-I065-regiao-f4` | 3898 | 72 | 3897 | — (não terminou) | 19 |

H3 terminou em 6/30; entre essas, venceu o reverse-delete em 4. Reverse-delete devolveu ≥ 90% de V em 19/30.

### 3.1 Leitura

1. **O reverse-delete não escala.** Partindo de C = V, gasta o orçamento em poucas remoções: devolveu
   ≥ 90% de V em 19 das 30 (warehouse-m50: 5686 de 5699 vértices).
2. **O H3 medido tinha um defeito de implementação.** O desempate escolhia primeiro o vértice que
   aparecia em mais cortes já vistos. Medido depois, isoladamente: isso gera C 2–2,5× maior e leva
   4–10× mais tempo do que escolher só pelo grau de saída em A_r (mapf-room-m10: 574 estações em
   10,5 s contra 233 em 1,0 s; hc9u-regiao: 363 em 38 s contra 190 em 9,8 s). Somado à disputa de
   CPU com o E9, explica boa parte dos 24 casos em que a construção não terminou em 20 s. O desempate
   foi corrigido em `primal.greedy_augment`.
3. **Quando o H3 terminou, venceu o reverse-delete em 4 de 6** (hc9u 84 vs. 254, bip42p 92 e 82
   vs. ~1070, pucn-cc3-10n 70 vs. 914), mas nenhum dos dois chegou ao UB do COMP em nenhuma instância.
4. **O critério pré-registrado não se aplica.** Ele dizia "se o H3 perder, registra-se que o
   gargalo é dual". A inferência era inválida: os construtores falharam por escala e por
   implementação, não por falta de gap primal — o próprio UB do COMP está longe do LB (warehouse-m50:
   81 vs. 126). **O E10 não responde se o gap é primal ou dual.**

## 4. E10b — primal por reparo do núcleo

`run_e10b.py`, fase `construcao`, nas 30 D/A: núcleo (TL 60 s) → reparo guloso a partir da solução
do núcleo (`greedy_augment` com o desempate corrigido) → poda (reverse-delete só sobre C) → busca
local, até 120 s (`primal.build_primal_from_core`). Toda solução final foi checada viável por
`integer_oracle`. Validado nos 10 gabaritos de `synthetic.py` por
`experiments/cuts/verify_e10b_primal.py` (código 0): solução viável e igual ao OPT em todos — no
Sec59 a solução do núcleo é inviável (2, sem acoplamento de fluxo) e o reparo a corrige
(2 → reparo 8 → poda 7 = OPT). Fase `comp`: COMP 600 s com a solução como MIP start, só onde o
reparo venceu o UB do COMP.

| Instância | Regime | núcleo \|C\| | reparo | poda | final | LB COMP | UB COMP | LB c/ start | UB c/ start |
|---|---|---|---|---|---|---|---|---|---|
| `puc-cc9-2p-seed-r1` | R-a | 27 | 78 | 43 | 43 | 30 | 31 | — | — |
| `puc-hc9u-regiao-f4` | R-b | 36 | 84 | 66 | 66 | 36 | 39 | — | — |
| `puc-hc9u-seed-r1` | R-b | 32 | 60 | 52 | 52 | 32 | 41 | — | — |
| `puc-w23c23-seed-r1` | R-b | 139 | 161 | 157 | 157 | 141 | 158 | 141 | **156** |
| `pace18-t2-141-regiao-f4` | R-a | 8 | 27 | 15 | 13 | 10 | 12 | — | — |
| `puc-bip42p-seed-r1` | R-b | 37 | 128 | 59 | 59 | 33 | 43 | — | — |
| `puc-bip42p-regiao-f2` | R-b | 37 | 154 | 56 | 56 | 33 | 43 | — | — |
| `mapf-random-32-32-10-m50-f8` | R-a | 43 | 431 | 99 | 99 | 54 | 71 | — | — |
| `puc-hc10p-seed-r1` | R-b | 67 | 166 | 98 | 98 | 52 | 81 | — | — |
| `puc-cc10-2u-seed-r1` | R-a | 52 | 178 | 88 | 88 | 53 | 58 | — | — |
| `mapf-room-32-32-4-m10-f8` | R-a | 13 | 170 | 29 | 26 | 16 | 18 | — | — |
| `mapf-room-32-32-4-m25-f4-rho` | R-a | 14 | 267 | 30 | 27 | 16 | 20 | — | — |
| `puc-w3c571-seed-r1` | R-b | 571 | — | — | — | 665 | 1139 | — | — |
| `puc-cc11-2u-seed-r1` | R-a | 92 | 370 | 175 | 175 | 92 | 102 | — | — |
| `puc-hc11p-seed-r1` | R-b | 146 | — | — | — | 95 | 156 | — | — |
| `pucn-cc3-10n-seed-r1` | R-a | 18 | 79 | 40 | 34 | 17 | 26 | — | — |
| `mapf-random-32-32-10-m25-f4` | R-a | 12 | 339 | 27 | 26 | 14 | 21 | — | — |
| `pucn-cc7-3n-seed-r1` | R-a | 66 | 400 | 141 | 141 | 68 | 80 | — | — |
| `mapf-empty-32-32-m25-f4` | R-a | 11 | 527 | 36 | 33 | 13 | 19 | — | — |
| `puc-cc12-2u-seed-r1` | R-a | 164 | — | — | — | 165 | 200 | — | — |
| `puc-hc12p-seed-r1` | R-b | 512 | — | — | — | 171 | — | — | — |
| `mapf-random-64-64-20-m100-f4` | R-a | 39 | — | — | — | 41 | 67 | — | — |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | R-a | 79 | — | — | — | 81 | 126 | — | — |
| `pucn-cc7-3n-regiao-f2` | misto | 10 | 38 | 24 | 24 | 9 | 13 | — | — |
| `mapf-den312d-m25-f4` | R-a | 13 | — | — | — | 15 | 17 | — | — |
| `vienna-I056-regiao-f4` | R-a | 9 | 197 | 15 | 14 | 9 | 12 | — | — |
| `vienna-I065-intercalado-f2` | misto | 16 | 528 | 446 | 446 | 16 | 20 | — | — |
| `mapf-den312d-m50-f2-rho` | misto | 6 | — | — | — | 6 | 9 | — | — |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | R-a | 28 | — | — | — | 29 | 53 | — | — |
| `vienna-I065-regiao-f4` | R-a | 13 | 59 | 20 | 19 | 14 | 19 | — | — |

Reparo < UB COMP (MAPF+Vienna): 0/13. Reparo < UB COMP (todas): 1/30.

> **Atenção à coluna `núcleo |C|`:** aqui ela é a *cardinalidade da solução incumbente* do IP do
> núcleo (`nucleo_obj`) — o C que serve de semente ao reparo. Na tabela do §2 a coluna homônima é o
> *dual bound* (`ip_nucleo_bound`). Nas instâncias em que o núcleo não fechou em 60 s as duas
> divergem, às vezes muito: hc12p 512 (|C|) contra 171 (LB), hc11p 146 contra 97, hc10p 67 contra
> 54. Só o LB é limite inferior do OPT; o |C| é limite superior e nem é bom.

### 4.1 Leitura

1. **O reparo não alcança o incumbente do Gurobi.** Venceu o UB do COMP em 1 de 30 (w23c23-seed,
   157 vs. 158 — margem de 1 estação, 0,6%) e em **0 de 13 nas MAPF/Vienna**. Nas 21 em que chegou
   à viabilidade no prazo, a solução final ficou, em mediana, 1,37× o UB do COMP, com cauda longa
   (máximo 22,3×, em vienna-I065-intercalado: 446 vs. 20).
2. **O reparo sobre-adiciona.** Cada passo resolve só o corte testemunha da vez; em mediana o C
   reparado tem 4,2× o tamanho do núcleo (mapf-empty-m25: 11 → 527), e a poda devolve boa parte,
   mas não tudo, dentro do prazo (vienna-I065-intercalado: 528 → 446).
3. **Em 9 das 30 não chegou à viabilidade em 120 s**, e não é o tamanho do dígrafo por si:
   vienna-I065-regiao (790 mil arcos, o maior do conjunto) terminou, enquanto den312d-m50
   (550 mil) não. As 9 se dividem em dois grupos, coerentes com o custo de cada etapa:
   (a) **núcleo grande** — w3c571 (571), hc12p (512), cc12-2u (164), hc11p (146): a poda testa
   remover cada vértice de C, uma chamada ao oráculo por vértice; (b) **MAPF grandes** —
   warehouse-m25/m50, den312d-m25/m50, random-64: o reparo sobre-adiciona centenas de vértices
   (item 2) antes de atingir viabilidade, cada passo sobre um dígrafo de 10⁵–10⁶ arcos.
4. **Nenhum dos dois desfechos pré-registrados ocorreu.** O critério previa "reparo < UB do COMP
   em ≥ 50% das MAPF/Vienna ⇒ gargalo primal" ou "reparo ≈ UB do COMP e LB parado ⇒ gap dual".
   Ambos os ramos foram pré-registrados **sobre o conjunto MAPF/Vienna**, onde o reparo ficou bem
   *acima* do UB do COMP em 13 de 13; a única vitória está fora desse conjunto (w23c23-seed, PUC) e
   não aciona nem um ramo nem o outro. Ficar acima do UB do COMP não informa sobre o gap: mostra só
   que heurísticas construtivas com o oráculo em Python são um instrumento pior do que o próprio
   B&B para achar soluções. **A pergunta primal × dual continua sem resposta**, e precisa de outro
   instrumento (o solver com ênfase primal ou TL maior, ou as soluções viáveis que o CBI produz ao
   iterar).
5. **Fase `comp` (w23c23-seed, única instância qualificada):** COMP 600 s com start de 157
   estações. UB melhorou de 158 → **156**; LB ficou em 141, idêntico ao de sem start. Gap residual
   9,6% (era 10,8%); status TIME_LIMIT nas duas execuções.
   **Isto não decide primal × dual, nem nessa instância.** Um MIP start age sobre o incumbente; o
   LB vem da relaxação, dos cortes e do branching, e só se beneficia do start de forma indireta
   (poda por bound). LB imóvel sob um start melhor é o comportamento esperado de qualquer MIP
   start, não evidência de que o gap seja dual — a mesma inferência que o item 4 do §3.1 rejeita.
   O que se registra é mais estreito: em 600 s o B&B sobe o LB de 133,3 (raiz com cortes) a 141 e
   estaciona aí, **com ou sem** um incumbente a 2 estações do melhor conhecido.

## 5. Correções a leituras anteriores

| O que foi dito | Correção | Fonte |
|---|---|---|
| "IP do núcleo = teto do LB do CBI"; rodar o E12 só onde OPT(núcleo) ≥ LB do COMP, "nas demais o CBI não pode vencer por construção" | O núcleo é o LB da **primeira** iteração do CBI; `solve_cbi` acrescenta cortes 𝒵 válidos e o LB só sobe. O filtro vira prioridade, não exclusão | plano de execução do E9; `bc_yspace.solve_cbi` |
| "O núcleo IP quase não acrescenta sobre o controle na maioria das famílias" | Falso em PUC/PUCN, onde o núcleo supera até o LB do COMP de 600 s em 6 instâncias (§2.1, item 4) | resumo do E9 na conversa |
| "O controle fecha 60–100% do gap" | Fração calculada contra o UB do protocolo, que é folgado: é um limite inferior da fração real | resumo do E9 na conversa |
| "Reverse-delete devolve praticamente V inteiro em 26/30" | ≥ 90% de V em 19/30 | plano de E9/E10 |
| E10: "se o H3 perder, o gargalo é dual" | Inferência inválida (§3.1, item 4) | critério pré-registrado |

## 6. Em aberto

- Se o gap de MAPF/Vienna é primal ou dual. Nem o E10 nem o E10b responderam: os três construtores
  (reverse-delete, H3, reparo do núcleo) devolvem soluções *piores* que o incumbente do Gurobi —
  acima do UB do COMP em 13 de 13 das MAPF/Vienna e em 29 de 30 no conjunto D/A.
- C3 não foi medido no benchmark-v1; exige oráculo fracionário restrito.
- `vienna-I065-regiao-f4`: z_LP e +C1+C2 sem valor (LP não fechou em 300 s); +C1 e o controle fecharam.
- Uma seed em tudo. Os LPs são determinísticos; o núcleo com TL e os construtores com prazo não.
- **`generate_C4_DM` não é determinística entre processos** — achado desta revisão, não previsto no
  plano. Ela percorre `S_only`/`T_only`, que são `set`s de rótulos, e passa essa ordem a
  `_max_matching` ([cuts.py:191–197](../../../experiments/cuts/cuts.py#L191-L197)). Emparelhamentos
  máximos não são únicos: mudando a ordem, mudam as origens não emparelhadas, as regiões
  alternantes e, portanto, a família C4 gerada. Verificado variando `PYTHONHASHSEED` no mesmo
  código e na mesma instância: `den312d-m50` gera 16, 16 ou 15 cortes distintos; o ótimo do núcleo
  sai 5 ou 6 (foi 5 no E9 e 6 no E10b — mesma instância, ótimo *provado* nos dois, sem contradição
  matemática porque os modelos diferem). Em `random-32-32-10-m25` sai 12 em 2 de 6 execuções e 13
  nas outras 4.
  O efeito é sobre reprodutibilidade: a tabela do §2 e a do §4 carregam ±1 nas linhas resolvidas ao
  ótimo, e uma reexecução não reproduz os CSVs bit a bit. Afeta todo resultado que usa C1+C2+C4 — o
  controle do protocolo de dificuldade e o COMP incluídos.
- **`generate_C4_DM` também gera cortes inválidos** quando `S∩T ≠ ∅` — achado posterior, na mesma
  revisão. Uma primeira leitura aqui concluiu "não é defeito de validade, `is_valid_cut` aprova
  100%"; **essa conclusão estava errada**, por uma chamada com os argumentos fora de ordem
  (`is_valid_cut(S, T, A_r, Z, …)`, com `Z` em quarto lugar). Refeita a chamada, o validador reprova
  cortes em 3 das 5 instâncias principais com `S∩T ≠ ∅`, e `integer_oracle` confirma cada caso
  exibindo solução viável em `V∖Z`. A causa era divergência entre implementação e teoria: o §5.4 de
  `direcoes-pli-min-station.md` mede a deficiência contra `T` inteiro, e o código usava `T∖S`.
  **Corrigido em 2026-09-26**, junto com o não-determinismo, e coberto por regressão nova
  (`verify_c4_dm.py`) — ver [`correcao-c4-dm.md`](correcao-c4-dm.md).

  **Efeito sobre este relatório.** Todos os números acima foram medidos antes da correção. Das
  instâncias das tabelas, só duas têm `S∩T ≠ ∅` — `mapf-den312d-m50-f2-rho` e
  `mapf-room-32-32-4-m25-f4-rho` — e a reavaliação corrigiu as referências de COMP usadas nas
  colunas "LB COMP"/"UB COMP": den312d-m50 passa de LB 6 para **LB 4**, e room-m25-rho de UB 20
  para **UB 19**. Nenhuma conclusão do relatório depende dessas duas linhas: as leituras por família
  são medianas sobre 10 MAPF, e as afirmações sobre PUC/PUCN vêm de instâncias com `S∩T = ∅`. As
  demais linhas não tinham cortes inválidos, mas carregam ±1 pelo não-determinismo, como já
  registrado acima.

## 7. Próximos passos propostos (não executados)

0. ~~**Corrigir `generate_C4_DM`**~~ — **feito em 2026-09-26**, ver
   [`correcao-c4-dm.md`](correcao-c4-dm.md). Era pré-requisito de tudo abaixo: cortes inválidos
   comprometem a validade dos LBs e o não-determinismo põe ±1 de ruído num E12 que decide por
   margens de 1–2 estações. Os passos seguintes já podem rodar sobre o gerador corrigido.
1. **Primal × dual com o solver como instrumento.** COMP com `MIPFocus=1` (ênfase primal), 600 s e
   depois 1800 s, nas 13 D/A de MAPF/Vienna. Se o UB cair de forma apreciável com o LB parado, é
   evidência de que parte do gap era primal; se o UB mal se mover sob ênfase primal e TL triplicado,
   é evidência de gap dual. Nenhum dos ramos é conclusivo isoladamente — ambos comparam contra o
   incumbente, não contra o OPT. Custo: ~2–6 h de máquina, sem código novo além de um parâmetro.
   Substitui o E10b como resposta a essa pergunta.
2. **E12 — CBI × COMP no subconjunto PUC/PUCN**, onde o núcleo já sai na frente, depois de corrigir
   o mestre do CBI (sem pool até o ótimo). As iterações do CBI também produzem soluções viáveis, o
   que serve de segundo instrumento primal. Critério pré-registrado em `plano-pos-e8-adiado.md`.
3. **E11 — C4 na versão mochila com δ ≥ 2**, só se o passo 1 indicar gap dual em MAPF/Vienna. Antes,
   fixar a família por escrito e validar por enumeração exaustiva nos gabaritos.
4. **Aposentar os construtores em Python como start padrão.** Para as próximas comparações, o start
   comum (quando houver) deve vir de uma execução curta do próprio solver, não de `primal.py`.
