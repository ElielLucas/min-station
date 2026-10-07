# Pré-registro R11 — certificadores de classes especiais (Spec D)

**Escrito em:** 2026-10-06
**Pré-registrado originalmente em:** 2026-10-06, antes da implementação dos algoritmos, de qualquer instância persistida e de qualquer medição de acordo/divergência. **Atualização de preparação:** 2026-10-07, após a implementação ser escrita, ainda antes de `verify_r11.py`, da materialização oficial das instâncias e de qualquer linha de `results/structural/r11-certificadores.csv`.
**Spec:** `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`
**Leituras:** `docs/technical/reference/leituras-r11-certificadores.md` (obrigatório; este arquivo não reabre SP-R*)
**WorkLimit da linha de base (164):** **não** se aplica a este lote. Aqui as instâncias são caminhos/ciclos/aranhas pequenos. Padrão copiado de F3 (`experiments/alternative-formulations/pre-registro-f3.md`): MIP exacto, sem `WorkLimit`.
**GF1:** PASS. F-CC entra como cruzamento, não como construtor do `C` do certificador.
**G1:** compatibility. R11 continua suporte. Este pré-registro não reabre G1 nem GF1.
**F-C3:** `OPEN` em todas as linhas.

Este arquivo congela o *contrato* da execução futura. A implementação preparatória existe, mas **nenhum teste R11, materialização oficial, enumeração, MIP, F-CC ou CSV foi executado nesta atualização**. Os hashes só passam a existir quando `prepare_r11.py` materializar os arquivos; o lote oficial não pode começar antes de esse manifesto estar congelado. Nenhum tamanho, semente ou variante entra depois de o CSV oficial começar, excepto novo pré-registro rotulado.

---

## 1. Objectivo do lote

Comparar os procedimentos publicados (variantes da matriz de leituras) com:

- enumeração independente, no cap;
- MIP da base até `OPTIMAL`, fora do cap de enumeração e como cruzamento;
- F-CC binária, no `max_W`;

em caminhos, ciclos e aranhas, incluindo SP-R1…SP-R5, `S∩T` e permanência.

Não é teste de velocidade. Runtime pode gravar-se como contexto.

---

## 2. Variantes congeladas

| `variante` | Classe | Definição (IDs em `leituras-r11-certificadores.md`) |
|---|---|---|
| `path-alg1` | path | PATH-ALG1 literal |
| `cycle-alg2` | cycle | DAS-A2; chama `path-alg1`; CYCLE-ORDER; CYCLE-SENTINEL; empate `≤` (última quebra) |
| `spider-A` | spider | L1A + INT-A + R1A + R2A + L2-sort + sit-keep + r0-zero + C2-3 |
| `spider-B` | spider | como A, mas L1B (PATH-ALG1 na radial) |
| `spider-U` | spider | como A, mas sit-unspecified e r0-unspecified |

Fora do CSV oficial (somente verificação local em `verify_r11.py`, quando executada): `spider-L2-gap`, qualquer `spider-repair-*`.

Uma linha CSV = `(instância, variante aplicável à classe)`. Path não corre spider. Instância spider corre as três variantes spider.

---

## 3. Famílias e estratos

### 3.1 Famílias

| `familia` | Grafo | Gerador preparado |
|---|---|---|
| `path` | caminho | `experiments/structural/path_cycle.py` (implementado; não executado) |
| `cycle` | ciclo `n≥3` | `experiments/structural/path_cycle.py` (implementado; não executado) |
| `spider` | aranha `deg(c)≥3` | `experiments/structural/spider.py` (implementado; não executado) |
| `spider-reading` | aranhas construídas à mão para SP-R* | persistidas sob `instances/estrutural/spider/` |

BP/HB/SC/TR **não** entram. Semântica actual dessas famílias não muda.

### 3.2 Estrato `micro`

`n ≤ n_opt_enum`. Onde a enumeração termina:

```text
especializado, baseline OPTIMAL, opt_por_enumeracao, F-CC se n_W ≤ max_W
```

### 3.3 Estrato `medium`

`n_opt_enum < n ≤ n_medium_max`. Mínimo:

```text
especializado, baseline OPTIMAL
```

F-CC se a enumeração de conexos em `H=G^r` ficar ≤ `max_W`; senão `fcc_status=cap_exceeded` e **sem** LP/IP incompleto.

