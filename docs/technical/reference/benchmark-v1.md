# Benchmark MIN-STATION v1 (versão preliminar, lote 1)

**Plano:** `docs/technical/plans/plano-benchmark-v1.md`
**Gerador:** `src/converters/build_benchmark.py` + `instances/benchmark-v1/spec.csv`
**Manifesto:** `instances/manifest.csv` (`src/converters/build_manifest.py`)
**Atributos:** `src/converters/instance_features.py`
**Dificuldade:** `experiments/benchmark/run_dificuldade.py` → `results/benchmark/dificuldade_v1*.csv`

## 1. Objetivo

Oferecer instâncias fiéis ao MIN-STATION de Das (grafo simples, não dirigido e conexo; autonomia
r inteira em passos; |S| = |T| = m; S ∩ T permitido), derivadas de benchmarks já usados em outros
problemas, com proveniência e geração reproduzíveis. Não existe benchmark publicado específico do
problema: Das é teórico e os trabalhos próximos não publicam dados.

## 2. Fontes

| Família | Fonte | Problema original | Por que serve | Licença |
|---|---|---|---|---|
| `puc`, `pucn` | SteinLib (PUC) e DIMACS 11 (SPG-PUCN) | Steiner em grafos (hipercubos, cobertura de código, bipartidos) | proximidade estrutural com Steiner; instâncias mais difíceis do projeto até aqui | uso acadêmico; SteinLib sem licença declarada |
| `steinlib-b`, `steinlib-i` | SteinLib (B de Beasley/OR-Library; I080/I160 de incidência) | Steiner em grafos | grafos esparsos e densos, pequenos (classe P) | idem |
| `steinlib-lin` | SteinLib (LIN, VLSI) | Steiner em grafos | grades com obstáculos; pesos L1 são comprimentos físicos | idem |
| `vienna` | DIMACS 11, Vienna I (Leitner et al. 2014) | Steiner (telecom real sobre malha viária) | topologia viária real com terminais reais | a confirmar |
| `pace2018` | PACE 2018, trilha 2 | Steiner com largura de árvore limitada | controla a largura de árvore (Das: caminhos e ciclos são polinomiais) | CC0 |
| `mapf` | MovingAI MAPF (Stern et al. 2019) | multi-agent path finding | aplicação de Das (robôs em ambientes internos); semântica de passos exata; início e destino dos agentes são dados | ODC-By |
| `urbano` | Global Urban Street Networks (Boeing), v3.1 | modelos de redes viárias (OSMnx) | topologias viárias contrastantes, snapshot com DOI | CC0 |

Detalhes, URLs e SHA-256 dos arquivos baixados em `raw-data/*/SOURCES.md`.

## 3. Transformação

Regras nomeadas, gravadas no cabeçalho `# meta:` de cada instância e no manifesto.

- **Grafo.** Grafo simples não dirigido subjacente, maior componente conexa.
  - `G-UNIT`: ignora pesos que não são comprimento de deslocamento (PUC, B, I, Vienna, PACE).
  - `G-SUBDIV:δ`: aresta de comprimento L vira caminho de max(1, round(L/δ)) passos, isto é,
    recarga possível a cada δ unidades (LIN com δ = 10 ou 20; cidades com δ = 100 m).
  - `G-GRID`: células livres de um mapa MAPF com 4-vizinhança.
- **S e T.**
  - `NATIVO`: início e destino dos m primeiros agentes do cenário MAPF `random-1` (prática
    padrão da área).
  - `ST-SEED:42`: terminais Steiner embaralhados com seed 42 e divididos ao meio — a regra das
    instâncias PUC antigas, mantida para reproduzi-las exatamente.
  - `ST-REGIAO`: terminais ordenados pela diferença de distância a dois vértices periféricos;
    S = os m mais próximos de um, T = os m mais próximos do outro (transporte de longo curso).
  - `ST-INTERCALADO`: emparelhamento guloso por proximidade (troca local, acoplamento denso).
  - `rho`: os ⌈ρ·m⌉ pares S–T mais próximos passam a ter destino = origem (S ∩ T ≠ ∅).
