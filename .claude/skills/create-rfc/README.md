# RFC Creator

Uma skill para agentes de codificação de IA que ajuda a criar documentos estruturados de Request for Comments (RFC) para propor mudanças significativas e conduzir decisões dos stakeholders.

## O Que Ela Faz

Esta skill orienta agentes de IA a criar RFCs bem estruturados que incluem:

- **Seções obrigatórias**: Background, Assumptions, Decision Criteria, Options Considered, Action Items, Outcome
- **Seções recomendadas**: Relevant Data, comparação de Pros/Cons, estimativas de Custo, Resources
- **Modelo RACI**: Driver, Approver, Contributors, Informed — separando claramente quem decide de quem aconselha

A skill se adapta automaticamente a:

- **Tipo de RFC**: Technical/Architecture, Process/Workflow, Product/Feature, Vendor Selection, Policy/Compliance
- **Contexto fornecido**: Se você fornecer contexto rico, ela gera imediatamente; se não, faz perguntas direcionadas
- **Idioma do usuário**: Gera automaticamente o RFC no mesmo idioma da sua solicitação (por exemplo, inglês, português ou espanhol)

## RFC vs TDD — Qual Você Precisa?

| Pergunta | Use |
|----------|-----|
| Devemos fazer X de fato? Qual opção? | **RFC** |
| Já decidimos por X — como construímos? | **TDD** |
| Precisa de alinhamento da liderança ou de múltiplos times antes de agir | **RFC** |
| Precisa documentar a arquitetura de implementação para o time de engenharia | **TDD** |

Quando um RFC é aprovado, frequentemente você cria um TDD a seguir para planejar a implementação.

## Como Usar

### Uso Básico

Basta pedir ao agente para escrever um RFC:

**English:**
```
Write an RFC for migrating our database from MySQL to PostgreSQL
```

**Portuguese:**
```
Escreva um RFC para migrar nosso banco de dados para PostgreSQL
```

**Spanish:**
```
Escribe un RFC para migrar nuestra base de datos a PostgreSQL
```

### Com Contexto Rico (mais rápido — pula perguntas)

```
Write an RFC for replacing our current logging infrastructure with OpenTelemetry.
We have 3 options: self-hosted Grafana stack, Datadog, or Honeycomb.
Main concern is cost and vendor lock-in. Decision needs approval from @CTO and @SRE-Lead by end of Q1.
```

### Fluxo Interativo

Se você fornecer contexto mínimo, a skill perguntará:

1. **Tópico e impacto**: O que está sendo proposto e o quão amplamente afeta sistemas/times
2. **Urgência**: Se há um prazo ou se isso é em aberto
3. **Opções**: Se você já tem alternativas em mente ou precisa de ajuda para estruturá-las

Em seguida, ela valida os campos obrigatórios antes de gerar o documento.

## Exemplos

### Exemplo 1: Seleção de Vendor/Ferramenta

**Sua solicitação:**
```
Write an RFC comparing self-hosted Kafka vs Amazon MSK vs Confluent Cloud for our event streaming needs
```

**O que acontece:**
1. O agente pergunta pelo prazo da decisão e quem aprova
2. O agente identifica isso como um RFC de Vendor Selection → adiciona comparação de custo e foco em risco de lock-in
3. O agente garante que os Decision Criteria sejam definidos antes de listar as opções
4. O agente gera o RFC com matriz de comparação entre as três opções

**Resultado:** Um RFC com:
- Background (configuração atual de event streaming e por que precisa mudar)
- Assumptions (ex.: "o tráfego não excederá 50k eventos/seg em 12 meses")
- Decision Criteria (custo, fardo operacional, lock-in de vendor, expertise do time — com pesos)
- Options: Self-hosted Kafka / Amazon MSK / Confluent Cloud + "Do Nothing"
- Matriz de Comparação de Opções
- Action Items (cronograma de PoC, revisão de segurança, aprovação de custo)
- Outcome (placeholder para a decisão aprovada)

### Exemplo 2: Mudança de Processo

**Sua solicitação:**
```
I need an RFC to propose changing our on-call rotation from weekly to bi-weekly shifts
```

**O que acontece:**
1. O agente identifica isso como um RFC de Process/Workflow
2. O agente pede dados que sustentem a proposta (ex.: relatórios de burnout, padrões de incidentes)
3. O agente gera o RFC focado no impacto no time e no plano de adoção

**Resultado:** Um RFC com:
- Background (pontos de dor da rotação atual com dados)
- Assumptions (ex.: "o tamanho do time permanece em 8 engenheiros")
- Decision Criteria (bem-estar do engenheiro, SLA de tempo de resposta, lacunas de cobertura)
- Options: Bi-weekly / Monthly / Rotação assistida por ferramenta + Do Nothing
- Action Items (piloto com um time, medir por 60 dias)

### Exemplo 3: Decisão de Arquitetura

