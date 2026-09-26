# Direções de PLI para o MIN-STATION

> **Natureza deste documento.** Análise teórica, feita sem executar código e sem alterar arquivos do repositório. Referência matemática: a formulação base validada (variante U, que coincide com a formulação (2)–(8) quando `S ∩ T = ∅`; é o caso de todas as instâncias do repositório). Evidência experimental: somente os CSVs de resultados e logs do Gurobi já lidos nesta sessão. Por instrução, nenhum outro resultado do repositório foi analisado.
>
> Cada afirmação tem uma marca:
> - **[Provado]**: há prova neste documento ou no relatório de validação;
> - **[Esboço]**: há argumento, mas falta formalizar detalhes;
> - **[Hipótese]**: ainda precisa ser testada;
> - **[Evidência]**: sai de números do repositório, com a fonte citada.
>
> As referências bibliográficas estão no Apêndice B e **devem ser conferidas**; não foi possível verificá-las nesta sessão.
>
> **Verificação.** Dois verificadores adversariais independentes revisaram o documento: um cobriu as seções 0–4, o outro as seções 5–13. Também foi feita uma checagem direta da estrutura de `hc9u.txt`. As correções resultantes já estão incorporadas; o registro está no Apêndice C.

---

## 0. Convenções

- `G = (V,E)`, `n = |V|`, `S, T ⊆ V`, `|S| = |T| = m`. `A_r = {(u,v): u ≠ v, d(u,v) ≤ r}`, onde `d` é a distância de caminho mínimo usada na construção de `A_r`. No código, `d` é ponderada (Dijkstra); a distância em passos é um caso particular. Salvo indicação em contrário, os resultados valem para **qualquer** `d` desse tipo.
- `N⁺(v) = {w : (v,w) ∈ A_r}`, `N⁻(v) = {u : (u,v) ∈ A_r}`, e `N⁺(X) = ∪_{x∈X} N⁺(x)`.
- `a_v = [v ∈ S]`, `b_v = [v ∈ T]`, `in(v) = Σ_u f_uv`, `out(v) = Σ_w f_vw`.
- Formulação base (U): `min Σ_v y_v` sujeito a:
  - (B) `out(v) − in(v) = a_v − b_v`;
  - (E) `in(v) ≤ b_v + (m − b_v) y_v`;
  - (S) `out(v) ≤ a_v + (m − a_v) y_v`;
  - `y ∈ {0,1}^V`, `f ∈ Z₊^{A_r}`.
- **Trânsito:** `τ_v(f) := in(v) − b_v = out(v) − a_v`. As duas expressões coincidem por (B). Com `S ∩ T = ∅`, é o número de robôs que entram **e** saem de `v`. Na variante U, para `v ∈ S∩T`, `τ_v` pode valer −1 (robô parado) e o trânsito efetivo é `(in(v) − 1)⁺`.
- `h*(s,t)`: número mínimo de vértices interiores de um caminho `s → t` em `A_r` (distância em saltos em `A_r`, menos 1).
- `W* := min_π Σ_s h*(s,π(s))` é a atribuição de soma mínima. `L_bot := min_π max_s h*(s,π(s))` é a atribuição gargalo.
- `B_C`: grafo bipartido `S × T` com `s ~ t` ⇔ existe caminho `s → t` em `A_r` com interior contido em `C`.
- Nas derivações supõe-se `S ∩ T = ∅`. Quando a extensão para a variante U não é imediata, isso é dito explicitamente.

---

## 1. Estrutura matemática do problema

### 1.1 Reformulação combinatória exata

**Teorema 1 [Provado].** `C ⊆ V` é viável ⇔ `B_C` tem emparelhamento perfeito.

*Prova.* Pelo relatório de validação, `C` é viável ⇔ existe uma bijeção `π` e, para cada `s`, um caminho em `A_r` de `s` a `π(s)` com interior em `C`. As rotas são independentes: não há tempo, colisão nem capacidade de estação. Então os robôs só interagem através de `π`, e isso é exatamente um emparelhamento perfeito em `B_C`. ∎

Consequências:
- (a) a viabilidade é **monótona** em `C`: se `C ⊆ C'`, então `B_C ⊆ B_{C'}`;
- (b) fixado `C`, a viabilidade é polinomial (§3);
- (c) MIN-STATION ≡ `min { |C| : ν(B_C) = m }`, onde `ν` é o tamanho do emparelhamento máximo.

### 1.2 Onde está a dificuldade

- **O fluxo `f` é só um certificado.** Com `y` fixo, verificar viabilidade é polinomial (max-flow). Com as rotas fixas, o problema é trivial. A combinatória está inteira na escolha de `C`.
- **Duas fontes distintas de dificuldade**, que o §2 separa com duas famílias de instâncias:
  - **(D1) Conectividade com custo nos nós, compartilhado.** Cada robô precisa de uma cadeia de estações, e o que reduz o custo é compartilhar estações entre robôs. Com `m = 1` o problema é um caminho mínimo em `A_r`, portanto polinomial. A dificuldade nasce do compartilhamento entre dois ou mais robôs.
  - **(D2) Acoplamento de Hall.** Os robôs não são rotulados, então `π` é escolhido junto com `C`. Cada robô pode, sozinho, alcançar algum destino, e mesmo assim o conjunto de robôs violar a condição de Hall.
- **Complexidade.** O problema é NP-difícil em grafos gerais (Das). Com `π` fixo, o problema é um caso particular de floresta de Steiner dirigida com custos nos nós sobre `A_r`. Não verifiquei se a restrição a dígrafos de alcance preserva a NP-dificuldade dessa versão rotulada.

### 1.3 Relação com problemas clássicos (sem forçar a classificação)

| Problema clássico | Parte equivalente | Diferença |
|---|---|---|
| Projeto de rede de custo fixo, uma commodity, projeto nos nós | É a estrutura exata da base: fluxo único, e `y_v` libera capacidade `m` = demanda total | Aqui a agregação é **exata**, e não uma relaxação de um modelo multicommodity, porque o pareamento é livre. A capacidade `m` nunca é recurso escasso |
| Projeto com capacidade nos nós | (E) e (S) são capacidades de nó `m·y_v` | Como a capacidade é igual à demanda total, na prática o problema é não capacitado |
| Steiner (fluxo único × multicommodity × cortes dirigidos) | Mesmo fenômeno de LP fraco da formulação de fluxo único (§2) | A conectividade exigida é um emparelhamento perfeito, não uma árvore |
| Colocação de relés com alcance limitado (STP-MSPBEL, *relay placement*) | Minimizar pontos de relé sob saltos de comprimento ≤ `r` | Exige emparelhamento `S → T` e papéis dirigidos (origem sem estação só emite, destino sem estação só recebe) |
| Localização de postos de reabastecimento com alcance, versão de cobertura com roteamento | É o problema aplicado mais próximo | Nesses modelos os pares O-D são fixos. Aqui a bijeção é livre, e isso gera os cortes de Hall (§5), que não têm análogo lá |
| Set covering | A projeção exata sobre `y` é um set covering (Teorema 6) | A família de conjuntos a cobrir é exponencial e implícita |
| Interdição de rede/emparelhamento | A separação exata dos cortes fortes equivale a interditar relés de peso mínimo que destroem o emparelhamento perfeito | Aparece apenas na separação |
| Localização de facilidades | Não se aplica: as estações formam cadeias e não há cliente atendido por uma única facilidade | No regime de terminais isolados, a 1ª e a última estação de cada terminal se comportam como cobertura/dominação (§2.5) |
| Projeto sobrevivente | Não se aplica: não há exigência de redundância | — |

### 1.4 Tamanho e regimes

- **Tamanho de `A_r`.** `|A_r| = Σ_v (|B_d(v,r)| − 1)`, que cresce com o volume das bolas de raio `r`. Para `r ≥ diâmetro`, `|A_r| = n(n−1)`. No repositório vai de 1,7 mil a 2,8 milhões de arcos [Evidência: CSVs de resultados].
- **Efeito de `m`.** `m` é o Big-M, e o gap do LP chega a um fator `m` (§2).
- **Efeito da densidade de terminais.** Ela determina quantos robôs têm destino a um salto, e por isso define o regime.
- **Três regimes** [Evidência + Hipótese]:
  - **(R-a) Longo curso** (TNTP, com `m` de 5 a 50): cada robô precisa de vários relés. Na raiz pós-presolve o LP vale 0,4–3,5, contra ótimo ou melhor limite de 11–47.
  - **(R-b) Terminais densos e isolados.** Em `hc9u` verifiquei, varrendo o arquivo inteiro, que:
    - os 4608 arcos são arestas de hipercubo com peso 1;
    - os 256 terminais são **exatamente** os vértices de paridade par.

    Com `r = 1`, nenhum terminal é vizinho de outro, e todo robô precisa de estação no primeiro e no último salto. Minha hipótese é que `bip42p` e `hc10–12p` têm estrutura análoga (instâncias bipartidas/hipercubo da SteinLib), mas isso não foi verificado. O LP vale 1,0, contra LB de 31 a 149.
  - **(R-c) `r` grande** (`cc*`, `lin23`, com R = 500): `|A_r|` de 340 mil a 2,8 milhões, ótimo pequeno (UB de 3 a 24), LP de 0,1 a 1,1.

### 1.5 Estruturas parciais (detalhes nas seções indicadas)

- **`y` fixo:** um único max-flow (§3).
- **`f` contínuo, `y` binário:** mesmo conjunto de `y` viáveis e mesmo ótimo, pela propriedade TU (Prop. 3.2).
- **`y` relaxado:** o problema vira um fluxo de custo mínimo (Teorema 2).

### 1.6 Simetria e degenerescência

- **Em `y`.** Os automorfismos de `G` que preservam `S` e `T` geram soluções equivalentes. No hipercubo, cada vértice ímpar domina exatamente 9 terminais, o que produz muitas coberturas quase equivalentes. **[Evidência, E5]:** 0 gêmeos por C1 em hc9u–hc12p (maior classe de assinatura = 1); `Symmetry=2` do Gurobi não alterou resultado (sonda binária); orbital branching não testado. B2 encerrada por ausência de evidência positiva, não por prova de ausência de simetria (ver B2 em §13).
- **Em `f`.** Para o mesmo `y` existem muitas soluções `f`: rotas alternativas, pareamentos alternativos, circulações entre estações. Isso gera degenerescência. Ramificar em `f` não tem valor, porque a integralidade de `f` é automática (§3).
- **Vantagem da agregação.** Ela elimina a simetria de rótulos dos robôs. Essa é uma vantagem real da formulação atual e deve ser preservada em qualquer alternativa.

---

## 2. Diagnóstico da formulação BASE

### 2.1 O LP é um fluxo de custo mínimo

**Teorema 2 [Provado].** Seja `S ∩ T = ∅` e `m ≥ 2`. Então

`z_LP = min { Σ_{v ∉ S∪T} τ_v(f)/m + Σ_{v ∈ S∪T} τ_v(f)/(m−1) : f ≥ 0 satisfaz (B) }`.

Esse mínimo é atingido por um fluxo inteiro e acíclico, isto é, por um sistema de `m` caminhos simples com bijeção implícita.

*Prova.* Fixe `f` satisfazendo (B). As restrições (E) e (S) só limitam `y_v` por baixo:
- `v ∉ S∪T`: (E) dá `y_v ≥ in(v)/m = τ_v/m`, e (S) dá a mesma cota;
- `v ∈ S`: (S) dá `y_v ≥ (out(v) − 1)/(m−1) = τ_v/(m−1)`, que domina `in(v)/m = τ_v/m` vinda de (E);
- `v ∈ T`: simétrico, com `y_v ≥ τ_v/(m−1)`.

Logo, para `f` fixo, o `y` ótimo é `y_v = c_v τ_v`, com `c_v = 1/m` para não terminais e `c_v = 1/(m−1)` para terminais, desde que `c_v τ_v ≤ 1`.

O problema resultante, `min Σ c_v τ_v` sujeito a (B), é um fluxo de custo mínimo numa rede com divisão de vértices: o arco `v_in → v_out` tem custo `c_v`. Como todo `c_v > 0`, qualquer ciclo tem custo positivo, então o ótimo é acíclico. Fluxo acíclico se decompõe em `m` caminhos simples, e isso dá:
- `τ_v ≤ m` para não terminais;
- `τ_v ≤ m − 1` para terminais, porque o caminho que parte (ou termina) em `v` não transita por `v`.

Assim `y_v ≤ 1` nunca fica ativo. A matriz de rede é TU, então existe ótimo inteiro. ∎

*Variante U, `v ∈ S∩T`.* O custo passa a ser `(in(v) − 1)⁺/(m−1)`: a primeira unidade que entra é gratuita (a troca), e as seguintes custam `1/(m−1)`. O custo fica convexo e linear por partes, e a integralidade se mantém. Uma ressalva: aqui podem existir ciclos de custo zero. Por exemplo, `u, v ∈ S∩T` adjacentes, `f_uv = f_vu = 1` e `y = 0`. Então o que vale é "existe um ótimo acíclico", e não "todo ótimo é acíclico".

