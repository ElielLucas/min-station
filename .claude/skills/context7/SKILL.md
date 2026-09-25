---
name: context7
description: On-demand lookup of current, version-correct docs for a library, framework, SDK, or API via the Context7 MCP (resolve-library-id then get-library-docs) — triggers ONLY on an explicit request, never inferred from an implementation task. Use when the user says "usa/consulta/invoca o context7", "/context7", "verifica a documentação atual/oficial de X", "confirma a API/assinatura de X na versão Y", "isso mudou entre versões, confere", "check the latest docs for X", "verify the current API for X", or "what's the correct signature for X in vY". Do NOT trigger just because a request mentions implementing or integrating a library/SDK — wait for an explicit ask to check/verify docs, since each lookup costs an MCP call and tokens. Do NOT use for Figma design-to-code (figma-implement-design), Vuetify lookups (use the dedicated vuetify MCP), or Simpli Projects tasks (simpli-project).
license: CC-BY-4.0
metadata:
  author: Murilo Moreira - https://github.com/murilo2001
  version: '1.0.0'
  information-for-repository-maintainers:
    copy-date: null
    copy-url: null
    this-skill-can-be-resynchronized: false
    observations: 'Skill criada internamente em 05/08/20265 para consulta sob demanda ao MCP context7 (Upstash) — dispara apenas quando o usuário pede/invoca explicitamente, para evitar consumo desnecessário de tokens/chamadas MCP. Não derivada de repositório externo.'
---

# Context7 — On-Demand Library Docs Lookup

## Overview

LLMs generate plausible-looking but outdated or hallucinated API calls when they rely
only on training memory for third-party libraries. This skill fetches current,
version-correct docs via the Context7 MCP to fix that — but **only when the user
explicitly asks for it**. It does not run automatically on every implementation
request that happens to mention a library, because each lookup costs an MCP call and
tokens; the developer decides when the extra cost is worth it.

## Decision Rule — When to Trigger

Trigger only when the request contains an **explicit ask** to check, verify, or fetch
documentation — not merely a request to implement/use/integrate a library. Explicit
asks look like:

1. **Naming the skill/MCP directly**: "usa o context7", "consulta o context7",
   "invoca o context7", "/context7", "use context7", "check this with context7".
2. **Explicitly requesting current/official docs or version-specific verification**:
   "verifica a documentação atual de X", "confirma a API/assinatura correta de X na
   versão Y", "isso mudou entre versões, confere", "check the latest docs for X",
   "verify the current API for X", "what's the correct signature for X in vY".

If the request only says "implement X using library Y" or "integre a API do Y" with no
explicit check/verify/docs ask, do **not** trigger — proceed with normal implementation
and let the developer ask for verification if they want it.

## Do NOT Trigger

- Any implementation/integration request that doesn't explicitly ask to check, verify,
  or fetch documentation — including for a library new to the project. Silently
  assuming a doc check is needed defeats the point of making this on-demand.
- Pure business logic with no third-party library/API involved.
- Trivial language built-ins (e.g. `Array.map`, `str.split`).
- **Vuetify**: if the dedicated `vuetify` MCP already answers the question (component
  props, API, guides), prefer it — it's version-pinned and more precise for that one
  library. Only fall back to Context7 if the `vuetify` MCP is absent or insufficient,
  or the user explicitly asks for context7 anyway.
- **Figma-to-code**: use `figma-implement-design` instead.
- **Simpli Projects task retrieval**: use `simpli-project` instead. Note: these compose
  — a prompt like "leia a tarefa NRV-123 e depois confere no context7 a API do Stripe"
  should trigger `simpli-project` first for task context, then this skill's explicit
  ask for the Stripe part. They don't compete.

## Step-by-Step Tool-Call Sequence

1. Detect the library/framework/SDK/API name (and version, if stated or inferable from
   the project's dependency manifest).
2. Call `resolve-library-id` with that name. If multiple matches, disambiguate against
   the project's actual package/ecosystem.
3. Call `get-library-docs` with the resolved library ID, passing topic/version if the
   request is version-specific.
4. Treat the fetched docs as source of truth over training memory — write
   implementation code only after this.
5. Cache the resolved ID/docs for the rest of the session; don't re-resolve on every
   follow-up message about the same library.

## If the MCP Is Unavailable — Hard Stop

If `resolve-library-id` or `get-library-docs` fail, or the `context7` MCP isn't
connected: **stop before writing implementation code**. Tell the developer which MCP is
missing and how to install it (`context7` MCP from this repo's catalog). Only proceed
from training knowledge if the developer explicitly authorizes it, and flag that the
resulting code may use outdated API assumptions. Never silently degrade.

## Examples

**Should trigger (explicit ask to check/verify/fetch docs):**
- "Antes de continuar, verifica a documentação atual do Prisma 5."
- "Usa o context7 pra confirmar a assinatura desse método do axios."
- "Check the latest docs for the Stripe SDK before we continue."
- "Isso mudou entre versões do zod? Confere a API oficial."

**Should NOT trigger (implementation/integration ask, no explicit doc-check):**
- "Implement rate limiting using the Upstash Redis SDK." (implement, not verify)
- "Migre esse serviço de Prisma 4 para Prisma 5." (implement/migrate, not verify)
- "Integre a API de pagamentos do Stripe nesse checkout." (implement, not verify)
- "Refactor this function to reduce cyclomatic complexity." (no third-party lib)
- "Implemente esse botão seguindo o Figma." → `figma-implement-design`
- "Qual o prop `variant` do v-btn?" → prefer `vuetify` MCP
- "Leia essa tarefa NRV-1234." → `simpli-project`
