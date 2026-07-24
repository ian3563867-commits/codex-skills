---
name: drawio
description: Read, explain, validate, safely edit, and export draw.io/.drawio workflow files. Use when a user provides a .drawio diagram or asks to inspect pages, trace nodes and connectors, expand linked sub-flows, modify an existing workflow, compare versions, find broken or fragile links, or export a selected page to PDF. Especially useful for WMS, ASRS, WCS, ERP, and other system workflows with swimlanes, decisions, UI markers, notes, and cross-system handoffs.
---

# Draw.io Workflow Skill

Use this skill when the user asks to inspect, explain, summarize, validate, edit, compare, or export a `.drawio` workflow file. Treat `.drawio` files as structured XML rather than a flat image, and preserve UTF-8 when reading or writing.

## What This Skill Does

- Lists and selects diagram pages from a multi-page `.drawio` file.
- Reconstructs workflow order from nodes, connectors, swimlanes, coordinates, and edge labels.
- Explains decisions, branches, notes, UI screens, system ownership, and linked sub-flows.
- Makes targeted XML edits while preserving unrelated pages, styles, links, and metadata.
- Checks for broken, fragile, missing, or visually misleading connections.
- Exports a selected page to a cropped or original-layout PDF with the draw.io Desktop CLI.

This skill is designed for editable workflow assets. It does not treat a JPG or PNG as equivalent to the original `.drawio` source, and it does not guarantee a visually correct result from XML parsing alone. Structural edits must also be checked for coordinates, routing, labels, and rendered layout.

## Typical Requests

- "Summarize page `WF304` and expand every `%WSF...%` sub-flow."
- "Insert a validation step between these two workflow nodes."
- "Compare the old and new `.drawio` versions and list process changes."
- "Check whether any connectors are broken or point to the wrong node."
- "Export only the requested workflow page as a cropped PDF."

## Core Parsing Workflow

1. Load the `.drawio` as XML. A file may contain many `<diagram>` pages.
2. Match the requested page by `<diagram name="...">`. If several pages match, ask or choose the explicitly requested variant, such as `(改)`.
3. Extract both normal `mxCell` nodes and `UserObject` nodes. `UserObject` labels often contain important linked sub-flow text.
4. Decode HTML entities and remove presentation tags while preserving meaningful line breaks.
5. Use swimlane parent ids and node coordinates to reconstruct visual order. Read top-to-bottom within a flow unless the arrows indicate otherwise.
6. Read edges from `mxCell edge="1"` using `source`, `target`, and `value`. The edge `value` is the meaning of the connection.
7. When edges lack a source or target, inspect geometry points and nearby nodes before treating the link as broken.
8. For `UserObject` nodes, the meaningful id/label/link may live on the `UserObject`, while geometry and style live on the child `mxCell`. Treat them as one node.

## PDF Export Workflow

When exporting a requested `.drawio` page to PDF:

1. Prefer the native diagrams.net/draw.io CLI when available. On Windows, check `Get-Command drawio`, `Get-Command diagrams.net`, then common install paths such as `C:\Program Files\draw.io\draw.io.exe`.
2. Determine the requested diagram's zero-based page index from the `<diagram>` order. Match by `name`; for workflow title variants, also inspect header nodes such as `Doc Name` when the visible document title differs from the diagram page name.
3. Export only a cropped PDF by default. Cropped output is usually best for workflow attachments and visual review because it keeps the requested diagram on one fitted page:

```powershell
& 'C:\Program Files\draw.io\draw.io.exe' --export --format pdf --page-index <index> --crop --output '<output.pdf>' '<input.drawio>'
```

4. Export a non-cropped PDF only when the user explicitly asks for the printable multi-page/original-page-layout version:

```powershell
& 'C:\Program Files\draw.io\draw.io.exe' --export --format pdf --page-index <index> --output '<output_uncropped.pdf>' '<input.drawio>'
```

5. Verify the output exists, starts with `%PDF`, and has the expected page count. Cropped output is often one page, while uncropped output may span multiple printable pages for tall workflow diagrams.
6. If the CLI exits non-zero but writes a PDF, still validate the produced PDF before reporting success or failure.

## WMS Workflow Semantics

