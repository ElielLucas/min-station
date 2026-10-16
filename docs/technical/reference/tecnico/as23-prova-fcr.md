# AS23 — Revisão independente da validade de FC-R e FC-R-T

**Veredito matemático:** **PASS** para ambas as famílias, sob as hipóteses do modelo U/COMP com `y` binário. A separação ótima de `Q` para uma região fixa também é provada. Isso **não** comprova ganho em instâncias reais nem originalidade na literatura.

**Fonte de hipótese (não prova substituta):** [`parecer-astra-fcr-pos-as22.md`](parecer-astra-fcr-pos-as22.md). **Código auditado:** `experiments/alternative-formulations/as02_model_a.py` (`compile_u`), `experiments/cuts/cuts.py`, `experiments/cuts/verify_fcr_witness.py`.

## 1. Hipóteses e notação

O dígrafo de alcance é `H=(V,A_r)`, calculado das distâncias do grafo físico (não se usam arestas físicas no lugar de arcos de alcance). `S,T⊆V` são conjuntos internamente sem repetição, equicardinais, possivelmente intersectantes. `m=|S|=|T|`. Para cada `v`, `a_v=1[v∈S]`, `b_v=1[v∈T]`.

No compacto U usado para a comparação:

\[
 f^{out}(v)-f^{in}(v)=a_v-b_v,\quad
 f^{in}(v)\le b_v+(m-b_v)y_v,\quad
 f^{out}(v)\le a_v+(m-a_v)y_v,
\]

com `f≥0` e `y_v∈{0,1}` para a demonstração de validade. Os fluxos podem circular: a prova **não assume aciclicidade**. A relaxação LP permite `0≤y≤1` e **pode violar** FC-R, precisamente o fundamento de seu fortalecimento.

## 2. Validade de FC-R (origens)

Escolha uma região não vazia `L⊆V`, com excesso **estritamente positivo**

\[
 d_L=|S\cap L|-|T\cap L|>0.
\]

Defina a fronteira de saída `δ⁺(L)={(u,v)∈A_r:u∈L,v∉L}`. Seja `Q⊆N_H⁺(L)\setminus(L∪T)`. Pela soma dos balanços de U em `L`,

\[
 f(δ⁺(L))-f(δ⁻(L))=d_L,
\]

portanto `f(δ⁺(L))≥d_L` por não negatividade. A desigualdade proposta é

\[
 \boxed{f(L,V\setminus(L\cup Q))+d_Ly(Q)\ge d_L.}\tag{FC-R}
\]

**Prova por disjunção inteira:**

- Se `y(Q)=0`, então `y_v=0` para todo `v∈Q`. Como `Q∩T=∅`, `b_v=0` e `f^{in}(v)≤m y_v=0`; pela não negatividade, nenhum arco com cabeça em `Q` pode transportar fluxo. Assim, `f(L,Q)=0` e `f(L,V\setminus(L∪Q))=f(δ⁺(L))≥d_L`.
- Se `y(Q)≥1`, então `d_Ly(Q)≥d_L`; o termo de fluxo é não negativo.

A prova cobre fluxos com ciclos, estações compartilhadas e nós em `S∩T`, porque usa o balanço agregado exato e ativação. **Não** interpreta `d_L` como capacidade física por estação.

**Contraexemplo à exclusão de `T`:** `S={s}`, `T={t}`, arco direto `s→t`, `f_st=1`, `y_t=0`. A escolha proibida `L={s}`, `Q={t}` transforma FC-R na falsa desigualdade `0+y_t≥1`. Logo `Q∩T=∅` é necessária para o enunciado generalizado.

## 3. Validade de FC-R-T (destinos)

Se `h_L=|T∩L|-|S∩L|>0`, tome `Q⊆N_H⁻(L)\setminus(L∪S)`. O balanço fornece

\[
 f(δ⁻(L))-f(δ⁺(L))=h_L>0,
\]

logo `f(δ⁻(L))≥h_L`. A desigualdade é

\[
 \boxed{f(V\setminus(L\cup Q),L)+h_Ly(Q)\ge h_L.}\tag{FC-R-T}
\]

Se `y(Q)=0`, todos os `u∈Q` estão fora de `S`, portanto `f^{out}(u)≤m y_u=0` e nenhum arco com cauda em `Q` conduz fluxo. Caso `y(Q)≥1`, o termo inteiro cobre `h_L`. Em ambos os casos a desigualdade vale, inclusive na presença de circulação.

**Contraexemplo à exclusão de `S`:** viagem direta `s→t`, `L={t}`, `Q={s}`, `f_st=1`, `y_s=0`. A desigualdade incorreta exigiria `y_s≥1`, invalidando um ponto inteiro fisicamente viável.

**Regiões equilibradas:** se o excesso é zero, as formas com RHS positivo não são aplicáveis. Se `S=T`, ambas as famílias com excesso regional estrito ficam vazias, em conformidade com o ótimo zero por permanência.