Justificativa dos tamanhos (padrão já usado, sem medição nova):

| Parâmetro | Valor | Origem |
|---|---|---|
| `n_opt_enum` | 16 | F3: `2^16=65536` subconjuntos; o validador não tem tecto `n≤5` |
| `n_medium_max` | 32 | Acima do cap de enum; abaixo de qualquer instância D/A da linha de base. Caminho/ciclo/aranha com `n=32` e `m` pequeno é o mesmo regime “exacto barato” de F3 (`n_max=21` era para *conexos em H geral*; em caminho o número de conexos é `n(n+1)/2 ≤ 528`) |
| `n` micro pontuais | 3, 5, 8, 12, 16 | cobre VAL-A2 (`n=3`), ciclo mínimo (`n=3`), cap F3 (`n=16`) |
| `n` medium | 24, 32 | único par acima de 16 e ≤ 32; 24 é o primeiro múltiplo de 8 após 16, alinhado aos `n` micro 8/16 |

Não se usam `n>32` neste lote: a spec avisa que ciclo grande + `r` pequeno pode tornar o MIP caro, e R11 não é campanha de escala.

---

## 4. Caps e referências exactas

| Cap | Valor | Se excedido |
|---|---|---|
| `n_opt_enum` | 16 | `enum_status=not_run_cap`; **não** se chama enumeração |
| `max_W` | 200000 | F3. `fcc_status=cap_exceeded`; aborta enumeração de `W`; não reporta F-CC incompleta |
| `n_max` lote | 32 | gerador recusa |

Prioridade de `opt` / `fonte_opt` (spec R11b.3):

1. Se `n ≤ 16` e enum termina: `fonte_opt=enum`. Baseline e F-CC são cruzamento. Se baseline exacto ≠ enum: **parar a interpretação dessa linha** (`resultado=reference_failure`), não julgar o algoritmo.
2. Se `n > 16` e baseline `OPTIMAL`: `fonte_opt=mip_base`. T5 / `validacao-formulacao-base.md` §5.5.
3. F-CC binária exacta, se couber no cap, deve igualar `opt`. Se não: `reference_failure` antes de classificar o certificador.
4. Incumbente com tempo esgotado **não** é OPT.
5. F-C3: `fc3_status=OPEN` sempre. Nunca preenche `opt`.

`opt_fcc` está implementado em `experiments/alternative-formulations/fcc.py`: reutiliza a F-CC existente, cria `y` binário e exige `GRB.OPTIMAL`. O default de `construir_modelo_fcc` continua contínuo, portanto F3 e `lp_fcc` preservam a semântica anterior. O helper ainda não foi executado nesta preparação.

---

## 5. Sementes

Padrão do repositório: linha de base `42,43,44`; F3 solver `42`; BP estrutural `0,1`.

| Uso | Valor | Motivo |
|---|---|---|
| Gerador aleatório micro | `42`, `43` | duas sementes, como BP `0,1`; 42 é a semente canónica do projecto |
| Gerador aleatório medium | `42` | uma semente: lote de suporte, não D/A |
| Solver Gurobi (baseline / F-CC) | `42` | F3 |
| `PYTHONHASHSEED` | `0` | F3 / verify_fcc |

Construções SP-R* e casos à mão: **sem** semente de gerador; IDs fixos.

Não se usa a terceira semente `44` aqui: a spec C precisava de 3 sementes para *reproduzir melhoria primal*. R11 compara algoritmos combinatórios determinísticos. Duas sementes no micro bastam para não ter uma só amostra “aleatória”.

---

## 6. Valores de `r`

Inteiros, métrica em passos (peso 1).

| Papel | `r` | Motivo |
|---|---|---|
| duro / supercontagem Das | 1 | VAL-A2; SP-R5 |
| médio | 2 | SP-R2 com `d(c,t)=5`; VAL-A2 `r=2` |
| trivial definição | `r_diam` = diâmetro do grafo gerado | spec: `r ≥ diam(G)` |

Não se sorteia `r` contínuo. Não se usa percentil de distâncias (isso é conversor TNTP / extensão).

Em cada instância determinística por semente, o gerador seleciona **um** `r` em `{1,2,r_diam}` pela regra congelada da §8; não há sorteio em tempo de execução. Casos à mão fixam `r` na tabela §12.

---

## 7. Política `S` / `T`

