# Feilong

現代化資料分析與同步專案

## 專案結構

```
Feilong/
├── .env_sample                # 環境變數設定範例
├── requirements.txt           # 依賴套件清單
├── .gitignore                 # git 忽略規則
├── README.md                  # 專案說明
├── FAQ.md                     # 常見問題與操作指引
├── AI_Collaboration_Guide.md  # AI 協作開發建議
├── CHANGELOG.md               # 版本紀錄（每次重要調整請同步）
├── startup.md                 # 環境安裝與啟動說明
├── experiment.py              # 主流程/實驗腳本（建議從這裡啟動分析），可用於測試環境是否正常
├── tool_view_stock_dealers.py # 分點工具互動式範例腳本
├── table_column_hash_util.py  # 資料表欄位對應自動化（Hash Mapping Layer）
├── api/
│   ├── db_lib.py              # 資料庫連線、結構查詢等共用函式
│   ├── process_df.py          # 資料查詢、pandas 處理等共用函式，API 介面抽象、隱藏細節
│   ├── indicator.py           # 技術指標（如 MA、EMA、WMA、MACD、KD、Williams%R 等）統一管理
│   ├── dashboard.py           # 市場寬度指標、家數統計等 dashboard 指標
│   ├── backtest.py            # 彈性回測主流程 API
│   ├── utility.py             # 提供訊息與警告字串組裝等小工具
│   ├── plot.py                # 繪圖工具
│   └── filter.py              # 條件式資料篩選工具，彈性設計
├── tool_dashboard.py          # 市場寬度指標、家數統計等 dashboard demo 腳本
├── buffett_say.py             # 巴菲特選股條件範例腳本

├── common/
│   └── table_common_col_rule.txt # 欄位對應規則
├── app/
│   ├── __init__.py            # app package 初始化
│   └── list_tables.py         # 範例腳本：列出所有資料表
├── csv/                       # 匯出/暫存資料資料夾
├── .gitignore                 # Git 忽略規則，建議同步維護
└── .venv/                     # Python 虛擬環境（建議加到 .gitignore）
```

## API 檔案與函式一覽
- `api/` 層所有 function 皆強調抽象、隱藏細節，僅暴露必要參數。
- 例如 `get_db_df(date_range_str=...), get_db_pivot_df(date_range_str=...)`，可依需求自動決定抓取資料量。

### `api/backtest.py`
- `run_backtest(buy_signal, close_pivot, stop_loss=None, take_profit=None, trailing_stop=None, debug=False)`：彈性回測主流程，支援停損、停利、動態停利。

### `api/dashboard.py`
- `count_n_day_high(pivot_df, n)`：計算每天創 n 日新高價的股票家數。
- `count_n_day_low(pivot_df, n)`：計算每天創 n 日新低價的股票家數。
- `get_total_count_per_date(close_pivot_df)`：計算今天與昨天皆有收盤價的股票總家數。
- `get_close_below_count(close_pivot_df)`：計算下跌家數。
- `get_close_flat_count(close_pivot_df)`：計算持平家數。
- `get_close_above_count(close_pivot_df)`：計算上漲家數。
- `count_above_ma(close_pivot_df, volume_pivot_df, n, ma_type='sma')`：計算每天收盤價站上 n 日均線（SMA/EMA/WMA）的股票家數。

### `api/indicator.py`
- `sma_pivot_df(pivot_df, n)`：n 日簡單移動平均線（SMA）
- `ema_pivot_df(pivot_df, n)`：n 日指數移動平均線（EMA）
- `wma_pivot_df(pivot_df, weight_pivot_df, n)`：n 日加權移動平均線（WMA）
- `n_day_high_pivot_df(pivot_df, n)`：n 日新高價
- `n_day_low_pivot_df(pivot_df, n)`：n 日新低價
- `k_pivot_df(close_pivot_df, low_pivot_df, high_pivot_df, n=9)`：KD 隨機指標 K 值
- `d_pivot_df(k_pivot_df, n=3)`：KD 隨機指標 D 值
- `macd_pivot_df(pivot_df, fast=12, slow=26, signal=9)`：MACD 指標
- `williams_pivot_df(close_pivot_df, low_pivot_df, high_pivot_df, n=14)`：Williams %R 指標
- `add_ma(df, n, price_col='收盤價')`：計算 n 日移動平均線，欄位名 MA{n}
- `add_ma_pivots(df, ma_list)`：計算多股的 n 日移動平均線，欄位名 MA{n}
- `add_macd(df, fast=12, slow=26, signal=9, price_col='收盤價')`：計算 MACD 指標

### `tool_dashboard.py`
- 市場寬度指標、家數統計、均線站上家數等 demo 腳本，含多種指標統計與 CLI 範例

### `buffett_say.py`
- 巴菲特選股條件範例腳本，結合多因子指標篩股

