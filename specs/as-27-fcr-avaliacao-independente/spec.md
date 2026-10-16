# AS27 — Avaliação independente e generalização FC-R — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** somente planejado, não implementado nem validado. **Branch de referência:** `novos_testes`. **Pré-condição:** AS26 concluída e política aprovada/fixa; disponibilidade de split reservado com IDs de grafos originais.

## Problem Statement

Avaliar generalização em grafos reservados sem vazamento depois de política e parâmetros congelados e decisão científica favorável nas fases anteriores.

## Goals

- [ ] Avaliar generalização em grafos reservados sem vazamento depois de política e parâmetros congelados e decisão científica favorável nas fases anteriores.
- [ ] Gate e evidências rastreáveis: Etapa condicional e não autorizada; requer AS26 com aprovação e política congelada. Nenhum resultado reservado nesta entrega.

## Out of Scope

| Item | Razão |
|---|---|
| Busca/tuning de parâmetros sobre reserva | Vazamento metodológico. |
| Redefinição do corte após resultados reservados | Seria uma nova pesquisa, não validação independente. |
| Alegar novidade bibliográfica sem auditoria | Requer outra evidência. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Split | Utilizar a partição por grafo bruto que já consta no protocolo benchmark-v1 | Protege independência entre desenvolvimento e teste. | Não; premissa de planejamento |
| Execução | Nenhum parâmetro pode ser alterado após revelar resultados reservados | Evita overfitting. | Não; premissa de planejamento |
| Gate | Prosseguir apenas com autorização e protocolo congelado | Reserva não deve virar continuação exploratória. | Não; premissa de planejamento |

**Open questions:** none — as escolhas não confirmadas são premissas explícitas acima; antes da execução, revalidar alterações de escopo e gates.

## User Stories

### P1: Avaliar sem vazamento

**User Story:** Como pesquisador, quero testar o método em grafos reservados para medir robustez externa.

**Acceptance Criteria**

1. WHEN a avaliação reservada começar THEN the runner SHALL confirmar IDs e hashes sem sobreposição de grafo bruto com o conjunto de desenvolvimento.
2. IF a política FC-R não estiver congelada ou autorização ausente THEN the runner SHALL impedir acesso aos resultados reservados.
3. WHEN a campanha reservada terminar THEN the relatório SHALL registrar todos os pares e censuras, sem mudar parâmetros.

**Independent Test:** Verificar interseção vazia de raw_graph_id e falha em caso de edição de política.

### P2: Conclusão reprodutível

**User Story:** Como pesquisador, quero identificar generalização versus instância isolada para avaliar contribuição científica.

**Acceptance Criteria**

1. WHEN o relatório final for produzido THEN the sistema SHALL distinguir efeito médio, variação por família, censuras e custo de separação para LP e MIP conforme disponível.

**Independent Test:** Auditoria com manifesto congelado e resultados imutáveis.

## Edge Cases

- IF houver erro, censura ou evidência incompleta THEN the sistema SHALL registrar a razão e não atribuir resultado positivo à fase.
- IF a pré-condição não estiver satisfeita THEN the sistema SHALL bloquear a execução de AS27.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR27-01 | Avaliar sem vazamento | Tasks | Pending |
| FCR27-02 | Avaliar sem vazamento | Tasks | Pending |
| FCR27-03 | Avaliar sem vazamento | Tasks | Pending |
| FCR27-04 | Conclusão reprodutível | Tasks | Pending |

**Coverage:** 4 requisitos rastreáveis; tarefas detalhadas em `tasks.md`; 0 implementados.

## Success Criteria

- [ ] Manifesto de divisão sem sobreposição por grafo bruto.
- [ ] Resultados imutáveis e política congelada, sem uso de reserva para ajustes.
- [ ] Relatório com generalização e censuras explícitas.

## Dependências e gate

Etapa condicional e não autorizada; requer AS26 com aprovação e política congelada. Nenhum resultado reservado nesta entrega.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.
