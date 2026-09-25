# ADR Creator

Uma skill para agentes de codificação de IA que cria Architecture Decision Records (ADRs) — documentos concisos e duráveis que capturam o contexto, a decisão e as consequências de escolhas arquiteturais significativas, para que futuros engenheiros entendam *por que* as coisas são da forma que são.

## O Que Ela Faz

Esta skill orienta agentes de IA a criar ADRs bem estruturados em três formatos padrão da indústria:

- **MADR** (Markdown Architectural Decision Records) — estruturado com comparação de opções, recomendado para a maioria dos times
- **Nygard** — formato original mínimo: Context / Decision / Consequences
- **Y-Statement** — formato compacto de um único parágrafo para documentação inline

A skill automaticamente:

- Atribui o próximo número sequencial de ADR escaneando seu diretório `docs/adr/`
- Detecta seu idioma e gera o ADR nesse idioma (por exemplo, inglês, português, espanhol)
- Orienta você com perguntas se o contexto estiver faltando
- Aplica convenções de nomenclatura (`001-kebab-case-title.md`)
- Liga corretamente ADRs substituídos/substitutos

## ADR vs RFC — Qual Você Precisa?

| Pergunta | Use |
|----------|-----|
| Devemos fazer X? Qual opção? | **RFC** |
| Já decidimos — documentar para futuros engenheiros | **ADR** |
| Precisa de aprovação da liderança antes de agir | **RFC** |
| Precisa preservar a justificativa de uma escolha passada | **ADR** |

**Regra prática**: RFC conduz a decisão. ADR a registra. Um fluxo comum é RFC → reunião de decisão → ADR.

## Como Usar

### Uso Básico

Basta dizer ao agente que você quer um ADR:

**English:**
```
Write an ADR for using PostgreSQL as our primary database
```

**Portuguese:**
```
Escreva um ADR para documentar a decisão de usar PostgreSQL
```

**Spanish:**
```
Escribe un ADR sobre la decisión de usar microservicios
```

### Com Contexto Rico (mais rápido — pula a maioria das perguntas)

```
Write an ADR for adopting GraphQL over REST for our public API.
We evaluated REST, GraphQL, and gRPC. Chose GraphQL because our clients
need flexible queries and we're building a public partner API.
Main trade-off is increased backend complexity. Status: Accepted.
```

### Modo Interativo

Se você fornecer contexto mínimo, a skill perguntará:

1. **Formato**: MADR (estruturado), Nygard (mínimo), ou Y-Statement (compacto)?
2. **Status**: Accepted, Proposed, Deprecated, ou Superseded?
3. **Substitui**: Esta decisão substitui um ADR anterior?

Em seguida, ela valida os campos obrigatórios antes de gerar o documento.

## Formatos de ADR

### MADR (Recomendado)

Melhor para decisões em que múltiplas opções foram seriamente avaliadas. Inclui uma comparação estruturada de opções.

```markdown
# ADR-003: Use Redis for Session Storage

- **Date**: 2026-03-10
- **Status**: Accepted

## Context and Problem Statement
Our API requires fast session lookups at high concurrency...

## Decision Drivers
- Must support 50k concurrent sessions
- TTL-based expiry required

## Considered Options
- Redis (chosen)
- PostgreSQL session table
- JWT stateless tokens

## Decision Outcome
Chosen: **Redis**, because TTL support and in-memory performance...

### Positive Consequences
- Sub-millisecond session reads
- Built-in expiry without cron jobs

### Negative Consequences
- Additional service to operate
- Session data lost on Redis restart without persistence config
```

### Nygard (Mínimo)

Melhor para registro rápido de decisões diretas.

```markdown
# ADR-003: Use Redis for Session Storage

## Status
Accepted

## Context
Our API needs fast, expirable session storage at scale...

## Decision
We will use Redis for session storage, managed via AWS ElastiCache...

## Consequences
Fast reads with native TTL. Adds operational complexity.
```

### Y-Statement (Compacto)

Melhor para incorporar decisões inline ou em culturas de documentação muito enxutas.

```markdown
In the context of **high-concurrency session storage**,
facing **the need for automatic expiry and sub-millisecond reads**,
we decided **to use Redis**,
to achieve **low-latency session lookups with zero manual cleanup**,
accepting **the operational overhead of an additional managed service**.
```

## O Que o Agente Vai Perguntar (se o contexto estiver faltando)

**Sobre a decisão:**
- O que foi decidido? (frase nominal — ex.: "Use PostgreSQL for primary storage")
- Qual é o status atual — Accepted, Proposed, Deprecated, ou Superseded?

**Sobre o contexto:**
- Qual situação ou forças levaram a essa decisão?
- Quais restrições existiam (técnicas, de negócio, de time)?

