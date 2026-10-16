# AS23 — Revisão matemática independente de FC-R — Specification

**Referências:** `[docs/technical/reference/tecnico/parecer-astra-fcr-pos-as22.md]` (parecer externo) e `[docs/technical/plans/execucao/plano-fcr-as23-as27.md]` (plano científico). **Estado:** implementado e certificado matematicamente em microcaso; gate técnico `VALIDATED` após parecer independente e correções obrigatórias; commit/proveniência final pendentes no checkout local. **Branch de referência:** `novos_testes`. **Pré-condição:** AS22 concluída experimentalmente; parecer Astra registrado; COMP+K, C6, C8 e validador físico existentes.

## Problem Statement

Estabelecer validade formal da FC-R/FC-R-T, confirmar separação exata de Q para região L fixa e reproduzir independentemente a testemunha racional declarada pelo Astra, antes de escrever um separador para benchmarks.

## Goals

- [x] Estabelecer validade formal da FC-R/FC-R-T, confirmar separação exata de Q para região L fixa e reproduzir independentemente a testemunha racional declarada pelo Astra, antes de escrever um separador para benchmarks.
- [x] Gate e evidências rastreáveis: Gate `VALIDATED` somente se duas provas, testemunha física e racional independente, relação C6/C8 e verificação bibliográfica forem documentadas sem divergência bloqueante. `BLOCKED` em caso contrário.

## Out of Scope

| Item | Razão |
|---|---|
| Campanha LP nos seis grafos | É assunto da AS25; AS23 não confunde testemunha com desempenho. |
| Implementação de separador de produção | Pertence à AS24. |
| Alegação de novidade na literatura | Depende da verificação bibliográfica independente. |
| MIP e dados de avaliação reservada | Dependem de gates futuros. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Proveniência do parecer | Usar commit declarado `285261b` somente como contexto, verificando código e hashes atuais | SHA declarado não garante reproduzir alterações ainda não commitadas. | Não; premissa de planejamento |
| Relação com C6/C8 | Verificar geradores e versões do código antes de produzir assert de comparação | Famílias antigas têm variantes e condições específicas. | Não; premissa de planejamento |
| Aritmética | Usar `Fraction` ou outra aritmética racional exata para a testemunha | Evita falsos ganhos induzidos por tolerância. | Não; premissa de planejamento |
| Literatura | Classificar precedentes e novidade como pendentes até levantamento | FC-R é nome local e fixed-charge flow é conhecido. | Não; premissa de planejamento |

**Open questions:** none — as escolhas não confirmadas são premissas explícitas acima; antes da execução, revalidar alterações de escopo e gates.

## User Stories

### P1: Prova auditável

**User Story:** Como pesquisador, quero ter uma prova independente de FC-R e FC-R-T para evitar cortes inválidos.

**Acceptance Criteria**

1. The verificador SHALL demonstrar FC-R para todo ponto de COMP com y binário, considerando Q fora de T e L.
2. The verificador SHALL demonstrar FC-R-T com Q fora de S e L, incluindo fluxo com circulações.
3. IF Q contiver terminal proibido ou vértice de L THEN the verificador SHALL rejeitar a instância da desigualdade.

**Independent Test:** Checar as provas algébricas, uma variação com S∩T e contraexemplos para Q inválido.

### P1: Testemunha independente

**User Story:** Como pesquisador, quero reproduzir os valores fracionários declarados para distinguir hipótese de resultado demonstrado.

**Acceptance Criteria**

1. WHEN a instância de 24 vértices for reconstruída THEN the verificador SHALL checar exatamente seus vértices, 96 arcos de H, S, T, r=1 e a identidade das restrições K geradas.
2. WHEN os pontos racionais forem avaliados THEN the verificador SHALL conferir todas as restrições COMP+K, as C6/C8 aplicáveis, as quatro FC-R e os objetivos 1, 7/5, 47/30 e 17/10 conforme cada afirmação.
3. IF um ponto ou combinação algébrica não fechar exatamente THEN the relatório SHALL registrar a divergência e impedir o gate VALIDATED.

**Independent Test:** Reproduzir pontos racionalmente e limites inferiores sem chamar resultados do parecer como dados de teste.

### P2: Análise de não redundância

**User Story:** Como pesquisador, quero compreender relação com K/C6/C8 para priorizar uma candidata justificável.

**Acceptance Criteria**

1. WHEN a testemunha for validada THEN the relatório SHALL apresentar uma comparação comprovada de COMP+K, COMP+K+C8 e COMP+K+C6+C8 com e sem FC-R.
2. WHEN a busca bibliográfica terminar THEN the relatório SHALL distinguir o que já é conhecido em fixed-charge flow do que foi apenas adaptado ao MIN-STATION.

**Independent Test:** Tentar construir e conferir um ponto que respeita K/C6/C8 mas viola FC-R e documentar precedentes.

## Edge Cases

- IF houver erro, censura ou evidência incompleta THEN the sistema SHALL registrar a razão e não atribuir resultado positivo à fase.
- IF a pré-condição não estiver satisfeita THEN the sistema SHALL bloquear a execução de AS23.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| FCR23-01 | Prova auditável | Tasks | Validated; minor follow-ups documented |
| FCR23-02 | Prova auditável | Tasks | Validated; minor follow-ups documented |
| FCR23-03 | Prova auditável | Tasks | Validated; minor follow-ups documented |
| FCR23-04 | Testemunha independente | Tasks | Validated; minor follow-ups documented |
| FCR23-05 | Testemunha independente | Tasks | Validated; minor follow-ups documented |
| FCR23-06 | Testemunha independente | Tasks | Validated; minor follow-ups documented |
| FCR23-07 | Análise de não redundância | Tasks | Validated; minor follow-ups documented |
| FCR23-08 | Análise de não redundância | Tasks | Validated; minor follow-ups documented |

**Coverage:** 8 requisitos com evidência técnica; testes e prova em `experiments/cuts/test_as23_*`, `as23-prova-fcr.md` e `as23-validacao-fcr.md`. Revisão independente recebida em resumo; ver `validation.md` para limitações e achados menores.

## Success Criteria

- [x] Duas provas de validade conferidas independentemente e nenhum Q inválido aceito.
- [x] Pontos fracionários reproduzidos com certificados exatos e discrepâncias explícitas.
- [x] Pelo menos uma testemunha válida contra COMP+K+C6+C8, ou decisão BLOCKED justificada.

## Dependências e gate

Gate `VALIDATED` somente se duas provas, testemunha física e racional independente, relação C6/C8 e verificação bibliográfica forem documentadas sem divergência bloqueante. `BLOCKED` em caso contrário.

## Fora de escopo científico adicional

Nenhum resultado sintético é extrapolado para benchmark; nenhuma alegação de originalidade, de dominância geral ou de superioridade sobre COMP+K sem prova e dados comparáveis.

## Execução e verificação

Reprodução local: `results/benchmark/as23-fcr-witness-001.json`, **173 testes aprovados**. Aritmética racional exata e revisão bibliográfica documentadas em `docs/technical/reference/experimentos/as23-validacao-fcr.md`. Gate técnico **`VALIDATED`** após correção do MAJOR FC-R-T; liberar AS24 depois do commit e da atualização de proveniência descritos em `validation.md`.
