"""测试查询逻辑"""
import asyncio
from sqlalchemy import select, and_
from src.db import AsyncSessionLocal, init_db
from src.models import Trade, InsiderAlert

async def test():
    await init_db()
    async with AsyncSessionLocal() as session:
        # 测试 1: 直接查询大单
        print("=== 测试1: 查询所有大单 ===")
        result = await session.execute(
            select(Trade).where(Trade.is_whale == True)
        )
        whales = result.scalars().all()
        print(f"大单数量: {len(whales)}")
        for w in whales:
            print(f"  ID={w.id}, market={w.market_slug[:50]}..., amount=${w.amount_usd}")

        # 测试 2: 查询 insider_alerts 表
        print("\n=== 测试2: 查询 insider_alerts ===")
        result = await session.execute(select(InsiderAlert))
        alerts = result.scalars().all()
        print(f"已有警报数量: {len(alerts)}")
        for a in alerts:
            print(f"  trade_id={a.trade_id}")

        # 测试 3: 使用 LEFT JOIN 查询
        print("\n=== 测试3: LEFT JOIN 查询待分析大单 ===")
        result = await session.execute(
            select(Trade)
            .outerjoin(InsiderAlert, Trade.id == InsiderAlert.trade_id)
            .where(
                and_(
                    Trade.is_whale == True,
                    InsiderAlert.id == None
                )
            )
            .order_by(Trade.timestamp.desc())
            .limit(5)
        )
        pending = result.scalars().all()
        print(f"待分析大单数量: {len(pending)}")
        for p in pending:
            print(f"  ID={p.id}, market={p.market_slug[:50]}...")

asyncio.run(test())
