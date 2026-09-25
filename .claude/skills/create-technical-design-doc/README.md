# Technical Design Doc Creator

Uma skill para agentes de codificação de IA que ajuda a criar Technical Design Documents (TDDs) abrangentes seguindo os padrões da indústria.

## O Que Ela Faz

Esta skill orienta agentes de IA a criar Technical Design Documents bem estruturados que incluem:

- **Seções obrigatórias**: Context, Problem Statement, Scope, Technical Solution, Risks, Implementation Plan
- **Seções críticas**: Security (para pagamentos/auth), Monitoring, Rollback Plan, Testing Strategy
- **Seções opcionais**: Success Metrics, Glossary, Alternatives Considered, Dependencies, Performance Requirements, e mais

A skill se adapta automaticamente a:

- **Tamanho do projeto**: Small (< 1 semana), Medium (1-4 semanas), Large (> 1 mês)
- **Tipo de projeto**: Integration, Feature, Refactor, Infrastructure, Payment, Auth, Data migration
- **Idioma do usuário**: Gera automaticamente o TDD em português, inglês ou espanhol com base na sua solicitação

## Como Usar

### Uso Básico

Basta pedir ao agente de IA para criar um TDD:

**English:**

```
Create a TDD for Stripe payment integration
```

**Portuguese:**

```
Crie um TDD para integração com Stripe
```

**Spanish:**

```
Crea un TDD para integración con Stripe
```

### Fluxo Interativo

A skill vai te guiar por um processo interativo:

1. **Perguntas Iniciais**: Nome do projeto, tamanho, tipo e clareza do contexto
2. **Informação Obrigatória**: Problem statement, scope, abordagem técnica
3. **Seções Críticas**: Security, monitoring, rollback (se aplicável)
4. **Seções Opcionais**: Success metrics, glossário, alternativas, etc.

### Exemplos

#### Exemplo 1: Integração de Pagamento

**Sua Solicitação:**

```
Create a TDD for integrating Stripe payments into our subscription system
```

**O Que Acontece:**

1. O agente pergunta sobre o tamanho e tipo do projeto
2. O agente solicita: problem statement, scope, abordagem técnica
3. O agente identifica que é um sistema de pagamento → **a seção Security se torna OBRIGATÓRIA**
4. O agente pergunta por: requisitos de segurança, métricas de monitoramento, plano de rollback
5. O agente gera um TDD abrangente com todas as seções necessárias

**Resultado:** Um TDD completo com:

- Contexto e problem statement
- Funcionalidades dentro/fora do escopo
- Diagrama de arquitetura
- Contratos de API
- Considerações de segurança (compliance PCI DSS, criptografia, tratamento de PII)
- Estratégia de testes
- Monitoramento e observabilidade
- Plano de rollback
- Cronograma de implementação

#### Exemplo 2: Funcionalidade Simples

**Sua Solicitação:**

```
Write a design doc for adding user profile pictures
```

**O Que Acontece:**

1. O agente identifica que é uma funcionalidade pequena
2. O agente pede informações básicas
3. O agente gera um TDD simplificado apenas com as seções essenciais

**Resultado:** Um TDD focado com:

- Contexto
- Problem statement
- Scope (dentro/fora)
- Solução técnica (upload de arquivo, armazenamento, endpoints de API)
- Riscos
- Plano de implementação
- Estratégia de testes

#### Exemplo 3: Projeto de Migração

**Sua Solicitação:**

```
Crie um TDD para migração do banco de dados PostgreSQL para MongoDB
```

**O Que Acontece:**

1. O agente detecta o idioma português → gera o TDD em português
2. O agente identifica que é um projeto de migração
3. O agente solicita: estratégia de migração, mapeamento de dados, plano de rollback
4. O agente oferece a seção de plano de migração

**Resultado:** Um TDD em português com:

- Contexto (Context)
- Definição do Problema (Problem Statement)
- Escopo (Scope)
- Solução Técnica (Technical Solution)
- Plano de Migração (Migration Plan)
- Plano de Rollback (Rollback Plan)
- Estratégia de Testes (Testing Strategy)

