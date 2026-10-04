---
type: context-ai
file: project-overview
title: "MIN-STATION — Visão Geral do Projeto"
---

# MIN-STATION — Visão Geral do Projeto

## 1. O que é o projeto

Este repositório é um projeto de pesquisa sobre o problema de alocação mínima de estações de recarga para robôs com autonomia limitada, conhecido como **MIN-STATION**.

O problema de referência foi definido por Arun Kumar Das. Dado um grafo `G = (V,E)`, um conjunto de posições iniciais `S`, um conjunto de destinos `T`, com `|S| = |T|`, e uma autonomia comum `r`, deve-se instalar o menor número possível de estações para permitir que os robôs completem o movimento.

Os robôs são **não rotulados**: não existe pareamento origem-destino pré-fixado.

Das não exige `S ∩ T = ∅`: um mesmo vértice pode ser origem de um robô e alvo de outro (a prova do Lema 5 do artigo depende explicitamente desse caso — o robô pode ficar parado ocupando o próprio alvo). O baseline atual trata isso com um balanço unificado (ver `docs/context-ai/base-formulation.md` §6); não reintroduzir a suposição de disjunção sem decisão explícita.

## 2. Objetivo científico

O objetivo do projeto é avançar a resolução do MIN-STATION no âmbito de **Programação Linear Inteira e métodos exatos de otimização**.

A pesquisa não está vinculada a uma única formulação. O repositório pode conter e comparar diferentes modelos, fortalecimentos, relaxações, decomposições, cortes, pré-processamentos e outras estratégias voltadas a melhorar limites, desempenho e escalabilidade.

A formulação base atual funciona como **baseline experimental e matemático**.

## 3. Baseline atual

O baseline corrente utiliza:

- fluxo agregado;
- dígrafo de alcance;
- autonomia comum;
- variáveis de instalação `y_v` para todo `v ∈ V`;
- objetivo de minimizar o número total de estações.

A possibilidade de instalar estações em todo `V`, inclusive em origens e destinos, foi introduzida depois do artigo da SBPO como uma evolução da formulação base. Essa alteração aproxima o baseline da definição original de Das, mas não constitui o objetivo global da pesquisa.

### Não usar automaticamente no baseline

A menos que a tarefa peça explicitamente, não considerar:

- a formulação generalizada do artigo da SBPO;
- custos heterogêneos;
- autonomias heterogêneas;
- elegibilidade entre origens e destinos;
- a antiga formulação em que apenas vértices intermediários podem receber estações.

## 4. Estrutura de contexto

```text
min-station/
├── CLAUDE.md
├── RESEARCH.md
├── docs/
│   ├── project-overview.md
│   ├── context-ai/
│   │   ├── min-station-domain.md
│   │   ├── base-formulation.md
│   │   ├── research-direction.md
│   │   └── code-guidelines.md
│   └── technical/
│       ├── README.md
│       ├── governance/
│       │   └── open-questions.md
│       └── reference/
│           ├── source-map.md
│           ├── min-station-das.pdf
│           ├── novo_artigo_das_2026.pdf
│           ├── artigo-sbpo.pdf
│           ├── formulacao-base-all-vertices.pdf
│           └── overlap-ijcai2026-min-station.md
└── ... código do projeto ...
```

Os nomes dos PDFs são uma convenção sugerida. Atualize `source-map.md` se os nomes reais forem diferentes.

## 5. Ordem de leitura para IA

### Nível 0 — sempre

1. `docs/project-overview.md`
2. `RESEARCH.md`

### Nível 1 — conforme a tarefa

| Necessidade | Fonte |
|---|---|
| Definição do MIN-STATION e terminologia | `docs/context-ai/min-station-domain.md` |
| Formulação base atual | `docs/context-ai/base-formulation.md` |
| Novas formulações/técnicas de otimização | `docs/context-ai/research-direction.md` |
| Mudanças de implementação | `docs/context-ai/code-guidelines.md` + código relevante |
| Lacunas ou hipóteses não fechadas | `docs/technical/governance/open-questions.md` |
| Backlog de continuação e histórico de tarefas | `docs/technical/plans/backlog-continuacao.md` |
| Relação entre artigos/documentos | `docs/technical/reference/source-map.md` |

Não carregar todos os arquivos por precaução. Ler o conjunto mínimo necessário para a tarefa.

## 6. Invariantes do problema base

### 6.1 Robôs não rotulados

Não existe associação fixa entre uma origem `s ∈ S` e um destino `t ∈ T`.

### 6.2 Quantidade de robôs e destinos

`|S| = |T| = m`.

Ao final, cada destino deve ser ocupado por exatamente um robô.

### 6.3 Autonomia

Um robô pode percorrer no máximo `r` entre dois pontos consecutivos nos quais sua bateria está cheia.

Na definição original de Das, `r` é medido em passos/arestas. Se uma implementação usar pesos ou comprimentos de aresta, isso deve ser documentado explicitamente como extensão ou convenção experimental.

### 6.4 Início e destino

O robô inicia em sua origem com bateria completa e pode terminar em um destino sem que exista estação nesses vértices.

Uma origem ou destino só precisa de estação quando for efetivamente usado como ponto de recarga para continuidade de algum fluxo.

### 6.5 Estações no baseline atual

A formulação base corrente define `y_v` para todo `v ∈ V`.

Nunca substituir automaticamente por `v ∈ V \ (S ∪ T)`.

### 6.6 Compartilhamento

Uma estação pode ser utilizada por vários robôs. O problema base não modela capacidade da estação nem conflito de ocupação.

### 6.7 Rotas não são entrada

Nem o pareamento origem-destino nem os caminhos são fornecidos como parte da entrada.

## 7. Relação entre pesquisa e baseline

- O **problema de Das** define o objeto teórico principal.
- O **artigo IJCAI 2026** (Das, Hanaka, Melissinos e Ono, *Charging Station Placement for Anonymous Mobile Agents: A Parameterized Complexity Perspective*, pp. 72–80) estuda o mesmo problema e é o trabalho prévio mais próximo: `G^r`, verificação por matching, reduções de Set Cover e Bin Packing, FPT, árvores e aproximação já estão publicados ali. A sobreposição com o projeto está em `docs/technical/reference/overlap-ijcai2026-min-station.md`.
- O **artigo da SBPO** registra uma etapa anterior da pesquisa (variante com estações só em `V ∖ (S ∪ T)` e métrica ponderada) e deve ser preservado como referência histórica/metodológica.
- A **formulação em todos os vértices** é o baseline atual.
- Novas formulações e técnicas podem substituir ou complementar o baseline em experimentos, desde que identificadas claramente.
- Resultados negativos também devem ser documentados quando ajudam a explicar a estrutura do problema.

## 8. Regras gerais ao trabalhar no repositório

- Não confundir problema, formulação e método de solução.
- Não alterar silenciosamente o problema ao tentar melhorar o desempenho.
- Cada formulação experimental deve ter nome/identificador claro.
- Comparações devem usar instâncias e parâmetros compatíveis.
- O código deve ser consultado antes de afirmar o que está implementado.
- Divergências entre código e documentação devem ser apontadas.
- Hipóteses abertas ficam em `docs/technical/governance/open-questions.md`.
- Propostas de fortalecimento ou reformulação permanecem como propostas até serem incorporadas formalmente.