`|S|=|T|=m`. Pesos 1. `conferir_fidelidade(..., permitir_intersecao=True)` só nos geradores R11. Default da API existente permanece `False` (BP/HB/SC/TR).

### 7.1 `m`

| Estrato | `n` | `m` admitidos |
|---|---|---|
| micro | 3 | 1 |
| micro | 5, 8 | 1, 2 |
| micro | 12, 16 | 1, 2, 4 |
| medium | 24, 32 | 2, 4 |

Tecto `m=4`: F3 usa `m` pequenos nos gadgets; R11 precisa de vários robôs para matching, não de `m` tipo MAPF.

### 7.2 Construção em instâncias *aleatórias*

Com a semente da instância, o gerador escolhe uma política entre as seguintes (ciclo determinístico sobre a semente, não “a que der acordo”):

| Código | Política |
|---|---|
| `disj` | `S ∩ T = ∅` |
| `sit1` | exactamente um vértice em `S ∩ T` |
| `sitm` | `|S ∩ T| ≥ 2` quando `m≥2`; senão cai em `sit1` |
| `stay` | `S = T` (permanência total possível) |
| `sit_center` | só spider: `c ∈ S ∩ T`, e o resto `disj` |

Proibido: apagar interseção como pré-processamento.

### 7.3 Permanência

Cobertura mínima (não um único token):

- nenhum `S∩T`;
- um vértice de interseção, matching de Lemma 4 / KEEP *pode* permanecer;
- vários candidatos a permanência (`sitm`);
- `S=T`;
- spider: `c ∈ S`, `c ∈ T`, `c ∈ S ∩ T` em instâncias distintas;
- um caso path em que a interseção **não** é permanência do matching ordenado (VP-SIT-NPERM / §8.6 das leituras).

### 7.4 Aranha: movimento

Pelo menos uma instância de cada:

- só intramural;
- só cruzado;
- mistura;
- origem em `c`;
- destino em `c`;
- radial de um vértice;
- radiais de comprimentos diferentes;
- radial de alvo sem origem (SP-R1/SP-R2);
- origem adjacente a `c`.

---

## 8. Como o gerador determinístico fecha `r` e a política

O mapeamento deixou de ser PENDING. Não usa `random` nem hash nativo de Python.
A seleção de terminais usa SHA-256, portanto não depende de `PYTHONHASHSEED` nem
da ordem de um `set`.

Para cada célula com semente:

```text
r_choice = seed mod 3
0 -> 1
1 -> 2
2 -> r_diam

path/cycle policies = [disj, sit1, sitm, stay]
spider policies     = [disj, sit1, sitm, stay, sit_center]
policy_index = (n + 3*m + seed) mod len(policies)
```

Para escolher os vértices, ordena-se `V` pela chave:

```text
SHA256("R11|{familia}|{n}|{m}|{seed}|{v}")
```

com `str(v)` como desempate. A política consome essa ordem:

- `disj`: primeiros `m` em `S`, próximos `m` em `T`;
- `sit1`: primeiro vértice comum; os restantes de `S` e `T` são disjuntos;
- `sitm`: os primeiros `min(m,2)` são comuns; restantes disjuntos;
- `stay`: `S=T` nos primeiros `m`;
- `sit_center`: `c` é comum e o restante é disjunto.

Mapa congelado das células automáticas:

| id | r | política |
|---|---:|---|
| `path-m-n8-m1-s42` | 1 | `sit1` |
| `path-m-n8-m2-s42` | 1 | `disj` |
| `path-m-n8-m2-s43` | 2 | `sit1` |
| `path-m-n12-m2-s42` | 1 | `disj` |
| `path-m-n16-m4-s42` | 1 | `sitm` |
| `path-m-n16-m4-s43` | 2 | `stay` |
| `path-M-n24-m2-s42` | 1 | `disj` |
| `path-M-n24-m4-s42` | 1 | `sitm` |
| `path-M-n32-m4-s42` | 1 | `sitm` |
| `cycle-m-n8-m2-s42` | 1 | `disj` |
| `cycle-m-n12-m2-s43` | 2 | `sit1` |
| `cycle-m-n16-m4-s42` | 1 | `sitm` |
| `cycle-M-n24-m2-s42` | 1 | `disj` |
| `cycle-M-n32-m4-s42` | 1 | `sitm` |
| `spider-m-n16-m2-s42` | 1 | `sit_center` |
| `spider-m-n16-m4-s43` | 2 | `sit1` |
| `spider-M-n24-k3-m2-s42` | 1 | `sitm` |
| `spider-M-n32-k4-m4-s42` | 1 | `sit1` |

