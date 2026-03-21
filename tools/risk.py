from config import DEFAULT_CAPITAL, MAX_RISK_PER_TRADE, MIN_RISK_REWARD

def calculate_risk(
    current_price: float,
    stop_loss_pct: float = 0.03,
    target1_pct:   float = 0.06,
    target2_pct:   float = 0.10,
    capital:       float = DEFAULT_CAPITAL,
) -> dict:
    """
    Calculate position sizing, stop-loss and targets.

    stop_loss_pct: how far below entry to place stop (default 3%)
    target1_pct:   first target above entry (default 6%)
    target2_pct:   second target above entry (default 10%)
    capital:       total capital per trade
    """
    stop_loss = round(current_price * (1 - stop_loss_pct), 2)
    target1   = round(current_price * (1 + target1_pct),   2)
    target2   = round(current_price * (1 + target2_pct),   2)

    risk_per_share   = current_price - stop_loss
    reward_per_share = target1 - current_price

    rr_ratio = round(reward_per_share / risk_per_share, 2) if risk_per_share > 0 else 0

    # position sizing: only risk MAX_RISK_PER_TRADE% of capital
    max_loss      = capital * MAX_RISK_PER_TRADE
    shares        = int(max_loss / risk_per_share) if risk_per_share > 0 else 0
    total_invested = round(shares * current_price, 2)

    return {
        "current_price":   current_price,
        "stop_loss":       stop_loss,
        "target1":         target1,
        "target2":         target2,
        "rr_ratio":        rr_ratio,
        "rr_viable":       rr_ratio >= MIN_RISK_REWARD,
        "shares":          shares,
        "total_invested":  total_invested,
        "max_loss":        round(max_loss, 2),
        "potential_gain":  round(shares * reward_per_share, 2),
    }

def format_risk_report(ticker: str, risk: dict) -> str:
    """Clean string output for the LLM to read."""
    viable = "✅ VIABLE" if risk["rr_viable"] else "❌ SKIP (RR too low)"
    return f"""
RISK ANALYSIS — {ticker}
  Current price : ₹{risk['current_price']}
  Stop loss     : ₹{risk['stop_loss']}  ({round((risk['current_price']-risk['stop_loss'])/risk['current_price']*100,1)}% below)
  Target 1      : ₹{risk['target1']}   ({round((risk['target1']-risk['current_price'])/risk['current_price']*100,1)}% above)
  Target 2      : ₹{risk['target2']}   ({round((risk['target2']-risk['current_price'])/risk['current_price']*100,1)}% above)
  Risk/Reward   : 1:{risk['rr_ratio']}  {viable}
  Shares to buy : {risk['shares']} shares  (₹{risk['total_invested']} invested)
  Max loss      : ₹{risk['max_loss']}
  Potential gain: ₹{risk['potential_gain']}
""".strip()


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    from data.fetcher import get_historical_ohlcv
    from indicators.technical import compute_signals

    df      = get_historical_ohlcv("TCS.NS", period="60d")
    signals = compute_signals(df)
    price   = signals["current_price"]

    risk = calculate_risk(price)
    print(format_risk_report("TCS.NS", risk))