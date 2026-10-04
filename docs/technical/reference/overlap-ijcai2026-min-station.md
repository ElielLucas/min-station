# Sobreposição com o artigo IJCAI 2026 e posicionamento científico do projeto (T22)

**Data:** 2026-10-03
**Commit de base da análise:** `ef1c0ec` (árvore limpa, exceto `specs/bloco4-posicionamento-cientifico/spec.md`)
**Spec:** `specs/bloco4-posicionamento-cientifico/spec.md`
**Tarefa:** T22 de `docs/technical/plans/backlog-continuacao.md`

Este documento é o levantamento de posicionamento do projeto frente à literatura. Ele não contém
resultado experimental novo, não altera formulação, corte ou família, e não escreve o artigo. Ele
produz: a bibliografia, as verificações de literatura LC-1 a LC-5, a tabela de definições, a matriz
de sobreposição, a tabela de cortes, os quatro vereditos sobre a PLI, a tabela de contribuições, a
lista de correções de afirmações, o mapa de dependência científica e a narrativa experimental do
Bloco 3 como contribuição.

**Fontes lidas integralmente nesta análise:** `novo_artigo_das_2026.pdf` (IJCAI-26, 9 páginas,
pp. 72–80), `min-station-das.pdf` (preprint de periódico, 16 páginas), `artigo-sbpo.pdf` (12
páginas). Documentos do repositório citados por seção e, quando relevante, por linha. Fontes
externas consultadas por busca dirigida estão listadas na §2 com o que foi verificado em cada uma.

**Convenções.**
- O artigo IJCAI escreve `k` para o número de agentes e `c` para o orçamento de estações da versão
  de decisão. O projeto escreve `m` e resolve a versão de otimização. Toda comparação abaixo é
  feita pela definição, nunca pelo símbolo.
- "IJCAI p.N" refere-se à paginação dos anais (72–80). "Das p.N" refere-se à paginação do PDF do
  preprint (1–16). "SBPO p.N" refere-se à paginação do PDF (1–12).
- **Vocabulário de relação (fixo):** `SAME`, `DIRECT CONSEQUENCE`, `ADAPTATION`, `EXTENSION`,
  `IMPLEMENTATION`, `EXPERIMENTAL VALIDATION`, `NEW FORMULATION`, `NEW INEQUALITY`,
  `NEGATIVE RESULT`, `OPEN / UNCLEAR`. Quando o projeto não tem construto próprio para um tema,
  a coluna de relação recebe `—` e a linha existe só para registrar o que deve ser citado.
- **Categorias de contribuição:** T1 teórica, T2 algorítmica, T3 computacional, T4 experimental,
  T5 engenharia. **Status:** `KEEP`, `QUALIFY`, `REMOVE`, `EXPERIMENTAL ONLY`, `ENGINEERING ONLY`,
  `PENDING BLOCK 3`, `UNRESOLVED`.
- **Grau de protocolo de um resultado experimental** (Bloco 2, `protocolo-comparacao-pareada.md`):
  - `pré-protocolo / extensão`: E0–E8, sobre TNTP (extensão ponderada e dirigida);
  - `pré-protocolo / Das`: E9–E14, sobre o benchmark-v1 (classe `principal`), antes da ordem
    determinística (T6) e do orçamento por `WorkLimit` (T7);
  - `conforme protocolo`: piloto da fase P, fase E de SC, medição de C6 (T14) e diagnóstico de
    desagregação (T18), todos em 2026-10-03 com registro anterior à medição.

---

## 1. Bibliografia

Referências completas das fontes primárias e de todas as fontes usadas na comparação. Campos
marcados "(a conferir)" não foram verificados contra o registro oficial nesta sessão.

### 1.1 Fontes primárias

1. **Das, A. K.; Hanaka, T.; Melissinos, N.; Ono, H.** *Charging Station Placement for Anonymous
   Mobile Agents: A Parameterized Complexity Perspective.* In: Kwok, J. (ed.), Proceedings of the
   Thirty-Fifth International Joint Conference on Artificial Intelligence (IJCAI-26), Main Track,
   pp. 72–80, agosto de 2026. DOI 10.24963/ijcai.2026/9. PDF local:
   `docs/technical/reference/novo_artigo_das_2026.pdf`. (Registro oficial e BibTeX verificados em
   `ijcai.org/proceedings/2026/9` nesta sessão: `month = {8}`, `year = {2026}`.)
2. **Das, A. K.** *Charging Station Placement for Limited Energy Robots.* Versão preliminar: In:
   Gaur, D.; Mathew, R. (eds.), Algorithms and Discrete Applied Mathematics (CALDAM 2025), LNCS
   15536, pp. 97–108, Springer, 2025. DOI 10.1007/978-3-031-83438-7_9 (online em 5 de fevereiro de
   2025). Versão de periódico: *Discrete Applied Mathematics*, DOI 10.1016/j.dam.2025.11.020
   (online em 20 de novembro de 2025; volume datado de 2026, a conferir). PDF local do preprint
   (16 páginas, "A preliminary version of this paper appeared in the proceedings of CALDAM 2025"):
   `docs/technical/reference/min-station-das.pdf`.
3. **Carvalho, E. L. O.; Ravelo, S. V.** *Formulações de Programação Linear Inteira para o Problema
   de Alocação Mínima de Estações de Recarga.* LVIII Simpósio Brasileiro de Pesquisa Operacional
   (SBPO 2026), Belo Horizonte, 28 de setembro a 1 de outubro de 2026. Anais em publicação (prazo
   de até 90 dias após o evento, segundo a organização). PDF local:
   `docs/technical/reference/artigo-sbpo.pdf`.

### 1.2 Fontes secundárias consultadas nas verificações LC-1 a LC-3

4. **Pereira, L. C.; Ravelo, S. V.** *Placement of charging stations for energy-constrained robots in
   spider graphs.* Anais do Encontro de Teoria da Computação (ETC), SBC, publicado em 19 de julho de
   2026. Resultado: algoritmo linear para o MIN-STATION em grafos-aranha; sem PLI. Mesmo grupo do
   projeto; não estava registrado em nenhum documento do repositório.
5. **Storandt, S.; Funke, S.** *Enabling E-Mobility: Facility Location for Battery Loading Stations.*
   AAAI 2013, pp. 1341–1347. DOI 10.1609/aaai.v27i1.8478. Verificado: NP-dificuldade e
   inaproximabilidade do problema "de qualquer lugar a qualquer lugar"; heurísticas (Restricted
   Random, k-Greedy) e limites inferiores por *Partial EV-Cover*; **não há PLI**.
6. **Agarwal, P. K.; Pan, J.; Victor, W.** *An Efficient Algorithm for Placing Electric Vehicle
   Charging Stations.* ISAAC 2016, LIPIcs 64, 7:1–7:12. DOI 10.4230/LIPIcs.ISAAC.2016.7. Verificado:
   SHORTEST-PATH HITTING SET — todo caminho mínimo entre todo par deve ser "hit"; redução a hitting
   set; algoritmo bicritério de aproximação; **não há PLI** e não há emparelhamento origem–destino.
7. **Kundu, T.; Saha, I.** *Charging Station Placement for Indoor Robotic Applications.* ICRA 2018,
   pp. 3029–3036. Verificado: formulação por **SMT** (Z3, núcleo insatisfatível); problema de
   cobertura "de qualquer ponto a alguma estação", sem pares S–T.
8. **Kundu, T.; Saha, I.** *Approximation Algorithms for Charging Station Placement for Mobile
   Robots.* IROS 2023, pp. 4770–4776. Verificado: NP-dificuldade e aproximações (Set Cover,
   Dominating Set) para o mesmo problema de cobertura de 7; **não há PLI**.
9. **Castro-Gama, M.; Hassink-Mulder, Y.** *Optimal charging station placement for autonomous robots
   in drinking water networks.* Journal of Hydroinformatics 25(6), 2253–2267, 2023. DOI
   10.2166/hydro.2023.040. Verificado: **PLI "akin to set covering"** por distância de caminho
   mínimo a cada nó dentro de `δmax`; não há origens/destinos nem bijeção. É a PLI mais próxima
   encontrada e já é citada pela introdução do artigo da SBPO (SBPO p.2) como abordagem distinta.
10. **Kundu, T.; Saha, I.** *Mobile recharger path planning and recharge scheduling in a multi-robot
    environment.* IROS 2021, pp. 3635–3642. Citado pelo IJCAI; recarregadores móveis; não é o
    problema. Não lido além do resumo.
11. **Kumar, N. et al.** *The persistent robot charging problem for long-duration autonomy.* IEEE
    RA-L 10(3), 2191–2198, 2025. Citado pelo IJCAI; escalonamento de recarga; não é o problema. Não
    lido além do resumo.
12. **Jansen, K.; Kratsch, S.; Marx, D.; Schlotter, I.** *Bin packing with fixed number of bins
    revisited.* JCSS 79(1), 39–49, 2013. Fonte da W[1]-dificuldade usada no Teorema 4 do IJCAI. Não
    lido; citado apenas para rastrear a origem do gadget BP.
13. **Katsikarelis, I.; Lampis, M.; Paschos, V. Th.** *Structural parameters, tight bounds, and
    approximation for (k,r)-center.* DAM 264, 90–117, 2019. Fonte do Teorema 5 do IJCAI. Não lido.

### 1.3 Análogos clássicos usados como qualificadores (LC-2)

14. **Codato, G.; Fischetti, M.** *Combinatorial Benders' cuts for mixed-integer linear programming.*
    Operations Research 54(4), 2006. Já listado em `direcoes-pli-min-station.md` Apêndice B.
15. **Magnanti, T. L.; Mirchandani, P.; Vachani, R.** *Modeling and solving the two-facility
    capacitated network loading problem.* Operations Research 43(1), 1995. *Cut-set inequalities.*
    Já listado em `direcoes-pli-min-station.md` Apêndice B.
16. **Geoffrion, A. M.** *Lagrangean relaxation for integer programming.* Math. Prog. Study 2, 1974.
    Já listado em `direcoes-pli-min-station.md` Apêndice B.

As referências 14–16 constam do Apêndice B de `direcoes-pli-min-station.md` com a marca "a
conferir". Esta análise não as verificou contra o original; usa-as apenas para nomear o análogo.

---

## 2. Verificações de literatura (LC-1 a LC-5)

Busca dirigida, limitada pelas afirmações que o projeto pretende manter. Não é revisão
sistemática. Cada linha registra o conjunto verificado e se a condição de parada foi atingida.

