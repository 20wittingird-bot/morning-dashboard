"""GitHub Issue(label: schedule-anime)の本文から、毎週繰り返す放送スケジュールを
一括登録する。

本文の書式(1行に1作品、複数行可):

    アニメA 月曜 23:00
    アニメB 火曜 26:00

「26:00」のような深夜表記(=翌日午前2:00)にも対応。
同じ作品・同じ曜日の行が既にある場合は、時刻を上書きする。
"""
import json
import os
import re

WEEKDAY_MAP = {"月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5, "日": 6}

LINE_RE = re.compile(
    r"^(?P<title>.+?)\s+(?P<weekday>[月火水木金土日])(?:曜日?)?\s+(?P<time>\d{1,2}[:：]\d{2})\s*$"
)


def parse_body(body: str):
    entries = []
    errors = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if not m:
            errors.append(line)
            continue
        title = m.group("title").strip()
        weekday = WEEKDAY_MAP[m.group("weekday")]
        time_label = m.group("time").replace("：", ":")
        entries.append({"title": title, "weekday": weekday, "time_label": time_label})
    return entries, errors


def main():
    body = os.environ.get("ISSUE_BODY", "")
    entries, errors = parse_body(body)

    if not entries:
        raise SystemExit(
            "登録できる行が見つかりませんでした。"
            "「作品名 曜日 時刻」の形式で入力してください(例: アニメA 月曜 23:00)"
        )

    with open("data/anime_schedule.json", encoding="utf-8") as f:
        schedule = json.load(f)

    items = schedule.setdefault("items", [])
    index = {(it["title"], it["weekday"]): i for i, it in enumerate(items)}

    added, updated = 0, 0
    for entry in entries:
        key = (entry["title"], entry["weekday"])
        if key in index:
            items[index[key]]["time_label"] = entry["time_label"]
            updated += 1
        else:
            items.append(entry)
            index[key] = len(items) - 1
            added += 1

    with open("data/anime_schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)

    print(f"added {added}, updated {updated}, skipped {len(errors)} unparsable line(s): {errors}")


if __name__ == "__main__":
    main()