### 2.2 Consequências

- **2.2a [Provado] O LP presume compartilhamento perfeito.** Cada uso de um vértice custa `1/m`, como se toda estação fosse rateada entre os `m` robôs. O LP só é exato se o **fluxo de custo mínimo do Teorema 2** fizer cada vértice de trânsito ser usado por `m` robôs (ou `m − 1`, se for terminal). Não basta que exista um ótimo inteiro com compartilhamento total.
  - Contraexemplo, com `m = 2` e `r = 1`: arestas `s1–h`, `s2–h`, `h–t1`, `h–t2`, `s1–t2`.
  - `C = {h}` é ótimo, com os dois robôs passando por `h`.
  - O LP, porém, manda `s1 → t2` direto e `s2 → h → t1`, e fica com `z_LP = 1/2`.
  - Quando nenhuma estação é compartilhada, o erro chega a um fator `m` (F1, F2).
- **2.2b [Provado] Limites.** `min Σ τ_v = W*`, porque os caminhos são independentes. Daí:
  - `W*/m ≤ z_LP ≤ W*/(m−1)`;
  - a união dos interiores dos caminhos ótimos de `W*` é uma solução viável, então `OPT ≤ W*`;
  - logo `OPT/m ≤ z_LP ≤ OPT`, e a razão de integralidade é no máximo `m`.
- **2.2c [Provado] O LP não é melhor que um limite combinatório trivial.** `L_bot` é limite inferior válido: toda solução com bijeção `π` contém o interior da rota de cada robô, logo `|C| ≥ max_s h*(s,π(s))`. Então `z_LP ≤ W*/(m−1) = (m/(m−1))·(W*/m) ≤ (m/(m−1))·L_bot`. Em outras palavras, a menos do fator `m/(m−1)`, o LP não supera um limite que se obtém com BFS em `A_r` e uma atribuição gargalo, sem resolver LP algum.
- **2.2d [Provado] Com `m = 1` o LP é sempre exato**, porque o problema é um caminho mínimo. Esse é o único valor de `m` com `LP = OPT` em **toda** instância. Para cada `m ≥ 2` existem instâncias exatas (por exemplo, qualquer uma com `OPT = 0`) e instâncias com gap (F1 com `k = 1`).
- **2.2e [Evidência] Consistência com o repositório.**
  - `hc9u`: `z_LP = 1,0 = 128/128`. Cada robô atinge um destino com um único relé não terminal, pago a `1/128`. Esse valor aparece idêntico antes e depois do presolve (log `min_station_das_20260516_163057.txt`).
  - `cc10-2u`: `z_LP = 0,149`, compatível com 10 trânsitos não terminais para 67 robôs (`10/67`). O valor arredondado não determina `W*` de forma única.

### 2.3 Família F1 ("raios"): gap tendendo a `m` porque só o centro é compartilhado

**[Provado]**
- **Instância.** `r = 1`, um centro `h`. Para cada `i = 1..m` há um caminho `s_i — p_{i1} — … — p_{ik} — h` e um caminho `h — q_{i1} — … — q_{ik} — t_i`, com todos os raios disjuntos.
- **Ótimo inteiro.** Todo robô percorre inteiro o seu raio de origem, passa por `h` e percorre algum raio de destino. Os `m` raios de destino são todos usados. Logo `C` contém os `2mk` vértices dos raios mais `h`, e `OPT = 2mk + 1`.
- **LP.** Todos os trânsitos ocorrem em vértices não terminais, então `z_LP = W*/m = m(2k+1)/m = 2k + 1`.
- **Razão.** `(2mk+1)/(2k+1) → m` quando `k → ∞`. Aqui também `L_bot = 2k + 1`.

### 2.4 Família F2 ("bolsões de Hall"): gap igual a `m` com conectividade individual perfeita

**[Provado]**
- **Instância.** `r = 1`, `k` bolsões. O bolsão `j` tem:
  - origens `a_j, b_j` e o destino `c_j`, com arestas `a_j—c_j` e `b_j—c_j`;
  - o relé `x_j`, com arestas `a_j—x_j`, `b_j—x_j` e `x_j—d_j`;
  - o destino `d_j`, a origem `e_j` e o destino `g_j`, com arestas `d_j—e_j` e `e_j—g_j`.

  Os bolsões são ligados por caminhos de `L ≥ 2` vértices não terminais entre `g_j` e `g_{j+1}`. Assim `N⁺(a_j) ∪ N⁺(b_j) = {c_j, x_j}` continua valendo. No total, `m = 3k`.
- **Ótimo inteiro.**
  - Dentro de cada bolsão, `a_j` e `b_j` disputam `c_j`, e o robô excedente precisa de uma estação na sua primeira parada, que está em `{c_j, x_j}`. Os bolsões são disjuntos, então `OPT ≥ k`.
  - `C = {x_j}` é viável com as rotas `b_j → x_j → d_j`, `a_j → c_j` e `e_j → g_j`. Logo `OPT = k`.
- **LP.** Há um trânsito não terminal por bolsão, então `z_LP = k/(3k) = 1/3`, e a razão é `3k = m`.
- **O que F2 mostra.** Toda origem tem um destino vizinho e todo destino tem uma origem vizinha. Por isso **nenhum corte de conectividade individual** (C1 e C3 do §5) é violado por `y = 0`: o LP da base mais todos esses cortes continua valendo `1/3`. O gap aqui é de acoplamento (D2), não de conectividade (D1).

### 2.5 Terminais isolados (hc9u): o LP vale 1, o limite estrutural vale pelo menos 28,44

**[Provado, sob a estrutura verificada]**
- **Estrutura.** Em `hc9u`, `r = 1`, os terminais formam um conjunto independente e cada vértice ímpar tem exatamente 9 vizinhos, todos terminais.
- **Cortes de primeiro salto.** Toda origem `s` exige `Σ_{v∈N(s)} y_v ≥ 1` (C1, §5.1), e todo destino exige o análogo.
- **Soma das 256 desigualdades.** Cada vértice ímpar aparece em exatamente 9 delas, então `9 Σ_{v ímpar} y_v ≥ 256`, ou seja, `Σ y ≥ 256/9 ≈ 28,44`. Como o objetivo é inteiro, **`OPT ≥ 29`** sem resolver nenhum MIP.
- **Comparação** [Evidência]:
  - LP da base: 1,0;
  - melhor LB obtido pelo baseline em 3600 s: 31;
  - raiz com os cortes "camadas": 24,03;
  - raiz da variante VI após o presolve: 32.

### 2.6 Instância Tri ("triângulo"): a cobertura também tem gap

**[Provado]**
- **Instância.** `r = 1`, relés `a, b, c`. Cada par `s_i, t_i` é adjacente a dois relés: `{a,b}` para `i = 1`, `{b,c}` para `i = 2` e `{c,a}` para `i = 3`. Os terminais ficam isolados entre si.
- **Valores.**
  - `OPT = 2`: com um único relé, algum robô fica sem primeiro salto;
  - `z_LP = 3·(1/3) = 1`;
  - LP da cobertura (§4) = 1,5, com `y = 1/2` nos três relés;
  - a desigualdade `y_a + y_b + y_c ≥ 2` é válida: é um corte CG de posto 1, obtido somando as três coberturas, dividindo por 2 e arredondando.

  Portanto `OPT (2) > cobertura (1,5) > z_LP (1)`.

### 2.7 Padrões fracionários: onde o LP "compra frações de estação"

- **P1 — Diluição.** `y_v = τ_v/m`. As responsáveis são (E) e (S), com coeficiente agregado `m`. Uma estação usada por um único robô custa `1/m` (F1).
- **P2 — O "1+" dos terminais.** A origem emite o próprio robô de graça, e cada unidade extra que transita por um terminal custa `1/(m−1)`. O LP pode desviar robôs por terminais quando isso encurta a rota.
- **P3 — Pareamento de soma mínima.** O LP escolhe o `π` que minimiza o total de trânsitos (`W*`), e não o `π` que permite compartilhar estações. É cego ao acoplamento de Hall (F2).
- **P4 — Circulações contra desigualdades em `f`** [Provado nas condições abaixo]. Tome uma desigualdade por arco, válida, como `f_sv ≤ y_v + in(s)` para `v ∉ T`: se `y_v = 0`, `f_sv ≤ in(v) = 0`; se `y_v = 1`, `f_sv ≤ out(s) = 1 + in(s)`.
  - **Como o LP a contorna.** Com `f_sv = 1` e `y_v = 1/m`, o LP pode criar uma circulação `s → w → s` de valor `θ = 1 − 1/m`, através de outro vizinho `w ≠ v` com arco de volta `(w,s)`. O custo é `θ(1/(m−1) + 1/m)`, contra `θ` para elevar `y_v`.
  - **Quando compensa.** Só para `m ≥ 3` e se `w` existir. Para `m = 2`, ou para uma origem folha (como em F1), a desigualdade funciona.
  - **Custo do contorno.** Não é gratuito: a contribuição sobe de `1/m` para `(3m−1)/m²`, por exemplo de 1/3 para 8/9 com `m = 3`.
  - **Conclusão.** Fortalecer a formulação agregada no espaço de `f` é frágil (ganho parcial e dependente da topologia), e cortes no espaço de `y` são robustos.

### 2.8 Topologias que pioram a relaxação

- estações que não podem ser compartilhadas: corredores disjuntos (F1);
- bolsões com deficiência de Hall (F2);
- terminais isolados em que cada relé atende poucos terminais (hc9u);
- `r` grande, que faz `W*` ficar pequeno e o LP tender a 0 mesmo com `OPT ≥ 2` (`cc10-2u`).

### 2.9 O presolve recuperava força na variante VI, e não recupera na all-vertices

[Evidência + Hipótese]
- **Variante VI, `hc9u`** (`hc9u_log.txt`: 4864 inteiras, das quais 256 binárias): o presolve deixa todas as 2543 variáveis binárias, e a raiz vale **32**.
- **Variante all-vertices, `hc9u`:** a raiz pós-presolve vale **1,0**.
- **Interpretação provável** (não é possível confirmar como o Gurobi faz isso por dentro):
  - Na variante VI, origens nunca retransmitem, então `f_sv ≤ 1` nos arcos de origem. O presolve consegue apertar `in(v) ≤ m·y_v` para uma cota local, da ordem do número de origens vizinhas de `v`.
  - Na variante all-vertices, uma origem com estação pode emitir até `m` unidades. O limite superior dos arcos de origem passa a ser `m`, e esse aperto deixa de existir.
- **Lição.** A extensão para todos os vértices, que é correta e mais fiel a Das, **removeu uma propriedade estrutural que o presolve explorava**. Recuperar essa força exige cortes explícitos em `y` (§5).

---

## 3. Estrutura do subproblema com y fixo

### 3.1 Rede N(y)

- **Nós:** `σ`, `τ`, e dois nós `v_in` e `v_out` para cada `v`.
- **Arcos de origem e destino:** `σ → s_out` com capacidade 1, para cada `s ∈ S`; `t_in → τ` com capacidade 1, para cada `t ∈ T`.
- **Arcos de trânsito:** `v_in → v_out` com capacidade `κ_v y_v`, onde `κ_v = m` se `v ∉ S∪T` e `κ_v = m − 1` se `v` é terminal.
- **Arcos de alcance:** `u_out → w_in`, com capacidade infinita, para cada `(u,w) ∈ A_r`.

### 3.2 Teoremas e algoritmo

**Teorema 3 [Provado].** Fixado `y`, `f` satisfaz (B), (E) e (S) ⇔ `f` é a restrição, aos arcos de alcance, de um fluxo `σ–τ` de valor `m` em `N(y)`.

*Prova.* Identifique `τ_v` com o fluxo no arco `v_in → v_out`.
- `v ∉ S∪T`: `in = out = τ ≤ m·y_v`, que é (E) e (S).
- `s ∈ S`: `in(s) = τ_s` e `out(s) = 1 + τ_s`, que é (B). A restrição (S) equivale a `τ_s ≤ (m−1) y_s`, e (E) fica implicada.
- `t ∈ T`: simétrico. ∎

**Proposição 3.1 [Provado].** Para `y ∈ {0,1}^V`, a viabilidade se decide com um max-flow. De forma equivalente, pelo Teorema 1: uma busca por origem em `A_r` que **só expande vértices de `C`**, seguida de Hopcroft–Karp. Terminais fora de `C` entram apenas como extremidade.

*Cuidado.* Uma BFS no subgrafo induzido por `S ∪ C ∪ T` está **errada**. No caminho `s1–s2–t1–t2`, com `r = 1` e `C = ∅`, ela faria o robô de `s1` passar por `s2` e `t1`, que não têm estação.

**Proposição 3.2 [Provado] (integralidade gratuita).** A correspondência `f ↔ (f, τ(f))` é linear, injetiva e tem inversa inteira. O politopo de fluxo de `N(y)` é inteiro quando as capacidades são inteiras, que é o caso para `y` binário. Logo o poliedro `{f : (B),(E),(S)}` tem vértices inteiros. Consequência: **declarar `f` contínuo não muda o conjunto de `y` viáveis nem o ótimo**. As rotas inteiras se obtêm de qualquer max-flow inteiro.

