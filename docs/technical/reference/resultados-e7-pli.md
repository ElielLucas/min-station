# Resultados E7 — BC-y completo vs. modelo compacto

**Data:** 2026-09-26
**Formulação base:** BASE/variante U (Das, `S ∩ T` permitido), dígrafo de alcance A_r, fluxo contínuo
**Ambiente:** Gurobi 12.0.3 (licença acadêmica), Python 3.12 (Poetry, venv `projeto-mestrado`), 12 CPUs
**Parâmetros:** seed=42, threads=4, TL=300s por execução

## 1. Pergunta

O branch-and-cut só em y, **completo** (MIP start guloso + corte lazy 𝒵 no MIPSOL + user cuts
fracionários no MIPNODE), supera o modelo compacto (fluxo contínuo + C1+C2+C4 estáticos, a melhor
configuração do E4) em algum dos três regimes estudados? O E6 (relatório anterior, §7) testou um
BC-y incompleto — sem MIP start, sem user cuts, um corte lazy por incumbente — e não decidiu a
questão. Este experimento completa o mecanismo antes de julgar o método.

## 2. Extensões sobre o E6 (`bc_yspace.py`)

1. **MIP start guloso** (`_greedy_mip_start`): adiciona vértices não terminais em ordem
   decrescente de grau de saída, verificando o max-flow agregado após cada adição, com orçamento
   de tempo fixo (5s). Não avalia candidatos individualmente — isso foi tentado numa primeira
   versão (ganho marginal por candidato, até 60 avaliações por passo) e travou por mais de uma
   hora ao chegar em cc12-2p, cujo dígrafo de alcance tem quase 2,8 milhões de arcos: cada
   avaliação chama Edmonds-Karp inteiro, e O(n × avaliações) nesse tamanho é intratável. A versão
   com orçamento de tempo substitui a anterior.
2. **User cuts no MIPNODE**: separação fracionária clássica (`separate_classical_fracs`, já
   corrigida no E5) nos nós com `MIPNODE_NODCNT ≤ 200` (nós rasos), via `cbCut`.
3. **Cronometragem do callback**: soma o tempo gasto em cada invocação e reporta a fração sobre o
   tempo total (`cb_fraction`).

Smoke test em 5 gabaritos (Direct0, TermRelay, Tri, StayPut, SharedTerminal) — **5/5 PASS**,
confirmando que a extensão não quebrou a corretude do E6.

## 3. Bateria comparativa

| Instância | R | Regime | COMP obj/bound/gap | BC-Y obj/bound/gap | cb_fraction | lazy / user cuts |
|---|---|---|---|---|---|---|
| Chicago st15 | 7 | R-a | **17 / 17 / 0%** (OPT, 191s) | — / 11 / — (sem incumbente) | 86,1% | 4022 / 204 |
| Barcelona st15 | 5 | R-a | **15 / 15 / 0%** (OPT, 209s) | — / 8 / — (sem incumbente) | 92,0% | 2021 / 203 |
| Philadelphia st5 | 2 | R-a | 41 / 38 / 7,3% (TL) | — / 11 / — (sem incumbente) | 70,4% | 11437 / 205 |
| Philadelphia st25 | 3 | R-a | 47 / 41 / 12,8% (TL) | — / 28 / — (sem incumbente) | 85,9% | 4215 / 205 |
| hc9u | 1 | R-b | 42 / 32 / 23,8% (TL) | 56 / 29 / 48,2% (TL) | 85,1% | 641 / 22 |
| bip42p | 200 | R-b' | 43 / 33 / 23,3% (TL) | 208 / 33 / 84,1% (TL) | 91,7% | 507 / 14 |
| cc12-2p | 500 | R-c | 7 / 6 / 14,3% (317s) | — / **−∞** / — (1544,5s, TL **não respeitado**) | 99,9% | 4 / 0 |

Todos os valores de COMP e o UB/bound de BC-Y em cada linha vêm de `results/cuts/e7_comparative.csv`.

## 4. Análise por regime

### R-a (Chicago, Barcelona, Philadelphia st5, Philadelphia st25)

