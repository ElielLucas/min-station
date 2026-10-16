# AS26 — Design técnico: Piloto MIP condicional de FC-R

**Spec:** `spec.md`; **Status:** Proposed — depende de gate anterior.

## Architecture Overview

Determinar se o benefício LP de FC-R sobrevive à presolve/cortes automáticos e melhora busca exata, somente após autorização científica baseada na AS25.

**Fluxo:** AS25 com evidência suficiente e aprovação científica explícita documentada; caso contrário AS26 permanece bloqueada.

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
| Protocolo de MIP | `docs/technical/plans/execucao/as26-preregistro-fcr-mip.md` | Define gates, orçamento, callbacks/métricas e validação física. |
| Runner condicionado | `experiments/cuts/run_fcr_mip_as26.py` | Guard e execução pareada, sem alterar scripts históricos. |
| Relatório | `docs/technical/reference/experimentos/as26-resultado-mip-fcr.md` | Conserva tempos, nós, gap, valor primal físico e conclusão. |

## Data Models e evidências

- Entradas: hash do grafo físico e do dígrafo `H`, conjuntos `S/T`, autonomia e configuração de solver versionada.
- Saídas experimentais: JSON determinístico com `status`, `schema_version`, `source_commit`, identidade de instância, parâmetros, linhas/certificados, contagens, tempos e razões de abstenção.
- Cada resultado produzido deve indicar se é prova algébrica, microcaso, execução LP/MIP real, resultado censurado ou hipótese externa.
- Não sobrescrever resultados AS16–AS22 nem tratar verificador independente como sinônimo de execução do autor.

## Error Handling Strategy

Sem licença, parâmetros divergentes, incumbent inválida, timeout ou falha de memória geram evidência censurada; nunca remover pares difíceis da amostra.

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Automatismo indevido | Runner pode disparar MIP sem GO científico | Guard de autorização obrigatório e teste negativo. |
| Cortes nativos do Gurobi | Podem absorver melhoria LP | Instrumentar raiz antes/depois de cortes nativos. |
| Censuras e aleatoriedade | Medições MIP variam | Orçamento e parâmetros pareados, reporting conservador. |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Autorização | Flag disabled por padrão e aprovação escrita | Não tratar LP como permissão MIP. |
| Objetivo | Melhorar prova inteira, não apenas LP | Métricas raiz, nós, dual bound e tempo com custo total. |

## Critério de entrada na execução

Somente executar se AS25 tiver sido analisada com decisão científica humana formal; nenhum `GO_CANDIDATE_REVIEW` é autorização automática. Status inicial `BLOCKED_BY_GATE`.

**Proveniência:** decisões ainda propostas; nenhuma implementação realizada como parte desta entrega documental.
