# N2-T2B — Gate O: aceite operacional aprovado

**Estado deste registro:** `APROVADO PARA PROSSEGUIR À N2-T3` — decisão humana registrada em
2026-10-09 (America/Sao_Paulo), após avaliação técnica concluída com recomendação
`APTO PARA ACEITE`. O aceite abrange exclusivamente a implementação operacional
N2-T2B avaliada no commit identificado na §11; **não** certifica limites inferiores,
não altera a revisão matemática v2.1 e não substitui os critérios da N2-T3 a N2-T6.

## 1. Identificação

| Campo | Valor |
|---|---|
| Etapa | N2-T2B — Gate O (aceite operacional, pós-implementação) |
| Data da avaliação | 2026-10-09/10 (America/Sao_Paulo) |
| Branch | `novos_testes` |
| Commit HEAD no momento da avaliação | `d6d9517e484ee965c556ea228e0020bc624400e3` |
| Working tree | Limpo (`git status --short` sem saída) |
| Commits da N2-T2B avaliados | `e6a8d53` (Entrega 1), `babb176` (Entrega 2), `d6d9517` (Entrega 3, já com as correções de borda de Work/tempo) |
| Pré-requisito | Gate M `APROVADO PARA IMPLEMENTAÇÃO` em `n2-t2b-decisao-aprovacao-matematica.md` |

## 2. Objetivo e escopo

Verificar se a implementação das três entregas (master restrito, pricing MIP P0–P5, geração de colunas na raiz)
satisfaz os critérios operacionais P-2, P-6 e os critérios adicionais do §11.2 da revisão v2.1, **sem** exigir a
certificação ENUM/N1/N2 nem o critério G2 — ambos reservados à N2-T3 — e sem avançar a N2-T4/N2-T5/N2-T6.

**Fora de escopo desta avaliação** (confirmado como não tocado, ver §7): caminho A, variante trio,
branch-and-price, novos cortes, mudança de baseline/K/núcleo/`fcc.py`/`fcc_k.py`, certificação N2-T3, regressão
N2-T4, campanha N2-T5, gate científico N2-T6.

## 3. Documentação matemática e hashes de referência

| Documento | SHA-256 nesta avaliação | SHA-256 registrado no Gate M | Confere? |
|---|---|---|---|
| `n2-t2b-master-dual-pricing-revisao.md` (v2.1) | `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237` | `db1fb71b6e4afba421ccc9f8d4f244aee6700edb886dc1c0219ed7e812aa9237` | **Sim** |
| `parecer-independente-N2-T2B.md` | `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888` | `32a62d416e994de1d58f31e1d3b3aa61bf8d365e223025273728d52b9559a888` | **Sim** |

Nenhum dos dois documentos foi editado por esta avaliação (regra de integridade do Gate M preservada; este
registro é um arquivo separado, conforme instruído em §12.2 da revisão).

## 4. Verificação de integridade (antes dos testes)

| Item | Resultado |
|---|---|
| Branch | `novos_testes` (confirmado) |
| HEAD / alterações não commitadas | `d6d9517`; nenhuma alteração pendente |
| Hashes v2.1 e parecer vs. Gate M | Conferem (tabela §3) |
| `run_n2_t1.py check` | `PASS: N2-T1 freeze íntegro; caminho B; 2 famílias x 2 níveis; orçamento total 164 Work` |
| `verify_n1_t7_gate.py` | `DECISÃO N1-T7: PROMOTE FCC + EXISTING CUTS` / `N2: caminho B — F-CC + K (apenas raiz)`; hashes N1-T5/T6 íntegros, MR-F3 aceito |
| Arquivos/parâmetros congelados alterados | Nenhum. O freeze não foi refeito; `run_n2_t1.py check` já confere `source_hashes` (inclui `fcc.py`, `fcc_k.py`, `cuts.py`, `harness.py`, `n1-t7-decisao-cientifica.md`, a própria spec N2) byte a byte contra o congelamento |

**Nota de rastreabilidade:** a revisão v2.1 já reestrutura, nas suas próprias §§11–12, a separação Gate M / Gate
O com os critérios P-1 a P-9 renumerados; este registro usa exatamente essa numeração, sem reinterpretar os
critérios.

