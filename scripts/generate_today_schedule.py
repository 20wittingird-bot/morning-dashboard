"""data/anime_schedule.json(毎週繰り返す放送予定)と data/memos.json(その日限りのメモ)
から、今日(JST)分の表示用データを計算して data/today.json に書き出す。

深夜アニメの「26:00」のような表記は、翌日午前2:00を意味するものとして扱う。
つまり「月曜26:00」は実際には火曜の2:00に放送される、という前提で
「今日の放送か」を判定する(weekdayは月=0〜日=6、Pythonのdate.weekday()に合わせている)。
"""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tokyo")
WEEKDAY_JA = ["月", "火", "水", "木", "金", "土", "日"]


def parse_time_label(label: str):
    """'23:00' や '26:00' のような文字列から (hour, minute) を取り出す"""
    m = re.match(r"\s*(\d{1,2})[:：](\d{2})\s*$", label)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def actual_weekday_and_hour(weekday: int, hour: int, minute: int):
    """24時以降の深夜表記を、実際の曜日・時刻に変換する"""
    if hour >= 24:
        return (weekday + 1) % 7, hour - 24, minute
    return weekday, hour, minute


def main():
    with open("data/anime_schedule.json", encoding="utf-8") as f:
        anime_schedule = json.load(f)
    try:
        with open("data/memos.json", encoding="utf-8") as f:
            memos = json.load(f)
    except FileNotFoundError:
        memos = {}

    now = datetime.now(TZ)
    today_str = now.strftime("%Y-%m-%d")
    today_weekday = now.weekday()  # 月=0 ... 日=6

    items = []
    for entry in anime_schedule.get("items", []):
        parsed = parse_time_label(entry.get("time_label", ""))
        if not parsed:
            continue
        hour, minute = parsed
        a_weekday, a_hour, a_minute = actual_weekday_and_hour(entry["weekday"], hour, minute)
        if a_weekday == today_weekday:
            items.append({
                "sort_key": a_hour * 60 + a_minute,
                "time": entry["time_label"],
                "title": entry["title"],
            })

    items.sort(key=lambda x: x["sort_key"])
    for it in items:
        del it["sort_key"]

    result = {
        "date": today_str,
        "items": items,
        "memo": memos.get(today_str, ""),
    }

    with open("data/today.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"today.json updated ({WEEKDAY_JA[today_weekday]}曜日): {result}")


if __name__ == "__main__":
    main()
