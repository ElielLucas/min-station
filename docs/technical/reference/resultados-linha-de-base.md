# Resultados da linha de base — Spec A R4

**Data:** 2026-10-06
**Contrato:** `docs/technical/reference/linha-de-base-pre-registro.md`, congelado em 2026-10-04T15:08:42-03:00, antes da primeira linha do CSV.
**Dados:** `results/benchmark/linha_base.csv`
**Tabela:** saída de `experiments/benchmark/tabela_linha_base.py`. Nenhum número desta tabela foi copiado à mão.
**Commit gravado em toda linha:** `9b93650-dirty` (capturado no início de `medir`; a execução continuou depois dos commits de R1–R3).
**Orçamento:** `WorkLimit = 164`, `TimeLimit = 1800` só como guarda, 4 threads, sem MIP start.
**Partição:** `regra-particao-origem.md`. Estado congelado, sem tag `benchmark-v1.0`.

## 1. Checagem

- 411 linhas, igual ao desenho (75 `principal`; 3 braços; 3 sementes nas D/A; 1 semente nas F/M e nas 5 legado sem classe).
- Toda linha tem `sha256` e `commit`.
- `guarda_parede = 0` em todas. O `TimeLimit` não disparou.
- Status 2 (ótimo) em 187 linhas. Status 16 (`WorkLimit`) em 224.

`LB*` é o maior `mip_bound` entre base, COMP e núcleo, passado a inteiro por `ceil(x − 10⁻⁶)`, a mesma convenção do E12. O objetivo é inteiro, então esse teto é um limite inferior válido.

`UB*` é o menor `mip_obj` só da base e do COMP. O objetivo do núcleo é o ótimo do IP de cobertura. Ele pode ficar abaixo do LB do COMP (`puc-cc9-2p-seed-r1`: núcleo 27, COMP 30) e não é incumbente do MIN-STATION. Nenhuma instância ficou sem incumbente na base ou no COMP, então `UB*` não ficou ausente.

## 2. LB* e UB* por instância

Fonte: `results/benchmark/linha_base.csv`. Contrato: `docs/technical/reference/linha-de-base-pre-registro.md`.
Linhas: 411 (desenho 411).

