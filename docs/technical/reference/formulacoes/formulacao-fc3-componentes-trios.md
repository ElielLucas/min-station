# MIN-STATION: componentes com consistência de trios

Data: 01/10/2026, horário de São Paulo.

Referência do projeto: branch novos_testes, commit e9d1ccb5c8b998e98a721be693c2e78faf6eb7d5, consultado nos estudos anteriores. Este documento desenvolve uma formulação matemática; não altera o repositório, não executa modelos ou experimentos e não modifica o plano em andamento.

## 1. Resultado e alcance da proposta

A proposta F-C3 combina dois desenvolvimentos:

1. **Compressão exata de F-CC:** substituir as configurações (W,I,J) por um conjunto conectado W e variáveis separadas de atribuição de origens e destinos. A formulação resultante, F-CA, preserva exatamente a projeção da relaxação de F-CC nas variáveis de estação.
2. **Consistência de trios:** exigir que as atribuições de cada trio de origens, e de cada trio de destinos, admitam uma representação conjunta sem atendimento duplicado. Isso é expresso por redes auxiliares de estados, incorporadas integralmente à formulação.

As conclusões demonstradas neste documento são:

$$
z_{\mathrm{LP}}^{\mathrm{AG}}
\le z_{\mathrm{LP}}^{\mathrm{OD}}
\le z_{\mathrm{LP}}^{\mathrm{CC}}
=z_{\mathrm{LP}}^{\mathrm{CA}}
\le z_{\mathrm{LP}}^{\mathrm{C3}}
\le \mathrm{OPT}.
$$

A comparação é com a baseline matemática sem cortes adicionais, com F-OD e com a família completa de configurações de F-CC.

Em uma família de grafos conexos, simples e unitários:

$$
z_{\mathrm{LP}}^{\mathrm{AG}}=1,\qquad
z_{\mathrm{LP}}^{\mathrm{OD}}
=z_{\mathrm{LP}}^{\mathrm{CC}}
=\frac{3g}{2},
\qquad
z_{\mathrm{LP}}^{\mathrm{C3}}
=\mathrm{OPT}=2g.
$$

Para g=2, a melhora é de 3 para 4, portanto não se resume ao arredondamento de um limite fracionário.

F-C3 continua exponencial no número de vértices e não é ideal em geral. Também é apresentado um grafo de quinze vértices em que seu LP vale 5/2 e o ótimo vale 3. Não foi demonstrada superioridade em tempo, memória, número de nós ou escalabilidade.

É uma reformulação fortalecida da linha de componentes, não um paradigma inteiramente independente dela. Sua eventual novidade bibliográfica não está estabelecida.

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

## 4. O que ainda falta no núcleo

CA1–CA6 podem combinar grupos que funcionam isoladamente, mas não são uma mistura coerente de partições dos terminais.

Considere três grupos que atendem, respectivamente, os pares de origens:

$$
\{s_1,s_2\},\qquad\{s_2,s_3\},\qquad\{s_1,s_3\}.
$$

Usar metade de cada grupo atende cada origem com peso 1. Entretanto, numa atribuição inteira, não podem ser usados dois desses grupos completos: eles repetiriam alguma origem.

O problema não é volume de fluxo nem capacidade de estação. É a compatibilidade entre grupos diferentes. Esse é o alvo das redes da próxima seção.

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

## 7. Dominância da relaxação

Relaxe y para [0,1]. Remover as redes de F-C3 produz uma solução de F-CA com o mesmo y. Pela seção 3:

$$
\operatorname{proj}_y(P_{\mathrm{C3}})
\subseteq
\operatorname{proj}_y(P_{\mathrm{CA}})
=
\operatorname{proj}_y(P_{\mathrm{CC}}).
$$

Os estudos anteriores demonstraram:

$$
\operatorname{proj}_y(P_{\mathrm{CC}})
\subseteq
\operatorname{proj}_y(P_{\mathrm{OD}})
\subseteq
\operatorname{proj}_y(P_{\mathrm{AG}}).
$$

Isso prova a cadeia de limites apresentada na seção 1. A inclusão relativa a F-CC é estrita em geral, como mostra a próxima seção.

Não há aqui uma conclusão sobre o pipeline COMP com cortes ou sobre implementações específicas.

## 8. Uma família conexa com ganho estrito e crescente

### 8.1 Construção

Construa primeiro um grafo auxiliar L_g:

- g triângulos com vértices a_i,b_i,c_i;
- para i=1,...,g−1, acrescente uma ponte a_i–a_(i+1).

