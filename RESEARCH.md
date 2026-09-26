# RESEARCH — MIN-STATION

## 1. Objetivo da pesquisa

Este projeto investiga o **Minimum Charging Station Placement Problem (MIN-STATION)** sob a perspectiva de **Programação Linear Inteira e métodos exatos de otimização**.

O objetivo principal é desenvolver, analisar e comparar abordagens capazes de melhorar a resolução do problema em grafos gerais. O interesse não está restrito a uma única formulação: a pesquisa pode envolver formulações alternativas, fortalecimento de modelos, relaxações, decomposições, cortes e estratégias de solução integradas ao processo de branch-and-bound/branch-and-cut.

O foco deve permanecer na contribuição matemática e computacional para a resolução do MIN-STATION, com experimentos reprodutíveis e comparação justa entre abordagens.

## 2. Problema de referência

A referência conceitual é o MIN-STATION definido por Das:

- grafo simples, não direcionado e conexo `G = (V,E)`;
- conjunto de origens `S ⊆ V`;
- conjunto de destinos `T ⊆ V` (Das não exige `S ∩ T = ∅`: um vértice pode ser origem de um robô e alvo de outro ao mesmo tempo);
- `|S| = |T| = m`;
- robôs não rotulados;
- autonomia comum `r`;
- cada robô inicia com carga completa;
- após atingir uma estação, pode voltar a percorrer até `r` passos antes de nova recarga;
- cada destino deve estar ocupado por exatamente um robô ao final;
- objetivo: minimizar o número de vértices com estações.

A solução do problema original é um conjunto `C ⊆ V`.

## 3. Baseline atual

A formulação base atual do repositório utiliza:

1. fluxo agregado de robôs;
2. dígrafo de alcance para representar deslocamentos possíveis com uma carga;
3. autonomia comum;
4. variáveis de instalação em qualquer `v ∈ V`;
5. minimização da quantidade de estações;
6. restrições específicas para permitir que origens e destinos sejam usados como estações quando necessário;
7. balanço unificado que admite `S ∩ T ≠ ∅` (rodada E5; ver `docs/context-ai/base-formulation.md` §6 e `docs/technical/governance/open-questions.md` Q1).

Essa formulação é o **baseline atual para desenvolvimento e comparação**, não o limite do escopo científico do projeto.

A mudança que passou a permitir estações em todo `V` surgiu como uma evolução da formulação apresentada no artigo da SBPO, aproximando esse baseline da definição original do problema. Essa motivação histórica não deve ser tratada como o objetivo final da pesquisa.

## 4. Direção de investigação

A pesquisa deve buscar responder perguntas como:

- quais formulações representam o problema de forma mais forte ou compacta;
- como melhorar a qualidade da relaxação linear;
- quais desigualdades válidas ou cortes reduzem a árvore de busca;
- quando decomposições ou relaxações estruturadas são vantajosas;
- quais propriedades do problema podem ser exploradas em pré-processamento;
- como diferentes abordagens se comportam em função do tamanho, densidade, autonomia e estrutura das instâncias.

Uma abordagem que não melhora o baseline também é um resultado relevante quando a comparação é bem documentada e ajuda a entender a estrutura computacional do problema.

## 5. Fora do escopo padrão

Não fazem parte do baseline atual, salvo solicitação explícita:

- formulação generalizada do artigo da SBPO;
- custos de instalação `c_v`;
- autonomia individual `r_s`;
- elegibilidade `e_{s,t}`;
- problemas de colisão entre robôs;
- capacidade de atendimento de uma estação;
- tempo de recarga;
- limite de robôs simultâneos por vértice.

Esses elementos podem definir outros problemas ou extensões, mas não devem ser introduzidos inadvertidamente durante o estudo do MIN-STATION base.

## 6. Critérios para avaliar novas abordagens

Ao comparar formulações ou técnicas, registrar sempre que aplicável:

- valor da melhor solução inteira;
- melhor limite dual;
- gap;
- tempo até primeira solução e até prova de otimalidade;
- número de nós de busca;
- número de variáveis e restrições;
- tempo de pré-processamento;
- status do solver;
- versão do código, solver e parâmetros relevantes.

Resultados devem ser comparados sobre instâncias e configurações compatíveis.

## 7. Fontes principais

Os artigos e documentos de referência fazem parte do contexto do projeto e têm papéis diferentes:

- **Das:** definição do MIN-STATION e resultados teóricos originais;
- **artigo da SBPO:** marco anterior da pesquisa, com a primeira formulação de PLI desenvolvida no projeto e a variante de estações apenas em vértices intermediários;
- **formulação base atual:** baseline posterior, com estações permitidas em todos os vértices.

O detalhamento e a precedência dessas fontes estão em:

`docs/technical/reference/source-map.md`
