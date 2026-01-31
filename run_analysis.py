import asyncio
import sys
from src.db import AsyncSessionLocal, init_db
from src.agent.insider import InsiderAnalyzer

async def run_analysis():
    print("正在初始化数据库...")
    await init_db()

    print("正在初始化内幕分析器...")
    analyzer = InsiderAnalyzer(AsyncSessionLocal)

    print(f"使用的 API Base: {analyzer.client.base_url}")
    print(f"使用的模型: {analyzer.model}")

    print("\n开始扫描并分析...")
    try:
        # 直接调用扫描逻辑
        alerts = await analyzer.scan_pending_trades(limit=5)

        print(f"\n分析完成!")
        print(f"成功生成报告数: {len(alerts)}")

        if len(alerts) == 0:
            print("\n警告: 找到了待分析交易但生成报告数为 0，说明 AI 调用过程出错。")
            print("请检查上方是否有 '分析失败' 的报错信息。")

    except Exception as e:
        print(f"\n运行过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Windows 上的 asyncio 策略修复
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_analysis())
