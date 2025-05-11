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

# Alias 對應表
ALIAS_MAP = {
    "richmenu1": "richmenu-alias-1",
    "richmenu2": "richmenu-alias-2"
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

def bind_alias(alias_id, richmenu_id):
    url = f"{LINE_API_BASE}/richmenu/alias/{alias_id}"
    create = requests.post(
        f"{LINE_API_BASE}/richmenu/alias",
        headers=HEADERS,
        json={"richMenuAliasId": alias_id, "richMenuId": richmenu_id}
    )
    if create.status_code == 200:
        print(f"✅ Alias {alias_id} 已建立")
    elif create.status_code == 409:
        print(f"⚠️ Alias {alias_id} 已存在，執行更新...")
        patch = requests.patch(url, headers=HEADERS, json={"richMenuId": richmenu_id})
        if patch.status_code == 200:
            print(f"✅ Alias {alias_id} 已更新")
        else:
            print(f"❌ 更新 alias 失敗: {patch.text}")
    else:
        print(f"❌ 建立 alias 失敗: {create.text}")

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

    # 建立或更新 alias 綁定
    alias = ALIAS_MAP[menu_name]
    bind_alias(alias, richmenu_id)

    print(f"✅ 已完成部署：{menu_name} 並設為預設 Rich Menu（ID: {richmenu_id}）")
    print(f"→ Alias {alias} 也已完成綁定")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", required=True, help="richmenu1 或 richmenu2")
    parser.add_argument("--delete-old", action="store_true", help="刪除所有現有 Rich Menu")
    args = parser.parse_args()
    main(args.menu, args.delete_old)
