# AS33 — Tasks

## Execution Protocol

Executar com a skill `/tlc-spec-driven`, seguindo Specify, Design, Tasks e Execute. **Esta entrega produz somente o planejamento; nenhuma tarefa foi executada.** Cada tarefa futura deve ser testada e concluída com commit atômico após validação, com Verifier independente ao final. Não fazer push sem autorização explícita.

**Spec:** `specs/as-33-yrbc-piloto-integrado/spec.md`
**Design:** `specs/as-33-yrbc-piloto-integrado/design.md`
**Estado:** DRAFT; **pré-condição:** AS32/G2b GO aprovado; validação matemática AS30 continua válida.

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
| Spec | Antes de aprovar requisitos | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-33-yrbc-piloto-integrado/spec.md --strict` |
| Tasks | Antes de aprovar tarefas | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-33-yrbc-piloto-integrado/tasks.md --strict` |
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
T2 -> T3 -> T4
```

Fases sequenciais; as dependências entre fases são indicadas no campo de cada tarefa.

## Task Breakdown

### T1: Instrumentar telemetria

**What:** Campos e serialização validados sob status ótimo/timeout/erro.
**Where:** `experiments/yrbc/yrbc_telemetry.py`
**Depends on:** None
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR33-01, YR33-03
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as33): instrumentar telemetria`

### T2: Preparar runner piloto

**What:** Processos isolados e orçamento verificável, sem consumo de reserva; testes pareados.
**Where:** `experiments/yrbc/run_as33_pilot.py`
**Depends on:** T1
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR33-01, YR33-02
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as33): preparar runner piloto`

### T3: Montar regressão de integração

**What:** Mutantes BF/BR, timeout, solução inválida, memória e certificados detectados.
**Where:** `experiments/yrbc/test_as33_integration.py`
**Depends on:** T2
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR33-02, YR33-03, YR33-04
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as33): montar regressão de integração`

### T4: Executar piloto e verificação independente

**What:** Relatório com ablações, variância, status e decisão explícita G3.
**Where:** `docs/technical/reference/experimentos/as33-piloto-yrbc.md`
**Depends on:** T3
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR33-04, YR33-05
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Full
**Commit sugerido:** `docs(as33): executar piloto e verificação independente`

## Phase Execution Map

```text
Phase 1 + Phase 2: T1 -> T2 -> T3 -> T4
```

## Task Granularity Check

| Tarefa | Escopo | Verificação |
|---|---|---|
| T1 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T2 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T3 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |
| T4 | Um artefato/arquivo principal | Coeso; testes ficam com a implementação |

## Diagram-Definition Cross-Check

| Aresta da fase | Depends on de destino | Estado |
|---|---|---|
| T1 -> T2 | T2 depende T1 | OK |
| T3 -> T4 | T4 depende T3 | OK |

## Test Co-location Validation

| Camada | Regra | Estado planejado |
|---|---|---|
| Código | Criar testes no mesmo commit da função/runner | Obrigatório |
| Relatório | Auditar fonte primária antes de declarar PASS | Obrigatório |

## Dependência externa e decisão de gate

- **G3 — Integração estável:** G3 PASS somente com zero incumbente fisicamente inválida, zero corte errado, saída reproduzível e trace completo para todos os casos concluídos; tempo callback conhecido e guardas auditadas. G3 BLOCKED com falha de corretude ou registros incompletos; resultado computacional ruim é STOP científico, não bug encoberto.
- A etapa seguinte depende de aprovação explícita do gate. Não criar `validation.md` até existir evidência; o Verifier deve ser outro agente.
- Nenhuma execução ou commit acontece na entrega destas specs.
