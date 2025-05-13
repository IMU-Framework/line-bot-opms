```
line-bot-opms/
│
├── app.py               # 主要應用程式邏輯
├── .python-version      # 指定 Python 版本（選用）
├── Procfile             # Gunicorn 啟動指令（供 Render 使用）
├── render.yaml          # Render 自動部署設定
├── requirements.txt     # 相依套件清單
│
└── templates/
    ├── cis.json         # 企業識別色卡 Flex Message 模板
    └── paint.json       # 油漆色號 Flex Message 模板
```
