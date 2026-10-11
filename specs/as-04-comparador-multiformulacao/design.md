# AS04 — Comparador justo U, U+K e formulações candidatas — Design

**Status:** proposta técnica (sem execução)  
**Spec:** `specs/as-04-comparador-multiformulacao/spec.md`

## Design Constraints

- Preservar `N2 FAIL`, o código e os resultados históricos de N1/N2/FC.
- Preservar semântica MIN-STATION: grafo original não direcionado, alcance dirigido A_r, pareamento anônimo, |S|=|T|, S∩T permitido, robôs com autonomia r, estações compartilhadas sem limite de atendimento, somente y binário nas novas formulações recomendadas.
- Matriz experimental que não confunde U sem K, U+K, F-CC completa, LP numérico, núcleo IP e certificado racional.
- Caminhos sugeridos são **destinos propostos para criação futura**, não arquivos já implementados.

## Proposed Architecture and Contracts

1. Reusar `experiments/formulation-comparison/{fc_budget.py,fc_pairing.py,fc_core.py,fc_evidence.py,fc_integrity.py}`; evitar duplicar regras validadas.
2. Adapter API proposto `as_arms.py`: `build_arm(id,case,config)`; `as_compare.py`: `run_pair`; `as_schema.py`: registro com fingerprints, K hash, budget, status e evidência.
3. Armas U (contínuo f + y binário sem K), U_K (mesmos domínios com K), A2_K; A4_K se ativada; FCC_K só quando completa; CORE_IP estritamente LB auxiliar.
4. LP: registrar `lp_opt_value` apenas quando `OPTIMAL` numérico; bounds duais se válidos, identificando origem. MIP: distinguir `ObjBound`, `ObjVal`, UB físico e `certificate_kind`.
5. Painel comparativo: mesma instância e orçamento; hashes do conteúdo, Gurobi versão/seed/threads/Work, política de warm start e limite de RAM registrados.
6. Estados: `OPTIMAL_NUMERIC`, `FEASIBLE_PHYSICAL`, `TIME_LIMIT`, `NO_INCUMBENT`, `NOT_BUILT_SIZE`, `NOT_BUILT_CAP`, `MEMORY_LIMIT`, `SOLVER_ERROR`, `VALIDATION_FAIL`, `NOT_MEASURED`.
7. Arma construída mas não otimizada ≠ prova de que cabe; apenas reportar build e memória observados.

## Dependencies and Reuse

- **Pré-condição externa:** AS00=PASS; AS02=PASS para A; reusar FC-01–FC-04.
- **Código existente útil:** `baseline.py`, `ms_utils.py`, `experiments/cuts/independent_validator.py`, `experiments/cuts/harness.py` e `experiments/formulation-comparison/` quando aplicáveis; confirmar interfaces no momento da implementação.
- **Não alterar:** snapshots históricos em `results/`, freezes e decisões anteriores.

## Threats to Validity

**Interpretação obrigatória:** `U` é o modelo agregado sem K (ablação). `U_K` é a formulação que os relatórios anteriores frequentemente chamam `COMP`. A comparação U vs U_K isola efeito K; U_K vs A2_K isola mudança de formulação.

## Exit Gate

A feature somente poderá ser marcada como concluída após execução de testes derivados dos ACs, auditoria da rastreabilidade e verificador independente. As specs são planejamento; nenhum `PASS` de implementação é inferido de arquivos antigos.
