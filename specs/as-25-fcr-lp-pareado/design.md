# AS25 — Design técnico: Piloto LP pareado FC-R versus COMP+K

**Spec:** `spec.md`; **Status:** Runner/analisador implementados; real LP e revisão independente pendentes.

## Architecture Overview

Medir de forma preregistrada a contribuição marginal de FC-R em seis grafos de desenvolvimento com quatro braços e análise separada de regiões unitárias e maiores.

**Fluxo:** AS24 `VALIDATED` e política FC-R congelada antes da campanha; não reutilizar grafos reservados.

## Code Reuse Analysis

| Artefato atual | Reuso permitido |
|---|---|
| `experiments/alternative-formulations/as02_model_a.py` | Compilação de COMP e variáveis contínuas de fluxo. |
| `experiments/cuts/cuts.py` | Geradores K (C1/C2/C4-DM), sem mudanças no baseline. |
| `experiments/cuts/run_hl_lp_as22.py` | Convenções de orçamento, hashes e telemetria experimental. |
| `experiments/cuts/test_as22_hl_poly.py` | Padrões de testes de cortes e uso do compilador. |
| `docs/technical/reference/baseline-e-metodo/protocolo-comparacao-pareada.md` | Princípios de comparabilidade e censura. |

## Components

| Componente | Local | Contrato pretendido |
|---|---|---|
| Pré-registro | `docs/technical/plans/execucao/as25-preregistro-fcr-lp.md` | Amostra, versões, métricas, parâmetros, ablações, orçamento e gate. |
| Runner de quatro braços | `experiments/cuts/run_fcr_lp_as25.py` | Compila COMP/COMP+K sem mexer nos métodos originais e adiciona FC-R como módulo experimental. |
| Analisador pareado | `experiments/cuts/analyze_fcr_lp_as25.py` | Compara ganhos/custos, contabiliza grafos independentes, censuras e ablações. |
| Relatório | `docs/technical/reference/experimentos/as25-resultado-lp-fcr.md` | Conclusão reprodutível com fontes imutáveis. |

## Data Models e evidências

- Entradas: hash do grafo físico e do dígrafo `H`, conjuntos `S/T`, autonomia e configuração de solver versionada.
- Saídas experimentais: JSON determinístico com `status`, `schema_version`, `source_commit`, identidade de instância, parâmetros, linhas/certificados, contagens, tempos e razões de abstenção.
- Cada resultado produzido deve indicar se é prova algébrica, microcaso, execução LP/MIP real, resultado censurado ou hipótese externa.
- Não sobrescrever resultados AS16–AS22 nem tratar verificador independente como sinônimo de execução do autor.

## Error Handling Strategy

Licença Gurobi ausente, caso faltante, seed alterada, hash incorreto ou orçamento expirado devem ser registrados com estado não-ótimo; nunca forçar `OPTIMAL` no relatório.

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Censura | Confundir TIME_LIMIT com solução ótima | Pareamento somente entre braços com LP ótimo; manter censuras. |
| Dependência bruta | Seis casos podem representar menos grafos independentes | Usar raw_graph_id e contar unicamente. |
| Tempo de reotimização | Separação rápida não garante execução rápida | Parede total por braço, RAM, NNZ e custos detalhados. |
| Ganho aparente | Mudança de fluxos sem ganho de bound | Comparar objetivos e não quantidade de cortes apenas. |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Quatro braços | U, U_K, U_FCR, U_K_FCR | Isola complementaridade a K. |
| Congelamento | Novo manifesto preregistrado, sem sobrescrever campanhas antigas | Reprodutibilidade e prevenção de tuning retrospectivo. |

## Critério de entrada na execução

`GO_CANDIDATE_REVIEW` somente se ganho LP ≥1% em ≥2 grafos brutos independentes e custo parede total ≤2× controle nesses pares, cobertura auditável e revisão posterior. Censuras impedem inferência de ausência universal de ganho.

**Proveniência:** plano congelado no AS25 JSON e componentes implementados; sem executar campanha real. A implementação usa índice de fronteira e o construtor canônico de linhas AS24, cobrindo 2 rodadas delimitadas e ablação em campanha isolada.
