# Provas F-CC / F-C3 (F2)

**Data:** 2026-10-06
**Spec:** `specs/proxima-fase-b-formulacoes-fcc-fc3/spec.md`

Cada proposição P1–P11 recebe exactamente um rótulo. Nada marcado
`HYPOTHESIS` ou `OPEN` é usado como facto em F3. Cruzamento computacional
de P1 e P7: `experiments/alternative-formulations/verify_fcc.py`.

Notação comum: \(H=G^r\), \(B(W)\), \(D\), \(Q\) como em
`formulacao-fcc-configuracoes-conectadas.md`. Núcleo = IP em \(y\) com
C1+C2+C4-DM. \(\Gamma=\mathrm{OPT}-\)núcleo.

---

## P1 — F-CC é exata para \(y\) binário

**Rótulo: `PROVEN`**

**Enunciado.** Com \(y\in\{0,1\}^V\), o modelo F-CC é viável se e só se
\(C=\{v:y_v=1\}\) é um conjunto viável do MIN-STATION de Das (robôs não
rotulados, autonomia \(r\) em passos, estações em todo \(V\), \(S\cap T\)
permitido).

**Prova.**

(\(\Rightarrow\)) Seja \((y,\lambda,d)\) viável com \(y\) binário e
\(C=\{v:y_v=1\}\). Por R3, \(\lambda_q>0\) implica \(W_q\subseteq C\).
Como \(H[W_q]\) é conexo, \(W_q\) está contido numa componente conexa
\(K\) de \(H[C]\), e \(B(W_q)\subseteq B(K)\).

Defina o grafo bipartido \(B_C\) com partes \(S\) e \(T\) e aresta \(st\)
quando (i) \((s,t)\in D\), ou (ii) existe componente \(K\) de \(H[C]\) com
\(s,t\in B(K)\). R1 e R2 dizem que \(\lambda\) e \(d\) realizam um
emparelhamento perfeito fracionário de \(B_C\): cada \(d_{st}\) usa uma
aresta do tipo (i); cada \(\lambda_q\) com \(s\in I_q\), \(t\in J_q\) usa
arestas do tipo (ii) (todas com o mesmo \(K\supseteq W_q\)). O politopo
de emparelhamento bipartido é integral, portanto existe emparelhamento
perfeito inteiro em \(B_C\).

Resta ver que cada aresta de \(B_C\) é uma rota realizável em \(G\) com
estações \(C\). Tipo (i): \(d_G(s,t)\le r\), incluindo \(s=t\)
(permanência: \(d_G(s,s)=0\le r\), coberta por \(d_{ss}\) quando
\(s\in S\cap T\)). Tipo (ii): \(s\) alcança algum \(w\in K\) em no máximo
\(r\) passos (porque \(s\in B(K)\)); há uma caminhada em \(H[K]\) entre
estações de \(K\) (cada aresta de \(H\) é um salto \(\le r\) com recarga
nos extremos); o último vértice de \(K\) alcança \(t\) em no máximo \(r\)
passos. Logo o emparelhamento inteiro é uma solução física.

(\(\Leftarrow\)) Seja \(C\) viável. Cada robô usa ou um salto directo
\(s\to t\) com \(d_G(s,t)\le r\) (permanência se \(s=t\)), ou uma sequência
de saltos com recarga em vértices de \(C\). No segundo caso, as estações
visitadas formam uma caminhada em \(H[C]\), logo residem numa só
componente \(K\). Dois vértices de \(C\) com \(d_G\le r\) são adjacentes
em \(H\); portanto um mesmo caminho não usa duas componentes. Agrupe os
robôs que recarregam na componente \(K\) numa configuração
\(q=(K,I_K,J_K)\) com \(|I_K|=|J_K|\). Ponha \(\lambda_q=1\) nessas
configurações, \(d_{st}=1\) nos pares directos do emparelhamento, e
\(y=1_C\). R1–R3 valem.

**Cruzamento:** em Direct0, TermRelay, StayPut, StayPutIsolado, CaminhoABC
e SharedTerminal, para todo \(C\subseteq V\), `fcc_y_viavel` coincide com
`viavel`.

---