- **Autonomia.** λ\* = distância de gargalo do emparelhamento S–T. OPT = 0 se e somente se
  r ≥ λ\* (verificado nos gabaritos: `experiments/benchmark/verify_lambda.py`, 34 casos).
  `R-1`: r = 1. `R-FRAC:k`: r = max(1, ⌈λ\*/k⌉). Instâncias com r ≥ λ\* não são gravadas.

## 4. Reprodutibilidade

- Regerar tudo: `python src/converters/build_benchmark.py` (lê `raw-data/`, determinístico).
  Duas execuções produziram SHA-256 idênticos.
- As instâncias `puc-*-seed-r1` reproduzem exatamente as antigas `hc9u`, `hc10p`, `hc11p`,
  `hc12p` e `bip42p`: mesmos S e T e mesmo dígrafo de alcance
  (`experiments/benchmark/verify_lote1a.py`).

## 5. Classificação das instâncias antigas

Nenhum arquivo antigo foi movido; a classe está no manifesto.

| Classe | Instâncias | Observação |
|---|---|---|
| principal | hc9u, hc10p, hc11p, hc12p, bip42p | Das (as quatro últimas via A_r = E); regeradas como `puc-*-seed-r1` |
| extensão ponderada | cc10-2p, cc12-2p, cc12-2u | pesos em A_r |
| extensão dirigida | Chicago, Barcelona, Philadelphia, Anaheim (TNTP) | pesos e arcos de mão única |
| histórico | lin23, lin37, fnl4461fst | fora de escopo |

**Achado:** com o R gravado no arquivo, três instâncias TNTP são triviais, pois r ≥ λ\* e logo
OPT = 0: Chicago st5 (R = 32, λ\* = 28), Philadelphia st39 (R = 20, λ\* = 13) e Barcelona st54
(R = 21, λ\* = 11). Somado aos terminais em folhas, isso explica boa parte da baixa dificuldade
observada na TNTP.

## 6. Tamanho, dificuldade e regime

Três classificações independentes, todas gravadas no manifesto.

**Tamanho estrutural (a priori).** Pelo número de arcos do dígrafo de alcance, que domina o
tamanho do modelo compacto: P se |A_r| ≤ 2·10⁴, M se ≤ 2·10⁵, G acima disso.

**Dificuldade computacional (a posteriori).** Protocolo fixo: COMP = formulação base (variante U,
fluxo contínuo) mais os cortes estáticos C1+C2+C4; Gurobi 12.0.3, 4 threads, seed 42, TL 600 s, sem
solução inicial. F = ótimo provado em ≤ 60 s; M = ótimo em ≤ 600 s; D = gap final ≤ 10%;
A = gap > 10% ou sem incumbente.

**Regime (atributos).** R-a: alcance longo, λ\*/r ≥ 3. R-b: terminais densos, |S∪T|/n ≥ 15%.
R-c: alcance denso, |A_r|/n² ≥ 15%. "misto" quando mais de um critério vale.

### 6.1 Resultado: o tamanho estrutural não prediz a dificuldade

As 70 instâncias do lote 1 cruzadas nas duas classificações:

| Tamanho | F | M | D | A | Total |
|---|---|---|---|---|---|
| P (\|A_r\| ≤ 2·10⁴) | 21 | 0 | 3 | 9 | 33 |
| M (≤ 2·10⁵) | 10 | 2 | 1 | 10 | 23 |
| G (> 2·10⁵) | 4 | 3 | 0 | 7 | 14 |

As duas classificações separam mal as mesmas instâncias: 9 das 33 pequenas ficam em A, e
7 das 14 grandes são resolvidas até o ótimo. O caso extremo é `urb-apia-m25-f2`, com |A_r| = 1 934 384
arcos (o maior do lote) e ótimo provado em 70 s, contra `puc-hc9u-seed-r1`, com |A_r| = 4 608 e gap de
22% ao fim dos 600 s.

Medianas por classe de dificuldade:

