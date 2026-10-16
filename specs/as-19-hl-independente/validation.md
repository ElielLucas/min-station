# AS19 — Validation

**15/10/2026 — MICRO_VALIDATED (somente exemplo sintético), SEM GO para benchmark/MIP**

| AC | Evidência | Resultado |
|---|---|---|
| AS19-01 | autorização independente documentada | Pass |
| AS19-02 | complement viable -> `NO_CUT`, 1 chamada | Pass |
| AS19-03 | R maior que cap -> `SKIPPED_SIZE`, 0 chamadas | Pass |
| AS19-04 | padrões 16/16, `β=3` racional | Pass |
| AS19-05 | unknown/budget -> `ABSTAIN`, zero corte | Pass |
| AS19-06 | `α=(1/2,1,1,1)`, `β=5/2` | Pass |
| AS19-07 | recompilação de COMP+K e H2: `2,8/3,3` | Pass |
| AS19-08 | JSON com status, hash e custos | Pass |
| AS19-09 | registro sintético isolado, nenhuma conclusão real | Pass |
| AS19-10 | campanha real pré-registrada | Pendente: ainda não realizada |

```bash
python -m unittest discover -s experiments/cuts -p 'test_hl_local.py' -q
python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
python experiments/cuts/run_hl_micro.py --output results/benchmark/as19-hl-micro-k4-002.json
```

A última execução precisa de caminho **novo**: o runner nunca sobrescreve `as19-hl-micro-k4-001.json`.

**Evidência desta entrega:** `results/benchmark/as19-hl-micro-k4-001.json` contém execução local no ambiente Python do ChatGPT com SciPy/HiGHS, 16 chamadas físicas, LP 2, 2.6666666666666665, 3.0. Os tempos registrados são de um único run e não uma comparação estatística nem custos pareados equivalentes aos do AS16. Não havia Gurobi neste ambiente, e ele não foi necessário para este controle sintético. **Revisão matemática independente humana: pendente.**
