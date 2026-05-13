---
name: create-meeting-minutes-docx
description: Create a Chinese meeting minutes DOCX from a bundled eCATCH/KENMEC-style Word template. Use when the user asks to make or produce a 會議紀錄, meeting record, or formal meeting minutes from pasted notes, especially when they need the result as a .docx file using the included template or a user-specified compatible template.
---

# Create Meeting Minutes DOCX

## Required Inputs

If not already provided, ask the user for:

- 會議名稱
- 會議地點
- 會議時間
- 會議主席
- 新文件名稱

Use these defaults:

- 會議記錄: `Ian`
- 出席人員: leave blank for the user to fill
- Template path: use the bundled template at `assets/templates/0151-世祥斗南-MML-PMS、出貨流程確認-20210917.docx`
- Output directory: current working directory unless the user provides a specific path

Normalize obvious date typos before writing, but state the correction to the user. For example, treat `2026/05/061 14:00-15:00` as `2026/05/06 14:00-15:00`.

## Content Style

Convert pasted raw notes into concise formal meeting-record bullets. Preserve important names, systems, dates, owners, decisions, and follow-up expectations.

Example transformation:

```text
SAP對接主檔、單據如何對接需再跟Simon確認ㄒ
測試機要起來-5/7會起來
```

Write as:

```text
1. SAP 對接主檔及相關單據的對接方式，需再與 Simon 確認。
2. 測試機預計於 2026/05/07 建置完成並啟用。
```

Use full dates when the meeting year is known. Keep the content factual; do not invent owners or dates not present in the notes.

## DOCX Creation Workflow

1. Use the `documents` skill because the output is a `.docx`.
2. Use `scripts/create_minutes.py` with the bundled workspace Python runtime when possible.
3. Use the bundled template by default. If the user provides `--template` or a template path, use that compatible template instead.
4. Only fill the table fields and meeting-content cell. Do not delete or modify header/footer drawings, watermark objects, logos, appendix row text, or unrelated template structure.
5. Leave 出席人員 blank unless the user provides attendees.
6. Before final layout work, compare the original source notes against the newly generated DOCX for logical equivalence. Check conditions, constraints, dates, roles/owners, system names, responsibility, decisions, requirements, open items, and whether wording changed a fact from current state to requirement or vice versa. If any difference is found, correct the generated DOCX using the original source as authoritative, then repeat the comparison until the meaning, facts, conditions, and responsibility are aligned. Formal wording and concise phrasing are allowed only when they do not change the logic.
7. Render the DOCX with the documents skill renderer and visually inspect the PNG.
8. If the render shows overlap caused by content length, adjust only editable table rows or content formatting. Do not remove header/footer image objects to fix overlap.
9. Return only the final `.docx` link unless the user asks for QA artifacts.

## Script Usage

Run from any workspace:

```powershell
& '<bundled-python>' '<skill-dir>\scripts\create_minutes.py' `
  --output-name '0151-世祥銘基廠會議紀錄-20260506.docx' `
  --meeting-name '世祥銘基廠會議' `
  --place '線上會議' `
  --time '2026/05/06 14:00-15:00' `
  --chair 'Mars' `
  --content "1. ...`n2. ..."
```

Optional arguments:

- `--recorder`, default `Ian`
- `--attendees`, default blank
- `--template`, defaults to the bundled template
- `--output-dir`, defaults to current working directory

The script preserves template header/footer objects and the `附錄` row, then prints the output path plus object/text checks.
