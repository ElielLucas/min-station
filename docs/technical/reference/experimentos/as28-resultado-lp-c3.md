# AS28 — Resultado da triagem LP de C3-cut no MIN-STATION

**Data da campanha:** 17/10/2026.  
**Natureza:** relatório pós-execução; não altera nem reinterpreta retroativamente o pré-registro.  
**Branch declarada:** `novos_testes`. **Commit registrado:** `6f9e6e1e60e41876d916ca10fc82dd0aed43c275`. **Modificações rastreadas no manifesto:** `false`.  
**Veredito automático:** `NO_SIGNAL_BOUNDED_POLICY`. **Recomendação científica:** **encerrar a política limitada da AS28**, não promover C3-cut a nova linha principal a partir destes dados e manter **AS26/MIP bloqueados**.  
**Estado da decisão:** recomendação técnica pós-campanha; eventual aprovação final da estratégia fica a cargo do pesquisador e de revisão independente.

## 1. Objetivo e protocolo congelado

Pergunta: C3-cut individual por origem/destino, aplicado incrementalmente à relaxação COMP+K, consegue ganho LP material e barato nas instâncias **principais de desenvolvimento** do problema de Das?

O plano original (`docs/technical/plans/execucao/as28-preregistro-c3-lp.json`) comparou `U_K` com `U_K_C3` em **seis grafos**, com 90 segundos de tempo total por braço, **até 8 origens e 8 destinos**, **2 rodadas**, **16 cortes por rodada / 32 cortes totais** e tolerância de violação `1e-6`. São **12 braços**. Cada corte proposto por max-flow é verificado contra o alcance topológico via BFS antes de ser adicionado. O algoritmo **não procura um fecho global C3**.

O gate exigiu ganho LP **≥1%** e custo **≤2×** em **dois grafos brutos independentes**, com ambos os LPs ótimos e varreduras completas da amostra selecionada. O plano previa `NO_SIGNAL_BOUNDED_POLICY` quando pelo menos quatro pares fossem ótimos sem qualquer ganho ≥1%.

## 2. Reprodução e integridade

- Comando local relatado: `poetry run python -m unittest discover -s experiments/cuts -p 'test_*.py' -q` → **253 testes, `OK`**, com Gurobi acadêmico carregado no ambiente do pesquisador.
- Execução: `poetry run python experiments/cuts/run_c3_lp_as28.py --output-dir results/benchmark/as28-c3-lp-001`.
- Arquivos primários: `results/benchmark/as28-c3-lp-001/{manifest,rows,analysis}.json`.
- O manifesto registra escopo LP, parâmetros do solver, hashes dos módulos e commit de origem; na auditoria deste pacote, **os seis hashes dos módulos de código coincidiram** com o conteúdo do ZIP recebido.
- A classificação registrada em `analysis.json` coincide com a saída do runner: **`NO_SIGNAL_BOUNDED_POLICY`**, `paired_optimal=4`, `qualified_raw_graphs=[]`, `mip_automatically_authorized=false`.
- O plano AS28 e os resultados são mantidos como evidência histórica. Não há autorização de reclassificação retroativa.

## 3. Resultados LP (quatro pares ótimos)

| Instância | LP COMP+K | LP COMP+K+C3 | Ganho marginal | Tempo COMP+K / C3 (s) | Razão | Cortes | Varreduras selecionadas completas? |
|---|---:|---:|---:|---:|---:|---:|---|
| PUC CC9 | 27,026786 | 27,029687 | +0,0107% | 2,21 / 1,89 | 0,855× | 14 | Sim |
| PUC BIP42 | 31,706052 | 32,000346 | +0,9282% | 13,71 / 14,40 | 1,050× | 5 | Sim |
| PUCN CC3 | 16,933333 | 16,933333 | 0% | 5,18 / 6,38 | 1,233× | 5 | Sim |
| MAPF Room | 13,200000 | 13,200000 | 0% | 1,26 / 1,75 | 1,391× | 12 | Sim |

**Total:** 36 cortes adicionados nesses quatro braços; 4/6 pares de instâncias com ótimo LP nos dois controles. As varreduras foram completas **somente para os 16 terminais selecionados nas duas rodadas**, sem atingir teto de cortes. A palavra “completa” **não** significa C3 fechado sobre todos os terminais, cortes ou rodadas.

### 3.1 Censuras

- **Vienna I056:** `U_K` ótimo em aproximadamente **87,90 s**, objetivo **8,5**; `U_K_C3` chegou ao mesmo primeiro LP **8,5**, mas retornou `TIME_LIMIT` aos **88,80 s**, por **tempo insuficiente para separar e reotimizar**. Nenhum corte C3 foi adicionado. **Não há comparação final LP certificada**.
- **PUC W3C571:** ambos os braços tiveram `TIME_LIMIT` por teto externo de aproximadamente **90,10 s**; nenhum LP ótimo pareado disponível.

Censuras não são ganhos zero nem evidências de redundância. Não as excluir da descrição do alcance do estudo.

## 4. O caso BIP42 e o limite inteiro: observação importante, mas não avanço sobre LB*

Em BIP42, cinco linhas C3 elevaram o LP de **31,706052** para **32,000346**, o que é expressivo em comparação com o **teto inteiro da própria relaxação**:

\[
\lceil31{,}706052\rceil=32,\qquad
\lceil32{,}000346\rceil=33.
\]

Pelo critério numérico de teto usado no projeto, `ceil(LP−1e-6)` também muda de **32** para **33**. Esse salto requer checagem de estabilidade numérica se for utilizado como certificado individual; o resultado provém de LP solucionado numericamente pelo Gurobi.

**Entretanto, o limite inferior inteiro oficial do projeto para `puc-bip42p-regiao-f2` é LB*=35**, no relatório `docs/technical/reference/experimentos/resultados-linha-de-base.md`. Portanto, **33 não supera 35**. É ganho de uma relaxação particular, mas **não é novo recorde de limite inferior do MIN-STATION** para a instância.

### 4.1 Comparação com melhores limites existentes

| Instância | Teto inteiro de COMP+K+C3 (numérico) | LB* oficial anterior | Supera LB*? |
|---|---:|---:|---|
| PUC CC9 | 28 | 30 | Não |
| PUC BIP42 | 33 | 35 | Não |
| PUCN CC3 | 17 | 18 | Não |
| MAPF Room | 14 | 16 | Não |

**Comparabilidade:** LB* é um envelope histórico de **MIP/bounds** de outros braços e orçamentos, enquanto a AS28 mede **LP pareado com 90 s por braço**. Essa comparação serve para atribuir a **relevância do fortalecimento** perante o estado da arte *interno*, mas **não** para declarar que a comparação LP pareada foi inválida ou que C3 perdeu um confronto cronometrado com o método que gerou LB*.

## 5. Interpretação dos efeitos

1. **C3 detecta violações reais na política limitada.** Em CC9 foram 14 cortes e ganho pequeno; em BIP42, cinco cortes trouxeram ganho de 0,9282%; em CC3 e MAPF foram adicionados cinco e 12 cortes, respectivamente, **sem ganho no objetivo final**. Esses dois últimos casos ilustram que cortar pontos fracionários não garante elevar o ótimo LP.
2. **Separação barata nos quatro pares avaliáveis**, relativamente ao trabalho histórico de FC-R: os tempos medidos da separação C3 foram aproximadamente **0,21 s (CC9), 0,37 s (BIP42), 1,23 s (CC3), 0,47 s (MAPF)**. Isso não remove os custos de preparação de K nem as censuras de grafos grandes.
3. **BIP42 é o único sinal próximo do gate**, mas não o atinge e não excede LB*. A observação justifica guardar os cortes e a evidência, não aumentar retrospectivamente o número de terminais ou rodadas.
4. **Escopo limitado:** oito origens e oito destinos fixos, sem seleção adaptativa, duas rodadas. O experimento não prova redundância, fecho ou ausência de potencial de toda família C3.
5. **Sem autorização de MIP:** nenhuma métrica de nós, incumbente ou desempenho branch-and-bound foi medida. A AS26 permanece bloqueada.

## 6. Decisão sugerida e próximo trabalho

**Recomendação: STOP da política delimitada AS28.** Não otimizar o separador, ampliar instâncias, alterar limiar ou iniciar MIP somente porque BIP42 se aproximou de 1%. O protocolo exige dois grafos independentes com sinal; nenhum alcançou 1%.

O aprendizado científico preservável é que **C3-cut é válido e computacionalmente barato na amostra examinada**, mas **o fortalecimento incremental do objetivo foi insuficiente e não superou os limites inferiores históricos**. Preservar código e artefatos como controle para microexperimentos futuros, sem promover a família como nova linha principal.

**Próxima frente sugerida:** revisão curta das alternativas de **formulação/decomposição/algoritmos exatos**, diagnosticando quais relaxações e mecanismos realmente podem ultrapassar COMP+K e o envelope LB* existente. Essa revisão deve considerar os experimentos anteriores (F-CC, F-C3, CG/zero-half, H2, HL e FC-R) e escolher uma única hipótese falsificável antes de criar novas specs. Não há direção substituta pré-aprovada por este relatório.

**Pendências para encerramento administrativo:** anexar este relatório e os três JSONs ao projeto, atualizar status da AS28, realizar parecer independente se o pesquisador julgar necessário e registrar explicitamente a decisão de não promover C3-cut. Nada altera o pré-registro congelado.

## 7. Fontes

- `results/benchmark/as28-c3-lp-001/analysis.json` — resultado oficial do analisador.
- `results/benchmark/as28-c3-lp-001/rows.json` — métricas e status de cada braço.
- `results/benchmark/as28-c3-lp-001/manifest.json` — identidade, ambiente, orçamento e hashes.
- `docs/technical/plans/execucao/as28-preregistro-c3-lp.json` e `.md` — gate anterior à execução.
- `specs/as-28-c3-cut-triagem-lp/{spec,design,tasks,validation}.md` — escopo e salvaguardas.
- `docs/technical/reference/experimentos/resultados-linha-de-base.md` — LB* histórico e proveniência.
- `docs/technical/reference/experimentos/as251-diagnostico-fcr.md` — contexto de FC-R, sem comparador experimental novo.

> **Regra de leitura:** os números LP são retirados dos JSONs executados. As interpretações e a recomendação STOP são elaboradas neste relatório; não constam de uma prova automática de redundância global de C3.