| Instância | Dificuldade | Partição | Fora AV | LB* | fonte LB* | UB* | fonte UB* | guarda |
|---|---|---|---|---:|---|---:|---|---|
| b-b06-intercalado-f2.txt | F | desenvolvimento |  | 1 | nucleo seed 42 | 1 | base seed 42 |  |
| b-b06-regiao-f2.txt | F | desenvolvimento |  | 3 | nucleo seed 42 | 3 | base seed 42 |  |
| b-b09-intercalado-f2-rho.txt | F | avaliacao |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| b-b12-intercalado-f2.txt | F | desenvolvimento |  | 7 | nucleo seed 42 | 7 | base seed 42 |  |
| b-b12-regiao-f2.txt | F | desenvolvimento |  | 3 | nucleo seed 42 | 3 | base seed 42 |  |
| b-b15-regiao-f4.txt | F | avaliacao |  | 9 | comp seed 42 | 9 | base seed 42 |  |
| b-b18-intercalado-f2.txt | F | desenvolvimento |  | 1 | nucleo seed 42 | 1 | base seed 42 |  |
| b-b18-regiao-f2.txt | F | desenvolvimento |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| bip42p.txt |  | legado |  | 35 | nucleo seed 42 | 43 | comp seed 42 |  |
| hc10p.txt |  | legado |  | 56 | nucleo seed 42 | 77 | comp seed 42 |  |
| hc11p.txt |  | legado |  | 97 | nucleo seed 42 | 161 | comp seed 42 |  |
| hc12p.txt |  | legado | sim | 171 | nucleo seed 42 | 376 | base seed 42 |  |
| hc9u.txt |  | legado |  | 32 | comp seed 42 | 41 | comp seed 42 |  |
| i-i080-001-regiao-f2.txt | F | avaliacao |  | 1 | nucleo seed 42 | 1 | base seed 42 |  |
| i-i080-041-regiao-f2.txt | F | avaliacao |  | 1 | nucleo seed 42 | 1 | base seed 42 |  |
| i-i080-301-regiao-f2.txt | F | avaliacao |  | 5 | nucleo seed 42 | 5 | base seed 42 |  |
| i-i080-341-intercalado-f2.txt | F | avaliacao |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| i-i160-301-intercalado-f2-rho.txt | F | avaliacao |  | 5 | nucleo seed 42 | 5 | base seed 42 |  |
| i-i160-301-regiao-f2.txt | F | avaliacao |  | 4 | nucleo seed 42 | 4 | base seed 42 |  |
| lin-lin01-regiao-f2.txt | F | avaliacao |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| lin-lin03-regiao-f4.txt | F | avaliacao |  | 7 | comp seed 42 | 7 | base seed 42 |  |
| lin-lin06-intercalado-f2.txt | F | desenvolvimento |  | 3 | nucleo seed 42 | 3 | base seed 42 |  |
| lin-lin06-regiao-f4.txt | F | desenvolvimento |  | 7 | comp seed 42 | 7 | base seed 42 |  |
| mapf-den312d-m25-f4.txt | A | avaliacao |  | 15 | comp seed 44 | 17 | base seed 42 |  |
| mapf-den312d-m50-f2-rho.txt | A | avaliacao |  | 4 | comp seed 44 | 9 | base seed 42 |  |
| mapf-empty-32-32-m25-f4.txt | A | avaliacao |  | 13 | comp seed 44 | 18 | base seed 42 |  |
| mapf-empty-32-32-m50-f2.txt | A | avaliacao |  | 5 | comp seed 44 | 6 | base seed 42 |  |
| mapf-maze-32-32-2-m10-f4.txt | F | avaliacao |  | 7 | comp seed 42 | 7 | base seed 42 |  |
| mapf-maze-32-32-2-m25-f2.txt | F | avaliacao |  | 5 | comp seed 42 | 5 | base seed 42 |  |
| mapf-random-32-32-10-m25-f4.txt | A | avaliacao |  | 15 | comp seed 42 | 21 | base seed 42 |  |
| mapf-random-32-32-10-m50-f8.txt | A | avaliacao |  | 53 | comp seed 44 | 71 | base seed 42 |  |
| mapf-random-64-64-20-m100-f4.txt | A | avaliacao |  | 41 | comp seed 44 | 66 | comp seed 42 |  |
| mapf-room-32-32-4-m10-f8.txt | A | desenvolvimento |  | 16 | comp seed 43 | 18 | base seed 42 |  |
| mapf-room-32-32-4-m25-f4-rho.txt | A | avaliacao |  | 17 | comp seed 43 | 19 | base seed 43 |  |
| mapf-warehouse-10-20-10-2-1-m25-f4.txt | A | avaliacao |  | 29 | comp seed 44 | 37 | base seed 44 |  |
| mapf-warehouse-10-20-10-2-1-m50-f8.txt | A | avaliacao |  | 81 | comp seed 43 | 121 | base seed 43 |  |
| pace18-t2-001-regiao-f2.txt | F | avaliacao |  | 3 | comp seed 42 | 3 | base seed 42 |  |
| pace18-t2-061-regiao-f4.txt | F | desenvolvimento |  | 7 | comp seed 42 | 7 | base seed 42 |  |
| pace18-t2-081-regiao-f2.txt | F | avaliacao |  | 3 | comp seed 42 | 3 | base seed 42 |  |
| pace18-t2-141-regiao-f4.txt | A | desenvolvimento |  | 10 | comp seed 44 | 12 | base seed 42 |  |
| pace18-t2-181-regiao-f2.txt | F | avaliacao |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| pace18-t2-199-regiao-f4.txt | M | desenvolvimento |  | 7 | comp seed 42 | 7 | base seed 42 |  |
| puc-bip42p-regiao-f2.txt | A | desenvolvimento |  | 35 | nucleo seed 44 | 43 | comp seed 42 |  |
| puc-bip42p-seed-r1.txt | A | desenvolvimento |  | 35 | nucleo seed 44 | 43 | comp seed 42 |  |
| puc-cc10-2u-regiao-f2.txt | F | desenvolvimento |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| puc-cc10-2u-seed-r1.txt | A | desenvolvimento |  | 53 | comp seed 44 | 57 | comp seed 44 |  |
| puc-cc11-2u-seed-r1.txt | D | desenvolvimento |  | 92 | base seed 44 | 101 | comp seed 43 |  |
| puc-cc12-2u-seed-r1.txt | A | desenvolvimento |  | 165 | comp seed 44 | 193 | base seed 43 |  |
| puc-cc6-3p-seed-r1.txt | F | desenvolvimento |  | 32 | comp seed 42 | 32 | base seed 42 |  |
| puc-cc9-2p-seed-r1.txt | D | desenvolvimento |  | 30 | comp seed 44 | 31 | base seed 42 |  |
| puc-hc10p-regiao-f4.txt | F | avaliacao |  | 6 | nucleo seed 42 | 6 | comp seed 42 |  |
| puc-hc10p-seed-r1.txt | A | avaliacao |  | 56 | nucleo seed 42 | 79 | comp seed 42 |  |
| puc-hc11p-seed-r1.txt | A | avaliacao |  | 97 | nucleo seed 44 | 158 | comp seed 44 |  |
| puc-hc12p-seed-r1.txt | A | avaliacao | sim | 171 | nucleo seed 44 | 345 | base seed 44 |  |
| puc-hc9u-regiao-f2.txt | F | avaliacao |  | 5 | comp seed 42 | 5 | base seed 42 |  |
| puc-hc9u-regiao-f4.txt | D | avaliacao |  | 36 | nucleo seed 44 | 39 | comp seed 42 |  |
| puc-hc9u-seed-r1.txt | A | avaliacao |  | 32 | nucleo seed 44 | 41 | comp seed 43 |  |
| puc-w23c23-intercalado-f2-rho.txt | F | desenvolvimento |  | 128 | nucleo seed 42 | 128 | comp seed 42 |  |
| puc-w23c23-seed-r1.txt | A | desenvolvimento |  | 140 | comp seed 44 | 156 | comp seed 43 |  |
| puc-w3c571-seed-r1.txt | A | desenvolvimento | sim | 669 | comp seed 43 | 1064 | comp seed 42 |  |
| pucn-cc3-10n-seed-r1.txt | A | desenvolvimento |  | 18 | nucleo seed 44 | 26 | base seed 42 |  |
| pucn-cc3-5n-seed-r1.txt | F | desenvolvimento |  | 8 | comp seed 42 | 8 | base seed 42 |  |
| pucn-cc5-3n-seed-r1.txt | F | desenvolvimento |  | 15 | comp seed 42 | 15 | base seed 42 |  |
| pucn-cc6-2n-seed-r1.txt | F | desenvolvimento |  | 6 | comp seed 42 | 6 | base seed 42 |  |
| pucn-cc7-3n-regiao-f2.txt | A | avaliacao |  | 10 | nucleo seed 44 | 14 | comp seed 42 |  |
| pucn-cc7-3n-seed-r1.txt | A | avaliacao |  | 69 | comp seed 44 | 80 | base seed 43 |  |
| urb-apia-m10-f8.txt | F | avaliacao |  | 8 | nucleo seed 42 | 8 | base seed 42 |  |
| urb-apia-m25-f2.txt | M | avaliacao |  | 2 | nucleo seed 42 | 2 | base seed 42 |  |
| urb-belize_city-m25-f4.txt | F | avaliacao |  | 4 | nucleo seed 42 | 4 | base seed 42 |  |
| urb-mindelo-m25-f4.txt | M | desenvolvimento |  | 4 | nucleo seed 42 | 4 | base seed 42 |  |
| urb-st_helier-m10-f4.txt | F | avaliacao |  | 4 | nucleo seed 42 | 4 | base seed 42 |  |
| vienna-I052-regiao-f4.txt | M | avaliacao |  | 7 | nucleo seed 42 | 7 | base seed 42 |  |
| vienna-I056-regiao-f4.txt | A | desenvolvimento |  | 9 | nucleo seed 44 | 11 | base seed 43 |  |
| vienna-I065-intercalado-f2.txt | A | desenvolvimento |  | 16 | comp seed 44 | 20 | base seed 42 |  |
| vienna-I065-regiao-f4.txt | A | desenvolvimento |  | 14 | comp seed 44 | 20 | comp seed 42 |  |