**Sua solicitação:**
```
Draft an RFC for moving from our monolith to microservices
```

**O que acontece:**
1. O agente identifica impacto ALTO → garante que os Approvers sejam nomeados
2. O agente pede dados: Quais pontos de dor específicos o monolito causa?
3. O agente impõe a opção "Do Nothing" para avaliar honestamente o custo de não mudar

**Resultado:** Um RFC com:
- Background (limites de escala, acoplamento de deployment, dados de velocidade do time)
- Assumptions (ex.: "temos orçamento para investimento em platform engineering no H2")
- Decision Criteria (escalabilidade, autonomia do time, time to market, complexidade operacional)
- Options: Full microservices / Modular monolith / Strangler fig pattern / Do Nothing
- Matriz de Comparação (esforço, risco, reversibilidade, impacto no time)

## O Que o Agente Vai Perguntar (se o contexto estiver faltando)

**Sobre a proposta:**
- O que você está propondo e por que agora?
- O que acontece se você não tomar essa decisão?

**Sobre suposições:**
- O que você está dando como certo para que essa proposta funcione?
- O que precisaria ser verdade para sua opção preferida ter sucesso?

**Sobre critérios de decisão:**
- O que importa mais ao escolher entre opções?
- Há requisitos rígidos que desqualificariam uma opção?
- Como você pesa velocidade vs custo vs risco?

**Sobre stakeholders:**
- Quem está conduzindo essa proposta?
- Quem deve aprovar antes de qualquer avanço?
- Quem deve ser consultado vs apenas mantido informado?

**Sobre opções:**
- Quais alternativas você considerou?
- Você pensou em manter o status quo?

## O RFC Gerado

Todo RFC inclui:

1. **Cabeçalho e Metadados** — Impact (HIGH/MEDIUM/LOW), Status, Driver, Approver, Contributors, Informed, Due Date
2. **Background** — Estado atual, problema/oportunidade, por que agora, custo da inação
3. **Assumptions** — Suposições explícitas com níveis de confiança (High/Medium/Low) e gatilhos de invalidação
4. **Decision Criteria** — Critérios priorizados com pesos (Must-have / High / Medium / Low), definidos *antes* das opções
5. **Options Considered** — Cada opção com descrição, prós, contras e estimativa de esforço/risco/custo
6. **Options Comparison Matrix** — Visão lado a lado entre todas as opções e critérios
7. **Action Items** — Tarefas concretas com donos e prazos para depois da decisão
8. **Outcome** — Placeholder a ser preenchido quando a decisão for tomada, incluindo justificativa e follow-up

## Dicas para Melhores Resultados

### 1. Nomeie seus aprovadores antecipadamente

O motivo mais comum de RFCs travarem é a ausência de clareza sobre quem é o dono. Dizer ao agente quem precisa aprovar evita entradas placeholder `@TBD` nas quais ninguém age.

```
Write an RFC for adopting a monorepo. Approver is @VP-Engineering, contributors are @Frontend-Lead and @Backend-Lead.
```

### 2. Traga dados, mesmo que aproximados

RFCs com problemas quantificados são aprovados mais rápido. Mesmo números aproximados ajudam:

```
Our current CI pipeline takes ~45 minutes. We're spending roughly 20% of engineering time
waiting on builds. Write an RFC for switching to a faster CI provider.
```

### 3. Liste suas opções explicitamente

Se você já conhece as alternativas, nomeie-as. O agente não vai inventar opções ruins só para preencher o template.

```
Write an RFC comparing GitHub Actions, CircleCI, and Buildkite for our CI needs.
```

### 4. Declare suas restrições antecipadamente

```
Write an RFC for our logging solution. Must be SOC 2 compliant. Budget is under $2k/month.
Team has no Kubernetes experience.
```

Essas se tornam automaticamente seus Decision Criteria Must-have.

### 5. Use seu idioma

A skill detecta seu idioma automaticamente:

- **English**: "Write an RFC for..."
- **Portuguese**: "Escreva um RFC para..."
- **Spanish**: "Escribe un RFC para..."

## Suporte a Idiomas

| Idioma   | Gatilho de Exemplo                                      |
|------------|--------------------------------------------------------|
| English    | "Write an RFC for migrating to PostgreSQL"           |
| Portuguese | "Escreva um RFC para migrar para PostgreSQL"         |
| Spanish    | "Escribe un RFC para migrar a PostgreSQL"            |

Todos os cabeçalhos de seção e o conteúdo são gerados automaticamente no idioma detectado.

## O Que Torna Esta Skill Diferente

### 1. Decision Criteria Antes das Opções

A maioria dos templates de RFC lista opções primeiro e critérios por último — o que torna fácil escolher critérios que justificam a opção preferida depois do fato. Esta skill impõe critérios *antes* das opções, o que produz decisões que resistem ao escrutínio.

