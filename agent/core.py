from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from agent.prompts import SYSTEM_PROMPT
from agent.tools_registry import ALL_TOOLS
from config import GROQ_API_KEY, LLM_MODEL

def build_agent():
    """Build and return the LangGraph ReAct agent."""
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=0,
        api_key=GROQ_API_KEY,
    )
    return create_react_agent(llm, ALL_TOOLS)

def analyze_stock(ticker: str, company_name: str) -> str:
    """
    Run the full agent analysis on a stock.
    ticker:       e.g. 'TCS.NS'
    company_name: e.g. 'TCS' (for news search)
    """
    agent = build_agent()

    query = f"""{SYSTEM_PROMPT}

Now analyze {ticker} ({company_name}) for a short-term trade (2-5 days).
Use all three tools in order:
1. get_technical_signals for {ticker}
2. get_news_sentiment for {company_name}
3. get_risk_analysis for {ticker}

Then give your final BUY / AVOID / WAIT recommendation in the exact format specified.
"""
    result = agent.invoke({
        "messages": [HumanMessage(content=query)]
    })

    # extract final message from agent
    return result["messages"][-1].content


# ── quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Running agent on TCS...\n")
    output = analyze_stock("TCS.NS", "TCS")
    print("\n" + "="*60)
    print("FINAL AGENT OUTPUT:")
    print("="*60)
    print(output)