# AS31 — Tasks

## Execution Protocol

Executar com a skill `/tlc-spec-driven`, seguindo Specify, Design, Tasks e Execute. **Esta entrega produz somente o planejamento; nenhuma tarefa foi executada.** Cada tarefa futura deve ser testada e concluída com commit atômico após validação, com Verifier independente ao final. Não fazer push sem autorização explícita.

**Spec:** `specs/as-31-yrbc-reducoes-preprocessamento/spec.md`
**Design:** `specs/as-31-yrbc-reducoes-preprocessamento/design.md`
**Estado:** DRAFT; **pré-condição:** AS29/G0 PASS; AS30/G1 PASS; autorização explícita do pesquisador para campanha.

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
| Spec | Antes de aprovar requisitos | `python3 .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-31-yrbc-reducoes-preprocessamento/spec.md --strict` |
| Tasks | Antes de aprovar tarefas | `python3 .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-31-yrbc-reducoes-preprocessamento/tasks.md --strict` |
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

### T1: Congelar pré-registro de G2a

**What:** Garantir partição, seeds, WorkLimit, hashes e métrica alvo antes de solve.
**Where:** `docs/technical/plans/execucao/as31-preregistro-dominancia.json`
**Depends on:** None
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR31-03
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Quick
**Commit sugerido:** `docs(as31): congelar pré-registro de g2a`

### T2: Criar executor pareado

**What:** Implementar 3 braços controlados e guardas de consistência de fixações; testes junto do código.
**Where:** `experiments/yrbc/run_as31_reductions.py`
**Depends on:** T1
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR31-01, YR31-02
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as31): criar executor pareado`

### T3: Criar analisador independente

**What:** Conferir pareamento, status, censuras, ganho em cada dimensão e não adulteração do protocolo; testes junto.
**Where:** `experiments/yrbc/analyze_as31_reductions.py`
**Depends on:** T2
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR31-04, YR31-05, YR31-06
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** unit + integração; criar/atualizar testes no mesmo task para todos ACs aplicáveis, negativos e mutantes
**Gate:** Quick
**Commit sugerido:** `feat(as31): criar analisador independente`

### T4: Executar campanha controlada

**What:** Conferir árvores limpas/hash/outputs de três seeds com Gurobi; classificação não pode ser inferida de dry-run.
**Where:** `results/benchmark/as31-yrbc-dominancia-001/`
**Depends on:** T3
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR31-01, YR31-02, YR31-03
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** integração: validação de integridade e paridade com o pré-registro
**Gate:** Quick
**Commit sugerido:** `docs(as31): executar campanha controlada`

### T5: Emitir decisão sobre G2a

**What:** Parecer independente GO/STOP/INCONCLUSIVE com eventuais regressões.
**Where:** `docs/technical/reference/experimentos/as31-dominancia-resultado.md`
**Depends on:** T4
**Reuses:** fontes listadas em `design.md` (conferir versões).
**Requirement:** YR31-04, YR31-05, YR31-06
**Tools:** Python/Poetry, GitHub para fontes; `/tlc-spec-driven` para Execute; Gurobi somente quando previsto e aprovado.

**Done when:**
- [ ] Artefato documentado/implementado com hipóteses, dados e versões verificáveis.
- [ ] Critérios de aceite aplicáveis passam em teste independente e negativos (quando houver) falham.
- [ ] Não foram alteradas fontes/partições proibidas nem inventados status/certificados.
- [ ] Gate de teste/checagem passa e evidência é anexada ao mesmo commit atômico.
**Tests:** auditoria de fonte e consistência por verificador independente; comparação reprodutível
**Gate:** Full
**Commit sugerido:** `docs(as31): emitir decisão sobre g2a`

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

- **G2a — Relevância computacional da dominância:** G2a GO_CANDIDATE_REVIEW se ≥2 grafos brutos independentes apresentarem redução ≥50% no tempo de raiz sem piorar bound, OU melhora de tempo até OPT ≥2×, OU melhora inteira de LB/UB ≥1 estação, com evidência MIP e sem regressão grave em outros casos. STOP se não houver efeito de MIP e pouca redução útil fora de PUC; INCONCLUSIVE em censuras/variabilidade. Revisão humana autoriza AS32 somente após GO.
- A etapa seguinte depende de aprovação explícita do gate. Não criar `validation.md` até existir evidência; o Verifier deve ser outro agente.
- Nenhuma execução ou commit acontece na entrega destas specs.