| Classe | Instâncias | UB mediana | m mediana | \|A_r\| mediana |
|---|---|---|---|---|
| F | 35 | 4 | 19 | 5 262 |
| M | 5 | 6 | 25 | 483 196 |
| D | 4 | 48,5 | 94,5 | 7 424 |
| A | 26 | 41 | 72 | 29 611 |

O que separa as classes é o **valor da solução** (número de estações) e o **número de robôs**, não o
tamanho do modelo: F e M têm ótimo de um dígito; D e A têm dezenas ou centenas de estações.
A classe M é justamente a de maior |A_r| mediana. A leitura é que o custo está na árvore de
branch-and-bound (o número de estações a decidir e a simetria entre elas), não no tamanho da
relaxação linear. Isso é coerente com Das, que é NP-difícil já com r = 1: a dificuldade não vem do
alcance.

### 6.2 Resultado: o regime R-c não produz instâncias difíceis

| Regime | F | M | D | A | Total |
|---|---|---|---|---|---|
| R-a (alcance longo) | 7 | 2 | 3 | 15 | 27 |
| R-b (terminais densos) | 9 | 0 | 1 | 8 | 18 |
| R-c (alcance denso) | 17 | 2 | 0 | 0 | 19 |
| misto | 2 | 1 | 0 | 3 | 6 |

Nenhuma das 19 instâncias R-c fica em D ou A: com alcance denso o ótimo é pequeno (2 a 4 estações
nas instâncias urbanas e PACE) e o COMP o prova rapidamente. As instâncias difíceis concentram-se em
R-a (15 de 27 em A).

Isso delimita o resultado A2 do E8, obtido em `cc12-2p` (R-c, extensão ponderada), em que o CBI
provou o ótimo em 7,5 s e o compacto não provou em 300 s: a vantagem do CBI em R-c foi medida numa
instância ponderada com ótimo 6. Nas instâncias R-c compatíveis com Das do lote 1, o próprio COMP
resolve tudo, de modo que esse regime não serve para separar métodos. A comparação entre COMP, BC-Y'
e CBI deve ser refeita sobre as 30 instâncias D/A, quase todas R-a e R-b.

### 6.3 Resultado: a dificuldade acompanha estações por robô (UB/m), não o tamanho do modelo

O protocolo grava `n_cortes` (tamanho de C1+C2+C4) além de UB. Normalizando os dois pelo número de
robôs m:

| Classe | `n_cortes`/m (mediana) | UB/m (mediana) |
|---|---|---|
| F | 0,90 | 0,25 |
| M | 2,11 | 0,16 |
| D | 1,95 | 0,85 |
| A | 2,00 | 0,67 |

As instâncias fáceis compartilham estações de forma intensa (uma estação serve, em mediana, uns
4 robôs); as difíceis se aproximam de uma estação por robô. A densidade de cortes estáticos por
robô **não** separa as classes — as instâncias difíceis têm tantos ou mais cortes por robô que as
fáceis, então a dificuldade não vem de os cortes estarem ausentes.

A leitura é mecânica: as desigualdades de cobertura com RHS 1 (C1, C2, C4) exprimem "este conjunto
precisa de pelo menos 1 estação", mas não "precisa de δ estações" quando δ robôs distintos passam
por ali sem poder compartilhar — é o regime sem compartilhamento (família F1, §2.3 de
`direcoes-pli-min-station.md`), onde o LP erra por um fator próximo de m. Dentro das 30 D/A há
inclusive dois sub-regimes: 5 instâncias com UB/m ≥ 1,0 (praticamente uma estação por robô, todas
MAPF/`pucn`) e 11 com UB/m < 0,5 (mais compartilhamento, mas ainda insuficiente para o COMP
fechar). O fechamento da linha B2 ("reforço do núcleo não move o LB", medido em `hc*`, onde
C1=C2=C4) não se transfere a este regime — é candidato natural a cortes de multiplicidade (C6,
§5.6 de `direcoes-pli-min-station.md`).

## 7. Lote 1: composição e resultados de referência

