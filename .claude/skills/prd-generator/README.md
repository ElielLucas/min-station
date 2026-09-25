# PRD Generator

Uma skill para agentes de codificação de IA que ajuda product managers e times de produto a criar Product Requirements Documents (PRDs) abrangentes, bem estruturados e alinhados às melhores práticas da indústria.

## O Que Ela Faz

Esta skill orienta agentes de IA a criar PRDs completos que incluem:

- **Seções padrão**: Executive Summary, Problem Statement, Goals & Objectives, User Personas, User Stories, Success Metrics, Scope, Technical Considerations, Design & UX, Timeline, Risks, Dependencies e Open Questions
- **User stories estruturadas**: formato "As a / I want / So that" com acceptance criteria testáveis
- **Frameworks de métricas**: AARRR, HEART, North Star Metric e OKRs
- **Formatos adaptáveis**: PRD completo, Lean PRD, One-Pager, Technical PRD ou Design PRD

A skill automaticamente:

- Conduz uma fase de discovery quando o contexto está incompleto
- Usa o template em `references/prd_template.md` como base estrutural
- Consulta `references/user_story_examples.md` e `references/metrics_frameworks.md` quando necessário
- Pode validar o documento final com `scripts/validate_prd.sh`

## PRD vs RFC vs TDD — Qual Você Precisa?

| Pergunta | Use |
|----------|-----|
| O que vamos construir e por quê? Quais requisitos e métricas de sucesso? | **PRD** |
| Devemos fazer X? Qual opção escolher entre alternativas? | **RFC** |
| Já decidimos — como implementar tecnicamente? | **TDD** |
| Precisa alinhar stakeholders de produto, design e engenharia antes de desenvolver | **PRD** |
| Precisa documentar uma decisão arquitetural já tomada | **ADR** |

**Regra prática**: PRD define *o quê* e *por quê*. RFC conduz *se* e *qual caminho*. TDD detalha *como* construir. ADR registra *por que* uma decisão técnica foi tomada.

## Como Usar

### Uso Básico

Basta pedir ao agente para criar um PRD:

**English:**
```
Create a PRD for adding dark mode to our mobile app
```

**Portuguese:**
```
Crie um PRD para adicionar modo escuro no nosso app mobile
```

**Spanish:**
```
Crea un PRD para agregar modo oscuro a nuestra app móvil
```

### Com Contexto Rico (mais rápido — pula a maioria das perguntas)

```
Create a PRD for improving our checkout flow conversion.
Current conversion is 2.1%. Main drop-off at payment step.
Target users: mobile shoppers 25-45. Goal: increase conversion to 3% in Q2.
Out of scope: redesign of product catalog.
```

### Modo Interativo

Se você fornecer contexto mínimo, a skill perguntará:

1. **Nome do feature/produto**: O que estamos construindo?
2. **Problem statement**: Qual problema resolve?
3. **Usuários-alvo**: Para quem é?
4. **Objetivos de negócio**: O que queremos alcançar?
5. **Métricas de sucesso**: Como medimos?
6. **Timeline e restrições**: Prazos ou limitações?
7. **Escopo**: O que fica explicitamente fora?

Em seguida, ela gera o PRD usando o template padrão.

## Formatos de PRD

| Formato | Quando usar | Tamanho típico |
|---------|-------------|----------------|
| **Standard PRD** | Features ou produtos novos com múltiplos stakeholders | Documento completo |
| **Lean PRD** | Times ágeis com escopo já alinhado | Seções essenciais |
| **One-Pager** | Pequenas melhorias ou correções | 1–2 páginas |
| **Technical PRD** | Requisitos com foco em engenharia | Ênfase em arquitetura e dependências |
| **Design PRD** | Features com foco em UX/UI | Ênfase em fluxos, acessibilidade e design system |

Especifique o formato na solicitação: *"Create a lean PRD for..."* ou *"Crie um one-pager para..."*.

## Seções do PRD Gerado

Todo PRD padrão inclui:

1. **Executive Summary** — visão geral em 2–3 parágrafos
2. **Problem Statement** — problema claro e mensurável
3. **Goals & Objectives** — objetivos alinhados ao negócio
4. **User Personas** — quem são os usuários
5. **User Stories & Requirements** — requisitos funcionais detalhados
6. **Success Metrics** — KPIs com targets
7. **Scope** — in-scope e out-of-scope explícitos
8. **Technical Considerations** — arquitetura, dependências, segurança, performance
9. **Design & UX Requirements** — padrões visuais, acessibilidade, fluxos
10. **Timeline & Milestones** — fases e datas-chave
11. **Risks & Mitigation** — riscos e planos de mitigação
12. **Dependencies & Assumptions** — premissas e dependências externas
13. **Open Questions** — itens pendentes de decisão

## User Stories

Formato padrão gerado pela skill:

```markdown
As a [tipo de usuário],
I want to [ação],
So that [benefício/valor].

Acceptance Criteria:
- [Critério testável 1]
- [Critério testável 2]
- [Critério testável 3]
```

## Scripts Incluídos

### Gerar PRD interativamente

```bash
./scripts/generate_prd.sh
```

Workflow interativo que coleta informações e gera um arquivo PRD a partir do template.

### Validar PRD existente

