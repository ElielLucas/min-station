---
type: context-ai
file: code-guidelines
title: "MIN-STATION — Diretrizes para Código e Experimentos"
---

# MIN-STATION — Diretrizes para Código e Experimentos

## 1. Objetivo

Este documento define regras para agentes de IA trabalharem no código sem confundir implementação, formulação matemática e hipótese de pesquisa.

Antes de alterar implementação, leia o repositório real.

## 2. Não inferir arquitetura pelos artigos

Os artigos registram formulações e experimentos de momentos específicos da pesquisa. Eles não provam a estrutura atual do repositório.

Antes de editar:

1. localizar leitura/geração de instâncias;
2. localizar a construção de `V`, `E`, `S`, `T`, `r` e distâncias;
3. localizar a construção de `A_r`;
4. localizar as variáveis e famílias de restrições;
5. localizar objetivo e parâmetros do solver;
6. localizar exportação de resultados e testes;
7. identificar qual formulação/método está sendo executado.

## 3. Separação recomendada de responsabilidades

Quando a arquitetura permitir, manter conceitualmente separadas:

- leitura/geração de instância;
- pré-processamento de distâncias;
- construção do dígrafo de alcance;
- construção de cada formulação;
- componentes de cortes/decomposição/relaxação, quando existirem;
- configuração e execução do solver;
- extração da solução;
- validação/reconstrução de rotas;
- experimentos e relatórios.

Não criar novas camadas apenas para satisfazer esta lista. Respeitar primeiro a arquitetura existente.

## 4. Baseline e formulações experimentais

A formulação descrita em `base-formulation.md` é o **baseline atual**.

Não alterá-la silenciosamente para testar uma ideia nova. Preferir uma destas estratégias:

- nova função/classe de construção de modelo;
- opção explícita de configuração;
- branch experimental claramente identificada;
- módulo adicional para cortes, relaxações ou decomposições.

Toda formulação/método experimental deve ter nome inequívoco nos resultados.

Se versões históricas precisarem permanecer no repositório, evitar nomes vagos como `model_new.py`, `model2.py` ou `final.py`.

## 5. Fonte única por formulação

Evitar duplicar a mesma família de restrições em vários scripts.

Se houver uma função central que constrói o baseline, testes e experimentos devem reutilizá-la sempre que possível.

Não manter simultaneamente versões diferentes sob o mesmo identificador.

## 6. Nomenclatura matemática

Sempre que possível, preservar correspondência com a documentação:

- `V`, `E` — grafo;
- `S`, `T` — origens e destinos;
- `m` — número de robôs;
- `r` — autonomia;
- `A_r` — arcos de alcance;
- `y[v]` — instalação;
- `f[u,v]` — fluxo agregado do baseline.

Novas formulações podem usar variáveis diferentes, mas o mapeamento matemático deve ser documentado.

## 7. Testes mínimos

Qualquer alteração que pretenda manter a mesma semântica do MIN-STATION deve preservar casos pequenos com solução verificável.

Casos recomendados:

1. origem e destino a distância `<= r`: ótimo 0;
2. exatamente uma estação necessária;
3. estação ótima localizada em uma origem para servir outro fluxo;
4. estação ótima localizada em um destino para servir outro fluxo;
5. múltiplos robôs compartilhando uma estação;
6. vários pareamentos possíveis;
7. grafo com ciclos;
8. caso `S ∩ T != ∅`, após a política correspondente ser formalmente definida.

Validar, quando possível:

- valor objetivo;
- conjunto de estações;
- balanço/viabilidade;
- validade dos saltos;
- reconstrução das rotas.

## 8. Comparação experimental

Ao comparar formulações ou métodos, manter controlados:

- conjunto de instâncias;
- convenção de distância;
- limite de tempo;
- versão do solver;
- seed e threads, quando relevantes;
- gap alvo e demais parâmetros não padrão;
- hardware, quando a comparação depender de tempo.

Registrar pelo menos:

- incumbente/melhor solução inteira;
- limite dual;
- gap;
- nós de busca;
- tempo;
- variáveis e restrições;
- tempo de pré-processamento quando significativo;
- status final.

Não interpretar `time limit` com solução incumbente como prova de otimalidade.

## 9. Técnicas adicionais

Cortes, callbacks, relaxações, decomposições ou algoritmos híbridos devem ficar desacoplados da definição do problema sempre que possível.

Ao introduzir uma técnica:

1. declarar qual formulação ela usa como base;
2. explicar a propriedade matemática explorada;
3. distinguir restrição válida de heurística;
4. registrar se a técnica preserva exatidão;
5. comparar com a mesma formulação sem a técnica.

## 10. Resultados negativos

Não remover automaticamente implementações ou logs apenas porque uma abordagem teve desempenho ruim.

Antes, registrar o suficiente para entender:

- tamanho do modelo;
- qualidade do limite;
- comportamento da árvore de busca;
- custo da técnica adicionada;
- instâncias em que houve melhora ou piora.

## 11. Regra final

Se uma mudança alterar a semântica descrita em `base-formulation.md`, ela não é apenas uma otimização de código: é uma nova formulação ou uma nova variante e deve ser documentada como tal.
