# F-C3 — definição canônica v1.0.0 (N1-T2)

**Data da consolidação:** 2026-10-07. **Status da definição:** `SOURCE` reconciliada;
**status de validação MR-F3:** `OPEN` — **NÃO IMPLEMENTAR as redes até revisão aceita**.

**Documento fonte preservado:** `docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md`,
redigido em **01/10/2026**, recuperado e conferido em **07/10/2026**,
SHA-256 `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4`. A SOURCE não foi editada.

**Dependências citadas mas indisponíveis (`UNRECOVERED`):**
`MIN-STATION-formulacao-por-componentes.md`,
`MIN-STATION-formulacao-fluxos-origem-destino.md` e a versão
consolidada de 05/10/2026. Nenhum conteúdo dessas fontes foi reconstruído.

**Vocabulário:** `F-C3` é esta formulação por consistência de trios; `C3-cut`
é exclusivamente a antiga família de cortes por separação max-flow
(`experiments/cuts/cuts.py`, `check_C3_violations`); são objetos distintos.
A notação `K` no corpo matemático é o número de conjuntos `W`; nos
experimentos N1, `K` é exclusivamente o conjunto fixo de cortes C1+C2+C4-DM.
Para evitar colisão, o número de conjuntos na implementação pode ser
chamado `nW`, preservando a definição matemática da SOURCE.

**Âmbito:** MIN-STATION de Das com `S∩T`, estações em terminais, terminais
como relés, permanência e múltiplas componentes de H[C]. Formulação estática,
não método de solução. Base U, COMP e núcleo IP permanecem intocados.

## Roteiro para implementação — `SOURCE`/`DERIVED`

Os elementos a seguir contêm a formulação **integral**, transcrita da SOURCE
§§2–6, incluindo redes C31–C34. `CA5` integra obrigatoriamente F-CA e F-C3.
Quando `m<3`, não há redes e F-C3 coincide com F-CA. Cada trio de origens
é independente de cada trio de destinos mesmo para vértices em `S∩T`.

**Distância versus variável:** `d_G(s,s)=0`; para `s∈S∩T`, a variável de
atendimento direto `d_{ss}` permanece livre no intervalo `[0,1]`
e pode valer **1** (não imponha `d_ss=0`).

**Ordem/estados:** `W_1, …, W_nW` são ordenados deterministicamente; cada
rede de trio possui estados `(j,B)` (`j=0,…,nW`, `B⊆U`), não utilização,
utilização com `R⊆(U\B)∩S_Wj` ou `T_Wj`, **incluindo `R=∅`**,
e arcos `(nW,B)→ω`. Cada trio exige C31–C34.

**Gate:** o texto abaixo fixa o objeto da revisão; ele **não é** a
aceitação MR-F3 e não autoriza execução de LP F-C3 antes do gate.

---


## 2. Problema e notação

Considere G=(V,E) simples, conexo, não direcionado e unitário; origens S e destinos T, com |S|=|T|=m; e autonomia inteira r≥1. As estações podem ocupar qualquer vértice, inclusive terminais. Os robôs começam carregados, o pareamento é livre e não há capacidade de estação, colisões ou tempo.

Defina o grafo de alcance:

$$
H=(V,E_r),\qquad
E_r=\{\{u,v\}:u\ne v,\ d_G(u,v)\le r\}.
$$

Um par s,t é atendido por uma instalação C quando existe um caminho em H de s a t cujos vértices internos pertencem a C. Para s=t, admite-se permanência.

As viagens diretas são:

$$
D=\{(s,t)\in S\times T:d_G(s,t)\le r\}.
$$

Em particular, D contém (s,s) para s∈S∩T.

Para W⊆V, seja B(W) sua vizinhança fechada em H. A família de infraestruturas é:

$$
\mathcal W=
\{W\subseteq V:W\ne\varnothing,\ H[W]\text{ conexo},
\ S\cap B(W)\ne\varnothing,\ T\cap B(W)\ne\varnothing\}.
$$

Defina:

