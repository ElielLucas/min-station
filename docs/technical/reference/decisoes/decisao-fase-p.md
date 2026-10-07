# Decisão da fase P

**Data:** 2026-10-03
**Fonte:** `results/structural/piloto_fase_p.csv`, 108 linhas, 27 células. Critérios de `piloto-fase-p.md`, não reescritos.

Status 2 é ótimo. Status 16 é `WorkLimit`. O primeiro incumbente sai do callback de leitura.

## BP — DESCARTAR

O núcleo vale `2n+q` em todas as células (28, 42 e 56). No lado sim o ótimo provado é esse número, nas três escalas e nas duas sementes. No lado não o incumbente é `2n+q+1` e aparece em menos de 0,4 s. Onde a prova fecha (q = 4 nos dois métodos; q = 6 no COMP), o ótimo é `2n+q+1`. Em q = 8 a base, o COMP e o COMP+C6 param no `WorkLimit` com limite 56 e incumbente 57.

O critério de permanência pede lados duros opostos: limite superior no sim, limite inferior no não. No sim o incumbente também aparece em menos de 0,15 s, e a prova termina dentro do orçamento até em q = 8. O lado sim não é o lado duro de limite superior. Só o lado não é duro de limite inferior, e isso em q = 6 para a base e em q = 8 para a base e para o COMP.

O critério de descarte pede que os dois lados fechem depressa em q = 8. O lado não não fecha. Mesmo assim a família não avança: promover pelo gap do lado não trocaria o critério depois dos números. A construção reproduziu o núcleo e os valores; não há revisão de gerador.

Em q = 6 o COMP prova o lado não e a base não. Em q = 8 os dois param no mesmo gap. C6 não muda esse quadro.

## SC — PROMOVER

No GF2 a base tem trabalho 0,94, 69,8 e 298 nas escalas k = 5, 6 e 7. A prova sai em 3 s e em 37 s; em k = 7 não sai. O incumbente `UB = k` aparece em até 0,03 s nas três. O COMP prova k = 7 em 6 nós e 80 s, dentro do orçamento, com a raiz não fechada. O núcleo prova k = 7 em 1 nó. O descarte exigia k = 7 provado depressa com a raiz fechada pelos cortes do próprio solver. Seis nós não são a raiz.

Os três métodos se separam: a base para com limite 2, o COMP prova 7, o núcleo prova 7 na raiz do modelo de y. O fenômeno está em mais de uma escala.

O gêmeo difere: em k = 7 o COMP do GF2 prova e o COMP do gêmeo para com limite 3 e incumbente 4. Isso não explica o gap da base do GF2 por simetria. O gêmeo é o menos simétrico na individualização do 1-WL, e é o que o COMP não prova. A fase E leva o gêmeo como par, sem ler essa diferença como efeito do grupo linear.

COMP+C6 em k = 7 não prova (limite 5, incumbente 7). C6 não é o mecanismo que fecha o GF2.

## HB — DESCARTAR

Nas seis células os quatro métodos provam o ótimo previsto. Em k = 8, p = 1, o valor é 24; o núcleo é 8. Em p = 6 o valor e o núcleo são 8. Tudo em menos de 1 s, num nó, sem diferença de limite entre métodos. O descarte geral se aplica: no maior tamanho todo método prova depressa e o limite não separa ninguém.

O C6 não fecha o gap de LP medido antes do piloto, e o MIP também não precisa dele. A análise de coeficiente não fica refutada. Não há família de segunda camada fechando um gap que o modelo tenha deixado aberto.

## TR

Não entrou no piloto. A validação do Apêndice B permanece. Não há fase E.

## Fase E

Só SC avança. BP, HB e TR não entram. Sementes de avaliação 100 a 104, disjuntas de 0 e 1. Orçamento, métodos e métricas continuam os do piloto.
