# AS-06 — piloto MIP pareado

**Classificação:** exploratória, sem homologação independente.
**Etapa:** `screening` · **Decisão:** `GO_REPLICATION_EXPLORATORY`

Pares comparáveis: 6/6; materiais: 3; não comparáveis: 0.

| Caso | Seed | COMP gap | COMP+K gap | Δ gap | Estado |
|---|---:|---:|---:|---:|---|
| mapf-room-32-32-4-m10-f8 | 42 | 16.6667% | 11.1111% | 5.5556% | MATCHED |
| puc-bip42p-regiao-f2 | 42 | 28.2609% | 26.6667% | 1.5942% | MATCHED |
| puc-cc9-2p-seed-r1 | 42 | 3.2258% | 3.2258% | 0.0000% | MATCHED |
| puc-w3c571-seed-r1 | 42 | 57.8182% | 40.2878% | 17.5304% | MATCHED |
| pucn-cc3-10n-seed-r1 | 42 | 34.6154% | 34.6154% | 0.0000% | MATCHED |
| vienna-I056-regiao-f4 | 42 | 69.2308% | 30.7692% | 38.4615% | MATCHED |

## Limitações

- Gap MIP numérico usa melhor LB do Gurobi e UB fisicamente validada
- MIPGap não equivale a gap de integralidade com ótimo desconhecido
- Tempo até incumbente validado é relógio do solver, não wall total
- Ausência de evento validado NÃO é interpolada
- Somente desenvolvimento; decisão não promove AS08/AS11
