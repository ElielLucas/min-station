# Validação da formulação BASE atual (MIN-STATION, estações em todo V)

## Contexto

**Pedido:** validar matematicamente, sem executar código, a formulação base atual (`docs/technical/reference/formulacao-base-all-vertices.pdf`, espelhada em `docs/context-ai/base-formulation.md`) contra a definição do MIN-STATION de Das (`docs/technical/reference/min-station-das.pdf`). A validação cobre as duas direções da equivalência, procura contraexemplos e separa corretude, força e desempenho. A formulação generalizada da SBPO está fora do escopo.

**Método:** leitura integral dos três PDFs e dos documentos de contexto, provas por decomposição de fluxo e casos pequenos verificados à mão, restrição por restrição. Nenhum código foi executado. A verificação computacional exaustiva fica como próximo passo recomendado (ver o fim do documento).

**Resultado em uma frase:** sob distância em passos, a formulação é **exata**: para todo `C ⊆ V`, `C` é viável no MIN-STATION ⇔ existe `f` com `(f, χ_C)` viável na PLI. A versão com balanços separados (uma equação de origem, outra de destino) era inviável quando `S ∩ T ≠ ∅`, caso que Das permite (falso negativo) — **corrigido na rodada E5** com a adoção do balanço unificado (variante U, §8–9 abaixo), agora a formulação corrente em `baseline.py`. A correção foi local: só as equações de balanço mudaram.

**Escopo da validação.** As provas abaixo supõem grafo não dirigido e distância em passos, como em Das. Das instâncias usadas nos experimentos, só hc9u, hc10p–hc12p e bip42p satisfazem isso (as quatro últimas via `A_r = E`); cc10-2p/cc12-2p são extensão ponderada e as TNTP são extensão ponderada e dirigida (ver `open-questions.md` Q2 e Q7). A formulação continua bem definida sobre qualquer dígrafo de alcance, mas a equivalência com o problema de Das só vale no primeiro grupo.

---

## 1. Definição do MIN-STATION segundo Das

Elementos usados na validação, com citações de `min-station-das.pdf`:

| Elemento | O que Das diz | Onde |
|---|---|---|
| Grafo | "we assume that G is a simple connected undirected graph" | p. 2 |
| Entrada | `S ⊂ V` (posições iniciais de m robôs), `T ⊂ V` (alvos), `\|S\| = \|T\| = m`, `r` inteiro positivo | Problem 1, p. 2 |
| Passo | "A robot takes one step by moving from one vertex to an adjacent vertex in G" (custo unitário por aresta) | p. 2 |
| Autonomia | "it can move r steps without recharging when starting from its starting position or a charging station" | p. 2 |
| Saída | "A minimum cardinality subset C of V" (nenhuma restrição sobre onde ficam as estações) | Problem 1, p. 2 |
| Conclusão | "each target position needs to be occupied by exactly one robot"; o movimento termina quando cada alvo está ocupado | p. 2–3 |
| Não rotulados | "there is no fixed matching between the starting positions and the target positions" | p. 3 |
| Compartilhamento | "multiple robots may arrive at one vertex simultaneously, allowing them to recharge concurrently at a single charging station" | p. 3 |
| Rotas não fixas | "A robot may need to travel beyond its shortest paths" | p. 3 |
| Terminal | "A vertex v ∈ G is called a terminal if v ∈ S ∪ T" (só nomenclatura, sem papel semântico) | p. 3 |

**Pontos que exigiram interpretação:**

- **`S ∩ T` é permitido.** A definição não exige disjunção. A prova do Lema 5 considera explicitamente origens que são alvos: "every robot is starting from a target position" (Fig. 3, p. 11–12) e "The robot starting at s_i remains at s_i occupying the target t_o" (p. 12). O Algoritmo 1 testa `v_i ∈ S` e `v_i ∈ T` com dois `if` independentes na mesma iteração (p. 10).
- **Origens de outros robôs não recarregam.** A necessidade no Lema 2 só vale se `s2..sk` dentro do intervalo não recarregam.
- **Voltar à própria origem sem estação** é irrelevante. Qualquer rota `s → … → s → … → t` pode ser trocada pelo sufixo que parte de `s`, onde a bateria já está cheia.
- **Robô parado:** se `s ∈ S ∩ T`, o robô pode ficar em `s` e ocupar o alvo (Lema 5, p. 12).
- **Inconsistência interna na fonte** (não afeta a formulação). O Lema 2 e o Algoritmo 1 têm contagem divergente da definição: caminho a–b–c, S={a}, T={c}, r=1: o Algoritmo 1 devolve {a,b}, mas a definição exige apenas {b}. Esta validação usa a **definição** (Problem 1 + texto da p. 2).

