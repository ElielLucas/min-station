# AS-08 — Pipeline de pricing, geração de colunas e piloto LP

**Natureza:** implementação experimental para a branch `novos_testes`. Não é parecer científico independente nem homologação da AS-08.

## Escopo

- **T1** — Formulação matemática B1–B4 e equivalência com A unitária: parecer de 12/10/2026 produzido em separado; a revisão independente autor ≠ verificador continua pendente.
- **T2a** — Modelo B completo por enumeração, testes de projeção/viabilidade e comparador A unitária: arquivos já implementados e executados no ambiente do autor.
- **T2b** — Pricing por Dijkstra em H para cada origem, com custo reduzido `sum(gamma[s,v]+mu[v], v interno) - pi[s] - tau[t]`; inclui caminho `(s)` e caminhos passando por outros terminais. Verificação com aritmética `Fraction` e contra enumeração completa.
- **T3** — Mestre restrito (RMP) com B1/B2, B3 somente nos pares (origem, vértice) tocados pelas colunas, B4 nos destinos fora de S e BK. Fase inicial com artificiais penalizadas. Iteração master/pricing, limites por tempo, linhas, colunas e iterações. O objetivo RMP não é limite inferior do mestre completo.
- **Certificação T3** — Repara duais por meio dos mínimos globais dos custos reduzidos. O bound é construído em `Fraction` a partir de aproximações numéricas dos duais. É válida a desigualdade dual do modelo matemático completo, **condicionada à validade de K e à consistência da instância**; a igualdade com o ótimo LP é declarada somente após convergência e comparação de LB/UB dentro da tolerância. O pacote inclui um verificador separado de números racionais e K.
- **T4** — Runner de piloto LP exploratório COM + K vs B + K nas mesmas seis instâncias de desenvolvimento do AS05; 12 braços, orçamento integral por braço supervisionado com FC01 (carregamento, alcance, K, master/solver). Planos SHA, checkpoints imutáveis, retomada, manifesto SHA, análise que recusa dados censurados e gate sem autopromoção.

## Arquivos adicionados

- `experiments/alternative-formulations/as08_pricing.py`
- `experiments/alternative-formulations/as08_column_generation.py`
- `experiments/alternative-formulations/run_as08_b_pilot.py`
- `experiments/alternative-formulations/test_as08_pricing_cg.py`

## Arquivos anteriores incluídos novamente no ZIP cumulativo

- `experiments/alternative-formulations/as08_b_exact.py`
- `experiments/alternative-formulations/run_as08_t2a.py`
- `experiments/alternative-formulations/test_as08_t2a.py`
- `docs/technical/plans/execucao/as08-t2a-validacao-exata-caminhos.md`

## Política de resultados

- `CONVERGED`: CG completo, artificiais praticamente nulas, lower bound global calculado pelo dual racional e aproximação numérica primal coincidente dentro da tolerância. **Somente LP, não MIP**.
- `ITERATION_LIMIT`, `CAP_EXCEEDED`, `TIME_LIMIT`: execução censurada; não fabricar ótimo B nem declarar inexistência de ganho. Se um certificado intermediário existir, só utilizá-lo como limite inferior, nunca como prova de otimalidade.
- `NO_PATH_FOR_ORIGIN`, `NO_FEASIBLE_MASTER`, `UNCERTIFIED_LP_OPTIMALITY`: nenhuma alegação positiva de conclusão LP.
- `NO_GLOBAL_LB_CERTIFICATE_DISABLED`: master/pilot não deve promover valores numéricos a certificados.
- `INFEASIBLE_SUPPORT`: a fonte não alcança qualquer destino; verificação física independente não está implícita no status.
- Cortes: mesmas famílias C1+C2+C4-DM do projeto, reconstruídas e validadas para ambos os braços. A certificação do dual pressupõe que cada corte K preserva o problema físico original.

## Métricas do piloto

- LP de COMP+K (apenas se numérico e ótimo).
- LP de B+K (apenas se CG convergiu com certificação e coincidência UB/LB).
- Bound global racional de B+K, rechecável com `--verify --audit-dual`.
- Iterações CG, colunas geradas, linhas RMP, não zeros, artificiais, custo do master, tempo do worker, status, K SHA, instância SHA e proveniência.

## Gate exploratório (pré-especificado no runner)

- Dominância B+K < COMP+K acima da tolerância: `FAIL_DOMINANCE` (inconsistência a investigar).
- Pelo menos duas instâncias de duas origens de grafos distintas com melhora LP >= 1% e custo total <= 3x: `GO_FURTHER_MIP_RESEARCH_EXPLORATORY`.
- Nenhum critério acima: `STOP_LOW_LP_GAIN_OR_HIGH_COST_EXPLORATORY`.
- Qualquer braço censurado: `INVESTIGATE_CENSORED` (sem extrapolar melhoria ou fracasso).

Estes parâmetros são de **triagem exploratória**, não significância estatística nem validação acadêmica.

## Limitações reconhecidas

1. Não implementa branch-and-price nem solução MIP da Formulação B: explicitamente fora do escopo da spec AS-08. O próximo desenvolvimento inteiro depende de gate positivo.
2. Gurobi não foi disponibilizado no ambiente de implementação do pacote; o adaptador produtivo Gurobi do RMP precisa passar pelos testes no equipamento do pesquisador. O núcleo executou com SciPy/HiGHS.
3. O solver LP é reconstruído a cada iteração. Isso simplifica o controle de corretude, mas pode ser lento em instâncias grandes. O limite operacional de colunas/linhas evita criação ilimitada, e censura é esperada.
4. Os seis casos são do conjunto de **desenvolvimento** do AS05. Não há avaliação independente, nem afirmação de superioridade em produção.
5. T1 ainda necessita revisão humana independente, conforme `tasks.md`. Não houve commits no repositório local do usuário: a entrega é ZIP de integração, não uma operação sobre seu Git.