## 5. Evidência por entrega

### 5.1 Entrega 1 — Master restrito e dual (`n2_t2b_master.py`, 473 linhas)

- `RestrictedMaster.__init__` valida a instância (`G` simples, unitário, conexo; `A_r` recomputado e conferido
  contra `construir_arcos_alcance`), monta R1/R2 com todos os pares diretos `D`, R3 como `-y_v≤0` com os
  coeficientes de `λ` inseridos via `gp.Column` em `add_column` (equivalente a `Σλ−y≤0`), adiciona `K` por
  `add_cuts_to_model(..., validate=(S,T,A_r))` e insere a coluna inicial `(V,S,T)` antes de devolver o objeto.
  `self.K`/`self.k_hash` são atribuídos uma única vez no construtor; não há método de mutação de `K`.
- Nenhuma variável binária ou inteira no master: `y` é contínuo (`lb=0, ub=1`), `d` e `λ` contínuos — confirmado
  por `grep` (nenhuma ocorrência de `BINARY`/`INTEGER`).
- `_dual_snapshot`: `μ_v=-Pi(R3_v)`, `κ_Z=Pi(K_Z)`, `η_v=max(0,μ_v+κ(v)-1)` (linha
  `eta = {v: max(0.0, math.fsum([mu[v], -1.0] + incidence[v])) for v in V}`), exatamente a fórmula da revisão
  v2.1 §3. `DualChecks` compara `rc` recalculado contra `Var.RC` do Gurobi e a dualidade `ObjVal` vs `L`.
- `reduced_cost(column, snapshot=...)` levanta `StaleDualError` se o snapshot não for `is` o dual da última
  resolução deste mesmo master; `extract_duals()` só aceita `GRB.OPTIMAL` de LP contínuo.
- `MasterResult` registra `status`, `status_name`, `gurobi_version`, `parameters` (apenas os permitidos em
  `_ALLOWED_PARAMS`), `runtime`, `work`, `revision`, `solve_id`.

### 5.2 Entrega 2 — Pricing MIP P0–P5 (`n2_t2b_pricing.py`, 333 linhas)

- `build_pricing_model`/`_add_eligibility_balance`/`_add_connectivity` reproduzem P0–P5: binárias `x,a,b,ρ`,
  contínuas `g,f`; elegibilidade por `N_H[s]={s}∪H[s]`; balanço `Σa=Σb≥1`; raiz única (`Σρ=1`) e conservação de
  fluxo ligando `g`/`f` a `x` nos dois sentidos de cada aresta de `H` (usa `master.reach_graph`, não `G`).
- Extração: `W,I,J` por limiar 0,5, **seguida** de checagem de integralidade (`_integrality_violation` sobre
  **todas** as binárias do modelo, incluindo `ρ`, tolerância `INTEGRALITY_TOLERANCE=1e-6`) e só então
  `master.validate_column((W,I,J))`. Um incumbente fracionário é rejeitado como `INVALID_INCUMBENT` antes de
  qualquer validação combinatória.
- Custo reduzido recalculado por `values.column_rc(column)` (não pelo `ObjVal` do MIP) e comparado a `ObjVal`
  com `mismatch_tolerance`; divergência vira `OBJECTIVE_MISMATCH` e descarta a coluna.
- `pricing_label='heuristic'` fixo, `certification_status='UNCERTIFIED'` fixo,
  `proves_no_negative_column=False` fixo — nenhum caminho de código os altera. `solver_bound` (`ObjBoundC`) é
  apenas um campo de diagnóstico, nunca comparado em uma decisão de aceitação.
- `PricingResult` registra `status`, `status_name`, `termination`, `outcome`, `gurobi_version`, `parameters`,
  `runtime`, `work`, `solution_count`.

### 5.3 Entrega 3 — Geração de colunas na raiz (`n2_t2b_column_generation.py`, 457 linhas)

