# AS-09 — Benchmark ampliado COMP, COMP+K, C, C+K

**Classificação:** exploratório, equivalência matemática de projeções ainda depende de revisão independente.

**Protocolo:** 15 instâncias, 600 s por braço, seed 42, threads 4.
Wall inclui leitura, alcance, cortes, construção e solução; RSS é pico do processo.
Os casos de avaliação não autorizam ajustes de parâmetros posteriores.

## LP

| Caso | Braço | Status | LP | Variáveis | Restrições | Não zeros | Wall(s) | Solver(s) | RSS(MiB) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | U | OPTIMAL_NUMERIC | 2.4000 | 12304 | 2046 | 47852 | 1.16 | 0.18 | 107.3 |
| mapf-room-32-32-4-m10-f8 | U_K | OPTIMAL_NUMERIC | 13.2000 | 12304 | 2070 | 48549 | 1.27 | 0.20 | 107.3 |
| mapf-room-32-32-4-m10-f8 | C | OPTIMAL_NUMERIC | 2.4000 | 11172 | 4102 | 24390 | 1.13 | 0.20 | 92.5 |
| mapf-room-32-32-4-m10-f8 | C_K | OPTIMAL_NUMERIC | 13.2000 | 11172 | 4126 | 25087 | 1.14 | 0.13 | 92.4 |
| puc-bip42p-regiao-f2 | U | OPTIMAL_NUMERIC | 1.0000 | 9164 | 3600 | 34256 | 1.22 | 0.29 | 105.2 |
| puc-bip42p-regiao-f2 | U_K | OPTIMAL_NUMERIC | 31.7061 | 9164 | 3800 | 38238 | 2.67 | 0.50 | 106.9 |
| puc-bip42p-regiao-f2 | C | OPTIMAL_NUMERIC | 1.0000 | 10564 | 3700 | 21128 | 1.06 | 0.14 | 92.7 |
| puc-bip42p-regiao-f2 | C_K | OPTIMAL_NUMERIC | 31.7061 | 10564 | 3900 | 25110 | 2.32 | 0.24 | 93.5 |
| puc-cc9-2p-seed-r1 | U | OPTIMAL_NUMERIC | 1.2500 | 5120 | 1536 | 19456 | 0.84 | 0.06 | 83.7 |
| puc-cc9-2p-seed-r1 | U_K | OPTIMAL_NUMERIC | 27.0268 | 5120 | 1603 | 20356 | 1.11 | 0.14 | 84.1 |
| puc-cc9-2p-seed-r1 | C | OPTIMAL_NUMERIC | 1.2500 | 5696 | 1568 | 11392 | 0.82 | 0.04 | 83.5 |
| puc-cc9-2p-seed-r1 | C_K | OPTIMAL_NUMERIC | 27.0268 | 5696 | 1635 | 12292 | 1.06 | 0.08 | 83.8 |
| puc-w3c571-seed-r1 | U | OPTIMAL_NUMERIC | 10.3631 | 24553 | 11991 | 90218 | 2.39 | 0.89 | 157.0 |
| puc-w3c571-seed-r1 | U_K | OPTIMAL_NUMERIC | 432.9336 | 24553 | 14275 | 100496 | 37.18 | 1.70 | 162.2 |
| puc-w3c571-seed-r1 | C | OPTIMAL_NUMERIC | 10.3631 | 30834 | 13133 | 61668 | 2.54 | 0.94 | 149.3 |
| puc-w3c571-seed-r1 | C_K | OPTIMAL_NUMERIC | 432.9336 | 30834 | 15417 | 71946 | 36.78 | 1.56 | 158.1 |
| pucn-cc3-10n-seed-r1 | U | OPTIMAL_NUMERIC | 1.2000 | 28000 | 3000 | 110000 | 2.40 | 1.18 | 165.6 |
| pucn-cc3-10n-seed-r1 | U_K | OPTIMAL_NUMERIC | 16.9333 | 28000 | 3050 | 111350 | 3.47 | 1.63 | 168.4 |
| pucn-cc3-10n-seed-r1 | C | OPTIMAL_NUMERIC | 1.2000 | 29050 | 3025 | 58100 | 1.80 | 0.48 | 138.6 |
| pucn-cc3-10n-seed-r1 | C_K | OPTIMAL_NUMERIC | 16.9333 | 29050 | 3075 | 59450 | 2.78 | 0.85 | 140.1 |
| vienna-I056-regiao-f4 | U | OPTIMAL_NUMERIC | 2.4400 | 383591 | 5973 | 1530382 | 16.04 | 8.52 | 967.8 |
| vienna-I056-regiao-f4 | U_K | OPTIMAL_NUMERIC | 8.5000 | 383591 | 6074 | 1558364 | 22.30 | 12.13 | 981.1 |
| vienna-I056-regiao-f4 | C | OPTIMAL_NUMERIC | 2.4400 | 102432 | 27899 | 226765 | 5.99 | 2.99 | 338.9 |
| vienna-I056-regiao-f4 | C_K | OPTIMAL_NUMERIC | 8.5000 | 102432 | 28000 | 254747 | 10.25 | 4.53 | 351.8 |
| mapf-den312d-m50-f2-rho | U | OPTIMAL_NUMERIC | 0.2800 | 552141 | 7335 | 2203674 | 20.58 | 10.46 | 1295.8 |
| mapf-den312d-m50-f2-rho | U_K | OPTIMAL_NUMERIC | 3.2000 | 552141 | 7346 | 2207985 | 24.02 | 12.23 | 1297.0 |
| mapf-den312d-m50-f2-rho | C | OPTIMAL_NUMERIC | 0.2800 | 182927 | 44060 | 402529 | 12.52 | 7.59 | 524.9 |
| mapf-den312d-m50-f2-rho | C_K | OPTIMAL_NUMERIC | 3.2000 | 182927 | 44071 | 406840 | 16.59 | 10.17 | 528.0 |
| mapf-empty-32-32-m25-f4 | U | OPTIMAL_NUMERIC | 1.0000 | 38204 | 3072 | 150768 | 2.12 | 0.79 | 171.9 |
| mapf-empty-32-32-m25-f4 | U_K | OPTIMAL_NUMERIC | 11.2533 | 38204 | 3102 | 151991 | 2.67 | 1.09 | 172.8 |
| mapf-empty-32-32-m25-f4 | C | OPTIMAL_NUMERIC | 1.0000 | 21117 | 6169 | 45306 | 1.40 | 0.28 | 125.1 |
| mapf-empty-32-32-m25-f4 | C_K | OPTIMAL_NUMERIC | 11.2533 | 21117 | 6199 | 46529 | 1.95 | 0.46 | 127.6 |
| mapf-maze-32-32-2-m10-f4 | U | OPTIMAL_NUMERIC | 1.1000 | 60566 | 1998 | 240932 | 2.25 | 0.64 | 189.4 |
| mapf-maze-32-32-2-m10-f4 | U_K | OPTIMAL_NUMERIC | 5.4000 | 60566 | 2008 | 241847 | 2.38 | 0.56 | 188.6 |
| mapf-maze-32-32-2-m10-f4 | C | OPTIMAL_NUMERIC | 1.1000 | 45318 | 12664 | 101292 | 2.48 | 0.98 | 180.2 |
| mapf-maze-32-32-2-m10-f4 | C_K | OPTIMAL_NUMERIC | 5.4000 | 45318 | 12674 | 102207 | 3.12 | 1.52 | 182.4 |
| mapf-random-64-64-20-m100-f4 | U | OPTIMAL_NUMERIC | 1.0300 | 124902 | 9810 | 493068 | 5.90 | 3.20 | 375.4 |
| mapf-random-64-64-20-m100-f4 | U_K | OPTIMAL_NUMERIC | 38.8550 | 124902 | 9907 | 497582 | 12.36 | 4.72 | 380.2 |
| mapf-random-64-64-20-m100-f4 | C | OPTIMAL_NUMERIC | 1.0300 | 71710 | 22990 | 156500 | 3.60 | 1.51 | 242.4 |
| mapf-random-64-64-20-m100-f4 | C_K | OPTIMAL_NUMERIC | 38.8550 | 71710 | 23087 | 161014 | 9.24 | 2.41 | 248.0 |
| pace18-t2-061-regiao-f4 | U | OPTIMAL_NUMERIC | 2.7857 | 57666 | 1584 | 229608 | 2.49 | 0.90 | 196.4 |
| pace18-t2-061-regiao-f4 | U_K | OPTIMAL_NUMERIC | 6.7857 | 57666 | 1706 | 241511 | 5.04 | 2.90 | 217.9 |
| pace18-t2-061-regiao-f4 | C | OPTIMAL_NUMERIC | 2.7857 | 21402 | 5322 | 46500 | 1.74 | 0.56 | 125.7 |
| pace18-t2-061-regiao-f4 | C_K | OPTIMAL_NUMERIC | 6.7857 | 21402 | 5444 | 58403 | 2.95 | 1.30 | 142.5 |
| vienna-I052-regiao-f4 | U | OPTIMAL_NUMERIC | 1.6500 | 485559 | 7089 | 1937510 | 21.94 | 12.99 | 1145.4 |
| vienna-I052-regiao-f4 | U_K | OPTIMAL_NUMERIC | 7.0000 | 485559 | 7134 | 1950974 | 28.35 | 16.74 | 1150.7 |
| vienna-I052-regiao-f4 | C | OPTIMAL_NUMERIC | 1.6500 | 131148 | 35465 | 290652 | 8.59 | 4.76 | 417.0 |
| vienna-I052-regiao-f4 | C_K | OPTIMAL_NUMERIC | 7.0000 | 131148 | 35510 | 304116 | 13.90 | 7.80 | 415.7 |
| urb-apia-m10-f8 | U | OPTIMAL_NUMERIC | 6.5000 | 365348 | 4854 | 1458156 | 15.47 | 8.74 | 884.7 |
| urb-apia-m10-f8 | U_K | OPTIMAL_NUMERIC | 8.0000 | 365348 | 4965 | 1482290 | 16.07 | 8.22 | 897.4 |
| urb-apia-m10-f8 | C | OPTIMAL_NUMERIC | 6.5000 | 100884 | 33988 | 230892 | 5.80 | 2.89 | 341.4 |
| urb-apia-m10-f8 | C_K | OPTIMAL_NUMERIC | 8.0000 | 100884 | 34099 | 255026 | 6.88 | 2.81 | 351.3 |
| b-b18-regiao-f2 | U | OPTIMAL_NUMERIC | 0.1200 | 5096 | 300 | 20184 | 0.78 | 0.02 | 82.7 |
| b-b18-regiao-f2 | U_K | OPTIMAL_NUMERIC | 2.0000 | 5096 | 304 | 20315 | 0.78 | 0.03 | 82.4 |
| b-b18-regiao-f2 | C | OPTIMAL_NUMERIC | 0.1200 | 1700 | 525 | 3600 | 0.72 | 0.03 | 76.6 |
| b-b18-regiao-f2 | C_K | OPTIMAL_NUMERIC | 2.0000 | 1700 | 529 | 3731 | 0.75 | 0.03 | 76.7 |
| i-i160-301-regiao-f2 | U | OPTIMAL_NUMERIC | 0.5000 | 5422 | 480 | 21368 | 0.82 | 0.04 | 82.9 |
| i-i160-301-regiao-f2 | U_K | OPTIMAL_NUMERIC | 4.0000 | 5422 | 498 | 22007 | 0.93 | 0.03 | 82.8 |
| i-i160-301-regiao-f2 | C | OPTIMAL_NUMERIC | 0.5000 | 2160 | 820 | 4640 | 0.73 | 0.03 | 77.5 |
| i-i160-301-regiao-f2 | C_K | OPTIMAL_NUMERIC | 4.0000 | 2160 | 838 | 5279 | 0.75 | 0.02 | 77.8 |

