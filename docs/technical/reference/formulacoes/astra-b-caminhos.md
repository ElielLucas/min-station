# AS-08 · T1 — Formulação B por caminhos: formalização e equivalência LP com A unitária

**Natureza:** parecer matemático. Não há código novo, otimização ou experimento. Os exemplos numéricos são pequenos e foram verificados à mão. Eles ilustram as afirmações, mas não as demonstram.
**Spec:** `specs/as-08-formulacao-b-caminhos/` (tarefa T1; requisitos AS08-01, AS08-02, AS08-03).
**Data / branch:** 2026-10-12, `novos_testes` (HEAD `3392c79`).
**Gate do protocolo:** a revisão independente (autor ≠ verificador), exigida em `tasks.md`, **continua pendente**. Este documento fornece a prova a ser revisada. Ele não substitui esse parecer.

Marcas usadas: **[Provado]** indica prova completa neste documento. **[Citado]** indica resultado clássico externo, usado como lema. **[Exemplo]** indica instância pequena verificada à mão. **[Não verificado]** indica afirmação de outra fonte que não foi reexaminada aqui.

---

## 1. Resumo executivo e conclusão preliminar

1. **A formulação B do Astra está bem definida e é exata no domínio inteiro.** São as famílias B1–B4, com $\mathcal P_s$ formado pelos caminhos simples em $H$ e pelo caminho de comprimento zero quando $s\in T$. Para $y\in\{0,1\}^V$, B tem extensão viável se e somente se $C=\{v:y_v=1\}$ é fisicamente viável. A prova é direta, por Birkhoff–von Neumann, e não depende da exatidão de U (Teorema 1, §6.6).
2. **A igualdade $\operatorname{proj}_y LP(B)=\operatorname{proj}_y LP(A_{\text{unit}})$ vale, com ou sem K** (Teorema 2, §7–§8). A prova é autocontida e não usa alegações do parecer. Ela vale **ponto a ponto em $y$**: para cada $y\in[0,1]^V$, a fibra de B é não vazia se e somente se a de $A_{\text{unit}}$ é não vazia. Por isso a equivalência também vale para $y$ binário, no MIP com variáveis auxiliares contínuas.
3. **Há um ponto técnico que a prova precisa tratar explicitamente.** Em $A_{\text{unit}}$, o fluxo de uma origem $s\in S\cap T$ pode sair de $s$ e voltar a $s$ para terminar ali. Isso forma uma caminhada fechada, que é ponto extremo do poliedro por origem e não é caminho simples. Na passagem $A\to B$, essa massa vai para o caminho de comprimento zero com peso $p_{ss}$, e **não com peso $h_s$** (§8.2, Exemplo E4).
4. **B4 é necessária, mas só não é redundante em $v\in T\setminus S$.** Sem B4 obtém-se a F-h histórica. Na estrela de §6.5 (sem K), $z_{LP}(\text{F-h})=1/2<1=z_{LP}(B)$. Em $v\notin T\setminus S$, B4 é implicada pela soma de B3 (Proposição 6.1). O mesmo vale para A5 em **qualquer** partição da Formulação A (Observação 4.2).
5. **B domina U em projeção** (Corolário 8.4), e a dominância pode ser estrita (Exemplo E2). B4 é exatamente a família que recupera a restrição (E) de U nos destinos que não são origens.
6. **O pricing proposto pelo Astra decorre corretamente da formulação.** O custo reduzido é $\bar c_P=\sum_{v\in\operatorname{int}P}(\gamma_{sv}+\mu_v)-\pi_s-\tau_t$, com $\gamma,\mu\ge0$. O pricing é um caminho mínimo com custos não negativos nos vértices, uma execução por origem. Ele deve incluir o caminho de comprimento zero e os arcos diretos. O limite dual do parecer é válido por dualidade fraca, sob as condições do §11.4, e não exige duais ótimos.
7. **Escala.** B elimina as $m|A_r|$ variáveis de fluxo de $A_{\text{unit}}$, mas mantém até $m(n-1)$ linhas B3. Uma geração de linhas B3 acoplada às colunas é compatível com o limite dual (§11.5). **Nenhuma vantagem computacional fica demonstrada.**
8. **Natureza da equivalência.** Ela é de relaxação, não de desempenho. B é a reformulação de Dantzig–Wolfe de $A_{\text{unit}}$ por origem, com um subproblema que tem a propriedade de integralidade (Observação 8.6). Por isso B **não traz força LP nova** em relação a $A_{\text{unit}}$. B também é a F-h histórica acrescida de B4 e do tratamento explícito de $S\cap T$, e não uma formulação inédita (§10).

**Classificação preliminar:** EQUIVALÊNCIA DEMONSTRADA. A formulação do Astra não precisou de correção. Foram necessárias apenas precisões de definição, já implícitas no parecer, e uma observação de redundância (§13).

---

## 2. Referências efetivamente consultadas

| Documento / código | Uso |
|---|---|
| `CLAUDE.md`, `docs/project-overview.md`, `RESEARCH.md` | Escopo, invariantes e semântica de Das |
| `docs/context-ai/min-station-domain.md` §3–§7, §9 | Semântica dos saltos em $H$, terminais e $S\cap T$ |
| `docs/technical/reference/pareceres-astra/2026-10-11-02-parecer-fluxos-por-grupos.md` §4.A, §4.B, §5, §6 | Definição de A e de B1–B4, alegação de equivalência, pricing, bound e escalabilidade |
| `docs/technical/reference/tecnico/direcoes-pli-min-station.md` §0, §1.1, §2.2a, §3, §8, §9 | Convenções, Teorema 1 (viabilidade ⇔ emparelhamento), F-h (§8.1–§8.4), F-b e tabela §9 |
| `specs/as-08-formulacao-b-caminhos/{spec,design,tasks}.md` | Requisitos AS08-01..06; formulação do bound no design |
| `docs/technical/reference/formulacoes/formulacao-a-grupos-origens.md` | Definição de referência de A1–A7 |
| `docs/technical/reference/formulacoes/provas-formulacao-a.md` (Teoremas 1–4) | Provas de A; o Teorema 4 é o esboço de A unitária = B que este documento torna rigoroso |
| `docs/technical/reference/formulacoes/relacoes-lp-formulacao-a.md` | Cadeia LP, estrela T18 e Sec59 |
| `specs/as-01-formalizacao-matematica-a/validation.md` | Pendência explícita: "equivalência B↔A unitária [...] requer revisão" |
| `experiments/alternative-formulations/as02_model_a.py` (`compile_a`, l. 141–180) | Implementação de A, conferida contra o documento (§4.6) |
| `instances/manifest.csv` (colunas `n`, `m`, `n_arcos_alcance`, `rho_S_inter_T`) | Tamanhos usados no §12 |

Referências externas usadas como lemas clássicos [Citado]. Por convenção do projeto, os dados bibliográficos devem ser conferidos antes de qualquer uso em artigo:

- Ahuja, Magnanti e Orlin, *Network Flows*, Prentice Hall, 1993, cap. 3: teorema de decomposição de fluxos. Para tornar o documento autossuficiente, a versão necessária é reprovada no Lema 8.1.
- Birkhoff (1946) e von Neumann (1953): toda matriz duplamente estocástica é combinação convexa de matrizes de permutação.
- Geoffrion (1974), *Lagrangean relaxation for integer programming*, Math. Programming Study 2: propriedade de integralidade.
- Muter, Birbil e Bülbül (2013), *Simultaneous column-and-row generation for large-scale linear programs with column-dependent-rows*, Math. Programming 142: geração simultânea de linhas e colunas.

---

## 3. Definição formal do problema MIN-STATION

### 3.1 Dados

- $G=(V,E)$ é um grafo simples, não direcionado e conexo, com autonomia comum $r\ge1$ (Das; `min-station-domain.md` §3).
- $H=(V,A)$, com $A:=A_r=\{(u,v):u\ne v,\ d(u,v)\le r\}$, é o **dígrafo de alcance**. Ele não tem laços nem arcos paralelos. $n=|V|$.
- $S,T\subseteq V$ com $|S|=|T|=m\ge1$. **Não** se supõe $S\cap T=\varnothing$.
- $a_v=\mathbf 1[v\in S]$ e $b_v=\mathbf 1[v\in T]$.
- $\kappa_v=m-1$ se $v\in S\cup T$; $\kappa_v=m$ caso contrário.
- $\delta^+(v)$ e $\delta^-(v)$ são os arcos de saída e de entrada de $v$ em $H$. Para $\phi\in\mathbb R^A_{\ge0}$, $\operatorname{out}_\phi(v)=\phi(\delta^+(v))$ e $\operatorname{in}_\phi(v)=\phi(\delta^-(v))$.

**Observação 3.1 (métrica).** Na definição fiel de Das, $d$ é a distância em passos. O código também admite pesos (`direcoes-pli` §0; `base-formulation.md` §10.2). **Todos os resultados deste documento valem para qualquer dígrafo $H$ sem laços.** Nenhuma prova usa a métrica, a simetria de $A_r$ ou a conexidade de $G$. Portanto eles se aplicam tanto ao problema de Das quanto às extensões ponderadas e dirigidas, desde que estas sejam rotuladas como extensão.