- Loop único: resolve o master, exige snapshot (`mres.dual`) desta mesma resolução, chama **sempre**
  `pricer(master, snapshot, ...)` com o pricer padrão `price()` (nunca `price_vector()` por padrão — garantido
  por teste explícito com `price_vector` mockado para levantar `AssertionError` se chamado), confere
  `master.reduced_cost(column, snapshot=snapshot)` contra `pres.reduced_cost`, rejeita duplicata
  (`DUPLICATE_COLUMN`), rejeita custo reduzido não finito ou divergente, insere com `master.add_column` (que
  revalida a coluna e invalida o snapshot anterior) e reotimiza.
- Nenhuma variável binária/inteira no controlador; nenhuma chamada a rotina de corte nova; `master.K` nunca é
  reatribuído.
- Estados de parada implementados e mutuamente distintos: `NUMERICAL_STATIONARY`, `PRICING_INCOMPLETE`,
  `MASTER_FAILURE`, `PRICING_FAILURE`, `DUPLICATE_COLUMN`, `ITERATION_LIMIT`, `WORK_LIMIT`, `TIME_LIMIT`,
  `WORK_UNMEASURED` (`STOP_REASONS`, 9 elementos). `COMPLETED_NUMERICAL` foi deliberadamente omitido por ser
  sinônimo de `NUMERICAL_STATIONARY`.
- Work e tempo: `account()` soma apenas medições finitas e `≥0`; valores negativos/NaN/ausentes contam em
  `unmeasured_work_calls` e nunca são descontados do total; `overrun()` é reavaliado após **cada** subsolve,
  inclusive o último, cobrindo tanto Work quanto tempo global, para que um pricing `OPTIMAL` que já tenha
  estourado o orçamento não seja lido como estacionário; limites por chamada são sempre `min(limite do usuário,
  restante global)`.
- `certification_status` é sempre `UNCERTIFIED` no resultado; o controlador também verifica defensivamente que
  o pricing não devolveu outra coisa (`if pres.certification_status != UNCERTIFIED or
  pres.proves_no_negative_column: stop = PRICING_FAILURE`).

## 6. Matriz de conformidade — P-2, P-6 e critérios adicionais do Gate O (§11.2)

| ID | Critério | Status | Evidência |
|---|---|---|---|
| P-2 | Controles de master, dual, pricing e validade de colunas reexecutados contra as **funções reais** da geração de colunas, além das referências isoladas | **ATENDIDO** | `test_n2_t2b_column_generation.py::test_stationary_value_matches_full_fcc_k_lp` chama `cg.run_column_generation` de ponta a ponta e compara `result.rmp_objective` ao LP F-CC+K completo via `fcc_k.lp_fcc_plus_k` (histórico, não alterado) ao longo de 30 instâncias aleatórias geradas, tolerância `1e-6`; nem todas as 30 necessariamente terminam estacionárias (algumas podem interromper por outro motivo e ficam fora da comparação), e o teste exige **no mínimo 25** comparações estacionárias válidas contra o LP completo; `test_path_abc_reaches_one` reproduz o caso de referência da spec (3→1); demais testes de integridade (§4.3 do prompt) cobertos em `test_cycle_integrity_and_current_snapshots`, `test_degenerate_negative_column_is_not_an_error`, `test_duplicate_negative_column_stops_without_loop` |
| P-6 | Versão/parâmetros do Gurobi registrados nas rotas de pricing; toda coluna validada combinatoriamente; raiz, sem branching, sem mudar K | **ATENDIDO** | `gurobi_version`/`parameters` em `PricingResult` e `MasterResult`; `validate_column` chamado em `add_column`, `reduced_cost` e na extração do pricing; ausência de `BINARY`/`INTEGER` no master e no controlador (grep); `self.K`/`self.k_hash` atribuídos uma única vez, sem setter |
| — | Master restrito inicial viável | **ATENDIDO** | Coluna `(V,S,T)` inserida no construtor; `test_path_rmp_three_then_one_is_not_a_lower_bound` e o histórico da N2-T2B confirmam `ObjVal` inicial finito |
| — | Custo reduzido reproduzível | **ATENDIDO** | `DualChecks.max_rc_error` comparando `column_rc`/`direct_rc` contra `Var.RC`; recomputado de novo no controlador e no pricing, com tolerância explícita em cada ponto |
| — | Pricing rotulado `exact`/`heuristic`, resultado rastreável | **ATENDIDO** | `pricing_label='heuristic'` fixo (nenhum oráculo exato implementado nesta entrega — correto, pois ENUM/N1/N2 certificadores são N2-T3); `PricingResult`/`IterationRecord` guardam outcome, termination, status, custo reduzido, bound numérico |
| — | Nenhuma rotina emite `CERTIFIED` sem prova; padrão `UNCERTIFIED` | **ATENDIDO** | §6.4 abaixo |
| — | Integridade da N2-T1 reverificada | **ATENDIDO** | §4 (`run_n2_t1.py check` PASS nesta rodada) |
| — | Testes automatizados correspondentes aprovados | **ATENDIDO** | §7 (87/87 testes, 0 falhas) |

