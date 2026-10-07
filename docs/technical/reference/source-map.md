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

> **Desatualizado desde a rodada E5.** O PDF ainda usa balanços separados para
> origens e destinos (equações (2)–(3)), que tornam o modelo inviável quando
> `S ∩ T ≠ ∅`; o baseline atual usa o balanço unificado (variante U). O resumo
> do PDF também repete o texto da SBPO ("vértices intermediários") e há
> referências quebradas "(??)". Use-o só como registro histórico; a formulação
> vigente está em `docs/context-ai/base-formulation.md` §6–7 e em `baseline.py`.

Mudanças centrais:

- objetivo `min Σ_{v∈V} y_v`;
- balanço líquido em origens e destinos;
- origem pode emitir sua unidade inicial sem estação;
- destino pode receber sua unidade final sem estação;
- uso adicional de origem/destino como ponto de recarga exige instalação.

Essa versão é o **baseline atual**, mas não deve ser interpretada como a formulação definitiva da pesquisa.

O contexto organizado da formulação está em:

`docs/context-ai/base-formulation.md`.

## 4. Artigo IJCAI 2026 (Das, Hanaka, Melissinos e Ono)

**Arquivo:** `docs/technical/reference/novo_artigo_das_2026.pdf`

**Referência:** Arun Kumar Das, Tesshu Hanaka, Nikolaos Melissinos e Hirotaka Ono, *Charging Station Placement for Anonymous Mobile Agents: A Parameterized Complexity Perspective*. In: Proceedings of the Thirty-Fifth International Joint Conference on Artificial Intelligence (IJCAI-26), Main Track, pp. 72–80, agosto de 2026. DOI 10.24963/ijcai.2026/9.

### Papel na pesquisa

É o **trabalho prévio mais próximo**. Estuda exatamente o MIN-STATION de Das (robôs anônimos, autonomia comum, estações em qualquer vértice, `|S| = |T| = k`, emparelhamento final livre), sob o nome CHARGING STATION PLACEMENT e com `k` no lugar de `m`.

Usar para:

- a equivalência `(G, r) ↔ (G^r, 1)` (Proposição 1, p.75) — o dígrafo de alcance do projeto é `G^r`;
- a verificação polinomial de viabilidade por alcance e emparelhamento bipartido (Lemas 1–2, Teorema 1, p.75) e a pertinência a NP;
- as reduções de Set Cover (Teorema 3, p.76) e de Bin Packing (Teorema 4, p.76), que as famílias estruturais SC e BP do projeto instanciam;
- a complexidade clássica e parametrizada (Teoremas 2 e 5), os algoritmos FPT (Teoremas 6–8), o algoritmo polinomial em árvores (Teorema 9) e a `k`-aproximação (Teorema 10);
- decidir o que **não** é contribuição do projeto.

### Limite da fonte

O artigo não contém formulação de PLI, solver, experimento nem benchmark. Não serve para afirmar desempenho de método. Duas observações verificadas sobre o texto (a construção literal de `D` admite relé sem estação em `S ∩ T ∖ C`; o esboço do Teorema 10 inverte uma desigualdade) estão registradas em `overlap-ijcai2026-min-station.md` §4.3 e não refutam teorema.

### Sobreposição com o projeto

O levantamento completo — definições atributo a atributo, matriz de sobreposição, classificação das contribuições e lista de correções — está em:

`docs/technical/reference/overlap-ijcai2026-min-station.md`.

## 5. Pereira & Ravelo (ETC/CSBC 2026, aranhas)

**Arquivo:** `docs/technical/reference/pereira-ravelo-2026-aranhas.md`

**Referência:** Lucas Cardoso Pereira e Santiago Valdés Ravelo, *Placement of charging stations for energy-constrained robots in spider graphs*. Anais do Encontro de Teoria da Computação (ETC 2026) / 46º CSBC, publicado em 19 de julho de 2026.

### Papel na pesquisa

Artigo do mesmo grupo. Estuda o MIN-STATION de Das em grafos-aranha e dá um algoritmo guloso em `O(|V|)`. Não contém PLI.

Usar para:

- algoritmo de caminhos (revisão de Das) e de aranhas;
- fonte de ótimos exatos em `n` grande, como certificador (tarefa R11 / Spec D);
- conferir a referência 4 de `overlap-ijcai2026-min-station.md`.

### Limite da fonte

A prova no `.md` está em esboço e tem casos a testar (`plano-proxima-fase.md` §5). Não é baseline. Não define formulação nem protocolo experimental.

### R11 (leituras, preparação e pré-registro, 2026-10-06→07)

