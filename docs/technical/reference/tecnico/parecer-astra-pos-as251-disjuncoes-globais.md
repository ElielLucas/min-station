# Parecer Astra pós-AS25.1 — Encerramento FC-R e disjunções conjuntas globais

> **Tipo:** parecer externo de pesquisa, organizado a partir da análise fornecida em 17/10/2026.  
> **Autoria das conclusões e verificações relatadas:** Astra. **Organização editorial:** ChatGPT.  
> **Branch/commit analisado pelo Astra:** `novos_testes@ee5eb9d54ad6246a88536f038e3dbda1feec8693`.  
> **Status:** proposta sob revisão independente, **não** nova spec, prova independente ou autorização de implementação.  
> **Veredito:** **C — encerrar FC-R como linha principal e manter AS26 bloqueada**.

## 1. Resumo executivo

FC-R é válido e não redundante ante COMP+K. A AS25.1 removeu um gargalo real de preparação das regiões, preservando cortes equivalentes, mas o ganho marginal de LP permaneceu pequeno nos casos efetivamente comparáveis. O fechamento numérico sem tetos da **subfamília investigada** não equivale ao fechamento da família FC-R para todo `L ⊆ V`.

Astra recomenda um **diagnóstico limitado** de disjunções conjuntas de grupos de estações que preservem todas as linhas globais de COMP+K. A questão principal é se o ganho obtido **depende da informação do fluxo** e é material, ou se apenas recupera arredondamentos já disponíveis no núcleo K.

**Pergunta de pesquisa:** condicionar conjuntamente poucos grupos, preservando COMP+K, fortalece o LP além do efeito de K isolado, por pelo menos 1% em dois grafos brutos, sob custo aceitável?

## 2. Baseline e FC-R

O problema de referência usa o dígrafo de alcance `H=(V,A_r)`, `|S|=|T|=m`, autonomia comum `r`, estações em todo `V`, matching anônimo e estações sem limites físicos de atendimento; `S∩T` é permitido. Se `a_v=1[v∈S]` e `b_v=1[v∈T]`, COMP é:

$$
\min \sum_{v\in V}y_v
$$

$$
f^{out}(v)-f^{in}(v)=a_v-b_v,
$$
$$
f^{in}(v)\le b_v+(m-b_v)y_v,\qquad
f^{out}(v)\le a_v+(m-a_v)y_v,
$$
$$
f\ge0,\quad 0\le y\le1.
$$

No MIP, `y` é binário; o fluxo contínuo pode adquirir solução integral após fixação de instalações, pelas capacidades inteiras da representação em rede. O parâmetro `m` é um limite seguro de fluxo, **não** capacidade física de estação.

O núcleo K implementado compõe-se de C1 (primeiro/último salto), C2 (bandas de distância) e C4-DM (coberturas de deficiências de matching direto). C4-DM não representa todas as condições de Hall em todas as infraestruturas.

Para `d_L=|S∩L|-|T∩L|>0` e `Q ⊆ N_H⁺(L) \ (L∪T)`:

$$
\boxed{f(L,V\setminus(L\cup Q))+d_L y(Q)\ge d_L.}\tag{FC-R}
$$

A seleção ótima de Q **para L fixo e ponto LP dado** é:

$$
Q^*=\{v\in N_H^+(L)\setminus(L\cup T):f^*(L,\{v\})>d_L y_v^*\}.
$$

A versão FC-R-T é simétrica. FC-R decorre da disjunção `y(Q)=0 ∨ y(Q)≥1`, admite circulações e não fixa o pareamento origem/destino. A otimização em Q **não** resolve a seleção global de regiões L.

## 3. Evidência experimental AS25.1

**Fonte primária para revalidação:** `results/benchmark/as251-fcr-lp-001/rows.json`. O Astra afirma ter recalculado a classificação. Os números aqui reproduzem seu parecer e não substituem os JSONs.

| Caso | COMP+K LP | COMP+K+FC-R LP | Ganho | Tempo K / FC-R (s) | Cortes |
|---|---:|---:|---:|---:|---:|
| CC9 | 27,026786 | 27,056244 | 0,1090% | 1,81 / 4,54 | 128 |
| BIP42 | 31,706052 | 31,714021 | 0,0251% | 25,11 / 20,60 | 128 |
| CC3 | 16,933333 | 16,933333 | 0% | 7,03 / 9,66 | 128 |
| MAPF Room | 13,200000 | 13,280000 | 0,6061% | 1,75 / 3,02 | 51 |
| Vienna | censurado | censurado | indeterminado | ~90 / ~90 | — |
| W3C571 | censurado | censurado | indeterminado | ~90 / ~90 | — |

