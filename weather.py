import os
import requests
import json
import random
import re
import time

# ==========================================
# 1. 金鑰與試算表設定
# ==========================================
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN") or "M5dOcrWbmJCxMX6lDyXJbU5S/h51skZreDIa0gCmhpcchuBlzL2nXkBHU0eAaiPW4CZDHJfzhQ+l5RfGBMN2zr9aq/E55+/QwvFChXbvKF2ycUnbH1VPAcl9Bbd8XAkmkJ1SSgPaL2fGsInptYHRvwdB04t89/1O/w1cDnyilFU="
SPREADSHEET_ID = "1wfEbdMSwV4bUJzgMwnrWpwwrAsWb3cwzZv-qeA27h1w"

TAIWAN_LOCATIONS = {
    "冬山": {"lat": 24.6295, "lon": 121.7919}, "冬山鄉": {"lat": 24.6295, "lon": 121.7919},
    "羅東": {"lat": 24.6770, "lon": 121.7667}, "羅東鎮": {"lat": 24.6770, "lon": 121.7667},
    "宜蘭": {"lat": 24.7570, "lon": 121.7530}, "宜蘭市": {"lat": 24.7570, "lon": 121.7530},
    "礁溪": {"lat": 24.8236, "lon": 121.7718}, "頭城": {"lat": 24.8596, "lon": 121.8232},
    "蘇澳": {"lat": 24.5960, "lon": 121.8517}, "花蓮": {"lat": 23.9872, "lon": 121.6016},
    "吉安": {"lat": 23.9614, "lon": 121.5677}, "玉里": {"lat": 23.3365, "lon": 121.3125},
    "台東": {"lat": 22.7583, "lon": 121.1444}, "台北": {"lat": 25.0330, "lon": 121.5654},
    "新北": {"lat": 25.0116, "lon": 121.4628}, "板橋": {"lat": 25.0116, "lon": 121.4628},
    "基隆": {"lat": 25.1276, "lon": 121.7392}, "桃園": {"lat": 24.9936, "lon": 121.3010},
    "中壢": {"lat": 24.9537, "lon": 121.2257}, "新竹": {"lat": 24.8138, "lon": 120.9675},
    "苗栗": {"lat": 24.5602, "lon": 120.8214}, "台中": {"lat": 24.1477, "lon": 120.6736},
    "彰化": {"lat": 24.0817, "lon": 120.5385}, "南投": {"lat": 23.9099, "lon": 120.6848},
    "雲林": {"lat": 23.7092, "lon": 120.4313}, "嘉義": {"lat": 23.4800, "lon": 120.4491},
    "台南": {"lat": 22.9997, "lon": 120.2270}, "高雄": {"lat": 22.6273, "lon": 120.3014},
    "屏東": {"lat": 22.6761, "lon": 120.4941}
}

WEEKDAY_MAP = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]

def get_geo(name):
    clean = re.sub(r"[市縣鄉鎮區]", "", name)
    if name in TAIWAN_LOCATIONS:
        return TAIWAN_LOCATIONS[name]
    if clean in TAIWAN_LOCATIONS:
        return TAIWAN_LOCATIONS[clean]
    return {"lat": 24.6295, "lon": 121.7919}

# ==========================================
# 2. 讀取 Google 試算表（群組名單與笑話庫）
# ==========================================
def fetch_gviz_table(sheet_name=""):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json"
    if sheet_name:
        url += f"&sheet={sheet_name}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    match = re.search(r"google\.visualization\.Query\.setResponse\((.*)\);", res.text)
    if not match:
        return []
    
    data = json.loads(match.group(1))
    rows = data.get("table", {}).get("rows", [])
    return rows

def get_group_targets():
    targets = []
    try:
        rows = fetch_gviz_table(sheet_name="工作表1")
        for row in rows:
            c = row.get("c", [])
            if not c or not c[0]:
                continue
            gid = str(c[0].get("v", "")).strip()
            if not gid or gid == "groupId":
                continue
            loc = str(c[1].get("v", "冬山")).strip() if len(c) > 1 and c[1] else "冬山"
            targets.append({"groupId": gid, "locationName": loc})
    except Exception as e:
        print(f"讀取群組名單出錯: {e}")
    return targets

def get_random_joke():
    try:
        rows = fetch_gviz_table(sheet_name="笑話庫")
        jokes = []
        for row in rows:
            c = row.get("c", [])
            if c and c[0] and c[0].get("v"):
                text = str(c[0].get("v")).strip()
                if text and text != "笑話內容（GAS 機器人隨機抽取欄位）":
                    jokes.append(text)
        if jokes:
            return random.choice(jokes)
    except Exception as e:
        print(f"讀取笑話庫出錯: {e}")
    return "哪一種水果最容易迷路？\n答案：藍莓（因為「藍莓」方向感）。"

