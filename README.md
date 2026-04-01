# StockPredictionAI 📈

An AI-powered stock trading agent for Indian markets (NSE & BSE) that performs real-time market analysis and suggests trading actions through a conversational interface.

---

## Features

- Real-time stock data fetching using yfinance (NSE & BSE)
- Sentiment analysis on financial news using finBERT
- Agentic reasoning and trading suggestions powered by LangGraph + Groq (LLaMA 3.3-70b)
- Vector memory for context retention using ChromaDB
- Interactive Streamlit web interface

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq API (LLaMA 3.3-70b) |
| Agent Framework | LangGraph |
| Sentiment Analysis | finBERT |
| Market Data | yfinance |
| Vector Store | ChromaDB |
| Frontend | Streamlit |
| Language | Python |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Groq API key

### Installation

```bash
git clone https://github.com/athreya2007/StockPredtictionAI.git
cd StockPredtictionAI
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
streamlit run app.py
```

---

## Usage

1. Enter a stock symbol (e.g. `RELIANCE.NS`, `TCS.NS`)
2. The agent fetches real-time price data and recent news
3. finBERT scores the sentiment of the news
4. LangGraph agent reasons over the data and suggests BUY / SELL / HOLD
5. Results are displayed in the Streamlit interface

---

## Project Structure

```
StockPredictionAI/
├── app.py              # Streamlit frontend
├── agent.py            # LangGraph agent logic
├── tools.py            # yfinance + finBERT tools
├── memory.py           # ChromaDB vector memory
├── requirements.txt
└── .env.example
```

---

## Author

**Athreya** — Python Developer | ML & LLM Integration  
[Fiverr](https://www.fiverr.com/athreya_a) • [GitHub](https://github.com/athreya2007)

---

## License

MIT License
