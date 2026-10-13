# AS-08 — Piloto exploratório LP: COMP+K × B+K

**Decisão:** `INVESTIGATE_CENSORED`.
**Não comparar o objetivo RMP com o limite LP completo.**

| Caso | COMP+K LP | B+K LP | Ganho B | B LB racional | Status |
|---|---:|---:|---:|---:|---|
| mapf-room-32-32-4-m10-f8 | 13.200000 | — | — | — | CENSORED |
| puc-bip42p-regiao-f2 | 31.706052 | — | — | — | CENSORED |
| puc-cc9-2p-seed-r1 | 27.026786 | — | — | — | CENSORED |
| puc-w3c571-seed-r1 | 432.933611 | — | — | — | CENSORED |
| pucn-cc3-10n-seed-r1 | 16.933333 | — | — | — | CENSORED |
| vienna-I056-regiao-f4 | 8.500000 | — | — | — | CENSORED |

## Diagnóstico de progresso B+K
O evento representa o último checkpoint persistido pelo supervisor. 
Objetivos intermediários do RMP NÃO são limites inferiores globais.

| Caso | Status B | Etapa/limite | Último evento | Iteração | Colunas | Eventos |
|---|---|---|---|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | CAP_EXCEEDED | SELECTING max_columns 5000/5000 | CG_FINISHED | — | 5000 | 464 |
| puc-bip42p-regiao-f2 | CAP_EXCEEDED | SELECTING max_columns 5000/5000 | CG_FINISHED | — | 5000 | 158 |
| puc-cc9-2p-seed-r1 | CAP_EXCEEDED | SELECTING max_columns 5000/5000 | CG_FINISHED | — | 5000 | 158 |
| puc-w3c571-seed-r1 | TIMEOUT_SOLVER | — | PRICING_FINISHED | 8 | 1400 | 57 |
| pucn-cc3-10n-seed-r1 | CAP_EXCEEDED | SELECTING max_columns 5000/5000 | CG_FINISHED | — | 5000 | 158 |
| vienna-I056-regiao-f4 | CAP_EXCEEDED | SELECTING max_columns 5000/5000 | CG_FINISHED | — | 5000 | 158 |

O pilot é desenvolvimento exploratório, sem autorização de promoção científica.
Branch-and-price não foi implementado; nenhum resultado MIP para B é alegado.
