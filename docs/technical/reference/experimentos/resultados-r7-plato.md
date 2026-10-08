# Resultados R7 — anatomia do platô do núcleo

**Data:** 2026-10-06
**Pré-registro:** `docs/technical/reference/experimentos/pre-registro-r5.md` §4
**CSV:** `results/benchmark/r7-plato.csv`, resumo `results/benchmark/r7-plato-resumo.csv`
**Cap:** N = 200 ótimos do núcleo por instância. Sem CBI. Sem laço iterativo.
**H-desc:** um C inviável é caso H-desc se o emparelhamento perfeito no grafo de pares (arcos diretos em D ∪ bicliques B(K) das componentes de H[C]) falha.

## Contagens

| Instância | OPT_core | Gravados | Truncado | Viáveis (oráculo) | Inviáveis | H-desc | Inviáveis não H-desc | Z distintos | Max um Z |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TR-k2-L5-r2 | 3 | 8 | 0 | 2 | 6 | 6 | 0 | 4 | 2 |
| BP-nao-[3,1]-q2 | 6 | 2 | 0 | 0 | 2 | 2 | 0 | 2 | 1 |
| mapf-maze-32-32-2-m10-f4 | 5 | 200 | 1 | 0 | 200 | 200 | 0 | 55 | 49 |
| lin-lin03-regiao-f4 | 5 | 200 | 1 | 0 | 200 | 200 | 0 | 65 | 17 |
| puc-cc9-2p-seed-r1 | 27 | 200 | 1 | 0 | 200 | 200 | 0 | 66 | 21 |

TR reproduz o Apêndice B: 8 ótimos do núcleo, 2 viáveis, 6 inviáveis. Pool completo (não truncado).

BP n=16: oráculo e `independent_validator` concordam em todas as soluções gravadas (zero discordâncias). TR tem n=18, acima do limiar do validador; maze/lin/cc9 também.

Maze, lin e cc9 truncaram no cap. A fracção do platô coberta é **desconhecida**. Os ≤200 gravados são a evidência; não se extrapola.

Nenhum C gravado com OPT_core nas três instâncias truncadas foi viável (oráculo). Isso é compatível com Γ exacto do maze (2) e do lin (2): o núcleo está abaixo de OPT, portanto o pool a esse custo não contém solução do MIN-STATION. Em cc9 o Γ é intervalo [3, 4]; nenhum dos 200 C a custo 27 passou o oráculo.

## Veredito H-desc

**CONFIRMED** na amostra gravada: todo C inviável gravado é caso H-desc; nenhum C inviável deixa o emparelhamento por componentes viável (`n_inviaveis_nao_hdesc = 0` nas cinco instâncias).

O truncamento impede afirmar o mesmo para o platô inteiro de maze, lin e cc9. O veredito aplica-se aos C gravados.

## Componentes de H[C]

- TR: 1, 2 ou 3 componentes (mistura).
- BP-[3,1]: 2 componentes nos 2 C.
- Maze: 199/200 C com 5 componentes e OPT_core = 5 (uma estação por componente, quase sempre).
- lin: 5, 4 ou 3 componentes (112 / 87 / 1) com OPT_core = 5.
- cc9: 21–25 componentes com OPT_core = 27.

Nas instâncias com Γ > 0 medidas aqui, o núcleo mínimo dispersa as estações em H: as componentes não realizam, em conjunto, o emparelhamento S–T.

## Cortes Z do oráculo

Nenhum Z único cobre o platô gravado. O Z mais frequente no maze elimina 49 dos 200 C; em lin, 17; em cc9, 21. Há 55, 65 e 66 Z distintos nessas três instâncias. Um corte Z por vez (CBI) não é uma família compacta nestes pools.

## Hipótese (não implementada)

Os C inviáveis falham porque as componentes de H[C] não induzem um emparelhamento S–T via D ∪ {B(K)}. Isso é a descrição H-desc, confirmada nos C gravados.

Hipótese de família válida (R10, ainda bloqueado): desigualdades que exigem que o suporte de y, ou um subconjunto pago, seja compatível com uma configuração conexa em H que cubra os pares exigidos — a mesma motivação da F-CC, agora com evidência de platô além dos gadgets. Não se implementa nesta spec.

Não se encontrou uma família de cortes Z repetíveis que substitua essa hipótese: os Z são muitos e cada um cobre uma fracção pequena do pool (exceto um Z no maze, 49/200).

---

**Nota de auditoria N1-T0/T4 (2026-10-07).** `max_elimina_um_Z` no resumo antigo registra apenas **frequência de retorno** de um Z pelo oráculo, não quantas instalações seriam eliminadas por ele. `n_origens_sem_par` conta **grau zero** em `B_C`, não origens não emparelhadas por matching máximo. H-desc é a própria caracterização da viabilidade por componentes e emparelhamento, **não** mecanismo causal novo. A releitura offline separa retorno/cobertura (cc9: **21/27**), deficiência de Hall e testemunhas. Resultados válidos só para os 610 C gravados, incluindo três pools truncados em 200; ver `n1-t4-auditoria-r7.md`.
