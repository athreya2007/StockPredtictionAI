import pandas as pd
import numpy as np
from datetime import timedelta
from data.fetcher import get_historical_ohlcv
from indicators.technical import compute_signals
from tools.risk import calculate_risk
from watchlist import WATCHLIST
import json
from storage.db import get_connection

def init_backtest_table():
    """Create backtest results table in DB."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker        TEXT,
            signal_date   TEXT,
            signal        TEXT,
            entry_price   REAL,
            stop_loss     REAL,
            target1       REAL,
            target2       REAL,
            exit_price    REAL,
            exit_date     TEXT,
            outcome       TEXT,
            pnl_pct       REAL,
            created_at    TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()

def generate_signals_for_date(df_full: pd.DataFrame, 
                               as_of_index: int) -> dict:
    """
    Simulate running indicators on a specific past date.
    Only uses data up to as_of_index — no future data leakage.
    """
    df_slice = df_full.iloc[:as_of_index + 1].copy()
    if len(df_slice) < 30:  # need at least 30 days for indicators
        return {}
    return compute_signals(df_slice)

def check_outcome(df_full: pd.DataFrame,
                  entry_index: int,
                  entry_price: float,
                  stop_loss: float,
                  target1: float,
                  hold_days: int = 5) -> dict:
    """
    Check what happened after signal was generated.
    Looks forward hold_days to see if target or stop was hit.
    """
    future = df_full.iloc[entry_index + 1 : entry_index + 1 + hold_days]

    if future.empty:
        return {"outcome": "unknown", "exit_price": entry_price,
                "exit_date": None, "pnl_pct": 0}

    for date, row in future.iterrows():
        high  = float(row["High"])
        low   = float(row["Low"])
        close = float(row["Close"])

        # stop loss hit first (intraday low touched stop)
        if low <= stop_loss:
            pnl = round((stop_loss - entry_price) / entry_price * 100, 2)
            return {"outcome": "STOP_HIT", "exit_price": stop_loss,
                    "exit_date": str(date.date()), "pnl_pct": pnl}

        # target 1 hit
        if high >= target1:
            pnl = round((target1 - entry_price) / entry_price * 100, 2)
            return {"outcome": "TARGET_HIT", "exit_price": target1,
                    "exit_date": str(date.date()), "pnl_pct": pnl}

    # neither hit — exit at last close
    exit_price = float(future.iloc[-1]["Close"])
    pnl = round((exit_price - entry_price) / entry_price * 100, 2)
    return {"outcome": "EXPIRED", "exit_price": exit_price,
            "exit_date": str(future.index[-1].date()), "pnl_pct": pnl}

def backtest_ticker(ticker: str, period: str = "6mo",
                    step: int = 3) -> list:
    """
    Run full backtest on a single ticker.
    step: only generate signal every N days (reduces computation)
    """
    print(f"  Backtesting {ticker}...")
    df = get_historical_ohlcv(ticker, period=period, interval="1d")
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    results = []
    # start from index 50 (need enough history for indicators)
    for i in range(50, len(df) - 6, step):
        signals = generate_signals_for_date(df, i)
        if not signals or "error" in signals:
            continue

        price = signals["current_price"]
        risk  = calculate_risk(price)

        # count bullish signals
        bullish = sum([
            signals.get("rsi_signal")    == "oversold",
            signals.get("macd_crossover")== "bullish",
            signals.get("ema_trend")     == "bullish",
            signals.get("bb_position")   == "below_lower",
            signals.get("price_vs_vwap") == "above",
            signals.get("obv_trend")     == "accumulation",
        ])

        # only backtest BUY signals (4+ bullish, viable RR)
        if bullish < 4 or not risk["rr_viable"]:
            continue

        signal_date = str(df.index[i].date())
        outcome = check_outcome(df, i, price,
                                risk["stop_loss"], risk["target1"])

        result = {
            "ticker":      ticker,
            "signal_date": signal_date,
            "signal":      "BUY",
            "entry_price": price,
            "stop_loss":   risk["stop_loss"],
            "target1":     risk["target1"],
            "target2":     risk["target2"],
            **outcome
        }
        results.append(result)

    return results

def save_backtest_results(results: list):
    """Save results to DB."""
    conn = get_connection()
    for r in results:
        conn.execute("""
            INSERT INTO backtest_results
            (ticker, signal_date, signal, entry_price, stop_loss,
             target1, target2, exit_price, exit_date, outcome, pnl_pct)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            r["ticker"], r["signal_date"], r["signal"],
            r["entry_price"], r["stop_loss"], r["target1"], r["target2"],
            r["exit_price"], r["exit_date"], r["outcome"], r["pnl_pct"]
        ))
    conn.commit()
    conn.close()

def print_summary(all_results: list):
    """Print backtest performance summary."""
    if not all_results:
        print("No BUY signals generated in this period.")
        return

    df = pd.DataFrame(all_results)
    total       = len(df)
    targets_hit = len(df[df["outcome"] == "TARGET_HIT"])
    stops_hit   = len(df[df["outcome"] == "STOP_HIT"])
    expired     = len(df[df["outcome"] == "EXPIRED"])
    hit_rate    = round(targets_hit / total * 100, 1)
    avg_pnl     = round(df["pnl_pct"].mean(), 2)
    best        = round(df["pnl_pct"].max(), 2)
    worst       = round(df["pnl_pct"].min(), 2)

    print("\n" + "="*55)
    print("  BACKTEST RESULTS — 6 MONTHS")
    print("="*55)
    print(f"  Total BUY signals   : {total}")
    print(f"  Target hit          : {targets_hit} ({hit_rate}%)")
    print(f"  Stop loss hit       : {stops_hit}")
    print(f"  Expired (no hit)    : {expired}")
    print(f"  Average P&L         : {avg_pnl}%")
    print(f"  Best trade          : +{best}%")
    print(f"  Worst trade         : {worst}%")
    print("="*55)

    print("\nPer-ticker breakdown:")
    print(f"{'Ticker':<15} {'Signals':>8} {'Hit Rate':>10} {'Avg P&L':>10}")
    print("-"*45)
    for ticker in df["ticker"].unique():
        t = df[df["ticker"] == ticker]
        h = len(t[t["outcome"] == "TARGET_HIT"])
        r = round(h / len(t) * 100, 1)
        p = round(t["pnl_pct"].mean(), 2)
        print(f"{ticker:<15} {len(t):>8} {str(r)+'%':>10} {str(p)+'%':>10}")

    return df


if __name__ == "__main__":
    print("="*55)
    print("  HISTORICAL BACKTEST — Starting")
    print("="*55)

    init_backtest_table()
    all_results = []

    for ticker in WATCHLIST[:5]:   # start with 5 stocks
        results = backtest_ticker(ticker, period="6mo", step=3)
        all_results.extend(results)
        save_backtest_results(results)
        print(f"  → {len(results)} BUY signals found for {ticker}")

    print_summary(all_results)
    print("\nResults saved to storage/cache.db")
    print("Run pages/5_Backtest.py to view in the UI!")