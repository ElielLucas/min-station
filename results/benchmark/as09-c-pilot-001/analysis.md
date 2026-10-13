# AS09 — Comparação LP COMP × C

**Decisão exploratória:** `INVESTIGATE_CENSORED`.

**Equivalência matemática:** revisão independente pendente. LPs são numéricos (Gurobi).

| Caso | K | COMP LP | C LP | Equiv. numérica | U vars | C vars | U wall(s) | C wall(s) |
|---|---|---:|---:|---|---:|---:|---:|---:|
| vienna-I056-regiao-f4 | não | 2.44000 | 2.44000 | True | 383591 | 102432 | 16.85378 | 7.00353 |
| vienna-I056-regiao-f4 | sim | 8.50000 | 8.50000 | True | 383591 | 102432 | 23.07975 | 11.20533 |
| mapf-den312d-m50-f2-rho | não | — | 0.28000 | None | — | 182927 | 1.93261 | 12.39096 |
| mapf-den312d-m50-f2-rho | sim | — | 3.20000 | None | — | 182927 | 3.78897 | 17.60551 |
| puc-cc9-2p-seed-r1 | não | 1.25000 | 1.25000 | True | 5120 | 5696 | 1.26901 | 1.18196 |
| puc-cc9-2p-seed-r1 | sim | 27.02679 | 27.02679 | True | 5120 | 5696 | 1.66298 | 1.59678 |

O tempo wall inclui leitura, preparação de A_r, K nos braços com cortes, construção e solução.
Não inferir equivalência LP em caso de censura ou apenas por concordância numérica.