```bash
./scripts/validate_prd.sh meu_prd.md
./scripts/validate_prd.sh meu_prd.md --verbose
./scripts/validate_prd.sh meu_prd.md --sections user-stories,metrics
```

Verifica seções obrigatórias, formato de user stories, métricas definidas, escopo articulado e placeholders pendentes.

## Exemplos

### Exemplo 1: Feature mobile

**Sua solicitação:**
```
Create a PRD for adding biometric authentication to our iOS app
```

**O que acontece:**
1. O agente pergunta sobre requisitos de segurança, personas e autenticação existente
2. Gera PRD com problem statement, user stories (biometria, fallback, configurações), métricas (adoção, taxa de login) e considerações técnicas (Keychain, LocalAuthentication)
3. Documenta riscos (compatibilidade de dispositivos, privacidade)

### Exemplo 2: Melhoria de conversão

**Sua solicitação:**
```
Write requirements for improving our checkout flow conversion
```

**O que acontece:**
1. Coleta dados sobre taxa atual e pontos de abandono
2. Gera PRD com análise do estado atual, melhorias propostas, plano de A/B test
3. Define métricas before/after e user stories priorizadas

### Exemplo 3: Produto B2B

**Sua solicitação:**
```
I need a PRD for an admin dashboard for enterprise customers
```

**O que acontece:**
1. Identifica requisitos B2B (multi-tenancy, permissões, relatórios)
2. Gera personas enterprise (admin, manager, analyst)
3. Inclui RBAC, integrações (SSO, SCIM) e métricas de adoção

## O Que o Agente Vai Perguntar (se o contexto estiver faltando)

**Sobre o produto:**
- Qual feature ou produto estamos documentando?
- Qual problema resolve e para quem?

**Sobre negócio:**
- Quais objetivos de negócio e métricas de sucesso?
- Qual o timeline e restrições conhecidas?

**Sobre escopo:**
- O que está explicitamente fora do escopo?
- Existe MVP vs. nice-to-have já definido?

**Sobre contexto técnico:**
- Há dependências, integrações ou restrições técnicas conhecidas?

## Dicas para Melhores Resultados

### 1. Comece pelo problema, não pela solução

```
❌ Quero um botão de dark mode no settings
✅ Usuários reclamam de fadiga visual ao usar o app à noite — precisamos de tema escuro configurável
```

### 2. Métricas concretas, não adjetivos vagos

```
❌ A feature deve ser rápida e intuitiva
✅ Tempo de carregamento < 2s; taxa de adoção do tema escuro ≥ 40% em 30 dias
```

### 3. Escopo explícito previne creep

```
Out of scope (v1):
- Sincronização cross-device de preferências
- Temas customizados além de claro/escuro
```

### 4. Forneça contexto de pesquisa quando tiver

Dados de entrevistas, analytics, feedback de clientes ou análise competitiva aceleram a geração e melhoram a qualidade.

### 5. Escolha o formato certo

Pequenas correções → One-Pager. Iniciativas estratégicas → Standard PRD completo.

## Casos de Uso Comuns

### Bons casos de uso para um PRD

- Nova feature de produto (mobile, web, B2B)
- Melhoria significativa de fluxo existente
- Novo produto ou módulo com múltiplos stakeholders
- Requisitos de compliance com deadline fixo (GDPR, HIPAA)
- Documentação de dívida técnica com impacto visível ao usuário

### Não ideal para um PRD

- Decisão entre alternativas ainda não escolhida — use **RFC**
- Plano de implementação técnica detalhado — use **TDD**
- Registro de decisão arquitetural já tomada — use **ADR**
- Documentação de API ou contrato técnico — use documentação de engenharia

## Suporte a Idiomas

| Idioma | Gatilho de Exemplo |
|--------|-------------------|
| English | "Create a PRD for user authentication" |
| Portuguese | "Crie um PRD para autenticação de usuários" |
| Spanish | "Crea un PRD para autenticación de usuarios" |

O conteúdo do PRD é gerado no idioma detectado na sua solicitação.

## Solução de Problemas

### O agente continua fazendo perguntas

Isso é intencional — a skill não gera PRDs superficiais. Responda às perguntas ou forneça contexto rico antecipadamente para pular a discovery.

### O PRD ficou muito longo

Peça um formato enxuto:

```
Create a lean PRD for this small feature — problem, solution, acceptance criteria and metrics only.
```

### Requisitos muito vagos

Peça exemplos concretos, números e referências visuais. Substitua "rápido" por "carrega em menos de 2 segundos".

### Escopo expandindo

Use a seção Out-of-Scope agressivamente e crie PRDs separados para fases futuras.

## Próximos Passos Após Criar um PRD

1. **Revise com stakeholders** — produto, design, engenharia e negócio
2. **Valide com o script** — `scripts/validate_prd.sh` para checar completude
3. **Priorize user stories** — defina MVP antes do desenvolvimento
4. **Linke artefatos** — mockups, RFCs relacionados, ADRs de decisões técnicas
5. **Mantenha atualizado** — PRDs são documentos vivos; ajuste conforme o entendimento evolui

## Suporte

Para problemas ou perguntas sobre esta skill, consulte o [repositório agent-playbook](https://github.com/jamesrochabrun/skills/tree/main/skills/prd-generator).
