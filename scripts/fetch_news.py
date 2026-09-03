"""config.json の news_keywords を参照してニュースを取得し、
data/news.json に書き出す。
"""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

GENERAL_RSS = "https://www3.nhk.or.jp/rss/news/cat0.xml"


def get_element_text(element) -> str:
    """要素からテキストを安全に取得"""
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
        )
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
    # 1. config.json からニュースのキーワードを参照する
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    keywords = config.get("news_keywords", [])

    result = {"general": [], "topics": {}}

    # 一般ニュース（NHK）
    try:
        result["general"] = parse_rss(GENERAL_RSS, limit=6)
    except Exception as e:  # noqa: BLE001
        print("general news fetch failed:", e)

    # config.json で指定された各キーワードのニュースを取得
    for kw in keywords:
        params = urllib.parse.urlencode({
            "q": kw,
            "hl": "ja",
            "gl": "JP",
            "ceid": "JP:ja"
        })
        url = f"https://news.google.com/rss/search?{params}"
        
        try:
            result["topics"][kw] = parse_rss(url, limit=4)
        except Exception as e:  # noqa: BLE001
            print(f"topic news fetch failed ({kw}):", e)
            result["topics"][kw] = []

    # 2. 取得した結果を data/news.json に書き出す
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("news.json updated")


if __name__ == "__main__":
    main()