"""GitHub Issue(label: wardrobe-add)の本文から、持ち服を一括登録する。

本文の書式(空行区切りのブロックごとに: 1行目=カテゴリ、2行目以降=アイテム名):

    アウター
    ダウンジャケット
    デニムジャケット

    トップス
    白シャツ
"""
import json
import os


def parse_body(body: str):
    blocks = []
    current: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)

    items = []
    for block in blocks:
        if len(block) < 2:
            continue  # カテゴリ行のみでアイテムが無いブロックは無視
        category = block[0]
        for name in block[1:]:
            items.append({"category": category, "name": name})
    return items


def main():
    body = os.environ.get("ISSUE_BODY", "")
    new_items = parse_body(body)

    if not new_items:
        raise SystemExit(
            "登録するアイテムが見つかりませんでした。"
            "「カテゴリ見出し→アイテム名(改行区切り)」の形式で入力してください。"
        )

    with open("data/wardrobe.json", encoding="utf-8") as f:
        wardrobe = json.load(f)

    items = wardrobe.setdefault("items", [])
    existing = {(it["category"], it["name"]) for it in items}

    added = 0
    for it in new_items:
        key = (it["category"], it["name"])
        if key in existing:
            continue
        items.append(it)
        existing.add(key)
        added += 1

    with open("data/wardrobe.json", "w", encoding="utf-8") as f:
        json.dump(wardrobe, f, ensure_ascii=False, indent=2)

    print(f"added {added} item(s), skipped {len(new_items) - added} duplicate(s)")


if __name__ == "__main__":
    main()
