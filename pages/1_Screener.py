import streamlit as st
import pandas as pd
from tools.screener import run_screener, screen_stock
from watchlist import WATCHLIST

st.set_page_config(page_title="Screener", page_icon="🔍", layout="wide")
st.title("🔍 Watchlist Screener")
st.caption("Scans all stocks and ranks by signal strength")

if st.button("🚀 Run Screener", type="primary"):
    with st.spinner("Scanning watchlist..."):
        results = run_screener(WATCHLIST)

    # separate into categories
    buys  = [r for r in results if r.get("recommendation") == "BUY"]
    waits = [r for r in results if r.get("recommendation") == "WAIT"]
    avoids= [r for r in results if r.get("recommendation") == "AVOID"]

    col1, col2, col3 = st.columns(3)
    col1.metric("BUY candidates",  len(buys),   delta=f"{len(buys)} actionable")
    col2.metric("WAIT",            len(waits))
    col3.metric("AVOID",           len(avoids))

    st.divider()

    def color_rec(val):
        colors = {"BUY": "background-color:#1a472a; color:white",
                  "WAIT":"background-color:#3d3000; color:white",
                  "AVOID":"background-color:#4a0000; color:white"}
        return colors.get(val, "")

    df = pd.DataFrame([r for r in results if "error" not in r])
    if not df.empty:
        display_cols = ["ticker","price","recommendation",
                        "bullish_signals","rsi","rsi_signal",
                        "macd_crossover","ema_trend","rr_ratio"]
        df = df[display_cols]
        df.columns = ["Ticker","Price","Signal","Bullish/6",
                      "RSI","RSI Signal","MACD","EMA Trend","RR"]
        st.dataframe(
            df.style.applymap(color_rec, subset=["Signal"]),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("Click **Run Screener** to scan the watchlist")