## P2 — \(z_{\mathrm{LP}}(\mathrm{base})\le z_{\mathrm{LP}}(\mathrm{F\text{-}CC})\)

**Rótulo: `PROVEN`**

**Enunciado.** Toda solução viável da relaxação da F-CC induz uma solução
viável da relaxação da base com o mesmo \(y\). Logo o mínimo da F-CC é
pelo menos o da base.

**Prova.** Seja \((y,\lambda,d)\) viável no LP da F-CC. Construa fluxo
agregado em \(A_r\). Para cada \((s,t)\in D\) com \(s\neq t\), envie
\(d_{st}\) pelo arco \((s,t)\in A_r\). Para \(s=t\), o peso \(d_{ss}\) não
gera fluxo (permanência). Para cada \(q=(W,I,J)\), escolha uma raiz
\(w_q\in W\) e, para cada \(s\in I_q\), um \(w_s\in W\) com \(d_G(s,w_s)\le r\)
(existe porque \(s\in B(W)\)); análogo \(w_t\) para cada \(t\in J_q\).
Envie \(\lambda_q\) ao longo de \(s\to w_s\), depois ao longo de uma
caminhada em \(H[W]\) de \(w_s\) a \(w_t\) (saltos de \(A_r\)), depois
\(w_t\to t\). Conservação: cada origem emite o total
\(\sum_{q:s\in I_q}\lambda_q+\sum_t d_{st}=1\) (R1), cada destino absorve 1
(R2), vértices internos conservam.

Activação da base em \(v\): o fluxo que entra (sai) em \(v\) só usa
configurações com \(v\in W_q\) ou um salto directo que termina (começa)
em \(v\). A quantidade total que transita por \(v\) via configurações é
no máximo \(m\sum_{q:v\in W_q}\lambda_q\le m y_v\) (R3 e \(|I_q|\le m\)).
A restrição de entrada da base pede
\(\mathrm{in}(v)\le b_v+(m-b_v)y_v\) com \(b_v\in\{0,1\}\). Vale
\(m y_v\le b_v+(m-b_v)y_v\) para todo \(y_v\in[0,1]\), porque
\(b_v y_v\le b_v\). O salto directo que chega a um destino conta na parcela
\(b_v\) e não exige estação. O caso da saída é simétrico
(\(a_v\) no lugar de \(b_v\)). Portanto \((y,f)\) é viável na relaxação da
base e tem o mesmo custo.

**Cruzamento:** F3 aborta se `lp_fcc < lp_base - 1e-6` (`P2_REFUTADO`).

---

## P3 — o LP da F-CC implica C1

**Rótulo: `COMPUTATIONALLY VERIFIED` (argumento escrito; não extraído como
corte contra a solução F-CC em F3)**

**Enunciado.** Toda solução do LP da F-CC satisfaz os cortes C1 de
`cuts.generate_C1`.

**Prova.** C1, lado das origens: se \(s\in S\setminus T\) e
\(N^+(s)\cap T=\varnothing\) (nenhum destino a distância \(\le r\)), então
não existe \((s,t)\in D\). R1 reduz-se a \(\sum_{q:s\in I_q}\lambda_q=1\).
Se \(s\in I_q\), então \(s\in B(W_q)\), logo existe \(w\in W_q\) com
\(d_G(s,w)\le r\). Como \(s\notin W_q\) ou, se \(s\in W_q\), o próprio \(s\)
está em \(N^+(s)\)? Distância 0: \(s\in W_q\) implica \(s\in C\), e
\(s\in N^+(s)\) não: \(N^+(s)\) são vizinhos em \(A_r\), \(u\neq s\). Se
\(s\in W_q\), R3 dá \(\lambda_q\le y_s\). Se \(s\notin W_q\), o primeiro
salto de recarga está em \(N^+(s)\). Em ambos os casos cada configuração
que atende \(s\) cobra pelo menos uma estação em \(N^+(s)\cup\{s\}\).

