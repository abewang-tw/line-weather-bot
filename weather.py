import os
import requests

def check_weather_and_notify():
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("錯誤：找不到 LINE 密鑰，請檢查 Secret 設定！")
        return

    # 乾淨的 Open-Meteo 標準網址
    url = "https://open-meteo.com"
    
    # 預設的備用天氣（防止網站當機）
    message = "🌤️ 今日天氣預報小助手：\n\n目前天氣觀測站連線繁忙，小秘書提醒您出門在外還是要注意天氣變化，祝您有美好的一天！✨☔"

    try:
        print("正在嘗試連線天氣 API...")
        response = requests.get(url, timeout=15)
        print(f"天氣伺服器回應狀態碼: {response.status_code}")
        
        # 第一道防線：如果網站回傳錯誤代碼，直接走備用訊息，不強行轉換 JSON
        if response.status_code == 200:
            try:
                data = response.json()
                daily = data.get('daily', {})
                
                # 安全獲取列表內的第一個值
                temp_max_list = daily.get('temperature_2m_max', [25])
                temp_min_list = daily.get('temperature_2m_min', [20])
                rain_prob_list = daily.get('precipitation_probability_max', [0])
                
                temp_max = temp_max_list[0] if temp_max_list else 25
                temp_min = temp_min_list[0] if temp_min_list else 20
                rain_prob = rain_prob_list[0] if rain_prob_list else 0

                if temp_max < 15:
                    outfit = "天氣寒冷 🥶，請穿著厚外套、毛衣保暖！"
                elif 15 <= temp_max < 22:
                    outfit = "天氣偏涼 🧥，建議洋蔥式穿搭，帶件外套。"
                elif 22 <= temp_max < 28:
                    outfit = "氣候舒適 👕，穿著長袖或短袖搭配薄外套即可。"
                else:
                    outfit = "天氣炎熱 🥵，建議穿著透氣衣服並注意防曬！"

                umbrella_msg = "⚠️ 今天高機率下雨，出門記得帶傘喔！☔" if rain_prob >= 40 else "✨ 今天看來不用帶傘，祝你有美好的一天！☀️"

                message = (
                    f"🌤️ 今日天氣預報 (冬山)：\n"
                    f"🌡️ 氣溫：{temp_min}°C ~ {temp_max}°C\n"
                    f"💧 降雨機率：{rain_prob}%\n"
                    f"---\n"
                    f"👗 穿搭建議：{outfit}\n"
                    f"💡 貼心提醒：{umbrella_msg}"
                )
            except Exception as json_err:
                print(f"警告：網站回傳的不是乾淨的 JSON 格式。錯誤原因: {json_err}")
                print(f"伺服器實際回傳的文字內容為:\n{response.text}")
                print("將自動啟用備用暖心語句發送...")
        else:
            print(f"伺服器沒給200，回傳內容為:\n{response.text}")

    except Exception as network_err:
        print(f"網路連線超時或發生其他錯誤: {network_err}")
        print("將自動啟用備用暖心語句發送...")

    # 第二道防線：無論天氣 API 有沒有當機，程式都「絕對會」執行發送 LINE 指令
    print("正在準備發送訊息至 LINE...")
    api_url = "https://line.me"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    
    try:
        res = requests.post(api_url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            print("🎉 🎉 🎉 太棒了！天氣通知已真正成功發送到 LINE 群組了！")
        else:
            print(f"❌ LINE 伺服器拒絕發送，錯誤代碼: {res.status_code}")
            print(f"LINE 拒絕的原因為: {res.text}")
    except Exception as line_err:
        print(f"發送給 LINE 時網路發生錯誤: {line_err}")

if __name__ == "__main__":
    check_weather_and_notify()
