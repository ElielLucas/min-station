---
type: context-ai
file: base-formulation
title: "MIN-STATION — Formulação Base Atual"
---

# MIN-STATION — Formulação Base Atual

## 1. Status deste documento

Este arquivo descreve a **formulação base corrente**, usada como baseline matemático e experimental da pesquisa.

A principal mudança em relação à formulação base publicada no artigo da SBPO é permitir estações em **todos os vértices**. Essa alteração foi introduzida para aproximar esse baseline da definição original de Das, mas **não representa o objetivo final da pesquisa**.

O projeto pode investigar outras formulações e técnicas de otimização. Quando isso ocorrer, elas devem ser identificadas separadamente e comparadas com este baseline.

A formulação generalizada do artigo da SBPO não faz parte deste documento.

## 2. Entrada

Considere:

- `G = (V,E)`: grafo simples, não direcionado e conexo;
- `S ⊆ V`: origens;
- `T ⊆ V`: destinos;
- `|S| = |T| = m`;
- `r`: autonomia comum;
- `d(u,v)`: distância usada para determinar se um deslocamento cabe em uma carga.

Para aderência estrita ao MIN-STATION original, `d(u,v)` deve representar distância em número de arestas. Uso de comprimentos ponderados deve ser identificado como extensão.

## 3. Dígrafo de alcance

Defina:

`A_r = {(u,v) ∈ V × V : u != v, d(u,v) <= r}`.

Cada arco `(u,v) ∈ A_r` representa um salto que pode ser realizado com uma única carga.

## 4. Variáveis

### Instalação

`y_v ∈ {0,1}` para todo `v ∈ V`.

- `y_v = 1`: existe estação em `v`;
- `y_v = 0`: não existe estação em `v`.

**Importante:** `y_v` é definido para todo `V`, e não apenas para `V \ (S ∪ T)`.

### Fluxo agregado

`f_{u,v} ∈ Z_{>=0}` para todo `(u,v) ∈ A_r`.

`f_{u,v}` representa a quantidade de robôs que utiliza o salto `u -> v`.

## 5. Função objetivo

Minimizar o número total de estações:

`min Σ_{v∈V} y_v`.

## 6. Restrições correntes (balanço unificado — variante U)

Das não exige `S` e `T` disjuntos (Q1, fechada na rodada E5): a definição do
problema permite que um vértice seja origem de um robô e alvo de outro ao
mesmo tempo, e a prova do Lema 5 do artigo depende disso. As equações
abaixo usam por isso um balanço único por vértice, com indicadores
`a_v = 1` se `v ∈ S` (senão 0) e `b_v = 1` se `v ∈ T` (senão 0):

### 6.1 Balanço unificado

Para todo `v ∈ V`:

`Σ_{v:(v,w)∈A_r} f_{v,w} - Σ_{u:(u,v)∈A_r} f_{u,v} = a_v - b_v`.

Interpretação: `v ∈ S∖T` produz uma unidade líquida (equivale à antiga
restrição 6.1 de balanço nas origens); `v ∈ T∖S` consome uma unidade líquida
(equivale à antiga 6.2); `v ∉ S∪T` conserva fluxo (antiga 6.3); e
`v ∈ S ∩ T` também conserva fluxo (`in(v) = out(v)`), permitindo que o robô
que parte de `v` simplesmente fique parado ocupando o próprio alvo, sem
exigir caminho nem estação (Lema 5 de Das).

Quando `S ∩ T = ∅`, esta forma coincide exatamente com as três restrições
separadas usadas antes desta rodada.

## 7. Ativação por instalação

O objetivo destas restrições é distinguir:

- a unidade que naturalmente nasce em uma origem;
- a unidade que naturalmente termina em um destino;
- fluxo adicional que usa um terminal como ponto de recarga/passagem.

Use `m = |S|`.

### 7.1 Entrada

Para todo `v ∈ V`:

`Σ_{u:(u,v)∈A_r} f_{u,v} <= b_v + (m - b_v) y_v`.

Se `v ∉ T` (`b_v=0`): sem estação, `v` não pode receber fluxo algum
(equivale à antiga 7.1). Se `v ∈ T` (`b_v=1`) e `y_v = 0`: `v` pode
receber somente a unidade que termina nele (antiga 7.2).

