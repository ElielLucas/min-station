# R11 — Auditoria das divergências dos certificadores

**Data:** 2026-10-07  
**Spec:** `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`  
**CSV oficial:** `results/structural/r11-certificadores.csv`  
**Commit registrado no CSV:** `dd485dc`  
**Pré-registro:** `docs/technical/reference/experimentos/pre-registro-r11-certificadores.md`  
**Leituras:** `docs/technical/reference/experimentos/leituras-r11-certificadores.md`

## 1. Objetivo

Esta auditoria executa R11c.2–R11c.5: separar erro de referência, erro de implementação, divergência do procedimento literal e lacuna de leitura; reduzir as divergências por mecanismo sempre que prático; e registrar o limite das conclusões.

Ela **não** altera os certificadores depois da observação dos resultados e **não** modifica o lote oficial. Os casos reduzidos abaixo são verificações pós-lote, usadas apenas para tornar os mecanismos mínimos e auditáveis.

---

## 2. Consistência das referências

O CSV oficial contém 80 linhas para 44 instâncias. A pilha de referência foi consistente em todo o lote:

- baseline: `OPTIMAL` em 80/80 linhas;
- enumeração independente: `OPTIMAL` nas 69 linhas `micro` e `not_run_cap` nas 11 linhas `medium`;
- F-CC binária: `OPTIMAL` em 80/80 linhas;
- `reference_failure`: 0;
- `objective_below_reference`: 0;
- `implementation_error`: 0;
- F-C3: `OPEN` em todas as linhas.

Logo, as linhas classificadas como `suboptimal` ou `infeasible_solution` não decorrem de desacordo entre as referências exatas usadas pela R11.

---

## 3. Mecanismo D-PATH — Algorithm 1 literal superconta estações

### 3.1 Fonte

Das, Algorithm 1, processa o caminho da esquerda para a direita. Para cada vértice `v_i`:

1. incrementa `Tcounter` se `v_i ∈ S`;
2. decrementa `Tcounter` se `v_i ∈ T`;
3. se `Tcounter != 0`, incrementa `Vcounter`;
4. quando `Vcounter == r`, adiciona o próprio `v_i` a `C` e zera `Vcounter`.

A leitura R11 preserva literalmente esses passos. Em particular, `Vcounter` conta o vértice de origem como o primeiro vértice ativo.

### 3.2 Evidência oficial

O menor witness do lote oficial é:

```text
id       = path-hand-opt0-r2
n        = 3
S        = {v0}
T        = {v2}
r        = 2
sha256   = a12ac5cb286b01621029dc93651b1782c0eb599bea6610ac11c20a82cb5415eb
ALG1     = C={v1}, |C|=1, viável
OPT      = 0
resultado= suboptimal
```

Enumeração, baseline e F-CC retornam 0.

### 3.3 Redução pós-lote

A divergência pode ser reduzida a um caminho com **2 vértices**, que é o menor caminho com deslocamento não trivial:

```text
V = {v0,v1}
E = {{v0,v1}}
S = {v0}
T = {v1}
r = 1
```

Algorithm 1 literal:

```text
v0: Tcounter=1, Vcounter=1=r -> C={v0}
v1: Tcounter=0
```

Portanto `|C|=1`.

Pela definição do MIN-STATION, o robô percorre uma única aresta, igual à autonomia `r=1`, sem precisar recarregar. Logo `OPT=0`.

A verificação reproduzível em `experiments/structural/verify_r11_counterexamples.py` usa `opt_por_enumeracao` e confirma:

```text
alg_status = ok
alg_obj    = 1
alg_viavel = true
opt        = 0
```

### 3.4 Classificação

**CONFIRMED DIVERGENCE — literal published pseudocode vs. MIN-STATION definition.**

Esta classificação vale para o procedimento literal implementado a partir do Algorithm 1. Não autoriza, por si só, concluir qual correção matemática deve substituir o pseudocódigo.

---

