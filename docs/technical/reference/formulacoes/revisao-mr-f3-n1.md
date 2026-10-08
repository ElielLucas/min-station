# MR-F3 — Parecer matemático para a formulação F-C3 (N1-T2)

**Data:** 2026-10-07.
**Decisão:** `ACCEPTED` — **revisão matemática documental**, para liberar a implementação de F-C3 na N1-T3.
**Escopo do parecer:** definições, provas estruturais e exemplos analíticos; **não** é execução do modelo, certificação por solver, revisão por parecerista humano ou validação experimental.
**Branch consultada:** `novos_testes` (`ElielLucas/min-station`, árvore Git `7056ed2dd9124567e57d7cef574072f0c7f5afb7`).
**Spec vigente:** `specs/proxima-fase-n1-informacao-compatibilidade/spec.md`, N1-T2 (story 2), especialmente AC 1–9 e gate MR-F3.
**Formulação aprovada:** `docs/technical/reference/formulacoes/formulacao-fc3-canonica-v1.md`, versão **1.0.1**.
**SOURCE preservada:** `docs/technical/reference/formulacoes/formulacao-fc3-componentes-trios.md`, 01/10/2026, recuperada em 07/10/2026, SHA-256 `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4`.

> **Como ler este aceite:** as conclusões `PROVEN` abaixo se referem a argumentos escritos, examinados nesta revisão técnica. Não substituem a validação exaustiva por instalação da story 3. A intervenção de um parecerista humano independente ainda pode identificar lacunas; ela não é alegada como já realizada.

## 1. Delimitação e proveniência

O objeto revisado é o MIN-STATION de Das: grafo não direcionado e unitário `G=(V,E)`, origens `S`, destinos `T` com `|S|=|T|=m`, autonomia inteira `r≥1`, estações permitidas em **todo** `V`, pareamento livre, permanência em `s∈S∩T`, terminais utilizáveis como relés e ausência de capacidade/colisão/tempo. Uma instalação `C⊆V` é viável quando existe uma bijeção `S→T` cujos pares admitem caminhos com saltos de comprimento no máximo `r` entre recargas em `C`.

Usa-se `H=G^r` (sem laços) e a vizinhança **fechada** `B(W)=W∪N_H(W)`. Um salto direto `s→t` satisfaz `d_G(s,t)≤r`, incluindo `(s,s)` quando `s∈S∩T`. Para cada `W⊆V` não vazio, conexo em `H`, elegível para pelo menos uma origem e um destino, considere `S_W=S∩B(W)` e `T_W=T∩B(W)`.

| Objeto ou afirmação | Referência | Proveniência | Parecer |
|---|---|---|---|
| Domínio, `H`, `B(W)`, pares diretos | SOURCE §2 | `SOURCE` | Aceito |
| Variáveis e equações CA1–CA6 (inclusive CA5) | SOURCE §3 | `SOURCE` | Aceito; prova R1 |
| Polítopo de atribuições e relação com F-CC | SOURCE §3.3; P7 em `provas-fcc-fc3.md` | `SOURCE` + `DERIVED` | Aceito; prova R1 |
| Estágios `(j,B)`, arcos de não uso, arcos de uso `R=∅`, finais | SOURCE §5.1 | `SOURCE` | Aceito; R2 |
| C31–C34, redes para trios de `S` e `T` | SOURCE §§5.2–5.4 | `SOURCE` | Aceito; R2 |
| Exatidão de `y` binário | SOURCE §6 | `SOURCE` | Aceito; R3 |
| Dominância LP F-C3 / F-CC / OPT | SOURCE §7 e P7 | `DERIVED` | Aceito; R4 |
| Triângulos com pontes, LP `3g/2` e `2g` | SOURCE §8 | `SOURCE`, argumento revisado | Aceito; R5 |
| Ciclo de cinco vértices, LP `5/2` | SOURCE §9 | `SOURCE`, argumento revisado | Aceito; R6 |
| Limite `2·binom(m,3)·(35nW+8)` | SOURCE §10.2 | `SOURCE` | Aceito; R7 |
| Corrigir `d_ss=0` do resumo antigo | SOURCE §§2,3,6 | `DERIVED` | Aceito; `d_G(s,s)=0` mas `d_ss∈[0,1]` |
| Separar F-C3 de C3-cut; remover elo F-OD do N1 | decisão da spec N1 | `NEW` | Aceito como convenção do projeto |

