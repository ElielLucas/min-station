# R11 — resultados dos certificadores de classes especiais

**Data:** 2026-10-07  
**Spec:** `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`  
**Pré-registro:** `docs/technical/reference/pre-registro-r11-certificadores.md`  
**Leituras:** `docs/technical/reference/leituras-r11-certificadores.md`  
**CSV:** `results/structural/r11-certificadores.csv`  
**Auditoria:** `docs/technical/reference/auditoria-r11-divergencias.md`  
**Commit registrado no CSV:** `dd485dc`  
**F-C3:** `OPEN` em todo o lote

## 1. Cobertura do lote

O lote oficial contém 44 instâncias e 80 linhas `(instância, variante)`:

| família | instâncias | linhas |
|---|---:|---:|
| path | 15 | 15 |
| cycle | 11 | 11 |
| spider | 18 | 54 |
| **total** | **44** | **80** |

Por estrato:

| estrato | instâncias | linhas |
|---|---:|---:|
| micro | 37 | 69 |
| medium | 7 | 11 |

O catálogo, as seeds, tamanhos, valores de `r`, políticas `S/T`, variantes e caps foram congelados antes do `run_r11.py`.

---

## 2. Consistência das referências

A pilha de referência terminou sem falha:

| referência | resultado |
|---|---|
| baseline | `OPTIMAL` em 80/80 linhas |
| enumeração | `OPTIMAL` nas 69 linhas micro; `not_run_cap` nas 11 medium |
| F-CC binária | `OPTIMAL` em 80/80 linhas |
| F-C3 | `OPEN` em 80/80 linhas |
| `reference_failure` | 0 |
| `objective_below_reference` | 0 |
| `implementation_error` | 0 |

Quando enumeração e baseline foram ambos executados, seus ótimos coincidiram. F-CC coincidiu com o `opt` certificado em todas as linhas em que foi executada; neste lote, nenhuma instância excedeu `max_W=200000` (maior `n_W` observado: 14664).

Portanto, as divergências abaixo são classificadas contra uma referência exata consistente.

---

## 3. Resultado global

| classificação | linhas | fração |
|---|---:|---:|
| `agreement` | 19 | 23,75% |
| `suboptimal` | 32 | 40,00% |
| `infeasible_solution` | 13 | 16,25% |
| `unspecified` | 16 | 20,00% |
| **total** | **80** | **100%** |

Não houve `reference_failure`, `objective_below_reference` nem `implementation_error`.

---

## 4. Caminhos — `path-alg1`

| resultado | linhas |
|---|---:|
| agreement | 3 |
| suboptimal | 12 |
| infeasible | 0 |
| unspecified | 0 |

Todas as soluções `path-alg1` retornadas no lote foram viáveis. A divergência é de **cardinalidade**: em 12/15 casos o procedimento literal instalou mais estações que o ótimo.

Exemplos:

| instância | Alg. 1 | OPT | referência | resultado |
|---|---:|---:|---|---|
| `path-hand-opt0-r2` | 1 | 0 | enum | suboptimal |
| `path-hand-one-r1` | 2 | 1 | enum | suboptimal |
| `path-hand-sit` | 2 | 0 | enum | suboptimal |
| `path-hand-sit-nperm` | 4 | 2 | enum | suboptimal |
| `path-hand-diam` | 1 | 0 | enum | suboptimal |
| `path-M-n32-m4-s42` | 13 | 11 | mip_base | suboptimal |

O padrão coincide com PATH-05 de `leituras-r11-certificadores.md`: o pseudocódigo incrementa `Vcounter` no próprio vértice de origem e coloca estação quando o contador de **vértices ativos** chega a `r`.

A auditoria pós-lote reduz o mecanismo ao caminho mínimo `v0-v1`, `r=1`, para o qual Algorithm 1 retorna uma estação embora `OPT=0`.

**Conclusão da família:** `path-alg1` literal **não é um certificador exato** da definição do MIN-STATION usada no projeto.

---

## 5. Ciclos — `cycle-alg2`

| resultado | linhas |
|---|---:|
| agreement | 2 |
| suboptimal | 9 |
| infeasible | 0 |
| unspecified | 0 |

Assim como em caminhos, todas as soluções retornadas foram viáveis, mas 9/11 ficaram acima do ótimo.

Exemplos:

| instância | Alg. 2 | OPT | resultado |
|---|---:|---:|---|
| `cycle-hand-n5-r1` | 2 | 1 | suboptimal |
| `cycle-hand-breaks` | 2 | 0 | suboptimal |
| `cycle-hand-sym` | 1 | 0 | suboptimal |
| `cycle-m-n16-m4-s42` | 4 | 2 | suboptimal |
| `cycle-M-n32-m4-s42` | 7 | 6 | suboptimal |

O Algorithm 2 chama Algorithm 1 para cada quebra; portanto herda a supercontagem do caminho. A auditoria reduz o mecanismo ao triângulo `n=3`, `S={v0}`, `T={v1}`, `r=1`, em que o procedimento retorna 1 contra `OPT=0`.

**Conclusão da família:** `cycle-alg2` literal **não é um certificador exato** da definição corrente do MIN-STATION.

---

## 6. Aranhas

Cada uma das 18 instâncias de aranha foi executada com `spider-A`, `spider-B` e `spider-U`.

### 6.1 Por variante

| variante | agreement | suboptimal | infeasible | unspecified |
|---|---:|---:|---:|---:|
| `spider-A` | 6 | 1 | 8 | 3 |
| `spider-B` | 5 | 10 | 0 | 3 |
| `spider-U` | 3 | 0 | 5 | 10 |

