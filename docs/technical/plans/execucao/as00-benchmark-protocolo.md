# AS-00 — Benchmark difícil e pré-registro experimental

**Status:** protocolo pré-registrado para AS-00; **nenhuma otimização nova foi executada**.  
**Fontes:** `instances/manifest.csv`, `instances/benchmark-v1/spec.csv`, pareceres Astra (11/10/2026).  
**Implementação:** `experiments/benchmark/as00_protocol.py`, `as00_families.py`, `as00_preregister.py`.  
**Spec:** `specs/as-00-benchmark-e-pre-registro/`.

## 1. Diagnóstico e escopo

A FC-06 condicionou a comparação completa à capacidade de enumerar a F-CC explícita.
Este estudo usa dificuldade D/A no benchmark-v1, independentemente de F-CC,
e preserva `N2 FAIL` e todos os registros anteriores. A dificuldade é a
classificação histórica do COMP+K sob 600 segundos: **não é uma nova medição**.

- Universo: **31 D/A**, com **14 desenvolvimento** e **17 avaliação**.
- Seis casos de desenvolvimento em piloto; dez da avaliação pré-selecionados
  por família bruta distinta; sete outros casos mantidos em cobertura.
- Instâncias grandes não são removidas por estouro de memória, budget ou cap.
- Sem inclusão de `lin23` ou `lin37`: estão fora da classe principal D/A.

## 2. Identidade e independência

O protocolo registra por instância: arquivo-fonte, SHA dos bytes,
SHA do conteúdo, nome normalizado, `n`, `m`, `r`, hash do grafo original
(G com vértices, arestas e pesos), hash separado de S e T, hash do conjunto
canônico de arcos de alcance, grupo de proveniência e fingerprint de equivalência
(S/T/A_r). **Equivalência de alcance não implica igualdade do grafo original**.

Em MAPF, `family_id` combina mapa bruto e cenário, sem incluir quantidade
de agentes ou autonomia. `raw_graph_id` identifica o mapa sem cenário.
O subconjunto de avaliação relacionado a um desenvolvimento é marcado
`RELATED_SCENARIO` ou `RELATED_RAW_GRAPH`, sem exclusão silenciosa.

A variante `mapf-room-32-32-4-m25-f4-rho` pertence ao mesmo mapa/cenário
da variante de desenvolvimento `mapf-room-32-32-4-m10-f8`.
Não é base para reivindicar validação independente de uma política ajustada
com a primeira variante. Outros casos com proveniência ausente geram erro de
integridade, não uma presunção de independência.

## 3. Matriz de formulações e hipóteses

| Arm ID | Modelo | Papel |
|---|---|---|
| `U_NO_K` | COMP / U sem cortes K | Ablação da base |
| `U_PLUS_K` | COMP com K | Controle principal |
| `A2_PLUS_K` | A com 2 grupos + K | Candidata inicial, após AS-01 e AS-02 |
| `A4_PLUS_K` | A com 4 grupos + K | Condicional a piloto LP e custo |
| `FCC_PLUS_K_SMALL_CONTROL` | F-CC+K completa | Referência LP somente onde enumerável |
| `INTEGER_KERNEL_CONTROL` | Núcleo inteiro | Controle para atribuir origem do ganho em LB |
| `MATCHING_CUTS_CONDITIONAL` | COMP+K mais cortes | Alternativa condicional do primeiro parecer |
| `PATHS_B_CONDITIONAL` | Modelo B por caminhos | Condicional quando A exigir muitos grupos |
| `CUMULATIVE_C_CONDITIONAL` | Modelo C cumulativo | Condicional a alcance muito denso |

Hipóteses (a avaliar posteriormente, não confirmadas): A2+K melhora o LP em
mais de um grafo bruto independente; esse ganho reduz gap/tempo com custo de
montagem aceitável; fortalecimento LP não implica necessariamente ganho MIP.

## 4. Regras de seleção e orçamento

O piloto consiste nas seis instâncias de desenvolvimento assinaladas abaixo.
A avaliação principal foi congelada com **10 grafos brutos distintos**, antes
de novos resultados das candidatas; os outros sete casos permanecem no universo
para estatísticas de aplicabilidade e futuros experimentos autorizados.

- Seeds: 42 inicialmente; 42, 43 e 44 para reprodutibilidade dos candidatos promovidos.
- Gurobi (em execução futura): 4 threads, mesmo K e parâmetros comparáveis.
- LP diagnóstico: **90 s totais por braço** (inclui preparação compartilhada).
- MIP piloto: **300 s**, depois **600 s** quando o LP justificar.
- Avaliação: **até 3.600 s por braço**, só após gates e congelamento.
- Limite de memória inicialmente escolhido: **16 GiB por braço**. Esta é uma
  **premissa operacional nova**, não um valor comprovado ou prescrito pelo Astra.
  Ambiente com menos recursos deve gerar nova versão do protocolo ANTES de solves.
- Preparação, construção, presolve, solver, tempo total, memória e parâmetros
  devem ser registrados separadamente; tempo total é o denominador de comparação.
- Não alterar partições e freezes de benchmark anteriores; mudar o protocolo
  requer versão distinta com justificativa e desvio rastreável.

## 5. Casos incluídos

