"""GitHub Issue(label: wardrobe-remove)の本文から name を読み取り、
data/wardrobe.json から該当アイテムを削除する。
本文の書式(1行に1アイテムずつ、複数可):

    name: ダウンジャケット
    name: 白シャツ

もしくは単純にアイテム名だけを1行ずつ書いてもよい。
"""
import json
import os
import re


def parse_body(body: str):
    names = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = re.match(r"name\s*[:：]\s*(.+)", line, re.IGNORECASE)
        names.append(m.group(1).strip() if m else line)
    return names


def main():
    body = os.environ.get("ISSUE_BODY", "")
    names = parse_body(body)

    if not names:
        raise SystemExit("削除するアイテム名を1行ずつ入力してください")

    with open("data/wardrobe.json", encoding="utf-8") as f:
        wardrobe = json.load(f)

    items = wardrobe.get("items", [])
    remaining = [it for it in items if it["name"] not in names]
    removed = len(items) - len(remaining)

    wardrobe["items"] = remaining
    with open("data/wardrobe.json", "w", encoding="utf-8") as f:
        json.dump(wardrobe, f, ensure_ascii=False, indent=2)

    print(f"removed {removed} item(s)")


if __name__ == "__main__":
    main()
