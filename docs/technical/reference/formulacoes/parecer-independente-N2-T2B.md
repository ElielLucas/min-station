# MIN-STATION — Parecer matemático independente da N2-T2B

**Data:** 9 de outubro de 2026.  
**Objeto:** documento anexado *n2-t2b-master-dual-pricing-revisao.md*, 445 linhas, estado **REVISED — PENDING INDEPENDENT REVIEW**, referenciado ao commit c995b54.  
**Veredito geral:** **ACCEPTED WITH CONDITIONS**.  
**Escopo:** somente F-CC+K, geração de colunas na raiz, preservando N1 e o pré-registro N2-T1.

Este parecer rederiva as afirmações dos anexos. Não substitui nem modifica o documento auditado. Nenhum arquivo do projeto ou anexo foi alterado, nenhum algoritmo foi implementado, nenhum LP/MIP foi resolvido e nenhum experimento N2 foi executado nesta revisão. Foram realizados cálculos racionais pontuais para conferir os contraexemplos descritos abaixo. Os resultados históricos do verificador são tratados como resultados **relatados**, não como execuções reproduzidas nesta rodada.

## A. Veredito geral

**ACCEPTED WITH CONDITIONS.** O master, o dual, o custo reduzido, a equivalência com a forma separada e a formulação de conectividade do pricing estão matematicamente corretos no domínio declarado. O **Teorema L é válido**, incluindo seu uso com pricing incompleto e multiplicadores que não sejam duais ótimos do RMP.

O impedimento para um aceite irrestrito está no contrato de certificação numérica: **um ObjBound finito, mesmo acompanhado de uma margem fixa ou de status OPTIMAL, não demonstra sozinho a hipótese \(\ell\le c^*\) em aritmética real exata**. A revisão reconhece esse problema em H-NUM, mas sua regra operacional de §6.2-4 ainda autoriza certificação apenas pela existência do atributo finito. Essa regra deve ser corrigida antes de implementar a parte afetada.

Há ainda duas correções matemáticas operacionais: a observação §6.1(iv) esquece a violação dos pares diretos, e o critério de parada §6.2-5 não garante a precisão absoluta de \(10^{-6}\) no objetivo. Nenhuma dessas falhas invalida a fórmula principal do Teorema L.

| Decisão | Veredito individual | Consequência |
|---|---|---|
| D-1 — Teorema L | **ACCEPTED**, com explicitação do caso \(D=\varnothing\) e correção da observação (iv) | Usar a fórmula completa, incluindo a correção dos pares diretos |
| D-2 — ObjBound | **REJECTED como certificado autossuficiente** | MIP-OPT/MIP-BOUND sem verificação adicional permanecem **UNCERTIFIED** |
| D-3 — ENUM | **ACCEPTED WITH CONDITIONS** | Aritmética exata ou intervalos comprovados, cobertura integral e vetor único preservado |
| D-4 — Pricing MIP | **ACCEPTED**, corrigindo “bijeção” para “equivalência por projeção” | Pode ser a formulação do oráculo; resolver esse MIP numericamente é uma questão distinta |

As condições podem ser satisfeitas sem trocar de formulação, sem novos cortes, sem alterar o pré-registro e sem abrir outro caminho científico. A definição é aproveitável; o ramo de certificação numérica precisa de uma decisão restritiva explícita.

## B. Vereditos individuais

### B.1. D-1 — Validade do Teorema L

#### Hipóteses necessárias

Considere o master completo definido em C.1, com todas as configurações admissíveis \(Q\), todos os pares diretos \(D\), cortes unitários \(y(Z)\ge1\), e \(0\le y\le1\). São necessárias:

1. \(G\) simples, conexo, não dirigido, unitário; \(r\ge1\), \(|S|=|T|=m\ge1\). Esses são os pressupostos do documento auditado. Não se estende a prova silenciosamente a grafos dirigidos.
2. \(\pi,\tau\) finitos e livres; \(\mu,\kappa\) finitos e não negativos.
3. Um número **finito e comprovado** \(\ell\le\min_{q\in Q}\bar c_q\), calculado para o **mesmo vetor** \((\pi,\tau,\mu)\).
4. Definição correta de \(L\), incluindo a penalização dos limites superiores de \(y\).
5. Para a conclusão adicional \(LB\le\mathrm{OPT}\), validade de todos os cortes de \(K\) para as instalações do MIN-STATION.

Não são necessárias otimalidade do RMP, factibilidade de seus multiplicadores nas colunas existentes, solução completa do pricing, nem factibilidade de \(\pi_s+\tau_t\le0\). Esta última violação é precisamente o que \(\delta\) corrige. A hipótese de cobertura global não pode ser removida.

Defina, inclusive quando não há pares diretos:

\[
\eta_v=\max\{0,\mu_v+\kappa(v)-1\},\qquad
L=\sum_s\pi_s+\sum_t\tau_t+\sum_{Z\in K}\kappa_Z-\sum_v\eta_v,
\]

\[
a=\min\{0,\ell\},\qquad
\delta=\min\Bigl(\{0\}\cup\{-\pi_s-\tau_t:(s,t)\in D\}\Bigr).
\tag{L0}
\]

A escrita com união explicita \(\delta=0\) se \(D=\varnothing\). A fórmula do anexo só funciona nesse caso se adotar, sem dizê-lo, a convenção de mínimo do conjunto vazio igual a \(+\infty\).

O limite aprovado é:

\[
\boxed{
LB_{CG}=\max\left\{0,\ L+m\min\{a,\delta\},\ \frac{L+m\delta}{1-a}\right\}
\le z_Q.
}
\tag{L1}
\]

#### Demonstração independente

Fixe qualquer solução viável \((\lambda,d,y)\) do master completo. Escreva:

\[
z=\sum_v y_v,\qquad A=\sum_q\lambda_q,\qquad B=\sum_{(s,t)\in D}d_{st}.
\]

Somando as equações das origens, com \(k_q=|I_q|\ge1\):

\[
\sum_q k_q\lambda_q+B=m\quad\Longrightarrow\quad A+B\le m.
\tag{L2}
\]

Somando as ligações de estações, usando \(|W_q|\ge1\):

\[
A\le\sum_q |W_q|\lambda_q\le\sum_v y_v=z.
\tag{L3}
\]

A identidade primal-dual de C.2, com a escolha de \(\eta\) em L0, tem apenas termos não negativos além dos custos reduzidos de \(\lambda\) e \(d\). Logo:

\[
z\ge L+\sum_q\bar c_q\lambda_q+\sum_D(-\pi_s-\tau_t)d_{st}
\ge L+aA+\delta B.
\tag{L4}
\]

As duas últimas desigualdades usam \(\bar c_q\ge\ell\ge a\), \(-\pi_s-\tau_t\ge\delta\), e variáveis não negativas.

Primeiro, como \(a,\delta\le0\):