Declarar `f` contínuo reduz as variáveis inteiras de `|A_r| + n` para `n`. Se isso acelera o B&B é uma questão empírica **[Hipótese]**: o solver perde MIR/Gomory sobre `f`, mas deixa de ramificar em `f`.

**Teorema 4 [Provado] (caracterização por cortes).** Chame de *finito* um corte `X` (com `σ ∈ X`, `τ ∉ X`) do qual não sai nenhum arco de alcance. Para um corte finito, defina:
- `Z(X) = {v : v_in ∈ X, v_out ∉ X}`;
- `k(X)` = número de arcos `σ→s` e `t→τ` cortados.

A capacidade do corte é `k(X) + Σ_{v∈Z(X)} κ_v y_v`. Para `y` binário, viável ⇔ todo corte finito tem capacidade `≥ m` ⇔ condição de Hall em `B_C`.

**Variante U.** Com `v ∈ S∩T` aparecem arcos de permanência, como na rede auxiliar do relatório de validação, e `B_C` ganha o par `s ~ s` (caminho vazio). A caracterização por cortes continua válida, com `k(X)` contando esses arcos. Nesse caso, porém, a identidade `δ = m − k = |{s : s_out ∈ X}| − |{t : t_in ∈ X}|` do §4 precisa ser reescrita incluindo os arcos de permanência. Tudo o que segue supõe `S ∩ T = ∅`.

---

## 4. Poliedro e projeção sobre y

Defina a **deficiência** de um corte finito: `δ(X) := m − k(X) = |{s : s_out ∈ X}| − |{t : t_in ∈ X}|`.

**Teorema 5 [Provado] (projeção do LP = cortes fracos).**

`proj_y(LP base) = { y ∈ [0,1]^V : Σ_{v∈Z(X)} κ_v y_v ≥ δ(X), para todo corte finito X }`.

*Prova.* Para cada `y`, aplique max-flow/min-cut com capacidades `κ_v y_v ≥ 0`. ∎

Com `κ_v ≈ m`, cada restrição diz `y(Z) ≥ δ/m`. **O Big-M aparece aqui na sua forma exata:** um corte que só um robô precisa atravessar (`δ = 1`) exige apenas `1/m` de estação.

**Teorema 6 [Provado] (formulação exata só em y).** Seja `𝒵 = { Z(X) : X corte finito com δ(X) ≥ 1 }`. Então `C` é viável ⇔ `C ∩ Z ≠ ∅` para todo `Z ∈ 𝒵`. Consequentemente,

MIN-STATION ≡ `min { Σ y_v : y(Z) ≥ 1 ∀ Z ∈ 𝒵, y ∈ {0,1}^V }`,

um set covering.

*Prova.*
- (⇒) Se `C ∩ Z = ∅`, a capacidade do corte em `N(C)` é `k(X) = m − δ < m`, e `C` é inviável.
- (⇐) Seja `C` inviável e `X*` um corte mínimo, de capacidade `< m`. Primeiro, um detalhe: se um terminal `v ∈ S` pertence a `Z(X*)`, então `v_out ∉ X*`, e o arco `σ → v_out` está cortado, contando em `k`. O mesmo vale para `v ∈ T`, via o arco `v_in → τ`. Logo, para `v ∈ Z(X*) ∩ C`, a contribuição à capacidade é `≥ m`: igual a `m` se `v` não é terminal, e `≥ 1 + (m−1)` se é. Então capacidade `< m` implica `Z(X*) ∩ C = ∅` e `δ(X*) ≥ 1`. ∎

**Teorema 7 [Provado] (cada `y(Z) ≥ 1` é um corte CG de posto 1).** Não afirmo que essas linhas esgotam o fecho CG. Parta da desigualdade do Teorema 5 com `δ ≥ 1` e divida por `m`: `Σ_{v∈Z} (κ_v/m) y_v ≥ δ/m > 0`. Os coeficientes são `≤ 1` e `y ≥ 0`, então `y(Z) ≥ δ/m`, e o arredondamento inteiro dá `y(Z) ≥ 1`. É o análogo exato da *cut-set inequality* `Σ y ≥ ⌈D/C⌉` de projeto de rede capacitado, aqui com capacidade `C = m` e demanda `D = δ`.

**Corolário 7.1 [Provado].** Seja `P_cov = { y ∈ [0,1]^V : y(Z) ≥ 1, ∀ Z ∈ 𝒵 }`. Então `P_cov ⊆ proj_y(LP base)`, e portanto `LP_cov ≥ z_LP`.

*Prova.* Seja `X` finito com `δ ≥ 1`.
- Se `δ ≤ m − 1`: `Σ κ_v y_v ≥ (m−1)·y(Z) ≥ m − 1 ≥ δ`.
- Se `δ = m`: então `k = 0`, logo `Z` não tem terminais (pelo detalhe da prova do Teorema 6), `κ_v = m` em todo `Z`, e `Σ κ_v y_v = m·y(Z) ≥ m`. ∎

A inclusão pode ser **estrita por um fator `m`**:
- em F1, cada vértice de raio é um separador unitário, logo `LP_cov = OPT = 2mk + 1`, contra `z_LP = 2k + 1`;
- em F2, `LP_cov = k = OPT`, contra `z_LP = 1/3`.

**Estrutura de `P_cov`.**
- É um politopo de set covering.
- `Z` minimal é **condição necessária** para que `y(Z) ≥ 1` seja faceta. As condições suficientes da teoria de set covering (Apêndice B) ainda precisam ser verificadas neste contexto.
- `P_cov` também tem gap (Tri). Por isso cortes de posto ≥ 2 (tipo ciclo ímpar, `{0,½}`-CG) sobre as linhas de cobertura são relevantes. Com essas linhas explícitas no modelo, os cortes *zero-half* e *clique* genéricos do solver passam a agir sobre a estrutura certa [Hipótese].

---

## 5. Cortes e branch-and-cut

Para cada família são dados: (1) a desigualdade; (2) a prova de validade; (3) o que ela elimina; (4) se entra a priori ou dinamicamente; (5) a separação; (6) a complexidade.

### 5.1 C1: primeiro salto (por origem) e último salto (por destino)

1. Se `s ∈ S∖T` e `N⁺(s) ∩ T = ∅`: `Σ_{v∈N⁺(s)} y_v ≥ 1`. Se `t ∈ T∖S` e `N⁻(t) ∩ S = ∅`: `Σ_{v∈N⁻(t)} y_v ≥ 1`.
2. O robô de `s` precisa sair de `s`, e o primeiro salto chega a um `v ∉ T`, que é portanto interior da rota e precisa estar em `C`. É um caso particular do Teorema 6.
3. Em F1, força só o primeiro e o último vértice de cada raio. O LP passa a `2m + 2k − 1`, contra `OPT = 2mk + 1`, e F1 só fecha inteira quando `k = 1`. Em hc9u, leva o LP a exatamente 256/9.
4. A priori, com no máximo `2m` linhas e tamanho total ≤ `|A_r|`.
5. Não precisa de separação.
6. Trivial.

### 5.2 C2: bandas de distância (para o regime de longo curso)

1. Seja `s ∈ S∖T` e `D_s = min_{t∈T} d(s,t)`. Para todo `a ≥ 0` com `a + r < D_s`: `Σ_{v : a < d(s,v) ≤ a+r} y_v ≥ 1`. Para destinos vale o análogo, com `D'_t = d(S,t)`.
2. **[Provado]** Considere a rota `s = x_0, …, x_K = π(s)` e `d_i = d(s, x_i)`. Tome o último índice `i` com `d_i ≤ a`. Pela desigualdade triangular, `a < d_{i+1} ≤ d_i + d(x_i, x_{i+1}) ≤ a + r`. Como `d_{i+1} ≤ a + r < D_s`, `x_{i+1}` não é destino, logo é interior e está em `C`. **A prova vale para qualquer métrica**, inclusive a ponderada usada no código.
   - As bandas disjuntas `(0,r], (r,2r], …` são `⌈D_s/r⌉ − 1` ao todo. Somadas, dão `LP ≥ ⌈D_s/r⌉ − 1` para cada robô.
3. Elimina F1 inteira **quando usada dos dois lados**:
   - as bandas das origens a distâncias `1..k+1` são unitárias e forçam o raio da origem e `h`;
   - as bandas dos destinos forçam os raios de destino;
   - além de `h`, as bandas das origens contêm `2m − 1` vértices.

   Captura o custo mínimo individual de cadeias longas.
4. As bandas disjuntas entram a priori, com `O(Σ_s D_s/r)` linhas. Todas as janelas deslizantes podem ser separadas dinamicamente.
5. Para cada `s`, calcular `d(s,·)` (Dijkstra), ordenar e varrer janelas de largura `r`, somando `y*`.
6. `O(|E| + n log n)` por origem: polinomial.

### 5.3 C3: corte de nós por robô (conectividade individual)

1. Se `Z ⊆ V∖{s}` intercepta o interior de todo caminho `s → T` em `A_r`, então `y(Z) ≥ 1`. Para destinos vale o análogo.
2. Caso particular do Teorema 6. Tome `X` como o fecho de `s` evitando `Z`. Então `δ(X)` é o número de origens alcançadas sem atravessar `Z`, logo `δ ≥ 1`. Não vale necessariamente `δ = 1`: no caminho `s1–s2–z–{t1,t2}`, com `Z = {z}`, o fecho de `s1` tem `δ = 2`. Para a validade basta `δ ≥ 1`.
3. Elimina F1 e as cadeias longas. **Não** elimina F2, porque ali todo robô individualmente alcança um destino.
4. Separação dinâmica.
5. **Separação exata:** um max-flow de `s` até `T` com capacidade `y*_v` nos nós interiores e capacidade infinita nos arcos. Se o valor é `< 1`, o corte mínimo dá `Z` (Menger fracionário). *Atenção:* o critério não é o caminho mínimo com pesos `y*`. O caminho mínimo testa outra família de desigualdades.
6. `m` max-flows por rodada (mais `m` do lado dos destinos): polinomial.

Observação: o C3 **do lado das origens** é exatamente a projeção do modelo multicommodity por origem **sem** a restrição de atribuição (§9). O C3 do lado dos destinos corresponde, da mesma forma, à multicommodity por destino.

### 5.4 C4: Hall de primeiro salto (para o acoplamento; regime de terminais densos)

1. **RHS 1.** Para `S' ⊆ S∖T` com `|N⁺(S') ∩ T| < |S'|`: `Σ_{v ∈ N⁺(S')} y_v ≥ 1`. Os destinos de `N⁺(S')` entram também, porque podem ser relés.
2. **[Provado]** Pelo teorema de Hall nos arcos diretos, no máximo `|N⁺(S')∩T|` robôs de `S'` terminam em um salto. Os demais, pelo menos `δ(S') = |S'| − |N⁺(S')∩T| ≥ 1`, dão ≥ 2 saltos, e o primeiro ponto de parada deles é interior e está em `N⁺(S')`.
   - **Versão mochila:** `Σ_{v∈N⁺(S')} min(δ, |N⁻(v)∩S'|) y_v ≥ δ`. Cada estação `v` pode ser a primeira parada de no máximo `|N⁻(v)∩S'|` robôs de `S'`. O arredondamento dos coeficientes é válido para cobertura 0/1.
3. Elimina F2: com `S' = {a_j, b_j}`, dá `y_{c_j} + y_{x_j} ≥ 1`, e o LP passa a valer `k = OPT`.
4. **A priori, pela decomposição de Dulmage–Mendelsohn** [Provado]. Tome um emparelhamento máximo `M` do bipartido direto `B_∅`. Para cada origem `s₀` não emparelhada, seja `S'(s₀)` o conjunto de origens alcançáveis a partir de `s₀` por caminhos `M`-alternantes. Então `|N(S'(s₀))| = |S'(s₀)| − 1`, pois caso contrário haveria caminho aumentante. Isso gera `m − ν(B_∅)` cortes com Hopcroft–Karp; do lado dos destinos, o análogo. Em hc9u, `B_∅ = ∅` e esses cortes coincidem com C1.
5. **Separação dinâmica** [Provado para a redução; o resto é Hipótese].
   - *Redução:* se algum `S'` com `δ ≥ 1` viola o corte, existe `S'' ⊆ S'` com `δ(S'') = 1` que também viola. A cada remoção de uma origem, `δ` cai no máximo 1 (e pode subir) e `N⁺` só diminui. Como `δ(∅) = 0`, a sequência passa por um conjunto com `δ = 1` exatamente.
   - *Teste:* minimizar `g(S') = Σ_{v∈N⁺(S')} (y*_v + [v∈T]) − |S'|`. É um problema de fechamento/seleção num bipartido (Picard–Queyranne), resolvido por um corte mínimo. Se `min g ≥ 0`, nenhum corte está violado. Se o minimizador tem `δ = 1`, ele é um corte violado.
   - *Limite:* a separação exata com a restrição `δ ≥ 1` tem complexidade em aberto. Suspeito de NP-dificuldade, por analogia com corte mínimo com restrição de cardinalidade.
