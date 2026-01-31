"""Insider Hunter - Polymarket 内幕猎手主入口"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db, close_db, AsyncSessionLocal
from .api.routes import router
from .indexer.discovery import MarketDiscovery
from .indexer.listener import TradeListener
from .indexer.backfill import HistoryBackfill
from .indexer.fast_backfill import FastBackfill
from .profiler.analyzer import TraderProfiler
from .agent.insider import InsiderAnalyzer

settings = get_settings()

# 全局服务实例
listener: TradeListener = None
discovery: MarketDiscovery = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global listener, discovery

    # 启动时
    print("🚀 Insider Hunter 启动中...")

    # 初始化数据库
    await init_db()
    print("✓ 数据库初始化完成")

    # 初始化市场发现服务
    discovery = MarketDiscovery()

    # 同步市场数据
    try:
        markets = await discovery.fetch_all_active_markets(limit=200)
        async with AsyncSessionLocal() as session:
            count = await discovery.sync_markets_to_db(session, markets)
            print(f"✓ 同步了 {count} 个新市场，共 {len(markets)} 个活跃市场")
    except Exception as e:
        print(f"⚠ 市场同步失败: {e}")

    # 初始化链上监听器
    listener = TradeListener(AsyncSessionLocal)

    # 在后台启动监听器
    asyncio.create_task(listener.start())
    print("✓ 链上监听器已启动")

    print("✓ Insider Hunter 启动完成!")
    print(f"  API 地址: http://localhost:8000")
    print(f"  文档地址: http://localhost:8000/docs")

    yield

    # 关闭时
    print("🛑 Insider Hunter 关闭中...")

    if listener:
        await listener.stop()

    if discovery:
        await discovery.close()

    await close_db()
    print("✓ 已安全关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Insider Hunter",
    description="Polymarket 政治突发事件内幕猎手 - 链上大单监控与内幕分析系统",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Insider Hunter",
        "description": "Polymarket 政治突发事件内幕猎手",
        "version": "1.0.0",
        "docs": "/docs",
    }


# CLI 入口点
def run_server():
    """运行 API 服务器"""
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


async def run_profiler_refresh():
    """运行交易者画像刷新"""
    await init_db()
    profiler = TraderProfiler(AsyncSessionLocal)
    await profiler.refresh_all_profiles()
    await close_db()


async def run_insider_scan():
    """运行内幕分析扫描"""
    await init_db()
    analyzer = InsiderAnalyzer(AsyncSessionLocal)
    await analyzer.scan_pending_trades(limit=10)
    await close_db()


async def run_history_backfill(months: int = 6):
    """运行历史数据回填"""
    backfill = HistoryBackfill()
    await backfill.backfill(months=months)


async def run_sync_markets():
    """同步市场数据"""
    await init_db()
    discovery = MarketDiscovery()
    try:
        markets = await discovery.fetch_all_active_markets(limit=200)
        print(f"[*] 从 Gamma API 获取了 {len(markets)} 个市场")

        # 打印前几个市场的 token ID 用于验证
        for m in markets[:3]:
            print(f"  - {m['slug']}")
            print(f"    YES: {m['yes_token_id'][:30]}...")
            print(f"    NO:  {m['no_token_id'][:30]}...")

        async with AsyncSessionLocal() as session:
            count = await discovery.sync_markets_to_db(session, markets)
            print(f"[OK] 同步了 {count} 个新市场到数据库")
    finally:
        await discovery.close()
        await close_db()


async def run_fast_backfill(total: int = 10000):
    """运行快速回填 (使用 Polymarket Data API)"""
    backfill = FastBackfill()
    await backfill.backfill(total_trades=total)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "serve":
            run_server()
        elif command == "refresh-profiles":
            asyncio.run(run_profiler_refresh())
        elif command == "scan-insider":
            asyncio.run(run_insider_scan())
        elif command == "backfill":
            # 支持指定月数: python -m src.main backfill 6
            months = 6
            if len(sys.argv) > 2:
                try:
                    months = int(sys.argv[2])
                except ValueError:
                    pass
            print(f"📊 开始回填 {months} 个月的历史数据...")
            asyncio.run(run_history_backfill(months))
        elif command == "sync-markets":
            asyncio.run(run_sync_markets())
        elif command == "fast-backfill":
            # 支持指定数量: python -m src.main fast-backfill 10000
            total = 10000
            if len(sys.argv) > 2:
                try:
                    total = int(sys.argv[2])
                except ValueError:
                    pass
            print(f"⚡ 快速回填 {total} 条交易 (Polymarket Data API)...")
            asyncio.run(run_fast_backfill(total))
        else:
            print(f"未知命令: {command}")
            print("可用命令:")
            print("  serve              - 启动 API 服务")
            print("  sync-markets       - 同步市场数据")
            print("  fast-backfill [数量] - 快速回填交易 (推荐，默认 10000)")
            print("  backfill [月数]     - 链上回填历史数据 (慢)")
            print("  refresh-profiles   - 刷新交易者画像")
            print("  scan-insider       - 执行内幕分析扫描")
    else:
        run_server()