\[
aA+\delta B\ge\min(a,\delta)(A+B)\ge m\min(a,\delta).
\]

Segundo, por \(A\le z\), \(B\le m\), novamente com os coeficientes não positivos:

\[
aA+\delta B\ge az+m\delta,
\qquad z(1-a)\ge L+m\delta.
\]

Como \(1-a\ge1\), a divisão preserva o sentido. Finalmente \(z\ge0\). Os três limites valem para **todo ponto primal viável**, portanto também para \(z_Q\). Isso prova L1. Não há qualquer uso de dualidade forte nesta demonstração.

Se \(K\) é válido, toda instalação física viável estende-se a um ponto do master, conforme C.3. Portanto \(z_Q\le\mathrm{OPT}\), completando a certificação para MIN-STATION.

**Conclusão:** não encontrei erro na prova central. A validade é demonstrada pelas desigualdades acima, e não inferida dos testes V5.

#### Contraexemplo à observação §6.1(iv)

A frase “\(\ell\in[-\varepsilon,0)\) implica \(LB_{CG}\ge L-m\varepsilon\)” é falsa sem controlar \(\delta\).

Tome o grafo com dois vértices \(a,b\) ligados, \(r=1\), \(S=T=\{a\}\), \(K=\varnothing\). Existe o par de permanência \(d_{aa}\), e \(z_Q=\mathrm{OPT}=0\).

Com \(\varepsilon=10^{-6}\), escolha:

\[
\pi_a=1,\quad\tau_a=0,\quad
\mu_a=1-\varepsilon/2,\quad\mu_b=1.
\]

Todos os \(W\) não vazios são elegíveis; \(I=J=\{a\}\). Temos:

\[
L=1,\quad c^*=\ell=-\varepsilon/2,\quad\delta=-1.
\]

Pela fórmula correta, ambos os ramos são zero e \(LB_{CG}=0\). Entretanto:

\[
L-m\varepsilon=0{,}999999>0.
\]

**Correção:** se \(\ell\ge-\varepsilon\) **e** \(\delta\ge-\varepsilon\), então \(LB_{CG}\ge\max\{0,L-m\varepsilon\}\). Mais geralmente, se \(\delta\ge-\gamma\), vale \(LB_{CG}\ge\max\{0,L-m\max(\varepsilon,\gamma)\}\). O caso usual de dual exato do RMP tem \(\delta=0\), mas isso não pode ser presumido para todos os vetores permitidos pelo teorema.

#### Contraexemplo ao uso de uma busca parcial como limite global de pricing

No caminho \(a-b-c\), \(S=\{a\}\), \(T=\{c\}\), \(r=1\), temos \(D=\varnothing\), \(K=\{\{b\}\}\) e \(z_Q=\mathrm{OPT}=1\). O RMP contendo apenas \((V,S,T)\) tem valor 3.

Escolha \(\pi_a=3\), \(\tau_c=0\), \(\mu_v=1\), \(\kappa=0\). Este é um dual ótimo do RMP, com \(L=3\). Os conjuntos válidos de estações são \(\{b\},\{a,b\},\{b,c\},V\), com custos reduzidos \(-2,-1,-1,0\).

Uma busca limitada a \(V\) devolve 0, mas esse é um **limite superior** para o mínimo global de pricing. Usá-lo como \(\ell=0\) produz o falso certificado 3. O valor correto \(\ell=-2\) produz \(LB_{CG}=1\).

O exemplo também demonstra concretamente por que o objetivo do RMP não é um limite inferior. A frase genérica do anexo “RMP com apenas \(V\) tem valor \(n\)” deve ser entendida como exemplo sob ausência de matching direto perfeito: se \(D\) já contém tal matching, o valor pode ser zero.

### B.2. D-2 — Certificação numérica por ObjBound

**Veredito:** rejeitar a regra “ObjBound finito ⇒ CERTIFIED” como garantia matemática autossuficiente. Manter esse ramo **UNCERTIFIED** até existir uma verificação que demonstre \(\ell\le c^*\).

#### Sentido da otimização e natureza do limite

Para o pricing escrito como minimização, um bound global válido \(b\) satisfaz \(b\le c^*\). O valor de uma coluna encontrada satisfaz a desigualdade oposta: \(c^*\le\bar c(q)\). Se o pricing for implementado como maximização de \(-\bar c\), um **limite superior global** \(U\) para esse máximo fornece \(\ell=-U\).

A documentação oficial do Gurobi distingue ObjBound, que pode aproveitar integralidade do objetivo para arredondar o bound, de ObjBoundC, que não aplica esse fortalecimento [G1]. Aqui os coeficientes são multiplicadores duais reais; variáveis binárias não tornam automaticamente o objetivo inteiro. Recomendo ObjBoundC para registrar o candidato numérico sem pressupor uma estrutura de integralidade que não foi demonstrada. Essa preferência **não** transforma ObjBoundC em prova exata.

As tolerâncias de factibilidade, integralidade e otimalidade do solver tratam diferentes resíduos e não fornecem, por si, uma desigualdade global da forma \(|b-c^*|\le\varepsilon_\ell\). A documentação descreve expressamente aceitação de pequenas violações e efeitos de escala [G2]. Status OPTIMAL significa otimalidade sujeita às tolerâncias do solver [G3]. Não equivale a um certificado racional universal.

#### Por que uma margem fixa não resolve

Não há nos anexos um erro absoluto demonstrado \(E\) tal que o bound numérico \(b\) sempre obedeça \(b-E\le c^*\). Escolher \(E=10^{-6}\), \(10^{-8}\), ou função arbitrária das tolerâncias não preenche essa lacuna. A propagação depende de coeficientes, magnitudes, resíduos, bounds das variáveis e, em um MIP, da validade das exclusões efetuadas na árvore.

Recalcular exatamente o objetivo de um incumbente verifica seu custo e, junto com a validade combinatória da coluna, produz um **limite superior** de pricing. Isso não verifica os nós descartados nem o limite global inferior. Da mesma forma, MIPGap=0 não converte as operações internas em aritmética exata.

Um bound rigoroso poderia vir de enumeração completa, de um certificado exato de uma relaxação global, ou de prova verificável que cubra todos os nós/regiões relevantes do MIP. Sem isso, a classificação correta do candidato baseado apenas em ObjBound é UNCERTIFIED, mesmo quando o solver é interrompido com um valor finito.

#### Alternativa rigorosa dentro do mesmo caminho B

Não é necessário resolver exatamente o MIP para obter **algum** \(\ell\) válido. A afirmação de §7 de que, acima do cap, “só (M) certifica” é excessiva.

Uma opção simples, que pode ser fraca, é:

\[
\ell_{\rm analitico}=\min_{v\in V}\mu_v-
\max_{1\le k\le m}\left(\operatorname{Top}_k(\pi;S)+\operatorname{Top}_k(\tau;T)\right).
\tag{N1}
\]

