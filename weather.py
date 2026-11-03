import os
import requests
import json

def check_weather_and_notify():
    # 1. 讀取密鑰
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("錯誤：找不到 LINE_ACCESS_TOKEN 或 LINE_USER_ID，請檢查 Secret 設定！")
        return

    # 2. 終極穩定版網址：改用標準 API 並加上防出錯預設值
    url = "https://open-meteo.com"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"天氣 API 伺服器回傳錯誤代碼: {response.status_code}")
            return
            
        data = response.json()
        daily = data.get('daily', {})
        
        # 提取當天數據 (防出錯機制：若沒抓到則給予預設值)
        temp_max = daily.get('temperature_2m_max', [25.0])[0]
        temp_min = daily.get('temperature_2m_min', [20.0])[0]
        rain_prob = daily.get('precipitation_probability_max', [0])[0]
        wind_speed = daily.get('wind_speed_10m_max', [0.0])[0]
        
        # 處理時間格式
        def clean_time(time_str_list):
            if time_str_list and len(time_str_list) > 0:
                t = time_str_list[0]
                return t.split("T")[1] if "T" in t else t
            return "無"

        sunrise = clean_time(daily.get('sunrise'))
        sunset = clean_time(daily.get('sunset'))
        moonrise = clean_time(daily.get('moonrise'))
        moonset = clean_time(daily.get('moonset'))
        
        # 穿搭與雨具建議邏輯
        if temp_max < 15:
            outfit = "天氣寒冷 🥶，請穿著厚外套、毛衣，注意保暖！"
        elif 15 <= temp_max < 22:
            outfit = "天氣偏涼 🧥，建議洋蔥式穿搭，記得帶件外套。"
        elif 22 <= temp_max < 28:
            outfit = "氣候舒適 👕，穿著長袖或短袖搭配薄外套即可。"
        else:
            outfit = "天氣炎熱 🥵，建議穿著透氣涼爽的衣服，並注意防曬！"

        umbrella_msg = "⚠️ 今天有機會下雨，出門記得帶傘喔！☔" if rain_prob >= 40 else "✨ 今天看來不用帶傘，祝你有美好的一天！☀️"

        # 組合推播訊息文字
        message = (
            f"🌤️ 今日天氣預報 (冬山)：\n"
            f"🌡️ 氣溫：{temp_min}°C ~ {temp_max}°C\n"
            f"💧 降雨機率：{rain_prob}%\n"
            f"💨 最大風速：{wind_speed} km/h\n"
            f"🌅 日出時間：{sunrise}\n"
            f"🌇 日落時間：{sunset}\n"
            f"🌔 月出時間：{moonrise}\n"
            f"🌘 月落時間：{moonset}\n"
            f"---\n"
            f"👗 穿搭建議：{outfit}\n"
            f"💡 貼心提醒：{umbrella_msg}"
        )

        # 3. 發送至 LINE Messaging API
        api_url = "https://line.me"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": message}]
        }
        
        res = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            print("🎉 太棒了！天氣預報訊息已成功發送到 LINE 群組！")
        else:
            print(f"❌ LINE 發送失敗！錯誤代碼: {res.status_code}")
            print(f"原因（請截圖此行給我）：{res.text}")
            
    except Exception as e:
        print(f"💥 程式執行時發生嚴重錯誤: {e}")

if __name__ == "__main__":
    check_weather_and_notify()