**BC-Y não encontrou nenhum incumbente em nenhuma das quatro instâncias**, apesar de milhares de
cortes lazy (641 a 11437) e ~200 user cuts por instância, e apesar do MIP start guloso ter sido
projetado justamente para garantir uma solução inicial. Em Chicago e Barcelona, o COMP fecha o
ótimo (17 e 15, batendo com a referência histórica) em menos de 210s; em Philadelphia, o COMP fica
a 7–13% do ótimo. O BC-Y, no mesmo orçamento de 300s, não produz sequer uma solução viável a
reportar. **Leitura revisada (ver §5.1):** este resultado não é decisivo — BC-Y rodou com só C1
estático (COMP teve C1+C2+C4) e um MIP start que pode devolver `y` inviável sem sinalizar isso.
Não dá para separar, com estes dados, "o método não converge" de "a comparação era desigual".

### R-b (hc9u) e R-b' (bip42p)

Aqui o BC-Y **encontra** incumbentes, mas piores que o COMP: 56 contra 42 em hc9u (33% pior),
208 contra 43 em bip42p (383% pior). Os bounds ficam próximos (hc9u: 29 vs. 32; bip42p: **33 vs.
33**, empate exato) — a qualidade do limitante inferior é comparável, mas a busca por incumbentes
inteiros do BC-Y é muito mais fraca que a do B&B do Gurobi sobre o modelo compacto.

**Nota de comparação com o E6:** o bound de hc9u caiu de 32 (E6, BC-LAZY, TL=900s) para 29 aqui
(E7, TL=300s). Isso não é uma regressão do método — é o orçamento de tempo três vezes menor
(300s aqui contra 900s no E6), escolhido para comparar com o COMP sob o mesmo TL do E4. Os dois
resultados não são diretamente comparáveis entre si.

### R-c (cc12-2p)

**Resultado mais grave.** O BC-Y rodou por 1544,5s — mais de 5× o `TimeLimit=300` configurado —
sem encontrar incumbente e sem sequer estabelecer um bound válido (`ObjBound = -inf`). Apenas 4
cortes lazy e 0 user cuts foram gerados em todo esse tempo. A causa: `cc12-2p` tem `|A_r| ≈
2.795.100`; uma única chamada a `separate_classical_fracs` (Edmonds-Karp sobre a rede agregada
dessa instância) já é cara o bastante para que o Gurobi não consiga verificar o relógio de parede
entre chamadas de callback — o mecanismo de `TimeLimit` do Gurobi não interrompe uma chamada de
callback em andamento. Isso é uma limitação de robustez do BC-y como implementado, não só de
desempenho: em instâncias desse porte o método pode estourar qualquer orçamento de tempo
configurado.

## 5. Verificação de viabilidade

Toda solução do BC-Y com incumbente foi conferida no modelo compacto (fixando `y`). As duas
instâncias com incumbente (hc9u, bip42p) foram confirmadas **FEASIBLE**.

**Nota metodológica importante.** A primeira tentativa de verificação continha um defeito: em vez
de extrair o `y*` real do incumbente encontrado por `solve_bc_yspace` (que não devolvia essa
informação), o script re-resolvia o espaço-y do zero só com C1 estático — perdendo os cortes lazy
𝒵 acumulados durante a busca real — e impunha `y(V) ≤ obj + 0,5` na esperança de achar "uma"
solução com aquele valor. Essa reconstrução divergente encontrou soluções **INFEASIBLE** para
hc9u e bip42p, o que teria sido uma conclusão falsa sobre a corretude do corte lazy. Corrigido em
duas etapas: (1) `solve_bc_yspace` passou a devolver o `y*` real do incumbente (`res['y_star']`);
(2) uma reexecução dirigida das duas instâncias (300s cada) usando esse `y*` real confirmou
FEASIBLE em ambas — a busca paralela do Gurobi não é perfeitamente determinística entre execuções
mesmo com a mesma seed, então a reexecução achou valores de objetivo diferentes (48 em vez de 56
para hc9u; 69 em vez de 208 para bip42p), mas ambos igualmente viáveis. Isso reforça, em vez de
enfraquecer, a conclusão: o corte lazy (Teorema 6) está correto — o problema do BC-Y é a
qualidade/velocidade da busca por incumbentes, não a validade dos cortes.

## 5.1 Confundidores identificados na revisão pós-E7