`Fora AV` marca as três instâncias com `m ≥ 1000`, declaradas fora da avaliação de avanço antes da corrida: `hc12p.txt`, `puc-hc12p-seed-r1.txt`, `puc-w3c571-seed-r1.txt`.

Nas 29 D/A que entram no avanço, nenhuma tem `LB* = UB*`. O gap `(UB* − LB*) / UB*` vai de 3,2% (`puc-cc9-2p-seed-r1`, 30/31) a 55,6% (`mapf-den312d-m50-f2-rho`, 4/9). A mediana é 18,6% (`puc-bip42p-seed-r1`, 35/43).

## 3. Contexto com E9 e E12

Os dois experimentos são pré-protocolo: uma semente no E9, `TimeLimit` de 60 s no núcleo e de 600 s no COMP. O E12 usa `TimeLimit` de 600 s nos três braços, sem `WorkLimit`. Os números abaixo não substituem esses relatórios. A pergunta é quais leituras qualitativas se repetem sob o contrato desta linha.

**O núcleo continua abaixo do COMP em MAPF e Vienna, e competitivo em PUC/PUCN.** Nas 11 D/A de MAPF desta partição, o LB do núcleo fica abaixo do LB do COMP em todas (mediana da razão 0,82). Nas 3 de Vienna, em nenhuma o núcleo passa o COMP. Em PUC, o núcleo passa o COMP em 4 das 11 D/A do avanço e fica abaixo em outras 4. Em PUCN, passa em 2 de 3. É a leitura do E9 (§2.1, itens 4 e 5). A mediana 0,87 do E9 era das 10 MAPF da partição antiga; o conjunto mudou.

