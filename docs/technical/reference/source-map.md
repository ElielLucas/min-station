# MIN-STATION — Mapa de Fontes

Este arquivo explica o papel de cada referência no projeto. As fontes não são concorrentes: cada uma responde a um tipo diferente de pergunta.

## 1. Artigo original de Das

**Arquivo sugerido:** `docs/technical/reference/min-station-das.pdf`

**Referência:** Arun Kumar Das, *Charging Station Placement for Limited Energy Robots*.

### Papel na pesquisa

É a fonte principal para o **problema MIN-STATION original** e para seus primeiros resultados teóricos.

Usar para:

- definição do problema;
- semântica dos robôs não rotulados;
- autonomia em passos;
- solução `C ⊆ V`;
- NP-dificuldade em grafos gerais;
- propriedades e algoritmos para caminhos e ciclos;
- identificar o que pertence ao problema original e o que foi acrescentado pelo projeto.

### Limite da fonte

O artigo de Das não apresenta a formulação de PLI desenvolvida neste projeto. Portanto, não deve ser usado para inferir variáveis, restrições, implementação ou estratégia computacional do repositório.

## 2. Artigo da SBPO

**Arquivo sugerido:** `docs/technical/reference/artigo-sbpo.pdf`

**Título:** *Formulações de Programação Linear Inteira para o Problema de Alocação Mínima de Estações de Recarga*.

### Papel na pesquisa

É um **marco anterior do projeto** e documenta uma etapa importante da evolução da pesquisa em PLI.

Usar para:

- entender a primeira formulação base desenvolvida no projeto;
- recuperar decisões de modelagem baseadas em fluxo agregado e dígrafo de alcance;
- consultar a metodologia experimental e resultados daquela etapa;
- compreender a motivação para evoluções posteriores da formulação;
- preservar o histórico científico do trabalho.

Na formulação base publicada nesse artigo, as estações são restritas aos vértices intermediários `V \ (S ∪ T)`.

O artigo também contém uma formulação generalizada, que deve ser tratada como **outra variante/modelo**, e não como especificação automática do baseline atual.

### Regra atual

O artigo da SBPO é referência científica e histórica, mas não define sozinho a formulação corrente do repositório.

## 3. Formulação base com estações em todos os vértices

**Arquivo sugerido:** `docs/technical/reference/formulacao-base-all-vertices.pdf`

### Papel na pesquisa

Documenta a evolução do baseline posterior ao artigo da SBPO, em que a variável de instalação passa a ser definida para todo `v ∈ V`.

Mudanças centrais:

- objetivo `min Σ_{v∈V} y_v`;
- balanço líquido em origens e destinos;
- origem pode emitir sua unidade inicial sem estação;
- destino pode receber sua unidade final sem estação;
- uso adicional de origem/destino como ponto de recarga exige instalação.

Essa versão é o **baseline atual**, mas não deve ser interpretada como a formulação definitiva da pesquisa.

O contexto organizado da formulação está em:

`docs/context-ai/base-formulation.md`.

## 4. Documentos de contexto do repositório

### `RESEARCH.md`

Define o objetivo científico e a direção geral da pesquisa.

### `docs/context-ai/base-formulation.md`

Descreve o baseline matemático corrente.

### `docs/context-ai/research-direction.md`

Orienta a investigação de novas formulações, fortalecimentos e métodos de solução.

### `docs/technical/governance/open-questions.md`

Registra hipóteses e decisões ainda não fechadas.

## 5. Código do repositório

O código é a fonte para afirmar **o que está implementado e executando** em uma determinada versão.

Se código e documentação divergirem:

1. não mascarar a diferença;
2. identificar a versão/commit;
3. distinguir formulação desejada, formulação documentada e implementação atual;
4. corrigir somente após decisão explícita.

## 6. Precedência por tipo de pergunta

Não existe uma precedência única para tudo. Use a fonte adequada:

| Pergunta | Fonte principal |
|---|---|
| O que é o MIN-STATION original? | Artigo de Das |
| Quais resultados teóricos originais são conhecidos? | Artigo de Das |
| Como surgiu a primeira PLI do projeto? | Artigo da SBPO |
| Como era a variante com estações apenas em intermediários? | Artigo da SBPO |
| Qual é o baseline matemático atual? | `base-formulation.md` + formulação all-vertices |
| Qual é o objetivo científico do projeto? | `RESEARCH.md` |
| Que tipos de novas abordagens podem ser pesquisadas? | `research-direction.md` |
| O que o software realmente executa hoje? | Código + configuração da execução |
| Quais pontos ainda estão abertos? | `open-questions.md` |

## 7. Regra para novos artigos e experimentos

Quando uma nova formulação ou técnica for incorporada:

- criar identificação inequívoca para ela;
- registrar sua relação com o baseline;
- indicar se resolve exatamente o mesmo problema ou uma variante;
- manter referência ao artigo/experimento que a introduziu;
- não substituir silenciosamente documentos históricos.