**Não recuperados (`UNRECOVERED`):** `MIN-STATION-formulacao-por-componentes.md`, `MIN-STATION-formulacao-fluxos-origem-destino.md` e a consolidação F-C3 de 05/10/2026. Nada neste parecer depende de reconstruir seus textos. F-OD só é citado como história; não faz parte da cadeia aprovada.

## 2. R1 — Exatidão da compressão F-CA da F-CC (`PROVEN`)

Fixado `W`, F-CC usa variáveis por pares não vazios de subconjuntos `(I,J)` com `|I|=|J|≥1`. Em F-CA, definem-se `λ_W≥0`, `0≤α_sW,β_tW≤λ_W`, `Σ_s α_sW = Σ_t β_tW` e a restrição **CA5** `λ_W≤Σ_s α_sW`.

**F-CC → F-CA.** Some as massas das configurações F-CC por `W`. O peso de uma configuração conta `|I|≥1` vezes em `Σ_s α_sW`; portanto CA5 vale. As marginais por origem e destino e a carga das estações são preservadas.

**F-CA → F-CC.** Para `λ_W=0`, as marginais são zero por CA3. Para `λ_W>0`, normalize `a_s=α_sW/λ_W`, `b_t=β_tW/λ_W`. O ponto pertence a

\[
P_W=\left\{(a,b)\in[0,1]^{|S_W|+|T_W|}:\sum_s a_s=\sum_t b_t\ge1\right\}.
\]

Esse polítopo é integral. Se `Σa≥1` estiver estritamente folgada num vértice, somente uma igualdade acopla os limites de caixa e, portanto, no máximo uma coordenada poderia ser fracionária; com as demais integrais, `Σa=Σb` torna impossível que apenas uma coordenada seja fracionária. Se `Σa=1`, então também `Σb=1`, e a face é produto de dois simplexos unitários, cujos vértices são incidências 0–1 de conjuntos unitários. Em ambos os casos cada vértice é a incidência de `(I,J)` com `|I|=|J|≥1`. Decomponha `(a,b)` em combinação convexa desses vértices e multiplique os pesos por `λ_W`; obtém-se F-CC com os mesmos `λ_W`, `α`, `β`, `d` e `y`. Portanto

\[
\operatorname{proj}_y(P_{CA})=\operatorname{proj}_y(P_{CC}).
\]

**CA5 e código histórico:** `fcc.py` na forma `separada` permite massa de `λ` com `I=J=∅`. Essa massa não contribui para `α`, `β` ou `d`. Removê-la diminui apenas `λ`, afrouxando CA3/CA6, sem alterar as marginais ou `y`. Isso justifica **projeção em `y`** e valor LP idênticos, mas **não** preservação do `λ` original. O código histórico permanece inalterado.

## 3. R2 — Redes e acoplamento corretos (`PROVEN`)

Fixe uma enumeração global `W_1,…,W_nW`, independente de trios. Para **cada** `U∈binom(S,3)` e **cada** `U∈binom(T,3)`, construa uma rede distinta com estados `(j,B)` para `j∈{0,…,nW}`, `B⊆U`; raiz `(0,∅)` e sorvedouro `ω`. Uma etapa `j` tem:

1. Arco **não uso** `(j−1,B)→(j,B)`.
2. Arco **uso** `(j−1,B)→(j,B∪R)` para **todo** `R⊆(U\B)∩S_Wj` no lado origem (ou `T_Wj` no destino), **inclusive** `R=∅`, distinto do arco de não uso.
3. No final, `(nW,B)→ω`, rotulado com os membros `U\B` a serem servidos diretamente.

C31 impõe um fluxo unitário conservado na rede acíclica; C32 soma, por etapa e rede, a massa dos **arcos uso** igual a `λ_Wj`. C33 iguala, para cada terminal do trio, a massa dos arcos uso que o selecionam à marginal `α_sWj` ou `β_tWj`. C34 iguala a massa dos arcos finais em que um terminal não foi selecionado ao total de viagens diretas incidentes (`Σ_td_st` no lado origem, `Σ_sd_st` no destino).

Qualquer caminho raiz–sorvedouro usa uma única alternativa de cada etapa e não atribui o mesmo membro duas vezes porque `R⊆U\B`. A decomposição de um fluxo unitário em caminhos, válida por aciclicidade, demonstra que essas redes descrevem distribuições sobre atribuições **locais** coerentes. Não impõem uma distribuição global comum entre todos os trios, nem integralidade do modelo acoplado.

**Verificação de C34:** em todo caminho o membro `u` aparece exatamente em um dos dois eventos: atribuído em alguma etapa, ou ausente de `B` no final. Pela conservação e C33, o segundo evento tem peso `1−Σ_W α_uW` (origem) ou `1−Σ_W β_uW` (destino). CA1–CA2 identificam esses valores com as respectivas somas de `d`. Portanto C34 explicita uma consequência, sem mudar o domínio.

