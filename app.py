import streamlit as st

st.set_page_config(
    page_title="Stock Prediction AI",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Stock Prediction AI")
st.subheader("AI-powered NSE/BSE trading signals")

st.markdown("""
### What this app does
- 🔍 **Screener** — scans your entire watchlist every morning
- 🤖 **Analyzer** — deep AI analysis on any NSE stock
- 📊 **Chart** — live price chart with technical indicators
- 📋 **History** — track all past signals and their accuracy

### How to use
1. Go to **Screener** to see today's top candidates
2. Pick a BUY candidate and run it through **Analyzer**
3. View the **Chart** to confirm visually
4. Check **History** to track signal accuracy over time

---
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Watchlist Size", "10 stocks")
with col2:
    st.metric("Min Risk/Reward", "1:2")
with col3:
    st.metric("Max Risk Per Trade", "2%")

st.info("👈 Use the sidebar to navigate between pages")