| ID | Pergunta | Conjunto verificado | Resultado | Condição de parada |
|---|---|---|---|---|
| LC-1 | Alguém formulou este problema, ou variante próxima, como PLI? | Das 2025 (CALDAM/DAM, leitura integral do preprint); IJCAI-26 (leitura integral; p.73: "To our knowledge, CHARGING STATION PLACEMENT is not studied elsewhere"); Pereira & Ravelo 2026; Storandt & Funke 2013; Agarwal et al. 2016; Kundu & Saha 2018 e 2023; Castro-Gama & Hassink-Mulder 2023; busca dirigida "charging station placement unlabeled robots origins destinations integer programming" | **Nenhuma PLI para o MIN-STATION de Das encontrada.** A PLI mais próxima é a de Castro-Gama & Hassink-Mulder (cobertura por distância, sem S/T nem bijeção), que o próprio artigo da SBPO já cita como problema distinto. Kundu & Saha usam SMT para outro problema de cobertura. | **Atingida:** conjunto esgotado e registrado. A afirmação "primeira PLI" fica **limitada a este conjunto**; não é afirmação sobre toda a literatura. |
| LC-2 | A reformulação de cobertura sobre conjuntos de corte mínimo já existe para este problema ou isomorfo? | `direcoes-pli-min-station.md` §4, §6.2 (o próprio projeto a identifica como análoga à *cut-set inequality* e como Benders combinatório); IJCAI Teorema 8 (p.77), que constrói internamente uma instância de SET COVER para posicionar estações no conjunto independente de uma cobertura por vértices; Agarwal et al. 2016 (hitting set sobre caminhos mínimos, outro problema) | **Nenhuma formulação idêntica encontrada.** O mecanismo é clássico: projeção de viabilidade de fluxo sobre as variáveis de projeto gera cortes de viabilidade (Benders); o arredondamento CG de `Σ κ y ≥ δ` para `y(Z) ≥ 1` é a *cut-set inequality*; a família `𝒵` como cobertura exata é o corte de Benders combinatório de Codato–Fischetti aplicado a um subproblema de viabilidade. O que é específico do projeto é a identificação de `𝒵` e de `δ` (deficiência de Hall) para o MIN-STATION com papéis de terminal. | **Atingida pelo qualificador:** o análogo mais próximo é citado. O Teorema 6 do projeto deve ser apresentado como `DIRECT CONSEQUENCE` de max-flow/min-cut em `N(y)`, não como resultado novo em teoria de poliedros. |
| LC-3 | Existe benchmark público para este problema? | Das 2025 (nenhum experimento); IJCAI-26 (nenhum experimento, nenhum dado); Pereira & Ravelo 2026 (teórico); Kundu & Saha 2018/2023 (mapas internos para outro problema); Castro-Gama & Hassink-Mulder 2023 (redes hídricas para outro problema) | **Nenhum benchmark do MIN-STATION encontrado.** As instâncias existentes na literatura próxima são de outros problemas. | **Registrada.** A afirmação de `benchmark-v1.md` §1 ("Não existe benchmark publicado específico do problema") fica mantida **com este escopo explícito**. |
| LC-4 | Datas de publicação do LVIII SBPO e do IJCAI-26 | Registro oficial do IJCAI (`ijcai.org/proceedings/2026/9`, BibTeX `month = {8}`); site do LVIII SBPO (evento 28/09–01/10/2026; versão final 17/08/2026; anais "em até 90 dias") | **IJCAI-26 publicado em agosto de 2026. Anais do LVIII SBPO ainda não publicados em 2026-10-03.** O artigo da SBPO foi submetido até 11/05/2026 e aprovado em 20/07/2026 (datas do edital), antes da publicação do IJCAI. | **Atingida.** Prioridade de publicação: IJCAI-26. Independência do desenvolvimento: plausível pelas datas de submissão, mas **não demonstrável por registro público**; registrar como "desenvolvimento independente, publicação posterior". A questão só importa onde há sobreposição de conteúdo — ver §4, linha `G^r`. |
| LC-5 | Das 2025 contém `G^r`, matching ou algo que o projeto atribui ao IJCAI? | `min-station-das.pdf`, leitura integral das 16 páginas | **Não.** Das contém: definição (Problem 1, p.2); robôs não rotulados, recarga simultânea, definição de terminal (p.3); NP-dificuldade por 3,3-SAT com grau ≤ 6 (Lema 1, Teorema 1, pp.4–6); caminhos em O(n) (Lemas 2–4, Algoritmo 1, Teorema 2, pp.6–11); ciclos em O(n²) (Lema 5, Algoritmo 2, Teorema 3, pp.11–13); questões abertas sobre árvores, grades, planares e FPT (p.14). **Não contém** `G^r`, verificação polinomial, matching, pertinência a NP nem PLI. A permanência aparece na prova do Lema 5 (p.11: "every robot is starting from a target position"; p.12: "The robot starting at `s_i` remains at `s_i` occupying the target `t_o`"). | **Atingida.** Atribuições corretas: `G^r` e matching → IJCAI; permanência → Das (Lema 5) e IJCAI (definição de caminhada com `ℓ = 1`, p.73; `u_w`/`v_w` em `H`, p.75). |

**Consequência para a tabela de pré-condições da spec:** os itens 6, 9, 10 e 11 passam de
`UNRESOLVED` para "resolvido com escopo" (6 e 10), "resolvido por qualificador" (9) e "resolvido"
(11). Nenhum deles vira `NEW` sem qualificação.

---

## 3. T22.1 — Definições, atributo por atributo

Uma linha por atributo, uma coluna por fonte. Cada célula cita onde a fonte afirma o valor. "Ext.
ponderada" e "Ext. dirigida" são as classes `extensao_ponderada` e `extensao_dirigida` de
`instances/manifest.csv` (TNTP), e nunca entram em afirmação sobre o problema de Das.

| Atributo | Das (original) | IJCAI-26 | Formulação base atual (variante U) | SBPO (formulação base publicada) | Ext. ponderada | Ext. dirigida |
|---|---|---|---|---|---|---|
| Tipo de grafo | Simples, conexo, não dirigido (Problem 1, p.2; p.2 "we assume that G is a simple connected undirected graph") | Não dirigido; conexidade assumida sem perda (p.73 definição; p.75 §2.2) | Simples, não dirigido, conexo (`base-formulation.md` §2) | Simples, não dirigido, conexo, com função de comprimento `ℓ: E → R>0` (SBPO p.3 §2.1) | Não dirigido com pesos de aresta (`benchmark-v1.md` §5; TNTP) | Dirigido (TNTP; `manifest.csv` classe `extensao_dirigida`) |
| Direcionalidade | Não dirigido | Não dirigido | Não dirigido; `A_r` é dirigido por construção, mas simétrico quando `d` é simétrica (`base-formulation.md` §3) | Não dirigido (p.3) | Não dirigido | **Dirigido** — fora do problema de Das |
| Pesos / métrica | Passos: "A robot takes one step by moving from one vertex to an adjacent vertex" (p.2); distância = número de arestas | Comprimento de caminhada = número de arestas: "the length of each sub-walk `P_i` is at most `r`" (p.73); `N_r(v)` por `dist` (p.74) | Passos para aderência estrita; pesos = extensão (`base-formulation.md` §2, §10.2; `open-questions.md` Q2) | **Comprimentos reais** `ℓ(e) > 0`, `r ∈ R>0` (p.3) | Pesos reais | Pesos reais |
| Semântica da autonomia | `r` passos entre recargas; bateria cheia na origem e em cada estação (p.2) | `(C,r)`-walk: sub-caminhadas de comprimento `≤ r` que se emendam em vértices de `C` (p.73, itens 1–3) | Arco `(u,v) ∈ A_r` ⇔ `d(u,v) ≤ r`; recarga em vértice de `C` (`base-formulation.md` §3; `validacao-formulacao-base.md` §5.0) | Igual, com `d` ponderada (p.4 §3.1) | Igual, `d` ponderada | Igual, `d` ponderada e assimétrica |
| Onde estações podem ser instaladas | `C ⊆ V`, qualquer vértice (Problem 1, p.2) | `C ⊆ V` (p.73) | Todo `V` (`base-formulation.md` §4) | **Só `V_I = V ∖ (S ∪ T)`** (p.3 §2.1; p.4: `y_v`, `v ∈ V_I`) | Todo `V` (mesma formulação base) | Todo `V` |
| Objetivo | Minimizar `|C|` (p.2) | Minimizar `|C|`; versão de decisão com orçamento `c` (p.73) | `min Σ_{v∈V} y_v` (`base-formulation.md` §5) | `min Σ_{v∈V_I} y_v` (eq. (1), p.4); a formulação **estendida** usa custos `c_v` (p.6) | Cardinalidade | Cardinalidade |
| Número de agentes | `m`, com `|S| = |T| = m` (p.2) | `k`, com `|S| = |T| = k` (p.73) | `m` (`base-formulation.md` §2) | `m` (p.3) | `m` | `m` |
| Anonimato | "the robots are unlabeled ... there is no fixed matching" (p.3) | "anonymous version ... the final agent–terminal matching is not restricted" (p.73 §1.2) | Fluxo agregado; bijeção implícita na decomposição (`validacao-formulacao-base.md` §5.1 item 3) | Fluxo agregado na base (p.4); a estendida tem `p_{s,t}` e elegibilidade `e_{s,t}` (p.6) — variante | Igual à base | Igual à base |
| `S` | `S ⊂ V`, posições iniciais (p.2) | `S ⊆ V` (p.73) | `S ⊆ V` | `S ⊂ V` (p.3) | idem | idem |
| `T` | `T ⊂ V`, posições-alvo; cada alvo ocupado por exatamente um robô (p.2) | `T ⊆ V`; "each target position in `T` can be occupied with exactly one robot" (p.73) | `T ⊆ V` | `T ⊂ V` (p.3) | idem | idem |
| `S ∩ T` | **Permitido.** Sem cláusula de disjunção (p.2); a prova do Lema 5 usa "every robot is starting from a target position" (p.11) | **Permitido e tratado:** `H` cria `u_w` e `v_w` para `w ∈ S ∩ T` "because we may have optimal solutions that do not match `s` with `t`, even if `s = t`" (p.75) | Permitido; balanço unificado (`base-formulation.md` §6; `open-questions.md` Q1) | **Disjunto por construção das instâncias** ("garantindo que fossem disjuntos", p.7 §4.1); a formulação com balanços separados (2)–(5) é inviável se `S ∩ T ≠ ∅` (`validacao-formulacao-base.md` §5.4) | 5 instâncias `principal` com `S ∩ T ≠ ∅` no manifesto (`base-formulation.md` §10.1); TNTP tem `S ∩ T = ∅` | idem |
| Permanência (robô fica no próprio alvo) | Admitida: prova do Lema 5, p.12 ("remains at `s_i` occupying the target `t_o`") | Admitida pela definição: uma caminhada é uma sequência `v_1..v_ℓ` com `ℓ ∈ N`, logo `ℓ = 1` é uma `(C,r)`-walk de comprimento 0 (p.73) | Admitida: arco de permanência em `N(y)` e caminho `σ → v_out → v_in → τ` (`validacao-formulacao-base.md` §5.5.1, §5.5.3) | Não se aplica (S ∩ T = ∅ nas instâncias; a formulação não admite) | Não se aplica | Não se aplica |
| Recarga simultânea em uma estação | Permitida explicitamente: "multiple robots may arrive at one vertex simultaneously, allowing them to recharge concurrently" (p.3) | Sem restrição de tempo ou capacidade: "We do not consider any timing limitations" (p.73 §1.2); as `(C,r)`-walks são independentes por par | Sem capacidade (`min-station-domain.md` §6) | Sem capacidade | idem | idem |
| Emparelhamento final restrito? | Não (p.3) | Não (p.73) | Não | Base: não. Estendida: sim, por `e_{s,t}` (p.6) — variante | Não | Não |
| Bateria cheia na partida / destino sem estação | Sim (p.2: "from either its starting position or a charging station"); destino não precisa de estação (implícito na definição) | Sim: `P_1` parte de `s` com comprimento `≤ r`; nenhuma exigência de `t ∈ C` (p.73) | Sim: unidades livres `a_v`, `b_v` nas ativações (`base-formulation.md` §7–8) | Sim: "pontos de recarga a partida do robô, quaisquer vértices em `C` visitados e o destino" (p.3) | idem | idem |
| Rotas e pareamento como entrada? | Não (p.3: "neither the target position for a specific robot nor its path are given") | Não | Não | Não | Não | Não |

**Leituras obrigatórias desta tabela.**

1. **O problema do IJCAI-26 é literalmente o MIN-STATION de Das e o problema da formulação base
   atual.** Todos os atributos coincidem; a única diferença é notacional (`k`/`m`; versão de decisão
   com `c`). Todo teorema do IJCAI-26 aplica-se ao baseline do projeto.
2. **A formulação base publicada na SBPO modela uma variante**, por dois atributos: estações só em
   `V ∖ (S ∪ T)` e métrica ponderada. Nenhum teorema do IJCAI-26 ou de Das se transfere
   automaticamente a ela sem reexame (por exemplo, com estações proibidas em terminais, a
   redução do Teorema 3 do IJCAI continua válida porque `w_F ∉ S ∪ T`, mas a do Teorema 4 exige
   estações em `u_i` e `v_j`, que não são terminais, logo também continua; isso foi conferido só
   nesses dois casos e não é afirmação geral).
3. **Entre a formulação base atual e Das não há diferença de atributo.** A antiga hipótese
   `S ∩ T = ∅` (H1 de `validacao-formulacao-base.md` §5) foi removida pela variante U; a §5.5 prova
   a equivalência sem ela. Nenhum resultado publicado deixa de se aplicar.
4. **As extensões ponderada e dirigida diferem de Das em métrica (ambas) e em direcionalidade
   (dirigida).** Resultados E0–E8, obtidos em TNTP, são resultados sobre a extensão. Os Teoremas
   2–10 do IJCAI não se aplicam a elas sem reexame. Este documento não mistura esses resultados em
   nenhuma afirmação sobre o problema de Das.

