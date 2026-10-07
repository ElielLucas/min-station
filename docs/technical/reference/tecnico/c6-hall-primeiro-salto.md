# Proposição 5.4.2 — mochila de Hall de primeiro salto

**Data do texto:** 2026-10-03
**Estado:** derivação registrada antes de qualquer medição de desempenho do C6.
**Código:** `generate_C6` e `corte_ponderado_valido` em `experiments/cuts/cuts.py`. O gerador já existia quando este texto foi escrito; a medição ainda não.

Este enunciado é o item 2 de `direcoes-pli-min-station.md` §5.4, promovido a proposição numerada. O §5.6, que também usa o nome C6, continua marcado como esboço e não é esta desigualdade.

## Enunciado

Seja `S' ⊆ S\T` e

```text
δ = |S'| − |N⁺(S') ∩ T|.
```

`N⁺` e `N⁻` são as vizinhanças no dígrafo de alcance `A_r`: existe arco `u → v` quando a distância no grafo da instância é no máximo `r`. Se `δ ≥ 1`, toda solução viável da formulação base (variante U, `y` binário em todo `V`) satisfaz

```text
Σ_{v ∈ N⁺(S')} min(δ, |N⁻(v) ∩ S'|) y_v ≥ δ.
```

O gerador só emite o caso `δ ≥ 2`. Com `δ = 1` os coeficientes positivos valem 1 e a desigualdade coincide com o corte de RHS 1 do §5.4 item 1, já coberto por C4 na versão DM.

## Derivação

A formulação base atribui os robôs por uma bijeção entre `S` e `T` (`|S| = |T| = m`) e manda o fluxo pelo dígrafo de alcance. Um arco de `A_r` que chega a um vértice que não é o destino daquele robô exige estação nesse vértice, pelas restrições de ativação.

Fixe `S' ⊆ S\T`. Um robô que parte de `s ∈ S'` e termina em um único arco de `A_r` chega a um vizinho em `T`. Esses destinos estão em `N⁺(S') ∩ T`, e cada destino recebe no máximo um robô. Logo no máximo `|N⁺(S') ∩ T|` robôs de `S'` terminam em um salto. Pelo menos `δ` robôs de `S'` usam dois ou mais arcos de `A_r`.

O primeiro vértice depois da origem, numa dessas rotas, está em `N⁺(S')` e não é o destino. É interior, portanto estação. Os `δ` robôs se repartem entre essas primeiras estações. A estação `v` só pode ser a primeira parada de uma origem vizinha, então recebe no máximo `|N⁻(v) ∩ S'|` desses robôs, e no máximo `δ` no total. A soma

```text
Σ_v min(δ, |N⁻(v) ∩ S'|) y_v
```

é um limite superior para o número de robôs de `S'` que conseguem fazer o segundo salto. Se a solução é viável, esse número é pelo menos `δ`, e a desigualdade vale.

O teto `min(δ, ·)` não corta ponto binário viável que a versão sem teto preservaria. Se `y_v = 1` e a capacidade passa de `δ`, o termo já contribui `δ` e a desigualdade fecha sozinha. Se `y_v = 0`, os dois coeficientes concordam.

## Condições de validade

1. `S' ⊆ S\T`. Origem em `S∩T` pode ficar parada (Lema 5 de Das) e não entra no argumento de primeiro salto.
2. Vizinhanças no dígrafo de alcance, não na adjacência original quando `r > 1`. O “primeiro salto” é o primeiro arco de `A_r`.
3. `y` binário, estações permitidas em todo `V`, objetivo irrelevante para a validade.
4. `|S| = |T|` e atribuição bijetiva, como na formulação base.
5. Coeficientes não negativos. A desigualdade não fala de fluxo.

## O que não é esta proposição

- `is_valid_cut` decide `y(Z) ≥ 1` para um conjunto. Não recebe coeficiente nem RHS `δ ≥ 2`. Não serve para validar esta família.
- A separação exata com `δ ≥ 1` continua em aberto (§5.4 item 5). O piloto, quando usar C6, acrescenta as desigualdades de forma estática, por enumeração dentro de cada componente do grafo de origens que compartilham vizinho. Componente com mais de 16 origens contribui só com o conjunto inteiro. Isso não é separação exata.
- O §5.6 permanece esboço. Não há gerador para ele.

## Contraexemplos considerados

- Aplicar a desigualdade a `S'` que intersecta `T` contaria um robô que pode não sair. O gerador exclui `S∩T`.
- Trocar o teto por um coeficiente maior que a capacidade cortaria uma estação que de fato cobre aqueles vizinhos.
- Ler a desigualdade no grafo original com `r > 1` desloca o primeiro salto: o vértice a distância 1 pode não ser a primeira estação do dígrafo de alcance.

## Previsão registrada antes da medição

Nas bolsões HB com `ndir ≥ 1`, tome `S' = A`, o conjunto das `q` origens do bolsão. `N⁺(A) ∩ T` é o conjunto `C` dos destinos diretos, de tamanho `ndir`, porque os relés não são terminais e os destinos distantes não são vizinhos de `A`. Então `δ = q − ndir`, que é a deficiência da construção.

O destino direto compartilhado `c` tem `N⁻(c) ∩ A = A`, logo coeficiente `min(δ, q) = δ`. A atribuição `y_c = 1` e `y = 0` nos demais vértices de `N⁺(A)` satisfaz esta desigualdade sozinha. Ela força `y_c ≥ 1` e não força as outras estações.

A previsão para a família enumerada, por bolsão, é `LB ≈ 1` contra `OPT = 3`. Se o LB com C6 atingir o ótimo, a leitura de que o coeficiente `δ` no destino compartilhado deixa o gap aberto fica refutada, e a análise tem de ser refeita antes de qualquer conclusão sobre E11. Nenhuma medição desse LB foi executada antes deste parágrafo.

## Medição posterior ao registro

Script: `experiments/structural/verify_t14_c6.py`, depois do parágrafo acima.

Validade, antes do LB: no bolsão `q=4` as desigualdades geradas passam em `corte_ponderado_valido` e no mínimo da soma ponderada no modelo base. No bolsão `q=6, ndir=1, δ=5` a desigualdade de RHS 5 passa nos dois testes. No controle BP `[3,1]` os cortes gerados também passam: nenhum corta solução viável. `verify_t6_determinismo.py`, reexecutado depois da extensão da representação, manteve a ordem unitária (`f5eb8704eadb` e `7c501db6e7bc`).

| Bolsão | OPT enumerado | LP só C6 | LP com C1+C2+C4+C6 | Cortes C6 |
|---|---:|---:|---:|---:|
| q=4, ndir=2, p=1 | 2 | 1,167 | 1,500 | 1 |
| q=6, ndir=1, p=1 | 3 | 1,364 | 1,800 | 42 |
| q=6, ndir=1, p=2 | 3 | 1,273 | 1,600 | 17 |
| q=8, ndir=1, p=1 | 3 | 1,400 | 1,857 | 219 |

O LB fica entre 1 e 2. Não atinge o ótimo. A previsão `LB ≈ 1` por bolsão contra `OPT = 3` se confirma no que importa para E11: a família não fecha o gap. O valor fica um pouco acima de 1 porque outros subconjuntos, além de `S' = A`, entram na enumeração. A análise de coeficiente do §5.4 não fica refutada. Não há motivo, por este teste, para refazer a proposição antes de uma conclusão sobre E11.
