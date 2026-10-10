# Comparação formulação base × F-CC+K

Experimento novo e independente da fase N2 (N2-T2B/N2-T3..N2-T6, encerrada com `N2 FAIL`).
Compara a formulação base de Das (`baseline.py`) com F-CC+K **completo** (enumeração total de
`(W,I,J)`, `experiments/alternative-formulations/fcc_k.py`) — não a geração de colunas na raiz da
N2, cujo objetivo de master restrito nunca é um limite inferior certificado.

Metodologia completa, auditoria matemática e limitações:
[`docs/technical/plans/execucao/formulation-comparison-protocolo.md`](../../docs/technical/plans/execucao/formulation-comparison-protocolo.md).

## Arquivos

| Arquivo | Papel |
|---|---|
| `fc_instances.py` | Carrega `instances/manifest.csv`; seleciona lotes `pilot`/`main`/`scalability`; sonda tratabilidade da enumeração F-CC+K |
| `fc_config.py` | `ExperimentConfig` (threads/seed/time limits/checkpoints) e captura de ambiente |
| `fc_core.py` | Modalidades A (LP exato), B (IP exato) e C (evolução); reusa `baseline.py`, `experiments/cuts/harness.py`, `fcc.py`/`fcc_k.py`, `independent_validator.py` |
| `fc_reporting.py` | CSV de resultados/evolução, manifesto de reprodutibilidade |
| `run_comparison.py` | CLI |
| `test_comparison.py` | 23 testes (requer Gurobi) |

## Comandos

```bash
# Piloto (2 instâncias, ≤120s/execução)
PYTHONHASHSEED=0 python run_comparison.py --tier pilot

# Principal (6 instâncias; 3600s/execução de MIP é o default sem --time-limit)
PYTHONHASHSEED=0 python run_comparison.py --tier main --time-limit 3600 --lp-time-limit 600

# Escalabilidade (documenta a fronteira do cap de enumeração de F-CC+K)
PYTHONHASHSEED=0 python run_comparison.py --tier scalability --time-limit 600

# Testes e lint
PYTHONHASHSEED=0 python -m unittest discover -s . -p test_comparison.py -v
python -m ruff check *.py
```

Cada execução cria `results/formulation-comparison/<tier>-<timestamp>/` com `results.csv`,
`evolution.csv`, `manifest.json` (hashes, config, ambiente, comandos, limitações) e `run.log`.
Nenhuma execução sobrescreve outra, altera N1/N2 ou faz commit.

## Rótulos de certificação usados

- `CERTIFIED_LP`: LP exato resolvido até `GRB.OPTIMAL` (Modalidade A).
- `CERTIFIED_MIP_OPTIMAL`: MIP completo com prova de otimalidade (Modalidade B).
- `CERTIFIED_MIP_BOUND`: `ObjBound` de um branch-and-bound **nativo** do Gurobi sobre o modelo já
  fechado (todas as colunas presentes) — diferente do `ObjBound` de um MIP auxiliar de pricing
  sobre um master restrito exponencial, que a N2-T2B trata como não certificável.
- `NOT_MEASURED_CAP_EXCEEDED`: enumeração de `(W,I,J)` acima de `max_W`; nunca um valor aproximado.
- `UNCERTIFIED_NO_INCUMBENT`: `TimeLimit` atingido sem nenhuma solução viável.
