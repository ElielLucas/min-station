# AS05-FAC — Experimento LP fatorial A2/A4 × K — Specification

**Status:** implementação concluída e testes locais; campanha exploratória Gurobi pendente  
**Prioridade:** P1 (antes de promover candidatas à AS-06)  
**Dependências:** AS-00, AS-02, AS-03, AS-04, AS-05, AS05-DIAG v2  
**Local:** `specs/as-05-investigacao-fatorial-a2-a4/`

## Problem Statement

O piloto e o reensaio AS05-DIAG-v2 mostraram que a desagregação automática A2+K acrescentou pouco ao limite LP de U+K. Ainda não isolamos o efeito de **2 versus 4 grupos** nem a interação desses agrupamentos com a presença dos cortes K. Não é cientificamente adequado concluir que a formulação A, em geral, é pouco promissora apenas pelo desempenho de A2+K.

## Goals

- [x] Executar um mesmo desenho fatorial de seis braços: `U`, `U_K`, `A2`, `A2_K`, `A4`, `A4_K`.
- [x] Utilizar os compiladores AS02 existentes; sem duplicar/reformular suas restrições.
- [x] Aplicar **a mesma partição A2** nos braços A2/A2+K e **a mesma A4 estritamente aninhada** nos braços A4/A4+K.
- [x] Utilizar a política AS03 `reachability_degree`, seed de agrupamento 42, fixada antes dos solves.
- [x] Reutilizar geradores C1+C2+C4-DM e verificador K exato da v2, exigindo igualdade de SHA entre braços +K e com os hashes v2 preexistentes quando disponíveis.
- [x] Manter as seis instâncias de desenvolvimento AS00, 300 s por braço, 4 threads, sem warm start, mesmas configurações de solver por braço.
- [x] Estimar tamanho de A2/A4 antes de construir; preservar censuras de tamanho, memória e timeout no denominador.
- [x] Produzir por caso nove contrastes LP, custos totais/solver, tamanho, interação fatorial, hashes e análise em CSV/JSON/Markdown.
- [x] Permitir retomada de execução parcial apenas com checkpoints SHA íntegros; saída final append-only.
- [x] Impedir interpretação de resultados como revisão independente ou promoção científica automática.

## Out of Scope

| Item | Motivo |
|---|---|
| Alterar AS05 original ou AS05-DIAG-v1/v2 | Evidências históricas congeladas |
| Dados AS00 de avaliação | Evitar contaminação de avaliação por escolha exploratória |
| Buscar a melhor partição após ver objetivos LP | Seria seleção pós-hoc |
| Executar MIP, A8 ou formulação B/C | Fases distintas |
| Certificados racionais e revisão matemática independente | Permanecem pendentes |

## Assumptions & Open Questions

| Decisão | Default | Justificativa | Confirmado? |
|---|---|---|---|
| Política A2 | `reachability_degree`, seed 42 | Igual ao piloto original | Congelado no plano |
| Política A4 | `refine_four` sobre o mesmo objeto pai A2 | Garantir dominância de refinamento | Testado |
| K | C1+C2+C4-DM, `bitset-v2` | Método exato auditado na investigação anterior | SHA e testes |
| Orçamento | 300 s por braço, 4 threads | Rodada diagnóstica separada da campanha de 90 s | Congelado no plano |
| Cap | 2 milhões de variáveis/restrições; proxy de 8 GiB | Evitar construção arbitrariamente grande | Exploratório; proxy não é RSS |
| Classe | Desenvolvimento exploratório, `PENDING` | Não reinterpretar gate AS05 | Sim |

**Open questions: none — a revisão independente e a execução Gurobi constam como gates posteriores, não decisões de design pendentes.

## User Stories

### US-01 — Comparação justa de seis LPs

Como pesquisador, quero separar o efeito da desagregação A2/A4 e o efeito de K sem alterar origens, instâncias, políticas ou parâmetros do solver.

**Acceptance Criteria**