## O Que Esperar

### O Agente Vai Fazer Perguntas

A skill é projetada para coletar informações completas. Espere perguntas como:

**Para Problem Statement:**

- Qual problema estamos resolvendo?
- Por que isso é importante agora?
- O que acontece se não resolvermos?

**Para Scope:**

- O que SERÁ entregue na V1?
- O que NÃO será incluído (fora do escopo)?

**Para Abordagem Técnica:**

- Quais são os componentes principais?
- Como os dados fluem pelo sistema?
- Quais APIs serão criadas/modificadas?

**Para Projetos de Pagamento/Auth:**

- Como você vai lidar com autenticação?
- Qual criptografia será usada?
- Quais PII são coletados?
- Há requisitos de compliance (GDPR, PCI DSS)?

**Para Sistemas em Produção:**

- Como você vai monitorar isso?
- Quais métricas importam?
- Como você fará rollback se algo falhar?

### O TDD Gerado

O TDD vai incluir:

1. **Cabeçalho e Metadados**: Tech Lead, Time, link do Epic, Status, Datas
2. **Contexto**: Background, domínio, stakeholders
3. **Problem Statement**: Problemas específicos com impacto quantificado
4. **Scope**: Itens claros dentro e fora do escopo
5. **Solução Técnica**: Arquitetura, fluxo de dados, APIs, mudanças de banco de dados
6. **Riscos**: Matriz de risco com impacto, probabilidade e mitigação
7. **Plano de Implementação**: Divisão em fases com estimativas
8. **Security** (se aplicável): Autenticação, criptografia, compliance
9. **Estratégia de Testes**: Planos de teste unitário, integração, E2E
10. **Monitoramento e Observabilidade**: Métricas, alertas, dashboards
11. **Plano de Rollback**: Gatilhos e passos para revertimento de mudanças
12. **Seções opcionais**: Success metrics, glossário, alternativas, dependências, etc.

## Dicas para Melhores Resultados

### 1. Forneça Contexto Antecipadamente

Ao invés de:

```
Create a TDD for Stripe
```

Tente:

```
Create a TDD for integrating Stripe payments. We need to support subscriptions,
handle webhooks, and comply with PCI DSS. This is for our SaaS product.
```

### 2. Seja Específico Sobre o Escopo

O agente vai perguntar, mas você pode fornecer antecipadamente:

```
Create a TDD for user authentication. In scope: email/password, JWT tokens,
password reset. Out of scope: OAuth, 2FA, social login (those are V2).
```

### 3. Mencione o Tamanho do Projeto

```
Create a TDD for the database migration project. This is a large project
(expected 2 months).
```

### 4. Especifique Requisitos Críticos

Para sistemas de pagamento/auth, mencione requisitos de segurança:

```
Create a TDD for Stripe integration. We need PCI DSS compliance, webhook
signature validation, and encrypted storage of payment method tokens.
```

### 5. Use Seu Idioma

A skill detecta automaticamente seu idioma. Apenas escreva naturalmente:

- **English**: "Create a TDD for..."
- **Portuguese**: "Crie um TDD para..."
- **Spanish**: "Crea un TDD para..."

## Suporte a Idiomas

A skill suporta múltiplos idiomas:

| Idioma   | Gatilho de Exemplo                           |
| ---------- | ----------------------------------------- |
| English    | "Create a TDD for Stripe integration"     |
| Portuguese | "Crie um TDD para integração com Stripe"  |
| Spanish    | "Crea un TDD para integración con Stripe" |

Todos os cabeçalhos de seção e o conteúdo são automaticamente traduzidos para corresponder ao seu idioma.

## Integração com Outras Skills

### Publicação no Confluence

Depois de gerar um TDD, o agente vai oferecer para publicá-lo no Confluence:

```
Would you like me to publish this TDD to Confluence?
- I can create a new page in your space
- Or update an existing page
```

### Integração com Jira

O TDD inclui uma seção de metadados para links de Epic/Ticket. Você pode adicionar manualmente ou pedir ao agente para ajudar a criar tickets do Jira.