# ==========================================
# 3. 獲取週一~週日 7 天完整氣象預報 (氣溫/降雨/風速/UV/AQI)
# ==========================================
def get_uv_desc(uv):
    if uv < 3: return f"{uv:.1f}(低量)"
    elif uv < 6: return f"{uv:.1f}(中量)"
    elif uv < 8: return f"{uv:.1f}(高量)"
    elif uv < 11: return f"{uv:.1f}(過量)"
    return f"{uv:.1f}(危險)"

def get_aqi_desc(aqi):
    if aqi <= 50: return f"{aqi}(良好 🟢)"
    elif aqi <= 100: return f"{aqi}(普通 🟡)"
    elif aqi <= 150: return f"{aqi}(對敏感族不健康 🟠)"
    return f"{aqi}(不健康 🔴)"

def generate_weekly_comprehensive_report(location_name):
    geo = get_geo(location_name)
    lat, lon = geo["lat"], geo["lon"]
    
    # 1. 抓取 Open-Meteo 逐日天氣（氣溫、降雨機率、風速、紫外線指數）
    daily_data = {}
    try:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&daily="
            f"temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max,uv_index_max"
            f"&timezone=Asia%2FTaipei"
        )
        res = requests.get(weather_url, timeout=20)
        if res.status_code == 200:
            daily_data = res.json().get("daily", {})
    except Exception as e:
        print(f"天氣 API 連線失敗: {e}")

    # 2. 抓取 Open-Meteo 空氣品質 (AQI)
    aqi_data = []
    try:
        aqi_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={lat}&longitude={lon}&daily=us_aqi_max&timezone=Asia%2FTaipei"
        )
        res_aqi = requests.get(aqi_url, timeout=15)
        if res_aqi.status_code == 200:
            aqi_data = res_aqi.json().get("daily", {}).get("us_aqi_max", [])
    except Exception as e:
        print(f"空氣品質 API 連線失敗: {e}")

    # 3. 組裝週一至週日逐日卡片
    days_text = []
    dates = daily_data.get("time", [])
    min_temps = daily_data.get("temperature_2m_min", [])
    max_temps = daily_data.get("temperature_2m_max", [])
    rain_probs = daily_data.get("precipitation_probability_max", [])
    winds = daily_data.get("wind_speed_10m_max", [])
    uvs = daily_data.get("uv_index_max", [])

    for i in range(min(7, len(dates))):
        d_str = dates[i][5:] # MM-DD
        min_t = min_temps[i] if i < len(min_temps) else "--"
        max_t = max_temps[i] if i < len(max_temps) else "--"
        rain = rain_probs[i] if i < len(rain_probs) else 0
        wind = winds[i] if i < len(winds) else "--"
        uv_val = uvs[i] if i < len(uvs) else 0.0
        uv_text = get_uv_desc(uv_val)
        
        aqi_val = aqi_data[i] if i < len(aqi_data) else 45
        aqi_text = get_aqi_desc(int(aqi_val))

        weekday_name = WEEKDAY_MAP[i]

        day_block = (
            f"📌 【{weekday_name}】{d_str}\n"
            f"🌡️ 氣溫：{min_t}°C ~ {max_t}°C\n"
            f"💧 降雨機率：{rain}%\n"
            f"💨 風速：{wind} km/h\n"
            f"☀️ 紫外線：{uv_text}\n"
            f"🍃 空氣品質：{aqi_text}"
        )
        days_text.append(day_block)

    forecast_content = "\n\n".join(days_text) if days_text else "暫時無法取得完整一週預報。"
    joke = get_random_joke()

    return (
        f"📅【本週一週氣象趨勢】({location_name})\n"
        f"包含週一至週日氣溫、降雨、風速、紫外線與空氣品質：\n"
        f"---------------------------------\n\n"
        f"{forecast_content}\n\n"
        f"---------------------------------\n"
        f"💡 每日出門前如需當天精準鄉鎮預報與穿搭建議，請在群組輸入「即時預報」！\n\n"
        f"🎭 本週一笑：\n{joke}"
    )

# ==========================================
# 4. 推播主程式（帶防 429 緩衝）
# ==========================================
def send_line_push(to, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    payload = {"to": to, "messages": [{"type": "text", "text": text}]}
    res = requests.post(url, headers=headers, json=payload, timeout=15)
    return res.status_code

def main():
    targets = get_group_targets()
    if not targets:
        print("未找到任何訂閱群組。")
        return

    print(f"開始執行週一推播，共 {len(targets)} 個群組/目標")
    for t in targets:
        gid = t["groupId"]
        loc = t["locationName"]
        
        msg = generate_weekly_comprehensive_report(loc)
        code = send_line_push(gid, msg)
        print(f"推播給 [{loc}] ({gid}) -> HTTP {code}")
        time.sleep(2) # 間隔防 429

if __name__ == "__main__":
    main()
