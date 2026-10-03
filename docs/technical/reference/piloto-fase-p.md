# Piloto da fase P — registro congelado

**Data:** 2026-10-03
**Estado:** congelado antes do primeiro `optimize` de célula. Os parâmetros abaixo não mudam depois que os resultados aparecerem.

## Matriz

A matriz do parecer tinha 33 células. T16 ficou não aplicável (`decisao-t16-cbi.md`), então as 6 células de TR saem. O piloto tem 27 células. Nenhuma foi removida por pré-condição: o dry-run de `experiments/structural/piloto.py --dry-run` montou as 27, com hash estável, e a coluna `excluir` ficou vazia. O arquivo é `results/structural/piloto_dryrun.csv`.

| Família | Células | Instâncias |
|---|---|---|
| BP | `q ∈ {4,6,8}`, `n = 3q`, `B = 60`, lados sim e não, sementes de geração 0 e 1 | 12 |
| SC | `k ∈ {5,6,7}` × {GF2, gêmeo semente 0, gêmeo semente 1} | 9 |
| HB | `k ∈ {1,4,8}` × `(q, ndir, p) ∈ {(6,1,1), (6,1,6)}` | 6 |

Sementes de geração de avaliação, reservadas e não usadas neste piloto: 100, 101, 102, 103, 104. A interseção com {0, 1} é vazia. Os dois lados de um par BP compartilham `instancia_original` e a semente, então não se separam.

O gêmeo de SC passou na individualização do 1-WL e tem ótimo de set cover provado, inclusive em `k = 7`. HB com `k > 1` entrou com o certificado do modelo base registrado em `familias-estruturais.md` e com a solução explícita conferida por `viavel`.

## Métodos

| Método | Onde |
|---|---|
| M1 COMP, base U com C1+C2+C4 | todas |
| M2 base sem cortes | todas |
| M3 núcleo inteiro C1+C2+C4 | todas |
| M4 CBI | não roda |
| M5 COMP+C6 | HB, e BP e SC como controle |

Uma semente de solver, 42. Quatro threads. Sem MIP start. Duas fatias, gravadas na coluna `fatia`, resolvidas em sequência no mesmo processo: uma otimização por vez.

## Orçamento

Calibração, que não é resultado de célula: `bp-q8-nao-s0`, formulação base, sem cortes, `Threads = 1`, `TimeLimit = 20`, parâmetros padrão do solver. Status 9, `Work = 9,9374`, parede 20,094 s, taxa 0,4945 unidades de trabalho por segundo de parede. A instância não fechou nesses 20 s.

`WorkLimit = 600 × 9,9374 / 20,094 = 297`. É o trabalho de cerca de 600 s numa thread nesta máquina, neste modelo. `TimeLimit = 1800` s fica só como guarda de parede. Se a guarda disparar antes do trabalho, o status 9 entra na tabela com essa ressalva.

## Métricas

As de `schema-instrumentacao-mip.md`: status, objetivo, limite, gap, `NodeCount`, `Work`, tempo de modelo, tempo de MIP, tempo até o primeiro incumbente, tempo até o melhor, tempo até a prova quando o status é ótimo, número de cortes adicionados. Callback de incumbente só de leitura, ligado neste runner. Não há braço CBI, então não há coluna de iteração.

## Critérios de promoção

Copiados do parecer, §11.6, e fixados aqui. Não serão reescritos depois dos números.

Uma família vai à fase E só se as três condições valem: toda propriedade prevista reproduz em toda célula; o fenômeno aparece em pelo menos 2 dos 3 tamanhos e, quando o veredito depender de 1 ou 2 unidades, repete em 3 sementes de solver; a família separa pelo menos dois métodos ou duas famílias de corte.

Descarte geral: todo método prova o ótimo depressa no maior tamanho, sem diferença de limite; ou o tempo cresce só com o tamanho, sem diferença de gap ou de nós.

| Família | Fica se | Sai se |
|---|---|---|
| BP | os gêmeos mostram lados duros opostos (limite superior no “sim”, inferior no “não”) | os dois lados fecham depressa em `q = 8` |
| SC | nós e tempo de prova crescem com `k` e `UB = k` aparece cedo, ou o gêmeo difere com clareza | `k = 7` é provado depressa com a raiz fechada pelos cortes do próprio solver |
| HB | o LB com C6 fica em cerca de 1 por bolsão e alguma família de segunda camada fecha o gap; pode ficar como instrumento de limite mesmo sendo rápida | C6 fecha o gap |

O critério de BP que citava iterações do CBI não se aplica: M4 não roda. O de TR não se aplica: TR não entrou. Uma propriedade provada que falhe manda investigar implementação ou prova antes de ler o número como fenômeno computacional. Cada família recebe exatamente uma decisão: promover, descartar, ou rever teoria ou gerador.