### Comparação pareada — C versus COMP

| Caso | K | LP igual? | Tempo COMP(s) | Tempo C(s) | Economia de tempo | Economia RSS | Economia vars | Economia nnz |
|---|---|---|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | não | True | 1.16 | 1.13 | +2.3% | +13.7% | +9.2% | +49.0% |
| mapf-room-32-32-4-m10-f8 | sim | True | 1.27 | 1.14 | +10.2% | +13.9% | +9.2% | +48.3% |
| puc-bip42p-regiao-f2 | não | True | 1.22 | 1.06 | +12.7% | +11.8% | -15.3% | +38.3% |
| puc-bip42p-regiao-f2 | sim | True | 2.67 | 2.32 | +13.0% | +12.5% | -15.3% | +34.3% |
| puc-cc9-2p-seed-r1 | não | True | 0.84 | 0.82 | +1.9% | +0.2% | -11.2% | +41.4% |
| puc-cc9-2p-seed-r1 | sim | True | 1.11 | 1.06 | +4.8% | +0.4% | -11.2% | +39.6% |
| puc-w3c571-seed-r1 | não | True | 2.39 | 2.54 | -6.2% | +4.9% | -25.6% | +31.6% |
| puc-w3c571-seed-r1 | sim | True | 37.18 | 36.78 | +1.1% | +2.6% | -25.6% | +28.4% |
| pucn-cc3-10n-seed-r1 | não | True | 2.40 | 1.80 | +25.1% | +16.3% | -3.8% | +47.2% |
| pucn-cc3-10n-seed-r1 | sim | True | 3.47 | 2.78 | +19.9% | +16.8% | -3.8% | +46.6% |
| vienna-I056-regiao-f4 | não | True | 16.04 | 5.99 | +62.6% | +65.0% | +73.3% | +85.2% |
| vienna-I056-regiao-f4 | sim | True | 22.30 | 10.25 | +54.1% | +64.1% | +73.3% | +83.7% |
| mapf-den312d-m50-f2-rho | não | True | 20.58 | 12.52 | +39.2% | +59.5% | +66.9% | +81.7% |
| mapf-den312d-m50-f2-rho | sim | True | 24.02 | 16.59 | +30.9% | +59.3% | +66.9% | +81.6% |
| mapf-empty-32-32-m25-f4 | não | True | 2.12 | 1.40 | +33.8% | +27.2% | +44.7% | +69.9% |
| mapf-empty-32-32-m25-f4 | sim | True | 2.67 | 1.95 | +27.2% | +26.2% | +44.7% | +69.4% |
| mapf-maze-32-32-2-m10-f4 | não | True | 2.25 | 2.48 | -10.1% | +4.9% | +25.2% | +58.0% |
| mapf-maze-32-32-2-m10-f4 | sim | True | 2.38 | 3.12 | -31.1% | +3.3% | +25.2% | +57.7% |
| mapf-random-64-64-20-m100-f4 | não | True | 5.90 | 3.60 | +39.0% | +35.4% | +42.6% | +68.3% |
| mapf-random-64-64-20-m100-f4 | sim | True | 12.36 | 9.24 | +25.2% | +34.8% | +42.6% | +67.6% |
| pace18-t2-061-regiao-f4 | não | True | 2.49 | 1.74 | +30.0% | +36.0% | +62.9% | +79.7% |
| pace18-t2-061-regiao-f4 | sim | True | 5.04 | 2.95 | +41.5% | +34.6% | +62.9% | +75.8% |
| vienna-I052-regiao-f4 | não | True | 21.94 | 8.59 | +60.8% | +63.6% | +73.0% | +85.0% |
| vienna-I052-regiao-f4 | sim | True | 28.35 | 13.90 | +51.0% | +63.9% | +73.0% | +84.4% |
| urb-apia-m10-f8 | não | True | 15.47 | 5.80 | +62.5% | +61.4% | +72.4% | +84.2% |
| urb-apia-m10-f8 | sim | True | 16.07 | 6.88 | +57.2% | +60.9% | +72.4% | +82.8% |
| b-b18-regiao-f2 | não | True | 0.78 | 0.72 | +8.2% | +7.4% | +66.6% | +82.2% |
| b-b18-regiao-f2 | sim | True | 0.78 | 0.75 | +4.9% | +6.9% | +66.6% | +81.6% |
| i-i160-301-regiao-f2 | não | True | 0.82 | 0.73 | +11.4% | +6.5% | +60.2% | +78.3% |
| i-i160-301-regiao-f2 | sim | True | 0.93 | 0.75 | +19.4% | +5.9% | +60.2% | +76.0% |

