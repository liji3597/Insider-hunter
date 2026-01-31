"""Quick API test to view AI analysis results"""
import asyncio
import sys

from src.db import init_db, close_db, AsyncSessionLocal
from src.profiler.ai_analyzer import TraderAIProfiler


async def view_ai_results():
    """View AI analysis results"""
    await init_db()

    try:
        ai_profiler = TraderAIProfiler(AsyncSessionLocal)

        async with AsyncSessionLocal() as session:
            # Get top traders with AI analysis
            leaderboard = await ai_profiler.get_top_traders_with_ai(
                session=session,
                limit=5
            )

            print("=" * 80)
            print("AI TRADER ANALYSIS RESULTS")
            print("=" * 80)

            if not leaderboard:
                print("\nNo AI-analyzed traders found.")
                print("Run: py -m src.main ai-profile 10")
                return

            for i, trader in enumerate(leaderboard, 1):
                print(f"\n[{i}] Address: {trader['address']}")
                print(f"    Label: {trader['label']}")
                print(f"    Type: {trader['trader_type']}")
                print(f"    Style: {trader['trading_style']}")
                print(f"    Risk: {trader['risk_preference']}")
                print(f"    Win Rate: {trader['win_rate']:.1f}%")
                print(f"    Total Volume: ${trader['total_volume']:,.2f}")
                print(f"    Trades: {trader['total_trades']}")
                print(f"\n    AI Analysis:")
                print(f"    {trader['ai_analysis'][:200]}...")
                print("-" * 80)

    finally:
        await close_db()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(view_ai_results())
