from data.fetcher import get_historical_ohlcv, get_company_info
from indicators.technical import compute_signals
from tools.risk import calculate_risk

# Default watchlist — edit these to your preferred stocks
DEFAULT_WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "WIPRO.NS",
    "TATAMOTORS.NS",
    "ADANIENT.NS",
]

def screen_stock(ticker: str) -> dict:
    """
    Run full technical screen on a single stock.
    Returns a summary dict with signal strength.
    """
    try:
        df      = get_historical_ohlcv(ticker, period="60d", interval="1d")
        signals = compute_signals(df)

        if "error" in signals:
            return {"ticker": ticker, "error": signals["error"]}

        price = signals["current_price"]
        risk  = calculate_risk(price)

        # count how many signals are bullish
        bullish_count = sum([
            signals["rsi_signal"]    == "oversold",
            signals["macd_crossover"]== "bullish",
            signals["ema_trend"]     == "bullish",
            signals["bb_position"]   == "below_lower",
            signals["price_vs_vwap"] == "above",
            signals["obv_trend"]     == "accumulation",
        ])

        # simple scoring: 4+ bullish = BUY candidate
        if bullish_count >= 4 and risk["rr_viable"]:
            recommendation = "BUY"
        elif bullish_count <= 1:
            recommendation = "AVOID"
        else:
            recommendation = "WAIT"

        return {
            "ticker":         ticker,
            "price":          price,
            "recommendation": recommendation,
            "bullish_signals": bullish_count,
            "rsi":            signals["rsi"],
            "rsi_signal":     signals["rsi_signal"],
            "macd_crossover": signals["macd_crossover"],
            "ema_trend":      signals["ema_trend"],
            "rr_ratio":       risk["rr_ratio"],
            "stop_loss":      risk["stop_loss"],
            "target1":        risk["target1"],
            "target2":        risk["target2"],
        }

    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

def run_screener(watchlist: list = DEFAULT_WATCHLIST) -> list:
    """
    Screen all stocks in the watchlist.
    Returns sorted list — BUY candidates first.
    """
    print(f"[screener] Scanning {len(watchlist)} stocks...\n")
    results = []

    for ticker in watchlist:
        print(f"  → {ticker}...", end=" ", flush=True)
        result = screen_stock(ticker)
        results.append(result)
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"{result['recommendation']} ({result['bullish_signals']}/6 signals)")

    # sort: BUY first, then WAIT, then AVOID
    order = {"BUY": 0, "WAIT": 1, "AVOID": 2}
    results.sort(key=lambda x: order.get(x.get("recommendation", "AVOID"), 3))
    return results

def print_screener_report(results: list):
    """Print a clean summary table."""
    print("\n" + "="*65)
    print(f"{'TICKER':<15} {'PRICE':>8} {'REC':>6} {'SIGNALS':>8} {'RSI':>6} {'RR':>5}")
    print("="*65)
    for r in results:
        if "error" in r:
            print(f"{r['ticker']:<15} {'ERROR':>8}")
            continue
        print(
            f"{r['ticker']:<15}"
            f"{r['price']:>8.1f}"
            f"{r['recommendation']:>7}"
            f"{str(r['bullish_signals'])+'/6':>8}"
            f"{r['rsi']:>7.1f}"
            f"{r['rr_ratio']:>5.1f}"
        )
    print("="*65)


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    results = run_screener(DEFAULT_WATCHLIST[:4])  # test with 4 stocks
    print_screener_report(results)