6. Portanto: teste polinomial suficiente; exatidão da separação em aberto.

### 5.5 C5: Hall geral multi-salto (família completa do Teorema 6)

- **Separação inteira** [Provado]. Com `y*` binário, calcule um max-flow em `N(y*)`. Se o valor é `< m`, o corte mínimo `X` tem `Z(X) ∩ C* = ∅`, o que dá o corte lazy `y(Z) ≥ 1`. É exata e polinomial, e **garante a exatidão** do branch-and-cut.
- **Fortalecimento de Z** [Provado quanto à validade]:
  - escolher entre o corte mínimo mais próximo de `σ` e o mais próximo de `τ`;
  - minimalizar `Z` de forma gulosa: para cada `v ∈ Z`, retirar `v` de `Z` se `V ∖ (Z ∖ {v})` continuar **inviável** (um max-flow por teste).
  - *Cuidado:* testar `C* ∪ {v}` no lugar de `V ∖ (Z ∖ {v})` gera cortes inválidos. Exemplo: `s–u`, `s–w`, `u–t`, `w–x`, `x–t`, com `m = 1`, `C* = ∅` e `Z = {u,w}`. O teste errado reduz `Z` a `{u}`, mas `V ∖ {u}` é viável.
- **Pacote de cortes disjuntos** [Provado]. Depois de obter `Z_1`, adicione `Z_1` a `C*` e repita. Os `Z_i` resultantes são disjuntos e todos válidos, e o número deles é um **limite inferior combinatório**.
- **Separação fracionária exata:** é um corte mínimo bicritério (peso `y*(Z)` sujeito a `k(X) ≤ m−1`). Complexidade em aberto; hipótese de NP-dificuldade (interdição de emparelhamento).
- **Heurísticas de separação fracionária:**
  - (i) Min-cut paramétrico com capacidades `λ y*` nos trânsitos e 1 nos arcos terminais, seguido de conferência `y*(Z) < 1` de cada corte encontrado.
    - Com `λ ≥ m`, todo corte `< m` já é violado, mas só aparecem violações com `y*(Z) < δ/λ ≤ δ/m`.
    - Com `λ < m`, a conferência a posteriori captura também casos com `y*(Z) ∈ [δ/m, 1)`. Exemplo: `m = 2`, separador único com `y* = 1/2`, detectado com `λ = 1`.
    - Varrer vários `λ` é uma heurística razoável, sem garantia de exatidão.
  - (ii) Limiar `C_θ = {v : y*_v ≥ θ}`: separação inteira em `C_θ`, aceitando o `Z` obtido se `y*(Z) < 1`.
  - (iii) Reaproveitar o pool de cortes lazy como user cuts.

### 5.6 C6: cortes de Hall com multiplicidade (versão mochila, lado origem e lado destino)

Servem quando `δ ≥ 2` robôs precisam sair por separadores distintos. A cobertura com RHS 1 não conta multiplicidade. É a correção natural da diferença entre cobertura e multicommodity discutida no §9. A separação é heurística, por DM e fechamento. [Esboço]

### 5.7 C7: posto ≥ 2 sobre as linhas de cobertura

Exemplo: Tri, com `y_a + y_b + y_c ≥ 2`. Separação por `{0,½}`-CG (zero-half) aplicada às linhas C1, C2 e C4. Com essas linhas explícitas no modelo, o solver as encontra sozinho [Hipótese].

### 5.8 C8: desigualdades em f e cotas locais (apenas se o modelo compacto for mantido)

- **Por arco:** `f_sv ≤ y_v + in(s)` e `f_ut ≤ y_u + out(t)` são válidas, mas o LP as contorna com circulações (P4). [Esboço]
- **Cota local** `κ_v = min(m, |S_v|, |T_v|)`, onde `S_v` são as origens que alcançam `v` em `A_r` e `T_v` os destinos alcançáveis a partir de `v`. Preserva o conjunto de `y` inteiros viáveis: todo `y` viável admite um fluxo acíclico que respeita `κ`. Não é válida para todo ponto inteiro `(f, y)` com ciclos. Só ajuda quando o alcance é restrito, e é inútil em hc9u, onde `S_v = S`. [Provado]

### 5.9 Desenhos de branch-and-cut

- **(BC-comp) Compacto com cortes.** Base (U), com `f` contínuo, mais C1, C2 e C4-DM a priori; separação de C3 e C4 na raiz como user cuts. É a mudança mínima e mantém `f` para extrair rotas. Não precisa de lazy cuts, porque as restrições de fluxo garantem a exatidão.
- **(BC-y) Branch-and-cut só em y.** O mestre tem `n` binárias.
  - A priori: C1, C2 e C4-DM.
  - User cuts: C3, C4 e **também os cortes clássicos fracos** `Σ κ_v y_v ≥ δ` nos pontos fracionários. Esses últimos são separáveis de forma exata por um max-flow com capacidades `κ y*`, e é a presença deles que garante raiz `≥ z_LP`. Cada um vem acompanhado da versão arredondada `y(Z) ≥ 1`.
  - Lazy: C5 inteiro, que garante a exatidão.
  - As rotas saem de um max-flow ao final.
  - Os nós são LPs muito menores.

**Atenção [Provado por contraexemplo].** Sem os cortes clássicos fracionários, o BC-y com apenas as famílias polinomiais pode ter raiz **abaixo de `z_LP`**. Instância, com `m = 3` e `r = 1`:
- arestas `s1–t1`, `s2–t1`, `s1–w1`, `s2–w1`;
- um caminho `w1 … wL`;
- arestas `wL–t2`, `t2–s3`, `s3–t3`.

Então `OPT = L = LP_cov` e `z_LP = L/3`. As famílias C1 e C2 ficam vazias, e C4-DM dá apenas `y_{t1} + y_{w1} ≥ 1` e `y_{wL} + y_{s3} ≥ 1`. A raiz fica em 2, que é menor que `z_LP` para `L ≥ 7`. O bound de BC-y é o da família efetivamente gerada: fica `≤ LP_cov` e só atinge `LP_cov` com separação exata.

A comparação entre os dois desenhos é o objeto da estratégia A2 (§13).

---

## 6. Benders

### 6.1 Componentes

- **Master:** `min Σ_v y_v`, `y ∈ {0,1}^V`, sujeito aos cortes gerados.
- **Subproblema SP(ȳ):** decidir se existe `f ≥ 0` com (B), (E) e (S). Pelo Teorema 3, isso é um max-flow `φ(ȳ)` em `N(ȳ)`, e SP é viável ⇔ `φ(ȳ) = m`.
- **Dual/certificado:** `φ(ȳ) = min_X [k(X) + Σ_{v∈Z(X)} κ_v ȳ_v]`. Os pontos extremos do dual de max-flow são cortes (vetores 0/1), e o certificado de inviabilidade é um corte `X` com capacidade `< m`.
- **Corte de Benders clássico (viabilidade):** `Σ_{v∈Z(X)} κ_v y_v ≥ δ(X)`. **Não há cortes de otimalidade**, porque todo o custo está no master e o subproblema só decide viabilidade.

### 6.2 Resultados

**Teorema 8 [Provado].** O conjunto de todos os cortes clássicos, com `y ∈ [0,1]`, é igual a `proj_y(LP base)` (Teorema 5). Logo **a relaxação linear do master com cortes clássicos nunca supera o LP compacto**.

*Ressalva.* Para `y` binário, `Σ_{v∈Z} κ_v y_v ≥ δ` é logicamente equivalente a `y(Z) ≥ 1`, porque `κ_v ≥ m−1 ≥ δ`, ou `δ = m` e `Z` não tem terminais. Portanto:
- o **MIP** do master pode ultrapassar `z_LP` durante a árvore;
- o presolve e o aperto de coeficientes do solver podem recuperar parte do arredondamento quando os cortes entram como linhas do modelo, algo a conferir no log;
- o defeito do corte clássico está na **relaxação linear**, que é o que guia a árvore, e não no conjunto de soluções inteiras.

A troca de espaço tem valor próprio: master pequeno e ramificação só em `y`.

**Benders combinatório (tipo Codato–Fischetti) [Provado].**
- Para `ȳ` inteiro inviável, o corte mínimo tem `Z ∩ C̄ = ∅` (prova do Teorema 6), e o corte combinatório é `Σ_{v∈Z(X)} y_v ≥ 1`.
- É o arredondamento CG do corte clássico (Teorema 7) e pertence à família exata `𝒵`.
- Comparado com o *no-good* `Σ_{v∉C̄} y_v ≥ 1`, também válido por monotonicidade, o corte combinatório é muito mais forte, porque `Z` é pequeno.

**Branch-and-Benders-cut.** É uma única árvore: lazy constraints nos nós inteiros (max-flow) e user cuts nos fracionários (C3, C4 e C5 heurístico). **Neste problema, isso coincide com o BC-y do §5.9.** A formulação correta é: *Benders combinatório ≡ branch-and-cut na reformulação de set covering.*

**Separação por max-flow.** Não é preciso resolver o LP dual. Um único max-flow, com reinício a quente, resolve a separação.

**Seleção de cortes.** Algumas opções:
- preferir `Z` minimais;
- entre os cortes mínimos de `ȳ`, escolher o de menor `Σ_{Z} y^{LP}_v` em relação a um ponto de referência (análogo aos cortes Pareto-ótimos de Magnanti–Wong);
- gerar vários cortes disjuntos por iteração (§5.5).

**Benders com subproblema multicommodity.** Os cortes resultantes são a projeção do LP multicommodity, e a separação exige um LP acoplado pela atribuição, não um max-flow só. Faz sentido apenas se o LP multicommodity se mostrar muito mais forte (§9). [Esboço]

### 6.3 Comparação com o modelo compacto

| | Compacto base | Benders clássico | Benders combinatório (BC-y) |
|---|---|---|---|
| Variáveis | `|A_r| + n` | `n` | `n` |
| Bound da relaxação | `z_LP` | `z_LP` (Teorema 8) | LP da família gerada: `≤ LP_cov`; `≥ z_LP` só se os cortes clássicos fracionários também forem separados (§5.9); `= LP_cov` só com separação exata |
| Exatidão | restrições de fluxo | cortes de viabilidade | lazy C5 por max-flow |
| Custo por nó | LP grande | LP pequeno + max-flow | LP pequeno + max-flow + separações |

---

## 7. Relaxação Lagrangeana

| Candidata | Restrições dualizadas | Subproblema | Propriedade de integralidade? | Bound | Veredito |
|---|---|---|---|---|---|
| **L1** | (E),(S) da base (multiplicadores `μ_v, ν_v ≥ 0`) | Fluxo de custo mínimo com custo `ν_u + μ_w` no arco `(u,w)`; parte em `y` separável, em forma fechada | Sim (TU + caixa) | `= z_LP` (Geoffrion) | **Descartar**: no máximo reproduz o LP [Provado]. É o que o repositório implementou |
| **L2** | (B) (multiplicadores livres) | Seleção de nós com capacidades de entrada/saída abertas por `y` e lucros nos arcos: *b-matching* bipartido com custo fixo nos nós | Não | Poderia superar o LP | **Descartar**: o subproblema não é mais simples e não tem algoritmo polinomial evidente [Hipótese] |
| **L3** | Ligação `out^s(v) ≤ y_v`, para `v ≠ s`, da multicommodity por origem (a forma `in^s(v) ≤ y_v` é **inválida** em destinos: no caminho `s–t` com `m = 1` ela forçaria `y_t = 1`) | `m` Dijkstras em `A_r` com custos `μ^s ≥ 0` nos nós + problema de atribuição (Húngaro) + `y` separável | Sim | `= LP multicommodity` | **B/C**: é só um meio de calcular em escala o bound multicommodity. Custo por iteração: `O(m·|A_r| log n + m³)`, cerca de `6·10⁸ + 1,1·10⁹ ≈ 1,7·10⁹` operações em `hc12p`, com a atribuição dominando |
| **L4** | Atribuição na multicommodity | Continua acoplado em `y` entre as origens: um problema do tipo "grupo Steiner" | — | — | **Descartar**: não fica mais simples |
| **L5** | Cortes de cobertura (relax-and-cut) | `y` separável | Sim | `= LP` da família dualizada | **C**: resolver o LP não é o gargalo com `n ≤ 17 mil` |
| **L6** | Existe relaxação sem a propriedade de integralidade e ainda tratável? | Decomposição espacial por regiões: sub-MIPs acoplados na fronteira | Não | Poderia superar o LP | Não encontrei nenhuma natural. **Conclusão: não há relaxação Lagrangeana natural que seja ao mesmo tempo mais simples e mais forte que o LP da formulação a que se aplica** |

"Lagrangeana + B&B" só faria sentido na forma L3, como substituta barata do LP multicommodity, e só se esse LP se provar muito mais forte (estratégia B1). O método recomendado para o dual é bundle; subgradiente com Polyak depende de um UB bem calibrado.

