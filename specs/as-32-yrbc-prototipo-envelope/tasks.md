# AS32 — Tasks

## Execution Protocol

Executar com a skill `/tlc-spec-driven`, seguindo Specify, Design, Tasks e Execute. **Esta entrega produz somente o planejamento; nenhuma tarefa foi executada.** Cada tarefa futura deve ser testada e concluída com commit atômico após validação, com Verifier independente ao final. Não fazer push sem autorização explícita.

**Spec:** `specs/as-32-yrbc-prototipo-envelope/spec.md`
**Design:** `specs/as-32-yrbc-prototipo-envelope/design.md`
**Estado:** DRAFT; **pré-condição:** AS29 PASS; AS30 PASS; AS31 GO aprovado; gate da arquitetura aprovado.

## Test Coverage Matrix

> Derivada dos requisitos, da suíte `unittest` do projeto e dos comandos usados nas campanhas AS anteriores. Limiar: cobrir todas as cláusulas de aceite e todos os estados de erro. Documentos usam checagem de fonte/cálculo independente.

| Camada | Testes | Cobertura esperada | Localização | Comando |
|---|---|---|---|---|
| Formulação, prova e relatórios | revisão independente | Evidência rastreável por afirmação, prova e contraprova | `docs/technical/` | conferência manual + auditor independente |
| Funções matemáticas / oráculo | unitário + micro exaustivo | Todos ACs, terminais, cortes inválidos, gêmeos e mutantes | `experiments/yrbc/test_*.py` | `poetry run python -m unittest discover -s experiments -p "test_*.py" -q` (confirmar escopo no ambiente) |
| Runner, parser e analisador | unitário + integração | Hash inválido, fonte incompleta, dry-run, censura e classificação | `experiments/yrbc/test_*.py` | `poetry run python -m unittest discover -s experiments/cuts -p "test_*.py" -q` + testes novos |
| Artefatos de experimento | protocolo + reprodução | Pairing, orçamento/seed/status e imutabilidade da saída | `results/benchmark/` | script de validação e verificador independente |

## Gate Check Commands

| Gate | Quando | Comando |
|---|---|---|
| Spec | Antes de aprovar requisitos | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-32-yrbc-prototipo-envelope/spec.md --strict` |
| Tasks | Antes de aprovar tarefas | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-32-yrbc-prototipo-envelope/tasks.md --strict` |
| Quick | Após alteração de código matemático | `poetry run python -m unittest discover -s experiments/cuts -p "test_*.py" -q` + teste AS específico |
| Full | Antes de gate científico | suíte completa aplicável, microtestes e verificador independente |
| Build | Cada commit futuro | `git diff --check` e validação de arquivos experimentais |

## Execution Plan

### Phase 1: Preparação

```text
T1 -> T2
```

### Phase 2: Evidências e decisão

```text
T2 -> T3 -> T4 -> T5
```

Fases sequenciais; as dependências entre fases são indicadas no campo de cada tarefa.

## Task Breakdown

### T1: Criar contrato do oráculo de cortes

**What:** BF/BR certificados e casos S∩T, m=1, y=0 e erros com testes no mesmo task.
**Where:** `experiments/yrbc/yrbc_cut_oracle.py`
**Depends on:** None
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR32-01, YR32-02, YR32-03
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as32): criar contrato do oráculo de cortes`

### T2: Implementar solver y-space

**What:** MIPSOL/MIPNODE, guardas seguras, status/censura e testes de mutantes.
**Where:** `experiments/yrbc/yrbc_solver.py`
**Depends on:** T1
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR32-01, YR32-02, YR32-03
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as32): implementar solver y-space`

### T3: Implementar primal de reparação

**What:** Starts pequenos, reparação Hall e validação independente; testes de correção.
**Where:** `experiments/yrbc/yrbc_primal.py`
**Depends on:** T2
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR32-05
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as32): implementar primal de reparação`

### T4: Construir runner e ablação

**What:** Pareamento e logs por seed/budget; testes de regressão e comparação.
**Where:** `experiments/yrbc/run_as32_envelope.py`
**Depends on:** T3
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR32-04, YR32-05
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as32): construir runner e ablação`

### T5: Rodar triagem e revisar G2b

**What:** Registrar não inferioridade/ganho, callbacks, memória e status; parecer independente.
**Where:** `docs/technical/reference/experimentos/as32-yrbc-envelope.md`
**Depends on:** T4
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR32-06
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Full
**Commit sugerido:** `docs(as32): rodar triagem e revisar g2b`

## Phase Execution Map

```text
Phase 1 + Phase 2: T1 -> T2 -> T3 -> T4 -> T5
```

## Task Granularity Check

| Tarefa | Escopo | Verificação |
|---|---|---|
| T1 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T2 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T3 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T4 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T5 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |

## Diagram-Definition Cross-Check

| Aresta da fase | Depends on de destino | Estado |
|---|---|---|
| T1 -> T2 | T2 depende T1 | OK |
| T3 -> T4 | T4 depende T3 | OK |
| T4 -> T5 | T5 depende T4 | OK |

## Test Co-location Validation

| Camada | Regra | Estado planejado |
|---|---|---|
| Código | Criar testes no mesmo commit da função/runner | Obrigatório |
| Relatório | Auditar fonte primária antes de declarar PASS | Obrigatório |

## Dependência externa e decisão de gate

- **G2b — Potencial frente ao envelope:** G2b GO_CANDIDATE_REVIEW: ao menos 2 grafos brutos independentes com melhoria verificável em bound/UB/tempo frente ao melhor comparador PAREADO, nenhum erro de viabilidade, callback medianamente <50% do tempo e cobertura suficiente; exigir não regressão em ≥4/6 comparáveis como critério secundário, não teto absoluto de LB* de outra execução. STOP se custo de callback >50% sistematicamente, nenhum ganho e retrocesso em ≥3 casos; INCONCLUSIVE se tempo/variância impedirem atribuição.
- A etapa seguinte depende de aprovação explícita do gate. Não criar `validation.md` até existir evidência; o Verifier deve ser outro agente.
- Nenhuma execução ou commit acontece na entrega destas specs.