**Casos de borda cobertos:** um W utilizado por pessoas fora de U tem arco uso com `R=∅`; uma origem `s` também presente em T aparece em **duas redes com papéis distintos**; `d_ss` é permitido e pode valer 1; uma componente não utilizada pode manter `y_v=1` sem forçar `λ_W>0`; `m<3` implica nenhuma rede e F-C3 igual a F-CA.

## 4. R3 — Equivalência para instalações binárias (`PROVEN`)

**Instalação física `C` viável ⇒ F-C3 com `y=χ_C`.** Fixe uma bijeção viável entre S e T com caminhos de saltos em H. Separe viagens sem recarga, inclusive permanência, registradas em `d`; atribua cada viagem com recarga à componente de `H[C]` que contém as suas estações. Essas componentes `W` são não vazias, conexas, **disjuntas** e elegíveis para os terminais que servem. Para cada componente usada, defina `λ_W=1`, `α_sW=1` para seus pontos de partida e `β_tW=1` para seus destinos. Todas as demais massas são zero. CA1–CA5 valem pelo balanceamento dos grupos; CA6 vale porque os W usados são disjuntos e estão em C. Para cada trio, percorra exatamente o conjunto de W usados: arco uso com `R=U∩I_W` (ou `U∩J_W`), possivelmente vazio, e arco não uso nos outros. Os remanescentes são os atendidos diretamente. O fluxo desse caminho satisfaz C31–C34. Esta prova **não** supõe conectividade global de H[C].

**F-C3 com `y=χ_C` viável ⇒ instalação física `C` viável.** CA6 força `W⊆C` sempre que `λ_W>0`, porque cada `y_v∈{0,1}` e cada `W` é não vazio. Para cada W com `k_W=Σ_sα_sW=Σ_tβ_tW>0`, forme `p^W_st=α_sW β_tW/k_W` para `s∈S_W,t∈T_W`. As somas de linha e coluna de `p^W` são exatamente `α` e `β`. Somadas às viagens diretas `d`, formam uma matriz não negativa com todas as somas de linha/coluna iguais a 1. Cada aresta positiva de `p^W` é realizável: os dois terminais alcançam H[W], que é conexo, e `W⊆C`. Pela integralidade do politopo de emparelhamentos bipartidos, o suporte dessa matriz contém um matching perfeito inteiro; cada par desse matching tem rota física viável. As redes de trios apenas restringem o LP, não são necessárias a esta implicação.

A prova cobre explicitamente `S∩T`, estações em terminais, relés, permanência e componentes distintas de H[C]. O **teste independente** para cada `C⊆V` de cada instância selecionada na N1-T3 continua obrigatório e não foi realizado neste parecer.

## 5. R4 — Dominância sobre F-CC (`PROVEN`)

A relaxação linear de F-C3 é F-CA acrescida de redes C31–C34; assim
`proj_y(P_C3^LP)⊆proj_y(P_CA^LP)`. Por R1, a última projeção é a de F-CC. Portanto `z_LP(F-C3)≥z_LP(F-CC)`. Pela primeira direção de R3, todas as instalações inteiras viáveis aparecem na formulação; logo `z_LP(F-C3)≤OPT`. As duas desigualdades persistem com **o mesmo** conjunto K de cortes válidos aplicado a ambos os modelos, desde que se teste que os cortes não excluem instalações físicas.

Isso não prova que **COMP** seja dominada por F-C3, que F-C3 + K acrescente ganho estrito nem que o novo modelo execute mais rápido.

## 6. R5 — Família de triângulos com pontes (`PROVEN`)

Releitura independente da construção **SOURCE §8**. Seja `L_g` a união de `g` triângulos `{a_i,b_i,c_i}`, ligados pela aresta `a_i–a_(i+1)`. Para cada vértice `u` de L_g, crie candidato `c_u`; para cada aresta `e={u,v}`, crie origem `s_e` e destino `t_e`, cada um adjacente somente a `c_u,c_v`. Não acrescente outras arestas; `r=1`. Há `3g` candidatos, `4g−1` origens e o mesmo número de destinos; assim `n=11g−2`, `m=4g−1`.

