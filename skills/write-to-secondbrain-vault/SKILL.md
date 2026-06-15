---
name: write-to-secondbrain-vault
description: Safely write notes, work logs, decisions, issue updates, and reference snippets from any repo into an Obsidian secondbrain vault. Use when Codex is asked to write back to a vault, secondbrain, mind palace, Obsidian, notes, or to save project context, meeting notes, implementation decisions, bug findings, or follow-up items.
---

# Write To Secondbrain Vault

## Overview

Capture information from any working repo into an Obsidian secondbrain vault without disturbing the vault's later整理或同步流程. The default behavior is to create a new Markdown note in the vault Inbox and leave any vault commit, sync, or digestion workflow to the user's existing process.

## Locate The Vault

Determine the vault path in this order:

1. Use the current workspace if it contains an Obsidian-style vault structure such as `00_Inbox/`, `02_Projects/`, `03_Daily/`, or `04_Knowledge/`.
2. Use `SECOND_BRAIN_VAULT` if that environment variable is set.
3. Use a vault path explicitly given by the user.
4. If no vault can be identified, ask the user for the vault path before writing.

Default write destination:

```text
<vault>\00_Inbox\
```

If `00_Inbox/` does not exist, create it only after confirming the selected vault path is correct.

## Core Rules

- Reply and note content in Traditional Chinese unless preserving exact source text is necessary.
- Create a new Markdown note in `00_Inbox/` by default.
- Use the vault standard frontmatter only: `title`, `date`, `tags`, `project`.
- Put source context in the body under `來源`; do not add repo-specific metadata fields to frontmatter by default.
- Do not modify existing notes under `02_Projects/`, `03_Daily/`, or `04_Knowledge/` unless the user explicitly asks for that exact edit.
- Do not write directly into `04_Knowledge/`; treat it as a digested knowledge area owned by the user's vault process.
- Do not run `git commit`, `git push`, or tag changes in the vault unless the user explicitly asks for vault git operations.
- Preserve the user's meaning. Lightly structure the note, but do not over-rewrite.
- If the task requires a project-specific destination and the user explicitly asks to write directly to `02_Projects/`, first list `02_Projects/` and match an existing folder. If no clear folder exists, ask the user for the folder name before creating anything.
- If unsure where something belongs, prefer `00_Inbox/` over direct routing.

## Workflow

1. Identify the source context from the current repo:
   - repo name or root path
   - branch, issue, PR, commit, or file path if relevant
   - the user's raw request and the distilled content to save

2. Create a concise note title and filename:
   - filename format: `YYYYMMDD-主題.md`
   - use the user's local date when available
   - keep the subject short, specific, and searchable

3. Write the note to:

```text
<vault>\00_Inbox\YYYYMMDD-主題.md
```

4. Include only the vault standard frontmatter:

```yaml
---
title: 主題
date: YYYY-MM-DD
tags: []
project: 通用
---
```

Use a known project name when clear, otherwise use `通用`.

5. Body structure:

```markdown
# 主題

## 摘要
- 

## 內容
- 

## 待辦 / 後續
- 

## 來源
- repo:
- path:
```

Omit empty sections if they add no value, except keep `來源` when the note came from another repo.

## Searching The Vault

If context from the vault is needed before writing:

- Prefer the vault's local instructions such as `AGENTS.md` if present.
- On Windows, `rg` may be blocked by local policy. If it fails with access errors, switch to PowerShell native search instead of repeatedly retrying.
- Read and write text files as UTF-8.

PowerShell examples:

```powershell
Get-Content -LiteralPath '<vault>\04_Knowledge\index.md' -Encoding UTF8
Select-String -LiteralPath '<vault>\path\file.md' -Pattern 'keyword' -Encoding UTF8
Get-ChildItem -LiteralPath '<vault>\02_Projects' -Recurse -File -Include *.md | Select-String -Pattern 'keyword' -Encoding UTF8
```

When reporting search results to the user, include file path and line number.

## Completion Response

After writing the note, reply briefly in Traditional Chinese with:

- the created note path
- a one-line summary of what was saved
- a reminder that vault commit/sync is left to the user's existing process, if relevant
