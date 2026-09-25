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

## 6. Restrições correntes

As equações abaixo correspondem à versão atual da formulação quando origens e destinos são tratados por conjuntos separados.

### 6.1 Balanço nas origens

Para todo `s ∈ S`:

`Σ_{v:(s,v)∈A_r} f_{s,v} - Σ_{u:(u,s)∈A_r} f_{u,s} = 1`.

Interpretação: a origem produz uma unidade líquida de fluxo.

### 6.2 Balanço nos destinos

Para todo `t ∈ T`:

`Σ_{u:(u,t)∈A_r} f_{u,t} - Σ_{w:(t,w)∈A_r} f_{t,w} = 1`.

Interpretação: o destino consome uma unidade líquida de fluxo.

### 6.3 Conservação nos demais vértices

Para todo `v ∈ V \ (S ∪ T)`:

`Σ_{u:(u,v)∈A_r} f_{u,v} = Σ_{w:(v,w)∈A_r} f_{v,w}`.

## 7. Ativação por instalação

O objetivo destas restrições é distinguir:

- a unidade que naturalmente nasce em uma origem;
- a unidade que naturalmente termina em um destino;
- fluxo adicional que usa um terminal como ponto de recarga/passagem.

Use `m = |S|`.

### 7.1 Entrada em vértices que não são destinos

Para todo `v ∈ V \ T`:

`Σ_{u:(u,v)∈A_r} f_{u,v} <= m y_v`.

Sem estação, um vértice que não é destino não pode receber fluxo.

### 7.2 Entrada em destinos

Para todo `t ∈ T`:

`Σ_{u:(u,t)∈A_r} f_{u,t} <= 1 + (m-1)y_t`.

Se `y_t = 0`, o destino pode receber somente a unidade que termina nele.

Se `y_t = 1`, o destino pode receber fluxo adicional e funcionar como ponto de recarga.

### 7.3 Saída de vértices que não são origens

Para todo `v ∈ V \ S`:

`Σ_{w:(v,w)∈A_r} f_{v,w} <= m y_v`.

Sem estação, um vértice que não é origem não pode emitir fluxo.

### 7.4 Saída das origens

Para todo `s ∈ S`:

`Σ_{w:(s,w)∈A_r} f_{s,w} <= 1 + (m-1)y_s`.

Se `y_s = 0`, a origem pode emitir somente a unidade do robô que começa ali.

Se `y_s = 1`, a origem também pode encaminhar fluxo adicional após recarga.

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

### 10.1 Interseção `S ∩ T`

As restrições 6.1 e 6.2 entram em conflito se um mesmo vértice pertencer simultaneamente a `S` e `T`.

O problema original não deve ser tratado como se `S` e `T` fossem necessariamente disjuntos sem uma decisão formal.

Uma possível reformulação unificada, ainda **não adotada automaticamente**, é usar os indicadores:

- `a_v = 1` se `v ∈ S`, 0 caso contrário;
- `b_v = 1` se `v ∈ T`, 0 caso contrário.

Balanço candidato:

`out(v) - in(v) = a_v - b_v`.

Ativações candidatas:

`in(v) <= b_v + (m-b_v)y_v`

`out(v) <= a_v + (m-a_v)y_v`.

Essa alternativa deve ser analisada e aprovada antes de substituir a formulação corrente.

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
- [ ] o caso `S ∩ T` foi preservado, resolvido ou explicitamente assumido fora do escopo;
- [ ] a equivalência entre fluxo e rotas permanece válida;
- [ ] testes pequenos foram atualizados.
