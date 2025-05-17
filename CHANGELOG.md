# Feilong 專案更新日誌



## 2025-05-09
### [優化] 自動偵測資料表日期格式與月營收補齊測試
- get_db_pivot_df 現可自動偵測資料表日期格式（西元/民國），查詢 monthly_revenue、price 等表皆自動處理。
- 新增 utility.py: to_roc, to_ad, check_date_format 等日期轉換與偵測函式。
- experiment.py 增加測試：查詢 monthly_revenue 並將資料點補齊到每月 10 號。
- 修正 pivot_df 若有重複索引自動報錯，並於查詢時自動過濾。

### [新增] API 與腳本
- 新增 `api/backtest.py`：彈性回測主流程，支援停損、停利、動態停利。
- 新增 `api/dashboard.py`：市場寬度指標（創新高/新低家數、均線站上家數、漲跌持平家數等）
- 新增 `tool_dashboard.py`：dashboard demo 腳本，批次統計市場寬度指標。
- 新增 `buffett_say.py`：巴菲特選股條件範例腳本，結合多因子指標。
- `api/indicator.py` 新增多種指標函式：
    - `ema_pivot_df`、`wma_pivot_df`、`n_day_high_pivot_df`、`n_day_low_pivot_df`、`k_pivot_df`、`d_pivot_df`、`macd_pivot_df`、`williams_pivot_df`、`add_ma`、`add_ma_pivots`、`add_macd` 等。

---

## 2025-05-17
### [重構] 全面更名專案為 Feilong
- 將所有文件、說明、clone 指令、資料夾名稱等由 Wolong/Wolong/wolong 統一替換為 Feilong。
- FAQ、README、startup.md、AI_Collaboration_Guide.md 等皆已同步修正。
- 專案正式以 Feilong 名稱繼續維護與開發。

## 2025-05-04
### [重大] 欄位對應規則集中化與反向查詢 API
- 新增 `api/utility.py` 工具函式。
- `api/db_lib.py` 新增多個 function，支援資料表欄位與熟悉名 hash 對應、反查、產生對應表，如 新增 `reverse_column_mapping` API，支援熟悉名稱還原為 table 欄位名稱。
- `table_column_hash_util.py` 支援一鍵產生/更新所有 hash 對應檔案與人工可讀 table。
- 新增 `common/table_common_col_rule.txt` 集中管理 table/column 對應規則。
- 產生 `csv/table_column_mapping.csv` 供人工查閱。
- `json/` 目錄下產生 raw/common/filtered table column hash.json。
- `.gitignore` 已排除 `json/` 目錄。


---
# [重大] 欄位對應規則集中化與反向查詢 API
- 新增 `common/table_common_col_rule.txt`，
- `api/db_lib.py` 
- `table_column_hash_util.py` 支援一鍵產生 hash 與反查功能，提升欄位管理自動化。

---


## 2025-05-03
### [新增] 示範腳本與 API 優化- 新增 tool_view_stock_dealers.py，為券商分點與 K 線分析的完整示範程式，並補充詳細中文註解。
- process_df.py 新增 parse_date_range 支援多種日期區間格式，get_db_df/get_db_pivot_df 支援 date_range_str。
- 新增 get_stock_data 和 get_branch_data API，為策略和工具客製化查詢提供便利。

---


## 2025-05-01
### [重大] 多股均線驗證與資料完整性自動檢查
- 強化 moving average robust 計算，所有 MA 支援 NaN 與資料量自動檢查。
- 新增 golden_alignment_pivot/ma_entangled_pivot 支援 pivot 結構多股驗證。
- experiment.py 支援多股動態驗證與疊圖，繪圖流程自動化。
- 文件結構、協作規範同步優化。

### [init] 全面重構專案架構
- 共用邏輯集中於 api/，資料查詢、資料處理、資料庫操作明確分層。
- app/ 僅放簡單腳本或 CLI 工具，主流程/實驗腳本建議放根目錄（如 experiment.py）。
- instruction.md 詳細說明正確執行方法與 package import。
- .gitignore 覆蓋虛擬環境、.env、csv、__pycache__ 等。
- 優化 process_df.get_price_df 支援 min_days 參數，強化 API 抽象化、物件導向精神，並修正 experiment.py 彈性設計。依 AI_Collaboration_Guide.md 建議同步文件與結構。

---


如需進一步優化（如自訂分批單位、進度列等），請聯絡開發維護者。
