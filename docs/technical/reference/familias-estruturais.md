# Famílias estruturais BP, HB, SC e TR

**Data:** 2026-10-03
**Geradores:** `experiments/structural/`. Versão de gerador `1`.
**Problema:** MIN-STATION de Das. Grafo não dirigido, arestas de peso 1, `r` inteiro, `|S| = |T|`, `S∩T = ∅` por construção, estações em todo `V`, objetivo minimizar `|C|`.

Os números do Apêndice B do parecer foram recalculados pelos geradores. Não foram copiados como evidência.

## BP

Para cada caixa `j = 0..q−1` há um vértice `v_j` com `B` folhas de destino. Para cada item `i` de tamanho `e_i` há um vértice `u_i` com `e_i` folhas de origem e `q` conectores `c_{i,j}` nas arestas `u_i–c_{i,j}–v_j`. `r = 1` e `m = Σ e_i = qB`.

`|V| = q + qB + n + m + nq`, com `n` o número de itens e `m = qB`.

**Limite `2n + q`.** Cada `u_i` é a única saída das suas folhas de origem e não é destino, então C1 força `y` em `u_i`. Cada `v_j` é a única entrada das suas folhas de destino, então C1 força `y` em `v_j`. Cada item precisa ainda de um conector: a folha de origem chega a `u_i` num salto, e de `u_i` até um destino são mais dois saltos (`c_{i,j}` e `v_j`), com `r = 1`. Uma estação em algum `c_{i,j}` cobre esse segundo salto do item. São `n + q + n = 2n + q` estações. Este argumento é o do parecer; o script `verify_t12_bp.py` confere o valor no modelo base e no núcleo.

**Ótimo.** Se os itens cabem em `q` caixas de capacidade `B`, o conjunto `{u_i} ∪ {v_j} ∪ {c_{i,j} : i atribuído à caixa j}` tem tamanho `2n + q` e é viável: o robô da folha `s_{i,k}` segue `s → u_i → c_{i,j} → v_j → t`. Se não cabem, `2n + q` não basta, porque cada conector escolhido para o item `i` o liga a uma única caixa, e as `e_i` folhas daquele item ocupam `e_i` destinos da caixa. O certificado de existência é o plantio ou a programação dinâmica `particao_exata` em `bp.py`. Nenhum dos dois chama o modelo MIN-STATION. O modelo base só é usado para conferir o número já certificado.

O plantio “sim” do piloto usa três inteiros por caixa no intervalo aberto `(B/4, B/2)` somando `B`. O lado “não” aplica `+1/−1` até a mesma função dinâmica devolver `None`. As quatro linhas do Apêndice B usam as listas explícitas, não o tripleto: `B = 2` não tem inteiro nesse intervalo.

Hipóteses que o piloto não usa: `OPT = 2n + q + σ*` para um defeito `σ*`, e `OPT ≤ 2n + 2q − 1`.

## HB

Um bolsão tem `q` origens `A`, completas com `ndir` destinos diretos `C`. Os relés `X` repartem `A` em blocos disjuntos de `p` origens (`ceil(q/p)` relés). Há `δ = q − ndir` destinos distantes `D`. Cada `d ∈ D` liga todos os relés e um balanceador `e_d`, que liga um destino próprio `g_d`. `r = 1`. Vários bolsões se unem por um caminho de `L ≥ 2` vértices não terminais entre `g` de um bolsão e `g` do seguinte, no mesmo desenho de `make_F2`.

`|S| = |T| = 2q − ndir`.

**Limite superior `min(ceil(δ/p), 3)`, com `ndir ≥ 1`.** Duas soluções explícitas.

1. Escolha `δ` origens de `A` para os destinos distantes, empacotadas em `ceil(δ/p)` blocos, e instale o relé de cada bloco. Origem do bloco vai ao relé e do relé a qualquer `d`. As outras `ndir` origens vão direto a `C`. Cada balanceador vai direto a `g_d`. Nenhuma dessas rotas tem interior fora do conjunto de relés.
2. Com um destino direto `c` e uma origem `a'` cujo relé é `x`, o conjunto `{c, a', x}` cobre o bolsão. Qualquer origem `a` segue `a → c → a' → x → d`: `A` é completo com `C`, `a'` liga `x`, e `x` liga todo `D`. As `ndir` idas diretas a `C` e as idas `e_d → g_d` não pedem estação. O interior `{c, a', x}` está em `C`.

O menor dos dois tamanhos é `min(ceil(δ/p), 3)`. O teto 3 usa o destino direto como hub, então pede `ndir ≥ 1`.

**Limite inferior `OPT ≥ min(ceil(δ/p), 3)`.** Continua hipótese fora das instâncias enumeradas. Não há prova escrita que valha para todo parâmetro. Nas cinco configurações do Apêndice B, `verify_t13_hb.py` enumera o ótimo com `independent_validator` e confere com o modelo base. Se numa delas o enumerado ficasse abaixo do limite, a construção estaria errada.

**Aditividade em `k` bolsões.** Hipótese geral. Nas células do piloto o modelo base provou, em 2026-10-03, com status ótimo, que o valor é exatamente `k` vezes o limite de um bolsão. A §5.5 trata esse modelo como equivalente ao problema. Esses certificados liberam as células; não viram teorema para outros parâmetros.

