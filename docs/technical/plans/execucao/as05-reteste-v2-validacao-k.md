# AS-05 — Adendo de diagnóstico v2: validação exata de K e reensaio A2

**Natureza:** adendo exploratório *posterior* à AS-05 e à rodada diagnóstica v1. **Não substitui o pré-registro AS-00, o gate AS-05, os resultados v1 ou a revisão científica independente.**

## 1. Motivação e defeitos registrados

Em `results/benchmark/as05-diagnostic-001/censored/report.json`, os braços `A2_K` de `puc-w3c571-seed-r1` e `vienna-I056-regiao-f4` terminaram em `WORKER_ERROR`, com `ValueError: DIAG: política não autorizada`: o executor de `censored` transmitia `grouping_policy=None`. No mesmo diagnóstico, `U_K` da primeira instância sofreu `TIMEOUT_PREPARATION` após 271,69 s na fase `k_validation_cached`; em Vienna, essa fase durou ~24,55 s para 101 cortes.

**Não** interpretar `WORKER_ERROR` ou `TIMEOUT_PREPARATION` como incapacidade matemática de A2+K.

## 2. Correções versionadas

**Política A2:** no novo plano `results/benchmark/as05-diagnostic-retest-plan-v2.json`, `A2_K` recebe **explicitamente** `reachability_degree` e a mesma seed 42 utilizada no diagnóstico original. A política não pode ser trocada por `reachability_overlap` após observar resultados LP. Braços `U` e `U_K` mantêm política nula porque não formam grupos.

**Validação exata K:** `as05_diag_cut_fast.py` não muda os geradores C1, C2, C4-DM, a ordenação, o compilador matemático nem a semântica dos cortes. Para cada corte Z, verifica exatamente se não existe matching perfeito no grafo de alcançabilidade S→T quando os intermediários instalados são V\\Z:

1. BFS reversa multi-alvos identifica origens que não alcançam destino algum (certificado de validade).
2. BFS direta multi-origens identifica destinos não alcançáveis por nenhuma origem (certificado de validade, particularmente eficaz na família C1 do lado de T).
3. Se ambas as verificações passam, computa a relação completa de alcançabilidade via máscaras binárias propagadas pelo grafo **dirigido**, respeitando origens/destinos sobrepostos e o trânsito somente em relés passáveis.
4. Testa matching bipartido perfeito com caminhos aumentantes iterativos; somente aceita o corte quando matching perfeito inexiste.
5. Um corte inválido continua gerando `CorteInvalido`. O primeiro corte de cada lote também passa pelo verificador histórico como sentinela; os demais são integralmente verificados pelo novo algoritmo (não são pulados).

O método usado pela rodada v1 continua sendo `legacy` por padrão. A v2 especifica `bitset-v2` explicitamente no plano, nos checkpoints e nos relatórios. Os mesmos hashes SHA-256 de K devem ser preservados. A Vienna tem SHA conhecido do relatório anterior: `64d3500a49c52bbf3ea9a3ffd718711c2e6a809585d7f91db311ef44a3606796`. Para `w3c571`, o SHA de K foi calculado no pré-teste local sem solver antes da campanha v2 e fica identificado com proveniência distinta.

## 3. Plano prospectivo do REENSAIO v2

O novo plano foi criado **antes dos solves LP v2** e contém hashes do plano diagnóstico e dos manifestos das etapas v1. Apenas **duas instâncias censuradas** serão reensaiadas; resultados `grouping` das quatro instâncias já resolvidas não serão repetidos. O plano mantém o orçamento de **300 s por braço**, threads e seed originais e inclui três braços no reensaio: `U`, `U_K`, `A2_K@reachability_degree`.

Os diretórios de saída são novos:

- `results/benchmark/as05-diagnostic-v2-001/cuts`
- `results/benchmark/as05-diagnostic-v2-001/censored`
- `results/benchmark/as05-diagnostic-v2-001/analysis`

Nenhum resultado em `as05-diagnostic-001` ou em `as05-pilot-owner-exploratory-001` deve ser sobrescrito. `--resume` só pode completar **diretórios parciais**, com checkpoints íntegros. Arquivos finais são append-only.

## 4. Evidências locais da implementação (não equivalem aos solves do pesquisador)

- Testes diferenciais exaustivos sobre subconjuntos Z de grafos pequenos dirigidos, com sobreposição S∩T, comparados ao validador original.
- Testes de deficiência de Hall sem terminal isolado, mutação de corte, preservação dos hashes, exceções, autorização explícita A2, origem das evidências, checkpoint e censura.
- Perfis reais sem solver, na máquina de preparação:

| Instância | Cortes únicos | Hash K | Validação bitset-v2 | Tempo do estágio `cuts` |
|---|---:|---|---:|---:|
| `puc-w3c571-seed-r1` | 2.284 | `42b9f6336b56241a1318326d5df68d04ec1f1c8a427b74b7462eea116766e23f` | 4,44 s | 22,82 s |
| `vienna-I056-regiao-f4` | 101 | `64d3500a49c52bbf3ea9a3ffd718711c2e6a809585d7f91db311ef44a3606796` | 1,45 s | 3,18 s |

Tempos dependem da máquina e não devem ser interpretados como resultados reproduzidos no Gurobi do pesquisador. A fase C2 ainda demanda cerca de 17,5 s em w3c571 e é uma otimização separada, **não necessária para destravar o prazo de 300 s**.

## 5. Limites e critérios de análise

- Status `OPTIMAL_NUMERIC` é uma evidência LP numérica, não certificado racional.
- Timeout, erro e ausência de LP ficam com valor nulo e são mantidos no relatório.
- O comparador só calcula `A_EFFECT` com dois braços completos e mesmo K, instance SHA, modo e política do solver.
- Não concluir `GO` científico com o reensaio exploratório nem selecionar agrupamentos sobre avaliação AS-00.
- Só após execução v2 com Gurobi e consolidação, avaliar se A2 acrescentou ganho material; o critério de 1% da AS05 original não foi modificado.

## 6. Comandos

Ver `AS05-RETESTE-V2-INTEGRACAO.md` na raiz do pacote. Validar plano, executar primeiro `cuts`, depois `censored`, verificar ambos e consolidar em `analysis`, sempre com `PYTHONPATH=. poetry run python`.
