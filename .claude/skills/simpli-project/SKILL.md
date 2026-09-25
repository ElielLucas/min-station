---
name: simpli-project
description: Expert guide for reading and executing tasks from Simpli Projects via the simpli-projects MCP. Fetches complete task context — title, description, acceptance criteria, EAP hierarchy, assignees, dates, and hours — without any truncation, and intelligently detects whether the user wants to view task information only or proceed with implementation. Use when user shares a simpli-projects.norven.com.br URL, says "leia essa tarefa", "execute essa tarefa", "abra essa tarefa", "o que preciso fazer", "leia o contexto", "read this task", "execute this task", "open this task", "get task context", "show task details", "work on this task", "start this task", "implement this task", or pastes an NRV-XXXXX code with a project URL. Always use this skill for any simpli-projects.norven.com.br URL or NRV-XXXXX code, even when the request only asks for one or two fields (e.g., "extraia titulo e descrição", "pegue o contexto") and looks answerable with a single direct MCP call — do not call `get_task_by_url`/`get_project_summary` directly without first loading this skill, since it guarantees untruncated display of all fields and correct view/execute intent detection. Requires the simpli-projects MCP to be connected and active. Do NOT use when simpli-projects MCP is not available, for creating or updating tasks in Simpli Projects, or for general project management questions unrelated to a specific task or project URL.
license: CC-BY-4.0
metadata:
  author: Murilo Moreira - https://github.com/murilo2001
  version: '1.0.1'
  information-for-repository-maintainers:
    copy-date: null
    copy-url: null
    this-skill-can-be-resynchronized: false
    observations: 'Essa skill foi criada em 2026-06-08 e não foi derivada ou copiada de nenhum repositório existente. README.md traduzido do inglês para português durante normalização do catálogo (originalmente idêntico ao repositório de origem).'
---

# Simpli Project

You are an expert at extracting complete task and project context from Simpli Projects via the simpli-projects MCP. You never truncate, summarize, or omit any field returned by the MCP, and you intelligently detect whether the user wants to view task information only or proceed with implementation.

## Available MCP Tools

| Tool | Input | Returns |
|------|-------|---------|
| `get_task_by_url` | `{ url: string }` — full URL like `https://www.simpli-projects.norven.com.br/projects/{uuid}?eap_item=NRV-{number}` | `TaskContext`: task (id, code, title, description, acceptance_criteria, status, level, start_date, due_date, end_date, estimated_hours, actual_hours, progress, owner, executors, created_at, updated_at), hierarchy (array of N1–N4 nodes with id, code, level, title, status), project (id, code, name, status, client_name, start_date, end_date_planned, manager), url |
| `get_project_summary` | `{ url_or_id: string }` — project UUID or project URL | `ProjectSummary`: id, code, name, description, status, client_name, bu_name, start_date, end_date_planned, progress, manager, task_counts (total, concluido, em_execucao, bloqueado, nao_iniciado), pending_tasks (array of id, code, title, status, due_date) |

## Step 1: Identify the Request Type

Route to the correct tool based on what the user provided:

- **URL contains `?eap_item=NRV-`** → call `get_task_by_url` with the full URL
- **URL is a project URL without `eap_item`, or a standalone UUID** → call `get_project_summary` with the URL or UUID
- **No URL provided** → ask the user: "Please share the Simpli Projects URL or task code (NRV-XXXXX) so I can fetch the context."

Do not proceed until you have a URL or UUID to work with.

## Step 2: Fetch and Display Complete Context

After calling the appropriate tool, display **all fields** in a structured block. Never truncate, never summarize, never omit fields.

Format the output as:

```
### Task Info
- Code: {task.code}
- Title: {task.title}
- Status: {task.status}
- Level: {task.level}
- Progress: {task.progress}%
- Estimated Hours: {task.estimated_hours}
- Actual Hours: {task.actual_hours}

### Description
{task.description || "Not provided"}

### Acceptance Criteria
{task.acceptance_criteria || "Not provided"}

### Project & Hierarchy
- Project: {project.code} — {project.name} ({project.status})
- Client: {project.client_name}
- Manager: {project.manager.display_name}
- EAP Path: {hierarchy[0].code} > {hierarchy[1].code} > ... > {task.code}

### Assignees
- Owner: {task.owner.display_name} ({task.owner.email})
- Executors: {task.executors.map(e => e.display_name).join(', ') || "None"}

### Dates & Progress
- Start: {task.start_date || "Not set"}
- Due: {task.due_date || "Not set"}
- End: {task.end_date || "Not set"}
- Created: {task.created_at}
- Updated: {task.updated_at}
```

Render the `hierarchy` array as a breadcrumb (N1 > N2 > N3 > N4) using the `code` field of each node.

If `description` or `acceptance_criteria` is `null`, display "Not provided" — never skip the field.

## Step 3: Detect User Intent

After displaying the complete context, determine the user's intent:

- **View-only** (default when no action keyword is present): user said "leia", "mostre", "abra", "read", "show", "open", "get context", "leia o contexto" → display complete context and wait for the next instruction. Do not take any implementation action.

- **Execute**: user said "execute", "implemente", "faça", "trabalhe nisso", "start", "implement", "work on this", "do this", "execute essa tarefa", "implemente essa tarefa" → display complete context and then proceed with implementation in Step 4.

- **Ambiguous**: if intent is unclear, ask: "Would you like me to (1) just display the task context, or (2) read and start implementing it?"

## Step 4: Execution Mode

When the user wants execution, before writing a single line of code:

1. Read `title`, `description` and `acceptance_criteria` in full — not a summary, every word. These are the 3 most important fields: they carry the full context of the activity, defining what must be done and what success looks like.
2. Understand the `hierarchy` to grasp the project context and where this task fits
3. Check `status` and `due_date` for priority signals
4. Use available skills (`codenavi`, `tlc-spec-driven`, etc.) as appropriate for the implementation
5. Never begin implementation without having fully read and understood 100% of the acceptance criteria

## Examples

**Example 1 — View only:**

User: "leia essa tarefa: https://www.simpli-projects.norven.com.br/projects/abc-123?eap_item=NRV-42"

→ Call `get_task_by_url` with the URL → Display the complete structured context → Wait for next instruction. Do not start implementing.

**Example 2 — Execute:**

User: "execute essa tarefa: https://www.simpli-projects.norven.com.br/projects/abc-123?eap_item=NRV-42"

→ Call `get_task_by_url` with the URL → Display the complete structured context → Read description and acceptance_criteria in full → Proceed with implementation using available skills.
