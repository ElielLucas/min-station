# Backlog de continuação — MIN-STATION

Plano operacional do que já foi feito, do que está pausado e do que ainda falta.
A fonte científica das tarefas futuras é o
[parecer macro consolidado](../reference/MIN-STATION-parecer-macro-consolidado.md).
Este arquivo não executa pesquisa: só consolida histórico e backlog.

As tarefas futuras (T1–T22) preservam título, descrição, critérios de aceite e a
ordem do parecer: corretude, confiabilidade experimental, pesquisa/instâncias,
posicionamento científico.

## Como ler

| Status | Significado |
|---|---|
| `CONCLUÍDA` | Há evidência no repositório de que o trabalho foi executado. O resultado pode ser negativo ou inconclusivo. |
| `PARCIAL` | Há trabalho no repositório, mas o critério correspondente não fecha. |
| `A FAZER` | Ainda não executada. Critérios abaixo são a definição de pronto. |
| `PAUSADA` | Linha explicitamente suspensa até surgir evidência específica. |
| `ENCERRADA` | Decisão tomada com evidência: a linha não segue no escopo em que foi testada. |

Distinções que este backlog não mistura:

- **Problema de Das:** grafo simples, não dirigido, autonomia em passos, solução `C ⊆ V`.
- **Formulação base:** fluxo agregado, dígrafo de alcance, `y_v` em todo `V`, variante U. Baseline, não o objetivo da pesquisa.
- **Técnica experimental:** cortes, núcleo, CBI, BC-Y, Lagrangeana, preprocessamento. Não entra no baseline sem decisão explícita.
- **Experimento:** uma rodada nomeada (E0–E14), com plano, relatório e CSV.
- **Benchmark:** o protocolo e a partição do benchmark-v1, distintos das instâncias em si.
- **Instância:** arquivo e linha do manifesto. `classe = principal` é o recorte de Das; `extensao_ponderada` e `extensao_dirigida` são extensão.
- **Documentação/literatura:** Das, SBPO, parecer, artigo IJCAI 2026. Não substituem código nem CSV.

## Mapa

### Já feito

Formulação base all-vertices e variante U; validação e correção de cortes, inclusive C4-DM; campanha E0–E8; benchmark-v1 (lote 1); E9, E10, E10b, E12, E13, E14; regeneração do protocolo de dificuldade depois do C4-DM.

### Encerrado ou pausado

A2 (CBI como método para o problema de Das) encerrada no E12. B2 (simetria em hipercubos) encerrada no E5. R6 além de `L_bot` saiu no E9. O gatilho antigo do E11 (OPT = UB em ≥ 3/4 no E14) não disparou. Lagrangeana da base, Benders clássico como bound mais forte, BC-Y genérico, tuning de reverse-delete, C5, symmetry breaking genérico e geração de colunas ficam pausados. Detalhe na seção própria.

### Parcial

Nada do bloco 2 permanece parcial. A prova de equivalência da formulação base foi fechada na T5 (`validacao-formulacao-base.md` §5.5).

### Ainda por fazer

Nenhuma tarefa do parecer. T1–T22 foram executadas. Specs: `specs/bloco1-corretude-terminais-sT/spec.md`, `specs/bloco2-confiabilidade-experimental/spec.md`, `specs/bloco3-pesquisa-instancias-estruturais/spec.md` e `specs/bloco4-posicionamento-cientifico/spec.md`. Restam as edições de documentos científicos listadas em `docs/technical/reference/overlap-ijcai2026-min-station.md` §7.1 ("Passo posterior") e a redação do artigo, que não é tarefa deste backlog.

### Dependências

```text
T1, T2 → T3 → T4
T5 em paralelo com T1–T4 (mesma etapa; a prova cita a rede corrigida)
T6 antes de qualquer comparação nova de desempenho
T7, T8, T11 em paralelo com T6
T9 e T10 antes de T16, T19 e T21
T12 → T13 → T14
T15 depois de T12 na ordem recomendada; não bloqueia T13–T14
T16 só se a linha CBI ainda for relevante depois do E12, e depois de T1 e T10
T17 só se a linha CBI ainda for relevante depois do E12
T18 em paralelo, restrita a instâncias pequenas
T19 depois de T9, T10 e das famílias aplicáveis (T12–T17)
T20 depois de T19
T21 depois de T20
T22 pode começar em paralelo; entra no artigo só depois do levantamento
```

O E12 já encerrou A2 para instâncias de Das. T16 e T17 não reabrem essa bateria.

---

## Inconsistências (não reconciliadas)

Registradas aqui de propósito. Corrigi-las é trabalho da T11 ou de uma tarefa futura, não deste arquivo.

1. **E11 / C6 e o E14.** `resultados-e14-pli.md` aplica o critério pré-registrado: 0/4 com OPT = UB, então o E11 não volta à fila por esse gatilho. O parecer (§9, Etapa 3) e a T14 tratam C6 como linha matemática desacoplada do E14. As duas frases coexistem. A T14 foi executada como linha matemática, com derivação anterior à medição; o veredito do E14 permanece válido e não foi a autorização dessa medição.
2. **Regeneração e a T8.** O passo 2 de `plano-pos-e13.md` foi executado (`benchmark-v1.md` §8). A T8 pede mais: partição por grafo de origem, `hc9u` e `puc-hc9u-seed-r1` deixando de contar como evidências independentes, e proveniência completa por resultado. A regeneração está em H17; a T8 continua `A FAZER`.
3. **NodeCount e a T9.** `measure_mip` em `experiments/cuts/harness.py` já devolve `node_count`. Tempos do primeiro e do melhor incumbente, tempo até a prova e a separação geração/preprocessamento/heurística/solver não estão nesse retorno. A T9 continua `A FAZER`.
4. **Oráculo e o E12.** O E12 restringiu a avaliação a `S∩T = ∅` e os controles MAPF não usam `-rho` (`resultados-e12-pli.md`). A reavaliação das linhas `-rho` do E10/E10b com oráculo corrigido não existe, porque a correção do oráculo (T1) não foi feita. A T4 continua `A FAZER`, com esse recorte do E12 já coberto.
5. **T16 / T17 e o E12.** O teste discriminante COMP × núcleo × CBI em PUC/PUCN já rodou e encerrou A2 para Das. T16 e T17 valem para famílias novas, e só se a linha CBI continuar relevante. Não são repetição do E12.
6. **Contagem de instâncias.** `CLAUDE.md` fala em "22 antigas compatíveis + as 70 do benchmark-v1". O manifesto atual tem 92 linhas: 75 `principal`, 11 `extensao_dirigida`, 3 `extensao_ponderada`, 3 `historico`. O parecer (§5, commit `e9d1ccb`) lê as 75 principais como 70 do benchmark-v1 mais 5 legadas e pede o texto "5 antigas + 70". A correção está na T11 e não foi aplicada.
7. **Prosa do E13 e do E2–E4.** `resultados-e13-pli.md` §5 ainda diz que a divergência com o manifesto "não é ruído de execução" e não registra o confundimento `TimeLimit` × `MIPFocus`. `resultados-e2-e4-pli.md` ainda descreve Barcelona st25 de forma que o parecer marca como incorreta. Itens da T11.
8. **Q1 e o benchmark posterior.** `open-questions.md` Q1 diz que as 22 instâncias da época têm `|S∩T| = 0` e que nenhum resultado anterior é afetado. Isso descreve a rodada E5. O benchmark-v1 depois introduziu 5 principais com sobreposição, e o C4-DM inválido afetou 3 (`correcao-c4-dm.md`). A frase de Q1 não foi atualizada.
9. **Ranking A2.** `direcoes-pli-min-station.md` §13 acompanha A2 até o E9 e deixa o veredito para o E12. `resultados-e12-pli.md` encerra A2 para Das. O ranking não incorpora esse veredito. Não está na lista fechada da T11.