L_g tem 3g vértices e 4g−1 arestas.

Transforme-o em uma instância MIN-STATION:

- para cada vértice u de L_g, crie um candidato c_u;
- para cada aresta e={u,v} de L_g, crie uma origem s_e e um destino t_e;
- ligue s_e a c_u e c_v;
- ligue t_e a c_u e c_v;
- não acrescente outras arestas; tome r=1.

O grafo resultante é simples, conexo, bipartido e unitário, com:

$$
m=4g-1,\qquad n=11g-2.
$$

Todos os vértices, incluindo os terminais, permanecem elegíveis para estações.

### 8.2 Ótimo inteiro: 2g

Ao sair de s_e, o robô chega a c_u ou c_v. Nenhum deles é destino; com r=1, ele precisa recarregar nesse candidato antes de prosseguir. Portanto pelo menos um extremo de cada aresta de L_g precisa ter sua estação.

Os candidatos instalados formam uma cobertura de vértices de L_g. Cada triângulo exige pelo menos dois, totalizando 2g.

Instalar os candidatos correspondentes a a_i,b_i, para todo i, cobre também todas as pontes. Cada s_e pode ir ao próprio t_e por um candidato instalado. Logo:

$$
\mathrm{OPT}=2g.
$$

Instalar em terminais não elimina a necessidade da primeira recarga em um dos dois candidatos.

### 8.3 Baseline agregada: LP igual a 1

Envie cada origem ao próprio destino por um candidato incidente escolhido. Se k_u rotas passam por c_u, use y_cu=k_u/m e y=0 nos terminais.

As ativações agregadas são satisfeitas e Σ_u k_u=m, dando objetivo 1.

Para o limite inferior, todas as origens emitem fluxo líquido total m para candidatos. A conservação nesses candidatos e a ativação com coeficiente m obrigam Σ_u y_cu≥1.

Portanto:

$$
z_{\mathrm{LP}}^{\mathrm{AG}}=1.
$$

### 8.4 F-OD e F-CC: LP igual a 3g/2

A ativação por origem implica:

$$
y_{c_u}+y_{c_v}\ge1
\qquad(e=\{u,v\}\in E(L_g)).
$$

Somando as três condições de cada triângulo, obtém-se pelo menos 3/2 por triângulo, totalizando 3g/2.

Uma solução de F-CC atinge esse valor: para cada candidato c_u, use com peso 1/2 a configuração singleton W={c_u} que atende todas as origens e destinos correspondentes às arestas incidentes em u. Cada terminal aparece em duas configurações e recebe peso total 1. Faça y_cu=1/2.

Como F-CC domina F-OD, e a solução pode também ser representada dividindo cada rota igualmente entre os dois candidatos:

$$
z_{\mathrm{LP}}^{\mathrm{OD}}
=z_{\mathrm{LP}}^{\mathrm{CC}}
=z_{\mathrm{LP}}^{\mathrm{CA}}
=\frac{3g}{2}.
$$

### 8.5 F-C3: LP igual a 2g

Para cada triângulo i de L_g, considere o trio U_i formado pelas origens de suas três arestas internas. As origens correspondentes às pontes não integram esses trios.

Na rede de U_i, defina ρ_iW como a soma dos fluxos nos arcos que utilizam W e atendem pelo menos dois integrantes do trio.

Ao longo de um caminho da rede, no máximo uma infraestrutura pode atender pelo menos dois integrantes de U_i: dois grupos assim repetiriam alguma origem. Pela decomposição em caminhos:

$$
\sum_W\rho_{iW}\le1.
\tag{T1}
$$

Fixe W∈𝒲. Seja k_i o número de candidatos de W pertencentes ao triângulo i, k=Σ_i k_i e h o número de triângulos com k_i>0.

Todo W admissível contém algum candidato. Um singleton terminal não tem ambos os tipos de terminal em sua vizinhança. Se W tem mais vértices, sua conectividade também exige candidatos.

Além disso:

- se k_i=0, W não atende origens de U_i;
- se k_i=1, W é elegível para no máximo duas origens de U_i;
- se k_i≥2, há no máximo três origens de U_i para atender.

Consequentemente, para k_i>0:

$$
\sum_{s\in U_i}\alpha_{sW}
\le (2k_i-1)\lambda_W+\rho_{iW}.
\tag{T2}
$$

Para k_i=1, um arco selecionado atende no máximo uma origem mais uma unidade adicional quando atende duas. Para k_i≥2, o lado (2k_i−1)λ_W sozinho já é pelo menos 3λ_W.