### 6.1 Auditoria master e dual (prompt §4.1)

| Verificação | Status |
|---|---|
| Master inicial viável | **ATENDIDO** |
| Preservação de K e hash | **ATENDIDO** (`k_hash` conferido contra o fornecido; nunca regenerado silenciosamente) |
| Objetivo e restrições corretos | **ATENDIDO** (`min Σy`; R1/R2/R3/K/UB conforme v2.1 §2) |
| Sinais dos multiplicadores | **ATENDIDO** (`π,τ` livres; `μ=-Pi(R3)≥0`; `κ=Pi(K)≥0`) |
| Reconstrução de η | **ATENDIDO** (`η=max(0,μ+κ(v)-1)`) |
| Custo reduzido reproduzível | **ATENDIDO** |
| Snapshot vinculado à resolução | **ATENDIDO** (`StaleDualError` por identidade de objeto) |

### 6.2 Auditoria pricing (prompt §4.2)

| Verificação | Status |
|---|---|
| Correspondência com P0–P5 | **ATENDIDO** |
| Conectividade em H | **ATENDIDO** (fluxo `g,f` sobre `master.reach_graph`) |
| Elegibilidade/balanço de terminais | **ATENDIDO** |
| Validação combinatória de colunas | **ATENDIDO** |
| Rejeição de incumbentes não inteiros | **ATENDIDO** (`INTEGRALITY_TOLERANCE`, testado em `test_nonintegral_incumbent_is_rejected`) |
| Registro de status/versão/parâmetros | **ATENDIDO** |
| Classificação heurística sem certificação indevida | **ATENDIDO** |

### 6.3 Auditoria geração de colunas (prompt §4.3)

| Verificação | Status |
|---|---|
| Execução só na raiz | **ATENDIDO** |
| Integração master+pricing | **ATENDIDO** |
| Reotimização após inserção | **ATENDIDO** |
| Duplicatas/degeneração | **ATENDIDO** |
| Sem snapshot obsoleto | **ATENDIDO** |
| Paradas explícitas | **ATENDIDO** (9 estados) |
| Work/tempo contabilizados | **ATENDIDO** |
| Recursos não mensuráveis tratados | **ATENDIDO** (`WORK_UNMEASURED`, inclusive no último subsolve) |
| Limites globais monitorados, com parada classificada corretamente | **ATENDIDO** (consumo acumulado de Work/tempo é reavaliado após **cada** subsolve, inclusive o último; o restante global é encaminhado como `WorkLimit`/`TimeLimit` de cada chamada; uma ultrapassagem é detectada e classificada como `WORK_LIMIT`/`TIME_LIMIT`, nunca como estacionariedade. Isso não é a mesma coisa que uma garantia absoluta de nunca exceder o orçamento: o Gurobi pode extrapolar um `WorkLimit`/`TimeLimit` por chamada antes de retornar o controle ao Python, e o controlador só consegue agir — descartando o resultado e classificando a parada — depois que o subsolve termina) |
| Sem branching/corte novo | **ATENDIDO** |

### 6.4 Política de certificação (prompt §4.4, obrigatório)

