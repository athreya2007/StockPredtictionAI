import feedparser
import requests
from datetime import datetime

def get_stock_news(company_name: str, max_items: int = 5) -> list[dict]:
    """
    Fetch latest news for a company using Google News RSS.
    Completely free, no API key needed.
    company_name: e.g. 'Reliance Industries', 'TCS', 'HDFC Bank'
    """
    query = f"{company_name} NSE stock".replace(" ", "+")
    url   = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        feed = feedparser.parse(url)
        news = []
        for entry in feed.entries[:max_items]:
            news.append({
                "title":     entry.get("title", ""),
                "published": entry.get("published", ""),
                "source":    entry.get("source", {}).get("title", "Unknown"),
                "link":      entry.get("link", ""),
                "summary":   entry.get("summary", "")[:200],
            })
        return news
    except Exception as e:
        print(f"[news] failed for {company_name}: {e}")
        return []

def get_market_news(max_items: int = 10) -> list[dict]:
    """
    Fetch general Indian stock market news.
    """
    url = "https://news.google.com/rss/search?q=NSE+BSE+India+stock+market&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        feed = feedparser.parse(url)
        return [
            {
                "title":     e.get("title", ""),
                "published": e.get("published", ""),
                "source":    e.get("source", {}).get("title", "Unknown"),
            }
            for e in feed.entries[:max_items]
        ]
    except Exception as e:
        print(f"[news] market news failed: {e}")
        return []

def format_headlines(news_list: list[dict]) -> str:
    """
    Converts news list into a clean string for the LLM to read.
    """
    if not news_list:
        return "No recent news found."
    lines = []
    for i, item in enumerate(news_list, 1):
        lines.append(f"{i}. [{item.get('source','?')}] {item.get('title','')}")
        lines.append(f"   Published: {item.get('published','')}")
    return "\n".join(lines)


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Reliance News ===")
    news = get_stock_news("Reliance Industries", max_items=3)
    print(format_headlines(news))

    print("\n=== Market News ===")
    market = get_market_news(max_items=3)
    print(format_headlines(market))