# AS29 — Tasks

## Execution Protocol

Executar com a skill `/tlc-spec-driven`, seguindo Specify, Design, Tasks e Execute. **Esta entrega produz somente o planejamento; nenhuma tarefa foi executada.** Cada tarefa futura deve ser testada e concluída com commit atômico após validação, com Verifier independente ao final. Não fazer push sem autorização explícita.

**Spec:** `specs/as-29-yrbc-reconciliacao-lb-opt/spec.md`
**Design:** `specs/as-29-yrbc-reconciliacao-lb-opt/design.md`
**Estado:** DRAFT; **pré-condição:** AS28 encerrada; não depende de Y-RBC matematicamente válido.

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
| Spec | Antes de aprovar requisitos | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-29-yrbc-reconciliacao-lb-opt/spec.md --strict` |
| Tasks | Antes de aprovar tarefas | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-29-yrbc-reconciliacao-lb-opt/tasks.md --strict` |
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

### T1: Construir inventário de fontes

**What:** Localizar CSVs/JSONs/logs; associar hashes, código, versão e parâmetros; teste de unicidade da identidade de caso.
**Where:** `docs/technical/reference/experimentos/as29-envelope-proveniencia.csv`
**Depends on:** None
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR29-01
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Quick
**Commit sugerido:** `docs(as29): construir inventário de fontes`

### T2: Auditar limites e incumbentes

**What:** Recalcular envelope sem usar incumbente do núcleo como UB; checagem manual amostral de origens.
**Where:** `docs/technical/reference/experimentos/as29-envelope-lb-opt.md`
**Depends on:** T1
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR29-02
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Quick
**Commit sugerido:** `docs(as29): auditar limites e incumbentes`

### T3: Registrar divergências e erratas

**What:** Resolver CC9 e inconsistências reportadas; não mutar dados primários.
**Where:** `docs/technical/reference/experimentos/as29-erratas-e-incompatibilidades.md`
**Depends on:** T2
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR29-03, YR29-04
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Quick
**Commit sugerido:** `docs(as29): registrar divergências e erratas`

### T4: Revisar decisão e liberar G0

**What:** Parecer independente e tabela reconciliada para casos de desenvolvimento.
**Where:** `docs/technical/reference/experimentos/as29-envelope-lb-opt.md`
**Depends on:** T3
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR29-05, YR29-06
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Full
**Commit sugerido:** `docs(as29): revisar decisão e liberar g0`

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

- **G0 — Fontes reconciliadas:** G0 PASS: 100% dos casos de desenvolvimento usados nos futuros gates com hash, LB fonte, UB fisicamente validado e classe de status; divergências explicitamente abertas ou resolvidas; CC9 contextualizada. G0 BLOCKED se não houver rastro de proveniência suficiente.
- A etapa seguinte depende de aprovação explícita do gate. Não criar `validation.md` até existir evidência; o Verifier deve ser outro agente.
- Nenhuma execução ou commit acontece na entrega destas specs.
