import streamlit as st
from agent.core import analyze_stock
from watchlist import WATCHLIST, get_company_name

st.set_page_config(page_title="Analyzer", page_icon="🤖", layout="wide")
st.title("🤖 AI Stock Analyzer")
st.caption("Deep LLM analysis with technical + sentiment + risk")

ticker = st.selectbox(
    "Select stock",
    options=WATCHLIST,
    format_func=lambda t: f"{t} — {get_company_name(t)}"
)

if st.button("🔍 Analyze", type="primary"):
    company = get_company_name(ticker)
    with st.spinner(f"Analyzing {ticker}... (30-60 seconds)"):
        try:
            output = analyze_stock(ticker, company)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    # parse signal line
    lines = output.strip().split("\n")
    signal_line = next((l for l in lines if l.startswith("SIGNAL:")), "")
    signal = signal_line.replace("SIGNAL:", "").strip()

    # color the signal
    color = {"BUY": "green", "AVOID": "red", "WAIT": "orange"}.get(signal, "gray")
    st.markdown(f"## Signal: :{color}[{signal}]")

    st.divider()

    # show full output in a clean box
    st.code(output, language=None)