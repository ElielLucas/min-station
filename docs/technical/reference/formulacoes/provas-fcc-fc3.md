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

**Rótulo: `PROVEN` — prova reescrita em N1-T1 (2026-10-07).**

**Enunciado.** Toda solução do LP de F-CC induz um fluxo não negativo
factível para a relaxação da baseline U, preservando o mesmo \(y\) e o
objetivo. Isso não afirma que os politopos nas variáveis auxiliares coincidem.

**Prova.** Fixe \((y,\lambda,d)\) viável para F-CC. Para cada configuração
\(q=(W_q,I_q,J_q)\), ponha \(k_q=|I_q|=|J_q|\) e escolha **uma bijeção**
\(\pi_q:I_q\to J_q\). Para cada \(s\in I_q\), como ambos os terminais
estão em \(B(W_q)\) e \(H[W_q]\) é conexo, existe caminho em \(H\) de
\(s\) a \(\pi_q(s)\) cujos vértices internos estão em \(W_q\). Escolha
**caminho simples**; um par coincidente \(s=t\) usa caminhada de comprimento
zero. Envie \(\lambda_q\) por esse caminho. Para cada \((s,t)\in D\),
\(s\ne t\), envie \(d_{st}\) no arco direto; \(d_{ss}\) não gera arco.
Somando caminhos obtemos fluxo \(f\ge0\). Cada caminho não trivial de
\(s\) a \(t\) contribui \(+1\) ao balanço em \(s\), \(-1\) em \(t\) e
zero em todos os outros vértices. R1 e R2 implicam, inclusive no caso
\(S\cap T\ne\varnothing\),
\(\operatorname{out}(v)-\operatorname{in}(v)=a_v-b_v\), com
\(a_v=1_{v\in S}\), \(b_v=1_{v\in T}\).

**Ativação de entrada.** Defina chegada final como a contribuição do último
arco de um caminho cuja extremidade final é \(v\). Se \(v\in T\), seu
peso total é no máximo 1 por R2 (e pode ser menor quando há permanência).
Se \(v\notin T\), não há chegada final em \(v\). Toda outra entrada é
**trânsito** e deve passar por um vértice interno de \(W_q\); caminhos
simples garantem no máximo uma entrada em \(v\) por robô. Em uma
configuração com \(v\in W_q\), se \(v\in J_q\), exatamente um dos
\(k_q\) robôs termina em \(v\), logo no máximo \(k_q-1\le m-1\)
atravessam \(v\) em trânsito. Se \(v\notin J_q\) **e** \(v\in T\),
\(k_q\le m-1\), pois \(J_q\subseteq T\setminus\{v\}\). Portanto,
para \(v\in T\), o trânsito total é no máximo
\((m-1)\sum_{q:v\in W_q}\lambda_q\le(m-1)y_v\) por R3;
somado à chegada final, dá
\(\operatorname{in}(v)\le 1+(m-1)y_v\).

Se \(v\notin T\), cada configuração que transita em \(v\) tem
\(k_q\le m\), logo
\(\operatorname{in}(v)\le m\sum_{q:v\in W_q}\lambda_q\le my_v\).
Observe que o argumento inclui explicitamente entradas em destinos
\(t\in J_q\setminus W_q\): são **chegadas finais gratuitas**, não
trânsito, e sua soma está coberta por R2. Os demais caminhos não podem
visitar esses destinos fora de \(W_q\) como vértices internos.

**Ativação de saída.** É simétrica, mas com os papéis invertidos: a primeira
saída em cada \(s\in S\) tem peso total no máximo 1 por R1; para
\(v\in S\cap W_q\), se \(v\in I_q\), um dos \(k_q\) caminhos parte de
\(v\) e no máximo \(k_q-1\) passam em trânsito; se \(v\notin I_q\)
e \(v\in S\), então \(k_q\le m-1\). Segue
\(\operatorname{out}(v)\le 1+(m-1)y_v\) se \(v\in S\),
e \(\operatorname{out}(v)\le my_v\) caso contrário.
Terminais que desempenham simultaneamente os papéis de origem e destino
recebem as duas contagens gratuitas **separadamente**, como exige a U.

As quatro ativações são exatamente
\(\operatorname{in}(v)\le b_v+(m-b_v)y_v\) e
\(\operatorname{out}(v)\le a_v+(m-a_v)y_v\); logo \((y,f)\)
é factível no LP da baseline U, com mesmo custo. \(\square\)

**Nota de evidência.** Esta é uma prova escrita, não um teste computacional.
A verificação independente da argumentação matemática permanece distinta
da reprodução experimental F3.

---

## P3 — o LP da F-CC implica C1

**Rótulo: `HYPOTHESIS` — N1-T1 (2026-10-07).**

A versão histórica apresentava um argumento para C1, mas o rotulava
`COMPUTATIONALLY VERIFIED` **sem** teste de implicação de todos os cortes.
Não se preserva esse rótulo. Um teste correto minimizaria
\(\sum_{v\in Z} y_v\) sobre o LP de F-CC para cada \(Z\) gerado por C1,
em cada instância pré-declarada, exigindo valor \(\ge1-10^{-6}\).

**Distância zero resolvida:** \(s\notin N^+(s)\), pois `A_r` omite
\((s,s)\). A vizinhança fechada \(B(W)\) **inclui** \(W\), de forma que
\(s\in W\) não implica \(s\in N^+(s)\). A demonstração histórica não
fica automaticamente completa só por esclarecer essa distinção.

