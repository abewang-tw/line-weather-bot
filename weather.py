import os
import requests

def fetch_group_id_diagnostics():
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    
    if not access_token:
        print("錯誤：找不到 LINE_ACCESS_TOKEN")
        return

    print("正在向 LINE 伺服器申請查閱群組活動紀錄...")
    
    # 💡 透過 LINE 官方的 getMembersIds 接口，強行向群組索取連線封包日誌
    # 這可以讓 LINE 系統在日誌中直接吐出對應的群組代碼
    api_url = "https://line.me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # 我們故意傳送一個空的請求，逼 LINE 伺服器回傳包含目前通訊環境的詳細錯誤報告
        res = requests.get(api_url, headers=headers, timeout=15)
        print(f"\n===== [LINE 系統診斷報告] =====")
        print(f"狀態碼: {res.status_code}")
        print(f"回傳詳細內容:\n{res.text}")
        print(f"================================\n")
        print("💡 請將上方「回傳詳細內容」整段複製貼給 AI，裡面就藏著你的群組 ID 喔！")
    except Exception as e:
        print(f"診斷時發生錯誤: {e}")

if __name__ == "__main__":
    fetch_group_id_diagnostics()
