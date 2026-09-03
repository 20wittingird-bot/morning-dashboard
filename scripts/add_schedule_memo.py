"""GitHub Issue(label: schedule-memo)の本文を、Issue作成日(JST)のメモとして
data/memos.json に保存する。
"""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tokyo")


def main():
    body = os.environ.get("ISSUE_BODY", "").strip()
    created_at = os.environ.get("ISSUE_CREATED_AT", "")

    if not body:
        raise SystemExit("メモの本文が空です")

    if created_at:
        # GitHubのISO8601形式 (例: 2026-09-03T21:00:00Z) をJSTの日付に変換
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(TZ)
    else:
        dt = datetime.now(TZ)
    date_str = dt.strftime("%Y-%m-%d")

    try:
        with open("data/memos.json", encoding="utf-8") as f:
            memos = json.load(f)
    except FileNotFoundError:
        memos = {}

    memos[date_str] = body

    with open("data/memos.json", "w", encoding="utf-8") as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)

    print(f"memo saved for {date_str}: {body}")


if __name__ == "__main__":
    main()
