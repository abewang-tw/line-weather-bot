import os
import requests

def check_weather_and_notify():
    # 1. 從 GitHub 保險箱拿取新版的兩把鑰匙
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("找不到 LINE 密鑰，請檢查 Settings 中的 Secret 設定！")
        return

    # 2. 改用更穩定的 Open-Meteo 抓取台北天氣資料
    url = "https://api.open-meteo.com/v1/forecast?latitude=25.0478&longitude=121.5319&daily=precipitation_probability_max&timezone=Asia%2FTaipei"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 取得今天 (第0天) 的最高降雨機率
        rain_prob = data['daily']['precipitation_probability_max'][0]
        
        need_umbrella = False
        if rain_prob >= 40: # 降雨機率 40% 以上就提醒帶傘
            need_umbrella = True

        # 整理要發送的文字
        message = f"今日天氣預報：\n今日最高降雨機率：{rain_prob}%\n"
        if need_umbrella:
            message += "⚠️ 今天有機會下雨，出門記得帶傘喔！☔"
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
