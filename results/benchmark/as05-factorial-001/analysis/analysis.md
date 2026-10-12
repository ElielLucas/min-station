# AS-05 — Comparação fatorial exploratória (A2/A4 × K)

**Estado:** exploratório; sem revisão independente nem promoção automática.

**Interpretação:** `PROMISING_EXPLORATORY_REPLICATION_REQUIRED`

| Instância | U | U+K | A2 | A2+K | A4 | A4+K |
|---|---:|---:|---:|---:|---:|---:|
| mapf-room-32-32-4-m10-f8 | 2.400000 | 13.200000 | 2.800000 | 13.200000 | 4.635938 | 13.292857 |
| puc-bip42p-regiao-f2 | 1.000000 | 31.706052 | 1.000000 | 31.706052 | 1.358584 | 31.706052 |
| puc-cc9-2p-seed-r1 | 1.250000 | 27.026786 | 1.702197 | 27.031250 | 2.786631 | 27.052083 |
| puc-w3c571-seed-r1 | 10.363120 | 432.933611 | 10.903210 | 433.019342 | 11.544792 | 433.175276 |
| pucn-cc3-10n-seed-r1 | 1.200000 | 16.933333 | 1.399762 | 16.933333 | 2.127161 | 16.933333 |
| vienna-I056-regiao-f4 | 2.440000 | 8.500000 | 2.661282 | 8.509615 | 3.182083 | 8.555556 |

## Efeitos e cobertura

| Contraste | Comparáveis | Ganhos > 0,000001 | Ganhos ≥ 1% |
|---|---:|---:|---:|
| K_ON_U | 6/6 | 6 | 6 |
| GROUP_2_NO_K | 6/6 | 5 | 5 |
| GROUP_4_NO_K | 6/6 | 6 | 6 |
| A4_VS_U_NO_K | 6/6 | 6 | 6 |
| K_ON_A2 | 6/6 | 6 | 6 |
| K_ON_A4 | 6/6 | 6 | 6 |
| REFINEMENT_WITH_K | 6/6 | 4 | 0 |
| A2_OVER_U_K | 6/6 | 3 | 0 |
| A4_OVER_U_K | 6/6 | 4 | 0 |

## Interação entre cortes e refinamento

Interação = [LP(A4+K) − LP(A2+K)] − [LP(A4) − LP(A2)].
Pode ser positiva, zero ou negativa; não é um critério de promoção isolado.

| Instância | Interação LP |
|---|---:|
| mapf-room-32-32-4-m10-f8 | -1.743081 |
| puc-bip42p-regiao-f2 | -0.358584 |
| puc-cc9-2p-seed-r1 | -1.063600 |
| puc-w3c571-seed-r1 | -0.485648 |
| pucn-cc3-10n-seed-r1 | -0.727399 |
| vienna-I056-regiao-f4 | -0.474861 |

## Limitações

- Sem seleção/ajuste pós-hoc em casos de avaliação
- 1% apenas leitura descritiva, não gate científico GO
- Nem todo braço tem solução se censurado; mantém N=6
