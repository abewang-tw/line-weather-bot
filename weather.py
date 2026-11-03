import os
import requests

def test_group_id():
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    group_id = os.environ.get("LINE_USER_ID") # 保險箱中的 Group ID
    
    if not access_token or not group_id:
        print("❌ 錯誤：請先確認 GitHub Secret 中已設定 LINE_ACCESS_TOKEN 與 LINE_USER_ID！")
        return

    # 清理開頭結尾可能的空白
    access_token = access_token.strip()
    group_id = group_id.strip()

    print(f"🔍 正在測試發送至 ID: {group_id}")

    # 簡單驗證 Group ID 的基本開頭格式
    if not group_id.startswith("C"):
        print("⚠️ 警告：輸入的 Group ID 不是以 'C' 開頭，可能誤填到了個人 User ID (U開頭)！")

    # 呼叫 LINE Push Message API
    api_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": group_id,
        "messages": [
            {
                "type": "text",
                "text": "✅ Group ID 驗證成功！天氣小秘書已連線到本群組。"
            }
        ]
    }

    res = requests.post(api_url, headers=headers, json=payload, timeout=10)

    if res.status_code == 200:
        print("🎉 驗證成功！LINE 群組已順利收到測試訊息。")
    else:
        print(f"❌ 驗證失敗！LINE 回傳 HTTP 狀態碼: {res.status_code}")
        print(f"🔍 詳細錯誤細節: {res.text}")

if __name__ == "__main__":
    test_group_id()
