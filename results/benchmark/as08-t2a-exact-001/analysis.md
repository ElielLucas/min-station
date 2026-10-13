# AS-08/T2a — validação exata de B enumerada

**Natureza:** controle exploratório de desenvolvimento, não certifica a prova de T1.
**Backend:** `gurobi`. **Versão:** `as08-t2a-v1`.
**Decisão:** `PASS_EXPLORATORY`.

| Caso | Caminhos | Sem K | Com K |
|---|---:|---|---|
| e1-b4-star | 4 | 1.0 | 1.0 |
| e2-disaggregated-hub | 7 | 1.0 | 1.0 |
| e3-lp-gap | 8 | 0.5 | 1.0 |
| e4-stay-only | 1 | 0.0 | 0.0 |
| e5-origin-destination-swap | 4 | 0.0 | 0.0 |
| one-arc-direct | 1 | 0.0 | 0.0 |
| relay-line | 4 | 2.0 | 2.0 |
| autonomy-two | 12 | 0.0 | 0.0 |
| infeasible-components | 0 | None | None |
| overlap-triangle | 7 | 0.0 | 0.0 |

Todos os resultados de LP são numéricos; amostras finitas de fibras y não provam equivalência universal.
B completo por enumeração, não RMP nem bound de column generation.
K foi preparado pelas famílias C1+C2+C4-DM do projeto.
Não substitui revisão matemática independente de T1.