O grafo MIN-STATION é bipartido entre candidatos e terminais, e cada terminal tem grau dois. Um W conectado com k candidatos precisa de pelo menos k−1 terminais. Portanto:

$$
|W|\ge2k-1\ge2k-h.
$$

Somando T2:

$$
\sum_i\sum_{s\in U_i}\alpha_{sW}
\le |W|\lambda_W+\sum_i\rho_{iW}.
$$

Não existem viagens diretas S→T, pois r=1 e não há arestas entre origens e destinos. As 3g origens dos trios devem ser totalmente atendidas por infraestruturas. Somando sobre W, usando T1 e CA6:

$$
3g
\le\sum_W|W|\lambda_W+g
\le\sum_v y_v+g.
$$

Logo o objetivo é pelo menos 2g. A instalação inteira de custo 2g fornece a solução oposta:

$$
z_{\mathrm{LP}}^{\mathrm{C3}}=2g.
$$

### 8.6 Valores comparados

| Modelo | Família geral | g=2: 20 vértices, 7 robôs |
|---|---:|---:|
| Baseline agregada | 1 | 1 |
| F-OD | 3g/2 | 3 |
| F-CC | 3g/2 | 3 |
| F-CA, compressão exata | 3g/2 | 3 |
| F-C3 | 2g | 4 |
| Ótimo inteiro | 2g | 4 |

São valores demonstrados, não medições de solver. O ganho sobre F-CC cresce como g/2. Para g par, o limite anterior já é inteiro, eliminando a interpretação de mero arredondamento.

## 9. Contraexemplo: trios não resolvem toda a fracionalidade

Use a mesma transformação da seção 8, mas tome L como um ciclo de cinco vértices. Há cinco candidatos, cinco origens e cinco destinos: quinze vértices no total.

O ótimo inteiro é a cobertura mínima de vértices do ciclo ímpar:

$$
\mathrm{OPT}=3.
$$

Os modelos F-OD e F-CC têm LP 5/2, usando y_c=1/2 em todos os candidatos, sem estações em terminais. Cada origem e destino divide sua atribuição igualmente entre os dois candidatos incidentes.

Esse ponto também admite todas as redes de F-C3.

Fixe um trio U de origens. Ele corresponde a três arestas do ciclo de cinco vértices. O subgrafo formado por essas três arestas é uma floresta, portanto admite uma atribuição binária x aos candidatos com:

$$
x_u+x_v=1
\qquad\text{para cada aresta }\{u,v\}\text{ de }U.
$$

Escolha tal atribuição e sua complementar, cada uma com peso 1/2. Todo candidato é selecionado com probabilidade 1/2. Em cada realização, cada origem do trio é atendida exatamente uma vez, pelo seu extremo selecionado.

Um candidato selecionado sem origens do trio usa o arco de utilização com R vazio. As duas realizações definem caminhos da rede. Sua mistura reproduz λ=1/2 e todas as marginais α=1/2.

O mesmo argumento vale para todo trio de destinos. Os demais W têm peso zero e são ignorados pelos caminhos.

Assim:

$$
z_{\mathrm{LP}}^{\mathrm{C3}}=\frac52<3=\mathrm{OPT}.
$$

O modelo impõe coerência para cada trio, mas distribuições diferentes podem ser usadas por trios diferentes. Ele não exige uma única distribuição global de instalações e atribuições.

## 10. Tamanho da representação

### 10.1 Compressão F-CA

O núcleo tem:

$$
n+|D|+K+\sum_{W\in\mathcal W}(|S_W|+|T_W|)
\le n+m^2+(2m+1)K
$$

variáveis.

F-CC enumera, para cada W, todos os pares I,J equilibrados. Quando W é elegível para todos os terminais, são:

$$
\sum_{k=1}^m\binom{m}{k}^2
=\binom{2m}{m}-1
$$

configurações. F-CA substitui essa enumeração por até 2m+1 variáveis por W.

Isso elimina o fator exponencial da enumeração dos grupos de terminais. Não significa que o novo modelo tenha menos linhas ou menos variáveis em toda instância: para vizinhanças pequenas, o custo relativo pode se inverter.

### 10.2 Redes de trios

Existem 2 binom(m,3) redes. Cada uma tem no máximo:

- 8(K+1)+1 estados;
- 35K+8 arcos: até 27 arcos de utilização e 8 de não utilização por etapa, mais 8 finais.