As definições completas de `S` e `T` ficam em
`experiments/structural/r11_catalog.py`, que é a fonte executável congelada do
catálogo. Alterá-las depois do manifesto/hash exige novo pré-registro rotulado.

### 8.1 Terminais exatos das células automáticas

A aplicação da regra acima fica congelada também em forma explícita:

| id | S | T |
|---|---|---|
| `path-m-n8-m1-s42` | `{v2}` | `{v2}` |
| `path-m-n8-m2-s42` | `{v7,v5}` | `{v6,v1}` |
| `path-m-n8-m2-s43` | `{v6,v4}` | `{v6,v7}` |
| `path-m-n12-m2-s42` | `{v9,v8}` | `{v10,v1}` |
| `path-m-n16-m4-s42` | `{v0,v7,v11,v1}` | `{v0,v7,v3,v10}` |
| `path-m-n16-m4-s43` | `{v6,v1,v14,v4}` | `{v6,v1,v14,v4}` |
| `path-M-n24-m2-s42` | `{v17,v12}` | `{v2,v18}` |
| `path-M-n24-m4-s42` | `{v18,v0,v12,v3}` | `{v18,v0,v4,v2}` |
| `path-M-n32-m4-s42` | `{v1,v31,v20,v7}` | `{v1,v31,v10,v4}` |
| `cycle-m-n8-m2-s42` | `{v3,v4}` | `{v1,v7}` |
| `cycle-m-n12-m2-s43` | `{v4,v8}` | `{v4,v2}` |
| `cycle-m-n16-m4-s42` | `{v1,v0,v10,v3}` | `{v1,v0,v6,v9}` |
| `cycle-M-n24-m2-s42` | `{v15,v8}` | `{v11,v18}` |
| `cycle-M-n32-m4-s42` | `{v23,v25,v31,v4}` | `{v23,v25,v6,v5}` |
| `spider-m-n16-m2-s42` | `{c,r0_2}` | `{c,r0_3}` |
| `spider-m-n16-m4-s43` | `{r0_3,r2_2,r0_4,r3_2}` | `{r0_3,c,r2_4,r1_2}` |
| `spider-M-n24-k3-m2-s42` | `{r2_5,r1_4}` | `{r2_5,r1_4}` |
| `spider-M-n32-k4-m4-s42` | `{r2_7,r3_2,r3_6,r1_8}` | `{r2_7,r3_1,r2_3,r2_6}` |

A ordem listada é a ordem serializada pelo catálogo; semanticamente `S` e `T`
continuam conjuntos.


## 9. Baseline (política)

| Item | Valor |
|---|---|
| Modelo | `baseline.py` variante U, sem cortes (o exacto do problema, T5) |
| `f` | inteiro (modelo exacto; não COMP) |
| Cortes C1+C2+C4 | **não** no certificador de OPT; COMP não é necessário para OPT em n≤32 |
| MIP start | nenhum |
| Threads | 1 (F3; instâncias pequenas) |
| Seed | 42 |
| TimeLimit | 1800 s, só guarda |
| WorkLimit | nenhum |
| Status que certifica OPT | Gurobi `OPTIMAL` (2) |
| Timeout / não óptimo | `baseline_status=timeout` ou o código Gurobi; campo `opt` **não** preenchido por incumbente; `resultado=reference_failure` se não houver enum |

---

## 10. F-CC e F-C3

| Item | Política |
|---|---|
| Forma | modelo já em `fcc.py`; `y` binário no helper de OPT |
| `max_W` | 200000 |
| `n_W` | gravar no CSV |
| cap | `cap_exceeded`, sem número |
| F3 CSV / `run_f3.py` | **não** tocar |
| F-C3 | `fc3_status=OPEN` |

Em caminho, `|conexos(H)|` cresce com `r` (H fica mais denso). Com `r=r_diam`, H é completo e o número de conexos é `2^n−1`. Para `n=16`, `2^16−1=65535 < 200000`. Para `n=24`, `2^24−1 > 200000` se `r` for enorme. Logo:

- micro `n≤16`: F-CC sempre dentro do cap, qualquer `r` deste lote;
- medium `n=24` ou `32`: F-CC só se `r` pequeno deixar `|W|` ≤ cap; se `r=r_diam`, esperar `cap_exceeded`. Isto é consequência combinatória, não medição.

---

## 11. Acordo, divergência, `unspecified`, timeout, cap

Igual à spec D, copiado aqui para o runner não “interpretar”:

**Acordo** (`resultado=agreement`):

```text
alg_status == ok
AND alg_viavel == true
AND alg_obj == opt
```

`C` não precisa igualar um `C` de referência.

**Divergência:**

| `resultado` | Condição |
|---|---|
| `infeasible_solution` | `ok` e `viavel=false` |
| `suboptimal` | `ok`, viável, `alg_obj > opt` |
| `objective_below_reference` | `ok` e `alg_obj < opt` (investigar já; inconsistência) |

PATH-05 (VAL-A2) **não** é excepção de protocolo: se ocorrer no lote, é `suboptimal` ou `infeasible_solution` conforme `viavel`. O relatório humano cita PATH-05. Não se relabel como acordo.

**`unspecified`:** `alg_status=unspecified`. Não conta como acordo nem divergência. Esperado em `spider-U` quando `S∩T≠∅` ou `r'=0`.

**`reference_failure`:** enum ≠ baseline exacto; F-CC exacta ≠ `opt`; baseline sem OPT e sem enum.

**`implementation_error`:** `ok` mas `obj != |C|`; certificador chamou solver; grafo da classe errada com `status=ok`.

Timeout baseline: não apagar a linha.

`enum_status=not_run_cap` e `fcc_status=cap_exceeded` não são falha do algoritmo.

---

## 12. Lista oficial de instâncias (IDs e parâmetros)

Hashes: **PENDING MATERIALIZATION**. `experiments/structural/prepare_r11.py` grava os arquivos e `instances/estrutural/r11-manifest.csv`; esse manifesto deve ser conferido/versionado antes de `run_r11.py`. `run_r11.py` aborta se um arquivo faltar ou se o SHA-256 divergir. IDs e parâmetros abaixo já estão congelados.

### 12.1 Path — micro (à mão + grelha)

| id | n | m | r | S/T | seed | papel |
|---|---|---|---|---|---|---|
| path-hand-opt0-r2 | 3 | 1 | 2 | `S={v0}`, `T={v2}` | — | VAL-A2 / VP-OPT0 |
| path-hand-one-r1 | 3 | 1 | 1 | `S={v0}`, `T={v2}` | — | VAL-A2 origem+meio |
| path-hand-stay | 5 | 1 | 2 | `S=T={v2}` | — | permanência |
| path-hand-sit | 5 | 2 | 2 | `S={v0,v2}`, `T={v2,v4}` | — | `S∩T` |
| path-hand-sit-nperm | 5 | 2 | 1 | `S={v0,v1}`, `T={v1,v4}` | — | interseção presente; matching ordenado não força permanência em `v1` |
| path-hand-diam | 8 | 1 | 7 | `S={v0}`, `T={v7}` | — | `r≥diam` |
| path-m-n8-m1-s42 | 8 | 1 | gerador | gerador | 42 | aleatório |
| path-m-n8-m2-s42 | 8 | 2 | gerador | gerador | 42 | |
| path-m-n8-m2-s43 | 8 | 2 | gerador | gerador | 43 | |
| path-m-n12-m2-s42 | 12 | 2 | gerador | gerador | 42 | |
| path-m-n16-m4-s42 | 16 | 4 | gerador | gerador | 42 | cap enum |
| path-m-n16-m4-s43 | 16 | 4 | gerador | gerador | 43 | |

### 12.2 Path — medium

| id | n | m | seed |
|---|---|---|---|
| path-M-n24-m2-s42 | 24 | 2 | 42 |
| path-M-n24-m4-s42 | 24 | 4 | 42 |
| path-M-n32-m4-s42 | 32 | 4 | 42 |

`r` e política: valores exatos da §8; `r=1` nas três células.

### 12.3 Cycle — micro

