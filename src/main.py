from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import get_db, init_db
from .models import Trade, Market, InsiderAlert

app = FastAPI(title="Insider Hunter", description="Polymarket 内幕交易猎手")

# 允许前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Insider Hunter API", "status": "running"}


@app.get("/api/whales/live")
def get_live_whales(limit: int = 20, db: Session = Depends(get_db)):
    """获取实时大单交易流"""
    trades = db.query(Trade).filter(
        Trade.is_whale == True
    ).order_by(Trade.timestamp.desc()).limit(limit).all()

    return {"whales": [
        {
            "tx_hash": t.tx_hash,
            "market_slug": t.market_slug,
            "maker": t.maker,
            "side": t.side,
            "outcome": t.outcome,
            "amount_usd": float(t.amount_usd),
            "timestamp": t.timestamp.isoformat() if t.timestamp else None
        } for t in trades
    ]}


@app.get("/api/insider/alerts")
def get_insider_alerts(limit: int = 20, db: Session = Depends(get_db)):
    """获取内幕交易分析报告"""
    alerts = db.query(InsiderAlert).filter(
        InsiderAlert.is_insider_suspect == True
    ).order_by(InsiderAlert.created_at.desc()).limit(limit).all()

    return {"alerts": [
        {
            "id": a.id,
            "trade_tx_hash": a.trade_tx_hash,
            "market_slug": a.market_slug,
            "related_news": a.related_news,
            "news_time": a.news_time.isoformat() if a.news_time else None,
            "reason": a.reason,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in alerts
    ]}


@app.get("/api/market/{slug}")
def get_market_history(slug: str, db: Session = Depends(get_db)):
    """获取市场交易历史"""
    market = db.query(Market).filter(Market.slug == slug).first()
    if not market:
        return {"error": "Market not found"}

    trades = db.query(Trade).filter(
        Trade.market_slug == slug
    ).order_by(Trade.timestamp.desc()).limit(100).all()

    return {
        "market": {
            "slug": market.slug,
            "category": market.category,
            "active": market.active
        },
        "trades": [
            {
                "tx_hash": t.tx_hash,
                "side": t.side,
                "outcome": t.outcome,
                "amount_usd": float(t.amount_usd),
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "is_whale": t.is_whale
            } for t in trades
        ]
    }


@app.get("/api/markets")
def get_markets(category: str = None, db: Session = Depends(get_db)):
    """获取市场列表"""
    query = db.query(Market).filter(Market.active == True)
    if category:
        query = query.filter(Market.category == category)

    markets = query.all()
    return {"markets": [
        {
            "slug": m.slug,
            "category": m.category,
            "condition_id": m.condition_id
        } for m in markets
    ]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