### 3.2 Caminhadas, caminhos e interior

Uma caminhada em $H$ é uma sequência $W=(w_0,\dots,w_k)$, $k\ge0$, com $(w_{i-1},w_i)\in A$. Define-se $o(W)=w_0$, $e(W)=w_k$ e $|W|=k$. O **interior** é

$$\operatorname{int}(W)=\{w_i: 0<i<k\}.$$

$W$ é um **caminho simples** se os $w_i$ forem distintos. O caminho de comprimento zero $(s)$ tem $\operatorname{int}=\varnothing$, e um caminho de um arco também tem $\operatorname{int}=\varnothing$.

**Definição 3.2 (viabilidade física).** $C\subseteq V$ é viável se existirem uma bijeção $\pi:S\to T$ e, para cada $s$, uma caminhada $W_s$ em $H$ de $s$ a $\pi(s)$ com $\operatorname{int}(W_s)\subseteq C$. Se $\pi(s)=s$, $W_s$ pode ser trivial, e o robô permanece onde está. MIN-STATION consiste em minimizar $|C|$ sobre os $C$ viáveis.

Essa é a semântica de `min-station-domain.md` §3–§7: cada arco de $H$ é um deslocamento com uma carga, e só os pontos de transição entre saltos exigem estação. Ela corresponde também a `direcoes-pli` Teorema 1, à Proposição 1 do artigo IJCAI 2026 e à validação da base (`validacao-formulacao-base.md`). A redução dos movimentos em $G$ a caminhadas em $H$ é pré-existente e **não é reprovada aqui**. Robôs anônimos, estações sem capacidade e $S\cap T$ permitido estão incluídos. Nenhuma hipótese é acrescentada.

**Lema 3.3 (atalho) [Provado].** Para toda caminhada $W$ de $u$ a $w$ existe um caminho simples $P$ de $u$ a $w$ com $A(P)\subseteq A(W)$ e $\operatorname{int}(P)\subseteq\operatorname{int}(W)$. Se $u=w$, então $P=(u)$.

*Prova.* Enquanto houver $w_i=w_j$ com $i<j$, remova $w_{i+1},\dots,w_j$. O arco $(w_i,w_{j+1})=(w_j,w_{j+1})$ já pertencia a $W$. O processo termina num caminho simples $P$ de $u$ a $w$, e $P=(u)$ quando $u=w$. Seja $v\in\operatorname{int}(P)$. Como $P$ é simples, $v\notin\{u,w\}$. Logo toda ocorrência de $v$ em $W$ está numa posição $0<i<k$, e $v\in\operatorname{int}(W)$. ∎

**Corolário 3.4.** Na Definição 3.2 podem-se exigir caminhos simples sem alterar o conjunto dos $C$ viáveis.

---

## 4. Formulação A unitária completa

### 4.1 Formulação A geral (referência)

A referência é `formulacao-a-grupos-origens.md` §3–§5, que reproduz o parecer Astra §4.A. Fixa-se uma partição $\mathcal B$ de $S$ e define-se $c_{Bv}=|B|-\mathbf 1[v\in B]$. As variáveis são:

- $y_v\in\{0,1\}$;
- $f^B_{uv}\ge0$;
- $g^B_v\ge0$;
- $p_{Bt}\in[0,1]$ para $t\in T$;
- $h^B_v\in[0,1]$ para $v\in B\cap T$.

Por convenção, $p_{Bv}:=0$ para $v\notin T$ e $h^B_v:=0$ para $v\notin B\cap T$. As restrições são A1–A6 e o objetivo é A7.

### 4.2 Especialização para $\mathcal B_{\text{unit}}=\{\{s\}:s\in S\}$

Escreve-se $f^s$, $g^s$, $p_{st}$ e $h_s:=h^{\{s\}}_s$, que só existe quando $s\in T$. Então $c_{\{s\}v}=1-\mathbf 1[v=s]$.

**Variáveis:**

| Símbolo | Índices | MIP | LP |
|---|---|---|---|
| $y_v$ | $v\in V$ | $\{0,1\}$ | $[0,1]$ |
| $f^s_{uv}$ | $s\in S,(u,v)\in A$ | $\ge0$ contínua | $\ge0$ |
| $g^s_v$ | $s\in S,v\in V$ | $\ge0$ contínua | $\ge0$ |
| $p_{st}$ | $s\in S,t\in T$ | $[0,1]$ contínua | $[0,1]$ |
| $h_s$ | $s\in S\cap T$ | $[0,1]$ contínua | $[0,1]$ |

**Restrições**, para todo $s\in S$ e $v\in V$, com $h_s:=0$ se $s\notin T$:

$$\operatorname{in}_{f^s}(v)+\mathbf 1[v=s]\,h_s=p_{sv}+g^s_v \tag{A1}$$
$$\operatorname{out}_{f^s}(v)+\mathbf 1[v=s]\,h_s=\mathbf 1[v=s]+g^s_v \tag{A2}$$
$$\textstyle\sum_{s\in S}p_{st}=1\qquad(t\in T) \tag{A3}$$
$$g^s_v\le(1-\mathbf 1[v=s])\,y_v \tag{A4}$$
$$\textstyle\sum_{s\in S}g^s_v\le\kappa_v\,y_v\qquad(v\in V) \tag{A5}$$
$$\textstyle\sum_{v\in Z}y_v\ge1\qquad(Z\in K) \tag{A6}$$
$$\min\textstyle\sum_{v\in V}y_v \tag{A7}$$

**Domínios.** No MIP, apenas $y$ é binário. Na relaxação $LP(A_{\text{unit}}+K)$, vale $y\in[0,1]^V$. "Sem K" significa remover só A6.

**Lema 4.1 (estrutura por origem) [Provado].** Em todo ponto de $LP(A_{\text{unit}})$ e para todo $s\in S$, convencionando $p_{ss}:=0$ e $h_s:=0$ se $s\notin T$, valem:

1. $g^s_s=0$; para $v\neq s$, $\operatorname{out}_{f^s}(v)=g^s_v$ e $\operatorname{in}_{f^s}(v)=p_{sv}+g^s_v$.
2. $\operatorname{out}_{f^s}(s)=1-h_s$ e $\operatorname{in}_{f^s}(s)=p_{ss}-h_s$. Em particular, $h_s\le p_{ss}$.
3. O excesso líquido $e^s(v):=\operatorname{out}_{f^s}(v)-\operatorname{in}_{f^s}(v)$ satisfaz $e^s(s)=1-p_{ss}$ e $e^s(v)=-p_{sv}\le0$ para $v\neq s$.
4. $\sum_{t\in T}p_{st}=1$. Logo $e^s(s)\ge0$.

*Prova.* (1) A4 com coeficiente 0 e $g\ge0$ dão $g^s_s=0$. Para $v\ne s$, o termo $h$ não aparece, e A1–A2 dão as duas identidades. (2) Basta ler A1–A2 em $v=s$ com $g^s_s=0$; $\operatorname{in}\ge0$ dá $h_s\le p_{ss}$. (3) Subtraia (1) e (2). (4) $\sum_v e^s(v)=0$, porque cada arco conta uma vez como saída e uma vez como entrada. Logo $1-\sum_t p_{st}=0$. ∎

### 4.3 Como $A_{\text{unit}}$ representa cada elemento