---

## 4. T22.2 — Matriz de sobreposição

Colunas: tema; Das original; IJCAI-26; projeto; relação; novidade sustentável; evidência.

| Tema | Das (original) | IJCAI-26 | Projeto | Relação | Novidade sustentável | Evidência |
|---|---|---|---|---|---|---|
| Definição do problema | Problem 1 (p.2) | CHARGING STATION PLACEMENT (p.73) | Formulação base = mesmo problema (§3 acima) | `SAME` | Nenhuma | §3 desta análise |
| `G^r` / dígrafo de alcance | Ausente | Definição de `G^r` (p.74); **Proposição 1** (p.75): `(G,S,T,r,c)` sim-instância ⇔ `(G^r,S,T,1,c)` sim-instância | `A_r = {(u,v): u ≠ v, d(u,v) ≤ r}` (`base-formulation.md` §3; SBPO p.4); Lema 5.0 "A_r ⇔ caminhadas" (`validacao-formulacao-base.md` §5.0) | `SAME` | **Nenhuma.** O dígrafo de alcance é `G^r` orientado nos dois sentidos. O Lema 5.0 do projeto é a Proposição 1 mais as Observações 1–2 do IJCAI (p.75). A SBPO usou a construção como dispositivo de modelagem antes da publicação do IJCAI (LC-4), sem enunciá-la como proposição; registrar "uso independente, publicação posterior", nunca prioridade | IJCAI pp.74–75; `validacao-formulacao-base.md` §5.0 |
| Verificação de viabilidade por matching | Ausente | Dígrafo `D`, **Lema 1**, bipartido `H`, **Lema 2**, **Teorema 1** (polinomial, devolve bijeção e caminhadas), **Corolário 1** (NP), **Corolário 2** (`n^{O(c)}`) — p.75 | Teorema 1 de `direcoes-pli-min-station.md` §1.1 (`C` viável ⇔ `B_C` tem emparelhamento perfeito); Prop. 3.1 §3.2 (busca em `A_r` só por `C` + Hopcroft–Karp; ou um max-flow em `N(y)`); `is_valid_cut` (`cuts.py:673`), `integer_oracle` (`cuts.py:765`), `independent_validator.viavel` (`independent_validator.py:126`) | `SAME` (teorema) / `IMPLEMENTATION` (código) | **Nenhuma como teoria.** O projeto tem três implementações de uma caracterização publicada, uma delas corrigida para permanência (T1) e uma por estados `(v, bateria)` (T2). Isso é T3/T5 | IJCAI p.75; `direcoes` §1.1, §3.2; commits `dc83ac9`, `658099a`, `e0c36e7` |
| Hall | Ausente | Não enuncia Hall; usa emparelhamento perfeito em `H` (Lema 2, p.75) | Deficiência `δ(X)` de um corte finito (`direcoes` §4) e "condição de Hall em `B_C`" (Teorema 4, §3.2); C4 por Dulmage–Mendelsohn (§5.4) | `DIRECT CONSEQUENCE` | **Nenhuma como teoria** (Hall é clássico; Lema 2 + Hall dá a deficiência). O **uso** de `δ` como lado direito de cortes é do projeto (ver §4.1) | `direcoes` §3.2, §4, §5.4 |
| Set Cover | Ausente | **Teorema 3** (p.76): redução *de* SET COVER, `r = 1`, split/bipartido, W[2]-difícil em `c`; "preserves the objective value exactly"; **Corolário 3**: sem `(1−ε) ln k`-aproximação | **Teorema 6** (`direcoes` §4): MIN-STATION ≡ set covering *sobre* a família implícita `𝒵`; Teorema 7 (CG posto 1); Corolário 7.1 (`LP_cov ≥ z_LP`); família SC-GF2 instancia a redução do Teorema 3 | **Sentidos opostos.** IJCAI: redução *de* Set Cover para dureza. Projeto: reformulação *em* cobertura para limites. Teorema 6: `DIRECT CONSEQUENCE` (de max-flow/min-cut em `N(y)`); SC-GF2: `IMPLEMENTATION` | O Teorema 6 **não é** o Teorema 3 nem seu recíproco formal: um reduz a instância de Set Cover a uma instância do problema; o outro reduz qualquer instância do problema a um set covering exponencial e implícito. Nenhum deve ser apresentado como o outro. A ligação "a dureza vem de cobertura e o melhor limite do projeto vem de cobertura" é **interpretativa** até existir prova (ver §9) | IJCAI p.76; `direcoes` §4, §6.2; LC-2 |
| Bin Packing | Ausente | **Teorema 4** (p.76): redução de UNARY BIN PACKING; `m` caixas `v_j` com `B` folhas-destino; itens `u_i` com `e_i` folhas-origem; aresta `l^i_{e_i+j} v_j`; `(G,S,T,1,2n+m)` sim ⇔ empacotamento existe; "forces any feasible `C` to include `{u_i} ∪ {v_j}` and exactly one vertex from `{l^i_{e_i+1},…,l^i_{e_i+m}}`" | Gerador BP (`experiments/structural/bp.py`); `familias-estruturais.md` §BP: limite `2n+q` com `q` caixas; conectores `c_{i,j}` no lugar das folhas `l^i_{e_i+j}` | `ADAPTATION` | **Nenhuma como construção.** `2n+q` do projeto é `2n+m` do artigo. `familias-estruturais.md` atribui o argumento "ao parecer"; o parecer (§11, l.510, l.541) atribui ao Teorema 4, p.76. A cadeia deve apontar para o artigo. BP foi `DESCARTAR` em T20 | IJCAI p.76; `familias-estruturais.md` §BP; parecer l.510–566; `decisao-fase-p.md` §BP |
| NP-dificuldade | **Teorema 1** (p.6): NP-difícil com grau máximo ≤ 6, redução de 3,3-SAT (Lema 1, pp.4–6) | **Teorema 2** (p.75): NP-difícil com `r = 1` em planar bipartido `Δ = 6`; `r = 1` bipartido `Δ = 4`; `r = 3` planar bipartido `Δ = 3` (de VERTEX COVER, provas omitidas). Pertinência a NP: Corolário 1 (p.75) | Nenhum construto; cita Das (`RESEARCH.md` §2; `direcoes` §1.2) | `—` | Citar Das e IJCAI. Observação: o Teorema 1 do projeto (`direcoes` §1.1) também implica pertinência a NP, mas é posterior ao IJCAI em publicação e não foi enunciado como tal | IJCAI p.75; Das pp.4–6 |
| Aproximação | Ausente | **Teorema 10** (p.78): `k`-aproximação em `O(√k k⁴ + k³n + km)`; **Corolário 3** (p.76): inaproximável em `(1−ε) ln k` | Não implementada. Parecer §7: construção primal "opcional e condicionada"; prova substituta da desigualdade (ver §4.3 erratum 2). O projeto usa limites por distância do mesmo tipo: `L_bot` (atribuição gargalo) e `⌈D_s/r⌉ − 1` por robô via C2 (`direcoes` §0, §2.2, §5.2) | `—` (algoritmo) / `DIRECT CONSEQUENCE` (limite por distância) | Nenhuma. O limite `⌈dist/r⌉ − 1` é o mesmo argumento no IJCAI (p.78), em Das (Lema 2, p.7, para caminhos) e no C2 do projeto. Fator `k = m` (até 1142 no projeto) é vazio na prática (parecer §6) | IJCAI pp.76, 78; Das p.7; `direcoes` §5.2 |
| FPT em `k` | Questão aberta (Q2, p.14) | **Teorema 6** (p.77): `k^{O(k)} n^{O(1)}`, via "connecting forest" (Lema 3) e WEIGHTED STEINER TREE; rodapé 1: a floresta pode compartilhar vértices | Nunca tocado (`backlog-continuacao.md` "Fora do backlog ativo"; parecer §9 "Condicionar") | `—` | Nenhuma. Não há construto do projeto. Nota do parecer §6: o esboço com `S_i ∩ T_i` pede esclarecimento | IJCAI p.77; backlog l.820 |
| Vertex cover | Ausente | **Teorema 8** (p.77): `2^{2vc²+vc} n^{O(1)}`; constrói SET COVER com universo `W ⊆ X × X` | Nunca tocado | `—` | Nenhuma. Registro: é o análogo mais próximo, dentro do artigo, de um modelo de cobertura para posicionar estações (LC-2) | IJCAI p.77 |
| Modular-width | Ausente | **Teorema 7** (p.77): `2^{mw} n^{O(1)}`; Lema 4: um ótimo com ≤ 1 estação por módulo | Nunca tocado. B2 (simetria em hipercubos) encerrada em E5 por outro caminho (`direcoes` §13 B2) | `—` | Nenhuma. Parecer §6: "a existência de um ótimo estruturado não é desigualdade válida" | IJCAI p.77; `direcoes` §13 |
| `dts` / `dtc` | Ausente | **Teorema 4** (p.76): W[1]-difícil por `dts + r` e `dtc + r`, mesmo `r = 1` | Só indiretamente, via BP (que tem `dts ≤ q` por construção) | `—` | Nenhuma | IJCAI p.76 |
| `fvs` | Ausente | **Teorema 5** (pp.76–77): W[1]-difícil por `fvs + c`; sem `n^{o(fvs+c)}` sob ETH; de `(k,r)`-CENTER | Nunca tocado. `benchmark-v1.md` §2 usa PACE 2018 para controlar largura de árvore de `G`, com a ressalva (parecer §5) de que a largura de `G` não é a de `G^r` | `—` | Nenhuma | IJCAI pp.76–77; `benchmark-v1.md` §2 |
| Árvores | Questão aberta (Q1, p.14) | **Teorema 9** (p.78): polinomial para EXT-CHARGING STATION PLACEMENT (estações pré-instaladas) em árvores, por regra de redução e Teorema 1 | Nunca implementado. Backlog: "até o parâmetro justificar"; parecer §9: só depois de validar com `r > 1` e `S ∩ T` | `—` | Nenhuma | IJCAI p.78; backlog l.820; parecer §9 |
| Caminhos | **Teorema 2** (p.11): `O(n)` (Lemas 2–4, Algoritmo 1) | Cita Das (p.73) | Nenhum construto | `—` | Nenhuma. Pereira & Ravelo 2026 (mesmo grupo) estendem a grafos-aranha em `O(n)`; não está registrado no repositório | Das pp.6–11; ref. 4 |
| Ciclos | **Teorema 3** (p.13): `O(n²)` (Lema 5, Algoritmo 2) | Cita Das (p.73) | Nenhum construto; o projeto cita o Lema 5 pela permanência | `—` | Nenhuma | Das pp.11–13 |
| Formulação de PLI | Ausente (leitura integral) | Ausente (leitura integral); nenhuma referência a PLI na bibliografia (pp.79–80) | SBPO: PLI de fluxo na variante `V_I` (pp.4–5). Base atual: PLI all-V, variante U (`base-formulation.md` §4–7; `baseline.py`) | `NEW FORMULATION` (qualificada) | **Primeira PLI do MIN-STATION no conjunto verificado em LC-1.** A derivação é rotineira (ver §5, veredito 1). O valor principal é servir de baseline reprodutível e de objeto da análise de relaxação | LC-1; SBPO pp.4–5; `base-formulation.md` |
| Formulação de fluxo | Ausente | Ausente | Fluxo agregado de uma commodity, custo fixo nos nós, sobre `A_r`; `direcoes` §1.3 tabela: "É a estrutura exata da base: fluxo único, e `y_v` libera capacidade `m` = demanda total" | `ADAPTATION` | **A formulação é a tradução direta de um modelo padrão de fluxo com projeto nos nós para `G^r`.** O projeto já diz isso em `direcoes` §1.3. O que não é tradução direta: unidades livres de terminal (`a_v`, `b_v`), balanço unificado e exatidão da agregação porque o pareamento é livre (§1.3, linha 1, última coluna) | `direcoes` §1.3, §2.1 |
| `S ∩ T` | Permitido (Lema 5) | Tratado em `H` (`u_w`, `v_w`, p.75); **lacuna na construção literal de `D`** (ver §4.3) | Balanço unificado (variante U); oráculo corrigido (T1); validador independente (T2); regressão (T3); prova §5.5 (T5) | `IMPLEMENTATION` (semântica exigida pelo problema) | **Nenhuma como semântica:** Das já permite e o IJCAI já desdobra `u_w`/`v_w`. O que é do projeto: (i) a correção do próprio modelo e do próprio oráculo (T5/T3, não contribuição); (ii) a **observação verificada** sobre a construção `D` (§4.3), que é pequena e não refuta teorema | `validacao-formulacao-base.md` §5.4–5.5; `revalidacao-oraculo-pos-t1.md`; `regressao-terminais-t3.md`; IJCAI p.75 |
| Permanência | Prova do Lema 5 (pp.11–12) | Caminhada de comprimento 0 (p.73); `u_w`/`v_w` (p.75) | Arco de permanência `v_out → v_in` em `N(y)` (`validacao-formulacao-base.md` §5.5.1); `verify_t1_oracle_sT.py` (618 conjuntos `C`, 0 divergências) | `IMPLEMENTATION` | Nenhuma como semântica. A rede com arco de permanência é um dispositivo de implementação da equivalência | `validacao-formulacao-base.md` §5.5; commit `dc83ac9` |
| Núcleo de cobertura (IP em `y` com C1+C2+C4) | Ausente | Ausente | Teoremas 5–7 e Corolário 7.1 (`direcoes` §4); IP do núcleo como mecanismo de LB (E3, E9, E12, piloto, fase E) | `ADAPTATION` (teoria) + `EXPERIMENTAL VALIDATION` (medição) | **Como teoria:** `DIRECT CONSEQUENCE` de min-cut em `N(y)`, análogo exato da *cut-set inequality* e do Benders combinatório (LC-2) — `QUALIFY`. **Como mecanismo computacional medido:** sustentável — em PUC/PUCN dá LB maior que o COMP (E9, E12, pré-protocolo / Das, margens ±1) e em SC-GF2 `k ∈ {8,9}` prova `OPT = k` na raiz enquanto base e COMP param no `WorkLimit` (fase E, conforme protocolo, 3 sementes) — `KEEP` como T3 + T4 | `direcoes` §4, §13 A1; `resultados-e12-pli.md`; `fase-e-sc.md`; LC-2 |
| C1 | Argumento de Das no Lema 2 (p.7) é a versão em caminhos | Argumento usado na prova do Teorema 4 (p.76: "forces any feasible `C` to include `u_i`, `v_j`") | §5.1 de `direcoes`: primeiro/último salto; "caso particular do Teorema 6" | `DIRECT CONSEQUENCE` | Nenhuma como desigualdade. O uso a priori em `A_r` e sua medição são do projeto (T3) | `direcoes` §5.1; `cuts.py:96` |
| C2 | Lema 2 (p.7): `⌊|x − s_1|/r⌋` estações necessárias no intervalo | Mesmo argumento no Teorema 10 (p.78): `⌈dist/r⌉ − 1` | §5.2: bandas de distância; prova por desigualdade triangular, válida para métrica ponderada | `DIRECT CONSEQUENCE` | Nenhuma como desigualdade. A forma em bandas sobre métrica geral e a separação por janelas são do projeto (T3) | `direcoes` §5.2; `cuts.py:116` |
| C3 | Ausente | Ausente | §5.3: corte de nós por robô; "exatamente a projeção do modelo multicommodity por origem sem a restrição de atribuição"; separação por max-flow com capacidade `y*` nos nós | `ADAPTATION` (desigualdades de corte de nós de conectividade) | Nenhuma como desigualdade: é o corte de conectividade por nós de Menger. Medido em E2–E4 (pré-protocolo / extensão, `cc10-2p`: 237,7 s de LP parado, parecer §7) | `direcoes` §5.3; `resultados-e2-e4-pli.md` |
| C4 (Hall de primeiro salto, versão DM) | Ausente | Lema 2 (matching) é a base; Hall não enunciado | §5.4: RHS 1 por Hall nos arcos diretos; geração a priori por Dulmage–Mendelsohn; divergência corrigida em `correcao-c4-dm.md` | `DIRECT CONSEQUENCE` (desigualdade) / `ADAPTATION` (geração por DM) | Nenhuma como desigualdade (Hall). A geração a priori por DM e a correção para `S ∩ T` são do projeto (T2/T3). Fecha F2 com exatidão (provado, `direcoes` §2.4) | `direcoes` §5.4; `correcao-c4-dm.md`; `cuts.py:203` |
| C5 (família completa `𝒵`, separação inteira por max-flow) | Ausente | Ausente | §5.5: separação inteira exata; "Benders combinatório ≡ branch-and-cut na reformulação de set covering" (§6.2) | `ADAPTATION` (Benders combinatório, Codato–Fischetti) | Nenhuma como técnica. Pausada (`backlog` "Fora do backlog ativo": C5) | `direcoes` §5.5, §6.2 |
| C6 (Prop. 5.4.2, mochila de Hall de primeiro salto) | Ausente | Ausente | `c6-hall-primeiro-salto.md`: `Σ_{v∈N⁺(S')} min(δ, |N⁻(v) ∩ S'|) y_v ≥ δ`; derivada antes da medição; validada para RHS `δ ≥ 2` por `corte_ponderado_valido`; medida em HB: LB entre 1 e 2 contra OPT 2–3 | `NEW INEQUALITY` (qualificada) + `NEGATIVE RESULT` | **Desigualdade específica ao problema, não encontrada no conjunto verificado.** O padrão (cobertura com coeficientes truncados em `δ`) é clássico em desigualdades de cobertura por mochila. Efeito medido: não fecha o gap de HB (previsto antes da medição); não é o mecanismo que fecha SC-GF2 (`decisao-fase-p.md`). `QUALIFY` como T1 menor; `NEGATIVE RESULT` como T4 | `c6-hall-primeiro-salto.md`; `verify_t14_c6.py`; `decisao-fase-p.md` |
| CBI (mestre inteiro iterado com cortes `𝒵`) | Ausente | Ausente | `yspace.py`, `bc_yspace.py`; E7 (confundido), E8 (extensão), E12 (A2 encerrada para Das); T16 não aplicável | `EXPERIMENTAL VALIDATION` → `NEGATIVE RESULT` | Nenhuma como método. Linha investigada com veredito negativo pré-registrado: 1 vitória contra COMP em 7 grafos, 0 contra o núcleo (E12, 3 sementes, TL 600 s) | `resultados-e12-pli.md` §3; `decisao-t16-cbi.md` |
| Benchmark | Nenhum | Nenhum (sem experimento) | benchmark-v1: 70 instâncias fiéis a Das derivadas de SteinLib, DIMACS, PACE 2018, MovingAI MAPF e OSMnx; 5 legadas; 75 `principal`; regras de transformação nomeadas; `grupos_origem.csv`, `duplicata_de`; 31 D/A | `—` (artefato) | **Sustentável como T4 + T5, com escopo de LC-3.** As técnicas de conversão não são novas; o conjunto, a proveniência, a partição por grafo de origem e o protocolo de dificuldade são do projeto | `benchmark-v1.md`; `instances/manifest.csv`; LC-3 |
| Famílias estruturais | Ausente | Teoremas 3 e 4 fornecem os gadgets de SC e BP | BP (`ADAPTATION` do Teorema 4), SC-GF2 (`IMPLEMENTATION` do Teorema 3 com sistema GF(2)), HB (construção própria, derivada de F2 de `direcoes` §2.4), TR (construção própria) | `ADAPTATION` / `IMPLEMENTATION` (BP, SC); `EXPERIMENTAL VALIDATION` (HB, TR) | Nenhuma como construção para BP e SC. HB e TR são construções do projeto sem reivindicação teórica. Valor sustentável: **uso experimental** com critérios pré-registrados (T19–T21) | `familias-estruturais.md`; `piloto-fase-p.md`; `decisao-fase-p.md` |
| Resultados experimentais | Nenhum | Nenhum | E0–E14; piloto; fase E | `EXPERIMENTAL VALIDATION` / `NEGATIVE RESULT` | Ver §6 (tabela de contribuições) e §9 (narrativa). Cada afirmação carrega o grau de protocolo | `resultados-e*-pli.md`; `decisao-fase-p.md`; `fase-e-sc.md` |