C1 escrito no código é \(y(N^+(s))\ge 1\) **sem** incluir \(s\), e só quando
\(N^+(s)\cap T=\varnothing\) e \(N^+(s)\neq\varnothing\). Se o atendimento
usa \(s\) como estação e nenhum vértice de \(N^+(s)\), C1 poderia falhar.
Isso só é possível se \(s\in W_q\) e \(s\) alcança \(T\) via estações em
\(W_q\) sem o primeiro salto sair para \(N^+(s)\) — o primeiro salto a
partir de \(s\in C\) vai a algum \(v\in N^+(s)\cap W_q\), portanto
\(N^+(s)\) contém uma estação da mesma configuração. Somando R3 nesses
vértices: \(\sum_{v\in N^+(s)} y_v \ge \sum_{v\in N^+(s)}\sum_{q:v\in W_q}\lambda_q \ge \sum_{q:s\in I_q}\lambda_q=1\),
porque cada tal \(q\) tem pelo menos um vértice de \(W_q\) em \(N^+(s)\)
(o primeiro salto a partir de \(s\), ou um vizinho em \(H[W_q]\)). Se
\(W_q=\{s\}\), então \(T\cap B(\{s\})\neq\varnothing\) para \(J_q\neq\varnothing\),
logo algum \(t\in N^+(s)\cap T\), contradizendo a hipótese de C1. Portanto
\(|W_q|\ge 2\) ou o primeiro salto existe em \(N^+(s)\). O lado dos destinos
é simétrico.

---

## P4 — o LP da F-CC implica C2

**Rótulo: `COMPUTATIONALLY VERIFIED` (argumento de banda escrito; F3 não
testa violação de C2 na solução F-CC)**

**Enunciado.** Toda solução do LP da F-CC satisfaz os cortes C2 (bandas de
distância).

**Prova.** Para \(s\in S\setminus T\) com \(D_s=\min_{t\in T}d_G(s,t)>r\),
não há par directo. Qualquer configuração que atenda \(s\) tem \(W_q\)
conexo em \(H\) e \(s\in B(W_q)\). Uma caminhada de \(s\) até um destino
em \(B(W_q)\) atravessa cada banda \((a,a+r]\) com \(a+r<D_s\). A
conectividade em \(H\) força pelo menos uma estação da configuração em
cada banda (senão um salto de comprimento \(\le r\) saltaria a banda,
contradizendo a definição da banda). Somando R3 na banda:
\(y(\mathrm{banda})\ge\sum_{q:s\in I_q}\lambda_q=1\). Destinos: simétrico.

---

## P5 — C4 só parcialmente

**Rótulo: `HYPOTHESIS`**

