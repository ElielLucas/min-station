# Provas da formulação A — Condições e demonstrações

**Estado:** demonstrações preparadas para revisão matemática independente (AS01-02, AS01-03, AS01-04). **Não constituem parecer de autor diferente do verificador.**

## Hipóteses e definição

Adotam-se exatamente `G,S,T,m,r,H,𝓑,c,κ,A1–A7` de [formulacao-a-grupos-origens.md](formulacao-a-grupos-origens.md). Os cortes K, quando presentes, devem ser válidos para toda instalação física e idênticos entre as formulações comparadas. Seja `P_U^LP` a projeção em `(y,F)` da relaxação U com `0≤y≤1`; `P_A^LP(𝓑)` sua contraparte A. A equivalência física da **base U com y binário** é um resultado pré-existente usado como lema, sujeito à hipótese de `S∩T` não cancelado e ao tratamento de terminais conforme o código `baseline.py`. A prova abaixo também esclarece sua interpretação por decomposição de caminhos.

## Teorema 1 — A é exata no domínio binário

**Enunciado.** Para qualquer partição válida `𝓑` e vetor `y∈{0,1}^V`, A sem K tem extensão viável se e somente se a instalação `C={v:y_v=1}` é fisicamente viável. A propriedade persiste ao incluir cortes K que são válidos para toda instalação física.

### (Instalação → A)

Uma instalação viável induz uma bijeção `π:S→T` e um caminho em `H` de `s` a `π(s)` para cada origem, com todo vértice interno pertencente a `C`. Remova repetições: como não há capacidade de uso finita e saltos são entre vértices de alcance, remover um ciclo de uma caminhada em `H` mantém uma caminhada válida e não cria estações novas. Para `s=π(s)`, tome o caminho trivial.

Para cada bloco `B`, some as incidências de arcos dos caminhos com origem em `B` em `f^B`. Defina `p_{Bt}` como 1 se `π^{-1}(t)∈B` e 0 caso contrário; `h^B_v=1` para permanência trivial no próprio `v∈B∩T`, senão 0; `g^B_v` como o número de caminhos desse bloco cujo **vértice interno** é `v`. Cada caminho não trivial contribui entrada/saída ou uso interno exatamente como A1–A2; a bijeção dá A3.

Cada caminho simples do bloco que visita internamente `v∈B` **não** pode ser aquele que começa em `v` (pois então repetiria seu início); assim `g^B_v≤|B|−1=c_{Bv}`. Se `v∉B`, no máximo `|B|` caminhos do bloco visitam `v` internamente. Além disso, para `v∈S∪T`, há ao menos um caminho que começa ou termina em `v` e portanto não pode ter `v` como vértice interno; no total `Σ_Bg^B_v≤m−1`. Para outros vértices, `Σ_Bg^B_v≤m`. Como todo uso interno exige `y_v=1`, A4 e A5 são satisfeitas. K válido também é satisfeito.

### (A com y binário → instalação)

Some A1 e A2 sobre os grupos. Escrevendo `F=Σ_B f^B`, `G_v=Σ_Bg^B_v`, `H_v=Σ_Bh^B_v`, `a_v=1[v∈S]`, `b_v=1[v∈T]`, A3 fornece:

\[
\operatorname{in}_F(v)+H_v=b_v+G_v,\qquad
\operatorname{out}_F(v)+H_v=a_v+G_v.
\]

Logo `out_F−in_F=a_v−b_v`. A5 e `H_v≥0` dão

\[
\operatorname{in}_F(v)\le b_v+\kappa_vy_v
\quad\text{e}\quad
\operatorname{out}_F(v)\le a_v+\kappa_vy_v.
\]

Como `κ_v≤m−b_v` e `κ_v≤m−a_v` **não valem simultaneamente para todos os tipos de terminal** (por exemplo, `v∈S\T` e `m−b_v=m`), usamos as desigualdades separadas: para `v∈T`, `κ_v=m−1=m−b_v`; para `v∉T`, `κ_v≤m=m−b_v`. Analogamente, para `v∈S`, `κ_v=m−1=m−a_v`; para `v∉S`, `κ_v≤m=m−a_v`. Portanto U é satisfeita com **exatamente o mesmo y**.

Pela exatidão inteira da U: quando `y_v=0`, um vértice não terminal não pode ser atravessado por fluxo, e cada origem/destino pode oferecer/receber apenas seu próprio serviço gratuito; a decomposição de fluxo em caminhos origem→destino, com cancelamento de ciclos e recombinação nos terminais coincidentes, fornece uma bijeção viável. Vértices internos dos caminhos escolhidos têm `y_v=1`. Isso conclui a direção reversa.

**Dependência explícita:** a última decomposição é a propriedade de exatidão inteira da U; a prova escrita da AS-01 deve ser auditada também quanto à eventual necessidade de hipóteses adicionais em `S∩T`.

