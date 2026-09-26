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

O ponto que faltou: o bipartido de alcance direto `B_∅ = {(s,t) ∈ S×T : d(s,t) ≤ r}` contém o par
`(v,v)` para todo `v ∈ S∩T`, já que `d(v,v) = 0 ≤ r`. Ele não aparece porque `A_r` é construído sem
auto-laços (verificado: `v ∉ N⁺(v)` e `(v,v) ∉ A_r`). Com esse par presente, `v` nunca fica sem par
— o Lema 5 é respeitado — e continua disponível como destino para outras origens.

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

## 6. Estado da correção

- [x] Diagnóstico e confirmação por dois instrumentos independentes.
- [x] Alcance medido nas 75 instâncias principais.
- [ ] Regressão dedicada (`verify_c4_dm.py`) e correção do `except` em `verify_e5_validador.py`.
- [ ] Correção: auto-emparelhamento de `S∩T` no bipartido de DM, em vez da remoção.
- [ ] Reavaliação das instâncias afetadas e atualização do `manifest.csv`.

Todo resultado registrado antes desta data foi produzido com o gerador defeituoso. O alcance prático
se restringe às instâncias com `S∩T ≠ ∅`, que são 5 entre as principais e nenhuma nas rodadas
E1–E4, E7 e E8.
