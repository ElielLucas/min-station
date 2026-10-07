# Resultados E14 — Cutoff nas D/A de gap absoluto 2

**Data:** 2026-09-30
**Formulação:** baseline, variante U, fluxo contínuo, cortes C1+C2+C4
**Ambiente:** Gurobi 12.0.3, seed 42, 4 threads, TL 14400 s, 2 fatias
**Plano:** passo 3 de `docs/technical/plans/plano-pos-e13.md`
**Dados:** `results/benchmark/e14_fatia{1,2}.csv`
**Tabela:** gerada a partir desses CSVs

Quatro instâncias com UB_melhor − LB_melhor = 2 no E13. COMP com `Cutoff = UB_melhor − 0,5` e `MIPFocus = 3`. `OPT = UB_melhor` só com status `CUTOFF` e nenhuma solução abaixo de UB_melhor.

## 1. Resultado

| Instância | LB_melhor | UB_melhor | LB final | UB | status | veredito |
|---|---|---|---|---|---|---|
| `mapf-room-32-32-4-m10-f8` | 16.0 | 18.0 | 16.0 | — | TIME_LIMIT | inconclusivo |
| `mapf-room-32-32-4-m25-f4-rho` | 17.0 | 19.0 | 18.0 | — | TIME_LIMIT | inconclusivo |
| `vienna-I056-regiao-f4` | 9.0 | 11.0 | 9.0 | — | TIME_LIMIT | inconclusivo |
| `vienna-I065-intercalado-f2` | 17.0 | 19.0 | 17.0 | — | TIME_LIMIT | inconclusivo |

OPT = UB_melhor: **0/4**. Nenhuma solução abaixo de UB_melhor. O único LB que se moveu foi `mapf-room-32-32-4-m25-f4-rho`, de 17 para 18.

## 2. E11

O critério pré-registrado pede ≥ 3 das 4 com OPT = UB_melhor para o E11 voltar à fila. São 0. O E11 não volta.

São as instâncias de gap menor. O resultado não se estende às de 30–44% de residual.
