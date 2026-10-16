# AS21 — Validation

| Verificação | Resultado | Alcance |
|---|---|---|
| `python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` com `PYTHONPATH=experiments/cuts` | 148 testes, OK | Snapshot completo com 12 testes AS21 |
| `python experiments/cuts/run_hl_lp_as21.py --output-dir <novo> --dry-run` | `NOT_EXECUTED`, 6 casos, 12 linhas | Hashes e proveniência reais, sem solver |
| Integração K4, LP COMP+K real via SciPy/HiGHS | `2 → 3`; 11 chamadas físicas | Evidência **somente sintética** |
| Teste UNKNOWN e limites | Nenhum corte emitido | Falha fechada / abstenção |
| Determinismo e arquivo existente | Repetição estável; proteção append-only | Contrato de evidência |
| Execução LP nas seis instâncias com Gurobi | **Pendente** | Sem `gurobipy` neste ambiente |
| Revisão científica independente | **Pendente** | Validação automatizada não substitui revisão humana |

## Como repetir

```bash
poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
poetry run python experiments/cuts/run_hl_lp_as21.py \
  --output-dir results/benchmark/as21-hl-lp-001
poetry run python experiments/cuts/analyze_hl_lp_as21.py \
  --as20 results/benchmark/as20-hl-lp-001/analysis.json \
  --as21 results/benchmark/as21-hl-lp-001/analysis.json \
  --output results/benchmark/as21-hl-lp-001/comparison-as20.json
```

Saídas novas, jamais sobrescritas. A AS21 **não** conclui vitória sobre COMP+K sem resultados e revisão; `INVESTIGATE` não equivale a falha de HL.
