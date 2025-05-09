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
    text = event.message.text.strip().lower()
    config = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(config) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text in ["油漆色號", "paint"]:
            contents = load_flex_template("paint.json")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(
                        alt_text="油漆色號",
                        contents=FlexContainer.from_dict(contents)
                    )]
                )
            )
        elif text in ["cis", "企業識別"]:
            contents = load_flex_template("cis.json")
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(
                        alt_text="企業識別色卡",
                        contents=FlexContainer.from_dict(contents)
                    )]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請輸入以下指令之一：
- 油漆色號
- 企業識別 or CIS"
                    )]
                )
            )
