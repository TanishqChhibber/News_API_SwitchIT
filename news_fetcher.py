import feedparser
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache
from urllib.parse import urljoin
import traceback

# Cache setup
cache = TTLCache(maxsize=100, ttl=600)

# RSS Feed Sources (example)
FEEDS = {
    "tech": [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://thenextweb.com/feed/",
    ],
    "startup": [
        "https://inc42.com/feed/",
        "https://yourstory.com/feed",
    ],
    "ai": [
        "https://spectrum.ieee.org/rss/topic/artificial-intelligence",
        "https://www.analyticsvidhya.com/blog/category/artificial-intelligence/feed/",
    ],
    "news": [
        "https://www.hindustantimes.com/rss/topnews/rssfeed.xml",
    ],
    "business": [
        "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
        "https://economictimes.indiatimes.com/industry/banking/finance/rssfeeds/13358259.cms",
        "https://cfo.economictimes.indiatimes.com/rss/corporate-finance/rssfeeds/13358259.cms",
    ],
}

# Utility functions for cleaning and extracting data
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return soup.get_text(separator="\n", strip=True)

def extract_images(html: str, base_url: str = "") -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            if not src.startswith(("http://", "https://")):
                src = urljoin(base_url, src)
            images.append(src)
    return images

def extract_thumbnail_from_summary(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    img_tag = soup.find("img")
    return img_tag.get("src") if img_tag else None

def truncate(text: str, max_length: int = 250) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text

@cached(cache)
def fetch_news(feed_url: str) -> list[dict]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        response = requests.get(feed_url, headers=headers, timeout=10)

        # Log the response status and headers for debugging
        print(f"Fetching {feed_url} with status code {response.status_code}")
        if response.status_code != 200:
            print(f"⚠️ Error: Received status {response.status_code} for {feed_url}")
            return []

        # Parse the feed
        feed = feedparser.parse(response.content)

        # Check if feed is bozo (malformed)
        if feed.bozo:
            print(f"⚠️ Feed parsing error: {feed.bozo_exception}")
            return []

    except Exception as e:
        print(f"⚠️ Error fetching/parsing feed: {feed_url} -> {e}")
        traceback.print_exc()
        return []

    # Process the news items
    news_items = []
    for entry in feed.entries:
        try:
            summary_raw = entry.get("summary", entry.get("description", ""))
            clean_summary = truncate(clean_html(summary_raw))
            thumbnail = extract_thumbnail_from_summary(summary_raw)

            news_items.append({
                "title": entry.get("title", "No Title"),
                "summary": clean_summary,
                "link": entry.get("link", "#"),
                "thumbnail": thumbnail,
                "published": entry.get("published", entry.get("updated", "")),
            })
        except Exception as e:
            print(f"⚠️ Error parsing entry: {e}")
            continue

    return news_items

# Fetch and process news for a category
def fetch_news_for_category(category: str) -> list[dict]:
    feed_urls = FEEDS.get(category)
    if not feed_urls:
        print(f"[WARN] Invalid category: {category}")
        return []

    all_articles = []
    for url in feed_urls:
        all_articles.extend(fetch_news(url))

    # Optional: Sort and limit articles
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_articles[:30]  # return top 30

# Example of usage
if __name__ == "__main__":
    category = "business"  # Change this as needed
    articles = fetch_news_for_category(category)
    if articles:
        for article in articles:
            print(f"Title: {article['title']}\nLink: {article['link']}\nSummary: {article['summary']}\n")
    else:
        print(f"No articles found for category: {category}")