Interpretação executável: `docs/technical/reference/leituras-r11-certificadores.md`. Contrato do lote: `docs/technical/reference/pre-registro-r11-certificadores.md`. Implementação preparatória, ainda **não executada**: `experiments/structural/path_cycle.py`, `spider.py`, `r11_catalog.py`, `prepare_r11.py`, `verify_r11.py`, `run_r11.py`; cruzamento F-CC binário em `experiments/alternative-formulations/fcc.py::opt_fcc`. Spec: `specs/proxima-fase-d-certificadores-classes-especiais/spec.md`. Esses artefatos não substituem Das nem o `.md` das aranhas e ainda não constituem evidência experimental.

## 6. Formulações em avaliação (F-CC e F-C3)

**Arquivos:**

- `docs/technical/reference/formulacao-fcc-configuracoes-conectadas.md` (F-CC);
- `docs/technical/reference/formulacao-fc3-consistencia-trios.md` (F-C3).

### Papel na pesquisa

São **propostas externas em avaliação**, não o baseline. A cadeia de dominância adotada é `base ≤ F-CC ≤ F-C3 ≤ OPT`. O que foi conferido na análise de planejamento, o que é hipótese e o que falta estão no cabeçalho de estado de cada arquivo.

Usar para:

- definição das variáveis e restrições candidatas;
- planejar F1–F3 e o portão GF1.

### Limite da fonte

Nenhuma das duas substitui a formulação base. Comparações oficiais continuam contra COMP (`open-questions.md` Q6). As redes de trios da F-C3 estão `OPEN` (`formulacao-fc3-consistencia-trios.md` §3). Provas da F-CC: `provas-fcc-fc3.md`. Medição F3 e portão GF1: `resultados-f3-fcc.md`, `decisao-gf1.md`.

## 7. Documentos de contexto do repositório

### `RESEARCH.md`

Define o objetivo científico e a direção geral da pesquisa.

### `docs/context-ai/base-formulation.md`

Descreve o baseline matemático corrente.

### `docs/context-ai/research-direction.md`

Orienta a investigação de novas formulações, fortalecimentos e métodos de solução.

### `docs/technical/governance/open-questions.md`

Registra hipóteses e decisões ainda não fechadas.

## 8. Código do repositório

O código é a fonte para afirmar **o que está implementado e executando** em uma determinada versão.

Se código e documentação divergirem:

1. não mascarar a diferença;
2. identificar a versão/commit;
3. distinguir formulação desejada, formulação documentada e implementação atual;
4. corrigir somente após decisão explícita.

## 9. Precedência por tipo de pergunta

Não existe uma precedência única para tudo. Use a fonte adequada:

| Pergunta | Fonte principal |
|---|---|
| O que é o MIN-STATION original? | Artigo de Das |
| Quais resultados teóricos originais são conhecidos? | Artigo de Das (NP-dificuldade, caminhos, ciclos) |
| Complexidade parametrizada, verificação por matching, `G^r`, aproximação, árvores? | Artigo IJCAI 2026 |
| O que já está na literatura e o que é contribuição do projeto? | `overlap-ijcai2026-min-station.md` |
| Como surgiu a primeira PLI do projeto? | Artigo da SBPO |
| Como era a variante com estações apenas em intermediários? | Artigo da SBPO |
| Qual é o baseline matemático atual? | `base-formulation.md` (variante U); o PDF all-vertices é histórico |
| Qual é a implementação do baseline? | `baseline.py` + `ms_utils.py` |
| Qual métrica cada instância usa? | `open-questions.md` Q2 e Q7 |
| Qual é o objetivo científico do projeto? | `RESEARCH.md` |
| Que tipos de novas abordagens podem ser pesquisadas? | `research-direction.md` |
| O que o software realmente executa hoje? | Código + configuração da execução |
| Quais pontos ainda estão abertos? | `open-questions.md` |
| O algoritmo de aranhas e o artigo de Pereira & Ravelo? | `pereira-ravelo-2026-aranhas.md` |
| Como ler os algoritmos de caminho/ciclo/aranha para implementar R11? | `leituras-r11-certificadores.md` |
| Qual é o contrato experimental futuro de R11 (ainda sem CSV)? | `pre-registro-r11-certificadores.md` |
| Qual é a F-CC / F-C3 (em avaliação, não baseline)? | `formulacao-fcc-configuracoes-conectadas.md`, `formulacao-fc3-consistencia-trios.md` |

## 10. Regra para novos artigos e experimentos

Quando uma nova formulação ou técnica for incorporada:

- criar identificação inequívoca para ela;
- registrar sua relação com o baseline;
- indicar se resolve exatamente o mesmo problema ou uma variante;
- manter referência ao artigo/experimento que a introduziu;
- não substituir silenciosamente documentos históricos.
