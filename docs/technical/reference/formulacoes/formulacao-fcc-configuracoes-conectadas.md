# F-CC — formulação por configurações conectadas de estações

> **Estado deste documento (F1, 2026-10-06).**
>
> - **Papel:** formulação em avaliação, **não** o baseline. Código:
>   `experiments/alternative-formulations/fcc.py`.
> - **Definição:** seções 1–5 fecham `y`, `λ_q`, `d_st`, `q=(W,I,J)`,
>   conectividade em `H`, `B(W)`, pares diretos, R1–R3 e `S∩T`. Exemplo de
>   montagem no final.
> - **Provas (F2):** `docs/technical/reference/formulacoes/provas-fcc-fc3.md`.
> - Cadeia adotada: `base ≤ F-CC ≤ F-C3 ≤ OPT`. O elo F-C3 permanece
>   `HYPOTHESIS`/`OPEN` enquanto as redes de trios não tiverem definição.

A formulação proposta é a **F-CC: formulação por configurações conectadas de estações**. Ela escolhe a infraestrutura de recarga e os grupos de origens e destinos atendidos por essa infraestrutura.

Para escrevê-la completamente, precisamos definir primeiro o que constitui uma configuração válida.

**1. Conjuntos e parâmetros**

Considere:

- \(G=(V,E)\): grafo simples, conexo e não direcionado;
- \(S\subseteq V\): origens;
- \(T\subseteq V\): destinos;
- \(|S|=|T|=m\): quantidade de robôs;
- \(r\in\mathbb Z_{>0}\): autonomia;
- \(d_G(u,v)\): distância em número de arestas.

É permitido \(S\cap T\neq\varnothing\).

Construímos o grafo de alcance:

\[
H=(V,E_r),
\]

\[
E_r=
\left\{
\{u,v\}:u\neq v,\ d_G(u,v)\le r
\right\}.
\]

Uma aresta de \(H\) representa um deslocamento realizável com uma carga.

Definimos também os pares que podem ser atendidos **sem recarga**:

\[
D=
\left\{
(s,t)\in S\times T:d_G(s,t)\le r
\right\}.
\]

Como \(d_G(s,s)=0\), o conjunto \(D\) inclui a possibilidade de permanecer parado quando \(s\in S\cap T\).

Para um conjunto não vazio \(W\subseteq V\), sua vizinhança fechada em \(H\) é:

\[
B(W)=
W\cup
\left\{
v\in V:
\exists w\in W,\ \{v,w\}\in E_r
\right\}.
\]

Portanto, \(B(W)\) contém os vértices de \(W\) e aqueles que conseguem alcançar alguma estação de \(W\) com uma carga.

**2. Definição de uma configuração**

Uma configuração é uma tripla:

\[
q=(W_q,I_q,J_q),
\]

em que:

\[
\varnothing\neq W_q\subseteq V,
\qquad H[W_q]\text{ é conexo},
\]

\[
I_q\subseteq S\cap B(W_q),
\]

\[
J_q\subseteq T\cap B(W_q),
\]

\[
1\le |I_q|=|J_q|.
\]

A interpretação é:

| Elemento | Significado |
|---|---|
| \(W_q\) | Estações que formam uma infraestrutura conectada no grafo de alcance |
| \(I_q\) | Origens atendidas por essa infraestrutura |
| \(J_q\) | Destinos atendidos por essa infraestrutura |

Se todas as estações de \(W_q\) estiverem instaladas, qualquer origem de \(I_q\) pode alcançar qualquer destino de \(J_q\): o robô alcança \(W_q\), percorre suas estações conectadas e chega ao destino.

A igualdade \(|I_q|=|J_q|\) permite associar cada origem a um destino distinto. Como não existem capacidades ou colisões, as rotas podem compartilhar estações.

Definimos:

\[
Q=\{\text{todas as configurações que satisfazem essas condições}\}.
\]

Essas condições fazem parte da definição de \(Q\). Assim, autonomia, conectividade e equilíbrio já estão incorporados em cada configuração.

**3. Variáveis de decisão**

**Instalação de estações**

\[
y_v\in\{0,1\},
\qquad \forall v\in V.
\]

- \(y_v=1\): uma estação é instalada em \(v\);
- \(y_v=0\): não há estação em \(v\).

As variáveis existem para **todos os vértices**, inclusive origens e destinos.

**Utilização das configurações**

\[
\lambda_q\ge0,
\qquad \forall q\in Q.
\]

\(\lambda_q\) é o peso atribuído à configuração \(q\).

Quando \(\lambda_q=1\), a configuração representa o atendimento completo das origens de \(I_q\) aos destinos de \(J_q\), usando a infraestrutura \(W_q\).

Essa variável pode ser contínua. Valores fracionários são parte do certificado matemático; não significam dividir fisicamente um robô.

**Viagens diretas**

\[
d_{st}\ge0,
\qquad \forall(s,t)\in D.
\]

\(d_{st}\) representa o peso da atribuição direta de \(s\) a \(t\), sem recarga.

Quando \(d_{st}=1\), o robô de \(s\) vai diretamente a \(t\). Se \(s=t\), permanece parado.

Os limites \(\lambda_q\le1\) e \(d_{st}\le1\) são implicados pelas restrições seguintes.

**4. Função objetivo**

\[
\boxed{
\min \sum_{v\in V}y_v
}
\]

