# from flask import Flask, request, abort
# import os
# import json

# from linebot.v3 import WebhookHandler
# from linebot.v3.exceptions import InvalidSignatureError
# from linebot.v3.webhooks import MessageEvent, TextMessageContent
# from linebot.v3.messaging import (
#     Configuration, ApiClient, MessagingApi,
#     ReplyMessageRequest, TextMessage
# )

# app = Flask(__name__)

# # LINE credentials
# CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

# handler = WebhookHandler(CHANNEL_SECRET)

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     text = event.message.text.lower()
#     user_id = event.source.user_id
#     configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

#     with ApiClient(configuration) as api_client:
#         api = MessagingApi(api_client)

#         if text == "richmenu1":
#             api.link_rich_menu_to_user(user_id, "RICHMENU1_ID")
#         elif text == "richmenu2":
#             api.link_rich_menu_to_user(user_id, "RICHMENU2_ID")
#         elif text == "查詢功能索引":
#             api.reply_message(
#                 ReplyMessageRequest(
#                     reply_token=event.reply_token,
#                     messages=[TextMessage(
#                         text="請輸入以下指令之一：\n- 油漆色號\n- 企業識別 or CIS"
#                     )]
#                 )
#             )

# @app.route("/callback", methods=["POST"])
# def callback():
#     signature = request.headers.get("X-Line-Signature", "")
#     body = request.get_data(as_text=True)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)
#     return "OK"

from flask import Flask, request, abort
import os
import json
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
    CreateRichMenuRequest
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
    text = event.message.text.lower()
    user_id = event.source.user_id
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        if text == "richmenu1":
            api.link_rich_menu_to_user(user_id, "RICHMENU1_ID")
        elif text == "richmenu2":
            api.link_rich_menu_to_user(user_id, "RICHMENU2_ID")
        elif text == "查詢功能索引":
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請輸入以下指令之一：\n- 油漆色號\n- 企業識別 or CIS"
                    )]
                )
            )

@app.route("/deploy-richmenu", methods=["POST"])
def deploy_richmenu():
    try:
        configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
        api = MessagingApi(ApiClient(configuration))

        # 刪除所有舊 rich menu
        for menu in api.get_rich_menu_list().rich_menus:
            api.delete_rich_menu(menu.rich_menu_id)

        # richmenu1
        with open("Richmenu/richmenu1.json", "r", encoding="utf-8") as f:
            richmenu1_json = json.load(f)
        richmenu1_req = CreateRichMenuRequest.from_dict(richmenu1_json)
        richmenu1 = api.create_rich_menu(richmenu1_req)
        with open("Richmenu/OPMS_Richmenu_Advanced-1.png", "rb") as f:
            api.set_rich_menu_image(richmenu1.rich_menu_id, f, "image/png")

        # richmenu2
        with open("Richmenu/richmenu2.json", "r", encoding="utf-8") as f:
            richmenu2_json = json.load(f)
        richmenu2_req = CreateRichMenuRequest.from_dict(richmenu2_json)
        richmenu2 = api.create_rich_menu(richmenu2_req)
        with open("Richmenu/OPMS_Richmenu_Advanced-2.png", "rb") as f:
            api.set_rich_menu_image(richmenu2.rich_menu_id, f, "image/png")

        api.set_default_rich_menu(richmenu1.rich_menu_id)

        return "Rich menus deployed successfully", 200
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