70 instâncias em 9 famílias, todas compatíveis com Das e nenhuma trivial (r < λ\* em todas).
Resultados completos em `results/benchmark/dificuldade_v1_fatia{1,2}.csv`; o manifesto repete
dificuldade, LB e UB por instância.

| Família | Instâncias | n | \|A_r\| | r | F | M | D | A |
|---|---|---|---|---|---|---|---|---|
| `mapf` | 13 | 666–5699 | 9 192 – 602 328 | 2–18 | 2 | 1 | 0 | 10 |
| `pace2018` | 6 | 74–1011 | 2 360 – 244 714 | 3–15 | 4 | 1 | 0 | 1 |
| `puc` | 18 | 512–4096 | 4 608 – 179 200 | 1–3 | 5 | 0 | 4 | 9 |
| `pucn` | 6 | 64–2187 | 384 – 214 326 | 1–2 | 3 | 0 | 0 | 3 |
| `steinlib-b` | 8 | 50–100 | 300 – 4 996 | 1–3 | 8 | 0 | 0 | 0 |
| `steinlib-i` | 6 | 80–160 | 878 – 5 262 | 1–3 | 6 | 0 | 0 | 0 |
| `steinlib-lin` | 4 | 484–649 | 13 808 – 62 952 | 6–21 | 4 | 0 | 0 | 0 |
| `urbano` | 5 | 1345–2306 | 363 730 – 1 934 384 | 19–71 | 3 | 2 | 0 | 0 |
| `vienna` | 4 | 1991–3898 | 381 600 – 790 270 | 8–13 | 0 | 1 | 0 | 3 |

As famílias `steinlib-b`, `steinlib-i` e `steinlib-lin` são inteiramente F e as urbanas são F ou M:
servem de conjunto de regressão rápido, não de conjunto de comparação. A dificuldade está em `puc`,
`pucn`, `mapf` e `vienna`.

### 7.1 Instâncias D e A (referência para os próximos experimentos)

LB e UB do protocolo da §6 ao fim dos 600 s; o gap é o do Gurobi. Não são ótimos provados, salvo
onde indicado em outra fonte.

