"""API 路由模块 - REST 接口定义"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Trade, Market, TraderProfile, InsiderAlert
from ..profiler.analyzer import TraderProfiler
from ..agent.insider import InsiderAnalyzer

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "insider-hunter"}


# ==================== 大单接口 ====================

@router.get("/whales/live")
async def get_live_whales(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    market_slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取实时大单列表

    - **limit**: 返回数量 (1-100)
    - **offset**: 偏移量
    - **market_slug**: 可选，筛选特定市场
    """
    query = select(Trade).where(Trade.is_whale == True)

    if market_slug:
        query = query.where(Trade.market_slug == market_slug)

    # 获取总数
    count_query = select(func.count(Trade.id)).where(Trade.is_whale == True)
    if market_slug:
        count_query = count_query.where(Trade.market_slug == market_slug)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 获取数据
    query = query.order_by(Trade.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    trades = result.scalars().all()

    return {
        "total": total,
        "data": [
            {
                "tx_hash": t.tx_hash,
                "market_slug": t.market_slug,
                "maker": t.maker,
                "side": t.side,
                "outcome": t.outcome,
                "price": float(t.price),
                "size": float(t.size),
                "amount_usd": float(t.amount_usd),
                "timestamp": t.timestamp.isoformat(),
            }
            for t in trades
        ],
    }


# ==================== 市场接口 ====================

@router.get("/markets")
async def get_markets(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    获取市场列表

    - **limit**: 返回数量 (1-200)
    - **offset**: 偏移量
    - **active_only**: 是否只返回活跃市场
    """
    query = select(Market)

    if active_only:
        query = query.where(Market.active == True)

    # 获取总数
    count_query = select(func.count(Market.id))
    if active_only:
        count_query = count_query.where(Market.active == True)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 获取数据
    query = query.order_by(Market.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    markets = result.scalars().all()

    return {
        "total": total,
        "data": [
            {
                "slug": m.slug,
                "question": m.question,
                "category": m.category,
                "resolved": m.resolved,
                "resolution_outcome": m.resolution_outcome,
                "active": m.active,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in markets
        ],
    }


@router.get("/market/{slug}")
async def get_market_detail(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取市场详情

    - **slug**: 市场标识
    """
    result = await db.execute(
        select(Market).where(Market.slug == slug)
    )
    market = result.scalar_one_or_none()

    if not market:
        raise HTTPException(status_code=404, detail="市场不存在")

    # 获取该市场的交易统计
    trades_result = await db.execute(
        select(
            func.count(Trade.id).label("trade_count"),
            func.sum(Trade.amount_usd).label("total_volume"),
            func.count(Trade.id).filter(Trade.is_whale == True).label("whale_count"),
        ).where(Trade.market_slug == slug)
    )
    stats = trades_result.one()

    # 获取最近交易
    recent_trades_result = await db.execute(
        select(Trade)
        .where(Trade.market_slug == slug)
        .order_by(Trade.timestamp.desc())
        .limit(10)
    )
    recent_trades = recent_trades_result.scalars().all()

    return {
        "slug": market.slug,
        "question": market.question,
        "condition_id": market.condition_id,
        "yes_token_id": market.yes_token_id,
        "no_token_id": market.no_token_id,
        "category": market.category,
        "resolved": market.resolved,
        "resolution_outcome": market.resolution_outcome,
        "active": market.active,
        "stats": {
            "trade_count": stats.trade_count or 0,
            "total_volume": float(stats.total_volume) if stats.total_volume else 0,
            "whale_count": stats.whale_count or 0,
        },
        "recent_trades": [
            {
                "tx_hash": t.tx_hash,
                "maker": t.maker,
                "side": t.side,
                "outcome": t.outcome,
                "amount_usd": float(t.amount_usd),
                "timestamp": t.timestamp.isoformat(),
            }
            for t in recent_trades
        ],
    }


# ==================== 交易者接口 ====================

@router.get("/traders/leaderboard")
async def get_traders_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    min_trades: int = Query(default=5, ge=1),
    trader_type: Optional[str] = Query(default=None, regex="^(smart_money|dumb_money|normal)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取交易者胜率排行榜

    - **limit**: 返回数量 (1-100)
    - **min_trades**: 最小交易次数
    - **trader_type**: 交易者类型筛选 (smart_money/dumb_money/normal)
    """
    from ..db import AsyncSessionLocal

    profiler = TraderProfiler(AsyncSessionLocal)
    leaderboard = await profiler.get_leaderboard(
        session=db,
        limit=limit,
        min_trades=min_trades,
        trader_type=trader_type
    )

    return {"data": leaderboard}


@router.get("/trader/{address}")
async def get_trader_detail(
    address: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取交易者详情

    - **address**: 交易者钱包地址
    """
    from ..db import AsyncSessionLocal

    profiler = TraderProfiler(AsyncSessionLocal)
    detail = await profiler.get_trader_detail(session=db, address=address)

    if not detail:
        raise HTTPException(status_code=404, detail="交易者不存在")

    return detail


# ==================== 内幕分析接口 ====================

@router.get("/insider/alerts")
async def get_insider_alerts(
    suspect_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    获取内幕分析警报列表

    - **suspect_only**: 是否只返回可疑交易
    - **limit**: 返回数量 (1-100)
    - **offset**: 偏移量
    """
    from ..db import AsyncSessionLocal

    analyzer = InsiderAnalyzer(AsyncSessionLocal)
    return await analyzer.get_alerts(
        session=db,
        suspect_only=suspect_only,
        limit=limit,
        offset=offset
    )


@router.post("/insider/analyze")
async def trigger_insider_analysis(
    limit: int = Query(default=5, ge=1, le=20),
):
    """
    手动触发内幕分析

    - **limit**: 分析的交易数量 (1-20)
    """
    from ..db import AsyncSessionLocal

    analyzer = InsiderAnalyzer(AsyncSessionLocal)
    alerts = await analyzer.scan_pending_trades(limit=limit)

    suspect_count = sum(1 for a in alerts if a.is_suspect)

    return {
        "analyzed": len(alerts),
        "suspect_count": suspect_count,
        "message": f"已分析 {len(alerts)} 笔交易，发现 {suspect_count} 笔可疑交易",
    }
