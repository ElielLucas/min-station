# MIN-STATION — Questões Abertas e Decisões Pendentes

Este arquivo registra pontos que não devem ser resolvidos por suposição da IA ou por conveniência da implementação.

## Q1 — Como tratar `S ∩ T`?

**Status:** aberto.

A formulação corrente possui uma equação de balanço para cada origem e outra para cada destino. Se `v ∈ S ∩ T`, essas duas equações entram em conflito.

O problema de referência não deve ser tratado automaticamente como se `S` e `T` fossem disjuntos.

Alternativas a avaliar:

- declarar formalmente `S ∩ T = ∅` para a variante estudada;
- pré-processar vértices comuns com uma prova de validade;
- adotar balanço unificado `out(v)-in(v)=1_S(v)-1_T(v)` e adaptar ativações.

Não implementar uma dessas opções como decisão definitiva sem validação.

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
