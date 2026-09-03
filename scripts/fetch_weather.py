"""都市名から天気を取得して data/weather.json に書き出す。
Open-Meteo (APIキー不要) のジオコーディングAPI + 予報APIを利用する。
"""
import json
import urllib.parse
import urllib.request

WEATHER_CODE_JA = {
    0: "快晴", 1: "晴れ", 2: "薄曇り", 3: "曇り",
    45: "霧", 48: "霧氷",
    51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
    56: "着氷性の霧雨", 57: "強い着氷性の霧雨",
    61: "弱い雨", 63: "雨", 65: "強い雨",
    66: "着氷性の雨", 67: "強い着氷性の雨",
    71: "弱い雪", 73: "雪", 75: "強い雪",
    77: "霧雪",
    80: "にわか雨", 81: "強いにわか雨", 82: "非常に強いにわか雨",
    85: "にわか雪", 86: "強いにわか雪",
    95: "雷雨", 96: "雷雨(雹あり)", 99: "激しい雷雨(雹あり)",
}


def geocode(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {"name": city, "count": 1, "language": "ja"}
    )
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.load(r)
    results = data.get("results")
    if not results:
        raise SystemExit(f"都市が見つかりませんでした: {city}")
    top = results[0]
    return top["latitude"], top["longitude"], top.get("name", city)


def main():
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    city = config.get("city", "東京")

    lat, lon, resolved_name = geocode(city)

    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
            "timezone": "Asia/Tokyo",
            "forecast_days": 1,
        }
    )
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.load(r)

    daily = data["daily"]
    code = daily["weathercode"][0]
    result = {
        "city": resolved_name,
        "date": daily["time"][0],
        "temp_max": daily["temperature_2m_max"][0],
        "temp_min": daily["temperature_2m_min"][0],
        "weather_code": code,
        "weather_text": WEATHER_CODE_JA.get(code, "不明"),
        "precipitation_probability": (daily.get("precipitation_probability_max") or [None])[0],
    }

    with open("data/weather.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("weather.json updated:", result)


if __name__ == "__main__":
    main()