### 4.1 Tabela de cortes por família

| Família | Desigualdade | Origem matemática | Literatura prévia / análogo | Derivação no projeto | Novidade | Status experimental |
|---|---|---|---|---|---|---|
| C1 | `Σ_{v∈N⁺(s)} y_v ≥ 1` se `N⁺(s) ∩ T = ∅` (e simétrico em `T`) | Toda rota com ≥ 2 saltos tem interior em `C` | Argumento de Das (Lema 2, p.7) e do IJCAI (Teorema 4, p.76) | "Caso particular do Teorema 6" (`direcoes` §5.1) | Nenhuma como desigualdade | Medido E2–E14, piloto, fase E; componente do COMP e do núcleo |
| C2 | `Σ_{a<d(s,v)≤a+r} y_v ≥ 1` para `a + r < D_s` | Desigualdade triangular; uma estação em cada banda de largura `r` | Das Lema 2 (caminhos); IJCAI Teorema 10 (`⌈dist/r⌉ − 1`) | Prova própria para métrica geral (`direcoes` §5.2) | Nenhuma como desigualdade; forma em bandas sobre métrica ponderada é do projeto | Idem C1 |
| C3 | `y(Z) ≥ 1` para `Z` separador de `s` até `T` em `A_r` | Menger / corte de nós | Cortes de conectividade de Steiner com custo nos nós; "projeção do multicommodity sem atribuição" (`direcoes` §5.3) | Caso particular do Teorema 6 | Nenhuma | E2–E4 (extensão); LP parado em `cc10-2p` |
| C4 / C4-DM | `Σ_{v∈N⁺(S')} y_v ≥ 1` se `|N⁺(S') ∩ T| < |S'|` | Hall nos arcos diretos | Hall; Dulmage–Mendelsohn | `direcoes` §5.4; correção em `correcao-c4-dm.md` | Nenhuma como desigualdade; geração a priori por DM é do projeto | Componente do COMP; fecha F2 |
| C5 | `y(Z) ≥ 1` para `Z ∈ 𝒵`, separação por max-flow em `N(ȳ)` | Min-cut em `N(y)`; Teorema 6 | Benders combinatório (Codato–Fischetti 2006); *cut-set inequality* | `direcoes` §5.5, §6.2 | Nenhuma como técnica | Pausada; usada no CBI e BC-y (negativo) |
| C6 (Prop. 5.4.2) | `Σ_{v∈N⁺(S')} min(δ, |N⁻(v) ∩ S'|) y_v ≥ δ`, `δ ≥ 2` | Hall com multiplicidade; capacidade de primeira parada | Padrão de cobertura por mochila com coeficientes truncados | `c6-hall-primeiro-salto.md` (derivação, condições, contraexemplos) | Específica ao problema; não encontrada; `QUALIFY` | Validade confirmada; LB 1–2 contra OPT 2–3 em HB; não fecha SC-GF2 (`decisao-fase-p.md`) |
| C7, C8, §5.6 "C6 esboço" | Posto ≥ 2; desigualdades em `f`; Hall multi-salto com multiplicidade | — | — | Esboços em `direcoes` §5.6–5.8 | Não implementados; nenhuma afirmação | Nenhum |

Edge case aplicado: todo corte que é consequência imediata de Hall ou de cobertura foi classificado
`DIRECT CONSEQUENCE`. O Teorema 6 do projeto deriva C1, C3, C4 e C5 como casos particulares ou
como a família inteira; esta tabela registra a derivação em vez de reivindicar desigualdades
independentes.

### 4.2 Classes especiais e parâmetros do IJCAI-26: o que o projeto fez

