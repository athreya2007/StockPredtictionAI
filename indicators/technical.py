import pandas as pd
import pandas_ta as ta

def compute_signals(df: pd.DataFrame) -> dict:
    """
    Computes all technical indicators on an OHLCV dataframe.
    Returns a dict of signals the agent can reason about.
    """
    df = df.copy()

    # flatten MultiIndex columns if present
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

    # ── Trend ────────────────────────────────────────────────
    df["ema_9"]  = ta.ema(close, length=9)
    df["ema_21"] = ta.ema(close, length=21)
    df["ema_50"] = ta.ema(close, length=50)

    # ── Momentum ─────────────────────────────────────────────
    df["rsi"] = ta.rsi(close, length=14)

    macd = ta.macd(close)
    df["macd"]        = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"]   = macd["MACDh_12_26_9"]

    # ── Volatility ───────────────────────────────────────────
    bb = ta.bbands(close, length=20)
    bb_cols = bb.columns.tolist()
    upper_col = [c for c in bb_cols if c.startswith("BBU")][0]
    lower_col = [c for c in bb_cols if c.startswith("BBL")][0]
    mid_col   = [c for c in bb_cols if c.startswith("BBM")][0]
    df["bb_upper"] = bb[upper_col]
    df["bb_lower"] = bb[lower_col]
    df["bb_mid"]   = bb[mid_col]

    # ── Volume ───────────────────────────────────────────────
    df["vwap"] = ta.vwap(high, low, close, volume)
    df["obv"]  = ta.obv(close, volume)

    # drop rows where indicators haven't warmed up yet
    df.dropna(inplace=True)

    if df.empty:
        return {"error": "Not enough data to compute indicators"}

    latest = df.iloc[-1]
    prev   = df.iloc[-2]

    # ── Build signal dict ────────────────────────────────────
    signals = {

        # price
        "current_price": round(float(latest["Close"]), 2),

        # RSI
        "rsi": round(float(latest["rsi"]), 2),
        "rsi_signal": (
            "oversold"   if latest["rsi"] < 35 else
            "overbought" if latest["rsi"] > 65 else
            "neutral"
        ),

        # MACD crossover
        "macd_crossover": (
            "bullish" if prev["macd"] < prev["macd_signal"]
                      and latest["macd"] > latest["macd_signal"]
            else "bearish" if prev["macd"] > prev["macd_signal"]
                           and latest["macd"] < latest["macd_signal"]
            else "none"
        ),
        "macd_hist": round(float(latest["macd_hist"]), 4),

        # EMA trend
        "ema_trend": (
            "bullish" if latest["ema_9"] > latest["ema_21"] > latest["ema_50"]
            else "bearish" if latest["ema_9"] < latest["ema_21"] < latest["ema_50"]
            else "mixed"
        ),
        "ema_9":  round(float(latest["ema_9"]),  2),
        "ema_21": round(float(latest["ema_21"]), 2),
        "ema_50": round(float(latest["ema_50"]), 2),

        # Bollinger Bands
        "bb_position": (
            "above_upper" if latest["Close"] > latest["bb_upper"] else
            "below_lower" if latest["Close"] < latest["bb_lower"] else
            "middle"
        ),
        "bb_upper": round(float(latest["bb_upper"]), 2),
        "bb_lower": round(float(latest["bb_lower"]), 2),

        # VWAP
        "price_vs_vwap": "above" if latest["Close"] > latest["vwap"] else "below",
        "vwap": round(float(latest["vwap"]), 2),

        # OBV trend (positive = accumulation, negative = distribution)
        "obv_trend": (
            "accumulation" if latest["obv"] > prev["obv"]
            else "distribution"
        ),
    }

    return signals


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    from data.fetcher import get_historical_ohlcv

    df = get_historical_ohlcv("TCS.NS", period="60d", interval="1d")
    signals = compute_signals(df)

    print("=== TCS Technical Signals ===")
    for key, val in signals.items():
        print(f"  {key:<20} {val}")