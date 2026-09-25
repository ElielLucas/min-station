# cursor-subagent-creator

Skill que ensina o agente a criar **subagents específicos do Cursor** — arquivos Markdown em `.cursor/agents/` (ou `~/.cursor/agents/`) que o Cursor Agent pode delegar tarefas complexas e multi-etapas, com contexto isolado e execução paralela. É a versão "Cursor-aware" do `subagent-creator`, seguindo os padrões e diretórios específicos do editor (frontmatter com `model`, `readonly`, `is_background`, sintaxe `/nome`, resume via agent ID etc.).

## O que faz

- Orienta a definição do propósito do subagent (responsabilidade única, necessidade de contexto isolado, múltiplos passos, especialização).
- Explica onde salvar o arquivo: projeto (`.cursor/agents/agent-name.md`) ou usuário (`~/.cursor/agents/agent-name.md`), com convenção kebab-case.
- Detalha o frontmatter aceito pelo Cursor: `name`, `description` (crítico para delegação automática), `model` (`inherit` | `fast` | ID específico), `readonly`, `is_background`.
- Fornece template de prompt para o corpo do subagent: identidade, "when invoked", passos, formato de saída esperado.
- Traz 6 padrões prontos para reuso: Verification Agent, Debugger, Security Auditor, Test Runner, Documentation Writer, Orchestrator.
- Documenta como invocar (delegação automática, `/nome`, menção natural, execução paralela) e como retomar subagents em background (`~/.cursor/subagents/`).
- Lista boas práticas (DO/AVOID) e uma árvore de decisão Skill vs Subagent vs Slash Command.
- Define checklist de qualidade e o formato de mensagem de saída ao final da criação (local do arquivo, propósito, como invocar).

## Quando usar

- "criar subagent no Cursor" / "cursor subagent" / "cursor agent"
- Pedido para criar um assistente especializado, verificador, debugger ou orquestrador especificamente para o Cursor
- Tarefas complexas e multi-etapas que precisam de contexto isolado dentro do editor Cursor

Não use quando: a criação de subagent não for específica do Cursor (nesse caso use `subagent-creator`, que é agnóstico de agente); ou quando a tarefa for simples e pontual — nesse caso a skill recomenda usar uma **skill** comum em vez de um subagent.

## Exemplo de uso

Template rápido de subagent gerado pela skill:

```markdown
---
name: [agent-name]
description: [Expert em X]. Use when [contexto específico de delegação].
model: inherit
---

You are an [expert in X] specialized in [Y].

When invoked:
1. [Primeiro passo]
2. [Segundo passo]
3. [Terceiro passo]

Report [tipo de resultado]:
- [Formato específico]
- [Informação a incluir]
- [Critérios de sucesso]
```

Mensagem final sugerida após criar o arquivo:

```
✅ Subagent created successfully!

📁 Location: .cursor/agents/[name].md
🎯 Purpose: [breve descrição]
🔧 How to invoke:
   - Automatic: delegação quando o contexto for detectado
   - Explicit: /[name] [instrução]
   - Natural: "Use the [name] subagent to [tarefa]"
```
