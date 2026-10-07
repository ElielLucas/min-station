# MIN-STATION — parecer macro consolidado

O plano operacional (histórico, linhas pausadas e tarefas T1–T22) está em
`docs/technical/plans/backlog-continuacao.md`. Este parecer continua sendo a fonte
científica; não é o quadro de tarefas.

**Data:** 30/09/2026. **Commit auditado:** `e9d1ccb`, branch `novos_testes`.

**Fontes consolidadas:**
1. parecer macro original (`MIN-STATION-parecer-macro-e9d1ccb.md`, 28/09/2026, §§A–J);
2. revisão crítica desse parecer (30/09/2026), que conferiu as afirmações contra relatórios, CSVs e
   código em `e9d1ccb` e reproduziu os testes de corretude;
3. tréplica do autor do parecer, que aceitou a maior parte das correções e fez duas ressalvas à revisão.

**Estado do projeto quando este documento foi escrito:** o `plano-pos-e13.md` estava em execução.
A regeneração do benchmark-v1 (Passo 2) já tinha alterado o manifesto no working tree e o E14 estava
rodando. Tudo o que aqui descreve o benchmark vale para `e9d1ccb` e precisa ser refeito depois do fim
do plano.

**Papel deste documento:** ser a base de referência para decidir o plano de continuação depois do
`plano-pos-e13`. Nenhuma recomendação daqui foi executada.

## Como ler

| Rótulo | Significado |
|---|---|
| **Reproduzido** | Teste executado na revisão, com saída registrada; os comandos estão no Apêndice |
| **Confirmado** | Conferido nos documentos, CSVs ou código de `e9d1ccb`, com a fonte indicada |
| **Corrigido** | Afirmação do parecer original ajustada pela revisão e aceita na tréplica |
| **Em aberto** | Ainda não há evidência suficiente para concluir |

Separações mantidas ao longo do texto, conforme `CLAUDE.md`:
- o problema original de Das;
- a formulação base atual;
- os métodos experimentais;
- os resultados obtidos e as hipóteses.

---

## 1. Síntese

1. **A direção de pesquisa é sólida.** Formulação compacta de fluxo agregado, fortalecida por
   estrutura de cobertura e emparelhamento. As melhores evidências são as de C1, de C2 em percursos
   longos e do núcleo inteiro de cobertura como fonte de limites.
2. **Há um defeito de corretude real, e não está no modelo.** O oráculo em `cuts.py` rejeita
   instalações viáveis quando `S∩T ≠ ∅`, porque não representa a permanência de um robô no próprio
   alvo (Reproduzido, §2.1). O compacto (`baseline.py`) não é afetado.
3. **A construção de D do artigo IJCAI 2026 (p.75), lida literalmente, também falha com `S∩T`.** O erro
   é de sinal oposto: aceita trânsito sem estação (Reproduzido, §2.2).
4. **A reprodutibilidade experimental é menor do que os relatórios supõem.** A ordem das restrições
   varia entre processos, e o `TimeLimit` depende da carga da máquina (Reproduzido e Confirmado, §3).
5. **O E13 não atribui o gap.** Mostra que o incumbente melhora com mais tempo sob `MIPFocus=1`, mas
   mistura tempo e parâmetro, e não diz se o residual está no LB ou no UB (Confirmado, §3.3).
6. **A literatura precisa ser atualizada.** Das, Hanaka, Melissinos e Ono (IJCAI 2026) tratam o mesmo
   problema, e nenhum documento do projeto os cita (Confirmado, §6).
7. **Ordem recomendada para a continuação:** corretude → confiabilidade experimental → decisões de
   pesquisa → posicionamento frente à literatura (§9).

---

## 2. Corretude

### 2.1 Oráculo sem permanência em `S∩T` — Reproduzido

**Onde está.**
- `_build_flow_net_aggregate` (`cuts.py:403–410`) e `integer_oracle` (`cuts.py:680–691`) criam os arcos
  σ→`v_out` para origens e `v_in`→τ para destinos, com relé `v_in`→`v_out` de capacidade `(m−1)y_v`
  em terminais.
- Não existe arco `v_out`→`v_in`, e `A_r` não tem laços (`ms_utils.py:124`).
- Consequência: um robô em `v ∈ S∩T` é obrigado a sair de `v`.

**Contraexemplos.** Em ambos, o modelo base prova ótimo 0 com C = ∅ e o oráculo diz o contrário.

| Caso | Oráculo | Corte devolvido | `is_valid_cut` | Max-flow / m | Base (Gurobi) |
|---|---|---|---|---|---|
| caminho v–w, S=T={v}, r=1 | inviável | `y_w ≥ 1` | inválido | 0 / 1 | OPT 0, C=∅ |
| caminho a–b–c–d, S={a,d}, T={b,d}, r=1 | inviável | `y_c ≥ 1` | inválido | 1 / 2 | OPT 0, C=∅ |

`separate_classical_fracs` devolve os mesmos cortes inválidos.

**Consequências conforme o uso.** Formulação do parecer, refinada na revisão e aceita na tréplica:

| Uso do oráculo | Efeito | Onde (em `e9d1ccb`) |
|---|---|---|
| Heurísticas primais | Podem instalar estações em excesso ou perder soluções melhores. Uma solução que o oráculo **aceita** é viável, então os UBs continuam válidos, embora talvez pessimistas | `primal.py`: `reverse_delete`, `_swap_pass`, `greedy_augment`, `build_primal_h3`, `build_primal_from_core` |
| Cortes e fixações | Podem excluir soluções legítimas e comprometer LBs e certificados | `bc_yspace.solve_bc_yspace` (118, 136), `solve_cbi` (306), `yspace.solve_lp_cutting_plane` (168), C5 (`cuts.py:495`), `preprocess.find_mandatory` (129) |
| Formulação compacta | Nenhum. O defeito não demonstra erro no modelo | `baseline.py`, COMP |

**Resultados já registrados que tocam o defeito.** Das 75 instâncias principais, 5 têm `S∩T ≠ ∅`:
`mapf-den312d-m50-f2-rho`, `mapf-room-32-32-4-m25-f4-rho`, `puc-w23c23-intercalado-f2-rho`,
`b-b09-intercalado-f2-rho` e `i-i160-301-intercalado-f2-rho`.
- **E10 e E10b:** as duas MAPF `-rho` estão entre as 30 D/A e passaram pelo oráculo. Os UBs dessas
  linhas são válidos, mas talvez pessimistas. A conclusão "construtores piores que o COMP" (13/13) não
  depende delas.
- **E8:** todas as instâncias têm `S∩T = ∅`. Não afetado.
- **E9 (núcleo), E13, E14 e protocolo de dificuldade:** usam o compacto ou o núcleo sem oráculo. Não
  afetados.
- **E12 (planejado):** as instâncias de desenvolvimento (bip42p-regiao, hc10p, pucn-cc3-10n) têm
  `S∩T = ∅`. Os "2 controles MAPF" não estão especificados; se algum for `-rho`, os cortes 𝒵 do CBI
  podem ser inválidos nele.

**Por que as regressões não pegaram.**
- `verify_e8_oracle.py` compara duas redes com a mesma construção.
- `StayPut` (`synthetic.py:290–315`, S=T={a,b} com aresta a–b) é resolvido por troca e não isola a
  permanência.
