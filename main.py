from storage.db import init_db
from tools.screener import run_screener, print_screener_report
from agent.core import analyze_stock
from watchlist import WATCHLIST, get_company_name

def run_morning_scan():
    """
    Full morning routine:
    1. Screen entire watchlist for technical signals
    2. Run deep agent analysis on top BUY candidates
    3. Print final recommendations
    """
    print("="*60)
    print("   STOCK PREDICTION AI — MORNING SCAN")
    print("="*60)

    # Step 1 — init DB
    init_db()

    # Step 2 — screen all stocks
    print("\n📊 STEP 1: Screening watchlist...\n")
    results = run_screener(WATCHLIST)
    print_screener_report(results)

    # Step 3 — deep agent analysis on BUY candidates only
    buy_candidates = [r for r in results if r.get("recommendation") == "BUY"]

    if not buy_candidates:
        print("\n⚠️  No BUY candidates found today. Market may be bearish.")
        print("    Check WAIT candidates manually or wait for better setup.\n")
        return

    print(f"\n🤖 STEP 2: Deep agent analysis on {len(buy_candidates)} BUY candidate(s)...\n")

    for candidate in buy_candidates[:3]:  # max 3 deep analyses per run
        ticker = candidate["ticker"]
        company = get_company_name(ticker)

        print(f"\n{'='*60}")
        print(f"  ANALYZING: {ticker} ({company})")
        print(f"{'='*60}")

        try:
            output = analyze_stock(ticker, company)
            print(output)
        except Exception as e:
            print(f"Agent error for {ticker}: {e}")

    print("\n✅ Morning scan complete.")

def analyze_single(ticker: str):
    """Quick analysis of a single stock."""
    company = get_company_name(ticker)
    print(f"\nAnalyzing {ticker} ({company})...\n")
    output = analyze_stock(ticker, company)
    print(output)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # run single stock: python main.py TCS.NS
        analyze_single(sys.argv[1])
    else:
        # run full morning scan
        run_morning_scan()