## MIP

| Caso | Braço | Status | UB físico | LB solver | Gap validado | Nós | Wall(s) | 1ª UB(s) | RSS(MiB) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | U | TIME_LIMIT | 18 | 15.0000 | 0.16667 | 20712 | 555.15 | 0.11 | 497.3 |
| mapf-room-32-32-4-m10-f8 | U_K | TIME_LIMIT | 18 | 16.0000 | 0.11111 | 1665 | 555.09 | 0.07 | 368.5 |
| mapf-room-32-32-4-m10-f8 | C | TIME_LIMIT | 18 | 15.0000 | 0.16667 | 42254 | 555.11 | 0.12 | 461.1 |
| mapf-room-32-32-4-m10-f8 | C_K | TIME_LIMIT | 18 | 16.0000 | 0.11111 | 80371 | 555.13 | 0.13 | 535.7 |
| puc-bip42p-regiao-f2 | U | TIME_LIMIT | 46 | 33.0000 | 0.28261 | 956 | 555.58 | 0.07 | 278.4 |
| puc-bip42p-regiao-f2 | U_K | TIME_LIMIT | 44 | 33.0000 | 0.25000 | 6871 | 555.62 | 0.08 | 293.7 |
| puc-bip42p-regiao-f2 | C | TIME_LIMIT | 44 | 32.0000 | 0.27273 | 414 | 555.58 | 0.07 | 277.9 |
| puc-bip42p-regiao-f2 | C_K | TIME_LIMIT | 43 | 33.0000 | 0.23256 | 10666 | 555.60 | 0.09 | 399.7 |
| puc-cc9-2p-seed-r1 | U | OPTIMAL_NUMERIC | 31 | 31.0000 | 0.00000 | 10029 | 489.26 | 0.03 | 243.7 |
| puc-cc9-2p-seed-r1 | U_K | OPTIMAL_NUMERIC | 31 | 31.0000 | 0.00000 | 13670 | 502.52 | 0.03 | 246.1 |
| puc-cc9-2p-seed-r1 | C | TIME_LIMIT | 31 | 30.0000 | 0.03226 | 10970 | 555.15 | 0.04 | 235.0 |
| puc-cc9-2p-seed-r1 | C_K | TIME_LIMIT | 31 | 30.0000 | 0.03226 | 12193 | 555.14 | 0.04 | 240.3 |
| puc-w3c571-seed-r1 | U | TIME_LIMIT | 1087 | 576.0000 | 0.47010 | 5364 | 589.14 | 3.74 | 1009.9 |
| puc-w3c571-seed-r1 | U_K | TIME_LIMIT | 1079 | 664.0000 | 0.38462 | 5110 | 589.20 | 3.69 | 832.3 |
| puc-w3c571-seed-r1 | C | TIME_LIMIT | 1106 | 581.0000 | 0.47468 | 5333 | 589.01 | 5.04 | 921.5 |
| puc-w3c571-seed-r1 | C_K | VALIDATION_FAIL | — | — | — | 4650 | 590.21 | 4.77 | 710.3 |
| pucn-cc3-10n-seed-r1 | U | TIME_LIMIT | 26 | 17.0000 | 0.34615 | 2598 | 555.16 | 0.01 | 501.5 |
| pucn-cc3-10n-seed-r1 | U_K | TIME_LIMIT | 26 | 17.0000 | 0.34615 | 2662 | 555.20 | 0.01 | 465.7 |
| pucn-cc3-10n-seed-r1 | C | TIME_LIMIT | 26 | 3.0000 | 0.88462 | 5588 | 555.11 | 1.10 | 527.5 |
| pucn-cc3-10n-seed-r1 | C_K | TIME_LIMIT | 26 | 17.0000 | 0.34615 | 2882 | 555.19 | 3.64 | 469.7 |
| vienna-I056-regiao-f4 | U | TIME_LIMIT | 11 | 4.0000 | 0.63636 | 1 | 557.39 | 0.08 | 1197.3 |
| vienna-I056-regiao-f4 | U_K | TIME_LIMIT | 13 | 9.0000 | 0.30769 | 1 | 557.38 | 0.08 | 1248.5 |
| vienna-I056-regiao-f4 | C | TIME_LIMIT | 16 | 3.0000 | 0.81250 | 971 | 557.08 | 12.64 | 1290.3 |
| vienna-I056-regiao-f4 | C_K | TIME_LIMIT | 13 | 9.0000 | 0.30769 | 2501 | 556.41 | 21.76 | 1437.2 |
| mapf-den312d-m50-f2-rho | U | TIME_LIMIT | 9 | 1.0000 | 0.88889 | 907 | 557.39 | 0.11 | 4640.5 |
| mapf-den312d-m50-f2-rho | U_K | TIME_LIMIT | 9 | 4.0000 | 0.55556 | 1283 | 557.25 | 0.11 | 4538.1 |
| mapf-den312d-m50-f2-rho | C | TIME_LIMIT | 9 | 1.0000 | 0.88889 | 3379 | 555.91 | 18.65 | 2939.4 |
| mapf-den312d-m50-f2-rho | C_K | TIME_LIMIT | 11 | 4.0000 | 0.63636 | 1446 | 555.65 | 32.83 | 2478.5 |
| mapf-empty-32-32-m25-f4 | U | TIME_LIMIT | 19 | 14.0000 | 0.26316 | 1909 | 555.18 | 0.01 | 702.1 |
| mapf-empty-32-32-m25-f4 | U_K | TIME_LIMIT | 18 | 13.0000 | 0.27778 | 2396 | 555.19 | 0.01 | 583.9 |
| mapf-empty-32-32-m25-f4 | C | TIME_LIMIT | 19 | 12.0000 | 0.36842 | 4912 | 555.11 | 0.85 | 467.4 |
| mapf-empty-32-32-m25-f4 | C_K | TIME_LIMIT | 18 | 12.0000 | 0.33333 | 11128 | 555.14 | 1.78 | 690.8 |
| mapf-maze-32-32-2-m10-f4 | U | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1311 | 81.93 | 0.01 | 694.5 |
| mapf-maze-32-32-2-m10-f4 | U_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 7.16 | 0.01 | 364.6 |
| mapf-maze-32-32-2-m10-f4 | C | TIME_LIMIT | 7 | 3.0000 | 0.57143 | 83237 | 555.33 | 1.36 | 1711.6 |
| mapf-maze-32-32-2-m10-f4 | C_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 38.10 | 1.51 | 462.4 |
| mapf-random-64-64-20-m100-f4 | U | TIME_LIMIT | 68 | 39.0000 | 0.42647 | 1 | 555.45 | 6.96 | 1123.0 |
| mapf-random-64-64-20-m100-f4 | U_K | TIME_LIMIT | 66 | 42.0000 | 0.36364 | 1 | 555.77 | 11.30 | 1036.5 |
| mapf-random-64-64-20-m100-f4 | C | TIME_LIMIT | 75 | 2.0000 | 0.97333 | 1889 | 555.43 | 7.65 | 935.1 |
| mapf-random-64-64-20-m100-f4 | C_K | TIME_LIMIT | 68 | 41.0000 | 0.39706 | 1096 | 555.68 | 16.01 | 889.8 |
| pace18-t2-061-regiao-f4 | U | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1286 | 231.59 | 0.01 | 686.1 |
| pace18-t2-061-regiao-f4 | U_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 8.72 | 0.01 | 381.8 |
| pace18-t2-061-regiao-f4 | C | TIME_LIMIT | 7 | 4.0000 | 0.42857 | 20767 | 555.72 | 1.77 | 774.9 |
| pace18-t2-061-regiao-f4 | C_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 6.65 | 2.36 | 222.7 |
| vienna-I052-regiao-f4 | U | TIME_LIMIT | 9 | 3.0000 | 0.66667 | 1 | 556.98 | 0.10 | 1521.5 |
| vienna-I052-regiao-f4 | U_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 189.22 | 0.10 | 1502.1 |
| vienna-I052-regiao-f4 | C | TIME_LIMIT | 10 | 2.0000 | 0.80000 | 792 | 556.70 | 18.55 | 1716.8 |
| vienna-I052-regiao-f4 | C_K | OPTIMAL_NUMERIC | 7 | 7.0000 | 0.00000 | 1 | 80.82 | 35.84 | 1063.7 |
| urb-apia-m10-f8 | U | OPTIMAL_NUMERIC | 8 | 8.0000 | 0.00000 | 1 | 82.99 | 0.07 | 1573.0 |
| urb-apia-m10-f8 | U_K | OPTIMAL_NUMERIC | 8 | 8.0000 | 0.00000 | 1 | 18.90 | 0.08 | 1203.6 |
| urb-apia-m10-f8 | C | OPTIMAL_NUMERIC | 8 | 8.0000 | 0.00000 | 1 | 80.64 | 17.74 | 890.7 |
| urb-apia-m10-f8 | C_K | OPTIMAL_NUMERIC | 8 | 8.0000 | 0.00000 | 1 | 24.52 | 20.50 | 494.2 |
| b-b18-regiao-f2 | U | OPTIMAL_NUMERIC | 2 | 2.0000 | 0.00000 | 1 | 0.88 | 0.00 | 108.6 |
| b-b18-regiao-f2 | U_K | OPTIMAL_NUMERIC | 2 | 2.0000 | 0.00000 | 1 | 0.80 | 0.00 | 100.6 |
| b-b18-regiao-f2 | C | OPTIMAL_NUMERIC | 2 | 2.0000 | 0.00000 | 1 | 0.82 | 0.00 | 91.6 |
| b-b18-regiao-f2 | C_K | OPTIMAL_NUMERIC | 2 | 2.0000 | 0.00000 | 1 | 0.71 | 0.00 | 88.0 |
| i-i160-301-regiao-f2 | U | OPTIMAL_NUMERIC | 4 | 4.0000 | 0.00000 | 1 | 1.06 | 0.00 | 116.4 |
| i-i160-301-regiao-f2 | U_K | OPTIMAL_NUMERIC | 4 | 4.0000 | 0.00000 | 1 | 0.80 | 0.00 | 101.6 |
| i-i160-301-regiao-f2 | C | OPTIMAL_NUMERIC | 4 | 4.0000 | 0.00000 | 1 | 1.04 | 0.02 | 95.7 |
| i-i160-301-regiao-f2 | C_K | OPTIMAL_NUMERIC | 4 | 4.0000 | 0.00000 | 1 | 0.77 | 0.02 | 86.9 |