| Resultado IJCAI | Onde | Projeto |
|---|---|---|
| Árvores em P (Teorema 9) | p.78 | **Nunca tocado.** Backlog "Fora do backlog ativo"; parecer §9 condiciona a validar com `r > 1` e `S ∩ T`. PACE 2018 entra no benchmark por largura de árvore de `G`, não por `G^r` |
| Caminhos `O(n)`, ciclos `O(n²)` (Das Teoremas 2–3) | Das pp.11, 13 | **Nunca tocado.** Nenhuma instância do benchmark é caminho ou ciclo puro |
| FPT em `k` (Teorema 6) | p.77 | **Nunca tocado.** `m` no benchmark vai de 5 a 1142; o parâmetro não é pequeno nas instâncias difíceis |
| Modular-width (Teorema 7) | p.77 | **Nunca tocado.** B2 (simetria de hipercubos) foi encerrada em E5 sem usar módulos |
| Vertex cover (Teorema 8) | p.77 | **Nunca tocado** |
| `dts`, `dtc` (Teorema 4) | p.76 | **Indiretamente**, pela família BP (`dts ≤ q`). Nenhuma medição do parâmetro |
| `fvs` (Teorema 5) | pp.76–77 | **Nunca tocado** |
| `k`-aproximação (Teorema 10) | p.78 | **Pausado.** Parecer §7: construção primal opcional, "sem evidência de benefício"; não implementada |
| Inaproximabilidade `ln k` (Corolário 3) | p.76 | **Nunca usado.** É o elo interpretativo com o núcleo de cobertura (§9) |

### 4.3 Errata verificadas no artigo IJCAI-26

Ambas foram re-derivadas do texto do artigo nesta análise. Nenhuma refuta teorema. Ambas devem ser
registradas como observações verificadas sobre a literatura, com o artefato que as reproduz, e não
como contribuição de destaque.

**Erratum 1 — a construção literal de `D` admite relé sem estação em `S ∩ T ∖ C`.**

- *Texto (p.75):* "The vertex set of `D` is `S ∪ T ∪ C`. ... For any vertex `u ∈ S ∪ C` we add the
  arcs `uv` in `A(D)` if and only if `v ∈ N_r(u) ∩ (T ∪ C)`."
- *Mecanismo:* um vértice intermediário `v` de um caminho dirigido em `D` precisa de arco de
  entrada, logo `v ∈ T ∪ C`, e de arco de saída, logo `v ∈ S ∪ C`. Se `v ∉ C`, então `v ∈ S ∩ T`.
  Portanto a falha é confinada a `S ∩ T ∖ C`: um terminal que é origem e alvo, sem estação, passa a
  servir de relé. Isso é mais preciso do que o parecer §2.2, que fala em "`S ∩ T`" em geral.
- *Instância que reproduz:* `SharedTerminal` (`experiments/cuts/synthetic.py`): estrela com centro
  `v` e folhas `p1..p4`, `r = 1`, `S = {v, p1, p2}`, `T = {v, p3, p4}`. `D` literal tem o caminho
  `p1 → v → p3` com `C = ∅`; `H` então tem emparelhamento perfeito `{p1→p3, p2→p4, v→v}` e o Lema
  2, lido literalmente, declara `C = ∅` viável. O modelo base prova `OPT = 1`, `C = {v}`. A
  regressão `verify_t3_regressao_terminais.py` cobre o caso.
- *Alcance:* lacuna de especificação em uma construção usada dentro da prova do Teorema 1. A
  caracterização por emparelhamento (Lema 2) continua correta quando as arestas de `H`
  representam `(C,r)`-walks genuínas. Corolários 1–2 e Teoremas 2–10 não dependem da construção
  literal de `D`. Correção óbvia: arcos saem de `S ∪ C` e entram em `T ∪ C`, mas um vértice só pode
  ser **interior** de um caminho em `D` se estiver em `C` — ou, equivalentemente, usar a rede com
  papéis separados e arco de permanência da §5.5.1 de `validacao-formulacao-base.md`.

**Erratum 2 — o esboço do Teorema 10 inverte uma desigualdade.**

- *Texto (p.78):* "Since the length of any `(C*,r)`-walk between `s*` and `f(s*)` is at most
  `dist(s*,f(s*))`, at least `⌈dist(s*,f(s*))/r⌉ − 1` vertices must belong to `C*`."
- *Correção:* o comprimento de qualquer caminhada é **pelo menos** a distância. Com isso a
  conclusão segue: uma caminhada de comprimento `≥ dist` decomposta em sub-caminhadas de
  comprimento `≤ r` tem pelo menos `⌈dist/r⌉ − 1` pontos de emenda, todos em `C*`.
- *Alcance:* inversão de nível tipográfico; a conclusão e o fator `k` sobrevivem. O parecer §6
  registra a prova substituta `q ≤ OPT ≤ |C| ≤ kq`, conferida.

---

## 5. T22.3 — A contribuição em PLI, em quatro eixos separados

Fato de base, verificado por leitura integral: nem Das 2025 nem IJCAI-26 contêm formulação de PLI,
solver ou experimento; a bibliografia do IJCAI (pp.79–80) não cita trabalho de PLI sobre o
problema; LC-1 não encontrou PLI em nenhum dos trabalhos próximos. Isso torna a lacuna real **no
conjunto verificado**. Não torna a PLI do projeto forte por si só. Os quatro vereditos abaixo são
independentes e podem ser contestados separadamente.

### Veredito 1 — Formulação

- **O que é.** Fluxo agregado de uma commodity sobre `A_r = G^r`, com capacidade `m·y_v` nos nós
  (custo fixo nos nós), balanço `out − in = a_v − b_v` e unidades livres nos terminais.
- **Proximidade com o modelo padrão.** `direcoes-pli-min-station.md` §1.3 já classifica: "É a
  estrutura exata da base: fluxo único, e `y_v` libera capacidade `m` = demanda total". É a
  tradução direta de um modelo de projeto de rede de custo fixo nos nós para `G^r`. O edge case da
  spec se aplica: **a formulação é uma tradução direta e isto deve ser dito.**
- **Dificuldade de derivação.** Baixa a moderada. Os passos não triviais são três e todos são de
  semântica, não de modelagem de fluxo: (i) permitir `y` em todo `V` com unidades livres `a_v`,
  `b_v` para que terminal sem estação emita/receba só a própria unidade; (ii) balanço unificado para
  `S ∩ T`; (iii) perceber que a agregação é **exata** (e não uma relaxação de multicommodity)
  porque o pareamento é livre — `direcoes` §1.3 linha 1 e §1.6 "Vantagem da agregação".
- **O que a ausência de PLI concorrente não autoriza.** Não autoriza inferir força. A força
  computacional é julgada no Veredito 4; a força de relaxação é fraca por um fator até `m`
  (Teorema 2 e §2 de `direcoes`, provados e medidos).
- **Veredito:** `QUALIFY`. Categoria T1 (menor) + T3. Afirmação defensável: "primeira formulação de
  PLI registrada para o MIN-STATION de Das no conjunto verificado em LC-1; formulação compacta de
  fluxo agregado sobre `G^r`, de derivação rotineira, com tratamento correto de terminais e prova
  de equivalência; relaxação fraca por fator até `m`, caracterizada exatamente". Não afirmar
  "formulação forte" nem "formulação nova em sentido estrutural".

### Veredito 2 — Semântica de `S ∩ T` e permanência

- **O que o problema exige.** Das permite `S ∩ T ≠ ∅` e usa a permanência na prova do Lema 5
  (pp.11–12). O IJCAI desdobra `u_w`/`v_w` em `H` por esse motivo (p.75). A semântica é **exigida
  pelo problema**, não inventada pelo projeto.
- **Parte que só corrige o próprio modelo.** A formulação com balanços separados era inviável para
  `v ∈ S ∩ T` (P1, `validacao-formulacao-base.md` §5.4); o oráculo em `cuts.py` rejeitava
  instalações viáveis (parecer §2.1; T1). Corrigir isso é correção de software e de modelo (T5/T3).
  Não é contribuição; é pré-requisito.
- **Parte voltada à literatura.** O Erratum 1 (§4.3): a construção literal de `D` do IJCAI falha
  exatamente onde o oráculo do projeto falhava, com sinal oposto. É uma observação verificada e
  reproduzida, confinada a `S ∩ T ∖ C`, que não toca teorema. Cabe como nota de rodapé ou parágrafo
  de uma seção de verificação, com a instância `SharedTerminal` como testemunho.
- **Veredito:** `QUALIFY`. A afirmação defensável é "a PLI trata `S ∩ T` e permanência de forma
  provadamente correta (§5.5), com oráculo, validador independente e regressão; a construção `D`
  do IJCAI-26, lida literalmente, admite relé sem estação em `S ∩ T ∖ C`, caso que o projeto
  reproduz". Não afirmar que o projeto "descobriu" a semântica de `S ∩ T`.

### Veredito 3 — Prova de equivalência (`validacao-formulacao-base.md` §5.5)

- **Conteúdo.** Rede `N(y)` com arco de permanência; decomposição de fluxo inteiro em `m`
  caminhos e ciclos (Ahuja–Magnanti–Orlin, Thm. 3.5); bijeção pela saturação dos arcos terminais;
  invariante de bateria por arco de `A_r`; ciclos só por `y = 1`; balanço e ativação em cinco
  classes de vértice; TU para `f` contínuo; teorema final sem hipótese sobre `S ∩ T`.
- **Além da verificação rotineira?** Em parte. A estrutura (decomposição, bijeção, invariante) é
  rotineira para formulações de fluxo. O que não é rotineiro é o **arco de permanência** e a
  análise por classes, que é exatamente onde a formulação anterior e o oráculo falharam. A prova
  também entrega, como subproduto, o Teorema 3 e a Proposição 3.1 de `direcoes` (viabilidade com
  `y` fixo por um max-flow), que coincidem com o Teorema 1 do IJCAI.
- **Veredito:** `QUALIFY`. Categoria T1 (menor). É a evidência que sustenta "a PLI modela
  fielmente o problema de Das", e deve ser citada como tal, não como teorema de destaque. Não há
  afirmação de novidade além de "equivalência provada, inclusive para `S ∩ T`".

### Veredito 4 — Avaliação computacional

Graduada pelo protocolo do Bloco 2.

| Afirmação computacional | Experimento | Grau | O que demonstra | O que não demonstra |
|---|---|---|---|---|
| A relaxação da base é fraca por fator próximo de `m` | E0–E1 (TNTP, PUC), `direcoes` §2, §12 | pré-protocolo / extensão e Das; **mais prova** (Teorema 2) | Raiz 1,0 em `hc9u`–`hc12p` contra LB 31–149; o Teorema 2 explica | — |
| Cortes de cobertura a priori (C1+C2+C4-DM) elevam o LB | E2–E4 (TNTP, PUC), E9 | pré-protocolo | `hc9u`: LP com C1 ≥ 256/9 (provado); núcleo = 32 em 2,1 s (E3) | Não fecha `hc9u` (`OPT ∈ [32, 38]` em aberto, `direcoes` §13 B2) |
| O núcleo em `y` dá LB maior que o COMP em PUC/PUCN | E9 (TL 60 s × 600 s), E12 (3 sementes, TL 600 s) | pré-protocolo / Das; E12 com 3 sementes e mesmo TL, mas antes de T6/T7 | 6 instâncias PUC/PUCN com LB do núcleo acima do COMP por 1–2; em MAPF/Vienna ocorre o contrário | Margens de ±1 sob não-determinismo (corrigido só em T6); não decide método geral |
| CBI não supera núcleo nem COMP | E12 | pré-protocolo / Das, 3 sementes | A2 encerrada para Das por critério pré-registrado | Nada sobre a extensão (E8 em TNTP é extensão) |
| SC-GF2: núcleo prova `OPT = k` na raiz; base e COMP param no orçamento | Piloto (k 5–7), fase E (k 8–9, 3 sementes de solver) | **conforme protocolo** | O fenômeno reproduz em duas escalas acima do piloto e em três sementes | O gêmeo rígido não entrou na fase E (set cover não provou em 90 s); a leitura de simetria ficou sem avaliação |
| BP, HB: descartadas | Piloto | **conforme protocolo** | BP: lado "sim" não é o lado duro de UB; HB: todo método prova em < 1 s | Nada sobre instâncias maiores de BP (q = 8 lado "não" fica em gap) |
| C6 não fecha HB | T14 | **conforme protocolo**, previsão registrada antes | LB 1–2 contra OPT 2–3 | Nada sobre outras famílias |
| Desagregação all-V: LP melhor, custo `O(m·|A_r|)` | T18 | diagnóstico, sem comparação de método | `z_LP` sobe (1 → 1,5 em Tri; 0,333 → 1,375 em HB q=4) e não fecha | Nenhuma conclusão de desempenho |
| Dificuldade acompanha `UB/m`, não o tamanho | `benchmark-v1.md` §6 | pré-protocolo / Das, 1 semente | Correlação observada nas 75 principais | Não é causa; não foi repetido com 3 sementes |
| E13: incumbente melhora com mais tempo sob `MIPFocus=1` | E13 | pré-protocolo; **dois fatores confundidos** (`protocolo-comparacao-pareada.md` §Retrospectiva) | Efeito conjunto | Não atribui o residual a LB ou UB |
| E14: 0/4 com `OPT = UB_melhor` em 14 400 s | E14 | pré-protocolo / Das | O gatilho do E11 não disparou | Nada sobre as instâncias de gap 30–44 % |

