# Parecer externo — FC-R após AS22 (Astra, 2026-10-16)

> **Proveniência:** transcrição integral do parecer fornecido pelo pesquisador em `Texto colado(20261016-040142).txt`. Consulta declarada pelo Astra: branch `novos_testes`, commit `285261b`. **Este texto é uma fonte externa de hipóteses e demonstrações a reproduzir; não representa validação independente da equipe nem resultados de execução realizados nesta incorporação.**
>
> **Uso no projeto:** decisões propostas e plano derivados em [`plano-fcr-as23-as27.md`](../../plans/execucao/plano-fcr-as23-as27.md); especificações AS23–AS27 em `specs/`. Qualquer divergência entre o parecer e a evidência versionada deve ser registrada, não reconciliada silenciosamente.

---

**Minha recomendação é encerrar a estratégia atual de HL local e investigar cortes de cobertura de fluxo por regiões, mantendo COMP+K como referência.**

Encontrei uma candidata com três propriedades relevantes: prova de validade simples, separação exata e barata para uma região escolhida e uma testemunha racional de fortalecimento **inclusive sobre COMP+K acrescido de C6 e C8**. Isso justifica uma investigação curta. **Ainda não há evidência suficiente para concluir que ela melhorará as instâncias reais.**

Analisei a branch `novos_testes` no commit [`285261b`](https://github.com/ElielLucas/min-station/commit/285261ba4ab83318acc1ea2435a973651354310f). Não alterei arquivos do projeto nem implementei um separador. Executei apenas verificações algébricas e físicas de uma construção pequena, sem otimizações LP/MIP ou campanha experimental.

---

**1. Diagnóstico de COMP+K.** A formulação inteira continua sendo uma representação adequada do problema; a questão aberta é a qualidade de sua relaxação.

Escrevendo \(a_v=\mathbf1[v\in S]\), \(b_v=\mathbf1[v\in T]\) e \(m=|S|=|T|\), o comparador implementado utiliza:

\[
\min \sum_{v\in V}y_v,
\]

\[
f^{out}(v)-f^{in}(v)=a_v-b_v,
\]

\[
f^{in}(v)\le b_v+(m-b_v)y_v,
\]

\[
f^{out}(v)\le a_v+(m-a_v)y_v,
\]

com \(f\ge0\), \(y\) binário no MIP e \(0\le y\le1\) no LP.

Isso corresponde a [`compile_u`](https://github.com/ElielLucas/min-station/blob/285261b/experiments/alternative-formulations/as02_model_a.py). Uma distinção documental importante: o baseline histórico declara fluxo inteiro; o comparador atual usa fluxo contínuo. Para \(y\) binário, a existência de fluxo é preservada pela representação em rede com capacidades inteiras.

O modelo incorpora corretamente:

- alcance definido por distâncias no grafo físico;
- estações em qualquer vértice;
- partida com bateria cheia e chegada sem estação obrigatória;
- pareamento anônimo;
- compartilhamento ilimitado;
- interseção \(S\cap T\), incluindo permanência e troca de destinos.

A caracterização física utilizada pelo validador — alcance com recargas seguido de matching entre cópias distintas de origens e destinos — é compatível com essas condições e com o trabalho posterior de Das e coautores. [IJCAI](https://www.ijcai.org/proceedings/2026/9?utm_source=chatgpt.com)

O coeficiente \(m\) é um limite seguro para representar fluxo de robôs. **Não é uma capacidade física da estação.** Sua principal consequência negativa aparece no LP: uma quantidade pequena de fluxo pode atravessar uma estação instalada fracionariamente.

Os cortes K efetivamente implementados são coberturas

\[
y(Z)\ge1,
\]

geradas por C1, C2 e C4-DM: primeiro/último salto, bandas de distância e determinadas obstruções de Hall no bipartido direto. O código não gera todas as desigualdades de Hall possíveis. Veja [`cuts.py`](https://github.com/ElielLucas/min-station/blob/285261b/experiments/cuts/cuts.py).

K melhora substancialmente a exigência de instalação, mas não descreve todas as relações entre:

1. instalação de estações;
2. distribuição do fluxo entre alternativas;
3. recirculação por terminais;
4. atendimento simultâneo das origens e dos destinos.

Isso não significa que o modelo inteiro tenha esquecido o matching. Significa que sua **relaxação permite combinações fracionárias dessas decisões**.

Também existem situações sem espaço relevante para novos cortes: se a relaxação já atinge o ótimo inteiro, nenhum corte válido melhora seu objetivo. Mesmo quando existe diferença LP–IP, ela pode ser resolvida rapidamente pelos cortes automáticos e pelo branch-and-bound, tornando um separador adicional contraproducente.

---

**2. O que AS16–AS22 realmente mostram.** Os resultados sustentam interromper as estratégias testadas, sem provar redundância universal de H2 ou HL.

Na AS16, H2 não melhorou COMP+K nos cinco pares com ótimos LP comparáveis. Houve fortalecimento de COMP isoladamente, mas isso não demonstrou complementaridade com K. A decisão científica `STOP` está bem fundamentada; o gate automático `INVESTIGATE` deve permanecer como registrado. [Relatório AS16](https://github.com/ElielLucas/min-station/blob/285261b/docs/technical/reference/experimentos/as16-resultado-lp-h2.md).

Na AS22, os arquivos de resultados confirmam:

| Instância | LP COMP+K | LP COMP+K+HL | Cortes HL | Tempo total: K / K+HL |
|---|---:|---:|---:|---:|
| PUC CC9 | 27,026786 | 27,026786 | 0 | 1,80 / 2,51 s |
| PUC BIP42 | 31,706052 | 31,706052 | 0 | 14,81 / 16,95 s |
| PUCN CC3 | 16,933333 | 16,933333 | 0 | 5,83 / 7,60 s |
| MAPF Room | 13,200000 | 13,200000 | 0 | 1,29 / 1,82 s |
| Vienna I056 | baseline ótimo; par censurado | — | 0 | 87,98 / 90,05 s |
| PUC W3C571 | par censurado | — | 0 | aproximadamente 90 / 90 s |

São resultados numéricos arquivados, não resultados que reproduzi nesta revisão. Os 160 testes aprovados constam na documentação de validação; não executei novamente essa suíte. [Análise AS22](https://github.com/ElielLucas/min-station/blob/285261b/results/benchmark/as22-hl-lp-001/analysis.json).

Há duas inconsistências de documentação/proveniência a registrar:

- O relatório e a spec AS22 ainda dizem que a campanha está pendente, embora os resultados estejam presentes.
- O manifesto informa como `source_commit` o commit anterior à inclusão da implementação AS22. Isso pode resultar de execução sobre alterações ainda não commitadas, mas o SHA, isoladamente, não identifica integralmente o código executado.

Não invalidam automaticamente os resultados, mas exigem cuidado para uma publicação reprodutível.

**A conclusão mais importante vem dos suportes.** Conferi nos registros:

- 16 suportes, todos com tamanho 8;
- 11 `K_PAIR_PROJECTION`;
- 5 `LARGE_K_PROJECTION`;
- nenhum suporte selecionado era um K completo ou uma união completa;
- uma chamada física por suporte certificou o padrão vazio como viável;
- os outros 255 padrões foram inferidos por monotonicidade.

Portanto, foram 16 chamadas físicas e 4.080 inferências, não 4.096 verificações físicas independentes. [Registros completos](https://github.com/ElielLucas/min-station/blob/285261b/results/benchmark/as22-hl-lp-001/rows.json).

A interpretação do cubo completo está correta. Defina

\[
\mathcal F=\{C\subseteq V:C\text{ é fisicamente viável}\},
\]

\[
\Phi_R=\{\mathbf1_{C\cap R}:C\in\mathcal F\}.
\]

Se \(F=V\setminus R\) é viável, então, para qualquer \(A\subseteq R\),

\[
F\cup A\in\mathcal F
\]

por monotonicidade. Logo,

\[
\Phi_R=\{0,1\}^{R},
\qquad
\operatorname{conv}(\Phi_R)=[0,1]^R.
\]

**Consequência demonstrada:** nenhuma desigualdade válida que dependa exclusivamente de \(y_R\) pode separar um ponto desse cubo. Isso vale também para coeficientes negativos; não é uma limitação da escolha \(\alpha\ge0\).

Essa conclusão depende de:

- as estações adicionais serem opcionais e não prejudicarem a viabilidade;
- não existir orçamento externo de estações na definição de viabilidade;
- o certificado de viabilidade de \(F\) estar correto.

Essas hipóteses correspondem ao MIN-STATION estudado.

Há ainda uma observação útil: se um suporte contivesse integralmente um K válido \(Z\), seu complemento não poderia ser viável, pois teria \(y(Z)=0\). Portanto, os resultados são coerentes com a seleção de **projeções truncadas que perderam a obstrução original**.

Minha decisão seria:

> Encerrar a estratégia “suporte pequeno, complemento integralmente disponível, enumeração de padrões”, no formato AS20–AS22.

Não recomendo outra rodada apenas com coeficientes diferentes, mais tempo para o LP auxiliar ou pequenas alterações na ordenação dos mesmos suportes. Nesses 16 casos, o impedimento era matemático.

---

**3. Candidata prioritária: cobertura de fluxo por regiões — FC-R.** O mecanismo preserva variáveis de fluxo que HL eliminava na projeção.

O nome FC-R é apenas uma identificação para este parecer. Não estou afirmando novidade na literatura geral: desigualdades para redes com custos fixos e ativação binária são uma área clássica. A possível contribuição estaria na adaptação ao MIN-STATION, nas relações demonstradas com os cortes existentes e numa separação eficaz. [Operations Research](https://pubsonline.informs.org/doi/10.1287/opre.33.4.842?utm_source=chatgpt.com)

Considere o dígrafo de alcance \(H=(V,A_r)\). Para uma região \(L\subseteq V\), defina seu excesso de origens:

\[
d_L=|S\cap L|-|T\cap L|.
\]

Suponha \(d_L>0\). Pelo balanço de COMP,

\[
f(\delta^+(L))-f(\delta^-(L))=d_L,
\]

portanto

\[
f(\delta^+(L))\ge d_L.
\]

Escolha um conjunto de possíveis estações de saída

\[
Q\subseteq N_H^+(L)\setminus(L\cup T).
\]

A exclusão de \(T\) é essencial: um destino pode receber uma unidade sem estação.

A desigualdade candidata é

\[
\boxed{
f\big(L,V\setminus(L\cup Q)\big)
+d_L\sum_{v\in Q}y_v
\ge d_L.
}
\tag{FC-R}
\]

Aqui \(f(U,W)\) é a soma dos fluxos dos arcos de \(U\) para \(W\).

**Interpretação.** O excesso de robôs da região precisa sair. Se não houver estação em \(Q\), essa saída deverá ocorrer pelas outras alternativas. Se houver alguma estação em \(Q\), ela pode atender todas as unidades necessárias: não se exige uma estação por robô.

**Prova de validade.** Há dois casos para uma instalação binária:

1. Se \(y(Q)=0\), então \(f_{uv}=0\) para todo arco com cabeça em \(Q\), porque \(Q\cap T=\varnothing\). Assim, todo fluxo que sai de \(L\) sai por fora de \(Q\), e o balanço implica a desigualdade.
2. Se \(y(Q)\ge1\), então \(d_Ly(Q)\ge d_L\), e o restante do lado esquerdo é não negativo.

A prova vale para todo fluxo admissível de COMP com \(y\) binário, **inclusive fluxos com circulações**. Não depende de escolher uma representação acíclica.

Para uma região com excesso de destinos,

\[
h_L=|T\cap L|-|S\cap L|>0,
\]

obtém-se a versão simétrica. Para

\[
Q\subseteq N_H^-(L)\setminus(L\cup S),
\]

vale

\[
\boxed{
f\big(V\setminus(L\cup Q),L\big)+h_Ly(Q)\ge h_L.
}
\tag{FC-R-T}
\]

A exclusão de \(S\) preserva a unidade que pode partir gratuitamente de uma origem.

Essas duas famílias:

- preservam o pareamento anônimo;
- permitem estações em terminais;
- admitem \(S\cap T\);
- não introduzem capacidades físicas;
- usam \(H\), não indevidamente as arestas de \(G\).

Quando \(S=T\), todos os saldos regionais são zero, coerentemente com a solução sem estações por permanência.

**Separação exata para uma região fixa.** No ponto \((f^*,y^*)\), defina

\[
w_v=f^*(L,\{v\}).
\]

Cada vértice elegível \(v\) pode permanecer fora de \(Q\), contribuindo \(w_v\), ou entrar em \(Q\), contribuindo \(d_Ly_v^*\). Portanto, a escolha ótima é

\[
\boxed{
Q^*=\{v\in N_H^+(L)\setminus(L\cup T):
w_v>d_Ly_v^*\}.
}
\]

O menor lado esquerdo é

\[
f^*(\delta^+(L))
-\sum_{v\text{ elegível}}\max\{0,w_v-d_Ly_v^*\}.
\]

Não há enumeração de subconjuntos de \(Q\). O custo é linear na fronteira da região.

Para todas as regiões unitárias \(L=\{s\}\), \(s\in S\setminus T\), e suas versões nos destinos, uma rodada completa pode ser feita em \(O(|A_r|)\).

A escolha da melhor região \(L\) globalmente continua sendo um problema separado. **Não demonstrei um separador polinomial para todas as regiões.** Para regiões maiores, a proposta é seleção heurística de candidatos seguida de separação exata em \(Q\).

**Relação com K e C8.**

- C1 é recuperado quando \(L=\{s\}\), não há destino direto e \(Q=N_H^+(s)\).
- Não demonstrei que FC-R implique todo C2 ou C4-DM. Portanto, K deve permanecer.
- Para \(L=\{s\}\), \(s\in S\setminus T\), e \(Q=\{v\}\), FC-R equivale a

\[
f_{sv}\le y_v+f^{in}(s),
\]

que é o C8 individual já discutido no projeto.

A diferença é permitir \(Q\) com vários vértices:

\[
\boxed{
\sum_{v\in Q}f_{sv}
\le y(Q)+f^{in}(s).
}
\tag{1}
\]

Somar os C8 individuais produziria

\[
\sum_{v\in Q}f_{sv}
\le y(Q)+|Q|f^{in}(s).
\]

Assim, a nova linha contabiliza a reentrada de fluxo **uma única vez**, enquanto os cortes individuais permitem reutilizar essa mesma parcela em vários arcos.

Isso enfrenta precisamente uma fragilidade apontada em [`direcoes-pli-min-station.md`, P4/C8](https://github.com/ElielLucas/min-station/blob/285261b/docs/technical/reference/tecnico/direcoes-pli-min-station.md). Não elimina todas as circulações nem garante um LP forte, mas é uma diferença matemática demonstrável.

**Limitações concretas.**

- Regiões equilibradas não produzem diretamente essas desigualdades.
- Muitas alternativas de saída podem tornar os cortes fracos.
- O LP pode reorganizar o fluxo sem aumentar o objetivo.
- O solver pode recuperar parte do fortalecimento automaticamente.
- Regiões grandes podem gerar linhas densas.
- Separação barata não garante reotimização barata.

A vantagem inicial é que essas limitações podem ser investigadas sem construir um oráculo físico exponencial.

---

**4. Duas alternativas adicionais, com prioridade menor.** São possibilidades defensáveis, mas não proponho desenvolver três linhas simultaneamente.

**Disjunções regionais no COMP+K completo.** Esta é uma generalização mais cara de FC-R.

Seja

\[
P=\{x:Ax\ge b\},\qquad x=(y,f),
\]

incluindo todas as restrições de COMP+K e os domínios. Para \(B\subseteq V\), escreva \(\pi_B^\top x=y(B)\). Como \(y(B)\) é inteiro nas soluções inteiras, é válida a disjunção

\[
y(B)\le k
\quad\vee\quad
y(B)\ge k+1.
\]

Podem-se separar pontos do conjunto

\[
\operatorname{conv}\left(
P\cap\{y(B)\le k\}
\;\cup\;
P\cap\{y(B)\ge k+1\}
\right).
\]

Uma desigualdade \(c^\top x\ge\beta\) recebe certificado pelos multiplicadores

\[
u,v,\mu,\nu\ge0
\]

que satisfaçam

\[
c=A^\top u-\mu\pi_B
  =A^\top v+\nu\pi_B,
\]

\[
\beta\le b^\top u-\mu k,
\qquad
\beta\le b^\top v+\nu(k+1).
\]

A validade segue por combinação não negativa das restrições de cada ramo. Para uma disjunção fixada, procurar o corte sob uma normalização dos multiplicadores é um LP.

FC-R pertence a essa construção com a disjunção \(y(Q)=0\) ou \(y(Q)\ge1\). Portanto, ela oferece uma referência mais forte para estudar o que a forma explícita FC-R deixa escapar.

A técnica geral é conhecida como programação disjuntiva/lift-and-project; não seria correto apresentá-la como invenção do projeto. [Springer Nature Link](https://link.springer.com/article/10.1007/BF01581273?utm_source=chatgpt.com)

Sua aplicação específica faz sentido porque mantém:

- os custos das instalações externas;
- os fluxos de fronteira;
- as restrições de atendimento;
- as interações entre K e ativação.

Entretanto, um LP auxiliar associado à rede completa pode ser caro. Vienna I056, por exemplo, possui 383.591 variáveis no comparador AS22. Ser polinomial para uma disjunção não torna a estratégia automaticamente escalável.

Minha prioridade seria usar essa alternativa como **referência em microcasos**, não iniciar por ela a campanha real.

Se forem selecionadas apenas algumas linhas do modelo para reduzir o separador, elas devem definir uma relaxação válida, mantendo as variáveis de fronteira. Fixar silenciosamente o exterior pode invalidar o corte.

**Obstruções condicionais com variáveis externas explícitas.** Esta alternativa corrige a perda de informação de HL, mas continua próxima dessa linha.

Particione

\[
V=R\mathbin{\dot\cup}B\mathbin{\dot\cup}F.
\]

Suponha demonstrado que toda instalação viável contida em \(R\cup F\) satisfaz

\[
\alpha^\top y_R\ge\beta,
\qquad \alpha\ge0,\ \beta>0.
\]

Então é globalmente válida

\[
\boxed{
\alpha^\top y_R+\beta\,y(B)\ge\beta.
}
\tag{2}
\]

Se nenhuma estação de \(B\) é instalada, aplica-se a desigualdade condicional. Se alguma é instalada, o termo \(\beta y(B)\) já satisfaz o lado direito.

Ela mantém explicitamente o preço das alternativas externas em \(B\). Não contradiz o teorema do cubo: seu suporte real é \(R\cup B\).

Contudo:

- se \(y^*(B)\ge1\), a linha não será violada;
- escolher \(B\) útil pode ser difícil;
- coeficientes de levantamento melhores exigem novas provas;
- a certificação da premissa pode continuar cara.

**Não priorizo essa alternativa.** Ela é uma extensão legítima de HL, mas não há evidência que justifique reiniciar a linha após AS20–AS22.

---

**5. Testemunha matemática de ganho.** Construí uma extensão de HB com relés duplicados, que distingue FC-R de K, C8 e C6.

Considere \(r=1\), seis origens e seis destinos:

\[
S=\{a_1,a_2,a_3,a_4,e_1,e_2\},
\]

\[
T=\{c_1,c_2,d_1,d_2,g_1,g_2\}.
\]

Para cada \(i=1,\ldots,4\), existem três relés

\[
X_i=\{x_{i1},x_{i2},x_{i3}\}.
\]

As arestas, todas não direcionadas, são:

- cada \(a_i\) ligado a \(c_1,c_2\);
- cada \(a_i\) ligado aos três vértices de \(X_i\);
- cada relé ligado a \(d_1,d_2\);
- \(e_j\) ligado a \(d_j,g_j\), para \(j=1,2\).

São 24 vértices e 96 arcos de alcance.

O gerador existente produz exatamente quatro K:

\[
y(\{c_1,c_2\}\cup X_1\cup X_2\cup X_3)\ge1,
\]

\[
y(\{c_1,c_2\}\cup X_1\cup X_2\cup X_4)\ge1,
\]

\[
y(X)+y_{e_1}\ge1,
\qquad
y(X)+y_{e_2}\ge1,
\]

onde \(X=X_1\cup X_2\cup X_3\cup X_4\).

COMP+K admite objetivo 1: instale \(1/2\) em um relé de \(X_1\) e \(1/2\) em um de \(X_2\), enviando uma unidade por cada um aos dois destinos \(d_j\). As outras origens \(a_i\) atendem \(c_1,c_2\), e \(e_j\) atende \(g_j\). Esse ponto foi conferido exatamente no compilador.

Como K implica objetivo pelo menos 1,

\[
z_{LP}(COMP+K)=1.
\]

Por outro lado,

\[
OPT=2.
\]

Duas estações em grupos \(X_i\) distintos bastam. Uma única estação não permite atender as quatro origens \(a_i\): ou nenhuma delas ganha acesso útil aos destinos remotos, ou apenas uma ganha esse acesso, deixando três origens disputando \(c_1,c_2\).

**Todos os HL com suporte de tamanho até 8 são inúteis nessa instância.**

Para deixar disponíveis relés de apenas um grupo, seria necessário remover as possibilidades de instalação dos três outros grupos: nove relés.

Logo, qualquer conjunto \(R\) com \(|R|\le8\) deixa no complemento pelo menos dois grupos \(X_i\) com relés disponíveis. Esse complemento é fisicamente viável. Portanto,

\[
Q_R=[0,1]^R
\qquad\forall R:\ |R|\le8.
\]

Aqui “remover” significa retirar a possibilidade de instalar estações, não apagar vértices físicos ou terminais.

**Quatro FC-R já fortalecem o LP.**

Escolhendo \(L=\{a_i\}\) e \(Q=X_i\), obtemos

\[
\boxed{
y(X_i)+f_{a_i c_1}+f_{a_i c_2}\ge1,
\quad i=1,\ldots,4.
}
\tag{3}
\]

Abrevie

\[
x=y(X),\qquad
a=\sum_{i=1}^4y_{a_i},\qquad
c=y_{c_1}+y_{c_2}.
\]

As quatro linhas, combinadas com COMP, implicam

\[
x+5a\ge2,
\qquad
x+5c\ge2.
\tag{4}
\]

A primeira vem do excesso de duas origens na região \(\{a_1,\ldots,a_4,c_1,c_2\}\), junto ao limite de reentrada nas origens. A segunda vem de somar (3) e limitar o fluxo recebido por \(c_1,c_2\).

Multiplicando cada linha de (4) por \(1/5\), e cada K \(x+y_{e_j}\ge1\) por \(3/10\), resulta

\[
x+a+c+\frac3{10}(y_{e_1}+y_{e_2})\ge\frac75.
\]

Portanto,

\[
z_{LP}(COMP+K+\text{quatro FC-R})\ge\frac75.
\]

Existe um ponto racional viável de custo \(7/5\), conferido nas equações, logo esse valor é exato para o modelo com essas quatro linhas.

**A melhora não se limita a redescobrir C8.**

Um ponto que satisfaz todos os C8 individuais é:

- \(y_v=1/6\) nos seis relés de \(X_1\cup X_2\);
- cada \(a_i\), \(i=1,2\), envia \(1/3\) para cada relé de seu grupo;
- cada relé envia \(1/6\) para cada \(d_j\);
- adicionam-se circulações de \(1/6\) em \(a_1-c_1-a_1\) e \(a_2-c_2-a_2\);
- \(y_{a_1}=y_{a_2}=y_{c_1}=y_{c_2}=1/30\);
- os outros atendimentos são diretos.

Seu objetivo é

\[
1+\frac4{30}=\frac{17}{15}.
\]

Ele satisfaz COMP+K e os 36 C8 individuais aplicáveis, mas viola (3): para \(i=1,2\), o lado esquerdo vale \(2/3\).

Assim,

\[
\boxed{
z_{LP}(COMP+K+C8)
\le\frac{17}{15}
<
\frac75
=
z_{LP}(COMP+K+\text{quatro FC-R}).
}
\]

**Também há ganho marginal além de C6+C8.**

O C6 relevante gerado na direção das origens é

\[
x+2c\ge2.
\]

Há um ponto racional de COMP+K+C6+C8 com custo

\[
\frac{47}{30}.
\]

Com as quatro FC-R, a combinação

\[
\frac15(x+5a\ge2)
+\frac12(x+2c\ge2)
+\frac3{20}(x+y_{e_1}\ge1)
+\frac3{20}(x+y_{e_2}\ge1)
\]

implica objetivo pelo menos \(17/10\). Um ponto racional viável atinge esse valor.

Portanto,

\[
\boxed{
z_{LP}(COMP+K+C6+C8)
\le\frac{47}{30}
<
\frac{17}{10}
=
z_{LP}(COMP+K+C6+C8+\text{quatro FC-R}).
}
\]

Esses resultados demonstram **complementaridade**, não dominância universal de FC-R sobre C6.

A verificação realizada nesta revisão incluiu:

- checagem racional das 76 restrições compiladas de COMP+K;
- checagem dos C8 individuais;
- geração e conferência dos C6 nas duas orientações;
- checagem das quatro novas desigualdades;
- avaliação física do conjunto vazio, de todas as 24 instalações unitárias e de uma instalação viável com duas estações.

Não resolvi LPs para produzir esses números: os valores exatos afirmados decorrem de pontos viáveis e combinações algébricas que fornecem limites inferiores coincidentes.

---

**6. Comparação e prioridade.** A evidência disponível favorece uma triagem de FC-R, não uma promoção imediata.

| Família | Força / relação conhecida | Evidência de não redundância | Separação | Escalabilidade e risco | Decisão |
|---|---|---|---|---|---|
| COMP+K | Referência; forte ganho sobre COMP | Evidência LP e MIP existente | Geração estática existente | Custo conhecido | Manter |
| H2 | Pode fortalecer K em construções | Sintética; sem ganho marginal AS16 nos pares avaliáveis | Oráculo por suporte | Custo sem benefício observado | Encerrar linha testada |
| HL cardinalidade | Casco local parcialmente explorado | K4 | Enumeração ou camadas inferiores | Forte dependência do suporte | Encerrar estratégia atual |
| HL poliédrico AS22 | Casco completo do suporte escolhido | Sintética; 16 cubos completos no real | Exponencial no suporte | Mais coeficientes não resolvem projeção trivial | Encerrar estratégia atual |
| **FC-R** | Generaliza C8 individual; complementa K | **Prova e testemunha racional, inclusive além de C6+C8** | **Exata, linear na fronteira para região fixa** | Reotimização e escolha de regiões ainda incertas | **Prioridade única** |
| Disjunção regional completa | Contém FC-R para as disjunções correspondentes | Herda a testemunha; ganho adicional aberto | LP auxiliar | Memória e tempo potencialmente altos | Referência em microcasos |
| Levantamento com variáveis externas | Corrige o exterior gratuito de HL | Validade provada; ganho relevante não demonstrado aqui | Oráculo condicional | Pode reproduzir custo e seleção difíceis de HL | Não priorizar |

A prioridade de FC-R se apoia em quatro elementos:

1. Há uma deficiência específica que ela corrige: reutilização da mesma reentrada de fluxo em diversas desigualdades individuais.
2. Há ganho estrito demonstrado contra comparadores mais fortes que COMP+K.
3. O separador para regiões fixadas é simples e não depende de enumeração física.
4. A validade utiliza diretamente balanço, ativação e integralidade de \(y\), com coeficientes inteiros verificáveis.

Isso é suficiente para justificar **um próximo teste científico**, não uma expectativa garantida de desempenho.

A hipótese mais plausível é encontrar oportunidades em regiões com alternativas de saída fracionárias e redistribuição por terminais. Em grafos densos de alcance, as alternativas podem enfraquecer o corte; em MAPF, regiões espaciais podem ser úteis, mas precisam ser avaliadas em \(H\), pois uma barreira em \(G\) pode desaparecer com a autonomia.

---

**7. Plano AS23 em diante.** Eu adotaria uma sequência curta, com encerramento explícito se o sinal não aparecer.

| Etapa | Pergunta | Evidência exigida para avançar |
|---|---|---|
| **AS23 — Revisão matemática** | FC-R é válida e distinta das linhas antigas? | Revisão independente da prova, reprodução racional da testemunha e comparação com literatura de fixed-charge flow |
| **AS24 — Microvalidação do separador** | O separador encontra corretamente as violações da família declarada? | Concordância com enumeração de regiões/subconjuntos em instâncias pequenas; zero cortes inválidos |
| **AS25 — Piloto LP pareado** | Há ganho marginal útil sobre COMP+K nas instâncias reais? | Ganho e custo medidos nos seis casos de desenvolvimento, com censuras preservadas |
| **AS26 — Raiz MIP e piloto inteiro** | O ganho sobrevive aos cortes automáticos e melhora a busca? | Somente após sinal LP suficiente; comparação pareada com orçamento total |
| **Avaliação independente** | O efeito generaliza? | Política congelada e uso dos conjuntos reservados conforme sua proveniência |

Na AS23, a testemunha deste parecer deve ser reproduzida por outra implementação ou verificador. O ganho demonstrado aqui não substitui essa revisão.

Na AS24, os controles devem incluir:

- \(S=T\) e ótimo zero;
- interseção parcial \(S\cap T\);
- uma estação compartilhada por vários robôs;
- cadeias que exigem recargas sucessivas;
- pares diretos;
- circulações adversariais do tipo P4;
- \(r>1\), para impedir confusão entre \(G\) e \(H\);
- situações em que K já fecha o LP.

Para pequenos grafos, comparar a seleção fechada de \(Q^*\) com enumeração exaustiva. O resultado “nenhuma violação” precisa indicar se cobre todas as regiões unitárias, uma lista de regiões ou a família completa daquele microcaso.

Na AS25, usaria os mesmos seis casos de desenvolvimento e os braços:

\[
COMP,\quad COMP+K,\quad COMP+FC\!-\!R,\quad COMP+K+FC\!-\!R.
\]

Dentro de FC-R, uma ablação deve distinguir:

- regiões unitárias nos terminais;
- regiões maiores selecionadas por estrutura e fluxo.

C6 e C8 servem como controles matemáticos nos microcasos; não proponho reabrir campanhas inteiras dessas linhas.

Manteria inicialmente o orçamento exploratório de 90 segundos totais por braço. Se houver escalada de orçamento para resolver censuras, ela deve ser uma rodada separada, definida para ambos os métodos, sem eliminar os casos censurados anteriores.

As métricas indispensáveis são:

- objetivo LP e incremento absoluto/relativo;
- cortes candidatos, violados, adicionados e duplicados;
- tempo de preparação, separação, certificação algébrica e reotimização;
- variáveis, linhas, não zeros e memória;
- alteração apenas de fluxo versus aumento efetivo do objetivo;
- cobertura dos seis casos e censuras.

**Gate proposto, a congelar antes da execução:** avançar se houver ganho LP de pelo menos 1% em dois grafos brutos independentes, com custo total até duas vezes o controle nesses casos e sem perdas de aplicabilidade ocultadas.

Esses números são critérios propostos para o novo estudo, não alterações dos gates anteriores.

Interromperia se:

- os cortes apenas eliminarem representações de fluxo, sem melhorar o objetivo;
- o efeito ocorrer apenas no exemplo construído;
- a melhora depender de regiões cuja separação custe mais que o benefício;
- a contribuição desaparecer integralmente após os cortes automáticos do solver.

Para o MIP posterior, medir separadamente raiz antes/depois dos cortes automáticos, melhor limite dual, incumbente fisicamente validada, gap, tempo até primeira solução, tempo até prova, nós e memória. Uma melhora no LP puro não basta.

Há também uma distinção útil: quando um ponto LP ótimo satisfaz **toda uma subfamília separada exatamente**, adicionar essa subfamília não melhora o objetivo naquele caso. Isso permite uma decisão negativa rápida para a versão com regiões unitárias, sem repetir a sequência de mudanças de coeficientes ocorrida em HL.

**Minha escolha final é FC-R: cortes de cobertura de fluxo por regiões, começando pela separação completa nas regiões unitárias e por uma lista pequena de regiões maiores.** A primeira hipótese a testar é se a agregação que demonstrou ganho além de C6/C8 encontra violações que elevam o objetivo nas instâncias reais de COMP+K, a custo total controlado.

A matemática apresentada sustenta investigar essa hipótese. A superioridade computacional continua aberta.