| q | ndir | p | k | |V| | ótimo provado | previsão |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 1 | 1 | 2 | 58 | 6 | 6 |
| 6 | 1 | 1 | 4 | 118 | 12 | 12 |
| 6 | 1 | 1 | 8 | 238 | 24 | 24 |
| 6 | 1 | 6 | 2 | 48 | 2 | 2 |
| 6 | 1 | 6 | 4 | 98 | 4 | 4 |
| 6 | 1 | 6 | 8 | 198 | 8 | 8 |

**Previsão C6, anterior a qualquer medição.** Por bolsão, a desigualdade da Proposição 5.4.2 em `S' = A` é satisfeita por `y_c = 1` no destino direto compartilhado, porque o coeficiente desse vértice é `δ`. A previsão registrada em `c6-hall-primeiro-salto.md` é `LB ≈ 1` por bolsão contra `OPT = 3`.

C1 e C2 saem vazios nas cinco linhas do Apêndice B: toda origem tem um destino adjacente ou está a distância 1 de algum destino (os balanceadores), e a distância máxima até `T` não passa de `r`. O script confere que os geradores devolvem zero cortes.

## SC-GF2

`U = GF(2)^k \ {0}`, `n = 2^k − 1`. Para cada `a ≠ 0`, `F_a = {x ≠ 0 : a·x = 1}`, de tamanho `2^{k−1}`. Vértices `w_a`, `s_x`, `t_x`. Aresta `s_x–w_a` se e só se `a·x = 1`, e `w_a–t_x` para todo par. `r = 1`, `m = n`, `|V| = 3n`.

**Ótimo `k`.** Um conjunto de vetores `a` cobre todo `U` pelos `F_a` se e só se esses vetores geram `GF(2)^k`. A dimensão é no máximo `k`, e `k` vetores de uma base cobrem. Cada `w_a` escolhido é estação: `s_x` vai a `w_a` e de `w_a` a `t_x` em dois saltos. Não há estação menor que a cobertura, porque uma rota de um salto só existiria se alguma origem fosse adjacente a um destino, e o grafo não tem aresta `s–t`. Este é o teorema usual de cobertura pelos hiperplanos; o gerador não pede certificado de solver para o próprio GF2.

**LP com C1.** Cada origem `s_x` tem `2^{k−1}` vizinhos em `W` e nenhum em `T`, então C1 dá `Σ_{a : a·x = 1} y_{w_a} ≥ 1`. A atribuição uniforme `y = 2^{−(k−1)}` em `W` e zero fora soma `n / 2^{k−1} = (2^k − 1) / 2^{k−1}` e satisfaz toda linha, porque cada linha tem exatamente `2^{k−1}` variáveis. O valor é `2 − 2^{1−k}`.

O grupo `GL(k, 2)` age no sistema e é transitivo em `W`. Isso é propriedade do sistema linear, não uma medição.

O gêmeo rígido parte da mesma matriz e aplica trocas `2×2` que preservam a soma de cada linha e de cada coluna. O ótimo do gêmeo é o de um IP de set cover sobre o mesmo sistema (`opt_set_cover` em `sc.py`), não o do MIN-STATION.

`classes_wl` com cor inicial `(s ∈ S, t ∈ T)` vale 3 no GF2 e em qualquer gêmeo de mesmas margens: as três classes são `S`, `T` e `W`, e o refinamento não sai dali. Essa medida não separa simetria de gap. A medida usada no lugar dela individualiza uma estação, pendurando um vértice privado, e repete o 1-WL. No GF2 o número de cores depois da individualização é o mesmo para toda estação. O gêmeo entra na comparação só quando esse número é estritamente maior.

## TR

`m` origens ligadas a todas as entradas. O corredor `j` é o caminho `e_j–c_{j,1}–…–c_{j,L}–x_j`. Cada `x_j` liga todos os `m` destinos. `D = L + 3` é o número de arestas de uma origem até um destino por um corredor (`s–e` mais `L+1` arestas do corredor mais `x–t`). Degrau: aresta `c_{j,ℓ}–c_{j+1,ℓ}` quando `ℓ` é múltiplo de `σ`. `σ` ausente significa corredores disjuntos no miolo.

**Ótimo `ceil(D/r) − 1`.** Qualquer rota origem–destino tem comprimento pelo menos `D` quando não há atalho, e uma estação a cada `r` saltos no caminho mínimo pede `ceil(D/r) − 1` interiores. Com `σ` ausente o caminho mínimo tem exatamente `D` arestas. Instalar, em cada corredor, estações nas posições `r, 2r, …` ao longo do caminho `s–e–…–x–t` realiza o limite; como os corredores são iguais, o mesmo padrão num corredor serve para todos os robôs se eles podem escolher o mesmo corredor. O ótimo é o de um corredor, não `k` vezes isso.

O Apêndice B fixa `m = 2` mesmo com `k = 3`. O gerador segue essa escolha.

A contagem de ótimos do núcleo com `r > 1` não é assumida igual a `k^R`. Cada banda de C2 pode conter `r` vértices por corredor, e o conjunto de ótimos do IP de núcleo pode ser maior. A contagem usada no piloto, se TR entrar, sai de um pool de soluções do núcleo, não de uma fórmula imposta.
