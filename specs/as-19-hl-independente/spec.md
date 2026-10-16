# AS19 — HL independente: certificação local e microtriagem — Specification

**Status:** MICROTESTE SINTÉTICO IMPLEMENTADO/VALIDADO; BENCHMARK REAL PENDENTE  
**Branch-alvo:** `novos_testes`  
**Autorização:** decisão do pesquisador em 15/10/2026 de **manter HL** independentemente do resultado de H2. A decisão da AS18 é histórica; AS19 é uma nova investigação, não reversão de seu gate.  
**Dependências:** AS13 (fundamentação), AS14 (oráculo físico), COMP+K congelado. **Não depende de AS16 GO nem de AS17.**

## Problem Statement

H2 não trouxe ganho marginal LP frente a COMP+K no piloto AS16. Esse fato não resolve a questão de HL: HL descreve o casco `conv(Φ_R)`, cuja força pode ultrapassar H2 mesmo quando ambas compartilham o oráculo físico. Investigar essa possibilidade com escopo pequeno, prova operacional conservadora e resultados reproduzíveis antes de autorizar comparação extensa.

## Goals

- [x] Implementar certificação local de HL, independente da autorização de H2, para suporte `R` explicitamente limitado.
- [x] Certificar `β_R(α)` sobre **todos** os padrões binários de um suporte, sem admitir `UNKNOWN` como infeasibilidade.
- [x] Reproduzir, com o compilador COMP+K existente, o microexemplo de quatro relés `2 < 8/3 < 3` e registrar custo.
- [ ] Avaliar ganho marginal e custo em **instâncias reais de desenvolvimento**, com protocolo pré-registrado e solver disponível; não alegar benefício prático antes disso.

## Out of Scope

- Nenhum benchmark real, corrida MIP, faceta global, nova política de seleção de suportes ou alegação de originalidade de HL nesta etapa.
- Nenhuma modificação do baseline COMP+K, cortes K ou H2 e resultados congelados AS16/AS18.

## Assumptions & Open Questions

| Questão | Default escolhido | Justificativa | Confirmado? |
|---|---|---|---|
| Suporte inicial | K4 com `|R|=4` | Testemunha estrutural AS13 independente de AS16 | Sim, micro-piloto |
| Máximo genérico de suporte | 8 | Enumeração total até 256 padrões | Limite operacional do micro-piloto |
| Coeficientes | Alfa unitário por padrão; entrada racionalizada | Certificação exata e interpretabilidade | Sim |
| UNKNOWN | Abstenção para todo suporte | Evitar RHS inflado por amostra incompleta | Sim |
| Benefício prático | Não inferir antes de testes reais | K4 é exclusivamente sintético | Não testado |

**Open questions: none** — nenhuma questão impeditiva para o micro-piloto; critérios de benchmark real exigem novo pré-registro.

## User Stories

### P1 — Certificar padrão incompatível em HL independentemente de H2

Como pesquisador, quero separar LP fracionária sobre pequenos suportes de forma segura para testar a hipótese de complementaridade de HL sem assumir que H2 já produziu GO.

**Acceptance Criteria:**

1. **AS19-01:** WHEN HL for autorizado de forma independente THEN o protocolo SHALL registrar gate separado do AS16/AS18.
2. **AS19-02:** WHEN o complemento V\R for viável THEN o certificador SHALL descartar suporte sem enumerar.
3. **AS19-03:** WHEN o suporte exceder o limite THEN o certificador SHALL abster-se sem chamadas físicas.
4. **AS19-04:** WHEN emitir corte HL THEN o certificador SHALL recomputar β exato em todos os padrões do suporte.
5. **AS19-05:** IF qualquer classificação for UNKNOWN THEN o certificador SHALL abster-se de emitir o corte.
6. **AS19-06:** WHEN um coeficiente numérico for dado THEN o certificador SHALL racionalizar e recalcular β sobre os racionais.
7. **AS19-07:** WHEN o K4 for resolvido THEN o runner SHALL medir 2, 8/3 e 3 pelo modelo COMP+K e cortes certificados.
8. **AS19-08:** WHEN gerar evidência THEN o runner SHALL incluir hashes e tempos sem sobrescrever resultados.
9. **AS19-09:** WHEN observar ganho sintético THEN o relatório SHALL informar que isso não equivale a GO real.
10. **AS19-10:** WHEN iniciar benchmark real THEN o protocolo SHALL exigir pré-registro com comparação marginal e orçamento total.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---|---|---|---|
| AS19-01 | P1 | T1 | Verified |
| AS19-02 | P1 | T2 | Verified |
| AS19-03 | P1 | T2 | Verified |
| AS19-04 | P1 | T2 | Verified |
| AS19-05 | P1 | T2 | Verified |
| AS19-06 | P1 | T2 | Verified |
| AS19-07 | P1 | T3 | Verified |
| AS19-08 | P1 | T3 | Verified |
| AS19-09 | P1 | T4 | Verified |
| AS19-10 | P1 | Future | Pending |