- O comentário de `SharedTerminal` (`synthetic.py:323–324`) descreve um mecanismo errado ("libera o
  trânsito por v … de graça"), embora o OPT=1 registrado esteja certo.
- **A regressão do C4-DM continua válida** (Corrigido; o parecer generalizava a circularidade).
  `verify_c4_dm.py` confere contra `is_valid_cut`, que usa matching e trata a permanência
  corretamente. O oráculo só produz falso **negativo**, então as confirmações de corte inválido de
  `correcao-c4-dm.md` se mantêm. O que fica fraco é apenas o ramo do oráculo como detector de cortes
  inválidos em instâncias com `S∩T`.

### 2.2 Construção de D no artigo IJCAI 2026 — Reproduzido

- **O que o artigo diz (p.75):** "For any vertex u ∈ S ∪ C we add the arcs uv iff v ∈ N_r(u) ∩ (T ∪ C)".
- **O problema:** um `v ∈ S∩T` fora de C recebe e emite arcos, e passa a servir de relé sem estação.
  O Lema 1, lido literalmente, falha nesse caso.
- **Contraexemplo:** estrela com centro v e folhas p1–p4, r=1, S={v,p1,p2}, T={v,p3,p4}.
  - O D literal admite p1→v→p3 com C = ∅.
  - O modelo base prova **OPT = 1, C = {v}**.
  - A instância é exatamente o gabarito `SharedTerminal` do projeto, que já registra OPT=1. O projeto
    tem, portanto, uma regressão contra esse falso positivo; falta uma contra o falso negativo de §2.1.
- **Classificação:** lacuna de especificação na construção apresentada. Não refuta a caracterização
  por matching quando as arestas representam caminhadas viáveis, nem os demais teoremas.
- **Para uso no projeto:** recarga só em estações instaladas, exceto a partida da própria origem, ou a
  rede com papéis separados e arco de permanência (§2.3).

### 2.3 Equivalência da formulação base com `S∩T` — Confirmado parcialmente

- **A proposta do parecer (§B.3):** uma rede auxiliar com arco de permanência `v_out`→`v_in` de
  capacidade 1 para `v ∈ S∩T`, a partir da qual se prova que a base unificada (balanço
  `out−in = 1_S − 1_T`, ativação `in ≤ b_v + (m−b_v)y_v`) representa o problema original, inclusive
  com fluxo contínuo.
- **O que foi verificado:** os três casos pequenos (§2.1 e §2.2) batem com o modelo base.
- **Em aberto:** a prova não foi verificada linha a linha. Ela deve ser escrita no repositório e
  conferida antes de ser citada como resultado.

### 2.4 Casos que a especificação deve fixar (do parecer, §B.6)

- `S=T`: ótimo 0; não se exige ciclo de troca.
- `m=1` em grafo unitário: `OPT = max(0, ⌈d(s,t)/r⌉ − 1)`.
- Ótimo 0 se e somente se o bipartido de alcance direto, incluindo os pares s=t, tem matching perfeito.
- Terminais podem ser estações indispensáveis.
- A interseção não pode ser cancelada: no caminho a–b–c com S={a,b}, T={b,c} e r=1, a instalação vazia
  funciona, mas cancelar b exige recarga.
- A inconsistência do Algoritmo 1 e do Lema 2 de Das (contagem `⌊L/r⌋`) já estava registrada em
  `validacao-formulacao-base.md` §A.2 (Confirmado).

---

## 3. Reprodutibilidade e controles

### 3.1 Ordem do modelo varia entre processos — Reproduzido

- **Onde está:** `prepare_cuts` faz `list({frozenset(Z) …})` (`harness.py:87`), e `add_cuts_to_model`
  percorre `for v in Z` (`harness.py:51`). `bc_yspace` repete o padrão (236, 264, 124, 140). Nenhum
  script de cortes ou benchmark fixa `PYTHONHASHSEED`.
- **Teste:** `b-b15-regiao-f4` com `PYTHONHASHSEED` = 1, 2 e 3. O conjunto de 33 cortes é idêntico, e a
  ordem muda nas três execuções.
- **Consequência:** a correção de `generate_C4_DM` tornou determinístico o **conteúdo** da família, não
  a ordem do modelo entregue ao Gurobi.
- **Correção robusta** (ressalva da tréplica, aceita): ordenar explicitamente cortes, coeficientes e
  demais elementos da construção. Fixar `PYTHONHASHSEED` é paliativo.

### 3.2 Parada por tempo

Com `TimeLimit`, o trabalho feito até a parada depende da carga da máquina. A documentação do Gurobi
sobre determinismo, citada no parecer, recomenda construção determinística e, quando couber, limites de
trabalho. Confirmar a semântica de `WorkLimit` na documentação da versão 12.0.3 antes de adotá-lo.

**Em aberto:** quanto das diferenças de desempenho observadas vem da ordem, da parada por tempo ou da
mudança de família de cortes. O que se sabe é que as três causas existem.

### 3.3 E13 — Confirmado

- `focus1800` foi comparado contra o `controle` de 600 s, sem um controle de 1800 s. O resultado 7/13
  mistura mais tempo com a mudança de parâmetro, e o efeito isolado de `MIPFocus=1` não está
  identificado.
- Somando o melhor LB e o melhor UB dos três braços, 12 instâncias seguem abertas, com gaps de 10,5% a
  44,4%, e uma fecha em 17.
- Esses pares descrevem o conhecimento acumulado, não o desempenho de uma execução.
- Sem OPT, o intervalo não se divide entre erro do incumbente e fraqueza do bound. Comparar "queda
  primal" com "gap residual" usa denominadores diferentes (UB_controle e UB_melhor). Em estações
  absolutas a leitura qualitativa se mantém: warehouse-m50 tem queda de 9 e residual de 36.
- **Afirmação a corrigir no relatório:** `resultados-e13-pli.md` §5 (l.143) diz "Isto não é ruído de
  execução" e atribui a divergência de 9/13 com o manifesto à correção do C4-DM. A evidência permite só
  listar três causas candidatas (§3.1–3.2) sem separá-las.

### 3.4 Regressão de dados no manifesto — Confirmado, já tratado

`build_manifest.py` lê `results/benchmark/dificuldade_v1*.csv` e não lê `reavaliacao_c4dm.csv`. Um
rebuild em `e9d1ccb` reverteria as correções do C4-DM. O `plano-pos-e13` (Passo 2) já trata isso ao
regerar os CSVs.

**Recomendação que permanece:** o histórico de cada resultado deve registrar a versão dos cortes, o hash
da instância, a configuração e a origem do certificado.

---

## 4. Evidência por linha de pesquisa

UB é solução viável e LB é limite inferior. LP, bound final de MIP e ótimo do núcleo são grandezas
distintas. Todos os números abaixo foram confirmados nos CSVs indicados.

| Linha | Evidência | Fonte | Conclusão permitida |
|---|---|---|---|
| C1 | LP: hc9u 1 → 28,444; hc10p 1 → 51,2 | `results/cuts/e1_raiz.csv` | Fortalecimento estrutural comprovado da relaxação |
| C2 | Sobre C1: warehouse-m50 58,2 → 77,8; room-m10 9,2 → 13,2 | `resultados-e9-e10-pli.md` §2 | Relevante com várias recargas no trajeto |
| C4-DM | cc12-2p: núcleo C1 = 5, C1+C4 = 6; soma pouco no E9 | E8; E9 §2.1 | Informação coletiva existe; ganho geral de tempo não demonstrado |
| C3 | Raiz: Philadelphia st25 33,33 → 36,23; Barcelona st25 11 → 12 | `e2_yspace.csv` | Ganho real, mas em **extensões** ponderadas/dirigidas; no problema de Das não está medido |
| C5 | +0,024 em um caso, nada nos outros | `e2_yspace.csv` | Pausar |
| Compacto com cortes (E4) | hc9u (UB/LB, 300 s): BASE-I 45/28, BASE-C 47/30, CORTES 38/32 | `results/cuts/e4_arvore.csv` | Um caso claro de melhoria simultânea de UB e LB no problema original |
| E4, ressalvas | Barcelona st15: BASE-C prova 15 em 284 s, CORTES 16/14. Philadelphia st5: CORTES 42/37 contra BASE-C 41/36 | idem | Relaxação mais forte não implica busca mais rápida |
| E4, erro de prosa | Barcelona st25: o CSV registra BASE-C 16/16 ótimo em 299,432 s; a prosa diz "sem provar" | `resultados-e2-e4-pli.md` l.285 contra l.314–315 | Corrigir a prosa |
| Núcleo inteiro (E3) | hc9u 32 em 3,159 s; hc10p LB 56; hc11p LB 101; a solução de 32 testada é inviável no compacto | `e3_cobertura_ip.csv` | A cobertura inteira dá limites além do LP; uma solução ótima do núcleo não basta como UB |
| Núcleo inteiro (E9) | 6 linhas com LB (60 s) acima do COMP (600 s), por 1–2 estações | `resultados-e9-e10-pli.md` §2.1 | Sinal para PUC/PUCN; as 6 linhas não são 6 topologias independentes |
| CBI (E8) | cc12-2p: OPT 6 em 7,5 s de solver, com primal de 291 s fora do tempo; o COMP recebeu start de 4096 (sem start, UB 7 no E7) | `e8_comparative.csv`, `e7_comparative.csv` | Caso forte, mas único e numa **extensão ponderada**; diferença não atribuível só à arquitetura |
| CBI em hc10p/bip42p | LB com 1 iteração e 0 cortes (pool não terminou) | `e8_comparative.csv` | Evidência a favor do núcleo, não da decomposição iterativa |
| E10b | Melhorou em 1/30 (w23c23: 158 → 156 com start); LB 141 igual | `resultados-e9-e10-pli.md` §4 | Ganho localizado; a heurística não é um componente robusto |
| E13 | Δ_UB ≥ 5%: 2/13 em 600 s e 7/13 em 1800 s, contra o controle de 600 s | `resultados-e13-pli.md` | Existe margem primal em alguns casos; efeito de `MIPFocus` não identificado |
| Lagrangeana | 8/8 piores que o LP (bundle e subgradiente) | `results/lagrangean/*_resumo.csv` | Pausar ajustes da mesma relaxação |
| Preprocessing | 12/12 com LB igual; 1 UB pior (bip42p 46 → 49); 30 de 90 linhas sem baseline compatível | `results/preprocessing/` | Sem base para afirmar ganho robusto |
| Simetria | `Symmetry=2` "não alterou", só na prosa, sem CSV | `resultados-e2-e4-pli.md` l.73 | Pausa com base fraca; se reaberta, refazer com registro |

Não há comparação sistemática de NodeCount nem de trajetórias primal/dual nos CSVs de E4/E8/E9/E13, e
quase tudo usa uma única seed. **Em aberto:** redução da árvore de busca e estabilidade entre seeds.

---

## 5. Benchmark

Todos os números desta seção são de `e9d1ccb` e devem ser refeitos depois da regeneração.

- **Manifesto:** 92 linhas.
  - 75 principais: 70 do benchmark-v1 e 5 legadas (bip42p, hc9u, hc10p, hc11p, hc12p);
  - 11 `extensao_dirigida`, 3 `extensao_ponderada`, 3 `historico`.
  - `CLAUDE.md:70` ("22 antigas + 70") está desatualizado.
- **Benchmark-v1:** 35 F / 5 M / 4 D / 26 A. As 30 D/A são 13 PUC, 10 MAPF, 3 PUCN, 3 Vienna e
  1 PACE. Já há instâncias que pressionam a formulação, então resultados negativos não se explicam por
  o benchmark ser fácil.
- **Partição dependente:** a regra alfabética põe variantes do mesmo grafo nos dois lados em 11 grafos
  de origem: bip42p, hc9u, hc10p, I065, cc10-2u, w23c23, b06, b12, b18, lin06 e apia. A avaliação
  independente exige agrupar por grafo de origem.
- **Duplicata efetiva:** `hc9u.txt` e `puc-hc9u-seed-r1` têm V, S, T, R e arestas idênticos. Não contam
  como duas evidências.
- **Pouca variedade em `S∩T`:** só 5 instâncias principais têm sobreposição, e ela já expôs dois
  defeitos, no C4-DM e no oráculo. A variedade precisa cobrir permanência necessária, troca necessária
  e recarga em terminal.
- **Leitor de instâncias:**
  - `ms_utils.py:96–101` não simetriza arestas (inofensivo hoje: `arcos_sem_reverso=0` em todas as
    principais);
  - não valida duplicatas, pesos, conectividade nem `N`;
  - `baseline.py:305` trunca R com `int(float(R0))`, enquanto o harness preserva o float.
- **Conversões externas (MAPF, PACE):** a dificuldade no problema de origem não se transfere
  automaticamente. Registrar explicitamente a remoção de pares OD e de pesos, e que a largura de árvore
  de G não é a de G^r.

---

## 6. Literatura: IJCAI 2026

Das, Hanaka, Melissinos e Ono, *Charging Station Placement for Anonymous Mobile Agents: A Parameterized
Complexity Perspective*, IJCAI 2026, pp.72–80. O PDF está em
`docs/technical/reference/novo_artigo_das_2026.pdf`. O artigo usa k para o número de robôs (o nosso m).

**É o mesmo problema.** Robôs não rotulados, autonomia comum, objetivo de cardinalidade, estação em
qualquer vértice e distância em passos (p.73). A contribuição é teórica: não há formulação de PLI nem
experimentos. Portanto o artigo não mostra superioridade sobre COMP, CBI ou os nossos cortes.

| Resultado do artigo | Onde | Uso para o projeto | Limite |
|---|---|---|---|
| Equivalência (G, r) ↔ (G^r, 1) | Prop. 1, p.75 | Referência bibliográfica para o grafo de alcance; propriedade de validação | Não é validação independente se as duas representações usarem a mesma construção |
| Verificação por alcance e matching | Lemas 1–2, Teo. 1, p.75 | Oráculo independente, testemunhos, deficiências de Hall | A construção literal de D falha com `S∩T` (§2.2) |
| Redução de Set Cover | Teo. 3, p.76 | Família de controle positivo para o núcleo: C1 do lado das origens reproduz o Set Cover, e o artigo diz que a redução preserva o objetivo | Variações que introduzem conflitos de Hall precisam de nova prova do ótimo |
| Bin Packing; NP-dificuldade em planares e bipartidos de grau limitado | Teos. 2 e 4, pp.75–76 | Famílias esparsas estruturadas para multiplicidade | Dificuldade assintótica não garante dificuldade experimental |
| FPT em k (connecting forest, Steiner) | Lema 3, Teo. 6, p.77 | Referência exata para poucos robôs | `k^{O(k)}`; a "forest" pode compartilhar vértices (rodapé); o esboço com `S_i∩T_i` precisa de esclarecimento |
| FPT por modular-width e vertex cover | Lema 4, Teos. 7–8, p.77 | Compressão por módulos, com mais fundamento que symmetry breaking genérico | Só vale se o parâmetro medido for pequeno; a existência de um ótimo estruturado não é desigualdade válida |
| Algoritmo polinomial em árvores, com estações pré-instaladas | Teo. 9, p.78 | Referência exata em árvores; UB por árvore geradora | Aplicar à árvore física, não a G^r; nunca usar como LB para o grafo geral |
| k-aproximação | Teo. 10, p.78 | Construção primal com garantia | O esboço tem desigualdade invertida ("walk … is at most dist"). A prova substituta do parecer (`q ≤ OPT ≤ \|C\| ≤ kq`) foi conferida e está correta. Fator k = m (até 1142) é vazio na prática |

**Pendência de posicionamento (Em aberto).** Levantar quais resultados de
`direcoes-pli-min-station.md` e `validacao-formulacao-base.md` coincidem com o artigo: verificação
polinomial por matching, uso de G^r, argumentos de Hall. Só então se diz o que é contribuição própria.

Contribuições que podem permanecer próprias, sujeitas a esse levantamento:
- formulação compacta all-V com prova completa e tratamento correto de terminais;
- caracterização da fraqueza da relaxação e desigualdades de recarga e compatibilidade coletiva;
- integração eficiente de núcleo, fluxo e oráculos, com vantagem demonstrada;
- benchmark reprodutível que explique essas vantagens.

---

## 7. Correções ao parecer original

| Afirmação original | Versão consolidada | Base |
|---|---|---|
| "CBI é melhor para cobertura", "gargalo predominantemente primal" e "correção de `S∩T` concluída" como conclusões do projeto (§A.2) | São generalizações a evitar, não conclusões que o projeto assumiu. Os documentos já tinham ressalvas: `direcoes` l.662–664; `resultados-e13` §3.1; `correcao-c4-dm.md` com escopo em C4-DM | Revisão B.1; tréplica aceita |
| Corte de multiplicidade `Σ min(δ, p_v) y_v ≥ δ` como direção nova (§E.1) | Já existe como versão mochila do C4 / C6 (`direcoes-pli-min-station.md` §5.4 l.337 e §5.6) e como E11 planejado. A validade foi conferida | Revisão B.2; tréplica aceita |
| Árvores listadas como questão aberta pelo projeto (§A.3) | Nenhum documento do projeto faz isso. A atualização bibliográfica procede; a atribuição ao projeto, não | Revisão B.3; tréplica aceita |
| Validação circular em geral (§B.4, §I.1) | Restrita às verificações que compartilham a construção defeituosa. A regressão do C4-DM continua válida | Revisão B.4; tréplica aceita |
| Construção primal do Teorema 10 como "decisão adicional ao plano" (§J.5) | Investigação opcional, condicionada a custo e utilidade (ver abaixo) | Revisão B.7 e ressalva da tréplica |
| "E2 gastou centenas de segundos sem progresso em algumas instâncias" | Em uma só: cc10-2p, 237,7 s de C3 com o LP parado | Revisão B.5 |
| Contagens 35/5/4/26 e partição D/A | Retrato de `e9d1ccb`; refazer depois da regeneração | Revisão B.8; tréplica aceita |

**Construção primal: posição consolidada.** Não há evidência de benefício dela no projeto; cabe no
máximo uma avaliação pequena e condicionada.
- O argumento do E10b ("start melhor não move o LB") tem alcance limitado. O próprio relatório diz que
  isso não decide primal × dual, e um incumbente melhor pode ajudar na poda e no tempo de prova, que o
  E10b não mediu de forma sistemática.
- Também não se deve chamá-la de barata antes de medir o custo total: distâncias, matching e
  reconstrução de caminhos.

---

## 8. Em aberto

- Quanto das diferenças entre execuções vem da ordem do modelo, da parada por tempo ou da mudança de
  família de cortes (§3.2).
- Onde está o residual do E13, no LB ou no UB. O E14 cobre parcialmente as instâncias de gap pequeno e
  não caracteriza as de gap grande.
- A prova de equivalência com arco de permanência, linha a linha (§2.3).
- Se algum resultado registrado além de E10/E10b usou o oráculo numa instância com `S∩T`. O
  levantamento em `e9d1ccb` não achou outro, mas deve ser refeito depois do `plano-pos-e13`.
- Estabilidade entre seeds e redução do número de nós. Não há dados sistemáticos.
- Qual parte da fundamentação do projeto já está no artigo IJCAI (§6).

---

## 9. Subsídios para o plano de continuação

Para decidir depois do fim do `plano-pos-e13`, somando os resultados finais dele. Nada aqui altera o
plano em andamento.

**Ordem.** A etapa 1 é pré-requisito das etapas 3 e 4 sempre que um método usar o oráculo em instâncias
com `S∩T`. A etapa 2 é pré-requisito de qualquer comparação de desempenho.

### Etapa 1 — Corretude

1. Acrescentar arco de permanência ao oráculo e à rede agregada (ou usar papéis separados, §2.3).
2. Criar um **validador independente** por estados `(v, bateria)` com matching, enumerando C em grafos
   pequenos. Ele deve ser diferente de comparar duas implementações da mesma rede.
3. Criar uma regressão com os dois casos de §2.1, a estrela de §2.2 e o caminho a–b–c de §2.4, rodando
   em modelo base, oráculo, separação fracionária e validação de cortes.
4. Reavaliar os resultados que tocam o oráculo em `S∩T` (§2.1): as duas linhas `-rho` do E10/E10b, e a
   escolha dos controles MAPF do E12, se o E12 rodar antes da correção.
5. Escrever no repositório a prova de equivalência com permanência.

### Etapa 2 — Confiabilidade experimental

1. Construir o modelo em ordem explícita: ordenar a lista de cortes, os vértices de cada corte e os
   coeficientes, em `harness.py` e em `bc_yspace.py`. Fixar `PYTHONHASHSEED` só como proteção extra.
2. Avaliar `WorkLimit` como orçamento determinístico, depois de confirmar a semântica no Gurobi 12.0.3.
3. Consolidar o benchmark regerado:
   - contagens e classes novas;
   - partição por grafo de origem;
   - deduplicação de `hc9u`/`puc-hc9u-seed-r1`;
   - proveniência de cada resultado (versão dos cortes, hash, configuração, certificado).
4. Controles pareados em toda comparação: mesmo orçamento, mesmo start (ou nenhum), mais de uma seed
   onde o veredito depender de 1–2 unidades, e registro de NodeCount.

### Etapa 3 — Pesquisa, com base nos resultados finais

- **E11 / C6** (versão mochila, δ ≥ 2): linha matemática própria, **desacoplada do E14**. Ordem
  obrigatória: derivação escrita, validador próprio para RHS δ ≥ 2 (`is_valid_cut` não cobre esse
  caso) e só então medição.
- **Acoplamento além da cobertura:** separadores no grafo de alcance, deficiências após várias recargas
  e C3 seletivo por violação e custo. Um separador físico pode ser atravessado sem recarga dentro de um
  arco de alcance, então não se declara estação obrigatória numa articulação de G.
- **Núcleo inteiro como mecanismo de LB,** independente do CBI vencer.
- **CBI:** teste discriminante entre núcleo, oráculo e iteração, depois da correção do oráculo e do
  pool, com orçamento total.
- **Desagregação all-V,** primeiro só como diagnóstico de LP em instâncias pequenas (custo
  O(m·|A_r|)).
- **Famílias controladas:**
  - derivadas do Set Cover (controle positivo do núcleo, depois conflitos de Hall);
  - F1, F2 e Tri, com perturbações;
  - árvores com ótimo verificável;
  - pares G/r × G^r/1.
- **Construção primal** do Teorema 10: opcional e condicionada (§7).

### Etapa 4 — Posicionamento e artigo

- Citar o artigo IJCAI 2026 e fazer o levantamento de sobreposição (§6).
- Estruturar a contribuição em torno da pergunta: **quais estruturas tornam suficiente a cobertura de
  estações, quais exigem compatibilidade coletiva de rotas, e como capturar ambas em modelos exatos
  eficientes?**

### Manter pausadas

- Ajuste de subgradiente ou bundle da mesma relaxação lagrangeana.
- Benders clássico como promessa de bound mais forte.
- BC-Y genérico em todas as famílias.
- Tuning do reverse-delete a partir de C = V.
- C5 por limiar.
- Symmetry breaking genérico.
- Geração de colunas antes de testar a força da desagregação.
- Acrescentar instâncias sem hipótese.

**Reabrir quando:** houver evidência específica, conforme a tabela da seção F do parecer original.
Empacotamento e bounds de atribuição não foram refutados pelo L_bot e continuam sem prioridade
automática.

### Condicionar

FPT em k, modular-width, vertex cover e o algoritmo de árvores: só quando o parâmetro medido nas
instâncias for pequeno, ou, no caso das árvores, depois de implementar e validar com r > 1 e `S∩T`.

---

## 10. Correções documentais identificadas (não executadas)

| Arquivo | Correção |
|---|---|
| `docs/technical/reference/resultados-e13-pli.md` §5 (l.143) | Retirar "Isto não é ruído de execução"; listar as três causas candidatas (§3) |
| `docs/technical/reference/resultados-e13-pli.md` | Registrar o confundimento TL × `MIPFocus` do braço de 1800 s |
| `docs/technical/reference/resultados-e2-e4-pli.md` (l.314–315) | Barcelona st25: BASE-C provou o ótimo em 299,4 s |
| `CLAUDE.md` (l.70) | "5 antigas compatíveis + 70 do benchmark-v1" |
| `docs/technical/reference/validacao-formulacao-base.md` (l.102) e `docs/context-ai/base-formulation.md` (l.155) | Remover ou qualificar a hipótese `S∩T = ∅` |
| `experiments/cuts/synthetic.py` (`StayPut`, `SharedTerminal`) | Corrigir os comentários de mecanismo; acrescentar um gabarito de permanência pura |
| `experiments/alternative-formulations/modelo_estendido.py` | O nome "equivalente ao baseline" é enganoso: o modelo é VI-only e bloqueia trânsito por terminais |

---

## 11. Plano de instâncias sintéticas estruturais (subsídio para depois do `plano-pos-e13`)

**Estado:** plano, não executado. Nenhum gerador foi implementado. As propriedades marcadas como
"verificado em casos minúsculos" vêm das execuções descritas no Apêndice B.

Em cada família são separados:
- **[Demonstrado]:** prova curta dada aqui ou na literatura citada;
- **[Verificado]:** solução exata em casos minúsculos, o que não é prova;
- **[Hipótese]:** ainda não testado;
- **[Esperado]:** previsão de comportamento;
- **[Falsifica]:** resultado que derruba a hipótese.

### 11.1 Papel das instâncias sintéticas

As instâncias reais do benchmark-v1 mostram que há dificuldade (31 D/A após a regeneração), mas não
dizem **por quê**. Sem OPT, o intervalo UB−LB não se divide entre fraqueza do bound e incumbente ruim
(§3.3). O E14 confirmou o limite prático disso: em `room-32-32-4-m10-f8` e
`room-32-32-4-m25-f4-rho`, com gap de só 2 estações, 4 h com `Cutoff` e `MIPFocus=3` não certificaram
o ótimo.

As famílias sintéticas complementam o benchmark de três formas:
1. **Ótimo conhecido ou certificado independente,** que permite medir gap absoluto.
2. **Um mecanismo por família,** que permite atribuir causa.
3. **Pares quase idênticos** ("gêmeos") que diferem numa única propriedade estrutural.

Elas não substituem as instâncias reais: mostram que um mecanismo **pode** produzir dificuldade, não
que ele explique a dificuldade observada em MAPF, Vienna ou PUC. Essa ponte é sempre uma comparação
separada (§11.7).

**Classe própria no manifesto, a decidir.** As famílias não entram nas estatísticas do benchmark-v1
nem disputam o limite de 20% de sintéticos de `plano-benchmark-v1.md` §10. Esse limite trata de outro
papel ("só como validação"). A proposta é `classe = estrutural`, com proveniência completa.

### 11.2 Diagnóstico dos geradores atuais

**Gadgets em `experiments/cuts/synthetic.py`:** todos têm r=1, só F1, F2 e Sec59 têm parâmetros de
tamanho, e servem como regressão, não como benchmark.

| Gadget | Mecanismo representado | Limite |
|---|---|---|
| F1(m,k) | diluição: estação não compartilhável (z_LP = 2k+1 contra OPT = 2mk+1) | fechado por C1+C2 dos dois lados (D:312); trivial para o COMP com cortes |
| F2(k,L) | deficiência de Hall igual a 1 por bolsão (z_LP = 1/3 contra OPT = k) | fechado por C4; deficiência fixa em 1 |
| Tri | gap da própria cobertura (OPT 2 > LP_cov 1,5) | tamanho fixo (9 vértices) |
| Sec59(L) | raiz do BC-y abaixo de z_LP | específico do BC-y |
| StayPut, SharedTerminal, TermRelay* e outros | corretude (terminais, S∩T) | não são de desempenho; StayPut não isola a permanência (§2.1) |

**Gerador do benchmark-v1 (`src/converters/build_benchmark.py`):** a variedade é **superficial**. Ele
varia:
- a colocação de terminais (`ST-SEED`, `ST-REGIAO`, `ST-INTERCALADO`, `rho`);
- a autonomia (`R-FRAC` com k em {2, 4, 8});
- sobre 9 famílias de topologias externas.

A estrutura é medida **depois** de gerar (regime, `classes_wl`, `demanda_saltos`, UB/m), e nenhuma
instância foi construída para exercitar um mecanismo. Consequências:
- 11 grafos de origem aparecem nos dois lados da partição (§5);
- não se sabe, para nenhuma das 31 D/A, qual mecanismo produz o gap.

**Mecanismos ausentes em qualquer gerador do projeto:**

| Mecanismo | Ausente porque |
|---|---|
| Gap de cobertura escalável com OPT conhecido | Tri é fixo; hc* (Q_k) tem LP+C1 = 2^(k−1)/k, mas OPT(hc9u) ∈ [32, 38] segue aberto |
| Atribuição coletiva com cobertura exata | não há família em que o núcleo dê o valor exato e mesmo assim todas as suas soluções sejam inviáveis |
| Várias camadas de recarga com núcleo ambíguo | F1 tem uma única rota por robô; nada controla o número de ótimos do núcleo inviáveis (Philadelphia st25 tem ≥ 500, mas é extensão) |
| Deficiência de Hall com multiplicidade > 1 | F2 só tem deficiência 1; D:517-520 registra que a tentativa com "saídas privadas" falhou por desvios via terminais com estação |
| Simetria controlada | hc* é vértice-transitivo, mas não há gêmeo rígido de mesmo tamanho e mesmo gap |
| r > 1 em gadgets | todos os gadgets usam r=1 |

### 11.3 Famílias propostas

As quatro famílias são todas fiéis ao problema original de Das:
- grafo simples, conexo, não dirigido e não ponderado;
- r inteiro em número de arestas;
- estações permitidas em todo V e objetivo de cardinalidade;
- |S|=|T| e **S∩T=∅**.

A sobreposição fica fora de propósito (§11.5).

| Família | Função científica | Ótimo |
|---|---|---|
| **BP** — atribuição coletiva | cobertura exata no valor, mas inviável na estrutura; separa onde está a dificuldade, no UB ou no LB | conhecido ("sim" plantado) ou certificado independente |
| **SC** — cobertura com gap controlado | controle positivo do núcleo; separa simetria de gap da relaxação | conhecido (GF(2)) ou certificado independente (gêmeo rígido) |
| **HB** — bolsão de Hall com relé em terminal | instrumento do E11/C6: quando a contagem de primeiro salto não basta | verificado em casos pequenos; prova a escrever |
| **TR** — corredores entrelaçados | camadas de recarga: bound exato com muitos ótimos inviáveis do núcleo | demonstrado |

#### Família BP — Bin Packing (Teorema 4 do artigo IJCAI 2026)

**Pergunta científica.** Quando a cobertura dá o valor exato do LB e a dificuldade está toda na
atribuição coletiva de robôs a destinos, onde o método sofre: em achar a solução (UB) ou em provar que
ela não existe (LB)?

**Mecanismo.** Os cortes de cobertura são satisfeitos por qualquer escolha de "conector". Quem decide a
viabilidade é a contagem de destinos de cada grupo, que é uma partição numérica. A relaxação fraciona a
atribuição, e o núcleo não enxerga a contagem.

**Construção** (parâmetros: itens `e_1..e_n` inteiros positivos, q caixas, `B = Σe_i/q` inteiro):
- para cada caixa j: um vértice `v_j` com B folhas-destino;
- para cada item i: um vértice `u_i` com `e_i` folhas-origem e q conectores `c_{i,j}`, com arestas
  `u_i–c_{i,j}` e `c_{i,j}–v_j`;
- r = 1, m = Σe_i = qB robôs.

```
 origens do item i            conectores            caixas         destinos
 l_i1 ─┐                  ┌─ c_i1 ── v_1 ─┬─ t_11 … t_1B
 l_i2 ─┼── u_i ───────────┼─ c_i2 ── v_2 ─┼─ t_21 … t_2B
   …  ─┘                  └─ c_iq ── v_q ─┴─ …
```

O artigo usa m para o número de caixas; aqui é q, porque m é o número de robôs.

**Propriedades:**
- **[Demonstrado] LB = 2n+q em toda instância.**
  - Cada folha-origem só é adjacente a `u_i`, então C1 força `y_{u_i}`.
  - Cada folha-destino só é adjacente a `v_j`, então C1 força `y_{v_j}`.
  - A banda de distância 2 de C2 força `Σ_j y_{c_{i,j}} ≥ 1` por item.
  - Logo LP+C1+C2 ≥ 2n+q, e o núcleo vale exatamente 2n+q.
- **[Demonstrado, artigo p.76] OPT = 2n+q se e somente se existe partição exata** dos itens em caixas
  de soma B. Nas instâncias "sim" plantadas, OPT é conhecido por construção.
- **[Verificado]** Em 4 de 4 casos minúsculos:
  - "sim": OPT = 2n+q (8 e 10);
  - "não": OPT = 2n+q+1 (7 e 9);
  - núcleo = LP com cortes = 2n+q em todos;
  - nas "não", **nenhum** ótimo do núcleo é viável (0 de 2 e 0 de 6); nas "sim", 2 de 6 e 4 de 14.
- **[Hipótese, a demonstrar]**
  - OPT = 2n+q+σ\*, em que σ\* é o mínimo de divisões de itens entre caixas;
  - OPT ≤ 2n+2q−1, porque o next-fit com divisão cria no máximo q−1 divisões.

**Gêmeos.**
- "Sim" plantado: itens "tripleto" em (B/4, B/2), 3 por caixa.
- "Não": mesma distribuição e mesma soma, com uma perturbação +1/−1 em dois itens, e inexistência de
  partição certificada por um solver exato de bin packing independente (programação dinâmica ou IP
  próprio). Esse certificado não depende da formulação MIN-STATION.

**Escalonamento.** Varia q (com n = 3q) e B. Ficam fixos r = 1 e o padrão de tripleto. Como m = qB
cresce linearmente em B, B fica moderado.

**[Esperado]**
- **COMP:** raiz = 2n+q em todas.
- **Instâncias "sim":** o LB já está fechado, e a dificuldade está no UB (achar a partição).
- **Instâncias "não":** o UB 2n+q+1 é fácil (dividir um item), e a dificuldade está em subir o LB em 1.
  É o caso "fácil achar, difícil provar", com o OPT conhecido.
- **Núcleo/CBI:** devolve 2n+q sempre; nas "não", todo ótimo do núcleo é inviável. **[Hipótese]** O
  número de iterações do CBI cresce com o número de ótimos do núcleo.

**Sucesso.** Os gêmeos "sim" e "não", com o mesmo tamanho, mostram lados difíceis opostos (UB e LB) de
forma reproduzível em 3 seeds do solver.

**[Falsifica]**
- os dois gêmeos resolvidos em menos de 60 s em q = 8;
- ou a dificuldade igual nos dois lados.

**Validação:**
- solução exata em q ≤ 3 (enumeração de C);
- certificado de partição por solver independente;
- validador independente da §9 (Etapa 1) nas instâncias pequenas.

**Riscos.**
- A dificuldade é a do bin packing, um problema conhecido. A família não testa cortes de cobertura,
  que são exatos aqui por construção.
- O que ela mede é como os métodos lidam com acoplamento coletivo de atribuição, sem confundir isso
  com o bound.
- O m unário encarece o modelo de fluxo.

#### Família SC — cobertura exata com gap controlado (Teorema 3 do artigo, versão bipartida)

**Pergunta científica.** Quando a cobertura representa exatamente o problema, o COMP perde para o
núcleo e o CBI? E a dificuldade de provar o ótimo vem da simetria ou do gap da relaxação?

**Mecanismo.** É um set cover clássico com gap de integralidade logarítmico e grupo de automorfismos
grande. O fluxo não acrescenta restrição.

**Construção SC-GF2(k):**
- U = GF(2)^k∖{0}, com n = 2^k−1;
- conjuntos `F_a = {x : a·x = 1}` para cada a ∈ U;
- vértices `w_a`, `s_x` e `t_x`;
- arestas: `s_x–w_a` se e somente se a·x = 1, e `w_a–t_x` para todo par;
- r = 1, m = n, |V| = 3n, |E| = n·2^(k−1) + n².

**Propriedades:**
- **[Demonstrado] OPT = k.**
  - Pelo artigo (p.76), OPT = valor do set cover. Diretamente: cada `s_x` só tem vizinhos em W, e
    W–T é completo.
  - Uma família {F_a} cobre U se e somente se os a geram GF(2)^k: se não gerarem, existe x ≠ 0
    ortogonal a todos, que fica descoberto.
- **[Demonstrado] LP + C1 = n/2^(k−1) < 2.** A solução uniforme `y = 2^−(k−1)` em W é viável. Somando
  as n linhas de C1, cada `w_a` aparece 2^(k−1) vezes. O gap de integralidade é ≈ k/2.
- **[Verificado]** k = 3 e 4:
  - OPT = 3 e 4;
  - LP com C1+C2+C4 = 1,750 e 1,875;
  - z_LP = 1;
  - núcleo = OPT;
  - C2 e C4 coincidem com C1.
- **[Demonstrado]** O grupo contém GL(k,2), que age em a e x preservando a·x, e é transitivo em W.

**Gêmeo SC-rígida(k, seed).**
- Sistema de conjuntos aleatório com o mesmo n, o mesmo tamanho de conjunto e o mesmo grau de
  elemento, sem simetria (verificar com `classes_wl`).
- OPT é obtido por um IP de set cover separado, que é certificado válido pela equivalência do
  Teorema 3.
- Isola simetria de gap: mesmo LP aproximado, simetria diferente.

**Escalonamento.** k de 5 a 8 (n de 31 a 255; |V| de 93 a 765). Ficam fixos r = 1 e a estrutura.
W–T tem n² arestas, então k = 8 já dá |A_r| ≈ 2·(32 mil + 65 mil).

**[Esperado]**
- COMP: raiz ≈ LP+C1 < 2 e LB sobe só por B&B.
- **[Hipótese]** O guloso acha k cedo, o que caracteriza "primal fácil, prova difícil".
- O núcleo enfrenta o mesmo set cover sem fluxo; a diferença para o COMP mede o custo do fluxo.
- CBI: a primeira iteração já é viável, porque toda cobertura é viável. É o controle positivo do CBI.

**Sucesso.** Nós e tempo de prova crescem com k, com UB = k encontrado cedo, ou o gêmeo rígido se
comporta de forma claramente diferente no mesmo k.

**[Falsifica]** O Gurobi prova k = 7 em menos de 60 s, fechando a raiz com cortes próprios
(zero-half/CG) ou detecção de simetria. A família seria fácil demais e só serviria como sanidade.

**Validação:**
- conferência automática de LP+C1 = n/2^(k−1) e de OPT = k nos pequenos;
- IP de set cover independente para o gêmeo.

**Riscos.** A dificuldade é a do set cover, o que é intencional para um controle. W–T completo deixa
o dígrafo de alcance denso.

#### Família HB — bolsão de Hall com relé em terminal (generalização do F2; instrumento do E11/C6)

**Pergunta científica.** Num bolsão com deficiência de Hall δ ≥ 2, o gap entre C4 (RHS 1) e OPT é de
multiplicidade de primeiro salto, que a versão mochila (E11/C6) fecharia, ou vem de camadas adicionais?
Lembrando: E.1 do parecer é a linha E11/C6 já existente (§7).

**Mecanismo.**
- q origens disputam ndir < q destinos diretos compartilhados, o que dá deficiência δ = q − ndir.
- Os δ excedentes precisam de relés, e cada relé só é vizinho de p origens.
- Em grafo não dirigido existe sempre um desvio alternativo: uma estação num destino direto `c` mais uma
  estação numa origem `a'` mais um relé de `a'` ligam **todas** as origens aos relés de `a'`.

**Construção HB(q, ndir, p; k, L):**
- origens A, completas com os destinos diretos C;
- relés X, cada um adjacente a um bloco disjunto de p origens;
- δ destinos distantes D, cada um adjacente a todos os relés e a um balanceador `e_d` (origem) com
  destino próprio `g_d`, como em F2;
- r = 1;
- k bolsões ligados por caminhos de L ≥ 2 vértices não terminais, como em F2.

**Propriedades:**
- **[Verificado]** Em 5 de 5 bolsões isolados (δ de 2 a 7, p ∈ {1, 2}):
  - **OPT = min(⌈δ/p⌉, 3)**;
  - núcleo (C1+C2+C4) = 1;
  - LP com cortes entre 1,00 e 1,34;
  - **C1 e C2 não geram nenhum corte.**
- **[Demonstrado]** Valem os dois UBs (soluções explícitas: ⌈δ/p⌉ relés, ou {c, a', relé de a'}).
- **[Hipótese, a demonstrar]** OPT ≥ min(⌈δ/p⌉, 3), e a aditividade entre bolsões.
- **[Demonstrado pela fórmula de §5.4]** C6 de primeiro salto **não** fecha o gap. Com S' = A, o
  destino direto `c ∈ N⁺(S')` recebe coeficiente min(δ, |N⁻(c)∩S'|) = δ, então `y_c = 1` sozinho
  satisfaz a desigualdade. A previsão é LB com C6 ≈ 1 por bolsão, contra OPT 3.

**Gêmeos.**
- p ≥ δ: um relé basta, OPT = 1 = núcleo.
- p = 1 e δ ≥ 3: OPT = 3, núcleo = 1.
- δ = 2: OPT = 2, pelos relés.

**Escalonamento.** Variam k (bolsões) e q. Ficam fixos r = 1 e L. O gap absoluto cresce com k
(3k contra k); a razão fica em ≈ 3.

**[Esperado]**
- Bound fraco em todos os métodos de primeiro salto.
- Instâncias pequenas, provavelmente fáceis em tempo. O valor da família está nas medições de LP e de
  raiz, não no tempo.

**Sucesso.** Depois de implementado o E11, o LB com C6 reproduz a previsão (≈ 1 por bolsão) e uma
família de segunda camada (C3/𝒵, ou uma desigualdade nova de "relé em terminal" a derivar) fecha o
gap.

**[Falsifica]** O C6 implementado fecha o gap, o que significaria que a análise de coeficientes
acima está errada e precisa ser refeita antes de qualquer conclusão sobre o E11.

**Achado lateral [Hipótese].** Se o limite de 3 por bolsão for geral em grafos não dirigidos com
destinos diretos compartilhados, a multiplicidade de primeiro salto tem efeito limitado no problema de
Das. Isso redirecionaria o E11 para desigualdades de segunda camada. **Ainda não há evidência
suficiente para concluir** que o limite seja geral; até agora ele só foi observado nesta construção.

**Validação:**
- enumeração exaustiva de C em bolsões com q ≤ 8;
- prova escrita do LB;
- regressão com o validador independente (§9, Etapa 1).

**Riscos.**
- Por ser trivial em tempo, a família só serve para medir bounds.
- A construção pode ter outros desvios não previstos, o mesmo risco registrado em D:517-520. A
  enumeração serve para pegá-los.

#### Família TR — corredores entrelaçados (camadas de recarga)

**Pergunta científica.** Quando o bound de cobertura é exato mas há exponencialmente muitos ótimos do
núcleo inviáveis por incompatibilidade entre camadas de recarga, os métodos baseados no núcleo (CBI)
degradam enquanto o compacto não? E atalhos locais (degraus entre corredores) mudam isso?

**Mecanismo.**
- Cada banda de distância C2 pode ser coberta em qualquer corredor.
- O núcleo combina bandas de corredores diferentes, e a rota só existe se as estações consecutivas
  estiverem no mesmo corredor ou ligadas por atalho.

**Construção TR(k, L, r, σ):**
- m origens adjacentes às entradas `e_j` de k corredores;
- corredor j é o caminho `e_j – c_{j,1} … c_{j,L} – x_j`;
- `x_j` é adjacente a todos os m destinos;
- degraus `c_{j,ℓ}–c_{j+1,ℓ}` a cada σ posições (σ = ∞: sem degraus);
- distância origem→destino D = L+3.

**Propriedades:**
- **[Demonstrado] OPT = ⌈D/r⌉−1.**
  - LB: as bandas disjuntas de C2 dão ⌈D_s/r⌉−1 (D:307-320).
  - UB: um único corredor com estações a cada r passos, compartilhado por todos (sem capacidade).
- **[Demonstrado]** Com σ = ∞, há k^R ótimos do núcleo (R = ⌈D/r⌉−1 bandas, uma escolha de corredor
  por banda), e só k são viáveis.
- **[Verificado]** (k, L, r) = (2, 5, 2) e (3, 5, 2):
  - OPT = 3;
  - z_LP = LP com cortes = núcleo = 3;
  - ótimos do núcleo: 8 (2 viáveis) e 27 (3 viáveis).
- **[Hipótese]** Com σ ≤ r, a fração de ótimos viáveis cresce. É preciso contar.

**Variante TR-F1** (para tornar o compacto não trivial): grupos de origens restritos a feixes
disjuntos de corredores, o que reintroduz a diluição de F1. **[Hipótese]** a escrever e verificar.

**Escalonamento.** Variam k, R (por L/r) e σ. Ficam fixos m e o padrão de ligação.

**[Esperado]**
- COMP: LP exato (o compartilhamento é perfeito), solução imediata.
- CBI: iterações crescendo com k^R se cada corte 𝒵 eliminar poucos ótimos. **[Hipótese]**
- Degraus reduzem as iterações.

**Sucesso.** O número de iterações ou o tempo do CBI cresce de forma super-linear em R, com o COMP
estável.

**[Falsifica]** Os cortes 𝒵 de uma única solução inviável eliminam classes inteiras e as iterações
crescem só linearmente. Isso seria um achado positivo sobre a família 𝒵, mas a família deixaria de
servir como teste de estresse.

**Validação:**
- contagem exata dos ótimos do núcleo nos pequenos;
- verificação de OPT pela fórmula;
- validador independente.

**Riscos.** A família é trivial para o compacto por construção, então só discrimina métodos
baseados no núcleo. A relevância dela depende do E12 manter a linha A2 viva.

#### Fontes avaliadas e não adotadas agora

- **Reduções de NP-dificuldade em grafos esparsos (Teorema 2: planar bipartido com Δ ≤ 6 ou 3; bipartido
  com Δ ≤ 4).** O artigo omite as construções ("based on reductions from Vertex Cover"). Sem elas não
  dá para gerar fielmente nem explicar que parte produziria dificuldade para as nossas formulações.
  **Ainda não há evidência suficiente para concluir.** Reavaliar se uma versão completa do artigo for
  publicada.
- **Árvores (Teorema 9):** polinomiais. Úteis como referência exata e validação, não como fonte de
  dificuldade.
- **FPT (k, modular-width, vertex cover):** descrevem quando o problema é fácil; não geram
  dificuldade.
- **Grafos aleatórios maiores ou mais densos:** rejeitados pelo próprio objetivo; não isolam mecanismo.
- **Famílias com S∩T:** só como suíte de corretude (§11.5), nunca como desempenho, antes da correção e
  validação independente do oráculo (§2.1).

### 11.4 Matriz experimental mínima

**Fase P — piloto (desenvolvimento).** Parâmetros fixados antes de gerar.

| Família | Células | Instâncias |
|---|---|---|
| BP | q ∈ {4, 6, 8} (n = 3q, B = 60) × {sim, não} × 2 seeds de geração | 12 |
| SC | k ∈ {5, 6, 7} × {GF2, rígida s0, rígida s1} | 9 |
| HB | k bolsões ∈ {1, 4, 8} × {(q, ndir, p) = (6, 1, 1), (6, 1, 6)} | 6 |
| TR | (k, R) ∈ {(2, 4), (3, 4), (3, 6)} × σ ∈ {∞, r} | 6 |
| **Total** | | **33** |

**Métodos:**
- **M1:** COMP do protocolo (base U + C1+C2+C4).
- **M2:** BASE-C sem cortes, como referência da relaxação.
- **M3:** núcleo inteiro.
- **M4:** CBI com o mestre corrigido (E12). As quatro famílias têm S∩T=∅, então o defeito do oráculo
  não é exercitado; mesmo assim, M4 só roda depois da regressão da §9, Etapa 1.
- **M5:** COMP + C6, só depois do E11 implementado e validado, em HB e, como controle, em BP e SC.

**Orçamento e condições:**
- mesmo orçamento para todos os métodos: TL 600 s, ou `WorkLimit` equivalente se adotado (§3.2);
- 4 threads, duas fatias, sem start;
- 1 seed do solver no piloto, e 3 seeds nas células cujo veredito dependa de 1–2 unidades.

**Pior caso:** 33 instâncias × 4 métodos × 600 s ≈ 22 h de CPU, ou ≈ 11 h em duas fatias. A maioria
das instâncias pequenas deve terminar antes do TL.

**Medidas por execução, registradas separadamente:**
- tempo de geração, de preprocessing, de heurística e do solver;
- z_LP, raiz, LB e UB finais, gap e NodeCount;
- tempo até o primeiro incumbente, até o melhor incumbente e até a prova;
- iterações e cortes do CBI;
- cortes por família.

**Pré-requisito de implementação:** o `harness.measure_mip` atual não registra NodeCount nem os tempos
de incumbente. Isso exige um callback de registro, da §9, Etapa 2.

**Fase E — expansão, só para as famílias aprovadas na §11.6:**
- 2 níveis de tamanho acima do piloto;
- 5 seeds de geração e 3 seeds do solver;
- **conjunto de avaliação gerado com seeds novas** (por exemplo, ≥ 100) depois de congelar
  parâmetros e critérios.

**Separação desenvolvimento/avaliação:**
- desenvolvimento = piloto; avaliação = Fase E com seeds novas;
- toda variação do mesmo construtor e dos mesmos parâmetros-base fica no mesmo lado, como manda a
  correção de partição da §5;
- nenhum parâmetro é escolhido depois de ver qual método venceu.

### 11.5 Validação matemática e computacional antes da geração em escala

1. **Provas escritas** em `direcoes-pli-min-station.md` ou num documento próprio:
   - BP: LB 2n+q e OPT = 2n+q ⟺ partição (pelo artigo, refeito); limite superior com divisões.
   - SC: OPT = k, LP+C1 = n/2^(k−1) e o grupo GL(k,2).
   - HB: LB min(⌈δ/p⌉, 3), aditividade, e a análise do coeficiente C6 em `c`.
   - TR: OPT = ⌈D/r⌉−1 e a contagem k^R / k.

   Nenhuma família passa para a Fase P com propriedade marcada [Hipótese] que sustente o critério de
   sucesso dela.
2. **Validador independente** (§9, Etapa 1): estados `(v, bateria)` + matching, rodado em todas as
   instâncias pequenas de cada família, além da enumeração de C para OPT. É distinto de comparar duas
   implementações da mesma rede.
3. **Checagem automática do mecanismo** em cada instância gerada, como asserção do gerador:
   - BP: núcleo = 2n+q e certificado de partição (ou de inexistência) por solver independente;
   - SC: LP+C1 igual à fórmula e OPT = k nos pequenos;
   - HB: C1 e C2 vazios e núcleo = k;
   - TR: OPT pela fórmula e contagem de ótimos do núcleo nos pequenos.

   Uma instância que não exercita o mecanismo é descartada antes de entrar no manifesto.
4. **Fidelidade:** grafo simples e conexo, arquivo com as duas orientações de cada aresta (o leitor
   não simetriza, §5), pesos unitários, r inteiro, |S|=|T| e S∩T=∅. Também a equivalência G/r ×
   G^r/1 numa amostra.
5. **Determinismo e proveniência:**
   - gerador com seed explícita e saída ordenada;
   - sha256 do conteúdo;
   - entrada no manifesto com versão do gerador, parâmetros, seed, classe proposta (`estrutural`) e
     origem do certificado de OPT;
   - modelo construído em ordem explícita (§9, Etapa 2).
6. **Suíte de corretude com S∩T, separada:** permanência pura, troca necessária e recarga em terminal
   comum. Ela valida modelo, oráculo e cortes (§2), e não entra em nenhuma medição de desempenho antes
   da correção do oráculo.

### 11.6 Critérios para manter ou abandonar cada família (pré-registrados)

**Regra geral.** Uma família segue para a Fase E somente se cumprir as três condições:
1. todas as propriedades previstas se reproduzem em todas as instâncias do piloto. Se não, é erro de
   gerador ou de teoria, e o trabalho para até a causa ser encontrada;
2. o fenômeno previsto aparece em pelo menos 2 dos 3 níveis de tamanho e se repete em 3 seeds do
   solver;
3. a família discrimina pelo menos dois métodos ou duas famílias de cortes.

**Descarte geral:**
- todos os métodos provam o ótimo em menos de 60 s no maior tamanho do piloto, sem diferença de bound;
- ou o tempo cresce só com o tamanho, sem diferença em gap de raiz ou em nós (dificuldade de escala,
  não estrutural).

| Família | Manter se | Descartar se |
|---|---|---|
| BP | os gêmeos sim/não mostram lados difíceis opostos (UB nas "sim", LB nas "não") ou as iterações do CBI explodem nas "não" | ambos resolvidos em menos de 60 s com q = 8 |
| SC | nós e tempo de prova crescem com k com UB = k achado cedo, ou o gêmeo rígido difere de forma clara | k = 7 provado em menos de 60 s com a raiz fechada pelos cortes do solver |
| HB | LB com C6 igual à previsão (≈ 1 por bolsão) e alguma família de segunda camada fechando o gap. Mantida como instrumento de bound, mesmo fácil em tempo | C6 fecha o gap, o que exige refazer a análise antes de qualquer conclusão |
| TR | iterações do CBI super-lineares em R com o COMP estável, e efeito dos degraus | iterações lineares (registrar como achado sobre 𝒵 e abandonar como estressor) |

### 11.7 Prioridade depois do `plano-pos-e13`

**Pré-requisitos comuns:**
- §9, Etapa 1: oráculo corrigido e validador independente;
- §9, Etapa 2: construção determinística e registro de nós e incumbentes.

**Ordem recomendada:**
1. **BP.** É a mais informativa: OPT conhecido nas "sim", certificado independente nas "não", bound de
   cobertura exato por construção. Ataca a pergunta que o E13 e o E14 deixaram em aberto (onde está a
   dificuldade, no UB ou no LB) com o OPT na mão. Não depende do E11 nem do CBI.
2. **HB.** É barata (instâncias pequenas, só medições de bound) e **precisa vir antes de implementar o
   E11**: prevê que o C6 de primeiro salto não fecha o gap nesse tipo de bolsão. Se a previsão se
   confirmar, o E11 deve mirar desigualdades de segunda camada.
3. **SC.** Controle positivo do núcleo e do CBI, e separação simetria × gap. É útil para interpretar o
   E12.
4. **TR.** Depende do CBI corrigido e de a linha A2 seguir viva.

**Resultados finais do `plano-pos-e13` que podem mudar a ordem:**
- **E14 nas duas Vienna:**
  - se certificar OPT = UB_melhor, o residual em gap pequeno era de LB, o que sobe SC e HB
    (instrumentos de bound);
  - se achar solução melhor, sobe BP do tipo "sim" (dificuldade primal);
  - se for inconclusivo, como nas duas MAPF, reforça a necessidade de OPT conhecido, e a ordem se
    mantém.
- **E12:**
  - se o CBI corrigido vencer pelo critério pré-registrado (A2 segue), SC e TR sobem;
  - se A2 for encerrada para Das, TR cai para opcional e SC fica só como controle do núcleo.
- **Regeneração (31 D/A):** não muda a ordem. Serve só para escolher, na comparação-ponte da Fase E,
  as instâncias reais em que cada mecanismo será procurado. Exemplo: comparar o comportamento de BP com
  o de warehouse-m25/m50, em que o UB cai com mais tempo.

---

## Apêndice A — reprodução dos testes

Executar na raiz do repositório com o Python do projeto. Nenhum dos testes altera arquivos. Os dois
primeiros não usam solver.

**A. Oráculo sem permanência (§2.1):**

```python
import sys; sys.path.insert(0, 'experiments/cuts'); sys.path.insert(0, '.')
from cuts import (integer_oracle, build_neighborhoods, is_valid_cut,
                  _build_flow_net_aggregate, _edmonds_karp, separate_classical_fracs)
cases = [
    ('m1-stay', ['v'], ['v'], [('v', 'w'), ('w', 'v')]),
    ('m2-partial-overlap', ['a', 'd'], ['b', 'd'],
     [('a', 'b'), ('b', 'a'), ('b', 'c'), ('c', 'b'), ('c', 'd'), ('d', 'c')]),
]
for name, S, T, A in cases:
    Np, Nm = build_neighborhoods(A)
    ok, Z = integer_oracle(S, T, Np, set())
    g, cap, V, m = _build_flow_net_aggregate(S, T, A, {})
    print(name, ok, sorted(Z), is_valid_cut(S, T, A, Z, Np, Nm),
          _edmonds_karp(g, cap, '_s', '_t'), m,
          [sorted(z) for z in separate_classical_fracs(S, T, A, {})])
```

Saída esperada em `e9d1ccb`: `m1-stay False ['w'] False 0.0 1 [['w']]` e
`m2-partial-overlap False ['c'] False 1.0 2 [['c']]`.

**B. Ordem dos cortes (§3.1):** carregar uma instância pequena do benchmark-v1 (por exemplo,
`b-b15-regiao-f4`) com `harness.load_instance` e `prepare_cuts` com `{C1, C2, C4}`. Imprimir um hash da
lista na ordem de iteração e outro do conjunto ordenado. Repetir com `PYTHONHASHSEED` = 1, 2 e 3. O
esperado é o mesmo hash de conjunto e hashes de ordem diferentes.

**C. Modelo base nos contraexemplos (§2.1–2.2):** usar `construir_modelo_baseline(S, T, V, A)` com
1 thread nos três casos. O esperado é OPT 0 (C = ∅), OPT 0 (C = ∅) e, na estrela, OPT 1 (C = {v}).

---

## Apêndice B — verificações das famílias em casos minúsculos (30/09/2026)

**Condições:**
- modelo base (`construir_modelo_baseline`) resolvido ao ótimo com 1 thread;
- LP medido por `harness.measure_lp`;
- cortes de `harness.prepare_cuts` com {C1, C2, C4};
- núcleo = IP em y só com esses cortes;
- ótimos do núcleo enumerados, e viabilidade de cada um testada por `integer_oracle`. É válido porque
  S∩T=∅ em todos os casos e o oráculo só erra para falso negativo (§2.1);
- `PYTHONHASHSEED=0`.

Os scripts ficaram no scratchpad da sessão, fora do repositório. Para reproduzir, implementar as
construções exatamente como na §11.3.

| Caso | \|V\| | m | r | OPT | z_LP | LP C1+C2+C4 | Núcleo | Ótimos do núcleo (viáveis) |
|---|---|---|---|---|---|---|---|---|
| SC-GF2(k=3) | 21 | 7 | 1 | 3 | 1,000 | 1,750 | 3 | — |
| SC-GF2(k=4) | 45 | 15 | 1 | 4 | 1,000 | 1,875 | 4 | — |
| BP [1,1,2], q=2 (sim; 2n+q=8) | 19 | 4 | 1 | 8 | 3,000 | 8,000 | 8 | 6 (2) |
| BP [2,2,1,1], q=2 (sim; 10) | 26 | 6 | 1 | 10 | 3,000 | 10,000 | 10 | 14 (4) |
| BP [3,1], q=2 (não; 6) | 16 | 4 | 1 | 7 | 3,000 | 6,000 | 6 | 2 (0) |
| BP [2,2,2], q=2 (não; 8) | 23 | 6 | 1 | 9 | 3,000 | 8,000 | 8 | 6 (0) |
| TR(k=2, L=5) | 18 | 2 | 2 | 3 | 3,000 | 3,000 | 3 | 8 (2) |
| TR(k=3, L=5) | 25 | 2 | 2 | 3 | 3,000 | 3,000 | 3 | 27 (3) |
| HB q=4, ndir=2, δ=2, p=1 | 16 | 6 | 1 | 2 | 0,333 | 1,000 | 1 | — |
| HB q=5, ndir=2, δ=3, p=1 | 21 | 8 | 1 | 3 | 0,375 | 1,083 | 1 | — |
| HB q=6, ndir=1, δ=5, p=1 | 28 | 11 | 1 | **3** (⌈δ/p⌉ = 5) | 0,455 | 1,291 | 1 | — |
| HB q=8, ndir=1, δ=7, p=1 | 38 | 15 | 1 | **3** (⌈δ/p⌉ = 7) | 0,467 | 1,343 | 1 | — |
| HB q=6, ndir=1, δ=5, p=2 | 25 | 11 | 1 | 3 | 0,455 | 1,273 | 1 | — |

Nos casos HB, os cortes gerados foram só de C4 (C1 = C2 = 0).

São casos de validação de mecanismo, não de desempenho. Nenhum tempo medido aqui deve ser usado como
evidência de dificuldade.
