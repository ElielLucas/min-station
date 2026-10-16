# AS19 — Tasks

## Test Coverage Matrix

| Requisitos | Tipo | Verificação | Situação |
|---|---|---|---|
| AS19-01 | review | Histórico AS18 e exceção AS19 | Documentado |
| AS19-02–06 | unit | `test_hl_local.py` | Pass |
| AS19-07–08 | integration | `run_hl_micro.py`, K4 SciPy e evidência JSON | Pass |
| AS19-09 | review | `as19-hl-independente-microtriagem.md` | Pass |
| AS19-10 | review futuro | Novo plano real | Pendente |

## Gate Check Commands

```bash
python -m unittest discover -s experiments/cuts -p 'test_hl_local.py' -q
python -m unittest discover -s experiments/cuts -p 'test_*.py' -q
python .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-19-hl-independente/spec.md
python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-19-hl-independente/tasks.md
```

## Execution Plan

### Phase 1: Protocolo independente e microprova

T1 → T2 → T3 → T4. Cada entrega fica em um arquivo principal; os testes localizados acompanham a camada correspondente.

## Task Breakdown

### T1: Autorizar investigação independente HL

**Where:** `specs/as-19-hl-independente/spec.md`  
**Depends on:** none  
**Tests:** review — decisões e scopes de AS18 preservados  
**Gate:** revisão da autorização e premissas

- [x] Hipótese e autorização HL independentes de H2.
- [x] Histórico AS16 STOP / AS17 NOT_AUTHORIZED / AS18 NOT_AUTHORIZED preservado.
- [x] Escopo K4 e orçamento definidos antes do micro-piloto.

### T2: Certificar HL por padrões físicos

**Where:** `experiments/cuts/hl_local.py`  
**Depends on:** T1  
**Tests:** unit — `test_hl_local.py` valida UNKNOWN, complemento, β e budgets  
**Gate:** todos os testes de HL local passam

- [x] Enumerar suporte total, `β` racional exato, hashes e relatório append-only.
- [x] Abster-se com UNKNOWN/budget/tamanho acima do limite.
- [x] Validar coeficientes não negativos e entradas.

### T3: Executar micro-piloto LP K4

**Where:** `experiments/cuts/run_hl_micro.py`  
**Depends on:** T2  
**Tests:** integration — `test_comp_k_h2_hl_lp_hierarchy_from_actual_models`  
**Gate:** limites LP `2`, `8/3`, `3` e JSON emitido

- [x] Comparar COMP+K, quatro H2 e HL sobre o mesmo K4 compilado.
- [x] Registar tempos, hashes e chamadas do oráculo.
- [x] Não atribuir resultados sintéticos a instâncias reais.

### T4: Publicar síntese e próximos gates

**Where:** `docs/technical/reference/experimentos/as19-hl-independente-microtriagem.md`  
**Depends on:** T3  
**Tests:** review — separar prova, LP sintético e benefício real desconhecido  
**Gate:** documentação e validação completa da suíte de cortes

- [x] Relatório sintético e próximos critérios.
- [ ] Parecer científico humano independente (pendente).
- [ ] Protocolo de benchmarking real (etapa futura).

## Phase Execution Map

```text
T1 -> T2 -> T3 -> T4
```

**Estado:** T1–T3 verificados; T4 documentada, com parecer humano e experimento real explicitamente pendentes. Não houve GO real nem commit local executado pelo assistente.