| id | n | m | r | S/T | papel |
|---|---|---|---|---|---|
| cycle-hand-n3-opt0 | 3 | 1 | 2 | `S={v0}`, `T={v1}` | OPT 0 possível |
| cycle-hand-n5-r1 | 5 | 1 | 1 | `S={v0}`, `T={v2}` | uma estação / quebras |
| cycle-hand-breaks | 6 | 2 | 1 | `S={v0,v3}`, `T={v2,v5}` | `|X|` distintos antes do min |
| cycle-hand-sym | 6 | 2 | 2 | `S={v0,v3}`, `T={v1,v4}` | simetria |
| cycle-hand-sit | 6 | 2 | 1 | `S={v0,v2}`, `T={v2,v4}` | `S∩T` |
| cycle-hand-stay | 6 | 2 | 1 | `S=T={v0,v3}` | `S=T` (Lemma 5 / Fig. 3) |
| cycle-m-n8-m2-s42 | 8 | 2 | gerador | §8.1 | aleatório determinístico |
| cycle-m-n12-m2-s43 | 12 | 2 | gerador | §8.1 | |
| cycle-m-n16-m4-s42 | 16 | 4 | gerador | §8.1 | cap enum |

### 12.4 Cycle — medium

| id | n | m | seed |
|---|---|---|---|
| cycle-M-n24-m2-s42 | 24 | 2 | 42 |
| cycle-M-n32-m4-s42 | 32 | 4 | 42 |

### 12.5 Spider — micro (inclui SP-R*)

| id | radiais | r | S | T | papel |
|---|---|---:|---|---|---|
| spider-reading-01 | `[3,3,1]` | 2 | `{r0_3}` | `{r1_3}` | SP-R1 |
| spider-reading-02 | `[1,5,1]` | 2 | `{r0_1}` | `{r1_5}` | SP-R2: `d(s,c)=1`, `d(c,t)=5` |
| spider-reading-03 | `[4,4,4]` | 2 | `{r0_4,r1_4,r2_4}` | `{r0_2,r2_2,r2_1}` | SP-R3; mistura mista/desbalanceada deliberada |
| spider-reading-04 | `[2,2,1]` | 2 | `{c,r0_2}` | `{c,r1_2}` | SP-R4 |
| spider-reading-05 | `[1,3,1]` | 1 | `{r0_1}` | `{r1_3}` | SP-R5 (`r'=0`) |
| spider-hand-min3 | `[1,1,1]` | 1 | `{r0_1}` | `{r1_1}` | aranha mínima |
| spider-hand-rad1 | `[1,3,4]` | 2 | `{r1_3}` | `{r2_4}` | radial unitária presente |
| spider-hand-len | `[1,3,6]` | 2 | `{r2_6}` | `{r1_3}` | comprimentos diferentes |
| spider-hand-same | `[2,4,3]` | 2 | `{r1_4}` | `{r1_1}` | só intramural |
| spider-hand-cross | `[3,3,2]` | 2 | `{r0_3}` | `{r1_3}` | só cruzado |
| spider-hand-mix | `[4,4,3]` | 2 | `{r0_4,r1_4}` | `{r0_2,r2_3}` | um intramural + um cruzado |
| spider-hand-cs | `[3,2,1]` | 2 | `{c}` | `{r0_3}` | origem centro |
| spider-hand-ct | `[3,2,1]` | 2 | `{r0_3}` | `{c}` | destino centro |
| spider-hand-diam | `[3,2,1]` | 5 | `{r0_3}` | `{r1_2}` | `r=diam` |
| spider-m-n16-m2-s42 | `[5,5,5]` | 1 | §8.1 | §8.1 | automático |
| spider-m-n16-m4-s43 | `[4,4,4,3]` | 2 | §8.1 | §8.1 | automático |

`n` de `spider-reading-02`: `1 + 1 + (2·2+1) + 1 = 8` para `r=2`. Micro.

### 12.6 Spider — medium

| id | n | radiais | m | seed |
|---|---|---|---|---|
| spider-M-n24-k3-m2-s42 | 24 | 3 | 2 | 42 |
| spider-M-n32-k4-m4-s42 | 32 | 4 | 4 | 42 |

Número de radiais medium: 3 e 4 (`deg(c)≥3`; 4 exercita k>3). A partição está fechada por `q,resto = divmod(n-1,k)` e comprimento `q+1` nas primeiras `resto` radiais: `n=24,k=3 -> [8,8,7]`; `n=32,k=4 -> [8,8,8,7]`. No micro automático: `n=16,k=3 -> [5,5,5]` e `n=16,k=4 -> [4,4,4,3]`.

