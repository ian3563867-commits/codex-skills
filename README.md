# Codex Skills

Shared Codex skills maintained by Ian.

## Available Skills

- `create-meeting-minutes-docx`: Create a Chinese meeting minutes DOCX from pasted notes using the bundled Word template.

## Install

Install a skill from this repository with the Codex skill installer:

```powershell
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/create-meeting-minutes-docx
```

Or install by URL:

```powershell
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/create-meeting-minutes-docx
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
```

To publish another skill, add another folder under `skills/`, validate it, commit, and push.
