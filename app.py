from flask import Flask, request, abort
import os
import json
import subprocess

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip().lower()
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        if text == "查詢功能索引":
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請輸入下列指令之一：\n- 油漆色號\n- 企業識別 or CIS"
                    )]
                )
            )

        elif text == "油漆色號":
            with open("flex_templates/paint.json", "r", encoding="utf-8") as f:
                paint_flex = json.load(f)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(
                        alt_text="油漆色號",
                        contents=FlexContainer.from_dict(paint_flex)
                    )]
                )
            )

        elif text in ["企業識別", "cis"]:
            with open("flex_templates/cis.json", "r", encoding="utf-8") as f:
                cis_flex = json.load(f)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(
                        alt_text="企業識別色卡",
                        contents=FlexContainer.from_dict(cis_flex)
                    )]
                )
            )

        else:
            return  # 不回應其他非指定輸入

# 自動部署 Rich Menu（僅在雲端執行環境中）
if os.environ.get("AUTO_DEPLOY_RICHMENU") == "true":
    print("⚙️ 正在自動部署 Rich Menus...")
    subprocess.run(["python", "scripts/deploy_richmenu.py", "--menu", "all", "--delete-old"])
    print("✅ Rich Menu richmenu1 + richmenu2 自動部署完成")

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)