Uma revisão posterior a este experimento (antes de qualquer nova rodada) encontrou três
confundidores na implementação que impedem tratar o resultado acima como uma medida limpa do
método BC-y:

1. **Cortes estáticos desiguais entre configs.** BC-Y recebeu só C1 (`prepare_static_c1`); COMP
   recebeu C1+C2+C4. O CSV mostra a diferença: 15 vs. 24 cortes em Chicago, 20 vs. 28 em
   Barcelona, 10 vs. 50 em Philadelphia st5, 46 vs. 73 em Philadelphia st25. O desenho de A2 em
   `direcoes-pli-min-station.md` §13 é explícito: o baseline decisivo é "base (U) **com os mesmos
   cortes de A1**", justamente para isolar o valor da decomposição do valor dos cortes. Este
   experimento não fez essa comparação.
2. **MIP start não garante viabilidade.** `_greedy_mip_start` para no orçamento de tempo (5s) e
   devolve `y` parcial mesmo que o max-flow ainda não tenha atingido `m`. Em R-a, onde 4/4
   instâncias ficaram "sem incumbente", é provável que o Gurobi tenha de fato encontrado soluções
   inteiras que satisfazem C1 mas são rejeitadas pelo corte lazy no MIPSOL — sem nunca formar um
   incumbente aceito. Isso não distingue "o método não converge" de "o MIP start não ajudou".
3. **Separação sem guarda de tempo e sem restrição de rede.** Cada chamada de
   `separate_classical_fracs` reconstrói a rede agregada sobre **todos** os arcos de A_r e roda
   Edmonds-Karp em Python puro. Em cc12-2p (R-c) isso fez o `TimeLimit=300` virar 1544,5s porque
   o Gurobi não interrompe uma chamada de callback em andamento — um problema de robustez que
   também contamina a comparação de tempo nos outros regimes (`cb_fraction` de 70–99,9%).

Some-se a variância de seed já registrada em §5 (48 vs. 56 em hc9u; 69 vs. 208 em bip42p, mesma
seed, execuções diferentes) — a linha `bcy_sol_feasible` do CSV mistura o objetivo de uma
execução com o veredito de outra.

**Consequência:** as conclusões de §4 e §6 abaixo (mantidas como registro desta rodada) não
devem ser lidas como uma medida decisiva do método BC-y. O E8 refaz a bateria com: os mesmos
cortes estáticos nas duas configs, um MIP start que sempre entrega solução viável, e um oráculo de
viabilidade restrito à rede `S∪T∪C` (sem materializar A_r inteiro) com guarda de tempo explícita.
Ver plano em `docs/technical/plans/` (Bloco 1–4 do E8).

## 6. Decisão sobre A2 (revisar após o E8)

O critério pré-registrado no plano do E7 previa quatro desfechos possíveis. Os dados encaixam
formalmente no terceiro:

> "BC-Y perde, com o callback caro → resultado inconclusivo: fazer o C.8 (rede em cache/networkx)
> e repetir."

`cb_fraction` ficou entre 70,4% e 99,9% em todas as sete instâncias — o callback domina o tempo de
parede em todos os casos, então não se pode separar "o método não ajuda" de "o separador é lento
demais para dar ao método uma chance". Formalmente, portanto, a questão **permanece aberta** até
o C.8 ser feito.

**Atualização (ver §5.1): esta conclusão foi suspensa.** Além do callback caro, a bateria tinha
cortes estáticos desiguais entre COMP e BC-Y e um MIP start sem garantia de viabilidade — dois
confundidores que já bastam para não usar este experimento como base de decisão sobre A2, mesmo
independentemente do C.8. A decisão sobre A2 fica para o relatório do E8
(`resultados-e8-pli.md`), que refaz a comparação em base justa.

## 7. O que não fazer (mantido do plano)

Sem mudança: não introduzir custos heterogêneos, autonomias por robô, elegibilidade
origem-destino; não usar `lin23`/`lin37`/`fnl4461fst`; não reintroduzir estações só em vértices
intermediários; não implementar Benders/Lagrangeana/zero-half nesta rodada; sem push.

---

*Código em `experiments/cuts/bc_yspace.py` (estendido), `run_e7.py` (novo).*
*Resultados em `results/cuts/e7_comparative.csv`.*
