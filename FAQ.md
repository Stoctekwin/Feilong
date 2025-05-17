# Feilong 專案 Python 腳本執行指南

## 套件結構
本專案採用多層 package 結構（如 `api/`、`app/`），請務必使用「模組化」方式執行腳本，才能正確 import 其他 package。

## 執行 app 目錄下的腳本

### 正確方式（推薦）
請在專案根目錄（`Feilong`）下，使用 `-m` 參數執行，例如：

```bash
.venv\Scripts\python.exe -m app.price_ma
```
或
```bash
python -m app.price_ma
```
這樣 Python 會自動把 `Feilong` 當成 package root，能正確 import `api`、`app` 等模組。

### 常見錯誤
直接用
```bash
python app/price_ma.py
```
會出現 `ModuleNotFoundError: No module named 'api'`，因為 Python 無法自動找到專案根目錄。

### 備用方式（不推薦）
如果你必須用 `python app/price_ma.py`，可以在腳本最上方加：
```python
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```
但建議還是以 `-m` 方式執行，較乾淨且符合 Python package 標準。

---

## 其他
- 請確保在專案根目錄執行所有指令。
- 若有多層 package，皆建議用 `-m` 執行。
- 如有其他操作問題，請參考 README 或聯絡維護者。
