# AS16 — Piloto LP pareado COMP, K e H2 — Design

**Spec:** `specs/as-16-piloto-lp-h2/spec.md`  
**Status:** Draft — decisões pendentes de aprovação e verificação local na execução.

## Architecture Overview

Runner usa `compile_u` de `experiments/alternative-formulations/as02_model_a.py` e pipeline de validação/planos de `experiments/formulation-comparison` e `run_as09_extended.py` apenas onde compatíveis. K congelado sem C3 iterativo. Informar que ganho do LP puro pode não persistir após cortes do solver. Pool fixo: gerar uma coleção de H2 certificada comum e aplicá-la em comparações controladas; não usar cortes obtidos com informação do conjunto de avaliação para ajustar a heurística.

```mermaid
flowchart TD
    A[Entradas e invariantes] --> B[Etapa AS16]
    B --> C[Testes derivados dos ACs]
    C --> D{Gate cientifico}
    D -->|GO| E[Prosseguir apenas conforme dependencias]
    D -->|STOP ou inconclusivo| F[Registrar evidencias e nao promover]
```

## Code Reuse Analysis

| Artefato existente | Papel | Cuidado |
|---|---|---|
| `experiments/alternative-formulations/as02_model_a.py` | Controle COMP/U e K do comparador | Confirmar builder e política de relaxação/MIP no checkout usado. |
| `experiments/cuts/cuts.py` | C1/C2/C4-DM, ordenação de suportes, possíveis validadores existentes | Não trocar K existente, nem confundir C4-DM com todo Hall multissalto. |
| `docs/technical/plans/execucao/as00-benchmark-protocolo.md` | Seleção de desenvolvimento/avaliação e orçamento | Preservar provenance e grupos de grafos brutos. |
| `docs/technical/reference/baseline-e-metodo/protocolo-comparacao-pareada.md` | Isolar variáveis e orçamento comparável | Não misturar WorkLimit e TimeLimit. |

**Fontes para conferir no Execute (codebase primeiro):** `CLAUDE.md`, `docs/project-overview.md`, `RESEARCH.md`, `docs/context-ai/min-station-domain.md`, `docs/context-ai/base-formulation.md`, `experiments/alternative-formulations/as02_model_a.py`, `experiments/cuts/cuts.py`, `docs/technical/plans/execucao/as00-benchmark-protocolo.md`, `docs/technical/reference/baseline-e-metodo/protocolo-comparacao-pareada.md`.

## Components

| Entregável | Local proposto | Interface/comportamento esperado |
|---|---|---|
| Congelar plano e hashes dos seis casos AS-00 | `docs/technical/plans/execucao/as16-preregistro-lp-h2.md` (proposto) | Manifesto, thresholds, seeds e orçamento definidos antes de qualquer solve. |
| Implementar runner LP de braços pareados | `experiments/cuts/run_h2_lp.py` (proposto) | Quatro braços e relógio de parede absoluto por braço. |
| Implementar relatório de força, custo e pool fixo | `experiments/cuts/analyze_h2_lp.py` (proposto) | Dados censurados preservados; decomposição e atribuição corretas. |
| Produzir relatório e decisão auditável | `docs/technical/reference/experimentos/as16-resultado-lp-h2.md` (proposto) | GO/STOP/INVESTIGATE baseado em artefatos e thresholds pré-registrados. |

## Data Models

Todo registro experimental/certificado desta etapa terá: `schema_version`, `instance_sha256`, `source_commit`, `stage`, `status`, `elapsed_wall_s`, `evidence_path`, `budget_s`, `cut_family`, `cut_hash`, `validator_identity` quando aplicável. Para H2 usar suporte canônico `R`, conjuntos certificados `Bhat`, coeficientes 1/2 e RHS 2; para HL usar `R`, coeficientes racionais e β certificado. Campos inaplicáveis devem ser omitidos, não inventados.

## Error Handling Strategy

| Evento | Tratamento |
|---|---|
| Oráculo desconhecido, timeout ou erro | UNKNOWN/abstenção; jamais inferir inviabilidade. |
| Prova contradita | UNPROVEN/STOP; nenhuma emissão de corte dependente. |
| Sem suporte violado | NO_CUT, não confundir com inexistência global de corte. |
| Resultado LP/MIP censurado | Preservar métrica indisponível como ausente e motivo explícito. |
| Instância ou corte com SHA incompatível | INVALID_INPUT e bloquear comparação. |

## Risks & Concerns

| Risco | Impacto | Mitigação |
|---|---|---|
| Matching anônimo confundido com pareamento fixo | Corte inválido | Testes independentes com múltiplos matchings e S∩T. |
| Deficiência de Hall confundida com quantidade de estações | RHS incorreto | Certificar escolhas de instalações distintas; nunca usar déficit diretamente. |
| Heurística de suportes confundida com certificação | Desigualdade insegura | Separar seleção de R e prova da linha contra F=V\R. |
| Aumento do LB puro sem ganho após raiz MIP | Regressão de desempenho | Comparar bound após cuts do solver e tempo de separação. |
| Repetir K, CG/zero-half, CBI, C6 ou limite global | Contribuição redundante | Anotar controles históricos e medir ganho marginal. |

## Tech Decisions

- Usar esta etapa como pesquisa experimental **separada**: não trocar a formulação de produção nem alterar os freezes.
- Derivar testes dos ACs e executar verificador independente após implementação.
- Cada gate pode terminar com resultado negativo auditável; nenhuma etapa posterior começa automaticamente em caso de STOP.
- As políticas específicas de AS16 constam no `spec.md` e em `tasks.md`.

## Acceptance Gate

GO somente com ≥1% de melhoria de LB em ≥2 grafos brutos independentes e evidência de custo líquido aceitável em ≥1; senão STOP; INVESTIGATE por erros/censura inconclusiva.