## O Que Torna Esta Skill Diferente

### 1. Padrões da Indústria

Segue padrões de:

- Google Design Docs
- Amazon PR-FAQ (Working Backwards)
- RFC Pattern
- ADR (Architecture Decision Records)
- SRE Book (Monitoring, Rollback, SLOs)
- PCI DSS & OWASP (Security)

### 2. Focado em Arquitetura, Não em Implementação

O TDD documenta **decisões e contratos**, não código:

✅ **Inclui**: contratos de API, schemas de dados, diagramas de arquitetura, estratégias
❌ **Evita**: comandos CLI, trechos de código, implementação específica de framework

### 3. Adaptativo ao Tamanho do Projeto

- **Projetos pequenos**: Apenas seções essenciais (7-9 seções)
- **Projetos médios**: Seções obrigatórias + críticas (11-13 seções)
- **Projetos grandes**: Todas as seções (até 20 seções)

### 4. Imposição de Seções Obrigatórias

O agente vai **insistir** em completar as seções obrigatórias antes de finalizar o TDD. Você não pode pular:

- Problem Statement
- Scope
- Technical Solution
- Risks
- Implementation Plan

### 5. Seções Críticas para Tipos de Projeto Específicos

- **Payment/Auth**: A seção Security é OBRIGATÓRIA
- **Production**: Monitoring e Rollback são OBRIGATÓRIOS
- **Integration**: Dependencies e Security são altamente recomendados

## Casos de Uso Comuns

### ✅ Bons Casos de Uso

- Desenvolvimento de nova funcionalidade
- Integração de API externa
- Migração ou refatoração de sistema
- Mudanças de infraestrutura
- Design de sistema de pagamento/cobrança
- Sistema de autenticação/autorização
- Pipelines de processamento de dados

### ❌ Não Ideal Para

- Correções de bugs (muito pequeno)
- Refatoração de código sem mudanças arquiteturais
- Atualizações de documentação
- Mudanças simples de configuração

## Estrutura de Exemplo de Saída

```
# TDD - [Project Name]

## Metadata
- Tech Lead: @Name
- Team: Name1, Name2
- Status: Draft
- Created: 2026-02-04

## Context
[Background and domain description]

## Problem Statement & Motivation
[Specific problems with impact]

## Scope
### ✅ In Scope
[What will be delivered]

### ❌ Out of Scope
[What won't be included]

## Technical Solution
[Architecture, APIs, data flow, database changes]

## Risks
[Risk matrix with mitigation]

## Implementation Plan
[Phased breakdown with estimates]

## Security Considerations
[Authentication, encryption, compliance]

## Testing Strategy
[Unit, integration, E2E tests]

## Monitoring & Observability
[Metrics, alerts, dashboards]

## Rollback Plan
[Triggers and steps]

[Additional optional sections...]
```

## Solução de Problemas

### O Agente Continua Fazendo Perguntas

**Isso é normal!** A skill é projetada para coletar informações completas. Responda às perguntas para obter um TDD abrangente.

### Eu Quero Pular Uma Seção

Seções obrigatórias não podem ser puladas. Para seções opcionais, você pode dizer:

```
Skip the Alternatives Considered section for now
```

### O TDD Está Muito Detalhado

Para projetos pequenos, especifique o tamanho:

```
This is a small project (< 1 week), keep it simple
```

### Está Faltando Algo no TDD

Diga ao agente o que está faltando:

```
Add a section on performance requirements
```

## Próximos Passos Após Criar um TDD

1. **Revisar**: Verifique se todas as seções estão completas
2. **Compartilhar**: Obtenha feedback dos membros do time
3. **Aprovar**: Obtenha sign-off dos stakeholders
4. **Implementar**: Use o TDD como guia durante o desenvolvimento
5. **Atualizar**: Mantenha o TDD atualizado conforme o projeto evolui

## Suporte

Para problemas ou perguntas sobre esta skill, consulte o [repositório principal agent-skills](https://github.com/tech-leads-club/agent-skills).
