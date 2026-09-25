# subagent-creator

Guia agnóstico de ferramenta para criar **subagents de IA** — assistentes especializados com contexto isolado, aos quais um agente principal pode delegar tarefas complexas e multi-etapas. Diferente do `cursor-subagent-creator`, esta skill não assume nenhum editor ou plataforma específica: funciona com qualquer agente que suporte delegação de subagents.

## O que faz

- Explica o conceito de subagent: contexto isolado, execução paralela, especialização via prompt próprio, reuso entre contextos.
- Apresenta uma árvore de decisão simples para escolher entre Subagent e Skill, com base em complexidade da tarefa e necessidade de isolamento de contexto.
- Detalha a estrutura típica de um subagent: arquivo Markdown com frontmatter (`name`, `description`, `model`, `readonly`) seguido do prompt em si.
- Orienta o processo de criação: definir propósito, configurar metadados, escrever o prompt (identidade, "when invoked", processo, saída esperada).
- Fornece 4 padrões de subagent prontos para reuso: Verification Agent, Debugger, Security Auditor, Code Reviewer.
- Lista boas práticas (DO/AVOID) e um checklist de qualidade antes de finalizar um subagent.
- Define o formato de mensagem de saída ao concluir a criação de um subagent.

## Quando usar

- "create subagent" / "new agent" / "specialized assistant" / "create verifier"
- Pedido para criar um agente especializado, verificador, debugger ou orquestrador que precise de contexto isolado e especialização profunda
- Funciona com qualquer agente/plataforma que suporte delegação de subagents (não específico de editor)

Não use quando: o subagent for especificamente para o Cursor (nesse caso use `cursor-subagent-creator`, que segue os padrões e diretórios próprios do Cursor, como `.cursor/agents/`).

## Exemplo de uso

Template de subagent sugerido pela skill:

```markdown
---
name: [agent-name]
description: [Expert in X]. Use when [contexto específico de delegação].
model: inherit
---

You are an [expert in X] specialized in [Y].

When invoked:
1. [Primeira ação]
2. [Segunda ação]
3. [Terceira ação]

Report [tipo de resultado]:
- [Formato específico]
- [Informação a incluir]
- [Métricas ou critérios]
```

Mensagem final sugerida após criar o subagent:

```
✅ Subagent created successfully!

📁 Location: .agent/subagents/[name].md
🎯 Purpose: [breve descrição]
🔧 How to invoke:
   - Automatic: Agent delegates when it detects [contexto]
   - Explicit: /[name] [instrução]

💡 Tip: inclua frases como "use proactively" para incentivar delegação automática.
```