## Formalização

Para `R ⊆ V`, `F = V\R` e `Φ_R={z∈{0,1}^R : ν(F∪supp(z))=m}`, a linha

\[
\sum_{v\in R}\alpha_v y_v \ge \beta_R(\alpha),\qquad
\beta_R(\alpha)=\min_{z\in\Phi_R}\sum_{v\in R}\alpha_v z_v,
\quad\alpha_v\in\mathbb Q_{\ge0}
\]

é válida para toda instalação fisicamente viável, pela monotonicidade e projeção provadas em `docs/technical/reference/formulacoes/as13-prova-hl.md`. Neste micro-piloto só são aceitos suportes pequenos **e um `β` certificado por enumeração completa**, não por amostra ou LP auxiliar.

## Requisitos e critérios de aceite

| ID | Critério de aceite | Estado | Teste/evidência |
|---|---|---|---|
| AS19-01 | WHEN HL é investigado THEN o protocolo SHALL registrar autorização independente do gate H2 | Conforme | Esta spec e adendo à AS18 |
| AS19-02 | WHEN `ν(F)=m` THEN SHALL interromper para suporte sem corte HL não trivial | Pass | `test_viable_complement_short_circuits_no_enumeration` |
| AS19-03 | WHEN tamanho `|R|` exceder limite THEN SHALL abster-se sem enumeração | Pass | `test_support_cap_and_validation` |
| AS19-04 | WHEN for emitido corte THEN SHALL obter `β` racional exato em todos os `2^|R|` padrões físicos | Pass | `test_four_relay_exact_cut_and_h2_residual` |
| AS19-05 | IF houver `UNKNOWN`, orçamento esgotado ou classificação incompleta THEN SHALL **não emitir** corte | Pass | testes `unknown` e `budget` |
| AS19-06 | WHEN `α` numérico for fornecido THEN SHALL racionalizar e **recalcular `β`** exatamente | Pass | `test_rationalization_and_beta_are_exact` |
| AS19-07 | WHEN o K4 for rodado THEN SHALL reproduzir LP K=2, K+H2=8/3, K+H2+HL=3 via modelo real e cortar `y=2/3` | Pass | `test_comp_k_h2_hl_lp_hierarchy_from_actual_models` |
| AS19-08 | WHEN mensurar micro-piloto THEN SHALL registrar tempo de certificação, chamadas, hash, status e proveniência sintética | Pass | JSON `as19-hl-micro-k4-001.json` |
| AS19-09 | WHEN houver resultado sintético positivo THEN SHALL **não** promovê-lo a ganho real ou GO científico | Pass | `validation.md` e relatório AS19 |
| AS19-10 | WHEN uma campanha real for considerada THEN SHALL exigir pré-registro independente e confronto pareado com COMP+K (e pool H2) | Pendente | próxima autorização, **não incluída nesta etapa** |

## Escolhas de execução e limites

- Piloto inicial: somente **K4 sintético** já definido e provado na AS13. Nenhuma escolha post hoc de benchmark favorável.
- `max_support_size=4` no runner K4; contrato genérico aceita até 8 por padrão, com orçamento total de 15 s, por suporte de 5 s, até 300 chamadas e até 12 suportes. Controles explícitos, nunca enumeração global implícita.
- Alfa inicial = cardinalidade (`α=1`), com entrada opcional não negativa racionalizada de denominador máximo 1000. Recalcular o mínimo **depois** da racionalização.
- Registros `save_new()` e runner `open('x')`: não sobrescrevem evidência; `cut_hash` e `certificate_sha256` independem de tempo e cache.
- Sem modificar COMP, K, H2, planilhas de benchmark, splits AS00 ou resultados AS16/18.
- Não exigir Gurobi no micro-piloto: usar `scipy.optimize.linprog(method='highs')` já presente no projeto. Tempos em uma execução são apenas descritivos.

## Gates de decisão

1. **MICRO_VALIDATED:** testemunha HL certificada no K4, violação de ponto COMP+K+H2, modelo LP reproduz hierarquia e controles negativos passam.
2. **BENCHMARK_NOT_YET_EVALUATED:** ainda não há evidência de ganho líquido em instâncias reais nem justificação para MIP.
3. **GO/STOP prático:** somente mediante protocolo futuro com instâncias reais, tempo total e controles de mesma pool de cortes; não emitir a partir deste microteste.

## Outside scope e riscos

Não há separador global de facetas de `Q_R`, política de geração robusta de suportes reais, callback MIP, provas de originalidade poliédrica ou teste em outras instâncias. A enumeração é exponencial (`2^|R|`) e proibida além do teto configurado. `UNKNOWN` obriga abstenção total. O exemplo K4 também admite derivação por arredondamentos de K: não demonstra novidade frente ao fecho CG de K. Revisão matemática **humana independente** não foi realizada nesta execução.