**Sobre alternativas:**
- Quais outras opções foram consideradas?
- Por que foram rejeitadas?

**Sobre consequências:**
- O que se torna mais fácil ou melhor como resultado?
- Quais trade-offs ou desvantagens você está aceitando?

**Sobre histórico:**
- Isso substitui um ADR anterior?

## O ADR Gerado

Todo ADR inclui:

1. **Título** — frase nominal registrando a decisão (não uma pergunta)
2. **Metadados** — data, status, decisores, tags
3. **Contexto** — as forças e restrições que tornaram essa decisão necessária
4. **Decisão** — o que foi escolhido e por quê, com justificativa honesta
5. **Consequências** — consequências positivas e negativas dessa escolha
6. **Opções** (MADR) — alternativas consideradas com prós/contras por opção
7. **Links** — ADRs relacionados, RFCs, tickets e relações de substituição

## Convenção de Nomenclatura de Arquivos

ADRs vivem em um diretório dedicado, numerados sequencialmente:

```
docs/adr/
├── 001-use-postgresql-for-primary-storage.md
├── 002-adopt-event-driven-architecture.md
├── 003-use-redis-for-session-storage.md
└── README.md   ← índice opcional
```

A skill escaneia seus ADRs existentes para atribuir o próximo número correto.

Localizações comuns de diretório: `docs/adr/`, `docs/decisions/`, `adr/`, `.adr/`

## Dicas para Melhores Resultados

### 1. O título é uma frase nominal, não uma pergunta

```
❌ Should we use Redis for sessions?
✅ Use Redis for Session Storage
```

### 2. O contexto explica as *forças*, não apenas os fatos

```
❌ We needed a session store.
✅ Our API must support 50k concurrent sessions with automatic expiry.
   The team evaluated Redis, PostgreSQL, and stateless JWTs. PostgreSQL
   was ruled out due to TTL complexity; JWTs were ruled out because
   server-side revocation is required for security compliance.
```

### 3. As consequências são honestas sobre trade-offs

```
❌ Redis é rápido e fácil de usar.
✅ Leituras de sessão rápidas com suporte nativo a TTL.
   Adiciona um serviço gerenciado adicional à nossa infraestrutura.
   Os dados da sessão ficam em risco se a persistência do Redis estiver mal configurada..
```

### 4. Sempre substitua, nunca edite

Quando uma decisão muda, crie um novo ADR e marque o antigo como substituído. Isso preserva o contexto histórico — a decisão antiga estava correta *dado o que se sabia na época*.

### 5. Mantenha curto

Meta de 200–500 palavras. Se a decisão precisar de explicação extensa, link para o RFC ou TDD que a conduziu. ADRs são auxiliares de memória, não guias de implementação.

## Casos de Uso Comuns

### Bons casos de uso para um ADR

- Escolher um banco de dados, message broker ou tecnologia de infraestrutura
- Adotar um novo framework ou linguagem
- Selecionar um padrão arquitetural (event-driven, CQRS, BFF, etc.)
- Decidir sobre um estilo de API (REST, GraphQL, gRPC)
- Escolher uma estratégia de deployment (blue-green, canary, feature flags)
- Escolher uma estratégia de testes ou toolchain de CI/CD
- Registrar uma decisão de segurança ou compliance

### Não ideal para um ADR

- Decisões ainda não tomadas — use **RFC** para conduzir a decisão primeiro
- Planos de implementação — use **TDD** para como construir algo
- Escolhas triviais (convenções de nomenclatura, valores menores de configuração)
- Spikes exploratórios — escreva os achados separadamente e depois registre a decisão em um ADR

## Suporte a Idiomas

| Idioma | Gatilho de Exemplo |
|----------|-----------------|
| English | "Write an ADR for using PostgreSQL" |
| Portuguese | "Escreva um ADR para documentar o uso do PostgreSQL" |
| Spanish | "Escribe un ADR sobre la decisión de usar PostgreSQL" |

Todos os cabeçalhos de seção e o conteúdo são gerados automaticamente no idioma detectado.

## Próximos Passos Após Criar um ADR

1. **Comite** o ADR no seu repositório junto com o código que ele documenta
2. **Linke** a partir do código, PR ou RFC relevante que o disparou
3. **Atualize** seu índice de ADR (`docs/adr/README.md`) se você mantiver um
4. **Referencie** o ADR em descrições de PR ao implementar a decisão
5. **Substitua** com um novo ADR se a decisão mudar — nunca edite o antigo

## Suporte

Para problemas ou perguntas sobre esta skill, consulte o [repositório principal agent-skills](https://github.com/tech-leads-club/agent-skills).