**Veredito:** `KEEP` como T3 + T4, com cada afirmação carregando seu grau. A única afirmação
positiva de método **conforme protocolo** é a de SC-GF2 (núcleo × base × COMP). As afirmações de
E9/E12 são coerentes com ela, mas pré-protocolo. Nenhuma afirmação de que algum método "resolve" as
31 instâncias D/A do benchmark pode ser feita.

---

## 6. T22.4 — Tabela de contribuições (candidatos A–I e adicionais)

Cada candidato recebe exatamente uma categoria principal e um status. "Parte do projeto" diz o que
sobra depois de retirar o que é literatura.

| Cand. | Contribuição candidata | Categoria | Literatura prévia | Evidência do projeto | Parte do projeto | Status |
|---|---|---|---|---|---|---|
| A | PLI compacta all-V (variante U) | T1 (menor) + T3 | Nenhuma PLI no conjunto LC-1; modelo de fluxo com projeto nos nós é padrão; `G^r` é IJCAI Prop. 1 | `base-formulation.md`; `baseline.py`; §5.5; E0–E14 | Unidades livres de terminal; balanço unificado; exatidão da agregação; prova | `QUALIFY` |
| B | Semântica `S ∩ T` e permanência | T5 (correção) + observação sobre a literatura | Das Lema 5; IJCAI `u_w`/`v_w` | T1–T5 do Bloco 1; Erratum 1 | Correção do próprio modelo e oráculo; o erratum confinado a `S ∩ T ∖ C` | `QUALIFY` |
| C1 | Cortes C1, C2 | T3 | Argumentos de Das (Lema 2) e IJCAI (Teoremas 4, 10) | `direcoes` §5.1–5.2 | Uso a priori sobre `A_r` e medição | `REMOVE` como T1; `ENGINEERING ONLY` como componentes do COMP |
| C2 | Corte C3 | T3 | Cortes de conectividade por nós | `direcoes` §5.3; E2–E4 | Separação por max-flow com `y*` nos nós | `REMOVE` como T1; `EXPERIMENTAL ONLY` (extensão) |
| C3 | C4 / C4-DM | T2 + T3 | Hall; Dulmage–Mendelsohn | `direcoes` §5.4; `correcao-c4-dm.md`; fecha F2 | Geração a priori por DM com `S ∖ T` do lado da origem; correção para `S ∩ T` | `QUALIFY` |
| C4 | C5 / família `𝒵` | T2 | Benders combinatório; cut-set | `direcoes` §5.5, §6.2 | Separação inteira exata e minimalização de `Z` | `EXPERIMENTAL ONLY` (pausada) |
| C5 | C6 (Prop. 5.4.2) | T1 (menor) + T4 | Padrão de cobertura por mochila; não encontrada para este problema | `c6-hall-primeiro-salto.md`; `verify_t14_c6.py` | Desigualdade, validador para RHS `δ ≥ 2`, previsão registrada e medição negativa | `QUALIFY` |
| D | Núcleo inteiro de cobertura como mecanismo de LB; Teoremas 5–7 | T3 + T4 (mecanismo); T1 (menor) para os teoremas | Projeção de fluxo / cut-set / Benders combinatório (LC-2); IJCAI Teorema 8 usa Set Cover internamente | E3, E9, E12 (pré-protocolo); fase E de SC (conforme protocolo) | Identificação de `𝒵` e `δ` para este problema; o IP do núcleo como método; a medição | `KEEP` (T3 + T4); teoremas `QUALIFY` |
| E | CBI | T4 | Benders combinatório iterado | E7, E8, E12; `decisao-t16-cbi.md` | A bateria e o veredito negativo pré-registrado | `EXPERIMENTAL ONLY` (negativo) |
| F | Benchmark-v1 e manifesto | T4 + T5 | Nenhum benchmark do problema (LC-3); fontes SteinLib, DIMACS, PACE, MovingAI, OSMnx | `benchmark-v1.md`; `manifest.csv`; `grupos_origem.csv`; `build_benchmark.py` | Conjunto, proveniência, regras nomeadas, partição por origem, protocolo de dificuldade | `KEEP` |
| G | Estudo de dificuldade | T4 | Nenhum | `benchmark-v1.md` §6; E9–E14; piloto | Observação "dificuldade acompanha `UB/m`" e regimes R-a/R-b/R-c | `KEEP`, graduado: pré-protocolo salvo piloto/fase E |
| H | Famílias estruturais BP, SC, HB, TR | T4 | BP = IJCAI Teorema 4; SC = IJCAI Teorema 3 | `familias-estruturais.md`; piloto; fase E | HB e TR como construções; critérios pré-registrados; uso experimental de BP e SC | `EXPERIMENTAL ONLY` |
| I | Resultados negativos | T4 | — | Ver tabela abaixo | Pergunta, protocolo e veredito registrados | `KEEP` |
| J | Diagnóstico da relaxação: Teorema 2 (`z_LP` = fluxo de custo mínimo com custo `1/m`), famílias F1/F2/Tri, Teorema 8 (Benders clássico `= z_LP`), L1 `≤ z_LP` | T1 (menor) | Geoffrion (L1); análise de LP de fluxo único é clássica | `direcoes` §2, §6.2, §7 | A análise específica do problema e os contraexemplos | `QUALIFY` |
| K | Desagregação all-V | T3 (diagnóstico) | Multicommodity por origem é padrão | `desagregacao-por-origem.md` | Medição do ganho de LP e do custo | `EXPERIMENTAL ONLY` (negativo quanto a custo) |
| L | Instrumentação, determinismo, orçamento por `WorkLimit`, protocolo pareado | T5 | Prática padrão | Bloco 2 | — | `ENGINEERING ONLY` |
| M | Dígrafo de alcance; verificação por matching; BP e SC como construções | — | IJCAI Prop. 1, Lemas 1–2, Teoremas 1, 3, 4 | — | Nenhuma | `REMOVE` (nunca apresentar como contribuição) |

**O que foi removido.** M inteiro; C1 e C2 como teoria; qualquer leitura de T18 como formulação
competitiva; a afirmação da SBPO sem qualificação (ver §7). Se nada fosse removido, a auditoria
seria suspeita; aqui foram removidas quatro classes de afirmação.

### 6.1 Resultados negativos como contribuição T4

| Resultado negativo | Pergunta | Protocolo | Veredito | Fonte |
|---|---|---|---|---|
| CBI não supera núcleo nem COMP em PUC/PUCN | A iteração de cortes `𝒵` acrescenta LB além do núcleo? | pré-protocolo / Das; 3 sementes; mesmo TL; critério pré-registrado | A2 encerrada para Das | `resultados-e12-pli.md` §3 |
| Lagrangeana L1 fica `≤ z_LP` | Dualizar ativações dá bound melhor? | pré-protocolo / extensão e Das; **mais prova** (Geoffrion) | Descartada (D-1) | `direcoes` §7, §12, §13 |
| Benders clássico `= z_LP` | Cortes de min-cut sem arredondamento melhoram o bound? | prova (Teorema 8) | Descartado (D-2) | `direcoes` §6.2 |
| BC-y genérico não supera COMP | Branch-and-cut só em `y` é melhor? | E7 confundido (3 confundidores); E8 extensão | Suspenso; A2 depois encerrada | `direcoes` §13 A2; `resultados-e7-pli.md` §5.1 |
| BP descartada | Os lados "sim"/"não" são duros em sentidos opostos? | **conforme protocolo** | `DESCARTAR`: lado "sim" não é duro de UB | `decisao-fase-p.md` |
| HB descartada | C6 fecha o gap de primeiro salto? | **conforme protocolo** | `DESCARTAR`: todo método prova em < 1 s | `decisao-fase-p.md` |
| C6 não fecha HB | O coeficiente `δ` no destino compartilhado deixa o gap aberto? | **conforme protocolo**, previsão antes da medição | Confirmado: LB 1–2 contra OPT 2–3 | `c6-hall-primeiro-salto.md` |
| Desagregação all-V não justifica `O(m·|A_r|)` | O ganho de LP paga o custo? | diagnóstico pré-registrado | Não; sem expansão | `desagregacao-por-origem.md` |
| B2 (simetria em hipercubos) | A dificuldade de `hc*` é simetria? | pré-protocolo / Das | Não: 0 gêmeos por C1; `Symmetry=2` empata; gap está no acoplamento | `direcoes` §13 B2 |
| Construção primal / MIP start não move o LB | Incumbente melhor ajuda? | pré-protocolo | Não move LB (E10b); poda não medida | parecer §7 |
| TR validada, não medida | — | — | Sem afirmação experimental | `decisao-t16-cbi.md` |

---

## 7. T22.5 — Auditoria de afirmações e lista de correções

Convenção: **nenhum documento científico foi editado durante a fase de análise** (verificação por
`git status` em §11). A lista abaixo é executável por quem não fez a análise. A coluna "Aplicar em"
separa os três documentos de posicionamento que a spec manda corrigir nesta tarefa (`RESEARCH.md`,
`docs/project-overview.md`, `source-map.md`) dos documentos cuja edição fica para passo posterior.

### 7.1 Afirmações a corrigir

