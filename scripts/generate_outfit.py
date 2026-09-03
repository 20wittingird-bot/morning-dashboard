"""天気と持ち服リストをもとに、Claude APIで
1) 今日のおすすめコーデ
2) 全アイテムの相性マップ
を生成し、data/outfit.json に書き出す。ANTHROPIC_API_KEY 環境変数が必要。
"""
import json
import os
import re
import urllib.request

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-6"
API_URL = "https://api.anthropic.com/v1/messages"


def call_claude(prompt: str) -> str:
    if not API_KEY:
        raise SystemExit("ANTHROPIC_API_KEY が設定されていません(GitHub Secretsに登録してください)")

    body = json.dumps(
        {
            "model": MODEL,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)

    parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    return "".join(parts)


def extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
    return json.loads(text)


def main():
    with open("data/weather.json", encoding="utf-8") as f:
        weather = json.load(f)
    with open("data/wardrobe.json", encoding="utf-8") as f:
        wardrobe = json.load(f)

    items = wardrobe.get("items", [])
    if not items:
        outfit = {"suggestion": None, "compatibility": {}, "note": "持ち服リストが空です"}
        with open("data/outfit.json", "w", encoding="utf-8") as f:
            json.dump(outfit, f, ensure_ascii=False, indent=2)
        print("wardrobe empty, skipping")
        return

    items_by_category: dict[str, list[str]] = {}
    for it in items:
        items_by_category.setdefault(it["category"], []).append(it["name"])

    prompt = f"""あなたはファッションの専門家です。以下の情報から、今日着るべき服の組み合わせと、
持っている服それぞれについて相性の良い他のアイテムを提案してください。

【今日の天気】
気温: {weather.get('temp_min')}度〜{weather.get('temp_max')}度
天気: {weather.get('weather_text')}

【持っている服(カテゴリ別)】
{json.dumps(items_by_category, ensure_ascii=False, indent=2)}

以下のJSON形式で、JSONのみを出力してください(前置き・説明文・コードブロック記号は一切不要):
{{
  "suggestion": {{
    "items": ["カテゴリ: アイテム名", "..."],
    "reason": "この組み合わせを選んだ理由を1〜2文で"
  }},
  "compatibility": {{
    "アイテム名1": ["相性の良いアイテム名", "..."],
    "アイテム名2": ["...", "..."]
  }}
}}
compatibilityには持っている服の全アイテムについて、色・素材・スタイルの観点から
相性の良い他のアイテムを2〜4個ずつ挙げてください。"""

    raw = call_claude(prompt)
    outfit = extract_json(raw)

    with open("data/outfit.json", "w", encoding="utf-8") as f:
        json.dump(outfit, f, ensure_ascii=False, indent=2)

    print("outfit.json updated")


if __name__ == "__main__":
    main()
