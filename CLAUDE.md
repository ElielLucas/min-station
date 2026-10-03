# MIN-STATION — Instruções para IA

## Antes de qualquer ação

Leia sempre, nesta ordem:

1. `docs/project-overview.md` — visão geral do projeto, objetivo da pesquisa e fontes principais.
2. `RESEARCH.md` — direção científica, baseline atual e limites de escopo.

Depois, leia apenas o contexto aplicável à tarefa:

| Tarefa | Arquivo obrigatório |
|---|---|
| Entender o problema MIN-STATION | `docs/context-ai/min-station-domain.md` |
| Trabalhar na formulação base atual | `docs/context-ai/base-formulation.md` |
| Propor ou avaliar novas abordagens de PLI | `docs/context-ai/research-direction.md` + formulação/código relevante |
| Alterar ou revisar código | `docs/context-ai/code-guidelines.md` + arquivos de código relevantes |
| Verificar lacunas ou pontos ainda não decididos | `docs/technical/governance/open-questions.md` |
| Ver o backlog de continuação e o histórico de tarefas | `docs/technical/plans/backlog-continuacao.md` |
| Comparar documentos/artigos | `docs/technical/reference/source-map.md` |
| Escolher ou interpretar instâncias experimentais | `docs/technical/reference/benchmark-v1.md` + `instances/manifest.csv` |
| Comparar dois métodos ou duas configurações | `docs/technical/reference/protocolo-comparacao-pareada.md` |

## Objetivo do projeto

O projeto é uma pesquisa em **Programação Linear Inteira e métodos exatos para o MIN-STATION**.

A formulação base atual é um **baseline de pesquisa**, não o objetivo final do trabalho. Ela serve como ponto de partida para estudar, comparar e desenvolver formulações, fortalecimentos e estratégias de solução capazes de melhorar qualidade de limites, desempenho computacional e escalabilidade.

A alteração que passou a permitir estações em todos os vértices foi uma etapa de evolução do baseline após o artigo da SBPO. Ela não deve ser confundida com o objetivo científico global do projeto.

## Escopo padrão

Como referência inicial, considere:

- o problema MIN-STATION original de Das;
- a formulação base atual com fluxo agregado e dígrafo de alcance;
- estações permitidas em todo `V`;
- autonomia comum;
- minimização da quantidade de estações.

Novas formulações, cortes, relaxações, decomposições e outros métodos de otimização podem fazer parte da pesquisa quando a tarefa solicitar sua investigação.

### Não introduzir automaticamente

Sem pedido explícito, não trazer para a formulação base atual:

- custos de instalação heterogêneos;
- autonomias diferentes por robô;
- restrições de elegibilidade origem-destino;
- a formulação generalizada do artigo da SBPO;
- a antiga restrição de instalação apenas em vértices intermediários.

Esses elementos pertencem a outra variante/modelo e não devem contaminar o baseline atual.

## Regras transversais

- Sempre responder em português brasileiro, salvo pedido explícito em outro idioma.
- Não inventar definição, hipótese, restrição, variável, conjunto ou resultado matemático.
- Distinguir claramente:
  1. o problema original de Das;
  2. a formulação base atual;
  3. formulações ou métodos experimentais;
  4. resultados já obtidos e hipóteses ainda não validadas.
- Não tratar uma proposta experimental como parte do baseline sem decisão explícita.
- Não usar a formulação generalizada da SBPO como referência automática para alterar a base.
- Não reintroduzir a hipótese de que estações só podem ser instaladas em vértices intermediários.
- Quando documentação, artigo, código e experimento divergirem, não reconciliar silenciosamente. Identificar a divergência e a fonte usada.
- Antes de alterar código de modelagem, localizar onde conjuntos, variáveis, objetivo e restrições são realmente construídos.
- Mudanças matemáticas devem vir acompanhadas de justificativa e, quando possível, casos pequenos verificáveis.
- Ao comparar métodos, preservar a mesma definição de instância e registrar claramente qual formulação e configuração foram usadas.
- Experimentos sobre o problema de Das usam as instâncias `classe = principal` de `instances/manifest.csv` (75 principal: 5 legadas + 70 do benchmark-v1; ver `docs/technical/reference/benchmark-v1.md`). Resultados obtidos em instâncias ponderadas ou dirigidas (classes `extensao_ponderada`/`extensao_dirigida`) devem ser rotulados como extensão, não generalizados para o problema de Das sem ressalva.
- Não efetuar commit automaticamente. Só commitar quando solicitado ou aprovado pelo usuário.

## Ao revisar uma formulação ou método

Verifique, no mínimo:

1. correção matemática e correspondência com soluções válidas do problema estudado;
2. efeito sobre a relaxação linear e limites inferior/superior;
3. tamanho do modelo: variáveis, restrições e estrutura;
4. existência de simetrias, ciclos de fluxo ou redundâncias;
5. impacto esperado sobre branch-and-bound/branch-and-cut;
6. necessidade de pré-processamento ou separação de cortes;
7. comparabilidade experimental com o baseline;
8. tratamento de `S ∩ T`, métrica de distância e semântica de terminais;
9. consistência entre formulação documentada e implementação.

## Documentação de terceiros

Quando uma tarefa depender de comportamento específico de Gurobi, NetworkX, Python ou outra biblioteca:

- consultar a documentação da versão efetivamente usada no projeto;
- não preencher diferenças de API por memória;
- não confundir limitação do solver com propriedade matemática do modelo.