## 4. Mecanismo D-CYCLE — Algorithm 2 herda a supercontagem do Algorithm 1

### 4.1 Fonte

Das, Algorithm 2:

1. remove cada uma das `n` arestas do ciclo;
2. resolve o caminho resultante com `Min-Station-On-Path`;
3. conserva a solução de menor cardinalidade, usando `<=` e portanto a última em caso de empate.

Assim, a correção de Algorithm 2 depende diretamente da correção de Algorithm 1 em cada quebra.

### 4.2 Evidência oficial

Um witness oficial pequeno é:

```text
id       = cycle-hand-n5-r1
n        = 5
m        = 1
r        = 1
sha256   = 442478e1cc844a243c4863a2aa5f2a4c2fa52be62d87fb2c4832d0af2751c604
ALG2     = |C|=2, viável
OPT      = 1
resultado= suboptimal
```

Também há `cycle-hand-breaks`, com `|C|=2` contra `OPT=0`.

### 4.3 Redução pós-lote

O mecanismo reduz ao menor ciclo possível, um triângulo:

```text
V = {v0,v1,v2}
E = {{v0,v1},{v1,v2},{v2,v0}}
S = {v0}
T = {v1}
r = 1
```

Pela definição, `v0` e `v1` são adjacentes; logo `OPT=0`.

Algorithm 2 literal executa Algorithm 1 em cada quebra. O menor resultado entre as três quebras tem cardinalidade 1:

```text
alg_C     = {v0}
alg_obj   = 1
alg_viavel= true
opt       = 0
```

O mesmo script pós-lote confirma `OPT=0` por enumeração independente.

### 4.4 Classificação

**CONFIRMED DIVERGENCE — Algorithm 2 literal inherits Algorithm 1 divergence.**

Não é necessário atribuir um novo mecanismo matemático às 9 linhas `suboptimal` de ciclo; elas são witnesses repetidos da mesma dependência estrutural.

---

## 5. Mecanismo D-SPIDER — entrada em radial / alcance a partir do centro

### 5.1 Fonte e lacuna

Pereira & Ravelo, Lemma 1, processa uma radial da folha em direção ao centro e maximiza a carga restante ao chegar a `c`. Depois, Lemma 2 ordena robôs remanescentes por carga e alvos por distância. O texto afirma que, quando necessária, uma estação adicional deve ficar em `c`, porque “from `c` every target or charging station associated with `L_T` is reachable”.

A fonte não fecha de forma única como colocar novas estações **na descida para uma radial de alvo** que não recebeu estações no processamento folha→centro. Essa é a questão pré-registrada SP-R1/SP-R2.

### 5.2 Witness oficial SP-R2

```text
id       = spider-reading-02
radiais  = [1,5,1]
n        = 8
r        = 2
S        = {r0_1}
T        = {r1_5}
sha256   = 03ba6bee4194239271d3942580f87887b7edf7d5bd925e3af9673576e327d302
```

A construção satisfaz literalmente:

```text
d(s,c) = 1
d(c,t) = 2r+1 = 5
s e t em radiais distintas
radial de t sem origem
```

Resultados oficiais:

| variante | status | C | viável | obj | OPT | classificação |
|---|---|---|---:|---:|---:|---|
| spider-A | ok | `{c}` | não | 1 | 2 | `infeasible_solution` |
| spider-B | ok | `{r1_4,r1_2,c}` | sim | 3 | 2 | `suboptimal` |
| spider-U | ok | `{c}` | não | 1 | 2 | `infeasible_solution` |

Enumeração, baseline e F-CC retornam `OPT=2`.

### 5.3 Minimalidade estrutural de SP-R2

Sob as condições **específicas de SP-R2** e `r=2`, o caso é mínimo:

- uma radial de origem precisa ter ao menos 1 vértice além de `c`;
- a radial do alvo precisa ter distância `2r+1=5`;
- uma aranha precisa de pelo menos 3 radiais, e a terceira radial precisa ter ao menos 1 vértice;
- mais o centro.