| Instância | Família | Partição | Dificuldade histórica | Plano | Independência frente ao desenvolvimento |
|---|---|---|---|---|---|
| `mapf-den312d-m25-f4` | mapf | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `mapf-den312d-m50-f2-rho` | mapf | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `mapf-empty-32-32-m25-f4` | mapf | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `mapf-empty-32-32-m50-f2` | mapf | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `mapf-random-32-32-10-m25-f4` | mapf | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `mapf-random-32-32-10-m50-f8` | mapf | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `mapf-random-64-64-20-m100-f4` | mapf | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `mapf-room-32-32-4-m10-f8` | mapf | desenvolvimento | A | Piloto | DEVELOPMENT |
| `mapf-room-32-32-4-m25-f4-rho` | mapf | avaliacao | A | Apoio | RELATED_SCENARIO |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | mapf | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | mapf | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `pace18-t2-141-regiao-f4` | pace2018 | desenvolvimento | A | Apoio | DEVELOPMENT |
| `puc-bip42p-regiao-f2` | puc | desenvolvimento | A | Piloto | DEVELOPMENT |
| `puc-bip42p-seed-r1` | puc | desenvolvimento | A | Apoio | DEVELOPMENT |
| `puc-cc10-2u-seed-r1` | puc | desenvolvimento | A | Apoio | DEVELOPMENT |
| `puc-cc11-2u-seed-r1` | puc | desenvolvimento | D | Apoio | DEVELOPMENT |
| `puc-cc12-2u-seed-r1` | puc | desenvolvimento | A | Apoio | DEVELOPMENT |
| `puc-cc9-2p-seed-r1` | puc | desenvolvimento | D | Piloto | DEVELOPMENT |
| `puc-hc10p-seed-r1` | puc | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `puc-hc11p-seed-r1` | puc | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `puc-hc12p-seed-r1` | puc | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `puc-hc9u-regiao-f4` | puc | avaliacao | D | Final | INDEPENDENT_RAW_SOURCE |
| `puc-hc9u-seed-r1` | puc | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `puc-w23c23-seed-r1` | puc | desenvolvimento | A | Apoio | DEVELOPMENT |
| `puc-w3c571-seed-r1` | puc | desenvolvimento | A | Piloto | DEVELOPMENT |
| `pucn-cc3-10n-seed-r1` | pucn | desenvolvimento | A | Piloto | DEVELOPMENT |
| `pucn-cc7-3n-regiao-f2` | pucn | avaliacao | A | Final | INDEPENDENT_RAW_SOURCE |
| `pucn-cc7-3n-seed-r1` | pucn | avaliacao | A | Apoio | INDEPENDENT_RAW_SOURCE |
| `vienna-I056-regiao-f4` | vienna | desenvolvimento | A | Piloto | DEVELOPMENT |
| `vienna-I065-intercalado-f2` | vienna | desenvolvimento | A | Apoio | DEVELOPMENT |
| `vienna-I065-regiao-f4` | vienna | desenvolvimento | A | Apoio | DEVELOPMENT |

## 6. Ausências, censura e publicação

- `NOT_RUN`: braço ainda não autorizado/executado.
- `NOT_MEASURED_INPUT`: entrada insuficiente.
- `NOT_MEASURED_CAP`: construção excedeu o cap.
- `NOT_MEASURED_MEMORY`: memória excedida.
- `NOT_MEASURED_BUDGET`: orçamento esgotado antes da medição.
- `ERROR`: falha técnica diagnosticada.
- `TIME_LIMIT`: solver rodou mas não concluiu, mantendo limites e tempo medidos.
- `OPTIMAL`: status do solver, nunca tratar como prova racional independente.

Cada par instância/braço, inclusive ausências, será registrado por AS-04/AS-06;
nenhuma ausência vira zero nem remove o caso do denominador de aplicabilidade.
Uma incumbente só serve como UB físico após validação independente.

## 7. Gates científicos

1. AS-01: definição e revisão independente de formulação A e provas.
2. AS-02/AS-03: protótipo, validação física e políticas de agrupamento.
3. AS-04: comparador com contratos de paridade.
4. AS-05: piloto LP em desenvolvimento; promoção por resultado e custo total.
5. AS-06: teste MIP pareado 300/600 s, seeds e controle do núcleo.
6. AS-11: avaliação final pré-selecionada, condicionada a ganho reproduzido
   em ao menos **dois grafos brutos independentes**, sem perdas graves ocultadas.

AS-00 não autoriza solves, não reabre N2 e não declara superioridade de A.

## 8. Reproduzir o snapshot e a auditoria

```bash
python experiments/benchmark/as00_protocol.py --output-dir results/benchmark/as00-NOVA-VERSAO
PYTHONHASHSEED=0 python -m unittest discover -s experiments/benchmark -p 'test_as00*.py' -v
python .claude/skills/tlc-spec-driven/scripts/validate_spec.py specs/as-00-benchmark-e-pre-registro/spec.md
python .claude/skills/tlc-spec-driven/scripts/validate_tasks.py specs/as-00-benchmark-e-pre-registro/tasks.md
```

`--output-dir` deve apontar para um caminho ainda inexistente. Um diretório
existente é recusado, sem overwrite. A integridade de `protocol.json` é
verificável por `protocol.sha256`. O estado histórico em `results/` não é tocado.