Aqui Top é a soma dos \(k\) maiores valores, inclusive negativos. Para qualquer configuração, \(W\ne\varnothing\), \(\mu\ge0\), logo \(\mu(W)\ge\min_v\mu_v\). Se \(|I|=|J|=k\), sua soma de prêmios não excede a soma dos \(k\) maiores em cada conjunto completo. Portanto \(\ell_{\rm analitico}\le c^*\). Avaliado exatamente, ele pode alimentar L1 em qualquer tamanho. Isso demonstra validade, **não** utilidade para o gate N2.

Outra opção é certificar uma relaxação LP do próprio pricing. Escreva-a, sem eliminar os dados necessários à verificação, como:

\[
\min c^T w:\quad Aw=b,\ Bw\ge h,\quad0\le w\le u.
\]

Os bounds de todas as variáveis do pricing são finitos: 1 para as binárias relaxadas, \(n\) para \(g\) e \(n-1\) para \(f\). Para quaisquer multiplicadores racionais \(\theta\) livres e \(\nu\ge0\), calcule exatamente:

\[
\boxed{\ell_{\rm caixa}=\theta^Tb+\nu^Th+
\sum_j u_j\min\{0,c_j-(A^T\theta)_j-(B^T\nu)_j\}.}
\tag{N2}
\]

Para qualquer \(w\) viável, expandir \(c^Tw\) e minimizar o termo residual sobre a caixa dá \(c^Tw\ge\ell_{\rm caixa}\). Consequentemente:

\[
\ell_{\rm caixa}\le z_{\rm LP(pricing)}\le c^*.
\]

Os multiplicadores podem ser propostos por um solver em ponto flutuante e então tratados como racionais exatos. Não é necessário que sejam duais ótimos ou sequer satisfaçam as restrições duais usuais: o termo residual da caixa paga a violação. A matriz, o objetivo e os bounds usados nessa verificação devem ser os do modelo racional original.

N1 e N2 são propostas matemáticas explicitamente acrescentadas por este parecer, não funcionalidades existentes no anexo. Permanecem dentro de F-CC+K e do Teorema L; não abrem outro caminho da N2. A menor correção operacional continua sendo autorizar ENUM rigoroso e deixar o ramo MIP numérico sem certificação. Um desses limites globais pode ser adotado se for desejada certificação além da enumeração.

#### Interrupção

Se o oráculo for interrompido, só usar um novo \(\ell\) cuja validade global já tenha sido verificada. Caso contrário, conservar o último limite certificado, com sua origem; sem tal limite, registrar UNCERTIFIED. Um MIP pode fornecer colunas válidas úteis mesmo quando seu bound não foi certificado. A coluna encontrada deve ser conferida combinatoriamente antes de entrar no master.

### B.3. D-3 — Aritmética exata no ramo ENUM

**Veredito:** aprovar ENUM como ramo de certificação apenas com avaliação exata ou enclosure numérico demonstrado. Aritmética racional é uma solução implementável e especialmente simples neste caso.

Não é necessário calcular o dual ótimo do RMP em aritmética exata. O Teorema L aceita multiplicadores arbitrários. O solver pode propor floats; cada float finito passa a definir um racional exato, independentemente de sua distância a algum dual ideal.

#### Procedimento recomendado

1. Rejeitar NaN e infinitos. Registrar o vetor recebido sem perda de informação, por exemplo por representação hexadecimal ou pares numerador/denominador.
2. Converter cada float finito no racional binário que ele representa, e impor exatamente \(\mu_v\leftarrow\max(0,\mu_v)\), \(\kappa_Z\leftarrow\max(0,\kappa_Z)\).
3. Fixar esse vetor para a certificação da iteração. Não misturar \(L\) anterior à projeção com custos reduzidos posteriores, nem usar um bound do pricing de outra iteração.
4. Recalcular exatamente \(\kappa(v),\eta,L,\delta\), todos os prêmios e todos os custos reduzidos considerados no certificado.
5. Enumerar completamente os conjuntos conectados de \(H\); em cada um usar a expressão TopK exata de B.4. Sem exclusões não demonstradas e sem aceitar cap atingido como conclusão de cobertura.
6. Calcular \(\ell=\min_Q\bar c\) e L1 em aritmética racional. O denominador \(1-a\) é sempre positivo.
7. Preservar o racional final no certificado. Se for exportado em decimal ou float para uso como LB, arredondar **para baixo**, e não apenas aplicar conversão usual.

Floats binários são racionais diádicos: antes da divisão final, pode-se usar um denominador comum potência de dois e trabalhar com inteiros nas somas, comparações, mínimos e máximos. Isso não requer um solver racional do master. Não se afirma aqui que o custo de enumerar todos os conjuntos seja pequeno.

O parâmetro \(10^{-6}\) usado no arredondamento inteiro congelado também pode ser representado exatamente como \(1/10^6\). Para \(LB\le\mathrm{OPT}\in\mathbb Z\), tanto \(\lceil LB\rceil\) quanto o conservador \(\lceil LB-1/10^6\rceil\) são válidos. Deve-se manter a convenção congelada. A subtração de \(10^{-6}\) não torna válido um LB anteriormente não certificado.

#### Onde ponto flutuante é aceitável

| Operação | Uso seguro de ponto flutuante |
|---|---|
| Resolver RMP ou propor multiplicadores | Sim; a etapa de certificação verifica o vetor escolhido |
| Heurística de pricing e ordem de exploração | Sim; validar a coluna encontrada e não inferir cobertura global |
| Elegibilidade, conectividade e construção de \(H\) no problema unitário | Preferir distâncias inteiras e operações combinatórias exatas |
| Ordenação TopK e decisão de omitir termos/conjuntos no certificado | Somente se a decisão for exata ou comprovada por intervalos |
| \(L,\delta,\ell,LB\) que sustentam CERTIFIED | Exatos ou com arredondamento dirigido/intervalos justificados |
| Tempo, Work, gráficos e diagnóstico | Floats são adequados; não constituem a prova do LB |

Com intervalos, calcular um enclosure de toda a expressão, respeitando dependências e o denominador positivo, e publicar a extremidade inferior. Uma soma de floats seguida de uma chamada isolada a arredondamento para baixo não limita o erro acumulado anterior. Se os intervalos de prêmios se sobrepuserem, uma ordenação arbitrária não pode fundamentar a poda de alternativas sem um limite correto para o máximo.

#### Cap e enumeração parcial

No código anexado, enumerar_conexos retorna um indicador de truncamento. Para certificação, o certificado deve registrar conclusão da enumeração, não apenas o número de conjuntos visitados. Em enumeração parcial, o mínimo visitado é um limite superior do mínimo de todos os conjuntos.

Seria possível combinar mínimos já calculados com um limite inferior comprovado para a região não explorada, mas esse procedimento não está definido no anexo. Não presumir que exista.

