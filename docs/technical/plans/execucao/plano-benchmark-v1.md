# Plano: benchmark de instâncias MIN-STATION (benchmark-v1)

> **Documento histórico.** Plano de construção do benchmark-v1 (lote 1).
> O programa de pesquisa corrente está em
> `docs/technical/plans/plano-proxima-fase.md`. A partição por grafo de
> origem e a tag `benchmark-v1.0` são a tarefa R2 desse plano. Números e
> vereditos abaixo não foram reescritos.

## Contexto

O projeto tem poucas instâncias e não existe benchmark específico de MIN-STATION: Das é teórico
e não publica instâncias, e os trabalhos próximos (Kundu e Saha, ICRA 2018 e IROS 2023) não
disponibilizam dados. A revisão pré-E8 mostrou que a maior parte dos resultados E0–E8 foi obtida
em extensões ponderadas e/ou dirigidas. A partir de agora os experimentos principais usam
instâncias compatíveis com Das: grafo simples, não dirigido e conexo; autonomia r inteira em
passos; |S|=|T|=m; S∩T permitido.

Este plano organiza a linha de revisão, ampliação e documentação das instâncias, antes dos
próximos experimentos de PLI. Nada é implementado nem baixado antes da aprovação.

Fatos de base (verificados nesta sessão):
- Das: NP-difícil já com **r = 1** e grau máximo 6 (redução de (3,3)-SAT, OPT = nº de variáveis
  se e só se a fórmula é satisfatível); algoritmos linear em **caminhos** e quadrático em
  **ciclos**. Estrutura quase-árvore tende a ser fácil; r pequeno não implica instância fácil.
- `ms_utils.ler_instancia` ignora linhas iniciadas por `#`: metadados podem ir no cabeçalho.
- Já estão locais: `raw-data/steinlib/` (B, I080, I160, LIN, PUC, wrp3-83, fnl4461fst) e
  `raw-data/TransportationNetworks/` (~25 redes TNTP).

---

## 0. Linha E8 adiada (preservada, não descartada)

Ao aprovar, salvar em `docs/technical/plans/plano-pos-e8-adiado.md`. Itens (de
`resultados-e8-pli.md` §7–8), a retomar sobre o benchmark Das:
1. E8 com 3 seeds (`run_e8.py --seeds 42 43 44`).
2. CBI com mestre sem pool até o ótimo e enumeração só depois (não termina em hc10p/bip42p).
3. Heurística primal partindo de C pequeno (ótimo do núcleo) em vez de C = V.
4. Decidir o recorte de escopo de A2 (proposta: fora de R-a).
5. Commit do trabalho E7–E8 (pendente de aprovação).

A revisão pré-E8 (plano anterior deste arquivo) já foi executada; registro em
`plano-experimentos-e8.md`, seção "Revisão pré-execução".

---

## 1. O que temos hoje e lacunas

### 1.1 Inventário (medido nos arquivos de `instances/`)

| Instâncias | Origem / problema original | Transformação usada | Das? | Classe proposta |
|---|---|---|---|---|
| hc9u | SteinLib PUC (Steiner; hipercubo, pesos 1) | terminais SteinLib embaralhados (seed 42) e divididos ao meio; R=1 | **sim** (r=1) | principal |
| hc10p, hc11p, hc12p, bip42p | SteinLib PUC, pesos 100–110 | idem; R=150/200 | **sim, via A_r = E** (≡ r=1) | principal (regerar sem pesos, r=1) |
| cc10-2p, cc12-2p | SteinLib PUC, pesos 101–310 | idem; R=500 | não (ponderada) | extensão; OPT(cc12-2p)=6 certificado |
| cc12-2u | SteinLib PUC, pesos 1–3 | idem; R=2 | não | extensão; versão Das imediata ignorando pesos |
| lin23, lin37 | SteinLib LIN (VLSI, grade com buracos, L1) | idem; R=500 | não | extensão/histórico (fora de escopo por pedido) |
| fnl4461fst | SteinLib TSPFST | idem; R=250 | não | histórico (fora de escopo) |
| Chicago st5/10/15, Barcelona st15/25/50/54, Philadelphia st5/25/39, Anaheim st19 | TNTP (tráfego) | subgrafo por BFS; S/T = maiores origens/destinos O/D (disjuntos); km inteiros; R por percentil, **sobrescrito** nos experimentos (Chicago 26→7 etc.) | não (ponderada e dirigida) | extensão |
| F1, F2, Tri, Sec59, Direct0, TermRelay(Forced), StayPut, SharedTerminal, PathM1 | `synthetic.py` | manual, OPT conhecido | sim | sintético de teste |
| `inputs/hc9u.txt` | cópia | — | — | duplicata |