`benchmark-v1.md` §7.2 (classe D com 4 instâncias) descreve a partição anterior; §8 já diz que, depois da regeneração, D ficou com 3. Não é divergência escondida.

---

## Histórico — concluídas

Cada item abaixo tem evidência no repositório. Números finos ficam nos relatórios citados.

### Formulação base e corretude

#### H01 — Formulação base com estações em todo `V`

**Status:** `CONCLUÍDA`

**Descrição:** A formulação deixou a restrição do artigo da SBPO (estações só em vértices intermediários) e passou a definir `y_v` para todo `v ∈ V`, com fluxo agregado e dígrafo de alcance. Isso aproxima o baseline do problema de Das. Não é o objetivo científico do projeto.

**Resultado:** Baseline documentado e separado da formulação generalizada da SBPO.

**Evidência:** `docs/context-ai/base-formulation.md`, `RESEARCH.md` §3, `docs/project-overview.md` §3.

#### H02 — Balanço unificado para `S∩T` (variante U)

**Status:** `CONCLUÍDA`

**Descrição:** A formulação com balanços separados ficava inviável em `v ∈ S∩T` (`0 = 2`), um falso negativo. A rodada E5 adotou o balanço unificado. Q1 foi fechada. Pré-processar vértices comuns removendo-os de `S` e `T` foi rejeitado (CE1').

**Resultado:** `baseline.py` implementa a variante U. Com `S∩T = ∅` a forma coincide com a anterior.

**Evidência:** `docs/technical/governance/open-questions.md` Q1, `docs/context-ai/base-formulation.md` §6 e §10.1, `docs/technical/reference/validacao-formulacao-base.md`.

#### H03 — Correção de cortes inválidos na campanha E5

**Status:** `CONCLUÍDA`

**Descrição:** Blocos B e C de `resultados-e2-e4-pli.md`: defeito de corretude em `S∩T` (coberto por H02) e seis defeitos de validade de corte corrigidos e verificados. A prova formal de equivalência não fecha neste item (ver P1 e T5).

**Resultado:** Cortes revisados para o Lema 5 de Das (o robô pode permanecer no próprio alvo). O relatório lista os defeitos como corrigidos.

**Evidência:** `docs/technical/reference/resultados-e2-e4-pli.md` §2–§3 e §8.1, `docs/technical/plans/plano-experimentos-e5.md`.

#### H04 — Correção de `generate_C4_DM`

**Status:** `CONCLUÍDA`

**Descrição:** O gerador produzia cortes inválidos quando `S∩T ≠ ∅` (deficiência medida contra `T\S` em vez de `T`) e não era determinístico entre processos. Ambos corrigidos em 2026-09-26, com regressão que reprova o código anterior.

**Resultado:** Das 5 principais com sobreposição, 3 tinham cortes inválidos. Reavaliação corrigiu 3 linhas do manifesto, inclusive `b-b09-intercalado-f2-rho` (4 → 2). Nenhuma classe de dificuldade mudou nessa correção pontual. A regeneração completa do protocolo é H17.

**Evidência:** `docs/technical/reference/correcao-c4-dm.md`, `experiments/cuts/verify_c4_dm.py`.

### Experimentos de cortes e decomposição

Instâncias de E0–E8 são, em grande parte, extensão ponderada ou dirigida. Conclusões dessa campanha não se generalizam ao problema de Das sem a ressalva de `benchmark-v1.md` e de Q2/Q7.

#### H05 — E0, E1' e E1: cortes de cobertura (A1)

**Status:** `CONCLUÍDA`

**Descrição:** Comparou BASE-I e BASE-C, validou famílias sintéticas e mediu C1/C2/C4 em instâncias reais da época.

**Resultado:** Hipótese A1 fortemente suportada no recorte testado (hc9u 1 → 29 com C1; hc10p 1 → 52; Philadelphia 3 → 34 com C1+C2; cc10-2p fecha na raiz). C4-DM eficaz em F2 sintética e redundante nas reais daquele conjunto. C3 melhora o LP em Philadelphia e não entra na raiz sem separação iterativa.

**Evidência:** `docs/technical/reference/resultados-e0-e1-pli.md`, `docs/technical/plans/plano-experimentos-e0-e1.md`, `results/cuts/`.

#### H06 — E2, E3 e E4: espaço-y, núcleo e árvore curta

**Status:** `CONCLUÍDA`

**Descrição:** Laço de cortes no LP em y, IP do núcleo de cobertura e MIP com cortes estáticos (TL 300 s), com R corrigido.

**Resultado:** O núcleo de hc9u resolve em poucos segundos (OPT do núcleo = 32) e uma solução ótima do núcleo testada no compacto é inviável. OPT(hc9u) ficou em [32, 38]. Cortes estáticos melhoram o LB e, em parte das instâncias pequenas, pioram o UB.

**Evidência:** `docs/technical/reference/resultados-e2-e4-pli.md` §4–§6, `docs/technical/plans/plano-experimentos-e2-e4.md`.

#### H07 — E6: branch-and-cut em y com corte lazy

**Status:** `CONCLUÍDA`

**Descrição:** Callback lazy da família 𝒵, sem MIP start e sem user cuts.

**Resultado:** Mecanismo validado e funcional. Insuficiente com C1 puro no prazo testado. Não decide A2.

**Evidência:** `docs/technical/reference/resultados-e2-e4-pli.md` §7.

#### H08 — E7: BC-y completo contra o compacto

**Status:** `CONCLUÍDA`

**Descrição:** BC-y com MIP start, lazy no MIPSOL e user cuts no MIPNODE, contra o compacto com A1, em 7 instâncias, TL 300 s.

**Resultado:** BC-y não superou o COMP em LB final nem em tempo até o ótimo. Revisão posterior invalidou o experimento como medida do método: cortes estáticos diferentes, start sem viabilidade garantida, callback sem guarda de tempo. A2 ficou sem decisão.

**Evidência:** `docs/technical/reference/resultados-e7-pli.md` §5.1 e §6, `docs/technical/plans/plano-experimentos-e7.md`.

#### H09 — E8: COMP × BC-Y' × CBI

**Status:** `CONCLUÍDA`

**Descrição:** Mesmos cortes estáticos, mesmo start e mesmo TL (300 s, uma seed). Certificou OPT(cc12-2p) = 6.

**Resultado:** No critério da época, A2 continua: em R-c o CBI prova o ótimo e o compacto não; em hc10p e bip42p o CBI tem o melhor LB, com uma iteração e zero cortes 𝒵 (ganho do núcleo, não da iteração). O recorte "A2 só fora de R-a" foi suspenso pelo benchmark-v1, porque R-c não produz instância difícil fiel a Das e as vitórias de R-a estão em TNTP. O veredito posterior para Das é H16.

**Evidência:** `docs/technical/reference/resultados-e8-pli.md`, `docs/technical/plans/plano-experimentos-e8.md`, `results/cuts/e8_certificado_cc12.txt`.

### Benchmark, instâncias e diagnóstico no problema de Das

#### H10 — Benchmark-v1, lote 1

**Status:** `CONCLUÍDA`

**Descrição:** 70 instâncias fiéis a Das, manifesto, classificação de dificuldade e divisão desenvolvimento/avaliação. Plano em `plano-benchmark-v1.md`.

**Resultado:** A dificuldade acompanha UB/m, não o tamanho do dígrafo de alcance. O regime R-c não produz instância difícil nesse lote. Classes na partição anterior à regeneração: F 35, A 26, M 5, D 4 (30 D/A). Lacunas de maturidade seguem abertas: D abaixo do alvo, `pucn` com dois níveis de r, uma seed, sem tag de versão. A partição por variante (não por grafo de origem) é dívida da T8.

**Evidência:** `docs/technical/reference/benchmark-v1.md`, `docs/technical/plans/plano-benchmark-v1.md`, `instances/manifest.csv`.

#### H11 — Classificação de métrica e de grafos dirigidos

**Status:** `CONCLUÍDA`

**Descrição:** Medição, instância a instância, de pesos, arcos sem reverso e relação de `A_r` com o problema de Das. Q7 decidida em 2026-09-26: TNTP atuais ficam como extensão dirigida, fora das conclusões sobre Das; a versão não dirigida entra no lote 2 do benchmark.

**Resultado:** hc9u é Das em passos. hc10p–hc12p e bip42p são equivalentes a Das com r = 1 (`A_r = E`). cc10-2p/cc12-2p são extensão ponderada. Chicago, Barcelona e Philadelphia são extensão ponderada e dirigida. Três TNTP com o R do arquivo são triviais (OPT = 0).

**Evidência:** `docs/technical/governance/open-questions.md` Q2 e Q7, `docs/technical/reference/benchmark-v1.md` §5.

Q2 ainda registra como não decidido se conclusões por regime devem ser refeitas em passos. Isso não é uma tarefa nova; continua em `open-questions.md`.

#### H12 — E9: diagnóstico de raiz nas D/A

**Status:** `CONCLUÍDA`

**Descrição:** `z_LP` e efeito de C1, C2, C4 e do IP do núcleo nas 30 D/A do benchmark-v1. Sem C3 e sem R6 além de `L_bot`.

**Resultado:** `L_bot` é dominado pela raiz com cortes; R6 além de `L_bot` sai da agenda. O núcleo (TL 60 s) supera o LB do COMP (600 s) em 6 linhas, todas PUC/PUCN, por 1–2 estações. Em MAPF e Vienna o COMP fica acima. As 6 linhas não são 6 grafos independentes. Números medidos antes da correção do C4-DM; o relatório delimita o efeito.

**Evidência:** `docs/technical/reference/resultados-e9-e10-pli.md` §2.

#### H13 — E10 e E10b: primal construtivo

**Status:** `CONCLUÍDA`

**Descrição:** Substitutos do reverse-delete que parte de `C = V`. E10b repara a solução do núcleo.

**Resultado:** Inconclusivo quanto a gap primal ou dual. Os construtores devolvem soluções piores que o incumbente do Gurobi na maior parte das D/A. O reparo vence o UB do COMP em 1/30. Um MIP start melhor não move o LB. O critério "se H3 perder, o gargalo é dual" foi rejeitado como inferência inválida.

**Evidência:** `docs/technical/reference/resultados-e9-e10-pli.md` §3–§5.

#### H14 — E13: ênfase primal em MAPF/Vienna

**Status:** `CONCLUÍDA`

**Descrição:** COMP com `MIPFocus = 1`, controle em 600 s e fase longa em 1800 s, 13 instâncias.

**Resultado:** Veredito de gap primal no limiar (7/13 com Δ_UB ≥ 5%). A fase de 600 s sozinha daria o sinal oposto. O gap residual permanece entre cerca de 10% e 44% e supera a queda primal nas 12 não resolvidas. O experimento não atribui o residual ao LB ou ao UB. Nove controles divergem do manifesto.

**Evidência:** `docs/technical/reference/resultados-e13-pli.md`, `docs/technical/plans/plano-pos-e13.md` passos 0–1.

A prosa da §5 do relatório ainda contradiz o parecer. Correção é a T11, não uma reabertura do E13.

#### H15 — E14: Cutoff nas quatro D/A de gap absoluto 2

**Status:** `CONCLUÍDA`

**Descrição:** COMP com `Cutoff = UB_melhor − 0,5` e `MIPFocus = 3`, TL 14400 s, quatro instâncias.

**Resultado:** 0/4 com OPT = UB. As quatro terminam em `TIME_LIMIT`. Nenhuma solução abaixo de UB_melhor. O único LB que se move é `mapf-room-32-32-4-m25-f4-rho` (17 → 18). O critério que devolvia o E11 à fila não dispara. O resultado não se estende às instâncias de residual 30–44%.

**Evidência:** `docs/technical/reference/resultados-e14-pli.md`, `experiments/benchmark/run_e14.py`, `results/benchmark/e14_fatia{1,2}.csv`. Relatório e CSVs estavam fora do commit no momento desta consolidação.

#### H16 — E12: CBI × núcleo × COMP em PUC/PUCN

**Status:** `CONCLUÍDA`

**Descrição:** Três braços com os mesmos cortes estáticos, sem MIP start, TL 600 s, `PYTHONHASHSEED=0`. Avaliação em 9 instâncias (7 grafos), mais desenvolvimento e controles MAPF sem `-rho`. Re-seeds 43 e 44 onde a margem exigia.

**Resultado:** A2 encerrada para Das. Uma vitória contra o COMP, em um grafo (`hc11p`), e nenhuma vitória contra o núcleo. Onde o núcleo fecha, os cortes 𝒵 não sobem o LB acima dele. Controles MAPF repetem o esperado: CBI no núcleo e abaixo do COMP.

**Evidência:** `docs/technical/reference/resultados-e12-pli.md`, `experiments/benchmark/run_e12.py`, `experiments/benchmark/tabela_e12.py`, `results/benchmark/e12_fatia{1,2}.csv`, `docs/technical/plans/plano-pos-e13.md` passo 4.

#### H17 — Regeneração do protocolo de dificuldade depois do C4-DM

**Status:** `CONCLUÍDA`

**Descrição:** Reexecução do protocolo da §6 de `benchmark-v1.md` com o gerador corrigido (TL 600 s, seed 42, 4 threads, 2 fatias). Histórico preservado. `MELHORES` recebe limites do E13. O manifesto é atualizado só nas colunas de dificuldade e limites.

**Resultado:** Classes das 70: F 35, A 28, M 4, D 3 (D/A passa de 30 para 31). Entra `mapf-empty-32-32-m50-f2` (M → A). As três correções manuais do C4-DM reaparecem no CSV novo. E9, E10, E10b e E13 usaram a partição anterior e não são refeitos. `treewidth_ub` mudou em 49 instâncias na reconstrução completa e não foi aplicado.

**Evidência:** `docs/technical/reference/benchmark-v1.md` §8, `experiments/benchmark/comparar_regeneracao_c4fix.py`, `results/benchmark/regeneracao_c4fix.csv`, `results/benchmark/dificuldade_v1_fatia{1,2}.csv`, `results/benchmark/historico/`. Parte desses arquivos estava fora do commit no momento desta consolidação.

Isto não cumpre a T8.

### Outras campanhas com evidência

#### H18 — Preprocessamento experimental

**Status:** `CONCLUÍDA`

**Descrição:** Baterias em `results/preprocessing/` (estratégias, separadores, preprocessamento, TL 1200 s).

**Resultado:** O parecer, lendo esses CSVs, não encontra ganho robusto: LB igual nas linhas comparáveis, um UB pior, e linhas sem baseline compatível. Não há decisão de incorporar preprocessamento ao baseline.

**Evidência:** `results/preprocessing/experimentos_preprocess/`, parecer §4.

#### H19 — Relaxação lagrangeana da formulação base

**Status:** `CONCLUÍDA`

**Descrição:** Subgradiente e bundle sobre a ativação da base.

**Resultado:** Pior que o LP nas execuções registradas. A linha de novos ajustes dessa mesma relaxação fica `PAUSADA` (parecer §9; ranking D-1 em `direcoes-pli-min-station.md`).

**Evidência:** `results/lagrangean/`, parecer §4.

#### H20 — Nota de direções de PLI

**Status:** `CONCLUÍDA`

**Descrição:** Documento de estrutura, cortes C1–C8, Benders, Lagrangeana, formulações alternativas e ranking A/B/C/D. Anotado com E7, E8 e E9. Não é formulação do baseline.

**Resultado:** A1 apoiada pela campanha inicial. Várias linhas D ficam descartadas por enquanto, com a justificativa no próprio documento. O ranking A2 está desatualizado em relação ao E12 (inconsistência 9).

**Evidência:** `docs/technical/reference/direcoes-pli-min-station.md`.

---

## Parciais

Não marcar como concluído.

#### P1 — Prova de equivalência da formulação base

**Status:** `CONCLUÍDA` (fechada pela T5; o texto abaixo descreve o estado anterior)

**Descrição:** `validacao-formulacao-base.md` escreve a correspondência restrição a restrição e uma prova que o próprio texto declara falha quando `S∩T ≠ ∅`. Q3 pede as duas direções (solução do problema → PLI, e decomposição do fluxo inteiro em rotas) e diz que igualdade computacional não substitui a prova. A variante U (H02) mudou o modelo depois dessa escrita.

**Resultado:** Há validação e casos adversariais. Não há prova versionada que cubra permanência, `S = T` e ótimo zero na rede corrigida.

**Evidência:** `docs/technical/reference/validacao-formulacao-base.md` §5.4 e apêndice A.10, `docs/technical/governance/open-questions.md` Q3, parecer §2.3.

**O que falta:** nada. A T5 escreveu a prova na §5.5, com a rede auxiliar corrigida pela T1.

#### P2 — Determinismo da construção do modelo

**Status:** `PARCIAL`

**Descrição:** O gerador C4-DM foi tornado determinístico (H04). O parecer ainda reproduz variação de ordem por `set`/`frozenset` na montagem do modelo em `harness.py` e `bc_yspace.py`. `PYTHONHASHSEED` foi usado no E12 como proteção entre braços, não como determinismo do modelo.

**Resultado:** Cortes C4 reprodutíveis. A construção geral do MIP não está ordenada de forma explícita.

**Evidência:** `docs/technical/reference/correcao-c4-dm.md`, parecer §3.1, `plano-pos-e13.md` §4.3.

**O que falta:** T6.

#### P3 — Instrumentação do harness

**Status:** `PARCIAL`

**Descrição:** `measure_mip` persiste objetivo, bound, gap, status, `sol_count`, `node_count` e tempo de MIP. A raiz tem bound e tempo próprios. Não há tempo do primeiro incumbente, tempo do melhor incumbente nem colunas separadas de geração, preprocessamento e heurística no retorno usado pelas rodadas recentes.

**Resultado:** Dá para ler LB, UB, gap e, onde o runner grava, nós. Não dá para separar dificuldade primal, dual e tamanho da árvore do jeito que a T9 exige.

**Evidência:** `experiments/cuts/harness.py` (`measure_mip`), parecer §9 Etapa 2.

**O que falta:** T9.

#### P4 — Consolidação do benchmark depois da regeneração

**Status:** `PARCIAL`

**Descrição:** H17 atualizou classes, limites e a nota de que E9–E13 usaram a partição antiga. A divisão desenvolvimento/avaliação continua por variante, em ordem de nome. `hc9u` e `puc-hc9u-seed-r1` seguem como duas linhas. Proveniência completa (versão dos cortes, origem do certificado, versão do código em cada resultado histórico) não está no manifesto.

**Resultado:** Protocolo de dificuldade regerado. Benchmark ainda não é a visão que a T8 define.

**Evidência:** `docs/technical/reference/benchmark-v1.md` §7–§8, parecer §5.

**O que falta:** T8.

Nada mais no repositório foi marcado `PARCIAL`. Trabalho só planejado está em `A FAZER` ou `PAUSADA`.

---

## Pausadas ou encerradas

Não são tarefas a executar. Reabrir só com evidência específica, como o parecer §9 pede.

| Linha | Status | Por quê | Evidência |
|---|---|---|---|
| A2 / CBI como método para Das | `ENCERRADA` | E12: uma vitória contra o COMP, nenhuma contra o núcleo | H16 |
| B2, simetria em hipercubos hc9u–hc12p | `ENCERRADA` | Fixação orbital elimina 1 variável; `Symmetry=2` empata; o gap que resta não é de simetria do núcleo | `direcoes-pli-min-station.md` §13 B2, E5 |
| R6 além de `L_bot` | `ENCERRADA` | Dominado pela raiz com cortes em todas as D/A medidas | H12 |
| Gatilho antigo do E11 via E14 | `ENCERRADA` | 0/4 com OPT = UB. Não cancela a T14, que é outra pergunta | H15 |
| Lagrangeana da mesma relaxação (subgradiente, bundle, Kelley) | `PAUSADA` | Bound ≤ LP; execuções piores que o LP | H19, ranking D-1 |
| Benders clássico como bound mais forte | `PAUSADA` | Teorema 8: igual a `z_LP` | `direcoes-pli-min-station.md` §6 e D-2 |
| BC-Y genérico em todas as famílias | `PAUSADA` | E7 inconclusivo por confundidores; E8 não generaliza a Das; E12 encerra o CBI para Das | H08, H09, H16 |
| Tuning de reverse-delete a partir de `C = V` | `PAUSADA` | Não escala; devolve C grande | H13, parecer §9 |
| C5 por limiar | `PAUSADA` | Ganho desprezível no E2 | parecer §4, `direcoes-pli-min-station.md` §5.5 |
| Symmetry breaking genérico | `PAUSADA` | A evidência de B2 é estreita e, no caso do Gurobi, só está na prosa | parecer §4 e §9 |
| Geração de colunas | `PAUSADA` | Antes de testar a força da desagregação; pricing de conjuntos de estações é o problema original | ranking D-5, parecer §9 |
| C3 exato (oráculo fracionário restrito) | `PAUSADA` | Fora da agenda até o E11 falhar; no Das não foi medido | `plano-pos-e8-adiado.md`, parecer §4 |
| Acrescentar instâncias sem hipótese | `PAUSADA` | Parecer §9 | parecer §9 |
| FPT, modular-width, vertex cover, algoritmo de árvores | `PAUSADA` | Só se o parâmetro medido for pequeno; árvores ainda exigem r > 1 e `S∩T` | parecer §9, "Condicionar" |
| Pré-processar "robô em `S∩T` fica parado" removendo o vértice | `ENCERRADA` | Inválido (CE1') | Q1, `validacao-formulacao-base.md` |

O núcleo inteiro como mecanismo de LB não está nesta tabela. O E12 separa o núcleo da iteração do CBI. O núcleo continua utilizável; a iteração com 𝒵 não mostrou ganho sobre ele no recorte de Das.

---

## A fazer

Ordem obrigatória do parecer: T1–T5, depois T6–T11, depois a sequência de famílias e o posicionamento. Critérios de aceite são os do arquivo de tarefas derivado do parecer.

### Bloco 1 — Corretude

A etapa 1 é pré-requisito de método que use o oráculo em instância com `S∩T ≠ ∅`.

Spec detalhada de T1–T5 (estado atual verificado, histórias, critérios EARS):
`specs/bloco1-corretude-terminais-sT/spec.md`.

#### T1 — Corrigir o oráculo para suportar permanência em `S∩T`

**Status:** `CONCLUÍDA` — arco `v_out → v_in` de capacidade 1 em `integer_oracle` e `_build_flow_net_aggregate`. `verify_t1_oracle_sT.py`: 618 conjuntos `C`, 0 divergências.
**Depende de:** nada
**Bloqueia:** T3, T4 e qualquer uso novo do oráculo com sobreposição

**Descrição:** Corrigir o `integer_oracle` e a rede agregada para representar corretamente o caso em que um robô já está em seu destino, sem obrigá-lo a sair do vértice. A solução pode usar o arco de permanência `v_out → v_in` ou uma modelagem equivalente com papéis separados.

**Critérios de aceite:**

- O oráculo aceita corretamente o caso `S=T={v}` com nenhuma estação instalada.
- O caso de sobreposição parcial de `S` e `T` retorna o mesmo resultado de viabilidade que o modelo base.
- A correção não altera resultados dos casos com `S∩T=∅`.
- `integer_oracle`, rede agregada e separação fracionária usam a mesma semântica corrigida.
- Testes automatizados cobrem os novos comportamentos.

#### T2 — Implementar validador independente de viabilidade

**Status:** `CONCLUÍDA` — `experiments/cuts/independent_validator.py`. Exaustivo para `n ≤ 4` e amostra documentada para `n = 5`; ver `validacao-formulacao-base.md`, seção "Verificação recomendada".
**Depende de:** nada
**Bloqueia:** T3; também as famílias estruturais, que pedem enumeração de `C` em casos pequenos

**Descrição:** Criar um segundo mecanismo de validação que não reutilize a construção de fluxo do oráculo. O parecer propõe estados `(v, bateria)` combinados com matching e enumeração de conjuntos `C` para grafos pequenos.

**Critérios de aceite:**

- O validador não chama nem replica estruturalmente `integer_oracle`.
- Representa deslocamento e consumo de bateria explicitamente.
- Trata corretamente `S∩T`.
- Consegue verificar a viabilidade de um conjunto `C`.
- Permite enumerar `C` em instâncias pequenas para obter OPT.
- Resultados coincidem com o modelo base nos casos de regressão conhecidos.

#### T3 — Criar suíte de regressão de corretude para terminais

**Status:** `CONCLUÍDA` — `experiments/cuts/verify_t3_regressao_terminais.py`. Evidência em `docs/technical/reference/regressao-terminais-t3.md`.
**Depende de:** T1, T2

**Descrição:** Transformar os contraexemplos identificados no parecer em uma suíte permanente de regressão.

**Critérios de aceite:**

- Contém o caso de permanência pura `S=T={v}`.
- Contém o caso de sobreposição parcial.
- Contém a estrela `SharedTerminal`.
- Contém o caminho `a-b-c` discutido no parecer.
- Cada caso é validado no modelo base, no oráculo, na separação fracionária, na validação de cortes e no validador independente.
- A suíte falha automaticamente em caso de divergência.

#### T4 — Revalidar resultados experimentais afetados pelo antigo oráculo

**Status:** `CONCLUÍDA` — auditoria em `docs/technical/reference/revalidacao-oraculo-pos-t1.md`. Nenhum veredito publicado dependeu do defeito a ponto de exigir reexecução.
**Depende de:** T1

**Descrição:** Identificar e reexecutar experimentos em que o oráculo defeituoso possa ter sido aplicado a instâncias com `S∩T ≠ ∅`.

**Critérios de aceite:**

- E10 e E10b `-rho` são reavaliados.
- É verificado se algum outro experimento utilizou o oráculo em instâncias com sobreposição.
- Os controles MAPF do E12 são conferidos, se aplicável.
- Resultados antigos afetados são marcados como obsoletos ou substituídos.
- O relatório registra claramente o que mudou e o que permaneceu válido.

**Nota de estado:** O E12 já conferiu `S∩T` vazio no próprio CSV e escolheu controles MAPF sem `-rho` (H16). Isso não substitui a reavaliação do E10/E10b.

#### T5 — Formalizar a prova de equivalência da formulação base

**Status:** `CONCLUÍDA` — `validacao-formulacao-base.md` §5.5. As seis lacunas de A.10 estão marcadas fechadas.
**Depende de:** a rede auxiliar corrigida (T1), no trecho que relaciona formulação e rede. O restante da prova pode ser escrito em paralelo.
**Continua:** P1

**Descrição:** Escrever no repositório a prova completa de que a formulação base representa corretamente o MIN-STATION original, incluindo `S∩T`, permanência e trânsito por terminais.

**Critérios de aceite:**

- A prova está versionada em `docs`.
- Trata explicitamente `S∩T`.
- Trata `S=T` e o caso de ótimo zero.
- Justifica a utilização de fluxo contínuo, quando aplicável.
- Relaciona a formulação à rede auxiliar corrigida.
- Todos os lemas necessários estão explicitados, sem depender apenas de testes computacionais.

### Bloco 2 — Confiabilidade experimental

A etapa 2 antecede comparações de desempenho.

Spec detalhada de T6–T11: `specs/bloco2-confiabilidade-experimental/spec.md`.

#### T6 — Tornar determinística a construção dos modelos

**Status:** `CONCLUÍDA` — `cortes_ordenados` em `harness.py`, `bc_yspace.py` e `yspace.py`. `verify_t6_determinismo.py`: `b-b15-regiao-f4` com 33 cortes, quatro ordens antigas e uma ordem nova nas sementes 0–3.
**Depende de:** nada
**Continua:** P2
**Bloqueia:** comparações novas de desempenho

**Descrição:** Eliminar dependências da ordem de `set`, `frozenset` e hash do Python na geração dos modelos.

**Critérios de aceite:**

- Lista de cortes é explicitamente ordenada.
- Vértices de cada corte são ordenados.
- Coeficientes e demais estruturas relevantes são adicionados em ordem determinística.
- `harness.py` e `bc_yspace.py` são corrigidos.
- Execuções com diferentes `PYTHONHASHSEED` produzem a mesma ordem de construção.
- `PYTHONHASHSEED` passa a ser proteção adicional, e não o mecanismo principal de determinismo.

**Nota de estado:** H04 já ordenou `generate_C4_DM`. O critério acima é o modelo inteiro.

#### T7 — Avaliar e padronizar orçamento determinístico com `WorkLimit`

**Status:** `CONCLUÍDA` — `decisao-orcamento-worklimit.md`. `WorkLimit` na comparação de métodos, `TimeLimit` no lote de parede. Sem migração dos runners.
**Depende de:** nada

**Descrição:** Verificar a semântica de `WorkLimit` no Gurobi utilizado pelo projeto e decidir se ele deve substituir ou complementar `TimeLimit` nas comparações experimentais.

**Critérios de aceite:**

- Comportamento do `WorkLimit` é confirmado para a versão do Gurobi do projeto.
- Existe um experimento controlado comparando `TimeLimit` e `WorkLimit`.
- A decisão de uso está documentada.
- O protocolo experimental define explicitamente o orçamento adotado.
- Caso `WorkLimit` não seja adotado, a justificativa fica registrada.

#### T8 — Consolidar o benchmark após a regeneração

**Status:** `CONCLUÍDA` — `grupos_origem.csv`, `duplicata_de`, `verify_t8_consolidacao.py`. A partição não foi reatribuída; os 11 vazamentos ficaram marcados.
**Depende de:** H17 (já feita)
**Continua:** P4

**Descrição:** Reconstruir a visão oficial do benchmark depois do `plano-pos-e13`, eliminando inconsistências e vazamentos entre desenvolvimento e avaliação.

**Critérios de aceite:**

- Novas contagens e classes são registradas.
- A partição passa a ser feita por grafo de origem, e não por variante.
- `hc9u` e `puc-hc9u-seed-r1` deixam de contar como evidências independentes.
- Cada resultado possui hash da instância, versão dos cortes, configuração, seed, origem do certificado e versão do código.
- O manifesto é regenerável sem perder correções anteriores.

**Nota de estado:** Contagens novas e a regeneração do protocolo estão em H17 e em `benchmark-v1.md` §8. Os outros critérios não.

#### T9 — Ampliar a instrumentação do harness experimental

**Status:** `CONCLUÍDA` — tempos de incumbente em `measure_mip` (`coletar_incumbente`). Inventário em `schema-instrumentacao-mip.md`. Runners históricos não foram reexecutados.
**Depende de:** nada
**Continua:** P3
**Bloqueia:** T19

**Descrição:** Adicionar as métricas que hoje impedem distinguir dificuldade primal, dificuldade dual e tamanho da árvore de busca. O parecer registra que `measure_mip` não coleta `NodeCount` nem os tempos dos incumbentes.

**Critérios de aceite:**

- `NodeCount` é persistido.
- Tempo do primeiro incumbente é persistido.
- Tempo do melhor incumbente é persistido.
- Tempo até a prova do ótimo é registrado quando disponível.
- LB, UB, gap e bound de raiz continuam registrados.
- Tempos de geração, preprocessing, heurística e solver são separados.
- Para CBI, número de iterações e cortes é registrado.
- CSVs/resultados possuem schema documentado.

**Nota de estado:** `node_count` já sai de `measure_mip` (P3). O restante do critério não. O texto do parecer sobre `NodeCount` está desatualizado em relação ao código; o critério permanece até a persistência estar no protocolo, não só no retorno da função.

#### T10 — Padronizar protocolo de comparações pareadas

**Status:** `CONCLUÍDA` — `protocolo-comparacao-pareada.md`, citado em `CLAUDE.md`. A fase longa do E13 fica como efeito conjunto de prazo e `MIPFocus`.
**Depende de:** T7, se o orçamento adotado for `WorkLimit`. Com `TimeLimit`, pode avançar em paralelo.
**Bloqueia:** T16, T19, T21

**Descrição:** Evitar experimentos como o E13, em que mudança de tempo e parâmetro ficam confundidas.

**Critérios de aceite:**

- Métodos comparados recebem o mesmo orçamento.
- Usam o mesmo start ou todos executam sem start.
- Threads e demais parâmetros relevantes são equivalentes.
- Comparações sensíveis a 1–2 unidades são repetidas com múltiplas seeds.
- `NodeCount` faz parte da comparação.
- Mudança de parâmetro nunca é confundida com mudança de tempo.
- Cada experimento possui um controle explicitamente definido.

#### T11 — Corrigir documentação inconsistente identificada no parecer

**Status:** `CONCLUÍDA` — os sete itens de prosa. `construir_modelo_estendido_vi` não afirma equivalência com o baseline: y só em VI e destino sem saída.
**Depende de:** nada

**Descrição:** Aplicar as correções documentais já enumeradas pelo parecer.

**Critérios de aceite:**

- `resultados-e13-pli.md` deixa de afirmar que a diferença "não é ruído de execução".
- O confundimento `TimeLimit` × `MIPFocus` do E13 é documentado.
- O resultado Barcelona st25 do E2/E4 é corrigido.
- `CLAUDE.md` contém as contagens corretas.
- Documentos da formulação deixam de assumir indevidamente `S∩T=∅`.
- Comentários de `StayPut` e `SharedTerminal` são corrigidos.
- É adicionado o gabarito de permanência pura.
- `modelo_estendido.py` deixa de ser descrito como equivalente ao baseline.

A inconsistência 9 (`direcoes-pli-min-station.md` §13 sem o veredito do E12) não está nesta lista. Fica visível na seção de inconsistências para não ser tratada como já coberta.

### Bloco 3 — Pesquisa e instâncias estruturais

Ordem recomendada: BP, HB, E11/C6, SC, teste do CBI, TR, diagnóstico all-V, piloto, decisão, expansão. T12–T20 estão executadas. A decisão da fase P está em `docs/technical/reference/decisao-fase-p.md`: BP e HB descartadas, SC promovida, T16 e TR encerradas sem bateria de CBI, desagregação sem expansão. A fase E de SC está em `fase-e-sc.md`: o GF2 em `k = 8` e `k = 9` repetiu a separação, e os gêmeos saíram sem certificado do set cover.

#### T12 — Implementar e validar a família estrutural BP

**Status:** `CONCLUÍDA`
**Depende de:** T2 para a enumeração de `C` nos casos pequenos; T6 antes de usar a família em comparação de desempenho

**Descrição:** Criar o gerador da família baseada em Bin Packing para separar experimentalmente dificuldade de UB e dificuldade de LB.

**Critérios de aceite:**

- Gerador recebe parâmetros `q`, `B`, itens e seed.
- Produz pares "sim" e "não" comparáveis.
- Nas instâncias "sim", existe certificado construtivo independente.
- Nas "não", inexistência de partição é certificada por solver independente.
- Nos casos pequenos, enumeração de `C` confirma o OPT.
- Núcleo reproduz `2n+q`.
- As propriedades matemáticas usadas pelo experimento estão documentadas.
- Gerador é determinístico e produz `sha256`.

#### T13 — Implementar e validar a família estrutural HB

**Status:** `CONCLUÍDA`
**Depende de:** T12 na ordem recomendada; T2 para enumeração

**Descrição:** Implementar os bolsões de Hall para testar deficiências de multiplicidade e verificar se C6 realmente não fecha o gap de primeiro salto.

**Critérios de aceite:**

- Gerador implementa `HB(q, ndir, p; k, L)`.
- Casos pequenos são validados por enumeração.
- C1 e C2 são vazios nos casos previstos.
- Núcleo e OPT reproduzem as previsões teóricas.
- A fórmula do LB é provada ou corrigida antes do piloto.
- O comportamento do coeficiente C6 em destinos compartilhados é validado.
- Resultado determina se E11 deve permanecer em primeiro salto ou migrar para desigualdades de segunda camada.

#### T14 — Derivar, validar e implementar E11/C6

**Status:** `CONCLUÍDA`
**Depende de:** T13 (HB como controle). Não depende do gatilho do E14.

**Descrição:** Tratar C6 como uma linha matemática independente: derivação, validação própria, implementação, medição. O parecer alerta que `is_valid_cut` atual não serve para RHS `δ ≥ 2`.

**Critérios de aceite:**

- Desigualdade é formalmente derivada.
- Condições de validade estão documentadas.
- Existe validador específico para `δ ≥ 2`.
- Casos pequenos são enumerados antes de qualquer benchmark.
- Implementação passa no validador.
- HB é utilizada como teste de controle.
- Só depois dessas etapas são executadas medições de desempenho.

**Nota de estado:** H15 encerrou o gatilho "E11 volta se o E14 certificar OPT = UB". Esta tarefa é a linha desacoplada do parecer. Medir desempenho antes da derivação e do validador viola o critério.

#### T15 — Implementar e validar a família estrutural SC

**Status:** `CONCLUÍDA`
**Depende de:** T6 antes de comparação de desempenho. Na ordem recomendada, depois de T14; a construção do gerador não espera o fim de T14.

**Descrição:** Criar SC-GF2 e seu gêmeo rígido para separar efeitos de gap da relaxação e simetria.

**Critérios de aceite:**

- Gerador SC-GF2(k) implementado.
- Verificação automática de `OPT=k`.
- Verificação automática da expressão de `LP+C1`.
- Gêmeo rígido preserva tamanho/graus relevantes sem a mesma simetria.
- OPT do gêmeo é certificado por um IP de Set Cover independente.
- `classes_wl` ou mecanismo equivalente registra diferença estrutural.
- Instâncias pequenas reproduzem os resultados esperados.

#### T16 — Executar teste discriminante do núcleo e do CBI

**Status:** `ENCERRADA`
**Depende de:** T1, T10, T9. Só se a linha CBI continuar relevante depois do E12.

**Descrição:** Separar a contribuição do núcleo inteiro, do oráculo e do processo iterativo do CBI, evitando concluir que "CBI venceu" quando o ganho veio apenas do núcleo.

**Critérios de aceite:**

- COMP, núcleo isolado e CBI são executados separadamente.
- Todos recebem o mesmo orçamento total.
- Tempo do primal externo entra no orçamento quando aplicável.
- Número de iterações e cortes é registrado.
- LB produzido pelo núcleo é comparado diretamente com COMP.
- O relatório atribui qualquer ganho ao componente correspondente.

**Nota de estado:** H16 já fez esse desenho em PUC/PUCN e encerrou A2 para Das. Esta tarefa não repete o E12. Aplica-se a famílias novas, se a linha seguir.

#### T17 — Implementar e validar a família estrutural TR

**Status:** `ENCERRADA`
**Depende de:** a linha CBI continuar relevante depois do E12 (H16). Sem isso, o gerador não avança para benchmark.

**Descrição:** Criar os corredores entrelaçados para testar se múltiplos ótimos inviáveis do núcleo degradam o CBI enquanto o COMP permanece simples.

**Critérios de aceite:**

- Gerador `TR(k,L,r,σ)` implementado.
- OPT reproduz `⌈D/r⌉−1`.
- Para casos pequenos, a contagem de ótimos do núcleo é verificada.
- A quantidade de soluções viáveis dentro dos ótimos é medida.
- Variantes com e sem degraus são geradas.
- CBI registra iterações por valor de `R`.
- A tarefa só avança para benchmark se a linha CBI continuar relevante após E12.

#### T18 — Avaliar desagregação all-V como diagnóstico de LP

**Status:** `ENCERRADA`
**Depende de:** nada. Não é candidata a método de produção neste passo.

**Descrição:** Implementar a formulação desagregada apenas como ferramenta de diagnóstico em instâncias pequenas, antes de considerá-la uma alternativa computacional completa.

**Critérios de aceite:**

- Formulação implementada fielmente.
- Comparação inicial restrita a instâncias pequenas.
- LP da desagregada é comparado com LP do COMP.
- Custo em variáveis/restrições é registrado.
- Nenhuma conclusão de desempenho é baseada apenas em força de LP.
- Só há expansão caso apareça ganho estrutural relevante.

Formulação experimental, comparada à base. Não substitui o baseline.

#### T19 — Executar piloto das famílias estruturais

**Status:** `CONCLUÍDA`
**Depende de:** T9, T10, T12, T13, T15 e, onde o critério cita o método, T14, T16 e T17

**Descrição:** Executar a Fase P pré-registrada com BP, SC, HB e TR. O parecer define uma matriz inicial de 33 instâncias e os métodos COMP, BASE-C, núcleo, CBI e posteriormente C6.

**Critérios de aceite:**

- Matriz contém as 33 instâncias previstas.
- Parâmetros são fixados antes de observar resultados.
- COMP, BASE-C e núcleo são executados em todas as células aplicáveis.
- CBI só é executado após a correção/regressão do oráculo.
- C6 só é executado após validação do E11.
- Mesmo orçamento e condições são usados entre métodos.
- Todas as métricas experimentais da Tarefa 9 são persistidas.

#### T20 — Aplicar critérios de promoção ou descarte das famílias

**Status:** `CONCLUÍDA`
**Depende de:** T19

**Descrição:** Evitar continuar investindo em famílias que apenas crescem em tamanho sem revelar um mecanismo estrutural. O parecer já pré-registra critérios de promoção à Fase E.

**Critérios de aceite:**

- As propriedades previstas aparecem em todas as instâncias do piloto.
- O fenômeno aparece em pelo menos 2 dos 3 níveis de tamanho.
- Resultado é reproduzido em 3 seeds quando necessário.
- A família discrimina pelo menos dois métodos ou famílias de cortes.
- Critério específico de BP, SC, HB ou TR é aplicado.
- Decisão final é registrada como `PROMOVER`, `DESCARTAR` ou `REVISAR TEORIA/GERADOR`.
- Critério não é alterado retroativamente depois de observar resultados.

#### T21 — Executar Fase E das famílias aprovadas

**Status:** `CONCLUÍDA`
**Depende de:** T20, T8 (separação desenvolvimento/avaliação), T10

**Descrição:** Expandir somente as famílias que sobreviverem ao piloto, mantendo separação rígida entre desenvolvimento e avaliação.

**Critérios de aceite:**

- Somente famílias aprovadas na Tarefa 20 entram.
- São adicionados dois níveis de tamanho.
- São utilizadas 5 seeds de geração.
- São utilizadas 3 seeds do solver.
- Avaliação usa seeds novas, não usadas no desenvolvimento.
- Construtores/variantes relacionados permanecem no mesmo lado da divisão.
- Nenhum parâmetro é escolhido depois de observar qual método venceu.

### Bloco 4 — Posicionamento científico

#### T22 — Mapear sobreposição com o artigo IJCAI 2026 e atualizar contribuição

**Status:** `CONCLUÍDA` (2026-10-03). Evidência: `docs/technical/reference/overlap-ijcai2026-min-station.md`; spec em `specs/bloco4-posicionamento-cientifico/spec.md`.
**Depende de:** nada para o levantamento. A narrativa do artigo espera o restante do backlog só no que for afirmação de resultado novo.

**Descrição:** Revisar explicitamente o que já aparece no artigo de Das et al. de 2026 e o que permanece contribuição própria do projeto.

**Critérios de aceite:**

- Artigo IJCAI 2026 é incluído na bibliografia do projeto. — Feito: `overlap` §1; `source-map.md` §4; `RESEARCH.md` §7; `project-overview.md` §7.
- É criada uma tabela "resultado do projeto × resultado IJCAI". — Feito: `overlap` §4 (matriz), §4.1 (cortes), §4.2 (classes e parâmetros).
- Matching, `G^r` e argumentos de Hall são comparados. — Feito: `overlap` §4, linhas `G^r`, matching, Hall. Veredito: `SAME`/`IMPLEMENTATION`/`DIRECT CONSEQUENCE`.
- As reduções de Set Cover (Teorema 3) e Bin Packing (Teorema 4) são comparadas com as famílias SC e BP. — Acrescentado na execução (a spec identificou a lacuna): `overlap` §4; BP e SC são instanciações, não construções novas.
- A afirmação da SBPO sobre ausência de PLI é verificada por busca registrada. — Acrescentado: `overlap` §2 (LC-1), §7.1 #1–#2. Resultado: nenhuma PLI para o MIN-STATION no conjunto verificado; a afirmação fica qualificada por escopo e por variante.
- Nenhuma ideia já existente na literatura é apresentada como contribuição inédita. — Feito: `overlap` §6, status `REMOVE` para `G^r`, matching, BP e SC como construções, C1–C2 como teoria.
- São identificadas claramente as contribuições ainda sustentáveis. — Feito: `overlap` §6 (A–M com categoria T1–T5 e status), §6.1 (negativos), §7.5 (mapa de dependência).
- A narrativa do artigo é reorganizada em torno de cobertura × compatibilidade coletiva, conforme proposto no parecer. — **Subsidiado, não executado:** a spec coloca a redação do artigo fora do escopo de T22. O subsídio está em `overlap` §9, com a ligação Set Cover ↔ núcleo de cobertura marcada como interpretativa até existir prova. A redação é tarefa separada.

**Pendências derivadas (edição de documentos científicos, passo posterior à análise):** lista em `overlap` §7.1, itens marcados "Passo posterior" (`base-formulation.md`, `direcoes-pli-min-station.md`, `familias-estruturais.md`, `min-station-domain.md`, `docs/technical/README.md`, `benchmark-v1.md`, ponteiro no parecer §6). Fora do escopo de T22, registradas em `overlap` §7.4: `open-questions.md` Q1 e cabeçalho de `direcoes` ainda dizem que todas as instâncias têm `S ∩ T = ∅`.

---

## Fora do backlog ativo

O parecer pede para não transformar em tarefa agora, e este arquivo obedece:

- novos ajustes da mesma Lagrangeana;
- Benders clássico;
- BC-Y genérico;
- tuning de reverse-delete;
- C5;
- symmetry breaking genérico;
- geração de colunas;
- FPT, modular-width, vertex cover e algoritmo de árvores, até o parâmetro justificar.

Estão na tabela de linhas pausadas ou encerradas, com a evidência que sustenta a pausa.
