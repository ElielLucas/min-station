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
| `fc_budget.py` | **FC-01:** relógio monotônico, deadlines globais e processos `spawn` interrompíveis |
| `fc_config.py` | `ExperimentConfig` (threads/seed/time limits/checkpoints) e captura de ambiente |
| `fc_core.py` | Modalidades A (LP exato), B (IP exato) e C (evolução); reusa `baseline.py`, `experiments/cuts/harness.py`, `fcc.py`/`fcc_k.py`, `independent_validator.py` |
| `fc_reporting.py` | CSV de resultados/evolução, manifesto de reprodutibilidade |
| `run_comparison.py` | CLI |
| `test_comparison.py` | Testes integrados (requer Gurobi) |
| `test_fc01_budget.py` | Testes de timeout, fases, cap e falha, independentes de Gurobi |

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

## FC-01 — Orçamento global real

**Atualização experimental; não altera N1/N2.** Cada braço LP (base, COMP e
F-CC+K) tem `lp_time_limit_s` próprio; cada braço MIP (base, F-CC+K) tem
`time_limit_s` próprio. Cada prazo começa **antes da preparação** do braço:
spawn, geração de cortes K (quando aplicável), enumeração de configurações,
montagem, solve e validação física contam no mesmo teto.

As chamadas `Model.Params.TimeLimit` recebem o **restante efetivo** após
montagem, com reserva para fechamento/validação. Um supervisor em processo
separado interrompe Python durante enumeração que não verifica deadlines.
O término excede eventualmente o teto por alguns milissegundos de
escalonamento/terminação do SO; o excesso não é escondido.

`results.csv` conserva `time_s` (agora wall ponta a ponta), acrescenta
`wall_total_s`, `solver_runtime_s`, `wall_phases_json`, colunas `wall_*_s`,
`stop_reason`, e Work Gurobi também para os LPs.

- `CAP_EXCEEDED`, `TIMEOUT_PREPARATION`, `TIMEOUT_SOLVER`,
  `TIMEOUT_VALIDATION`, `SOLVER_UNAVAILABLE`, `WORKER_ERROR`: sem valor
  ótimo falso, com razão da parada e wall time observado.
- `TIME_LIMIT` com resultado do Gurobi: pode preservar incumbente/bound
  numérico, sujeito às ressalvas da próxima spec FC-03.
- Se o deadline externo matar o processo durante o solve, **nenhum valor
  parcial que não tenha sido reportado é publicado**. Não extrapolar dados.
- `ru_maxrss` passa a ser o pico acumulado de **cada worker independente**;
  falhas sem observação de memória usam vazio, não zero inventado.
- `time_to_first_feasible_s`, `time_to_best_s`, evolução e tempo de prova
  são tempos a partir do início do braço; `solver_runtime_s` é apenas solver.

**Testes rápidos sem licença Gurobi:**

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_fc01_budget.py' -v
```

**Aceite com Gurobi real no ambiente do projeto:**

```bash
PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v
python -m ruff check experiments/formulation-comparison
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --time-limit 120 --lp-time-limit 60
```

Não execute o lote completo de 3.600s antes do gate FC-05. FC-01 corrige
contabilização e interrupção; não redefine prova racional nem comparação
COMP inteiro × F-CC+K (tarefas FC-03/FC-02).