`inst_Barcelona_n1020_m2522_st_54` declara n=1020, tem 930 vértices.

### 1.2 Lacunas

1. **Só 5 instâncias Das**, todas da família PUC, todas com r=1, |S∪T|/n de 17% a 50% e muita
   simetria. Nenhuma Das com r > 1, topologia real, poucos terminais ou S∩T≠∅.
2. **Proveniência incompleta.** R de hc9u e hc10p–hc12p não sai da regra do conversor (distância
   mínima S–T ≥ 2 contra R=1; ≥ 200 contra R=150); R das TNTP são "referências históricas" sem regra;
   divisão S/T da SteinLib é sorteio simples.
3. **TNTP pouco desafiadora por construção:** terminais são centroides de zona em folhas (Chicago
   st15: 30 de 30 com grau ≤ 1), o que torna C1 muito forte; m pequeno (5–54) frente a n (400–930);
   redes esparsas quase planares com periferia arbórea (perto dos casos polinomiais de Das); R pelo
   percentil 50 das distâncias S–T deixa muitos pares a um salto.
4. **Sem classificação** de tamanho ou dificuldade.
5. **Sem separação desenvolvimento/avaliação:** métodos foram ajustados olhando hc9u e Philadelphia.

## 2. Instâncias atuais que continuam

- **Principal (Das):** hc9u, hc10p, hc11p, hc12p, bip42p, regeradas como grafos não ponderados com
  r=1 (idênticas às atuais, agora com metadados) + variantes r=2 e r=3; versões Das de cc10-2u,
  cc11-2u, cc12-2u (pesos ignorados).
- **Extensões (resultados preservados e rotulados):** cc10-2p, cc12-2p, TNTP, lin23, lin37, fnl4461fst.
- **Sintéticos:** gabaritos de `synthetic.py`, só para corretude.
- Nenhum arquivo existente é movido ou apagado; a classificação vai para o manifesto (§7).

## 3. Fontes externas: avaliação crítica

Critérios: relação com MIN-STATION; reconhecimento; disponibilidade e licença; fidelidade possível
a Das; diversidade acrescentada; informação nativa para G, S, T e r.

### 3.1 Problemas vizinhos (base da justificativa)

| Problema | Relação com MIN-STATION |
|---|---|
| Steiner com mínimo de pontos de Steiner e arestas limitadas (SMT-MSP; relay placement em redes de sensores) | o mais próximo: minimizar pontos intermediários para que todo "salto" caiba num alcance. Diferença: conecta terminais numa árvore, sem emparelhamento S→T. Sem benchmark público encontrado |
| Steiner com restrição de saltos (HCSTP; Voß 1999, Annals of OR) e sua versão dirigida (HCDST, UAVs como relé) | limite de saltos ≈ autonomia |
| Steiner em grafos (SPG) | terminais conectados por vértices intermediários; famílias PUC já deram as instâncias mais difíceis do projeto |
| Flow Refueling Location (FRLM; Kuby e Lim 2005) e localização de recarga para VE | estações com alcance limitado sobre pares O/D; caminhos fixos em vez de escolhidos |
| MAPF anônimo / robôs não rotulados | mesmo modelo de movimento (passos em grafo) e robôs não rotulados; o objetivo é outro |
| Recarga para robôs de inspeção em tubulações de água (J. Hydroinformatics 25(6), 2023) | aplicação real publicada de estações de recarga com alcance máximo sobre redes de tubulação |

### 3.2 Fontes candidatas

