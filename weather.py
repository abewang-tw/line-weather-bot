import os
import requests

def check_weather_and_notify():
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("找不到 LINE 密鑰！")
        return

    # 💡 使用最乾淨的 Open-Meteo 標準格式網址
    url = "https://open-meteo.com"
    
    try:
        response = requests.get(url)
        # 如果伺服器回傳狀態碼不是 200，直接印出錯誤
        if response.status_code != 200:
            print(f"天氣 API 請求失敗，狀態碼: {response.status_code}")
            return
            
        data = response.json()
        daily = data.get('daily', {})
        
        # 安全地獲取清單中的第一個元素
        temp_max = daily.get('temperature_2m_max', [25.0])[0]
        temp_min = daily.get('temperature_2m_min', [20.0])[0]
        rain_prob = daily.get('precipitation_probability_max', [0])[0]
        wind_speed = daily.get('wind_speed_10m_max', [0.0])[0]
        
        # 修正時間格式，安全擷取時間部分
        def get_time_str(time_list):
            if time_list and len(time_list) > 0 and "T" in time_list[0]:
                return time_list[0].split("T")[1]
            return "無"

        sunrise = get_time_str(daily.get('sunrise'))
        sunset = get_time_str(daily.get('sunset'))
        moonrise = get_time_str(daily.get('moonrise'))
        moonset = get_time_str(daily.get('moonset'))
        
        # 穿搭邏輯
        if temp_max < 15:
            outfit = "天氣寒冷 🥶，請穿著厚外套、毛衣，注意保暖！"
        elif 15 <= temp_max < 22:
            outfit = "天氣偏涼 🧥，建議洋蔥式穿搭，記得帶件外套。"
        elif 22 <= temp_max < 28:
            outfit = "氣候舒適 👕，穿著長袖或短袖搭配薄外套即可。"
        else:
            outfit = "天氣炎熱 🥵，建議穿著透氣涼爽的衣服，並注意防曬！"

        need_umbrella = rain_prob >= 40
        umbrella_msg = "⚠️ 今天有機會下雨，出門記得帶傘喔！☔" if need_umbrella else "✨ 今天看來不用帶傘，祝你有美好的一天！☀️"

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

        api_url = "https://line.me"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": message}]
        }
        
        res = requests.post(api_url, headers=headers, json=payload)
        if res.status_code == 200:
            print("天氣預報發送成功！")
        else:
            print(f"發送失敗，錯誤碼: {res.status_code}, 原因: {res.text}")
            
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    check_weather_and_notify()