- 24 braços; nove censuras (oito em Vienna/W3C571 e uma na infraestrutura antiga de CC3).
- `classification=B` na AS25.1 e `as25_reference_gate=INVESTIGATE`: **não** foi emitido `STOP` pelo analisador.
- AS26 permanece bloqueada; decisão C é **juízo científico do Astra** posterior, não saída automática do gate.

### 3.1 Diagnóstico sem tetos usuais (apenas subfamília testada)

| Caso | Fecho numérico LP | Ganho sobre K | Cortes: singletons / singletons + 12 pares |
|---|---:|---:|---:|
| CC9 | 27,082111 | 0,2047% | 267 / 344 |
| BIP42 | 32,077607 | 1,1719% | 5.089 / 5.203 |
| CC3 | 16,933333 | 0% | 1.067 / 1.385 |
| MAPF | 13,280000 | 0,6061% | 73 / 232 |

Em BIP42, o primeiro ganho ≥1% aparece na rodada 13, após 2.506 linhas e cerca de 79 s de laço além da preparação; o fechamento consumiu aproximadamente **406 s de reotimização LP**. Após o novo índice, o principal custo residual é resolver a sequência de LPs com muitas linhas.

**Limitações:** (i) apenas singletons e até 12 pares escolhidos foram investigados, não regiões gerais; (ii) varrer regiões antes da reotimização não prova fechamento após novo ótimo; (iii) overhead >100% pode surgir da diferença entre tempos de braços distintos e não indica economia física superior a 100%; (iv) documentos históricos AS25/AS25.1 ainda podem dizer “não executada”, em desacordo com JSONs; (v) a complexidade anunciada de `fast_region_plan` omite potencialmente enumeração de pares de terminais `Θ(m²)`; (vi) nos seis casos `S∩T=∅`, e a maior autonomia está censurada.

## 4. Decisão científica sobre FC-R

| Alternativa | Favorável | Contrário | Avaliação Astra |
|---|---|---|---|
| A — continuar | Regiões gerais não exploradas | Nenhuma hipótese sustentada de ganho substancial | Não justificada |
| B — última investigação restrita | BIP42 excede 1% no fecho | Caso único, milhares de linhas, custo elevado | Não prioritária |
| **C — encerrar linha principal** | Retorno marginal baixo depois de corrigir principal gargalo | Não prova fraqueza universal | **Recomendada** |

BIP42 alcançou `32,077607`; caso esse limite LP seja **certificado**, o arredondamento do limite inferior inteiro fornece 33. Tal observação pode ser útil, mas não estabelece ganho frente aos cortes automáticos do solver nem justifica AS26.

Preservar AS23, AS24, AS25/AS25.1, provas, scripts e resultados como contribuição e controles. Não atribuir ao encerramento uma afirmação de redundância ou inutilidade universal.

## 5. Lacunas estruturais de COMP+K

1. Ativação fracionária de trânsito por coeficientes `m` no fluxo.
2. Compatibilidade global de matching físico que coberturas locais não garantem integralmente.
3. Escolhas de instalação fracionárias que satisfazem alternativas individualmente, mas não uma escolha **inteira conjunta**.

FC-R atua parcialmente no primeiro mecanismo, não necessariamente no terceiro.

Para HL local, seja `Φ_R={χ_{C∩R}: C instalação física viável}`. Se `V\R` já é viável, monotonicidade implica `Φ_R={0,1}^R` e `conv(Φ_R)=[0,1]^R`. Portanto **nenhum corte apenas nas variáveis y_R dentro da caixa** consegue separar uma solução fracionária. A próxima abordagem não pode tratar as estações externas como instaladas gratuitamente; deve preservar as linhas globais.

## 6. Famílias candidatas

### 6.1 Disjunções conjuntas com COMP+K global — prioridade de diagnóstico

Explorar duas decisões de grupos de estações simultaneamente, condicionando a soma de instalações por grupo e mantendo fluxo e coberturas globais. Trata-se de **programação disjuntiva clássica**, não uma técnica nova. A possível contribuição é especialização e eficácia comprovada para MIN-STATION. **Risco decisivo:** o ganho já ser obtido pelo fecho inteiro ou arredondamentos de K.

### 6.2 Projeção de F-CC — reserva, com gargalo de pricing

Para `α_s,β_t∈ℝ`, `γ_v≥0`, impondo

