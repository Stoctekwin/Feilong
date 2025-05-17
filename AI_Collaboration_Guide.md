# AI 協作開發指南

本文件彙整了 Feilong 專案在與 AI（如 aider、windsurf、Codeium 等）協作開發時的最佳實踐與注意事項，適用於人類開發者與 AI 助手。請務必遵循以下建議，以確保程式碼品質、專案可維護性，以及團隊與 AI 之間的高效協作。

---

## 0. 專案架構與協作原則
- 本專案已全面模組化，所有共用邏輯集中於 `api/`（如 db_lib.py、process_df.py）。
- 資料查詢、資料處理、分析 function 請統一寫在 api/ 下，方便 app/、experiment.py、Jupyter notebook 等共用。
- app/ 僅放簡單腳本或 CLI 工具，主流程/實驗腳本建議放在根目錄（如 experiment.py），以便直接 `python experiment.py` 執行。
- app/ 下腳本如需獨立執行，請用 `python -m app.腳本名` 方式，確保 package import 正確。
- 請參考 instruction.md 取得正確的執行方式與 import 範例。

## 1. 版本控制、Git 與自動化測試
- **每次重大結構、API、協作規範調整，請同步更新：**
  - `CHANGELOG.md`（記錄所有重要更動與設計決策）
  - `README.md`（同步專案結構、API 用法、協作規範）
  - `AI_Collaboration_Guide.md`（協作精神、OOP、API 抽象、Git 流程等）
  - `.gitignore` 請隨專案需求持續補充，確保敏感/暫存資料不被提交。
- **每次完成改動後，務必執行自動化測試**（如 pytest），確保功能正確且無副作用。
- 測試通過後再進行 git commit，並撰寫具體、明確且有意義的 commit message。
- 建議 commit 前先進行格式化（black/isort）與靜態檢查（flake8）。
- 推薦 commit 流程：
  ```bash
  pytest && black . && isort . && flake8 . && git add .
  git commit -m "feat: XXX/opt: XXX/docs: XXX (簡明說明本次調整內容)"
  git push
  ```
- 任何自動化腳本、CI/CD、協作規範調整，也請記錄於上述文件。
- 保持 .gitignore、requirements.txt、README.md 等文件最新。

## 2. docstring 實踐
- 每個 module、class、function 都應有完整 docstring。
- 說明用途、參數、回傳值、例外狀況與使用範例。
- 建議格式：
  ```python
  def foo(bar: int) -> str:
      """
      說明 foo 的功能。
      
      參數：
          bar (int): 說明 bar 參數
      回傳：
          str: 說明回傳內容
      範例：
          foo(123) -> "abc"
      """
  ```
- 支援中英文，重點在清楚、具體。
- 禁止在程式碼輸出（print/log/exception）中使用 emoji 字元，避免跨平台亂碼與編碼錯誤。

## 3. 善用 Type Hints
- 所有公開函數、class 屬性、重要變數都應加上型別註解。
- 讓 AI 與 IDE 能精確推論資料流，提升自動補全與 refactor 品質。
- 範例：
  ```python
  def get_data(path: str) -> list[dict[str, str]]:
      ...
  df: pd.DataFrame = ...
  ```

## 4. 專案結構、文件與 API 設計
- 維持清晰目錄結構（如 app/、tests/、requirements.txt、README.md 等）。
- README.md 應說明專案目標、結構、安裝、測試與開發規範。
- 若有環境變數，請提供 .env_sample 範本。
- **API 設計應盡量抽象、善用參數與變數，隱藏實作細節。**
  - 上層呼叫者只需關心「要做什麼」，不必知道「怎麼做」。
  - 內部邏輯調整、資料庫 schema 變動等，應盡量不影響外部呼叫方式。
  - 推薦 pattern：以 class 或 function 封裝資料操作、商業邏輯，僅暴露必要參數與回傳。
  - 所有技術指標（如 MA、MACD）皆集中於 `api/indicator.py` 統一管理，後續新指標請一律新增於此。
  - 這樣可大幅提升維護性、可測試性與協作彈性。
  - 範例：
    ```python
    # API 層
    def get_price_df(limit=None, min_days=None):
        ... # 實作細節隱藏於內部
    # 上層只需：
    df = get_price_df(min_days=200)
    ```

## 5. AI Prompt 與上下文
- 與 AI 協作時，盡量明確描述需求、預期行為與限制條件。
- 若需 AI 理解專案全貌，請主動要求先閱讀 README、requirements.txt、app/ 目錄等。
- 指定格式規範（如 black/isort/flake8）時，請在 prompt 或文件明確說明。

## 6. 測試與 CI/CD
- 測試腳本統一放在 tests/，命名規範 test_*.py。
- 可考慮自動化流程（如 GitHub Actions）於每次 PR 時自動執行測試與格式檢查。

## 7. 其他協作建議
- commit 原子化，訊息明確。
- 多人/AI 協作時，建議分工不同檔案或功能模組，減少衝突。
- 定期同步專案狀態給 AI（如 session 開始時讓 AI 重新讀取專案說明與依賴）。


---

如需進一步協作規範、AI prompt 範本或自動化腳本範例，歡迎補充或聯繫維護者。