---

## 8. Dantzig-Wolfe / geração de colunas

### 8.1 Reformulação por rotas

- `P_s`: rotas de `s` até algum destino, com variáveis `λ_p ∈ [0,1]`.
- Master:
  - `min Σ_v y_v`;
  - `Σ_{p∈P_s} λ_p = 1`, para todo `s` (dual `α_s`);
  - `Σ_{p termina em t} λ_p = 1`, para todo `t` (dual `β_t`);
  - `Σ_{p∈P_s : v∈int(p)} λ_p ≤ y_v`, para todo par `(s,v)` (dual `γ_sv ≥ 0`).
- **Compartilhamento de estações:** o mesmo `y_v` limita **cada** origem separadamente. O custo compartilhado é representado pelo máximo sobre os robôs, e não pela soma. Por isso a ligação precisa ser **desagregada**. Com ligação agregada, `Σ λ ≤ m·y_v`, o LP do master volta a ser `z_LP`.

### 8.2 Pricing e branching

**Pricing [Provado].** O custo reduzido de `p ∈ P_s` que termina em `t` é `Σ_{v∈int(p)} γ_sv − α_s − β_t`. Para cada `s`, basta um Dijkstra com custos `γ ≥ 0` nos nós, e essa única execução serve para todos os `t`. Não há ciclos negativos. É polinomial.

**LP do master [Provado].** Pela equivalência entre caminhos e arcos por commodity, o LP do master é igual ao LP multicommodity por origem.

**Branching só em y [Provado].** Com `y` inteiro, a ligação força `λ_p = 0` sempre que `int(p) ⊄ C`. Então `z_st = Σ λ` define um emparelhamento perfeito fracionário em `B_C`, e o politopo de emparelhamento bipartido é inteiro. Logo **não é preciso ramificar em rotas**: basta um branch-and-price "leve", com ramificação em `y` e pricing que só remove vértices.

### 8.3 Alternativas de coluna

- **Conjuntos de estações:** o pricing seria o problema original. Descartar.
- **Padrões multi-robô:** também descartar. Os robôs só interagem pela atribuição e pelo compartilhamento, que o master já representa.

### 8.4 Avaliação

A decomposição por rotas é natural e o pricing é fácil, mas ela só produz o bound multicommodity. O master tem `m·n` linhas de ligação: 4 milhões em `hc12p`. Seria preciso gerar também as linhas de ligação dinamicamente. Classificação: **B/C**, condicionada ao resultado de B1.

---

## 9. Formulações alternativas

| Formulação | Variáveis (ordem) | Restrições | Força do LP | Geração dinâmica | Implementação | Escalabilidade |
|---|---|---|---|---|---|---|
| **F0: base (U)** | `|A_r| + n` (`f` pode ser contínuo) | `~3n` | `z_LP = W*/m` a menos de fator (Teorema 2) | não | existente | limitada por `|A_r|` |
| **F-a: só `y` + cobertura** | `n` | exponenciais (a priori C1/C2/C4-DM + dinâmicas) | `LP_cov ≥ z_LP`, até `m×` (Cor. 7.1), **se a separação for exata**; com famílias parciais pode ficar abaixo de `z_LP` (§5.9) | sim (lazy + user) | média (callbacks + max-flow) | boa: LP pequeno; `A_r` só no max-flow |
| **F-b: multicommodity por origem** (`x^s`, `z`, ligação forte `out^s(v) ≤ y_v`, `v ≠ s`) | `m·|A_r| + m² + n` | `~2mn` | forte só do lado das origens: em F1 vale `mk + k + 1` contra `OPT = 2mk + 1` (razão → 2); **fraca em F2** (`k/2`, exato) | não | simples | ruim: ~607 mil (hc9u), 2,4 milhões (Barcelona st_50 R6), 51 milhões (hc12p) |
| **F-b-cut: `y` + atribuição `z` + cortes por origem** | `n + m²` | exponenciais: `y(Z) ≥ Σ_{t∈T'} z_st` | `=` LP de F-b | sim (max-flow por origem com `z*_st` nos arcos até o sumidouro) | média | boa para `m ≤ ~100`; `m²` pesa em `hc12p` |
| **F-c: multicommodity por destino** | idem a F-b | idem | simétrica a F-b | — | — | — |
| **F-d: por par** | `m²·|A_r|` | — | ≤ F-b (ligação menos agregada por origem) | — | — | inviável: descartar |
| **F-e: desagregação parcial** (1º/último salto do próprio robô) | `≤ 2|A_r| + n` | `O(|A_r|)` | recupera C1 com acoplamento fraco; exposta a P4 | não | simples | média; dominada por F0 + C1 |
| **F-f: κ local no Big-M** | `|A_r| + n` | `~3n` | ganho só com alcance restrito | não | trivial | igual a F0 |
| **F-g: camadas de bateria** | `n(R+1)` nós, `|E|·R` arcos | — | mesma projeção de F0 [Esboço] | não | média | só ajuda com métrica em passos e `r` pequeno |
| **F-h: rotas (DW)** | colunas | `m·n` ligações | `=` F-b | sim (colunas) | alta | ver §8 |
| **F-i: atribuição `p_st` + cortes por par** | `n + m²` | exponenciais | ≤ F-b-cut (agrega menos) | sim | média | dominada por F-b-cut |
| **F-j: "cumulativa"** (repo) | — | — | não analisada nesta etapa, por instrução | — | — | resultado conhecido: hc9u 31/40 em 3600 s |

**Hierarquia de relaxações.**
- `z_LP(F0) ≤ LP_cov(F-a)` **[Provado]**.
- F-b com as linhas agregadas (E),(S) adicionadas domina F0, e isso é trivial.
  - Sem essas linhas, a F-b pode violar `in(t) ≤ 1 + (m−1)y_t` quando a atribuição é fracionária, então convém incluí-las.
- **A multicommodity por origem não domina a cobertura [Provado], por dois mecanismos distintos:**
  - **F2 (acoplamento de Hall).** O LP multicommodity vale exatamente `k/2`: com `y_x = 1/2`, cada um de `a_j` e `b_j` manda metade para `c_j` e metade via `x_j` para `d_j`, e em cada bolsão vale `2(y_x + y_c) ≥ 1`. Já `LP_cov = k`. A multicommodity só consegue dar `y(Z) ≥ δ/|S'|` nos cortes de Hall.
  - **F1 (lado dos destinos).** Com atribuição uniforme `z = 1/m`, cada vértice dos raios de destino fica com `y = 1/m`. O LP vale `mk + k + 1`, contra `LP_cov = OPT = 2mk + 1`.
  - Consequência: se a desagregação for usada, convém combinar commodities por origem e por destino, ou somar os cortes C3 dos dois lados.
- **A cobertura com RHS 1 não domina a multicommodity [Hipótese, mecanismo identificado].**
  - O mecanismo é: `δ ≥ 2` robôs precisam sair por separadores disjuntos, e nenhum robô é forçado individualmente. A multicommodity impõe `Σ_{s∈S'} y(Z_s) ≥ δ`, enquanto a cobertura impõe só `y(∪Z_s) ≥ 1`.
  - Tentei um exemplo com "saídas privadas", e ele **falhou**: na variante all-vertices, terminais com estação criam desvios baratos. Não tenho ainda um exemplo limpo.
  - A versão mochila (C6) é a correção natural.
- **Mais forte disponível:** F-a ∪ F-b-cut, isto é, `y` e `z` com cortes de cobertura e cortes por origem.

**Registro importante.** A única evidência multicommodity no repositório (`modelo_estendido.py`) usa `x` e `p` **binários** e está na **variante VI**, que é outro problema. O fracasso de tempo ali não diz nada sobre o LP multicommodity na variante all-vertices. Além disso, `x` e `p` podem ser contínuos sem perda (§8), o que já reduziria muito o modelo.

---

## 10. Pré-processamento e fixações

- **R1. Vértices irrelevantes [Provado].** Se `v ∉ RS ∩ RT` (`RS` = alcançáveis a partir de `S` em `A_r`, `RT` = que alcançam `T`), então `v` nunca é interior e pode-se fixar `y_v = 0`.
  - *Quando R1 é vazia:* com `G` não direcionado **e todo peso de aresta ≤ r**, vale `A_r ⊇ E`, então `A_r` é simétrico e fortemente conexo e `RS = RT = V`.
  - *Quando R1 atua:* com arcos de mão única, ou com arestas de peso maior que `r`. Exemplo: `a–b` com peso 1, `b–c` com peso 3 e `r = 2` deixam `c` isolado em `A_r`. O critério correto é que `A_r` é conexo ⇔ o subgrafo das arestas com `w_e ≤ r` é conexo. Isso é relevante para as instâncias ponderadas (TNTP, `cc12-2u`).
- **R2. Obrigatórios [Provado].** `v` é obrigatório ⇔ `V∖{v}` é inviável (um max-flow por candidato), e então fixa-se `y_v = 1`. Generalização para pares: se `V∖{u,v}` é inviável, então `y_u + y_v ≥ 1` (cobertura de tamanho 2 a priori), mas isso custa `O(n²)` max-flows e deve ser restrito às vizinhanças dos terminais. Hipótese: os "separadores obrigatórios" do repositório são um caso particular de R2. O código não foi relido nesta etapa.
- **R3. Dominância [Provado].** Se `u ∉ C`, `N⁻(v)∖{u} ⊆ N⁻(u)` e `N⁺(v)∖{u} ⊆ N⁺(u)`, então `C' = C − v + u` é viável.
  - *Prova:* troque cada trecho `x → v → w` por `x → u → w`. Se `x = u` ou `w = u` (terminal), use o atalho `u → w` ou `x → u`, e remova repetições.
  - Se `v` é terminal, o papel dele como terminal não se altera.
  - Logo existe ótimo com `y_v = 0`.
  - **Aplicação em lote:** deve ser sequencial, recalculando as vizinhanças sobre os pontos de rota ainda utilizáveis. Aplicar tudo ao mesmo tempo a gêmeos (`N^±(u)∖{v} = N^±(v)∖{u}`) pode remover os dois, o que é **inválido**. Mantenha um representante por classe de gêmeos, o que também quebra simetria.
  - Um vértice dominado nunca é obrigatório, então R2 e R3 são consistentes.
  - O dominador `u` precisa estar livre, isto é, não pode ter sido fixado em 0 por outra regra.
- **R4. Arcos [Provado].**
  - Podem ser removidos: arcos incidentes a vértices irrelevantes (R1) e arcos que usam como ponto de passagem um não terminal fixado em 0.
  - **Não** podem ser removidos: arcos que entram em origens ou saem de destinos, a menos que o terminal esteja fixado em `y = 0` (contraexemplo C1 do relatório de validação).
  - **Não** existe redução transitiva válida: remover `(u,w)` quando existe `u → v → w` obrigaria a instalar uma estação em `v`.
- **R5. Monotonicidade em r [Provado].** Para `r ≤ r'`, `A_r ⊆ A_{r'}`, então viáveis(`r`) ⊆ viáveis(`r'`). Consequências:
  - `OPT(r') ≤ OPT(r)`;
  - soluções para `r` são pontos de partida viáveis para `r'`;
  - obrigatórios em `r'` são obrigatórios em `r`;
  - **cortes válidos em `r'` são válidos em `r`.**

  Numa varredura de `R` como a do repositório: os cortes passam de `R` maior para menor, e os incumbentes de `R` menor para maior.

  **Ressalva:** fixações que dependem de otimalidade (dominância R3, custo reduzido R7, quebra de simetria) **não** são desigualdades válidas e não se transferem entre valores de `r`.
- **R6. Limites combinatórios antes do solver [Provado].**
  - `L_bot` (atribuição gargalo em `h*`);
  - `max_s (⌈D_s/r⌉ − 1)` (bandas);
  - número de conjuntos C1/C2 disjuntos (empacotamento);
  - número de cortes disjuntos do §5.5;
  - `⌈LP(C1)⌉`, que em hc9u dá **29**.
- **R7. Fixação por custo reduzido [Provado, padrão].** Após um LP forte, se `LB + rc_v > UB − 1`, fixa-se `y_v = 0`. É válido porque o objetivo é inteiro.
- **R8. Poda de componentes pendentes sem terminais [Provado].** O argumento vale para a componente inteira, **não vértice a vértice**. Um vértice interno `q` pode ser vizinho de `p` sem ser vizinho de `a`. Exemplo: `a–p–q` com `r = 1`.
  - *Prova.* Seja `K` uma componente de `G − a` sem terminais (árvore pendente ou qualquer outro caso). Toda rota que entra em `K` entra e sai pelo vértice de ligação `a`. Troque cada trecho maximal da rota dentro de `K` por uma parada em `a`: pela desigualdade triangular, `d(x,a) ≤ d(x,p₁)` e `d(a,w) ≤ d(p_k,w)`. As estações em `K` são substituídas por no máximo uma estação em `a`.
  - Remover `K` preserva as distâncias entre os demais vértices, também com métrica ponderada.
  - Alternativa equivalente: remover folha por folha, em sequência, usando o pai como dominador (R3).
