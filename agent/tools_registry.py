from langchain_core.tools import tool
from data.fetcher import get_historical_ohlcv
from indicators.technical import compute_signals
from tools.risk import calculate_risk, format_risk_report
from tools.sentiment import get_stock_sentiment

@tool
def get_technical_signals(ticker: str) -> str:
    """
    Get technical indicator signals for an NSE stock ticker.
    Input: NSE ticker with .NS suffix e.g. 'TCS.NS', 'RELIANCE.NS'
    Returns: RSI, MACD crossover, EMA trend, Bollinger Band position, VWAP, OBV
    """
    try:
        df      = get_historical_ohlcv(ticker, period="60d", interval="1d")
        signals = compute_signals(df)
        return str(signals)
    except Exception as e:
        return f"Error fetching technical signals for {ticker}: {e}"

@tool
def get_news_sentiment(ticker: str) -> str:
    """
    Get news sentiment for a company.
    Input: company name e.g. 'TCS', 'Reliance Industries', 'HDFC Bank'
    Returns: overall sentiment (positive/negative/neutral) with scores
    """
    try:
        result = get_stock_sentiment(ticker, max_news=5)
        return (
            f"Sentiment: {result['overall'].upper()}\n"
            f"Positive: {result['positive']} | "
            f"Negative: {result['negative']} | "
            f"Neutral: {result['neutral']}\n"
            f"Based on {result['headline_count']} headlines\n\n"
            f"{result['headlines']}"
        )
    except Exception as e:
        return f"Error fetching sentiment for {ticker}: {e}"

@tool
def get_risk_analysis(ticker: str) -> str:
    """
    Get risk analysis including stop-loss, targets and position sizing.
    Input: NSE ticker with .NS suffix e.g. 'TCS.NS'
    Returns: stop-loss, target1, target2, risk/reward ratio, shares to buy
    """
    try:
        df      = get_historical_ohlcv(ticker, period="60d", interval="1d")
        signals = compute_signals(df)
        price   = signals["current_price"]
        risk    = calculate_risk(price)
        return format_risk_report(ticker, risk)
    except Exception as e:
        return f"Error calculating risk for {ticker}: {e}"

# export all tools as a list
ALL_TOOLS = [get_technical_signals, get_news_sentiment, get_risk_analysis]