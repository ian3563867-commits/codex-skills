# Codex Skills

Shared Codex skills maintained by Ian.

## Available Skills

- `create-meeting-minutes-docx`: Create a Chinese meeting minutes DOCX from pasted notes using the bundled Word template.
- `drawio`: Read, explain, validate, safely edit, compare, and export editable draw.io workflows, including multi-page WMS/ASRS/WCS diagrams with swimlanes and linked sub-flows.
- `publish-codex-skill-to-github`: Safely publish or update Codex and Claude skills through a shared GitHub repository.
- `write-to-secondbrain-vault`: Capture repo notes, decisions, and follow-ups into an Obsidian vault Inbox without committing the vault.

## Install

Install a skill from this repository with the Codex skill installer:

```powershell
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/create-meeting-minutes-docx
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/drawio
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/publish-codex-skill-to-github
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/write-to-secondbrain-vault
```

Or install by URL:

```powershell
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/create-meeting-minutes-docx
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/drawio
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/publish-codex-skill-to-github
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/write-to-secondbrain-vault
```

Restart Codex after installing a skill.

## Layout

Each skill lives under `skills/<skill-name>/`.

```text
skills/
  create-meeting-minutes-docx/
    SKILL.md
    agents/
    assets/
    scripts/
  drawio/
    README.md
    SKILL.md
    agents/
  publish-codex-skill-to-github/
    SKILL.md
    agents/
  write-to-secondbrain-vault/
    SKILL.md
    agents/
```

To publish another skill, add another folder under `skills/`, validate it, commit, and push.
