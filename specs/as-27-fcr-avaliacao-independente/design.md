# AS27 — Design técnico: Avaliação independente e generalização FC-R

**Spec:** `spec.md`; **Status:** Proposed — depende de gate anterior.

## Architecture Overview

Avaliar generalização em grafos reservados sem vazamento depois de política e parâmetros congelados e decisão científica favorável nas fases anteriores.

**Fluxo:** AS26 concluída e política aprovada/fixa; disponibilidade de split reservado com IDs de grafos originais.

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
| Plano de avaliação | `docs/technical/plans/execucao/as27-preregistro-fcr-avaliacao.md` | Escopo, split, hashes, congelamento, métricas. |
| Verificador de split | `experiments/cuts/verify_fcr_reserved_split.py` | Confere ausência de vazamento e manifesta a política. |
| Relatório | `docs/technical/reference/experimentos/as27-avaliacao-independente-fcr.md` | Resultados globais e por família com censuras. |

## Data Models e evidências

- Entradas: hash do grafo físico e do dígrafo `H`, conjuntos `S/T`, autonomia e configuração de solver versionada.
- Saídas experimentais: JSON determinístico com `status`, `schema_version`, `source_commit`, identidade de instância, parâmetros, linhas/certificados, contagens, tempos e razões de abstenção.
- Cada resultado produzido deve indicar se é prova algébrica, microcaso, execução LP/MIP real, resultado censurado ou hipótese externa.
- Não sobrescrever resultados AS16–AS22 nem tratar verificador independente como sinônimo de execução do autor.

## Error Handling Strategy

Diferença de hashes, interseção de raw IDs ou tentativa de mudar política aborta a rodada sem entregar performance reservada.

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Vazamento | Reutilização de instâncias de desenvolvimento | Validação programática de raw_graph_id e provenance. |
| Tuning | Ajustar caps após resultados pode invalidar teste | Snapshot da política com hash e bloqueio. |
| Censura | Excluir difíceis superestima benefício | Persistir e analisar todos os casos. |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Avaliação reservada | Só depois de política FC-R congelada e decisão científica | Preserva independência metodológica. |

## Critério de entrada na execução

Etapa condicional e não autorizada; requer AS26 com aprovação e política congelada. Nenhum resultado reservado nesta entrega.

**Proveniência:** decisões ainda propostas; nenhuma implementação realizada como parte desta entrega documental.