- `%...%` means a work sub-flow reference. Follow it to the matching page name, e.g. `%WSF230_堆棧作業%` means read `WSF230_堆棧作業`.
- `{...}` means a UI screen or function page.
- `WEB`, `PDA`, or `WEB、PDA` above a `{...}` screen means the screen is available on those platforms.
- Rhombus nodes are decisions. They usually split into two or more branches.
- `是` / `否` labels may be actual edge labels or separate text nodes near the branch. If they are separate text, infer the branch by coordinate proximity and line direction.
- Ellipse nodes with `開始` or `結束` are flow start/end points.
- Document-shaped nodes, such as a node with a wavy bottom, represent documents or forms. If the text includes `(ERP)` or another system label, treat it as that system's document.
- Text beside a line represents the meaning of that connection. If it appears as an edge `value`, attach it directly to that edge.
- `(MES)`, `(ERP)`, `(WMS)`, `(WCS)`, `ASRS`, and similar labels inside a node identify the responsible system, not just decorative text.
- Right-side note lane entries such as `(4)` correspond to nodes or decisions that show the same `(4)`.
- A red `註` marker in a node corresponds to a nearby right-side `註.` note, usually matched by similar Y position and context.
- Notes explain the referenced node or branch; do not treat right-side notes as independent process steps.

## Output Style

When summarizing a workflow:

- Start with the main flow, then expand referenced `%...%` sub-flows in the order they appear.
- For each UI screen, state the platform and screen name, e.g. `WEB、PDA {堆棧確認}`.
- For each decision, list the branches with their labels.
- Attach numbered notes and `註` notes to the relevant step.
- Include system-to-system handoffs using edge labels, e.g. `MES → ERP：傳送庫存異動資料`.
- Call out uncertain or visually inferred branches clearly.

## Workflow Change Control

When the diagram already uses document-control metadata, preserve its conventions unless the user gives a different rule:

- For each changed diagram page, update its header `Date` to today's date and increment `Version` by `0.1` when that is the repository's established convention.
- Set `Author` only from the user's instruction, repository rules, or existing document convention. Never invent or hardcode an author identity.
- Treat `Version +0.1` as once per affected page per delivered change batch, not once per individual XML edit, retry, validation pass, or small correction within the same user request. If a later user request introduces a new business/process change, increment the affected page again.
- If `COVER` is updated because of the change, update its header `Date`, increment its `Version` by `0.1` once for the same delivered change batch, and add a `Revise History` row describing the modified WF/WSF pages and the business/process changes.
- Do not create extra start/end nodes when adding branches. A changed WF/WSF should have one logical start node and one logical end node; route new branches back to the existing end when possible.
- If an existing page already has multiple separate process blocks, preserve the existing structure unless the user asks to normalize it, but do not introduce additional duplicated start/end nodes.

## Editing Guidance

Before editing a `.drawio` file:

- Preserve the original file encoding as UTF-8.
- Keep unrelated diagrams unchanged.
- Prefer small, targeted changes to node labels, links, styles, or geometry.
- After editing, reload the XML to verify it parses.
- If changing visual flow, check both `source`/`target` references and any standalone `是` / `否` / note text positions.
- When editing `UserObject` flow nodes, preserve their `link` attributes and existing labels unless the requested change explicitly targets them. Many `%...%` sub-flow jumps depend on these links.

When changing workflow structure:

- Ask the user to save and close the `.drawio` file if it is open in draw.io/diagrams.net. The editor may keep an older in-memory version and overwrite external XML edits when saved.
- Prefer edges with explicit `source` and `target` node ids. Avoid creating flow lines that rely only on `sourcePoint` or `targetPoint`.
- Treat edges with missing `source` or `target` plus fixed `sourcePoint`/`targetPoint` as fragile. If connected nodes move, those fixed-coordinate lines do not move with them and may appear attached to the wrong node.
- When moving a node, inspect all incoming and outgoing edges for that node. Update edge geometry, labels, and nearby standalone branch text as needed.
- Check `exitX`/`exitY` and `entryX`/`entryY` on important edges. These control where the line visually attaches; after rerouting, update them if the line should leave from the bottom, right side, etc.
- For cross-swimlane lines, set the edge parent to a shared container, usually the main process swimlane, not an individual lane.
- When inserting a new intermediate step, rewire the old edge rather than leaving parallel or obsolete paths:
  - old: `A -> B`
  - new: `A -> new step -> B`
- If adding a node shifts the visual flow, move downstream nodes as a group and update nearby branch labels, note markers, and edge routing points.
- Move downstream related nodes across all affected lanes, not only the lane where the new node was added. Keep paired handoffs aligned horizontally when they represent the same step, such as `%WSF230% -> 回報成品堆棧資訊 -> (MES) 更新出貨資訊`.
- If a downstream node has a corresponding right-side note `(n)` or `註`, move or resize that note as needed so the note still visually corresponds to the referenced step.
- For edge labels such as `傳送庫存異動資料`, preserve the edge `value` and any label offset. If moving the connected nodes changes spacing, verify the label still sits beside the intended line.
- After editing, verify key edges by listing `id`, `parent`, `source`, and `target`. For important handoffs, confirm the visual source matches the semantic source.
- Also verify key node coordinates after edits. A successful XML parse is necessary but not enough; the diagram can still be visually wrong if old fixed points or unmoved downstream nodes remain.