Minimizamos a quantidade total de estações instaladas.

Uma estação utilizada por vários robôs é contabilizada uma única vez, pela variável \(y_v\).

**5. Restrições**

**R1 — Atendimento de cada origem**

\[
\boxed{
\sum_{\substack{q\in Q\\s\in I_q}}\lambda_q
+
\sum_{\substack{t\in T\\(s,t)\in D}}d_{st}
=1,
\qquad \forall s\in S.
}
\]

Cada origem deve ter seu atendimento total igual a uma unidade.

Esse atendimento pode ser representado por configurações que contêm a origem ou por viagens diretas. A igualdade impede que uma origem seja ignorada ou atendida mais de uma vez.

**R2 — Ocupação de cada destino**

\[
\boxed{
\sum_{\substack{q\in Q\\t\in J_q}}\lambda_q
+
\sum_{\substack{s\in S\\(s,t)\in D}}d_{st}
=1,
\qquad \forall t\in T.
}
\]

Cada destino deve receber atendimento total igual a uma unidade.

R1 e R2, juntas, garantem que todas as origens e todos os destinos participem da atribuição.

Quando um vértice pertence a \(S\cap T\), ele aparece nas duas famílias de restrições, com papéis distintos. Seu robô pode permanecer ou partir enquanto outro robô chega.

**R3 — Ligação entre configurações e estações**

\[
\boxed{
\sum_{\substack{q\in Q\\v\in W_q}}\lambda_q
\le y_v,
\qquad \forall v\in V.
}
\]

Se \(y_v=0\), nenhuma configuração que exige uma estação em \(v\) pode receber peso positivo.

Se \(y_v=1\), a soma dos pesos dessas configurações pode ser, no máximo, 1.

**Essa restrição não limita a quantidade de robôs que utilizam a estação.** Uma única configuração pode atender todos os \(m\) robôs.

O fundamento é que uma instalação real pode ser representada pelas componentes conexas de \(H[C]\). Cada estação pertence a uma componente, e os robôs atendidos por ela são agrupados em uma configuração. Grupos que compartilham estações podem ser reunidos.

A soma em R3 é essencial: substituí-la apenas por ligações individuais \(\lambda_q\le y_v\) enfraqueceria a formulação.

**R4 — Domínios**

\[
\boxed{
y_v\in\{0,1\},
\qquad \forall v\in V,
}
\]

\[
\boxed{
\lambda_q\ge0,
\qquad \forall q\in Q,
}
\]

\[
\boxed{
d_{st}\ge0,
\qquad \forall(s,t)\in D.
}
\]

Somente as variáveis de instalação precisam ser binárias.

**Por que as variáveis contínuas preservam a exatidão?**

Com \(y\) binário, toda configuração de peso positivo utiliza apenas estações instaladas. Dentro dela, existe uma bijeção viável entre suas origens e destinos.

Combinando essas bijeções com os pesos \(\lambda_q\) e as viagens diretas, R1 e R2 produzem um matching perfeito fracionário composto apenas por pares alcançáveis. Pela integralidade do matching bipartido, existe um matching perfeito inteiro nesse suporte, sem instalar novas estações.

No sentido inverso, qualquer solução física pode ser representada agrupando suas rotas pelas componentes de \(H[C]\), além das viagens diretas. Portanto, a formulação preserva exatamente as instalações viáveis.

**O custo da representação**

O modelo tem \(n+2m\) restrições principais, mas \(Q\) pode ser exponencial. A conectividade não desapareceu: ela está incorporada à definição das configurações.

A exatidão apresentada considera **todas** as configurações de \(Q\). Restringir arbitrariamente essa família pode excluir soluções válidas e exige outra análise.

**6. Exemplo de montagem (6 vértices)**

Instância: \(V=\{s_1,s_2,u,w,t_1,t_2\}\), \(S=\{s_1,s_2\}\), \(T=\{t_1,t_2\}\), \(r=1\).
Arestas de \(G\): \(s_1u\), \(s_2u\), \(uw\), \(wt_1\), \(wt_2\). Grafo conexo, \(S\cap T=\varnothing\).

\(H=G^r=G\) (autonomia 1). Pares diretos: \(D=\varnothing\), porque \(d_G(s_i,t_j)=3>1\).

\(B(\{w\})=\{u,w,t_1,t_2\}\). \(B(\{u\})=\{s_1,s_2,u,w\}\). \(B(\{u,w\})=V\).

Uma configuração válida: \(W=\{u,w\}\) (conexo em \(H\)), \(I=\{s_1,s_2\}\), \(J=\{t_1,t_2\}\). R1/R2 com \(\lambda_q=1\) e \(y_u=y_w=1\) dão ótimo 2. Não existe \(W\) unitário com \(S\cap B(W)\) e \(T\cap B(W)\) ambos não vazios e do mesmo tamanho cobrindo as duas origens: \(\{u\}\) não alcança \(T\); \(\{w\}\) não alcança \(S\).

Variáveis: \(y_v\) nos seis vértices; um \(\lambda_q\) por tripla \((W,I,J)\) com \(W\) conexo não vazio, \(I\subseteq S\cap B(W)\), \(J\subseteq T\cap B(W)\), \(|I|=|J|\ge 1\); nenhum \(d_{st}\).

Restrições a escrever: duas R1 (\(s_1,s_2\)), duas R2 (\(t_1,t_2\)), seis R3.