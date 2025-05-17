# Feilong 專案快速啟動指南（含 SSH 與 uv 虛擬環境）

本指南整理從 SSH 金鑰設定、GitHub 連線、專案 clone、到使用 uv 建立 Python 虛擬環境的完整流程，適合新環境部署、協作成員 onboarding。

---

## 1. 設定 GitHub SSH 金鑰

1. **產生 SSH 金鑰**（若尚未建立）
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   - 依照指示按 Enter，預設會產生於 `C:/Users/你的使用者/.ssh/id_ed25519.pub`

2. **複製公鑰內容**
   ```powershell
   cat $env:USERPROFILE\.ssh\id_ed25519.pub
   ```
   - 複製顯示內容。

3. **新增至 GitHub**
   - 登入 GitHub > Settings > SSH and GPG keys > New SSH key。
   - 貼上剛剛複製的內容，命名 Title。

4. **驗證連線**
   ```powershell
   ssh -T git@github.com
   ```
   - 若顯示歡迎訊息即設定成功。

---

## 2. Clone Feilong 專案

```powershell
git clone git@github.com:Stoctekwin/Feilong.git
cd Feilong
```

若已經有本地資料夾，可在該資料夾下：
```powershell
git init
git remote add origin git@github.com:Stoctekwin/Feilong.git
git fetch origin
git pull origin main
```

---

## 3. 建立 Python 虛擬環境（推薦 uv）

### 3.1 安裝 uv（建議用 conda/python 執行）
```powershell
python -m pip install uv
```

### 3.2 建立虛擬環境
```powershell
uv venv
```

### 3.3 安裝依賴
```powershell
uv pip install -r requirements.txt
```

---

## 4. 啟動虛擬環境

Windows Powershell：
```powershell
.venv\Scripts\activate
```

---

## 5. 常見問題排查
- 若出現 `pip`、`uv` 指令找不到，請確認 Python 路徑與安裝方式（可用 conda/python.exe 明確指定執行）。
- 若 `.venv` 內缺少 pip，可用：
  ```powershell
  .venv\Scripts\python.exe -m ensurepip
  ```
- 若遇到權限、網路、依賴問題，請參考 Feilong 專案 README 或聯絡維護者。

---

## 6. 參考文件
- [AI_Collaboration_Guide.md]
- [README.md]
- [CHANGELOG.md]
- [requirements.txt]

---

本指南可依實際經驗持續補充，歡迎 PR！
