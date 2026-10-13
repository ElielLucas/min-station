# AS18 — HL condicional e síntese científica dos novos cortes — Design

**Spec:** `specs/as-18-hl-condicional-e-sintese/spec.md`  
**Status:** Draft — decisões pendentes de aprovação e verificação local na execução.

## Architecture Overview

Se HL for autorizado, explorar somente suporte pequeno R onde ν(V\R)<m e H2 deixa fração residual. Enumerar Φ_R ou usar oracle exato para β, nunca usar amostra incompleta como conjunto final. Linha de cardinalidade 3 pode ser certificada provando inviabilidade de cardinalidades 0,1,2 com 1+k+C(k,2) chamadas; experimentar isso antes do casco geral.

```mermaid
flowchart TD
    A[Entradas e invariantes] --> B[Etapa AS18]
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
| Formalizar autorização e política local de HL | `docs/technical/plans/execucao/as18-gate-hl.md` (proposto) | Decisão documentada antes de enumerar padrões. |
| Implementar enumeração local e β exato | `experiments/cuts/hl_local.py` (proposto) | Padrões totais/UNKNOWN conservador e certificados racionais. |
| Implementar microteste e triagem incremental LP | `experiments/cuts/test_hl_local.py` (proposto) | Hierarquia K–H2–HL reproduzida e margem de custo medida. |
| Publicar síntese científica e próxima decisão | `docs/technical/reference/experimentos/as18-sintese-h2-hl.md` (proposto) | Resultados próprios, limites e literatura diferenciados, incluindo STOP. |

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
- As políticas específicas de AS18 constam no `spec.md` e em `tasks.md`.

## Acceptance Gate

GO de HL apenas com melhoria marginal certificada e custo justificado; caso negativo registrar STOP. Síntese final obrigatória mesmo se HL não autorizado.
