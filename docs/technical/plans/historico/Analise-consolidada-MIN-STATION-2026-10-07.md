# Análise consolidada do MIN-STATION e próximos passos

**Data:** 7 de outubro de 2026.  
**Branch examinada:** `novos_testes`.  
**Versão de referência:** [`b3c7337e12196c9b8ddf3150fdf31561fc507e91`](https://github.com/ElielLucas/min-station/commit/b3c7337e12196c9b8ddf3150fdf31561fc507e91), conferida novamente ao concluir a leitura.  
**Escopo:** análise científica e estratégica. Nenhum código do projeto, spec ou pré-registro foi alterado. Nenhum modelo de otimização nem nova bateria experimental foi executado. As contagens e a cobertura dos cortes de R7 abaixo foram recalculadas exclusivamente a partir dos CSVs existentes.

## 1. Resumo executivo

**A direção mais sustentada é estudar limites de compatibilidade que capturem o ganho da F-CC com custo controlado.** O projeto tem uma base matemática substancialmente mais confiável, um referencial experimental oficial e evidência concreta de que cobertura, isoladamente, não resolve todas as instâncias. Ainda não tem um método novo demonstrado competitivo nas instâncias difíceis do benchmark.

Três resultados mudam o planejamento:

1. **GF1 passou pela F-CC, sem F-C3.** Em HB e no pequeno BP negativo, seu LP atinge o ótimo; em Sec59 melhora o limite, mas deixa gap importante. Isso justifica investigar a formulação, sem demonstrar velocidade ou escalabilidade. A enumeração já excede o limite de 200 mil conjuntos conectados em SC-GF2 com 21 vértices. [E09–E12]
2. **G1 favorece pesquisar limites de compatibilidade, mas não identifica completamente o mecanismo causal.** Há $Γ$ positivo certificado em oito famílias e nenhuma melhora primal reproduzida pelo teste de `MIPFocus=1`. Entretanto, o teste de H-desc em R7 confirma uma caracterização de viabilidade; não distingue sozinho quais restrições de compatibilidade seriam eficazes. Há também um erro de mensuração da cobertura dos cortes, detalhado na seção 10. [E13–E17]
3. **R11 terminou com `CONFIRMED DIVERGENCE`.** Os procedimentos literais de caminhos/ciclos e as leituras de spiders testadas não podem ocupar o papel de certificadores exatos universais previsto no plano. Isso exige substituir uma dependência de validação, e abre uma oportunidade de revisão teórica delimitada. Não exige abandonar a formulação base nem reiniciar GF1/G1. [E18–E22]

A pergunta científica principal deve ser:

> **Que informação de compatibilidade coletiva, ausente ou mal representada nos limites atuais, permite obter um limite certificado melhor que o melhor referencial disponível, sem transferir toda a dificuldade para a enumeração ou para o pricing?**

A menor sequência útil é: **(i)** fechar a comparação matemática e discriminar a contribuição de F-CC, cortes existentes e trios em casos pequenos; **(ii)** testar uma única via econômica de obter esse limite, inicialmente na raiz, com certificação; **(iii)** só então avaliar desempenho em desenvolvimento e, se houver ganho reproduzível, confirmar em avaliação. F-C3 participa do primeiro passo com esforço limitado; não deve bloquear a investigação de F-CC.

O projeto está tecnicamente bem orientado quando separa corretude, força do limite e desempenho. O principal risco agora é transformar gates exploratórios positivos em autorização para uma implementação grande antes de esclarecer essas três dimensões.

## 2. Estado atual do projeto

### Problema e formulação de referência

O alvo permanece o MIN-STATION de Das: grafo simples, conexo e não dirigido; autonomia comum em número de arestas; estações em qualquer vértice; robôs anônimos; $\vert S\vert =\vert T\vert $; interseção permitida; permanência permitida; matching final livre. Não há capacidades de atendimento, colisões ou horários. As extensões ponderadas/dirigidas do histórico não sustentam, sozinhas, conclusões sobre esse problema. [E01–E03, E26]

A baseline U usa $y_v$ em todo $V$, fluxo agregado no dígrafo de alcance e balanço $out(v)-in(v)=a_v-b_v$. As ativações distinguem a unidade inicial/final gratuita do trânsito que exige estação. A prova da seção 5.5 da validação cobre sobreposição, permanência e fluxo contínuo quando $y$ é binário. Portanto, **a agregação de fluxo é uma formulação inteira exata; a fraqueza está na relaxação e no processamento computacional, não na ausência de rótulos dos robôs**. [E02–E03]

O método oficial de comparação é **COMP = U + C1+C2+C4-DM, com fluxo contínuo**. O núcleo inteiro é um problema de cobertura em $y$ que fornece limite inferior; seu objetivo não é automaticamente uma solução viável do MIN-STATION. [E04, E07]

### O que está efetivamente pronto

| Componente | Estado real no corte auditado |
|---|---|
| T1–T22 | Backlog histórico encerrado; corretude, confiabilidade, famílias estruturais e posicionamento têm artefatos próprios |
| R1–R4 / Fase A | Executados; 411 linhas de baseline, partição por origem, limites oficiais; versão congelada sem tag `benchmark-v1.0` |
| Fase B | F-CC definida, implementada e avaliada; GF1 passou. Parte F-C3 continua aberta na branch |
| R5–R7 / Fase C | Executados; G1 selecionou compatibilidade, com limitações interpretativas identificadas nesta revisão |
| R11 / Fase D | Encerrada com divergência confirmada, e não com certificadores especializados aprovados |
| R8, R9, R10 | Direções liberadas ou condicionais pelos gates; não executadas como métodos novos |
| R12 | Bloqueada pelo gate atual; não há evidência positiva para abri-la agora |
| R13 | Bloqueada até um método passar a etapa de desenvolvimento |

O benchmark principal tem **75 entradas: 70 do benchmark-v1 e cinco legadas**. As 70 vêm de nove famílias e 56 grafos de origem, sem vazamento entre desenvolvimento e avaliação na partição vigente. Existem variantes e legados associados ao mesmo grafo; 75 linhas não significam 75 problemas independentes. [E06–E08]

Na corrida oficial, **nenhuma das 29 D/A elegíveis para avanço teve $LB^*=UB^*$**. O gap relativo combinado varia de 3,2% a 55,6%, com mediana de 18,6%. Logo o benchmark atual não é globalmente fácil demais. A questão é selecionar o mecanismo relevante, não simplesmente aumentar seu tamanho. [E07]

### Como as evidências foram tratadas

Para resultados numéricos, esta revisão prioriza CSV e código de cálculo, depois relatório, gate, plano e histórico. Para fidelidade matemática, a definição do problema e uma prova válida têm precedência sobre um rótulo documental ou uma tabela de solver.

Os identificadores abaixo são links para a versão fixa auditada; as citações ao longo do texto apontam esses artefatos.

| ID | Evidência principal | Uso nesta análise |
|---|---|---|
| E01 | [CLAUDE.md][e01], [RESEARCH.md][research], [project-overview.md][overview], [source-map.md][sources] | Contexto, escopo e papel das fontes |
| E02 | [base-formulation.md][e02] e [baseline.py][baseline] | Baseline vigente |
| E03 | [validacao-formulacao-base.md][e03], §5.5 e verificação final | Equivalência, terminais e validação independente |
| E04 | [open-questions.md][e04] | Decisões vigentes e questões abertas |
| E05 | [backlog-continuacao.md][e05] e [plano-proxima-fase.md][plan] | Histórico T1–T22 e programa R1–R13 |
| E06 | [manifest.csv][e06] e [regra-particao-origem.md][partition] | Benchmark e unidade de agrupamento |
| E07 | [linha_base.csv][e07], [resultados-linha-de-base.md][baseline-report], [pré-registro][baseline-pre] | Referencial oficial de limites |
| E08 | [Spec A][e08] | R1–R4, orçamento e pendências administrativas |
| E09 | [F-CC][e09] e [provas-fcc-fc3.md][proofs] | Definição e proposições P1–P11 |
| E10 | [fcc.py][e10] e [verify_fcc.py][fcc-verify] | Modelos implementados e cruzamentos |
| E11 | [f3-fcc.csv][e11], [resultados-f3-fcc.md][f3-report], [pré-registro F3][f3-pre] | Força do LP e exclusões |
| E12 | [decisao-gf1.md][e12] e [Spec B][specb] | Gate GF1 e limites da autorização científica |
| E13 | [r6-gamma.csv][e13] e [resultados-r6-gamma.md][gamma-report] | Gap de compatibilidade |
| E14 | [r6-primal.csv][e14] e [resultados-r6-primal.md][primal-report] | Teste primal de um fator |
| E15 | [r7-plato.csv][e15] e [resultados-r7-plato.md][r7-report] | Soluções do platô e cortes devolvidos |
| E16 | [run_r7_plato.py][e16] | Definição operacional das métricas de R7 |
| E17 | [decisao-g1.md][e17], [pré-registro R5][r5-pre], [Spec C][specc] | Gate G1 |
| E18 | [r11-certificadores.csv][e18] | Lote oficial de R11 |
| E19 | [resultados-r11-certificadores.md][e19] | Resultado por classe e variante |
| E20 | [auditoria-r11-divergencias.md][e20] | Redução e revisão das divergências |
| E21 | [conclusao-r11-certificadores.md][e21] e [Spec D][specd] | Fechamento de R11 |
| E22 | [leituras R11][e22], [pré-registro R11][r11-pre], [path_cycle.py][pathcode], [spider.py][spidercode] | Interpretações e execução literal |
| E23 | [familias-estruturais.md][e23], [piloto_fase_p.csv][phasep-csv], [decisao-fase-p.md][phasep] | BP, HB, SC, TR e decisão da Fase P |
| E24 | [fase_e_sc.csv][e24] e [fase-e-sc.md][phasee] | Avaliação ampliada de SC |
| E25 | [C6][e25], [desagregação all-V][disagg], [decisão T16][t16] | Limites de linhas anteriores |
| E26 | [overlap-ijcai2026-min-station.md][e26], [Das original][das], [IJCAI-26][ijcai], [Pereira & Ravelo][spiderpaper] | Posicionamento e definições das fontes |
| E27 | [resultados-e12-pli.md][e27], [E9/E10][e9e10], [E13][e13-report], [E14][e14-report] | CBI e histórico de testes primais |
| E28 | [direcoes-pli-min-station.md][e28], [bundle][bundle], [subgradiente][subgradient] | Limites teóricos e negativos anteriores |
| E29 | [F-C3 atual][e29] | Estado realmente incorporado na branch |
| E30 | [benchmark-v1.md][e30] e [protocolo de comparação][protocol] | Cobertura experimental e interpretação |

## 3. Linha do tempo das decisões recentes

Cada linha distingue pergunta, execução, evidência, resultado e consequência. Uma decisão posterior não apaga a condição experimental em que a anterior foi tomada.

| Etapa | Hipótese/pergunta → trabalho realizado | Evidência → resultado | Decisão e consequência |
|---|---|---|---|
| Base all-V e variante U | A formulação representa Das, inclusive terminais compartilhados? → revisão de balanços, prova e validação por bateria | E02–E03: balanço separado era inválido para sobreposição; U e oráculo com permanência concordam com o validador | Preservar U como referência exata; não remover automaticamente $S∩T$ |
| C4-DM e auditoria do oráculo | Cortes e validação respeitam permanência? → correções e regressões | E03–E05: erros locais corrigidos; T4 não encontrou veredito publicado que exigisse reexecução | Fortalecer controle de corretude antes de comparar desempenho |
| E9–E14 / E12 | O núcleo, CBI ou busca primal explicam/resolvem o residual? → campanhas e controles | E27: CBI não supera núcleo; construtores fracos; E13 mistura fatores; E14 não certifica nenhuma das quatro instâncias | Encerrar A2/CBI para Das no formato testado; não concluir automaticamente que todo residual é dual |
| Bloco 2 | As pequenas diferenças são reproduzíveis? → ordem determinística, instrumentação, protocolo e orçamento por trabalho | E05, E30: infraestrutura mais consistente; passado continua pré-protocolo | Comparações futuras devem ser pareadas e separar origem dos grafos |
| BP | Redução de Bin Packing cria lados difíceis de UB e LB? → gerador, certificado e piloto | E23: lado sim fácil; lado não retém gap em escala maior | Descartar como expansão prevista da Fase E; preservar como instrumento de compatibilidade |
| HB | Deficiência de Hall com relés repartidos gera dificuldade? → enumeração e piloto | E23: gap do núcleo existe, mas MIP resolve as células do piloto rapidamente | Descartar como benchmark difícil naquele formato; manter para estudar limites |
| E11/C6 | Multiplicidade de primeiro salto fecha HB? → desigualdade válida e medição | E25: LP melhora parcialmente, mas não fecha; COMP+C6 não muda a decisão do piloto | Não ampliar a mesma família de primeiro salto como principal resposta ao gap |
| SC | Cobertura com gap conhecido separa modelos? → GF2 e gêmeos, Fase P | E23: separação entre base, COMP e núcleo | Promover somente SC |
| TR | Há muitos ótimos inviáveis do núcleo mesmo quando $Γ=0$? → gerador e validação | E23, E25: 8/2 e 27/3 ótimos/viáveis nos controles registrados | Preservar diagnóstico; não abrir outra bateria de CBI |
| All-V desagregada | Identificar origens fortalece o LP suficientemente? → formulação e pequenos testes | E25: ganho parcial, custo $O(m\vert A_r\vert )$; não fecha os exemplos | Não expandir como método sem nova compressão ou ganho discriminante |
| Fase E | Separação de SC persiste acima do piloto? → k=8,9, três seeds | E24: núcleo prova na raiz; modelos de fluxo param na raiz; gêmeos excluídos por falta de certificado | Preservar fenômeno; simetria continua inconclusiva |
| T22 / IJCAI | O que ainda pode ser contribuição? → comparação de definições, teoremas e literatura | E26: matching, alcance, reduções e árvores têm antecedentes diretos | Posicionar contribuição em formulação, análise de limites e experimentação; evitar reivindicações de novidade indevidas |
| Fase A | Há uma referência atual comparável? → R1–R4 | E07: 411 linhas, 75 entradas, três braços; nenhuma D/A elegível fechada | Referencial oficial pronto; $LB^*/UB^*$ não são um único algoritmo |
| Fase B / GF1 | Configurações conectadas superam os limites disponíveis? → F3 | E11–E12: F-CC passa; F-C3 ausente | R8 ganha justificativa exploratória; custo ainda não resolvido |
| Fase C / G1 | Onde priorizar o próximo esforço? → $Γ$, teste primal e pool | E13–E17: sinal pró-compatibilidade; diagnóstico específico ainda incompleto | R10 e investigação de F-CC recomendados; R12 não liberada |
| R11 / Fase D | Algoritmos de classes especiais fornecem certificação independente? → 44 instâncias, 80 linhas e auditoria | E18–E22: divergências confirmadas e leituras não determinadas | Não usar procedimentos literais como oráculos; substituir essa dependência e avaliar oportunidade teórica separadamente |

Os commits `4cd425f`, `d2fad3b`, `eafcd7b`, `2ff71d2`, `ea785a0`, `1403019`, `dd485dc`, `dd4d401` e `b3c7337` registram essa passagem de corretude e estrutura para linha de base, F-CC, diagnóstico e auditoria de certificadores.

## 4. Matriz dos últimos planos e specs

| Fase/Spec | Pergunta | Resultado | Evidência | Decisão | Estado |
|---|---|---|---|---|---|
| Bloco 1 / T1–T5 | U e oráculo representam Das? | Prova com permanência e bateria de cruzamento | E03, E05 | Base preservada | `SUPPORTED / CLOSED` |
| Bloco 2 / T6–T11 | Comparações são rastreáveis? | Determinismo, instrumentação e protocolo; dívida de snapshots ainda existe | E05, E07, E30 | Usar infraestrutura e qualificar histórico | `SUPPORTED / CLOSED` |
| Bloco 3 / BP | Família discrimina dificuldade primal/dual prevista? | Não pelo critério congelado | E23 | Sem expansão P→E | `NEGATIVE RESULT / CLOSED` |
| Bloco 3 / HB | Gap local gera MIP difícil? | Não nas células testadas | E23 | Instrumento de bound, não bateria difícil | `NEGATIVE RESULT / CLOSED` |
| Bloco 3 / C6 | Primeiro salto com multiplicidade fecha gap? | Válida, ganho insuficiente | E25 | Não expandir mesmo mecanismo | `NEGATIVE RESULT` |
| Bloco 3 / SC, P→E | Núcleo se separa dos modelos de fluxo? | Sim em GF2; gêmeos não avaliados em E | E23–E24 | Preservar GF2; não concluir simetria | `SUPPORTED / INCONCLUSIVE` |
| Bloco 3 / TR | Platô pode coexistir com $Γ=0$? | Sim nos controles | E23, E15 | Uso diagnóstico | `SUPPORTED / CLOSED` |
| Bloco 3 / all-V | Ganho justifica multiplicação de variáveis? | Não há demonstração suficiente | E25 | Sem expansão | `PAUSED` |
| Bloco 4 / T22 | Qual contribuição resta frente ao IJCAI? | Sobreposição delimitada; redação de artigo não feita | E26 | Atualizar posicionamento com F3/R11 | `SUPPORTED / CLOSED` |
| Fase A / R1–R4 | Referencial oficial? | Executado; tag e AV pendentes | E07–E08 | Prosseguir sem refazer baseline indiscriminadamente | `CLOSED` operacionalmente |
| Fase B / F-CC | LP mais forte no regime compatibilidade? | GF1 passou em três tipos pequenos | E09–E12 | Candidata ativa | `SUPPORTED` |
| Fase B / F-C3 | Incremento dos trios? | Sem braço implementado nem valores na branch | E29 | Fechamento limitado e posterior validação | `OPEN` |
| Fase C / R5–R6 | $Γ>0$ e folga primal de um fator? | Oito famílias positivas; limiar primal não atingido | E13–E14 | Priorizar investigação de LB | `SUPPORTED / CLOSED` |
| Fase C / R7 | Qual mecanismo explica platô? | Pool útil; H-desc não discrimina mecanismo; métrica de cortes incorreta | E15–E16 | Reinterpretar e completar análise específica | `INCONCLUSIVE` quanto à causa |
| G1 | Qual lado pesquisar primeiro? | Compatibilidade pela regra registrada | E17 | Manter decisão operacional, limitar a interpretação | `SUPPORTED` como gate |
| Fase D / R11 | Certificadores especializados exatos? | Divergências e indefinição nas leituras de spiders | E18–E22 | Não usar como referência universal de OPT | `CONFIRMED DIVERGENCE / CLOSED` |
| R8/R10 | Bound de compatibilidade viável em escala? | Não executado | E05, E12, E17 | Próxima pergunta principal | `OPEN` |
| R9/R12/R13 | Método inteiro, primal, confirmação? | Dependências não satisfeitas ou gate negativo | E05, E17 | Adiar conforme seção 14 | `BLOCKED` |

## 5. Resultados mais fortes

### Resultados que devem ser preservados e explorados

| Resultado | Evidência | Por que importa | Grau de confiança | Potencial de continuidade |
|---|---|---|---|---|
| Exatidão da baseline U com todos os terminais | E03, §5.5; 7.998 instâncias e 125.922 instalações no recorte exaustivo n≤4, além da amostra n=5 e gadgets | Permite distinguir falha de uma hipótese de falha do modelo de referência | Prova e verificação exaustiva no recorte declarado | Fundamento do artigo e de toda validação; não precisa de nova campanha ampla |
| Componentes de $H[C]$ mais matching caracterizam viabilidade; F-CC dá formulação exata | E09–E10; cruzamento adicional em R11 | Representa compartilhamento real de infraestrutura sem reintroduzir rótulos artificiais | Prova da caracterização/F-CC e cruzamentos pequenos | Formulação e análise poliédrica; a caracterização básica tem antecedente no IJCAI |
| F-CC LP supera o melhor controle de F3 em HB, BP e Sec59 | E11–E12 | Primeira evidência recente diretamente favorável a uma formulação de compatibilidade no regime $Γ>0$ | Evidência experimental em piloto delimitado | Teoremas por família, pricing certificado ou projeção de informação útil |
| Núcleo inteiro e modelos de fluxo têm comportamento distinto em SC-GF2 | E23–E24 | Mostra que representar o mesmo componente de cobertura de outra forma muda muito o processamento | Duas escalas de avaliação e três seeds, com OPT analítico | Resultado experimental forte; investigar representações sem confundir com novo teorema de Set Cover |
| $Γ>0$ aparece em múltiplas famílias | E13 | A insuficiência do núcleo não é um único gadget nem apenas problema de solver | Valores exatos em parte da amostra, intervalos explicitados no restante | Motiva pesquisar informação além da cobertura |
| Referencial oficial reproduz a heterogeneidade do núcleo | E07 | Núcleo é útil em parte de PUC/PUCN; COMP continua superior em MAPF/Vienna | Corrida de orçamento controlado, com três seeds nas D/A | Comparação por regime; eventual combinação de limites com custo contabilizado |
| R11 fornece contraexemplos reduzidos e auditados | E18–E22 | Protege o projeto contra uma fonte de certificados incorretos e torna a divergência verificável sem depender de desempenho | Argumentos manuais nos mínimos e concordância entre referências no lote | Nota técnica/revisão de algoritmo, condicionada à conferência da versão publicada e revisão humana |

A parte exaustiva de T2 não deve ser descrita como validação de todos os grafos até cinco vértices: para $n=5$ houve amostra de 60 instâncias. Analogamente, as 80 linhas de R11 incluem três variantes sobre uma mesma aranha; não são 80 instâncias independentes.

O resultado de F-CC é o candidato mais direto a uma nova contribuição em formulação. O resultado de SC é atualmente o mais sólido para uma afirmação experimental de separação entre representações. Eles respondem a perguntas diferentes.

## 6. Resultados negativos e linhas encerradas

### Linhas que não devem continuar no formato atual

| Linha | O que se buscava e o que ocorreu | Aprendizado reutilizável | Condição concreta para reabrir |
|---|---|---|---|
| CBI / A2 | Ganhar com separação iterativa em $y$. E12: uma vitória sobre COMP, nenhuma sobre o núcleo; muitos cortes não elevaram o LB | O ganho de E8 vinha, em parte, do núcleo e de extensões; separar oráculo exato de método competitivo | Uma nova desigualdade/representação que elimine classes do platô e melhore o limite, antes de nova bateria iterativa |
| BC-Y genérico | Substituir o compacto por árvore em $y$. E7 tinha confundidores; E8 não sustenta generalização a Das | Não há demonstração limpa de superioridade geral; E12 reforça o problema de bound | Novo mecanismo e comparação pareada; não apenas reorganizar callbacks |
| Lagrangeana da ativação da base | Superar ou calcular melhor o bound. Bundle e subgradiente ficaram abaixo do LP em 8/8 linhas de cada tabela | A relaxação dualizada possui teto teórico no LP da própria base; tuning não muda esse teto | Outro subproblema com força comprovadamente distinta e custo justificável |
| Benders clássico | Obter bound superior por decomposição | A família completa dos cortes clássicos projeta o LP da base; não o fortalece | Gargalo demonstrado de memória/solução do LP ou nova estrutura inteira no subproblema; não promessa de bound mais forte por si só |
| Reverse-delete desde $C=V$ | Incumbente bom rapidamente. Em E10, devolveu ≥90% de V em 19/30 casos | Uma construção inicial enorme torna o orçamento de remoção improdutivo | Novo ponto de partida pequeno e estruturalmente justificado, com evidência incremental sobre o solver |
| C5 por limiar | Separação fracionária prática da família de cortes | Histórico registra ganho desprezível; oráculo inteiro continua útil | Separador matematicamente mais informativo, com testemunho de ganho além dos cortes já usados |
| Symmetry breaking genérico | Reduzir busca por equivalências de estações | Testes de hipercubos não deram sinal suficiente; anonimato já elimina rótulos de robôs | Automorfismos úteis identificados e ablação limpa; a comparação SC/gêmeos ainda não forneceu essa evidência |
| BP como grande benchmark do piloto | Separar lados difíceis de primal e dual | O lado sim foi fácil; não passou pelo critério original. Isso não invalida seu papel como pequeno teste de F-CC | Nova hipótese explícita sobre compatibilidade, apoiada por GF1, com novos critérios; não rebatizar a Fase P como sucesso |
| HB como benchmark difícil | Dificuldade por Hall local | Todos os métodos fecharam rapidamente o piloto; terminais como hubs limitam a dificuldade pretendida | Acoplamento entre bolsões com prova/validação de que não há atalhos all-V; não repetir bolsões fáceis |
| TR como bateria de CBI | Expor remoção pontual de ótimos inviáveis | Mostra platô com $Γ=0$; não comprova insuficiência do melhor bound | Método novo que use a estrutura do platô; não continuar CBI só porque há muitas soluções |
| C6 atual | Capturar multiplicidade do primeiro salto | Válida, porém não captura o restante da rota/compatibilidade; gerações maiores não garantem informação nova | Um witness de deficiência em outra camada e uma desigualdade que o elimine sem cortar instalações viáveis |
| Desagregação all-V | Ganhar pela distinção de origens | Melhora LP, mas abaixo de controles relevantes e com expansão $O(m\vert A_r\vert )$ | Compressão específica ou ganho incremental que justifique o custo; não há teste amplo que prove lentidão universal |
| Caminhos/ciclos literais como certificadores | OPT independente barato | R11 confirmou subotimalidade, inclusive em casos de OPT zero | Algoritmo corrigido, prova completa e nova validação; um ajuste ad hoc de contador não basta |
| Spider universal a partir do texto atual | Certificador linear | Leituras A/B/U divergem ou ficam não determinadas | Especificação executável inequívoca, análise de entradas/saídas de radiais e prova que cubra os casos SP-R* |
| Preprocessing genérico | Redução robusta do esforço de solve | Histórico tem comparações limitadas e ausência de ganho robusto | Fixação/dominância com prova e alvo estrutural mensurado, preservando terminais |

Fontes: E23–E28, resultados E7/E8 preservados no histórico E05, e E18–E22 para R11. Os negativos antigos são em parte pré-protocolo ou sobre extensões; o motivo para não reabri-los não é uma alegação universal de impossibilidade, mas a ausência de nova evidência frente a opções mais bem sustentadas.

## 7. Resultados inconclusivos

**Força matemática não é desempenho.** A desagregação all-V não foi submetida a uma campanha pareada capaz de demonstrar lentidão universal. A F-CC tampouco foi submetida a uma campanha que demonstre ganho de tempo, nós ou capacidade de resolver D/A. A decisão de priorizar uma e pausar outra deve refletir a força incremental já medida e o custo esperado, com essa diferença explícita. [E11, E25]

**F-C3 não tem resultado computacional na branch.** Nenhum valor de F3 pode ser atribuído às redes de trios. Existe material matemático anterior disponível nesta sessão, mas a integração e a validação são questões separadas, tratadas na seção 9.

**O fracasso do teste primal não elimina métodos primais.** Ele elimina o sinal mínimo exigido daquele fator, naquela amostra e orçamento. Os testes E10/E13/E14 não autorizam uma conclusão mais ampla. [E14, E27]

**Simetria em SC não foi isolada.** Os dez gêmeos previstos em k=8,9 não obtiveram certificado de Set Cover no cap de 90 segundos e não entraram na avaliação. A Fase E comprova a separação entre modelos em GF2, não seu motivo causal nem sua prevalência em sistemas de incidência genéricos. [E24]

**H-desc não identificou ainda a família de desigualdades adequada.** Todo conjunto de estações inviável precisa falhar no matching de pares realmente alcançáveis. Essa equivalência não decide entre falta de alcance individual, deficiência coletiva, custo de conectar alternativas e inconsistência fracionária de configurações. [E09, E15–E16]

**SC não teve LP de F-CC em F3.** Houve exclusão por cap. A frase “não há ganho em SC” no gate não é um resultado medido desse braço. O efeito de F-C3 em SC também não pode ser declarado nulo a partir desse teste. [E11–E12]

**Os resultados estruturais não se generalizam automaticamente em parâmetros.** O próprio documento HB mantém como hipótese a fórmula geral do limite inferior e a aditividade; certificados nas células executadas não fecham todos os parâmetros. BP negativo pequeno com F-CC ótima não prova que a formulação feche toda instância da redução. [E23]

Para qualquer afirmação de superioridade geral, causalidade da simetria, escala da F-CC ou benefício incremental de F-C3 no regime $Γ>0$: **Ainda não há evidência suficiente para concluir.**

## 8. F-CC e GF1

### O que a formulação representa e fortalece

Uma configuração $q=(W,I,J)$ reúne estações conectadas em $H=G^r$ e grupos balanceados de origens/destinos alcançáveis dessa infraestrutura. Dentro de uma configuração, qualquer origem elegível pode ser associada a qualquer destino elegível. As equações globais cobrem cada terminal uma vez; a ligação $∑_{q:v∈W_q}λ_q≤y_v$ cobra a infraestrutura compartilhada. [E09]

A mudança relevante frente ao fluxo agregado é que **a conectividade do conjunto utilizado já está embutida na configuração**. Frente ao núcleo de cobertura, ela representa conjuntamente quais origens e destinos essa infraestrutura pode servir. Não exige que todas as estações instaladas pertençam a uma única componente.

Com $y$ binário, a integralidade do matching bipartido dá exatidão mesmo mantendo $λ,d$ contínuas. No LP, distribuições de configurações podem continuar incompatíveis com uma instalação conjunta inteira; por isso F-CC não é ideal em geral.

### Evidência numérica que decidiu GF1

Valores do CSV, sem executar solver nesta análise:

| Instância | LP base | LP COMP | Núcleo IP | LP F-CC | OPT | Γ |
|---|---:|---:|---:|---:|---:|---:|
| HB q4, ndir2, p1 | 0,3333 | 1 | 1 | **2** | 2 | 1 |
| HB q5, ndir2, p1 | 0,375 | 1,0833 | 1 | **3** | 3 | 2 |
| BP não [3,1], q2 | 3 | 6 | 6 | **7** | 7 | 1 |
| Sec59, L7 | 2,3333 | 3,6667 | 2 | **4,5** | 7 | 5 |
| SharedTerminal | 0,5 | **1** | 1 | 0,5 | 1 | 0 |
| Tri | 1 | 1,5 | **2** | 1,5 | 2 | 0 |
| TR k2,L5,r2 | 3 | 3 | 3 | 3 | 3 | 0 |
| SC-GF2 k3 | 1 | 1,75 | 3 | **não medido** | 3 | 0 |

Há ganho sobre $max(LP(COMP),z_{core}^{IP})$ em três tipos com $Γ>0$. A regra registrada usa $(z_{FCC}-max)/Γ$ e é satisfeita. **GF1=PASS é sustentado pela tabela**, sem depender de interpretar R7 ou de supor resultados de F-C3. [E11–E12]

Contudo, a fração de GF1 não é sempre a fração do residual do melhor controle que foi fechada. Em Sec59, o ganho é $5/6$; dividido por $Γ=5$ dá 16,7%, mas dividido pelo residual $7-11/3=10/3$ dá 25%. Em HB q5, F-CC atinge OPT, apesar da fração registrada de 95,8%. **Preservar a regra histórica; usar métricas distintas e nomes precisos no próximo contrato.**

### Uma complementaridade já demonstrada

SharedTerminal mostra $z_{FCC}=0,5<1=z_{COMP}$, enquanto HB/BP mostram a desigualdade oposta. Logo **F-CC e o LP fortalecido de COMP não têm dominância universal de valor em nenhuma direção**. A cadeia com “base” refere-se à base sem os cortes, não a COMP. [E11]

Isso favorece um controle barato e informativo antes de outra formulação: **F-CC acrescida dos cortes estáticos válidos já existentes**. A interseção preserva as soluções inteiras do MIN-STATION. Sob a inclusão da projeção de F-CC na base, seu LP domina ambos os controles. A vantagem estrita e o custo precisam ser medidos; não são resultados já executados.

### Custo e limites

O CSV registra 9.341 conjuntos em HB q4, 163.616 em HB q5, 83.845 em TR, e exclusão de SC k3 ao ultrapassar 200 mil. Esses números expõem o gargalo antes de chegar às D/A. O modelo original tem poucas linhas principais, mas exponencialmente muitas configurações; a forma separada troca a enumeração de I/J por marginais, não remove a explosão dos W. [E10–E11]

O LP de um master com apenas algumas colunas não é automaticamente um LB do MIN-STATION: restringir colunas em minimização pode elevar o objetivo acima do ótimo do modelo completo. É necessário pricing completo ou um limite dual global comprovadamente válido. Esse ponto decide se R8 produzirá ciência verificável ou apenas números otimistas.

### Duas provas que precisam de acabamento

1. **P7, incidência vazia.** O argumento de decomposição usa $\vert I\vert =\vert J\vert $ e pode produzir $I=J=∅$, embora Q exclua esse caso. Para igualdade do LP e projeção em y, basta descartar a massa vazia: α,β,d não mudam, λ diminui e as ligações em y afrouxam. Não se pode alegar que todas as marginais λ permanecem idênticas sem normalização adicional. A restrição $λ_W≤∑_sα_{sW}$ é relevante quando λ alimenta redes de consistência. Isso corrige a prova, sem refutar os valores de F3. [E09, provas P7; E10]
2. **P2, ativação em terminais.** O texto limita trânsito por $my_v$ e depois acrescenta chegada direta gratuita; essa soma não prova $in(v)≤b_v+(m-b_v)y_v$. Uma prova correta escolhe bijeções e caminhos simples em cada configuração, separa atendimento final de trânsito e limita o trânsito de um destino por $(m-1)∑_{q:v∈W_q}λ_q$. Se o destino não pertence a J, o grupo tem no máximo m−1 integrantes; se pertence, seu robô final não transita internamente por ele. O lado das origens é simétrico. **É uma lacuna reparável de exposição, não um contraexemplo à dominância.**

Esses reparos e a ablação com cortes existentes têm prioridade sobre expandir prematuramente uma árvore de branch-and-price.

## 9. F-C3 — estado real

### Três estados diferentes que precisam continuar separados

**Na branch auditada:** há a forma separada da F-CC e uma descrição incompleta das redes de trios. O documento enumera O1–O5: etapas, arcos, ligações, escopo de cada rede e ordem. Não há implementação, braço F3 nem CSV da F-C3. P8 e P11 permanecem hipóteses/abertos. Esse é o estado oficial do projeto neste corte. [E29, E09–E12]

**No material anterior disponível nesta sessão:** existe a definição consolidada de 05/10/2026, preparada sobre `a81e197`, e o documento externo completo de 01/10/2026 que a fundamentou. A consolidação não está incorporada em `b3c7337`. Ela especifica a rede, corrige a normalização da forma separada, apresenta provas analíticas e exemplos. Portanto, “ausente da branch” não equivale a “nenhuma definição disponível”. O material deve ser recuperado e revisado antes de gastar esforço reconstruindo-o novamente.

**Como evidência de método:** continua inexistente. Provas e exemplos analíticos dessa proposta não substituem implementação auditada, cruzamento com `viavel` e avaliação de benefício incremental. Nenhum desses resultados deve ser lançado retroativamente em F3.

Referências complementares externas à branch: [documento original de componentes e trios](sandbox:/workspace/scratch/c87335ddaac1/MIN-STATION-formulacao-componentes-consistencia-trios.md) e [definição consolidada de F-C3, versão 05/10/2026](sandbox:/workspace/scratch/c87335ddaac1/min-station-fc3-definition/docs/technical/reference/formulacao-fc3-consistencia-trios.md), §§5–14. Os SHA-256 dos arquivos examinados são, respectivamente, `fd5e9a0054ef6d10ba9f791f2cc77df55389c8cf72bcac3ccf56376558ef49f4` e `b68e9b6bfaab97456bc50fcfc2f2c6191eb5e654d70e805050c32e093a01e236`. As conclusões condicionais a seguir usam precisamente essa definição, não uma F-C3 adivinhada a partir do resumo atual.

### O que os trios acrescentariam

Na definição consolidada, os oito estados representam **os subconjuntos de um trio já atendidos**. Cada etapa corresponde a um W conectado. A rede distingue pular W de selecioná-lo, mesmo quando ele não atende nenhum integrante daquele trio. Arcos de seleção atribuem um subconjunto ainda não atendido; as marginais coincidem com λ e α, ou λ e β. O atendimento direto residual fecha a rede. As redes de origens e destinos compartilham as variáveis do núcleo.

Trata-se de distribuições **locais** coerentes com as mesmas marginais. Não é um único sorteio global de todas as instalações nem uma nova necessidade de integralizar o matching bipartido. Para uma instalação fixa, o matching já é integral; o problema está em combinar decisões fracionárias de infraestrutura/atribuição de modo realizável.

A proposta analítica demonstra exatidão inteira e dominância do LP sobre F-CC para a família completa de W. Demonstra também que consistência de trios não torna o LP integral: a construção a partir de um ciclo de cinco alternativas admite valor 2,5 contra OPT 3. Essas propriedades devem ser revisadas e incorporadas com procedência explícita; **o repositório ainda não as certifica como parte da Fase B executada**.

### Por que isso não torna F-C3 automaticamente a prioridade central

Os exemplos analíticos de melhora estrita — inclusive 1,5→2 e 3→4 — têm **núcleo IP igual ao ótimo**, isto é, $Γ=0$. Eles demonstram força poliédrica adicional, mas não demonstram ganho acima do referencial que motivou GF1/G1.

Além disso:

- F-CC já fecha os pequenos HB e BP em F3; nesses pontos, trios não podem melhorar o objetivo acima de OPT.
- Sec59 deixa residual e é um teste mais informativo para uma possível extensão, mas seu resultado com trios ainda é desconhecido.
- O custo não é apenas “oito estados”: há estágios para os W e $2\binom m3$ redes quando se usam todos os trios dos dois lados. A dependência exponencial de W continua existindo.
- Não há prova de que a F-C3 proposta domine sempre COMP ou o núcleo IP. O exemplo de ciclo de cinco alternativas refuta a segunda dominância.

**Decisão recomendada:** finalizar a rastreabilidade e a revisão matemática é uma tarefa curta, de alto valor e custo limitado. Tornar F-C3 uma frente algorítmica de escala é **condicional** a ganho adicional sobre F-CC com cortes existentes e sobre o melhor controle relevante, preferencialmente em casos com $Γ>0$. Não manter a linha indefinidamente apenas porque há uma separação estrita de LP em algum gadget.

### SC como controle: distinguir a pergunta

A definição consolidada contém um argumento analítico segundo o qual a F-C3 corta o ótimo fracionário uniforme de SC-GF2: um trio linearmente dependente sobre GF(2) força escolhas que atendem zero ou dois de seus integrantes e não consegue particionar três integrantes dessa forma. Para essa definição, a melhora sobre o LP de F-CC é compatível com $Γ=0$ e não supera o núcleo IP.

Esse argumento deve ser conferido na integração. Ele já é suficiente para **não usar a premissa “qualquer ganho em SC é erro” como critério universal**. SC é controle negativo para avanço acima do núcleo IP naquela família; pode ser controle positivo de consistência local. O pré-registro antigo fica intacto; o próximo deve distinguir essas duas comparações.

### Erro documental pontual a corrigir

O texto atual de F-C3 diz “incluindo $d_{ss}=0$”. A distância $d_G(s,s)$ é zero; **a variável de permanência não deve ser fixada em zero**. O código de F-CC cria o par $(s,s)$ e deixa sua variável assumir o atendimento direto, inclusive valor 1. É uma confusão de notação na referência de F-C3, não evidência de que o código medido bloqueie permanência. [E29, E10]

## 10. Diagnóstico da Fase C e G1

### O sinal sólido de R6

O CSV de Γ tem **61 linhas: 43 exatas, 12 intervalares e seis desconhecidas**. Entre as exatas, há Γ positivo em oito famílias: MAPF, PACE, PUC, PUCN, SteinLib-b, lin, BP e HB. Não se deve transformar as linhas positivas em réplicas independentes: há variantes do mesmo grafo e pequenos instrumentos da mesma construção. [E13]

Os intervalos têm interpretação precisa quando o núcleo foi resolvido:

\[
\max\{0,LB^*-z_{core}^{IP}\}\leq Γ\leq UB^*-z_{core}^{IP}.
\]

Quando o núcleo não foi certificado, Γ exato não está disponível. O estado `unknown` foi corretamente preservado no CSV. R6 também não amostra todas as D/A possíveis de modo equilibrado; os resultados certificados fáceis e os casos de desenvolvimento têm maior representação.

O teste primal tem **13 instâncias × três seeds × dois braços = 78 linhas**. A mudança foi `MIPFocus=1`, mantendo o orçamento de 164 unidades de trabalho, quatro threads e ausência de start. Nenhuma das 13 instâncias melhorou o UB em pelo menos uma estação nas três seeds. Isso sustenta o gate registrado. [E14]

O que não sustenta é a afirmação causal de que nenhum investimento primal poderia ajudar. Um parâmetro sem ganho não mede a distância do incumbente ao ótimo nem a qualidade de toda classe de heurísticas. O rótulo de G1 deve ser lido como **prioridade operacional de pesquisa em LB**, não como decomposição demonstrada de todo gap de solver.

### O que R7 realmente mediu

O pool contém 610 instalações, das quais 608 inviáveis segundo o oráculo. Em TR há oito ótimos do núcleo, dois viáveis; em BP há dois, ambos inviáveis; os três pools maiores param no cap de 200. [E15]

Para um C fixo, defina B_C com os pares diretos e os pares que podem usar uma componente de H[C]. Então:

\[
C\text{ viável}\iff B_C\text{ tem matching perfeito}.
\]

Essa é a caracterização usada em P1 e em `matching_componentes`. Logo encontrar H-desc em todos os C inviáveis é um cruzamento de consistência com a caracterização; **não é um teste que possa identificar, entre várias causas candidatas, por que o núcleo perde informação**.

Também é esperado que nenhum ótimo do núcleo seja viável quando se sabe $Γ>0$. Essa observação, sozinha, não revela um mecanismo novo. TR é particularmente útil porque separa essas duas noções: possui muitas instalações ótimas inviáveis, mas também instalações ótimas viáveis, e portanto $Γ=0$.

R7 fornece material valioso — instalações, componentes e testemunhos Z — para uma segunda leitura discriminante. Faltam testemunhos de Hall com seus conjuntos deficientes, distinção entre origens sem alcance e déficit de matching coletivo, e operações de reparo cuja validade explique quais classes de instalações um corte eliminaria.

### Erro de mensuração identificado no código

O runner incrementa `z_elimina[frozenset(Z)] += 1` quando o oráculo devolve Z. O resumo usa o maior contador como `max_elimina_um_Z`. Isso mede **quantas vezes aquele Z foi devolvido**, não quantas instalações registradas violam seu corte.

Para o corte $∑_{v∈Z}y_v≥1$ e uma instalação inteira C, a violação é exatamente $C∩Z=∅$. Recalculei essa incidência cruzada para cada Z distinto, usando somente os campos `estacoes`, `Z` e `oracle_viavel` do CSV:

| Pool | Instalações inviáveis | Z distintos | Máxima frequência de retorno, publicada como eliminação | Máxima quantidade de instalações realmente cortadas |
|---|---:|---:|---:|---:|
| TR k2,L5,r2 | 6 | 4 | 2 | 2 |
| BP não [3,1],q2 | 2 | 2 | 1 | 1 |
| MAPF maze m10 | 200 | 55 | 49 | 49 |
| lin03 | 200 | 65 | 17 | 17 |
| PUC cc9-2p | 200 | 66 | **21** | **27** |

Nos quatro primeiros casos os máximos coincidem; isso não torna o cálculo original correto. Em cc9, a diferença é concreta: 13,5% do pool, e não 10,5%. A correção não demonstra que a separação inteira de CBI seria competitiva. Refere-se apenas ao pool observado e aos Z devolvidos, não a todos os cortes possíveis nem a todo o platô.

Há outra nomenclatura inadequada: `n_origens_sem_par` conta origens de grau zero em B_C, e não o número de origens não emparelhadas num matching máximo. É possível ter todas as origens com vizinhos e ainda violar Hall. [E16]

**Consequência:** a afirmação de que o requisito de medir quantos ótimos cada corte elimina está completamente cumprido precisa ser corrigida. O pré-registro e os CSVs devem ser preservados; cabe uma nota posterior e a correção do produtor de resumo em outra tarefa.

### O que permanece válido depois dessa revisão

G1 se baseia em R6 e no teste primal, não no contador de R7. Portanto, **o erro não derruba G1**. Sustenta-se pesquisar compatibilidade e F-CC. Não se sustenta a passagem direta de “há várias componentes” para uma desigualdade que obrigue conectividade global: múltiplas componentes podem atender grupos balanceados e formar uma solução perfeitamente válida.

O que G1 libera é uma investigação; o que ainda falta é identificar qual testemunho é generalizável e qual representação consegue explorá-lo com custo menor.

## 11. R11 — impacto das divergências confirmadas

### Resultado bruto e confiança das referências

O CSV contém **44 instâncias únicas e 80 linhas**, distribuídas em 15 caminhos, 11 ciclos e 18 aranhas, estas últimas com três leituras. Há 69 linhas micro com enumeração ótima e 11 linhas acima do cap de enumeração. Baseline e F-CC binária terminam `OPTIMAL` nas 80 linhas; não há `reference_failure`. O máximo de conjuntos conectados registrado foi 14.664. [E18]

| Procedimento | Acordo | Subótimo | Solução inviável | Não determinado |
|---|---:|---:|---:|---:|
| path-alg1 | 3 | 12 | 0 | 0 |
| cycle-alg2 | 2 | 9 | 0 | 0 |
| spider-A | 6 | 1 | 8 | 3 |
| spider-B | 5 | 10 | 0 | 3 |
| spider-U | 3 | 0 | 5 | 10 |
| **Total** | **19** | **32** | **13** | **16** |

As concordâncias entre três referências aumentam a confiança; a enumeração por bateria é o cruzamento mais independente. Baseline e F-CC compartilham o problema, distâncias e parte da infraestrutura, portanto não são três provas experimentais completamente independentes. Os contraexemplos mínimos admitem argumentos manuais, que evitam depender dessa independência parcial.

### Caminhos

A auditoria reduz a divergência a uma aresta $v_0v_1$, $S={v_0}$, $T={v_1}$ e $r=1$. O movimento direto requer zero estações. O pseudocódigo literal incrementa o contador no vértice de origem e instala ali uma estação: custo 1. No lote congelado já existia o controle de três vértices com distância 2 e autonomia 2, igualmente de ótimo zero. [E20, E22; Das, Algorithm 1]

A conclusão sustentada é: **a implementação literal do pseudocódigo da versão auditada diverge do ótimo definido pelo próprio problema**. Não se segue que o problema em caminhos deixe de ser polinomial, nem que basta trocar uma linha para provar um algoritmo correto em todas as situações. É preciso distinguir contador, decisões gulosas, reinícios entre intervalos e prova de otimalidade.

### Ciclos

O procedimento de ciclos aplica o de caminhos após remover cada aresta. Assim, parte da divergência é herdada. O triângulo com origem e destino adjacentes e autonomia 1 também tem OPT zero, mas a leitura literal retorna uma estação. As nove linhas subótimas de ciclo não são nove mecanismos teóricos independentes. [E20–E22; Das, Algorithm 2]

### Spiders

O artigo de Pereira & Ravelo apresenta uma estratégia e provas em esboço, mas não determina univocamente todos os passos executáveis necessários. As variantes A/B/U documentam decisões interpretativas; falhas dessas variantes não autorizam atribuir silenciosamente cada decisão nova ao artigo.

O witness SP-R2 é especialmente informativo: centro c, radiais de comprimentos 1,5,1, origem no primeiro e destino na ponta do segundo, autonomia 2. A rota origem–destino tem seis arestas, logo duas estações bastam e são necessárias. Por exemplo, na radial longa podem ser colocadas a uma e três arestas do centro. A/U devolvem apenas c e são inviáveis; B devolve três estações e é subótima. [E18–E22]

O resultado não é “spiders são difíceis”: é que o estado usado na descrição local não fecha uma implementação exata universal. As necessidades de entrada em uma radial, estações existentes nela, demanda interna e energia residual não podem ser substituídas por uma regra informal de “atingiu o centro, então alcança qualquer alvo”.

Também importa distinguir **igualdade de custo de viabilidade**: SP-R1 mostra leitura com custo igual ao ótimo certificado, mas instalação inviável. Certificador deve produzir C e validar suas rotas/matching, não apenas acertar um número.

### Impacto no programa de pesquisa

R11 retirou uma fonte planejada de certificadores grandes. A sequência “prova → enumeração → certificadores da Spec D → D/A” não pode continuar literal. Ela deve usar:

- provas e contraexemplos verificáveis à mão;
- `viavel` e enumeração nos pequenos;
- baseline exata e F-CC completa como cruzamentos, com a dependência compartilhada declarada;
- famílias com certificado combinatório próprio, quando ele existe e foi demonstrado;
- algoritmos especializados novos apenas após sua própria prova e auditoria.

Isso não obriga a desenvolver um certificador universal novo antes de qualquer pesquisa de limites. Para validar uma desigualdade, uma prova geral e verificações adversariais pequenas são mais importantes do que um algoritmo especializado ainda não confiável.

**R11 também revelou uma oportunidade científica**, sobretudo na distinção entre pseudocódigo, propriedade estrutural e algoritmo corrigido. Mas é uma frente paralela limitada. O IJCAI-26 já afirma um algoritmo polinomial para árvores, incluindo estações pré-instaladas; propor simplesmente “resolver árvores” não oferece novidade por si só. [E26, Teorema 9]

Antes de uma afirmação pública sobre a literatura, conferir a versão final dos artigos contra as cópias auditadas e submeter o raciocínio à revisão humana/comunicação apropriada. Este parecer não envia mensagens nem faz uma alegação pública de erratum. O estado interno continua **`CONFIRMED DIVERGENCE`**, sem diluí-lo para `INCONCLUSIVE` só porque algumas leituras de spiders permanecem não determinadas.

## 12. O que aprendemos sobre a estrutura do MIN-STATION

### O que sabemos hoje que não sabíamos no início

**1. S∩T tem dois papéis, não um cancelamento automático.** Um terminal compartilhado pode permanecer ocupado ou trocar seu robô com outro. Como estação, também pode servir como relé de várias rotas. Removê-lo de S e T ou tratá-lo como relé gratuito altera o problema. Essa exigência vem da definição; a contribuição do projeto é tratá-la corretamente na formulação, no oráculo e nos testes. [E03–E04, E26]

**2. O matching é fácil depois que a infraestrutura está fixada.** A dificuldade combinatória principal é escolher estações que produzam o grafo de pares alcançáveis apropriado. Duplicar variáveis de atribuição ou reimplementar matching não cria, por si só, uma formulação forte. [E09, E26]

**3. Cobertura é muito útil, mas não suficiente em geral.** O núcleo pode produzir bons limites e até resolver estruturalmente SC, mas suas instalações ótimas podem falhar na compatibilidade dos pares. Γ mede essa perda relativamente ao núcleo escolhido; mudar o núcleo muda Γ. [E07, E13, E23–E24]

**4. Γ positivo, platô e gap de LP são fenômenos diferentes.** TR tem instalações ótimas inviáveis sem perda de valor do núcleo; SC-GF2 tem gap grande no LP de cobertura, mas núcleo inteiro igual a OPT; HB/BP têm perda de compatibilidade inteira do núcleo; Sec59 deixa residual mesmo no LP de F-CC. Uma única métrica de gap não separa esses mecanismos. [E11, E13, E15, E23]

**5. Conectividade é por infraestrutura utilizada, não global.** A solução pode possuir várias componentes em H[C], cada uma atendendo um grupo balanceado, além de pares diretos. Isso dá a F-CC e limita quais cortes baseados em “desconexão” são válidos. [E09]

**6. Os terminais podem criar atalhos que destroem a dificuldade pretendida.** HB admite usar um destino direto como hub com poucas estações. Gerar instâncias “difíceis” ignorando essa possibilidade produz uma variante artificial ou uma família fácil. [E23]

**7. A mesma estrutura combinatória pode ser fácil em uma representação e cara em outra.** Em SC-GF2, o IP do núcleo prova na raiz enquanto o processamento dos modelos com fluxo consome o orçamento ainda na raiz. Isso é um fenômeno de formulação/solver, não prova de que o Set Cover subjacente seja trivial em geral. [E24]

**8. Algoritmo publicado não substitui auditoria de semântica.** R11 e o caso de relé indevido em S∩T da construção literal discutida no overlap reforçam a necessidade de testar endpoints, permanência e contagem de arestas. Não autorizam desconsiderar a literatura, que continua sendo a referência de novidade e complexidade. [E20, E26]

## 13. Perguntas científicas ainda abertas

| Prioridade / pergunta precisa | Por que continua aberta e evidência existente | Potencial | Custo / dependências | Critério de parada |
|---|---|---|---|---|
| **Q1. Quanto do ganho de F-CC pode ser obtido como limite certificado de custo controlado?** | GF1 prova ganho pequeno, mas enumeração explode; não há pricing/projeção medidos | Formulação e algoritmo de limites, possível contribuição principal | Médio inicialmente; alto se houver árvore. Depende de P1/P2/P7 fechados e controle correto | Não abrir árvore se o bound não puder ser certificado ou seu custo consumir o ganho nas duas escalas escolhidas |
| **Q2. Cortes existentes e configurações são complementares de forma útil?** | SharedTerminal e HB já refutam dominância total entre os controles; combinação não medida | Definição de um referencial mais forte e ablação limpa | Baixo; prova de validade e pequenos modelos completos | Se só recuperar o máximo conhecido sem ganho útil, manter como controle e encerrar como contribuição autônoma |
| **Q3. Trios acrescentam informação útil além de F-CC reforçada, especialmente quando Γ>0?** | Proposta analítica disponível fora da branch; nenhum experimento; exemplos estritos conhecidos têm Γ=0 | Fortalecimento local e eventual família projetada de desigualdades | Baixo/médio com caps; depende de definição única, normalização e validação all-C | Pausar expansão se o lote discriminante não mostrar incremento relevante; preservar teorema de separação como resultado menor |
| **Q4. Que testemunho explica e generaliza a perda de compatibilidade do núcleo?** | R7 oferece pools, mas H-desc não discrimina e a métrica de cobertura precisa correção | Cortes que eliminem classes, em vez de reapresentar o mesmo no-good | Baixo para reanálise; médio para derivação. Depende de Q1/Q2 como controles | Máximo de duas ou três tentativas com prova; parar se apenas reproduzirem cortes existentes ou removerem pontos isolados |
| **Q5. O ganho de limite sobrevive ao custo em famílias não triviais?** | HB fácil para MIP; BP de piloto falhou no critério; Sec59 residual; benchmark tem D/A reais | Evidência algorítmica publicável | Médio, depois de Q1–Q4; orçamento global e partição intacta | Sem melhora em desenvolvimento em dois níveis/tipos independentes, não promover à avaliação |
| **Q6. Qual parte das divergências de classes especiais admite correção provada simples?** | R11 tem mínimos fortes; não fornece algoritmo corrigido | Nota teórica/certificador independente | Baixo para delimitar; potencialmente alto para resolver. Depende de conferir versões e IJCAI árvores | Se exige uma nova teoria ampla ou repete resultado conhecido sem benefício, preservar auditoria e pausar |
| **Q7. Quais parâmetros predizem a dificuldade relevante?** | Há associação com UB/m e medidas de G, mas pouca análise de H e testemunhos | Benchmark científico mais explicativo | Baixo para dados existentes; novas famílias apenas depois da hipótese | Se parâmetro não separa regimes controlados ou só recodifica tamanho/gap do solver, não criar método FPT com base nele |

Q1 é a pergunta principal. Q2 e Q3 são testes curtos que evitam investir no modelo errado; Q4 deve orientar a escolha da representação. Q5 é a confirmação algorítmica, não a primeira experiência. Q6 é uma oportunidade paralela. Q7 serve às demais, sem se tornar um inventário de parâmetros sem hipótese.

### Adequação do benchmark para essas perguntas

Nos 70 casos unitários, os dados atuais cobrem $n=50\ldots5699$, $m=2\ldots1142$, $r=1\ldots71$ e densidade de alcance de 0,00129 a 0,73936. Há 23 casos com r=1 e cinco com sobreposição, de aproximadamente 10%–12%. Esses números foram recalculados do manifesto, separando os cinco legados, alguns dos quais usam pesos originais mas têm $A_r=E$. [E06]

Há variedade de tamanho e topologia suficiente para **confirmar um método que já passou pelos testes estruturais**. Não há variedade controlada suficiente para atribuir causalmente os ganhos a trios, largura, simetria ou deficiência coletiva. A distribuição desenvolvimento/avaliação por origem também é desequilibrada: MAPF tem só um grafo de origem em desenvolvimento; SteinLib-i ficou inteiramente em avaliação. Isso não deve ser “corrigido” após observar resultados movendo instâncias. [E06, E30]

As lacunas relevantes são:

- **Microinstâncias com Γ>0 e residual após F-CC.** HB/BP fechados não discriminam trios; Sec59 é um ponto de partida, não uma família suficiente.
- **Sobreposição controlada mais ampla.** As cinco variantes rho são poucas e têm níveis próximos. São necessários casos de permanência, troca e relé que testem o mecanismo proposto.
- **Contrafactuais estruturais.** Pares com mesmo porte e autonomia, mas graus distintos de compatibilidade, sem depender apenas do tempo observado do solver.
- **Topologia de H.** A largura de G ou o tamanho do arquivo não representa necessariamente a complexidade da enumeração/pricing em $H=G^r$. A potência do grafo pode destruir separadores pequenos.
- **Distinção entre dificuldade de raiz e de árvore.** SC desafia o processamento na raiz; BP negativo pode desafiar prova inteira; confundir ambos leva à técnica errada.

Continuar criando sintéticos é justificável **em pequena quantidade, orientada por Q3/Q4**, não como objetivo de produzir timeouts. Um candidato deve variar, por exemplo, a deficiência e a sobreposição dos conjuntos de terminais atendidos por alternativas de infraestrutura, ter controle sem essa obstrução e permitir certificado independente em escala pequena. É indispensável verificar se instalações em origens/destinos ou junções entre gadgets oferecem atalhos.

Não recomendo simplesmente concatenar HB, ampliar BP, densificar aleatoriamente ou aumentar m. A replicação de gadgets fáceis pode só aumentar tamanho. Uma combinação de obstruções de ordem maior que três pode ser um bom **teste de limitação** de F-C3, mas deve vir acompanhada da prova de que o mecanismo sobrevive à transformação em MIN-STATION all-V.

Benchmarks externos já fornecem topologias úteis: PACE, SteinLib, MAPF e redes urbanas estão no projeto. Novas importações só se justificam por uma característica ausente, como separadores controlados em H ou mistura entre gargalos e alto compartilhamento. A atribuição de S/T e r continua sendo parte do gerador de MIN-STATION e deve ser documentada; dificuldade no problema de origem não é certificado de dificuldade aqui.

## 14. Auditoria do plano R1–R13

| Item | Classificação | Justificativa e decisão recomendada |
|---|---|---|
| **R1 — saneamento** | `DONE` | Renomeações/contexto feitos. As novas contradições da seção 15 são manutenção pós-resultados, não motivo para reabrir toda a fase |
| **R2 — partição e versão** | `DONE` | Partição por origem e integração de SC feitas; tag continua pendência administrativa explícita. Não refazer a divisão após conhecer resultados |
| **R3 — pré-registro da baseline** | `DONE` | Contrato e calibração executados. AV-1…AV-4 ainda pedem definição/aceitação prospectiva no próximo plano |
| **R4 — baseline oficial** | `DONE` | CSV e tabela disponíveis. Separar referência do protocolo de melhor conhecimento histórico; não apagar UB histórico melhor |
| **R5 — pré-registro diagnóstico** | `DONE` | Executado; preservar regra original |
| **R6 — Γ e teste primal** | `DONE` | Resultados e G1 sustentados. Interpretar falha de MIPFocus com seu alcance limitado |
| **R7 — anatomia do platô** | `SPLIT` | Coleta concluída; correção da cobertura e diagnóstico causal específico ainda necessários. Integrar essa segunda parte a N1, sem repetir a coleta grande |
| **R8 — geração de colunas F-CC** | `REORDER` | GF1 libera explorar. Primeiro formalizar pricing, bound global e controles F-CC+cortes; depois protótipo de raiz limitado. Não depende de F-C3 completa |
| **R9 — branch-and-price / price-and-branch** | `BLOCKED` | Precisa de R8 útil e certificado. Resolver IP sobre colunas geradas só na raiz não é, por si, algoritmo exato de branch-and-price |
| **R10 — desigualdades de compatibilidade** | `MERGE` | Mesma pergunta científica de R8: extrair informação útil de compatibilidade. Investigar projeção/corte como alternativa econômica, não duas grandes frentes concorrentes. Substituir dependência literal dos certificadores R11 |
| **R11 — classes especiais** | `DONE` | Fechada com `CONFIRMED DIVERGENCE`. **Substituir sua função de suporte exato**, sem reexecutar a spec até obter acordo. Correção teórica futura é escopo novo e delimitado |
| **R12 — primal/matheurística** | `BLOCKED` | Nenhum sinal novo para abrir agora. Só reordenar se a próxima medição mostrar LB próximo do ótimo e UB comprovadamente melhorável |
| **R13 — confirmação** | `KEEP` | Preservar como fase condicional após gate de desenvolvimento, com partição por origem e custo total. Ainda não executar |

**Linha F:** F1/F2 da F-CC têm definição útil e pequenas correções de prova; F3/GF1 da F-CC estão concluídos. F-C3 precisa de **fechamento matemático e teste incremental próprios**, sem confundir isso com reabrir GF1 para aprovar novamente a F-CC.

A principal mudança no plano é retirar o encadeamento automático “GF1/G1 positivos → dois métodos grandes → certificadores especializados → benchmark”. A sequência recomendada começa pela pergunta de informação incremental, escolhe uma representação e só promove a implementação quando força e custo justificarem.

## 15. Contradições/documentação a atualizar

Esta é uma lista de correções futuras; nenhum arquivo foi alterado nesta revisão. Documentos históricos devem receber ponteiros ou notas datadas, preservando o texto e os pré-registros anteriores.

| Local | Divergência encontrada | Atualização necessária |
|---|---|---|
| Spec A, rastreabilidade | Tabela final ainda marca requisitos como `Pending`, apesar de R1–R4 executados | Atualizar estado e ligar aos artefatos; manter tag/AV como pendências específicas |
| Spec B, “Current State” | Código/LP aparecem como não iniciados; checkboxes podem sugerir medição de ambas as formulações | Separar F-CC concluída de F-C3 aberta; citar F3/GF1 |
| Spec C, estado inicial e rodapé | Estado inicial anterior às execuções; rodapé usa “BLOCKED” e depois “released” para R8/R9 | Datar fotografia histórica e explicitar que R9 ainda depende de R8 |
| Spec D, relações/futuro R8/R10 | Mesmo após `CONFIRMED DIVERGENCE`, diz que os certificadores R11 poderão/devem validar os métodos | Substituir a dependência; preservar os algoritmos literais como objetos auditados, não fontes de OPT |
| Plano R1–R13 | Mantém resultados/gates como futuros e expectativas de BP/HB anteriores a F3 | Inserir decisões posteriores; BP pequeno ganhou com F-CC, HB foi fechado no LP |
| Backlog, tabela de pausadas | “Geração de colunas” ainda aparece genericamente pausada, com argumento de outro pricing | Distinguir colunas antigas de conjuntos completos de estações da F-CC cujo GF1 passou |
| GF1, seção SC | Diz “não há ganho em SC” após exclusão do braço por cap | Trocar a leitura atual por “não medido”; registrar limite do controle sem alterar o resultado PASS |
| Provas P2/P7 | Ativação terminal e descarte de massa vazia não estão completamente justificados | Corrigir os argumentos descritos na seção 8 |
| Provas P3/P4 | Rótulo `COMPUTATIONALLY VERIFIED`, com nota de que F3 não testa violação dos cortes | Alinhar rótulo à prova efetiva ou registrar teste específico; comparação de objetivos não verifica inclusão de politopos |
| F-C3 atual, §2 | $d_{ss}=0$ confunde distância com variável | Manter distância zero e atendimento direto livre, inclusive permanência com variável 1 |
| F-C3 / spec B / plano | Fonte externa e redes permanecem ausentes; há material consolidado fora da branch | Importação/revisão explícita com SOURCE/DERIVED/NEW; não declarar implementação concluída |
| Regra “ganho em SC = erro” | Mistura ganho sobre LP F-CC com ganho sobre núcleo IP | Definir o comparador no próximo pré-registro; preservar o antigo |
| R7, relatório/runner | Frequência de Z tratada como cobertura de soluções; contagem “sem par” é grau zero | Nota de auditoria, medida cruzada correta e nomes precisos; cc9 máximo 27, não 21 |
| G1/R7, interpretação | H-desc usada como identificação causal forte | Qualificar como consistência da caracterização; formular hipótese discriminante para a etapa seguinte |
| README | Diretório `alternative-formulations` tratado genericamente como histórico | Distinguir modelos antigos da F-CC atual |
| `direcoes`, ranking A2 e D-5 | Recomendação de A2 anterior a E12 e pausa genérica de colunas | Atualizar ponteiro para encerramento de CBI e novo escopo F-CC, sem reescrever experimentos |
| `overlap`, classes especiais | Fotografia de 03/10 diz caminhos/ciclos nunca implementados | Acrescentar R11 e seus resultados; não editar retroativamente a auditoria antiga |
| Validação da base e contexto | Trechos históricos de balanço separado, “prova a justificar” ou algoritmo não usado sobrevivem a T5/R11 | Deixar inequívoco qual seção é vigente, quais são histórico e onde está a prova fechada |
| Referenciais hc9u | Baseline atual tem UB 41; plano usa histórico UB 38 | Conservar ambos com protocolo/fonte; corrida pior não revoga solução histórica validável de custo 38 |
| Proveniência experimental | Baseline inteira e P/E usam commit `-dirty`; F3 tem esquema mais enxuto | Arquivar snapshot/patch ou hash completo do código nas futuras rodadas; não tratar só o hash do gerador de cortes como snapshot de todo o experimento |

Há uma dívida mais substantiva do que edição: a tabela de estados não deve marcar **inferência causal** como fechada apenas porque a coleta correspondente terminou. Essa distinção evitará que uma spec operacionalmente completa se transforme em premissa científica mais forte do que os dados.

## 16. Opções de continuidade avaliadas

| Direção | Decisão | Justificativa específica ao MIN-STATION |
|---|---|---|
| Finalizar F-C3 | **FAZER AGORA**, com escopo limitado à definição/revisão e teste pequeno | O material externo permite fechar a definição sem uma reconstrução extensa. Falta demonstrar valor adicional no regime que motivou a pesquisa; não é autorização para versão em escala |
| Novas formulações de compatibilidade | **CONDICIONAL** | Primeiro localizar uma obstrução que F-CC reforçada não represente. Formular novamente sem esse alvo pode apenas deslocar o custo |
| Aprofundar F-CC | **FAZER AGORA** | GF1 fornece evidência direta. A pergunta passa de “é mais forte?” para “qual parte dessa força pode ser obtida com custo certificado aceitável?” |
| Cortes de compatibilidade | **FAZER AGORA**, como derivação focalizada | Os pools e a comparação F-CC/núcleo podem revelar obstruções reutilizáveis. Exigir validade para todo C e diferença em relação a C4/C5/C6; não repetir um corte pontual com outro nome |
| Matching | **FAZER AGORA como instrumento**, não como contribuição autônoma | Extrair déficit de matching e testemunhos de Hall é a forma correta de examinar B_C. O algoritmo de matching e a caracterização já pertencem à literatura |
| Consistência de trios em escala | **CONDICIONAL** | Só se o teste incremental superar F-CC+cortes em casos relevantes. A ordem três pode resolver obstruções locais e falhar em ciclos maiores |
| Estrutura de S∩T | **FAZER AGORA como requisito transversal** | Permanência/troca/relé afetam validade de cortes e pricing. Uma linha autônoma de preprocessing depende de novas propriedades provadas, não da hipótese de cancelamento |
| Novos certificadores | **CONDICIONAL** | R11 deixou uma lacuna de suporte, mas não é preciso preenchê-la com algoritmo universal antes da pesquisa de limites. Priorizar certificados explícitos para famílias usadas |
| Árvores | **ADIAR como frente principal** | O IJCAI já fornece resultado polinomial. Implementação auditada pode ser útil futuramente, sobretudo com r>1 e sobreposição, mas não é novidade por si |
| Classes especiais | **CONDICIONAL** | Boa fonte de prova, contraexemplo ou algoritmo corrigido se uma questão precisa surgir de R11; evitar inventário de classes por disponibilidade |
| Novos benchmarks sintéticos | **CONDICIONAL, dentro do diagnóstico** | Justificados para separar Γ, gap de LP e obstruções de ordem maior; devem possuir controles e certificados pequenos. Não ampliar o benchmark por volume |
| Instâncias difíceis | **CONDICIONAL** | Já há D/A abertas. Uma nova instância deve pressionar a informação que o método explora, e não apenas aumentar memória ou tempo de montagem |
| Parâmetros estruturais | **FAZER AGORA na análise descritiva; método FPT ADIAR** | Medir H, deficiências e grupos alcançáveis pode orientar pricing/cortes. Treewidth de G pequeno não basta para H; m grande limita uso direto do FPT em agentes |
| Formulações mais fortes | **CONDICIONAL à força incremental e custo** | F-CC dá sinal positivo; uma formulação exponencial mais forte pode ser só referência teórica. Comparar sempre com os cortes existentes e com núcleo IP |
| Desagregação all-V completa | **DESCARTAR NO FORMATO ATUAL como próximo método** | Os pequenos ganhos conhecidos não justificam multiplicar fluxo por origem. Manter como controle diagnóstico; reconsiderar somente uma compressão ligada a uma obstrução concreta |
| Decomposição | **CONDICIONAL e específica** | Geração de colunas de configurações pode calcular o novo LP; Benders clássico da mesma base não o fortalece. Decomposição espacial exige interface que preserve carga, papéis de terminal e matching |
| Branch-and-price completo | **ADIAR** | O pricing, o limite global e a utilidade na raiz ainda precisam ser demonstrados. A árvore acrescentaria decisões técnicas antes de responder à pergunta principal |
| Nova frente primal | **ADIAR** | O teste disponível não a favoreceu. Reabrir com evidência de que melhorar UB, e não apenas representar melhor compatibilidade, é a próxima intervenção discriminante |

As classificações “fazer agora” aqui se referem à próxima fase recomendada. Esta entrega permanece exclusivamente analítica.

## 17. Plano recomendado da próxima fase

O plano tem **um eixo principal — informação de compatibilidade e custo de obtê-la — e uma oportunidade teórica paralela, condicional**. Não recomendo abrir simultaneamente novas specs de F-C3 em escala, R8, R9, R10, árvores e novos benchmarks.

### N1 — Identificar a informação incremental que vale perseguir

**Pergunta científica.** O que falta ao melhor referencial atual: coerência de uma infraestrutura conectada, cortes de cobertura/Hall que a F-CC não implica, ou consistência conjunta entre configurações?

**Hipótese.** F-CC com os cortes existentes captura uma parte substancial do ganho necessário; trios acrescentam valor somente em determinados padrões de marginais. As obstruções observadas não devem ser todas chamadas de “desconexão”.

**Motivação.** GF1 positivo, SharedTerminal abaixo de COMP, Sec59 ainda aberto no LP, F-C3 não medida e R7 pouco discriminante. [E09–E17, E29]

**Trabalho necessário.**

1. Corrigir a exposição de P2/P7; integrar/revisar a definição externa da F-C3 com procedência explícita; conferir d_ss e distinguir a formulação F-C3 da família de cortes chamada C3 no código.
2. Reanalisar o pool já existente: incidência corte×instalação, tamanho do matching, conjuntos deficientes de Hall, alcance individual e grupos que poderiam ser atendidos por cada componente. Não coletar outro grande pool para substituir o anterior.
3. Preparar um único diagnóstico pequeno com os controles de F3 pertinentes, incluindo SharedTerminal, HB, BP, Sec59, TR e controle SC que caiba. Comparar **LP base, LP COMP, núcleo IP, LP F-CC, LP F-CC+cortes existentes, LP F-C3 e LP F-C3+os mesmos cortes**, além de OPT certificado. As ablações com os mesmos cortes impedem atribuir aos trios um ganho que veio de C4.
4. Se os exemplos existentes não discriminarem os trios, permitir **uma busca limitada a até 12 pares de microinstâncias candidatas**, com contrafactual de estrutura e certificado por enumeração. Para novos casos, começar em n≤10; os exemplos existentes maiores podem usar os certificados já registrados e respeitar o cap de enumeração de W. A busca não é exaustiva sobre todos os grafos de dez vértices.

Antes de medir a nova F-C3, sua implementação futura deverá passar pelo teste **para cada instalação C**, comparando viabilidade com `viavel`, incluindo S∩T e permanência. Igualar apenas o ótimo não basta. Todos os W necessários ao LP devem ser enumerados ou o caso deve ser explicitamente excluído. Valores analíticos do material externo entram como previsões, não como resultados medidos.

**Dependências.** Baseline, F-CC e validador atuais. Não depende de R11 corrigida nem de geração de colunas.

**Evidência esperada.** Uma matriz curta de inclusões, contraexemplos e ablações; pelo menos um testemunho completo do mecanismo escolhido. Para instâncias certificadas, registrar separadamente:

\[
B_0=\max\{z_{COMP}^{LP},z_{core}^{IP}\},\quad
\Delta_{FCC}=z_{FCC}-B_0,\quad
\Delta_{trio}=z_{FCC+C3+K}-z_{FCC+K},
\]

onde K são exatamente os cortes estáticos comuns. Na última expressão, FCC+C3 significa a F-C3 definida e validada, sem criar uma terceira variante implícita. Valores negativos de Δ_FCC são possíveis, como SharedTerminal; não truncá-los para esconder complementaridade.

**Critério de sucesso.** Definições e validade sem ambiguidade; um mecanismo sustentado por prova/testemunho e por ganho incremental em pelo menos dois casos de estruturas distintas. Para promover os trios à etapa de escala, exigir que o ganho não se restrinja aos exemplos em que o núcleo IP já resolve tudo. Esta é uma proposta de critério prospectivo, a congelar na spec futura.

**Critério de parada.** Uma rodada definida, sem acrescentar instâncias após ver o resultado para “salvar” a hipótese. Se a busca não produzir incremento relevante dos trios, pausar F-C3 como método e preservar seus resultados teóricos. Se o mecanismo só reproduzir C4/C5 ou cortes individuais, encerrar essa tentativa de desigualdade.

**Resultado positivo leva a:** N2 com a representação mínima que captura o ganho.  
**Resultado negativo leva a:** F-CC+cortes permanece como referência; trios/cortes novos sem ganho saem da frente ativa. Se nem houver alvo incremental além dos controles nos casos relevantes, revisar a pergunta antes de qualquer implementação maior.

### N2 — Obter o limite de compatibilidade sem enumerar toda a formulação

**Pergunta científica.** É possível recuperar o ganho de N1 com um limite global certificado cujo custo justifique seu uso?

**Hipótese.** Apenas uma parte das configurações ou uma família projetada de restrições será necessária para obter uma parcela útil da força, embora certificar essa afirmação exija tratar o restante implicitamente.

**Motivação.** O limite de W já é atingido em F3. O ganho de bound torna relevante buscar uma representação econômica; a mera existência de um modelo exato não resolve seu custo. [E10–E12]

**Trabalho necessário.** Escolher **uma** via inicial, segundo N1:

- se a obstrução admitir uma desigualdade de validade geral e separação tratável, desenvolver essa família com prova e validação independente;
- se a informação exigir configurações inteiras, formalizar o dual e o pricing da F-CC com os cortes escolhidos, incluindo elegibilidade de terminais, equilíbrio de I/J, conectividade em H e ligações de estações.

No segundo caso, começar por geração de colunas **somente na raiz**. Pricing heurístico pode encontrar colunas, mas não certificar ausência de colunas melhorantes. Pricing interrompido só permite anunciar LB se seu limite global sustentar uma correção dual provada. Nas instâncias pequenas, o resultado deve concordar com a enumeração completa de N1.

Não fixar matching de antemão para tornar o pricing mais fácil: isso altera o problema. Não substituir grupos balanceados por cobertura independente de origens e destinos sem demonstrar equivalência. Tampouco chamar um bound lagrangeano do novo master de reabertura da velha Lagrangeana da baseline: são objetos diferentes, cuja força e validade devem ser derivadas.

**Dependências.** N1 para escolher e validar a informação; P1/P2/P7; nenhuma dependência de branch-and-price ou de algoritmo universal para árvores.

**Evidência esperada.** Curva de LB certificado contra trabalho/tempo total; decomposição do custo entre montagem, master e pricing/separação; número de colunas/cortes; concordância com o LP completo nos pequenos; resultado em dois níveis de tamanho de pelo menos duas estruturas escolhidas antes da execução.

**Critério de sucesso.** Certificação correta em todos os controles e ganho de LB sobre o referencial comparável em pelo menos dois tipos, reproduzido em dois níveis. Quando o LP completo for conhecido, exigir a recuperação de uma fração pré-definida de seu ganho — sugestão inicial: pelo menos 50% do incremento positivo sobre B_0 — dentro do orçamento total reservado. Registrar o valor contínuo e seu arredondamento inteiro válido.

**Critério de parada.** Parar a via escolhida se não produzir limite certificado, se o pricing/separação consumir o orçamento sem ganho útil ou se o ganho desaparecer nas duas escalas. No máximo uma mudança de representação motivada pelo diagnóstico, dentro do limite geral de duas ou três tentativas do programa; não alternar indefinidamente entre técnicas.

**Resultado positivo leva a:** N3.  
**Resultado negativo leva a:** preservar F-CC como formulação/diagnóstico e publicar o limite de escalabilidade observado; uma via projetada só abre se N1 lhe der sustentação nova. Não avançar à árvore para compensar uma raiz sem benefício.

### N3 — Demonstrar utilidade algorítmica e confirmar fora do desenvolvimento

**Pergunta científica.** O limite novo melhora a resolução do MIN-STATION sob custo comparável, além dos pequenos instrumentos escolhidos para construí-lo?

**Hipótese.** O ganho de compatibilidade reduz o esforço de prova ou o gap final nas famílias que apresentam o mecanismo, sem regressões generalizadas que anulem o benefício.

**Motivação.** GF1 mede força; a pesquisa precisa transformar isso em evidência de método. O benchmark possui D/A abertas e protocolos preparados. [E07, E30]

**Trabalho necessário.** Primeiro executar desenvolvimento com orçamento total, três seeds quando houver aleatoriedade de solver relevante, dois níveis de tamanho e análise por família/grafo de origem. Comparar com COMP e com o referencial de núcleo pertinente, contabilizando o custo de qualquer portfólio. Incluir SC como controle de mecanismo e registrar regressões, não apenas vitórias.

Somente depois desse gate decidir se vale integrar o mecanismo à busca inteira. Branch-and-price exige pricing compatível com as decisões de branching e bound válido em todos os nós relevantes. Price-and-branch sobre colunas da raiz pode ser heurística primal útil, mas não certifica o ótimo global sem argumento adicional.

Após congelar método e parâmetros, fazer a confirmação equivalente a R13 na partição de avaliação. A consulta prévia a resultados da baseline não invalida o conjunto como comparação futura, mas limita uma narrativa de avaliação totalmente inédita; não usar as respostas do método em avaliação para revisá-lo e depois reapresentá-las como confirmação.

**Dependências.** N2 passou. Critérios AV e tratamento de legados/duplicatas definidos prospectivamente. Desenvolvimento antes da confirmação.

**Evidência esperada.** LB, UB, gap, status, nós, tempo até incumbente/prova, trabalho e custos auxiliares. Resultados agregados por origem, com diferenças por seed e contagem explícita de exclusões/caps.

**Critério de sucesso.** Passar um critério de avanço previamente fixado, não escolhido entre métricas após observar resultados: por exemplo, fechar pelo menos três D/A em duas famílias, ou reduzir a mediana do gap em pelo menos 25% em duas famílias com reprodução nas três seeds. Esses limiares retomam o espírito dos AV atuais; devem ser fixados antes da corrida, pois no plano ainda estão pendentes. Confirmar o sinal em avaliação, sem tuning adicional.

**Critério de parada.** Não promover se o ganho só ocorrer em um gadget, em uma seed, sobre uma base deliberadamente fraca, ou se o custo total eliminar a vantagem. Falha em avaliação é resultado negativo e deve permanecer visível.

**Resultado positivo leva a:** contribuição algorítmica e redação de artigo com escopo demonstrado.  
**Resultado negativo leva a:** contribuição teórica/experimental delimitada, sem insistência automática em mais tempo, mais parâmetros ou novos benchmarks favoráveis.

### N4 — Delimitar a oportunidade teórica aberta por R11

**Pergunta científica.** A divergência literal decorre de uma correção local demonstrável, de uma lacuna de especificação ou de uma propriedade gulosa que exige outra prova/algoritmo?

**Hipótese.** Há resultados pequenos e úteis a obter da auditoria, mas uma solução nova de classes especiais pode ser mais custosa ou menos inédita do que parece diante do Teorema 9 do IJCAI.

**Motivação.** Contraexemplos mínimos e SP-R2, com referências consistentes. [E18–E22, E26]

**Trabalho necessário.** Conferir a versão final publicada, distinguir cada interpretação, e escolher no máximo um alvo: por exemplo, a contagem/seleção em caminhos ou a interface de demanda e energia de uma radial. Propor correção somente com especificação completa e prova; comparar o alvo com o algoritmo conhecido de árvores. Usar enumeração e contraexemplos R11 para tentar refutar a correção antes de promovê-la a certificador.

**Dependências.** Não bloqueia N1–N3. Antes de comunicação pública, revisão humana e procedimento de contato apropriado. Nenhum contato foi feito nesta análise.

**Evidência esperada.** Teorema/correção com condições explícitas ou nota técnica que demonstre por que o texto atual não determina um procedimento único; corpus mínimo reproduzível.

**Critério de sucesso.** Uma conclusão nova, precisamente limitada e comprovada, ou um certificador independente que tenha utilidade concreta para o programa. Simples concordância numa nova bateria não é prova geral.

**Critério de parada.** Se o alvo exigir uma nova frente ampla, repetir resultado já coberto no IJCAI sem vantagem ou depender de hipóteses fora de Das, preservar a auditoria e pausar. Não transformar R11 numa busca indefinida por uma variante que concorde com o solver.

**Resultado positivo leva a:** nota teórica ou ferramenta de validação, com escopo próprio.  
**Resultado negativo leva a:** manter R11 como resultado negativo relevante e usar os certificados já confiáveis.

## 18. Prioridades

### Prioridade 1 — fazer agora

1. **N1: fechar a comparação matemática e o diagnóstico incremental**, incluindo revisão limitada da F-C3, complementaridade com cortes e reanálise correta de R7.
2. **N2: preparar uma única via certificada para o limite de compatibilidade**; sua escolha empírica e implementação seguem a evidência de N1. Começar pela raiz, sem árvore completa.

### Prioridade 2 — depende dos resultados

- **N3:** desempenho em desenvolvimento e confirmação apenas depois de N2.
- **N4:** revisão teórica de um alvo de R11, se houver espaço para contribuição delimitada e revisão humana; não é dependência obrigatória do eixo principal.
- Sintéticos adicionais e trios em escala somente se responderem a uma lacuna identificada em N1.

### Prioridade 3 — manter no radar

- Certificador auditado para árvores; exploração de largura modular, cobertura por vértices ou outros parâmetros somente se forem pequenos nos grafos relevantes.
- Decomposição por regiões com interface de compatibilidade rigorosa.
- Nova linha primal se surgirem instâncias com LB já forte e evidência de UB melhorável.

### Não fazer agora

Branch-and-price completo, nova campanha ampla de F-C3, reabrir CBI/BC-Y genérico, ajustar a mesma Lagrangeana, usar Benders clássico como fortalecimento, ampliar BP/HB/TR sem hipótese nova, gerar instâncias só para obter timeout, ou executar benchmark-v1 inteiro antes de um resultado discriminante pequeno.

## 19. Riscos e critérios de parada

| Risco | Como evitar / quando parar |
|---|---|
| Alterar a baseline para favorecer o método | Preservar U/COMP e registrar novas formulações separadamente; qualquer diferença de semântica bloqueia a comparação |
| Confundir base, COMP, núcleo IP e LP F-CC | Nomear exatamente o objeto. Núcleo IP não é uma relaxação linear nem um UB do problema sem validação de C |
| Atribuir ganho de C4 aos trios | Mesmos cortes estáticos nos braços da ablação; comparação F-C3+K contra F-CC+K |
| Chamar LP de master restrito de limite inferior global | Exigir pricing completo ou correção dual provada; sem certificado, não emitir LB do MIN-STATION |
| Tratar price-and-branch como método exato | Separar solução restrita de certificado global; sem pricing/limite adequado na árvore, não afirmar otimalidade |
| Igualar ótimo e concluir equivalência | Teste por instalação C e prova nos dois sentidos; incluir soluções não ótimas, permanência e terminais como relés |
| Interpretar H-desc como causa descoberta | Extrair testemunho que discrimine mecanismos; não usar número de componentes como corte automático |
| Comparar custo apenas do master com tempo integral de COMP | Contabilizar montagem, distâncias, enumeração, pricing, separação e validação; limitar trabalho/tempo do procedimento completo |
| Interpretar WorkLimit como igualdade física universal | Mantê-lo como controle reproduzível no mesmo ambiente; registrar também tempo, memória e fases fora do solver. O trabalho de subsolves deve entrar no orçamento global |
| Comparar um método de uma seed com melhor de nove execuções sem esclarecer | Separar comparação pareada de envelope LB*/UB*. Se usar portfólio, cobrar seu orçamento; se usar envelope como alvo de pesquisa, declarar que não é um algoritmo unitário |
| Ignorar soluções históricas melhores | Separar recorde validado de referência do protocolo. Caso hc9u: UB 41 da corrida não revoga UB 38 histórico |
| Vazamento por variantes ou legados | Agrupar por grafo de origem e verificar duplicatas/alcance equivalente. Legados não são novas réplicas independentes das variantes benchmark |
| Confundir três seeds com três instâncias | Unidade científica é o grafo/construção; seeds medem variabilidade do solver ou do gerador, explicitamente distinguidas |
| Escolher sintéticos favoráveis após ver os métodos | Hipótese, gerador, controles, caps e regra de promoção antes da medição; registrar exclusões e fracassos |
| Interpretar exclusão como resultado negativo | SC de F3 não medido; gêmeos de E sem certificado. Nenhum dos dois mostra ausência de ganho |
| Aumentar tamanho sem manter mecanismo | Certificar pequenos e demonstrar que o mecanismo sobrevive à escala; verificar atalhos em terminais e entre gadgets |
| Apoiar uma prova em algoritmo literal refutado | Usar definição e referências confiáveis; R11 literal fica como objeto de auditoria, não oráculo |
| Reivindicar novidade de matching, G^r, BP, SC ou árvores | Citar IJCAI e classificar adaptação/implementação/experimento; novidades precisam estar na formulação ou em propriedade adicional demonstrada |
| Snapshot `-dirty` incompleto | Futuras corridas com commit identificável e patch/hash de código inteiro; não rerodar tudo sem uma dúvida concreta de reprodutibilidade |
| Trocar critérios depois dos números | Manter GF1/G1/P/E e pré-registros intactos; novas perguntas recebem novo contrato e nova interpretação |
| Manter uma linha indefinidamente por possibilidade teórica | Aplicar caps de N1, uma via inicial em N2 e gate antes de N3; resultado negativo suficiente encerra a versão da hipótese |

Uma medição adicional só deve entrar se puder mudar uma decisão. Verificações de corretude são obrigatórias quando muda a matemática; baterias maiores são condicionais a uma pergunta ainda discriminável.

## 20. Potencial de contribuição científica

### Resultado teórico

**Sustentado:** equivalência da formulação U ao problema de Das, inclusive S∩T; caracterização/formulação F-CC; análise da fraqueza de relaxações e limites das decomposições estudadas. A prova da U sustenta fidelidade, mas sua estrutura de fluxo é próxima de técnicas conhecidas. Matching e potência do grafo devem ser atribuídos ao trabalho anterior. [E03, E09, E26, E28]

**Candidato mais interessante:** propriedades poliédricas da F-CC, complementaridade com cortes de Hall, separações estritas por famílias e condições sob as quais configurações ou consistência local fecham o gap. A proposta externa de F-C3 contém material analítico a revisar; não basta chamá-lo de novo sem comparação com formulações de configurações e relaxações de consistência já conhecidas.

### Resultado algorítmico

**Ainda não há um novo método geral vencedor demonstrado.** F-CC foi avaliada pela força do LP e utilizada como referência binária, não como solução em escala do benchmark. O resultado que poderia sustentar essa contribuição é N2/N3: limites certificados úteis com pricing ou separação de custo controlado, e benefício reproduzível.

Uma correção de algoritmo de classe especial pode constituir outra contribuição, mas precisa de prova e delimitação de novidade frente ao resultado de árvores. Não deve ser apresentada como consequência automática de encontrar um contraexemplo ao pseudocódigo.

### Resultado experimental

Há uma narrativa forte e coerente: **cobertura, compatibilidade e representação computacional produzem regimes diferentes**. SC-GF2, Γ, F3 e o platô de TR fornecem instrumentos concretos; a baseline oficial fornece casos não resolvidos e comparação atual. Uma publicação deve separar o que é prova, piloto, avaliação ampliada e histórico pré-protocolo. [E07, E11, E13, E15, E23–E24]

A contribuição de benchmark é plausível se acompanhada de conversões, proveniência, licenças, partições e certificados claros. Não se deve afirmar “primeiro benchmark existente” de modo universal a partir de uma busca dirigida limitada. O mesmo vale para “primeira PLI”: o levantamento sustenta ausência no conjunto revisado, não uma prova bibliográfica exaustiva. [E26, E30]

### Resultado negativo relevante

CBI sem ganho sobre o núcleo; C6 de primeiro salto insuficiente; BP/HB não promovidos pelos critérios originais; limites da desagregação; teste primal sem reprodução. Esses resultados têm valor porque eliminam hipóteses concretas e ajudam a explicar por que uma formulação exata ou um corte válido não se transforma automaticamente em método útil.

O negativo mais valioso é o que possui mecanismo: por exemplo, teto do Benders clássico no LP da base, ou o hub terminal de HB satisfazendo uma desigualdade de primeira camada sem resolver a compatibilidade restante. Repetir timeouts sem esse diagnóstico tem menos potencial científico.

### Infraestrutura/metodologia

Validador por bateria independente, regressões de terminais, contratos prospectivos, rastreabilidade de gates e conjuntos de contraexemplos são ativos do projeto. São pré-requisitos para confiar na pesquisa, e podem integrar um artefato reproduzível. Sozinhos, dificilmente substituem um resultado de otimização; combinados à comparação de formulações e mecanismos, fortalecem muito a contribuição.

### Correção ou divergência encontrada na literatura

R11 já sustenta uma afirmação técnica interna precisa: **a implementação literal dos pseudocódigos auditados de caminhos e ciclos diverge do ótimo certificado nos contraexemplos registrados; as leituras de spiders testadas não formam um certificador universal**. Isso pode originar comunicação técnica ou correção, após conferir a versão final e revisar as provas.

O registro oficial do trabalho de Das identifica a versão de periódico em *Discrete Applied Mathematics*, volume 381, páginas 129–136, de março de 2026, DOI [10.1016/j.dam.2025.11.020](https://doi.org/10.1016/j.dam.2025.11.020). A versão local usada em R11 é um preprint de 16 páginas; sua paginação e seu pseudocódigo precisam ser correlacionados à versão final antes de generalizar a comunicação externa. O IJCAI-26 está nos [anais oficiais, pp. 72–80](https://www.ijcai.org/proceedings/2026/9); Pereira & Ravelo consta nos [anais do ETC 2026](https://sol.sbc.org.br/index.php/etc/article/view/43666). A verificação bibliográfica não constitui, por si, uma auditoria integral de todas as versões finais.

O posicionamento mais defensável para o eixo principal é: **uma investigação exata e experimental de representações de cobertura e compatibilidade para MIN-STATION, com formulações equivalentes, limites comparados e mecanismos de dificuldade demonstrados**. A oportunidade de literatura pode ser um resultado separado, sem dominar artificialmente a narrativa de PLI.

## 21. Recomendação final

**Continuar a pesquisa de compatibilidade, com F-CC como principal referência de força, e reduzir a próxima fase a uma decisão de informação incremental seguida de uma decisão de custo.**

A evidência não recomenda voltar a testar técnicas genéricas. Tampouco recomenda saltar diretamente para F-C3 em escala ou branch-and-price completo. A F-CC já justificou investigação; agora precisa demonstrar que sua informação pode ser utilizada economicamente e que o ganho persiste fora dos pequenos exemplos.

O primeiro trabalho deve fechar três pontos conectados: **F-CC com os cortes existentes; valor adicional real dos trios; testemunhos de compatibilidade que expliquem o platô além da caracterização de viabilidade**. Essa etapa pode ser pequena, usar os artefatos existentes e encerrar hipóteses rapidamente. Só a representação que passar merece a etapa de limite certificado na raiz e depois a avaliação algorítmica.

R11 deve ser preservada como divergência confirmada e como oportunidade teórica delimitada. Sua função de certificador no plano precisa ser substituída; ela não deve bloquear toda a pesquisa nem ser “resolvida” por ajustes destinados apenas a obter acordo nos exemplos.

**A pergunta mais importante é se conseguimos capturar compatibilidade coletiva com um limite simultaneamente forte, certificado e economicamente útil. A menor sequência para descobrir isso é N1 → N2; N3 só se esses dois passos justificarem continuar.**

---

**Nota de rastreabilidade da reanálise.** Foram conferidas as contagens de `linha_base.csv` (411), `f3-fcc.csv` (16), `r6-gamma.csv` (61), `r6-primal.csv` (78), `r7-plato.csv` (610), `piloto_fase_p.csv` (108), `fase_e_sc.csv` (24) e `r11-certificadores.csv` (80). Em R7, cada Z distinto foi cruzado com todas as instalações inviáveis de seu próprio pool pela condição C∩Z=∅. Essa operação é reanálise dos dados publicados, não nova execução experimental. Todas as propostas de N1–N4 são prospectivas; não modificam os contratos anteriores.


[e01]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/CLAUDE.md
[research]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/RESEARCH.md
[overview]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/project-overview.md
[sources]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/source-map.md
[e02]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/context-ai/base-formulation.md
[baseline]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/baseline.py
[e03]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/validacao-formulacao-base.md
[e04]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/governance/open-questions.md
[e05]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/plans/backlog-continuacao.md
[plan]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/plans/plano-proxima-fase.md
[e06]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/instances/manifest.csv
[partition]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/regra-particao-origem.md
[e07]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/benchmark/linha_base.csv
[baseline-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-linha-de-base.md
[baseline-pre]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/linha-de-base-pre-registro.md
[e08]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/specs/proxima-fase-a-fundacao/spec.md
[e09]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/formulacao-fcc-configuracoes-conectadas.md
[proofs]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/provas-fcc-fc3.md
[e10]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/alternative-formulations/fcc.py
[fcc-verify]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/alternative-formulations/verify_fcc.py
[e11]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/alternative-formulations/f3-fcc.csv
[f3-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-f3-fcc.md
[f3-pre]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/alternative-formulations/pre-registro-f3.md
[e12]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/decisao-gf1.md
[specb]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/specs/proxima-fase-b-formulacoes-fcc-fc3/spec.md
[e13]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/benchmark/r6-gamma.csv
[gamma-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-r6-gamma.md
[e14]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/benchmark/r6-primal.csv
[primal-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-r6-primal.md
[e15]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/benchmark/r7-plato.csv
[r7-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-r7-plato.md
[e16]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/benchmark/run_r7_plato.py
[e17]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/decisao-g1.md
[r5-pre]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/pre-registro-r5.md
[specc]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/specs/proxima-fase-c-diagnostico-gap-plato/spec.md
[e18]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/structural/r11-certificadores.csv
[e19]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-r11-certificadores.md
[e20]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/auditoria-r11-divergencias.md
[e21]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/conclusao-r11-certificadores.md
[specd]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/specs/proxima-fase-d-certificadores-classes-especiais/spec.md
[e22]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/leituras-r11-certificadores.md
[r11-pre]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/pre-registro-r11-certificadores.md
[pathcode]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/structural/path_cycle.py
[spidercode]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/experiments/structural/spider.py
[e23]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/familias-estruturais.md
[phasep-csv]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/structural/piloto_fase_p.csv
[phasep]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/decisao-fase-p.md
[e24]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/structural/fase_e_sc.csv
[phasee]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/fase-e-sc.md
[e25]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/c6-hall-primeiro-salto.md
[disagg]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/desagregacao-por-origem.md
[t16]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/decisao-t16-cbi.md
[e26]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/overlap-ijcai2026-min-station.md
[das]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/min-station-das.pdf
[ijcai]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/novo_artigo_das_2026.pdf
[spiderpaper]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/pereira-ravelo-2026-aranhas.md
[e27]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-e12-pli.md
[e9e10]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-e9-e10-pli.md
[e13-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-e13-pli.md
[e14-report]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/resultados-e14-pli.md
[e28]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/direcoes-pli-min-station.md
[bundle]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/lagrangean/bundle_static/original_all_bundle_resumo.csv
[subgradient]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/results/lagrangean/subgradient_static/original_all_subgradient_resumo.csv
[e29]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/formulacao-fc3-consistencia-trios.md
[e30]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/benchmark-v1.md
[protocol]: https://github.com/ElielLucas/min-station/blob/b3c7337e12196c9b8ddf3150fdf31561fc507e91/docs/technical/reference/protocolo-comparacao-pareada.md
