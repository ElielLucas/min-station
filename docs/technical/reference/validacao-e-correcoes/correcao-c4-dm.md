# Cortes inválidos em `generate_C4_DM` quando `S ∩ T ≠ ∅`

Registro do defeito encontrado em 2026-09-26, durante a revisão do relatório do E10b. Cobre o
diagnóstico, a causa raiz, por que a regressão não pegou, e o estado da correção.

## 1. O defeito

`generate_C4_DM` (`experiments/cuts/cuts.py:181`) gera desigualdades `y(Z) ≥ 1` que **eliminam
soluções viáveis** do MIN-STATION. Não é imprecisão numérica nem variação de força do relaxamento:
é corte inválido, que pode excluir o ótimo e produzir um "limite inferior" acima do OPT verdadeiro.

Confirmado por dois instrumentos independentes, exigindo que os dois concordem em cada corte:

1. `is_valid_cut` (`cuts.py:538`) reprova o corte;
2. `integer_oracle` — validado exaustivamente em `verify_e8_oracle.py`, 0 divergências contra
   `_build_flow_net_aggregate` + Edmonds-Karp — confirma que `V∖Z` é **viável**, exibindo a solução
   que a desigualdade corta.

## 2. Alcance medido

Das 75 instâncias `classe = principal` do manifesto, 5 têm `S ∩ T ≠ ∅`, todas variantes `-rho`.
Três delas geram cortes inválidos; a condição é necessária, mas não suficiente:

| Instância | classe | \|S∩T\| | \|C4\| | inválidos | confirmados pelo oráculo |
|---|---|---|---|---|---|
| `b-b09-intercalado-f2-rho` | F | 2 | 6 | **3** | 3 |
| `i-i160-301-intercalado-f2-rho` | F | 2 | 10 | **2** | 2 |
| `mapf-den312d-m50-f2-rho` | A | 5 | 16 | **4** | 4 |
| `mapf-room-32-32-4-m25-f4-rho` | A | 3 | 28 | 0 | 0 |
| `puc-w23c23-intercalado-f2-rho` | F | 28 | 496 | 0 | 0 |

Em `b09` e `i160-301` o defeito é determinístico (idêntico em `PYTHONHASHSEED` 0, 1 e 2); em
`den312d-m50` depende da execução (ver §5). Grupo de controle com `S ∩ T = ∅` — `puc-hc9u-seed-r1`
(256 cortes), `pucn-cc7-3n-seed-r1` (146) e `mapf-room-32-32-4-m10-f8` (12), três seeds cada —
não acusa nenhum corte inválido, como a causa raiz prevê.

**Consequência a verificar:** `b-b09-intercalado-f2-rho` (LB=UB=4) e `i-i160-301-intercalado-f2-rho`
(LB=UB=5) estão registradas como resolvidas ao ótimo. Esses ótimos foram obtidos com cortes
inválidos no modelo e podem estar inflados.

## 3. Causa raiz

A função monta o bipartido de alcance direto sobre `T_only = T ∖ S`, removendo `S ∩ T` dos dois
lados (`cuts.py:190-197`), e emite um corte por origem não emparelhada.

A remoção não se sustenta. O balanço unificado da formulação base (`base-formulation.md` §6.1) é
**permissivo** em `v ∈ S∩T`: o vértice conserva fluxo, de modo que o robô que parte de `v` *pode*
ficar parado ocupando o próprio alvo (Lema 5 de Das), mas *também pode* sair, desde que outro robô
chegue a `v`. Logo `v` permanece disponível como destino para uma origem de `S_only`. Removê-lo do
lado dos destinos suprime emparelhamentos legítimos, cria deficiência de Hall onde não há, e o corte
derivado dessa deficiência corta soluções viáveis.

Medição em `mapf-den312d-m50-f2-rho` (`PYTHONHASHSEED=3`), sobre as 8 origens sem par:

