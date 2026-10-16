# AS20 — Resultado da triagem LP de HL em desenvolvimento

**Estado:** campanha Gurobi executada em 15/10/2026; gate calculado `INVESTIGATE`. A execução não certificou cortes HL. **Não constitui prova de redundância de HL sobre COMP+K.**

## Dados arquivados

- `results/benchmark/as20-hl-lp-001/manifest.json`
- `results/benchmark/as20-hl-lp-001/rows.json`
- `results/benchmark/as20-hl-lp-001/analysis.json`
- Casos: seis; braços: 12; cortes certificados/adicionados: zero.

## Desempenho observado

| Caso | Status COMP+K | Status COMP+K+HL | LP base | LP HL | Tempo base (s) | Tempo HL (s) | Chamadas |
|---|---|---|---:|---:|---:|---:|---:|
| puc-cc9-2p-seed-r1 | OPTIMAL | OPTIMAL | 27.0268 | 27.0268 | 2.2207 | 25.7143 | 464 |
| puc-bip42p-regiao-f2 | OPTIMAL | OPTIMAL | 31.7061 | 31.7061 | 13.9259 | 38.1167 | 54 |
| pucn-cc3-10n-seed-r1 | OPTIMAL | OPTIMAL | 16.9333 | 16.9333 | 6.1782 | 6.3068 | — |
| mapf-room-32-32-4-m10-f8 | OPTIMAL | OPTIMAL | 13.2000 | 13.2000 | 1.3712 | 20.8751 | 1430 |
| vienna-I056-regiao-f4 | TIME_LIMIT | OPTIMAL | — | — | 90.1028 | 88.8438 | — |
| puc-w3c571-seed-r1 | TIME_LIMIT | TIME_LIMIT | — | — | 90.0986 | 90.1018 | — |

## Diagnóstico e decisão

- Quatro pares LP ótimos apresentaram ganho marginal zero.
- O suporte dos cortes e a certificação foram limitados: orçamento parcial, ausência de candidatos elegíveis e censuras impediram observação ampla.
- A comparação de tempos é por execução única e não constitui estimativa estatística de desempenho.
- **Gate AS20: `INVESTIGATE`**, preservado sem modificação dos dados.
- **Encaminhamento:** AS21 implementa certificação por camadas inferiores e propostas estruturais, mantendo uma campanha LP própria e independente de H2.
- **Revisão científica humana independente:** pendente.