-## API 檔案與函式一覽

### `api/db_lib.py`  
- `get_connection()`：連線至資料庫（自動讀取 .env 設定）
- `list_tables()`：列出所有資料表
- `list_columns(table_name)`：查詢資料表欄位


### `api/process_df.py`
- `parse_date_range(date_str)`：解析日期區間字串
- `get_db_df(date_range_str, column_str, index_name, table_name, constraint_str)`：取得 price 資料表 單股 df（index: date, columns: stock_id, values: 欄位值），自動檢查 NaN
- `get_feature_df(feature_name, key_value)`：取得 單股 df 中，feature_name 為 key_value 的資料
- `get_db_pivot_df(date_range_str, column_name, value_name)`：自動偵測資料表日期格式（西元/民國），查詢 monthly_revenue、price 等表皆自動處理。取得多股 pivot df（index: date, columns: stock_id, values: 欄位值），自動檢查 NaN
- `get_branch_data(date_range_str, stock_col, view_dealer_col, constraint_str)`：取得 dealer 資料表 單股 df（index: date, column: 股票名稱, 分點名稱, 買進金額, 賣出金額），自動檢查 NaN
- `get_stock_data(date_range_str, column_str)`：取得 price 資料表 單股 df（index: date, columns: stock_id, values: 欄位值），自動檢查 NaN

### `api/indicator.py`
- `add_ma(df, n, price_col='收盤價')`：計算 n 日移動平均線，欄位名 MA{n}
- `add_ma_pivots(df, ma_list)`：計算多股的 n 日移動平均線，欄位名 MA{n}
- `add_macd(df, fast=12, slow=26, signal=9, price_col='收盤價')`：計算 MACD 指標

### `api/filter.py`
- `golden_alignment_pivot(ma_pivots, ma_list)`：多頭排列條件（pivot 結構，支援多股）
- `ma_entangled_pivot(ma_pivots, ma_list, tol=0.01)`：均線糾纏條件（pivot 結構，支援多股）

### `api/plot.py`
- `plot_overlay(df, indicator_cols, stock_id, price_col='收盤價', volume_col='成交股數', date_col='date', title=None)`：收盤價與多指標疊圖，含成交量

---

## API 範例
- `api/filter.py`：
  - `golden_alignment_pivot(ma_pivots, ma_list)`：多頭排列條件（pivot 結構，支援多股）
  - `ma_entangled_pivot(ma_pivots, ma_list, tol)`：均線糾纏條件（pivot 結構，支援多股）
- `api/indicator.py`：
  - `add_ma(df, n)`：計算 n 日移動平均線
  - `add_macd(df)`：計算 MACD 指標
- `api/plot.py`：
  - `plot_overlay(df, indicator_cols, stock_id, ...)`：收盤價與多指標疊圖
