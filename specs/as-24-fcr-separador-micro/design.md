# AS24 — Design técnico: Separador FC-R e microvalidação

**Spec:** `spec.md`; **Status:** Proposed — depende de gate anterior.

## Architecture Overview

Implementar separação FC-R/FC-R-T comprovadamente válida, completa para regiões unitárias e exata na seleção de Q para cada região fixada, com seleção controlada de regiões maiores e microcasos adversariais.

**Fluxo:** AS23 `VALIDATED` e documento de prova com hipóteses resolvidas.

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
| Constituidor de linhas FC-R | `experiments/cuts/fcr_rows.py` | Representa termos de fluxo e ativação e valida exclusões de terminais. |
| Separador L/Q | `experiments/cuts/fcr_separator.py` | Seleciona Q por regra fechada, orientações e violação. |
| Seletor regional | `experiments/cuts/fcr_regions.py` | Enumera singletons, propõe regiões maiores limitadas. |
| Validação micro | `experiments/cuts/test_as24_fcr.py` | Testes de validade, enumeração Q, determinismo, tolerâncias, casos adversariais. |

## Data Models e evidências

- Entradas: hash do grafo físico e do dígrafo `H`, conjuntos `S/T`, autonomia e configuração de solver versionada.
- Saídas experimentais: JSON determinístico com `status`, `schema_version`, `source_commit`, identidade de instância, parâmetros, linhas/certificados, contagens, tempos e razões de abstenção.
- Cada resultado produzido deve indicar se é prova algébrica, microcaso, execução LP/MIP real, resultado censurado ou hipótese externa.
- Não sobrescrever resultados AS16–AS22 nem tratar verificador independente como sinônimo de execução do autor.

## Error Handling Strategy

Falhas de solver, entradas sem solução LP, tempo esgotado ou L fora de escopo geram abstenção explícita com razão. Nunca promover `UNKNOWN` a ausência de violação.

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Fluxos fracionários e ruído | Violações falsas por tolerâncias | Usar tolerância preregistrada e checagem de coeficientes/balanço. |
| Seleção de regiões | Heurística pode não encontrar cortes que existem | Reportar alcance exato unitário versus seleção parcial de L maiores. |
| Terminais | Cabeça/cauda isentas podem invalidar linhas | Verificações estáticas de Q e testes S∩T. |
| Custo de LP | Linhas densas e múltiplas reotimizações | Caps, contagem de não zeros, tempo total por braço na AS25. |

## Tech Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Separação unitária | Cobertura completa de L={v} com saldo não zero | Custo linear por fronteira na rodada, conforme hipótese do parecer. |
| Regiões maiores | Heurística determinística, separação exata somente em Q | Não alegar ótimo global de L. |

## Critério de entrada na execução

Separador não emite corte inválido; decisão `VALIDATED` depende de concordância exata na escolha de Q em microcasos, cobertura total declarada dos singletons e testes adversariais completos.

**Proveniência:** decisões ainda propostas; nenhuma implementação realizada como parte desta entrega documental.