**Caracterização usada.** Seja `C ⊆ V`. `C` é viável ⇔ existe uma bijeção `π: S → T` tal que cada robô tem uma caminhada de `s` a `π(s)` em que:
- cada passo atravessa uma aresta;
- entre dois pontos de carga consecutivos há no máximo `r` passos;
- os pontos de carga são `s` (só no início) e vértices de `C`.

Não há tempo, colisão nem capacidade de estação. Portanto os robôs só interagem pela bijeção.

---

## 2. Formulação atual (reescrita)

**Conjuntos e parâmetros.**
- `G = (V, E)`; `S, T ⊆ V`; `m = |S| = |T|`; `r ∈ Z_{>0}`.
- `d(u, v)`: distância de caminho mínimo em G. Para Das, deve ser o **número de arestas**.

**Dígrafo de alcance.** `A_r = {(u, v) ∈ V × V : u ≠ v, d(u, v) ≤ r}`.

**Notação.** `in(v) = Σ_{(u,v)∈A_r} f_uv` e `out(v) = Σ_{(v,w)∈A_r} f_vw`.

**Variáveis.** `y_v ∈ {0,1}` para todo `v ∈ V`; `f_uv ∈ Z_{≥0}` para todo `(u,v) ∈ A_r`.

```
(1) min  Σ_{v∈V} y_v
(2) out(s) − in(s) = 1              ∀ s ∈ S
(3) in(t) − out(t) = 1              ∀ t ∈ T
(4) in(v) = out(v)                  ∀ v ∈ V ∖ (S ∪ T)
(5) in(v)  ≤ m·y_v                  ∀ v ∈ V ∖ T
(6) in(t)  ≤ 1 + (m−1)·y_t          ∀ t ∈ T
(7) out(v) ≤ m·y_v                  ∀ v ∈ V ∖ S
(8) out(s) ≤ 1 + (m−1)·y_s          ∀ s ∈ S
```

Com indicadores `a_v = [v∈S]` e `b_v = [v∈T]`, o domínio de cada ativação se lê assim:
- entrada: `in(v) ≤ b_v + (m − b_v)·y_v`, que reúne (5) e (6);
- saída: `out(v) ≤ a_v + (m − a_v)·y_v`, que reúne (7) e (8).

Essas duas formas valem para **todo** `v`, inclusive `v ∈ S ∩ T`, que cai em (6) e (8).

---

## 3. Correspondência MIN-STATION ↔ PLI

| MIN-STATION (Das) | PLI |
|---|---|
| estação em `v` | `y_v = 1` |
| conjunto solução `C` | `{v : y_v = 1}` |
| trecho entre dois pontos de carga (≤ r passos) | arco `(u,v) ∈ A_r` |
| passagem física por um vértice sem recarregar | vértice interno ao caminho mínimo que realiza um arco; **não aparece** na PLI |
| recarga em `v` | `v` é ponto de junção entre dois arcos de uma mesma rota (entra e sai fluxo) |
| rota de um robô | caminho dirigido em `(V, A_r)` de `s` a `π(s)` com interior em `C` |
| m robôs não rotulados | fluxo inteiro agregado de valor m; identidade não representada |
| robô inicial com bateria cheia | oferta líquida 1 em (2) e saída livre de 1 unidade em (8) |
| alvo ocupado por exatamente um robô | demanda líquida 1 em (3) e entrada livre de 1 unidade em (6) |
| pareamento `π` | implícito, recuperado pela decomposição do fluxo |
| compartilhamento de estação | Big-M permite até m unidades por vértice |
| robô parado (`s = π(s)`, `s ∈ S∩T`) | **não representável** na formulação atual (modelo fica inviável); na correção (§8), caminho vazio |
| objetivo `\|C\|` | `Σ y_v` |

---

## 4. Validação restrição por restrição

Salvo menção em contrário, assume-se `S ∩ T = ∅`.

**(1) Objetivo.** Correto: conta todas as estações, inclusive em terminais. Um `y_v = 1` sem fluxo é permitido, mas nunca aparece num ótimo.

**(2) Balanço nas origens.**
- Representa a oferta de um robô.
- Válida: na solução induzida por rotas (§5.2), nenhuma rota termina em `s ∉ T`, e rotas que passam por `s` têm líquido 0.
- Com `y_s = 0`: (5) dá `in(s) = 0` e então `out(s) = 1`. Origem sem estação só emite o próprio robô.
- Com `y_s = 1`: `out(s) = in(s) + 1`. Robôs chegam, recarregam e saem, além do robô original.
- Caso limite: `s ∈ T` torna o sistema inconsistente (§6, CE1).

**(3) Balanço nos destinos.** Simétrico a (2).
- `y_t = 0` ⇒ (7) dá `out(t) = 0`, logo `in(t) = 1`.
- `y_t = 1` ⇒ `in(t) = out(t) + 1`: exatamente um robô termina em `t`, os demais passam.