| origem livre | \|S'\| | \|N(S') ∩ T_only\| | \|N(S') ∩ T\| | defic. vs `T_only` | defic. vs `T` | corte válido |
|---|---|---|---|---|---|---|
| `14_22` | 3 | 2 | 4 | 1 | −1 | sim |
| `28_20` | 13 | 12 | 15 | 1 | −2 | sim |
| `24_25` | 13 | 12 | 15 | 1 | −2 | sim |
| `22_38` | 1 | 0 | 0 | 1 | **1** | sim |
| `41_26` | 16 | 15 | 18 | 1 | −2 | sim |
| `13_38` | 8 | 7 | 9 | 1 | −1 | **não** |
| `47_52` | 7 | 6 | 7 | 1 | 0 | **não** |
| `6_26` | 3 | 2 | 4 | 1 | −1 | **não** |

Toda origem livre tem deficiência 1 contra `T_only`, como Hall prevê. Contra `T` inteiro a
deficiência some (≤ 0) em todas menos `22_38` — a única com deficiência real, e seu corte é válido.
Os três cortes inválidos estão no grupo de deficiência artificial.

A correção E5 anterior (`plano-experimentos-e5.md:128`) atacou o sintoma oposto: antes, `S∩T`
entrava nos dois lados como origem *e* destino não emparelhados, gerando corte que o Lema 5
invalida. Removê-lo eliminou aquele caso e abriu este.

**A implementação divergia da teoria já documentada.** O §5.4 de `direcoes-pli-min-station.md`
define o corte para `S' ⊆ S∖T` com a condição `|N⁺(S') ∩ T| < |S'|` — com `T` **inteiro**. A
assimetria é deliberada e necessária: a origem precisa estar fora de `S∩T` para que o argumento de
primeiro salto valha (um robô que parte de `v ∈ S∩T` pode ficar parado, e não precisa de relé), mas
o *destino* não tem essa restrição. O código aplicava `T∖S` dos dois lados.

Não se trata, portanto, de uma escolha de modelagem em aberto: a forma correta já estava provada no
documento e a implementação é que não a seguia.

## 4. Por que nenhuma regressão pegou

- `verify_e5_gabaritos.py` resolve o modelo compacto e compara com o OPT dos gabaritos. **Não gera
  corte algum.**
- `verify_e5_validador.py:71-77` roda `solve_lp_cutting_plane(validate_cuts=True)`, que levantaria
  `CorteInvalido`, mas embrulha o laço num `except Exception` que imprime a exceção **sem
  incrementar `total_diverg`**. A linha 80 então imprime "RESULTADO FINAL: 0 divergências —
  validador correto" mesmo quando um corte inválido foi detectado.
- `verify_e8_oracle.py` valida o oráculo e os cortes que o *oráculo* devolve, não os de C4-DM.
- `verify_e8_cc12_opt.py:162-167` é o único que valida saída de `generate_C4_DM`, mas numa única
  instância (`cc12-2p`, que tem `S∩T = ∅`) e como certificado pontual, não como regressão.

A docstring de `solve_ip_yspace` (`yspace.py:231-232`) afirma que "C1/C2/C4-DM já são validadas por
oráculo nos gabaritos de regressão da rodada E5" e usa isso para justificar `validate_cuts=False`
por padrão. A afirmação não se sustenta.

Os 10 gabaritos de `synthetic.py` não reproduzem o defeito: os dois com `S∩T ≠ ∅` são pequenos
demais — `StayPut` gera 0 cortes e `SharedTerminal` gera 1, válido.

## 5. Não-determinismo (defeito distinto, mesma função)

`generate_C4_DM` percorre `S_only`/`T_only`, que são `set`s de rótulos, e passa essa ordem a
`_max_matching`. Emparelhamentos máximos não são únicos: mudando a ordem, mudam as origens sem par,
as regiões alternantes e a família gerada. Variando `PYTHONHASHSEED` na mesma instância e no mesmo
código, `den312d-m50` produz 16, 16 ou 15 cortes distintos, e o ótimo do IP do núcleo sai 5 ou 6 —
foi 5 no E9 e 6 no E10b, ótimo *provado* nos dois, sem contradição porque os modelos diferem.
`mapf-random-32-32-10-m25-f4` dá 12 em 2 de 6 execuções e 13 nas outras 4.

Isso é independente da validade (atinge também instâncias com `S∩T = ∅`) e importa porque o E12
decide por margens de 1–2 estações.

## 6. A correção

`generate_C4_DM` passa a emparelhar `S∖T` contra `T` inteiro, e `T∖S` contra `S` inteiro, como o
§5.4 já especificava. Duas mudanças na mesma função, de naturezas distintas:

1. **Validade:** a vizinhança que define a deficiência deixa de ser restrita a `T∖S` (resp. `S∖T`).
   Só altera instâncias com `S∩T ≠ ∅`.
2. **Determinismo:** as iterações passam a ser ordenadas (`sorted`) antes do emparelhamento máximo,
   e a lista devolvida sai ordenada. Emparelhamento máximo não é único, e a ordem de iteração de um
   `set` varia entre processos. Isso altera a família gerada em qualquer instância, com ou sem
   `S∩T ≠ ∅`.

Efeito medido nas instâncias que acusavam cortes inválidos:

| Instância | antes | depois |
|---|---|---|
| `b-b09-intercalado-f2-rho` | 6 cortes, 3 inválidos | 3 cortes, 0 inválidos |
| `i-i160-301-intercalado-f2-rho` | 10 cortes, 2 inválidos | 9 cortes, 0 inválidos |
| `mapf-den312d-m50-f2-rho` | 15–16 cortes, até 5 inválidos | 11 cortes, 0 inválidos |

Determinismo conferido em `den312d-m50`: quatro execuções com `PYTHONHASHSEED` distintos produzem a
mesma lista de cortes (hash idêntico), contra 16/16/15 cortes e hashes distintos antes.

### Rede de segurança

- **`experiments/cuts/verify_c4_dm.py`** (novo): exige que todo corte gerado seja aprovado por
  `is_valid_cut` *e* que `integer_oracle` confirme `V∖Z` inviável — divergência entre os dois
  instrumentos também é falha. Cobre os gabaritos, as instâncias com `S∩T ≠ ∅` e um controle com
  `S∩T = ∅`, repetindo em subprocessos com `PYTHONHASHSEED` distintos, porque uma execução só pode
  passar por sorte. **Confirmado que reprova o código anterior à correção** (5 cortes inválidos em
  `den312d-m50`), executado num worktree do commit `20d3fc1`.
- **`verify_e5_validador.py`**: o `except Exception` do laço de validação passa a contar a exceção
  como divergência. Antes, um `CorteInvalido` era impresso e o script ainda encerrava com
  "0 divergências — validador correto".

## 7. Reavaliação das instâncias afetadas

Protocolo de dificuldade refeito nas 5 instâncias com `S∩T ≠ ∅`, mesma configuração do benchmark-v1
(COMP = U + C1+C2+C4, Gurobi, 4 threads, seed 42, TL 600 s), por
`experiments/benchmark/reavaliar_c4dm.py`. Resultado bruto em
`results/benchmark/reavaliacao_c4dm.csv`.

| Instância | LB antes | LB depois | UB antes | UB depois | classe | veredito |
|---|---|---|---|---|---|---|
| `b-b09-intercalado-f2-rho` | 4 | **2** | 4 | **2** | F → F | **ótimo publicado estava errado** |
| `mapf-den312d-m50-f2-rho` | 6 | **4** | 9 | 9 | A → A | **LB publicado era inválido** |
| `mapf-room-32-32-4-m25-f4-rho` | 16 | 16 | 20 | **19** | A → A | UB melhorou |
| `i-i160-301-intercalado-f2-rho` | 5 | 5 | 5 | 5 | F → F | inalterado |
| `puc-w23c23-intercalado-f2-rho` | 128 | 128 | 128 | 128 | F → F | inalterado |

**`b-b09-intercalado-f2-rho` é o caso grave**: estava registrada como resolvida na otimalidade com
4 estações, e o ótimo real é 2 — o dobro. Os cortes inválidos eliminavam toda solução com 2 ou 3
estações, e o solver provou otimalidade dentro de um espaço de busca que já não continha o ótimo.
Um "ótimo provado" pode estar errado quando o modelo contém corte inválido, e foi o que aconteceu.

Em `mapf-den312d-m50-f2-rho` o LB caiu de 6 para 4: o valor anterior não era limite inferior válido.
Em `mapf-room-32-32-4-m25-f4-rho`, que não acusava cortes inválidos, o UB melhorou de 20 para 19 —
efeito da mudança de família de cortes, não de correção de erro.

Nenhuma classe de dificuldade mudou, então o desenho do benchmark (partições, regimes, seleção das
30 D/A) segue válido. `manifest.csv` atualizado nas três linhas, com `fonte_lb_ub` marcando a
reavaliação; os valores anteriores ficam preservados em `reavaliacao_c4dm.csv`.

## 8. Estado

- [x] Diagnóstico e confirmação por dois instrumentos independentes.
- [x] Alcance medido nas 75 instâncias principais.
- [x] Regressão dedicada e correção do `except` em `verify_e5_validador.py`.
- [x] Correção de validade e de determinismo em `generate_C4_DM`.
- [x] Reavaliação das instâncias afetadas e atualização do `manifest.csv`.

Todo resultado registrado antes de 2026-09-26 foi produzido com o gerador defeituoso. O alcance da
falha de **validade** se restringe às instâncias com `S∩T ≠ ∅` — 5 entre as principais, nenhuma nas
rodadas E1–E4, E7 e E8, e das que aparecem em E9/E10/E10b só `den312d-m50` e `room-m25-rho`. A falha
de **determinismo** alcança qualquer instância e move o LB em ±1; os números não regerados
permanecem os da versão anterior e estão marcados como tal nos respectivos relatórios.