---

## 13. Colunas CSV

As da spec D, mais:

```text
n_radiais
max_W
n_W
solver_seed
threads
runtime
notes
estrato
alg_variant   # = coluna variante
```

`resultado ∈ {agreement, infeasible_solution, suboptimal, objective_below_reference, unspecified, reference_failure, implementation_error}`.

Linha em falta ≠ acordo.

---

## 14. Redução de contraexemplo

Se divergência confirmada (fluxo R11c da spec):

1. hash = pré-registro;
2. conferir `opt`;
3. `viavel(C)` independente;
4. reler fonte passo a passo;
5. ver se a variante explica (A diverge, B não ⇒ não dizer “o artigo falha”);
6. reduzir `|V|`, `m`, radiais, `r` sem sair da classe.

Se o reduzido tiver `n≤16`, `opt_por_enumeracao`. Comunicação aos autores **antes** de afirmação pública. Relatório interno pode descrever o facto técnico.

---

## 15. Stop criterion (R11)

Parar quando:

1. as três linhas de algoritmo existem ou os casos `unspecified` estão no documento de leituras;
2. este lote (tabelas §12) foi todo escrito no CSV, com status explícito;
3. inconsistências de referência resolvidas ou `INCONCLUSIVE`;
4. divergências confirmadas passaram por R11c;
5. `resultados-r11-certificadores.md` e `conclusao-r11-certificadores.md` existem.

Não alargar sementes, `n`, famílias ou variantes depois de ver o CSV.

Critério de lote (não de prova): o lote está completo mesmo se houver `suboptimal` em PATH-05. Isso não autoriza “corrigir” `path-alg1` no mesmo R11.

---

## 16. Pendência anterior à execução oficial

A preparação de implementação fechou as antigas rubricas PENDING IMPLEMENTATION:

1. mapa semente → (`r`, política): fechado na §8 e em `r11_catalog.py`;
2. partição dos comprimentos das radiais: fechada na §12.6 e em `spider.py::comprimentos_quase_iguais`;
3. helper `opt_fcc`: implementado em `fcc.py` com `y` binário;
4. CLI: `prepare_r11.py`, `verify_r11.py` e `run_r11.py` estão definidos.

Resta uma única pendência que **exige materialização**, não decisão metodológica:

- `sha256` dos arquivos oficiais. Gerar com `prepare_r11.py`, conferir e versionar `instances/estrutural/r11-manifest.csv` antes do lote.

Não estão pendentes: `n_opt_enum`, `max_W`, seeds, `n_medium_max`, IDs, variantes, política F-C3, `WorkLimit`, mapeamento de terminais ou comprimentos medium.


## 17. Ordem antes do lote oficial

A implementação existe, mas esta atualização não executa nenhuma etapa R11.
A ordem obrigatória quando a execução for autorizada é:

1. `PYTHONHASHSEED=0 poetry run python experiments/structural/verify_r11.py`;
2. executar também as regressões estruturais BP/HB/SC/TR exigidas pela spec;
3. commit/versionar a preparação R11 e confirmar working tree limpa;
4. `PYTHONHASHSEED=0 poetry run python experiments/structural/prepare_r11.py`;
5. conferir/versionar `instances/estrutural/r11-manifest.csv` e os arquivos gerados;
6. somente então `PYTHONHASHSEED=0 poetry run python experiments/structural/run_r11.py`.

Se `verify_r11.py` revelar **bug de implementação**, corrigir o código antes da
materialização. Se revelar a divergência matemática já pré-registrada, não
alterar o certificador para coincidir com a referência.


## 18. Reprodução futura

```bash
PYTHONHASHSEED=0 poetry run python experiments/structural/verify_r11.py
# regressões estruturais existentes, conforme a spec
# commit/versione a preparação e deixe a working tree limpa
PYTHONHASHSEED=0 poetry run python experiments/structural/prepare_r11.py
# revisar/versionar instances/estrutural/r11-manifest.csv
PYTHONHASHSEED=0 poetry run python experiments/structural/run_r11.py
```

`prepare_r11.py` exige working tree limpa e não chama solver nem certificador. `run_r11.py` valida todos
os hashes antes de chamar enumeração, baseline ou F-CC e é o único produtor
oficial de `results/structural/r11-certificadores.csv`.
