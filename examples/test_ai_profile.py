"""测试 AI 交易者画像分析功能"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import init_db, close_db, AsyncSessionLocal
from src.profiler.ai_analyzer import TraderAIProfiler
from src.profiler.analyzer import TraderProfiler


async def test_single_trader_analysis():
    """测试单个交易者 AI 分析"""
    print("=== 测试单个交易者 AI 分析 ===\n")

    await init_db()

    try:
        # 先获取一个有交易记录的地址
        profiler = TraderProfiler(AsyncSessionLocal)

        async with AsyncSessionLocal() as session:
            leaderboard = await profiler.get_leaderboard(
                session=session,
                limit=1,
                min_trades=5
            )

            if not leaderboard:
                print("❌ 没有找到符合条件的交易者（至少 5 笔交易）")
                print("请先运行: python -m src.main refresh-profiles")
                return

            test_address = leaderboard[0]["address"]
            print(f"测试地址: {test_address}")
            print(f"基础数据: 胜率 {leaderboard[0]['win_rate']:.1f}%, "
                  f"交易量 ${leaderboard[0]['total_volume']:,.2f}\n")

        # 运行 AI 分析
        ai_profiler = TraderAIProfiler(AsyncSessionLocal)

        async with AsyncSessionLocal() as session:
            print("🤖 正在调用 AI 分析...")
            result = await ai_profiler.analyze_trader(
                session=session,
                address=test_address,
                force_refresh=True
            )

            if result:
                print("\n✅ AI 分析完成!\n")
                print(f"标签: {result.get('label')}")
                print(f"交易风格: {result.get('trading_style')}")
                print(f"风险偏好: {result.get('risk_preference')}")
                print(f"\n深度分析:")
                print("-" * 60)
                print(result.get('ai_analysis'))
                print("-" * 60)
            else:
                print("\n❌ AI 分析失败")

    finally:
        await close_db()


async def test_batch_analysis():
    """测试批量 AI 分析"""
    print("\n=== 测试批量 AI 分析 ===\n")

    await init_db()

    try:
        ai_profiler = TraderAIProfiler(AsyncSessionLocal)

        print("🤖 批量分析前 5 个交易者...")
        results = await ai_profiler.batch_analyze(
            limit=5,
            min_trades=5,
            force_refresh=False
        )

        print(f"\n✅ 完成分析: {len(results)} 个交易者\n")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['address'][:16]}...")
            print(f"   标签: {result.get('label', 'N/A')}")
            print(f"   风格: {result.get('trading_style', 'N/A')}")
            print(f"   缓存: {'是' if result.get('cached') else '否'}")

    finally:
        await close_db()


async def test_ai_leaderboard():
    """测试 AI 排行榜"""
    print("\n=== 测试 AI 排行榜 ===\n")

    await init_db()

    try:
        ai_profiler = TraderAIProfiler(AsyncSessionLocal)

        async with AsyncSessionLocal() as session:
            leaderboard = await ai_profiler.get_top_traders_with_ai(
                session=session,
                limit=10
            )

            if not leaderboard:
                print("❌ 没有找到已分析的交易者")
                print("请先运行: python -m src.main ai-profile")
                return

            print(f"📊 Top {len(leaderboard)} AI 分析交易者:\n")

            for i, trader in enumerate(leaderboard, 1):
                print(f"{i}. {trader['address'][:16]}...")
                print(f"   {trader['label']}")
                print(f"   风格: {trader['trading_style']} | "
                      f"风险: {trader['risk_preference']} | "
                      f"胜率: {trader['win_rate']:.1f}%")
                print()

    finally:
        await close_db()


async def main():
    """主测试流程"""
    print("╔════════════════════════════════════════╗")
    print("║   AI 交易者画像分析功能测试            ║")
    print("╚════════════════════════════════════════╝\n")

    # Windows 平台修复
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        # 测试 1: 单个交易者分析
        await test_single_trader_analysis()

        # 测试 2: 批量分析
        await test_batch_analysis()

        # 测试 3: AI 排行榜
        await test_ai_leaderboard()

        print("\n" + "="*60)
        print("✅ 所有测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
