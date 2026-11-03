import os
import requests

def check_weather_and_notify():
    # 1. 從 GitHub 保險箱拿取新版的兩把鑰匙
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("找不到 LINE 密鑰，請檢查 Settings 中的 Secret 設定！")
        return

    # 2. 抓取天氣資料
    city = "Taipei"
    url = f"https://wttr.in/{city}?format=%l:+%C+%t+下雨機率:+%p"
    
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        weather_info = response.text.strip()
        
        need_umbrella = False
        if "雨" in weather_info or "Rain" in weather_info or "Shower" in weather_info:
            need_umbrella = True

        # 整理要發送的文字
        message = f"今日天氣預報：\n{weather_info}\n"
        if need_umbrella:
            message += "⚠️ 今天高機率會下雨，出門記得帶傘喔！☔"
        else:
            message += "✨ 今天看來不用帶傘，祝你有美好的一天！☀️"

        # 3. 使用新版 Messaging API 發送訊息給自己
        api_url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        res = requests.post(api_url, headers=headers, json=payload)
        
        if res.status_code == 200:
            print("新版官方帳號訊息發送成功！")
        else:
            print(f"發送失敗，錯誤碼: {res.status_code}, 回傳內容: {res.text}")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    check_weather_and_notify()