$$
S_W=S\cap B(W),\qquad T_W=T\cap B(W),\qquad K=|\mathcal W|.
$$

Os W são conjuntos conectados candidatos a representar componentes utilizadas. Não precisam ser componentes maximais de H.

Se m=0, o ótimo é zero. Quando m<3, não existem redes de trios e F-C3 coincide com F-CA.

---

## 3. Núcleo F-CA: componentes com atribuição separada

### 3.1 Variáveis

$$
y_v\in\{0,1\}\quad(v\in V),
$$

$$
\lambda_W\ge0\quad(W\in\mathcal W),
$$

$$
\alpha_{sW}\ge0\quad(W\in\mathcal W,\ s\in S_W),
\qquad
\beta_{tW}\ge0\quad(W\in\mathcal W,\ t\in T_W),
$$

$$
d_{st}\ge0\quad((s,t)\in D).
$$

Interpretação:

- y instala estações;
- λ representa o peso de utilização de uma infraestrutura W;
- α indica quanto de uma origem é atribuído a W;
- β indica quanto de um destino é atribuído a W;
- d representa deslocamentos sem recarga, incluindo permanência.

Adote α_sW=0 e β_tW=0 fora dos respectivos domínios de elegibilidade. Esses zeros são constantes.

### 3.2 Objetivo e restrições

$$
\min\sum_{v\in V}y_v.
\tag{CA0}
$$

Atendimento das origens:

$$
\sum_{W\in\mathcal W}\alpha_{sW}
+\sum_{t:(s,t)\in D}d_{st}=1
\qquad(s\in S).
\tag{CA1}
$$

Atendimento dos destinos:

$$
\sum_{W\in\mathcal W}\beta_{tW}
+\sum_{s:(s,t)\in D}d_{st}=1
\qquad(t\in T).
\tag{CA2}
$$

Atribuição condicionada à utilização de W:

$$
0\le\alpha_{sW}\le\lambda_W\quad(s\in S_W),
\qquad
0\le\beta_{tW}\le\lambda_W\quad(t\in T_W).
\tag{CA3}
$$

Equilíbrio de origens e destinos em W:

$$
\sum_{s\in S_W}\alpha_{sW}
=\sum_{t\in T_W}\beta_{tW}
\qquad(W\in\mathcal W).
\tag{CA4}
$$

Uma infraestrutura utilizada representa um grupo não vazio:

$$
\lambda_W\le\sum_{s\in S_W}\alpha_{sW}
\qquad(W\in\mathcal W).
\tag{CA5}
$$

Compatibilidade da infraestrutura com as estações:

$$
\sum_{W:v\in W}\lambda_W\le y_v
\qquad(v\in V).
\tag{CA6}
$$

CA6 não limita o número de robôs atendidos. Um W de peso 1 pode atender várias origens e vários destinos. A soma restringe a representação de componentes, pois uma instalação real pode ser representada por componentes disjuntas.

CA6 também implica λ_W≤1, porque W é não vazio e y≤1.

### 3.3 Por que isso comprime F-CC sem perder força

Em F-CC, havia uma variável η_(W,I,J) para cada escolha de grupos equilibrados I⊆S_W e J⊆T_W, com |I|=|J|≥1.

Agrupe essas variáveis:

$$
\lambda_W=\sum_{I,J}\eta_{(W,I,J)},\quad
\alpha_{sW}=\sum_{I,J:s\in I}\eta_{(W,I,J)},\quad
\beta_{tW}=\sum_{I,J:t\in J}\eta_{(W,I,J)}.
$$

As restrições CA1–CA6 seguem imediatamente. Isso fornece uma direção da inclusão.

Para a volta, fixe W com λ_W>0 e normalize:

$$
a_s=\alpha_{sW}/\lambda_W,\qquad b_t=\beta_{tW}/\lambda_W.
$$

O vetor (a,b) pertence ao politopo:

$$
0\le a,b\le1,\qquad
\sum_s a_s=\sum_t b_t,\qquad
\sum_s a_s\ge1.
\tag{P}
$$

Esse politopo tem somente vértices 0–1:

- Se a última desigualdade não está ativa, há apenas uma igualdade além dos limites. Um vértice teria no máximo uma coordenada fracionária; a igualdade com coeficientes ±1 e todas as outras coordenadas inteiras impede essa única coordenada fracionária.
- Se a última desigualdade está ativa, ambas as somas valem 1. A face é produto de dois simplexos, cujos vértices selecionam uma origem e um destino.

Logo (a,b) é combinação convexa de incidências de pares de conjuntos I,J não vazios e equilibrados. Multiplicar seus pesos por λ_W reconstrói as variáveis η de F-CC, preservando as atribuições e a carga de cada estação.

Portanto, para todo y fracionário:

$$
\operatorname{proj}_y(P_{\mathrm{CA}})
=\operatorname{proj}_y(P_{\mathrm{CC}}).
\tag{EQ}
$$

A compressão é exata, e não apenas uma aproximação.

---

## 4. O que ainda falta no núcleo

CA1–CA6 podem combinar grupos que funcionam isoladamente, mas não são uma mistura coerente de partições dos terminais.

Considere três grupos que atendem, respectivamente, os pares de origens:

$$
\{s_1,s_2\},\qquad\{s_2,s_3\},\qquad\{s_1,s_3\}.
$$

Usar metade de cada grupo atende cada origem com peso 1. Entretanto, numa atribuição inteira, não podem ser usados dois desses grupos completos: eles repetiriam alguma origem.

O problema não é volume de fluxo nem capacidade de estação. É a compatibilidade entre grupos diferentes. Esse é o alvo das redes da próxima seção.

---

## 5. F-C3: redes de atribuição conjunta para trios

As redes a seguir fazem parte da formulação linear. Seus fluxos são certificados auxiliares de atribuição; não representam deslocamentos físicos de robôs.

Enumere uma vez:

$$
\mathcal W=\{W_1,\ldots,W_K\}.
$$

Para cada trio U⊆S, e separadamente para cada trio U⊆T, construa uma rede dirigida acíclica. As redes de origens e destinos são distintas mesmo quando S e T se sobrepõem.

### 5.1 Estados e arcos

Um estado é:

$$
(j,B),\qquad j=0,\ldots,K,\quad B\subseteq U.
$$

j indica quantas infraestruturas já foram consideradas; B registra quais integrantes do trio já foram atribuídos a uma infraestrutura.

A raiz é (0,∅). Há um sorvedouro adicional ω.

Na etapa j, partindo de (j−1,B), existem:

1. **Arco de não utilização:** vai a (j,B) e indica que W_j não foi selecionado nessa representação local.
2. **Arcos de utilização:** para cada R⊆(U∖B)∩S_Wj, no caso das origens, um arco a (j,B∪R), marcado como utilização de W_j e atendimento de R. Para destinos, substitua S_Wj por T_Wj.

R pode ser vazio: W_j pode ser utilizado para terminais que estão fora do trio. Esse arco é distinto do arco de não utilização.

Como R não intersecta B, nenhum integrante do trio pode ser atribuído duas vezes.

Finalmente, cada estado (K,B) tem um arco para ω. Seu rótulo indica que os integrantes restantes U∖B serão atendidos diretamente.

Há no máximo oito estados por etapa. A ordem dos W serve para representar escolhas, não para impor tempo, deslocamento ou sequência física de recargas.

### 5.2 Variáveis e conservação de fluxo

Em cada rede N, use uma variável contínua:

$$
\phi^N_e\ge0
\qquad(e\text{ arco de }N).
$$

Imponha uma unidade de fluxo da raiz ao sorvedouro:

$$
\sum_{e\in\delta^+(u)}\phi^N_e
-\sum_{e\in\delta^-(u)}\phi^N_e
=
\begin{cases}
1,&u=(0,\varnothing),\\
-1,&u=\omega,\\
0,&\text{demais estados}.
\end{cases}
\tag{C31}
$$

Todo fluxo factível nessa rede acíclica é uma combinação convexa de caminhos da raiz ao sorvedouro. Cada caminho representa uma atribuição local sem duplicações.

