import os
import requests

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_PAINT_TABLE_DB")

def fetch_notion_paint_data():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    return res.json().get("results", [])

def build_paint_table_flex():
    notion_rows = fetch_notion_paint_data()

    bubbles = []
    for row in notion_rows:
        props = row["properties"]

        title = get_text(props.get("Title", {}).get("title", []))
        name = get_text(props.get("Name", {}).get("rich_text", []))
        site1 = get_text(props.get("Site1", {}).get("rich_text", []))
        site2 = get_text(props.get("Site2", {}).get("rich_text", []))
        site3 = get_text(props.get("Site3", {}).get("rich_text", []))
        brand = get_text(props.get("Brand", {}).get("rich_text", []))
        color_number = get_text(props.get("ColorNumber", {}).get("rich_text", [])) or "色號未提供"
        uri = props.get("uri", {}).get("url", "#")
        color_code = get_text(props.get("ColorCode", {}).get("rich_text", [])) or "#CCCCCC"

        site_contents = []
        for site in [site1, site2, site3]:
            if site:
                site_contents.append({
                    "type": "text",
                    "text": site,
                    "size": "xs",
                    "wrap": True
                })

        bubble = {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": title or "無標題",
                        "weight": "bold",
                        "size": "sm",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": name,
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "md",
                        "contents": site_contents
                    },
                    {
                        "type": "text",
                        "text": brand,
                        "size": "xs",
                        "color": "#aaaaaa",
                        "margin": "md",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": color_number,
                            "uri": uri
                        },
                        "color": color_code
                    }
                ],
                "flex": 0
            },
            "styles": {
                "body": {
                    "backgroundColor": color_code
                },
                "footer": {
                    "backgroundColor": color_code
                }
            }
        }

        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }

def get_text(rich_items):
    if not rich_items:
        return ""
    return "".join([r.get("plain_text", "") for r in rich_items])
