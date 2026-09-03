"""天気と持ち服リストをもとに、Gemini APIで
1) 今日のおすすめコーデ
2) 全アイテムの相性マップ
を生成し、data/outfit.json に書き出す。GEMINI_API_KEY 環境変数が必要。
"""
import json
import os
import re
import urllib.error
import urllib.request

API_KEY = os.environ.get("GEMINI_API_KEY")
# モデル名を gemini-2.5-flash または gemini-1.5-flash に指定
MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def call_gemini(prompt: str) -> str:
    if not API_KEY:
        raise SystemExit("GEMINI_API_KEY が設定されていません(GitHub Secretsに登録してください)")

    url = f"{API_URL}?key={API_KEY}"

    body = json.dumps(
        {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            # レスポンスを強制的にJSONフォーマット指定（JSON崩れを防ぎます）
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        raise SystemExit(f"Gemini API Error (HTTP {e.code}): {error_msg}")

    # レスポンス文字列の抽出
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"APIからのレスポンス解析に失敗しました: {data}") from e


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

以下のJSON形式で出力してください:
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

    raw = call_gemini(prompt)
    outfit = extract_json(raw)

    with open("data/outfit.json", "w", encoding="utf-8") as f:
        json.dump(outfit, f, ensure_ascii=False, indent=2)

    print("outfit.json updated")


if __name__ == "__main__":
    main()