Os seis casos em que o E9 viu o núcleo (60 s) acima do COMP (600 s) repetem o sentido aqui:

| Instância | E9 núcleo / COMP | Esta linha, LB do núcleo / LB do COMP |
|---|---|---|
| `puc-bip42p-regiao-f2` | 35 / 33 | 35 / 33 |
| `puc-bip42p-seed-r1` | 35 / 33 | 35 / 33 |
| `puc-hc10p-seed-r1` | 54 / 52 | 56 / 52 |
| `puc-hc11p-seed-r1` | 97 / 95 | 97 / 95 |
| `pucn-cc3-10n-seed-r1` | 18 / 17 | 18 / 17 |
| `pucn-cc7-3n-regiao-f2` | 10 / 9 | 10 / 9 |

`w3c571` continua do outro lado: o COMP chega a 669 e o núcleo fica em 571. No E9 eram 665 e 571. O acoplamento de fluxo ainda pesa nessa instância. Ela está fora do avanço (`m = 1142`).

**Onde o E12 já tinha separado núcleo e COMP, o sentido se mantém.** `cc9-2p`: núcleo 27, COMP com LB 30 e UB 31, como no E12. `cc11-2u`: LB 92 e UB 101, como a seed 42 do E12. `hc9u-regiao-f4`: LB 36 e UB 39, como no E12. `cc7-3n-regiao`: núcleo 10 contra COMP 9, como nas três seeds do E12; o UB* desta linha é 14, igual à pior seed do E12 e pior que o 12 da seed 42. `cc3-10n`: núcleo 18 e UB 26, iguais ao E12.

**Três leituras mudaram de valor, não de sentido.**

- `hc11p`. No E12 o núcleo chegou a LB 102 em 600 s de parede. Aqui para em 97, ainda acima do COMP (95). O UB* viável é 158, contra 159 do COMP no E12.
- `w23c23-seed`. No E12 o COMP ficou em LB 141. Aqui o LB* é 140, ainda acima do núcleo (139). O UB* é 156, contra 157.
- `cc7-3n-seed`. No E12 o COMP ficou em LB 68. Aqui o LB* é 69, ainda acima do núcleo (66). O UB* é 80, contra 83.

**`hc9u` continua aberta.** O LB* de `puc-hc9u-seed-r1` é 32, o mesmo do E9, do E12 e do intervalo histórico [32, 38]. O UB* desta linha é 41 (COMP, semente 43). A semente 44 do E12 tinha chegado a UB 38 sob `TimeLimit` de 600 s. Esta corrida não reproduz esse 38 e não estreita o intervalo. O legado `hc9u.txt`, com uma semente, repete LB 32 e UB 41.

**O COMP de `hc12p` continua sem incumbente**, nas três sementes, como no E9 e no E12. O UB* 345 vem da base, semente 44. O caso da spec em que `UB*` fica ausente não ocorreu.

**As quatro F em que o E9 viu o núcleo abaixo do ótimo repetem o mesmo par.** O núcleo fica em 5, 2, 4 e 5, e o COMP prova 7, 3, 6 e 7, nesta ordem: maze, pace-001, `pucn-cc6-2n`, lin03. As outras quatro F daquela regressão (`w23c23-intercalado`, `b-b12-intercalado`, `i-i080-301`, `urb-apia-m10`) fecham com núcleo e COMP no mesmo inteiro, como no E9.

**Os controles MAPF do E12 repetem o núcleo abaixo do COMP.** `mapf-random-32-32-10-m50-f8`: LB* 53 e UB* 71, contra 53 e 72 na seed 42 do E12; o núcleo fica em 43. `mapf-empty-32-32-m25-f4`: LB* 13 e UB* 18, contra 14 e 18; o núcleo fica em 11. A queda de 14 para 13 é uma unidade, a margem que o próprio E9 já marcava como instável.