$$
\alpha_s+\beta_t\le0\quad\forall (s,t)\in D,
$$
$$
\alpha(I)+\beta(J)\le\gamma(W)\quad\forall (W,I,J)\in\mathcal Q,
$$

segue a desigualdade válida

$$
\boxed{\sum_v\gamma_v y_v\ge\sum_s\alpha_s+\sum_t\beta_t.}
$$

A prova multiplica atendimentos da F-CC e aplica limites de ativação. A condição **para toda configuração q** requer pricing certificado; usar somente uma subcoleção não prova validade. A testemunha abaixo também admite solução F-CC fracionária de valor 2, segundo o Astra, logo não comprova superioridade desta alternativa.

### 6.3 Extensão FC-R com absorção em destinos — validade alegada, sem prioridade

Para `Q⊆N_H⁺(L)\L`, `k=|Q∩T|`, `δ=d_L-k>0`:

$$
\boxed{f(L,V\setminus(L\cup Q))+\delta y(Q)\ge\delta.}
$$

Se `y(Q)=0`, destinos em Q absorvem no máximo k; caso `y(Q)≥1`, a parcela `δy(Q)` basta. A simétrica desconta `|Q∩S|`. Para `d_L=1`, `k=0`, de modo que não amplia os singletons. Não há prova de ganho adicional sobre FC-R completo, portanto não priorizar.

## 7. Formulação proposta para disjunções conjuntas

Defina a relaxação global implementada `P={x=(y,f): Ax≥b}`, incluindo COMP, K, não negatividade e caixa, com `c₀ᵀx=Σ_v y_v`. Igualdades podem ser escritas como pares de desigualdades.

Escolha `p∈{1,2}` grupos não vazios `B_i⊆V`, inicialmente disjuntos, e `q_i=π_iᵀx=Σ_{v∈B_i}y_v`. Para qualquer inteiro `k_i`, soluções inteiras satisfazem

$$
q_i\le k_i\quad\lor\quad q_i\ge k_i+1.
$$

No caso `k_i=0`, os estados são **nenhuma estação** e **pelo menos uma**; o segundo não equivale a exatamente uma.

Para `σ∈{0,1}^p`:

$$
g_{\sigma i}=(2\sigma_i-1)\pi_i,\qquad
h_{\sigma i}=(2\sigma_i-1)k_i+\sigma_i,
$$
$$
P_\sigma=\{x\in P:g_{\sigma i}^\top x\ge h_{\sigma i},\ i=1,\ldots,p\}.
$$

Toda solução inteira pertence a um termo. Assim, desigualdades válidas para `conv(∪_σ P_σ)` são válidas para MIN-STATION.

### 7.1 Certificado por multiplicadores

Para cada termo **não vazio**, `u_σ≥0`, `v_{σi}≥0`, e coeficientes comuns `c,β`:

$$
c=A^\top u_\sigma+\sum_i v_{\sigma i}g_{\sigma i},
$$
$$
\beta\le b^\top u_\sigma+\sum_i v_{\sigma i}h_{\sigma i}.
$$

Conclui-se que `cᵀx≥β` é válido em todos os termos. Para separar `x*`, maximizar `β−cᵀx*` com uma normalização, por exemplo

$$
\sum_\sigma(\mathbf1^\top u_\sigma+\sum_i v_{\sigma i})\le1.
$$

Termos inviáveis exigem **certificado de inviabilidade**; cortes numéricos devem passar por auditoria das identidades e desigualdades, preferencialmente racional. **LP exato para grupos fixos** não significa seleção exata global dos grupos.

FC-R pode ser recuperado por disjunções gerais `y(Q)=0 ∨ y(Q)≥1`, mas uma política restrita de pares de grupos **não domina necessariamente** o separador existente. Revisar tecnicamente a extensão dessa afirmação.

## 8. Testemunhas matemáticas declaradas pelo Astra

### 8.1 K4 de grupos: FC-R não fecha a lacuna

Quatro grupos `X₁,...,X₄` de `b` relés. Para cada `1≤i<j≤4`, há uma origem `s_ij` e um destino `t_ij`, cada qual adjacente a todos os relés em `X_i∪X_j` e sem outras arestas. `r=1`, `|S|=|T|=6`, `|V|=12+4b`, estações em todo V.

Uma instalação viável exige pelo menos três grupos ativos (dois vazios deixariam o respectivo par descoberto); três bastam. Então `OPT=3`.