### 7.2 Saída

Para todo `v ∈ V`:

`Σ_{w:(v,w)∈A_r} f_{v,w} <= a_v + (m - a_v) y_v`.

Se `v ∉ S` (`a_v=0`): sem estação, `v` não pode emitir fluxo algum
(equivale à antiga 7.3). Se `v ∈ S` (`a_v=1`) e `y_v = 0`: `v` pode emitir
somente a unidade do robô que começa ali (antiga 7.4).

Para `v ∈ S ∩ T`, as duas restrições ficam `in(v) <= 1 + (m-1)y_v` e
`out(v) <= 1 + (m-1)y_v`: cada lado tem sua própria unidade livre, e
qualquer fluxo além disso (trânsito de outro robô) exige `y_v = 1`.

## 8. Semântica das estações em terminais

### Origem

Uma estação em uma origem não é necessária para o robô que já começa ali com carga completa.

Ela só deve ser cobrada se a origem precisar funcionar como estação para fluxo adicional.

### Destino

Uma estação em um destino não é necessária para o robô que encerra sua rota ali.

Ela só deve ser cobrada se o destino precisar funcionar como estação para fluxo adicional.

Essa é a razão das constantes `1` presentes nas restrições de entrada em destinos e saída das origens.

## 9. Interpretação da solução

Uma solução inteira fornece:

- `C = {v ∈ V : y_v = 1}`;
- um fluxo agregado inteiro no dígrafo de alcance.

Para estabelecer equivalência formal com rotas de robôs, deve-se justificar que o fluxo pode ser decomposto em `m` caminhos origem-destino válidos, removendo ciclos de fluxo que não sejam necessários.

Esse ponto deve aparecer na demonstração de correção da formulação, não apenas ser assumido pela implementação.

## 10. Pontos ainda não fechados

### 10.1 Interseção `S ∩ T` — RESOLVIDO (rodada E5)

Adotado o balanço unificado (variante U) descrito em §6 e §7. Não é mais
uma alternativa candidata: é a formulação corrente, implementada em
`baseline.py`. Verificado que coincide exatamente com a formulação anterior
quando `S ∩ T = ∅`. No manifesto atual, `S ∩ T ≠ ∅` ocorre em 5 instâncias
`classe = principal`: `mapf-den312d-m50-f2-rho`, `mapf-room-32-32-4-m25-f4-rho`,
`puc-w23c23-intercalado-f2-rho`, `b-b09-intercalado-f2-rho` e
`i-i160-301-intercalado-f2-rho` (`rho_S_inter_T > 0`). A frase anterior desta
seção falava em todas as 22 instâncias do repositório.

### 10.2 Distância ponderada vs. passos

A definição original utiliza passos. Se `d(u,v)` for calculada com pesos arbitrários, o projeto está resolvendo uma extensão ponderada.

### 10.3 Big-M

O limitante `m = |S|` é seguro como limite de fluxo agregado, mas pode enfraquecer a relaxação linear.

Esse ponto é um dos possíveis alvos de pesquisa. Fortalecimentos, cortes, reformulações ou outras estratégias devem ser avaliados comparativamente e não podem alterar a semântica do problema sem que isso seja explicitado.

### 10.4 Reconstrução das rotas físicas

Um arco do dígrafo de alcance representa existência de um caminho no grafo original. Se o software precisar exibir a rota física, o pré-processamento deve preservar informação suficiente para reconstruir um caminho correspondente.

## 11. Checklist para qualquer alteração

Antes de aceitar uma mudança na formulação, verificar:

- [ ] continua permitindo estação em todo `V`;
- [ ] origem pode iniciar sem estação;
- [ ] destino pode terminar sem estação;
- [ ] fluxo adicional em terminal exige estação;
- [ ] toda transição respeita `r`;
- [ ] não foi introduzida identidade de robô desnecessariamente;
- [ ] não foi reintroduzida a formulação generalizada;
- [x] o caso `S ∩ T` é tratado pelo balanço unificado (§6, §10.1) — não reintroduzir balanços separados sem justificativa;
- [ ] a equivalência entre fluxo e rotas permanece válida;
- [ ] testes pequenos foram atualizados.
