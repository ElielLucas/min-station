# AS24 — Separador FC-R e microvalidação — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** `VALIDATED_WITH_MINOR_FINDINGS` após parecer favorável `APPROVED_WITH_MINOR_FINDINGS`; detalhes dos achados menores ainda não fornecidos. **Branch de referência:** `novos_testes`. **Pré-condição:** AS23 tecnicamente `VALIDATED` conforme `specs/as-23-fcr-revisao-matematica/validation.md`; proveniência final do commit é responsabilidade do checkout local.

## Problem Statement

Implementar separação FC-R/FC-R-T comprovadamente válida, completa para regiões unitárias e exata na seleção de Q para cada região fixada, com seleção controlada de regiões maiores e microcasos adversariais.

## Goals

- [x] Implementar separação FC-R/FC-R-T comprovadamente válida, completa para regiões unitárias e exata na seleção de Q para cada região fixada, com seleção controlada de regiões maiores e microcasos adversariais.
- [x] Gate e evidências rastreáveis: Separador não emite corte inválido; decisão `VALIDATED` depende de concordância exata na escolha de Q em microcasos, cobertura total declarada dos singletons e testes adversariais completos.

## Out of Scope

| Item | Razão |
|---|---|
| Separador ótimo sobre todas as regiões L | Parecer não prova separação global polinomial. |
| Campanha LP real | Pertence à AS25. |
| Mudança no compilador ou reescrita de K | Não necessária para linha experimental aditiva. |
| MIP | Só AS26 com gate. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Regiões exatas | Incluir todas as regiões unitárias admissíveis; regiões maiores formam lista heurística parametrizada | Promove cobertura auditável sem prometer separação global. | Não; premissa de planejamento |
| Q ótimo | Escolha por comparação `w_v > d*y_v*`, empates fora de Q com ordenação estável | Reproduz separação exata para L fixo sem enumeração de Q. | Não; premissa de planejamento |
| Teste de validade | Exigir conferência algébrica para cada linha e testes com pontos físicos inteiros | FC-R dispensa oráculo físico exponencial. | Não; premissa de planejamento |
| Recursos | Orçamento por instância, teto de regiões/linhas, deduplicação e abstenção | Evita piora descontrolada e falsos resultados negativos. | Não; premissa de planejamento |

**Open questions:** none — as escolhas não confirmadas são premissas explícitas acima; antes da execução, revalidar alterações de escopo e gates.

## User Stories

### P1: Separar a família declarada

**User Story:** Como pesquisador, quero encontrar violações em L fixo para obter cortes reproduzíveis.

**Acceptance Criteria**

1. WHEN L tiver excesso de origens THEN the separador SHALL calcular Q ótimo usando os coeficientes de fluxo da fronteira e `d_L*y*`, excluindo T e L.
2. WHEN L tiver excesso de destinos THEN the separador SHALL aplicar a forma simétrica de FC-R-T, excluindo S e L.
3. WHEN todas as regiões unitárias forem solicitadas THEN the separador SHALL examiná-las sem omissões e registrar sua contagem.

**Independent Test:** Comparar seleção Q com enumeração sobre micrografos.

### P1: Emitir somente cortes válidos

**User Story:** Como pesquisador, quero integrar cortes certificados de fluxo para não introduzir inequações erradas.

**Acceptance Criteria**

1. IF L for equilibrada, Q for inválido ou a violação não ultrapassar a tolerância declarada THEN the separador SHALL abster-se de emitir linha.
2. WHEN uma linha for emitida THEN the separador SHALL registrar L, Q, saldo, orientação, coeficientes e uma justificativa algébrica reproduzível.
3. WHEN linhas coincidentes surgirem THEN the separador SHALL deduplicá-las por assinatura canônica.

**Independent Test:** Aplicar a linha a todas as soluções inteiras enumeradas dos microcasos.

### P2: Avaliar regiões maiores

**User Story:** Como pesquisador, quero selecionar regiões pela estrutura e fluxo para testar sinal adicional com custo limitado.

**Acceptance Criteria**

1. WHEN a seleção heurística de L maiores estiver habilitada THEN the separador SHALL registrar quantas regiões foram geradas, descartadas, testadas e com violação.
2. IF o orçamento terminar THEN the runner SHALL registrar cobertura parcial e não declarar ausência global de cortes.

**Independent Test:** Comparar todos os singletons com subconjunto maior fixado e confirmar transparência dos limites.

## Edge Cases

- IF houver erro, censura ou evidência incompleta THEN the sistema SHALL registrar a razão e não atribuir resultado positivo à fase.
- IF a pré-condição não estiver satisfeita THEN the sistema SHALL bloquear a execução de AS24.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR24-01 | Separar Q origem para L fixa | T2, T4 | Validado com achados menores |
| FCR24-02 | Separar Q destino para L fixa | T2, T4 | Validado com achados menores |
| FCR24-03 | Cobrir os singletons elegíveis | T3, T4 | Validado com achados menores |
| FCR24-04 | Rejeitar L/Q inválidos e tolerância | T1, T2, T4 | Validado com achados menores |
| FCR24-05 | Certificado algébrico reproduzível | T1, T5 | Validado com achados menores |
| FCR24-06 | Deduplicação por assinatura | T1, T2, T4 | Validado com achados menores |
| FCR24-07 | Seleção heurística limitada | T3, T4 | Validado com achados menores |
| FCR24-08 | Limites e cobertura parcial explícitos | T2, T3, T4, T5 | Validado com achados menores |

**Coverage:** 8 requisitos rastreáveis; implementados, com testes e evidências. Revisão independente favorável registrada; achados menores não detalhados permanecem em acompanhamento.

## Success Criteria

- [x] Zero cortes inválidos em enumeração integral de padrões pequenos.
- [x] Concordância com enumeração de Q para região fixa e as duas orientações.
- [x] Cobertura total de todos os singletons elegíveis, com cobertura parcial explícita de regiões maiores.

## Dependências e gate

Separador não emite corte inválido; decisão `VALIDATED` depende de concordância exata na escolha de Q em microcasos, cobertura total declarada dos singletons e testes adversariais completos.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.

## Resultado de implementação (16/10/2026)

- Componentes: `experiments/cuts/fcr_rows.py`, `fcr_separator.py`, `fcr_regions.py`, `run_fcr_micro_as24.py`, `test_as24_fcr.py`.
- Dados: `results/benchmark/as24-fcr-micro-001.json` (`SYNTHETIC_ONLY`).
- Evidência e pendências formais: `docs/technical/reference/experimentos/as24-validacao-separador-fcr.md` e `validation.md`.
- **Gate científico:** `VALIDATED_WITH_MINOR_FINDINGS`; AS25 liberada para implementação e pré-registro, não para execução real sem protocolo congelado. Ver `validation.md` e `docs/technical/reference/experimentos/as24-revisao-independente-claude.md`.