**Ótimo inteiro `2g`.** Sem uma estação em pelo menos um dos candidatos extremos de cada aresta `e`, a origem `s_e` não alcança destino algum com uma única carga: primeiro atinge um dos dois candidatos e precisa recarregar para seguir. Estações em `s_e` ou `t_e` não substituem essa recarga. Logo toda instalação viável contém uma cobertura de vértices de L_g, exigindo ao menos dois candidatos de cada triângulo. Instalar `a_i,b_i` em todos os triângulos atende também às pontes. Consequentemente `OPT=2g`.

**F-CC e F-CA: `3g/2`.** A origem `s_e` não tem destino direto. Toda infraestrutura admissível W capaz de servi-la deve conter `c_u` ou `c_v`: se W não contivesse nenhum deles, teria de conter `s_e` para cobrir a origem, mas não poderia conectar esse vértice a uma infraestrutura que também cobrisse um destino. Logo CA1, CA3 e CA6 dão `y_cu+y_cv≥1`. Somando as três arestas de cada triângulo, obtemos `Σ_{u∈triângulos} y_cu≥3g/2`. Atribuir `y_cu=λ_{ {c_u} }=1/2` a todo candidato, e `α_s,{c_u}=β_t,{c_u}=1/2` para cada terminal de uma aresta incidente, satisfaz CA1–CA6 e atinge `3g/2`. R1 transfere esse valor a F-CC.

**F-C3: `2g`.** Para o trio de origens `U_i` correspondente às três arestas internas do triângulo `i`, defina `ρ_iW` como massa dos arcos **uso de W** que atendem pelo menos duas origens de `U_i`. Como em cada caminho da rede dois grupos que cobrem dois membros do trio se interceptariam, `Σ_Wρ_iW≤1` por C31. Escreva `k_i=|W∩{c_ai,c_bi,c_ci}|`, `k=Σ_i k_i`, `h=|{i:k_i>0}|`. Para `k_i=0`, W não pode servir `U_i` (pela estrutura de adjacências e conectividade). Para `k_i=1`, W pode servir no máximo duas origens de `U_i`, com esperança de quantidade no máximo `λ_W+ρ_iW`. Para `k_i≥2`, serve no máximo três, e `3λ_W≤(2k_i−1)λ_W+ρ_iW`. Então

\[
\sum_{s\in U_i}\alpha_{sW}\le(2k_i-1)\lambda_W+\rho_{iW}\quad(k_i>0).
\]

Qualquer W admissível contém algum candidato (um singleton de terminal não alcança terminais do outro lado) e, no grafo G bipartido candidatos–terminais, conectar `k≥1` candidatos exige ao menos `k−1` terminais intermediários: cada terminal tem grau no máximo dois; um subgrafo conexo com `k` candidatos e `t` terminais tem ao menos `k+t−1` arestas, e no máximo `2t`, logo `t≥k−1`. Portanto `|W|≥2k−1≥2k−h` e

\[
\sum_i\sum_{s\in U_i}\alpha_{sW}\le|W|\lambda_W+\sum_i\rho_{iW}.
\]

Nenhuma origem dos trios tem destino diretamente alcançável; somando CA1 para essas `3g` origens e aplicando C31 e CA6:

\[
3g\le\sum_W|W|\lambda_W+\sum_i\sum_W\rho_{iW}
\le\sum_{v\in V}y_v+g.
\]

Logo `Σ_vy_v≥2g`. A instalação inteira de custo `2g` estabelece o limite oposto. Assim `z_LP(F-C3)=2g`. Para `g=2` a previsão é `n=20`, `m=7`, `z_LP(F-CC)=3`, `z_LP(F-C3)=OPT=4` **como resultado matemático**, não como medição.

## 7. R6 — Ciclo de cinco candidatos (`PROVEN`)

Tome L igual ao ciclo `C_5` e aplique a mesma transformação SOURCE §9. Há cinco candidatos, cinco origens e cinco destinos, `n=15`, `m=5`, `r=1`. A instalação inteira ótima cobre arestas do ciclo e exige três candidatos: `OPT=3`.

Para cada aresta `e={u,v}`, o argumento de R5 dá `y_cu+y_cv≥1`. Cada candidato participa de duas arestas: `Σ_v y_cv≥5/2`; F-CC atinge `5/2` com os cinco candidatos de peso `1/2`. Restam provar viáveis suas redes de trios. Um trio de origens equivale à seleção de três arestas do ciclo; essas três arestas formam uma **floresta**. Escolha uma 2-coloração do grafo dessa floresta, representada por `x_c∈{0,1}`, de modo que `x_u+x_v=1` para cada aresta selecionada; escolha seus valores arbitrariamente nas demais componentes isoladas. A realização `x` escolhe, entre os cinco W singleton, exatamente os candidatos com `x_c=1`; a realização complementar `1−x` escolhe os restantes. Cada origem do trio tem exatamente um extremo selecionado em cada realização, e a mistura 1/2–1/2 dá `λ_W=1/2` e `α_sW=1/2` para incidências elegíveis. Arcos uso com `R=∅` representam candidatos selecionados sem membro daquele trio. Faça o mesmo, independentemente, em cada rede de trios de destinos. C31–C34 valem, com `d=0`. A mistura satisfaz F-C3 com objetivo `5/2`, dando

