import yfinance as yf
import pandas as pd
from nsetools import Nse

nse = Nse()

def get_historical_ohlcv(ticker: str, period: str = "60d", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical price data from Yahoo Finance.
    ticker:   NSE format e.g. 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'
    period:   '5d', '1mo', '60d', '6mo', '1y'
    interval: '1d', '1h', '15m', '5m'
    """
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    df.dropna(inplace=True)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

def get_live_quote(symbol: str) -> dict:
    """
    Fetch live NSE quote.
    symbol: WITHOUT .NS suffix e.g. 'RELIANCE', 'TCS', 'INFY'
    """
    try:
        quote = nse.get_quote(symbol.upper())
        return {
            "symbol":       symbol.upper(),
            "last_price":   quote.get("lastPrice"),
            "change_pct":   quote.get("pChange"),
            "day_high":     quote.get("dayHigh"),
            "day_low":      quote.get("dayLow"),
            "volume":       quote.get("totalTradedVolume"),
            "52w_high":     quote.get("high52"),
            "52w_low":      quote.get("low52"),
            "avg_delivery": quote.get("deliveryToTradedQuantity"),
        }
    except Exception as e:
        print(f"[fetcher] live quote failed for {symbol}: {e}")
        return {}

def get_company_info(ticker: str) -> dict:
    """
    Fetch basic company info from Yahoo Finance.
    ticker: NSE format e.g. 'RELIANCE.NS'
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "name":     info.get("longName"),
            "sector":   info.get("sector"),
            "pe_ratio": info.get("trailingPE"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low":  info.get("fiftyTwoWeekLow"),
            "mkt_cap":  info.get("marketCap"),
        }
    except Exception as e:
        print(f"[fetcher] company info failed for {ticker}: {e}")
        return {}

def get_top_gainers() -> list:
    """Returns top gaining stocks on NSE today."""
    try:
        return nse.get_top_gainers()
    except Exception as e:
        print(f"[fetcher] top gainers failed: {e}")
        return []

def get_top_losers() -> list:
    """Returns top losing stocks on NSE today."""
    try:
        return nse.get_top_losers()
    except Exception as e:
        print(f"[fetcher] top losers failed: {e}")
        return []


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing fetcher...\n")

    df = get_historical_ohlcv("RELIANCE.NS", period="5d", interval="1d")
    print("Historical OHLCV (RELIANCE, 5 days):")
    print(df.tail(3))

    print("\nCompany info:")
    print(get_company_info("RELIANCE.NS"))