Isso não torna o modelo acoplado integral. Garante somente a interpretação de cada fluxo local como mistura de atribuições coerentes para aquele trio.

### 5.3 Acoplamento com o núcleo

Denote por E^N_j os arcos de utilização de W_j. Os arcos de não utilização não entram nesse conjunto.

O peso de utilização deve coincidir com λ:

$$
\sum_{e\in E^N_j}\phi^N_e=\lambda_{W_j}
\qquad(j=1,\ldots,K).
\tag{C32}
$$

Se N corresponde a um trio U de origens:

$$
\sum_{\substack{e\in E^N_j\\s\in R(e)}}\phi^N_e
=\alpha_{sW_j}
\qquad(s\in U,\ j=1,\ldots,K).
\tag{C33S}
$$

Para trios de destinos:

$$
\sum_{\substack{e\in E^N_j\\t\in R(e)}}\phi^N_e
=\beta_{tW_j}
\qquad(t\in U,\ j=1,\ldots,K).
\tag{C33T}
$$

Nos arcos finais, a probabilidade de um terminal ficar para atendimento direto deve coincidir com d:

$$
\sum_{\substack{B\subseteq U\\s\notin B}}
\phi^N_{(K,B),\omega}
=\sum_{t:(s,t)\in D}d_{st}
\qquad(s\in U)
\tag{C34S}
$$

nas redes de origens, e:

$$
\sum_{\substack{B\subseteq U\\t\notin B}}
\phi^N_{(K,B),\omega}
=\sum_{s:(s,t)\in D}d_{st}
\qquad(t\in U)
\tag{C34T}
$$

nas redes de destinos.

Essas últimas igualdades também decorrem das marginais e de CA1–CA2; ficam explícitas para fixar a semântica.

### 5.4 Formulação completa

F-C3 é:

$$
\min\sum_v y_v
$$

sujeita a CA1–CA6, a C31–C34 para todos os trios dos dois lados, e:

$$
y\in\{0,1\}^{V},\qquad
\lambda,\alpha,\beta,d,\phi\ge0.
$$

Apenas y precisa ser binário. Não há coeficiente global m nas ativações.

---

## 6. Equivalência com o MIN-STATION

### 6.1 Toda instalação física admite F-C3

Fixe uma instalação viável C e uma bijeção de origens para destinos com rotas válidas. Escolha caminhos simples no grafo de alcance.

Agrupe as rotas com recarga pelas componentes W de H[C]. Cada componente utilizada recebe um conjunto I_W de origens e J_W de destinos de mesmo tamanho. Rotas sem recarga são representadas por d.

Use y=χ_C; λ_W=1 nas componentes utilizadas; α_sW=1 para s∈I_W; β_tW=1 para t∈J_W; e os d dos pares diretos. As demais variáveis são zero.

CA1–CA6 valem porque os grupos particionam os papéis de origem e destino e as componentes de C são disjuntas.

Em cada rede de trio, percorra as infraestruturas na ordem fixada. Se uma componente for usada, selecione o arco que atende I_W∩U ou J_W∩U; caso contrário, use o arco de não utilização. Os grupos não repetem terminais. No fim, os restantes são exatamente os atendidos diretamente.

O caminho resultante satisfaz C31–C34. Estações instaladas mas não utilizadas podem permanecer com y=1, preservando exatamente C.

### 6.2 F-C3 com y binário implica uma instalação viável

Toda solução de F-C3 satisfaz F-CA. Pela equivalência da seção 3, admite uma representação em F-CC com o mesmo y.

Também há uma prova direta. Se λ_W>0, CA6 obriga todos os vértices de W a estarem instalados. Dentro de W, qualquer origem elegível pode alcançar qualquer destino elegível.

Defina k_W=Σ_s α_sW=Σ_t β_tW. Para k_W>0, a matriz:

$$
p^W_{st}=\frac{\alpha_{sW}\beta_{tW}}{k_W}
\qquad(s\in S_W,\ t\in T_W)
$$