- **Conservação de fluxo.** Há uma commodity por origem, com oferta unitária em $s$ e demanda $p_{st}$ em cada $t$ (Lema 4.1(3)).
- **Atendimento.** A origem é atendida pela oferta unitária, e $\sum_t p_{st}=1$ é implicado (Lema 4.1(4)). Cada destino é atendido por A3. **Nenhum pareamento é fixado.**
- **Instalação e uso.** $g^s_v$ é a saída da commodity $s$ por $v\ne s$, isto é, o trânsito, e é limitada por $y_v$ (A4). A commodity $s$ **não pode transitar pela própria origem**, porque $g^s_s=0$. Fluxo de $s$ que volta a $s$ só pode terminar ali, se $s\in T$.
- **Compartilhamento.** O mesmo $y_v$ limita cada origem separadamente (A4). O custo de uma estação compartilhada é, portanto, o **máximo** do uso por origem, e não a soma.
- **Acoplamento global.** A5 limita o trânsito total por $\kappa_v y_v$; A3 acopla as origens pelos destinos.
- **$S\cap T$.** $h_s$ representa a permanência. Outros robôs podem chegar a $s$ (via $p_{s't}$ com $t=s$) e $s$ pode partir, de modo que a troca de ocupantes é permitida.
- **Caminhos sem recarga.** Arcos diretos $(s,t)$ geram $g=0$ e não consomem $y$.

**Observação 4.2 (A5 só é necessária em $T\setminus S$) [Provado].** Para qualquer partição $\mathcal B$, somar A4 sobre os blocos dá

$$\sum_B g^B_v\le\Big(\sum_B|B|-\sum_B\mathbf 1[v\in B]\Big)y_v=(m-a_v)\,y_v.$$

Compare com $\kappa_v$: $m-a_v=\kappa_v$ para $v\in S$ e para $v\notin S\cup T$. A diferença só ocorre em $v\in T\setminus S$, onde $m-a_v=m>m-1=\kappa_v$. **Logo A5 é implicada por A4 fora de $T\setminus S$, em qualquer partição.**

**Observação 4.3.** Isso é coerente com a estrela T18 (`relacoes-lp-formulacao-a.md`): o vértice violado é $c\in T\setminus S$.

### 4.4 Inconsistências encontradas em A

Nenhuma inconsistência matemática foi encontrada em A1–A7. Há dois registros:

1. O documento de A pressupõe $G$ conexo e $r$ medido em arestas. Como dito na Observação 3.1, os resultados aqui não dependem disso.
2. A redundância da Observação 4.2 não é um erro, apenas linhas supérfluas.

### 4.5 Correspondência documento ↔ código

`compile_a` (`as02_model_a.py` l. 141–180) implementa exatamente:

- A1: `in f + h − p − g = 0`;
- A2: `out f + h − g = 1[v∈B]`;
- A4 com coeficiente `len(B) − int(v in B)`;
- A5 com `kappa = m − int(v∈S∪T)`;
- A3;
- $h$ apenas em $B\cap T$, com $p,h\le1$ e $y\le1$.

**Não há divergência.**

---

## 5. Formulação B completa

### 5.1 Conjuntos e parâmetros

- $H=(V,A)$, $S$, $T$, $m$ e $\kappa_v$ são os do §3.
- Para $s\in S$, $\mathcal P_s$ é o conjunto de:
  - **todos os caminhos simples** $P$ em $H$ com $o(P)=s$ e $e(P)\in T$, de comprimento $\ge1$;
  - o **caminho de comprimento zero** $(s)$, se $s\in T$.
- $\mathcal P=\bigsqcup_s\mathcal P_s$, e $\mathcal P_s(t)=\{P\in\mathcal P_s:e(P)=t\}$.

Propriedades que decorrem da definição:

- **Vértices internos** podem ser quaisquer, inclusive outras origens e outros destinos. Cada vértice interno exige estação.
- **A origem $s$ nunca é interna** a um caminho de $\mathcal P_s$, pois o caminho é simples.
- **Caminhos de $\mathcal P_s$ que terminam em $s$**: o único é $(s)$, já que um caminho simples de comprimento $\ge1$ não termina no próprio início.
- **Caminhos que repetem vértices ou arcos** não estão em $\mathcal P_s$. A Proposição 5.1 mostra que incluí-los não muda a projeção.

**Carga** da origem $s$ no vértice $v$:

$$L^s_v(x):=\sum_{P\in\mathcal P_s:\ v\in\operatorname{int}P}x_P.$$

Note que $L^s_s\equiv0$.

### 5.2 Variáveis

- $y_v$: $\{0,1\}$ no MIP e $[0,1]$ no LP.
- $x_P\ge0$ contínua, $P\in\mathcal P$, tanto no MIP quanto no LP. O Teorema 1 mostra que, com $y$ binário, existe $x$ inteiro quando $x$ contínuo existe. $x_P\le1$ é implicado por B1.
- Não há variáveis auxiliares indispensáveis. Atribuição, permanência e trânsito são funções lineares de $x$ (§8.3).

### 5.3 Objetivo

$$\min\ \sum_{v\in V}y_v. \tag{B0}$$

### 5.4 Restrições

$$\sum_{P\in\mathcal P_s}x_P=1\qquad(s\in S) \tag{B1}$$
$$\sum_{s\in S}\ \sum_{P\in\mathcal P_s(t)}x_P=1\qquad(t\in T) \tag{B2}$$
$$L^s_v(x)\le y_v\qquad(s\in S,\ v\in V\setminus\{s\}) \tag{B3}$$
$$\sum_{s\in S}L^s_v(x)\le\kappa_v\,y_v\qquad(v\in V) \tag{B4}$$
$$\sum_{v\in Z}y_v\ge1\qquad(Z\in K) \tag{BK}$$

Em B2, os caminhos que terminam em $t$ incluem o caminho zero $(t)$ quando $t\in S$, além dos caminhos de outras origens que chegam a $t$. $LP(B+K)$ designa B0–B4+BK com $y\in[0,1]^V$ e $x\ge0$; "sem K" remove BK.

### 5.5 Bastam caminhos simples

**Proposição 5.1 [Provado].** Seja $\mathcal W_s\supseteq\mathcal P_s$ um conjunto qualquer de caminhadas de $s$ que terminam em $T$. Defina $B^{\mathcal W}$ por B1–B4 sobre $\mathcal W$, com carga dada pela indicadora de $v\in\operatorname{int}W$ ou pela multiplicidade das ocorrências internas. Então $\operatorname{proj}_y LP(B^{\mathcal W}+K)=\operatorname{proj}_y LP(B+K)$.

*Prova.*

- ($\supseteq$) Uma solução de B é solução de $B^{\mathcal W}$ com $x=0$ nas caminhadas não simples.
- ($\subseteq$) Substitua cada caminhada $W$ pelo seu atalho $P$ (Lema 3.3), transferindo o peso $x_W$ para $x_P$. Os extremos se preservam, portanto B1 e B2 também. $P\in\mathcal P_s$, e uma caminhada fechada em $s\in T$ vira $(s)$. Como $\operatorname{int}P\subseteq\operatorname{int}W$, nenhuma carga aumenta, e B3–B4 se preservam. $y$ não muda. ∎

---

## 6. Interpretação das restrições B1–B4

### 6.1 B1 — atendimento da origem

1. $\sum_{P\in\mathcal P_s}x_P=1$.
2. Cada robô sai de sua origem por exatamente uma unidade de rotas, ou permanece no lugar.
3. Necessária: sem B1, nada obriga a origem a ser usada, e B2 poderia ser satisfeita com mais de uma unidade saindo de uma origem.
4. Corresponde à oferta unitária de A2 em $v=s$ e ao Lema 4.1(4), $\sum_t p_{st}=1$.
5. Remover B1 permite que poucas origens bem posicionadas atendam todos os destinos, o que deixa de modelar o problema.

### 6.2 B2 — atendimento do destino

1. $\sum_{P:e(P)=t}x_P=1$.
2. Cada destino recebe exatamente um robô, possivelmente o próprio ocupante $(t)$.
3. Necessária pela definição de Das.
4. Corresponde a A3, com $p_{st}=\sum_{P\in\mathcal P_s(t)}x_P$.
5. Sem B2, todos os robôs poderiam ir ao destino mais barato. A matriz $z_{st}=p_{st}$ deixaria de ser duplamente estocástica, e a prova do Teorema 1 falharia.

### 6.3 B3 — ativação por origem

1. $L^s_v\le y_v$ para $v\ne s$.
2. A fração de rotas da origem $s$ que recarregam em $v$ não excede a instalação em $v$.
3. Necessária: é a ligação desagregada. Sem ela resta só a ligação agregada B4, que divide o custo de cada estação por até $\kappa_v$ origens.
4. Corresponde a A4 com $c_{\{s\}v}=1$, via $g^s_v=L^s_v$ (§8).
5. Sem B3, a exatidão inteira se mantém: com $y_v=0$, B4 já anula toda carga em $v$, e a prova do Teorema 1 se adapta. O LP, porém, enfraquece. No Exemplo E2, o ponto $y_h=1/2$ satisfaz B1, B2 e B4 ($1\le2y_h$), mas viola B3. A linha $v=s$ é omitida porque é vazia ($L^s_s\equiv0$).

### 6.4 B4 — acoplamento global

1. $\sum_sL^s_v\le\kappa_vy_v$.
2. O trânsito total por $v$ é limitado pelo número máximo de caminhos simples de uma bijeção que podem ter $v$ como vértice interno. Esse número é $m$, ou $m-1$ quando $v$ é terminal, porque o caminho que começa ou termina em $v$ não o atravessa. **Não se trata de capacidade física de estação.**
3. É necessária em $T\setminus S$ e implicada nos demais vértices (Proposições 6.1 e 6.2).
4. Corresponde a A5.
5. Removida, obtém-se a F-h histórica, cujo LP pode ficar abaixo do de U e do de $A_{\text{unit}}$ (§6.5).

**Proposição 6.1 (redundância fora de $T\setminus S$) [Provado].** Se $v\notin T\setminus S$, B4 em $v$ é implicada por B3.

*Prova.* Como $L^v_v=0$, somando B3: $\sum_sL^s_v=\sum_{s\ne v}L^s_v\le|S\setminus\{v\}|\,y_v=(m-a_v)y_v$. Se $v\in S$, $m-a_v=m-1=\kappa_v$. Se $v\notin S\cup T$, $m-a_v=m=\kappa_v$. ∎

Consequentemente, B4 pode ser imposta só para $v\in T\setminus S$, num total de $m-|S\cap T|$ linhas, **sem alterar o LP**. A projeção do Teorema 2 é a mesma com B4 completa ou restrita, e o mesmo vale para A5 restrita (Observação 4.2).

### 6.5 Necessidade de B4 (contraexemplo para F-h)

**Proposição 6.2 [Provado, Exemplo E1].** Sem B4 e sem K, a inclusão $\operatorname{proj}_yLP(\text{B sem B4})\subseteq\operatorname{proj}_yLP(A_{\text{unit}})$ **falha**.

*Instância (estrela, a mesma de `relacoes-lp-formulacao-a.md`).* Arestas $ac$, $bc$, $cd$; $S=\{a,b\}$, $T=\{c,d\}$, $r=1$. Logo $H$ é simétrico com os arcos $a\leftrightarrow c$, $b\leftrightarrow c$, $c\leftrightarrow d$.

Caminhos relevantes:

- $a\to c$, com interior $\varnothing$;
- $a\to c\to d$, com interior $\{c\}$;
- os análogos para $b$;
- não há outros, porque $a$ e $b$ só alcançam $c$, e $c$ só leva a $a$, $b$ e $d$.

*Ponto em B sem B4.* Tome $x_{ac}=x_{acd}=x_{bc}=x_{bcd}=1/2$ e $y_c=1/2$, com os demais $y$ nulos.

- B1: $1/2+1/2=1$ para cada origem.
- B2: $c$ recebe $1/2+1/2=1$, e $d$ recebe $1/2+1/2=1$.
- B3: $L^a_c=L^b_c=1/2\le y_c$.

Objetivo $1/2$. Esse é o mínimo: todo caminho até $d$ tem $c$ interno, a massa total em $d$ é 1, e B3 dá $y_c\ge\max(L^a_c,L^b_c)\ge1/2$.

*Em B (com B4).* $c\in T\setminus S$, então $\kappa_c=1$. Todo caminho que termina em $d$ tem $c$ interno, logo $\sum_sL^s_c\ge1$, e B4 dá $y_c\ge1$. Assim $z_{LP}(B)=1=OPT$. Pelo Teorema 2, $y_c=1/2$ não pertence a $\operatorname{proj}_yLP(A_{\text{unit}})$. ∎

*Ressalva.* Com o K real, C1 aplicada a $d$ ($N^-(d)\cap S=\varnothing$) impõe $y_c\ge1$ e fecha o exemplo. **A necessidade de B4 com K não está demonstrada por este exemplo.** A necessidade poliédrica, sem K, está.

### 6.6 Exatidão inteira de B

**Teorema 1 [Provado].** Seja $y\in\{0,1\}^V$ e $C=\{v:y_v=1\}$. Existe $x\ge0$ tal que $(y,x)$ satisfaz B1–B4 se e somente se $C$ é viável. Nesse caso existe $x\in\{0,1\}^{\mathcal P}$. Se K for válido para toda instalação viável, o mesmo vale com BK.

*Prova.*

(⇐) Pelo Corolário 3.4, existem $\pi$ e caminhos simples $P_s$ de $s$ a $\pi(s)$ com $\operatorname{int}P_s\subseteq C$, tomando $P_s=(s)$ quando $\pi(s)=s$. Faça $x_{P_s}=1$ e os demais $x$ nulos.

- B1 e B2 seguem da bijeção.
- B3: $L^s_v\in\{0,1\}$, e $L^s_v=1$ implica $v\in C$.
- B4: se $y_v=0$, nenhum caminho tem $v$ interno. Se $y_v=1$, contam-se os $m$ caminhos. Quando $v\in T$, o caminho que termina em $v$ não o tem como interno; quando $v\in S$, o caminho que começa em $v$ não o tem como interno. Em ambos os casos a carga é $\le m-1=\kappa_v$. Nos demais vértices, $\le m=\kappa_v$.

(⇒) Defina $z_{st}=\sum_{P\in\mathcal P_s(t)}x_P$. Por B1–B2 e $x\ge0$, $z$ é duplamente estocástica. Se $z_{st}>0$, existe $P\in\mathcal P_s(t)$ com $x_P>0$. Para todo $v\in\operatorname{int}P$ (e $v\ne s$), B3 dá $y_v\ge x_P>0$, logo $y_v=1$ e $\operatorname{int}P\subseteq C$. Portanto o suporte de $z$ está contido nas arestas do bipartido $B_C$, em que $s\sim t$ se e somente se existe caminho de $s$ a $t$ com interior em $C$; o caso $s=t$ é coberto por $(s)$. Por Birkhoff–von Neumann [Citado], o suporte de $z$ contém uma matriz de permutação $\pi$. Logo $C$ é viável, e os caminhos correspondentes dão um $x$ binário. ∎

*Notas.*

- B4 não é usada em (⇒). Ela é válida, mas inativa no inteiro. Seu papel é exclusivamente de LP.
- A prova não depende da exatidão de U nem de A.
- O resultado coincide com o "branching só em y" de `direcoes-pli` §8.2. Aqui ele é reprovado com $S\cap T$ e B4 incluídos.

### 6.7 Viabilidade da relaxação

**Proposição 6.3 [Provado].** Suponha que todo $Z\in K$ seja não vazio. Então $LP(B+K)\neq\varnothing$ se e somente se a instância é viável, isto é, se $C=V$ é viável.

*Prova.* (⇐) Teorema 1 com $y=\mathbf 1$.

(⇒) Seja $(y,x)$ viável. Mostra-se que $(\mathbf 1,x)$ também é:

- B3: $L^s_v\le1$ por B1.
- B4, para $v\in T$: os caminhos que terminam em $v$ somam 1 (B2), nenhum tem $v$ interno, e o total de massa é $m$. Logo a carga é $\le m-1$.
- B4, para $v\in S$: os caminhos de $\mathcal P_v$ somam 1 e não têm $v$ interno. Logo a carga é $\le m-1$.
- B4, demais vértices: carga $\le m$.
- BK: cada $Z$ é não vazio, então $y=\mathbf 1$ o satisfaz.

Pelo Teorema 1, $C=V$ é viável. ∎

Consequência: a relaxação de B **nunca declara viável uma instância inviável**, e a inviabilidade é detectada já no LP.

---

## 7. Teorema de equivalência das projeções LP

**Teorema 2 [Provado].** Sejam $H$ um dígrafo sem laços, $S,T\subseteq V$ com $|S|=|T|=m\ge1$, e $K$ uma família de subconjuntos de $V$. Para todo $y\in[0,1]^V$:

$$\exists(f,g,p,h):\ (y,f,g,p,h)\in LP(A_{\text{unit}}+K)\iff\exists x:\ (y,x)\in LP(B+K).$$

Em particular,

$$\operatorname{proj}_yLP(B+K)=\operatorname{proj}_yLP(A_{\text{unit}}+K)\quad\text{e}\quad z_{LP}(B+K)=z_{LP}(A_{\text{unit}}+K).$$

O mesmo vale sem K, e com B4/A5 completas ou restritas a $T\setminus S$.

---

## 8. Demonstração

### 8.1 Lema de decomposição

**Lema 8.1 (decomposição com fonte única) [Provado; versão de AMO cap. 3].** Seja $\phi\in\mathbb R^A_{\ge0}$ com excesso $e(v)=\operatorname{out}_\phi(v)-\operatorname{in}_\phi(v)$ tal que $e(s)\ge0$ e $e(v)\le0$ para todo $v\ne s$. Então existem:

- caminhos simples $Q_1,\dots,Q_k$ com $o(Q_i)=s$, $e(Q_i)\in\{v\neq s:e(v)<0\}$ e pesos $w_i>0$;
- ciclos dirigidos simples $C_1,\dots,C_l$ com pesos $\omega_j>0$;

tais que $\phi=\sum_iw_i\chi^{A(Q_i)}+\sum_j\omega_j\chi^{A(C_j)}$, $\sum_{i:e(Q_i)=t}w_i=-e(t)$ para todo $t\ne s$, e $\sum_iw_i=e(s)$.

*Prova.* Indução em $N(\phi)=|\{a:\phi_a>0\}|+|\{v:e(v)\ne0\}|$.

- Se $\phi=0$, então $e\equiv0$ e não há nada a fazer.
- Se $e(s)>0$: parta de $s$ e, em cada vértice $u$ alcançado, faça o seguinte. Se $u\ne s$ e $e(u)<0$, pare (encontrou-se um caminho). Caso contrário, $\operatorname{out}_\phi(u)\ge\operatorname{in}_\phi(u)>0$, ou $u=s$ com $\operatorname{out}_\phi(s)\ge e(s)>0$, e então siga um arco com $\phi>0$. Se algum vértice se repetir, extraia o ciclo simples formado.
  - Num caminho $Q$ de $s$ a $t$, subtraia $\varepsilon=\min\{\min_{a\in Q}\phi_a,\,e(s),\,-e(t)\}>0$.
  - Num ciclo, subtraia $\varepsilon=\min_{a\in C}\phi_a$.
  - Em ambos os casos, $\phi\ge0$ e o padrão de sinais de $e$ se mantêm, e $N$ diminui.
- Se $e(s)=0$, então $\sum_ve(v)=0$ e $e\le0$ dão $e\equiv0$: $\phi$ é uma circulação. Parta de um arco positivo e extraia um ciclo da mesma forma.

As igualdades de massa seguem porque ciclos não alteram $e$ e cada caminho altera $e(s)$ e $e(t)$ em exatamente $\varepsilon$. ∎

**Fato 8.2.** Seja $Q$ um caminho simples com $o(Q)=s$ e $v\ne s$. Então:

- $Q$ entra em $v$ no máximo uma vez, e entra exatamente quando $v\in\operatorname{int}Q$ ou $v=e(Q)$;
- $Q$ sai de $v$ no máximo uma vez, e sai exatamente quando $v\in\operatorname{int}Q$.

Um ciclo simples entra e sai de cada vértice no máximo uma vez. Um caminho simples que começa em $s$ nunca entra em $s$.

### 8.2 Direção $A_{\text{unit}}\Rightarrow B$

Seja $(y,f,g,p,h)\in LP(A_{\text{unit}}+K)$. Fixe $s$. Pelo Lema 4.1(3)–(4), $f^s$ satisfaz as hipóteses do Lema 8.1, com $e^s(s)=1-p_{ss}\ge0$ e $e^s(v)=-p_{sv}\le0$. Obtêm-se caminhos simples $Q$ de $s$ a destinos $t\ne s$ com $p_{st}>0$, logo $t\in T$, e ciclos simples.

**Construção.**

$$x_P=\sum_{i:\ Q_i=P}w_i\quad(P\in\mathcal P_s,\ |P|\ge1),\qquad x_{(s)}=p_{ss}\ \ (s\in S\cap T),$$

e $x_P=0$ nos demais caminhos. **Os ciclos são descartados.** Isso inclui os ciclos que passam por $s$, de peso total $\operatorname{in}_{f^s}(s)=p_{ss}-h_s$: correspondem às caminhadas que saem de $s$ e voltam para terminar em $s$.

**Verificação.**

- **B1.** $\sum_{P\in\mathcal P_s}x_P=(1-p_{ss})+p_{ss}=1$.
- **B2.** Para $t\in T$, a massa que termina em $t$ é $\sum_{s\ne t}p_{st}$, somada a $p_{tt}$ quando $t\in S$ (caminho zero). O total é $\sum_sp_{st}=1$ por A3.
- **B3.** Seja $v\ne s$. Pelo Fato 8.2, $v\in\operatorname{int}Q$ se e somente se $Q$ sai de $v$. Então
  $$L^s_v=\sum_{Q:\,v\in\operatorname{int}Q}w_Q\le\sum_Qw_Q|\delta^+(v)\cap A(Q)|+\sum_C\omega_C|\delta^+(v)\cap A(C)|=\operatorname{out}_{f^s}(v)=g^s_v\le y_v,$$
  usando o Lema 4.1(1) e A4.
- **B4.** $L^v_v=0$ e $g^v_v=0$, logo $\sum_sL^s_v\le\sum_{s\ne v}g^s_v=\sum_sg^s_v\le\kappa_vy_v$ por A5.
- **BK e domínios.** $y$ não muda e $x\ge0$.

**Elementos pedidos.**

- **Frações:** nenhum argumento usa integralidade.
- **Ciclos:** só podem diminuir cargas, por isso são descartados.
- **$S\cap T$:** tratado pelo caminho zero com peso $p_{ss}$.
- **Destinos atendidos:** pela igualdade de massas do Lema 8.1.

**Atenção.** Usar $x_{(s)}=h_s$ em vez de $p_{ss}$ violaria B1 e B2 sempre que $h_s<p_{ss}$ (Exemplo E4). ∎

### 8.3 Direção $B\Rightarrow A_{\text{unit}}$

Seja $(y,x)\in LP(B+K)$. Defina, para cada $s$, um mapa linear:

$$f^s_{uv}=\sum_{P\in\mathcal P_s:(u,v)\in A(P)}x_P,\qquad p_{st}=\sum_{P\in\mathcal P_s(t)}x_P,\qquad h_s=x_{(s)}\ (s\in S\cap T),$$
$$g^s_v=L^s_v(x)\ (v\ne s),\qquad g^s_s=0.$$

**Verificação** (Fato 8.2):

- **A1, $v\ne s$.** $\operatorname{in}_{f^s}(v)=\sum_{P:v\in\operatorname{int}P}x_P+\sum_{P\in\mathcal P_s(v)}x_P=g^s_v+p_{sv}$. Os caminhos que terminam em $v\ne s$ têm comprimento $\ge1$; se $v\notin T$, não há tais caminhos e $p_{sv}=0$.
- **A2, $v\ne s$.** $\operatorname{out}_{f^s}(v)=g^s_v$, que é o lado direito.
- **A1, $v=s$.** $\operatorname{in}_{f^s}(s)=0$, e $0+h_s=x_{(s)}=p_{ss}=p_{ss}+g^s_s$. Se $s\notin T$, ambos os lados são nulos.
- **A2, $v=s$.** $\operatorname{out}_{f^s}(s)=\sum_{P\in\mathcal P_s,|P|\ge1}x_P=1-x_{(s)}$ por B1. Logo $\operatorname{out}+h_s=1=1+g^s_s$.
- **A3.** $\sum_sp_{st}=1$ por B2.
- **A4.** Para $v\ne s$, $g^s_v=L^s_v\le y_v$ por B3. Para $v=s$, $g^s_s=0$.
- **A5.** $\sum_sg^s_v=\sum_sL^s_v\le\kappa_vy_v$ por B4.
- **A6** coincide com BK.
- **Domínios.** $f,g\ge0$. $p_{st}\le\sum_{P\in\mathcal P_s}x_P=1$. $h_s\in[0,1]$.

O acoplamento global A5 é exatamente B4 transportada pelo mapa. Nenhuma passagem usa integralidade. ∎

### 8.4 Conclusão e corolários

**Prova do Teorema 2.** Os §8.2 e §8.3 dão as duas inclusões **para o mesmo $y$**. A afirmação com B4/A5 restritas segue da Observação 4.2 e da Proposição 6.1. ∎

**Corolário 8.3 (MIP) [Provado].** Para $y\in\{0,1\}^V$, as fibras coincidem. Logo B e $A_{\text{unit}}$, com auxiliares contínuas, têm o mesmo conjunto de $y$ inteiros viáveis e o mesmo ótimo, igual ao OPT físico pelo Teorema 1.

**Corolário 8.4 ($B$ domina U) [Provado].** $\operatorname{proj}_yLP(B+K)\subseteq\operatorname{proj}_yLP(U+K)$.

*Prova.* Use o mapa do §8.3 e $F=\sum_sf^s$. Seja $G_v=\sum_sL^s_v$ e $\sigma_v=\mathbf 1[v\in S\cap T]\,x_{(v)}$. Então

$$\operatorname{in}_F(v)=b_v-\sigma_v+G_v,\qquad\operatorname{out}_F(v)=a_v-\sigma_v+G_v,$$

o que dá o balanço $\operatorname{out}-\operatorname{in}=a_v-b_v$. Além disso,

- $\operatorname{in}_F(v)\le b_v+\kappa_vy_v\le b_v+(m-b_v)y_v$;
- $\operatorname{out}_F(v)\le a_v+(m-a_v)y_v$;

pois $\kappa_v\le m-b_v$ e $\kappa_v\le m-a_v$ para todo $v$. ∎

A desigualdade de entrada em $v\in T\setminus S$ usa B4. B3 sozinha daria apenas $G_v\le my_v$.

Estrita: no Exemplo E2, $z_{LP}(U)=1/2<1=z_{LP}(B)$ sem K. Este corolário não depende dos Teoremas 2–3 de `provas-formulacao-a.md`, que ainda aguardam revisão.

**Observação 8.5 (consequências).**

1. **Força LP:** B não é mais forte nem mais fraca que $A_{\text{unit}}$; as projeções são idênticas.
2. **Valor ótimo LP:** idêntico, com ou sem K.
3. **Relação com A:** B é uma *representação* de $A(\mathcal B_{\text{unit}})$, o topo da hierarquia de refinamentos de A. Pelo Teorema 3 de `provas-formulacao-a.md`, ainda pendente de revisão, B domina $A(\mathcal B)$ para toda partição $\mathcal B$.
4. **Vantagem possível:** apenas de representação, sem as $m|A_r|$ variáveis $f$ e as $2mn$ linhas A1–A2. Isso **não implica** desempenho melhor (§12).

**Observação 8.6 (leitura de Dantzig–Wolfe).** Elimine $g$ de $A_{\text{unit}}$ pelo Lema 4.1(1). Para cada $s$, o poliedro $Q_s=\{(f^s,p_{s\cdot},h_s)\ge0:\ \text{A1–A2 de }s\}$ é um poliedro de fluxo com matriz de rede, portanto inteiro. Seus pontos extremos são de três tipos:

- caminhos simples de $s$ a $t\ne s$;
- o caminho zero $(s)$;
- as **caminhadas fechadas simples** $s\to\cdots\to s$ que terminam em $s$, quando $s\in T$.

Esse terceiro tipo é ponto extremo. Por exemplo, para $s\leftrightarrow u$, $f_{su}=f_{us}=1$, $p_{ss}=1$, $h_s=0$ é a única solução das restrições ativas. Os raios extremos são os ciclos que não passam por $s$.

B é a reformulação de DW que retém só os dois primeiros tipos. O terceiro tipo e os raios são dominados, pois o atalho reduz as cargas. Como $Q_s$ tem a propriedade de integralidade (Geoffrion [Citado]), já se esperava que a reformulação não fortalecesse o LP. O Teorema 2 confirma isso e mostra que o descarte das colunas dominadas não enfraquece a formulação. **Este é o ponto que `provas-formulacao-a.md` Teorema 4 e `as-01/validation.md` (limitação 2) deixaram para auditoria.**

---

## 9. Casos-limite

| Caso | Tratamento | Coberto por |
|---|---|---|
| $S\cap T\ne\varnothing$ | Caminho $(s)$; outros robôs podem terminar em $s$; troca de ocupantes permitida | §8.2 (peso $p_{ss}$), §8.3 ($h_s=x_{(s)}$); E4, E5 |
| Origem = destino ($\pi(s)=s$) | $(s)$, interior vazio, sem custo | Teorema 1; §8 |
| Caminho sem vértices internos | Arco direto $(s,t)$: carga zero em todos os vértices | Prova geral (Fato 8.2) |
| Várias recargas | Cada vértice interno recebe a carga | Prova geral |
| Estação compartilhada | B3 por origem (máximo) + B4 (total) | Prova geral; E2 |
| Frações de várias origens na mesma estação | Nenhum argumento usa integralidade | §8.2–§8.3; E1 |
| Caminhos por outras origens ou destinos | Permitidos em $\mathcal P_s$; exigem estação | Definição §5.1; E1 ($c\in T$ interno) |
| Grafos desconectados | Se $\mathcal P_s=\varnothing$ ou B2 é insatisfazível, os dois LPs são vazios. A igualdade dos conjuntos vale trivialmente. Nenhuma prova usa conexidade | Teorema 2; Proposição 6.3 |
| Instâncias inviáveis | $LP(B+K)=\varnothing$ ⇔ instância inviável (com $Z\ne\varnothing$) | Proposição 6.3 |
| Ciclos em soluções de fluxo | Só existem em A. Descartados sem aumentar cargas. Caminhadas fechadas em $s\in T$ vão para $(s)$ | Lema 8.1, §8.2; Observação 8.6; E4 |
| LP × inteiro | Equivalência ponto a ponto em $y$, válida para $y$ binário. Ambos exatos. Gap LP–OPT existe (E3) | Corolário 8.3; Teorema 1 |
| $m=1$ | $\kappa_v=0$ nos terminais; B4 trivial ($L=0$ nos terminais) | Prova geral |
| Métrica ponderada ou dirigida | Nenhuma prova usa a métrica | Observação 3.1 (rotular como extensão) |

### Exemplos verificáveis à mão

- **E1 (estrela; necessidade de B4).** Ver §6.5.
- **E2 (B ⊋ U; `direcoes-pli` §2.2a).** Arestas $s_1h$, $s_2h$, $ht_1$, $ht_2$, $s_1t_2$; $m=2$, $r=1$, sem K.
  - Em U: $s_1\to t_2$ direto e $s_2\to h\to t_1$ dão $\operatorname{in}(h)=1\le2y_h$, logo $y_h=1/2$ e $z_{LP}(U)=1/2$.
  - Em B: todo caminho de $s_2$ passa por $h$, já que $N^+(s_2)=\{h\}$ e $s_2\notin T$. Logo $L^{s_2}_h=1$, B3 dá $y_h\ge1$, e $z_{LP}(B)=1=OPT$.
  - Com K, C1 em $s_2$ já impõe $y_h\ge1$.
- **E3 (gap de B; sem K).** Arestas $ac$, $bc$, $ax$, $bx$, $xd$; $S=\{a,b\}$, $T=\{c,d\}$, $r=1$.
  - Todo caminho até $d$ tem $x$ interno, logo $\sum_sL^s_x\ge1$. B4 em $x$ (não terminal, $\kappa=2$) dá $y_x\ge1/2$, e o ponto $x_{ac}=x_{axd}=x_{bc}=x_{bxd}=1/2$, $y_x=1/2$ atinge esse valor. $z_{LP}(B)=1/2$.
  - $OPT=1$, porque sem estação $d$ é inalcançável.
  - Com K, C1 em $d$ impõe $y_x\ge1$.
- **E4 (caminhada fechada em $s\in S\cap T$).** $S=T=\{s\}$, $V=\{s,u\}$, arcos $s\leftrightarrow u$.
  - Ponto de $A_{\text{unit}}$: $f_{su}=f_{us}=1$, $p_{ss}=1$, $h_s=0$, $g_u=1$, $y_u=1$. É viável e é ponto extremo de $Q_s$.
  - A decomposição dá $e(s)=0$ e um único ciclo $s\to u\to s$. A construção do §8.2 dá $x_{(s)}=p_{ss}=1$, com $y_u=1$ ainda viável (carga 0).
  - Com $x_{(s)}=h_s=0$, B1 seria $0=1$.
  - Note que $y=0$ também é viável nas duas formulações; a projeção é $[0,1]$ em ambas.
- **E5 (troca; parecer Astra §5).** $G:a-v-b$, $S=\{a,v\}$, $T=\{v,b\}$, $r=1$.
  - Em B: $x_{av}=x_{vb}=1$, $y=0$, com cargas nulas e $z_{LP}=OPT=0$.
  - Cancelar $v$ dos dois conjuntos deixaria $a\to b$, que exige estação em $v$. Isso confirma que B não deve pré-processar $S\cap T$ por cancelamento.

---

## 10. Comparação com a F-h histórica

Fonte da F-h: `direcoes-pli-min-station.md` §8.1–§8.4 e a linha F-h da tabela do §9.

| Item | F-h histórica | B do Astra (§4.B) | B nesta análise |
|---|---|---|---|
| Colunas | "rotas de $s$ até algum destino", sem dizer se são simples nem incluir caminho zero. As derivações supõem $S\cap T=\varnothing$ (§0) | Caminhos simples em $H$, mais $(s)$ se $s\in T$, inclusive por terminais | Igual ao Astra. Caminhadas não mudam a projeção (Proposição 5.1) |
| Domínio | $\lambda_p\in[0,1]$ | $x_P\ge0$ | $x_P\ge0$ ($\le1$ implicado) |
| Atendimento da origem | $\sum\lambda=1$ ($\alpha_s$) | B1 | B1 |
| Atendimento do destino | $\sum\lambda=1$ ($\beta_t$) | B2 | B2, incluindo $(t)$ quando $t\in S$ |
| Ligação por origem | $\forall(s,v)$: $\sum\lambda\le y_v$ ($\gamma_{sv}$) | B3, $v\ne s$ | B3. A linha $v=s$ é vazia em ambos |
| Ligação global | **Ausente**. O §8.1 considera só *substituir* B3 por $\sum\lambda\le my_v$, o que reverte a $z_{LP}$ | B4, $\forall v$, coeficiente $\kappa_v$ | B4. Só $v\in T\setminus S$ importa (Proposição 6.1) |
| Cortes K | Não | Sim | Sim; a equivalência independe de K |
| Pricing | $\sum\gamma_{sv}-\alpha_s-\beta_t$ | $\sum(\gamma_{sv}+\mu_v)-\pi_s-\tau_t$ | Igual ao Astra; inclui $(s)$ e arcos diretos (§11) |
| LP | "= F-b". Não domina U (E1) | "= $A_{\text{unit}}$" (alegado) | $=A_{\text{unit}}$ (Teorema 2); $\subseteq$ U (Corolário 8.4) |
| Exatidão inteira | "Branching só em y [Provado]" | Implícita | Teorema 1, com $S\cap T$ |

**Preservado.** Colunas por origem, B1–B3, estrutura do pricing e a exatidão com ramificação só em $y$.

**Introduzido.** B4, K e o tratamento explícito de $S\cap T$ (caminho zero e destinos atravessáveis).

**Por que B4 foi proposta.** A desagregação por origem limita, em cada vértice, o máximo das cargas por origem, mas não a soma. Em $v\in T\setminus S$, a soma de B3 permite trânsito $my_v$, enquanto U exige $(m-1)y_v$ (restrição (E) de U). O próprio `direcoes-pli` §9 registra que F-b, sem as linhas agregadas, "pode violar $\operatorname{in}(t)\le1+(m-1)y_t$". Mesmo assim, §8.1 define F-h sem essas linhas.

**B4 corrige a deficiência?** Sim. Com B4, B ⊆ U (Corolário 8.4); sem B4, F-h ⊄ U (E1). Além disso, B4 é exatamente o necessário: basta impô-la em $T\setminus S$.

**Diferenças ainda não reconhecidas nos documentos anteriores:**

1. B4 é redundante fora de $T\setminus S$, e o mesmo vale para A5.
2. Na passagem A→B, o peso de $(s)$ é $p_{ss}$, não $h_s$, porque caminhadas fechadas em $s$ são pontos extremos de $Q_s$.
3. A afirmação da tabela §9 de que LP(F-h) = LP(F-b) concerne à versão sem ligação global. **Não confundir com LP(B) = LP($A_{\text{unit}}$).** A relação exata entre F-b com linhas agregadas e $A_{\text{unit}}$ não foi analisada aqui.

**Originalidade.** B não é inédita. É a F-h histórica do projeto acrescida da ligação global B4 e do tratamento de $S\cap T$. Formulações por caminhos com ligação desagregada são clássicas em projeto de redes de custo fixo, como reconhece o parecer Astra §3 (Gendron e Larose).

---

## 11. Estrutura de pricing

O pricing não é implementado aqui. A análise é conceitual.

### 11.1 Mestre completo e colunas

As colunas são $x_P$, $P\in\mathcal P$. O mestre contém:

- as variáveis $y$;
- B1, B2, B3, B4 (completa ou só em $T\setminus S$), BK e $y\le1$.

Forma normalizada, com o dual de cada linha:

| Linha | Forma | Dual |
|---|---|---|
| B1 | $\sum_{P\in\mathcal P_s}x_P=1$ | $\pi_s$ livre |
| B2 | $\sum_{P:e(P)=t}x_P=1$ | $\tau_t$ livre |
| B3 | $y_v-L^s_v\ge0$ | $\gamma_{sv}\ge0$ |
| B4 | $\kappa_vy_v-\sum_sL^s_v\ge0$ | $\mu_v\ge0$ |
| BK | $\sum_{Z}y\ge1$ | $\theta_Z\ge0$ |
| Limite de $y$ | $-y_v\ge-1$ | $\eta_v\ge0$ |

Dual:

$$\max\ \sum_s\pi_s+\sum_t\tau_t+\sum_Z\theta_Z-\sum_v\eta_v$$

sujeito a

$$\pi_s+\tau_t-\sum_{v\in\operatorname{int}P}(\gamma_{sv}+\mu_v)\le0\qquad(P\in\mathcal P_s(t)),$$
$$\sum_{s\ne v}\gamma_{sv}+\kappa_v\mu_v+\sum_{Z\ni v}\theta_Z-\eta_v\le1\qquad(v\in V).$$

### 11.2 Custo reduzido

$$\bar c_P=\sum_{v\in\operatorname{int}P}(\gamma_{sv}+\mu_v)-\pi_s-\tau_{e(P)}.$$

**Coincide com o parecer.** Se B4 for restrita a $T\setminus S$, faz-se $\mu_v:=0$ fora desse conjunto. Para $(s)$, $\bar c=-\pi_s-\tau_s$. Para um arco direto $(s,t)$, $\bar c=-\pi_s-\tau_t$.

### 11.3 O pricing é caminho mínimo com custos nos vértices

**Proposição 11.1 [Provado].** Seja $w_{sv}=\gamma_{sv}+\mu_v\ge0$, com $\gamma_{sv}:=0$ para linhas B3 ausentes. Seja $d_s(t)$ a distância de $s$ a $t$ em $H$ com comprimento de arco $\ell_s(u,v)=w_{su}$ se $u\ne s$ e $\ell_s(s,v)=0$. Então:

$$\min_{P\in\mathcal P_s}\bar c_P=-\pi_s+\min\Big\{\mathbf 1[s\in T](-\tau_s),\ \min_{t\in T\setminus\{s\}}\big(d_s(t)-\tau_t\big)\Big\}.$$

*Prova.* Para um caminho simples $P$ de $s$ a $t$, o comprimento é $\sum_{v\in\operatorname{int}P}w_{sv}$. Para uma caminhada, o comprimento é maior ou igual ao do seu atalho (Lema 3.3, com pesos não negativos). Logo a distância mínima sobre caminhadas, calculada por Dijkstra porque $\ell\ge0$, é atingida por um caminho simples de $\mathcal P_s(t)$. O termo $-\tau_t$ é constante por destino e é somado depois do Dijkstra, de modo que $\tau$ livre não cria pesos negativos. ∎

O custo é um Dijkstra por origem, ou seja, $O(m(|A_r|+n\log n))$ por rodada de pricing.

Os custos dependem da origem através de $\gamma_{sv}$, e por isso **não há uma árvore única compartilhada** entre as origens.

**Dependências globais.** B2 ($\tau$) e B4 ($\mu$) acoplam as origens, mas entram no custo reduzido como constantes duais nos vértices e nos extremos. Não inviabilizam a decomposição por origem. BK envolve só $y$ e não entra no pricing. Não há restrição de recurso no caminho, porque a autonomia já está em $H$. **O pricing do Astra decorre corretamente da formulação.**

### 11.4 Limite dual (`design.md` item 3)

**Proposição 11.2 [Provado].** Sejam $\pi,\tau$ quaisquer e $\gamma,\mu,\theta\ge0$ quaisquer, com zero nas linhas ausentes. Defina

$$\eta_v=\max\Big\{0,\ \kappa_v\mu_v+\sum_{s\ne v}\gamma_{sv}+\sum_{Z\ni v}\theta_Z-1\Big\},\qquad L=\sum\pi+\sum\tau+\sum\theta-\sum\eta.$$

Se $\ell_s\le\min_{P\in\mathcal P_s}\bar c_P$ para todo $s$, então

$$LB=\max\{0,\ L+\textstyle\sum_s\min(0,\ell_s)\}\le z_{LP}(B+K)\le OPT.$$

*Prova.* Tome $\pi'_s=\pi_s+\min(0,\ell_s)$. Para $P\in\mathcal P_s(t)$,

$$\pi'_s+\tau_t-\sum(\gamma+\mu)=-\bar c_P+\min(0,\ell_s)\le-\ell_s+\min(0,\ell_s)\le0.$$

As restrições de $y$ valem pela definição de $\eta$, e $\eta\ge0$. Logo $(\pi',\tau,\gamma,\mu,\theta,\eta)$ é dual viável, e a dualidade fraca dá $L+\sum\min(0,\ell_s)\le z_{LP}$. Além disso, $z_{LP}\ge0$, e $z_{LP}\le OPT$ porque toda solução inteira é viável no LP. Se o LP for vazio, $z_{LP}=+\infty$ e a desigualdade é trivial. ∎

**Condições explícitas:**

1. $\ell_s$ deve cobrir todo $\mathcal P_s$, inclusive $(s)$ e arcos diretos.
2. Duais negativos de $\gamma,\mu,\theta$ devem ser projetados em 0 **antes** de calcular $\ell_s$.
3. A validade não exige duais ótimos. Avaliar $L$ e $\ell_s$ em aritmética exata basta para um certificado racional.
4. Isso confirma o AS08-05: o objetivo do RMP sozinho não é limite inferior global.
5. A orientação dos duais devolvidos pelo solver precisa ser conferida na documentação da versão usada, na T2/T3. Ela não é preenchida aqui de memória.

### 11.5 Linhas B3 acopladas às colunas

Se o RMP contiver todas as linhas $(s,v)$ com $v$ interno a alguma coluna presente de $s$, então:

- as linhas ausentes são $0\le y_v$, vazias, e o RMP é exatamente a restrição do mestre completo às colunas presentes. Seu valor é limite **superior** de $z_{LP}$;
- estender os duais com $\gamma=0$ nas linhas ausentes dá um dual completo, e a condição "nenhuma coluna com $\bar c<0$" certifica a otimalidade (Proposição 11.2 com $\ell_s\ge0$).

A geração simultânea de linhas e colunas é, portanto, compatível com B (cf. Muter, Birbil e Bülbül [Citado]). **O algoritmo não é desenvolvido aqui.**

---

## 12. Escalabilidade teórica

Notação: $a=|A_r|$, $h=|S\cap T|$, $\Pi=|\mathcal P|$.

| Componente | $A_{\text{unit}}$ | B completa | B com geração de colunas e linhas |
|---|---|---|---|
| $y$ | $n$ | $n$ | $n$ |
| Fluxo / colunas | $ma$ ($f$) $+\,mn$ ($g$) $+\,m^2$ ($p$) $+\,h$ | $\Pi$, que pode ser exponencial | Colunas geradas |
| Conservação | $2mn$ (A1, A2) | — | — |
| Atendimento | $m$ (A3) | $2m$ (B1, B2) | $2m$ |
| Ligação por origem | $mn$ (A4) | $\le m(n-1)$ (B3) | B3 só para pares tocados por colunas |
| Ligação global | $n$ (A5), $m-h$ úteis | $n$ (B4), $m-h$ úteis | $m-h$ |
| K | $|K|$ | $|K|$ | $|K|$ |
| Não zeros por coluna | — | $2+|\operatorname{int}P|+|\operatorname{int}P\cap(T\setminus S)|$ | idem |

**Número de caminhos.** Com $H$ completo ($r\ge$ diâmetro), $|\mathcal P_s(t)|=\sum_{k=0}^{n-2}\frac{(n-2)!}{(n-2-k)!}=\lfloor e\,(n-2)!\rfloor$. A representação completa é inviável em geral; só a implícita faz sentido.

**Linhas B3.** O pré-processamento por alcançabilidade (eliminar $(s,v)$ se não houver caminho de $s$ a $v$ e de $v$ a $T$) é válido. Mas em $H$ simétrico e conexo ele quase não remove nada. O risco principal é o número de linhas B3, não o de colunas.

**Tamanhos.** São estimativas a partir de $n$, $m$ e `n_arcos_alcance` do `instances/manifest.csv`, todos conferidos nesta análise. Não são medições de modelos construídos.

| Instância | $n$ | $m$ | $a$ | $ma$ | Variáveis $A_{\text{unit}}$ | Linhas $A_{\text{unit}}$ ($3mn+m+n$) | Linhas B3 $m(n-1)$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `puc-hc11p-seed-r1` | 2.048 | 512 | 22.528 | 11.534.336 | 12.847.104 | 3.148.288 | 1.048.064 |
| `puc-hc12p-seed-r1` | 4.096 | 1.024 | 49.152 | 50.331.648 | 55.578.624 | 12.588.032 | 4.193.280 |
| `puc-w3c571-seed-r1` | 3.997 | 1.142 | 20.556 | 23.474.952 | 29.347.687 | 13.698.861 | 4.563.432 |
| `mapf-den312d-m50-f2-rho` | 2.445 | 50 | 549.696 | 27.484.800 | 27.612.000 | 369.245 | 122.200 |
| `mapf-random-64-64-20-m100-f4` | 3.270 | 100 | 121.632 | 12.163.200 | 12.503.470 | 984.370 | 326.900 |
| `pucn-cc7-3n-regiao-f2` | 2.187 | 111 | 214.326 | 23.790.186 | 24.047.451 | 730.569 | 242.646 |
| `vienna-I056-regiao-f4` | 1.991 | 25 | 381.600 | 9.540.000 | 9.592.391 | 151.341 | 49.750 |

As variáveis de $A_{\text{unit}}$ são contadas como $n+ma+mn+m^2+h$, com $h=0$, exceto em `den312d`, onde $\rho_{S\cap T}=0{,}1$ dá $h=5$.

O parecer Astra §6 cita "4.564.574 ligações" em w3c571. Esse valor é $m\cdot n$; excluindo as linhas vazias $v=s$, ficam $m(n-1)=4.563.432$. A tabela do §6 escreve "até $m(n-1)$ ligações **por origem**", mas $m(n-1)$ é o total; por origem são $n-1$.

**Leitura.**

- Nos regimes MAPF/Vienna ($m$ pequeno, $a$ grande), B troca até ~27 milhões de variáveis $f$ por $\le$ ~$10^5$ linhas B3. **É o regime em que a representação pode compensar.**
- Nos regimes PUC ($m$ grande, $a$ esparso), B3 completa tem milhões de linhas. Só a geração de linhas acoplada às colunas evita isso. O número final de linhas necessárias depende de quantos vértices distintos as colunas geradas atravessam por origem, o que é **desconhecido**.
- Degenerescência (muitas colunas de custo zero, $y$ degenerado), *tailing-off* e custo de m Dijkstras por rodada são riscos conhecidos da literatura de projeto de redes. Não foram quantificados.

**Nada aqui permite afirmar superioridade computacional de B.**

---

## 13. Lacunas, riscos, auditoria e divergências

### 13.1 Auditoria (itens do §9 do pedido)

| Verificação | Resultado |
|---|---|
| Restrições faltantes | Nenhuma para a equivalência com $A_{\text{unit}}$ nem para a exatidão inteira. $p\le1$ e $x\le1$ são implicados |
| Restrições redundantes | B4/A5 fora de $T\setminus S$ (Observação 4.2, Proposição 6.1); linhas B3 com $v=s$ (vazias) |
| Restrições incorretas | Nenhuma |
| Dependência circular | Nenhuma. O Teorema 2 usa só Lema 3.3, Lema 4.1, Lema 8.1 e o Fato 8.2. O Teorema 1 usa Birkhoff. Nenhum dos dois usa a exatidão de U nem os Teoremas 1–4 de `provas-formulacao-a.md` |
| Hipóteses não declaradas | $H$ sem laços (vale por construção de $A_r$); $Z\neq\varnothing$ em K (Proposição 6.3); K depende só de $y$ |
| Integralidade usada indevidamente em LP | Não. O Teorema 1 é o único que usa $y$ binário, e está separado do Teorema 2 |
| Fluxo por origem × agregado | Separados. U só aparece no Corolário 8.4 |
| Ativação individual × global | B3/A4 contra B4/A5, tratadas separadamente no §8 |
| Ciclos e caminhos de comprimento zero | Tratados (Lema 8.1, §8.2, Observação 8.6, E4) |

### 13.2 Divergências entre fontes (registradas, não reconciliadas silenciosamente)

1. **`direcoes-pli` §8.1 × §9.** A F-h não tem ligação global, e o §9 reconhece que F-b sem linhas agregadas viola U nos destinos. A F-h, tal como está escrita, não domina U (E1).
2. **`direcoes-pli` §0** supõe $S\cap T=\varnothing$ nas derivações. B trata $S\cap T$ explicitamente. As conclusões históricas sobre F-h não cobrem $S\cap T$.
3. **Parecer Astra §4.B** impõe B4 para todo $v\in V$. Só $T\setminus S$ importa. Não é erro.
4. **Parecer Astra §6.** "m(n−1) ligações por origem" deveria ser "no total"; 4.564.574 equivale a $mn$ (§12).
5. **`provas-formulacao-a.md` Teorema 4.** O esboço está correto. Este documento completa a parte das caminhadas que retornam a $s$ e explicita que o peso de $(s)$ é $p_{ss}$.
6. **Métrica.** O documento de A fala em $r$ medido em arestas; o código admite pesos. Os resultados valem para os dois casos (Observação 3.1).

### 13.3 Lacunas e riscos que permanecem

- **Revisão independente** (autor ≠ verificador), exigida pelo protocolo da AS-08, ainda **pendente**.
- **Necessidade de B4 com o K real.** Não foi demonstrada; o exemplo E1 é fechado por C1.
- **Ganho de B sobre $A(\mathcal B)$ com poucos grupos.** Fora do escopo. A única testemunha é Sec59, do parecer Astra, e $z_{LP}(\text{F-CC}+K)=5$ e $OPT=7$ estão [Não verificados] aqui.
- **Cadeia F-CC+K ≥ B+K** (`relacoes-lp-formulacao-a.md`) e **dominância de B sobre a "proposta anterior de cortes"** (parecer Astra §5): [Não verificadas] aqui.
- **Sinais dos duais no solver.** Verificar na documentação da versão do Gurobi usada (T2).
- **Escalabilidade de B3.** Ainda é questão aberta; não pode ser inferida do LP teórico (AS08-06).
- **RMP inicial.** Precisa ser viável (variáveis artificiais ou colunas iniciais); é decisão de implementação (T2), não analisada aqui.

### 13.4 Ajustes recomendados para as tarefas seguintes

Os ajustes abaixo não alteram a formulação; são observações para T2–T4.

1. Impor B4 só em $T\setminus S$ ($m-h$ linhas). O LP é idêntico (Proposição 6.1).
2. O oráculo deve incluir $(s)$ e arcos diretos, e usar $\gamma_{sv}=0$ para linhas B3 ausentes.
3. Associar a criação de linhas B3 à criação de colunas (§11.5).
4. Testes de T1/T2 sugeridos pelos exemplos:
   - E1–E5;
   - $\operatorname{proj}_y$ de B contra $A_{\text{unit}}$ (via `compile_a` com grupos unitários) em instâncias pequenas com $S\cap T$;
   - $LP(B)\ge LP(U)$.

---

## 14. Conclusão e recomendação de continuidade

**Conclusões demonstradas:**

1. B, definida por B1–B4 sobre caminhos simples e o caminho de comprimento zero, é exata para $y$ binário com $x$ contínuo (Teorema 1).
2. $\operatorname{proj}_yLP(B+K)=\operatorname{proj}_yLP(A_{\text{unit}}+K)$ ponto a ponto em $y$, portanto também no MIP (Teorema 2, Corolário 8.3).
3. B domina U em projeção, possivelmente de forma estrita (Corolário 8.4, E2).
4. B4 é necessária para a equivalência (E1) e é não redundante só em $T\setminus S$ (Proposição 6.1).
5. O pricing é um caminho mínimo por origem com custos não negativos nos vértices (Proposição 11.1).
6. O limite dual do design é válido por dualidade fraca, sob as condições do §11.4 (Proposição 11.2).

**Equivalência matemática não é equivalência computacional.** B não oferece LP mais forte que $A_{\text{unit}}$. Seu único possível ganho é de representação, e ele depende do número de linhas B3 efetivamente necessárias, da degenerescência e do custo do pricing. Nada disso está medido.

**Recomendação.**

- Considerar AS08-01, AS08-02 e AS08-03 **matematicamente atendidos, sujeitos à revisão independente** exigida pelo protocolo.
- Manter a condição de gatilho da spec: só prosseguir para T2 (pricing) se AS-05/AS-06 indicarem que A precisa de muitos grupos.
- Se prosseguir, implementar primeiro um verificador em instâncias pequenas que compare B por enumeração de caminhos com `compile_a` unitária e com U, antes de qualquer piloto de desempenho.
- Não iniciar T2–T4 nesta etapa.

**Classificação final:**

**EQUIVALÊNCIA DEMONSTRADA**
