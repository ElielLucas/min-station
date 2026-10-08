# Leituras R11 — certificadores de caminhos, ciclos e aranhas

**Data:** 2026-10-06
**Atualização de preparação:** 2026-10-07
**Spec:** `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`
**Estado:** interpretação executável das fontes fechada; a implementação preparatória correspondente já foi escrita em `experiments/structural/`, mas **não foi executada**. Este documento não produz CSV, instâncias materializadas nem benchmark.

Vocabulário: **[Fato]**, **[Conferido]**, **[Hipótese]**, como em `plano-proxima-fase.md`.

Pergunta guia: como o algoritmo *publicado* se comporta sob o MIN-STATION deste repositório? Não: como alterar o MIN-STATION para o algoritmo funcionar.

---

## 1. Objetivo e escopo

Este arquivo transforma Das (caminhos/ciclos) e Pereira & Ravelo (aranhas) em passos auditáveis, IDs de leitura e um contrato de saída.

Serve para que outra pessoa implemente sem inventar decisões matemáticas. Não prova os artigos. Não corrige os artigos. Não escolhe a leitura que reproduz o baseline.

Fora deste arquivo: código dos geradores/certificadores, `verify_r11.py`, materialização das instâncias, lote oficial, CSV e comunicação pública de erro. O código preparatório existe, mas a evidência executável continua pendente.

---

## 2. Fontes utilizadas

| ID | Documento | Trecho | Uso |
|---|---|---|---|
| DAS-P1 | `docs/technical/reference/min-station-das.pdf` | Problem 1, p. 2 | Definição do MIN-STATION |
| DAS-SEM | mesmo | p. 2–3 | Passo, autonomia, não rotulados, compartilhamento, terminais |
| DAS-L2 | mesmo | Lemma 2, p. 6–7 | Estações para grupo no mesmo sentido |
| DAS-L3 | mesmo | Lemma 3, p. 7–8 | Troca quando caminhos se cruzam em sentidos opostos |
| DAS-L4 | mesmo | Lemma 4, p. 8–9 | Matching `s_i ↔ t_i` após ordem esquerda–direita |
| DAS-A1 | mesmo | Algorithm 1, p. 10; texto p. 10–11 | Procedimento de caminho |
| DAS-T2 | mesmo | Theorem 2, p. 11 | `O(n)` e correção alegada via Lemma 4 |
| DAS-L5 | mesmo | Lemma 5, p. 11–12 | Existe aresta não atravessada; permanência na prova |
| DAS-A2 | mesmo | Algorithm 2, p. 13 | Ciclo por `n` quebras |
| DAS-T3 | mesmo | Theorem 3, p. 13 | `O(n²)` |
| VAL-A2 | `docs/technical/reference/validacao-e-correcoes/validacao-formulacao-base.md` | §1; Apêndice A.2 | Invariantes; armadilha `⌊L/r⌋` vs definição |
| BF-U | `docs/context-ai/base-formulation.md` | §6–7 | Balanço unificado; `S∩T`; permanência |
| POV | `docs/project-overview.md` | §6 | Invariantes do problema base |
| PR-DEF | `docs/technical/reference/artigos-externos/pereira-ravelo-2026-aranhas.md` | §2 | Aranha, centro, radiais |
| PR-REV | mesmo | §3 | Revisão do guloso de caminhos |
| PR-L1 | mesmo | Lemma 1, p. do `.md` após §4 | Guloso na radial, folha → centro |
| PR-L2 | mesmo | Lemma 2 | Matching carga restante × alvo mais longe |
| PR-T1 | mesmo | Theorem 1 | `O(|V|)`; condições para estação no centro |
| PLAN-5 | `docs/technical/plans/execucao/plano-proxima-fase.md` | §5 | Cinco leituras SP-R1…SP-R5, já como hipótese |
| FCC | `docs/technical/reference/formulacoes/formulacao-fcc-configuracoes-conectadas.md` | definição | Referência de cruzamento futuro; **não** entra no certificador |
| GF1 | `docs/technical/reference/decisoes/decisao-gf1.md` | veredito | F-CC disponível como referência; F-C3 `OPEN` |
| G1 | `docs/technical/reference/decisoes/decisao-g1.md` | veredito | R11 continua linha de suporte |

Não há PDF original de Pereira & Ravelo no repositório. A fonte de aranhas é só o `.md` acima.

O artigo IJCAI 2026 (árvores, FPT) está fora de R11.

Numeração: Pereira cita “Lemmas 1 and 2 in [2]” para colocação no mesmo sentido. Em Das, o Lema 1 é NP-dificuldade; o resultado usado é o **Lemma 2**. Isso é deslize de numeração, não um terceiro lema.

---

## 3. Invariantes do MIN-STATION (o problema, não o algoritmo)

Fonte: DAS-P1, DAS-SEM, POV, BF-U, VAL-A2. A certificação futura compara o algoritmo com *isto*, não com uma versão mais cômoda.

