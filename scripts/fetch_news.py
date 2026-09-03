"""NHKの総合ニュースRSSとGoogleニュース検索RSS(キーワード別)を取得して
data/news.json に書き出す。APIキーは不要。
"""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

GENERAL_RSS = "https://www3.nhk.or.jp/rss/news/cat0.xml"


def parse_rss(url: str, limit: int = 5):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
    root = ET.fromstring(raw)
    items = []
    for item in root.findall(".//item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title:
            items.append({"title": title, "link": link})
    return items


def main():
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    keywords = config.get("news_keywords", [])

    result = {"general": [], "topics": {}}

    try:
        result["general"] = parse_rss(GENERAL_RSS, limit=6)
    except Exception as e:  # noqa: BLE001
        print("general news fetch failed:", e)

    for kw in keywords:
        query = urllib.parse.quote(kw)
        url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            result["topics"][kw] = parse_rss(url, limit=4)
        except Exception as e:  # noqa: BLE001
            print(f"topic news fetch failed ({kw}):", e)
            result["topics"][kw] = []

    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("news.json updated")


if __name__ == "__main__":
    main()
