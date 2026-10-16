# AS20 — Validation

| Verificação | Resultado | Escopo |
|---|---|---|
| `python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` | **136 testes OK** | Snapshot AS18+AS19+AS20 reconstruído, inclui evidências AS16 |
| `python experiments/cuts/run_hl_lp.py --output-dir /tmp/as20-hl-dry-run-002 --dry-run` | `NOT_EXECUTED`, 12 linhas | Verifica seis fontes reais e integridade; **sem LP** |
| Teste K4 com proposta automática | LP `2 → 3`, corte HL certificado | Apenas testemunha sintética |
| Execução Gurobi real AS20 | **Executada pelo pesquisador**; 6 casos, 12 braços, `INVESTIGATE` | Evidência em `results/benchmark/as20-hl-lp-001/` |
| Revisão matemática humana independente | Pendente | Não substituída por testes |

## Pendências para completar a tarefa

1. ~~Executar a campanha LP com Gurobi e coletar evidências.~~ Concluído, 15/10/2026.
2. ~~Avaliar `analysis.json`, verificando tempos, censuras, provas e ganhos.~~ Concluído, gate `INVESTIGATE`.
3. ~~Atualizar relatório e definir continuação.~~ AS21 autorizada para investigar certificação e suportes, sem coeficientes não unitários.
4. Revisão científica independente continua pendente.

**Importante:** `NO_GAIN_IN_BOUNDED_SCREEN` limita-se aos pequenos suportes K e `α=1`. Não é demonstração de dominância matemática sobre HL nem justificativa automática para encerrar toda a família.