1. **FAC-01 — Pré-registro:** WHEN criar plano THEN SHALL selecionar exclusivamente os seis casos de desenvolvimento do AS00 original, preservar hashes de origem e registrar os seis braços antes dos solves.
2. **FAC-02 — Compilação:** WHEN compilar A2/A4 THEN SHALL reutilizar `compile_a`; WHEN compilar U/U+K THEN SHALL reutilizar `compile_u`; braços sem K SHALL conter zero restrições A6.
3. **FAC-03 — Aninhamento:** WHEN compilar A4/A4+K THEN SHALL usar filho de `refine_four(A2)` com `parent_hash` verificável; SHALL rejeitar partições arbitrárias.
4. **FAC-04 — Validação K:** WHEN executar um braço +K THEN SHALL preparar e validar K pelo mesmo procedimento; SHALL preservar SHA do conjunto e registrá-lo em cada execução; braços sem K SHALL evitar preparação de K.
5. **FAC-05 — Orçamento/censura:** WHEN orçamento/memória/tamanho forem excedidos THEN SHALL registrar status e razão e SHALL não publicar objetivo LP interrompido ou parcial.
6. **FAC-06 — Cobertura/integridade:** WHEN gerar relatório THEN SHALL conter seis casos × seis braços, checkpoints por braço, manifesto SHA e comparação reconstituível; SHALL detectar remoção ou alteração de evidências.
7. **FAC-07 — Resultados:** WHEN todas as execuções terminarem THEN SHALL produzir análise LP e deltas para nove pares e interação K/refinamento, distinguindo custos de construção, K e solver.
8. **FAC-08 — Proteção científica:** WHEN a execução for exploratória THEN SHALL manter `scientific_gate=PENDING`, `scientific_promotion=NOT_AUTHORIZED` e não alterar o veredito AS05 original.

**Independent Test:** smoke SciPy de seis braços com cortes válidos; 19+ testes unitários/integração que verificam partições, hashes, censuras, retomada, relatório e integridade.

## Edge Cases

- Menos de quatro origens: A2 continua aplicável com duas/três origens; A4 é `NOT_APPLICABLE`, sem remover a linha.
- A4 com mais de dois milhões de variáveis: `NOT_BUILT_SIZE`, antes de construir o modelo.
- Estimativa de memória > 8 GiB: `NOT_BUILT_MEMORY` (proxy heurístico, não limite garantido de RSS).
- Gurobi ausente: status de erro/abstenção, sem inventar bound LP.
- Solver LP interrompido: valor LP global não publicável; manter `None`.
- Hash K divergente: falha explícita, sem selecionar outro conjunto de cortes.
- Checkpoint parcial/adulterado: retomada bloqueada.
- Comparação U sem cortes NÃO carrega o custo de gerar K.

## Requirement Traceability

| ID | Evidência de teste | Estado |
|---|---|---|
| FAC-01 | `test_six_dev_arms_and_fixed_policy`, `test_mutation_rejected` | PASS local |
| FAC-02 | `test_six_compilers_exactly_use_k_where_expected` | PASS local |
| FAC-03 | `test_same_partition_without_and_with_k`, `test_nonnested_a4_rejected` | PASS local |
| FAC-04 | `test_u_does_not_compute_k_nor_assign_it`, smoke completo | PASS local |
| FAC-05 | `test_A2_applicable_with_three_origins_but_A4_not`, `test_reject_censored_lp_value` | PASS local |
| FAC-06 | `test_all_36_rows_and_8_contrasts`, testes de corrupção/retomada | PASS local |
| FAC-07 | `test_analysis_is_exploratory_and_append_only` | PASS local |
| FAC-08 | `test_all_36_rows_and_8_contrasts` | PASS local |

## Success Criteria

- [x] Plano fatorial congelado e validado com arquivos originais.
- [x] Código executor separado, todos seis braços implementados.
- [x] Testes sintéticos e verificadores passam sem depender de Gurobi.
- [x] Registros integram métricas de LP, fases, tamanhos e censuras.
- [ ] Executar os 36 braços reais em Gurobi no ambiente do pesquisador.
- [ ] Verificar e interpretar os resultados reais, com critérios de replicação.

## Tests Derived from Acceptance Criteria

- Pure tests de compilação e contagem de A6 (A sem/com K).
- Pequeno grafo com dominância LP verificada em HiGHS.
- Mock 6×6 com relatórios integrais e 9 contrastes/caso.
- Mutação de hash K, alteração de pai A4 e remoção de braço detectadas.
- Checkpoints retomados e corrompidos recusados.
- Relatório sem objetivo LP para censuras.
- Não executa K em U/A2/A4 sem cortes.

## Implicit-Requirement Sweep

- **Autonomia/instância:** preservadas pelo loader FC e SHA do manifesto AS00.
- **Cortes:** conjunto idêntico e aplicado somente nos braços rotulados +K.
- **Agrupamentos:** totalmente independentes do solver/objetivo e com refinamento estrito.
- **Desempenho:** tempo de K é cobrado separadamente por braço que o utiliza.
- **Cientificidade:** estudo exploratório posterior ao piloto; não reinterpretar como experimento confirmatório.