K contém `q_i+q_j≥1` para os seis pares, onde `q_i=y(X_i)`. Com `y_v=1/(2b)` em cada relé e zero nos terminais, e fluxo `f_{s_ij,v}=f_{v,t_ij}=1/(2b)` para cada `v∈X_i∪X_j`, cada par transporta uma unidade; o objetivo LP é 2 e satisfaz COMP e K. O Astra afirma que satisfaz **todos** os FC-R/FC-R-T, inclusive para regiões arbitrárias, pois cada fluxo de um par em um relé é no máximo `y_v` e as trajetórias que atravessam a fronteira cobrem o saldo. Logo é alegado `z(COMP+K+todos FC-R)=2 < OPT=3`.

### 8.2 Variante H2 e HL local

Suba as instalações fracionárias para `y_v=2/(3b)`, mantendo os fluxos. As somas por grupo são `q_i=2/3` e objetivo `8/3`. Segundo o Astra, isso satisfaz todos FC-R e todos H2. Para `b=5` há 32 vértices, e qualquer suporte de ≤8 vértices deixa pelo menos três grupos presentes no complemento; logo não existe corte HL **restrito a esses suportes**.

A disjunção conjunta de `X₁` e `X₂` tem termos:

| Estado | Consequência de K |
|---|---|
| `q₁=0,q₂=0` | inviável (`q₁+q₂≥1`) |
| `q₁=0,q₂≥1` | `q₂,q₃,q₄≥1` |
| `q₁≥1,q₂=0` | `q₁,q₃,q₄≥1` |
| `q₁≥1,q₂≥1` | `q₃+q₄≥1` |

Todos os termos implicam

$$
\boxed{y(X_1\cup X_2\cup X_3\cup X_4)\ge3.}
$$

A violação no ponto `8/3` é `1/3`. **Limitação essencial:** esta é uma cobertura de `K₄` que também pode resultar de arredondamentos sucessivos de K; logo **não constitui testemunha de novidade física além do núcleo inteiro K**.

### 8.3 Uso genuíno do fluxo numa microinstância

No microcaso AS23, condicionando grupos `X₁` e `X₂` com o modelo global, os quatro termos têm ótimos LP relatados de `3/2`, `7/6`, `7/6` e `2`. O mínimo é `7/6>1`, enquanto o núcleo K admitiria inteiro 1. Astra afirma ter rechecado certificados primais/duais racionais; o efeito é, porém, inferior a fortalecimentos anteriormente conhecidos e **não** evidencia superioridade prática.

### 8.4 Verificações relatadas, ainda não reproduzidas por esta documentação

- Linhas reais de `compile_u` e K verificadas racionalmente para `b=1` e `b=5`.
- **50.752** regiões de saldo não nulo e Q ótimo para b=1, duas orientações.
- Oráculo de viabilidade para **137** instalações com ≤2 estações no caso de 16 vértices e **529** no caso de 32; todas inviáveis; instalações com 3 verificadas.
- Certificados algébricos dos estados e dos casos H2 por simetria.
- Quatro LPs AS23 resolvidos com HiGHS e rechecados com certificados racionais.

Esses números e provas são **alegações documentadas do Astra**. Uma revisão independente deve reproduzi-los ou marcar explicitamente o que permanece não demonstrado.

## 9. Diagnóstico antes de desenvolver um separador

Para **uma disjunção fixa**, e o objetivo original `c₀`, vale:

$$
\boxed{\min_{x\in\operatorname{conv}(\cup_\sigma P_\sigma)}c_0^\top x
=\min_\sigma \min_{x\in P_\sigma}c_0^\top x.}
$$

Até **quatro LPs** medem o melhor limite objetivo da **disjunção isolada**. Se um termo ainda tem ótimo igual à baseline, essa disjunção isolada não melhora o objetivo, embora possa separar o ponto LP corrente ou interagir com outras disjunções.

Plano exploratório: (1) agrupar vértices por perfil de incidência nas linhas K; (2) escolher grupos com `q_i` fracionário; (3) priorizar pares que interajam em K ativo, com regra congelada; (4) resolver até quatro termos com COMP+K completo **e** somente K+caixa; (5) controlar CG/zero-half/arredondamentos e limite inteiro de K; (6) somente com potencial material, estudar o gerador de cortes; (7) censurar/abster-se sob falta de certificação, sem inventar resultados.

**Importante:** quatro termos para dois grupos não são `2^{|B₁∪B₂|}` estados, mas os quatro LPs ainda podem ser grandes em Vienna e outros grafos difíceis. A escolha de pares é heurística.

