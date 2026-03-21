from transformers import pipeline
from data.news import get_stock_news, format_headlines

# load once at module level so it doesn't reload every call
# this downloads the model on first run (~500MB, one time only)
print("[sentiment] Loading finBERT model...")
_sentiment_pipe = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    top_k=None,
)
print("[sentiment] Model ready.")

def analyze_headlines(headlines: list[dict]) -> dict:
    """
    Run finBERT sentiment on a list of news headlines.
    Returns aggregated positive/negative/neutral scores.
    """
    if not headlines:
        return {"overall": "neutral", "positive": 0, "negative": 0, "neutral": 1}

    titles = [h["title"] for h in headlines if h.get("title")]
    if not titles:
        return {"overall": "neutral", "positive": 0, "negative": 0, "neutral": 1}

    scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    for title in titles:
        result = _sentiment_pipe(title[:512])[0]  # finBERT max 512 chars
        for item in result:
            label = item["label"].lower()
            scores[label] = scores.get(label, 0) + item["score"]

    # normalize
    total = sum(scores.values())
    for k in scores:
        scores[k] = round(scores[k] / total, 3)

    # determine overall sentiment
    overall = max(scores, key=scores.get)

    return {
        "overall":  overall,
        "positive": scores["positive"],
        "negative": scores["negative"],
        "neutral":  scores["neutral"],
        "headline_count": len(titles),
    }

def get_stock_sentiment(company_name: str, max_news: int = 5) -> dict:
    """
    Fetch news + run sentiment for a company in one call.
    company_name: e.g. 'Reliance Industries', 'TCS', 'HDFC Bank'
    """
    headlines = get_stock_news(company_name, max_items=max_news)
    sentiment = analyze_headlines(headlines)
    sentiment["headlines"] = format_headlines(headlines)
    return sentiment


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    result = get_stock_sentiment("TCS", max_news=5)

    print(f"\n=== TCS Sentiment ===")
    print(f"  Overall   : {result['overall'].upper()}")
    print(f"  Positive  : {result['positive']}")
    print(f"  Negative  : {result['negative']}")
    print(f"  Neutral   : {result['neutral']}")
    print(f"  Headlines : {result['headline_count']}")
    print(f"\nHeadlines analyzed:")
    print(result["headlines"])