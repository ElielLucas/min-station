# F-C3 — formulação por componentes com consistência de trios

> **Estado deste documento (F1, 2026-10-06).**
>
> - **Papel:** formulação em avaliação, **não** o baseline.
> - **Origem:** proposta externa. Este arquivo é o documento de referência no
>   repositório. O texto em primeira pessoa foi descartado.
> - Cadeia adotada: \(z_{\mathrm{LP}}^{\mathrm{base}} \le z_{\mathrm{LP}}^{\mathrm{F\text{-}CC}} \le z_{\mathrm{LP}}^{\mathrm{F\text{-}C3}} \le \mathrm{OPT}\).
>   O primeiro elo é P2 (`PROVEN`). O segundo e o terceiro dependem das redes
>   de trios e ficam `HYPOTHESIS`/`OPEN`.
> - **Não implementar** a parte marcada `OPEN`. Uma implementação adivinhada
>   mediria o palpite, não a F-C3.
> - Documento externo de provas
>   (`MIN-STATION-formulacao-componentes-consistencia-trios.md`): **ausente**
>   deste repositório. Não bloqueia F2/F3 da F-CC.

## 1. Relação com a F-CC

A F-CC usa uma variável \(\lambda_q\) por tripla \(q=(W,I,J)\). A F-C3
pretende duas mudanças:

1. separar a infraestrutura \(W\) das atribuições \(I,J\);
2. acrescentar consistência de trios sobre essas atribuições.

A primeira mudança, sozinha, é a **forma separada** da F-CC. P7 em
`provas-fcc-fc3.md` classifica a equivalência de LP como `PROVEN`. Essa
forma **não** é a F-C3: falta o item 2.

## 2. Forma separada (parte fechada)

Variáveis, para cada \(W\subseteq V\) não vazio e conexo em \(H=G^r\):

| Variável | Domínio | Significado |
|---|---|---|
| \(y_v\) | \(\{0,1\}\) | instalação em \(v\in V\) |
| \(\lambda_W\) | \(\ge 0\) | peso da infraestrutura \(W\) |
| \(\alpha_{sW}\) | \(\ge 0\) | atribuição da origem \(s\in S\cap B(W)\) a \(W\) |
| \(\beta_{tW}\) | \(\ge 0\) | atribuição do destino \(t\in T\cap B(W)\) a \(W\) |
| \(d_{st}\) | \(\ge 0\) | atendimento direto, \((s,t)\in D\) |

Restrições fechadas:

\[
\alpha_{sW}\le\lambda_W,
\qquad
\beta_{tW}\le\lambda_W,
\qquad
\sum_{s}\alpha_{sW}=\sum_{t}\beta_{tW},
\]

\[
\sum_{W\ni v}\lambda_W\le y_v,
\qquad
\sum_{W}\alpha_{sW}+\sum_{t:(s,t)\in D}d_{st}=1,
\qquad
\sum_{W}\beta_{tW}+\sum_{s:(s,t)\in D}d_{st}=1.
\]

Objetivo: \(\min\sum_v y_v\). \(H\), \(B(W)\) e \(D\) são os da F-CC,
incluindo \(d_{ss}=0\) para \(s\in S\cap T\).

## 3. Redes de trios — `OPEN`

O resumo original afirma: para cada trio de origens e cada trio de destinos,
uma rede auxiliar de oito estados (subconjuntos do trio) cujos fluxos devem
concordar com \(\lambda,\alpha,\beta,d\); as transições impediriam que um
integrante fosse atendido duas vezes; a construção seria um diagrama de
decisão.

**Pontos que o texto disponível não define:**

| # | Lacuna | Por que impede implementação |
|---|---|---|
| O1 | O que é uma **etapa** da rede | Sem o índice da etapa não há nós |
| O2 | Conjunto de arcos (de qual estado para qual, em qual etapa) | Sem arcos não há fluxo |
| O3 | Como o fluxo da rede se iguala a \(\lambda_W\), \(\alpha_{sW}\), \(\beta_{tW}\) e \(d_{st}\) | Sem as igualdades a rede não corta nada |
| O4 | A rede é por trio global ou por trio \(\times W\) | Muda o tamanho e a semântica |
| O5 | Ordem das etapas (sobre \(W\), sobre robôs, outra) | Altera o politopo |

Enquanto O1–O5 não tiverem definição no repositório, **não há modelo F-C3
implementável**. O braço F-C3 de F3/GF1 fica `OPEN`. GF1 avalia só a F-CC
(default da spec B).

## 4. Valores numéricos alegados — `HYPOTHESIS`

Nenhuma das famílias abaixo está definida neste repositório. Só podem ser
checadas se a instância for reconstruída a partir de uma definição
completa **e** as redes de trios deixarem de ser `OPEN`.

| Alegação | Condição para checar | Status |
|---|---|---|
| Família com 20 vértices e 7 robôs: base \(1\), F-CC \(3\), F-C3 \(4\), OPT \(4\) | Gerador ou lista de arestas no repositório + F-C3 fechada | `HYPOTHESIS` |
| Família geral: F-CC \(=1{,}5g\), F-C3 \(=2g\) (ótimo) | Definição do parâmetro \(g\) e da família | `HYPOTHESIS` |
| Exemplo com 15 vértices: F-C3 \(=2{,}5\), OPT \(=3\) | Instância no repositório + F-C3 fechada | `HYPOTHESIS` |

F3 **não** ajusta medição nem alegação se houver divergência. Sem instância,
não há comparação.

## 5. Tamanho

Ainda com a forma separada, o número de \(W\) conexos é exponencial. As redes
de trios, se definidas, acrescentam \(O(m^3)\) blocos. Em escala a F-C3
exigiria separação preguiçosa, fora desta spec.

## 6. O que F3 mede

F3 mede o LP da F-CC (forma separada, após P7). Não mede F-C3.