| Verificação | Status |
|---|---|
| Objetivo RMP não publicado como LB certificado | **ATENDIDO** (`rmp_objective`; nenhum campo `lb`/`lower_bound`; testado por `assert_uncertified` em todos os 27 testes) |
| `ObjBound`/`ObjBoundC` não tratados como certificado | **ATENDIDO** (`solver_bound` é só diagnóstico; `test_solver_bound_never_blocks_a_negative_column`, `test_nonnegative_interrupted_pricing_is_not_stationary`) |
| `GRB.OPTIMAL` não implica `CERTIFIED` | **ATENDIDO** (`test_optimal_is_never_certified_and_bound_is_diagnostic`, `test_stationary_is_numeric_only`) |
| Estacionariedade numérica não é convergência certificada | **ATENDIDO** (`convergence_status=NUMERIC_UNCERTIFIED`, nunca `CERTIFIED`) |
| `UNCERTIFIED` na ausência de prova | **ATENDIDO** (default de dataclass + checagem defensiva no controlador) |
| Interrupções não geram certificado fictício | **ATENDIDO** (`test_interrupted_*`, `test_work_overrun_is_never_stationary`, `test_time_overrun_after_last_pricing_is_not_stationary`) |

**Conforme instruído, a ausência de ENUM/N1/N2 e do critério G2 nesta entrega não reprova o Gate O**: nenhum
teste exige certificação; todos exigem precisamente o oposto (ausência de certificação indevida).

## 7. Resultados reais dos testes (reexecutados nesta avaliação)

Ambiente: Gurobi 12.0.3, `PYTHONHASHSEED=0`, venv do projeto.

| Suíte | Testes | Falhas | Erros | Skipped |
|---|---:|---:|---:|---:|
| `test_n2_t2b_master.py` | 15 | 0 | 0 | 0 |
| `test_n2_t2b_pricing.py` | 20 | 0 | 0 | 0 |
| `test_n2_t2b_column_generation.py` | 27 | 0 | 0 | 0 |
| `test_n2_t2b_controles_matematicos.py` | 18 | 0 | 0 | 0 |
| `test_n2_t1_offline.py` | 7 | 0 | 0 | 0 |
| **Total** | **87** | **0** | **0** | **0** |

Verificadores:

```text
PYTHONHASHSEED=0 python experiments/alternative-formulations/run_n2_t1.py check
PASS: N2-T1 freeze íntegro; caminho B; 2 famílias x 2 níveis; orçamento total 164 Work

PYTHONHASHSEED=0 python experiments/alternative-formulations/verify_n1_t7_gate.py
PASS: N1-T5 = 18; N1-T6 = 6; cadeia de hashes íntegra; MR-F3 aceito
DECISÃO N1-T7: PROMOTE FCC + EXISTING CUTS
N2: caminho B — F-CC + K (apenas raiz; implementação ainda não iniciada)
```

Ruff (6 arquivos, 3 módulos + 3 suítes de teste): `All checks passed!`

**Nota sobre o texto fixo do verificador N1-T7:** a linha `implementação ainda não iniciada` é um literal do
script histórico `verify_n1_t7_gate.py` (não alterado por nenhuma entrega da N2-T2B) e não reflete o estado da
N2-T2B; não é um sinal de regressão, é texto desatualizado de um artefato que esta avaliação não tem mandato
para editar.

A comparação do item P-2 é **regressão numérica contra o LP F-CC+K completo histórico**, não a campanha
prospectiva dos 23 controles N1 (reservada à N2-T4) nem medição N2-T5; nenhuma das duas foi executada aqui.

## 8. Pendências identificadas

Nenhum defeito bloqueante foi encontrado nesta avaliação. Pendências não bloqueantes, já documentadas nas
entregas anteriores e aqui reconfirmadas:

| # | Pendência | Criticidade | Etapa de destino |
|---|---|---|---|
| 1 | Work contabilizado exclui preparação fora do Gurobi (cálculo de K, alcance, montagem do modelo); só aparece no tempo de parede | Não bloqueante | Decisão de protocolo para N2-T5 |
| 2 | Custo de remontar o MIP de pricing a cada iteração não medido em escala (nível 2) | Não bloqueante | N2-T5 |
| 3 | Texto fixo desatualizado em `verify_n1_t7_gate.py` ("implementação ainda não iniciada") | Cosmético | Não requer ação da N2-T2B |

## 9. Limitações matemáticas reservadas à N2-T3 (não avaliadas, por definição de escopo)

