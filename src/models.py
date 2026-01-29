from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    condition_id = Column(String)
    yes_token_id = Column(String)
    no_token_id = Column(String)
    category = Column(String)  # "Politics", "Business"
    active = Column(Boolean, default=True)


class Trade(Base):
    __tablename__ = "trades"

    tx_hash = Column(String, primary_key=True)
    log_index = Column(Integer, primary_key=True)
    market_slug = Column(String, index=True)
    maker = Column(String, index=True)
    side = Column(String)  # BUY/SELL
    outcome = Column(String)  # YES/NO
    amount_usd = Column(Numeric(18, 2))
    timestamp = Column(DateTime, index=True)

    # 内幕猎手专属字段
    is_whale = Column(Boolean, default=False)  # 是否大单 (>1000U)
    news_checked = Column(Boolean, default=False)  # Agent 是否已分析过


class InsiderAlert(Base):
    __tablename__ = "insider_alerts"

    id = Column(Integer, primary_key=True, index=True)
    trade_tx_hash = Column(String, index=True)
    market_slug = Column(String, index=True)
    related_news = Column(Text)
    news_time = Column(DateTime)
    is_insider_suspect = Column(Boolean, default=False)
    reason = Column(Text)
    created_at = Column(DateTime)
