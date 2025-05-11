from flask import Flask, request, abort
import os
import json
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from scripts.deploy_richmenu import handle_postback_event
from scripts.richmenu_map import RICHMENU_ID_MAP
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
)

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
handler = WebhookHandler(CHANNEL_SECRET)

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

@handler.add(PostbackEvent)
def route_postback(event):
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        handle_postback_event(event, api)

if __name__ == "__main__":
    app.run(debug=True)