### 2. Suposições Explícitas com Gatilhos de Invalidação

Toda suposição tem um nível de confiança e um gatilho que a invalidaria. Isso transforma suposições de bombas-relógio invisíveis em riscos rastreados, e dá aos times um sinal claro de quando revisitar uma decisão.

### 3. "Do Nothing" Como Opção de Primeira Classe

O status quo é sempre uma opção. Incluí-lo honestamente força o time a articular o verdadeiro custo da inação — e às vezes revela que a mudança não vale o esforço.

### 4. Modelo de Stakeholder Baseado em RACI

Driver / Approver / Contributors / Informed separa "quem decide" de "quem aconselha" de "quem é notificado". Isso previne tanto o design-by-committee quanto decisões tomadas sem as pessoas certas na sala.

### 5. Consciente do Ciclo de Vida

O RFC rastreia status (NOT STARTED → IN PROGRESS → COMPLETE) e a seção Outcome é deixada explicitamente como placeholder durante o rascunho — para ser preenchida depois que os Approvers decidirem. Decisões são datadas e assinadas, criando uma trilha de auditoria.

## Casos de Uso Comuns

### Bons casos de uso para um RFC

- Adotar uma nova tecnologia, framework ou vendor
- Mudar um padrão arquitetural importante (ex.: monolito → microservices)
- Propor um novo processo ou política de engenharia
- Descontinuar um sistema ou API
- Tomar uma decisão de build-vs-buy
- Resolver um desacordo técnico significativo entre times
- Propor uma mudança de orçamento que requer aprovação da liderança

### Não ideal para um RFC

- Implementar algo já decidido (use um **TDD** em vez disso)
- Correções de bugs ou mudanças menores de código
- Decisões de um único time com um único aprovador e baixo impacto
- Spikes exploratórios (documente os achados em um texto separado primeiro)

## Estrutura de Exemplo de Saída

```markdown
# RFC: Adopt OpenTelemetry for Distributed Tracing

| Field        | Value                        |
|--------------|------------------------------|
| Impact       | HIGH                         |
| Status       | IN PROGRESS                  |
| Driver       | @platform-lead               |
| Approver     | @vp-engineering, @sre-lead   |
| Contributors | @backend-lead, @frontend-lead|
| Informed     | @engineering-all             |
| Due Date     | 2026-04-15                   |

## Background
[Current observability gaps, cost of incidents without tracing...]

## Assumptions
| # | Assumption | Confidence | Invalidation Trigger |
|---|------------|------------|----------------------|
| 1 | Team can dedicate 2 sprints to migration | Medium | If Q2 roadmap changes |

## Decision Criteria
| Priority | Criterion        | Weight    |
|----------|-----------------|-----------|
| 1        | Vendor-neutral  | Must-have |
| 2        | Cost < $3k/mo   | High      |
| 3        | Team familiarity| Medium    |

## Options Considered
### Option 1: OpenTelemetry + Grafana Tempo ⭐ (Recommended)
### Option 2: Datadog APM
### Option 3: Do Nothing

## Options Comparison
[Matrix across all options and criteria]

## Action Items
[Tasks with owners and due dates]

## Outcome
[To be filled after decision]
```

## Solução de Problemas

### O agente continua fazendo perguntas

Isso é intencional — a skill não vai gerar um RFC superficial. Responda às perguntas para obter um documento que resista a uma revisão de stakeholders. Se quiser pular adiante, forneça a informação faltante diretamente:

```
Driver is @me, Approver is @cto. Assumptions: team has capacity in Q2.
Decision criteria: cost first, then operational simplicity.
```

### Eu quero menos opções

Duas opções são o mínimo — uma não é uma escolha, é um anúncio. Se você só vê um caminho viável, faça da segunda opção "Do Nothing" e argumente honestamente por que ela é pior.

### O RFC está muito longo

Especifique o escopo antecipadamente:

```
Write a concise RFC for a LOW impact decision — just Background, two options, and Action Items.
```

### Preciso atualizar uma decisão que já foi tomada

RFCs são registros históricos. Em vez de editar o Outcome de um RFC passado, escreva um novo RFC que referencie o original e proponha uma mudança. Isso preserva a trilha de auditoria.

## Próximos Passos Após Criar um RFC

1. **Compartilhe** com os Contributors para feedback (defina um prazo para comentários)
2. **Apresente** aos Approvers em uma reunião de revisão
3. **Registre** a decisão na seção Outcome com a justificativa
4. **Notifique** as partes Informed sobre a decisão
5. **Crie um TDD** se a opção aprovada exigir planejamento de implementação
6. **Arquive** o RFC onde o time possa encontrá-lo depois (Confluence, Notion, GitHub)

## Suporte

Para problemas ou perguntas sobre esta skill, consulte o [repositório principal agent-skills](https://github.com/tech-leads-club/agent-skills).