- **R9. Decomposição.** Se todo peso de aresta for `≤ r`, então `A_r ⊇ E` e `A_r` é conexo, sem decomposição trivial. Com arestas de peso maior que `r`, `A_r` pode se partir em componentes. Nesse caso:
  - cada componente precisa ser balanceada (`|S∩K| = |T∩K|`), senão a instância é inviável;
  - se todas forem, as componentes podem ser resolvidas independentemente.

  Não encontrei regra geral de decomposição por separadores: o emparelhamento acopla as regiões.

---

## 11. Heurísticas para auxiliar métodos exatos

Critério de seleção: só heurísticas estruturalmente justificadas, e nenhuma delas afeta a exatidão.

- **H1. Incumbente pelo fluxo de custo mínimo.** Calcule o fluxo mínimo de `W*` e tome a união dos interiores: `UB ≤ W*`. O vértice do LP devolvido pelo solver pode ter `f` fracionário, então convém resolver esse fluxo à parte, o que é barato.
- **H2. Repesagem para induzir compartilhamento.** Justificativa: o LP ignora o compartilhamento (2.2a). Repita um fluxo de custo mínimo com custo de nó igual a 0 para as estações já escolhidas e igual a 1 para as demais, até estabilizar, como nas heurísticas de caminho mínimo para Steiner.
- **H3. Aumento guloso de emparelhamento.** Parta de `C = ∅` (mais os obrigatórios) e adicione o `v` que mais aumenta `ν(B_C)`; cada avaliação é um max-flow. É adequada ao regime de terminais densos, que tem estrutura de cobertura.
  - *Limitação:* H3 fica sem sinal quando nenhum vértice sozinho aumenta `ν`. Exemplo: `s–u1–u2–t` exige `u1` e `u2` juntos.
  - *Correção:* desempatar pela redução da distância em saltos (`h*`) ou pelo número de cortes C1/C4 cobertos.
- **H4. Remoção reversa.** Retire estações enquanto a solução continuar viável, testando com max-flow. O resultado é uma solução minimal. Deve ser aplicada a todo incumbente.
- **H5. Arredondamento do LP de cobertura.** Limiar, reparo guloso e depois H4.
- **H6. Busca local drop/add/swap** com oráculo de max-flow incremental, como callback de heurística.
- **H7. Fix-and-optimize por regiões** (bandas ou vizinhanças), usando sub-MIPs.
- **H8. Continuação em r (R5).** Incumbentes de `r` servem como ponto de partida em `r' > r`, seguidos de H4.

O primal não parece ser o gargalo nas instâncias médias; o dual é. Nas grandes (`hc12p`: UB 308 contra LB 149, com um único nó explorado), as duas coisas pesam [Evidência].

---

## 12. Análise das tentativas existentes no repositório

Baseada apenas no que já foi lido. As partes não analisadas estão indicadas.

| Tentativa | Ideia matemática | Bound produzido [Evidência] | Diagnóstico: técnica ou implementação? | Variante que ainda vale testar |
|---|---|---|---|---|
| Baseline all-vertices (`results/results_min_station_das.csv`, logs `min_station_das_*`) | F0 compacta, `f` inteiro | Raiz pós-presolve: hc9u 1,0; hc10–12p 1,0; bip42p 1,0; w23c23 1,07; lin23 1,12; cc10-2u 0,149; Barcelona st_15 R5 3,47, st_25 R5 2,08, st_50 R6 0,40; Philadelphia st_25 R3 3,28 | Coerente com o Teorema 2: **a fraqueza é da formulação, não da implementação** | F0 com `f` contínuo e cortes C1/C2/C4 (A1) |
| Variante VI (`results_final_*.csv`, `hc9u_log.txt`) | Outro problema: estações só em VI | hc9u: raiz **32** após presolve; 36/38 em 8000 s | O presolve recupera a força por causa das cotas `f ≤ 1` (§2.9). **Não comparar com all-vertices** | — |
| Benders (`benders_min_station.py`) | Benders clássico: corte de min-cut com coeficientes `m − base`, sem arredondamento (l. 467–506, 827–832); mestre MIP re-resolvido a cada iteração com 10 s; cortes iniciais C1 limitados a 80; remove `S∩T` | Não encontrei resultados deste script | **Técnica mal escolhida:** a relaxação linear do mestre com cortes clássicos não passa de `z_LP` (Teorema 8). Com `y` binário, os cortes são logicamente equivalentes a `y(Z) ≥ 1`, então o problema está na relaxação que guia a árvore do mestre. O re-solve do mestre desperdiça trabalho, e o limite de 80 corta a família C1 (hc9u precisa de 256) | Benders combinatório `y(Z) ≥ 1` em callback lazy + C1/C2 completos = BC-y (A2) |
| Lagrangeano (`lagrangeano_min_station.py`, `p_relaxation*`, bundle, subgradiente) | L1: ativações dualizadas por vértice (alpha/beta); subproblema de fluxo + `y` separável | Todos ≤ LP: hc9u 0,997; bundle bip42p 0,959; subgradiente 0,54–0,89 contra LP 1,0; cc10-2p 0,012 contra 0,149. UB manual igual a 42 no passo de Polyak na maioria das execuções, inclusive em instâncias cujo UB real é muito diferente | **A limitação é da técnica aplicada a essas restrições** (integralidade ⇒ `≤ z_LP`). O UB fixo é um defeito adicional de implementação, mas mesmo uma convergência perfeita daria 1,0 | Só L3 (ligação multicommodity), e só se B1 justificar |
| Kelley no dual lagrangeano (log `original_benders_all_vs_lp`) | Planos de corte no dual de L1 | LB 0 contra LP 1 | Mesma limitação teórica de L1, e o script está ausente | — |
| Cortes "u2_violacao_diversidade" (script ausente) | Cortes de cobertura/violação, **no máximo 30** | Raiz: hc9u 1,0→4,8; hc10p 1,0→5,75; Barcelona st_25 1,12→4,15 (resolve em 190 s, contra 270–310 s); Philadelphia st_25 R3 2,32→9,4 | **O limite está na implementação** (teto de 30 cortes), não na técnica: cerca de +0,13 de bound por corte em hc9u | A1 com as famílias completas |
| Cortes "camadas" (script ausente) | Provavelmente bandas/primeiro salto por origem (128 = `m`) [Hipótese] | hc9u: raiz **24,03**, mas final 31/42, igual ao baseline | A raiz melhora 24×, mas a árvore não fecha mais em 3600 s. A dificuldade restante parece ser o núcleo de cobertura e a simetria [Hipótese] | Acrescentar o lado dos destinos, zero-half sobre a cobertura, BC-y e quebra de simetria (A2, B2) |
| Cortes "hall_capacity" (script ausente) | Cortes de Hall com capacidade | Ganho de raiz **0** | Coerente com o Teorema 5: qualquer corte da forma `Σ κ y ≥ δ` já está implicado pelo LP base. **Provavelmente faltou o arredondamento (Teorema 7)** [Hipótese] | Versão arredondada `y(Z) ≥ 1` (C4/C5) |
| MIP start (`results_base_mipstart.csv`) | Incumbente inicial igual a 42 | 31/42 | O incumbente não ajuda o bound, como esperado | — |
| Multicommodity estendida (`modelo_estendido.py`) | F-b com `x` e `p` binários, **variante VI** | Até 2,4 milhões de variáveis; raiz não termina; pior que o baseline VI em 1200 s | Problema diferente e tamanho inflado por binárias desnecessárias | F-b-cut (`y`, `z` contínuo, cortes por origem) na variante all-vertices (B1) |
| Pré-processamento (`preprocessamento/`) | Folhas, alcance RS/RT, arcos forçados a zero, dominância Pred/Succ, separadores obrigatórios | Único dado lido: Barcelona st_25 R5 com candidatos 930→914 e raiz inalterada (2,08); st_50 com 930→923 e raiz 0,40 inalterada | Reduz tamanho e não mexe no bound, como a teoria prevê (§10). **CSVs dos experimentos não analisados, por instrução** | R2, R5, R6 e R7, que atacam o bound ou a varredura em `R` (B4) |
| Formulação cumulativa (`cumulativo_min_station.py`) | Não analisada | hc9u 31/40 | — | — |

**Divergências registradas:**
1. os `results_final_*.csv` são da variante VI;
2. os scripts de "diversidade", "camadas" e "hall_capacity" não estão no repositório, então esses resultados não são reprodutíveis;
3. o Benders remove `S ∩ T` (pré-processamento provado inválido, CE1' de `validacao-formulacao-base.md`); script histórico, fora de uso, não corrigido nesta rodada;
4. ~~`base-formulation.md` §10.1 trata a variante U como "não adotada", mas parte do código já a implementa~~ — **resolvida na rodada E5**: `baseline.py` adotou a variante U (Q1 fechada em `open-questions.md`), e `base-formulation.md` §10.1 já reflete isso.

---

## 13. Ranking das linhas de pesquisa

Cada linha segue a cadeia **propriedade → problema observado → técnica → por que pode funcionar → como testar**.

### Prioridade A

**A1. Cortes de cobertura a priori na projeção sobre y** (C1 primeiro/último salto, C2 bandas, C4 via DM), somados à base com `f` contínuo.
- **Propriedade:** a viabilidade é um set covering (Teorema 6), e o LP só enxerga `δ/m` de cada corte (Teorema 5).
- **Problema observado:** raiz de ≈ `W*/m`, que vale 1,0 em hc9u contra LB de 31.
- **Técnica:** arredondamento CG explícito (Teorema 7) das famílias separáveis em tempo polinomial.
- **Por que pode funcionar:** famílias F1 e F2 (gap fechado por completo), hc9u (≥ 28,44 garantido), "camadas" com raiz 24,03 e "diversidade" com cerca de +0,13 por corte.
- **Como testar:** §14 E1 e §15.

**A2. Branch-and-cut só em y** (Benders combinatório / branch-and-Benders-cut): lazy C5 por max-flow, user cuts C3 e C4, famílias a priori de A1.
- **Propriedade:** `f` é só um certificado (Teorema 3 e Prop. 3.2), e o Benders clássico não passa de `z_LP` (Teorema 8).
- **Problema observado:** o modelo compacto é grande (até 2,8 milhões de colunas), degenerado em `f`, e a árvore estagna (hc9u 31 em todas as variantes testadas).
- **Técnica:** mestre em `y`, cortes combinatórios, separação por max-flow.
- **Por que pode funcionar:** o bound se aproxima do da cobertura na medida em que a separação é completa, e os cortes clássicos fracionários garantem pelo menos `z_LP`. Os nós são LPs de `n` variáveis e a ramificação é só em `y`. No regime R-c, dá para evitar materializar `A_r` fora do max-flow.
- **Como testar:** §14 E2.
- **Resultado [E7] — suspenso, não decide A2.** BC-y completo (MIP start guloso + lazy 𝒵 no
  MIPSOL + user cuts fracionários no MIPNODE) testado contra o compacto+A1 (COMP) em 7 instâncias,
  TL=300s cada. BC-y não superou o COMP em LB final nem em tempo até o ótimo em nenhuma das 7. Uma
  revisão posterior encontrou três confundidores que invalidam o experimento como medida do
  método: (1) BC-y recebeu só C1 estático, COMP recebeu C1+C2+C4 — o critério de abandono abaixo
  exige "os mesmos cortes de A1" nos dois lados, o que não aconteceu; (2) o MIP start podia
  devolver `y` sem viabilidade garantida, então "sem incumbente" em R-a pode ser artefato do
  start, não do método; (3) o separador não tinha guarda de tempo e reconstruía a rede inteira a
  cada chamada, o que fez o `TimeLimit` estourar 5× em cc12-2p e deixou o callback consumir
  70–99,9% do tempo em toda a bateria. Por isso a questão sobre A2 **não está decidida** — nem no
  sentido de abandono (critério abaixo não foi testado em base justa) nem no de "inconclusivo por
  callback caro" (o callback caro é ele próprio um dos confundidores, não uma medida limpa do
  método). Detalhes em `resultados-e7-pli.md` §5.1. O E8 (`plano-experimentos-e8` no plano de
  execução) refaz a comparação com os mesmos cortes estáticos, um MIP start sempre viável e um
  oráculo com guarda de tempo — só depois disso o critério de abandono desta seção se aplica.
