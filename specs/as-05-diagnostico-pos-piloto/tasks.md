# AS05-DIAG — Diagnóstico pós-piloto — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Aplicar `/tlc-spec-driven`; preservar originais e commits históricos. Implementação local e testes antes de campanha; não fazer push. Revisor independente após execução científica, autor distinto de verificador.

**Status:** Código preparado e testes locais; solves diagnósticos Gurobi pendentes.  
**Spec:** `specs/as-05-diagnostico-pos-piloto/spec.md`  
**Design:** `specs/as-05-diagnostico-pos-piloto/design.md`

## Test Coverage Matrix

| Camada | Testes exigidos | Resultado esperado |
|---|---|---|
| K | igual SHA, corte inválido falha, tempos separados | K equivalente |
| Modelo | compiladores AS02 originais, U sem K | same LP model |
| Integração | 2×3, 4×4, orçamento, falhas, checkpoints | sem perda de braço |
| Relatório | hashes, conteúdo consistente, sem `GO` | auditável |

## Gate Check Commands

| Gate | Comando / procedimento |
|---|---|
| Spec | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-05-diagnostico-pos-piloto/spec.md --strict` |
| Tasks | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-05-diagnostico-pos-piloto/tasks.md --strict` |
| Quick | `PYTHONHASHSEED=0 PYTHONPATH=. poetry run python -m unittest discover -s experiments/formulation-comparison -p 'test_as05_diag.py' -v` |
| Full | Quick + regressões AS04, AS05, AS02, AS03 e `poetry run ruff check` nos novos módulos |
| Commit | `git commit -m 'feat(as05): prepara diagnostico pos-piloto de cortes e agrupamentos'` |

## Execution Plan

```
T1 -> T2 -> T3 -> T4 -> T5
```

## Task Breakdown

### T1: Congelar plano diagnóstico vinculado ao piloto

**What:** Planejar `cuts/censored/grouping`, instâncias, budgets, políticas, hashes.  
**Where:** `as05_diag_core.py`  
**Depends on:** None  
**Requirement:** AS05D-01  
**Done when:**

- [x] Plano reproduzido com mesmo SHA a partir do piloto real.
- [x] Mutação dos parâmetros é rejeitada.
- [ ] Revalidado no ambiente do pesquisador.

**Tests:** `test_plan_is_bound_to_original_report`.  
**Gate:** quick

### T2: Instrumentar e preservar os cortes K

**What:** Separar subfases K e reutilizar N+/N− sem desativar validação.  
**Where:** `as05_diag_core.py`  
**Depends on:** T1  
**Requirement:** AS05D-02, AS05D-03  
**Done when:**

- [x] K igual ao legado no controle racional pequeno.
- [x] U não executa K; timeout `k_*` é preparação.
- [ ] Perfil real Gurobi/CPU executado.

**Tests:** `test_k_cached_has_exact_legacy_hash`, `test_u_never_calls_k`.  
**Gate:** quick

### T3: Preparar reensaio dos casos censurados

**What:** 300 s por braço, sem substituir a rodada original.  
**Where:** `run_as05_diagnostics.py`  
**Depends on:** T2  
**Requirement:** AS05D-04, AS05D-06  
**Done when:**

- [x] Matriz 2×3 e checkpoints por braço conferidos artificialmente.
- [x] Resume rejeita adulteração e preserva trabalho concluído.
- [ ] 2×3 execuções Gurobi concluídas/censuradas no novo relatório.

**Tests:** `test_censored_and_grouping_full_pipeline`, `test_corrupted_checkpoint_blocks_resume`.  
**Gate:** quick

### T4: Comparar agrupamentos no desenvolvimento

**What:** Três políticas determinísticas, U_K novo em cada caso.  
**Where:** `as05_diag_core.py`  
**Depends on:** T3  
**Requirement:** AS05D-05, AS05D-08  
**Done when:**

- [x] Partições independentes da ordem, sem consultar LP.
- [x] K distinto invalida comparação.
- [ ] 4×4 execuções Gurobi no novo relatório.

**Tests:** `test_preselected_policies_are_deterministic`, `test_different_k_hash_refuses_pair`.  
**Gate:** quick

### T5: Consolidar e interpretar sem promoção automática

**What:** Integridade, métricas por fase, deltas, censuras e indicação exploratória.  
**Where:** `as05_diag_analysis.py`  
**Depends on:** T4  
**Requirement:** AS05D-07  
**Done when:**

- [x] Consolidação produz JSON/CSV/Markdown em testes artificiais.
- [x] Nenhum `GO` científico é emitido.
- [ ] Relatório diagnóstico real emitido e interpretado.

**Tests:** `test_complete_analysis_exploratory_no_promotion`.  
**Gate:** full

## Phase Execution Map

```
T1 -> T2 -> T3 -> T4 -> T5
```

**Cross-check:** todas as dependências apontam para a tarefa anterior; nenhum resultado histórico é sobrescrito.

## Closing Verification

- [ ] Testes e Ruff reexecutados no Poetry do pesquisador.
- [ ] Os três estágios produzem manifestos válidos e logs reais.
- [ ] Verificador independente avalia rigor científico após campanha.
