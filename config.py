import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    else:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

LLM_MODEL = "llama-3.3-70b-versatile"

MARKET_OPEN  = "09:15"
MARKET_CLOSE = "15:30"
TIMEZONE     = "Asia/Kolkata"

DEFAULT_PERIOD   = "60d"
DEFAULT_INTERVAL = "1d"
CACHE_DB_PATH    = "storage/cache.db"

DEFAULT_CAPITAL    = 10000
MAX_RISK_PER_TRADE = 0.02
MIN_RISK_REWARD    = 2.0