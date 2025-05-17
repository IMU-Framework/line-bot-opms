import os
import requests

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_PAINT_TABLE_DB")

def fetch_notion_paint_data():
    """
    從 Notion 資料庫獲取油漆資料
    
    Returns:
        list: Notion 資料庫中的所有記錄
    """
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
    """
    構建油漆表格的 Flex Message
    
    Returns:
        dict: LINE Flex Message 格式的輪播卡片
    """
    notion_rows = fetch_notion_paint_data()

    bubbles = []
    for row in notion_rows:
        props = row["properties"]

        # 設定預設/空白/fallback值，確保即使資料庫欄位缺失也能正常顯示
        title = get_text(props.get("Title", {}).get("title", [])) or "未命名"
        name = get_text(props.get("Name", {}).get("rich_text", [])) or "unnamed"
        site1 = get_text(props.get("Site1", {}).get("rich_text", [])) or "-"
        site2 = get_text(props.get("Site2", {}).get("rich_text", [])) or "-"
        site3 = get_text(props.get("Site3", {}).get("rich_text", [])) or "-"
        brand = get_text(props.get("Brand", {}).get("rich_text", [])) or "品牌未定"
        color_number = get_text(props.get("ColorNumber", {}).get("rich_text", [])) or "色號未定"
        color_code = get_text(props.get("ColorCode", {}).get("rich_text", [])) or "#CCCCCC"  # 預設灰色

        # URI 處理 - 如果為空則完全禁用按鈕
        uri = props.get("uri", {}).get("url", "")
        if not uri:
            # 當 URI 為空時，使用不同的內容呈現方式，而不是按鈕
            footer_content = {
                "type": "text",
                "text": color_number,
                "align": "center",
                "color": "#888888"  # 使用灰色文字表示這不是可點擊的內容
            }
        else:
            # 當 URI 有值時，使用按鈕
            footer_content = {
                "type": "button",
                "action": {
                    "type": "uri",
                    "label": color_number,
                    "uri": uri
                },
                "style": "link"
            }

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
                    # site1
                    {
                        "type": "box",
                        "layout": "baseline",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置1",
                                "flex": 1
                                "size": "sm",
                                "color": "#8C8C8C",
                                # "wrap": True,
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
                    # site2
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
                                "size": "sm"
                                "color": "#666666",

                            }
                        ]
                    },
                    # site3
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置3",
                                "flex": 1,
                                "size": "sm",
                                "color": "#8C8C8C"
                            },
                            {
                                "type": "text",
                                "text": site3,
                                "flex": 2,
                                "size": "sm"
                                "color": "#666666",
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
                        },
                        "style": "link",
                        "disabled": button_disabled  # 根據 URI 是否存在來設置按鈕狀態
                    }
                ]
            }
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
    """
    從 Notion 富文本欄位中提取純文本
    
    Args:
        rich_items: Notion 富文本欄位
        
    Returns:
        str: 提取的純文本
    """
    if not rich_items:
        return ""
    return "".join([r.get("plain_text", "") for r in rich_items])
