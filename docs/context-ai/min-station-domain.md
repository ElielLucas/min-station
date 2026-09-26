---
type: context-ai
file: min-station-domain
title: "MIN-STATION — Domínio e Semântica"
---

# MIN-STATION — Domínio e Semântica

## 1. Definição de referência

Considere:

- `G = (V,E)`: grafo simples, não direcionado e conexo;
- `S ⊆ V`: posições iniciais;
- `T ⊆ V`: destinos;
- `|S| = |T| = m`;
- `r > 0`: autonomia comum dos robôs.

Cada robô começa com bateria carregada. A cada recarga, sua autonomia é restaurada. O objetivo é escolher um conjunto mínimo de vértices `C ⊆ V` com estações, de forma que todos os destinos possam ser ocupados.

## 2. Robôs não rotulados

Os robôs são indistinguíveis para fins de alocação.

Isso significa que:

- não existe `s_i -> t_i` fixado na entrada em grafos gerais;
- qualquer origem pode ser conectada a qualquer destino, desde que a solução global seja válida;
- o modelo base não precisa manter a identidade de cada robô se uma representação agregada preservar a viabilidade.

Não confundir isso com o resultado específico para caminhos do artigo original, em que existe uma propriedade de solução ótima após ordenar origens e destinos.

## 3. Autonomia e recarga

No problema original, uma movimentação elementar corresponde à travessia de uma aresta. Um robô percorre no máximo `r` passos antes de precisar de nova recarga.

Para o modelo com dígrafo de alcance, um salto `u -> v` significa:

> existe no grafo original uma rota de `u` a `v` que o robô consegue percorrer com uma única carga.

Na versão estritamente fiel ao problema original, a distância usada para construir esse salto deve ser a distância em número de arestas.

Se a implementação utilizar pesos positivos de aresta, registrar explicitamente que se trata de uma extensão ponderada ou de uma convenção experimental.

## 4. Terminais

Um vértice é terminal quando pertence a `S ∪ T`.

### Origem sem estação

Uma origem já contém um robô com bateria cheia. Portanto, uma unidade de fluxo pode sair dela sem custo de instalação.

### Destino sem estação

Um destino pode receber o robô que encerra sua rota ali sem custo de instalação.

### Origem ou destino com estação

Como a formulação atual permite `y_v` para todo `v ∈ V`, uma origem ou destino pode também servir como ponto de recarga para outros deslocamentos.

Nesse caso, a estação deve ser contabilizada no objetivo.

## 5. Passagem por vértices

O problema base não proíbe que trajetos atravessem vértices que também sejam terminais.

O simples fato de um caminho físico passar por um vértice não significa que exista recarga nesse vértice. A recarga ocorre quando o vértice é utilizado como ponto de transição entre saltos do dígrafo de alcance e a formulação exige/ativa a estação correspondente.

## 6. Compartilhamento de estações

A mesma estação pode atender vários robôs. Não há, no problema base:

- limite de capacidade da estação;
- fila de recarga;
- duração de recarga;
- conflito por uso simultâneo.

Não adicionar essas restrições sem mudar explicitamente o problema estudado.

## 7. Dígrafo de alcance

Dada uma função de distância `d(u,v)`, define-se:

`A_r = {(u,v) ∈ V × V : u != v e d(u,v) <= r}`.

O dígrafo de alcance é `(V,A_r)`.

Cada arco representa um deslocamento realizável com uma carga.

A formulação decide onde uma sequência de saltos requer estações. Ela não precisa acompanhar o consumo de bateria aresta por aresta no grafo original.

## 8. O que não faz parte do baseline atual

Não incorporar por padrão:

- `c_v` como custo heterogêneo;
- `r_s` como autonomia individual;
- `e_{s,t}` como elegibilidade;
- variável de pareamento explícito `p_{s,t}`;
- fluxo binário por robô `x_{u,v,s}`.

Esses elementos pertencem à formulação generalizada do trabalho anterior e não ao baseline atual. Eles podem ser estudados em trabalhos específicos, mas não devem ser introduzidos automaticamente ao pesquisar técnicas para o MIN-STATION base.

## 9. `S ∩ T` — resolvido (rodada E5)

`S` e `T` não são necessariamente disjuntos: Das permite que um vértice seja origem de um robô e alvo de outro ao mesmo tempo (Lema 5 do artigo).

A formulação corrente usa um balanço unificado por vértice (ver `docs/context-ai/base-formulation.md` §6), que cobre esse caso sem exigir tratamento separado. Não reintroduzir balanços separados (origem/destino) sem justificativa — isso reproduziria o erro de modelagem documentado em `docs/technical/reference/validacao-formulacao-base.md` (P1).

Decisão registrada em `docs/technical/governance/open-questions.md` (Q1, fechada).
