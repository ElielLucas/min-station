# AS-06 — piloto MIP pareado

**Classificação:** exploratória, sem homologação independente.
**Etapa:** `replication` · **Decisão:** `REPLICATION_SIGNAL_EXPLORATORY`

Pares comparáveis: 18/18; materiais: 11; não comparáveis: 0.

| Caso | Seed | COMP gap | COMP+K gap | Δ gap | Estado |
|---|---:|---:|---:|---:|---|
| mapf-room-32-32-4-m10-f8 | 42 | 16.6667% | 11.1111% | 5.5556% | MATCHED |
| mapf-room-32-32-4-m10-f8 | 43 | 11.1111% | 11.1111% | 0.0000% | MATCHED |
| mapf-room-32-32-4-m10-f8 | 44 | 16.6667% | 11.1111% | 5.5556% | MATCHED |
| puc-bip42p-regiao-f2 | 42 | 28.2609% | 25.0000% | 3.2609% | MATCHED |
| puc-bip42p-regiao-f2 | 43 | 28.2609% | 23.2558% | 5.0051% | MATCHED |
| puc-bip42p-regiao-f2 | 44 | 26.6667% | 20.9302% | 5.7364% | MATCHED |
| puc-cc9-2p-seed-r1 | 42 | 0.0000% | 0.0000% | 0.0000% | MATCHED |
| puc-cc9-2p-seed-r1 | 43 | 0.0000% | 0.0000% | 0.0000% | MATCHED |
| puc-cc9-2p-seed-r1 | 44 | 0.0000% | 0.0000% | 0.0000% | MATCHED |
| puc-w3c571-seed-r1 | 42 | 47.1021% | 38.4615% | 8.6406% | MATCHED |
| puc-w3c571-seed-r1 | 43 | 47.2527% | 38.0734% | 9.1794% | MATCHED |
| puc-w3c571-seed-r1 | 44 | 46.9557% | 37.3961% | 9.5596% | MATCHED |
| pucn-cc3-10n-seed-r1 | 42 | 34.6154% | 34.6154% | 0.0000% | MATCHED |
| pucn-cc3-10n-seed-r1 | 43 | 34.6154% | 34.6154% | 0.0000% | MATCHED |
| pucn-cc3-10n-seed-r1 | 44 | 34.6154% | 34.6154% | 0.0000% | MATCHED |
| vienna-I056-regiao-f4 | 42 | 63.6364% | 30.7692% | 32.8671% | MATCHED |
| vienna-I056-regiao-f4 | 43 | 69.2308% | 30.7692% | 38.4615% | MATCHED |
| vienna-I056-regiao-f4 | 44 | 69.2308% | 30.7692% | 38.4615% | MATCHED |

## Limitações

- Gap MIP numérico usa melhor LB do Gurobi e UB fisicamente validada
- MIPGap não equivale a gap de integralidade com ótimo desconhecido
- Tempo até incumbente validado é relógio do solver, não wall total
- Ausência de evento validado NÃO é interpolada
- Somente desenvolvimento; decisão não promove AS08/AS11
