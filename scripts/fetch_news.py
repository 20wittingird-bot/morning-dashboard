"""NHKの総合ニュースとGoogleニュース検索(キーワード別)を取得し、
合計最大5件に制限して data/news.json に書き出す。
"""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

GENERAL_RSS = "https://www3.nhk.or.jp/rss/news/cat0.xml"
MAX_TOTAL_ITEMS = 5  # 全体の最大件数


def get_element_text(element) -> str:
    if element is None:
        return ""
    text = "".join(element.itertext())
    return text.strip()


def parse_rss(url: str, limit: int = 5):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()

    root = ET.fromstring(raw)
    items = []

    for item in root.findall(".//item")[:limit]:
        title_elem = item.find("title")
        link_elem = item.find("link")

        title = get_element_text(title_elem)
        link = get_element_text(link_elem)

        if title:
            items.append({"title": title, "link": link})

    return items


def main():
    # 1. config.json の読み込み
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    keywords = config.get("news_keywords", [])
    result = {"general": [], "topics": {}}

    total_count = 0

    # 2. 主要ニュース（NHK）を最大2件取得
    try:
        general_items = parse_rss(GENERAL_RSS, limit=2)
        result["general"] = general_items
        total_count += len(general_items)
    except Exception as e:  # noqa: BLE001
        print("[ERROR] general news fetch failed:", e)

    # 3. キーワード設定ニュース（合計で最大5件に達するまで追加）
    for kw in keywords:
        if total_count >= MAX_TOTAL_ITEMS:
            result["topics"][kw] = []
            continue

        # 残りの枠数を計算（キーワード1つあたり最大2件まで）
        remaining_slots = min(2, MAX_TOTAL_ITEMS - total_count)

        params = urllib.parse.urlencode({
            "q": kw,
            "hl": "ja",
            "gl": "JP",
            "ceid": "JP:ja"
        })
        url = f"https://news.google.com/rss/search?{params}"

        try:
            items = parse_rss(url, limit=remaining_slots)
            result["topics"][kw] = items
            total_count += len(items)
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] topic news fetch failed ({kw}):", e)
            result["topics"][kw] = []

    # 4. 取得結果を保存
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"news.json updated (Total: {total_count} items)")


if __name__ == "__main__":
    main()