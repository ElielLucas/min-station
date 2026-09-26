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

**Status:** precisa ser explicitado por experimento/instância.

No problema original, autonomia é medida em passos.

Se as arestas das instâncias tiverem comprimentos e o dígrafo de alcance usar caminho mínimo ponderado, trata-se de uma extensão ponderada.

Documentação, nomes de experimento e conclusões devem distinguir os dois casos.

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