## 10. Etapas e critérios de parada propostos (não registrados como spec)

| Etapa | Evidência | Go | Stop |
|---|---|---|---|
| 1. Auditoria matemática | Provas, termos, certificados, `S∩T` | Validade sem ambiguidade | Corte exclui instalação viável |
| 2. Atribuição do mecanismo | COMP+K vs. somente K, controles históricos | Evidência de informação nova do fluxo | Ganho só do núcleo K/limite já disponível |
| 3. Potencial sem separador | Até quatro LPs por par e poucos pares pré-selecionados | **≥1% em dois grafos brutos** com custo aceitável | Só sintéticos, ganho pequeno, muitos timeouts |
| 4. Separador + LP | Cortes certificados, benchmarks pareados | Ganho replicado e custo competitivo | Muitas linhas e ganho marginal |
| 5. MIP condicional | Sinal LP prévio e controles solver | Aprovação explícita | Sem ganho na raiz ou piora do B&B |

Critério 1%/dois grafos é **proposição prospectiva**. Censuras não são ganhos iguais a zero. Evitar vazamento de instâncias reservadas. Validar `S∩T≠∅`, não alterar COMP+K e não reabrir AS26 sem gate.

## 11. Perguntas obrigatórias para auditoria independente

1. A construção de K4 realmente satisfaz **todos** FC-R/FC-R-T, inclusive para L gerais, com prova independente?
2. `OPT=3`, objetivo 2 e variante 8/3 estão demonstrados para todo b? Que partes só foram enumeradas?
3. O ganho sobre H2/HL é genuíno ou artefato do suporte e da definição da família?
4. A desigualdade de K4 é CG/zero-half/fecho inteiro K já conhecido? Qual é o **rank** e o custo de separação?
5. Na testemunha AS23, `7/6` depende de COMP e é superior ao que K e seus fortalecimentos históricos já obtêm?
6. O certificado dual de `cᵀx≥β` tem sinais, normalização, tratamento de igualdade e dos termos vazios corretos?
7. O diagnóstico por quatro LPs é suficiente como gate **para disjunções isoladas**, sem confundi-lo com interseção de disjunções?
8. Quão caros seriam os termos, mesmo sem gerar cortes? Como lidar com status não ótimos e custos sobrepostos?
9. Existe outra direção com melhor plausibilidade matemática que a disjunção? Ou seria melhor considerar nova formulação/decomposição?
10. Como atualizar documentação histórica sem reescrever dados, e preservar decisão científica separada do gate automático?

## 12. Conclusão do parecer

**Encerrar FC-R como linha principal** significa interromper novas otimizações dessa família sob a evidência disponível, preservando provas e separador. **Não significa afirmar redundância ou fraqueza universal.** O próximo passo sugerido não é implementar imediatamente uma família nova, mas verificar o **potencial discriminante** de poucos pares de grupos com COMP+K completo, comparado ao núcleo K e a cortes já conhecidos. Se nada material depender de fluxo, parar também essa linha e reavaliar outras formulações, decomposição ou métodos exatos.

## 13. Fontes e roteamento interno

- Parecer anterior: [`parecer-astra-fcr-pos-as22.md`](parecer-astra-fcr-pos-as22.md).
- Plano AS23–AS27: [`plano-fcr-as23-as27.md`](../../plans/execucao/plano-fcr-as23-as27.md).
- AS25.1: [`as251-diagnostico-fcr.md`](../experimentos/as251-diagnostico-fcr.md).
- Dados: `results/benchmark/as251-fcr-lp-001/rows.json` e `results/benchmark/as251-diagnostico-001/`.
- Referência teórica F-CC/F-C3: `docs/technical/reference/formulacoes/`.
- Contexto: `RESEARCH.md`, `docs/context-ai/base-formulation.md`, `experiments/alternative-formulations/as02_model_a.py`, `experiments/cuts/cuts.py`.
- Das et al., IJCAI 2026: https://www.ijcai.org/proceedings/2026/0009.pdf
- Programação disjuntiva (referência citada pelo Astra, bibliografia a conferir): https://link.springer.com/article/10.1007/BF01581273
- Desigualdades de três partições em redes (referência citada pelo Astra, aplicabilidade não estabelecida): https://users.iems.northwestern.edu/~simge/Preprints/TPI-Net16.pdf

**Rastreabilidade:** a publicação deste parecer não altera status de tarefas, dados, scripts, provas ou gates. Nenhum experimento novo foi executado na elaboração editorial deste documento.
