import os
import requests

def check_weather_and_notify():
    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    
    if not access_token or not user_id:
        print("找不到 LINE 密鑰！")
        return

    # 若要更改預報地點，請修改下方的 latitude (緯度) 與 longitude (經度)
    # 並在網址參數中新增了 moonrise,moonset
    url = "https://api.open-meteo.com/v1/forecast?latitude=24.6295226&longitude=121.7919422&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,moonrise,moonset,precipitation_probability_max,wind_speed_10m_max&timezone=Asia%2FTaipei"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        daily = data['daily']
        temp_max = daily['temperature_2m_max'][0]
        temp_min = daily['temperature_2m_min'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        wind_speed = daily['wind_speed_10m_max'][0]
        
        # 處理時間格式 (擷取 T 後面的時間字串)
        def format_time(t_list):
            return t_list[0].split("T")[1] if t_list and t_list[0] else "無"

        sunrise = format_time(daily.get('sunrise'))
        sunset = format_time(daily.get('sunset'))
        moonrise = format_time(daily.get('moonrise'))
        moonset = format_time(daily.get('moonset'))
        
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
            f"🌤️ 今日天氣預報 (台北)：\n"
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

        api_url = "https://api.line.me/v2/bot/message/push"
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
            print("進階天氣預報發送成功！")
        else:
            print(f"發送失敗，錯誤碼: {res.status_code}")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    check_weather_and_notify()