## Teorema 2 — O LP com um grupo projeta-se no LP de U

Seja `𝓑={S}`. A inclusão `proj_y LP(A({S})) ⊆ proj_y LP(U)` já segue da soma dos balanços acima, sem exigir `y` binário.

Reciprocamente, considere `(y,F)` factível no LP de U. Ponha `f^S=F`, `p_{St}=1` para todo `t∈T`, e para cada vértice defina os auxiliares por casos:

| Classe de `v` | `h_v` | `g_v` |
|---|---:|---:|
| `v∉S∪T` | 0 | `in_F(v)=out_F(v)` |
| `v∈S\T` | 0 | `in_F(v)=out_F(v)−1` |
| `v∈T\S` | 0 | `in_F(v)−1=out_F(v)` |
| `v∈S∩T` | `max{0,1−in_F(v)}` | `max{0,in_F(v)−1}` |

No último caso, `in_F(v)=out_F(v)` pelo balanço de U. A conservação de U garante `g_v≥0`; A1/A2 são satisfeitas em todas as classes. Para `v∉S∪T`, as ativações de U impõem `g_v≤my_v`; em `S\T`, `out_F(v)≤1+(m−1)y_v` implica `g_v≤(m−1)y_v`; em `T\S`, `in_F(v)≤1+(m−1)y_v` implica a mesma desigualdade; em `S∩T`, `g_v≤(m−1)y_v`. Como `c_{Sv}=m−1` se `v∈S`, e `m` nos demais casos, A4 é respeitada, inclusive em `T\S` por ser limite mais permissivo. A5 segue das cotas de `κ` por classe. `h_v∈[0,1]`.

Assim toda solução do LP de U admite a extensão de A com um bloco, **preservando y e F**. O mesmo vale com os mesmos cortes K, pois eles dependem só de y:

\[
\operatorname{proj}_y LP(A(\{S\})+K)=\operatorname{proj}_y LP(U+K).
\]

## Teorema 3 — Refinar blocos não enfraquece o LP

Se `𝓑'` refina `𝓑`, defina para cada bloco original `B` a soma dos valores dos subblocos `B'⊆B` de `f,g,p,h`. A1–A3 são preservadas pela linearidade; A5 não muda; A4 resulta de

\[
\sum_{B'\subseteq B}c_{B'v}=
\sum_{B'\subseteq B}|B'|-\sum_{B'\subseteq B}\mathbf1_{\{v\in B'\}}
=|B|-\mathbf1_{\{v\in B\}}=c_{Bv}.
\]

Como `h^B_v` é a soma de variáveis que só podem existir para o único subbloco que contém `v` (ou nenhuma), seu limite superior `[0,1]` é preservado. Para `p`, `Σ_{B'⊆B}p_{B't}≤1` por A3 e não negatividade. Portanto a soma é factível em A(𝓑). Logo

\[
\operatorname{proj}_y LP(A(\mathcal B')+K)\subseteq
\operatorname{proj}_y LP(A(\mathcal B)+K)
\]

e `z_LP(A(𝓑)+K)≤z_LP(A(𝓑')+K)` para a minimização. **Não existe ordem automática para partições não comparáveis por refinamento.**

## Teorema 4 — A unitária e a formulação B de caminhos

Com `𝓑={{s}:s∈S}`, as restrições A1/A2 descrevem, para cada origem, uma rede de fluxo com injeção na origem, absorção nos destinos e trânsito em vértices com `g^s_v≤y_v` para `v≠s` (pois `c_{\{s\}v}=1`), e `g^s_s=0`. Remover circulações não aumenta nenhum `g`, e permite decompor o fluxo em caminhos simples origem→destino e, se `s∈T`, permanência de comprimento zero. Um percurso que sai de `s` e retorna a `s` para terminar pode ser substituído por permanência, sem aumentar `g`, sem mudar o atendimento de destinos e sem alterar y. Os pesos de caminhos satisfazem B1–B4, e vice-versa (somando incidências por origem), incluindo os limites globais `κ_v`. Logo as **projeções em y** de `LP(A(unitária)+K)` e `LP(B+K)` coincidem.

**Revisão necessária:** esta passagem por decomposição, em especial os percursos que retornam a `s` quando `s∈S∩T`, merece auditoria independente antes de rotular o teorema como `PROVEN` no repositório.

## O que não foi demonstrado neste documento

Não se provou que A2 supera A4 em tempo, que o LP é estritamente mais forte em toda instância, nem que uma partição arbitrária domina outra. Tampouco foi provada uma relação de inclusão geral entre A2+K e a proposta anterior de cortes por origem. Os resultados exatos de exemplos aparecem separadamente, sem inferência de desempenho geral.
