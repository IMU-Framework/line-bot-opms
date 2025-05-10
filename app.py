from flask import Flask, request, abort
import os
import json
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

# 用於暫存 rich menu ID
RICHMENU1_ID = None
RICHMENU2_ID = None

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
    global RICHMENU1_ID, RICHMENU2_ID

    text = event.message.text.strip().lower()
    user_id = event.source.user_id
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        if text == "richmenu1" and RICHMENU1_ID:
            api.link_rich_menu_to_user(user_id, RICHMENU1_ID)

        elif text == "richmenu2" and RICHMENU2_ID:
            api.link_rich_menu_to_user(user_id, RICHMENU2_ID)

        elif text == "查詢功能綜合":
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

@app.route("/deploy-richmenu", methods=["POST"])
def deploy_richmenu():
    global RICHMENU1_ID, RICHMENU2_ID

    try:
        configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
        api = MessagingApi(ApiClient(configuration))

        # 刪除所有舊 rich menu
        for menu in api.get_rich_menu_list().rich_menus:
            api.delete_rich_menu(menu.rich_menu_id)

        # 建立 richmenu1
        with open("Richmenu/richmenu1.json", "r", encoding="utf-8") as f:
            richmenu1_dict = json.load(f)
        richmenu1 = api.create_rich_menu(richmenu1_dict)
        RICHMENU1_ID = richmenu1.rich_menu_id
        with open("Richmenu/OPMS_Richmenu_Advanced-1.png", "rb") as f:
            api.set_rich_menu_image(RICHMENU1_ID, f, "image/png")

        # 建立 richmenu2
        with open("Richmenu/richmenu2.json", "r", encoding="utf-8") as f:
            richmenu2_dict = json.load(f)
        richmenu2 = api.create_rich_menu(richmenu2_dict)
        RICHMENU2_ID = richmenu2.rich_menu_id
        with open("Richmenu/OPMS_Richmenu_Advanced-2.png", "rb") as f:
            api.set_rich_menu_image(RICHMENU2_ID, f, "image/png")

        # 設定預設顯示
        api.set_default_rich_menu(RICHMENU1_ID)

        return "Rich menus deployed and linked.", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
