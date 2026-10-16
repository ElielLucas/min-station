# AS20 — Triagem LP de HL independente em instâncias reais de desenvolvimento — Specification

**Status:** EXPERIMENTO EXECUTADO; GATE INVESTIGATE; INVESTIGAÇÃO CONTINUA NA AS21  
**Branch:** `novos_testes`  
**Autorização:** usuário autorizou prosseguir após confirmar AS19 (K4 físico e 124 testes, 15/10/2026).  
**Dependências:** AS19, AS13/AS14, COMP+K, pré-registro AS16 (somente casos de desenvolvimento). **Sem dependência do gate de H2.**

## Problem Statement

AS19 demonstrou que HL pode reforçar COMP+K no K4 sintético; não demonstrou ganho, custo nem aplicabilidade nas instâncias reais. A AS20 implementa uma **triagem de baixo escopo**, com limite por braço, enumeração certificada de suportes pequenos e comparações LP pareadas sobre o mesmo conjunto de seis grafos de desenvolvimento da AS16. O objetivo é obter evidências de **ganho marginal e custo total** sem confundir ausência de corte para suportes pequenos com redundância matemática de toda a família HL.

## Goals

- [x] Congelar entradas e hiperparâmetros da campanha antes da execução real.
- [x] Selecionar deterministicamente suportes K pequenos e uniões de K, priorizando incompatibilidades coletivas, sem enumerar subconjuntos de V.
- [x] Certificar cada corte com `separate_hl()` AS19 sobre todos os padrões binários do suporte; `UNKNOWN`/timeout implicam abstenção.
- [x] Comparar `U_K` com `U_K_HL` no **mesmo modelo COMP+K**, por LP contínuo, com orçamento total de 90 segundos para cada braço incluindo carregamento, K, solver e oráculo.
- [x] Registrar tempo, número de chamadas físicas, tamanho dos suportes, cortes, status e ganho marginal. Proibir avaliação, MIP e sobrescrita.
- [x] Analisar censura, falta de suporte elegível e execuções parciais sem classificá-las como falha da família HL.
- [x] Executar os dois braços reais no Gurobi com a licença do pesquisador e arquivar evidências; gate calculado `INVESTIGATE`.
- [ ] Revisão científica humana independente e decisão posterior da linha HL (continuação AS21 autorizada).

## Out of Scope

- MIP, instâncias de avaliação, novos cortes K, alterações do baseline, refinamento de H2, procura exata de facetas de `conv(Φ_R)`, redução do custo de enumeração e grande benchmark multi-seed.
- Este piloto usa somente cortes HL **de cardinalidade** (`α=1`) e suportes até 10 vértices. Resultados negativos **não** implicam dominância de HL por K ou redundância de HL em geral.

## Premissas e escolhas pré-registradas

| Item | Decisão | Justificativa |
|---|---|---|
| Instâncias | Exatamente os seis casos AS16, split desenvolvimento | Comparabilidade de dados e independência de grafo bruto |
| Braços | `U_K` e `U_K_HL` | Ganho marginal sobre o baseline relevante |
| Limite | 90 s totais por braço | Mesmo teto de AS16; subprocessos separados |
| Solver | Mesmos parâmetros AS16 Gurobi (seed 42, threads 4 etc.) | Reduzir fontes de viés |
| Suportes | K de tamanho ≤10 e uniões de dois K que caibam em 10; máximo 3 suportes | Evitar enumeração global |
| Priorização | Maior cobertura de restrições K; menor massa `∑ y*`; ordenação estável | Preferir relações entre K, não apenas cortes isolados |
| Enumeração | Até 2^10 padrões por suporte; ≤2200 chamadas; ≤24s global; ≤12s por suporte | Custo e segurança física explícitos |
| RHS | Mínimo exato sobre todos os padrões certificados | Nunca inferir inviabilidade de `UNKNOWN` |
| Corte | Máximo 3 cortes; apenas violados por ≥10^-7 | Evitar cortes inúteis |
| Gate preliminar | Candidato de GO com ≥1% de LP em ≥2 grafos independentes e custo ≤2× K, com todos seis casos submetidos | Evidência mínima para **revisão**, não promoção direta |
| Sem ganho | `NO_GAIN_IN_BOUNDED_SCREEN` apenas quando seis pares completos e triagem não censurada | Escopo limitado; nunca prova matemática global |

