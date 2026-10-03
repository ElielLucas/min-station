# Desagregação por origem, estações em todo V

**Data do texto:** 2026-10-03
**Estado:** formulação escrita antes da medição.
**Código:** `experiments/alternative-formulations/desagregacao.py`. Não altera `baseline.py`.

`modelo_estendido.py` restringe `y` aos vértices intermediários e zera a saída de destino. Não é esta formulação e não é equivalente à base.

## Problema

O mesmo MIN-STATION da formulação base: grafo com autonomia `r` em saltos, `|S| = |T| = m`, estações em qualquer vértice de `V`, objetivo `Σ_v y_v`. O fluxo anda no dígrafo de alcance `A_r`.

## Variáveis

- `y_v ∈ {0,1}` para cada `v ∈ V`.
- `p_{s,t} ∈ {0,1}` para `s ∈ S`, `t ∈ T`. `p_{s,s}` só existe de fato quando `s ∈ S∩T`; para `s ∉ T` o índice não é um destino.
- `f^s_{uv} ∈ {0,1}` para cada origem `s ∈ S` e cada arco `(u,v) ∈ A_r`.

Contagem: `|V|` variáveis de estação, `m²` de atribuição, `m |A_r|` de fluxo. Restrições de balanço e de ativação: `Θ(m |V|)`, mais `2m` de atribuição.

## Restrições

Atribuição bijetiva:

```text
Σ_{t ∈ T} p_{s,t} = 1    para cada s ∈ S
Σ_{s ∈ S} p_{s,t} = 1    para cada t ∈ T
```

Balanço da commodity `s`, em cada `v ∈ V`:

```text
out^s(v) − in^s(v) = [v = s] − [v ∈ T] p_{s,v}
```

`[v = s]` vale 1 só na origem da commodity. Se `s ∈ S∩T` e `p_{s,s} = 1`, o balanço em `s` é zero e o robô fica parado, sem arco, como no Lema 5. Outra commodity pode ter `s` como destino: o balanço dela em `s` exige uma unidade de entrada.

Ativação, por commodity:

```text
in^s(v)  ≤ y_v                 se v ∉ T
in^s(v)  ≤ p_{s,v} + y_v       se v ∈ T
out^s(v) ≤ y_v                 se v ≠ s
out^s(s) ≤ 1
```

A origem sai sem precisar ser estação. O destino da própria commodity recebe a unidade final sem estação. Qualquer passagem ou entrada que não seja esse destino exige `y_v = 1`. Circulação de uma commodity continua possível, como no fluxo agregado; uma circulação só pode exigir estação extra, então não cria ótimo inteiro abaixo do problema.

## Relação com a base

Somar `f^s` sobre `s` produz um fluxo agregado que obedece o balanço unificado da variante U. A ativação por commodity implica a ativação agregada, porque a entrada total é a soma das entradas e cada uma já está limitada por `y`. A recíproca não vale no LP: o agregado pode misturar commodities no mesmo `y` fracionário. Por isso `z_LP` desagregado é pelo menos o `z_LP` da base. Nos inteiros as duas descrições pedem uma bijeção e rotas com estações nos interiores, então os ótimos coincidem quando as duas estão corretas. O teste de fidelidade é essa igualdade, mais a enumeração independente nas instâncias pequenas.

A comparação abaixo não autoriza tratar o modelo como candidato de produção. O custo `O(m |A_r|)` é o motivo de mantê-lo em instâncias pequenas.

## Medição

Feita depois do texto acima. Fidelidade em `verify_t18_desagregacao.py`: Tri, CaminhoABC e StayPutIsolado têm o mesmo OPT na desagregação, na base e na enumeração independente. No Tri a base tem `z_LP = 1` e a desagregação `1,5`, com OPT `2`.

| Instância | z_LP base | z_LP desagregado | OPT | variáveis |
|---|---:|---:|---:|---|
| Tri | 1,000 | 1,500 | 2 | 33 → 90 |
| HB q=4 | 0,333 | 1,375 | 2 | 64 → 340 |
| BP [3,1] | 3,000 | 5,000 | 7 | 48 → 160 |
| SC-GF2(3) | 1,000 | 1,750 | 3 | 175 → 1148 |

O ganho existe e não fecha o ótimo. Em SC-GF2(3) o `z_LP` desagregado iguala o LP com C1 (`1,75`), corte estático que não multiplica as variáveis por `m`. Em BP `[3,1]` o núcleo com C1+C2+C4 já vale 6, acima dos 5 da desagregação. O aumento de variáveis acompanha `m |A_r|`.

Decisão: o ganho de relaxação não justifica o custo. Não há expansão planejada, nem geração de colunas em cima deste modelo. A força do LP na raiz não é evidência de que a formulação seja computacionalmente melhor.