| # | Arquivo | Afirmação atual | Problema | Evidência | Afirmação recomendada | Status | Aplicar em |
|---|---|---|---|---|---|---|---|
| 1 | `artigo-sbpo.pdf`, resumo (p.1, PT e EN) | "O problema é recente, NP-difícil em grafos gerais e ainda não tratado por meio de Programação Linear Inteira (PLI)" / "has not yet been addressed through Integer Linear Programming (ILP)" | (a) Nenhuma busca registrada sustenta o "ainda não"; (b) a formulação da SBPO modela a variante `V ∖ (S ∪ T)` com métrica ponderada, não o problema de Das | LC-1; §3 desta análise | Em qualquer texto futuro: "Até onde a busca registrada em `overlap-ijcai2026-min-station.md` §2 alcança, não há formulação de PLI para o MIN-STATION de Das; a formulação apresentada na SBPO modela uma variante com estações restritas a `V ∖ (S ∪ T)` e métrica ponderada." O PDF publicado não é editável; a qualificação vale para o artigo seguinte e para os documentos do repositório | `QUALIFY` | Texto futuro; registro aqui |
| 2 | `artigo-sbpo.pdf`, introdução (p.2) | "Entretanto, ainda não foram exploradas formulações em PLI para resolver o MIN-STATION." | Mesmo problema de #1; a própria introdução cita a PLI de Castro-Gama & Hassink-Mulder para problema relacionado, o que já é a distinção correta | LC-1 | Manter a distinção com Castro-Gama & Hassink-Mulder e acrescentar o escopo da busca | `QUALIFY` | Texto futuro |
| 3 | `RESEARCH.md` §7 "Fontes principais" | Lista Das, SBPO e formulação base | Omite o IJCAI-26, que é o trabalho prévio mais próximo e resolve questões que o projeto tratava como abertas (`G^r`, verificação por matching, NP) | §4 | Acrescentar o IJCAI-26 como fonte principal com seu papel: "complexidade clássica e parametrizada, verificação polinomial por `G^r` e matching, aproximação; sem PLI nem experimentos" | `KEEP` + adicionar | **Esta tarefa** |
| 4 | `RESEARCH.md` §2 | "A referência conceitual é o MIN-STATION definido por Das" | Correto, mas sem registro de que o IJCAI-26 define o mesmo problema | §3 | Acrescentar uma frase: "O IJCAI-26 estuda o mesmo problema sob o nome CHARGING STATION PLACEMENT, com `k = m`" | `QUALIFY` | **Esta tarefa** |
| 5 | `docs/project-overview.md` §1 e §7 | Fontes: Das, SBPO, all-vertices; árvore de arquivos lista três PDFs | Omite o IJCAI-26 e o PDF `novo_artigo_das_2026.pdf` já presente no repositório | §4; `ls docs/technical/reference` | Acrescentar o artigo em §7 e o PDF na árvore de §4 | `KEEP` + adicionar | **Esta tarefa** |
| 6 | `docs/technical/reference/source-map.md` | Três fontes numeradas; §6 "Quais resultados teóricos originais são conhecidos? → Artigo de Das" | Omite o IJCAI-26; é o arquivo que `CLAUDE.md` designa para comparar artigos | §4 | Acrescentar a fonte 4 (IJCAI-26) com "Papel na pesquisa" e "Limite da fonte"; acrescentar linha na tabela de precedência para complexidade parametrizada/NP/FPT → IJCAI; apontar para este documento como fonte da sobreposição. A inserção renumera as seções seguintes (precedência passa de §6 para §7); nenhum outro arquivo referenciava esses números | `KEEP` + adicionar | **Esta tarefa** |
| 7 | `docs/context-ai/base-formulation.md` §3 | Define `A_r` sem referência | É `G^r` do IJCAI (Prop. 1, p.75) | §4 linha `G^r` | Nota: "`(V, A_r)` é o grafo `G^r` do IJCAI-26 (p.74), orientado; a equivalência `(G,r) ↔ (G^r,1)` é a Proposição 1 (p.75)" | `QUALIFY` | Passo posterior |
| 8 | `docs/context-ai/base-formulation.md` §6 | "Das não exige `S` e `T` disjuntos ... prova do Lema 5" | Correto e incompleto: o IJCAI também trata o caso (`u_w`/`v_w`, p.75) | §3 linha `S ∩ T` | Acrescentar a referência ao IJCAI p.75 e registrar que a semântica é exigida pelo problema | `QUALIFY` | Passo posterior |
| 9 | `docs/context-ai/base-formulation.md` §9 | "Esse ponto deve aparecer na demonstração de correção da formulação, não apenas ser assumido pela implementação." | A demonstração existe (`validacao-formulacao-base.md` §5.5, commit `97b290d`) | T5 | Trocar por: "Demonstrado em `validacao-formulacao-base.md` §5.5, inclusive para `S ∩ T`" | `KEEP` (atualizar) | Passo posterior |
| 10 | `docs/technical/reference/direcoes-pli-min-station.md` §1.1 Teorema 1 | "`C` viável ⇔ `B_C` tem emparelhamento perfeito" apresentado como `[Provado]` do documento | É o Lema 2 do IJCAI (p.75), publicado antes | §4 linha matching | Manter a prova e acrescentar: "Coincide com o Lema 2 de Das et al. (IJCAI-26, p.75)" | `QUALIFY` | Passo posterior |
| 11 | `direcoes-pli-min-station.md` §3.2 Prop. 3.1 | Viabilidade com `y` fixo por max-flow ou busca + Hopcroft–Karp | É o Teorema 1 do IJCAI (p.75) | §4 | Acrescentar a referência | `QUALIFY` | Passo posterior |
| 12 | `direcoes-pli-min-station.md` §4 Teorema 6 | "formulação exata só em `y` ... um set covering" | Falta a nota de que corre em sentido oposto ao Teorema 3 do IJCAI e a classificação como consequência direta de min-cut (o qualificador *cut-set* já está no Teorema 7) | §4 linha Set Cover; LC-2 | Acrescentar: "Não confundir com a redução de Set Cover do IJCAI-26 (Teorema 3, p.76), que corre no sentido inverso. O teorema é consequência direta de max-flow/min-cut em `N(y)` e corresponde ao corte de Benders combinatório (§6.2)" | `QUALIFY` | Passo posterior |
| 13 | `direcoes-pli-min-station.md` §1.2 "Complexidade" | "NP-difícil em grafos gerais (Das)" | Omite IJCAI Teoremas 2–5 e Corolário 1 (pertinência a NP) | §4 | Acrescentar os resultados do IJCAI com página | `QUALIFY` | Passo posterior |
| 14 | `direcoes-pli-min-station.md` Apêndice B | Lista de referências sem o IJCAI-26 | — | §1 | Acrescentar refs. 1, 4, 9 desta análise | adicionar | Passo posterior |
| 15 | `docs/technical/reference/familias-estruturais.md` §BP | "Este argumento é o do parecer" | A cadeia de atribuição deve apontar para IJCAI Teorema 4, p.76 (`2n + m`); o parecer (l.510, l.541) já aponta | §4 linha Bin Packing | "Este é o argumento da prova do Teorema 4 de Das et al. (IJCAI-26, p.76), com `q` no lugar de `m`" | `QUALIFY` | Passo posterior |
| 16 | `familias-estruturais.md` §SC-GF2 | Descreve a construção sem citar a redução | Instancia o Teorema 3 do IJCAI (p.76) com sistema GF(2) | §4 | Acrescentar: "Instancia a redução de Set Cover do Teorema 3 (IJCAI-26, p.76) com o sistema de hiperplanos de GF(2)^k" | `QUALIFY` | Passo posterior |
| 17 | `docs/context-ai/min-station-domain.md` §1, §9 | Definição sem IJCAI; §9 cita só Das para `S ∩ T` | — | §3 | Acrescentar o IJCAI-26 em §1 (mesmo problema) e em §9 (`u_w`/`v_w`) | `QUALIFY` | Passo posterior |
| 18 | `docs/technical/README.md` "Papel das principais referências" e árvore | Omite o IJCAI-26 e o PDF | — | §4 | Acrescentar item e arquivo | adicionar | Passo posterior |
| 19 | `docs/technical/reference/benchmark-v1.md` §1 | "Não existe benchmark publicado específico do problema: Das é teórico e os trabalhos próximos não publicam dados." | Verdadeiro no conjunto verificado; sem escopo registrado | LC-3 | Acrescentar "(verificado em `overlap-ijcai2026-min-station.md` §2, LC-3)" | `QUALIFY` | Passo posterior |
| 20 | `docs/technical/reference/MIN-STATION-parecer-macro-consolidado.md` §6 | "Pendência de posicionamento (Em aberto)" | Superada por este documento | — | Acrescentar ponteiro: "Fechada em `overlap-ijcai2026-min-station.md`". O parecer é histórico; só o ponteiro | `KEEP` (ponteiro) | Passo posterior |
| 21 | `docs/technical/plans/backlog-continuacao.md` T22 | Status `A FAZER`; critérios não citam Set Cover nem Bin Packing | Inconsistência 4 da spec | §4 | Status `CONCLUÍDA` com ponteiro; acrescentar aos critérios a comparação de Set Cover e Bin Packing e a verificação LC-1 | atualizar | **Esta tarefa** (histórico de tarefas) |
| 22 | `backlog-continuacao.md` T22, critério "A narrativa do artigo é reorganizada em torno de cobertura × compatibilidade coletiva" | Pede reorganização de narrativa | Fora do escopo de T22 segundo a spec ("Writing the paper ... Out of Scope"); a ligação cobertura–dureza fica interpretativa (§9) | spec §Out of Scope | Marcar o critério como "subsidiado por §9 do overlap; redação do artigo é tarefa separada" | `QUALIFY` | **Esta tarefa** |

### 7.2 Documentos verificados e já corretos quanto ao IJCAI-26