Pré-registro **machine readable**: `docs/technical/plans/execucao/as20-preregistro-hl-lp.json`, que inclui o SHA do pré-registro AS16, os hashes dos seis arquivos, parâmetros e política de seleção.

## User Story P1 — Triagem real rastreável e segura

Como pesquisador, desejo testar HL nas mesmas instâncias de desenvolvimento já usadas para H2, sem permitir que um corte sem prova física ou um resultado censurado gere uma conclusão científica indevida.

### Acceptance Criteria

1. **AS20-01:** WHEN executar qualquer instância THEN o runner SHALL validar o pré-registro AS16, hashes do manifesto, arquivos e origem de desenvolvimento antes de otimizar.
2. **AS20-02:** WHEN selecionar R THEN SHALL usar apenas suportes K pequenos ou uniões bounded, sem truncar um K grande para simular um suporte válido.
3. **AS20-03:** WHEN um `R` tiver mais de 10 vértices THEN SHALL recusá-lo; se nenhum R elegível existir, SHALL registrar `NO_ELIGIBLE_SUPPORT` sem concluir que HL falhou.
4. **AS20-04:** WHEN um padrão for `UNKNOWN`/não classificado THEN SHALL abster-se; `β` só pode vir de enumeração completa certificada.
5. **AS20-05:** WHEN adicionar HL THEN SHALL manter `compile_u(ins,K,relax=True)` idêntico ao do braço de controle e reotimizar sobre o mesmo modelo.
6. **AS20-06:** WHEN qualquer braço vencer o teto de 90s THEN SHALL ser censurado, sem inferir ótimo ou ganho.
7. **AS20-07:** WHEN gerar a saída THEN SHALL criar nova pasta contendo `manifest.json`, `rows.json` e `analysis.json`; saída existente SHALL gerar erro.
8. **AS20-08:** WHEN avaliar ganho THEN SHALL comparar somente pares LP ótimos, usando tempo total de parede e taxa de ganho marginal; ausência de suporte e orçamento parcial SHALL ser inconclusiva.
9. **AS20-09:** WHEN usar `--dry-run` THEN SHALL validar as entradas, mas NÃO executar solver nem afirmar ganho.
10. **AS20-10:** WHEN houver resultado experimental favorável THEN SHALL exigir revisão científica e nova autorização antes de qualquer MIP.

## Requirement Traceability

| Requirement | Task | Evidência | Status |
|---|---|---|---|
| AS20-01 | T1/T3 | `load_plan`, `validate_sources`, dry-run | Implementado/testado |
| AS20-02/03 | T2 | `hl_supports.py`, `test_as20_hl_lp.py` | Implementado/testado |
| AS20-04/05/06 | T3 | `hl_local.py` herdado, `run_hl_lp.py` | Implementado; campanha pendente |
| AS20-07/08/09 | T4 | `analyze_hl_lp.py`, testes | Implementado/testado |
| AS20-10 | T5 | relatório de execução AS20 | Pendente |

## Gates

- `NOT_EXECUTED`: dry-run apenas.
- `INVESTIGATE`: subset, censura, ausência de suportes, classificação incompleta ou outra insuficiência.
- `NO_GAIN_IN_BOUNDED_SCREEN`: campanha completa, comparável e sem ganho nas condições examinadas; **não** é STOP da família HL.
- `GO_CANDIDATE_REVIEW`: pelo menos dois grafos com ganho e custo aceitável; **não** autoriza MIP automaticamente.

**Revisão matemática humana independente:** ainda pendente. **Execução real registrada** em `results/benchmark/as20-hl-lp-001/`, com zero cortes e gate `INVESTIGATE`. AS21 investiga as limitações da certificação e seleção.
