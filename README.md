# OPMS LINE Bot + Rich Menu Deployer (整合版)

這是一個整合版 LINE Bot 專案，包含 webhook 事件處理與自定義 Rich Menu 部署功能。

---

## 📦 專案結構

```
root/
├── app.py                          # 主程式，整合 webhook 與 richmenu 部署功能
├── requirements.txt               # 套件需求
├── .render.yaml                   # Render 自動部署設定（若有）
├── .python-version                # 指定 Python 版本（若有）
├── Richmenu/
│   ├── richmenu1.json
│   ├── richmenu2.json
│   ├── OPMS_Richmenu_Advanced-1.png
│   └── OPMS_Richmenu_Advanced-2.png
```

---

## 🚀 部署至 Render

1. 建立新 Web Service，綁定此專案 GitHub Repository
2. 指定 Build Command（可留空）
3. 指定 Start Command：
   ```bash
   gunicorn app:app
   ```
4. 新增以下環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`：你的 LINE Bot token
   - `LINE_CHANNEL_SECRET`：你的 webhook 驗證用密鑰

---

## 🔁 Webhook 功能

當使用者輸入以下訊息時：

| 關鍵字          | 行為                       |
|-----------------|----------------------------|
| `richmenu1`     | 切換至文件資訊查詢頁        |
| `richmenu2`     | 切換至設計施工圖冊頁        |
| `查詢功能索引` | 回傳功能索引提示訊息         |

---

## 🧩 Rich Menu 部署功能

### 使用方式：
部署完成後，POST 到以下 endpoint：

```
POST https://your-render-app.onrender.com/deploy-richmenu
```

### 功能內容：
- 刪除所有舊的 richmenu
- 建立 richmenu1 & richmenu2，並分別綁定圖片
- 設定 richmenu1 為預設顯示

---

## 📝 注意事項

- 請在 `app.py` 中手動填入實際上傳成功後的 `RICHMENU1_ID` 與 `RICHMENU2_ID`
- 圖片必須為 PNG 格式，大小建議 2500x1686 或 2048x1381
- Rich Menu JSON 檔與圖片路徑已固定為 `Richmenu/` 資料夾