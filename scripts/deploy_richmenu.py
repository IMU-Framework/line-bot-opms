import os
import json
import argparse
import requests

LINE_API_BASE = "https://api.line.me/v2/bot"
ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Alias 對應表
ALIAS_MAP = {
    "richmenu1": "richmenu-1",
    "richmenu2": "richmenu-2"
}

# Menu 對應 JSON 與圖片
MENU_MAP = {
    "richmenu1": {
        "json": "Richmenu/richmenu1.json",
        "img": "Richmenu/OPMS_Richmenu_Advanced-1.png"
    },
    "richmenu2": {
        "json": "Richmenu/richmenu2.json",
        "img": "Richmenu/OPMS_Richmenu_Advanced-2.png"
    }
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

# def upload_image(richmenu_id, image_path):
#     with open(image_path, "rb") as f:
#         image_data = f.read()
#     image_headers = {
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#         "Content-Type": "image/png"
#     }
#     response = requests.post(f"{LINE_API_BASE}/richmenu/{richmenu_id}/content", headers=image_headers, data=image_data)
#     response.raise_for_status()

def upload_image(richmenu_id, image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 找不到圖片檔案：{image_path}")

    with open(image_path, "rb") as f:
        image_data = f.read()

    image_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "image/png"
    }

    response = requests.post(
        f"{LINE_API_BASE}/richmenu/{richmenu_id}/content",
        headers=image_headers,
        data=image_data
    )
    response.raise_for_status()

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

def deploy(menu_name, delete_old=False):
    if menu_name not in ["richmenu1", "richmenu2", "all"]:
        print("錯誤：請指定 richmenu1、richmenu2 或 all")
        return

    if delete_old:
        print("🧹 正在刪除所有舊有 Rich Menu...")
        for menu in list_richmenus():
            try:
                delete_richmenu(menu["richMenuId"])
                print(f"🗑 已刪除：{menu['name']} ({menu['richMenuId']})")
            except Exception as e:
                print(f"❌ 刪除失敗：{e}")

    menu_list = MENU_MAP.keys() if menu_name == "all" else [menu_name]
    for name in menu_list:
        print(f"🚧 建立並部署 {name} 中...")
        menu = MENU_MAP[name]
        richmenu_id = create_richmenu(menu["json"])
        upload_image(richmenu_id, menu["img"])
        bind_alias(ALIAS_MAP[name], richmenu_id)
        print(f"✅ {name} 部署完成（ID: {richmenu_id}）並綁定 alias {ALIAS_MAP[name]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", required=True, help="richmenu1、richmenu2 或 all")
    parser.add_argument("--delete-old", action="store_true", help="刪除所有現有 Rich Menu")
    args = parser.parse_args()
    deploy(args.menu, args.delete_old)
