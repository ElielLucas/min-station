# AS09 — Comparação LP COMP × C

**Decisão exploratória:** `PROMISING_EXPLORATORY_PROOF_REVIEW_PENDING`.

**Equivalência matemática:** revisão independente pendente. LPs são numéricos (Gurobi).

| Caso | K | COMP LP | C LP | Equiv. numérica | U vars | C vars | U wall(s) | C wall(s) |
|---|---|---:|---:|---|---:|---:|---:|---:|
| vienna-I056-regiao-f4 | não | 2.44000 | 2.44000 | True | 383591 | 102432 | 16.94116 | 6.12959 |
| vienna-I056-regiao-f4 | sim | 8.50000 | 8.50000 | True | 383591 | 102432 | 22.12037 | 10.39618 |
| mapf-den312d-m50-f2-rho | não | 0.28000 | 0.28000 | True | 552141 | 182927 | 20.26156 | 11.56169 |
| mapf-den312d-m50-f2-rho | sim | 3.20000 | 3.20000 | True | 552141 | 182927 | 24.12374 | 16.68367 |
| puc-cc9-2p-seed-r1 | não | 1.25000 | 1.25000 | True | 5120 | 5696 | 0.84154 | 0.82868 |
| puc-cc9-2p-seed-r1 | sim | 27.02679 | 27.02679 | True | 5120 | 5696 | 1.11916 | 1.07162 |

O tempo wall inclui leitura, preparação de A_r, K nos braços com cortes, construção e solução.
Não inferir equivalência LP em caso de censura ou apenas por concordância numérica.