Nenhuma das três variantes funciona como certificador exato universal:

- `spider-A` preserva a leitura folha→centro, mas pode devolver conjunto inviável em movimento cruzado;
- `spider-B` adiciona uma reconstrução via path na radial de entrada; torna várias soluções viáveis, porém frequentemente superconta;
- `spider-U` prefere `unspecified` nos silêncios explicitamente identificados, mas em SP-R1/SP-R2 ainda reproduz a leitura A e pode devolver conjunto inviável.

### 6.2 SP-R1

`spider-reading-01`:

| variante | obj | viável | OPT | resultado |
|---|---:|---:|---:|---|
| A | 2 | não | 2 | infeasible_solution |
| B | 3 | sim | 2 | suboptimal |
| U | 2 | não | 2 | infeasible_solution |

Mesmo cardinalidade não basta: A/U têm `obj=OPT`, mas `C` é inviável.

### 6.3 SP-R2

`spider-reading-02` é o caso construído `d(s,c)=1`, `d(c,t)=2r+1`, radial de alvo sem origem.

| variante | C | obj | viável | OPT | resultado |
|---|---|---:|---:|---:|---|
| A | `{c}` | 1 | não | 2 | infeasible_solution |
| B | `{r1_4,r1_2,c}` | 3 | sim | 2 | suboptimal |
| U | `{c}` | 1 | não | 2 | infeasible_solution |

A construção é estruturalmente mínima para SP-R2 com `r=2`: `1 + 1 + 5 + 1 = 8` vértices.

### 6.4 SP-R3

`spider-reading-03` retornou `unspecified` nas três variantes devido a radial mista desbalanceada (`INT-A`). Esse resultado é deliberado: a fonte não determina sem reconstrução como escolher os remanescentes naquela radial.

### 6.5 SP-R4 — `S∩T`

`spider-reading-04`:

| variante | resultado |
|---|---|
| A | agreement (`0 = OPT`) |
| B | suboptimal (`2 > 0`) |
| U | unspecified (`S∩T`) |

A execução confirma por que `v∈S∩T` não pode ser simplesmente cancelado: a leitura escolhida altera o comportamento.

### 6.6 SP-R5 — `r'=0`

`spider-reading-05`:

| variante | resultado |
|---|---|
| A | infeasible_solution |
| B | suboptimal (`5 > 3`) |
| U | unspecified (`r'=0`) |

A variante U mantém o silêncio da fonte em vez de inserir uma estação não publicada.

---

## 7. `S∩T` e permanência

A cobertura oficial inclui:

- `S∩T=∅`;
- uma interseção;
- interseção sem permanência forçada pelo matching;
- `S=T`;
- centro em `S`, centro em `T` e centro em `S∩T`;
- movimento intramural, cruzado e misto.

Os resultados não sustentam nenhum pré-processamento que apague `S∩T`. `path-hand-stay` e `cycle-hand-stay` dão agreement com `C=∅`, enquanto outros casos com interseção têm comportamento distinto.

---

## 8. Casos `r ≥ diam(G)`

A spec corrigida exigiu **testar** esses casos, não special-case do certificador.

- `path-hand-diam`: Algorithm 1 retorna 1 contra `OPT=0` → suboptimal;
- `spider-hand-diam`: A/B/U retornam `C=∅` → agreement;
- ciclo mínimo `cycle-hand-n3-opt0` com `r=2` retorna `C=∅` → agreement.

Isto confirma que o requisito correto é preservar o algoritmo literal e classificar o resultado, não forçar `C=∅` dentro do certificador.

---

## 9. Divergências e redução

A auditoria separa as 45 linhas divergentes em mecanismos repetidos:

1. **D-PATH:** supercontagem do Algorithm 1;
2. **D-CYCLE:** herança de D-PATH pelo Algorithm 2;
3. **D-SPIDER-ENTRY:** lacuna de estações na descida para radial de alvo;
4. **D-SPIDER-PATH:** reconstrução B herda a supercontagem de path;
5. silêncios da fonte: `unspecified`, não divergência.

Casos mínimos/reduzidos e a releitura de fonte estão em `auditoria-r11-divergencias.md`.

---

## 10. O que estes resultados permitem afirmar

**[Conferido]** O lote oficial contém divergências exatas entre os procedimentos literais de caminho/ciclo e o MIN-STATION formal do projeto.

**[Conferido]** As três leituras de aranha testadas não produzem um certificador exato universal no lote; SP-R2 oferece um witness direto para A/U e subotimalidade para B.

**[Conferido]** As referências exatas usadas pela R11 são internamente consistentes no lote.

---

## 11. O que estes resultados não permitem afirmar

- não provam uma caracterização matemática corrigida para caminhos/ciclos;
- não identificam automaticamente a correção adequada do artigo;
- não provam, sem revisão humana/contato, um erratum público;
- não transformam `spider-U` em algoritmo: `unspecified` continua ausência deliberada de definição;
- não dizem que baseline/F-CC são mais rápidos; aqui eles são referências exatas;
- não fecham F-C3, que permanece `OPEN`.

---

## 12. Resultado da R11

O lote não terminou em “nenhuma divergência”. Portanto o ramo aplicável da spec é:

```text
CONFIRMED DIVERGENCE
```

A formulação precisa desse veredito está em `docs/technical/reference/conclusao-r11-certificadores.md`.
