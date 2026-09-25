# Simpli Project Skill

Skill que orienta o agente a interagir com o MCP do Simpli Projects, buscando o contexto completo de tarefa e projeto sem truncamento e detectando inteligentemente se deve visualizar ou executar.

## O que é esta skill?

Quando você compartilha uma URL do Simpli Projects, esta skill garante que o agente:

1. Chame a ferramenta MCP correta (`get_task_by_url` ou `get_project_summary`)
2. Exiba **100% dos dados retornados** — descrição, critérios de aceitação, hierarquia EAP, responsáveis, datas
3. Detecte se você quer **apenas ler** o contexto da tarefa ou **começar a implementá-la**

## Início Rápido

Compartilhe uma URL de tarefa com uma frase de ação:

```
leia essa tarefa: https://www.simpli-projects.norven.com.br/projects/{uuid}?eap_item=NRV-123
execute essa tarefa: https://www.simpli-projects.norven.com.br/projects/{uuid}?eap_item=NRV-123
```

## Frases de Gatilho

| Idioma | Frases |
|----------|---------|
| Portuguese | `leia essa tarefa`, `execute essa tarefa`, `abra essa tarefa`, `o que preciso fazer`, `leia o contexto` |
| English | `read this task`, `execute this task`, `open this task`, `get task context`, `show task details`, `work on this task`, `start this task`, `implement this task` |
| Implícito | Colar uma URL `simpli-projects.norven.com.br` ou um código `NRV-XXXXX` |

## Detecção de Intenção

| Modo | Quando é disparado | O que acontece |
|------|---------------|--------------|
| **Apenas visualização** | "leia", "mostre", "read", "show", "open", "get context" | Busca e exibe todos os dados da tarefa, depois espera |
| **Execução** | "execute", "implemente", "start", "implement", "work on this" | Busca, exibe, depois segue com a implementação |
| **Ambíguo** | Intenção não está clara | Pergunta: "View only or start implementing?" |

## Requisito de MCP

Esta skill requer que o MCP **`simpli-projects`** esteja conectado e ativo no seu agente.

Para instalá-lo:

```bash
npx agent-playbook mcp install simpli-projects
```

Você será solicitado a informar seu token pessoal de MCP, gerado em **Meu Perfil → Token MCP** no Simpli Projects.
