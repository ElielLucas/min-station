**Minha recomendação mudou: antes de implementar os cortes anteriormente propostos, eu investigaria uma recuperação da desagregação por origem, usando poucos grupos de origens e uma ligação global corrigida com as estações.** Essa alternativa permite controlar o tamanho do modelo, preserva o problema inteiro e admite uma hierarquia demonstrável de relaxações.

Isso ainda não significa que ela será mais rápida que COMP+K. Há fundamento matemático para o teste; **a superioridade computacional permanece não demonstrada**.

Analisei a branch `novos_testes` no [commit `e25b056`](https://github.com/ElielLucas/min-station/commit/e25b056e2faab88afb9a56769d33fb90704e4440). Não alterei arquivos nem executei otimização. Fiz leituras de código e resultados, pesquisa bibliográfica e verificações pontuais com aritmética racional e o validador existente.

## 1. Resposta direta

**Existe uma alternativa promissora, mas nenhuma já demonstrou substituir COMP+K nas instâncias difíceis.**

A candidata que considero mais interessante agora é uma **formulação de fluxo por grupos de origens**, com estas propriedades:

- Não enumera conjuntos conectados.
- Usa \(k\) fluxos, onde \(k\) é o número escolhido de grupos, em vez de necessariamente usar \(m\) fluxos.
- Mantém o pareamento livre entre origens e destinos.
- Só exige variáveis binárias de instalação.
- Recupera a relaxação de COMP quando há um único grupo.
- Não enfraquece a relaxação quando um grupo é subdividido.
- Pode ser estritamente mais forte que COMP+K mesmo com apenas dois grupos.

Nesta análise, obtive um exemplo concreto na instância existente `Sec59(L=7)`:

\[
z_{\mathrm{LP}}(\mathrm{COMP+K})=\frac{11}{3},
\qquad
z_{\mathrm{LP}}(\text{dois grupos}+K)=\frac92.
\]

Esses valores decorrem de demonstrações e testemunhas racionais apresentadas adiante. **Não são resultados de uma nova campanha experimental.**

A diferença de tamanho também merece atenção: em `puc-hc12p-seed-r1`, a T18 completa teria aproximadamente **51,38 milhões de variáveis**; a formulação proposta com quatro grupos teria aproximadamente **221 mil**, antes do presolve.

Minha escolha seria, portanto:

> **Recuperar a ideia da desagregação, corrigir seu acoplamento e estudar uma versão com tamanho controlado. Manter os cortes por origem como concorrente, não como decisão já tomada.**

---

## 2. Inventário das formulações existentes

Há uma questão de nomenclatura: nos experimentos atuais, **COMP já costuma significar a variante U com fluxo contínuo e K**. Abaixo, separo “U” de “U+K” para evitar contar os mesmos cortes duas vezes.

Escrevendo \(a_v=1_{v\in S}\), \(b_v=1_{v\in T}\), a formulação U usa:

\[
\min \sum_v y_v,
\]

\[
\operatorname{out}_f(v)-\operatorname{in}_f(v)=a_v-b_v,
\]

\[
\operatorname{in}_f(v)\le b_v+(m-b_v)y_v,
\qquad
\operatorname{out}_f(v)\le a_v+(m-a_v)y_v.
\]

O fluxo percorre o dígrafo de alcance \(A_r\). A variante COMP permite fluxo contínuo, preservando a equivalência física quando \(y\) é binário.

| Formulação ou método | Estado real | Propriedades e limitações relevantes |
|---|---|---|
| **U / baseline** | Implementada em `baseline.py` | Fluxo agregado; \(n+|A_r|\) variáveis. Trata \(S\cap T\), permanência e estações em terminais. Equivalência física demonstrada no projeto. |
| **COMP, isto é, U+K com fluxo contínuo** | Referência dos experimentos recentes | Modelo inteiro exato; relaxação fortalecida por C1/C2/C4. Continua deixando gaps substanciais em diversas instâncias grandes. |
| **F-CC** | Implementada nas formas \(q=(W,I,J)\) e separada | Exata com apenas \(y\) binário. Seu LP domina U. A forma separada reduz a enumeração de \(I,J\), mas ainda enumera conjuntos conectados \(W\). |
| **F-CC+K** | Implementada em `fcc_k.py`; selecionada pela N1 | Ganhos de LP documentados em Sec59, HB e BP. Escalabilidade explícita insuficiente para o objetivo atual. |
| **F-C3** | Implementada e formalizada na N1 | Fortalece F-CC por redes de trios. Crescimento associado a \(\binom m3|\mathcal W|\). Ganho observado em Tri, onde o núcleo inteiro já resolve o ótimo. |
| **T18 / desagregação por origem** | Implementada em `desagregacao.py` | \(n+m^2+m|A_r|\) variáveis; \(p\) e fluxos binários no código. A alegação documental de dominância sobre U é falsa sem correção. Há sinais positivos de LP, mas avaliação pequena. |
| **Modelo estendido VI** | Implementação histórica em `modelo_estendido.py` | Instalações só em intermediários, outras origens bloqueadas e destinos sem saída. **Outro problema**; seu desempenho não decide a qualidade da desagregação all-vertices. |
| **F-b/F-c/F-b-cut/F-h** | Definições em `direcoes-pli-min-station.md` | Fluxos por origem/destino, projeções por cortes e caminhos. Não correspondem a uma implementação escalável validada nos casos difíceis. O documento já registra a necessidade de conservar as restrições agregadas. |
| **Núcleo inteiro K** | Implementado e amplamente medido | Relaxação do problema físico. Pode produzir excelentes LBs; uma solução do núcleo não é necessariamente uma instalação viável. |
| **C3** | Separador implementado | Trabalha com alcançabilidade individual. Não implementa o pareamento compartilhado da proposta anterior. |
| **C6** | Implementado | Fortalecimento associado a Hall/cobertura de primeiro salto. Não eliminou os gargalos de SC-GF2 nem estabeleceu vantagem geral. |
| **BC-y / CBI** | Implementados em `bc_yspace.py` | Seleção de instalações com oráculo e cortes de viabilidade. A campanha E12 não demonstrou vantagem suficiente sobre COMP e núcleo. |
| **Benders clássico histórico** | Implementado em `experiments/benders/` | Sua decomposição básica reproduz a projeção do agregado. O script remove \(S\cap T\), procedimento inválido em geral e já apontado na documentação de validação. |
| **Cumulativa / estados de bateria** | Implementada em `experiments/cumulative/` | Representa consumo e recarga no grafo original. Usa ativações separadas por estado, mais fracas que o acoplamento total necessário para reproduzir o LP de U. |
| **Lagrangeanas históricas** | Implementadas, com bundle/subgradiente | Dualizam ativações da base; não criam automaticamente um limite superior ao LP dessa base. Algumas implementações exigem \(S\cap T=\varnothing\). |
| **F-OD** | Referenciada historicamente | Não encontrei uma definição operacional auditável que permita tratá-la como modelo implementado. Não a uso em cadeias de dominância. |

Fontes centrais para conferir esse inventário: [direções de PLI](https://github.com/ElielLucas/min-station/blob/e25b056/docs/technical/reference/tecnico/direcoes-pli-min-station.md), [T18](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/alternative-formulations/desagregacao.py), [cumulativa](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/cumulative/cumulativo_min_station.py) e [provas F-CC/F-C3](https://github.com/ElielLucas/min-station/blob/e25b056/docs/technical/reference/formulacoes/provas-fcc-fc3.md).

**O histórico não justifica encerrar toda a linha de desagregação.** Ele justifica rejeitar sua implantação completa e ingênua. A decisão de abandonar a desagregação parcial porque F-CC seria mais estruturada não foi acompanhada de uma comparação que demonstrasse sua inferioridade computacional.

Também é preciso corrigir a leitura da campanha recente:

- Os seis pares resolvidos estão no diretório `main-20261011T005611Z`.
- A seleção da campanha estendida registrou `NOT_ELIGIBLE`, com nenhuma instância selecionada.
- **Não houve ali uma campanha de 3.600 segundos.**

A evidência continua desfavorável à F-CC explícita: em HB-q5, foram **2.390.603 variáveis e 100,59 s totais**, contra **93 variáveis e 0,69 s** de COMP. Porém, isso caracteriza o custo nessa seleção de instâncias pequenas, não a qualidade de todos os métodos implícitos possíveis.

A N2 permanece `FAIL`. Seus quatro certificados vieram do certificador N1; ENUM estava desabilitado no runner e N2-box iniciou com multiplicadores zero. Isso não demonstra que a relaxação completa de F-CC seja intrinsecamente fraca.

---

## 3. Revisão das alternativas da literatura

A literatura oferece mecanismos úteis, mas não um modelo pronto que possa ser transplantado sem revisão.

| Referência | Ideia aproveitável | Limite da transferência |
|---|---|---|
| **Das, Hanaka, Melissinos e Ono, 2026. _Charging Station Placement for Anonymous Mobile Agents: A Parameterized Complexity Perspective_. IJCAI, 72–80. DOI: 10.24963/ijcai.2026/9.** | Grafo de alcance e viabilidade por atribuição de agentes a terminais. | É o mesmo problema de referência. Seus resultados não demonstram desempenho de uma nova PLI. [IJCAI](https://www.ijcai.org/proceedings/2026/9?utm_source=chatgpt.com) |
| **Chen, Ljubić e Raghavan, 2015. _The Generalized Regenerator Location Problem_. INFORMS Journal on Computing 27(2), 204–220. DOI: 10.1287/ijoc.2014.0621.** | Divisão de vértices, formulações multicommodity e projeção por cortes de vértices. | As exigências de comunicação são especificadas; não são uma bijeção livre entre \(S\) e \(T\). Não podemos impor que todas as estações ou terminais pertençam a uma única componente. [terpconnect.umd.edu](https://terpconnect.umd.edu/~raghavan/preprints/grlp.pdf?utm_source=chatgpt.com) |
| **Kazemi, Le Bodic, Ernst e Krishnamoorthy, 2021. _New partial aggregations for multicommodity network flow problems: An application to the fixed-charge network design problem_. Computers & Operations Research 136, 105505.** | Controlar o compromisso entre tamanho e força por agregação parcial. | O artigo agrega commodities em partes da rede e trata demandas especificadas. A formulação por grupos abaixo é uma adaptação própria ao pareamento livre, não uma transcrição desse modelo. [Monash University](https://research.monash.edu/en/publications/new-partial-aggregations-for-multicommodity-network-flow-problems?utm_source=chatgpt.com) |
| **Kuby e Lim, 2005. _The flow-refueling location problem for alternative-fuel vehicles_. Socio-Economic Planning Sciences 39(2), 125–145. DOI: 10.1016/j.seps.2004.03.001.** | Localização de recarga e representação de sequências de abastecimento. | O FRLM trabalha com fluxos OD sobre caminhos especificados e maximização de cobertura. Fixar esses caminhos ou pares alteraria MIN-STATION. [Arizona State University](https://asu.elsevierpure.com/en/publications/the-flow-refueling-location-problem-for-alternative-fuel-vehicles/?utm_source=chatgpt.com) |
| **MirHassani e Ebrazi, 2013. _A Flexible Reformulation of the Refueling Station Location Problem_. Transportation Science 47(4), 617–628. DOI: 10.1287/trsc.1120.0430.** | Evitar a enumeração de combinações de estações por reformulação em rede. | Sustenta investigar representações compactas, mas não transfere seus ganhos experimentais para o nosso problema. [Transportation Science](https://pubsonline.informs.org/doi/10.1287/trsc.1120.0430?utm_source=chatgpt.com) |
| **Gendron e Larose, 2012. _Branch-and-Price-and-Cut for Large-Scale Multicommodity Capacitated Fixed-Charge Network Design_. CIRRELT-2012-74.** | Ligações fortes desagregadas, geração de linhas/colunas e relação com formulações por caminhos. | São demandas OD fixas e custos/capacidades de arcos. Seu estudo também evidencia degenerescência e custo das ligações fortes; geração de colunas não elimina esses problemas. [cirrelt.ca](https://www.cirrelt.ca/documentstravail/cirrelt-2012-74.pdf?utm_source=chatgpt.com) |
| **Zetina, Contreras e Cordeau, 2019. _Exact algorithms based on Benders decomposition for multicommodity uncapacitated fixed-charge network design_. Computers & Operations Research 111, 311–324. DOI: 10.1016/j.cor.2019.07.007.** | Benders fortalecido, seleção de cortes e integração com busca inteira. | Justifica estudar uma decomposição depois de identificar um subproblema e uma relaxação úteis. Não demonstra que decompor U fortaleça seu LP. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0305054819301832?utm_source=chatgpt.com) |
| **Lu et al., 2019. _Optimizing resource recharging location-routing plans_. Computers & Industrial Engineering 127, 1241–1258. DOI: 10.1016/j.cie.2018.03.015.** | Redes com estados de recurso. | Tempo, roteamento e outras restrições do artigo não pertencem ao MIN-STATION. Aqui só interessa a representação exata da autonomia. [Arizona State University](https://asu.elsevierpure.com/en/publications/optimizing-resource-recharging-location-routing-plans-a-resource-/?utm_source=chatgpt.com) |

Duas consequências importantes:

1. **Caminhos, desagregação, divisão de vértices e estados de bateria são técnicas conhecidas.** Não devem ser apresentados como invenções do projeto.
2. O possível resultado científico está na adaptação ao pareamento anônimo, nas relações poliedrais demonstradas e na identificação experimental de quando cada representação compensa.

---

## 4. Formulações candidatas

Seleciono três **alternativas de implementação matemática**, com uma ressalva: **A e B pertencem à mesma família poliedral**. B representa implicitamente a versão mais desagregada de A; não é uma terceira fonte independente de força.

As definições abaixo são propostas para esta investigação. Não são modelos já implementados no repositório.

### A. Fluxo por grupos de origens com acoplamento global

Esta é minha candidata principal.

Considere uma partição:

\[
\mathcal B=\{B_1,\ldots,B_k\}
\]

de \(S\), com blocos não vazios. Defina:

\[
c_{Bv}=|B|-1_{\{v\in B\}},
\]

\[
\kappa_v=
\begin{cases}
m-1,&v\in S\cup T,\\
m,&v\notin S\cup T.
\end{cases}
\]

Esses coeficientes limitam o número de **caminhos simples que precisam recarregar** no vértice. Não representam capacidade física de atendimento das estações.

**Variáveis**

\[
y_v\in\{0,1\},
\qquad
f^B_{uv}\ge0 \quad ((u,v)\in A_r),
\]

\[
g^B_v\ge0,
\qquad
0\le p_{Bt}\le1 \quad(t\in T),
\]

\[
0\le h^B_v\le1 \quad(v\in B\cap T).
\]

Interpretações:

- \(f^B\): deslocamentos dos robôs cujas origens pertencem a \(B\);
- \(g^B_v\): trânsito com recarga em \(v\);
- \(p_{Bt}\): atendimento do destino \(t\) pelo grupo \(B\);
- \(h^B_v\): permanência da origem \(v\) no próprio destino.

Adote \(p_{Bv}=0\) fora de \(T\) e \(h^B_v=0\) fora de \(B\cap T\).

**Conservação nos dois lados do vértice**

Para todo \(B,v\):

\[
\sum_{u:(u,v)\in A_r}f^B_{uv}+h^B_v
=
p_{Bv}+g^B_v,
\tag{A1}
\]

\[
\sum_{w:(v,w)\in A_r}f^B_{vw}+h^B_v
=
1_{\{v\in B\}}+g^B_v.
\tag{A2}
\]

A primeira equação separa chegada final de recarga. A segunda separa partida inicial de saída após recarga.

**Atendimento global**

\[
\sum_{B\in\mathcal B}p_{Bt}=1
\qquad(t\in T).
\tag{A3}
\]

Somando os balanços, obtém-se automaticamente:

\[
\sum_{t\in T}p_{Bt}=|B|.
\]

Portanto, não há atribuição prévia de destinos aos grupos.

**Ativação por grupo**

\[
g^B_v\le c_{Bv}y_v
\qquad(B\in\mathcal B,\ v\in V).
\tag{A4}
\]

Se \(v\in B\), o robô que nasce ali pode iniciar sem recarga e seu caminho simples não precisa retornar à própria origem. Restam, no máximo, \(|B|-1\) caminhos do grupo que podem usar \(v\) internamente.

**Acoplamento global**

\[
\sum_{B\in\mathcal B}g^B_v\le\kappa_v y_v
\qquad(v\in V).
\tag{A5}
\]

Esta família é essencial: impede que as ativações separadas por grupo percam o limite agregado correto nos terminais.

**Cortes e objetivo**

\[
\sum_{v\in Z}y_v\ge1
\qquad(Z\in K),
\tag{A6}
\]

\[
\min\sum_{v\in V}y_v.
\tag{A7}
\]

Só \(y\) precisa ser binário. Os demais domínios podem ser contínuos.

A formulação substitui o fluxo agregado por fluxos de grupos. Não exige acrescentar uma cópia independente de COMP.

### B. Caminhos com ativação por origem e acoplamento global

Seja \(\mathcal P_s\) o conjunto de todos os caminhos simples no grafo de alcance que começam em \(s\) e terminam em algum \(t\in T\).

Inclua:

- caminhos diretos;
- o caminho de comprimento zero quando \(s\in T\);
- caminhos cujos vértices internos incluem origens ou destinos.

Use \(x_P\ge0\) e \(y_v\in\{0,1\}\):

\[
\sum_{P\in\mathcal P_s}x_P=1
\qquad(s\in S),
\tag{B1}
\]

\[
\sum_{P:\operatorname{fim}(P)=t}x_P=1
\qquad(t\in T),
\tag{B2}
\]

\[
\sum_{\substack{P\in\mathcal P_s\\v\in\operatorname{int}(P)}}x_P
\le y_v
\qquad(s\in S,\ v\ne s),
\tag{B3}
\]

\[
\sum_{P:v\in\operatorname{int}(P)}x_P
\le\kappa_v y_v
\qquad(v\in V),
\tag{B4}
\]

mais K e \(\min\sum_vy_v\).

A atribuição está implícita:

\[
p_{st}=\sum_{P:s\rightarrow t}x_P.
\]

**B4 é uma correção relevante em relação à versão histórica apenas por caminhos.** Não basta supor que as ligações individuais impliquem todas as ativações da base.

Essa formulação tem a mesma projeção em \(y\) que A com grupos unitários, após remoção de circulações.

Seu interesse é computacional: representar caminhos implicitamente, evitando construir \(m|A_r|\) variáveis.

### C. Recuperação da cumulativa com ativação total de recarga

Para o problema original, com arestas unitárias e \(r\) inteiro, use estados \((v,q)\), onde \(q\in\{0,\ldots,r\}\) é o consumo desde a última recarga.

Variáveis contínuas:

- \(F^q_{uv}\): movimento por uma aresta original, de consumo \(q\) para \(q+1\);
- \(z_v^q\): recarga em \(v\), voltando do consumo \(q\ge1\) ao consumo zero;
- \(e_t^q\): absorção final no destino \(t\), com consumo \(q\).

A conservação é:

\[
\sum_{u:\{u,v\}\in E}F^{q-1}_{uv}
+
1_{\{q=0\}}
\left(a_v+\sum_{\ell=1}^{r}z_v^\ell\right)
=
\sum_{w:\{v,w\}\in E}F^q_{vw}
+
1_{\{q\ge1\}}z_v^q
+
e_v^q,
\tag{C1}
\]

omitindo termos fora dos índices e usando \(e_v^q=0\) quando \(v\notin T\).

Exija:

\[
\sum_{q=0}^{r}e_t^q=1
\qquad(t\in T),
\tag{C2}
\]

\[
\boxed{\sum_{q=1}^{r}z_v^q\le\kappa_v y_v}
\qquad(v\in V),
\tag{C3}
\]

além de K, \(y\) binário e objetivo \(\min\sum_vy_v\).

O código histórico usa \(z_v^q\le my_v\) separadamente para cada estado. Isso permite reutilizar a mesma instalação fracionária em vários níveis sem controlar a soma.

A versão corrigida tem outro propósito: **reproduzir a força de COMP usando uma representação potencialmente menor quando o grafo de alcance fica denso**. Não a proponho como fonte de ganho LP.

---

## 5. Comparação matemática

### Equivalência inteira da candidata A

**Instalação física \(\Rightarrow\) A.**

Escolha uma bijeção viável e caminhos simples em \(H=G^r\). Agrupe os caminhos conforme suas origens.

- Cada destino é atendido uma vez.
- Vértices internos exigem estação.
- No bloco \(B\), no máximo \(|B|-1\) caminhos usam internamente uma origem pertencente ao próprio bloco.
- Globalmente, no máximo \(m-1\) caminhos usam internamente um terminal, pois pelo menos um caminho começa ou termina nele.

Esses caminhos produzem variáveis que satisfazem A1–A6. Permanências usam \(h\).

**A com \(y\) binário \(\Rightarrow\) instalação física.**

Some A1–A2 sobre os grupos. Com

\[
F=\sum_B f^B,\quad G_v=\sum_Bg^B_v,\quad H_v=\sum_Bh^B_v,
\]

obtém-se:

\[
\operatorname{in}_F(v)+H_v=b_v+G_v,
\qquad
\operatorname{out}_F(v)+H_v=a_v+G_v.
\]

Logo, o balanço de U vale. Como \(H_v\ge0\) e \(G_v\le\kappa_vy_v\), também valem suas ativações de entrada e saída.

Assim, a solução projeta-se em U com o mesmo \(y\). Pela equivalência de U já demonstrada para o problema original, a instalação é fisicamente viável.

**Resultado: A é inteira e fisicamente exata para qualquer partição de \(S\).**

### Um grupo recupera o LP da base

Com \(\mathcal B=\{S\}\), a projeção em \(y\) coincide com a de U.

O caso delicado é \(v\in S\cap T\). Se o fluxo agregado tem entrada e saída iguais a \(x_v\), escolha:

\[
h_v=\max\{0,1-x_v\},
\qquad
g_v=\max\{0,x_v-1\}.
\]

A ativação de U garante:

\[
g_v\le(m-1)y_v.
\]

Nos demais tipos de vértices, basta usar como \(g_v\) o fluxo de trânsito, descontando a partida ou chegada gratuita.

Isso demonstra a direção inversa, inclusive para \(y\) fracionário.

### Refinar a partição não enfraquece o LP

Se \(B\) é dividido em \(B'\) e \(B''\), somar suas variáveis recupera uma solução do bloco original, pois:

\[
c_{B'v}+c_{B''v}=c_{Bv}.
\]

Portanto, para uma partição \(\mathcal B'\) que refine \(\mathcal B\):

\[
z_{\mathrm{LP}}(A(\mathcal B)+K)
\le
z_{\mathrm{LP}}(A(\mathcal B')+K).
\]

Partições que não são refinamentos uma da outra não recebem uma ordem automática.

### Relação com F-CC

Uma configuração \((W,I,J)\) pode ser decomposta em uma bijeção e caminhos simples internos a \(W\). Para cada bloco \(B\), o número desses caminhos que atravessa \(v\) internamente é limitado por \(c_{Bv}\).

Multiplicando pelos pesos das configurações e usando:

\[
\sum_{q:v\in W_q}\lambda_q\le y_v,
\]

obtêm-se A4 e A5. Os pares diretos não consomem trânsito interno.

Consequentemente, com o mesmo K:

\[
\boxed{
z_{\mathrm{LP}}(\mathrm{COMP+K})
\le
z_{\mathrm{LP}}(A(\mathcal B)+K)
\le
z_{\mathrm{LP}}(B+K)
\le
z_{\mathrm{LP}}(\mathrm{F\!-\!CC+K})
\le OPT.
}
\]

Essa cadeia é uma derivação para as definições acima. Não depende de aceitar a alegação antiga sobre T18.

### Relação com a proposta anterior de cortes

Considere a versão completa da proposta anterior: COMP+K, matching compartilhado e todas as restrições de fluxo unitário por origem.

Uma solução de B fornece simultaneamente:

- um matching fracionário;
- os fluxos unitários;
- um fluxo agregado viável para COMP.

Portanto, **B domina essa proposta no LP**.

Entretanto:

- não demonstrei que a dominância seja estrita;
- não estabeleci uma relação geral entre a proposta anterior e A com poucos grupos.

**Ainda não há evidência suficiente para concluir qual das duas é computacionalmente superior.**

### Contraexemplo à dominância da T18

Considere a estrela:

\[
E=\{\{a,c\},\{b,c\},\{c,d\}\},
\quad S=\{a,b\},\quad T=\{c,d\},\quad r=1.
\]

Na T18 relaxada:

\[
y_c=\frac12,\qquad y_a=y_b=y_d=0,
\]

\[
p_{ac}=p_{ad}=p_{bc}=p_{bd}=\frac12,
\]

\[
f^a_{ac}=f^b_{bc}=1,
\qquad
f^a_{cd}=f^b_{cd}=\frac12.
\]

As restrições implementadas aceitam o ponto, com objetivo \(1/2\).

Na base, chegam pelo menos duas unidades a \(c\), mas:

\[
\operatorname{in}(c)\le1+y_c.
\]

Logo, \(y_c\ge1\).

A cumulativa histórica também permite objetivo \(1/2\) nesse exemplo: uma unidade recarrega em \(c\), sob a ativação \(z_c^1\le2y_c\).

**Esses contraexemplos são sem K.** Demonstram a falha das alegações gerais; não afirmam que o mesmo ponto sobreviva aos cortes atuais.

### Exemplo estrito com o K real: Sec59

Na instância `Sec59(L=7)`, existem:

- origens \(s_1,s_2,s_3\);
- destinos \(t_1,t_2,t_3\);
- cadeia \(w_1,\ldots,w_7\);
- arestas \(s_1t_1,s_2t_1,s_1w_1,s_2w_1\);
- arestas consecutivas da cadeia;
- arestas \(w_7t_2,t_2s_3,s_3t_3\).

O K efetivamente gerado contém:

\[
y_{t_1}+y_{w_1}\ge1,
\qquad
y_{s_3}+y_{w_7}\ge1.
\]

Pelo menos um dos dois robôs à esquerda precisa atravessar toda a cadeia.

Em COMP:

\[
y_{w_i}\ge\frac13.
\]

As duas desigualdades de K, somadas às cinco posições interiores, dão:

\[
z_{\mathrm{LP}}(\mathrm{COMP+K})
\ge 2+5\cdot\frac13=\frac{11}{3}.
\]

A igualdade é atingida com \(y_{w_1}=y_{w_7}=1\), demais \(y_{w_i}=1/3\), e metade de cada origem esquerda seguindo pela cadeia.

Agora use:

\[
\mathcal B=\big\{\{s_1,s_2\},\{s_3\}\big\}.
\]

O primeiro grupo precisa enviar pelo menos uma unidade pela cadeia. Por A4:

\[
1\le g^{\{s_1,s_2\}}_{w_i}\le2y_{w_i}.
\]

Assim:

\[
z_{\mathrm{LP}}(A(\mathcal B)+K)
\ge2+5\cdot\frac12=\frac92.
\]

A mesma distribuição de caminhos, agora com os cinco \(y_{w_i}=1/2\), atinge a igualdade.

O ótimo inteiro é 7. O valor registrado para F-CC+K na N1 é 5.

**Limitação importante:** a proposta anterior com todos os cortes por origem também alcança \(9/2\) nesse exemplo. Ele demonstra ganho sobre COMP+K, mas não superioridade sobre aquela proposta.

### Tratamento de \(S\cap T\)

As três candidatas preservam permanência e troca de ocupantes.

Um contraexemplo à remoção prévia de \(S\cap T\) é:

\[
G:a-v-b,\quad S=\{a,v\},\quad T=\{v,b\},\quad r=1.
\]

Sem estações, os movimentos \(a\to v\) e \(v\to b\) são viáveis. Se \(v\) for removido dos conjuntos de terminais, sobra \(a\to b\), que exige uma estação.

O validador existente confirmou esses dois resultados nesta análise. Isso afeta o script histórico de Benders, **não implica invalidar o CBI atual**.

### Certificação e pricing da candidata B

Com multiplicadores não negativos \(\gamma_{sv}\) para B3 e \(\mu_v\) para B4, o custo reduzido de um caminho é:

\[
\bar c_P=
\sum_{v\in\operatorname{int}(P)}
(\gamma_{sv}+\mu_v)-\pi_s-\tau_t.
\]

Os custos internos são não negativos. Para cada origem, um cálculo de caminhos mínimos numa rede com vértices divididos encontra o melhor destino, descontando \(\tau_t\).

**Não é necessário resolver um problema de configuração conectada.** A autonomia já está incorporada em \(H\); não existe aqui uma restrição adicional de comprimento total da rota.

Há também uma certificação simples. Se \(\theta_Z\ge0\) corresponde a K, defina:

\[
\eta_v=
\max\left\{
0,\,
\kappa_v\mu_v+
\sum_{s\ne v}\gamma_{sv}
+\sum_{Z\ni v}\theta_Z-1
\right\},
\]

\[
L=\sum_s\pi_s+\sum_t\tau_t+\sum_Z\theta_Z-\sum_v\eta_v.
\]

Se \(\ell_s\) é um limite inferior válido para o menor custo reduzido de todos os caminhos de \(s\), então:

\[
\boxed{
LB=
\max\left\{0,\,
L+\sum_s\min(0,\ell_s)
\right\}
\le z_{\mathrm{LP}}(B+K)\le OPT.
}
\]

A prova consiste em substituir:

\[
\pi_s\leftarrow\pi_s+\min(0,\ell_s),
\]

tornando todas as restrições duais de caminhos satisfeitas.

Com multiplicadores racionalizados consistentemente e caminhos mínimos em aritmética exata, esse mecanismo evita depender de um `ObjBound` de pricing MIP. **Isso é uma vantagem matemática potencial, não um certificador já implementado.**

---

## 6. Comparação de escalabilidade

Denote \(a=|A_r|\), \(e=|E|\), \(k=|\mathcal B|\), \(h=|S\cap T|\).

| Representação | Variáveis antes do presolve | Principal custo adicional |
|---|---:|---|
| COMP | \(n+a\) | Construção do alcance e LP/MIP agregado |
| T18 completa | \(n+m^2+ma\) | Fluxos e balanços por origem |
| **A, com \(k\) grupos** | \(n+k(a+n+m)+h\) | Aproximadamente \(3kn+n+m+|K|\) linhas |
| **B, por caminhos** | \(n+\) caminhos gerados | Até \(m(n-1)\) ligações por origem; pricing e degenerescência |
| **C, cumulativa corrigida** | \(2re+(n+m)(r+1)\) | Conservação em \(n(r+1)\) estados |
| Proposta anterior com \(u\) origens | \(n+a+um\), além dos cortes | Separação de até \(u\) redes por rodada |
| F-CC separada | \(n+|D|+|\mathcal W|+\sum_W(|S\cap B(W)|+|T\cap B(W)|)\) | Enumeração exponencial |
| F-C3 | F-CC mais \(O(m^3|\mathcal W|)\) | Redes de trios |

As contagens abaixo foram calculadas a partir do manifesto atual. **São estimativas de tamanho, não medições de modelos construídos.**

| Instância | \(n\) | \(m\) | \(a\) | T18 completa | A com 4 grupos |
|---|---:|---:|---:|---:|---:|
| `puc-hc11p-seed-r1` | 2.048 | 512 | 22.528 | 11.798.528 | 102.400 |
| `puc-hc12p-seed-r1` | 4.096 | 1.024 | 49.152 | 51.384.320 | 221.184 |
| `puc-w3c571-seed-r1` | 3.997 | 1.142 | 20.556 | 24.783.113 | 106.777 |
| `mapf-den312d-m50-f2-rho` | 2.445 | 50 | 549.696 | 27.489.745 | 2.211.214 |
| `mapf-random-64-64-20-m100-f4` | 3.270 | 100 | 121.632 | 12.176.470 | 503.278 |
| `pucn-cc7-3n-regiao-f2` | 2.187 | 111 | 214.326 | 23.804.694 | 868.683 |
| `vienna-I056-regiao-f4` | 1.991 | 25 | 381.600 | 9.542.616 | 1.536.455 |

A leitura é distinta por regime:

- **PUC com muitos robôs e alcance esparso:** poucos grupos parecem materialmente viáveis. A desagregação completa é uma escolha muito mais arriscada.
- **MAPF/Vienna com alcance denso:** mesmo quatro grupos podem custar milhões de variáveis. É necessário limitar grupos ou mudar a representação.
- **Caminhos:** eliminam a construção de \(ma\) variáveis, mas não eliminam as linhas de ligação. Em `w3c571`, são potencialmente **4.564.574 ligações**.
- **Bateria:** pode reduzir variáveis em alcance denso. A contagem corrigida é aproximadamente **102 mil** para `I056` e **183 mil** para `den312d`, contra aproximadamente 384 mil e 552 mil de COMP. Isso vem acompanhado de mais equações de estado.

Para C, a projeção LP coincide com a de COMP: decompor o fluxo em deslocamentos entre recargas produz caminhos em \(H\); inversamente, cada salto de \(H\) pode ser realizado nos estados de consumo. A restrição de recarga total preserva o mesmo limite de trânsito.

Logo, **C disputa custo de representação, não força de relaxação**.

Também não elimina automaticamente o preparo de \(H\): o pipeline atual de K ainda utiliza suas vizinhanças.

**Aplicabilidade prática não está demonstrada apenas pelas contagens.** Memória de objetos Python, fatoração do LP, degenerescência e comportamento do presolve continuam desconhecidos para as propostas.

Os casos difíceis realmente existem. Nos registros de 600 s:

| Instância | LB numérico | UB numérico | Gap |
|---|---:|---:|---:|
| `puc-hc11p-seed-r1` | 96 | 160 | 40,0% |
| `puc-w3c571-seed-r1` | 666 | 1.131 | 41,1% |
| `mapf-den312d-m50-f2-rho` | 4 | 9 | 55,6% |
| `mapf-random-64-64-20-m100-f4` | 41 | 70 | 41,4% |
| `pucn-cc7-3n-regiao-f2` | 9 | 14 | 35,7% |

As versões legadas `hc9u`, `hc10p`, `hc11p`, `hc12p` e `bip42p` também estão presentes. Seus tempos históricos não devem ser comparados diretamente com uma campanha nova sem controlar ambiente, parâmetros e identidade da instância.

---

## 7. Matriz de decisão

| Direção | Força LP | Escala potencial | Risco de implementação | Evidência no projeto | Papel recomendado |
|---|---|---|---|---|---|
| **COMP+K** | Referência | Já executa as classes difíceis | Baixo | Ampla | Controle obrigatório |
| **Cortes por origem anteriormente propostos** | Pelo menos COMP; ganho específico ainda precisa ser medido | Controlável por número de origens e cortes | Médio | Proposta matemática; sem campanha própria | Concorrente de baixo compromisso |
| **A: grupos de origens** | Hierarquia provada; ganho estrito sobre COMP+K em Sec59 | Boa perspectiva com poucos grupos; custo cresce com \(ka\) | Baixo a médio | Provas e testemunha desta análise; sem desempenho medido | **Primeiro protótipo recomendado** |
| **B: caminhos corrigidos** | Igual à versão totalmente desagregada de A | Evita \(ma\) colunas, mas pode ter \(mn\) linhas | Médio a alto | Caminhos já documentados; sem implementação atual validada | Condicional à necessidade de maior desagregação |
| **C: cumulativa corrigida** | Igual a COMP | Interessante quando \(re\ll a\) | Médio | Código histórico existente, com ativação diferente | Reserva para gargalo de representação |
| **F-CC implícita** | Mais forte que A/B pela cadeia demonstrada | Pricing e certificação continuam difíceis | Alto | N1 positiva para força; N2 negativa no objetivo certificado | Referência teórica; não primeira continuação |
| **F-C3 completa** | Ainda mais forte em alguns casos | Muito desfavorável em \(m\) grande | Alto | Ganho restrito na N1 | Pausar expansão |

Isso responde às quatro opções exigidas:

1. **Manter COMP+K e acrescentar cortes:** continua defensável, mas não está automaticamente escolhida.
2. **Recuperar uma alternativa existente:** é a opção que recomendo, através de A.
3. **Desenvolver uma formulação estendida sem enumeração:** A satisfaz esse papel, aproveitando ideias existentes com uma definição corrigida.
4. **Usar representação implícita:** B é mais atraente como próximo passo do que retomar imediatamente o pricing conectado de F-CC.

Não há razão, neste momento, para desenvolver os três algoritmos em paralelo.

---

## 8. Recomendação principal

**Eu priorizaria a formulação A, começando com duas ou quatro classes de origens.**

O motivo não é somente seu tamanho. A combinação é favorável porque:

1. **Explora uma propriedade específica do MIN-STATION:** os robôs são anônimos. Podemos agrupar origens sem fixar destinos e sem alterar a viabilidade inteira.
2. **Tem uma referência matemática interna:** um grupo recupera COMP; refinamentos formam uma hierarquia.
3. **Corrige o problema da T18:** a capacidade global de trânsito continua ligada às mesmas decisões de rota.
4. **Produz um MIP completo:** com uma partição fixa, pode-se usar diretamente branch-and-bound, sem pricing em nós.
5. **Dispensa inicialmente um novo motor de separação ou certificação.**
6. **Já possui um exemplo relevante de ganho além de K**, embora pequeno.

A partição deve ter fundamento estrutural. Algumas possibilidades são agrupar origens com vizinhanças de alcance semelhantes ou separar regiões/bolsões com demandas distintas. Outra opção é isolar poucas origens críticas e manter as restantes em um bloco agregado.

**Essas políticas de agrupamento são hipóteses computacionais.** O exemplo Sec59 não demonstra que agrupamento geográfico ou por similaridade será bom no benchmark.

O risco principal é simples: poucos grupos podem preservar quase toda a fraqueza do agregado. Se o ganho exigir centenas de grupos, a vantagem de tamanho desaparece. Esse risco pode ser investigado rapidamente.

Eu não priorizaria agora:

- T18 completa com \(p\) e todos os fluxos binários;
- branch-and-price;
- uma nova rodada genérica de CBI;
- expansão de F-C3;
- novos ajustes na Lagrangeana que apenas reproduzem o LP de U.

Em SC-GF2, por exemplo, o núcleo já demonstrou resolver o que COMP não provou no orçamento. Aumentar a complexidade dos fluxos não é uma resposta automaticamente adequada a esse regime.

---

## 9. Experimentos discriminantes de baixo custo

Proponho uma sequência que permita abandonar cedo uma ideia sem ganho.

### Primeiro: fechar e revisar as propriedades matemáticas

Antes do código experimental:

- revisar A nas duas direções;
- revisar a igualdade entre A com um grupo e COMP;
- revisar a monotonicidade por refinamento;
- revisar os casos de \(S\cap T\), permanência e estações em terminais;
- comparar A unitária com B e com T18 corrigida;
- preservar os contraexemplos apresentados.

A revisão independente deve distinguir as provas gerais das testemunhas numéricas.

**O que executei agora:** extração dos dois cortes K de Sec59, verificação racional dos pontos de valores \(11/3\) e \(9/2\), e duas chamadas ao `viavel` no exemplo de sobreposição. Não executei `optimize`.

### Segundo: um protótipo mínimo de A

Implementar apenas A, reutilizando grafos, K e validador.

Em instâncias pequenas:

- enumerar instalações \(C\subseteq V\);
- comparar viabilidade com `viavel`;
- conferir A com um grupo versus COMP;
- conferir refinamentos aninhados;
- comparar o LP totalmente desagregado com uma referência por caminhos/fluxos;
- incluir Sec59, Tri, SharedTerminal, permanência, terminais usados como estações e o contraexemplo da estrela.

**Parada imediata:** qualquer perda de uma instalação física válida, ganho abaixo do ótimo físico ou violação da hierarquia demonstrada.

### Terceiro: piloto LP nas seis instâncias de desenvolvimento

Os seis nomes anteriormente propostos existem e estão classificados como desenvolvimento no manifesto atual:

| Instância | \(n\) | \(m\) | \(r\) | Função no piloto |
|---|---:|---:|---:|---|
| `puc-cc9-2p-seed-r1` | 512 | 32 | 1 | Gap residual pequeno |
| `puc-bip42p-regiao-f2` | 1.200 | 100 | 1 | Compartilhamento e muitos terminais |
| `pucn-cc3-10n-seed-r1` | 1.000 | 25 | 1 | Topologia distinta |
| `mapf-room-32-32-4-m10-f8` | 682 | 10 | 4 | Poucos robôs e autonomia maior |
| `vienna-I056-regiao-f4` | 1.991 | 25 | 12 | Alcance denso |
| `puc-w3c571-seed-r1` | 3.997 | 1.142 | 1 | Teste indispensável de escala em \(m\) |

Começar por COMP e A com dois grupos. Testar quatro grupos somente se houver ganho ou uma dúvida concreta a resolver.

Registrar:

- tempo de preparo, construção e LP;
- variáveis, restrições e não zeros;
- memória de pico;
- objetivo LP quando efetivamente resolvido;
- ganho sobre COMP+K;
- comparação com o limite do núcleo inteiro.

Um orçamento curto de diagnóstico, por exemplo **60–90 s por braço**, serve para detectar construção inviável ou LP caro. Um LP interrompido não deve ser registrado como ótimo nem como “igual” ao controle.

**Critério de parada:** se a linha não produzir ganho além de K nos casos de desenvolvimento, ou só melhorar Sec59 com custo alto nos casos reais, não avançar para uma campanha longa por inércia.

Há um cuidado de partição: `room` com 10 agentes está em desenvolvimento e uma variante do mesmo mapa/cenário com 25 agentes está em avaliação. Essa segunda variante não deve ser contada como origem experimental independente depois de ajustar a política na primeira. Não é necessário alterar freezes históricos para registrar essa dependência no novo estudo.

### Quarto: piloto inteiro apenas da candidata aprovada

Executar pares de **300 s**, depois **600 s** se houver sinal útil. Repetir as configurações promissoras com seeds 43 e 44.

Controles indispensáveis:

- mesma instância e mesmo K, com hashes;
- fluxo contínuo e apenas \(y\) binário nos modelos comparáveis;
- mesmos parâmetros gerais do solver;
- mesmo tratamento de soluções iniciais;
- orçamento total incluindo construção;
- validação física independente dos incumbentes;
- núcleo como controle de origem do ganho.

Comparar:

- LB e UB ao longo do tempo;
- gap absoluto e relativo;
- tempo até primeira solução;
- tempo até melhor solução;
- nós;
- memória e custo de construção.

**Só promover após ganho reproduzido em pelo menos dois grafos independentes, com custo aceitável e sem perdas graves ocultadas pela média.**

Se a formulação precisar de muitos grupos para melhorar, B passa a ser a alternativa de representação a investigar. Se o problema for exclusivamente o crescimento de \(A_r\), C passa a ser relevante.

A campanha de até uma hora vem depois, contabilizando também falhas de construção e memória. Nenhuma instância será excluída porque F-CC explícita não cabe.

Resultados numéricos do Gurobi são evidência computacional legítima. Certificação racional independente deve ser identificada separadamente. No caso de B, o objetivo do master restrito continua sem ser um LB global por si só.

---

## 10. Decisão sobre o planejamento P0–P5

**Recomendo ajustar o planejamento e inserir a decisão matemática antes de consolidar o separador por origem.**

| Etapa anterior | Decisão recomendada |
|---|---|
| **P0 — Escopo experimental** | **Manter.** Instâncias difíceis independentes da viabilidade de enumerar F-CC; identidade, origem dos grafos e orçamento total auditados. |
| **P1 — Formalização** | **Ampliar e redirecionar.** Fechar A e suas relações com COMP, T18 corrigida, caminhos e a proposta anterior. Revisão independente das provas. |
| **P2 — Separador mínimo** | **Substituir inicialmente por um protótipo mínimo de A.** Não implementar ainda três motores distintos. |
| **P3 — Integração ao COMP com cortes na raiz** | **Tornar uma decisão condicionada.** Primeiro avaliar A como MIP completo com poucos grupos; os cortes anteriores continuam como alternativa se a desagregação explícita não compensar. |
| **P4 — Comparação exploratória** | **Manter o desenho 300/600 s**, as repetições e o controle do núcleo, aplicados à candidata que passar pelo piloto. |
| **P5 — Campanha final** | **Manter condicionada ao benefício em desenvolvimento**, com até 3.600 s e aproximadamente 8–12 instâncias de avaliação escolhidas antes dos resultados. |

A decisão científica que eu tomaria agora é **reabrir a desagregação sob uma formulação por grupos, corrigida e controlável**, em um estudo curto. A versão completa da T18 não deve ser simplesmente reativada.

Há uma contribuição possível de mestrado nessa linha: demonstrar uma hierarquia exata, identificar seu compromisso entre força e tamanho e verificar se ela melhora a resolução das instâncias difíceis. **Ainda não há evidência suficiente para concluir que ela superará COMP+K em tempo ou gap final.** O próximo piloto deve responder precisamente a essa pergunta, mantendo `N2 FAIL` e todos os resultados anteriores intactos.