- P-1: contrato ENUM (vetor racional exato, cobertura íntegra, exportação para baixo) — não implementado, correto para esta etapa.
- P-3: bounds globais verificáveis N1/N2 — não implementados.
- P-4: `U` primal validado para o critério G2 — não implementado.
- P-5: registro do hash de K e de `assert_valid_cuts` no certificado por instância — não implementado.
- P-7: certificação de `B0` em campo próprio — não implementado.
- P-8: regressão prospectiva nos 23 controles N1 — não executada (N2-T4).

Nenhum destes bloqueia o Gate O, conforme §11.2 da revisão v2.1.

## 10. Recomendação técnica

**`APTO PARA ACEITE`**

Fundamentação: todos os itens de P-2, P-6 e dos critérios adicionais do §11.2 foram verificados com evidência de
código e de teste reexecutado nesta avaliação (não apenas herdada); 87 de 87 testes aprovados, 0 falhas/erros/
skips; Ruff limpo nos 6 arquivos; integridade N1/N2-T1 confirmada sem reconstrução do freeze; nenhuma rota do
código emite `CERTIFIED` nem confunde `z_R`/`ObjBound`/`ObjBoundC`/`GRB.OPTIMAL` com certificação; nenhum
branching, corte novo ou alteração de K; nenhuma pendência bloqueante.

As três pendências do §8 são de escopo e desempenho, não de corretude, e já têm etapa de destino definida pela
própria revisão v2.1 (N2-T3/N2-T4/N2-T5).

**Esta é a fundamentação técnica do aceite;** a decisão humana correspondente está registrada
separadamente na §11, conforme §12.2 da revisão matemática v2.1.

## 11. Decisão formal do responsável — Gate O encerrado

| Campo | Registro |
|---|---|
| Tipo | Aceite operacional de código já implementado (Gate O) |
| Decisão | **`APROVADO PARA PROSSEGUIR À N2-T3`** |
| Responsável | Pesquisador responsável pelo projeto MIN-STATION, que solicitou o fechamento nesta conversa; nome e assinatura digital não foram atribuídos por inferência |
| Data da decisão | **2026-10-09**, America/Sao_Paulo (hora exata não incorporada à evidência) |
| Manifestação de autorização | Solicitação do responsável nesta conversa: **“me de necessário ajustado para o fechamento”**, após receber o parecer `APTO PARA ACEITE` e as instruções para concluir o Gate O |
| Commit exato da implementação aceita | **`d6d9517e484ee965c556ea228e0020bc624400e3`** — HEAD do código avaliado no registro técnico (§1); não é o commit futuro deste próprio documento |
| Evidência técnica | Critérios P-2 e P-6 atendidos (§6); **87/87 testes** e Ruff sem falhas registrados na avaliação (§7); Gate M e freeze N2-T1 íntegros (§§1–4) |
| Ressalvas / condições | Manter as três pendências não bloqueantes do §8 no escopo de destino; todos os resultados atuais são **`UNCERTIFIED`**; não tratar `z_R`, `ObjBound`/`ObjBoundC` ou `GRB.OPTIMAL` como certificado; N2-T3 permanece responsável pelos critérios P-1/P-3/P-4/P-5/P-7 |
| Resultado do Gate O | **`ENCERRADO — APROVADO`** para iniciar o trabalho da N2-T3 |

**Alcance da decisão.** O aceite confirma a conformidade operacional da implementação
N2-T2B no commit acima, com base nas evidências relatadas na avaliação técnica. Não
atesta, por si só, que os testes foram reexecutados no momento desta decisão; os
resultados continuam identificados com a avaliação da §7. Não constitui aprovação de
limites inferiores certificados, nem demonstração de convergência pelo critério G2.

**Próxima etapa autorizada:** iniciar a **N2-T3 — Certificação Rigorosa dos Limites
Inferiores**, respeitando o pré-registro e a matemática v2.1. Esta autorização de
prosseguimento não conclui automaticamente a N2-T3, não autoriza medições N2-T5,
não substitui a regressão N2-T4 nem o gate científico N2-T6. A revisão matemática,
o parecer, o freeze, K e os arquivos históricos permanecem inalterados.
