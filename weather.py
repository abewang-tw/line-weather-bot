import os
import requests

def get_group_targets(gas_url):
    """向 GAS 讀取所有登記群組與其自選地區經緯度（支援 Google 302 轉址）"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(gas_url, headers=headers, allow_redirects=True, timeout=15)
        print(f"📡 GAS 回傳狀態碼: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"📡 GAS 回傳資料: {data}")
            return data
        else:
            print(f"⚠️ 無法取得群組清單，GAS 狀態碼: {res.status_code}，回應: {res.text[:200]}")
    except Exception as e:
        print(f"⚠️ 連線 GAS 取得名單失敗: {e}")
    return []

def fetch_weather_report(location_name, lat, lon):
    """依據經緯度抓取該地區天氣與天文數據並組裝訊息"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily="
        f"temperature_2m_max,temperature_2m_min,sunrise,sunset,moonrise,moonset,"
        f"precipitation_probability_max,wind_speed_10m_max&timezone=Asia%2FTaipei"
    )
    
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f"❌ Open-Meteo 狀態碼異常: {res.status_code}")
            return None
            
        data = res.json()
        daily = data.get("daily", {})
        
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        rain_prob = daily["precipitation_probability_max"][0]
        wind_speed = daily["wind_speed_10m_max"][0]
        
        def format_time(t_list):
            return t_list[0].split("T")[1] if t_list and t_list[0] else "無"

        sunrise = format_time(daily.get("sunrise"))
        sunset = format_time(daily.get("sunset"))
        moonrise = format_time(daily.get("moonrise"))
        moonset = format_time(daily.get("moonset"))
        
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
            f"🌤️ 今日天氣預報 ({location_name})：\n"
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
        return message
    except Exception as e:
        print(f"抓取天氣資料失敗: {e}")
        return None

def main():
    access_token = os.environ.get("LINE_ACCESS_TOKEN", "").strip()
    gas_url = os.environ.get("GAS_WEBHOOK_URL", "").strip()
    fallback_user_id = os.environ.get("LINE_USER_ID", "").strip()

    if not access_token:
        print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN！")
        return

    targets = []
    if gas_url:
        print("📡 正在向 GAS 抓取訂閱群組清單...")
        targets = get_group_targets(gas_url)

    # 若 GAS 未設定或回傳空名單，使用 fallback 預設推播
    if not targets and fallback_user_id:
        print("ℹ️ 使用預設 LINE_USER_ID 進行推播（冬山地區）")
        targets = [{
            "groupId": fallback_user_id,
            "locationName": "冬山",
            "lat": 24.6295226,
            "lon": 121.7919422
        }]

    if not targets:
        print("⚠️ 無推播目標群組，程序結束。")
        return

    print(f"📋 共取得 {len(targets)} 個推播目標，開始發送...")

    line_push_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    for item in targets:
        group_id = item.get("groupId")
        loc_name = item.get("locationName", "冬山")
        lat = item.get("lat", 24.6295)
        lon = item.get("lon", 121.7919)

        if not group_id:
            continue

        try:
            report_msg = fetch_weather_report(loc_name, lat, lon)
            if not report_msg:
                print(f"❌ 抓取【{loc_name}】天氣失敗，略過此群組。")
                continue

            payload = {
                "to": group_id,
                "messages": [{"type": "text", "text": report_msg}]
            }
            res = requests.post(line_push_url, headers=headers, json=payload, timeout=10)
            
            if res.status_code == 200:
                print(f"🎉 成功推播【{loc_name}】至群組 {group_id[:6]}***")
            else:
                print(f"❌ 推播至 {group_id[:6]}*** 失敗: {res.status_code}, 原因: {res.text}")
        except Exception as e:
            print(f"💥 處理群組 {group_id[:6]}*** 時發生例外: {e}")

if __name__ == "__main__":
    main()
