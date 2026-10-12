# AS05-FAC — Design técnico

## Arquitetura

- `as05_factorial.py`: plano, carregamento AS00, preparação de partições, compilação U/A via AS02, filtro AS03 de tamanho/memória, validação K bitset-v2 da DIAG, worker supervisionado FC-01, contrastes, relatório e validação de integridade.
- `run_as05_factorial.py`: CLI com `--init-plan`, `--check-plan`, `--preflight`, `--execute`, `--resume`, `--verify`, `--analyze`.
- `run_as05_factorial_smoke.py`: pequeno F1 (quatro origens), todas seis LPs resolvidas numericamente com SciPy/HiGHS; **não é campanha real**.
- `test_as05_factorial.py`: cobertura de matematização, aninhamento, ausência de K, censuras, compatibilidade de plano e integridade.
- `results/benchmark/as05-factorial-plan-v1.json`: protocolo fatorial derivado do piloto AS05 e diagnóstico v2.

## Fluxo

1. `make_plan()` carrega AS05/AS00, vincula SHA das fontes e evidências v2 e define os seis braços com política fixa.
2. `preflight_sizes()` carrega cada instância e estima tamanho antes de conhecer K; **não roda solver**.
3. `run_experiment()` cria diretório novo e executa cada braço através do supervisor `run_bounded()` com orçamento total de 300 s.
4. `_factorial_worker()` carrega fonte/alcance; prepara A2 e A4 quando necessário; aborta por tamanho/memória antes de K e do modelo; prepara K apenas nos braços +K; compila por AS02; otimiza com Gurobi.
5. `verify_case()` valida integralidade das seis linhas, K, pai/filho, identidade da instância e dominância numérica com tolerância.
6. `_read_or_run_checkpoint()` grava resultados por braço com SHA; `--resume` só funciona com plano idêntico e checkpoints íntegros.
7. `verify_experiment()` reconstrói resultados e contrastes, valida CSV, checkpoints e manifesto; `analyze_experiment()` produz JSON/CSV/Markdown append-only.

## Métricas e nove contrastes

| Nome | Pares | Interpretação |
|---|---|---|
| `K_ON_U` | U → U+K | Efeito K na base |
| `GROUP_2_NO_K` | U → A2 | Efeito desagregação sem K |
| `GROUP_4_NO_K` | A2 → A4 | Refinamento sem K |
| `A4_VS_U_NO_K` | U → A4 | Desagregação total sem K |
| `K_ON_A2` | A2 → A2+K | Efeito K em dois grupos |
| `K_ON_A4` | A4 → A4+K | Efeito K em quatro grupos |
| `REFINEMENT_WITH_K` | A2+K → A4+K | Refinamento com K |
| `A2_OVER_U_K` | U+K → A2+K | Efeito incremental A2 sobre U+K |
| `A4_OVER_U_K` | U+K → A4+K | Efeito incremental A4 sobre U+K |

**Nota:** são **nove** contrastes neste desenho. O relatório é calculado exclusivamente dos pares ótimos completos. Interação = `[A4+K − A2+K] − [A4 − A2]`.

## Garantias e limites

- `LP_OPTIMAL` só é publicado se Gurobi reportou `OPTIMAL_NUMERIC`; status censurado implica objetivo nulo no relatório.
- O proxy AS03 de memória não é garantia de RSS; o supervisor impõe `RLIMIT_AS` quando definido.
- A4 é autorizada somente por esta investigação exploratória, sem mudança do gate AS05 original.
- Tempo total de cada +K inclui K, modelo e solver; sem K não prepara cortes. Comparar também `solver_runtime_s`, `wall_phases_s` e tamanho.
- 300 segundos por braço são **um novo orçamento exploratório**, não retroativamente o orçamento original de 90 s.
- São seis instâncias AS00 de desenvolvimento; dados AS00 de avaliação proibidos.
- Nenhuma escolha do melhor braço ou política é promovida automaticamente.
