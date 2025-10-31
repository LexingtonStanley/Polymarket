# database_schema.py

"""
Recommended Database Schema for Polymarket Data

EVENT (Parent)
├── MARKET 1: "Will Trump win?" → [Yes, No]
├── MARKET 2: "Will Biden win?" → [Yes, No]
├── MARKET 3: "Will DeSantis win?" → [Yes, No]
└── MARKET 4: "Will Harris win?" → [Yes, No]

OR

EVENT (Parent)
└── MARKET 1: "Who will win?" → [Trump, Biden, DeSantis, Harris]
"""

# Using SQLAlchemy as an example
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    # Primary Key
    id = Column(String, primary_key=True)  # Polymarket event ID

    # Basic Info
    slug = Column(String, unique=True, index=True)
    ticker = Column(String)
    title = Column(String)
    description = Column(Text)

    # Status
    active = Column(Boolean)
    closed = Column(Boolean)
    archived = Column(Boolean)
    restricted = Column(Boolean)
    featured = Column(Boolean)

    # Dates
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    start_time = Column(DateTime)
    end_date = Column(DateTime)

    # Media
    icon = Column(String)
    image = Column(String)

    # Market Info
    resolution_source = Column(String)

    # Metrics
    liquidity = Column(Integer)
    liquidity_amm = Column(Integer)
    liquidity_clob = Column(Integer)
    open_interest = Column(Integer)

    # Volume metrics
    volume = Column(Integer)
    volume_24hr = Column(Integer)
    volume_1wk = Column(Integer)
    volume_1mo = Column(Integer)
    volume_1yr = Column(Integer)

    # Other flags
    cyom = Column(Boolean)  # Create Your Own Market
    competitive = Column(Integer)
    comment_count = Column(Integer)
    enable_order_book = Column(Boolean)
    neg_risk = Column(Boolean)

    # Tags stored as JSON array
    tags = Column(JSON)

    # Relationships
    markets = relationship("Market", back_populates="event", cascade="all, delete-orphan")


class Market(Base):
    __tablename__ = 'markets'

    # Primary Key
    id = Column(String, primary_key=True)  # Polymarket market ID

    # Foreign Key to Event
    event_id = Column(String, ForeignKey('events.id'), index=True)

    # Basic Info
    slug = Column(String, index=True)
    question = Column(String)
    description = Column(Text)
    question_id = Column(String)  # Blockchain question ID
    condition_id = Column(String)  # Blockchain condition ID

    # Status
    active = Column(Boolean)
    closed = Column(Boolean)
    archived = Column(Boolean)
    restricted = Column(Boolean)
    featured = Column(Boolean)
    accepting_orders = Column(Boolean)

    # Dates
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    end_date_iso = Column(String)
    event_start_time = Column(DateTime)
    accepting_orders_timestamp = Column(DateTime)

    # Media
    icon = Column(String)
    image = Column(String)

    # Trading Info
    best_bid = Column(Float)
    best_ask = Column(Float)
    spread = Column(Float)
    last_trade_price = Column(Float)

    # Liquidity
    liquidity = Column(String)  # Can be string in API
    liquidity_num = Column(Integer)
    liquidity_amm = Column(Integer)
    liquidity_clob = Column(Integer)

    # Volume
    volume = Column(String)  # Can be string in API
    volume_num = Column(Integer)
    volume_24hr = Column(Integer)
    volume_1wk = Column(Integer)
    volume_1mo = Column(Integer)
    volume_1yr = Column(Integer)

    # Price changes
    one_hour_price_change = Column(Float)
    one_day_price_change = Column(Float)
    one_week_price_change = Column(Float)
    one_month_price_change = Column(Float)
    one_year_price_change = Column(Float)

    # Order settings
    order_min_size = Column(Integer)
    order_price_min_tick_size = Column(Float)

    # Resolution
    resolution_source = Column(String)
    resolved_by = Column(String)
    uma_bond = Column(String)
    uma_reward = Column(String)

    # Blockchain IDs
    clob_token_ids = Column(JSON)  # Array of token IDs

    # Outcomes stored as JSON array ["Yes", "No"] or ["Trump", "Biden", ...]
    outcomes = Column(JSON)

    # Other flags
    neg_risk = Column(Boolean)
    enable_order_book = Column(Boolean)
    competitive = Column(Integer)
    cyom = Column(Boolean)

    # Address fields
    submitted_by = Column(String)
    market_maker_address = Column(String)

    # Relationships
    event = relationship("Event", back_populates="markets")


# Optional: If you want to track individual outcome prices over time
class OutcomePrice(Base):
    __tablename__ = 'outcome_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String, ForeignKey('markets.id'), index=True)
    outcome = Column(String)  # "Yes", "No", or candidate name
    price = Column(Float)
    timestamp = Column(DateTime, index=True)

    # Could add bid/ask/volume per outcome if needed


# For tracking tags
class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    label = Column(String, unique=True)
    slug = Column(String)


if __name__ == "__main__":
    # Example of creating tables
    from sqlalchemy import create_engine

    # Create SQLite database (change to PostgreSQL/MySQL for production)
    engine = create_engine('sqlite:///polymarket.db')
    Base.metadata.create_all(engine)
    print("Database schema created successfully!")