### B.4. D-4 — Exatidão do pricing

**Veredito:** a formulação proposta é exata por projeção sobre \((x,a,b)\). Não exclui configurações válidas nem admite configurações inválidas dentro do domínio declarado. A expressão “bijeção entre soluções inteiras e Q” é falsa e desnecessária.

Para evitar confundir a variável binária \(a_s\) com \(a=\min(0,\ell)\) do teorema, a notação nesta subseção é local.

Seja \(A_H\) o conjunto que contém os dois sentidos de cada aresta de \(H\), \(n=|V|\). Variáveis:

\[
x_v,\rho_v\in\{0,1\},\quad a_s,b_t\in\{0,1\},\quad
g_v\ge0,\quad f_{uv}\ge0\ ((u,v)\in A_H).
\]

O pricing completo é:

\[
c^*=\min\ \sum_v\mu_vx_v-\sum_s\pi_sa_s-\sum_t\tau_tb_t,
\tag{P0}
\]

\[
a_s\le\sum_{v\in N_H[s]}x_v\quad(s\in S),\qquad
b_t\le\sum_{v\in N_H[t]}x_v\quad(t\in T),
\tag{P1}
\]

\[
\sum_sa_s=\sum_tb_t,\qquad \sum_sa_s\ge1,
\tag{P2}
\]

\[
\sum_v\rho_v=1,\qquad \rho_v\le x_v,\qquad 0\le g_v\le n\rho_v,
\tag{P3}
\]

\[
g_v+\sum_{u:(u,v)\in A_H}f_{uv}
-\sum_{w:(v,w)\in A_H}f_{vw}=x_v\quad(v\in V),
\tag{P4}
\]

\[
0\le f_{uv}\le(n-1)x_u,\qquad f_{uv}\le(n-1)x_v
\quad((u,v)\in A_H).
\tag{P5}
\]

O fluxo é um certificado auxiliar de conectividade, não fluxo de robôs e não precisa ser inteiro. Todas as condições de seleção e de terminais estão nas binárias.

#### MIP ⇒ configuração

Defina \(W=\{v:x_v=1\}\), \(I=\{s:a_s=1\}\), \(J=\{t:b_t=1\}\). P3 seleciona uma única raiz em \(W\), portanto \(W\ne\varnothing\). P1 implica elegibilidade fechada e P2 implica \(|I|=|J|\ge1\).

Se \(H[W]\) fosse desconexo, existiria uma componente \(U\subseteq W\) sem a raiz. Somando P4 sobre \(U\), os fluxos internos cancelam. Nenhum fluxo cruza entre componentes de \(H[W]\), porque não há aresta entre elas. Fluxos entre \(W\) e vértices não selecionados são zero por P5. Além disso, \(g_v=0\) em \(U\) por P3. Obteríamos:

\[
0=\sum_{v\in U}x_v=|U|>0,
\]

contradição. Logo \(H[W]\) é conexo e \((W,I,J)\in Q\).

#### Configuração ⇒ MIP

Fixe \((W,I,J)\in Q\), \(k=|W|\). Tome as incidências de \(W,I,J\), escolha qualquer raiz \(v_0\in W\), e uma árvore geradora de \(H[W]\) orientada a partir dela. Defina \(g_{v_0}=k\), demais \(g=0\). Em cada arco da árvore dirigido de pai para filho, envie o número de vértices da subárvore do filho; nos demais arcos, envie zero.

A raiz consome uma unidade, cada outro vértice consome uma unidade, e todos os não selecionados têm balanço zero. Portanto P4 vale. Cada arco transporta no máximo \(k-1\le n-1\), e \(g_{v_0}=k\le n\), satisfazendo P3/P5. Elegibilidade e balanço vêm da definição de Q. O objetivo P0 é exatamente \(\bar c(W,I,J)\).

Isso também cobre \(|W|=1\), inclusive \(n=1\): não é necessário fluxo em aresta e \(g=1\).

#### Correção da alegação de bijeção

Mesmo no grafo de dois vértices ligados, uma configuração com \(W=V\) pode usar qualquer um deles como raiz, com fluxo 1 na direção correspondente. Há duas extensões para a mesma tripla. Em grafos com ciclos, há outras escolhas de árvore e de fluxo.

O enunciado correto é:

\[
\operatorname{proj}_{x,a,b}(\text{soluções viáveis inteiras de P1--P5})
=\{(1_W,1_I,1_J):(W,I,J)\in Q\}.
\]

Não há necessidade de unicidade. A quebra de simetria opcional \(\rho_v+x_u\le1\) para \(u<v\) é válida porque toda configuração possui uma menor estação selecionada que pode ser escolhida como raiz. Ela não cria uma bijeção de fluxos.

#### Matching, terminais e casos compartilhados

A única ligação entre \(I\) e \(J\) é o tamanho igual. A conectividade das estações faz todo \(I\times J\) alcançável; qualquer bijeção entre esses conjuntos é realizável. Não se deve acrescentar um pareamento predeterminado nem exigir que \(I=J\), que terminais pertençam a \(W\), ou que todas as estações da instalação global formem uma só componente.

Se \(s\in S\cap T\), existem as duas variáveis independentes \(a_s,b_s\). O par \(d_{ss}\) permanece no master. Um terminal fora de \(W\) é extremo elegível, não um ponto de recarga gratuito. Trajetos físicos podem passar por terminais dentro de um salto de comprimento até \(r\); isso não equivale a recarregar neles.

#### Forma TopK

Para \(W\) fixo, seja \(k_W=\min(|S_W|,|T_W|)\). Se \(k_W=0\), não existe coluna. Caso contrário:

\[
\min_{I,J}\bar c(W,I,J)=\mu(W)-
\max_{1\le k\le k_W}\left(\operatorname{Top}_k(\pi;S_W)+\operatorname{Top}_k(\tau;T_W)\right).
\tag{P6}
\]

Ordenando ambas as listas em ordem decrescente, os incrementos \(\pi_{(i)}+\tau_{(i)}\) também são não crescentes. Por isso a expressão do anexo, que inclui obrigatoriamente o primeiro incremento e soma os incrementos positivos posteriores, é correta. Não se pode eliminar prêmios negativos indiscriminadamente: pelo menos um terminal de cada lado é obrigatório.

A prova de NP-dificuldade apresentada no anexo é válida para os vetores arbitrários ali declarados. Ela usa \(S=T=V\) e \(\pi=\tau=M>0\), que **violam D-d** nos pares de permanência. Portanto não demonstra NP-dificuldade para a subfamília de duais factíveis do RMP. O próprio anexo limita sua afirmação; essa ressalva deve permanecer.

## C. Formulação matemática consolidada e correções

### C.1. Master primal completo e restrito

Defina \(H=G^r\), vizinhanças fechadas \(B(W)\), e:

\[
D=\{(s,t)\in S\times T:d_G(s,t)\le r\},
\]

