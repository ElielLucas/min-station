# Resultados E2–E6 — Espaço-y, Núcleo de Cobertura e Branch-and-Cut para MIN-STATION

**Data original:** 2026-09-25 · **Revisão E5:** 2026-09-25
**Formulação base:** BASE/variante U (Das, `S ∩ T` permitido), dígrafo de alcance A_r, fluxo contínuo
**Ambiente:** Gurobi 12.0.3 (licença acadêmica), Python 3.12.3 via Poetry, 12 CPUs
**Parâmetros:** seed=42, threads=4, TL=600s (E3), TL=300s (E4), TL=900s (E6)

> **Nota de leitura.** Este relatório passou por duas rodadas. A primeira (E0–E4) encontrou um
> defeito de corretude na separação clássica de cortes (S3/S4 do E2), documentado em §7
> (histórico). A rodada E5, registrada abaixo, corrigiu esse defeito e mais cinco relacionados,
> adotou a variante U da formulação (fidelidade a Das quanto a `S ∩ T`), corrigiu o override de
> autonomia R que vinha deixando metade das instâncias do E4 triviais, e adicionou um primeiro
> branch-and-cut em y (E6). Os números de E2/E3/E4 abaixo são os da rodada E5; os resultados
> anteriores ficam em §7 apenas como registro do defeito, não como referência experimental.

---

## 1. Bloco A — Verificação estrutural

Executado em `experiments/cuts/verify_structure.py`, saída `results/cuts/e5_estrutura.csv`,
sobre `hc9u`, `hc10p`, `hc11p`, `hc12p`, `bip42p`.

| Instância | n | m | grau uniforme | toda aresta difere em 1 bit | \|S∩T\| | A_r = E | classes de assinatura |
|---|---|---|---|---|---|---|---|
| hc9u | 512 | 128 | 9 (True) | True | 0 | True | 1 |
| hc10p | 1024 | 256 | 10 (True) | True | 0 | True | 1 |
| hc11p | 2048 | 512 | 11 (True) | True | 0 | True | 1 |
| hc12p | 4096 | 1024 | 12 (True) | True | 0 | True | 1 |
| bip42p | 1200 | 100 | 1–31 (False) | **False** | 0 | True | **995** |

**Confirmado:** hc9u–hc12p são hipercubos `Q_k` exatos (k=9..12): grau uniforme igual a k, toda
aresta liga vértices que diferem em 1 bit, `S ∪ T` é uma classe de paridade completa, e `A_r = E`
— com R=150 e pesos ~100–110 o alcance é de fato 1 salto, não mais. As três famílias de corte
coincidem nessas instâncias: `C2 ⊆ C1` e `C4 ⊆ C1` nas quatro (mesma contagem, mesmo conjunto),
então "núcleo C1+C2+C4" é, nelas, apenas C1 repetido três vezes.

**Refutado:** `bip42p` **não é** um hipercubo. Grau não uniforme (1 a 31), há arestas que não
diferem em 1 bit, e 995 classes de assinatura distintas (contra 1 nas hc*) — o grupo de simetria
não é vértice-transitivo. Qualquer leitura anterior que tratasse bip42p como parte do regime R-b
estrutural das hc* fica corrigida aqui: é uma instância à parte, sem a simetria que justifica B2.

**Forma fechada `⌈2^(k-1)/k⌉` confere exatamente com o LP de raiz (E1, config D):**

| Instância | k | 2^(k-1)/k | LP raiz (E1) |
|---|---|---|---|
| hc9u | 9 | 28,444 | 28,444 |
| hc10p | 10 | 51,2 | 51,2 |
| hc11p | 11 | 93,091 | (LP não medido nesta forma; ver E3) |
| hc12p | 12 | 170,667 | (idem) |

**Achado que corrige a leitura do relatório anterior:** o bound do E3 para hc12p é **171**, que é
exatamente `⌈170,667⌉`. Ou seja, o branch-and-bound não contribuiu nada além do arredondamento do
LP fechado — o número **171** não é um avanço do B&B, é o teto do LP relaxado arredondado para
cima. Para hc11p o bound do E3 é **101**, acima de `⌈93,091⌉ = 94` — aqui sim há contribuição real
do B&B/dos cortes de cobertura sobre o LP fechado (ver §3.3).