## 4. Separação exata de Q com L fixada

No ponto LP candidato `(f*,y*)` e região de origem com `d_L>0`, escreva `B=N_H⁺(L)\setminus(L∪T)` e `w_v=f*(L,{v})`. A parte variável do lado esquerdo de FC-R ao escolher `Q⊆B` é

\[
 \sum_{v\in Q}(d_Ly^*_v-w_v).
\]

Logo **cada escolha é independente** e

\[
 Q^*=\{v\in B:w_v>d_Ly^*_v\}
\]

minimiza exatamente o lado esquerdo entre todos os `2^|B|` subconjuntos (empates podem ficar fora). Para destinos, `B=N_H⁻(L)\setminus(L∪S)`, `w_u=f*({u},L)`, `d_L` substituído por `h_L`, com a mesma regra. A prova é algébrica e não exige que `(f*,y*)` seja ponto viável: a fórmula minimiza a expressão para qualquer valores dados. A seleção global de **L** não é coberta por este resultado; não há alegação de separação polinomial de todas as regiões.

O verificador AS23 implementa a regra somente para testes e a compara com enumeração exaustiva de `Q` em `test_as23_fcr_q_selection.py`. O separador de produção pertence à AS24.

## 5. Relação com K, C8 e C6

Se `L={s}`, `s∈S\setminus T`, então `d_L=1` e pelo balanço `f^{out}(s)=1+f^{in}(s)`. FC-R equivale a

\[
 f(s,Q)\le y(Q)+f^{in}(s).
\]

Para `Q={v}` fora de `T`, esta é exatamente a desigualdade **C8 individual de origem** documentada no §5.8 de `direcoes-pli-min-station.md`. Para diversos `v∈Q`, somar C8 individuais produz `f(s,Q)≤y(Q)+|Q|f^{in}(s)`, enquanto FC-R conta `f^{in}(s)` uma vez. O análogo em destinos usa `f^{out}(t)`.

A relação com C6 é de **complementaridade**, não dominância universal. Na testemunha AS23, um corte C6 é gerado por `generate_C6` com `δ=2`, e o ganho estrito de FC-R persiste quando as 36 linhas C8 e C6 estão presentes. Nenhuma conclusão geral sobre implicar todos os cortes K ou C6 foi demonstrada.

## 6. Revisão bibliográfica delimitada

FC-R é nome operacional local. As ideias de fluxo ativado por variáveis binárias, flow-cover, flow-pack, cortes de rede de custo fixo e programação disjuntiva são clássicas. **Não reivindicar novidade teórica de FC-R** com base no parecer ou na presente revisão. Fontes verificadas quanto a título, autores, DOI e escopo por resumos/editoras:

1. Padberg, Van Roy & Wolsey (1985), *Valid Linear Inequalities for Fixed Charge Problems*, **Operations Research** 33(4), 842–861. DOI: [10.1287/opre.33.4.842](https://doi.org/10.1287/opre.33.4.842). Cobre desigualdades válidas para variáveis de fluxo contínuo ativadas por 0–1.
2. Van Roy & Wolsey (1985), *Valid inequalities and separation for uncapacitated fixed charge networks*, **Operations Research Letters** 4(3), 105–112. DOI: [10.1016/0167-6377(85)90012-4](https://doi.org/10.1016/0167-6377(85)90012-4). Trata cortes e separação para redes de custo fixo sem capacidade.
3. Rardin & Wolsey (1993), *Valid inequalities and projecting the multicommodity extended formulation for uncapacitated fixed charge network flow problems*, **European Journal of Operational Research** 71(1), 95–109. DOI: [10.1016/0377-2217(93)90263-M](https://doi.org/10.1016/0377-2217(93)90263-M). Estuda projeções e desigualdades dicut.
4. Atamtürk (2001), *Flow pack facets of the single node fixed-charge flow polytope*, **Operations Research Letters** 29(3), 107–114. DOI: [10.1016/S0167-6377(01)00100-6](https://doi.org/10.1016/S0167-6377(01)00100-6). Aborda facetas locais de fluxo com custo fixo.

**Limite da revisão:** os resumos e metadados permitem posicionar a técnica e negar presunção de novidade, mas não bastam para provar que a expressão exata FC-R é ou não conhecida na literatura. Revisão de equivalência/facetas em textos completos permanece trabalho científico posterior; não é gate de correção matemática da AS23.

## 7. Evidência independente e limites

O arquivo [`../experimentos/as23-validacao-fcr.md`](../experimentos/as23-validacao-fcr.md) apresenta a reprodução racional. A prova acima pode ser auditada independentemente de SciPy. O JSON contém tanto pontos primais quanto multiplicadores duais, e `recheck_saved` rejeita certificados inconsistentes usando somente `fractions.Fraction`.

Não foram executadas campanhas reais, callbacks, branch-and-cut ou testes de ganho MIP nesta fase.
