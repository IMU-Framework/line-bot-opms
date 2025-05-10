from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
import json

app = Flask(__name__)

# 使用環境變數
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

def load_flex_template(filename):
    with open(f"flex_templates/{filename}", encoding="utf-8") as f:
        return json.load(f)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text.strip()

    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    if text == "油漆色號":
        flex_message = load_paint_flex_json()
        reply = FlexMessage(
            alt_text="油漆色號資訊",
            contents=FlexContainer.from_dict(flex_message)
        )

    elif text in ["企業識別", "CIS"]:
        flex_message = load_cis_flex_json()
        reply = FlexMessage(
            alt_text="企業識別色卡",
            contents=FlexContainer.from_dict(flex_message)
        )

    elif text == "查詢功能索引":
        reply = TextMessage(
            text=(
                "請輸入以下指令之一：\n"
                "- 油漆色號\n"
                "- 企業識別 or CIS"
            )
        )
    else:
        # 非指令 → 不回覆
        return

    # 發送訊息（在前面任何條件中有匹配才會執行）
    try:
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[reply]
                )
            )
    except Exception as e:
        print(f"回覆訊息時發生錯誤: {str(e)}")