\[
z_{LP}(F-C3)=\tfrac52<3=OPT.
\]

As distribuições podem variar por trio, o que explica por que a consistência de trios não elimina toda a fracionalidade.

## 8. R7 — Tamanho e semântica de índice (`PROVEN`)

Em cada etapa existem 8 estados de partida. Para cada membro do trio há três alternativas (já atendido, atendido agora ou ainda não atendido), gerando no máximo `3³=27` arcos uso; somam-se até 8 arcos não uso e, no fim, 8 arcos para `ω`. Daí **até `35nW+8` variáveis de arco por rede** e **`2·binom(m,3)` redes**. O cap congelado na N1 é

\[
2\binom{m}{3}(35nW+8)\le5\,000\,000.
\]

O `nW` aqui é a quantidade **filtrada** de infraestruturas. O símbolo **K experimental** refere-se aos cortes C1+C2+C4-DM e não deve ser usado como tamanho de `𝒲` em código ou registros.

## 9. Decisão e pendências separadas

| Item do gate MR-F3 | Decisão | Fundamento |
|---|---|---|
| CA1–CA6 e CA5 | `ACCEPTED` | R1 |
| Redes C31–C34, ambos os lados, `R=∅` | `ACCEPTED` | R2 |
| Permanência `d_ss`, terminais/relés e várias componentes | `ACCEPTED` | R2–R3 |
| Exatidão para `y∈{0,1}^V` | `ACCEPTED` | R3 |
| P8: dominância F-C3 ≥ F-CC, limite ≤ OPT | `PROVEN` / `ACCEPTED` | R1, R3–R4 |
| P11: g-triângulos e C5 | `PROVEN` / `ACCEPTED` | R5–R6 |
| N1-T3, verificação de implementação com `viavel` | `NOT MEASURED` | Próxima story; **não** substituída pelo parecer |
| N1-T3, valores LP e regressões SOURCE | `NOT MEASURED` | Exigem modelo, Gurobi e caps |
| Avaliação independente por parecerista humano | `OPEN` | Não ocorreu nesta entrega |
| Novidade bibliográfica / melhor tempo de solução | `OPEN` | Não é resultado desta revisão |

**Conclusão:** a revisão matemática documental MR-F3 está **aceita** para fins do gate da spec N1 e autoriza apenas **iniciar a implementação de F-C3** como módulo novo. Não autoriza publicar conclusões experimentais nem executar o diagnóstico N1-T5 antes de passar pelos testes de equivalência por instalação de N1-T3. Os testes devem incluir `S∩T`, permanência, terminais como relés, instalações viáveis com mais de uma componente, instâncias com `m≥3` e instalações ótimas e não ótimas; qualquer discordância bloqueia leitura de LP dessa arm.

## 10. Invariantes a conferir na implementação subsequente

- Use **a mesma** lista determinística `𝒲` para o núcleo e para **todas** as redes; mantenha `nW` separado de K (cortes).
- Inclua **CA5** sem alterar o `fcc.py` histórico; não aceite configuração vazia `I=J=∅` como peso útil.
- Preserve arcos uso com `R=∅`, distintos de não uso, e inclua **C32** para cada W em cada rede.
- Mantenha `d_ss` quando `s∈S∩T` e não introduza a restrição errada `d_ss=0`.
- Fixe `y=χ_C` e teste viabilidade nos dois sentidos contra `viavel` para **todo** `C⊆V` do conjunto de validação da story 3 antes de qualquer medida de LP F-C3.
- Em instâncias com `m<3`, confirme que F-C3 reduz a F-CA (núcleo comprimido); isso **não** significa igualdade de variáveis auxiliares com a forma `separada` sem CA5.
- Exclua por cap antes de resolver; registre `NOT MEASURED` em vez de inferir ausência de ganho.
- Confira, posteriormente, as regressões de `g=2` e `C5` sem ajustar a formulação para forçar o resultado; discrepância é bloqueio/investigação.

**Arquivo histórico SOURCE inalterado. Nenhum commit e nenhuma medição de solver fazem parte deste parecer.**
