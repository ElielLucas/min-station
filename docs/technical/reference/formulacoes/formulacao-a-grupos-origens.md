# Formulação A — Fluxos por grupos de origens

**Estado:** proposta matemática documentada, ainda não homologada por verificador independente.  
**Spec:** `specs/as-01-formalizacao-matematica-a/`  
**Fonte:** `docs/technical/reference/pareceres-astra/2026-10-11-02-parecer-fluxos-por-grupos.md`.  
**Implementação computacional:** não realizada; reservada à AS-02.

## 1. Problema original

Seja `G=(V,E)` um grafo simples, não direcionado e conexo. `r>=1` é a autonomia (número de arestas), e `H=(V,A_r)` é seu **dígrafo de alcance**, contendo `(u,v)` se `u≠v` e `dist_G(u,v)≤r`. Uma trajetória em `H` representa saltos entre pontos de partida, recarga e chegada; somente os **vértices internos** de cada trajetória precisam de estação. O caminho trivial `s=t` é permitido. As estações podem ocupar quaisquer vértices, inclusive origens e destinos, sem limite de capacidade de atendimento.

`S,T⊆V` são conjuntos de **vértices distintos dentro de cada conjunto**, com `|S|=|T|=m≥1`. A atribuição origem→destino é uma **bijeção livre**, inclusive com `S∩T ≠ ∅`. Cada origem fornece exatamente um robô; cada destino recebe exatamente um robô. A decisão é `y_v∈{0,1}`, e o objetivo é minimizar `Σ_v y_v`. Caminhos físicos podem ser reduzidos a caminhos simples em `H` sem criar nova estação.

Esta definição **não** corresponde à variante histórica de estações apenas em intermediários (VI).

## 2. Base U e cortes K

Defina `a_v=1[v∈S]` e `b_v=1[v∈T]`, e `F≥0` nos arcos de `A_r`. A formulação U do `baseline.py` impõe, para todo `v`:

\[
\operatorname{out}_F(v)-\operatorname{in}_F(v)=a_v-b_v,
\quad \operatorname{in}_F(v)\le b_v+(m-b_v)y_v,
\quad \operatorname{out}_F(v)\le a_v+(m-a_v)y_v.
\]

Para comparações `+K`, `K` significa exatamente as famílias válidas `C1+C2+C4-DM` obtidas para a **mesma instância**, com desigualdades `Σ_{v∈Z} y_v ≥ 1`; os conjuntos `Z` e as regras de geração devem ser fixados e auditados. **U sem K** e **U+K (COMP+K)** são braços diferentes. `y` relaxado no LP significa `0≤y≤1`; `F` permanece contínuo. O código da base usa fluxo inteiro no MIP, mas a projeção relevante para esta documentação considera fluxos contínuos e `y` binário.

## 3. Partição e constantes

Fixe uma partição `𝓑={B₁,…,Bₖ}` de `S`, com blocos disjuntos não vazios e união `S`.

\[
 c_{Bv}=|B|-\mathbf1_{\{v\in B\}},\qquad
 \kappa_v=\begin{cases}m-1,&v\in S\cup T,\\m,&v\notin S\cup T.\end{cases}
\]

São **limites combinatórios do número de caminhos simples que usam `v` como vértice interno**, não capacidades físicas de estações. A4 e A5 compartilham o mesmo `y_v`.

## 4. Variáveis

| Símbolo | Índices | Domínio | Interpretação |
|---|---|---|---|
| `y_v` | `v∈V` | `{0,1}` | Estação instalada |
| `f^B_{uv}` | `B∈𝓑, (u,v)∈A_r` | `≥0`, contínuo | Salto de fluxo do grupo |
| `g^B_v` | `B∈𝓑, v∈V` | `≥0`, contínuo | Trânsito que precisa de estação |
| `p_{Bt}` | `B∈𝓑, t∈T` | `[0,1]`, contínuo | Chegada final ao destino pelo grupo |
| `h^B_v` | `B∈𝓑, v∈B∩T` | `[0,1]`, contínuo | Permanência sem deslocamento |

Adote `p_{Bv}=0` para `v∉T` e `h^B_v=0` para `v∉B∩T`. Esses valores fora de domínio são **constantes convencionais**, não variáveis adicionais. Não se impõe uma atribuição fixa dos destinos aos blocos.

## 5. Modelo completo — A1 a A7

Para cada `B∈𝓑` e `v∈V`:

\[
\boxed{\sum_{u:(u,v)\in A_r}f^B_{uv}+h^B_v=p_{Bv}+g^B_v}\tag{A1}
\]
\[
\boxed{\sum_{w:(v,w)\in A_r}f^B_{vw}+h^B_v=\mathbf1_{\{v\in B\}}+g^B_v}\tag{A2}
\]

Atendimento global, para cada `t∈T`:

\[
\boxed{\sum_{B\in\mathcal B}p_{Bt}=1}\tag{A3}
\]

Ativação por grupo e acoplamento global:

\[
\boxed{g^B_v\le c_{Bv}y_v}\qquad(B\in\mathcal B,v\in V)\tag{A4}
\]
\[
\boxed{\sum_{B\in\mathcal B}g^B_v\le\kappa_v y_v}\qquad(v\in V)\tag{A5}
\]

Cortes comuns quando se escolhe o braço `+K`:

\[
\boxed{\sum_{v\in Z}y_v\ge1}\qquad (Z\in K).\tag{A6}
\]

Objetivo:

\[
\boxed{\min\sum_{v\in V}y_v}.\tag{A7}
\]

Sem K, remova **somente** A6. Todas as demais variáveis e restrições permanecem. Somando A1 e A2 ao longo de `V`, verifica-se que `Σ_t p_{Bt}=|B|` para cada grupo: não é necessária uma restrição extra de cardinalidade.

## 6. Semântica dos casos especiais

- **Permanência:** se `v∈B∩T`, `h^B_v` absorve a origem em seu próprio destino; para uma solução física integral de caminhos, `h=1` e nenhuma aresta é usada nesse robô.
- **Troca de ocupantes:** mesmo quando `v∈S∩T`, fluxos de outros grupos podem chegar ao destino `v` e a origem `v` pode partir; não reduzir `S∩T` por cancelamento prévio.
- **Destino intermediário:** passar por um destino e continuar exige `g^B_v>0` e estação `y_v=1` no MIP; apenas **terminar** no destino é gratuito.
- **Origem intermediária:** a partida de `v` é gratuita apenas ao robô cujo bloco contém `v`; os demais atravessamentos requerem estação.
- **Ciclos de fluxo:** podem existir em soluções contínuas; na construção de caminhos são elimináveis sem aumentar `y` ou violar capacidades. Não confundir um ciclo fracionário com uma solução física distinta.
- **m=1:** para terminais `κ_v=0`; esse limite não proíbe início e chegada gratuitos.

## 7. Limitações e rastreabilidade

As provas e as qualificações de força LP estão em [provas-formulacao-a.md](provas-formulacao-a.md) e [relacoes-lp-formulacao-a.md](relacoes-lp-formulacao-a.md). A formulação é uma **proposta matemática**, não um resultado de desempenho computacional. O gate de revisão independente da AS-01 é obrigatório antes da implementação da AS-02.
