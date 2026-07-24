# Draw.io Workflow Skill

讓 Codex 直接讀取、理解、檢查、修改與匯出可編輯的 `.drawio` 流程圖。

這個 skill 把 draw.io 檔案視為結構化 XML，而不是單純圖片。它會解析頁面、節點、連線、泳道、判斷分支、註解與子流程，特別適合 WMS、ASRS、WCS、ERP 等跨系統工作流程。

## 適合用在什麼情境

- 解讀多頁 `.drawio`，整理主流程與各個子流程。
- 追蹤節點、箭頭、分支條件及系統間資料交接。
- 修改既有流程圖，例如新增步驟、插入判斷點或重接流程線。
- 比較新舊版本，說明實際流程差異。
- 找出斷線、孤立節點、錯接或使用固定座標造成的脆弱連線。
- 將指定頁面匯出成裁切版或原始版面 PDF。

## 能力重點

### 1. 讀懂 draw.io 結構

- 支援一個檔案內含多個 `<diagram>` 頁面。
- 同時解析一般 `mxCell` 與帶連結的 `UserObject`。
- 利用 `source`、`target`、edge label、座標與 swimlane parent 還原流程順序。
- 保留中文、HTML 換行與有意義的節點文字。

### 2. 理解工作流程語意

- `%WSF...%`：連到另一頁的子流程。
- `{...}`：WEB、PDA 等操作畫面或功能頁。
- 菱形：判斷節點，可整理「是／否」等分支。
- `(ERP)`、`(WMS)`、`(MES)`、`(WCS)`：負責處理該步驟的系統。
- 右側編號或「註」：附加到對應流程步驟，不視為獨立節點。

### 3. 安全修改

- 優先做小範圍 XML 修改，不動無關頁面。
- 插入新步驟時，將原本的 `A → B` 改為 `A → 新步驟 → B`，避免留下舊線。
- 保留既有樣式、超連結、edge label 與文件控制資訊。
- 修改後重新解析 XML，並檢查節點座標、連線端點與視覺路由。

### 4. PDF 匯出

若電腦已安裝 draw.io Desktop／diagrams.net CLI，可將指定頁面匯出成 PDF：

```powershell
& 'C:\Program Files\draw.io\draw.io.exe' --export --format pdf --page-index <index> --crop --output '<output.pdf>' '<input.drawio>'
```

預設建議使用 `--crop`，讓一個工作流程以單頁適切尺寸輸出。若需要原始列印版面，可移除 `--crop`。

## 使用範例

安裝後可對 Codex 說：

```text
使用 $drawio 解讀這個檔案的 WF304 頁面，並依序展開所有 %WSF...% 子流程。
```

```text
使用 $drawio 比較這兩版流程圖，列出節點、判斷條件及系統交接的差異。
```

```text
使用 $drawio 在 A 與 B 之間加入重量檢查步驟，保留原本樣式並驗證連線。
```

```text
使用 $drawio 將指定頁面匯出成裁切版 PDF，並確認輸出檔有效。
```

## 安裝

使用 Codex 內建的 skill installer：

```powershell
python scripts/install-skill-from-github.py --repo ian3563867-commits/codex-skills --path skills/drawio
```

或使用 GitHub URL：

```powershell
python scripts/install-skill-from-github.py --url https://github.com/ian3563867-commits/codex-skills/tree/main/skills/drawio
```

安裝完成後請重新啟動 Codex。

## 檔案內容

```text
drawio/
  README.md          對外使用說明
  SKILL.md           Codex 執行規則與完整工作流程
  agents/
    openai.yaml      顯示名稱、簡介與預設提示
```

## 使用限制與注意事項

- 最佳輸入是原始 `.drawio` 檔；JPG／PNG 無法保留完整節點與連線結構。
- XML 能成功解析，不代表版面一定正確；結構修改後仍需檢查視覺結果。
- 缺少 `source` 或 `target`、只靠固定座標連接的線，移動節點後可能錯位。
- 編輯前應先關閉 draw.io 中正在開啟的同一檔案，避免舊的記憶體版本覆蓋外部修改。
- PDF 匯出功能需要另外安裝 draw.io Desktop；讀取與修改 XML 本身不需要 CLI。

## English summary

This Codex skill reads, explains, validates, safely edits, compares, and exports editable `.drawio` workflow files. It supports multi-page diagrams, swimlanes, decisions, linked sub-flows, UI markers, notes, and cross-system handoffs. It is particularly useful for WMS, ASRS, WCS, ERP, and other operational workflows.

See [`SKILL.md`](./SKILL.md) for the complete agent instructions and validation rules.