| Instância | Regime | n | m | r | \|A_r\| | LB | UB | gap | Classe |
|---|---|---|---|---|---|---|---|---|---|
| `puc-w3c571-seed-r1` | R-b | 3997 | 1142 | 1 | 20 556 | 665 | 1139 | 42% | A |
| `puc-cc12-2u-seed-r1` | R-a | 4096 | 236 | 1 | 49 148 | 165 | 200 | 18% | A |
| `puc-hc12p-seed-r1` | R-b | 4096 | 1024 | 1 | 49 152 | 171 | — | — | A |
| `puc-w23c23-seed-r1` | R-b | 1081 | 276 | 1 | 6 348 | 141 | 158 | 11% | A |
| `puc-hc11p-seed-r1` | R-b | 2048 | 512 | 1 | 22 528 | 95 | 156 | 39% | A |
| `mapf-warehouse-10-20-10-2-1-m50-f8` | R-a | 5699 | 50 | 4 | 144 984 | 81 | 126 | 36% | A |
| `puc-cc11-2u-seed-r1` | R-a | 2048 | 122 | 1 | 22 526 | 92 | 102 | 10% | D |
| `puc-hc10p-seed-r1` | R-b | 1024 | 256 | 1 | 10 240 | 52 | 81 | 36% | A |
| `pucn-cc7-3n-seed-r1` | R-a | 2187 | 111 | 1 | 30 616 | 68 | 80 | 15% | A |
| `mapf-random-32-32-10-m50-f8` | R-a | 922 | 50 | 2 | 9 192 | 54 | 71 | 24% | A |
| `mapf-random-64-64-20-m100-f4` | R-a | 3270 | 100 | 5 | 121 632 | 41 | 67 | 39% | A |
| `puc-cc10-2u-seed-r1` | R-a | 1024 | 67 | 1 | 10 240 | 53 | 58 | 9% | D |
| `mapf-warehouse-10-20-10-2-1-m25-f4` | R-a | 5699 | 25 | 9 | 602 328 | 29 | 53 | 45% | A |
| `puc-bip42p-regiao-f2` | R-b | 1200 | 100 | 1 | 7 964 | 33 | 43 | 23% | A |
| `puc-bip42p-seed-r1` | R-b | 1200 | 100 | 1 | 7 964 | 33 | 43 | 23% | A |
| `puc-hc9u-seed-r1` | R-b | 512 | 128 | 1 | 4 608 | 32 | 41 | 22% | A |
| `puc-hc9u-regiao-f4` | R-b | 512 | 128 | 1 | 4 608 | 36 | 39 | 8% | D |
| `puc-cc9-2p-seed-r1` | R-a | 512 | 32 | 1 | 4 608 | 30 | 31 | 3% | D |
| `pucn-cc3-10n-seed-r1` | R-a | 1000 | 25 | 1 | 27 000 | 17 | 26 | 35% | A |
| `mapf-random-32-32-10-m25-f4` | R-a | 922 | 25 | 4 | 28 606 | 14 | 21 | 33% | A |
| `mapf-room-32-32-4-m25-f4-rho` | R-a | 682 | 25 | 5 | 16 206 | 16 | 20 | 20% | A |
| `vienna-I065-intercalado-f2` | misto | 3898 | 72 | 8 | 392 398 | 16 | 20 | 20% | A |
| `mapf-empty-32-32-m25-f4` | R-a | 1024 | 25 | 4 | 37 180 | 13 | 19 | 32% | A |
| `vienna-I065-regiao-f4` | R-a | 3898 | 72 | 11 | 790 270 | 14 | 19 | 26% | A |
| `mapf-room-32-32-4-m10-f8` | R-a | 682 | 10 | 4 | 11 622 | 16 | 18 | 11% | A |
| `mapf-den312d-m25-f4` | R-a | 2445 | 25 | 9 | 249 528 | 15 | 17 | 12% | A |
| `pucn-cc7-3n-regiao-f2` | misto | 2187 | 111 | 2 | 214 326 | 9 | 13 | 31% | A |
| `pace18-t2-141-regiao-f4` | R-a | 294 | 19 | 3 | 7 354 | 10 | 12 | 17% | A |
| `vienna-I056-regiao-f4` | R-a | 1991 | 25 | 12 | 381 600 | 9 | 12 | 25% | A |
| `mapf-den312d-m50-f2-rho` | misto | 2445 | 50 | 16 | 549 696 | 6 | 9 | 33% | A |

`puc-hc12p-seed-r1` é a única instância em que o COMP não encontra nenhum incumbente em 600 s. Como
o protocolo roda sem solução inicial, isso mede o solver puro; com a heurística primal de
`experiments/cuts/primal.py` a instância tem solução viável.

### 7.2 Lacunas frente aos critérios de maturidade (§10 do plano)

Atendidos: 70 instâncias compatíveis com Das em 9 famílias topológicas (alvo: ≥ 60 e ≥ 5); classes
P/M/G com 33, 23 e 14 instâncias (alvo: ≥ 5 cada); 30 instâncias D/A (alvo: ≥ 10); S∩T ≠ ∅ em cinco
instâncias de quatro famílias (alvo: ≥ 1 família); manifesto completo; regeração reproduz os SHA-256;
divisão desenvolvimento/avaliação fixada (1 de cada 3 por família, em ordem de nome).

Pendentes:

1. A classe D tem 4 instâncias (alvo: 5). É um efeito da definição: o gap de 10% é uma faixa
   estreita entre provar o ótimo e não chegar perto.
2. `pucn` tem só dois níveis de r (1 e 2) — o alvo é 3 por família. Os grafos PUCN de cobertura de
   código têm diâmetro pequeno, então λ\* é baixo e R-FRAC:4 cai em r = 1.
3. Faltam as três seeds nas instâncias D/A (§10 pede 3 seeds). O protocolo atual usa só a seed 42.
4. Falta a tag de versão que congela o benchmark-v1.