O limite 27 vem dos três estados possíveis de cada integrante do trio numa transição: já atendido, atendido agora, ou ainda não atendido.

Assim, o número adicional de variáveis contínuas é limitado por:

$$
2\binom m3(35K+8).
$$

O tamanho é O(Km³+n+m²) para trios. Continua exponencial em n, pois K pode ser exponencial.

O núcleo comprimido pode ser útil independentemente das redes de trios. Não foi demonstrado que a versão completa F-C3 seja menor em memória ou mais rápida que F-CC ou F-OD.

## 11. Por que não prometer uma formulação polinomial dominante

Há um limite conceitual relevante para a busca por uma formulação simultaneamente compacta e mais forte que F-CC.

O estudo anterior construiu uma família de MIN-STATION baseada em cobertura de conjuntos, com um hub obrigatório, na qual:

$$
z_{\mathrm{LP}}^{\mathrm{CC}}=\mathrm{OPT}=1+\tau,
$$

onde τ é o ótimo inteiro da cobertura de conjuntos.

Se existisse uma formulação LP de tamanho e codificação polinomiais, construída em tempo polinomial, cuja relaxação dominasse F-CC para todas as instâncias, resolver seu LP nessa família calcularia τ em tempo polinomial.

Sob P≠NP, não podemos esperar simultaneamente essas propriedades gerais. Isso não impede modelos polinomiais melhores que a baseline, melhorias em classes particulares, nem desempenho prático favorável em benchmarks. Impede tratar “polinomial e universalmente tão forte quanto F-CC” como uma promessa inocente.

## 12. Relação com literatura e limites científicos

Formular diagramas de decisão como redes de fluxo é uma construção conhecida. O tutorial de van Hoeve, seção 6, descreve a representação de soluções por caminhos e a ligação entre fluxos nas redes e variáveis do modelo. Aqui essa construção é aplicada a atribuições de trios entre componentes do MIN-STATION.

A incompatibilidade de grupos que cobrem dois integrantes de um trio está relacionada às desigualdades subset-row de modelos de particionamento. Jepsen, Petersen, Spoorendonk e Pisinger apresentam essa família no contexto de roteamento.

O tratamento por redes neste documento não estabelece novidade bibliográfica, nem demonstra que ele seja preferível a outras representações lineares dessas compatibilidades. A eventual contribuição específica precisaria ser avaliada pela compressão, pela formulação para o domínio completo do MIN-STATION, pelas relações de projeção e pelos exemplos de separação.

Este estudo apresenta uma formulação estática e suas propriedades. Não propõe neste momento um algoritmo de separação, geração de colunas, callbacks, decomposição ou procedimento experimental.

Os resultados se dividem em:

- **Demonstrado:** exatidão; compressão F-CC→F-CA sem perda de LP; dominância de F-C3; separação estrita numa família conexa; gap remanescente no ciclo de cinco alternativas.
- **Não demonstrado:** ganho computacional; adequação do tamanho às instâncias atuais; superioridade sobre COMP fortalecido; novidade científica.

Ainda não há evidência suficiente para concluir que F-C3 seja computacionalmente superior às anteriores. Há uma demonstração de superioridade de relaxação em parte das instâncias e de não inferioridade para o domínio inteiro considerado.

## Referências e documentos relacionados

- Estudo anterior: MIN-STATION-formulacao-por-componentes.md, em especial as provas de exatidão, dominância e a família de cobertura com hub.
- Estudo anterior: MIN-STATION-formulacao-fluxos-origem-destino.md, prova da relação F-CC→F-OD→F-AG.
- [Formulação base do projeto no commit consultado](https://github.com/ElielLucas/min-station/blob/e9d1ccb5c8b998e98a721be693c2e78faf6eb7d5/docs/context-ai/base-formulation.md).
- [Willem-Jan van Hoeve. An Introduction to Decision Diagrams for Optimization. INFORMS Tutorials in Operations Research, 2024. Seção 6](https://www.andrew.cmu.edu/user/vanhoeve/papers/DD_TutORial.pdf).
- [Mads Jepsen, Bjørn Petersen, Simon Spoorendonk e David Pisinger. Subset-Row Inequalities Applied to the Vehicle-Routing Problem with Time Windows. Operations Research 56(2), 497–511, 2008](https://doi.org/10.1287/opre.1070.0449).

As provas específicas de F-CA, F-C3 e das famílias deste documento são derivações desta investigação, não teoremas atribuídos aos artigos citados. Os exemplos foram analisados matematicamente, sem execução computacional.
