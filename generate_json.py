# generate_json.py
import json
from pathlib import Path
from news_fetcher import fetch_news, FEEDS

def main():
    all_news = {}

    for category, feed_url in FEEDS.items():
        print(f"📡 Fetching {category} news...")
        try:
            news_items = fetch_news(feed_url)
            all_news[category] = news_items
            print(f"✅ Fetched {len(news_items)} items for '{category}'")
        except Exception as e:
            print(f"❌ Failed to fetch '{category}' news: {e}")
            all_news[category] = []

    # Save to JSON
    output_path = Path("data/news_data.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_news, f, indent=4, ensure_ascii=False)

    print(f"\n📝 All news saved to '{output_path.resolve()}'")

if __name__ == "__main__":
    main()
