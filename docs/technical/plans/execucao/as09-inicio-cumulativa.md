# AS-09 — Plano curto de execução

1. **T1/T2:** instalar o protótipo, rodar testes numéricos e revisar a prova da projeção. Enquanto não houver parecer independente, marcar `PROOF_REVIEW_REQUIRED`.
2. **Triagem:** executar `run_as09_screen.py` com `results/benchmark/as09-screen-001` (ou nova pasta). Isso usa somente metadados de manifesto e produz contagens de variáveis/linhas teóricas, **sem K nem solver**.
3. **Selecionar as instâncias reais:** Vienna I056 e MAPF den312d como casos com maior potencial de economia de variáveis; PUC cc9 como controle negativo. Mapf-room como caso intermediário opcional.
4. **T3 (runner implementado, execução Gurobi pendente):** usar Gurobi em protocolos pareados com U e C, nos regimes sem K e com K. Medir tempo global (input + A_r + K + modelo + solver), nvars/nconstr/nnz realmente instalados, RSS por processo, resultados LP, limites e timeouts. Tratar excesso de memória e censura sem imputação.
5. **T4:** só decidir se C vale MIP quando a revisão LP e a medição de custo total justificarem. Não alegar melhoria do limite LP por contagem de variáveis.

Comandos do protótipo em raiz do repositório:

```bash
PYTHONPATH=. poetry run python -m unittest discover -s experiments/alternative-formulations -p 'test_as09_*.py' -v
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_screen.py --output-dir results/benchmark/as09-screen-001
PYTHONPATH=. poetry run python experiments/alternative-formulations/run_as09_pilot.py --init-plan --plan results/benchmark/as09-c-plan-v1.json --budget 300
```

A tela emitirá `SCREEN_ONLY_NO_SCIENTIFIC_PROMOTION` no JSON; isso é intencional. Não criar campanha MIP antes de T3/T4.
