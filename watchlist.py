# Your personal stock watchlist
# Add or remove tickers freely — format: "SYMBOL.NS"

WATCHLIST = [
    # Large cap
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "WIPRO.NS",

    # Mid cap / high momentum
    "TATAMOTORS.NS",
    "ADANIENT.NS",
    "BAJFINANCE.NS",
    "ZOMATO.NS",
]

# Maps ticker → company name (for news search)
COMPANY_NAMES = {
    "RELIANCE.NS":   "Reliance Industries",
    "TCS.NS":        "TCS",
    "INFY.NS":       "Infosys",
    "HDFCBANK.NS":   "HDFC Bank",
    "ICICIBANK.NS":  "ICICI Bank",
    "WIPRO.NS":      "Wipro",
    "TATAMOTORS.NS": "Tata Motors",
    "ADANIENT.NS":   "Adani Enterprises",
    "BAJFINANCE.NS": "Bajaj Finance",
    "ZOMATO.NS":     "Zomato",
}

def get_company_name(ticker: str) -> str:
    return COMPANY_NAMES.get(ticker, ticker.replace(".NS", ""))