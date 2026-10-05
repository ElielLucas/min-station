# F-C3 — formulação por componentes com consistência de trios

> **Estado deste documento (R1, 2026-10-04).**
>
> - **Origem:** proposta externa, recebida como resposta de chat em primeira pessoa. O corpo
>   abaixo foi mantido como chegou, salvo o ajuste da cadeia de dominância e da tabela de
>   valores. Não é o baseline do projeto; é uma **formulação em avaliação** (Linha F de
>   `docs/technical/plans/plano-proxima-fase.md`). A reescrita como documento de referência é a
>   tarefa F1.
> - **Conferido na análise de planejamento** (`plano-proxima-fase.md` §6.2, marca [Conferido],
>   ainda não escrito como prova no repositório): a separação `λ_W / α / β` preserva o LP da F-CC
>   (o politopo `{(a,b) ∈ [0,1]^S × [0,1]^T : Σa = Σb}` tem vértices inteiros), o que dá
>   `z_LP^F-CC ≤ z_LP^F-C3`.
> - **Hipótese** (alegado no texto, não verificável no repositório): a família de 20 vértices e 7
>   robôs com valores 1/3/4 (base/F-CC/F-C3) e ótimo 4; a família geral com F-CC `= 1,5g` contra
>   F-C3 `= 2g`; o contraexemplo de 15 vértices com F-C3 `= 2,5` contra ótimo 3. Ficam como
>   [Hipótese] até o documento de provas ser obtido ou os valores serem reproduzidos (tarefa F3).
> - **Falta:** o documento completo de provas (`MIN-STATION-formulacao-componentes-consistencia-trios.md`),
>   que o texto aponta para um sandbox externo e **não está no repositório**. Sem ele, F2/F3 seguem
>   com re-derivação própria. O número de trios é `O(m³)`; em escala exigiria separação preguiçosa,
>   que não está projetada.
> - Cadeia de dominância adotada pelo projeto: `base ≤ F-CC ≤ F-C3 ≤ OPT`.

**Sim. Consegui desenvolver uma candidata cuja relaxação linear domina as anteriores, inclusive a formulação por componentes.** O ganho é matemático; ainda não podemos afirmar que ela será mais rápida.

Chamei-a de **F-C3: formulação por componentes com consistência de trios**. Ela evolui a F-CC em dois pontos.

**Primeiro, reduz a enumeração sem perder força.**

Na F-CC, cada variável representa uma combinação:

\[
(W,I,J),
\]

em que \(W\) é uma infraestrutura conectada, \(I\) são as origens atendidas e \(J\), os destinos.

Isso enumera muitos grupos diferentes para a mesma infraestrutura. Na nova representação, separamos essas decisões:

| Variável | Significado |
|---|---|
| \(y_v\) | Instalação de estação em \(v\) |
| \(\lambda_W\) | Utilização da infraestrutura conectada \(W\) |
| \(\alpha_{sW}\) | Atribuição da origem \(s\) a \(W\) |
| \(\beta_{tW}\) | Atribuição do destino \(t\) a \(W\) |
| \(d_{st}\) | Atendimento direto, sem recarga |

Cada infraestrutura recebe a mesma quantidade de origens e destinos:

\[
\sum_s\alpha_{sW}=\sum_t\beta_{tW}.
\]

As atribuições dependem da utilização de \(W\):

\[
\alpha_{sW}\le\lambda_W,
\qquad
\beta_{tW}\le\lambda_W.
\]

E sua utilização depende das estações:

\[
\sum_{W:v\in W}\lambda_W\le y_v.
\]

**Demonstrei que essa representação preserva exatamente a força da relaxação da F-CC**, eliminando a enumeração explícita dos pares de grupos \(I,J\).

**Segundo, representa conjuntamente decisões que antes podiam ser fracionadas de maneira incompatível.**

Considere três grupos que atendem:

\[
\{s_1,s_2\},\qquad
\{s_2,s_3\},\qquad
\{s_1,s_3\}.
\]

A relaxação anterior pode usar metade de cada grupo. Assim, cada origem recebe atendimento total igual a 1.

Entretanto, não é possível selecionar dois desses grupos completos numa mesma atribuição: eles repetiriam alguma origem. A relaxação está combinando atendimentos que não correspondem a uma mistura coerente de partições.

A F-C3 enfrenta isso representando **cada trio de origens conjuntamente**, e fazendo o mesmo para os destinos.

Para cada trio, uma rede auxiliar registra quais integrantes já foram atribuídos. São oito estados possíveis por etapa, correspondentes aos subconjuntos do trio. As transições impedem que um integrante seja atendido duas vezes.

Os fluxos dessas redes precisam concordar com \(\lambda,\alpha,\beta,d\). Portanto, as atribuições individuais passam a ter um certificado de compatibilidade conjunta.

Essa representação por redes é uma construção conhecida de formulações estendidas com diagramas de decisão; a aplicação e as provas específicas para este modelo estão no documento. Não estou reivindicando novidade bibliográfica. [www.andrew.cmu.edu](https://www.andrew.cmu.edu/user/vanhoeve/papers/DD_TutORial.pdf?utm_source=chatgpt.com)

**O que consegui demonstrar sobre a melhoria**

Para as formulações completas:

\[
\boxed{
z_{\mathrm{LP}}^{\mathrm{baseline}}
\le
z_{\mathrm{LP}}^{\mathrm{F\text{-}CC}}
\le
z_{\mathrm{LP}}^{\mathrm{F\text{-}C3}}
\le
\mathrm{OPT}
}
\]

Além disso, construí uma família de grafos conexos em que a melhoria sobre F-CC é estrita. Um integrante dessa família possui **20 vértices e 7 robôs**:

| Modelo | Limite da relaxação |
|---|---:|
| Baseline agregada | \(1\) |
| F-CC | \(3\) |
| **F-C3** | **\(4\)** |
| Ótimo inteiro | **\(4\)** |

Esses valores foram demonstrados analiticamente, sem executar solver. Como o limite anterior já era inteiro, o ganho de \(3\) para \(4\) vai além de arredondar o objetivo.

Na família geral, F-CC vale \(1{,}5g\), enquanto F-C3 chega a \(2g\), que é o ótimo.

**Ela continua representando o problema original.** A prova inclui estações em qualquer vértice, \(S\cap T\), permanência, compartilhamento de estações e pareamento livre. Somente \(y\) precisa ser binário; as demais variáveis podem ser contínuas.

Há duas limitações importantes:

- **O tamanho continua exponencial**, pois ainda consideramos conjuntos conectados \(W\). As redes de trios também acrescentam variáveis.
- **A relaxação ainda pode ter gap.** Encontrei um exemplo de quinze vértices em que F-C3 vale \(2{,}5\), mas o ótimo é \(3\). Compatibilidade de trios não garante compatibilidade global.

Portanto, esta é uma candidata **comprovadamente mais forte em relaxação** que as anteriores. **Ainda não há evidência suficiente para concluir que seja computacionalmente superior.**

Registrei a formulação completa, as provas, a família de separação e o contraexemplo em MIN-STATION-formulacao-componentes-consistencia-trios.md[MIN-STATION-formulacao-componentes-consistencia-trios.md](sandbox:/workspace/scratch/c87335ddaac1/MIN-STATION-formulacao-componentes-consistencia-trios.md).