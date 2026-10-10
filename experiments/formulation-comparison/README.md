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
| `fc_evidence.py` | **FC-03:** classificação de evidência numérica, UB físico e recibo opcional de prova racional independente |
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

## Status e proveniência de evidência — FC-03

**Nenhum rótulo `CERTIFIED_*` significa certificação matemática independente.**
No novo schema `FC03-v1` eles foram removidos. `GRB.OPTIMAL` vira
`SOLVER_NUMERIC_OPTIMAL` (sujeito às tolerâncias numéricas). `ObjBound` de um
MIP completo com `TIME_LIMIT` vira `SOLVER_NUMERIC_BOUND` e não vira prova
racional. `ObjBoundC` de pricing/MIP restrito não é limite global físico.

A coluna `certification` agora é `NOT_CERTIFIED` por padrão. Uma prova
externa aceita por um verificador matemático independente, com identificador,
SHA-256 do artefato, instância e contexto compatíveis, pode ser anexada pela
API opt-in `fc_evidence.attach_independent_proof`, mas o runner **não** gera
nem importa provas automaticamente. O ID de contexto **não** é hash da
matriz completa do modelo.

`physical_feasible_ub` é a cardinalidade exata de instalação aceita pelo
validador físico independente. Não derivar UB físico apenas de `ObjVal`.
`certified_gap_status=INCONCLUSIVE` até existir um LB racional verificado e
um UB físico da mesma instância.

Os campos antigos ambíguos `lb_best`, `ub_best`, `gap_abs`, `gap_rel`,
`optimality_proven` e `time_to_proof_s` estão intencionalmente vazios em
`results.csv`; usar as novas colunas `solver_numeric_*`, `rational_*`,
`physical_feasible_ub`, `solver_time_to_optimal_s` e `certified_gap_*`.
Os pontos `evolution.csv` identificam explicitamente `evidence_source` numérica.

`NOT_MEASURED_CAP_EXCEEDED` continua sendo um resultado de interrupção real,
sem objetivo/bound fictício. CSVs históricos anteriores à FC-03 permanecem
inalterados e podem usar rótulos antigos; **não os reinterpretar retroativamente**.

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

## FC-02 — Comparação inteira justa COMP+K × F-CC+K

O par **primário** da Modalidade B agora é:

- `comp_mip`: `harness._make_mip(..., f_type='cont', upfront_cuts=K)`;
  estações `y` binárias, fluxos `f` contínuos, todos os cortes K aplicados.
- `fcc_k`: `fcc_k.build_fcc_plus_k(..., K=K, integer_y=True)`;
  enumeração completa sob cap e o mesmo K.

`baseline` mantém o modelo U legado, **sem K**, e é somente **ablação
opcional**, não mais o controle científico principal.

Cada braço usa seu próprio orçamento FC-01, com os mesmos valores de
`seed`, `threads`, `time_limit_s`, `max_w` e a mesma instância. A ordem dos
dois braços principais alterna entre instâncias. K é produzido e validado
dentro de cada worker, sob o relógio do próprio braço; o hash é confrontado
entre braços **antes** de declarar o par comparável. O hash da instância
é dos bytes reais, confrontado com `sha256` do manifesto. O campo separado
`sha256_conteudo` é validado após remover as linhas `# meta:`: não confundir
essas duas semânticas do manifesto.

`results.csv` acrescenta `comparison_role`, `pair_status`, `pair_reason`,
`k_sha256`, `n_K`, `n_K_added`, `k_validated`, `physical_ub_status`,
`pair_instance_sha256` e `pair_k_sha256`.

- `PAIR_VALID`: instância e K idênticos, cortes íntegros e incumbentes,
  quando existentes, fisicamente validados pelo oráculo independente. **Não**
  significa valores racionalmente certificados nem otimalidade dos braços.
- `PAIR_NOT_AVAILABLE`: braço ausente, timeout, cap, erro ou status sem
  evidência suficiente. Os valores não são inferidos.
- `INTEGRITY_ERROR`: hashes diferentes, cortes não validados/aplicados ou
  falha explícita de integridade dos cortes.
- `INVALID_PHYSICAL_WITNESS`: pelo menos uma incumbente não foi validada.
- `ABLATION_ONLY`: linha do baseline sem K, fora do par primário.

Os rótulos `CERTIFIED_LP`, `CERTIFIED_MIP_OPTIMAL` e `CERTIFIED_MIP_BOUND`
são legados da FC-01/FC-02 e não são mais publicados. O contrato normativo
novo está na seção **Status e proveniência de evidência — FC-03** acima.

```bash
# Par principal, sem ablação
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --time-limit 120 --lp-time-limit 60

# Par principal + ablação sem K (três braços MIP)
PYTHONHASHSEED=0 python experiments/formulation-comparison/run_comparison.py \
  --tier pilot --modalities A,B --formulations comp_mip,fcc_k,baseline \
  --time-limit 120 --lp-time-limit 60

# Testes independentes de Gurobi
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_fc02_*.py' -v

# Suíte integral — requer licença Gurobi
PYTHONHASHSEED=0 python -m unittest discover \
  -s experiments/formulation-comparison -p 'test_*.py' -v
```

A FC-02 **não altera** `baseline.py`, `harness.py`, `fcc.py`, `fcc_k.py`,
certificadores ou resultados congelados de N1/N2.
