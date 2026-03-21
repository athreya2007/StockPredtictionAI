import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
from data.fetcher import get_historical_ohlcv
from watchlist import WATCHLIST, get_company_name

st.set_page_config(page_title="Chart", page_icon="📊", layout="wide")
st.title("📊 Live Price Chart")

col1, col2 = st.columns([2,1])
with col1:
    ticker = st.selectbox("Stock", WATCHLIST,
                          format_func=lambda t: f"{t} — {get_company_name(t)}")
with col2:
    period = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=1)

if st.button("📈 Load Chart", type="primary"):
    with st.spinner("Fetching data..."):
        df = get_historical_ohlcv(ticker, period=period, interval="1d")
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        # compute indicators
        df["ema_9"]  = ta.ema(df["Close"], length=9)
        df["ema_21"] = ta.ema(df["Close"], length=21)
        df["rsi"]    = ta.rsi(df["Close"], length=14)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3], vertical_spacing=0.05)

    # candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"], name="Price"
    ), row=1, col=1)

    # EMAs
    fig.add_trace(go.Scatter(x=df.index, y=df["ema_9"],
                             line=dict(color="orange", width=1),
                             name="EMA 9"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ema_21"],
                             line=dict(color="blue", width=1),
                             name="EMA 21"), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"],
                             line=dict(color="purple", width=1),
                             name="RSI"), row=2, col=1)
    fig.add_hline(y=65, line_dash="dash", line_color="red",   row=2, col=1)
    fig.add_hline(y=35, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(
        title=f"{ticker} — {period}",
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)