\[
Q=\{(W,I,J):\varnothing\ne W\subseteq V,\ H[W]\text{ conexo},\quad
I\subseteq S\cap B(W),\ J\subseteq T\cap B(W),\ 1\le|I|=|J|\}.
\]

Cada \(Z\in K\) é um subconjunto não vazio de \(V\) correspondente a um dos cortes unitários congelados C1/C2/C4-DM. O modelo é:

\[
z_Q=\min\sum_v y_v,
\]

\[
\sum_{q:s\in I_q}\lambda_q+\sum_{t:(s,t)\in D}d_{st}=1
\quad(s\in S),
\tag{R1}
\]

\[
\sum_{q:t\in J_q}\lambda_q+\sum_{s:(s,t)\in D}d_{st}=1
\quad(t\in T),
\tag{R2}
\]

\[
y_v-\sum_{q:v\in W_q}\lambda_q\ge0\quad(v\in V),
\tag{R3}
\]

\[
\sum_{v\in Z}y_v\ge1\quad(Z\in K),\qquad
0\le y_v\le1,\quad\lambda_q\ge0,\quad d_{st}\ge0.
\tag{R4}
\]

Não existe termo \(|W_q|\lambda_q\) no objetivo. O custo de infraestrutura é pago por \(y\). Os limites \(\lambda_q\le1\) e \(d_{st}\le1\) são consequências das equações de atendimento, **tanto no master completo quanto no restrito**. Omiti-los explicitamente é uma escolha correta para simplificar a extração dual. Acrescentá-los não alteraria o ótimo primal, mas exigiria tratar seus multiplicadores e os possíveis custos reduzidos negativos de variáveis no limite superior.

O RMP substitui \(Q\) por \(Q_R\subseteq Q\), mantendo todos os pares diretos, vértices, cortes e bounds. O ponto \(\lambda_{(V,S,T)}=1\), \(y=1\), \(d=0\) é viável no domínio conexo declarado. O conjunto Q é finito; os limites implícitos tornam o primal limitado. Master e RMP inicial são viáveis, têm ótimo finito e satisfazem dualidade forte de programação linear.

Por inclusão de conjuntos viáveis:

\[
z_Q\le z_R.
\]

Essa desigualdade não compara \(z_R\) a OPT em uma direção útil para certificar LB. K pode continuar integralmente estático enquanto novas colunas entram: cada coluna de configuração tem coeficiente zero nas linhas K.

### C.2. Dual, custos reduzidos e identidade

Multiplicadores livres \(\pi_s,\tau_t\); não negativos \(\mu_v,\kappa_Z,\eta_v\), sendo \(\eta\) associado a \(-y_v\ge-1\). O dual completo é:

\[
\max\Phi=\sum_s\pi_s+\sum_t\tau_t+\sum_Z\kappa_Z-\sum_v\eta_v,
\tag{D0}
\]

\[
\pi(I_q)+\tau(J_q)-\mu(W_q)\le0\quad(q\in Q),
\tag{D1}
\]

\[
\pi_s+\tau_t\le0\quad((s,t)\in D),
\tag{D2}
\]

\[
\mu_v+\kappa(v)-\eta_v\le1\quad(v\in V).
\tag{D3}
\]

O dual do RMP impõe D1 somente em \(Q_R\). D2 e D3 continuam completos.

Usando as igualdades na forma “1 menos atendimento” e as desigualdades na forma “lado direito menos lado esquerdo”, o Lagrangiano é:

\[
\mathcal L=
\Phi+
\sum_q[\mu(W_q)-\pi(I_q)-\tau(J_q)]\lambda_q
+\sum_D[-\pi_s-\tau_t]d_{st}
+\sum_v[1-\mu_v-\kappa(v)+\eta_v]y_v.
\]

Ao representar UB por linha e minimizar sobre variáveis não negativas, a finitude do ínfimo exige cada coeficiente não negativo. Isso produz D1–D3 e justifica os sinais. Os custos reduzidos são:

\[
\bar c_q=\mu(W_q)-\pi(I_q)-\tau(J_q),\quad
\bar c_{st}=-\pi_s-\tau_t,\quad
\bar c_v=1-\mu_v-\kappa(v)+\eta_v.
\tag{RC}
\]

No pricing, uma coluna com \(\bar c_q<0\) viola uma restrição dual ausente e é candidata a entrada. Em situação degenerada, inserir uma coluna negativa não garante queda estrita do objetivo já na próxima reotimização. O teste de sinal está correto; a promessa de ganho imediato seria indevida.

Para \(\sigma_v=y_v-\sum_{q:v\in W_q}\lambda_q\) e \(\sigma_Z=y(Z)-1\), vale:

\[
\sum_vy_v-\Phi=
\sum_q\bar c_q\lambda_q+\sum_D\bar c_{st}d_{st}
+\sum_v\bar c_vy_v
+\sum_v\mu_v\sigma_v+\sum_Z\kappa_Z\sigma_Z
+\sum_v\eta_v(1-y_v).
\tag{ID}
\]

A expansão cancela os coeficientes auxiliares por R1/R2 e é válida mesmo sem factibilidade dual. Na prova de L1, \(\eta_v=\max(0,\mu_v+\kappa(v)-1)\) garante \(\bar c_v\ge0\).

Como o código escreve R3 como \(\sum\lambda-y\le0\), a conversão é \(\mu=-\mathrm{Pi}(R3)\). Com UB nativo, \(\eta\) não aparece em Pi. Recalculá-lo pela fórmula é a opção apropriada para um certificado, especialmente após projetar \(\mu,\kappa\). Usar simultaneamente UB nativo e uma segunda cópia da penalização não é a derivação acima.

**Teste matemático da necessidade de \(\eta\):** no caminho \(a-b-c\), com um robô de \(a\) para \(c\), escolha \(\pi_a=2,\tau_c=0,\mu_b=2,\mu_a=\mu_c=0,\kappa=0\). Todas as configurações válidas contêm \(b\), portanto \(c^*=0\). O termo \(\eta_b=1\) dá \(L=1=z_Q\). Omiti-lo daria 2, um falso LB acima de OPT=1.

### C.3. Equivalência com a implementação e com MIN-STATION

**Divergência real, já corretamente reconhecida no anexo:** fcc_k.py monta a forma separada sem CA5; o novo master utiliza colunas \((W,I,J)\). Os modelos auxiliares não são idênticos. A igualdade de valor tem prova e não depende de V1.

Para cada \(W\), o código separado impõe:

\[
0\le\alpha_{sW},\beta_{tW}\le\Lambda_W,\qquad
\sum_s\alpha_{sW}=\sum_t\beta_{tW},
\]

além de atendimento e \(\sum_{W:v\in W}\Lambda_W\le y_v\).

Se \(\Lambda_W>0\), normalize \((\alpha,\beta)/\Lambda_W\). O politopo:

\[
P_W=\{(a,b)\in[0,1]^{|S_W|+|T_W|}:\sum a=\sum b\}
\]

é integral. Com duas coordenadas fracionárias, uma pequena perturbação não nula que mantém a única igualdade produz um segmento viável em torno do ponto, impedindo-o de ser vértice. Com exatamente uma coordenada fracionária, a igualdade e as demais coordenadas inteiras a obrigariam a ser inteira. Logo todos os vértices são incidências de pares de conjuntos de mesmo tamanho, incluindo o par vazio.

Decomponha o ponto normalizado nesses vértices e multiplique os pesos por \(\Lambda_W\). Descarte a massa do par vazio. O descarte preserva \(\alpha,\beta,d,y\), e só diminui a soma de pesos que usa as estações de W. Obtém-se um ponto qij. No sentido inverso, agregar colunas por W produz um ponto separado. Portanto as projeções em \((y,d)\), e em particular em y, coincidem. Acrescentar o mesmo K e os mesmos bounds em y preserva essa igualdade.

A prova de P7 anexada, via \(\Lambda'_W=\min(\Lambda_W,\sum_s\alpha_{sW})\), é outra demonstração válida. A justificativa informal por menores 2×2 em §2.1 não deve ser apresentada como critério geral de unimodularidade total; o argumento de vértices acima evita esse problema de exposição.

**Atenção à geração parcial:** restringir uma lista de triplas qij não é a mesma operação que manter alguns W com todas as suas marginais livres. Um W na forma separada representa implicitamente todas as suas combinações elegíveis. A equivalência de modelos completos não autoriza confundir esses dois RMPs.

#### Instalações inteiras

Para uma instalação C, construa um grafo bipartido com cópias separadas dos papéis S e T. Um par é alcançável se é direto ou se ambos os extremos estão na vizinhança fechada de uma componente de H[C].

Se y é binário e o master é viável, R3 implica \(W_q\subseteq C\) em toda coluna positiva. Escolha uma bijeção entre \(I_q\) e \(J_q\) para cada coluna; ela é fisicamente realizável pela infraestrutura conectada. Atribua peso \(\lambda_q\) às arestas dessa bijeção e adicione os d diretos. R1 e R2 geram um matching perfeito fracionário composto de pares alcançáveis. Pela integralidade do politopo de matching bipartido, há um matching perfeito inteiro no mesmo suporte, realizável com C.

Inversamente, em uma solução física, cada rota que recarrega usa estações de uma única componente de H[C]. Agrupar suas origens e destinos por componente dá configurações balanceadas de peso 1; rotas diretas usam d. Componentes sem robôs atendidos podem ficar sem coluna. Componentes são disjuntas e R3 vale.

Isso demonstra P1 independentemente dos testes. Permitir \(S\cap T\) não invalida a integralidade: são duas cópias de um mesmo vértice físico nos papéis bipartidos. O par \(d_{ss}=1\) representa permanência. Não se deve fixá-lo obrigatoriamente: partidas e chegadas diferentes também são permitidas.

A descrição original de Das, Problema 1 e texto subsequente, permite estações em qualquer vértice, robôs não rotulados e compartilhamento de estações. Não há capacidade nem colisão que invalidem o argumento de matching.

### C.4. Validade de K e limites do que foi verificado

Os cortes K são necessários apenas como desigualdades válidas para instalações inteiras. Não é necessário provar que já sejam implicados pelo LP da F-CC. Assim, o estado aberto de P3/P4 sobre implicação no LP não bloqueia esta derivação.

Para cortes unitários, a viabilidade de instalações é monótona: adicionar estações não remove rotas. Logo:

\[
y(Z)\ge1\text{ é válido para todas as instalações inteiras}
\iff V\setminus Z\text{ é inviável}.
\tag{K0}
\]

Isso justifica o método de validação usado em cuts.py: calcular pares alcançáveis por estações fora de Z e decidir matching perfeito. Origens e destinos permanecem extremos gratuitos de seus próprios percursos; um terminal só é intermediário de recarga se tiver estação. A exceção do código que impede relés terminais quando m=1 não altera a resposta nesse caso, pois só existem os extremos da única viagem e uma rota pode ser simplificada para não revisitá-los.

Os argumentos de validade das famílias efetivamente escolhidas são:

- **C1:** se uma origem exclusiva não alcança nenhum destino diretamente, alguma primeira recarga positiva ocorre em sua vizinhança de alcance. O argumento inverso vale para destinos exclusivos.
- **C2:** em uma rota, considere o primeiro ponto de recarga/chegada cuja distância desde s supera a fronteira a. O ponto anterior tem distância no máximo a e o salto tem comprimento no máximo r, então esse ponto fica na banda \((a,a+r]\). Como todos os destinos têm distância maior que a+r na banda gerada, esse ponto é uma estação. O lado do destino é simétrico. A prova usa o modelo unitário e distâncias coerentes com os saltos.
- **C4-DM:** uma região alternante gerada a partir de uma origem não emparelhada em um matching máximo define um conjunto deficiente S' de origens exclusivas. Há menos destinos diretamente alcançáveis do que origens em S'; algum robô desse conjunto precisa de recarga. Sua primeira estação pertence à união N⁺(S'), que é o suporte do corte. O código usa T inteiro para medir a deficiência, incluindo S∩T; isso está correto. O lado dos destinos é análogo.

Conferi as funções pertinentes de cuts.py e, como complemento, prepare_cuts/add_cuts_to_model de harness.py no checkout do commit c995b54. Os anexos fcc.py, fcc_k.py, cuts.py, provas-fcc-fc3.md e a spec são byte a byte iguais às versões desse commit. O harness adiciona os cortes unitários após assert_valid_cuts; fcc_k verifica número de cortes e hash quando fornecido.

O parecer não reexecuta os 23 controles nem atesta os hashes de cada execução histórica: os CSVs, logs completos e manifesto de certificados do verificador não foram anexados. A prova da validade das famílias não depende dessas medições. A futura certificação de uma instância deverá preservar o conteúdo exato de K e registrar a validação pertinente.

### C.5. Regra de certificação e de convergência corrigidas

**Certificação de um limite:** aplicar L1 apenas com um \(\ell\) comprovado e aritmética segura. Não exigir RMP ótimo. Manter o máximo dos limites certificados de iterações anteriores. O máximo de limites inferiores válidos continua válido.

**Convergência do valor do LP:** é uma afirmação adicional. Seja U o custo de uma solução primal do RMP cuja viabilidade foi verificada. Como esse ponto também é viável no master completo:

\[
LB_{CG}\le z_Q\le z_R\le U.
\tag{G1}
\]

Um critério suficiente e verificável de convergência absoluta é:

\[
\boxed{U-LB_{CG}\le\varepsilon_{\rm abs}.}
\tag{G2}
\]

Se não há U validado, pode existir LB certificado sem certificado de convergência. Um ObjVal numericamente quase viável não deve ser chamado de upper bound exato sem verificar os resíduos ou reconstruir uma solução viável.

Por que \(\ell\ge-10^{-6}\) isoladamente não basta:

1. O teorema permite multiplicadores arbitrários. No caminho de três vértices já usado, o vetor todo zero tem \(\ell=0,\delta=0,L=0\). O RMP com só V ainda vale 3, contra LP completo 1. Não é um dual ótimo do RMP, mas é um vetor permitido para certificação. Portanto o teste de pricing, sozinho, não decide convergência nesse regime.
2. Mesmo com dual exato ótimo do RMP, \(L=z_R\), \(\delta=0\), a desigualdade imediata é \(z_R-z_Q\le m\varepsilon\), e não a tolerância absoluta \(\varepsilon\) exigida pela regressão. O critério do anexo não demonstra a precisão que anuncia.

No caso ideal de RMP resolvido exatamente e \(\delta=0\), \(\ell\ge0\) implica \(L=z_R=z_Q\). Para tolerância positiva, G2 trata conjuntamente erro de pricing e precisão do master. Uma alternativa suficiente é reservar o erro entre gap do master e \(m\max(\varepsilon,\gamma)\), com \(\delta\ge-\gamma\); essa contabilidade precisa ser explícita.

**B0:** manter campo e justificativa separados. Um fallback proveniente de B0 é limite para MIN-STATION, mas não necessariamente para o LP completo F-CC+K. A decisão N1-T7 registra Tri com \(B0=\mathrm{OPT}=2\) e LP F-CC+K=1,5. Portanto não submeter um fallback B0 à comparação \(LB\le z_Q\) destinada ao limite derivado do master. O texto revisado já separa as origens em §6.2-7; a implementação deve manter essa separação, inclusive nas interrupções.

Se core IP for interrompido, seu incumbente é uma cota superior do **core**, não uma prova de limite inferior para MIN-STATION. Apenas o ótimo comprovado ou uma cota inferior validada desse core pode compor um bound. Um valor parcial não deve ser rebatizado como o B0 ótimo usado no cálculo do incremento experimental.

## D. Problemas identificados e alcance do verificador

### D.1. Correções por gravidade

| ID | Gravidade | Local do anexo | Problema | Correção necessária |
|---|---|---|---|---|
| R-01 | **Bloqueante para certificação MIP** | §5.3; §6.2-1/4; §6.3; D-2 | ObjBound finito/status ótimo são encaminhados a CERTIFIED sem demonstração de H-NUM | Exigir bound verificado; caso contrário UNCERTIFIED, sem escolher margem arbitrária |
| R-02 | **Importante** | §6.1, observação (iv) | \(LB\ge L-m\varepsilon\) omite controle de \(\delta\); contraexemplo com permanência | Acrescentar \(\delta\ge-\varepsilon\), ou usar correção geral L1 |
| R-03 | **Importante** | §6.2-5 | Parada por \(\ell\ge-10^{-6}\) não garante gap absoluto de objetivo e ignora qualidade do master | Usar gap certificado G2 ou contabilidade de erros demonstrada |
| R-04 | **Importante** | §6.1, definição de \(\delta\) | Mínimo interno não definido explicitamente quando D é vazio | Escrever L0; \(\delta=0\) no caso vazio |
| R-05 | **Importante antes de implementar ENUM certificado** | §6.3; D-3 | Aritmética racional é possibilidade/recomendação, mas não contrato executável de certificação | Exigir vetor racional único, cobertura completa, cálculo exato/intervalar e exportação conservadora |
| R-06 | **Secundário** | §5.2, prova do MIP | “Bijeção” é falsa porque raiz e fluxos não são únicos | Substituir por equivalência por projeção; usar as duas provas de B.4 |
| R-07 | **Importante para a arquitetura de certificação** | §7, último item; A8 | “Só M certifica acima do cap” não é consequência matemática | Admitir qualquer bound global demonstrado, como N1/N2, distinguindo validade de utilidade |
| R-08 | **Secundário** | §2.1, comentário sobre TU | Menores 2×2 citados não constituem um critério geral de TU | Usar a prova de vértices ou explicitar a redução de todos os menores pela estrutura identidade |
| R-09 | **Secundário** | §2.2 | Valor n do RMP com apenas V não vale se há matching direto perfeito | Dar o exemplo concreto com D vazio ou explicitar a condição |
| R-10 | **Importante para validação futura** | §9 e verificador | Comparações em floats e amostras aleatórias não verificam H-NUM nem uma equivalência universal | Preservar como regressão; acrescentar controles exatos e de cobertura antes da medição |

Não identifiquei erro de sinal no dual, omissão de termo no custo reduzido, nem erro nas restrições de conectividade. Não proponho modificar a baseline, K, a estrutura qij, o objetivo, as referências históricas ou o orçamento congelado.

### D.2. O que o verificador realmente verifica

Foi lido o arquivo anexado verify_n2_t2b_algebra.py, incluindo a montagem do master e do MIP auxiliar. A formulação de pricing ali escrita coincide com P0–P5. O script usa otimização e comparações em ponto flutuante, apesar de seu nome “algébrico”. Isso é apropriado para regressão, mas não torna os testes provas formais.

| Teste | Evidência que produz se passar | O que não demonstra |
|---|---|---|
| V1 | Igualdade numérica dos ótimos das duas montagens nas instâncias geradas | Igualdade de projeções para todas as instâncias |
| V2/V3 | Consistência de sinais, custo reduzido e reconstrução dual nos ótimos calculados | Limite exato em presença de resíduos ou após interrupção |
| V4 | TopK coincide com força bruta nos vetores e conjuntos visitados | Cobertura correta quando há truncamento, poda ou aritmética imprecisa adversarial |
| V5 | Os dois ramos numéricos do limite ficam abaixo do LP de referência nas amostras | H-NUM, bound MIP interrompido, erro acumulado rigoroso ou Teorema L universal |
| V6 | Igualdade do mínimo do MIP e da enumeração para os objetivos amostrados | Igualdade de todos os pontos projetados, ou segurança do bound numérico |
| V7 | A identidade da redução para conjunto dominante conexo coincide em 15 grafos | NP-dificuldade universal ou dureza nos duais factíveis do RMP |

As provas deste parecer substituem a necessidade de inferir essas propriedades dos testes, mas não dispensam regressão quando a implementação existir.

Lacunas concretas do script:

- Usa \(\ell\) como mínimo enumerado em floats; não testa a origem ObjBound de um MIP interrompido, embora esse seja o principal risco de certificação.
- Não testa deliberadamente um \(\ell<c^*\) rigoroso, a exportação do LB para baixo, ou reconstrução racional dos multiplicadores.
- Não testa a falsa observação (iv), a parada com dual arbitrário, nem uma corrida com enumeração truncada que deve ser recusada como certificado.
- Verifica ótimos do MIP, não a projeção de cada padrão fixado \((W,I,J)\). Isso não seria suficiente para provar exatidão sem a demonstração escrita.
- Os casos aleatórios têm n entre 4 e 8, m até 3, r em {1,2}; não cobrem os limites n=1, W unitário com capacidade n−1=0, nem todos os padrões de overlap.
- O relatório diz que só 20 dos 60 casos têm objetivo positivo; muitos exercitam sobretudo matching direto. São controles úteis, mas não diversidade universal de infraestrutura.
- O script conta eta_pos, porém o documento não registra esse valor nem exige caso determinístico com \(\eta>0\). O exemplo exato de C.2 é um controle positivo necessário para esse termo.
- Em V1, o modelo separado é otimizado e ObjVal é lido sem uma asserção explícita de status ótimo para esse segundo modelo; o helper qij, em contraste, faz a asserção. Uma falha não deve ser interpretada como uma comparação de ótimos.
- Contagens específicas e PASS não são acompanhados de log de execução anexado. São declarações do documento, não evidência que esta revisão tenha reproduzido.

**D-5, recomendação complementar:** manter o verificador como regressão auxiliar. Removê-lo não melhoraria o rigor. Documentar seus limites e acrescentar controles dirigidos é mais adequado. Não houve edição ou execução dele nesta rodada.

### D.3. Validação mínima posterior, sem campanha experimental

Antes de medições da N2, bastam controles matemáticos dirigidos aos riscos encontrados:

1. Casos racionais deste parecer: D vazio, permanência com \(\delta<0\), \(\eta>0\), RMP acima de OPT, pricing parcial inválido e parada com vetor zero.
2. Cobertura ENUM: comparar os W de grafos minúsculos a todos os subconjuntos conectados; cap atingido não pode gerar CERTIFIED por esse ramo.
3. Pricing: padrões com W unitário, W desconexo, conectividade via terminal instalado, terminal elegível fora de W e S∩T. Fixar as incidências para conferir extensões, além da comparação de objetivos.
4. Certificado: usar \(\ell=c^*\), um \(\ell<c^*\) validado e um falso \(\ell>c^*\) como controle negativo; testar publicação racional e arredondamento dirigido.
5. Só depois, a regressão prospectivamente exigida nos 23 controles N1. O verificador aleatório de 60 casos não substitui essa exigência.

São verificações propostas, não resultados produzidos. Nenhuma conclusão de desempenho, força do bound em nível 2 ou aprovação do gate N2 decorre delas.

## E. Decisão de implementação

**A implementação pode começar com a matemática atual? Não como autorização irrestrita da versão anexada.** O núcleo matemático está demonstrado e não requer uma reformulação. As regras de certificação e parada ainda precisam incorporar as condições deste parecer antes de implementar as partes afetadas.

A menor sequência de correções é:

1. Registrar este veredito e incorporar L0, a condição correta da observação (iv), a equivalência por projeção do pricing e o critério de convergência G2 no documento matemático não congelado.
2. Fechar D-2/D-3 com uma decisão inequívoca: **ENUM com aritmética exata é certificável; ObjBound/ObjBoundC sem verificação independente não é**. O MIP pode gerar colunas e diagnósticos, mas o rótulo CERTIFIED exige um \(\ell\) demonstrado. Opcionalmente adotar um dos bounds globais verificados N1/N2 para uso além da enumeração.
3. Registrar o aceite das correções e então implementar somente o escopo aprovado, com os controles mínimos de D.3 antes de qualquer medição N2. Preservar a exigência de registro de aprovação da spec; **ACCEPTED WITH CONDITIONS não deve ser convertido automaticamente em ACCEPTED**.

| Parte | Situação após este parecer |
|---|---|
| Master qij + K, dual e custo reduzido | **Demonstrado** |
| Igualdade do LP com fcc_k separado | **Demonstrado** por projeção |
| Teorema L | **Demonstrado**, com convenção para D vazio e observação corrigida |
| Exatidão do MIP de pricing | **Demonstrado** por projeção |
| ENUM como certificado | **Condicional** à cobertura integral e à aritmética segura especificada |
| MIP-OPT/MIP-BOUND sustentado apenas por ObjBound | **Não autorizado como CERTIFIED** |
| Certificado via bound global racional do pricing | **Demonstrado matematicamente**; implementação e validação ainda não realizadas |
| Aprovação operacional após incorporar correções | **Pendente** |
| Ganho, custo e escalabilidade da N2 | **Ainda não há evidência suficiente para concluir.** |

Nenhuma alteração no pré-registro, caminho científico ou formulação-base é necessária para satisfazer essas condições. Este parecer não constitui aprovação de desempenho, do gate N2 nem de branch-and-price.

## Fontes e rastreabilidade

**Fontes principais anexadas:** spec(1).md; n2-t2b-master-dual-pricing-revisao.md; formulacao-fcc-configuracoes-conectadas.md; fcc.py; fcc_k.py; cuts.py; verify_n2_t2b_algebra.py; provas-fcc-fc3.md, especialmente P1/P7/P10; n1-t7-decisao-cientifica.md; n2-t1-pre-registro.md; min-station-das(6).pdf, especialmente Problema 1 e a descrição de robôs não rotulados nas páginas 2–3.

**Complemento local de proveniência identificada:** CLAUDE.md e contexto indicado por ele; experiments/cuts/harness.py e a construção dos arcos de alcance em ms_utils.py no checkout c995b54, para conferir as chamadas transitivas. No domínio unitário, a construção por distâncias coincide com os saltos definidos aqui; a extensão a dados ponderados/dirigidos não é autorizada por esta prova. Não foram usados documentos alternativos de revisão como prova de correção do anexo.

**SHA-256 do documento auditado:** e7741dd27200aedea8a2e429f0f694797a4c1980f21bd3467708eceb5a4f314e.  
**SHA-256 do verificador auditado:** 69fbbd4e84cb14020b8e21e6d43af9977bb8e99ac29a0404329d31638ae3ad63.  
**SHA-256 da spec anexada:** 4b220b66639be24411cd691dbcee83e8b4c70d6c93cb37c74d03e289e40e3d90.

Referências oficiais de semântica numérica, consultadas em 09/10/2026; as conclusões de dualidade e as correções de erro foram derivadas neste parecer:

- **[G1]** Gurobi, [Model Attributes — ObjBound e ObjBoundC](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/model.html#objboundc).
- **[G2]** Gurobi, [Tolerances and User-Scaling](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/tolerances_scaling.html).
- **[G3]** Gurobi, [Optimization Status Codes](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html).

As páginas oficiais correntes explicam a semântica; não se afirma que o verificador anexado tenha sido reexecutado sob outra versão. O anexo declara Gurobi 12.0.3, e sua reprodução deverá preservar a versão registrada.