O argumento de planejamento dá \(y(Z)\ge\delta/|S'|\) no LP da F-CC, não
necessariamente \(y(Z)\ge 1\) (C4-DM). Não há prova nem refutação no
repositório. F3 não usa P5.

---

## P6 — relação com \(\mathrm{LP}_{cov}\) sobre \(\mathcal{Z}\)

**Rótulo: `OPEN`**

Não há definição fechada neste repositório da família \(\mathcal{Z}\)
relativa à F-CC. F3 não usa P6.

---

## P7 — forma separada \(\lambda_W,\alpha,\beta\) tem o mesmo LP que a F-CC

**Rótulo: `PROVEN`**

**Enunciado.** Seja \(z_Q\) o valor do LP com variáveis \(\lambda_q\)
indexadas por \(Q=\{(W,I,J)\}\) e \(z_{\mathrm{sep}}\) o LP com
\(\lambda_W\), \(\alpha_{sW}\le\lambda_W\), \(\beta_{tW}\le\lambda_W\),
\(\sum_s\alpha_{sW}=\sum_t\beta_{tW}\), e as mesmas R1–R3 em termos de
\(\alpha,\beta,\lambda_W\). Então \(z_Q=z_{\mathrm{sep}}\).

**Prova.** (\(z_{\mathrm{sep}}\le z_Q\)) Dada \(\lambda_q\), ponha
\(\lambda_W=\sum_{I,J}\lambda_{(W,I,J)}\),
\(\alpha_{sW}=\sum_{I\ni s,J}\lambda_{(W,I,J)}\),
\(\beta_{tW}=\sum_{J\ni t,I}\lambda_{(W,I,J)}\). As caixas
\(\alpha\le\lambda_W\) valem porque cada \(\lambda_{(W,I,J)}\) com \(s\in I\)
é parcela de \(\lambda_W\). O equilíbrio \(\sum\alpha=\sum\beta\) é
\(\sum_{I,J}|I|\lambda=\sum_{I,J}|J|\lambda\). R1–R3 passam.

(\(z_Q\le z_{\mathrm{sep}}\)) Fixe \(W\) com \(\lambda_W>0\). Seja
\(a_s=\alpha_{sW}/\lambda_W\in[0,1]\) para \(s\in S\cap B(W)\) (zero fora),
e \(b_t\) análogo. Então \(\sum a=\sum b\). O politopo
\(P=\{(a,b)\in[0,1]^{S'}\times[0,1]^{T'}:\sum a=\sum b\}\) tem vértices
inteiros: a matriz da igualdade é TU com limites de caixa; num vértice,
no máximo uma coordenada é fracionária, e a igualdade força essa
coordenada a ser inteira. Todo ponto de \(P\) é combinação convexa de
vértices \((1_I,1_J)\) com \(|I|=|J|\). Distribuindo \(\lambda_W\) por
esses vértices obtêm-se \(\lambda_{(W,I,J)}\) que reproduzem \(\alpha,\beta\).
Se \(\lambda_W=0\), então \(\alpha=\beta=0\). R1–R3 e o objectivo em \(y\)
não mudam.

**Cruzamento:** `verify_fcc.py` compara os dois LPs nas seis instâncias de
P1; diferença \(<10^{-6}\).

F3 pode portanto medir F-CC na forma separada.

---

## P8 — \(z_{\mathrm{LP}}(\mathrm{F\text{-}CC})\le z_{\mathrm{LP}}(\mathrm{F\text{-}C3})\le\mathrm{OPT}\)

**Rótulo: `HYPOTHESIS`** (redes de trios `OPEN`)

Sem a definição das redes, F-C3 não é um modelo. A desigualdade da
esquerda para a **forma separada** é igualdade (P7), não um fortalecimento.
F3 não mede F-C3.

---

## P9 — em SC-GF2 o LP da F-CC iguala o LP de set-cover

**Rótulo: `HYPOTHESIS`** até F3; o esboço abaixo não fecha a igualdade.

**Esboço (não prova).** Em SC-GF2 cada estação \(w_a\) cobre um conjunto
de origens; configurações de uma estação com pesos \(2^{-(k-1)}\)
reproduzem o LP de cobertura, valor \(n/2^{k-1}\) (\(1{,}75\) para \(k=3\),
não \(\approx 2\)). Isso mostra \(z_{\mathrm{LP}}(\mathrm{F\text{-}CC})\le z_{\mathrm{SC}}\).
A desigualdade inversa não está escrita. F3 **mede** os dois valores no
controle negativo e trata qualquer F-CC estritamente acima do LP de
set-cover como erro a investigar, não como ganho.

---

## P10 — permanência em \(S\cap T\) é \(d_{ss}\)

**Rótulo: `PROVEN`** (corolário de P1)

\(d_G(s,s)=0\le r\), logo \((s,s)\in D\) para todo \(s\in S\cap T\). R1 e
R2 aceitam \(d_{ss}=1\) sem estação. Nenhuma configuração é necessária
para o robô que permanece. Teste: StayPut e StayPutIsolado, OPT \(=0\),
F-CC viável com \(y=0\).

---

## P11 — valores 20/15 vértices e família \(1{,}5g\) vs \(2g\)

**Rótulo: `HYPOTHESIS`**

Instâncias não definidas no repositório. Redes F-C3 `OPEN`. Sem
reconstrução, F3 não compara. Condição de checagem: ver
`formulacao-fc3-consistencia-trios.md` §4.

---

## Tabela

| # | Rótulo |
|---|---|
| P1 | `PROVEN` |
| P2 | `PROVEN` |
| P3 | `COMPUTATIONALLY VERIFIED` |
| P4 | `COMPUTATIONALLY VERIFIED` |
| P5 | `HYPOTHESIS` |
| P6 | `OPEN` |
| P7 | `PROVEN` |
| P8 | `HYPOTHESIS` |
| P9 | `HYPOTHESIS` (medição em F3) |
| P10 | `PROVEN` |
| P11 | `HYPOTHESIS` |
