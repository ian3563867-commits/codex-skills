---
name: publish-codex-skill-to-github
description: Publish or update a local Codex or Claude skill in a shared GitHub skills repository safely. Use when the user asks to put a skill on GitHub, update a public skills repo, or hand a skill between AI coding agents through GitHub.
---

# Publish a Skill to GitHub

## Overview

Copy a local skill into an existing shared Git repository, review the public copy, validate it, update the repository README, then commit and push only the intended files. Keep the runtime copy untouched.

## Required inputs

Resolve these values before editing:

- `SKILL_SOURCE`: local runtime skill directory.
- `SHARING_REPO`: existing local clone of the public skills repository.
- `SKILL_NAME`: folder name under `skills/`.
- `GITHUB_REPO`: GitHub `owner/repo` identifier.

Ask the user for any value that cannot be discovered safely. Do not initialize Git inside `SKILL_SOURCE` or create a standalone repository unless explicitly requested.

## Safety rules

- Treat the destination repository as public.
- Edit only the public copy under `$SHARING_REPO\skills\$SKILL_NAME`.
- Remove personal paths, tokens, passwords, secrets, `.env` references, customer information, and private workflow details.
- Prefer environment variables, workspace discovery, relative paths, or user-provided parameters.
- If the sharing repository has unrelated changes, stop and ask before staging.
- Stage only the root `README.md` and `skills/$SKILL_NAME/...`.
- Do not commit unrelated workspaces, vaults, or runtime skill directories.

## Workflow

### 1. Inspect source and destination

```powershell
Get-ChildItem -LiteralPath $SKILL_SOURCE -Recurse -File
git -C $SHARING_REPO status -sb
git -C $SHARING_REPO remote -v
```

Confirm that the remote matches `GITHUB_REPO` and the worktree is clean.

### 2. Create the public copy

```powershell
$destination = Join-Path $SHARING_REPO "skills\$SKILL_NAME"
Copy-Item -LiteralPath $SKILL_SOURCE -Destination $destination -Recurse
```

If `$destination` already exists, update it deliberately rather than creating a nested duplicate. Do not edit `SKILL_SOURCE`.

### 3. Review public safety

```powershell
Get-ChildItem -LiteralPath $destination -Recurse -File |
  Select-String -Pattern 'Users\\|token|password|secret|\.env' -Encoding UTF8 |
  Select-Object Path,LineNumber,Line
```

Review every match in context. Rewrite machine-specific instructions and remove material that should not be public.

### 4. Check cross-agent compatibility

Keep `SKILL.md` as the portable core. Its YAML frontmatter should contain `name` and `description`. Agent-specific metadata directories such as `agents/` may remain optional, but the workflow must not depend on them.

When importing a Claude skill for Codex, inspect tool names, filesystem paths, permission assumptions, hooks, subagent calls, and product-specific commands. Adapt unsupported instructions in the public copy before installation.

### 5. Validate

If Codex's validator is available:

```powershell
$env:PYTHONUTF8='1'
python "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" $destination
```

If the skill contains scripts, run at least one representative test. A metadata check alone is not enough.

### 6. Update README

Add the skill to:

- Available skills.
- Repository-path and URL installation examples.
- The repository layout.

### 7. Review, commit, and push

```powershell
git -C $SHARING_REPO status -sb
git -C $SHARING_REPO diff -- README.md "skills/$SKILL_NAME"
git -C $SHARING_REPO add README.md "skills/$SKILL_NAME"
git -C $SHARING_REPO commit -m "Add $SKILL_NAME skill"
git -C $SHARING_REPO push
```

Use `Update $SKILL_NAME skill` when updating an existing public copy.

### 8. Verify from GitHub

```powershell
gh repo view $GITHUB_REPO --json url,visibility,defaultBranchRef
gh api "repos/$GITHUB_REPO/contents/skills/$SKILL_NAME/SKILL.md" --jq '.html_url'
```

Optionally install into a temporary directory and validate the installed copy.

## Completion response

Report:

- Public GitHub link.
- Commit hash and branch.
- Validation and representative test results.
- Whether the runtime skill directory remained untouched.
- Any unresolved cleanup or compatibility concerns.