**(4) Conservação.** Válida e suficiente para vértices não terminais.

**(5) Entrada em não destinos.**
- `v ∉ S∪T`, `y_v = 0` ⇒ `in(v) = 0`, e por (4) `out(v) = 0`.
- Origem com `y_s = 0` ⇒ `in(s) = 0`.
- Big-M `m` válido: `m` caminhos simples entram em `v` no máximo `m` vezes.

**(6) Entrada em destinos.**
- `y_t = 0` ⇒ `in(t) ≤ 1`: só o robô que termina ali.
- `y_t = 1` ⇒ `in(t) ≤ m`, válido porque o robô que termina em `t` não passa por `t` antes.
- Com `m = 1`, a cota é sempre `in(t) ≤ 1`, o que é correto: com um robô, estação no destino é inútil.

**(7) Saída de não origens.**
- `y_t = 0` ⇒ `out(t) = 0`.
- `v ∉ S∪T` e `y_v = 0` ⇒ `out(v) = 0`.

**(8) Saída de origens.**
- `y_s = 0` ⇒ `out(s) ≤ 1`, que com (2) dá `in(s) = 0`, `out(s) = 1`.
- `y_s = 1` ⇒ `out(s) ≤ m`.

**Fluxo em vértice sem estação?**

Não, desde que `S ∩ T = ∅`. De (5)–(8) sai o **Lema L0**: `y_v = 0 ⇒ in(v) ≤ b_v e out(v) ≤ a_v`. Num vértice sem estação, o fluxo nunca **entra e sai**:
- origem pura: só sai;
- destino puro: só entra;
- intermediário: nada entra nem sai.

O único "uso sem estação" é a passagem física por dentro de um arco de `A_r`, e Das a permite.

**Redundâncias** (não afetam a corretude; ver §7, P5):
- Em `s ∈ S`: (2) + (8) dão `in(s) ≤ (m−1)·y_s`, o que domina (5). Logo (5) é redundante nas origens.
- Em `t ∈ T`: (3) + (6) dão `out(t) ≤ (m−1)·y_t`, o que domina (7). Logo (7) é redundante nos destinos.
- Em `v ∉ S∪T`: com (4), (5) ⇔ (7).

A ativação efetiva é uma restrição por vértice:
- `in(s) ≤ (m−1)·y_s` nas origens;
- `out(t) ≤ (m−1)·y_t` nos destinos;
- `in(v) ≤ m·y_v` nos intermediários.

---

## 5. Prova de equivalência

**Hipóteses.**
- (H1) `S ∩ T = ∅`.
- (H2) `d` é a distância em número de arestas.
- (H3) G conexo. Só é usada para garantir existência de solução, não para a equivalência.

### 5.0 Lema de trechos (A_r ⇔ caminhadas)

Seja `W = (w_0 = s, …, w_L = t)` uma caminhada válida para `C`. Os índices de carga `0 = i_0 < i_1 < … < i_k = L` (com `w_{i_j} ∈ C` para `0 < j < k`) satisfazem `i_{j+1} − i_j ≤ r`. Logo `d(w_{i_j}, w_{i_{j+1}}) ≤ r`.

Os pontos de carga formam uma sequência em `(V, A_r)`. Para obter um **caminho simples** de `s` a `t` com interior em `C`:
1. descartar pontos consecutivos iguais;
2. atalhar repetições: se `x_p = x_q` com `p < q`, remover `x_{p+1..q}`.

Reciprocamente, a partir de um caminho em `A_r` com interior em `C`:
1. concatenar caminhos mínimos de G para cada arco, cada um com ≤ r passos;
2. recarregar em cada ponto interior.

O que a equivalência "caminhada de ≤ r passos de u a v ⇔ d(u,v) ≤ r" usa:
- (i) custo unitário por passo;
- (ii) recarga somente em vértices e restaurando a bateria inteira;
- (iii) nenhuma restrição sobre vértices atravessados.

### 5.1 PLI → MIN-STATION (não há falso positivo)

Seja `(f, y)` inteira viável e `C = {v : y_v = 1}`.

1. `f` é um fluxo inteiro com excesso `+1` em cada `s`, `−1` em cada `t` e `0` nos demais vértices.
2. Pelo teorema de decomposição de fluxo (conformal; Ahuja–Magnanti–Orlin, Thm. 3.5), `f` é soma de caminhos simples e ciclos simples, cada um com fluxo unitário. Cada caminho vai de um vértice com excesso positivo a um com excesso negativo.
3. Contagem: cada `s` inicia exatamente 1 caminho e cada `t` termina exatamente 1. Isso dá `m` caminhos e uma bijeção `π: S → T` (pareamento implícito).
4. Seja `v` interior a um caminho, ou pertencente a um ciclo. Então `in(v) ≥ 1` e `out(v) ≥ 1`:
   - se `v ∉ T`, (5) força `y_v = 1`;
   - se `v ∈ T` (logo `v ∉ S`), (7) força `y_v = 1`.