- **Resultado [E8] — critério aplicado: A2 continua, mas o escopo proposto está sob suspeita
  (ver benchmark-v1).** Comparação com mesmos cortes, mesmo start primal e mesmo TL (300 s, uma
  seed). R-a (TNTP): o compacto vence em UB e LB nas quatro instâncias; BC-y e CBI não saem do UB
  do primal. R-b/R-b': LB empata em hc9u (32) e o CBI dá o melhor LB em hc10p (53 vs. 52) e
  bip42p (35 vs. 33); UB melhor no compacto. R-c: CBI prova OPT(cc12-2p)=6 em 7,5 s, BC-y em 292 s,
  e o compacto não prova. Proposta a decidir: seguir A2 só fora de R-a, com o CBI (mestre exato
  iterado) como variante principal. Ver `resultados-e8-pli.md`.
  **Ressalva [benchmark-v1, 2026-09-26]:** as quatro instâncias que sustentam "compacto vence em
  R-a" são TNTP — extensão ponderada e dirigida, terminais em folhas, e três das sete instâncias
  TNTP do projeto são triviais (r ≥ λ\*, logo OPT = 0; ver `benchmark-v1.md` §5). A instância que
  sustenta "CBI vence em R-c" é `cc12-2p`, extensão ponderada. Nas 70 instâncias do benchmark-v1,
  fiéis a Das, o regime R-c não produz nenhuma instância difícil (17 de 19 resolvidas em ≤ 60 s,
  as outras 2 em ≤ 600 s) — o regime em que o CBI venceu não se reproduz no problema de Das. As
  instâncias R-a do benchmark-v1 (MAPF, Vienna, PUCN) têm caráter muito diferente das TNTP e ainda
  não foram testadas com os três métodos. **A proposta de recorte de escopo ("A2 só fora de R-a")
  fica suspensa até um veredito refeito sobre o benchmark-v1 (E12, `plano-pos-e8-adiado.md`)** —
  mesmo status de suspensão que o E7 teve até o E8.
- **Evidência [E9], sem veredito.** Nas instâncias D/A do benchmark-v1 (fiéis a Das), o IP do
  núcleo em espaço-y (C1+C2+C4, TL 60 s) dá LB maior que o COMP após 600 s de B&B em 6 instâncias,
  todas das famílias PUC/PUCN: bip42p (×2) 35 vs. 33, hc10p 54 vs. 52, hc11p 97 vs. 95,
  pucn-cc3-10n 18 vs. 17, pucn-cc7-3n-regiao 10 vs. 9. Em MAPF e Vienna ocorre o contrário (o LB do
  COMP fica acima do núcleo), sinal de que ali o acoplamento de fluxo pesa. Coerente com o E8
  (melhor LB do CBI em hc10p e bip42p). Não decide A2 — não é o CBI completo —, mas define o
  subconjunto em que o E12 deve rodar primeiro. Ver `resultados-e9-e10-pli.md`.
  - *Ressalva de precisão [revisão E10b].* As margens são de 1 a 2 estações e `generate_C4_DM` não
    é determinística entre processos (percorre `set`s antes do emparelhamento máximo, que não é
    único), o que move o LB do núcleo em ±1 na mesma instância. Os cortes permanecem válidos, então
    a leitura qualitativa — núcleo competitivo em PUC/PUCN, não em MAPF/Vienna — se sustenta; os
    valores individuais, não. Das 6, só `pucn-cc3-10n` foi verificada estável (18 em 6 execuções).
    Corrigir o determinismo é pré-requisito do E12, cujo critério decide por 1 estação.

### Prioridade B

- **B1. Relaxação multicommodity em forma de cortes (F-b-cut).** `y` e `z` contínuo, com cortes por origem.
  - *Propriedade:* desagregação por origem.
  - *Problema:* a cobertura com RHS 1 não conta multiplicidade (C6).
  - *Teste:* comparar o LP de F-b-cut com `LP_cov` em instâncias pequenas e médias.
  - *Por que é B:* a teoria mostra que as duas relaxações são incomparáveis; o ganho real é empírico.
- **B2. Núcleo de cobertura e simetria** no regime de terminais densos — **encerrada na rodada E5, com evidência.**
  - *Técnicas testadas:* fixação orbital na raiz (1 variável, grupo vértice-transitivo), representante de gêmeos (R3), parâmetro `Symmetry=2` do Gurobi.
  - *Evidência [E5]:* hc9u–hc12p são hipercubos `Q_k` com `S ∪ T` = classe par inteira (verificado por medição, `verify_structure.py`); o grupo relevante (translações pares + permutações de coordenadas) é vértice-transitivo, então fixação orbital elimina só 1 variável; a assinatura por linha C1 é única para cada variável (0 classes de gêmeos com mais de 1 elemento em hc9u–hc12p); `Symmetry=2` empatou com o padrão do solver.
  - *Achado que fecha a linha:* o núcleo de cobertura (C1+C2+C4-DM) de hc9u resolve na otimalidade em 2,1 s (E3) com OPT(núcleo)=32. Uma solução ótima do núcleo testada no modelo compacto é **inviável** (max-flow=108 < m=128). Isso mostra que aquela solução particular não resolve o problema real — o núcleo pode ter outras soluções de 32 estações não testadas; **OPT(hc9u) ∈ [32, 38] segue aberto**. O que é claro: o gap está em restrições de acoplamento de fluxo que C1 não captura (em hc*, C2=C4=C1), logo qualquer reforço do núcleo (zero-half, mochila C6) não move o LB e não fecha a instância. A família 𝒵 (Teorema 6), separada por max-flow, é o passo natural. Isso promove **A2** sobre B2 nesse regime.
- **B3. `f` contínuo + prioridade de ramificação em `y`** na formulação compacta.
  - *Propriedade:* Prop. 3.2.
  - *Por que é B:* é barato e serve também como controle experimental de A1 e A2; o efeito no B&B é empírico.
- **B4. Pré-processamento que ataca o bound ou a varredura em R:** R2 (obrigatórios por max-flow), R5 (cortes e incumbentes entre valores de `R`), R6 (limites combinatórios), R7 (custo reduzido após LP forte) e gêmeos.
- **B5. Heurísticas primais estruturais:** H2, H3 e H4, sobretudo para instâncias grandes (`hc11p`, `hc12p`), onde o UB está longe.
- **B6. L3 ou DW por rotas,** apenas se B1 mostrar que o LP multicommodity é bem maior que o de cobertura e grande demais para resolver diretamente.
- **B7. Geração preguiçosa de A_r no regime R-c.** Calcular arcos só a partir de `S ∪ C̄` durante a separação inteira. `OPT` é pequeno nesse regime, o que torna a ideia promissora [Hipótese].

### Prioridade C

- **C-1. κ local no Big-M (F-f):** só ajuda com alcance restrito.
- **C-2. Grafo em camadas de bateria (F-g):** mesmo LP; só reduz tamanho com métrica em passos e `r` pequeno.
- **C-3. Desigualdades por arco e desagregação parcial (F-e, C8):** o LP as contorna com circulações (P4).
- **C-4. Benders com subproblema multicommodity:** B1 obtém o mesmo bound de forma mais barata.
- **C-5. Relax-and-cut (L5):** resolver o LP não é o gargalo.

### Descartar por enquanto

- **D-1. Lagrangeana dualizando ativações da base (L1) e suas variantes de subgradiente, bundle e Kelley:** bound `≤ z_LP` (Geoffrion), confirmado pelos resultados do repositório.
- **D-2. Benders clássico com cortes não arredondados como meio de melhorar o bound:** `= z_LP` (Teorema 8).
- **D-3. Lagrangeana dualizando o balanço (L2) ou a atribuição (L4):** os subproblemas não ficam mais simples.
- **D-4. Multicommodity compacta com `x` e `p` binários:** o tamanho proíbe, e as binárias são desnecessárias; substituir por F-b-cut.
- **D-5. Colunas de "conjuntos de estações":** o pricing seria o problema original.
- **D-6. Pré-processamento "robô em S∩T fica parado":** inválido (relatório de validação).

### Detalhamento das estratégias A

#### A1: cortes de cobertura a priori

- **Hipótese.** A projeção da base sobre `y` admite famílias de cobertura calculáveis em tempo polinomial (C1, C2, C4 via DM) que eliminam o padrão de diluição `y = τ/m`. Somadas à base, elas levam a raiz de ≈ `W*/m` para perto do melhor LB conhecido nos três regimes.
- **Fundamento.** Teoremas 2 e 5–7 e o Corolário 7.1. Em F1 e F2 o gap fecha por completo. Em hc9u, o bound é ≥ 256/9 (contra 1,0). Evidências parciais: "camadas" (24,03) e "diversidade" (ganhos limitados pelo teto de cortes).
- **Formulação.** Base (U) com `f ≥ 0` contínuo, mais:
  - C1: `Σ_{v∈N⁺(s)} y_v ≥ 1` e `Σ_{v∈N⁻(t)} y_v ≥ 1` para terminais sem terminal oposto a um salto;
  - C2: `Σ_{a<d(s,v)≤a+r} y_v ≥ 1` para `a = 0, r, 2r, …` com `a + r < D_s`, e o análogo para destinos;
  - C4-DM: `Σ_{v∈N⁺(S'(s₀))} y_v ≥ 1` para cada origem `s₀` não emparelhada em `B_∅`, e o análogo para destinos.
- **Experimento mínimo.** Resolver somente LPs e a raiz do solver, sem árvore, em uma a três instâncias por regime (hc9u, bip42p, w23c23; Philadelphia st_25 R3, Barcelona st_25 R5 e st_50 R6, Chicago st_15 R7; cc10-2u R4, lin23 R500). Medir a raiz em cinco configurações:
  - (a) `z_LP`;
  - (b) + C1;
  - (c) + C2;
  - (d) + C4-DM;
  - (e) + C3 separado iterativamente por max-flow.
- **Baseline.** Mesma instância, mesma formulação (U) sem os cortes, mesma versão do solver, threads e seed. Referências: a raiz do solver na base (presolve + cortes do Gurobi), o melhor LB conhecido e o ótimo quando conhecido (Barcelona st_15 R5 = 15, st_25 R5 = 16, Chicago).
- **Métricas.**
  - LP puro e raiz do solver;
  - root gap: `(UB_ref − raiz)/UB_ref`;
  - fração do gap fechado: `(raiz_nova − raiz_base)/(LB_ref − raiz_base)`;
  - tempo de raiz;
  - número de cortes por família e tempo de geração;
  - linhas, colunas e não zeros.
- **Critério de abandono.** Abandonar se, em pelo menos dois dos três regimes, as famílias a priori mais C3 fecharem menos de 20% do gap entre a raiz do solver na base e `LB_ref`, ou se a raiz do solver na base já alcançar esses valores com os cortes internos dele.

#### A2: branch-and-cut só em y

- **Hipótese.** Considere um B&C só em `y` com:
  - as famílias de A1;
  - cortes lazy `y(Z) ≥ 1` por max-flow;
  - user cuts C3/C4;
  - cortes clássicos fracionários com a versão arredondada, que garantem raiz `≥ z_LP` (§5.9).

  Ele obtém LB final maior e/ou tempo menor que a formulação compacta com os mesmos cortes, por três motivos: nós menores, ramificação só em `y` e ausência de degenerescência em `f`.
- **Fundamento.** Teoremas 3, 6, 7 e 8; integralidade do emparelhamento (§8); evidência de estagnação da árvore compacta (hc9u em 31 em todas as variantes).
- **Formulação.**
  - Mestre: `min Σ y` com as famílias de A1.
  - Lazy: para `ȳ` inteiro, max-flow em `N(ȳ)`; se o valor é `< m`, `Z` minimal e o corte `y(Z) ≥ 1`.
  - User: C3 (max-flow por robô), C4 (fechamento) e cortes clássicos fracionários (max-flow com capacidades `κ y*`) com a versão arredondada.
  - Rotas extraídas por max-flow ao final.
- **Experimento mínimo.** Duas instâncias já resolvidas pelo baseline, para validar a exatidão com o mesmo ótimo (Barcelona st_25 R5 e Chicago st_15 R9), mais duas não resolvidas (hc9u e Philadelphia st_25 R3). Mesmo tempo limite do baseline.
- **Baseline.**
  - (a) Base (U) pura, para comparar com o histórico;
  - (b) **base (U) com os mesmos cortes de A1.** É a comparação decisiva, porque isola o valor da decomposição do valor dos cortes.
- **Métricas.** Todas as de A1, mais:
  - número de nós;
  - tempo total;
  - primal e dual final;
  - gap final;
  - número de cortes lazy e de user cuts;
  - tempo de max-flow por chamada e número de callbacks.
- **Critério de abandono.** Abandonar se, nas quatro instâncias, o B&C em `y` não superar (b) em LB final nem em tempo até o ótimo, ou se a quantidade de cortes lazy crescer sem melhora de bound (por exemplo, mais de 10⁵ cortes com LB estagnado). Nesse caso, fica a formulação compacta com os cortes de A1.
  - **[E7]** Não aplicável ainda: o experimento não comparou "base (U) com os mesmos cortes de
    A1" nos dois lados (BC-y rodou só com C1). Ver nota de suspensão no bullet de A2 acima (§13)
    e `resultados-e7-pli.md` §5.1. Este critério se aplica ao E8, não ao E7.
  - **[E8]** Não satisfeito, logo A2 não é abandonada: em cc12-2p o CBI chega ao ótimo e o
    compacto não, e o CBI tem LB maior em hc10p e bip42p. Em R-a o B&C em y não supera o compacto
    em nenhuma instância (`resultados-e8-pli.md`).

---

## 14. Experimentos recomendados (sequência incremental)