### Comparação pareada — C versus COMP

| Caso | K | Gap COMP | Gap C | Melhora gap (p.p.) | UB COMP | UB C | LB COMP | LB C | Economia de tempo |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | não | +16.7% | +16.7% | 0.00 | 18 | 18 | 15.0000 | 15.0000 | +0.0% |
| mapf-room-32-32-4-m10-f8 | sim | +11.1% | +11.1% | 0.00 | 18 | 18 | 16.0000 | 16.0000 | -0.0% |
| puc-bip42p-regiao-f2 | não | +28.3% | +27.3% | 0.99 | 46 | 44 | 33.0000 | 32.0000 | +0.0% |
| puc-bip42p-regiao-f2 | sim | +25.0% | +23.3% | 1.74 | 44 | 43 | 33.0000 | 33.0000 | +0.0% |
| puc-cc9-2p-seed-r1 | não | +0.0% | +3.2% | -3.23 | 31 | 31 | 31.0000 | 30.0000 | -13.5% |
| puc-cc9-2p-seed-r1 | sim | +0.0% | +3.2% | -3.23 | 31 | 31 | 31.0000 | 30.0000 | -10.5% |
| puc-w3c571-seed-r1 | não | +47.0% | +47.5% | -0.46 | 1087 | 1106 | 576.0000 | 581.0000 | +0.0% |
| puc-w3c571-seed-r1 | sim | +38.5% | — | — | 1079 | — | 664.0000 | — | -0.2% |
| pucn-cc3-10n-seed-r1 | não | +34.6% | +88.5% | -53.85 | 26 | 26 | 17.0000 | 3.0000 | +0.0% |
| pucn-cc3-10n-seed-r1 | sim | +34.6% | +34.6% | 0.00 | 26 | 26 | 17.0000 | 17.0000 | +0.0% |
| vienna-I056-regiao-f4 | não | +63.6% | +81.2% | -17.61 | 11 | 16 | 4.0000 | 3.0000 | +0.1% |
| vienna-I056-regiao-f4 | sim | +30.8% | +30.8% | 0.00 | 13 | 13 | 9.0000 | 9.0000 | +0.2% |
| mapf-den312d-m50-f2-rho | não | +88.9% | +88.9% | 0.00 | 9 | 9 | 1.0000 | 1.0000 | +0.3% |
| mapf-den312d-m50-f2-rho | sim | +55.6% | +63.6% | -8.08 | 9 | 11 | 4.0000 | 4.0000 | +0.3% |
| mapf-empty-32-32-m25-f4 | não | +26.3% | +36.8% | -10.53 | 19 | 19 | 14.0000 | 12.0000 | +0.0% |
| mapf-empty-32-32-m25-f4 | sim | +27.8% | +33.3% | -5.56 | 18 | 18 | 13.0000 | 12.0000 | +0.0% |
| mapf-maze-32-32-2-m10-f4 | não | +0.0% | +57.1% | -57.14 | 7 | 7 | 7.0000 | 3.0000 | -577.8% |
| mapf-maze-32-32-2-m10-f4 | sim | +0.0% | +0.0% | 0.00 | 7 | 7 | 7.0000 | 7.0000 | -431.9% |
| mapf-random-64-64-20-m100-f4 | não | +42.6% | +97.3% | -54.69 | 68 | 75 | 39.0000 | 2.0000 | +0.0% |
| mapf-random-64-64-20-m100-f4 | sim | +36.4% | +39.7% | -3.34 | 66 | 68 | 42.0000 | 41.0000 | +0.0% |
| pace18-t2-061-regiao-f4 | não | +0.0% | +42.9% | -42.86 | 7 | 7 | 7.0000 | 4.0000 | -140.0% |
| pace18-t2-061-regiao-f4 | sim | +0.0% | +0.0% | 0.00 | 7 | 7 | 7.0000 | 7.0000 | +23.7% |
| vienna-I052-regiao-f4 | não | +66.7% | +80.0% | -13.33 | 9 | 10 | 3.0000 | 2.0000 | +0.0% |
| vienna-I052-regiao-f4 | sim | +0.0% | +0.0% | 0.00 | 7 | 7 | 7.0000 | 7.0000 | +57.3% |
| urb-apia-m10-f8 | não | +0.0% | +0.0% | 0.00 | 8 | 8 | 8.0000 | 8.0000 | +2.8% |
| urb-apia-m10-f8 | sim | +0.0% | +0.0% | 0.00 | 8 | 8 | 8.0000 | 8.0000 | -29.7% |
| b-b18-regiao-f2 | não | +0.0% | +0.0% | 0.00 | 2 | 2 | 2.0000 | 2.0000 | +6.2% |
| b-b18-regiao-f2 | sim | +0.0% | +0.0% | 0.00 | 2 | 2 | 2.0000 | 2.0000 | +11.7% |
| i-i160-301-regiao-f2 | não | +0.0% | +0.0% | 0.00 | 4 | 4 | 4.0000 | 4.0000 | +2.0% |
| i-i160-301-regiao-f2 | sim | +0.0% | +0.0% | 0.00 | 4 | 4 | 4.0000 | 4.0000 | +4.0% |

**Decisão exploratória:** `EXPLORATORY_WITH_CENSORED_ARMS`.