5. Cada caminho, pelo Lema 5.0, é uma rota válida. Logo `C` é viável e `|C| = Σ y_v`.

**Ciclos:** só passam por estações e não representam robôs. Removê-los mantém (2)–(4) e só diminui os lados esquerdos de (5)–(8). São redundantes: nunca tornam viável algo inválido, porque a parte "caminhos" já é viável sozinha.

**Troca de identidade:** a decomposição pode parear diferentemente em estações onde fluxos se juntam. Qualquer escolha é válida, porque a validade de uma rota só depende de seus pontos interiores serem estações, e os robôs são indistinguíveis. Em vértices sem estação não há junção (Lema L0), logo não há troca ilegítima.

### 5.2 MIN-STATION → PLI (não há falso negativo, sob H1)

Seja `C` viável, com bijeção `π` e rotas.

1. Pelo Lema 5.0, cada robô tem um caminho simples `P_s` em `A_r` de `s` a `π(s)` com interior em `C`. Sob H1, `s ≠ π(s)`.
2. Faça `f = Σ_s χ(P_s)` e `y = χ_C`.
3. **Balanço:** cada caminho soma +1 em `out` na origem, +1 em `in` no fim e 0 no interior. Isso dá (2)–(4).
4. **(5):** para `v ∉ T`, `in(v) = #{caminhos com v interior}`. Vale 0 se `v ∉ C` e é ≤ m, porque caminhos simples passam no máximo uma vez.
5. **(6):** `in(t) = 1 + #{caminhos com t interior}`. Vale 1 se `t ∉ C` e é ≤ 1 + (m−1), porque o caminho que termina em `t` não o tem como interior.
6. **(7) e (8):** análogos. Em (8), `out(s) = 1 + #{caminhos com s interior} ≤ 1 + (m−1)`.

Logo `(f, χ_C)` é viável e `OPT_PLI ≤ OPT_MS`.

**Big-M.** `m` é um limitante válido em (5)–(8). Nenhuma solução válida exige mais que `m` unidades num vértice, porque sempre existe representação por `m` caminhos simples. Valores acima de `m` só aparecem com ciclos, que são dispensáveis.

### 5.3 Teorema

Sob H1–H2, para todo `C ⊆ V`: `C` é viável no MIN-STATION ⇔ existe `f` com `(f, χ_C)` viável em (2)–(8). Consequentemente, `OPT_PLI = OPT_MS`, e toda solução ótima da PLI fornece um conjunto ótimo de estações.

### 5.4 Onde a prova falha: `S ∩ T ≠ ∅`

Se `v ∈ S ∩ T`, somando (2) e (3) em `v` obtém-se `0 = 2`: a PLI é inviável. O MIN-STATION, por outro lado, é sempre viável: com `C = V`, cada aresta é um salto válido, porque G é conexo e `r ≥ 1`. É a única falha de corretude encontrada.

---

## 6. Casos limite e contraexemplos

Todos verificados à mão.

**CE1 — falso negativo por `S ∩ T` (contraexemplo real).**
- Instância: caminho `a–b–c`, `S = {a, b}`, `T = {b, c}`, `r = 1`. `A_1 = {ab, ba, bc, cb}`.
- MIN-STATION: `π(a) = b`, `π(b) = c`. Cada robô anda 1 passo, então `C = ∅` e `OPT = 0`.
- PLI atual: em `b`, (2) dá `out − in = 1` e (3) dá `in − out = 1`. É **inviável**.
- PLI corrigida (§8): `f_ab = f_bc = 1`, `y = 0`. Em `b`: `in = out = 1 ≤ 1 + (m−1)·0`. Viável com valor 0 ✓.

**CE1' — pré-processamento "robô em S∩T fica parado" é inválido.** Na mesma instância, remover `b` de `S` e de `T` deixa `S = {a}`, `T = {c}` e exige estação em `b`. O ótimo passa a ser 1 ≠ 0.

**CE0 — caso trivial.** `V = {v}`, `S = T = {v}`. MIN-STATION: `OPT = 0`. PLI: `A_r = ∅` e (2) vira `0 = 1`, inviável.

