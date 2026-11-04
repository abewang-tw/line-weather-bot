import os
import requests

def diagnose_and_send():
    access_token = os.environ.get("LINE_ACCESS_TOKEN", "").strip()
    target_id = os.environ.get("LINE_USER_ID", "").strip()

    print(f"📌 當前設定的目標 ID: {target_id}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 1. 驗證 Token 是否正常有效
    print("\n--- 檢查 1: 驗證 Token 狀態 ---")
    bot_info_res = requests.get("https://api.line.me/v2/bot/info", headers=headers)
    print(f"機器人資料狀態: {bot_info_res.status_code}")
    if bot_info_res.status_code != 200:
        print(f"❌ Token 異常，LINE 回傳: {bot_info_res.text}")
        return
    else:
        bot_data = bot_info_res.json()
        print(f"✅ Token 有效！當前機器人名稱: {bot_data.get('displayName')}")

    # 2. 查詢機器人目前加入的所有群組 ID
    print("\n--- 檢查 2: 查詢機器人所在的所有群組 ---")
    groups_res = requests.get("https://api.line.me/v2/bot/user/all/group/ids", headers=headers)
    print(f"群組清單狀態: {groups_res.status_code}")
    
    real_group_ids = []
    if groups_res.status_code == 200:
        real_group_ids = [item.get("groupId") for item in groups_res.json().get("groupDetails", [])]
        print(f"📋 官方確認機器人所在的群組清單: {real_group_ids}")
    else:
        print(f"⚠️ 無法取得群組清單: {groups_res.text}")

    # 3. 比對 ID 是否吻合
    print("\n--- 檢查 3: ID 比對 ---")
    if target_id in real_group_ids:
        print("✅ target_id 與官方群組 ID 完全吻合！準備測試推播...")
    else:
        print(f"❌ 警告：你的 target_id ({target_id}) 不在機器人加入的群組清單中！")
        if real_group_ids:
            print(f"👉 請將 GitHub Secret 的 LINE_USER_ID 改為清單中的正確 ID: {real_group_ids[0]}")
            target_id = real_group_ids[0]
        else:
            print("❌ 官方清單為空，代表 LINE 伺服器端尚未判定機器人已加入任何群組。")
            return

    # 4. 嘗試傳送測試推播
    print("\n--- 檢查 4: 執行測試發送 ---")
    payload = {
        "to": target_id,
        "messages": [{"type": "text", "text": "🔔 群組連線驗證測試：天氣小秘書推播成功！"}]
    }
    push_res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print(f"推播回應碼: {push_res.status_code}")
    if push_res.status_code == 200:
        print("🎉 發送成功！請檢查群組訊息！")
    else:
        print(f"❌ 發送失敗: {push_res.text}")

if __name__ == "__main__":
    diagnose_and_send()
