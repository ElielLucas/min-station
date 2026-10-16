# AS26 — Piloto MIP condicional de FC-R — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** somente planejado, não implementado nem validado. **Branch de referência:** `novos_testes`. **Pré-condição:** AS25 com evidência suficiente e aprovação científica explícita documentada; caso contrário AS26 permanece bloqueada.

## Problem Statement

Determinar se o benefício LP de FC-R sobrevive à presolve/cortes automáticos e melhora busca exata, somente após autorização científica baseada na AS25.

## Goals

- [ ] Determinar se o benefício LP de FC-R sobrevive à presolve/cortes automáticos e melhora busca exata, somente após autorização científica baseada na AS25.
- [ ] Gate e evidências rastreáveis: Somente executar se AS25 tiver sido analisada com decisão científica humana formal; nenhum `GO_CANDIDATE_REVIEW` é autorização automática. Status inicial `BLOCKED_BY_GATE`.

## Out of Scope

| Item | Razão |
|---|---|
| MIP automático após `GO_CANDIDATE_REVIEW` | O gate é apenas sinal para revisão. |
| Benchmark independente | AS27 reservado, posterior. |
| Alterar validade do problema | O modelo físico de Das permanece. |
| Tuning pós-hoc para favorecer FC-R | Parâmetros precisam ser congelados. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Ativação | A etapa começa com flag disabled e documento de aprovação obrigatório | Restringe autorizações implícitas. | Não; premissa de planejamento |
| Comparação | Manter COMP+K e COMP+K+FC-R com orçamento pareado e configuração fixa | Efeito marginal de FC-R. | Não; premissa de planejamento |
| Cortes automáticos | Medições na raiz antes e depois de cuts e ramo inteiro | Permite detectar redundância com cortes do solver. | Não; premissa de planejamento |
| Metas | Não transportar gate LP como gate MIP; definir quantitativos antes de executar | Melhora LP não implica melhora do MIP. | Não; premissa de planejamento |

**Open questions:** none — as escolhas não confirmadas são premissas explícitas acima; antes da execução, revalidar alterações de escopo e gates.

## User Stories

### P1: Execução condicional segura

**User Story:** Como pesquisador, quero impedir execução MIP não autorizada para preservar decisões científicas.

**Acceptance Criteria**

1. IF a autorização pós-AS25 estiver ausente THEN the runner SHALL bloquear execução MIP e registrar motivo verificável.
2. WHEN houver autorização válida THEN the runner SHALL carregar os mesmos casos de desenvolvimento e orçamento pareado congelado.

**Independent Test:** Testar bloqueio mesmo com artefatos presentes mas sem autorização.

### P1: Medir contribuição após solver

**User Story:** Como pesquisador, quero comparar FC-R na árvore para não concluir apenas por bound LP.

**Acceptance Criteria**

1. WHEN a execução alcançar a raiz THEN the sistema SHALL registrar limites antes e depois dos cortes automáticos com estados observáveis.
2. WHEN a execução MIP terminar THEN the sistema SHALL medir melhor limite dual, incumbente fisicamente validada, gap, nós, tempo até primeira solução/prova e memória.
3. IF houver falha de incumbente física THEN the analisador SHALL impedir classificação positiva do piloto.

**Independent Test:** Validar colunas e statuses em microcasos e simulação de censura.

### P2: Avaliar continuidade

**User Story:** Como pesquisador, quero julgar se o custo adicional compensa para evitar promoção precipitada.

**Acceptance Criteria**

1. WHEN o relatório MIP for compilado THEN the sistema SHALL distinguir ganhos em raiz, árvore e tempo total, com todos os pares censurados preservados.

**Independent Test:** Revisão do relatório contra JSON brutos e parâmetros congelados.

## Edge Cases

- IF houver erro, censura ou evidência incompleta THEN the sistema SHALL registrar a razão e não atribuir resultado positivo à fase.
- IF a pré-condição não estiver satisfeita THEN the sistema SHALL bloquear a execução de AS26.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR26-01 | Execução condicional segura | Tasks | Pending |
| FCR26-02 | Execução condicional segura | Tasks | Pending |
| FCR26-03 | Medir contribuição após solver | Tasks | Pending |
| FCR26-04 | Medir contribuição após solver | Tasks | Pending |
| FCR26-05 | Medir contribuição após solver | Tasks | Pending |
| FCR26-06 | Avaliar continuidade | Tasks | Pending |

**Coverage:** 6 requisitos rastreáveis; tarefas detalhadas em `tasks.md`; 0 implementados.

## Success Criteria

- [ ] Guard nega execução sem aprovação científica.
- [ ] Métricas raiz, nós, incumbentes e tempos são rastreáveis a execuções reais.
- [ ] Relatório distingue melhoria teórica de ganho computacional em MIP.

## Dependências e gate

Somente executar se AS25 tiver sido analisada com decisão científica humana formal; nenhum `GO_CANDIDATE_REVIEW` é autorização automática. Status inicial `BLOCKED_BY_GATE`.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.