**C1 — dois robôs no mesmo arco; f_uv > 1 necessário.**
- Instância: caminho `a–b–c–d`, `S = {a, b}`, `T = {c, d}`, `r = 1`. Ótimo 2, com `C = {b, c}`.
- Rotas: `a→b→c` (recarga em b) e `b→c→d` (recarga em c).
- PLI: `f_ab = 1`, `f_bc = 2`, `f_cd = 1`. Confere:
  - (2) em a: 1 − 0 = 1; em b: 2 − 1 = 1;
  - (3) em c: 2 − 1 = 1; em d: 1 − 0 = 1;
  - (6) em c: 2 ≤ 1 + 1·1; (8) em b: 2 ≤ 1 + 1·1.
- Mostra que `f_uv > 1` é necessário. Uma cota `f_uv ≤ y_v` seria inválida.

**C2 — estrela `K_{1,3}`, centro `t1 ∈ T`, folhas `s1, s2 ∈ S` e `t2 ∈ T`.**
- `r = 1`: o robô que vai para `t2` precisa recarregar em `t1`. Ótimo 1 com estação num destino. A PLI dá o mesmo: `y_{t1} = 1` e `in(t1) = 2 ≤ 1 + 1·1`.
- `r = 2`: o arco `(s2, t2)` ∈ A_2 atravessa `t1` fisicamente sem estação. Ótimo 0. A passagem física por um destino não exige estação ✓.

**C3 — ciclo C4 1-2-3-4-1, `S = {1, 3}`, `T = {2, 4}`, `r = 1`.**
- Ótimo 0 (`1→2`, `3→4`).
- Existe solução inteira viável com circulação: `y_2 = y_3 = 1`, com ciclo `f_23 = f_32 = 1`. O ciclo só existe pagando estações. Removê-lo mantém a viabilidade — é redundante, nunca um falso positivo.

**C4 — `m = 1`.** (6) e (8) viram `in(t) ≤ 1` e `out(s) ≤ 1` para qualquer `y`. Correto: um único robô nunca reentra na origem nem sai do destino num caminho simples.

**C5 — gadget do Lema 1 de Das (r = 1).**
- Fórmula `(x1)`: C4 `v1–v2–v3–v4–v1`, com `vc1` e `vc2` ligados a `v1`; `S = {vc1, v2}`, `T = {vc2, v4}`.
  - Das: `OPT = 1`, com estação em `v1`.
  - PLI: o único arco que sai de `vc1` é `(vc1, v1)`. Logo `in(v1) ≥ 1`, (5) força `y_{v1} = 1`. `OPT = 1` ✓.
- Fórmula `(x1) ∧ (¬x1)`: força `y_{v1} = y_{v3} = 1`, dando `OPT = 2`. Coerente com "insatisfatível".

---

## 7. Problemas encontrados

| # | Problema | Classificação | Afeta corretude? |
|---|---|---|---|
| P1 | `S ∩ T ≠ ∅` ⇒ (2)+(3) inconsistentes ⇒ PLI inviável, embora Das permita o caso e ele seja sempre viável (CE0, CE1) — **RESOLVIDO na rodada E5**: opção (B) abaixo adotada em `baseline.py` | Era erro de modelagem em relação a Das; corrigido | Não mais (era falso negativo) |
| P2 | O PDF define `d` como "distância do caminho mais curto em G" sem fixar pesos unitários; Das exige passos | Ambiguidade | Só se `d` for ponderada |
| P3 | Implementação: Dijkstra com pesos (`ms_utils.py`) e adjacência só `u→v`. Instâncias TNTP têm pesos ≠ 1 | Extensão ponderada/direcionada, não erro da formulação | Não para a PLI; sim para "comparar com Das" |
| P4 | `preprocessamento/modelo_min_station_das_preprocess.py` já implementava o balanço unificado antes de `base-formulation.md` §10.1 adotá-lo — **RESOLVIDO na rodada E5** (documentação atualizada). Nota de higiene: `modelo_min_station_fluxo_2.py`, citado nesta seção como rejeitando `S ∩ T`, não existe mais no repositório; `experiments/alternative-formulations/modelo_min_station_fluxo.py` também tem balanços separados, sem essa guarda | Divergência código × documentação (já corrigida) | Não |
| P5 | Redundâncias: (5) em S, (7) em T e uma de (5)/(7) em `V∖(S∪T)` | Apenas eficiência/documental | Não |
| P6 | Texto do PDF: resumo ainda fala em "vértices intermediários"; referências "(??)–(??)"; "`\|S\|` limitante seguro para o total de fluxo" (é limite por vértice; `Σ f` pode exceder m); "o fluxo só atravessa vértices com estação" (confunde passagem física com junção de saltos); "em cada destino entra uma unidade" (é líquida) | Problema textual/documental | Não |
| P7 | Big-M `m` torna a relaxação fraca: um robô que precisa de k estações contribui ≈ k/m ao limite linear | Apenas relaxação | Não |
| P8 | Lema 2 e Algoritmo 1 de Das com contagem ⌊dist/r⌋ divergente da definição | Ambiguidade na fonte | Não (não usar como oráculo) |