tem marginais α e β e suporte em pares alcançáveis. Somando essas matrizes aos pares diretos d, obtemos uma matriz não negativa com todas as somas de linha e coluna iguais a 1.

A integralidade do matching bipartido garante um pareamento perfeito inteiro nesse suporte. Cada par tem uma rota válida utilizando as estações selecionadas.

As redes de trios fortalecem a relaxação; não são necessárias a essa direção da prova.

### 6.3 Domínio preservado

O argumento inclui:

- S∩T, distinguindo papéis e permitindo d_ss;
- estações em origens e destinos;
- origem inicialmente carregada e chegada final sem recarga;
- várias rotas compartilhando estações;
- vários grupos de estações desconectados;
- caminhos físicos que atravessam terminais sem recarregar.

Não é imposto pareamento fixo, capacidade unitária, sincronização ou proibição de trânsito em terminais.

---

## 7. Relação de dominância usada em N1 — `DERIVED`, sob MR-F3

F-C3 é F-CA com redes adicionais, portanto sua projeção fracionária em
`y` está contida na de F-CA. Pelo argumento de decomposição de F-CA
(§3 e P7 reparada), F-CA e F-CC possuem a mesma projeção `y`.
Assim `z_LP(F-C3) ≥ z_LP(F-CC)`. Como qualquer instalação viável inteira
admite representação por caminhos nas redes (§6), `z_LP(F-C3) ≤ OPT`.
A cadeia relativa à baseline U depende **separadamente** da P2 revisada;
N1 não utiliza o elo com F-OD da versão SOURCE.

**Status:** `HYPOTHESIS` para qualquer propriedade ainda não aprovada
pelo registro MR-F3. Não se confundem prova analítica, execução numérica
e superioridade computacional.

## 8–9. Regressões analíticas da SOURCE — `SOURCE`, revisão pendente

- SOURCE §8: construção de `g` triângulos unidos por pontes, `n=11g−2`,
  `m=4g−1`, `r=1`; `g=2` tem **20 vértices**, **7 pares**,
  previsão `z_LP(F-CC)=3`, `z_LP(F-C3)=OPT=4`.
- SOURCE §9: transformação do ciclo ímpar de cinco vértices, `n=15`,
  `m=5`, `r=1`, previsão `z_LP(F-C3)=5/2 < OPT=3`.
- Esses valores estão escritos como argumentos analíticos na SOURCE,
  não como resultados de solver obtidos nesta fase. Enquanto a revisão
  matemática dos argumentos e os testes exigidos não forem aceitos,
  sua classificação N1 permanece `HYPOTHESIS`, não `PROVEN`.
- A discussão de `F-OD` na SOURCE é **histórica**; não entra na cadeia
  de N1 nem autoriza dependência de fontes `UNRECOVERED`.

## 10. Tamanho e limite de exclusão — `SOURCE` / `DERIVED`

Há `2·binom(m,3)` redes (uma por trio de origens e destinos). Cada uma
possui no máximo `8(nW+1)+1` estados e `35·nW+8` arcos. O limite
pré-registrado de N1 exclui antes de medir F-C3 quando
`2·binom(m,3)·(35·nW+8) > 5_000_000`.
O `nW` é contado **depois** do filtro de configurações úteis, ao contrário
da contagem bruta de conjuntos conectados. Não há variante de trios
restritos nesta fase.

## 11–12. Limitações e bibliografia — `SOURCE`

- SOURCE §11 apresenta uma limitação condicional de extensão polinomial
  universalmente tão forte quanto F-CC (`P≠NP`). É uma afirmação
  analítica que requer revisão se for reutilizada.
- SOURCE §12 não sustenta novidade bibliográfica e não afirma melhor
  desempenho em tempo, memória ou escala.
- Nenhum método de pricing, geração de colunas ou benchmark amplo
  integra esta definição (N2 permanece condicional).

## Auditoria de proveniência: SOURCE §§2–12 versus resumo histórico

