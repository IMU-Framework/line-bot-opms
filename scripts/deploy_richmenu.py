import os
import json
import argparse
import requests
from linebot.v3.webhooks import PostbackEvent

LINE_API_BASE = "https://api.line.me/v2/bot"
ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

RICHMENU_ID_MAP = {
    "richmenu1": None,
    "richmenu2": None
}

def list_richmenus():
    response = requests.get(f"{LINE_API_BASE}/richmenu/list", headers=HEADERS)
    response.raise_for_status()
    return response.json().get("richmenus", [])

def delete_richmenu(richmenu_id):
    response = requests.delete(f"{LINE_API_BASE}/richmenu/{richmenu_id}", headers=HEADERS)
    response.raise_for_status()

def create_richmenu(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    response = requests.post(f"{LINE_API_BASE}/richmenu", headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()["richMenuId"]

def upload_image(richmenu_id, image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    image_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "image/png"
    }
    response = requests.post(f"{LINE_API_BASE}/richmenu/{richmenu_id}/content", headers=image_headers, data=image_data)
    response.raise_for_status()

def set_default_richmenu(richmenu_id):
    response = requests.post(f"{LINE_API_BASE}/user/all/richmenu/{richmenu_id}", headers=HEADERS)
    response.raise_for_status()

def save_richmenu_map(mapping):
    with open("richmenu_map.py", "w", encoding="utf-8") as f:
        f.write("RICHMENU_ID_MAP = " + json.dumps(mapping, indent=2, ensure_ascii=False))

def handle_postback_event(event: PostbackEvent, line_bot_api):
    user_id = event.source.user_id
    data = event.postback.data

    print(f"[POSTBACK] user_id: {user_id}")
    print(f"[POSTBACK] data: {data}")

    if data.startswith("goto="):
        target_key = data.split("=")[1]
        target_id = RICHMENU_ID_MAP.get(target_key)

        if target_id:
            print(f"[POSTBACK] Switching to: {target_key} ({target_id})")
            line_bot_api.link_rich_menu_to_user(user_id, target_id)
        else:
            print(f"[ERROR] Unknown richmenu key: {target_key}")

def main(menu_name, delete_old):
    menu_map = {
        "richmenu1": {
            "json": "Richmenu/richmenu1.json",
            "img": "Richmenu/OPMS_Richmenu_Advanced-1.png"
        },
        "richmenu2": {
            "json": "Richmenu/richmenu2.json",
            "img": "Richmenu/OPMS_Richmenu_Advanced-2.png"
        }
    }

    if menu_name not in menu_map:
        print("錯誤：請指定 richmenu1 或 richmenu2")
        return

    if delete_old:
        print("正在刪除所有舊有 Rich Menu...")
        for menu in list_richmenus():
            try:
                delete_richmenu(menu["richMenuId"])
                print(f"已刪除：{menu['name']} ({menu['richMenuId']})")
            except Exception as e:
                print(f"刪除失敗：{e}")

    print(f"建立並部署 {menu_name} 中...")
    menu = menu_map[menu_name]
    richmenu_id = create_richmenu(menu["json"])
    upload_image(richmenu_id, menu["img"])
    set_default_richmenu(richmenu_id)

    # 更新對應表並存入 richmenu_map.py
    RICHMENU_ID_MAP[menu_name] = richmenu_id
    save_richmenu_map(RICHMENU_ID_MAP)

    print(f"已完成部署：{menu_name} 並設為預設 Rich Menu（ID: {richmenu_id}）")
    print("→ richmenu_map.py 已更新")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", required=True, help="richmenu1 或 richmenu2")
    parser.add_argument("--delete-old", action="store_true", help="刪除所有現有 Rich Menu")
    args = parser.parse_args()
    main(args.menu, args.delete_old)