（可任意傳入指標欄位）
  from api.plot import plot_overlay
  plot_overlay(df, ['MA5', 'MA10', 'MA20', 'MA60', 'MA120', 'MACD'], stock_id='2330')
  ```
- 詳細精神請見 AI_Collaboration_Guide.md 之 OOP 與 API 抽象設計。


## tool_dashboard.py 示範腳本

本檔案為「市場寬度指標、家數統計」的 demo 腳本，展示如何批次統計創新高/新低家數、均線站上家數、漲跌持平家數等。
- 可直接執行，並列印各指標統計結果。
- 適合用於 dashboard 或市場寬度分析。

## buffett_say.py 示範腳本

本檔案為「巴菲特選股條件」範例腳本，結合多因子指標（如均線、成交量、EPS、月營收等）進行篩股。
- 可自訂條件組合，篩選出最後一天符合條件的股票清單。
- 適合因子策略、價值型選股參考。

## tool_view_stock_dealers.py 示範腳本

本檔案為「券商分點與股票 K 線分析」的互動式範例腳本，適合初學者觀摩及快速上手。
- 支援 CLI 輸入股票代碼，顯示近 100 日 K 線、成交量與主要券商買賣行為。
- 主要流程與繪圖皆有詳細註解，便於學習與自訂。

### 執行方式
```bash
# 建議於專案根目錄下，啟用虛擬環境後執行：
.venv/Scripts/python.exe tool_view_stock_dealers.py
```

### 功能簡介
- 互動式輸入股票代碼
- 顯示該股近 100 日 K 線圖與均線
- 取得「台積電」分點券商買賣金額，找出累積前三大券商並繪圖


## 文件與版本管理規範
- `.gitignore`：務必包含 .venv、.env、csv/ 等暫存/敏感資料。

---

### 資料表欄位對應自動化（Hash Mapping Layer）

本專案支援自動化的資料表欄位名稱與常用熟悉名（familiar name）對應管理，提升資料查詢與程式維護便利性。

#### 主要組件

- `api/utility.py`：
  - `to_roc(date_str)`：將西元日期（YYYY-MM-DD）轉民國日期（YYY-MM-DD）
  - `to_ad(roc_str)`：將民國日期（YYY-MM-DD）轉西元日期（YYYY-MM-DD）
  - `check_date_format(try_parse_date)`：自動判斷日期字串格式（支援西元/民國、各種分隔符號）
  - 其他訊息與警告組裝等小工具
- `api/db_lib.py`：
  - 新增多個 function 負責資料表欄位與熟悉名的 hash 對應、反查、產生對應表。
  - 產生與管理 raw/common/filtered table column hash。
  - 提供 `get_table_column_mapping_df()` 產生欄位對應 DataFrame 並自動輸出 csv。
- `table_column_hash_util.py`：
  - 一鍵產生/更新所有 hash 對應檔案。
  - 產生人工可讀的 table（db, table, column, familiar_name）並顯示於 CLI。
- `common/table_common_col_rule.txt`：
  - 管理所有熟悉名（常用代號）的對應規則。
- `csv/table_column_mapping.csv`：
  - 產生的對應表，供人工查閱。
- `json/` 目錄：
  - 儲存 raw_table_column_hash.json、common_table_column_hash.json、filtered_table_column_hash.json 三個對應檔案。

#### 使用流程

1. 執行 `python table_column_hash_util.py`，自動產生/更新所有 hash 檔案與 csv 對應表。
2. 在程式中可透過 `from api.db_lib import get_table_column_mapping_df` 取得對應 DataFrame。
3. 欲修改熟悉名對應規則，請編輯 `common/table_common_col_rule.txt`，再重新執行產生指令。

#### 注意事項
- `json/` 資料夾已加入 `.gitignore`，避免將大量自動產生檔案納入 git。
- 欄位對應表與 hash 過程皆自動化，減少人工維護成本。

---
 共用欄位對應規則（Column Mapping Rules）

- 所有 table/column 對應規則集中於 `common/table_common_col_rule.txt`，可依需求增減或調整。
- 若需新增/修改規則，請直接編輯該檔案。


---
# 目錄說明補充
- `api/backtest.py`：彈性回測主流程 API
- `api/dashboard.py`：市場寬度指標、家數統計等 dashboard 指標
- `api/indicator.py`：技術指標（SMA/EMA/WMA/KD/MACD/Williams%R）統一管理
- `tool_dashboard.py`：市場寬度指標 demo 腳本
- `buffett_say.py`：巴菲特選股條件範例腳本
- `common/`：集中存放欄位對應規則。
- `CHANGELOG.md`：每次重要結構、API、協作規範調整請同步紀錄。
- `AI_Collaboration_Guide.md`：協作、API 設計、OOP 抽象精神等皆有說明，建議新成員必讀。

## 跨平台環境快速建立

本專案支援 Windows、macOS、Linux。

推薦使用 [uv](https://github.com/astral-sh/uv) 建立乾淨、快速的 Python 執行環境：

```bash
# Windows 環境下安裝 uv (僅需一次)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 在專案根目錄自動建立虛擬環境
uv venv

# 安裝依賴
uv pip install -r requirements.txt
```

如未安裝 uv，也可用傳統 pip：
```bash
pip install -r requirements.txt
```

## 套件安裝與環境還原

本專案的 requirements.txt 已完整收錄所有必要的第三方依賴（pandas、pymysql、python-dotenv、pytest、black、isort、flake8 等）。

### 一鍵安裝（推薦 uv）

建議使用 [uv](https://github.com/astral-sh/uv) 來安裝所有依賴：
```bash
uv pip install -r requirements.txt
```
或使用傳統 pip：
```bash
pip install -r requirements.txt
```

安裝後即可直接進行測試、格式化、靜態檢查與開發，跨主機/團隊/CI/CD 都能保證一致環境。

### app/tool_lib.py
通用工具庫，現有功能：
- `discord_notification_msg(sender_account, sender_avatar_url, msg, webhook_url)`：發送 Discord webhook 通知，支援自訂名稱、頭像、訊息內容，遇錯誤自動顯示狀態。

## 測試與開發規範

### 自動化測試
- 測試腳本放於 `tests/`，使用 pytest。
- 執行所有測試：
  ```bash
  pytest
  ```

### 程式碼格式化與靜態檢查
- 格式化：
  ```bash
  black .
  isort .
  ```
- 靜態檢查：
  ```bash
  flake8 .
  ```
- 格式化/檢查規則已設定於 `pyproject.toml`。

### 開發建議
- 新增/修改功能請同步補測試。
- 保持 type hints、docstring 完整。
- commit 前請先格式化、靜態檢查與測試。

---
如需進一步自動化、通知、錯誤處理等功能，歡迎 issue 或聯絡維護者。
