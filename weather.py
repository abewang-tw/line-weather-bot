import os
import requests
import json
import random
import re

# ==========================================
# 1. 金鑰與試算表設定
# ==========================================
# 支援環境變數或直接帶入金鑰
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "M5dOcrWbmJCxMX6lDyXJbU5S/h51skZreDIa0gCmhpcchuBlzL2nXkBHU0eAaiPW4CZDHJfzhQ+l5RfGBMN2zr9aq/E55+/QwvFChXbvKF2ycUnbH1VPAcl9Bbd8XAkmkJ1SSgPaL2fGsInptYHRvwdB04t89/1O/w1cDnyilFU=")
CWA_API_KEY = os.environ.get("CWA_API_KEY", "CWA-204D87D0-CB59-4714-BDC3-104663B1FF50")
SPREADSHEET_ID = "1wfEbdMSwV4bUJzgMwnrWpwwrAsWb3cwzZv-qeA27h1w"

# 台灣主要縣市與鄉鎮座標
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

COUNTY_MAPPING = {
    "冬山": "宜蘭縣", "羅東": "宜蘭縣", "宜蘭": "宜蘭縣", "礁溪": "宜蘭縣", "頭城": "宜蘭縣", "蘇澳": "宜蘭縣",
    "花蓮": "花蓮縣", "吉安": "花蓮縣", "玉里": "花蓮縣", "台東": "臺東縣", "臺東": "臺東縣",
    "台北": "臺北市", "臺北": "臺北市", "新北": "新北市", "板橋": "新北市", "基隆": "基隆市",
    "桃園": "桃園市", "中壢": "桃園市", "新竹": "新竹市", "苗栗": "苗栗縣",
    "台中": "臺中市", "臺中": "臺中市", "彰化": "彰化縣", "南投": "南投縣", "雲林": "雲林縣",
    "嘉義": "嘉義市", "台南": "臺南市", "臺南": "臺南市", "高雄": "高雄市", "屏東": "屏東縣"
}

def get_county_name(name):
    for k, v in COUNTY_MAPPING.items():
        if k in name:
            return v
    return name if ("市" in name or "縣" in name) else "宜蘭縣"

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
    res = requests.get(url, headers=headers, timeout=10)
    match = re.search(r"google\.visualization\.Query\.setResponse\((.*)\);", res.text)
    if not match:
        return []
    
    data = json.loads(match.group(1))
    rows = data.get("table", {}).get("rows", [])
    return rows

def get_group_targets():
    """讀取 工作表1 的群組名單與設定地點"""
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
            lat = float(c[2].get("v", 0)) if len(c) > 2 and c[2] else 0.0
            lon = float(c[3].get("v", 0)) if len(c) > 3 and c[3] else 0.0
            
            if lat == 0 or lon == 0:
                geo = get_geo(loc)
                lat, lon = geo["lat"], geo["lon"]
                
            targets.append({"groupId": gid, "locationName": loc, "lat": lat, "lon": lon})
    except Exception as e:
        print(f"讀取群組名單出錯: {e}")
    return targets

def get_random_joke():
    """從試算表 笑話庫 隨機抽取笑話"""
    try:
        rows = fetch_gviz_table(sheet_name="笑話庫")
        jokes = []
        for row in rows:
            c = row.get("c", [])
            if c and c[0] and c[0].get("v"):
                text = str(c[0].get("v")).strip()
                if text and text != "笑話內容":
                    jokes.append(text)
        if jokes:
            return random.choice(jokes)
    except Exception as e:
        print(f"讀取笑話庫出錯: {e}")
    return "哪一種水果最容易迷路？\n答案：藍莓（因為「藍莓」方向感）。"

# ==========================================
# 3. 雙來源氣象組裝（CWA 地理生活預報 + Open-Meteo 風速與日月出落）
# ==========================================
def generate_weather_report(location_name, lat, lon):
    county = get_county_name(location_name)
    
    # 1. 中央氣象署 (CWA) 獲取白天預報、溫度與降雨機率
    wx, pop, min_t, max_t = "晴時多雲", 20, "20", "28"
    try:
        cwa_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWA_API_KEY}&locationName={county}"
        res = requests.get(cwa_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            loc_data = data.get("records", {}).get("location", [])
            if loc_data:
                elements = loc_data[0].get("weatherElement", [])
                for el in elements:
                    name = el.get("elementName")
                    times
