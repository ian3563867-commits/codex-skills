---
name: linebot-vault-regression
description: Run the fixed 9002 Vault LINE Bot retrieval regression suite after changing LINE Bot search logic, deterministic pre-check behavior, prompt routing, `retrieval.py`, `prompt_rules.py`, `main.answer_query()`, or `04_Knowledge/index.md` high-value entries. Use when Codex needs to verify that vault queries such as 建準關單MSG, Teams 自動化, 家庭資產, ADPS 通知系統 SQL, and related regression cases still route correctly without calling LINE or Claude APIs.
---

# LINE Bot Vault Regression

## Quick Start

Run the bundled script against the local `vault-line-bot` repo:

```powershell
python C:\Users\ian35\.codex\skills\linebot-vault-regression\scripts\run_linebot_vault_regression.py --repo C:\Users\ian35\Desktop\Claude\vault-line-bot
```

Use `--json` for machine-readable output:

```powershell
python C:\Users\ian35\.codex\skills\linebot-vault-regression\scripts\run_linebot_vault_regression.py --repo C:\Users\ian35\Desktop\Claude\vault-line-bot --json
```

## When To Run

Always run this regression after editing any LINE Bot vault-search behavior:

- `retrieval.py`
- `prompt_rules.py`
- `main.answer_query()`
- `04_Knowledge/index.md` high-value operation entries
- LINE Bot search prompts, index hints, candidate routing, or deterministic pre-check logic

## What It Checks

The script is non-destructive. It imports the target repo, mocks `ask_agent`, reads the real vault, and validates route/prompt behavior. It does not start uvicorn/ngrok, call LINE, call Claude, write to the vault, or write to the repo log.

Regression coverage:

- Deterministic pre-check core cases: 建準關單MSG, 圓展 POClose, 關單msg, 建準調撥 UI 不能上架, 松川目前問題, YouTrack 用法.
- 2026-05-18 validation cases: Teams 自動化內容, 家庭資產, 建準關單MSG, 世祥人員名單.
- ADPS notification SQL regression: 通知系統 SQL with ADPS should route to WMS common SQL and include `NS_M_SEND_GROUP` / `NS_M_USER` hints.

## Exit Codes

- `0`: all regression cases passed.
- `1`: one or more regression cases failed.
- `2`: setup/config problem, such as missing repo, missing `main.py`, or import failure.

## Path Resolution

Repo path priority:

1. `--repo`
2. `VAULT_LINE_BOT_REPO`
3. `C:\Users\ian35\Desktop\Claude\vault-line-bot`

Vault path priority:

1. `--vault`
2. `VAULT_DIR` from the target repo `.env`
3. `C:\Users\ian35\Documents\secondbrain`

## Reporting

After running the script, summarize:

- total passed/failed cases
- failed query names and mismatch reason
- command used
- whether this blocks the LINE Bot search-logic change
