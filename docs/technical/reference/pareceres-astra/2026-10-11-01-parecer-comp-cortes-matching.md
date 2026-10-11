**Eu retiraria a F-CC+K explícita do papel de método principal para o benchmark difícil. Priorizaria o COMP+K, com um fortalecimento implícito que preserve sua capacidade de iniciar e continuar a otimização sob orçamento.** A F-CC continuaria como referência matemática e como controle em instâncias pequenas.

Isso não significa que já exista evidência de superioridade da alternativa que proponho. Significa que ela oferece uma pergunta científica mais viável para a próxima fase: **quanto da informação de conectividade e pareamento conseguimos incorporar ao compacto sem pagar pela enumeração de configurações?**

Analisei a branch `novos_testes` no commit [`e25b056`](https://github.com/ElielLucas/min-station/commit/e25b056e2faab88afb9a56769d33fb90704e4440). Não alterei arquivos do projeto nem executei otimizações. Executei auditorias de artefatos, a verificação existente de identidade entre instâncias e duas verificações algébricas com aritmética racional.

## 1. Diagnóstico executivo

Sua interpretação da FC-06 está **essencialmente correta**: a seleção ficou sem candidatos porque seu universo já estava condicionado à tratabilidade da F-CC explícita.

Há três problemas distintos.

**Primeiro: seleção experimental condicionada à representação.** Em `fc_instances.py`, `MAIN_NAMES` contém seis instâncias escolhidas pela tratabilidade da enumeração. Em `fc06_campaign.py`, `choose_instances()` proíbe selecionar nomes fora desse conjunto. Além disso, `pair_screening()` exige modelos completos dos dois braços.

Assim, uma instância difícil na qual a F-CC não consegue ser construída fica impedida de justificar a campanha longa. Essa regra protege uma comparação de modelos completos, mas não responde à pergunta mais ampla sobre aplicabilidade aos casos difíceis.

**Segundo: explosão da representação.** O problema não se limita a uma implementação ingênua de todas as combinações \((W,I,J)\). **O braço atual já usa a forma separada**:

\[
\lambda_W,\qquad \alpha_{sW},\qquad \beta_{tW}.
\]

Mesmo assim, HB-q5 produz aproximadamente **2,39 milhões de variáveis**, contra **93** no COMP. Portanto, recomendar simplesmente “usar a forma separada” seria recomendar algo que já está implementado.

**Terceiro: confundiram-se, em alguns documentos, exatidão matemática e enumeração explícita.** O protocolo afirma que somente a construção completa enumerada permite uma comparação exata. Essa afirmação é excessiva: uma representação implícita, acompanhada de separação ou pricing adequados, também pode resolver o modelo completo. A dificuldade está em fornecer as garantias necessárias, não em materializar antecipadamente todas as variáveis.

**Decisão:** a FC-06 agiu corretamente dentro de seu contrato, mas esse contrato é estreito demais para orientar a próxima contribuição do mestrado.

## 2. Evidências do repositório

### Resultados FC efetivamente confirmados

Confirmei os seis pares do arquivo [`main-20261011T005611Z/results.csv`](https://github.com/ElielLucas/min-station/blob/e25b056/results/formulation-comparison/main-20261011T005611Z/results.csv):

| Instância | COMP+K, tempo total | F-CC+K, tempo total | Objetivo numérico de ambos |
|---|---:|---:|---:|
| HB-q4-ndir2-p1 | 0,736 s | 5,560 s | 2 |
| BP-nao-q2-B2 | 0,688 s | 2,878 s | 7 |
| HB-q5-ndir2-p1 | 0,693 s | 100,585 s | 3 |
| HB-q6-ndir1-p6 | 0,668 s | 103,815 s | 1 |
| BP-sim-q2-B2 | 0,717 s | 6,230 s | 8 |
| BP-nao-q2-B3 | 0,825 s | 77,278 s | 9 |

Todos aparecem como `OPTIMAL`, `PAIR_VALID`, com UB físico validado.

O **HB-q6 da FC não é o HB-q6 da N2**:

- FC: `hb-q6-ndir1-p6-k1-L2`, com 23 vértices;
- N2: `HB-q6-ndir2-p1`, com 26 vértices.

Os objetivos 1 e 3 não constituem uma divergência entre métodos na mesma instância.

A decomposição de tempo também é informativa:

| Instância, braço F-CC+K | Construção | Solver |
|---|---:|---:|
| HB-q5 | 53,53 s | 44,87 s |
| HB-q6-ndir1-p6 | 56,55 s | 45,00 s |
| BP-nao-q2-B3 | 44,26 s | 31,09 s |

Logo, **a preparação pesa muito, mas o modelo grande também encarece a resolução**. Otimizar apenas o enumerador não eliminaria todo o custo observado.

### Arquivos que sustentam o diagnóstico

| Arquivo ou função | Constatação |
|---|---|
| [`fcc.py::enumerar_conexos`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/alternative-formulations/fcc.py) | Enumera conjuntos conectados e mantém conjuntos visitados, fila e saída em memória. |
| [`fcc_k.py::build_fcc_plus_k`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/alternative-formulations/fcc_k.py) | Chama explicitamente `forma='separada'`; a explosão observada já ocorre nessa representação. |
| [`fc_instances.py`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/formulation-comparison/fc_instances.py) | Define o universo MAIN pela tratabilidade da enumeração. |
| [`fc06_campaign.py`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/formulation-comparison/fc06_campaign.py) | Restringe a seleção a MAIN e exige completude de ambos os modelos. |
| [`fc_core.py`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/formulation-comparison/fc_core.py) | Compara COMP com fluxo contínuo e F-CC+K, usando o mesmo K e validação física. |
| [`n2_t3_cert_integration.py`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/alternative-formulations/n2_t3_cert_integration.py) | Integra N2-box com multiplicadores nulos; não chama o gerador de multiplicadores otimizados. |
| [`desagregacao.py`](https://github.com/ElielLucas/min-station/blob/e25b056/experiments/alternative-formulations/desagregacao.py) | Já contém uma formulação por origem; sua alegação documental de dominância LP exige correção, conforme demonstrarei. |

Há também uma limitação operacional para a próxima campanha: `run_comparison.py` materializa as instâncias e seus arcos de alcance **antes** dos braços supervisionados. Esse custo é registrado em `shared_instance_loading_wall_s`, mas não integra o `wall_total_s` individual.

Isso é pouco relevante nos seis casos minúsculos. Nos grafos grandes, deve entrar explicitamente no orçamento e na medição de memória.

### Verificações realizadas nesta revisão

- Auditor FC-04 sobre MAIN: **`PASS`, sem problemas**.
- Verificador do piloto corrigido: **`READY_FOR_EXTENDED`**, com auditoria de artefatos aprovada.
- `verify_lote1a.py`: confirmou as equivalências esperadas entre instâncias antigas e normalizadas.
- Verificações racionais de dois exemplos matemáticos: executadas.
- Novos solves, pilotos ou campanhas: **não executados**.

Essas auditorias conferem os contratos e artefatos examinados. Não transformam os resultados do Gurobi em provas racionais independentes.

## 3. Avaliação das formulações existentes

### Formulação base e COMP+K

A base usa o dígrafo de alcance \(A_r\), instalação \(y_v\) e fluxo agregado \(f\). Com \(a_v=1_{v\in S}\), \(b_v=1_{v\in T}\) e \(m=|S|\), suas restrições centrais são:

\[
\operatorname{out}(v)-\operatorname{in}(v)=a_v-b_v,
\]

\[
\operatorname{in}(v)\le b_v+(m-b_v)y_v,
\]

\[
\operatorname{out}(v)\le a_v+(m-a_v)y_v.
\]

O COMP utiliza essa estrutura com fluxo contínuo e os cortes K. A equivalência física para \(y\) binário é a propriedade relevante; não é necessário tornar todo o fluxo inteiro para representar o problema.

O tamanho é da ordem de:

\[
O(|V|+|A_r|)
\]

variáveis, além dos cortes. Isso explica sua capacidade de efetivamente processar os grafos do benchmark, embora não garanta bons gaps.

A fraqueza LP é concreta: uma instalação fracionária pode suportar fluxo agregado proporcional a \(m y_v\). Entretanto, **não se pode atribuir todo gap observado ao big-M**. Também interferem:

- qualidade das incumbentes;
- estrutura de cobertura dos cortes K;
- conectividade necessária entre recargas;
- compatibilidade global do pareamento;
- comportamento de presolve, cortes internos e busca.

O E13 mostrou que incumbentes podiam melhorar. Não demonstrou que os limites inferiores fossem suficientemente fortes.

### F-CC+K

A exatidão inteira e a relação com a base estão justificadas pelas construções de rotas e matching apresentadas em [`provas-fcc-fc3.md`](https://github.com/ElielLucas/min-station/blob/e25b056/docs/technical/reference/formulacoes/provas-fcc-fc3.md).

Com a família completa de configurações e o mesmo K:

\[
z_{\mathrm{LP}}(\text{base})
\le
z_{\mathrm{LP}}(\text{COMP+K})
\le
z_{\mathrm{LP}}(\text{F-CC+K})
\le
OPT.
\]

O argumento essencial é que cada configuração pode ser decomposta em caminhos simples entre uma bijeção de suas origens e destinos. Somando essas contribuições, obtém-se um fluxo admissível na base, preservando \(y\).

**Essa dominância LP não implica dominância computacional.** A FC forneceu exemplos claros disso: melhor informação na relaxação pode vir acompanhada de milhões de variáveis e custo total muito maior.

Também não implica dominância sobre o **núcleo inteiro**. O projeto contém exemplos em que o núcleo inteiro supera o LP da F-CC+K.

Minha avaliação é:

- **valor matemático:** estabelecido;
- **ganho de relaxação em casos específicos:** observado;
- **vantagem como método geral para instâncias difíceis:** não demonstrada;
- **representação explícita como caminho principal:** inadequada para o objetivo atual.

### O que a N2 realmente demonstrou

A N2 permaneceu corretamente encerrada como `N2 FAIL`.

Os registros mostram:

- RMP numericamente estacionário;
- limites publicados provenientes do certificador N1;
- ENUM desativado na execução prospectiva;
- N2-box integrado com multiplicadores nulos;
- parada muito antes de consumir o orçamento;
- ausência de ganho certificado sobre B0.

Isso **não demonstra fraqueza intrínseca da F-CC+K**. Demonstra que a combinação implementada de geração de colunas, certificação e critério de parada não entregou o limite exigido.

Há duas limitações matemáticas especialmente importantes.

**1. N2-box com multiplicadores nulos não oferece a informação estrutural que se pretendia recuperar.**

Para um mesmo vetor dual, com \(\mu\ge0\), o limite analítico é:

\[
\ell_{\mathrm{N1}}
=
\min_v\mu_v-
\max_{1\le k\le m}
\left(
\operatorname{Top}_k(\pi)+\operatorname{Top}_k(\tau)
\right).
\]

Com multiplicadores nulos, a caixa fornece:

\[
\ell_{\mathrm{box},0}
=
-\sum_s\max(0,\pi_s)
-\sum_t\max(0,\tau_t).
\]

Como a soma dos maiores prêmios balanceados não excede a soma de todos os prêmios positivos,

\[
\ell_{\mathrm{box},0}\le \ell_{\mathrm{N1}}.
\]

Portanto, nesse regime, não há fundamento para esperar que N2-box melhore o limite de pricing de N1.

**2. Otimizar os multiplicadores da caixa não resolve automaticamente a conectividade.**

No LP do pricing, considere qualquer \(x\in[0,1]^V\), com

\[
k=\sum_vx_v\ge1.
\]

Escolhendo

\[
\rho_v=\frac{x_v}{k},\qquad g_v=x_v,\qquad f_{uv}=0,
\]

as restrições P3–P5 são satisfeitas. Isso funciona mesmo com suporte de \(x\) desconexo.

Logo, **o bloco relaxado de conectividade não restringe \(x\) além da não vacuidade**. As restrições de elegibilidade continuam presentes, mas a conectividade inteira não foi preservada na relaxação.

Essa é uma limitação estrutural da relaxação usada pelo certificador. Não é simplesmente uma questão de dar mais tempo ao solver.

### Limites globais com geração de colunas

Para minimização:

\[
z_{\mathrm{LP}}(\text{F-CC+K completa})
\le z_{\mathrm{RMP}}.
\]

Assim, o objetivo do RMP isolado não é LB global.

A regra do Teorema L continua sendo uma ferramenta válida quando suas hipóteses são satisfeitas. Com \(L\) calculado pelo vetor dual e pela penalização dos limites superiores de \(y\), defina:

\[
a=\min(0,\ell),
\qquad
\delta=\min\bigl(\{0\}\cup\{-\pi_s-\tau_t:(s,t)\in D\}\bigr),
\]

onde \(\ell\) deve limitar inferiormente o custo reduzido de **todas** as configurações. Então:

\[
LB=
\max\left\{
0,\;
L+m\min(a,\delta),\;
\frac{L+m\delta}{1-a}
\right\}.
\]

O ponto difícil continua sendo obter um \(\ell\) global suficientemente forte.

Um `ObjBound` do pricing de minimização tem a orientação necessária, dentro da evidência numérica do solver. Já o custo de uma coluna encontrada tem a orientação oposta. Uma prova racional independente exige verificação adicional; não surge automaticamente do status do Gurobi. A documentação distingue explicitamente `ObjBound`, `ObjBoundC` e `ObjVal`. [Gurobi Optimizer Reference Manual](https://docs.gurobi.com/projects/optimizer/en/12.0/reference/attributes/model.html?utm_source=chatgpt.com)

## 4. Alternativas matemáticas e algorítmicas

### Uma correção necessária antes de escolher outra formulação

A documentação de [`desagregacao-por-origem.md`](https://github.com/ElielLucas/min-station/blob/e25b056/docs/technical/reference/analise-estrutural/desagregacao-por-origem.md) afirma que a ativação por commodity implica a ativação agregada da base e, portanto, domina seu LP.

**Essa afirmação é falsa para a formulação implementada.**

Considere:

\[
V=\{a,b,c,d\},\quad
E=\{ac,bc,cd\},\quad
S=\{a,b\},\quad T=\{c,d\},\quad r=1.
\]

Na relaxação da desagregação, tome:

\[
y_c=\frac12,\qquad y_a=y_b=y_d=0,
\]

\[
p_{ac}=p_{ad}=p_{bc}=p_{bd}=\frac12,
\]

\[
f^a_{ac}=f^b_{bc}=1,
\qquad
f^a_{cd}=f^b_{cd}=\frac12.
\]

Essa solução satisfaz os balanços e as ativações por origem existentes. Seu custo é \(1/2\).

Na base, cada origem é uma folha e precisa enviar uma unidade a \(c\). Portanto:

\[
\operatorname{in}(c)\ge2.
\]

Como \(c\in T\) e \(m=2\), a base exige:

\[
\operatorname{in}(c)\le1+y_c,
\]

de modo que \(y_c\ge1\). O ótimo LP da base é 1.

Assim:

\[
z_{\mathrm{LP}}(\text{desagregação implementada})
=
\frac12
<
1
=
z_{\mathrm{LP}}(\text{base}).
\]

O erro está no tratamento da unidade que termina em um destino: somar limites por origem não produz automaticamente o coeficiente \(m-1\) da base.

**Isso refuta a dominância LP alegada, não a equivalência inteira.** Também não invalida a prova de dominância da F-CC, que usa um argumento diferente.

### Caminho principal proposto: COMP+K com cortes por origem e matching compartilhado

Minha proposta é **manter integralmente o COMP+K** e acrescentar uma extensão que represente fluxos unitários por origem por meio de cortes, sem materializar \(m|A_r|\) variáveis de fluxo.

Essa é uma proposta de pesquisa nova neste parecer; não estou afirmando que já esteja implementada ou validada experimentalmente.

Escolha um conjunto de origens \(U\subseteq S\). Acrescente:

\[
p_{st}\ge0
\qquad(s\in U,\ t\in T),
\]

\[
\sum_{t\in T}p_{st}=1
\qquad(s\in U),
\]

\[
\sum_{s\in U}p_{st}\le1
\qquad(t\in T).
\]

Quando \(U=S\), as últimas desigualdades tornam-se igualdades por contagem.

Os destinos permanecem livres: **não há pareamento previamente fixado**.

Para cada origem selecionada, considere uma rede auxiliar:

- fonte no porto de saída de \(s\);
- arcos de alcance de \(A_r\);
- arco de trânsito \(v_{\mathrm{in}}\to v_{\mathrm{out}}\) com capacidade \(y_v\);
- saída final de \(t_{\mathrm{in}}\) para o sorvedouro com capacidade \(p_{st}\);
- saída inicial de \(s\) gratuita;
- permanência gratuita com capacidade \(p_{ss}\), quando \(s\in T\).

O trânsito pela própria origem pode ser eliminado: caminhos simples não precisam retornar a ela.

**Um destino somente absorve fluxo gratuitamente; continuar a viagem através dele usa a capacidade de estação.** Essa distinção é indispensável.

A exigência de fluxo unitário equivale, por fluxo máximo–corte mínimo, a desigualdades da forma:

\[
\sum_{v\in Z(A)}y_v+
\sum_{t\in J_s(A)}p_{st}\ge1.
\]

Aqui:

- \(A\) é o lado da fonte de um corte da rede auxiliar;
- \(Z(A)\) contém os arcos de trânsito que cruzam o corte;
- \(J_s(A)\) identifica as saídas finais que cruzam o corte;
- cortes violados relevantes não atravessam arcos de alcance de capacidade ilimitada.

Essas desigualdades podem ser separadas por fluxo máximo para o ponto fracionário atual.

**Por que isso é específico do MIN-STATION?**

Cada origem precisa de uma unidade de deslocamento, mas as estações são compartilhadas sem capacidade global. Por isso, a capacidade \(y_v\) vale **separadamente em cada rede**, não como soma dos fluxos de todos os robôs. O acoplamento entre origens ocorre nas capacidades de ocupação dos destinos, dadas por \(p\).

Isso preserva a característica anônima do problema.

**Por que manter a base?**

O contraexemplo anterior mostra que simplesmente substituí-la por uma desagregação pode enfraquecer o LP.

Mantendo-a:

1. qualquer solução física admite uma extensão \(p\), obtida de um matching válido;
2. qualquer solução inteira aceita continua satisfazendo a base;
3. adicionar apenas parte dos cortes não exclui nenhuma instalação física válida.

Consequentemente, **interromper o fortalecimento não destrói a exatidão inteira do modelo de instalação**. Deixa apenas uma relaxação menos fortalecida.

Essa é uma diferença importante em relação a interromper a geração de colunas e interpretar o RMP como modelo completo.

**Relação com a F-CC.**

Uma solução F-CC pode ser decomposta em caminhos para cada origem. A quantidade dessa origem que transita por \(v\) é limitada pela massa das configurações que contêm \(v\), portanto por \(y_v\). Isso fornece a extensão \(p\) e os fluxos unitários necessários.

Para a construção descrita, o argumento estabelece a cadeia não estrita:

\[
z_{\mathrm{LP}}(\text{COMP+K})
\le
z_{\mathrm{LP}}(\text{COMP+K+cortes propostos})
\le
z_{\mathrm{LP}}(\text{F-CC+K})
\le OPT.
\]

A primeira desigualdade decorre de conservar o compacto; a segunda, da extensão dos caminhos das configurações.

**Dominância estrita, ganho computacional e qualidade da seleção de origens continuam pendentes. Ainda não há evidência suficiente para concluir.**

**Custo de representação.**

O master teria aproximadamente:

\[
O(|V|+|A_r|+|U|m)
\]

variáveis, mais os cortes efetivamente adicionados.

Uma rede auxiliar pode ser reutilizada por vez. Evita-se armazenar simultaneamente \(m|A_r|\) fluxos.

O custo não desaparece: passa a envolver \(|U|\) problemas de fluxo máximo por rodada e o crescimento dos cortes. Entretanto, é controlável por orçamento, sem exigir enumeração exponencial antes do primeiro solve.

A escolha de \(U\) parcial deve ser declarada. Ela não autoriza afirmar que foi resolvida a extensão completa com todas as origens.

### Diferença em relação às tentativas anteriores

Esta proposta não deve ser apresentada como simples novidade por usar Benders ou fluxo máximo.

Ela precisa ser comparada explicitamente com:

- **C3 existente:** testa alcance por origem, sem o mesmo acoplamento de atribuições entre todas as origens;
- **CBI:** acrescenta cortes de inviabilidade inteira; o E12 não mostrou ganho consistente sobre o núcleo;
- **T18:** materializa os fluxos por origem e contém a alegação incorreta de dominância LP;
- **C6:** explora informação de primeiro salto, que não esgota a conectividade ao longo de vários saltos.

A pergunta nova é sobre **matching compartilhado, conectividade fracionária e representação por cortes**, preservando as restrições agregadas.

### F-CC implícita e pricing

É matematicamente possível trabalhar com F-CC sem enumeração completa. O código N2 já demonstra parte da arquitetura necessária.

Ainda assim, eu não a escolheria como frente principal agora, porque seria necessário resolver conjuntamente:

- força dos limites globais do pricing;
- conectividade na relaxação do pricing;
- estabilidade da geração de colunas;
- produção de incumbentes físicas competitivas;
- custo nas instâncias grandes.

Um MIP sobre as colunas geradas pode produzir uma solução física válida e, portanto, um UB após validação. Seu bound de branch-and-bound **não** é LB global da F-CC completa.

Branch-and-price acrescentaria pricing nos nós, tratamento de inviabilidade de masters restritos e compatibilidade com branching. **Não há evidência atual que justifique assumir esse custo de desenvolvimento.**

### Alternativas que eu não priorizaria

- Materialização completa da desagregação \(m|A_r|\).
- Nova campanha ampla de F-C3.
- Repetição do CBI sem uma família de cortes demonstravelmente diferente.
- Aumento do cap de enumeração como estratégia central.
- Benders que apenas projete o mesmo LP agregado e seja apresentado como fortalecimento.
- Novas instâncias artificiais escolhidas apenas por provocar timeout.

A literatura já oferece resultados estruturais, parametrizados e para árvores. Eles são relevantes como referência, mas não justificam automaticamente um algoritmo eficaz para os grafos gerais e números de agentes do benchmark atual. [IJCAI](https://www.ijcai.org/proceedings/2026/9?utm_source=chatgpt.com)

## 5. Matriz de decisão

As classificações abaixo são avaliações qualitativas, não medições novas.

| Alternativa | Correção matemática | Aplicabilidade aos difíceis | Limites inferiores | Soluções primais |
|---|---|---|---|---|
| COMP+K atual | Fundamentada | Já observada | Limitados em várias famílias | Já produz incumbentes |
| COMP+K com cortes propostos | Argumento de preservação apresentado; revisão formal pendente | Estrutura compatível; desempenho pendente | Entre COMP e F-CC na construção descrita | Mantém a capacidade do compacto |
| F-CC+K explícita | Fundamentada | Limitada pela representação | LP mais forte que COMP | Disponíveis quando o modelo cabe |
| F-CC+K por CG na raiz | Modelo fundamentado; garantia depende do pricing/bound | Ainda não demonstrada no benchmark difícil | Potencial alto; certificação N2 fraca | Exige componente primal adicional |
| Branch-and-price | Exige nova arquitetura e provas | Desconhecida | Potencial alto | Possíveis, com implementação extensa |
| COMP+K com busca primal limitada | Preservável por validação e uso apenas como UB | Compatível com o modelo existente | Sem promessa de ganho dual | Principal objetivo da alternativa |

| Alternativa | Custo de representação | Implementação | Risco experimental | Contribuição potencial |
|---|---|---|---|---|
| COMP+K atual | Polinomial em \(A_r\) | Existente | Baixo operacional | Referência essencial |
| Cortes propostos | Polinomial mais cortes gerados | Médio | Ganho pode não pagar a separação | Relações entre relaxações e método aplicável |
| F-CC explícita | Exponencial | Existente | Alto risco de construção/memória | Referência teórica e diagnóstica |
| CG na raiz | Master pequeno, pricing difícil | Alto para torná-la competitiva | Alto | Boa, se houver ganho global útil |
| Branch-and-price | Dinâmica em toda a árvore | Muito alto | Muito alto para o prazo | Condicionada a resultados anteriores |
| Busca primal no compacto | Próximo ao compacto | Baixo a médio | Ganho pode ser apenas circunstancial | Computacional, se controlada e consistente |

A prioridade dos cortes propostos se baseia na **preservação do método existente e na possibilidade de limitar o custo adicional**. Não se baseia em desempenho já demonstrado.

## 6. Recomendação principal

Eu adotaria uma única frente principal:

> **COMP+K com fortalecimento na raiz por cortes de fluxo unitário acoplados ao matching, seguido da resolução inteira do compacto fortalecido.**

A primeira versão deveria separar cortes **antes** do MIP, com orçamento limitado. Não começaria por uma integração sofisticada em callbacks.

Isso evita introduzir prematuramente questões delicadas sobre cortes nas variáveis auxiliares, soluções incumbentes e separação nos nós.

Os papéis ficariam assim:

- **Base:** referência matemática e ablação.
- **COMP+K:** controle computacional principal.
- **Núcleo inteiro:** controle auxiliar obrigatório quando puder explicar um ganho de bound.
- **F-CC+K:** referência de força LP e controle em casos enumeráveis.
- **CG da N2:** patrimônio preservado, sem prioridade de expansão.
- **F-C3 e branch-and-price:** pausados.

O núcleo merece destaque: em SC-GF2 nas escalas 8 e 9, os resultados existentes mostram o núcleo fechando valores que COMP não fecha no orçamento. Não seria uma contribuição convincente produzir um novo limite inferior que apenas reproduza, mais caro, um resultado já disponível nesse controle.

Antes de implementar, a nova frente precisa de:

1. definição formal dos cortes e da rede, incluindo \(S\cap T\);
2. prova de preservação de todas as instalações físicas;
3. revisão da cadeia de dominância apresentada;
4. distinção explícita em relação a T18, C3 e CBI;
5. orçamento e critério de parada da separação.

A novidade publicável não está em “usar fluxo máximo”. Poderia estar na formulação apropriada ao pareamento livre, nas relações entre relaxações, na separação e no comportamento em instâncias difíceis.

## 7. Plano experimental revisado

### Inventário difícil confirmado

Os cinco resultados históricos de aproximadamente 3.600 segundos estão presentes no CSV citado, com os gaps informados.

Além disso, executei `verify_lote1a.py`, que confirmou os mesmos \(S,T\) e \(A_r\) para:

- `hc9u`;
- `hc10p`;
- `hc11p`;
- `hc12p`;
- `bip42p`;

e suas versões `puc-*-seed-r1`.

O controle `cc12-2u` apresentou a diferença de alcance esperada. Isso reforça por que não se deve comparar apenas pelos nomes.

**Equivalência da instância não significa equivalência do experimento.** O CSV histórico não fornece, sozinho, toda a rastreabilidade necessária para uma comparação contemporânea de tempo. Além disso, os métodos e cortes diferem.

Nos CSVs atuais de dificuldade, confirmei:

| Instância | Método registrado | LB / UB numéricos | Gap |
|---|---|---:|---:|
| `mapf-den312d-m50-f2-rho` | COMP, 600 s | 4 / 9 | 55,56% |
| `mapf-random-64-64-20-m100-f4` | COMP, 600 s | 41 / 70 | 41,43% |
| `puc-w3c571-seed-r1` | COMP, 600 s | 666 / 1131 | 41,11% |
| `puc-hc11p-seed-r1` | COMP, 600 s | 96 / 160 | 40,00% |
| `pucn-cc7-3n-regiao-f2` | COMP, 600 s | 9 / 14 | 35,71% |

São evidências de dificuldade **para aquele método e orçamento**, não provas de dificuldade intrínseca.

O manifesto corrente contém **31 casos D/A do benchmark-v1: 14 em desenvolvimento e 17 em avaliação**.

### Piloto recomendado

Usaria seis casos de desenvolvimento:

| Instância | Aspecto investigado |
|---|---|
| `puc-cc9-2p-seed-r1` | Caso esparso com gap menor; controle de custo adicional |
| `puc-bip42p-regiao-f2` | Estrutura bipartida e competição entre terminais |
| `pucn-cc3-10n-seed-r1` | Outra topologia, com menos agentes |
| `mapf-room-32-32-4-m10-f8` | Deslocamento em ambiente com obstáculos |
| `vienna-I056-regiao-f4` | Dígrafo de alcance grande |
| `puc-w3c571-seed-r1` | Estresse de tamanho e número de agentes |

O último caso não deve ser retirado porque incomoda a nova representação. Ele é justamente um teste necessário.

Acrescentaria controles pequenos de correção, incluindo permanência, estação em terminal e compartilhamento. SC-GF2 maior serviria como controle posterior de cobertura, respeitando seu uso histórico.

### Um problema adicional de independência

A partição atual usa `instancia_original`. No MAPF, essa string inclui o número de agentes.

Assim, aparecem:

- `room-32-32-4` com 10 agentes em desenvolvimento;
- o mesmo mapa e cenário com 25 agentes em avaliação.

A regra documental pode estar satisfeita, mas **esses casos não são independentes quanto ao grafo de origem**.

No novo estudo, eu agruparia também pelo mapa bruto. Não alteraria os freezes antigos; registraria que a variante de avaliação do mesmo mapa não é um teste independente após usar a variante de desenvolvimento.

As instâncias de avaliação já possuem resultados históricos conhecidos. Portanto, a avaliação futura será prospectiva para o novo método, não um benchmark nunca observado.

### Orçamentos e progressão

Recomendo:

1. **Piloto exploratório:** 300 segundos totais por braço e instância, inicialmente seed 42.
2. **Confirmação em desenvolvimento:** 600 segundos, seeds 42, 43 e 44, se houver sinal.
3. **Campanha final:** até 3.600 segundos, com política congelada, em aproximadamente 8–12 instâncias estratificadas de avaliação.

Doze instâncias, dois métodos e três seeds representam um teto de **72 horas de execução dos braços**, antes das terminações antecipadas.

O limite de uma hora é adequado como medida prática de desempenho. **Não é uma garantia de que o experimento será informativo**: isso depende da seleção, do piloto e das curvas de evolução.

### Critério de elegibilidade corrigido

Uma instância entra pelo problema representado, sua proveniência e o estrato experimental.

**Não precisa caber na F-CC explícita para entrar no estudo.**

Para F-CC explícita, registrar separadamente:

- modelo construído;
- cap excedido;
- limite de memória;
- orçamento de construção esgotado;
- falha técnica.

Esses casos permanecem no denominador de aplicabilidade. Não recebem objetivo zero nem um tempo fictício de resolução.

A comparação de força LP será feita onde os valores estiverem disponíveis. A comparação de capacidade de processamento utilizará todo o conjunto selecionado.

### Comparação justa e métricas

O par principal deve mudar somente o fortalecimento:

- COMP+K;
- COMP+K com a extensão e os cortes propostos.

Usar o mesmo K, hash da instância, versão de solver, threads, seed e política de incumbentes iniciais.

Registrar:

- ingestão e construção de \(A_r\);
- geração e validação de K;
- construção do modelo;
- separação;
- solver;
- validação física;
- tempo total;
- memória do processo e, quando disponível, do solver;
- primeira incumbente física e melhor UB;
- LB numérico e sua origem;
- LP inicial e LP após fortalecimento;
- bound da raiz após os procedimentos internos do solver;
- nós, Work, cortes e origens ativadas;
- estados sem LB, sem incumbente ou sem modelo construído.

**Não usar o objetivo primal de um LP interrompido como limite inferior.** É necessário o valor ótimo numérico ou um limite dual apropriado, quando disponível.

Os resultados devem manter três campos distintos:

1. evidência numérica do solver;
2. UB físico validado;
3. certificado racional independente.

A ausência do terceiro não impede publicar a comparação dos dois primeiros.

Para análise agregada, usar resultados pareados e agrupar variantes pelo grafo de origem. Tempos de resolução devem tratar timeouts como censura; médias calculadas apenas sobre casos resolvidos pelos dois métodos são insuficientes.

## 8. Plano de implementação em etapas

Estas são etapas futuras; nenhuma foi implementada nesta revisão.

| Etapa | Objetivo e atividades | Dependência | Aceite e testes | Esforço / gate |
|---|---|---|---|---|
| **P0 — Escopo experimental** | Congelar universo difícil, grupos de origem, controle COMP e contabilização completa do orçamento | Parecer científico | Nenhuma exclusão por falha da F-CC; auditoria de identidades e estados | Pequeno; avançar após contrato claro |
| **P1 — Formulação** | Formalizar a extensão, os cortes e as relações de LP; registrar o contraexemplo de T18 | P0 | Provas das duas direções de preservação física; tratamento de terminais e permanência | Pequeno a médio; revisão independente antes de código |
| **P2 — Separador mínimo** | Implementar a rede e a separação em instâncias pequenas, sem campanha | P1 | Comparar com uma extensão explícita pequena; enumeração de instalações; testes adversos e cortes inválidos rejeitados | Médio; parar se houver divergência matemática |
| **P3 — Fortalecimento limitado na raiz** | Integrar seleção limitada de origens, rodadas de cortes e continuação pelo compacto | P2 | Parada em qualquer ponto preserva modelo válido; custo e memória limitados; teste nos seis difíceis | Médio; avançar somente com sinal útil |
| **P4 — Comparação exploratória** | Executar os pares de 300/600 s, com ablações mínimas e controle do núcleo | P3 | Ganho não explicado apenas por K, núcleo ou orçamento; repetição em grafos distintos | Médio; interromper linha se custo consumir o benefício |
| **P5 — Avaliação congelada** | Executar a campanha de até 3.600 s e produzir análise pareada | P4 | Todos os casos previstos contabilizados; nenhuma alteração de política após resultados | Predominantemente computacional |

Para P4, o critério deve exigir **ganho além dos controles em pelo menos duas origens independentes**, acompanhado de custo aceitável. O limiar numérico precisa ser pré-registrado antes da execução.

Não consideraria suficiente melhorar apenas HB, apenas uma seed, ou um LP minúsculo que o COMP já resolve instantaneamente.

## 9. Riscos e plano de contingência

| Risco | Conduta recomendada |
|---|---|
| Os cortes não melhoram o LP além de K | Encerrar essa família; não expandir para callbacks ou novos grafos à procura de uma vitória |
| Melhoram o LP, mas pioram o resultado final | Reduzir o orçamento da separação no desenvolvimento; avaliar o ganho líquido, não apenas a raiz |
| A extensão consome memória | Limitar \(|U|\), reutilizar redes e manter o compacto; registrar a perda de força adicional |
| Não aparecem incumbentes úteis | Usar uma política primal comum aos braços; separar completamente o estudo primal do fortalecimento |
| O pricing permanece fraco ou caro | Não afeta o caminho principal; CG continua fora da dependência experimental |
| Nenhum ganho em 3.600 s | Registrar o resultado negativo e a causa observada; não aumentar indefinidamente o prazo |
| O desenvolvimento excede o prazo do mestrado | Parar antes de branch-and-price ou separação em toda a árvore |

**Minha única contingência seria permanecer no COMP+K e investigar uma melhoria primal limitada**, com incumbentes validadas e eventual aproveitamento do núcleo como fonte de limite.

A motivação é o E13, que mostrou incumbentes ainda melhoráveis. A ressalva é igualmente importante: os construtores do E10/E10b não apresentaram o ganho desejado, e a fase longa do E13 mudou tempo e ênfase simultaneamente. Portanto, a contingência precisa de um experimento controlado, não de uma repetição dos mesmos construtores.

Uma busca em vizinhança de uma instalação pode produzir UB. O bound de seu subproblema restrito não deve ser apresentado como LB global. A resolução global do compacto precisa manter seu próprio histórico de limites.

## 10. Conclusão e decisão

**Eu escolheria agora o compacto fortalecido por informação implícita de origem–destino, com separação limitada na raiz e preservação integral do COMP+K.**

Essa escolha permite:

- começar pelos grafos difíceis já existentes;
- limitar o esforço adicional;
- continuar com um modelo inteiro válido quando o fortalecimento for interrompido;
- comparar desempenho numérico sem depender de certificação racional;
- investigar uma relação matemática clara entre o compacto e a F-CC.

A F-CC explícita permanece útil como referência de relaxação. A geração de colunas permanece uma linha matematicamente legítima, mas os resultados atuais não justificam torná-la a principal aposta de implementação.

**Ainda não há evidência suficiente para concluir que o fortalecimento proposto será competitivo. Há, porém, fundamento para testá-lo com um piloto pequeno, discriminante e composto por instâncias realmente difíceis.** Esse é o próximo investimento que considero mais defensável para o mestrado, preservando integralmente `N2 FAIL` e os resultados anteriores.