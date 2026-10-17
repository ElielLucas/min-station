# AS24 — Design técnico: Separador FC-R e microvalidação

**Spec:** `spec.md`; **Status:** `VALIDATED_WITH_MINOR_FINDINGS` após veredito independente favorável; detalhes menores a acompanhar.

## Architecture Overview

Implementar separação FC-R/FC-R-T comprovadamente válida, completa para regiões unitárias e exata na seleção de Q para cada região fixada, com seleção controlada de regiões maiores e microcasos adversariais.

**Fluxo:** AS23 `VALIDATED` técnico → AS24 separação + microtestes → revisão independente → eventual AS25.

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

**Proveniência:** implementação entregue nesta etapa, com hashes de arquivos e `source_commit` no JSON. O SHA de HEAD não substitui o commit posterior que incluirá os arquivos. AS25 não foi iniciada.

## Limites da implementação

- `separate_fixed` usa a regra ótima de `Q` e não precisa resolver LP auxiliar. `scan` cobre todos os singletons admissíveis quando não censurado, mas somente uma lista heurística de regiões maiores.
- `FCRRow` mantém nomes de arcos `F[u,v]` e ativação `y[v]`; `as_compiled` fornece somente a ponte auditável ao compilador da AS23. Nenhuma mudança foi feita em COMP+K nem no gerador K.
- A violação só gera linha quando excede `tolerance`. Orçamentos de tempo e de linhas, domínio numérico, duplicação e cobertura são registrados. Pontos LP de entrada pressupõem satisfação das restrições de COMP; a AS25 deverá conferir status e factibilidade do solver antes de separar.
- Testes enumeram Q por um avaliador independente e procuram contraexemplos com fluxos adversariais em micrografos, fixando todas as instalações binárias e minimizando cada linha sob COMP.

## Fechamento AS24 (16/10/2026)

Revisão independente favorável, `APPROVED_WITH_MINOR_FINDINGS`, conforme registro em `docs/technical/reference/experimentos/as24-revisao-independente-claude.md`. A implementação e os controles matemáticos não foram alterados neste fechamento. O JSON original é evidência sintética pré-revisão e mantém esse gate histórico; a autorização atual está em `validation.md`. A campanha LP de AS25 exige protocolo congelado e commit/proveniência auditável antes de executar.