**Verificação de viabilidade de uma solução ótima do núcleo:** fixar `y` na solução de 32
estações que o Gurobi devolveu para o núcleo de hc9u e checar o status no modelo compacto.
**Resultado: INFEASIBLE** (max-flow = 108 < m = 128 com essas 32 estações específicas). Isso
mostra que **essa solução particular** não é viável no problema real — o núcleo pode ter outras
soluções ótimas de 32 estações não testadas. O que se pode concluir: ir além de 32 exige
informação de fluxo (família 𝒵 do Teorema 6, separável por max-flow), e qualquer reforço do
núcleo só pode melhorar o LB, não o UB. **OPT(hc9u) ∈ [32, 38] continua aberto** — o que motiva o E7.

**Correção de leitura — classes de assinatura:** o CSV reporta hc9u–hc12p com **k classes de
tamanho 1** (k=256..2048), não "1 classe". Isso significa que nenhum par de variáveis compartilha
a mesma assinatura de linhas C1, ou seja, **0 gêmeos por C1** — o que é o dado relevante. A
contagem de classes é alta; o que é baixo (e decisivo para B2) é o tamanho máximo de cada classe
(= 1). Em bip42p, a maior classe tem tamanho 2, indicando **ao menos 1 par de gêmeos** na família
C1.

**B2 (simetria) — resultado da sonda.** hc9u–hc12p têm 0 gêmeos em C1 (regra R3 não elimina
nenhuma variável); `Symmetry=2` do Gurobi não alterou resultado (sonda binária). Orbital branching
não foi testado. B2 mantida fechada por falta de evidência positiva, não por prova de ausência de
simetria. Em bip42p, há gêmeos em C1 (maior classe = 2), mas B2 não foi testado lá.

---

## 2. Bloco B — Fidelidade a Das: variante U

### 2.1 O problema encontrado