Até haver prova revisada ou teste de implicação, **P3 não é usada para
afirmar inclusão de politopos**. Comparar apenas objetivos de LP não
serviria como teste de implicação.

---

## P4 — o LP da F-CC implica C2

**Rótulo: `HYPOTHESIS` — N1-T1 (2026-10-07).**

O argumento histórico de bandas não substitui uma prova revisada para
cada corte efetivamente retornado por `cuts.generate_C2` (incluindo
regras da implementação e incidência dos terminais). Nenhum teste do
mínimo do lado esquerdo de **cada** C2 sobre o LP F-CC foi registrado.
A etiqueta anterior `COMPUTATIONALLY VERIFIED` era incompatível com a
evidência; ela foi retirada.

Para elevar o rótulo, escrever uma prova de implicação para todos os
cortes gerados ou executar um teste de implicação por corte e instância,
com tolerância \(10^{-6}\). Comparar valores objetivos não basta.

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

## P7 — F-CA com CA5 tem a mesma projeção em \(y\) que F-CC

**Rótulo: `PROVEN` — prova reparada em N1-T1 (2026-10-07).**

A F-CA da SOURCE (§3) usa, por \(W\), \(\lambda_W\), \(\alpha_{sW}\)
e \(\beta_{tW}\), com CA1–CA6, inclusive
\(\lambda_W\le\sum_s\alpha_{sW}\) (**CA5**).
O código histórico `fcc.py` na forma `separada` omite CA5.

**F-CC → F-CA.** Agrupar \(\lambda_{(W,I,J)}\) produz \(\lambda_W\),
\(\alpha\) e \(\beta\). Toda configuração possui
\(|I|=|J|\ge1\), portanto também satisfaz CA5: para um dado \(W\),
\(\sum_s\alpha_{sW}=\sum_{I,J}|I|\lambda_{(W,I,J)}\ge\lambda_W\).
Atendimento, equilíbrio e instalações não mudam.

**F-CA → F-CC.** Quando \(\lambda_W=0\), CA3 força \(\alpha=\beta=0\).
Quando \(\lambda_W>0\), normalize
\(a_s=\alpha_{sW}/\lambda_W\),
\(b_t=\beta_{tW}/\lambda_W\). Por CA3–CA5,
\(0\le a,b\le1\), \(\sum_s a_s=\sum_t b_t\ge1\).
Esse politopo é a envoltória convexa das incidências
\((1_I,1_J)\) com \(|I|=|J|\ge1\): se a desigualdade de soma
não for ativa, a igualdade e os limites inteiros deixam no máximo uma
coordenada fracionária, impossível pela soma inteira dos demais termos;
quando é ativa, as duas somas são 1 e a face é produto de simplexos.
Decompor \((a,b)\) nessas incidências e multiplicar os coeficientes por
\(\lambda_W\) reconstrói pesos de configurações não vazias,
preservando \(\lambda_W\), \(\alpha\), \(\beta\), \(d\) e \(y\).

**Remoção da massa vazia no código histórico.** Considere agora um ponto
da forma `separada` **sem CA5**. Em cada \(W\) escreva
\(h_W=\sum_s\alpha_{sW}=\sum_t\beta_{tW}\) e defina
\(\lambda'_W=\min\{\lambda_W,h_W\}\). Como cada
\(\alpha_{sW},\beta_{tW}\le h_W\) e \(\le\lambda_W\), CA3 segue
válida para \(\lambda'_W\); CA5 passa a valer. \(\alpha\), \(\beta\),
\(d\) não mudam; CA1, CA2 e CA4 continuam iguais. O único coeficiente
alterado é \(\lambda_W\), que **diminui**, logo CA6 se torna mais
frouxa. Assim a massa correspondente a \(I=J=\varnothing\) é descartada:
não reproduzimos necessariamente as marginais **antigas** de
\(\lambda_W\), mas preservamos a projeção em \(y\) e o objetivo.
Em particular, com \(h_W=0\), \(\lambda'_W=0\).

Portanto F-CC, F-CA **com CA5** e a implementação `separada` **sem CA5**
possuem a mesma projeção em \(y\) e o mesmo mínimo LP, embora os
polítopos de variáveis auxiliares sejam diferentes. \(\square\)

**Evidência computacional histórica:** `verify_fcc.py` testa igualdade
de valores LP em seu conjunto declarado, o que apoia a reprodução de
valores mas **não** demonstra igualdade de projeções.

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
| P3 | `HYPOTHESIS` |
| P4 | `HYPOTHESIS` |
| P5 | `HYPOTHESIS` |
| P6 | `OPEN` |
| P7 | `PROVEN` |
| P8 | `HYPOTHESIS` |
| P9 | `HYPOTHESIS` (medição em F3) |
| P10 | `PROVEN` |
| P11 | `HYPOTHESIS` |

## Nota pós-análise N1-T1 — 2026-10-07

P2 e P7 receberam provas completas acima (`PROVEN`). P3 e P4 permanecem
`HYPOTHESIS` até prova revisada ou teste de implicação **por corte**.
Nenhum rótulo `COMPUTATIONALLY VERIFIED` foi atribuído por igualdade de
objetivos. A reprodução numérica F3 não foi executada nesta edição.
