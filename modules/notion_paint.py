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

        # 擷取欄位值
        title = get_text(props.get("Title", {}).get("title", []))
        name = get_text(props.get("Name", {}).get("rich_text", []))
        site1 = get_text(props.get("Site1", {}).get("rich_text", [])) or "-"
        site2 = get_text(props.get("Site2", {}).get("rich_text", [])) or "-"
        site3 = get_text(props.get("Site3", {}).get("rich_text", [])) or "-"
        brand = get_text(props.get("Brand", {}).get("rich_text", [])) or ""
        color_number = get_text(props.get("ColorNumber", {}).get("rich_text", [])) or "色號未提供"
        uri = props.get("uri", {}).get("url", "#")
        color_code = get_text(props.get("ColorCode", {}).get("rich_text", [])) or "#CCCCCC"

        bubble = {
            "type": "bubble",
            "size": "deca",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "color": "#ffffff",
                        "align": "start",
                        "size": "xxl",
                        "gravity": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": name,
                        "color": "#ffffff",
                        "align": "start",
                        "size": "lg",
                        "gravity": "center",
                        "margin": "lg"
                    }
                ],
                "paddingTop": "19px",
                "paddingAll": "12px",
                "paddingBottom": "16px",
                "height": "150px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置1",
                                "color": "#8C8C8C",
                                "size": "sm",
                                "wrap": True,
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": site1,
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置2",
                                "flex": 1,
                                "size": "sm",
                                "color": "#8C8C8C"
                            },
                            {
                                "type": "text",
                                "text": site2,
                                "flex": 2,
                                "color": "#666666",
                                "size": "sm"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": brand,
                        "align": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": color_number,
                            "uri": uri
                        }
                    }
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": color_code
                },
                "footer": {
                    "separator": False
                }
            }
        }

        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles[:10]  # 限制最多10張卡片
    }

def get_text(rich_items):
    if not rich_items:
        return ""
    return "".join([r.get("plain_text", "") for r in rich_items])