| Arquivo | O que foi verificado | Resultado |
|---|---|---|
| `MIN-STATION-parecer-macro-consolidado.md` §6 | Referência completa, `k = m`, "mesmo problema", tabela por resultado com página (Prop. 1 p.75; Lemas 1–2 e Teo. 1 p.75; Teo. 3 p.76; Teos. 2 e 4 pp.75–76; Lema 3 e Teo. 6 p.77; Lema 4 e Teos. 7–8 p.77; Teo. 9 p.78; Teo. 10 p.78) | **Correto.** Todas as páginas conferem com o PDF. A ressalva de §2.2 sobre `D` é correta, mas menos precisa que §4.3 (confinada a `S ∩ T ∖ C`). Não alterar além do ponteiro #20 |
| `MIN-STATION-parecer-macro-consolidado.md` §11 (BP, SC) | Atribuição de BP ao Teorema 4 (l.510) e de SC ao Teorema 3 (l.588), "artigo p.76" (l.541, l.605) | **Correto** |
| `backlog-continuacao.md` l.30 | "Documentação/literatura: Das, SBPO, parecer, artigo IJCAI 2026" | **Correto**, mas T22 estava `A FAZER` (#21) |
| `specs/bloco1-corretude-terminais-sT/spec.md`, `specs/bloco3-pesquisa-instancias-estruturais/spec.md` | Citam o artigo com página | **Correto**; não são documentos científicos |
| `validacao-formulacao-base.md` | Não cita o IJCAI; a prova é autocontida e cita Das | **Aceitável**; a referência cruzada (#10–#11) vai em `direcoes` |

### 7.3 Varredura por palavras de novidade

`rg -n -i "inédit|pela primeira vez|primeiro a |unprecedented|\bnovel\b|\bfirst\b|primeira (formula|PLI)"`
em `docs/`, `RESEARCH.md` e `CLAUDE.md` (excluindo PDFs e este arquivo) devolve, em `ef1c0ec`:
uma frase de arquitetura (`code-guidelines.md` l.43), uma frase de verificação experimental
(`resultados-e2-e4-pli.md` l.320), o próprio critério de T22 (`backlog` l.801) e quatro afirmações
cronológicas internas ("a primeira formulação de PLI desenvolvida no projeto", `RESEARCH.md` l.93;
`docs/technical/README.md` l.33; "primeira formulação base desenvolvida no projeto" e "primeira PLI
do projeto", `source-map.md` l.41 e l.121). Nenhuma afirmação de ineditismo frente à literatura foi
encontrada em Markdown. A exposição está na **ausência** do enquadramento IJCAI, não em adjetivo
inflado.

### 7.4 Observações fora do escopo de T22 (registradas, não corrigidas)

- `docs/technical/governance/open-questions.md` Q1 (l.28–30): "todas as 22 instâncias do
  repositório têm `|S ∩ T| = 0`" está desatualizado — o manifesto tem 5 instâncias `principal` com
  `S ∩ T ≠ ∅` (`base-formulation.md` §10.1). Não é posicionamento; fica para T11 ou tarefa de
  documentação.
- `direcoes-pli-min-station.md` cabeçalho: "é o caso de todas as instâncias do repositório"
  (`S ∩ T = ∅`) — idem.

### 7.5 Mapa de dependência científica

Para cada afirmação que o projeto pretende manter: em que ela se apoia.

| Afirmação | Prova | Experimento | Benchmark | Bloco 3 | Literatura |
|---|---|---|---|---|---|
| A PLI base modela fielmente o MIN-STATION de Das, inclusive `S ∩ T` | `validacao-formulacao-base.md` §5.5 | `verify_t1_oracle_sT.py`, `verify_t2_validador_independente.py`, `verify_t3_regressao_terminais.py` | — | — | Das Problem 1 e Lema 5; IJCAI p.73, p.75 |
| Não há PLI prévia para o problema (no conjunto verificado) | — | — | — | — | LC-1 (§2) |
| A relaxação da base erra por fator até `m` | `direcoes` Teorema 2, §2 | E0–E1 (pré-protocolo) | 75 principais (raiz) | — | — |
| MIN-STATION ≡ set covering sobre `𝒵`; `y(Z) ≥ 1` é CG posto 1; `LP_cov ≥ z_LP` | `direcoes` Teoremas 6–7, Cor. 7.1 | — | — | — | Qualificado por LC-2 (cut-set, Benders combinatório); sentido oposto ao IJCAI Teo. 3 |
| O núcleo de cobertura é um mecanismo de LB competitivo em PUC/PUCN | — | E3, E9, E12 (pré-protocolo / Das) | 31 D/A | — | — |
| Em SC-GF2 o núcleo prova `OPT = k` na raiz e base/COMP não | — | Fase E (conforme protocolo) | — | SC promovida (T20), fase E (T21) | Construção = IJCAI Teo. 3 |
| CBI não supera núcleo nem COMP para Das | — | E12 (pré-protocolo / Das, 3 sementes) | PUC/PUCN de avaliação | T16 não aplicável | — |
| C6 é válida (RHS `δ ≥ 2`) e não fecha HB | `c6-hall-primeiro-salto.md` (derivação) | T14 (conforme protocolo) | — | HB descartada | — |
| BP é instanciação do Teorema 4 e foi descartada | `familias-estruturais.md` (limite `2n+q`) | Piloto | — | T20 | IJCAI Teo. 4 p.76 |
| A desagregação all-V melhora o LP e não paga o custo | — | T18 (diagnóstico) | — | — | — |
| Existe um benchmark reprodutível do problema de Das com proveniência | — | `verify_lambda.py`, `verify_lote1a.py` | benchmark-v1 | — | LC-3 |
| A dificuldade acompanha `UB/m` e não o tamanho | — | `benchmark-v1.md` §6 (pré-protocolo, 1 semente) | 75 principais | — | — |
| A construção `D` do IJCAI, lida literalmente, admite relé em `S ∩ T ∖ C` | Derivação em §4.3 | `SharedTerminal`, `verify_t3_regressao_terminais.py` | — | — | IJCAI p.75 |
| O esboço do Teorema 10 inverte uma desigualdade; a conclusão sobrevive | Parecer §6 (prova substituta) | — | — | — | IJCAI p.78 |
| A ligação "dureza por Set Cover ↔ limite por cobertura" | **Nenhuma** | — | — | — | Interpretativa (§9) |

---

## 8. Inconsistências encontradas entre spec, backlog, parecer, literatura e código

Registradas, não reconciliadas.

1. **A spec afirma que "30 documentos técnicos já citam o artigo"; o repositório não confirma.**
   `rg -l "IJCAI|Hanaka|novo_artigo|Das et al"` em `docs/`, `specs/`, `RESEARCH.md` e `CLAUDE.md` em
   `ef1c0ec` devolve 5 arquivos: o parecer, o backlog e as três specs (Blocos 1, 3 e 4). Nenhum
   `resultados-e*-pli.md`, nenhum documento de evidência do Bloco 3 e nenhum documento de
   `context-ai/` cita o artigo. A lacuna é maior do que a spec descreve, e a lista de correções da
   §7.1 reflete isso.
2. **A spec afirma que `familias-estruturais.md` "já atribui a equivalência a 'artigo p.76'".**
   Não: o arquivo atribui "ao parecer" (§BP: "Este argumento é o do parecer"). Quem atribui ao
   artigo é o parecer (l.541). Corrigido na lista (#15).
3. **O parecer §2.2 descreve a falha de `D` como "com `S ∩ T`" em geral.** A derivação em §4.3
   confina a falha a `S ∩ T ∖ C`. O parecer está correto e menos preciso; este documento carrega a
   versão precisa.
4. **A spec não registra a PLI de Castro-Gama & Hassink-Mulder (2023)**, citada pela própria
   introdução do artigo da SBPO como PLI para problema relacionado. Ela é a PLI mais próxima
   encontrada em LC-1 e muda a forma correta de enunciar a lacuna: não "nenhuma PLI para
   posicionamento de estações de recarga", mas "nenhuma PLI para o MIN-STATION (com `S`, `T`,
   bijeção livre)".
5. **A spec não registra Pereira & Ravelo (ETC 2026)**, do mesmo grupo, sobre o MIN-STATION em
   grafos-aranha. Nenhum documento do repositório o cita.
6. **Os critérios de aceite de T22 no backlog pedem "reorganizar a narrativa do artigo"**, o que a
   spec coloca fora de escopo. A §9 fornece o subsídio; a redação fica para tarefa separada (#22).
7. **`open-questions.md` Q1 e o cabeçalho de `direcoes` dizem que todas as instâncias têm
   `S ∩ T = ∅`**; o manifesto tem cinco com `S ∩ T ≠ ∅`. Fora do escopo de T22 (§7.4).
8. **O IJCAI afirma que a pertinência a NP "was not previously known" (resumo, p.72).** O Teorema
   1 de `direcoes` §1.1 também implica pertinência a NP, mas foi escrito depois da publicação do
   IJCAI (agosto de 2026) e não enuncia a consequência. Não há questão de prioridade.
9. **O IJCAI (p.73) declara "To our knowledge, CHARGING STATION PLACEMENT is not studied
   elsewhere"**, sem citar o artigo da SBPO (anais não publicados em agosto de 2026) nem Pereira &
   Ravelo (julho de 2026). Coerente com as datas de LC-4.

---

## 9. T22.6 — Narrativa experimental do Bloco 3 como contribuição

Escrita só contra artefatos consolidados do Bloco 3 (`decisao-fase-p.md`, `fase-e-sc.md`,
`piloto-fase-p.md`, `familias-estruturais.md`, `c6-hall-primeiro-salto.md`,
`desagregacao-por-origem.md`, `decisao-t16-cbi.md`, CSVs em `results/structural/`). Nenhuma
afirmação abaixo é preenchida por suposição; o que não tem artefato está marcado `PENDING`.

| Linha | Classificação | Afirmação posicionada | Grau de protocolo | Artefato |
|---|---|---|---|---|
| SC-GF2 | `IMPLEMENTATION` da redução do Teorema 3 do IJCAI (p.76), usada como **instrumento experimental** | "Em instâncias que instanciam a redução de Set Cover de Das et al. com o sistema de hiperplanos de GF(2)^k (`OPT = k`, `|V| = 3(2^k − 1)`), o IP do núcleo de cobertura prova o ótimo na raiz em `k ∈ {5,…,9}`, enquanto a formulação base e a base com C1+C2+C4 param no orçamento de trabalho com limite entre 1 e 4, em três sementes de solver." A construção não é nova; o uso e a medição são do projeto | **conforme protocolo** (fase E: `WorkLimit = 297`, 3 sementes, sementes de geração 100–104 reservadas) | `fase-e-sc.csv` (24 linhas); `fase-e-sc.md`; `decisao-fase-p.md` §SC |
| SC gêmeo rígido | — | **`PENDING`:** a comparação de simetria em `k ∈ {8,9}` não foi avaliada porque o IP de set cover não certificou o ótimo do gêmeo em 90 s. Em `k = 7` (piloto) o COMP prova o GF2 e não prova o gêmeo; isso **não** se lê como efeito do grupo linear (`decisao-fase-p.md`) | piloto conforme protocolo; fase E sem célula | `piloto_fase_p.csv`; `fase-e-sc.md` |
| BP | `ADAPTATION` do gadget do Teorema 4 do IJCAI (p.76); **resultado negativo** | "A família que reproduz a redução de Bin Packing não separa métodos pelo critério pré-registrado: o lado 'sim' não é o lado duro de limite superior (incumbente em < 0,15 s, prova dentro do orçamento até `q = 8`); só o lado 'não' é duro de limite inferior, e C6 não altera o quadro." Descartada em T20 sem revisão de critério | **conforme protocolo** | `decisao-fase-p.md` §BP; `piloto_fase_p.csv` |
| HB | Construção própria (de F2, `direcoes` §2.4); **resultado negativo** | "Nos bolsões de Hall, os quatro métodos provam o ótimo previsto em < 1 s num nó, sem diferença de limite; C6 não fecha o gap de LP medido antes do piloto (LB 1–2 contra OPT 2–3) e o MIP não precisa dele." Descartada em T20 | **conforme protocolo** | `decisao-fase-p.md` §HB; `c6-hall-primeiro-salto.md` |
| TR | Construção própria; **sem afirmação experimental** | Validação do gerador e da contagem de ótimos do núcleo (`TR(2,5,2,∞)`: 8 ótimos, 2 viáveis; `TR(3,5,2,∞)`: 27, 3). Não entrou no piloto porque o método que ela discriminaria (CBI) ficou não aplicável | validação apenas | `decisao-t16-cbi.md`; `verify_t17_tr.py` |
| C6 | `NEW INEQUALITY` qualificada; **resultado negativo medido** | "A desigualdade de mochila de Hall de primeiro salto é válida (verificada para RHS `δ ≥ 2` por `corte_ponderado_valido` e pelo mínimo da soma ponderada no modelo base) e, conforme previsto antes da medição, não fecha o gap em HB nem é o mecanismo que fecha SC-GF2." | **conforme protocolo**, previsão registrada | `c6-hall-primeiro-salto.md`; `verify_t14_c6.py`; `decisao-fase-p.md` |
| Desagregação all-V | Diagnóstico; **resultado negativo quanto a custo** | "A desagregação por origem eleva `z_LP` (Tri 1 → 1,5; HB q=4 0,333 → 1,375; BP [3,1] 3 → 5; SC-GF2(3) 1 → 1,75) sem fechar o ótimo, iguala o LP com C1 em SC-GF2(3) e fica abaixo do núcleo em BP; o custo `O(m·|A_r|)` não se justifica." Nunca apresentar como formulação competitiva | diagnóstico pré-registrado | `desagregacao-por-origem.md`; `verify_t18_desagregacao.py` |
| CBI | **negativo**, fora do Bloco 3 | A2 encerrada em E12 (pré-protocolo / Das, 3 sementes); T16 não aplicável | pré-protocolo / Das | `resultados-e12-pli.md`; `decisao-t16-cbi.md` |

**Ligação estrutural a registrar — e seu limite.** O IJCAI prova a dureza (W[2] em `c`,
NP-dificuldade em split/bipartidos, inaproximabilidade em `(1 − ε) ln k`) por uma redução de SET
COVER que "preserva o objetivo exatamente" (Teorema 3, Corolário 3, p.76). O mecanismo de limite
mais forte medido no projeto é o núcleo de cobertura, que é a reformulação exata do problema em
set covering (Teorema 6) restrita às famílias C1+C2+C4. Nas instâncias que instanciam a redução
do Teorema 3, o núcleo prova o ótimo na raiz. **A teoria e a medição apontam para a mesma
estrutura.** Essa frase é **interpretativa**: não existe prova no repositório de que, na classe de
instâncias do Teorema 3, o LP do núcleo com C1 seja igual ao ótimo (em SC-GF2 ele não é: vale
`2 − 2^{1−k}` contra `OPT = k`, `familias-estruturais.md` §SC-GF2; quem prova é o IP do núcleo, não
seu LP). Até que uma proposição seja escrita e provada, a ligação deve ser apresentada como
observação, e não como teorema.

**O que não pode ser dito.** Que alguma família estrutural "revela a dificuldade do problema de
Das" (BP e HB foram descartadas; SC é uma instanciação de redução conhecida); que C6 é um corte
útil (medido negativo); que a desagregação é uma alternativa (custo não justificado); que o CBI é
competitivo (A2 encerrada).

---

## 10. Rastreabilidade com a spec (SCI-01 a SCI-40)

| Requisito | História | Onde está atendido |
|---|---|---|
| SCI-01 … SCI-06 | T22.1 | §3 (tabela de definições e leituras obrigatórias 1–4) |
| SCI-07 … SCI-13 | T22.2 | §4 (matriz), §4.1 (cortes), §4.2 (classes e parâmetros), §4.3 (errata) |
| SCI-14 … SCI-20 | T22.3 | §5 (quatro vereditos; tabela de grau de protocolo; T18 em Veredito 4) |
| SCI-21 … SCI-28 | T22.4 | §6 (tabela A–M), §6.1 (negativos), §7.1 #1–#2 (SBPO) |
| SCI-29 … SCI-34 | T22.5 | §1 (bibliografia), §7.1 (lista de correções), §7.2 (verificados), §7.5 (mapa de dependência), §11 (verificação de não edição) |
| SCI-35 … SCI-40 | T22.6 | §9 |

---

## 11. Verificação da fase de análise

Antes de qualquer edição em documento científico, `git status --short` em `ef1c0ec` devolvia uma
única linha (`?? specs/bloco4-posicionamento-cientifico/`). Este arquivo foi o primeiro artefato
criado. As edições autorizadas pela spec para esta tarefa (`RESEARCH.md`, `docs/project-overview.md`,
`source-map.md`, mais o registro de histórico em `backlog-continuacao.md`) foram feitas **depois**
deste documento e estão listadas em §7.1 com a marca "Esta tarefa" (itens #3–#6, #21, #22; todos
aplicados). As referências a linhas em §7.3 valem para `ef1c0ec`, antes dessas edições. Qualquer outro arquivo
modificado no mesmo working tree é desvio e deve ser revertido.
