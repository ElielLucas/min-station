# FC-04 — Identidade de instâncias, integridade e relatórios — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implementar com `/tlc-spec-driven` ativado, seguindo os gates dos scripts originais e verificador independente (autor ≠ verificador). **Este arquivo é planejamento, não representa execução.** Não modificar branch remoto, não criar PR/push; commits locais somente mediante autorização específica do usuário.

**Spec:** `specs/fc-04-integridade-manifesto-e-relatorios/spec.md`  
**Design:** `specs/fc-04-integridade-manifesto-e-relatorios/design.md`  
**Status:** implementação local realizada; homologação integrada pendente (consulte `validation.md`)  
**Pré-requisito externo:** FC-01, FC-02 e FC-03 (schema final)

## Test Coverage Matrix

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
|---|---|---|---|---|
| Domínio/controle de comparativo | unit | Cada AC e todos os estados adversos, inclusive abstenções | `experiments/formulation-comparison/test_comparison.py` e `test_*.py` da nova feature | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v` |
| Certificação racional (se aplicável) | unit/integration | Cada prova verificada e contraexemplo pequeno | `experiments/alternative-formulations/test_n2_t3_*.py` e `test_diagnose_*.py` | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_*.py' -v` |
| CLI/arquivo gerado | integration | Testes de timeout, cap, hash e round-trip de manifesto sem solver quando possível | `experiments/formulation-comparison/test_comparison.py` | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v` |
| Configuração e documentação | static | Validadores de specs e Ruff; sem afirmar que documento testa código | `specs/fc-04-integridade-manifesto-e-relatorios/*.md` | `python -m ruff check experiments/formulation-comparison experiments/alternative-formulations` (escopo de arquivos alterados se legado tiver pendências) |

## Gate Check Commands

| Gate Level | When to Use | Command |
|---|---|---|
| Quick | Após cada task | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_comparison.py' -v` (ou suíte específica do módulo alterado) |
| Full | Fim de fase | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/formulation-comparison -p 'test_*.py' -v`; quando certificar, também suites N2-T3/E5 afetadas |
| Regression | Mudança na N2 opt-in | `PYTHONHASHSEED=0 python -m unittest discover -s experiments/alternative-formulations -p 'test_n2_t3_cert_*.py' -v` e testes N2-T2B afetados |
| Build | Fim de fase | `python -m ruff check` nos scripts alterados e `python -m py_compile` desses scripts |
| Structural | Antes da aprovação e no fim | `python .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/fc-04-integridade-manifesto-e-relatorios/spec.md --strict` + `validate_tasks.py specs/fc-04-integridade-manifesto-e-relatorios/tasks.md --strict` |
| Complete | Só ao declarar implementada | Verifier independente + `validation.md` com referências arquivo:linha; depois `validate_state.py` se a feature estiver registrada na convenção `.specs/features/` da skill |

Os comandos que usam Gurobi devem ser executados no ambiente do projeto com licença; sem Gurobi, registrar bloqueio, nunca declarar PASS.

## Execution Plan

Phases ordered sequentially; tasks are atomic. A tarefa seguinte só começa após o gate da anterior.

### Phase 1 — Contrato e fundamento

```text
T1 -> T2
```

### Phase 2 — Integração e publicação

```text
T2 -> T3 -> T4
```

## Task Breakdown

### T1: Verificar bytes e metadados no carregamento

**What:** Recalcular SHA e comparar n,m,r com o manifesto onde suportado.  
**Where:** `experiments/formulation-comparison/fc_instances.py`  
**Depends on:** None  
**Reuses:** Código existente identificado em `design.md`; não recriar as formulações.  
**Requirement:** AUDIT-01; e demais ACs relevantes de `spec.md`.  
**Tools:** skill `/tlc-spec-driven` e `/karpathy-guidelines`; Python, Gurobi quando aplicável.  
**Done when:**
- [ ] Entrega única implementada exatamente conforme o contrato dos ACs.
- [ ] Testes independentes negativos/positivos passando, sem remover testes existentes.
- [ ] Evidência local reproduzível com referência de arquivo e linha.

**Tests:** unit: instância adulterada e metadata mismatch. Criar/atualizar `test_comparison.py` ou teste co-localizado do novo módulo na MESMA tarefa.  
**Gate:** Quick após task; Full + Ruff ao fim da fase.

### T2: Completar manifesto de código e dados

**What:** Inventariar módulos fc, códigos de modelo e arquivos emitidos.  
**Where:** `experiments/formulation-comparison/fc_reporting.py`  
**Depends on:** T1  
**Reuses:** Código existente identificado em `design.md`; não recriar as formulações.  
**Requirement:** AUDIT-02; e demais ACs relevantes de `spec.md`.  
**Tools:** skill `/tlc-spec-driven` e `/karpathy-guidelines`; Python, Gurobi quando aplicável.  
**Done when:**
- [ ] Entrega única implementada exatamente conforme o contrato dos ACs.
- [ ] Testes independentes negativos/positivos passando, sem remover testes existentes.
- [ ] Evidência local reproduzível com referência de arquivo e linha.

**Tests:** unit: digests reproducíveis e referências sem caminhos absolutos. Criar/atualizar `test_comparison.py` ou teste co-localizado do novo módulo na MESMA tarefa.  
**Gate:** Quick após task; Full + Ruff ao fim da fase.

### T3: Implementar auditor read-only

**What:** Recalcular bytes e apontar divergências, sem reexecutar solver.  
**Where:** `experiments/formulation-comparison/verify_comparison_artifacts.py`  
**Depends on:** T2  
**Reuses:** Código existente identificado em `design.md`; não recriar as formulações.  
**Requirement:** AUDIT-04; e demais ACs relevantes de `spec.md`.  
**Tools:** skill `/tlc-spec-driven` e `/karpathy-guidelines`; Python, Gurobi quando aplicável.  
**Done when:**
- [ ] Entrega única implementada exatamente conforme o contrato dos ACs.
- [ ] Testes independentes negativos/positivos passando, sem remover testes existentes.
- [ ] Evidência local reproduzível com referência de arquivo e linha.

**Tests:** unit: byte adulterado, arquivo ausente, manifesto truncado. Criar/atualizar `test_comparison.py` ou teste co-localizado do novo módulo na MESMA tarefa.  
**Gate:** Quick após task; Full + Ruff ao fim da fase.

### T4: Corrigir conclusões da sondagem

**What:** Recalcular totais por linhas medidas e remover universais não sondados.  
**Where:** `docs/technical/plans/execucao/formulation-comparison-protocolo.md`  
**Depends on:** T3  
**Reuses:** Código existente identificado em `design.md`; não recriar as formulações.  
**Requirement:** AUDIT-05; e demais ACs relevantes de `spec.md`.  
**Tools:** skill `/tlc-spec-driven` e `/karpathy-guidelines`; Python, Gurobi quando aplicável.  
**Done when:**
- [ ] Entrega única implementada exatamente conforme o contrato dos ACs.
- [ ] Testes independentes negativos/positivos passando, sem remover testes existentes.
- [ ] Evidência local reproduzível com referência de arquivo e linha.

**Tests:** review + test: 9/10 sob dataset fornecido e 75 não provados. Criar/atualizar `test_comparison.py` ou teste co-localizado do novo módulo na MESMA tarefa.  
**Gate:** Quick após task; Full + Ruff ao fim da fase.


## Task Granularity / Coverage Check

| Task | Single primary file | Tests co-located | Gate |
|---|---|---|---|
| T1 | um arquivo principal | sim, na mesma tarefa | Quick/Full conforme fase |
| T2 | um arquivo principal | sim, na mesma tarefa | Quick/Full conforme fase |
| T3 | um arquivo principal | sim, na mesma tarefa | Quick/Full conforme fase |
| T4 | um arquivo principal | sim, na mesma tarefa | Quick/Full conforme fase |

## Traceability Cross-Check

- Todos os IDs `AUDIT-NN` de `spec.md` devem ser cobertos pelos testes listados por AC antes do aceite; a linha `Requirement` por task indica o grupo âncora e **não** dispensa testar os demais ACs.
- A única dependência intrafase é uma cadeia sucessiva; o diagrama da própria fase contém todos os arcos `Depends on` que caem na mesma fase.
- O verificador deve comparar a entrega final contra requisitos, e não inferir sucesso da existência de arquivos.
