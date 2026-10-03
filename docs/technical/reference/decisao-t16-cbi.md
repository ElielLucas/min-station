# Decisão de aplicabilidade — T16

**Data:** 2026-10-03
**Estado:** registrada antes de qualquer execução do piloto da fase P.

## Decisão

T16 fica **não aplicável / encerrada**. O braço M4 (CBI) não entra no piloto. A família TR para na validação do gerador e do Apêndice B e não avança para o benchmark.

## Por quê

E12 encerrou A2 para o problema de Das no benchmark real. O resultado está em `direcoes-pli-min-station.md` §13 e em `plano-pos-e8-adiado.md`. T16 não repete esse experimento e não reabre A2. Não há corrida em PUC nem em PUCN.

As famílias novas levantam perguntas de limite e de simetria: o lado “sim” e o lado “não” de BP, o gap de primeiro salto em HB, a simetria de SC contra o gêmeo. Essas perguntas se leem em COMP, na base sem cortes e no núcleo inteiro. Não pedem a iteração do CBI.

A pergunta de iteração — se os cortes `𝒵` eliminam classes de ótimos inviáveis do núcleo, ou se o número de iterações acompanha `k^R` — é a pergunta para a qual TR foi desenhada. O parecer, depois de E12, tira de TR o método que ela servia para discriminar. Rodar a bateria de três braços porque a tarefa está no backlog repetiria esse desenho sem uma hipótese nova adotada neste bloco.

O critério de promoção de BP que cita explosão de iterações do CBI no gêmeo “não” fica inativo. A promoção de BP, se houver, usa só o contraste dos dois lados no compacto e no núcleo.

## O que foi validado mesmo assim

`verify_t17_tr.py` conferiu a fórmula `OPT = ceil(D/r) − 1` e a contagem do Apêndice B: `TR(k=2,L=5,r=2,σ=∞)` tem 8 ótimos de núcleo, 2 viáveis; `TR(k=3,L=5,r=2,σ=∞)` tem 27 ótimos, 3 viáveis. A variante com degrau `σ = r` gera outro arquivo. Isso encerra a validação. Não há avanço para a fase P.

## Consequência no piloto

A matriz pré-registrada tinha 33 células, 6 delas de TR. Sem TR ficam 27: BP 12, SC 9, HB 6. Essa redução está anotada antes de qualquer solve do piloto.