| # | Fonte | Problema original / reconhecimento / licença | Fidelidade a Das | Diversidade | Lógica G, S, T, r |
|---|---|---|---|---|---|
| 1 | **MAPF benchmarks** — MovingAI; Stern et al., SoCS 2019; [movingai.com/benchmarks/mapf.html](https://movingai.com/benchmarks/mapf.html) | MAPF; padrão da área; ODC-By | **exata**: células livres, 4-vizinhança, passo unitário, não dirigido | 33 mapas: empty, random, room, maze, warehouse, cidades raster (Berlin/Boston/Paris 256²), jogos (den312d … orz900d) | S, T = início e destino dos k primeiros agentes de um cenário (25 "random" + 25 "even" por mapa, prática padrão da área); r por R-FRAC (§4.4) |
| 2 | **SteinLib** ([steinlib.zib.de](https://steinlib.zib.de/steinlib.php); Koch, Martin e Voß, citação KMV00 do site) e **DIMACS 11** ([dimacs11.zib.de/downloads.html](https://dimacs11.zib.de/downloads.html)) | Steiner e variantes; referência da área | exata para famílias de peso unitário (PUCN no DIMACS 11: cobertura de código da PUC sem pesos); G-UNIT ou G-SUBDIV nas demais | PUC/PUCN (hipercubos, códigos, bipartidos), I080–I640 (incidência), B–E (esparsos aleatórios, OR-Library), VLSI (ALUE, DIW, LIN…), grades 1R/2R, **Vienna** (redes reais de telecomunicação sobre malha viária de cidades austríacas; Leitner et al. 2014), **Cologne** (fibra óptica, GIS), **RELAY** (HCDST: UAVs como relé, até 40 mil nós e 20 milhões de arcos) | terminais nativos (sem papel S/T) + regra ST-REGIAO / ST-INTERCALADO; r por R-FRAC |
| 3 | **PACE 2018 Steiner Tree** ([github.com/PACE-challenge/SteinerTree-PACE-2018-instances](https://github.com/PACE-challenge/SteinerTree-PACE-2018-instances)) | desafio PACE; CC0 | G-UNIT ou G-SUBDIV | trilha com **largura de árvore controlada** (decomposição fornecida) e trilha com poucos terminais: permite medir o efeito da largura de árvore, coerente com os casos polinomiais de Das | como a SteinLib |
| 4 | **Global Urban Street Networks** (Boeing; Harvard Dataverse [doi:10.7910/DVN/KA5HJ3](https://doi.org/10.7910/DVN/KA5HJ3)) | modelos OSMnx de 8.914 áreas urbanas, versão com DOI | G-SUBDIV com comprimentos em metros, versão não dirigida | topologias viárias muito variadas (grade regular a orgânica), com indicadores prontos para escolher casos contrastantes | sem terminais nativos: regra estrutural (ST-REGIAO entre bairros periféricos, ou terminais = interseções de maior centralidade); substitui o OpenStreetMap "cru" com snapshot reproduzível |
| 5 | **TNTP retrabalhada** (já local) | redes de tráfego; muito usadas em transporte | subgrafo não dirigido + G-SUBDIV (depende da decisão Q7) | viária com demanda real | S/T das maiores demandas O/D, terminais deslocados do centroide-folha para a interseção |
| 6 | **Redes de distribuição de água** — benchmarks do Centre for Water Systems, Exeter ([exeter.ac.uk/.../cws/resources/benchmarks](https://www.exeter.ac.uk/research/centres/cws/resources/benchmarks/)) | otimização de redes de água; referência da área; licença a confirmar | G-SUBDIV com comprimento dos tubos | redes de infraestrutura esparsas com laços; aplicação de recarga publicada | S = nós mais próximos de reservatórios/tanques, T = nós de maior demanda (dados nativos); r por R-FRAC |
| 7 | **League of Robot Runners** (competição de MAPF contínuo, ICAPS 2024; [github.com/MAPF-Competition](https://github.com/MAPF-Competition)) | robótica de armazém; mapas até 54 mil vértices | exata (grade) | armazéns e sortation realistas, só classe G | tarefas/agentes da competição como S/T |
| 8 | **Instâncias pela redução de Das** a partir de CNFs de benchmark de SAT (ex.: SATLIB, URL a confirmar) | SAT; muito usado | exata (é a construção da prova, r=1) | pouca (grafo de gadgets) | S, T e r=1 da própria redução; **OPT conhecido**. Família de validação, não principal |
| 9 | PACE 2025 Dominating Set ([pacechallenge.org/2025/ds](https://pacechallenge.org/2025/ds/)); pglib-opf (redes elétricas IEEE, CC-BY); EVRP (Mavrovouniotis et al., CEC 2020) | reconhecidos | fraca ou indireta | alguma | sem S/T nativos (DS, pglib) ou sem grafo (EVRP: pontos euclidianos completos). Só exploratório |

Descartadas: TSPLIB (exigiria inventar o raio de um grafo de disco); OR-Library p-mediana
(aleatórios, sem ganho sobre B–E); DIMACS 9 (malha viária dos EUA, dados com erros conhecidos,
coberta pelas fontes 4 e 5); redes genéricas SNAP; relay placement em sensores (sem benchmark
público).

### 3.3 Prioridade resultante

1. **MAPF** (aplicação de Das, semântica exata, S/T nativos).
2. **SteinLib + DIMACS 11 + PACE 2018** (proximidade estrutural, dificuldade conhecida, largura de
   árvore controlada, redes reais Vienna/Cologne).
3. **Redes urbanas de Boeing** (diversidade viária reproduzível) e **redes de água** (aplicação de
   recarga publicada).
4. TNTP retrabalhada, LoRR e a família da redução de Das.

## 4. Metodologia de transformação

Pipeline único e determinístico com regras nomeadas; cada instância registra as regras usadas.

### 4.1 Grafo
- Grafo subjacente simples e não dirigido; sem laços nem arestas paralelas; maior componente conexa.
- **G-UNIT**: ignora pesos quando eles não são comprimento de deslocamento (PUC, I-series, B–E).
- **G-SUBDIV(δ)**: quando o peso é comprimento físico (VLSI, redes viárias, tubulações), aresta de
  comprimento L vira caminho com max(1, round(L/δ)) arestas unitárias: pontos de recarga possíveis
  a cada δ unidades. δ calibrado para a classe de tamanho alvo e registrado.
- **G-GRID**: células livres e 4-vizinhança (MAPF, LoRR).
- Fonte dirigida (TNTP, RELAY): grafo subjacente não dirigido, declarado como adaptação.

### 4.2 Terminais e m
1. Nativos com papel: MAPF/LoRR (início e destino dos k primeiros agentes), TNTP (maiores origens e
   destinos O/D), água (fontes e demandas). m = k, vários níveis por grafo.
2. Nativos sem papel: terminais de Steiner; m = ⌊|terminais|/2⌋ ou níveis menores por regra.
3. Sem informação nativa (Boeing, redes genéricas): regra estrutural declarada.

### 4.3 Divisão S/T
- **ST-REGIAO**: duas regiões distantes (BFS a partir de dois vértices periféricos, desempate por id);
  S numa, T na outra. Transporte de longo curso.
- **ST-INTERCALADO**: emparelhamento guloso por proximidade; um de cada par para S e outro para T,
  pela ordem dos ids. Troca local e acoplamento denso.
- **ST-SEED(k)**: sorteio com seed registrada — só controle, para comparar com a divisão atual.
- **S∩T**: parâmetro ρ ∈ {0, 0,1}; os ρ·m terminais de S mais próximos de T também entram em T.
  No MAPF, S∩T surge se o destino de um agente coincide com o início de outro (a verificar).

### 4.4 Autonomia r
- **λ\*** = distância de gargalo do emparelhamento S–T (menor λ com emparelhamento perfeito só com
  pares d(s,t) ≤ λ). **OPT = 0 ⟺ r ≥ λ\***: sem estação ninguém recarrega, então cada robô precisa de
  um destino a ≤ r; com r ≥ λ\* o emparelhamento de gargalo basta.
- **R-FRAC(k)**: r = max(1, ⌈λ\*/k⌉), k ∈ {2, 4, 8} (≈ k−1 recargas no par mais longo).
- **R-1**: r = 1 (caso da prova de NP-dificuldade; A_r = E).
- A regra atual do conversor (percentil 50 das distâncias S–T) não garante r < λ\*.

## 5. Diversidade estrutural

Vetor de atributos por instância: n, |E|, grau médio/máximo, diâmetro, estimativa de largura de
árvore (heurística de grau mínimo; exata quando a PACE fornece), planaridade, fração de folhas,
|S∪T|/n, m, fração de terminais-folha, ρ, λ\*/r, |A_r|/n, classes do refinamento de cores (proxy de
simetria).

Seleção por cobertura: famílias topológicas (grade/armazém, labirinto, sala, cidade raster, jogo,
hipercubo/código, aleatório esparso, incidência, VLSI com buracos, telecom/viária, tubulação,
gadget) × r (R-1, R-FRAC 2/4/8) × densidade de terminais (baixa/média/alta) × regra S/T. Uma
instância nova só entra se ocupar uma célula vazia ou pouco coberta.

## 6. Tamanho e dificuldade (classificações separadas)

**Tamanho estrutural (a priori):** pelo modelo, dominado por |A_r| e n.
P: |A_r| ≤ 2·10⁴; M: ≤ 2·10⁵; G: > 2·10⁵. (hc9u 4,6 mil; Chicago R7 10 mil; Barcelona R5 33 mil;
cc12-2p 2,8 milhões.)

**Dificuldade computacional (a posteriori, protocolo fixo):** COMP (baseline U + C1+C2+C4, Gurobi,
4 threads, seed fixa, TL 600 s). F: ótimo ≤ 60 s; M: ótimo ≤ 600 s; D: gap final ≤ 10%; A: gap > 10%
ou sem incumbente.

**Regime (atributos):** R-a (λ\*/r alto, terminais esparsos), R-b (r pequeno, terminais densos),
R-c (|A_r|/n² alto), como nos relatórios E1–E8.

Indicadores a priori (λ\*/r, densidade de terminais, simetria, largura de árvore, gap do LP, justeza
do núcleo) são confrontados com a dificuldade medida; descobrir quais preveem dificuldade já é
resultado de pesquisa.

## 7. Proveniência e reprodutibilidade

- `raw-data/<fonte>/`: original intocado + `SOURCES.md` com URL, data de download, versão/DOI,
  licença, referência e SHA-256.
- `instances/benchmark-v1/<familia>/<nome>.txt` no formato atual, com cabeçalho `# meta:`.
- `instances/manifest.csv`, uma linha por instância, **inclusive as antigas**: nome, classe
  (principal / extensão ponderada / extensão dirigida / sintético / histórico), original, fonte,
  problema original, URL, referência, regras (G-, ST-, R-, ρ), m, r, seed, script e commit do gerador,
  SHA-256, atributos (§5), tamanho (§6) e, quando medidos, dificuldade e LB/UB.
- Gerador único `src/converters/build_benchmark.py` dirigido por `instances/benchmark-v1/spec.csv`;
  reaproveita `parse_stp` (`steinlib_to_minstation.py`), a leitura TNTP
  (`gen_min_station_tntp_to_minstation.py`) e `construir_arcos_alcance` (`ms_utils.py`).
- Teste: regerar tudo a partir de `raw-data/` e conferir os SHA-256.
- Documento `docs/technical/reference/benchmark-v1.md` com metodologia e justificativas.

## 8. Primeiro lote (≈ 50 instâncias)

| Sub-lote | Conteúdo | Download |
|---|---|---|
| 1a | PUC em Das: hc9u, hc10p, hc11p, hc12p, bip42p (r=1, iguais às atuais) + r=2; cc10-2u, cc11-2u, cc12-2u com G-UNIT e r ∈ {1,2} | não |
| 1b | MAPF: empty-32-32, random-32-32-10, room-32-32-4, maze-32-32-2, warehouse-10-20-10-2-1, den312d; cenário "even" 1; m ∈ {10, 25, 50}; R-FRAC 2/4/8 (seleção por cobertura, não todas as combinações) | sim, pequeno |
| 1c | Steiner: I080 (~6) e b01–b18 (~6) locais; PUCN (DIMACS 11); 2–3 Vienna/Cologne menores com G-SUBDIV; 4–6 da trilha de largura de árvore da PACE 2018; divisões ST-REGIAO e ST-INTERCALADO | parcial |
| 1d | Redes urbanas de Boeing: 4–6 áreas pequenas escolhidas pelos indicadores (grade regular vs. orgânica); G-SUBDIV; ST-REGIAO | sim |
| 1e (opcional) | 5–10 instâncias pela redução de Das a partir de CNFs pequenas SAT/UNSAT, OPT conhecido | sim |

Lote 2: redes de água, TNTP retrabalhada (após Q7), LoRR (classe G), mapas MAPF grandes.

## 9. Validação de utilidade

1. **Corretude:** lê com `ler_instancia`; conexa; |S|=|T|; C = V viável; SHA-256 reproduzível.
2. **Não trivial:** r < λ\* e não resolvida só por fixações forçadas.
3. **Referência:** LB e UB pelo protocolo da §6; UB conferido no compacto.
4. **Informativa:** região nova no espaço de atributos (distância normalizada mínima às já aceitas
   acima de um limiar) ou classe de dificuldade pouco coberta.
5. **Conjunto:** o lote separa métodos (o ranking COMP × CBI muda entre famílias, como no E8).

## 10. Maturidade (benchmark-v1 congelado)

- ≥ 60 instâncias Das de ≥ 5 famílias topológicas, a maioria derivada de benchmarks existentes;
  sintéticos e gadgets ≤ 20%, só como validação;
- classes P/M/G e F/M/D/A com ≥ 5 instâncias cada onde possível, com ≥ 10 D/A;
- ≥ 3 níveis de r por família; S∩T≠∅ em pelo menos uma família;
- manifesto completo; regeração reproduz os SHA-256;
- resultados de referência (COMP, protocolo §6; 3 seeds nas D/A);
- divisão **desenvolvimento / avaliação** fixa (ex.: 1/3 para ajustar métodos, 2/3 reservados às
  conclusões);
- tag de versão e `benchmark-v1.md`. Só então E9 em diante.

## Decisões tomadas (delegadas pelo usuário, 2026-09-26)

O usuário delegou as decisões pendentes à recomendação técnica:

1. **Q7 (TNTP):** as instâncias TNTP atuais ficam como extensão ponderada e dirigida declarada,
   fora das conclusões sobre Das. A versão retrabalhada (não dirigida + G-SUBDIV + terminais fora
   das folhas) vai para o lote 2, como família de aplicação.
2. **MAPF:** aceita como fonte prioritária.
3. **Redes urbanas de Boeing:** entram no lote 1 (1d) com poucas áreas pequenas. **Redes de água:**
   lote 2.
4. **Redução de Das:** lote 2, como família de validação com OPT conhecido.
5. **Itens E8 adiados:** pausados até o lote 1 ter resultados de referência (evita continuar
   ajustando métodos nas mesmas 5 instâncias).

## Etapas de execução (após aprovação)

1. Salvar este plano em `docs/technical/plans/plano-benchmark-v1.md` e a §0 em
   `plano-pos-e8-adiado.md`. Verificar: arquivos criados.
2. `instances/manifest.csv` com as 22 instâncias atuais classificadas, sem mover arquivos.
   Verificar: cada arquivo de `instances/` aparece uma vez.
3. Script de atributos (§5) e de λ\*. Verificar: OPT = 0 ⟺ r ≥ λ\* nos gabaritos.
4. `build_benchmark.py` + spec, lote 1a (local). Verificar: reproduz hc9u/hc10p/bip42p com A_r
   idêntico ao atual; SHA-256 estáveis em duas execuções.
5. Pedir aprovação dos downloads (MAPF, DIMACS 11/PACE 2018, Boeing) com `raw-data/*/SOURCES.md`.
6. Lotes 1b–1d; protocolo de dificuldade da §6; `benchmark-v1.md` preliminar.