| Elemento | SOURCE | Resumo histórico | Classificação N1 | Decisão |
|---|---|---|---|---|
| Domínio de Das, grafo H, D, B(W) | §2 | §§1–2 (parcial) | `SOURCE` | Copiado integralmente |
| F-CA: CA1–CA4 e CA6 | §3.2 | §2 (parcial) | `SOURCE` | Copiado integralmente |
| **CA5**: λ≤Σα | §3.2 | Omitida | `SOURCE` | Obrigatória na forma canônica |
| Projeção exata F-CA = F-CC | §3.3 | Remetida a P7 antiga | `SOURCE` + P7 `DERIVED` | Prova em P7 reparada |
| Obstrução por cobertura duplicada | §4 | §3 (apenas alusão) | `SOURCE` | Copiada |
| O1: estágios em W_j | §5.1 | `OPEN` | `SOURCE` | Definido `j=1..nW` |
| O2: arcos não uso e uso (R=∅) | §5.1 | `OPEN` | `SOURCE` | Definidos |
| O3: vínculos λ,α,β,d | §§5.2–5.3 C31–C34 | `OPEN` | `SOURCE` | Definidos |
| O4: rede por trio de cada lado | §5 | `OPEN` | `SOURCE` | Duas famílias de redes separadas |
| O5: ordem sobre W_j | §5.1 | `OPEN` | `SOURCE` | Ordem fixa determinística |
| Exatidão para y binário, S∩T, relés | §6 | Ausente | `SOURCE` | Transcrito; exige MR-F3 |
| Dominância F-C3/F-CC | §7 | Cadeia condicional | `SOURCE` + `DERIVED` | Sem F-OD no elo N1 |
| Família 20 vértices/g=2 | §8 | Só número sem gerador | `SOURCE` | Regressão analítica, revisão pendente |
| Ciclo 15 vértices | §9 | Só número sem gerador | `SOURCE` | Regressão analítica, revisão pendente |
| Tamanho exponencial e cap | §10 | Tamanho qualitativo | `SOURCE` + cap `NEW` | Cap de N1 pré-registrado |
| Limitação de representação polinomial | §11 | Ausente | `SOURCE` | Fora da escolha algorítmica |
| Relação bibliográfica sem novidade provada | §12 | Ausente | `SOURCE` | Histórico, sem reivindicação de novidade |
| `d_G(s,s)=0` versus `d_ss` livre | §2, §3 (d_st), §6.3 | Erro `d_ss=0` | `SOURCE` + esclarecimento `DERIVED` | Variável pode valer 1 |
| Separação F-C3 versus C3-cut | nomenclatura do projeto | Ambígua | `NEW` | Convenção obrigatória |

## MR-F3 — registro de revisão (07/10/2026)

**Estado global: `OPEN` — não aceito.** A recuperação da fonte e a
identificação textual das restrições não equivalem à validação de toda
argumentação e de suas consequências. Registro por argumento:

| Argumento | Revisão nesta edição | Rótulo |
|---|---|---|
| Domínio e semântica CA1–CA6 | Transcrição conferida com SOURCE §§2–3 | `SOURCE`, revisão de validade pendente |
| P7, equivalência F-CA/F-CC | Prova reescrita em `provas-fcc-fc3.md` | `PROVEN` no registro P7 |
| Exatidão F-C3 para y binário | SOURCE §6 documenta duas direções; validação por instalação não executada | `HYPOTHESIS` até MR aceitar |
| Redes C31–C34 e vínculo de marginais | SOURCE §5 inteiramente recuperada; consistência ainda não testada | `OPEN` para MR |
| Dominância F-C3 sobre F-CC | Argumento formal dado, dependente de §5 e §6 | `HYPOTHESIS` até MR aceitar |
| Família g=2 | SOURCE §8 contém prova escrita; não auditada numericamente | `HYPOTHESIS` |
| Ciclo 5 | SOURCE §9 contém argumento; não auditado numericamente | `HYPOTHESIS` |

**Condição para mudar para `ACCEPTED`:** revisão matemática independente
linha a linha dos itens ainda pendentes, com registro explícito de
argumentos aceitos/refutados; só então é permitido implementar as redes
F-C3. Um teste de LP isolado não substitui revisão do modelo.