Portanto:

```text
n_min = 1 + 1 + 5 + 1 = 8
```

O próprio `spider-reading-02` já é o witness mínimo dentro dessa construção.

### 5.4 Classificação

- `spider-A` / `spider-U`: **CONFIRMED DIVERGENCE OF THESE LITERAL READINGS** no SP-R2;
- `spider-B`: **CONFIRMED SUBOPTIMALITY OF THE R11 RECONSTRUCTION**, que adiciona a estratégia de caminho na radial de entrada e herda a supercontagem de PATH-ALG1.

Isto **não** é redigido como “Theorem 1 is disproved” porque o artigo não fornece pseudocódigo único suficiente para identificar uma única implementação canônica em todos os silêncios. O resultado é, portanto, leitura-dependente.

---

## 6. SP-R3, SP-R4 e SP-R5

### SP-R3

`spider-reading-03` devolveu `unspecified` nas três variantes por radial mista desbalanceada (`INT-A`). Isso confirma que a fonte/leitura não fecha a seleção de origens/alvos remanescentes sem reconstrução adicional.

### SP-R4

`spider-reading-04`:

- `spider-A`: `agreement`, OPT 0;
- `spider-B`: `suboptimal`, 2 contra 0;
- `spider-U`: `unspecified` por `S∩T`.

A diferença é explicitamente dependente da política KEEP vs. conservadora. Não se apaga `S∩T`.

### SP-R5

`spider-reading-05`:

- `spider-A`: solução inviável;
- `spider-B`: solução viável, porém 5 contra OPT 3;
- `spider-U`: `unspecified` em `r'=0`.

Forçar uma estação antes de `c` para resolver `r'=0` continuaria sendo reconstrução, não leitura literal.

---

## 7. Agrupamento das 45 linhas divergentes

O CSV possui 32 `suboptimal` e 13 `infeasible_solution`. Para redução, elas são agrupadas por **mecanismo**, não tratadas como 45 teoremas independentes:

| mecanismo | witnesses principais | efeito |
|---|---|---|
| D-PATH | path oficial + path n=2 pós-lote | Algorithm 1 conta vértices ativos/origem e superconta |
| D-CYCLE | cycle oficial + triângulo pós-lote | Algorithm 2 herda D-PATH em todas as quebras |
| D-SPIDER-ENTRY | SP-R1/SP-R2 e casos cruzados | leitura folha→centro não fecha estações na radial de entrada |
| D-SPIDER-PATH | `spider-B` | reconstrução baseada em PATH-ALG1 pode ser viável porém subótima |
| source silence | SP-R3/SP-R4/SP-R5 | `unspecified`, não divergência |

Isto evita “reduzir” repetidamente a mesma falha determinística observada em seeds diferentes.

---

## 8. Regra de comunicação

Os resultados internos podem ser versionados no repositório como evidência técnica.

Qualquer afirmação pública do tipo “o artigo está errado”, “o teorema é falso” ou “há um erratum” exige revisão humana final da fonte e comunicação aos autores, conforme a spec.

**COMMUNICATION REQUIRED BEFORE PUBLIC CLAIM.**

---

## 9. Veredito da auditoria

A auditoria não encontrou inconsistência na pilha de referência nem evidência de erro de implementação nos checks definidos pela R11.

Há:

1. divergência confirmada do Algorithm 1 literal de Das em caminhos;
2. divergência confirmada do Algorithm 2 literal, herdada de Algorithm 1, em ciclos;
3. divergência confirmada das leituras `spider-A/U` no SP-R2 e subotimalidade de `spider-B` nesse mesmo witness;
4. casos de aranha em que a fonte permanece insuficiente para produzir uma única leitura executável, corretamente classificados como `unspecified`.

Isso satisfaz o ramo `CONFIRMED DIVERGENCE` da conclusão R11 sem transformar a evidência em alegação pública sobre errata.