---

## 8. Correções mínimas necessárias

Só **P1** era problema de corretude. Existiam duas opções legítimas; o projeto escolheu (B) na rodada E5:

**(A) Restringir o escopo:** declarar a hipótese `S ∩ T = ∅`. As equações não mudam, mas o modelo deixa de cobrir todo o MIN-STATION de Das. Atenção: instâncias com `S ∩ T ≠ ∅` **não** podem ser reduzidas fixando os robôs comuns (CE1').

**(B) Corrigir apenas o balanço.** Correção mais local possível: as ativações (5)–(8) permanecem idênticas, porque para `v ∈ S∩T` já se aplicam (6) e (8).

ANTES
```
(2) out(s) − in(s) = 1     ∀ s ∈ S
(3) in(t) − out(t) = 1     ∀ t ∈ T
(4) in(v) = out(v)         ∀ v ∈ V ∖ (S ∪ T)
```
DEPOIS
```
(2') out(s) − in(s) = 1    ∀ s ∈ S ∖ T
(3') in(t) − out(t) = 1    ∀ t ∈ T ∖ S
(4') in(v) = out(v)        ∀ v ∈ (V ∖ (S ∪ T)) ∪ (S ∩ T)
```
Forma compacta equivalente: `out(v) − in(v) = a_v − b_v` para todo `v ∈ V`. Com (5)–(8), isso coincide exatamente com a variante (U) de `base-formulation.md` §10.1 e com o que o código de pré-processamento já faz.

**Por que (B) é correta.**
- Para `v ∈ S∩T` com `y_v = 0`: (6), (8) e (4') dão `in(v) = out(v) ∈ {0, 1}`. O valor 0 é o robô parado; o valor 1 é "o robô de v parte e outro chega", válido sem estação. O Lema L0 continua valendo.
- A decomposição de PLI→MS para (B) usa uma rede auxiliar com super-fonte σ e super-sumidouro τ: cada `v ∈ S∩T` com `y_v = 0` é dividido em `v⁻` e `v⁺` com arco de permanência `v⁺→v⁻`. O caminho `σ→v⁺→v⁻→τ` representa o robô parado.
- MS→PLI: robôs com `π(s) = s` não geram fluxo. Em `v ∈ S∩T`, `out(v) = 1 ⇔ π(v) ≠ v ⇔ π⁻¹(v) ≠ v ⇔ in(v) = 1`, logo (4') vale.
- Quando `S ∩ T = ∅`, (B) é idêntica à formulação atual. A mudança é conservadora.

Nenhuma outra alteração é necessária para a corretude.

---

## 9. Formulação corrigida (se a opção B for adotada)

```
(1)  min  Σ_{v∈V} y_v
(2') out(s) − in(s) = 1              ∀ s ∈ S ∖ T
(3') in(t) − out(t) = 1              ∀ t ∈ T ∖ S
(4') in(v) = out(v)                  ∀ v ∈ (V ∖ (S ∪ T)) ∪ (S ∩ T)
(5)  in(v)  ≤ m·y_v                  ∀ v ∈ V ∖ T
(6)  in(t)  ≤ 1 + (m−1)·y_t          ∀ t ∈ T
(7)  out(v) ≤ m·y_v                  ∀ v ∈ V ∖ S
(8)  out(s) ≤ 1 + (m−1)·y_s          ∀ s ∈ S
     y ∈ {0,1}^V,  f ∈ Z_{≥0}^{A_r},  A_r = {(u,v): u≠v, d(u,v) ≤ r},  d = distância em arestas
```

É válida para o MIN-STATION de Das sem hipótese sobre `S ∩ T`. Se o projeto preferir a opção A, a formulação atual já é válida sob `S ∩ T = ∅` e `d` em passos.

---

## 10. Questões de fortalecimento (apenas registro)

- **Big-M efetivo por vértice:** já está implícito `in(s) ≤ (m−1)·y_s` e `out(t) ≤ (m−1)·y_t`. Candidatos adicionais: cotas locais por alcance (número de origens que alcançam `v` ou de alvos alcançáveis a partir de `v`); para `v ∈ S∩T`, `in(v) ≤ 1 + (m−2)·y_v`.
- **Relaxação:** formulação multi-commodity por origem (`x^s_uv ≤ y_v`) ou por destino; cortes do tipo "toda origem sem alvo em um salto precisa de estação em `N_r^+(s)`": `Σ_{v∈N_r^+(s)} y_v ≥ 1`. Generalizações por cortes de conjuntos `W` com `|S∩W| > |T∩W|`.
- **Eliminação de arcos/vértices:** vértices não alcançáveis a partir de S ou que não alcançam T (com prova); arcos dominados. Não é válido eliminar arcos que entram em origens ou saem de destinos (ver C1).
- **Redundâncias** (P5): remoção explícita das ativações implicadas.
- **Formulações alternativas:** rede com divisão de vértice (`y_v` ativa `v_in→v_out`), caminhos/colunas, Benders e Lagrangeano. O repositório já tem protótipos, a comparar com o baseline em condições idênticas.

---

## Apêndice A — Resultados da verificação adversarial (6 agentes independentes)

Este apêndice registra os achados dos agentes refutadores que leram o código e os PDFs de forma independente. Nenhum código foi executado. Os agentes tentaram refutar as conclusões do relatório; os que não conseguiram confirmam por ausência de contraexemplo.

### A.1 Veredito geral dos três agentes refutadores

Todos os três agentes devolveram `holds_with_caveats`. Nenhuma prova central foi derrubada. As ressalvas mais importantes são listadas abaixo.

### A.2 Armadilha de oráculo: Lema 2 e Algoritmo 1 de Das

Os agentes identificaram, à mão, que o Lema 2 e o Algoritmo 1 de Das **superconstam estações em caminhos** quando `r` divide a distância `L`. A contagem correta é `⌈L/r⌉ − 1`; Das usa `⌊L/r⌋`, que dá um a mais quando `r | L`. Exemplos verificados:

- Caminho `v1–v2–v3`, `S = {v1}`, `T = {v3}`, `r = 2`: `OPT_MS = 0`; Algoritmo 1 devolve `{v2}`.
- Caminho `a–b–c–d`, `S = {p1,p2}`, `T = {p3,p4}`, `r = 1`: `OPT_MS = 2`; Algoritmo 1 devolve 3 estações.

**Consequência:** qualquer validação que use o Algoritmo 1 ou o Lema 2 como gabarito verá a PLI com valor menor e pode concluir erroneamente que há falso positivo. Os algoritmos de Das **não servem como oráculo** sem correção.

O repositório não usa o Algoritmo 1 atualmente; isso é apenas um alerta para testes futuros.

### A.3 Falso positivo condicional (extensão ponderada)

Um agente identificou o seguinte cenário: caminho `a–b–c` com pesos `w(ab) = w(bc) = 0.5`, `S = {a}`, `T = {c}`, `r = 1`. Com Dijkstra ponderado, `d_w(a,c) = 1.0 ≤ 1`, portanto o arco `(a,c) ∈ A_r`. A PLI dá `OPT = 0`; o MIN-STATION de Das (em passos) exige estação em `b`.

Este **não** é defeito da formulação matemática — é consequência de usar `d` ponderada em vez de passos. Com pesos `≥ 1`, `A^w ⊆ A^passos`, portanto não há falso positivo em relação a Das, mas pode haver falso negativo. O resultado deve ser interpretado como **extensão ponderada (Q2)**, não como MIN-STATION de Das.

### A.4 Falso negativo de implementação: adjacência assimétrica

O código `construir_adjacencia` (`ms_utils.py:96-102`) só insere `u→v` para cada linha de aresta, sem o arco reverso. Instâncias que não listam as duas direções da aresta geram `A_r` direcionada, o que produz falso negativo quando a rota de Das exige o sentido reverso.

Nas instâncias amostradas pelos agentes, as arestas aparecem nos dois sentidos. Porém instâncias TNTP (redes de transporte) podem ter vias de mão única. Se isso ocorrer, o modelo resolve uma variante **direcionada**, não o MIN-STATION de Das.

### A.5 Forma forte do Lema L0

Os agentes apontaram que o Lema L0 do relatório principal (`y_v = 0 ⇒ in(v) ≤ b_v` e `out(v) ≤ a_v`) pode ser enunciado de forma mais forte: quando `S ∩ T = ∅`, as cotas são atingidas com igualdade:

| Caso | `in(v)` | `out(v)` |
|---|---|---|
| `v ∈ S ∖ T`, `y_v = 0` | 0 | 1 |
| `v ∈ T ∖ S`, `y_v = 0` | 1 | 0 |
| `v ∉ S ∪ T`, `y_v = 0` | 0 | 0 |

Com essa forma forte, a rede auxiliar dividida (`v⁻`, `v⁺`) não é necessária na prova PLI→MS sob `S ∩ T = ∅`. Ela só é indispensável para a variante (U) com `v ∈ S ∩ T` e `y_v = 0`.

### A.6 Bug provável no Benders: remoção inválida de S ∩ T

O agente de auditoria identificou que `benders_min_station.py:610-621` aplica `remover_origem_destino_iguais`, o pré-processamento inválido descrito em CE1' (§6). O subproblema de fluxo interno (`montar_rede_fluxo`, linhas 404–464) já implementa a variante (U) e trataria `S ∩ T` corretamente sem a remoção. A correção sugerida é não chamar `remover_origem_destino_iguais` — mas isso não afeta as instâncias atuais, cujos geradores produzem `S ∩ T = ∅`.

### A.7 Divergência código × documentação (confirmada)

Os agentes confirmaram, restrição a restrição:

| Arquivo | Modelo implementado |
|---|---|
| `experiments/alternative-formulations/modelo_min_station_fluxo.py:72-94` | Variante (U) |
| `preprocessamento/modelo_min_station_das_preprocess.py:921-956` | Variante (U) |
| `experiments/lagrangean/lagrangeano_min_station.py`, `p_relaxation_min_station.py` | Formulação (2)–(8), rejeitam `S ∩ T` com `ValueError` (scripts históricos, fora de uso; não corrigidos nesta rodada) |
| `baseline.py` | Variante (U) — **adotada na rodada E5** (era formulação (2)–(8) até então) |

**Nota de higiene (E5):** a versão anterior desta tabela citava `modelo_min_station_fluxo_2.py:108-160`, arquivo que não existe mais no repositório. Removido.

`base-formulation.md §10.1` dizia que (U) "não [foi] adotada" — **já corrigido**: (U) é a formulação corrente em `baseline.py` desde a rodada E5. Com `S ∩ T = ∅`, as duas versões são idênticas e nenhum resultado experimental anterior é invalidado.

### A.8 Instâncias com peso não unitário

Os agentes verificaram que a maioria das instâncias usa pesos `≥ 1`, nunca `< 1`, o que garante `A^w ⊆ A^passos` (nenhum falso positivo em relação a Das). Porém:

- Apenas `hc9u` tem todos os pesos `= 1`.
- `cc12-2u` tem pesos `1`, `2` e `3` (apesar do sufixo `u`).
- Instâncias TNTP têm pesos inteiros não unitários.

Resultados dessas instâncias devem ser apresentados como extensão ponderada (Q2), não como MIN-STATION de Das.

### A.9 Novos casos verificados à mão pelos agentes

Os agentes verificaram 15 casos adicionais, incluindo:
- `S = T` (todos os robôs já estão nos alvos): PLI atual inviável; (U) dá `OPT = 0`.
- `|V| = 1`, `S = T = {v}`: PLI atual inviável; (U) dá `OPT = 0`.
- Estrela `K_{1,4}` com `S ∩ T = {v}`: (U) dá `OPT = 1`; confirma que a troca em `v ∈ S ∩ T` funciona com `y_v = 0` somente quando um único robô troca, mas dois robôs chegando forçam `y_v = 1`.
- Gadget do Lema 1 de Das (satisfatível e insatisfatível): PLI acerta em ambos; LP com Big-M `m` não distingue os dois casos nem no menor gadget (razão de integralidade 2).

Todos os casos com `S ∩ T = ∅` concordaram com o MIN-STATION. Todos os casos com `S ∩ T ≠ ∅` tiveram PLI atual inviável e (U) correta.

### A.10 Lacunas de prova a preencher em versão formal

Os agentes listaram os pontos que uma prova formal deve detalhar:

1. Definir a rede auxiliar `N` completa com `σ`, `τ` e arcos de capacidade 1 nas extremidades.
2. Citar o teorema de decomposição de fluxos inteiros (Ahuja–Magnanti–Orlin, Thm. 3.5) e provar que cada caminho `σ–τ` tem peso 1.
3. Provar a bijeção `π: S → T` explicitamente pela injetividade dos arcos terminais.
4. Enunciar o invariante de bateria formalmente: ao partir de `x_i ∈ C`, a bateria vale `r`; ao longo do caminho mínimo até `x_{i+1}`, a bateria é `≥ r − d ≥ 0`.
5. Separar dois casos no Lema dos ciclos: (i) ciclos não tocam vértices com `y = 0`; (ii) subtrair um ciclo mantém a viabilidade.
6. Para a variante (U): refazer a análise de balanço e ativação por classe (`S ∖ T`, `T ∖ S`, `S ∩ T` com robô parado, `S ∩ T` com troca, `V ∖ (S ∪ T)`).

---

## Verificação recomendada (não executada)

Script de teste pequeno com oráculo independente de `A_r` (BFS em estados `(vértice, bateria)` + emparelhamento perfeito), comparado com a PLI atual e com (B) em todos os grafos conexos com n ≤ 5, r ∈ {1,2,3}, m ≤ 3, incluindo `S ∩ T ≠ ∅`. Critério de sucesso: OPT igual e, para cada `C`, a mesma viabilidade. O modelo atual deve falhar exatamente nos casos com `S ∩ T ≠ ∅`.
