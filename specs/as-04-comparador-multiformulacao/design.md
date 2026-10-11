# AS04 — Comparador justo U, U+K e formulações candidatas — Design

**Status:** infraestrutura local implementada para testes (sem campanha; Gurobi pendente)  
**Spec:** `specs/as-04-comparador-multiformulacao/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Arquitetura e contratos implementados

1. `experiments/formulation-comparison/as04_schema.py`: schema `AS04-COMPARISON-v1`, IDs estáveis, evidência numérica/UB física/racional separada; `SolverPolicy` com SHA da configuração completa.
2. `as04_arms.py`: adapters que chamam `compile_u`, `compile_a`, `prepare_K`, `partition_two` e `refine_four` existentes, sem cópias do modelo; K ordenado/canonicalizado e hash aplicado.
3. `as04_runner.py`: `run_bounded` (FC-01) supervisiona cada braço desde carga+alcance+K até Gurobi e validador físico. Loading é repetido por braço e cobrado integralmente. `as02_validation_gate` impede A2 sem AS01/AS02 homologadas; A4 requer gate adicional AS05.
4. `as04_compare.py`: `K_EFFECT`, `A_EFFECT`, `REFINEMENT_EFFECT` independentes; requer mesma instância, mesmo A_r, mesmo K (exceto `U WITHOUT_K`) e política solver; par incompleto não produz alegações.
5. `as04_reporting.py`: publicação append-only JSON/CSV/manifesto SHA-256, sem apagar linhas de falha ou convertê-las para zero.
6. `run_as04_case.py`: execução individual pré-campanha; `run_as04_smoke.py`: HiGHS/SciPy sintético, não é experimento principal.
7. FCC, CORE_IP, CUTS, B, C ficam `NOT_AUTHORIZED` até adapter completo e gates respectivos. F-CC restrita nunca é tratada como F-CC completa. CORE é LB auxiliar, nunca uma instalação.
8. Gurobi `ObjBound` MIP numérico é distinto de incumbente e UB físico validado; primal LP só vira `lp_opt_value` em `OPTIMAL` para modelo completo. Nenhum certificado racional é inferido de solver.
9. `wall_total_s` inclui startup, leitura+alcance, K, build, solver, validação, shutdown. `solver_runtime_s` inclui presolve; `presolve_wall_s` fica nulo até medição própria. `ru_maxrss` é pico acumulado de processo, não RAM incremental.

## Dependencies and Reuse

- **Pré-condição externa:** AS00=PASS; AS02=PASS para A; reusar FC-01–FC-04.
- **Código existente útil:** `fc_budget.run_bounded`, `fc_instances.load_instance`, `fc_integrity.dump_json_bytes`, `as02_model_a`, `as03_grouping`, `as02_validation_gate` e `independent_validator.viavel` verificados no snapshot do ZIP.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

**Interpretação obrigatória:** `U` é o modelo agregado sem K (ablação). `U_K` é a formulação que os relatórios anteriores frequentemente chamam `COMP`. A comparação U vs U_K isola efeito K; U_K vs A2_K isola mudança de formulação.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