1. **E0. Controle.** Base (U) com `f` inteiro contra `f` contínuo (B3), no mesmo ambiente. Registrar LP puro, raiz do solver, nós, tempo e gap. Todos os experimentos seguintes usam esse registro. Custo: baixo.
2. **E1 (A1). Somente raiz**, com as configurações (a) a (e) acima. Adicionalmente, calcular os limites combinatórios R6 (`L_bot`, bandas, empacotamentos). Custo: só LPs.
3. **E1'. Testes unitários de bound** nas famílias sintéticas F1, F2 e Tri, e na instância do §5.9 (em que o BC-y sem cortes clássicos fica abaixo de `z_LP`). Os valores `OPT`, `z_LP` e `LP_cov` previstos neste documento servem de gabarito para a implementação dos cortes.
4. **E2 (A2).** BC-y contra compacto com cortes, com o desenho de A2.
5. **E3 (B1).** LP de F-b-cut contra LP de cobertura, nas mesmas instâncias de E1. O resultado decide se B6 (L3/DW) vale o investimento.
6. **E4 (B2).** Zero-half/CG, mochila C6 e simetria nas instâncias densas (hc9u, bip42p, w23c23).
7. **E5 (B4 e B5).** Obrigatórios, varredura em `R` com reaproveitamento de cortes e incumbentes, e heurísticas H2–H4 no melhor pipeline.
8. **E6 (B6/B7).** Só se E3 indicar ganho; e, no regime R-c, geração preguiçosa de `A_r`.

Todos os experimentos devem registrar commit, instâncias, convenção de distância, versão do solver, threads, seed, tempo limite e formulação exata, conforme Q6.

---

## 15. Próxima hipótese a testar

**Hipótese escolhida (E1).** Três famílias polinomiais da projeção sobre `y`, adicionadas a priori ou separadas por max-flow:
- primeiro e último salto (C1);
- bandas de distância (C2);
- Hall de primeiro salto via Dulmage–Mendelsohn (C4).

Afirmo que elas levam a raiz da formulação base (U) de ≈ `W*/m` para uma fração substancial do melhor LB conhecido, com fechamento de pelo menos 20% do gap da raiz em pelo menos dois dos três regimes. Previsão já garantida pela teoria: hc9u ≥ 28,44 (contra 1,0).

**Por que esta é a hipótese de maior informação por menor custo:**
1. **Testa o diagnóstico central do estudo.** O LP presume compartilhamento perfeito (Teorema 2), o Big-M enfraquece cada corte para `δ/m` (Teorema 5) e o arredondamento o recupera (Teorema 7). Se a hipótese falhar nas instâncias reais, a agenda muda de direção.
2. **É barata.** Exige só BFS/Dijkstra, Hopcroft–Karp e alguns max-flows para montar as linhas, e depois LPs. Não precisa de callbacks, de árvore nem de nova formulação.
3. **Discrimina os regimes.** Mostra onde o gap é de conectividade (C1/C2/C3), onde é de acoplamento de Hall (C4) e onde sobra algo que exige posto 2 ou multicommodity (B1, B2).
4. **Condiciona tudo o que vem depois.** A2 só vale se A1 levantar a raiz; B1 só vale se sobrar gap que as coberturas não explicam.
5. **O fracasso também é informativo.** Se C1–C4 fecharem pouco no longo curso, o gap residual está no Hall multi-salto (C5 fracionário) ou em multiplicidade (C6/B1), e a prioridade passa para B1.

**O que ainda não se sabe e o experimento revela.** Para hc9u o resultado é essencialmente previsto (≥ 28,44). A incerteza real está no regime de longo curso (TNTP), onde as bandas e C3 são o fator decisivo, e no regime de `r` grande (cc, lin23), onde C1 e C2 tendem a ser vazias e só C4 e C5 atuam.

---

## Apêndice A: resumo dos resultados teóricos deste documento

| # | Enunciado | Status |
|---|---|---|
| T1 | `C` viável ⇔ `B_C` tem emparelhamento perfeito | Provado |
| T2 | `z_LP` = fluxo de custo mínimo com custo `1/m` (ou `1/(m−1)`) por trânsito | Provado |
| 2.2 | `OPT/m ≤ z_LP ≤ OPT`; `z_LP ≤ (m/(m−1))·L_bot` | Provado |
| F1 | Gap → `m` (só o centro é compartilhado) | Provado |
| F2 | Gap `= m`; cortes por robô inúteis; Hall de 1º salto fecha | Provado |
| hc9u | `LP + C1 ≥ 256/9`, logo `OPT ≥ 29` | Provado (estrutura verificada no arquivo inteiro) |
| Tri | `OPT 2 > LP_cov 1,5 > z_LP 1` | Provado |
| P4 | Desigualdades por arco em `f` contornadas por circulação (só com `m ≥ 3` e vizinho de retorno) | Provado nas condições enunciadas |
| T3 | `y` fixo ⇔ max-flow; `f` contínuo sem perda | Provado |
| BC-y | Famílias parciais podem dar raiz `< z_LP`; os cortes clássicos fracionários corrigem isso | Provado (contraexemplo §5.9) |
| T5 | `proj_y(LP)` = cortes fracos `Σ κ y ≥ δ` | Provado |
| T6 | Formulação exata de set covering em `y` | Provado |
| T7 | `y(Z) ≥ 1` = CG de posto 1; `LP_cov ≥ z_LP` | Provado |
| T8 | Benders clássico ≡ `z_LP` | Provado |
| L1 | Lagrangeana nas ativações `≤ z_LP` | Provado |
| DW | Pricing polinomial; ramificação só em `y` basta | Provado |
| MC×cov | Multicommodity por origem não domina cobertura (F2 e F1) | Provado |
| cov×MC | Cobertura (RHS 1) não domina multicommodity | Hipótese |
| Sep | Separação fracionária exata de C4/C5 é NP-difícil | Hipótese |
| R2–R9 | Regras de pré-processamento | Provado (R3 com ressalva de lote; R1/R9 dependem de pesos `≤ r`; R8 só para a componente inteira) |

## Apêndice B: referências a conferir (não verificadas nesta sessão)

- Das, A. K. — *Charging Station Placement for Limited Energy Robots* (fonte do problema; no repositório).
- Kuby, M.; Lim, S. (2005). The flow-refueling location problem for alternative-fuel vehicles. *Socio-Economic Planning Sciences*.
- Capar, I.; Kuby, M.; Leon, V. J.; Tsai, Y.-J. (2013). An arc cover–path-cover formulation and strategic analysis of alternative-fuel station locations. *European Journal of Operational Research*.
- Yıldız, B.; Arslan, O.; Karaşan, O. E. (2016). A branch and price approach for routing and refueling station location model. *European Journal of Operational Research*.
- Arslan, O.; Karaşan, O. E.; Mahjoub, A. R.; Yaman, H. (2019). A branch-and-cut algorithm for the alternative fuel refueling station location problem with routing. *Transportation Science*.
- Göpfert, P.; Bock, S. (2019). A branch&cut approach to recharging and refueling infrastructure planning. *European Journal of Operational Research*.
- Lin, G.-H.; Xue, G. (1999). Steiner tree problem with minimum number of Steiner points and bounded edge-length. *Information Processing Letters*.
- Wong, R. T. (1984). A dual ascent approach for Steiner tree problems on a directed graph. *Mathematical Programming*.
- Magnanti, T. L.; Mirchandani, P.; Vachani, R. (1995). Modeling and solving the two-facility capacitated network loading problem. *Operations Research*.
- Geoffrion, A. M. (1974). Lagrangean relaxation for integer programming. *Mathematical Programming Study*.
- Magnanti, T. L.; Wong, R. T. (1981). Accelerating Benders decomposition. *Operations Research*.
- Codato, G.; Fischetti, M. (2006). Combinatorial Benders' cuts for mixed-integer linear programming. *Operations Research*.
- Picard, J.-C.; Queyranne, M. (1982). Selected applications of minimum cuts in networks. *INFOR*.
- Zenklusen, R. (2010). Matching interdiction. *Discrete Applied Mathematics*.
- Bruglieri, M.; Maffioli, F.; Ehrgott, M. (2004). Cardinality constrained minimum cut problems: complexity and algorithms. *Discrete Applied Mathematics*.
- Balas, E.; Ng, S. M. (1989). On the set covering polytope: I. All the facets with coefficients in {0,1,2}. *Mathematical Programming*.

## Apêndice C: registro da verificação

**Método.**
- Dois verificadores adversariais independentes, somente leitura e sem executar código, tentaram refutar com contraexemplos pequenos verificados à mão: um cobriu as seções 0–4 e o Apêndice A; o outro, as seções 5–11 e 13.
- Uma checagem direta de `instancias/hc9u.txt`, feita com uma varredura do arquivo por script de uma linha:
  - os 4608 arcos ligam vértices cujos rótulos diferem em exatamente um bit;
  - todos têm peso 1;
  - os 256 terminais (128 em `S`, 128 em `T`, todos distintos) têm paridade par.

**Afirmações confirmadas.**
- Teoremas 1–8, incluindo o detalhe do terminal em `Z(X)`.
- Corolários 2.2b–c e 7.1.
- Proposição 3.2.
- As famílias F1, F2 e Tri, com seus valores.
- O limite 256/9 em hc9u, que é o valor exato do LP só com C1.
- Validade de C1, C2 (qualquer métrica de caminho mínimo), C3, C4 (RHS 1 e versão mochila, DM, redução a `δ = 1`), C5 e C8.
- O corte combinatório de Benders.
- L1 = `z_LP`.
- O pricing do DW, com ramificação só em `y`.
- O valor `k/2` da multicommodity em F2.
- R2, R3 para um vértice, R4, R5 e R7.

**Correções incorporadas.** Nenhuma delas invalida a conclusão central (diagnóstico do LP, projeção em set covering, prioridades A1/A2, próxima hipótese).

| # | Onde | Problema encontrado | Correção |
|---|---|---|---|
| 1 | §3, Prop. 3.1 | A BFS no subgrafo induzido por `S∪C∪T` deixa passar por terminais sem estação | Busca por origem que só expande vértices de `C` |
| 2 | §2.7, P4 | O contorno por circulação só vale com `m ≥ 3` e vizinho de retorno, e não é gratuito | Condições e custo exato enunciados |
| 3 | §2.2a | "Exato quando todos compartilham" era falso para o ótimo inteiro | Exatidão depende do fluxo de custo mínimo; contraexemplo incluído |
| 4 | §2.2d | "`m = 1` é o único caso exato" era impreciso | Reformulado |
| 5 | §0, §2.1, §3 (variante U) | Trânsito negativo em `S∩T`, ciclos de custo zero, redefinição de `δ` | Ressalvas explícitas |
| 6 | §4, Teorema 7 | O título sugeria igualdade com o fecho CG | Título corrigido |
| 7 | §2.2e | `0,149 = 10/67` não é determinado pelo valor arredondado | "Compatível com" |
| 8 | §10, R1/R9 | `A_r ⊇ E` exige todo peso `≤ r` | Condição e consequências (componentes) incluídas |
| 9 | §10, R8 | A dominância vértice a vértice falha dentro da árvore | Prova para a componente inteira |
| 10 | §5.1, §5.2 | C1 não fecha F1; C2 fecha só usada dos dois lados; custo do Dijkstra omitido | Corrigido |
| 11 | §5.3 | O fecho `X` tem `δ ≥ 1`, não `δ = 1` | Corrigido |
| 12 | §5.5 | O teste de minimalização de `Z` estava errado (gerava cortes inválidos) | Teste correto `V ∖ (Z∖{v})` inviável |
| 13 | §5.5(i) | O paramétrico com `λ < m` mais conferência detecta mais casos | Corrigido |
| 14 | §6, Teorema 8 | O MIP do mestre pode superar `z_LP`; o defeito está na relaxação | Ressalva incluída |
| 15 | §5.9, §6.3, §9, A2 | BC-y só com famílias polinomiais pode ter raiz `< z_LP` (contraexemplo) | Separar também os cortes clássicos fracionários, com a versão arredondada |
| 16 | §7, L3 | A ligação `in^s(v) ≤ y_v` é inválida em destinos; o custo omitia `m³` | Ligação `out^s(v) ≤ y_v` (`v ≠ s`); custo ≈ 1,7·10⁹ |
| 17 | §9 | A multicommodity por origem não é forte em F1 (vale `mk + k + 1`) | Tabela e hierarquia corrigidas; F1 reforça que ela não domina a cobertura |
| 18 | §10, R5; §11 | Fixações por otimalidade não se transferem entre `r`; H3 fica sem sinal em alguns casos; H1 exige recalcular o fluxo | Ressalvas incluídas |
| 19 | §12 | O UB = 42 não valia em "todas" as execuções; diagnóstico do Benders | Corrigido |

**Pontos ainda não verificados:**
- as referências do Apêndice B;
- a estrutura de `bip42p` e `hc10–12p` (hipótese de terminais isolados);
- a complexidade da separação fracionária exata de C4/C5 (hipótese de NP-dificuldade);
- a existência de um exemplo limpo em que a multicommodity supera a cobertura com RHS 1.