1. `G` simples, conexo, não dirigido. R11: pesos unitários (`das_compat = exata`).
2. `S ⊆ V`, `T ⊆ V`, `|S| = |T| = m`. **Não** se exige `S ∩ T = ∅`.
3. Robôs **não rotulados**: a bijeção `S → T` é decisão, não entrada.
4. Autonomia comum `r ∈ Z_{>0}`, em **arestas**. Origem (e cada estação usada como recarga) parte com carga cheia.
5. Solução: `C ⊆ V` de cardinalidade mínima. Estações em qualquer vértice, inclusive terminais.
6. Viabilidade: existe bijeção `π: S → T` e, para cada `s`, uma caminhada de `s` a `π(s)` em que entre dois pontos de carga consecutivos há ≤ `r` arestas. Pontos de carga: `s` só no início da caminhada, depois só vértices de `C`. Destino não precisa de estação para *terminar*.
7. Sem capacidade, colisão, tempo ou fila.
8. `v ∈ S ∩ T` **não** implica que o robô em `v` fica em `v`. Permanência é *opção* viável (Das Lemma 5 usa essa opção numa melhoria). Outro matching pode mandar o robô de `v` a outro alvo e trazer outro robô a `v`.
9. Remover `v` de `S` e de `T` porque `v ∈ S ∩ T` **não** é redução válida (CE1' em `validacao-formulacao-base.md`).
10. Ótimo 0 quando existe matching em que cada par tem distância ≤ `r` (inclui `r ≥ diam(G)` e permanências suficientes).

Contagem correta de estações num único deslocamento de comprimento `L` (arestas), sem estações prévias: `max(0, ⌈L/r⌉ − 1)`. VAL-A2 registra que Das Lemma 2 usa `⌊L/r⌋`, distinto disto quando `r` divide `L`.

---

## 4. Caminhos — Das

### 4.1 Resultado teórico alegado

**[Fato]** Theorem 2: Algorithm 1 devolve solução em `O(n)` para caminho com `n` vértices. A correção é remetida ao Lemma 4.

**[Fato]** Lemma 4: após ordenar origens `s_1,…,s_m` e alvos `t_1,…,t_m` da esquerda para a direita, existe ótimo em que o robô de `s_i` vai a `t_i`.

**[Fato]** Lemma 3: cruzar em sentidos opostos não ajuda; troca de alvos não aumenta o número de estações.

**[Conferido, projetado]** O matching de Lemma 4 *não* é “cada robô fica no próprio vértice”. Se `s_i = t_i` na ordem, esse par é permanência. Se um vértice está só em `S` e outro só em `T`, o matching ordenado pode mover.

### 4.2 Pré-condições

- `G` é caminho. Vértices enumerados `v_1,…,v_n` esquerda → direita.
- `S` e `T` reordenados nessa ordem (entrada do Algorithm 1).
- `r ≥ 1` inteiro.
- `m ≤ n` no enunciado do Theorem 2; a definição só exige `|S|=|T|`.

### 4.3 Entrada / saída

Entrada: caminho ordenado, `S`, `T`, `r`.
Saída publicada: `C ⊂ P` de cardinalidade mínima (alegada).
Saída R11: ver §9. O certificador devolve o `C` do procedimento, sem consultar PLI.

### 4.4 Estado

| Nome | Início | Papel |
|---|---|---|
| `C` | `∅` | estações |
| `Tcounter` | 0 | saldo de origens vistas menos alvos vistos, na varredura |
| `Vcounter` | 0 | vértices consecutivos com `Tcounter ≠ 0` desde a última estação (ou início do trecho ativo) |

Não há estado de bateria por robô. Não há matching explícito no código.

### 4.5 Passos executáveis (Algorithm 1 literal)

Fonte de todos os passos: DAS-A1, p. 10.

```text
Passo P0 — inicializar
Fonte: C = ϕ; Vcounter=0, Tcounter=0
Condição: sempre
Ação: C ← ∅; Tcounter ← 0; Vcounter ← 0
Estado alterado: os três
Consequência: nenhuma estação ainda
```

```text
Passo P1 — para i = 1..n, vértice vi
Fonte: for every i = 1, 2, . . . , n
Condição: sempre, uma vez por vértice, esquerda → direita
Ação: executar P2, P3, P4 nesta ordem sobre vi
Estado alterado: conforme subpassos
Consequência: um único passe, O(n)
```

```text
Passo P2 — origem
Fonte: if vi ∈ S then Tcounter++
Condição: vi ∈ S
Ação: Tcounter ← Tcounter + 1
Estado alterado: Tcounter
Consequência: um robô “ainda não pareado na ordem” entra no saldo
```

```text
Passo P3 — alvo
Fonte: if vi ∈ T then Tcounter--
Condição: vi ∈ T
Ação: Tcounter ← Tcounter − 1
Estado alterado: Tcounter
Consequência: um alvo na ordem consome uma unidade do saldo
Nota: P2 e P3 são `if` independentes. Se vi ∈ S ∩ T, os dois disparam na mesma iteração; o saldo líquido em vi é 0.
```

```text
Passo P4 — trecho ativo e colocação
Fonte: if Tcounter!=0 then Vcounter++; if Vcounter==r then C = C ∪ vi; Vcounter=0
Condição: após P2–P3, Tcounter ≠ 0
Ação: Vcounter ← Vcounter + 1; se Vcounter = r, incluir vi em C e Vcounter ← 0
Estado alterado: Vcounter, possivelmente C
Consequência: estação no vértice onde o contador de vértices ativos atinge r
Se Tcounter = 0: Vcounter não muda (o texto não zera Vcounter neste ramo)
```

```text
Passo P5 — término
Fonte: return C
Condição: i = n concluído
Ação: devolver C
Estado alterado: nenhum
Consequência: obj = |C| no contrato R11
```

### 4.6 Interpretação matemática de cada passo

- Lemma 4 justifica varrer na ordem espacial e tratar o matching `s_i ↔ t_i` de forma agregada: `Tcounter` é o número de origens já vistas menos alvos já vistos. Enquanto ≠ 0, há demanda de deslocamento atravessando aquele ponto na leitura agregada.
- `Vcounter` conta **vértices** do trecho com demanda residual, não arestas. O primeiro vértice ativo (muitas vezes a própria origem) já incrementa.
- Estação quando `Vcounter = r`: o artigo diz “quando a distância se torna igual a r”. A implementação publicada mede essa “distância” em vértices do trecho ativo, inclusive o extremo já visitado.

### 4.7 Como `C` é construído e por que cada estação entra

Uma estação entra se e só se, imediatamente após processar `vi` como origem e/ou alvo, o saldo é não nulo e o número de vértices ativos desde o último reset vale `r`.

Não há teste “o robô chegou com carga 0”. Não há teste “vi já é origem com bateria cheia”. Origem pode entrar em `C` (exemplo abaixo).

### 4.8 Condição de término

Fim da lista `v_1…v_n`. Não há segundo passe. Não se minimiza entre várias `C`.

### 4.9 Casos de borda (caminho)

| Caso | Comportamento literal do Algorithm 1 | Relação com a definição (Problem 1) |
|---|---|---|
| `Tcounter` sempre 0 (inclui `S = T` como conjuntos alinhados na ordem, ou `m = 0`) | `C = ∅` | Coincide com OPT = 0 por permanência / instância vazia |
| `r ≥` comprimento do único deslocamento, `Tcounter` ativo `L` vértices com `L < r` | `C = ∅` | Pode coincidir |
| `S = {v_1}`, `T = {v_3}`, `r = 2` (VAL-A2) | `C = {v_2}` | OPT da definição = 0. Supercontagem |
| `S = {a}`, `T = {c}`, caminho `a–b–c`, `r = 1` (VAL-A2) | `C = {a,b}` | OPT da definição = `{b}`. Supercontagem e estação na origem |
| `vi ∈ S ∩ T` | P2 e P3 anulam-se; `vi` só recebe estação se o saldo *após* os dois `if` ainda for ≠ 0 (robôs de fora) | Não força permanência |
| `Tcounter = 0` no alvo final | o alvo não incrementa `Vcounter`; estação no destino só se o saldo ainda for ≠ 0 (outros robôs) | Destino sem estação para terminar: compatível neste ponto |
| `Tcounter` negativo | o pseudocódigo permite; o texto não discute. Ocorre se mais alvos que origens à esquerda, o que a ordem de Lemma 4 não deveria produzir se `|S|=|T|` e a ordem é a espacial dos dois conjuntos | **UNSPECIFIED** se a entrada violar a ordenação; com ordenação correta, o saldo no fim deve ser 0 |

### 4.10 `S ∩ T` no Algorithm 1

Tratamento **explícito no código** (dois `if`), **implícito na prova** do Lemma 4 (os seis casos de ordem incluem coincidência de posições só via as listas, não via interseção de conjuntos).

Não há ramo “ficar parado”. A permanência aparece quando, na ordem, a origem `s_i` e o alvo `t_i` são o mesmo vértice: nesse índice o saldo não abre trecho ativo *por esse par*.

### 4.11 Permanência no caminho

Se o matching de Lemma 4 usa `s_i = t_i`, aquele robô não gera intervalo de viagem. Outros robôs podem ainda atravessar o vértice; aí `Tcounter` pode ser ≠ 0 por *eles*, e uma estação pode cair nesse vértice.

### 4.12 Pontos não especificados pela fonte

1. Relação entre `Vcounter` (vértices) e passos (arestas). O texto mistura “distance” com o contador de vértices.
2. `Vcounter` não é zerado quando `Tcounter` volta a 0. Se um trecho ativo acaba e outro começa mais à direita, o contador pode *continuar*. Com matching ordenado e um único passe, trechos ativos são intervalos; um intervalo que fecha e reabre depois deixaria resíduo. **[Hipótese de implementação]** com `S`, `T` ordenados e `|S|=|T|`, os trechos com `Tcounter≠0` são disjuntos e o resíduo na prática só importa se o saldo zera no meio. Caso de teste: dois pares separados.
3. Lemma 2 coloca estações em `s_1+r, s_1+2r, …` (índices de vértice) e conta `⌊|x−s_1|/r⌋`. Algorithm 1 não replica essa fórmula. São dois procedimentos da mesma seção.
4. Theorem 2 afirma correção via Lemma 4. Lemma 4 fala do matching, não da regra `Vcounter==r`. A ponte Lemma 2 → Algorithm 1 não está escrita como invariante de `Vcounter`.

### 4.13 Três objetos que não devem ser fundidos

| ID | O que é | Status para R11 |
|---|---|---|
| PATH-DEF | Problem 1 + contagem `⌈L/r⌉−1` | Régua do projeto (baseline / enumeração / validador) |
| PATH-L2 | Fórmula e colocação do Lemma 2 | Bloco de prova; **não** é o Algorithm 1 |
| PATH-ALG1 | Pseudocódigo p. 10 | **Única** variante executável de caminho em R11 |

Não se implementa um “Algorithm 1 corrigido” como se fosse Das. Se PATH-ALG1 divergir de PATH-DEF, isso é dado experimental (possível `suboptimal` / `infeasible_solution`), não licença para consertar o certificador.

**Estado PATH-ALG1 vs PATH-DEF:** a divergência em casos com `r | L` já está em VAL-A2. R11 **testa** o algoritmo publicado contra PATH-DEF. Não se declara o artigo falso antes do lote e da regra de comunicação da spec.

---

## 5. Ciclos — Das

### 5.1 Resultado teórico alegado

**[Fato]** Lemma 5: existe ótimo em que pelo menos uma aresta do ciclo não é atravessada por nenhum robô.

**[Fato]** A prova usa (i) se todas as arestas são usadas e nada se cruza, então “every robot is starting from a target position” e ninguém precisa mover (Fig. 3); (ii) cruzamento em sentidos opostos: Lemma 3 produz aresta livre; (iii) cruzamento no mesmo sentido: um robô **permanece** em `s_i` ocupando o alvo `t_o`, outro não atravessa `[s_i, s_{i+1}]`.

**[Fato]** Algorithm 2: para cada aresta, remove-a, chama Algorithm 1 no caminho, guarda o `X` de menor cardinalidade.

**[Fato]** Theorem 3: `O(n²)` porque `n` arestas × `O(n)` no caminho.

### 5.2 O que diferencia ciclo de caminho

No ciclo há duas direções e não há “esquerda” canônica. O Lemma 5 reduz a um caminho: adivinhar a aresta não usada. O Algorithm 2 **não** tem teoria própria de colocação; herda PATH-ALG1, inclusive a supercontagem.

### 5.3 Quebras / orientações

```text
Passo C0
Fonte: C = {v0, v2, . . . , vn−1}
Condição: início
Ação: C ← V  (leitura: todos os vértices. A lista omite v1 na notação; tratar como sentinela |C|=n, não como “pular v1”)
Estado: C sentinela, pior cardinalidade
```

```text
Passo C1 — para i = 0..n−1
Fonte: for every i = 0, 1, 2, . . . , n − 1
Ação: P ← G menos a aresta {v_i, v_{(i+1) mod n}}
Consequência: P é caminho com os mesmos n vértices. Ordem esquerda→direita do Algorithm 1 = v_{(i+1)}, v_{(i+2)}, …, v_i (sentido horário a partir do sucessor da aresta removida).
```

```text
Passo C2
Fonte: X = Min-Station-On-Path(P)
Ação: reordenar S e T da esquerda para a direita em P; executar PATH-ALG1
Nota: o artigo não escreve a reordenação. Sem ela, Algorithm 1 está mal definido. Leitura obrigatória CYCLE-ORDER: reordenar. Não é fortalecimento; é pré-condição publicada do Algorithm 1.
```

```text
Passo C3
Fonte: if cardinality of X ≤ cardinality of C then C = X
Ação: se |X| ≤ |C|, C ← X
Consequência: empate fica com a **última** quebra de índice maior (teste `≤`, não `<`)
```

```text
Passo C4
Fonte: return C
Ação: devolver o C de menor |X| (com o desempate acima)
```

Não se enumeram as duas orientações do ciclo como grafos distintos: uma quebra já lineariza numa direção. A quebra da aresta oposta gera a outra linearização.

### 5.4 De onde vem `O(n²)`

`n` iterações, cada uma `O(n)` no passe do caminho (Theorem 2). Ordenar `S,T` em cada quebra é `O(m log m)` ou `O(n)` se for extraído da ordem do caminho; de qualquer modo `O(n²)` cobre.

### 5.5 Escolha da melhor solução

Mínimo de `|X|` entre as `n` quebras. Não se escolhe `X` por inclusão de vértices. Empate: última quebra (C3). Dois `C` diferentes com o mesmo `|C|` são igualmente aceitáveis para acordo R11 (a spec compara viabilidade + objetivo, não igualdade de conjuntos).

### 5.6 Dependência do caminho

Toda estação de ciclo vem de PATH-ALG1. Qualquer defeito de `Vcounter` reproduz-se, possivelmente em quebras diferentes com `|X|` diferentes **antes** do mínimo. Daí os testes “quebras discordam, o min alinha ou não”.

### 5.7 `S ∩ T` e permanência no ciclo

Lemma 5 trata permanência **explicitamente** na prova. Algorithm 2 **não** tem ramo extra: herda os dois `if` do caminho.

Se `S = T` como conjuntos e o matching identidade é ótimo, a prova diz que ninguém precisa mover. PATH-ALG1 em qualquer quebra vê, para cada `v ∈ S ∩ T`, saldo líquido 0 naquele vértice; se não houver outros desbalanceamentos, `C = ∅`.

### 5.8 Pontos não especificados

1. Notação `{v0, v2, …, vn−1}` vs `{v0,…,vn−1}`. Leitura CYCLE-SENTINEL: `C ← V`.
2. Reordenação de `S,T` após a quebra: implícita (CYCLE-ORDER).
3. Ciclo de 1 ou 2 vértices: a definição de ciclo no artigo pede ≥ 3 vértices. Entrada menor: `invalid_input`.
4. `r ≥ n`: diâmetro do ciclo é `⌊n/2⌋`. `r ≥ diam` ⇒ OPT = 0 na definição se o matching espacial funcionar; PATH-ALG1 ainda pode colocar estações em alguma quebra. O min sobre quebras pode ou não zerar. Teste obrigatório.

---

## 6. Aranhas — Pereira & Ravelo

### 6.1 Definições **[Fato]**

- Aranha: árvore com exactamente um vértice `c` de grau ≥ 3; os outros têm grau ≤ 2.
- Radiais: componentes de `G − c`. Cada radial é um caminho. Folha da aranha = único grau 1 da radial. O outro extremo da radial é o único vizinho de `c` nessa radial.
- Radial de um vértice: folha adjacente a `c`.
- Distâncias: número de arestas da árvore. De `c` a um vértice da radial `R_i` a distância é 1 + posição na radial.

O centro **não** pertence a radial alguma.

### 6.2 Revisão de caminhos no artigo (não reimplementar aqui)

§3 resume Das: estações no limite `r` no mesmo sentido; não cruzar em sentidos opostos; matching esquerda–direita. Aponta os lemas no apêndice (o `.md` do repositório **não** inclui esse apêndice).

### 6.3 Lemma 1 — o que afirma e o que a prova faz

**Afirma:** numa solução ótima, as estações *dentro de `R_i`* podem ser determinadas pelo “greedy path strategy” da folha para `c`, colocando estações só quando a capacidade `r` é atingida.

**Prova, literalmente:**

1. Quem sai de `R_i` para `SP \ R_i` ou o contrário passa por `c`.
2. Segmentos inteiramente em `R_i` têm topologia de caminho.
3. Por “Lemmas 1 and 2 in [2]” (leitura: Das Lemma 2), no mesmo sentido minimiza-se colocando no vértice mais longe possível (distância `r`).
4. Processar folha → `c` minimiza estações em `R_i` e maximiza a carga restante `r'` em `c`, com **`0 < r' ≤ r`**.
5. Colocar mais cedo só diminuiria (ou preservaria) `r'` em `c` e poderia forçar estação extra fora, contradizendo otimalidade.

**O que a prova não faz:**

- Não escreve pseudocódigo.
- Não diz se o “greedy path strategy” é o Algorithm 1 de Das (dois sentidos + `Tcounter`) ou só o guloso num sentido (saindo da radial).
- Não processa robôs que *entram* na radial, salvo a frase “or vice versa” no primeiro parágrafo, sem regra de carga à chegada.
- Não trata pares origem–alvo ambos em `R_i` além de “topologia de caminho”.
- Não trata `c ∈ S ∪ T`.
- Exclui `r' = 0` por hipótese escrita.

### 6.4 Lemma 2 — o que afirma e o que a prova faz

**Afirma:** existe ótimo em que o robô de maior carga restante é associado a um alvo (ou estação) na radial *mais longe* entre as que ainda têm alvos restantes.

**Prova:** troca. `r_a` máxima carga; `t_f` alvo numa radial mais longe; se `r_a` não vai para essa radial, troca com `r_b` que vai. `r_a` chega a `c` com pelo menos a carga de `r_b`, logo de `c` alcança `t_f` e `r_b` alcança o alvo mais perto. A troca “não aumenta o número de estações”.

**O que a prova não faz (SP-R3):**

- Não menciona estações já colocadas na radial do alvo.
- Não menciona pares internos à mesma radial ainda em `L_R`/`L_T`.
- Não define `L_R` e `L_T` além de “remaining robots/targets”.
- Não justifica que a distância relevante é só `d(c, t)` ignorando recargas intermediárias.
- O parêntese “target (or charging station)” não define que estação substitui um alvo na ordenação.

### 6.5 Theorem 1 — o que afirma e o procedimento *derivado* (não fortalecido)

**Afirma:** MIN-STATION em aranha resolve-se de forma óptima em `O(|V|)`.

**Corpo do algoritmo que o texto realmente descreve:**

1. Para cada radial, independente, folha → centro; Lemma 1; tempo soma `O(|V|)`.
2. Agregar estado em `c`. Construir `L_R`, `L_T`. Associar por Lemma 2 (ordenar; counting sort `O(|V|)`).
3. Duas condições em que **não** se coloca estação em `c`:
   - (C1) após o matching guloso, cada robô alcança o alvo emparelhado com a carga restante;
   - (C2) um robô pode ir primeiro a alguma estação já colocada numa radial, a mais próxima de `c` em *alguma* radial, e daí todos os alvos são alcançáveis dessa estação.
4. Se nenhuma vale, “any feasible solution must place a charging station at `c`”.
5. Justificativa de otimalidade do sítio `c`: “all robots in `L_R` can reach `c`, and from `c` every target or charging station associated with `L_T` is reachable”.
6. Checagens por par em `O(1)`, `O(|V|)` pares.

Não há terceiro passo “completar estações na radial do alvo”. Não há reexecução do guloso nas radiais depois do matching.

### 6.6 Hipóteses necessárias (não silenciar)

- Robôs que precisam de `c` chegam a `c` (depende do guloso da radial de origem e de `r'`).
- De `c`, todo alvo restante é alcançável (com a estação em `c` e/ou estações já existentes). Isto é a afirmação atacada por SP-R2.
- `0 < r'`.
- `L_R`/`L_T` bem definidos após o passe nas radiais.
- O matching Lemma 2 não aumenta estações mesmo com estações internas (não provado no texto).

### 6.7 Procedimento executável derivado — eixos de leitura

O artigo não fecha um único pseudocódigo. R11 não escolhe o eixo que coincide com o baseline. Variantes futuras são produtos documentados abaixo, não um algoritmo “consertado”.

#### Eixo SP-L1 — o que corre em cada radial

**Interpretação A (`SP-L1-A`, um sentido, só quem sai)**  
Da folha para o vizinho de `c`, percorrer o caminho. Manter carga de robôs que ainda vão a `c` (nascidos na radial e não consumidos por um alvo *na própria radial*, se esses alvos forem resolvidos localmente ou não — ver eixo SP-INT). Colocar estação quando a carga de algum robô que continua cairia abaixo de 1 na próxima aresta, no espírito “atingiu `r`”. Recarregar nesses vértices. Quem só entra depois, neste passe, não existe.

**Interpretação B (`SP-L1-B`, Algorithm 1 de Das no caminho `folha…vizinho(c)`)**  
`S' = S ∩ V(R_i)`, `T' = T ∩ V(R_i)`. Rodar PATH-ALG1. `c` não está no caminho. Robôs cujo alvo está fora ficam como origens sem alvo no caminho: `Tcounter` pode não zerar. Isso **não** está no artigo. É uma costura possível, não uma citação.

**O artigo não afirma B.** B é costura com Das. A é mais próxima da frase “from the leaf toward `c`” + maximizar `r'` em `c`.

**Estado:** MULTIPLE-READINGS. Variantes futuras: `spider-L1A`, `spider-L1B`.

#### Eixo SP-INT — pares na mesma radial

**A:** resolver internamente no passe da radial (caminho), e só mandar a `c` o excesso de origens.  
**B:** mandar tudo que não for “óbvio” a `c` e deixar o Lemma 2 misturar radiais, inclusive alvos que tinham origem na mesma radial.

O Lemma 1 menciona segmentos internos; o Lemma 2 fala de `L_T` restantes. Nenhuma regra de partição.

**Estado:** MULTIPLE-READINGS (`SP-INT-A` / `SP-INT-B`).

**Fecho conservador de implementação (`SP-INT-A-EXEC`, 2026-10-07).** Para tornar
as variantes oficiais executáveis sem inventar quais terminais “sobram” numa
radial mista e desbalanceada:

- se `|S_i|=|T_i|`, INT-A resolve a subinstância interna com PATH-ALG1 na ordem
  folha→centro e nenhum terminal dessa radial entra em `L_R/L_T`;
- se `T_i=∅`, as origens locais são os robôs restantes; L1A coloca estações a
  cada `r` **arestas** a partir da origem mais profunda, folha→centro;
- se `S_i=∅`, os alvos locais permanecem em `L_T`; L1A não cria estação só por
  haver alvo;
- se `S_i` e `T_i` são ambos não vazios e `|S_i|≠|T_i|`, a fonte não determina
  quais terminais são resolvidos internamente. As variantes oficiais devolvem
  `status=unspecified` em vez de escolher um matching por conveniência.

`spider-B` mantém a mesma regra de INT-A para decidir o que sobra, mas usa o
passe literal PATH-ALG1 sobre cada radial para a colocação L1B, inclusive em
radiais só com origem ou só com alvo. Isso preserva a costura documentada e
pode produzir estações diferentes de `spider-A`.

Este fecho não afirma que o artigo contém essa regra; ele delimita precisamente
onde a implementação se recusa a completar o silêncio da fonte.

#### Eixo SP-IN — robôs que entram (SP-R1)

Nenhuma regra de carga para quem chega a `c` *vindo de outra radial* e segue para um alvo em `R_i`. As estações de `R_i` foram fixadas no passe folha→`c` (saindo).

**Estado:** a fonte não especifica o comportamento do *procedimento* para essa direcção. Ver SP-R1.

#### Eixo SP-R0 — fronteira `r' = 0` (SP-R5)

Texto: `0 < r' ≤ r`.  
**A:** se o guloso produz `r' = 0`, devolver `unspecified`.  
**B:** aceitar `r' = 0` como “chegou a `c` na última unidade; não sai de `c` sem recarga”.  
**C:** recuar e forçar estação no vizinho de `c` para garantir `r' > 0` (isto *altera* o guloso publicado; não é leitura fiel).

**Estado:** A e B são leituras; C é reconstrução. C não entra como “o algoritmo do artigo”.

#### Eixo SP-C1C2 — teste no centro

**C1** precisa de `d(c, t)` vs `r'` no matching. Distância na árvore é única.

**C2** é ambíguo:

- `SP-C2-1`: existe *uma* estação `σ` (a mais próxima de `c` em todo o grafo, entre as já colocadas) tal que todo robô de `L_R` alcança `σ` com `r'` e todo alvo de `L_T` é alcançável a partir de `σ` com autonomia `r` (recarga em `σ`).
- `SP-C2-2`: para cada robô, basta alcançar *alguma* estação mais próxima de `c` *na radial do seu alvo*.
- `SP-C2-3`: “closest charging station to `c` in some radial” = mínimo `d(c, σ)` sobre `σ ∈ C ∩ radiais`; se `C` nas radiais for vazio, C2 é falsa.

Se C1 e C2 falham: incluir `c` em `C`. O texto **para**. Não completa a rota até `t`.

### 6.8 Complexidade `O(|V|)`

Soma dos comprimentos das radiais + counting sort de distâncias em `[0, |V|−1]` + `O(|L_R|)` checagens. **[Fato]** no texto. Só vale se cada radial é um passe linear. Chamar PATH-ALG1 em cada radial ainda é linear. Não justifica um segundo guloso nas radiais de alvo depois do matching: isso ainda seria `O(|V|)`, mas **não está no artigo**.

---

## 7. Leituras obrigatórias SP-R1 … SP-R5

### SP-R1 — Robôs que entram numa radial

**Questão**

O Lemma 1 argumenta estações em `R_i` com o movimento *para* `c`. Um robô cujo alvo está em `R_i` e cuja origem está noutra radial chega a `c` com carga que depende do passe da radial de origem e de haver ou não estação em `c`. Como o procedimento publicado trata essa direcção?

**O que a fonte afirma explicitamente**

Quem vai de `R_i` para fora ou o contrário passa por `c`. Segmentos internos a `R_i` são um caminho. O guloso folha→`c` maximiza `r'` *ao chegar a* `c`.

**O que a fonte não afirma**

Regra de colocação para quem *desce* `R_i` depois de `c`. Dependência da carga em `c` em relação ao passo do centro (circularidade: o centro ainda não foi decidido quando as radiais são processadas). Que as estações do passe de saída sirvam à descida.

**Interpretação A (`SP-R1-A`)**

O procedimento não recoloca estações para a descida. Quem entra usa `C` já fixado na radial + possivelmente `{c}`. Se isso não alcança o alvo, o conjunto devolvido pode ser inviável. Não se “completa” a radial.

**Interpretação B (`SP-R1-B`)**

Depois do matching, reaplicar guloso da Folha? Não: da *centro para a folha* na radial do alvo, com a carga em `c`. Isso não está no artigo. Seria algoritmo novo.

**Consequência para uma futura implementação**

`spider-L1A` / `spider-L1B` seguem A no lote oficial. B não é variante do artigo; se algum dia existir, outro pré-registro e outro nome (`spider-repair-inward`), fora de R11 como certificador da publicação.

**Caso de teste necessário**

Três radiais. Origem em `R_1`, alvo em `R_2`, terceiro radial só para ser aranha. Pelo menos uma estação no passe de saída de `R_1`. `R_2` sem origens. Ver se `C ∩ R_2` é vazio e se `viavel(C)` falha.

**Estado**

MULTIPLE-READINGS (A = publicado; B = reconstrução, fora do certificador fiel).

---

### SP-R2 — Alcance a partir do centro

**Questão**

O Theorem 1 diz que, se for preciso uma estação extra, ela fica em `c`, porque de `c` todo alvo (ou estação associada a `L_T`) é alcançável. Isso vale quando `d(c,t) > r` numa radial sem robô saindo?

**O que a fonte afirma explicitamente**

“if a charging station is required, it must be placed at the center `c`, since all robots in `L_R` can reach `c`, and from `c` every target or charging station associated with `L_T` is reachable.”

Condições C1 e C2; senão, colocar `c`.

**O que a fonte não afirma**

Que existam estações em toda radial com alvo longe. Que `d(c,t) ≤ r` sempre. Um passo extra nas radiais vazias.

**Interpretação A (`SP-R2-A`, literal)**

Radiais sem origem que dispare o guloso ficam sem estações. `L_T` contém `t`. C1: `r' ≥ d(c,t)`? Se `d(c,t)=2r+1`, não. C2: se não há `σ ∈ C` nas radiais, C2 falha (leitura SP-C2-3). Coloca-se `c`. De `c` com carga `r` ainda se tem `2r+1 > r`. O procedimento devolve `C ⊆` (estações das radiais de *saída*) `∪ {c}` e **para**. Não torna `t` alcançável.

**Interpretação B (`SP-R2-B`)**

Completar a radial de `t` com guloso a partir de `c` após decidir `{c}`. Não está no Theorem 1. Reconstrução.

**Consequência para uma futura implementação**

Implementar A. Esperar possível `alg_viavel = false` ou `alg_obj < OPT` se o código devolver `C` pequeno demais. Não ajustar A depois de ver o baseline. B fora do certificador fiel.

**Caso de teste necessário**

Construção abstracta §7.1 (ainda sem ficheiro de instância).

**Estado**

MULTIPLE-READINGS. A é a leitura do texto. A afirmação de alcance **não está justificada** neste caso **[Conferido, leitura]**. Isso não é ainda um contraexemplo computacional.

#### 7.1 Construção abstracta obrigatória (não materializada agora)

Parâmetros: inteiro `r ≥ 1`. Vértices:

- centro `c`;
- radial `R_s`: um vértice `s`, aresta `s–c` (logo `d(s,c)=1`);
- radial `R_t`: caminho `u_1–u_2–…–u_{2r+1}` com aresta `c–u_1` e `t = u_{2r+1}`, logo `d(c,t)=2r+1`;
- radial `R_dummy`: um vértice `d`, aresta `d–c` (grau de `c` é 3). Sem `S`/`T` em `R_dummy`.

Instância:

```text
V = {c, s, u_1, …, u_{2r+1}, d}
S = {s}
T = {t}
E = {s c, c u_1, u_1 u_2, …, u_{2r} u_{2r+1}, c d}
R_t não contém origem
```

Análise sob o procedimento literal (eixo SP-L1-A, SP-R2-A), `r ≥ 2`:

| Pergunta | Resposta **[Conferido]** sobre o *procedimento publicado*, não sobre OPT |
|---|---|
| Estações em `R_s` | Comprimento 1 < `r`. Guloso folha→`c` não atinge intervalo de comprimento `r`. `C ∩ R_s = ∅` |
| Carga em `c` | Sai de `s` com carga `r`, uma aresta: `r' = r−1 > 0` |
| Estações em `R_t` | Sem robô saindo. `C ∩ R_t = ∅` |
| Estações em `R_dummy` | Nenhuma |
| `L_R`, `L_T` | Um robô em `c` com `r' = r−1`; um alvo `t` a `2r+1` |
| C1 | `r−1 ≥ 2r+1`? Não |
| C2 | Sem estações nas radiais; falha na leitura SP-C2-3 |
| Estação em `c` | Sim, o texto manda colocar |
| `t` alcançável com esse `C` | `C = {c}`. De `c` no máximo `r` arestas com uma carga. `2r+1 > r`. **Não** |
| OPT da definição | O caminho `s–c–…–t` tem comprimento `2r+2`. Precisa de `⌈(2r+2)/r⌉−1 = 2` estações (para `r ≥ 2`). Ex.: `r=2`, `L=6`, duas estações. `{c}` tem 1 e é inviável |

Para `r = 1`: `r' = 0` ao chegar a `c`. Sai do domínio escrito `0 < r'`. Ver SP-R5. `d(c,t)=3`. Mesma falha de alcance se só se coloca `c`.

ID congelado para futura materialização: `spider-reading-02` (spec e `r11_catalog.py`). O arquivo de instância ainda **não** foi materializado.

---

### SP-R3 — Argumento de troca do Lemma 2

**Questão**

A troca `r_a ↔ r_b` preserva o número de estações quando já há estações na radial do alvo, ou quando existem pares internos à mesma radial, ou quando há mistura interno/cruzado?

**O que a fonte afirma explicitamente**

Se `r_a` tem carga ≥ `r_b` em `c`, então de `c` `r_a` alcança `t_f` e `r_b` alcança o alvo mais perto. A troca não aumenta estações.

**O que a fonte não afirma**

Invariância das estações *já colocadas* nas radiais. Interacção com pares `s,t ∈` mesma radial. Que “alcançar de `c`” use só `d(c,t)` sem recarga interna.

**Interpretação A**

O matching ordenado (carga ↓, distância de `c` ↓) é a regra do procedimento, mesmo quando a prova não cobre o caso. Implementar a ordenação. Não “consertar” o matching com PLI.

**Interpretação B**

Declarar `unspecified` quando `L_T` contém um alvo numa radial que já tem estação, ou quando existe par interno misturado com cruzado.

A é executável e fiel à *estratégia* (“our strategy is to perform such a matching”). B é fiel à *lacuna da prova*.

**Consequência para uma futura implementação**

Lote oficial: variante `spider-L2-sort` = A. Variante `spider-L2-gap` = B só nos casos listados, `status=unspecified`. As duas entram com IDs estáveis. Não se elege A porque o baseline também ordena.

**Caso de teste necessário**

(1) Só cruzado, radiais sem estações internas. (2) Cruzado + estação já na radial do alvo (saída noutro robô daquela radial — misturar SP-R1). (3) Dois pares na mesma radial e um cruzado.

**Estado**

MULTIPLE-READINGS.

---

### SP-R4 — `S ∩ T` e permanência

**Questão**

O MIN-STATION permite `S ∩ T ≠ ∅` e permanência. O artigo das aranhas trata?

**O que a fonte afirma explicitamente**

Definição: `S ⊆ V`, `T ⊆ V`, `|S|=|T|`, sem disjunção. Mesmo problema de Das. Provas do Lemma 1–2 e Theorem 1: nenhuma ocorrência de interseção nem de “remain”.

**O que a fonte não afirma**

Regra para `v ∈ S ∩ T` em radial. Regra para `c ∈ S ∩ T`. Se permanência é forçada ou opcional.

**Interpretação A (`SP-R4-KEEP`)**

Não se apaga `v` de `S` e `T`. Vértices de interseção nas radiais entram no passe como origem *e* alvo (dois `if`, se se usar PATH-ALG1; ou saldo líquido 0 no guloso de um sentido). Em `c`: origem em `c` já está em `c` com `r' = r`; alvo em `c` tem `d(c,c)=0`. O matching pode usar permanência ou não.

**Interpretação B (`SP-R4-CANCEL`)**

Cancelar cada vértice de `S ∩ T` como par permanência *antes* do algoritmo. **Inválido como redução do problema** (CE1'). Não é leitura do artigo. **Não implementar** como certificador.

**Interpretação C (`SP-R4-UNSPEC`)**

Se `S ∩ T ≠ ∅`, `status = unspecified`, porque as provas não cobrem.

C é conservadora e fiel ao silêncio da prova. A é fiel à definição do problema que o próprio artigo adopta na introdução. As duas são matematicamente defensáveis para *implementação*. B não é.

**Consequência para uma futura implementação**

Variantes `spider-sit-keep` (A) e `spider-sit-unspecified` (C). Nunca B. Caminho e ciclo usam os `if` independentes de Das (KEEP), porque o código existe.

**Caso de teste necessário**

Os seis da §8.

**Estado**

MULTIPLE-READINGS (A e C). B rejeitada.

---

### SP-R5 — Fronteira `r' = 0`

**Questão**

O texto assume `0 < r'`. O que faz o algoritmo se o robô chega a `c` com carga 0?

**O que a fonte afirma explicitamente**

`r'` restante em `c` satisfaz `0 < r' ≤ r`. Counting sort em `[0, |V|−1]` (distâncias; não afirma que 0 é carga).

**O que a fonte não afirma**

Regra para `r' = 0`. Se carga 0 ainda “alcançou `c`”. Se carga 0 pode ser ordenada no Lemma 2.

**Interpretação A (`SP-R5-UNSPEC`)**

Qualquer `r' = 0` ⇒ `status = unspecified`.

**Interpretação B (`SP-R5-ZERO`)**

`r' = 0` significa: o robô está em `c` e não atravessa nenhuma aresta extra sem recarga. Pode ocupar um alvo em `c` (`d=0`). Não pode descer radial. C1 para `d(c,t)>0` falha. C2 depende de estação já existente. Provável colocação de `c` (recarga).

**Interpretação C**

Forçar estação antes de `c` para evitar 0. Reconstrução. Fora do certificador fiel.

**Consequência para uma futura implementação**

Variantes `spider-r0-unspecified` e `spider-r0-zero`. Caso mínimo: SP-R2 com `r = 1`.

**Caso de teste necessário**

Radial de um vértice, `r = 1`, origem na folha, alvo noutra radial. Também: radial de comprimento exactamente `k r` até `c`.

**Estado**

MULTIPLE-READINGS (A, B). C rejeitada.

---

## 8. `S ∩ T` e permanência — análise explícita

Semântica do projecto (não negociar):

```text
v ∈ S ∩ T
```

não implica

```text
o robô em v fica em v.
```

Permanência em `v` é sempre *um* matching viável localmente para uma unidade de origem e uma de alvo. O óptimo global pode usar outro matching.

### 8.1 `S ∩ T = ∅`

Das caminhos/ciclos: os `if` não coincidem no mesmo vértice. Pereira: caso único que as provas *parecem* ter em mente, sem o dizer. Implementação: caso normal.

### 8.2 Um vértice `v ∈ S ∩ T` (não o centro, ou num caminho/ciclo)

Das Algorithm 1: P2 e P3. Saldo líquido 0 *devido a esse vértice*. Outros robôs podem manter `Tcounter ≠ 0`.  
Das ciclo: Lemma 5 usa permanência noutro vértice da prova; o código não especializa.  
Pereira: se `v` está numa radial, L1/L2 não mencionam. Leituras SP-R4-A/C.

### 8.3 Centro `c ∈ S ∩ T`

`c` não está em radial. O passe L1 não o vê.

- Origem em `c`: já em `c`, carga `r` (cheia), sem guloso de chegada.
- Alvo em `c`: `d(c,c)=0`.
- Permanência: o robô que começa em `c` *pode* ocupar o alvo em `c`.
- Matching Lemma 2 *pode* enviar esse robô (carga `r`, máxima possível) ao alvo mais longe, e trazer outro a `c`.

Nada disto está no artigo. Variantes KEEP vs UNSPEC. Não cancelar `c` a priori (SP-R4-B).

### 8.4 Robô que *pode* permanecer

Sempre que existe `v ∈ S ∩ T`, a definição permite a caminhada de comprimento 0 em `v` para *uma* unidade. Não exige estação.

### 8.5 Matching que utiliza permanência

Óptimo pode ser identidade em alguns vértices de interseção. PATH-ALG1 não escolhe matching explicitamente; o saldo agregado *simula* Lemma 4, que pode coincidir com permanência quando `s_i` e `t_i` são o mesmo vértice na ordem. Em aranha, só o eixo KEEP + Lemma 2 pode *deixar de* usar permanência no centro.

### 8.6 Matching em que a interseção não é permanência

Exemplo abstracto em caminho: `S = {v_2, v_3}`, `T = {v_1, v_3}`, `v_3 ∈ S ∩ T`. Lemma 4 ordena origens `v_2,v_3` e alvos `v_1,v_3`, logo `s_1=v_2→t_1=v_1`, `s_2=v_3→t_2=v_3` (permanência no segundo). Outro matching: `v_3→v_1` e `v_2→v_3` (a interseção *não* é permanência do robô que está em `v_3`… espera: o robô em `v_3` iria a `v_1`, o de `v_2` a `v_3`). Lemma 4 afirma que o matching ordenado não é pior. O Algorithm 1 implementa o agregado desse matching, não o segundo.

Teste: instância em que o segundo matching exigiria estações diferentes. Documentar o `C` de PATH-ALG1 e o OPT da definição.

### 8.7 Quem trata o quê

| Fenómeno | Das caminho | Das ciclo | Pereira aranha |
|---|---|---|---|
| `S ∩ T` na definição | implícito (não proíbe) | implícito | explícito na def., silêncio nas provas |
| Permanência | só via saldo / Lemma 4 | **explícita** no Lemma 5 | não trata |
| Centro ∩ | n/a | n/a | não trata |
| Forçar ficar em `v` | não | não | não |

---

## 9. Contrato dos certificadores R11

Interface comum. Sem Python neste documento.

### 9.1 Campos

| Campo | Semântica |
|---|---|
| `status` | Resultado da *execução fiel*. Não é o acordo com o OPT. |
| `C` | Conjunto de vértices devolvido pelo procedimento da variante. `∅` se `status ≠ ok` (não inventar conjunto). |
| `obj` | `|C|` **se e só se** `status = ok`. Caso contrário, ausente / nulo, nunca um inteiro inventado. |
| `variant` | ID estável da matriz §10 (`path-alg1`, `cycle-alg2`, `spider-L1A-keep`, …). |
| `notes` | IDs de leitura disparados, quebra de ciclo escolhida, `r'` observados, motivo de `unspecified`. Sem consulta a solver. |

### 9.2 Estados de `status` (mínimo)

| Valor | Quando |
|---|---|
| `ok` | A variante tem leitura fechada para esta entrada e correu o procedimento até devolver um `C`. **Não** afirma que `C` é viável ou óptimo. |
| `unspecified` | A leitura da variante declara silêncio da fonte neste caso (`r'=0` na variante UNSPEC, `S∩T` na variante sit-unspecified, etc.). |
| `invalid_input` | A entrada não é da classe da variante (não é caminho / não é ciclo `n≥3` / não é aranha), ou `|S|≠|T|`, ou `r` não é inteiro ≥ 1. |

Nenhum outro estado no certificador. Timeout, `cap_exceeded`, falha de Gurobi pertencem ao *runner* de comparação, não ao algoritmo especializado.

### 9.3 Invariante

```text
status = ok  ⇒  obj = |C|
```

### 9.4 Independência

O corpo do certificador **não** consulta:

- `baseline.py` / Gurobi;
- `opt_por_enumeracao`;
- F-CC / F-C3;
- o validador, para *construir* `C`.

O validador entra só em `verify_r11.py` e `run_r11.py`, depois de `C` existir.

### 9.5 `r ≥ diam(G)`

A spec pede `C = ∅`, `obj = 0` quando a instância é viável sem recarga. **[Conferido]** isso é a definição PATH-DEF, não necessariamente PATH-ALG1.

Contrato:

- Se a *variante publicada* devolver `C = ∅`, `status=ok`, `obj=0`.
- Se PATH-ALG1 devolver `C ≠ ∅` mesmo com `r ≥ diam(G)`, **não** substituir por vazio. Reportar o `C` literal. O teste local confronta com o validador (`OPT=0`, possível `suboptimal`).
- Não implementar um atalho `if r >= diam: return ∅` no certificador de Das: isso seria reconstrução.

Para aranha, o mesmo: sem atalho que tape SP-R2.

### 9.6 Quem chama o quê

```text
certificador(classe, variant) : instância → {status, C, obj, variant, notes}
```

Ciclo chama caminho na mesma política PATH-ALG1, sem solver.

---

## 10. Matriz leitura → variante futura → teste

| ID | Fonte | Decisão matemática | Variante futura | Teste necessário |
|---|---|---|---|---|
| PATH-01 | DAS-A1 | Um passe, `Tcounter`/`Vcounter`, estação se `Vcounter==r` | `path-alg1` | OPT 0; uma estação; várias; `r\|L` (VAL-A2); origem recebe estação |
| PATH-02 | DAS-A1 P2–P3 | `S∩T`: dois `if`, saldo líquido 0 | `path-alg1` | um vértice em `S∩T`; múltiplos; matching que não usa permanência |
| PATH-03 | DAS-L4 | Ordenar `S` e `T` esquerda→direita antes do passe | `path-alg1` | pares cruzados vs ordenados |
| PATH-04 | DAS-L2 vs A1 | Fórmula `⌊L/r⌋` **não** é o código | *(não implementar L2 como certificador)* | documentar divergência A1 vs L2 vs DEF nos mesmos casos |
| PATH-05 | VAL-A2 / Problem 1 | Supercontagem possível; não corrigir | `path-alg1` | `v1–v2–v3`, `r=2`; `a–b–c`, `r=1` |
| PATH-06 | Spec D / PATH-DEF | `r ≥ diam` pode ter OPT 0; A1 pode não | `path-alg1` | caminho longo, `r = n−1` |
| CYCLE-01 | DAS-A2 | `n` quebras; min `|X|`; empate última | `cycle-alg2` | quebras com `|X|` diferentes; simetria |
| CYCLE-02 | CYCLE-SENTINEL | `C` inicial = `V` | `cycle-alg2` | n=3, OPT 0 |
| CYCLE-03 | CYCLE-ORDER | Reordenar `S,T` no caminho da quebra | `cycle-alg2` | `S,T` não monótonos no sentido horário inicial |
| CYCLE-04 | DAS-L5 | Prova usa permanência; código não ramifica | `cycle-alg2` | Fig. 3 abstracta: todo `s` é também `t`, sem cruzar |
| CYCLE-05 | DAS-T3 | `O(n²)` via n×PATH-ALG1 | `cycle-alg2` | herança da supercontagem numa quebra, min sobre as outras |
| SP-L1-A | PR-L1 | Guloso um sentido folha→`c` | `spider-L1A-*` | radial desigual; radial de 1 vértice |
| SP-L1-B | costura Das | PATH-ALG1 em `R_i` | `spider-L1B-*` | mesmo lote que L1A, comparar `C` |
| SP-INT-A | PR-L1 “path topology” | pares internos resolvidos na radial | (combinar com L1A/B) | só movimento intramural |
| SP-INT-B | silêncio L2 | internos vão a `L_R`/`L_T` | (combinar) | mistura interno + cruzado |
| SP-R1-A | PR-L1 silêncio na descida | sem completar radial de entrada | todas fiéis | origem noutra radial, alvo em radial sem saída |
| SP-R1-B | reconstrução | guloso centro→folha depois | *fora de R11 fiel* | — |
| SP-R2-A | PR-T1 literal | no máximo +`{c}`; sem estações em radial vazia | todas fiéis | construção §7.1, `spider-reading-02` |
| SP-R2-B | reconstrução | completar `R_t` | *fora* | — |
| SP-R3-A | PR-L2 estratégia | sort carga↓ × dist↓ | `spider-L2-sort` | três alvos a distâncias distintas |
| SP-R3-B | lacuna da prova | `unspecified` se estação já no alvo ou mistura | `spider-L2-gap` | casos (2)(3) de SP-R3 |
| SP-R4-A | def. Pereira + Das | KEEP, sem apagar interseção | `spider-sit-keep` | §8.2–8.6 |
| SP-R4-C | silêncio das provas | `unspecified` se `S∩T≠∅` | `spider-sit-unspecified` | qualquer interseção |
| SP-R4-B | CE1' | cancelar interseção | **proibido** | — |
| SP-R5-A | `0<r'` | `unspecified` se `r'=0` | `spider-r0-unspecified` | `r=1`, folha origem |
| SP-R5-B | extensão da carga | `r'=0` não sai sem recarga | `spider-r0-zero` | o mesmo caso |
| SP-C2-3 | PR-T1 C2 | sem estações nas radiais ⇒ C2 falsa | default com L1A | SP-R2 |
| CTR-01 | spec R11a.3 | `obj=\|C\|` se `ok`; 3 estados | todas | `verify_r11` |
| CTR-02 | spec | sem baseline/Gurobi/enum/F-CC na construção | todas | inspeção estática futura |

Variantes oficiais propostas para o *primeiro* lote (produto controlado, não combinatória total):

1. `path-alg1`
2. `cycle-alg2` (chama `path-alg1`)
3. `spider-A` = L1A + INT-A + R1A + R2A + L2-sort + sit-keep + r0-zero + C2-3  
4. `spider-B` = L1B + INT-A + R1A + R2A + L2-sort + sit-keep + r0-zero + C2-3  
5. `spider-U` = igual a `spider-A` mas sit-unspecified e r0-unspecified (silêncios)

`spider-L2-gap` pode ser uma sexta variante se o lote ainda for pequeno; senão fica no `verify_r11` local e fora do CSV oficial até segundo pré-registro.

---

## 11. Casos de teste de `verify_r11.py`

O script foi escrito em 2026-10-07 seguindo esta matriz, mas **ainda não foi executado** nesta preparação. Cada linha continua sendo a régua para distinguir desacordo esperado de bug de implementação.

### 11.1 Caminhos

| ID | Construção | Assertar |
|---|---|---|
| VP-OPT0 | `n=3`, `S={v1}`, `T={v3}`, `r=2` | PATH-DEF OPT=0 via `viavel(∅)`; `path-alg1` devolve o `C` literal (VAL-A2: `{v2}`). Se `C≠∅`, o teste **não** falha por isso: classifica divergência local esperada *ou* compara só contrato `obj=\|C\|` e `viavel(C)`. Spec: falhar alto em desacordo *inesperado*. Este caso é **esperado** como possível `suboptimal`. Marcar `expected_divergence=PATH-05` |
| VP-OPT0-true | `n=3`, `S={v1}`, `T={v2}`, `r=2` | `C=∅`, `viavel`, OPT 0 |
| VP-ONE | `n=4`, `S={v1}`, `T={v4}`, `r=2` | uma estação no literal A1; `viavel(C)`; confrontar OPT enum |
| VP-MULTI | caminho longo, `m=1`, `r=2` | várias estações A1 |
| VP-STAY | `S=T={v2}` em `n=5` | `C=∅` |
| VP-SIT | `S={v2,v4}`, `T={v2,v5}` | dois `if` em `v2` |
| VP-SIT-NPERM | §8.6 | matching ordenado vs outro |
| VP-DIAM | `r ≥ n−1`, `m≥1` | OPT 0 no validador; A1 literal |
| VP-MIN | `n=1` se gerado; senão `n=2` | contrato / `invalid` se a spec de caminho trivial ficar de fora |
| VP-OBJ | todo `ok` | `obj==len(C)` |

### 11.2 Ciclos

| ID | Construção | Assertar |
|---|---|---|
| VC-OPT0 | `n=4`, `r=2`, um par a distância 2 | OPT 0 possível; A2 literal |
| VC-ONE | `n=5`, um par antípoda, `r=1` | pelo menos uma quebra com estação |
| VC-BREAKS | instância em que duas quebras dão `|X|` diferentes | min = menor; `notes` com o `i` vencedor |
| VC-SYM | ciclo simétrico, rotação de `S,T` | `|C|` invariante; `C` pode rotacionar |
| VC-SIT | um `v` em `S∩T` e um par móvel | KEEP |
| VC-STAY | Fig. 3: `S=T`, nenhum movimento necessário | `C=∅` |
| VC-LEMMA5 | caso da prova com permanência forçada para libertar aresta | A2 vs OPT |

### 11.3 Aranhas

| ID | Construção | Assertar |
|---|---|---|
| VS-MIN3 | 3 radiais de 1 vértice, `m=0` inválido; `m=1` folha→folha | classe aranha; contrato |
| VS-RAD1 | radial de um vértice ≠ radial vazia | não tratar como `G−c` vazio |
| VS-LEN | radiais 1, 2, 5 | passe independente |
| VS-SAME | `s,t` na mesma radial | eixos INT |
| VS-CROSS | `s` e `t` em radiais distintas | matching centro |
| VS-MIX | um par interno e um cruzado | SP-R3 |
| VS-CS | `c ∈ S`, alvo numa folha | `r'=r` no centro |
| VS-CT | origem numa folha, `c ∈ T` | `d=0` para um alvo |
| VS-CST | `c ∈ S ∩ T` | KEEP vs UNSPEC |
| VS-SPR1 | SP-R1 | `C` na radial de entrada |
| VS-SPR2 | construção §7.1, `r=2` | `spider-A`: `C={c}` ou equivalente literal; `viavel` provavelmente falso; OPT enum = 2 |
| VS-SPR3 | SP-R3 casos | sort vs unspecified |
| VS-SPR4 | os seis da §8 | |
| VS-SPR5 | §7.1 com `r=1` | r0-unspecified vs r0-zero |
| VS-VAR | todas as variantes oficiais no mesmo input | `variant` distinto; nenhuma conserta a outra |

Todo `ok`: `viavel` no validador **nas instâncias locais** (n pequeno). `unspecified` esperado: assert explícito, não falha.

---

## 12. O que este documento não fecha

- Execução de `verify_r11.py` e das regressões estruturais.
- Materialização dos arquivos oficiais e seus SHA-256.
- Execução do lote, CSV, relatório e conclusão experimental.
- Se PATH-ALG1 “está errado”: VAL-A2 já mostra desacordo de *contagem* com a definição. R11 mede isso no protocolo; correção pública não é desta spec.
- F-C3 permanece `OPEN`.

A implementação preparatória agora está em `path_cycle.py`, `spider.py`,
`r11_catalog.py`, `prepare_r11.py`, `verify_r11.py` e `run_r11.py`. A existência
desses arquivos não constitui evidência experimental.

---

## 13. Rastreio da spec

| Requirement | Este arquivo |
|---|---|
| CERT-01…03 | §2–11 — leituras fechadas |
| CERT-10 (contrato) | §9 — contrato implementado; execução pendente |
| CERT-11 (leituras) | §7 e matriz — `unspecified` explicitado |
| CERT-14 (construções SP-R*) | §7 + `r11_catalog.py`; materialização pendente |
| CERT-21 (cobertura) | §8, §11; materialização no pré-registro |
