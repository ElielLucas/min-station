# MIN-STATION — Questões Abertas e Decisões Pendentes

Este arquivo registra pontos que não devem ser resolvidos por suposição da IA ou por conveniência da implementação.

## Q1 — Como tratar `S ∩ T`? — FECHADA (rodada E5)

**Status:** fechada. Adotado o balanço unificado (variante U).

Das não exige `S` e `T` disjuntos: a definição do Problem 1 usa `S ⊆ V`, `T ⊆ V`
sem cláusula de disjunção, e a prova do Lema 5 depende explicitamente de um
vértice que é origem e alvo ao mesmo tempo ("every robot is starting from a
target position"; "The robot starting at s_i remains at s_i occupying the
target t_o", p. 11–12 de `docs/technical/reference/min-station-das.pdf`). A
formulação com balanços separados (uma equação por origem, outra por
destino) ficava inviável para `v ∈ S ∩ T` (a soma das duas dá `0 = 2`),
embora o MIN-STATION seja sempre viável — um falso negativo, documentado
como P1 em `validacao-formulacao-base.md`.

Decisão: adotar o balanço unificado, com `a_v = 1_S(v)`, `b_v = 1_T(v)`:

```
out(v) - in(v) = a_v - b_v
in(v)  <= b_v + (m - b_v) y_v
out(v) <= a_v + (m - a_v) y_v
```

Verificado caso a caso (`base-formulation.md` §10.1) que esta forma coincide
exatamente com a formulação anterior quando `S ∩ T = ∅` — nenhum resultado
experimental já obtido é afetado, pois todas as 22 instâncias do repositório
têm `|S ∩ T| = 0` por construção do gerador. Implementado em `baseline.py`
(rodada E5); as famílias de cortes `generate_C4_DM` e as redes de fluxo em
`experiments/cuts/cuts.py` foram revisadas para tratar `S ∩ T` de forma
consistente com o Lema 5 (o robô pode ficar parado ocupando o próprio alvo,
sem exigir estação).

As alternativas descartadas: declarar `S ∩ T = ∅` por decisão (restringiria
o problema); pré-processar vértices comuns removendo-os de S e T (provado
inválido por contraexemplo em `validacao-formulacao-base.md`, CE1').

## Q2 — O projeto resolve o MIN-STATION original ou uma versão ponderada?

**Status:** classificação por instância registrada (revisão pré-E8); falta
decidir se as conclusões por regime devem ser reproduzidas na versão em passos.

No problema original, autonomia é medida em passos.

Se as arestas das instâncias tiverem comprimentos e o dígrafo de alcance usar caminho mínimo ponderado, trata-se de uma extensão ponderada.

Documentação, nomes de experimento e conclusões devem distinguir os dois casos.

O pipeline (`ms_utils.construir_arcos_alcance`) usa Dijkstra com os pesos do
arquivo e `d(u,v) ≤ R`. Medição nos arquivos de `instances/` usados de E0 a E8:

| Instância | Pesos | Arcos sem reverso | R | Classe |
|---|---|---|---|---|
| hc9u | todos 1 | 0 | 1 | Das (passos, não dirigido) |
| hc10p, hc11p, hc12p | 100–110 | 0 | 150 | equivalente a Das com r=1 (ver abaixo) |
| bip42p | 101–110 | 0 | 200 | equivalente a Das com r=1 (ver abaixo) |
| cc10-2p, cc12-2p | 101–310 | 0 | 500 | extensão ponderada |
| Chicago st15 | 1–17 | 48 de 1130 | 26 (7 nos experimentos) | extensão ponderada e dirigida |
| Barcelona st15 | 1–89 | 1074 de 2522 | 24 (5 nos experimentos) | extensão ponderada e dirigida |
| Philadelphia st5 / st25 | 1–8 | 12 de 2404 | 22 / 3 (2 / 3 nos experimentos) | extensão ponderada e dirigida |

Nenhuma dessas instâncias tem `S ∩ T ≠ ∅`.

O que define a instância para a formulação é `A_r`, não os pesos. Em hc10p–hc12p
e bip42p toda aresta cabe numa carga (peso ≤ 110 ≤ R) e dois passos nunca cabem
(≥ 200 > R), então `A_r = E` (confirmado em `results/cuts/e5_estrutura.csv`,
coluna `Ar_igual_E`): são exatamente as instâncias de Das com r=1 no mesmo grafo.
Em cc10-2p/cc12-2p um salto pode ter duas arestas curtas mas não uma longa, o que
nenhuma autonomia em passos reproduz.

**Instâncias triviais.** Com o R gravado no arquivo, Chicago st5 (R=32), Philadelphia st39 (R=20)
e Barcelona st54 (R=21) têm r ≥ λ\* (distância de gargalo do emparelhamento S–T), logo OPT = 0.
Detalhes em `docs/technical/reference/benchmark-v1.md` §5.

## Q3 — Demonstração de equivalência do fluxo agregado

**Status:** demonstração formal a consolidar.

O modelo usa fluxo inteiro agregado em vez de rotas individuais.

A correção da formulação deve justificar as duas direções:

1. uma solução do MIN-STATION gera uma solução inteira do PLI com o mesmo número de estações;
2. uma solução inteira do PLI pode ser decomposta em rotas válidas de robôs, sem que ciclos de fluxo artificiais sejam necessários.

Resultados computacionais iguais não substituem essa demonstração.

## Q4 — Como fortalecer o baseline atual?

**Status:** linha de pesquisa aberta.

O Big-M `m = |S|` é seguro para fluxo total, mas pode gerar relaxação linear fraca. O fortalecimento do baseline pode envolver esse ponto ou outras estruturas do modelo.

Investigar, sem alterar silenciosamente a definição do problema:

- limites locais mais fortes;
- desigualdades válidas e cortes;
- pré-processamento;
- remoção de arcos/vértices dominados quando houver prova;
- reformulações alternativas;
- relaxações/decomposições adequadas à estrutura do problema.

Cada alternativa deve ser comparada com o baseline em condições experimentais compatíveis.

## Q5 — Como reconstruir rotas no grafo original?

**Status:** depende da necessidade da implementação.

O PLI opera no dígrafo de alcance. Se o projeto precisar apresentar trajetos completos, o pré-processamento deve guardar um caminho correspondente para cada arco de alcance utilizado.

A rota reconstruída deve respeitar a mesma métrica usada na construção de `A_r`.

## Q6 — Qual versão é a baseline experimental oficial?

**Status:** deve ser definido quando novos experimentos forem consolidados.

Registrar para cada campanha:

- commit/tag;
- conjunto de instâncias;
- convenção de distância;
- versão do solver;
- parâmetros não padrão;
- limite de tempo;
- formulação exata usada.

Não comparar resultados de versões diferentes como se fossem da mesma formulação.

## Q7 — Instâncias dirigidas estão no escopo?

**Status:** aberta (levantada na revisão pré-E8).

Das define o problema em grafo não dirigido. O conversor TNTP
(`src/converters/gen_min_station_tntp_to_minstation.py`) mantém os arcos
dirigidos da rede de transporte, e `construir_adjacencia` não os simetriza;
em Barcelona 1074 de 2522 arcos não têm reverso. A formulação continua bem
definida num dígrafo, mas a validação formal (`validacao-formulacao-base.md`)
foi feita para grafo não dirigido e distância em passos, e o corte C2 precisou
de `dijkstra_to` justamente por causa da assimetria.

Decidir: (a) manter as TNTP como extensão dirigida declarada, (b) simetrizar
na conversão, ou (c) tirá-las das conclusões sobre o problema de Das.

**Decisão (2026-09-26, delegada):** (a) para as instâncias atuais, que ficam fora das conclusões
sobre Das; versão retrabalhada (não dirigida, com subdivisão e terminais fora das folhas) no
lote 2 do benchmark-v1.