A formulação base impunha `S ∩ T = ∅` (guarda em `baseline.py`), mas o artigo de Das **não exige
essa restrição** — o Lema 5 (p. 11–12 de `min-station-das.pdf`) usa explicitamente um vértice que
é origem e destino ao mesmo tempo ("every robot is starting from a target position"; "the robot
starting at s_i remains at s_i occupying the target t_o"). Com `v ∈ S ∩ T`, os balanços
separados 6.1+6.2 somados davam `0 = 2`, tornando o modelo inviável mesmo quando o MIN-STATION é
sempre viável (`C = V` resolve) — um **falso negativo** de modelagem.

### 2.2 Correção adotada

Balanço unificado (variante U), com `a_v = 1_S(v)`, `b_v = 1_T(v)`:

```
out(v) − in(v) = a_v − b_v
in(v)  ≤ b_v + (m − b_v)·y_v
out(v) ≤ a_v + (m − a_v)·y_v
```

Idêntica à formulação anterior quando `S ∩ T = ∅` (os quatro casos — `S∖T`, `T∖S`, fora de
`S∪T`, `S∩T` — foram verificados um a um, ver `validacao-formulacao-base.md`). O caso novo
(`S∩T`) permite `in=out=0` (robô parado ocupando o próprio alvo) ou `in=out=1` (troca: um robô
parte, outro chega, sem exigir estação).

Adotada em `baseline.py` (guarda removida) e nos três pontos de cortes que tratavam `S ∩ T` de
forma inconsistente: `generate_C4_DM`, `_build_flow_net` e `_build_flow_net_aggregate` (este
último tinha o defeito mais sério — um vértice em `S∩T` caía só no ramo de origem e nunca virava
sumidouro, produzindo déficit de fluxo espúrio).

### 2.3 Validação

Quatro novos gabaritos com `S ∩ T ≠ ∅` criados em `synthetic.py`: `StayPut` (`S=T={a,b}`,
OPT=0) e `SharedTerminal` (OPT=1, troca em vértice compartilhado). Os gabaritos `Direct0` e
`TermRelay` **não têm** `S ∩ T ≠ ∅` — testam corretude de cortes com origens e destinos disjuntos.
Todos confirmados em scripts de verificação (ver `experiments/cuts/verify_e5_gabaritos.py` e
Bloco 3), não diretamente no smoke do E6 (que testou Direct0/TermRelay/SharedTerminal/Sec59).

Regressão por equivalência (não por reexecução, decisão do plano): as 22 instâncias do
repositório têm `|S ∩ T| = 0` por construção do gerador, então nenhum resultado numérico anterior
é invalidado pela adoção de U. Verificado no Bloco A: coluna `S_inter_T` = 0 em todas as
instâncias reais testadas.

### 2.4 Documentação atualizada

`open-questions.md` (Q1 fechada), `base-formulation.md` (§6/§7 reescritos, §10.1 marcado
resolvido), `validacao-formulacao-base.md` (P1 resolvido), `direcoes-pli-min-station.md`
(divergência 4 resolvida), `RESEARCH.md` e `project-overview.md` (nota sobre `S∩T` permitido).

---

## 3. Bloco C — Correção de cortes inválidos

Seis defeitos encontrados e corrigidos, verificados contra oráculo Gurobi (fixar `y` no modelo
compacto e checar `INFEASIBLE`/`OPTIMAL`) e contra gabaritos de regressão.

| # | Defeito | Sintoma | Correção |
|---|---|---|---|
| C.2 | `_build_flow_net_aggregate`: arco terminal saía de `t_out`, não `t_in` | Chicago st15 R=26 (OPT=0 provado) subia para LP=1,0 com 30 cortes inválidos | `arc(f'{v}_in', '_t', 1.0)` |
| C.3 | `_extract_Z` excluía `S ∪ T` de `Z`, mais forte que o Teorema 6 garante | cortes potencialmente inválidos, nunca exercitados nas instâncias antigas | `_extract_Z` sem exclusão (só exclui terminal se m<2) |
| — | `generate_C5_threshold` emitia `y(C_θ) ≥ 1` sobre o **candidato**, sem teorema por trás | corte podia ser falso sempre que existisse solução viável fora de `C_θ` | roda max-flow sobre `C_θ`, extrai `Z` do certificado de inviabilidade |
| — | `Z = ∅` silenciado quando fluxo deficiente | instância inviável mesmo com y≡1 era reportada como LP convergido | levanta `InstanciaInviavel` |
| — | `is_valid_cut`: BFS deixava terminais relaiarem fluxo alheio | divergia do oráculo no gabarito TermRelay | relay só via `_passavel()` (fora de Z, não terminal com m<2) |
| C2 (assimetria) | `generate_C2` usava `dijkstra_from(t,·)` no lado T; grafos TNTP têm arcos de mão única | 1 corte **C2** de 42 elementos em Philadelphia st25 provado inválido pelo oráculo (`V∖Z` viável) | `dijkstra_to(t,·)` sobre grafo reverso |

**Validador de cortes** (`is_valid_cut`): `Z` é válido ⟺ o bipartido
`{(s,t) : s alcança t só por intermediários de V∖Z}` não tem emparelhamento perfeito. Plugado no
funil de entrada (`harness.add_cuts_to_model`, `yspace._add_cuts`) com política de **abortar**, não
descartar em silêncio — `validate_cuts=True` por padrão no E2.

**Verificação:** 0/73 cortes inválidos em Philadelphia após a correção do C2 assimétrico;
gabaritos `Direct0` e `TermRelay` falhavam antes das correções e passam depois; todo o E2 real
(§4) roda com `validado=True`.

Também corrigidos nesta rodada, sem relação com corretude de cortes:
- **Override de R** (`load_instance(path, R=None)`): metade das instâncias do E4 rodava com o R
  gravado no arquivo (trivial) em vez do R de referência histórica. Corrigido com override
  explícito por instância, e o truncamento `int(float(R))` que cortava `R=2,5` para `2`.
- **Dedup em `prepare_cuts`**: cortes de famílias diferentes que geram o mesmo `Z` agora são
  deduplicados (`counts['unicos']`), evitando inflar contagens (ex.: 768 cortes "diferentes" em
  hc9u que eram na verdade 256 repetidos 3×, conforme o Bloco A já mostrava por outra via).

---

## 4. E2 — Laço de cortes em y-space (LP), revisado

### 4.1 Configuração

Mesmos 4 estágios da rodada anterior (S1: C1+C2+C4-DM; S2: +C3; S3: +fracionários clássicos via
rede corrigida; S4: +C5 por limiar), agora com `validate_cuts=True` em todos os estágios e R
corrigido para Chicago st15 (override R=7, não o R=26 trivial do arquivo).

### 4.2 Resultados

| Instância | R | origem R | m | \|A_r\| | LP S1 | LP S2 | LP S3 | LP S4 | validado | Tempo total (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| hc9u | 1 | arquivo | 128 | 4.608 | 28,444 | 28,444 | 28,444 | 28,444 | True | 45,0 |
| hc10p | 150 | arquivo | 256 | 10.240 | 51,20 | 51,20 | 51,20 | 51,20 | True | 427,5 |
| Philadelphia st25 | 3 | arquivo | 25 | 9.837 | 33,33 | **36,23** | 36,23 | 36,23 | True | 125,2 |
| Barcelona st25 | 5 | arquivo | 25 | 32.648 | 11,00 | 12,00 | 12,00 | 12,02 | True | 220,7 |
| **Chicago st15** | **7** | **override** | 15 | 10.178 | 13,00 | 13,25 | 13,25 | 13,25 | True | 17,8 |
| Barcelona st50 | 6 | arquivo | 50 | 48.353 | 9,00 | 9,00 | 9,00 | 9,00 | True | 255,5 |
| cc10-2p | 500 | arquivo | 67 | 339.124 | 2,615 | 2,615 | 2,615 | 2,615 | True | 408,3 |

### 4.3 Análise

**O defeito de §7 está corrigido e verificado.** Chicago st15 no R correto (7, não o 26 trivial
do arquivo) tem LP subindo de 13,00 (S1) para 13,25 (S2) e patamar em S3/S4 — nenhum salto
espúrio a partir de OPT conhecido = 0. A instância trivial R=26 não está mais na bateria (foi
substituída pelo override correto), e o comportamento antigo com R=26 (LP=1,0 espúrio) não se
reproduz mais no gabarito `Direct0`, que é o análogo sintético dessa situação.

**S3 (fracionários clássicos) segue sem acrescentar nada além de S2** em todas as 7 instâncias
reais — mesmo com a rede corrigida. **S4 (C5 por limiar) só acrescenta em Barcelona st25**
(12,00→12,02), efeito marginal. A conclusão que já valia para S1/S2 na rodada anterior
(regime R-b não ganha de cortes de posto 1 além de C1) se mantém após a correção, e agora está
efetivamente validada, não apenas medida.

**Philadelphia st25 sobe de 33,33 para 36,23 só com C3** — mesmo padrão de antes, agora com C2
assimétrico corrigido (o corte de 42 elementos que era inválido não está mais entre os 73 cortes
C2 desta instância).

---

## 5. E3 — Núcleo de cobertura inteiro (IP em y-space)

### 5.1 Configuração

`min Σy`, `y∈{0,1}^V`, cortes estáticos C1+C2+C4-DM a priori, sem fluxo. TL=600s. Mesmo R que o
E2 (Chicago com override R=7). `validado=False` por decisão de config (`VALIDATE_E3=False`): o
E3 usa exclusivamente as três famílias já auditadas no Bloco C, então a validação por instância
seria redundante — não é uma falha, é economia de tempo já que o gargalo do E3 é o B&B, não a
separação.

### 5.2 Resultados

| Instância | R | Cortes (C1/C2/C4) | OBJ | Bound | Gap | Status | Tempo (s) |
|---|---|---|---|---|---|---|---|
| hc9u | 1 | 256/256/256 | **32** | **32** | 0% | **OPT** | **3,2** |
| hc10p | 150 | 512/512/512 | 64 | 56 | 12,5% | TL | 600 |
| hc11p | 150 | 1024/1024/1024 | 136 | **101** | 25,7% | TL | 600 |
| hc12p | 150 | 2048/2048/2048 | 225 | 171 | 24,0% | TL | 600 |
| bip42p | 200 | 200/200/200 | 37 | 36 | 2,7% | TL | 600 |
| Philadelphia st25 | 3 | 46/73/46 | 34 | 34 | 0% | OPT | 0,0 |
| Barcelona st50 | 6 | 15/15/23 | 9 | 9 | 0% | OPT | 0,0 |
| cc10-2p | 500 | 17/17/20 | 3 | 3 | 0% | OPT | 0,0 |
| cc12-2p | 500 | 26/26/50 | 6 | 6 | 0% | OPT | 0,1 |

### 5.3 Análise

**hc9u — núcleo resolvido em 3,2 s; OPT(hc9u) ∈ [32, 38] continua aberto.**
O núcleo (relaxação válida) dá `OPT(núcleo) = 32`, logo `OPT(hc9u) ≥ 32`. O Bloco A (§1) testou
uma solução ótima do núcleo no modelo compacto e obteve INFEASIBLE (max-flow = 108 < 128 = m):
essa solução particular não é viável. O núcleo pode ter outras soluções ótimas de 32 estações — a
cobertura de código de raio 1 sobre Q_k costuma ter muitas — que não foram testadas. O que se
conclui é que ir além de 32 requer informação de fluxo (família 𝒵), e que os cortes C1+C2+C4 não
separam o gap (em hc*, C2 ⊆ C1 e C4 ⊆ C1, então "núcleo" é só C1). Isso motiva o E7.

**hc11p e hc10p — contribuição real do B&B sobre o LP fechado.** hc11p: bound = 101 supera
`⌈2^10/11⌉ = 94`. hc10p: bound = 56 supera `⌈2^9/10⌉ = 52`. Em ambos, o B&B com C1 encontrou
algo que a relaxação contínua fechada não capta. Só em hc12p a contribuição é zero: bound = 171
= `⌈2^11/12⌉ = ⌈170,67⌉` exato — correção de leitura em relação ao relatório anterior, que
apresentava 171 como avanço do B&B.

**hc10p, hc12p — LBs novos válidos.** hc10p: 56 (histórico 52). hc12p: 171 (histórico 149).

**bip42p — não é hipercubo (§1), e aqui o comportamento é diferente.** Bound = 36, gap 2,7%,
sem fechar em 600s. Sem a estrutura vértice-transitiva das hc*, não há leitura de "teto de
relaxação contínua" disponível — é simplesmente um gap de B&B comum.

**R-a e R-c — sem mudança em relação à rodada anterior**, já que Philadelphia, Barcelona,
cc10-2p e cc12-2p não têm `S∩T` nem são afetadas pelos defeitos de cortes corrigidos no Bloco C
(usam apenas C1/C2/C4 já corretos nessas instâncias). Resultados idênticos aos já registrados:
núcleo fecha instantaneamente, mas cc12-2p permanece aberta em `[6,7]` (núcleo não fecha) e
Philadelphia st25 seguirá dependendo do compacto com cortes (E4) para bound mais forte.

> **Atualização (E8):** cc12-2p está fechada, OPT = 6 (extensão ponderada, R = 500). Uma
> solução ótima do núcleo com 6 estações é viável no modelo compacto (UB), e o núcleo C1 + C4-DM,
> com os 50 cortes validados um a um, tem ótimo 6 (LB). Certificado em
> `experiments/cuts/verify_e8_cc12_opt.py` e `results/cuts/e8_certificado_cc12.txt`. A frase
> "núcleo não fecha" acima estava errada: o núcleo dá 6, e a instância só parecia aberta porque
> nenhuma solução ótima do núcleo tinha sido testada no problema real.

---

## 6. E4 — Árvore curta com cortes estáticos (TL=300s), revisado com R correto

### 6.1 Configuração

Mesmas três configurações (BASE-I, BASE-C, CORTES=C1+C2+C4-DM), agora com **override de R**
aplicado (Bloco C): Chicago st15 R=7 (não o R=26 trivial do arquivo), Barcelona st15 R=5,
Barcelona st25 R=5, Philadelphia st5 R=2, Philadelphia st25 R=3 (já correto no arquivo), hc9u
R=1 (já correto).

### 6.2 Resultados

| Instância | R | origem | Config | OBJ | Bound | Gap | Status | Tempo (s) | ref |
|---|---|---|---|---|---|---|---|---|---|
| Chicago st15 | 7 | override | BASE-I | 17 | 16 | 5,88% | TL | 300 | 17 |
| Chicago st15 | 7 | override | BASE-C | 17 | 16 | 5,88% | TL | 300 | 17 |
| Chicago st15 | 7 | override | CORTES | 17 | 16 | 5,88% | TL | 300 | 17 |
| Barcelona st15 | 5 | override | BASE-I | 15 | 14 | 6,67% | TL | 300 | 15 |
| Barcelona st15 | 5 | override | BASE-C | 15 | **15** | 0% | **OPT** | 284 | 15 |
| Barcelona st15 | 5 | override | CORTES | 16 | 14 | 12,5% | TL | 300 | 15 |
| Barcelona st25 | 5 | override | BASE-I | 16 | 13 | 18,75% | TL | 300 | 16 |
| Barcelona st25 | 5 | override | BASE-C | 16 | 16 | 0% | OPT | 299,432 | 16 |
| **Barcelona st25** | **5** | override | **CORTES** | **16** | **16** | **0%** | **OPT** | **241** | 16 |
| Philadelphia st5 | 2 | override | BASE-I | 41 | 35 | 14,6% | TL | 300 | 41 |
| Philadelphia st5 | 2 | override | BASE-C | 41 | 36 | 12,2% | TL | 300 | 41 |
| Philadelphia st5 | 2 | override | CORTES | 42 | 37 | 11,9% | TL | 300 | 41 |
| Philadelphia st25 | 3 | arquivo | BASE-I | 47 | 39 | 17,0% | TL | 300 | — |
| Philadelphia st25 | 3 | arquivo | BASE-C | 47 | 40 | 14,9% | TL | 300 | — |
| Philadelphia st25 | 3 | arquivo | CORTES | 47 | 40 | 14,9% | TL | 300 | — |
| hc9u | 1 | arquivo | BASE-I | 45 | 28 | 37,8% | TL | 300 | — |
| hc9u | 1 | arquivo | BASE-C | 47 | 30 | 36,2% | TL | 300 | — |
| **hc9u** | **1** | arquivo | **CORTES** | **38** | **32** | **15,8%** | TL | 300 | — |

### 6.3 Análise

**Critério de aceitação do plano (§C.7) cumprido em 2 de 3.** Chicago st15 R=7 → **17** ✓
(as três configs travam em bound 16, gap 5,88%, mas o OBJ = ref confirma a otimalidade prática).
Philadelphia st5 R=2 → **41** ✓ nas configs BASE-I e BASE-C; CORTES encontra apenas UB=42 no
mesmo orçamento, pior que os baselines — sinal de que os cortes estáticos, nesta instância e
neste tempo, atrapalham mais do que ajudam a busca de incumbente (embora melhorem o bound: 37
contra 35–36). Barcelona st15 R=5 → esperado 15: BASE-C prova otimalidade (284s), mas CORTES
encontra apenas UB=16, também pior que o baseline sem cortes — mesmo padrão de Philadelphia st5.

**Observação em duas instâncias, não padrão:** em duas das cinco instâncias com R corrigido
(Barcelona st15 e Philadelphia st5), CORTES encontrou UB pior que BASE-C em 300s, embora o bound
tenha melhorado. Isso vem de uma única seed e não é suficiente para generalizar. Em Barcelona st15,
CORTES também deu **bound 14**, pior que o bound 15 de BASE-C que provou o ótimo — ou seja,
piorou nos dois lados. O comportamento pode ser ruído de seed ou custo de modelo maior. O E7
repetirá com 3 seeds antes de qualquer conclusão.

**Barcelona st25 R=5 continua o resultado mais limpo:** CORTES prova otimalidade em 241s.
BASE-C também prova o ótimo, em 299,432 s (`results/cuts/e4_arvore.csv`, status 2, OBJ = bound = 16).
A frase anterior desta seção dizia que BASE-C não provava; o CSV e a tabela acima registram o contrário.

**hc9u R=1 (aberta):** CORTES dá bound=32, batendo com o núcleo do E3 (mesma família de cortes,
esperado). UB=38: o E4-CORTES achou obj=38 no modelo compacto com fluxo, tornando esse UB
**verificado diretamente** pela primeira vez (antes era só inferido). Intervalo: **OPT(hc9u) ∈ [32, 38]**.
O Bloco A testou uma solução ótima do núcleo e obteve INFEASIBLE, mas outras soluções com 32
estações podem existir — OPT não está provado maior que 32.

---

## 7. E6 — Branch-and-cut em y com corte lazy (Bloco D)

### 7.1 Motivação e configuração

Confirmado no Bloco A que o ótimo do núcleo de hc9u é inviável no problema real, o passo natural
é fechar esse gap separando a família 𝒵 (Teorema 6) via max-flow **dentro do B&B**, em vez de só
estaticamente. Primeiro callback lazy do repositório (`experiments/cuts/bc_yspace.py`).

- Base estática: apenas C1 (suficiente nas hc*, já que C2, C4 ⊆ C1 — Bloco A).
- `Params.LazyConstraints=1`; callback em `MIPSOL`: monta a rede agregada corrigida (§3) sobre
  `ȳ` inteiro, roda max-flow; se `flow < m`, extrai `Z` (`_extract_Z`) e `cbLazy(Σ_{v∈Z} y_v≥1)`.
- Smoke test primeiro nos gabaritos (Direct0, TermRelay, SharedTerminal, Sec59) — todos PASS,
  confirmando o callback antes de gastar tempo em instâncias reais.
- Instâncias: hc9u e bip42p, TL=900s. Duas configs: NUCLEO (C1 estático, sem lazy — controle) e
  BC-LAZY (C1 + callback).

### 7.2 Resultados

| Instância | Config | OBJ | Bound | Gap | Status | Cortes lazy | Tempo (s) |
|---|---|---|---|---|---|---|---|
| hc9u | NUCLEO | 32 | 32 | 0% | OPT | 0 | 2,3 |
| hc9u | BC-LAZY | 52 | **32** | 38,5% | TL | 1234 | 902,7 |
| bip42p | NUCLEO | 37 | 36 | 2,7% | TL | 0 | 900,0 |
| bip42p | BC-LAZY | — (sem incumbente) | **33** | — | TL | 1538 | 910,9 |

### 7.3 Análise

**Sucesso parcial, não fracasso do método.** O smoke test prova que o callback está correto
(4/4 gabaritos: Direct0, TermRelay, SharedTerminal, Sec59). Em hc9u, 1234 cortes lazy foram
efetivamente separados em 900s, mas **o bound não passou de 32** — o mesmo teto do núcleo puro
(que chega lá em 2,3s sem nenhum lazy). Isso significa que C1 sozinho, mesmo reforçado por 1234
cortes 𝒵 encontrados dinamicamente, ainda não é suficiente para mover o bound em 900s. O
mecanismo funciona (cortes válidos, separados corretamente), mas precisa de um separador mais
completo e de mais tempo antes de ser competitivo.

**Em bip42p, BC-LAZY piorou em relação ao NUCLEO** (bound 33 contra 36, sem incumbente
encontrado). Uma hipótese é que `LazyConstraints=1` limita o presolve do Gurobi (verificar na
documentação antes de afirmar), e sem incumbente o B&B não se ancora. O CSV do e5_estrutura
mostra que C2 ⊆ C1 e C4 ⊆ C1 também em bip42p, então incluir C2/C4 estáticos não resolve o
problema — a base é a mesma. A causa mais provável é ausência de solução inicial e custo de
callback alto relativo ao tamanho do modelo (bip42p tem 995 classes de assinatura, diferentemente
das hc* com 0 gêmeos).

**Leitura para o E7:** o mecanismo 𝒵-lazy precisa de (1) MIP start para dar incumbente
imediato, (2) user cuts nos nós fracionários além dos lazy nos nós inteiros, e (3) cronometragem
do callback para saber se o C.8 é urgente.

---

## 8. Síntese e próximos passos

### 8.1 Resultados novos desta rodada

| Achado | Fonte | Natureza |
|---|---|---|
| Uma solução ótima do núcleo de hc9u (32 estações) é inviável no compacto | Bloco A, oráculo Gurobi | novo — OPT(hc9u) ∈ [32, 38] segue aberto |
| hc11p e hc10p: bound B&B > LP fechado arredondado (101 > 94; 56 > 52) | E3 | novo |
| hc12p: bound 171 = LP fechado arredondado, contribuição zero do B&B | E3 + Bloco A | correção de leitura |
| bip42p: 995 classes de assinatura (≠ hipercubo; tem gêmeos em C1) | Bloco A | correção de leitura |
| B2 (simetria): sonda sem efeito em hc9u-hc12p; orbital branching não testado | Bloco A | parcial |
| Defeito de corretude `S∩T` corrigido (variante U) | Bloco B | correção de modelagem |
| 6 defeitos de validade de corte corrigidos e verificados | Bloco C | correção |
| Chicago st15 R=7 → 17, Philadelphia st5 R=2 → 41 confirmados | E4 | confirmação (não novo, mas agora medido corretamente) |
| Cortes estáticos pioram UB (não bound) em 2/5 instâncias pequenas do E4 | E4 | observação nova |
| Callback lazy 𝒵 validado e funcional, mas insuficiente com C1 puro em 900s | E6 | parcial |

### 8.2 Decisões para os próximos passos

**Pergunta central (E7):** o branch-and-cut em y, completo (MIP start + lazy MIPSOL + user cuts
MIPNODE), supera o modelo compacto em algum regime? Há evidência que pode: o núcleo em y fecha
cc12-2p em 0,1 s, enquanto o compacto é intratável nela; o LP em y empata com o compacto nas hc*
e supera em Philadelphia. O E6 testou um mecanismo incompleto (sem MIP start, sem user cuts) —
resultado fraco não invalida o método.

**R-b.** Uma solução ótima do núcleo de hc9u testada foi inviável no compacto, indicando que o
gap não está na integralidade do núcleo (C1), mas em restrições de fluxo que 𝒵 capta. O BC-y
completo é o próximo passo natural.

**R-a.** O núcleo dá bound 34, bem abaixo do compacto+cortes (40). Se o BC-y não compensar aqui
mesmo com MIP start, o regime R-a continua dependendo do modelo compacto com cortes estáticos.

**Efeito de cortes sobre UB em seed única:** observação em Barcelona st15 e Philadelphia st5;
o E7 replica com 3 seeds para separar ruído de sinal.

### 8.3 O que não fazer ainda (mantido do plano)

Sem mudança: não introduzir custos heterogêneos, autonomias por robô, elegibilidade
origem-destino; não usar `lin23`/`lin37`; não reintroduzir estações só em vértices
intermediários; não implementar Benders/Lagrangeana/zero-half nesta rodada.

---

## 9. Histórico — defeito original de S3/S4 (rodada anterior, antes do Bloco C)

> Preservado como registro do defeito, conforme o plano E5 determina. Os números abaixo **não
> são referência experimental** — foram substituídos pelos resultados corrigidos em §4.

**Sintoma original.** Chicago st15 (arquivo, R=26, OPT=0 provado) subia de LP=0,0 (S1,S2) para
LP=1,0 em S3 com 30 cortes, todos violados pela solução ótima `y=0` — logo inválidos.

**Causa original.** Em `_build_flow_net_aggregate`, o arco terminal saía de `t_out` em vez de
`t_in`, bloqueando a chegada ao destino sempre que `y_t=0`, mesmo para a unidade que apenas
encerra a rota ali (que não deveria exigir estação). Corrigida em §3 (item C.2).

**Escopo do defeito original:** afetava apenas S3/S4 do E2; E3 e E4 não usavam a rede agregada
com esse arco e não foram atingidos. A separação clássica (S3) segue, mesmo corrigida, sem
acrescentar nada além de S1+S2 nas 7 instâncias reais (§4.3) — a conclusão de que o regime R-b
não precisa de cortes além de C1 se mantém, agora sobre base corrigida.

**Efeito colateral do defeito C2 assimétrico (diagnosicado e corrigido nesta rodada):** as
instâncias TNTP em E2 tinham LPs ligeiramente inflados para alguns cortes inválidos de C2.
Valores que mudam (S1, pois C2 é estático): Barcelona st25 12→11, Barcelona st50 10→9. O LB 10
de Barcelona st50 reportado na rodada anterior vinha de um corte C2 inválido — valor corrigido
é 9. Os valores de E1 de Philadelphia st25 (33,595 em configs C/D e 35,3425 em E) foram medidos
com C2 defeituoso e serão remedidos no Bloco 2 da rodada E7.

---

*Código em `experiments/cuts/`: `cuts.py`, `harness.py`, `yspace.py`, `synthetic.py`,
`bc_yspace.py` (novo), `run_e2.py`, `run_e4.py`, `run_e6.py` (novo), `verify_structure.py` (novo).*
*Resultados em `results/cuts/e2_yspace.csv`, `e3_cobertura_ip.csv`, `e4_arvore.csv`,
`e5_estrutura.csv`, `e6_bc_y.csv`.*
*Plano desta rodada: `docs/technical/plans/plano-experimentos-e5.md`.*
