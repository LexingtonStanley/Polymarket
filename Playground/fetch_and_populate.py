# fetch_and_populate.py

import os
import requests
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database_schema import Base, Event, Market

load_dotenv()

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///polymarket.db')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# API Configuration
GAMMA_API_BASE = "https://gamma-api.polymarket.com"


def parse_datetime(date_string):
    """Parse ISO datetime string to datetime object"""
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return None


def fetch_active_events(limit=100, offset=0):
    """Fetch active events from Polymarket API"""
    params = {
        'closed': 'false',
        'order': 'id',
        'ascending': 'false',
        'limit': limit,
        'offset': offset
    }

    response = requests.get(f"{GAMMA_API_BASE}/events", params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching events: {response.status_code}")
        return []


def fetch_all_active_events(max_events=None):
    """Fetch all active events with pagination"""
    all_events = []
    offset = 0
    limit = 100

    print("Fetching active events from Polymarket...")

    while True:
        events = fetch_active_events(limit=limit, offset=offset)

        if not events:
            break

        all_events.extend(events)
        print(f"  Fetched {len(events)} events (total: {len(all_events)})")

        if len(events) < limit:
            break

        if max_events and len(all_events) >= max_events:
            all_events = all_events[:max_events]
            break

        offset += limit

    print(f"\nTotal events fetched: {len(all_events)}")
    return all_events


def create_event_from_api(event_data):
    """Create Event object from API data"""
    return Event(
        id=str(event_data.get('id')),
        slug=event_data.get('slug'),
        ticker=event_data.get('ticker'),
        title=event_data.get('title'),
        description=event_data.get('description'),

        active=event_data.get('active', False),
        closed=event_data.get('closed', False),
        archived=event_data.get('archived', False),
        restricted=event_data.get('restricted', False),
        featured=event_data.get('featured', False),

        created_at=parse_datetime(event_data.get('createdAt')),
        updated_at=parse_datetime(event_data.get('updatedAt')),
        start_time=parse_datetime(event_data.get('startTime')),
        end_date=parse_datetime(event_data.get('endDate')),

        icon=event_data.get('icon'),
        image=event_data.get('image'),

        resolution_source=event_data.get('resolutionSource'),

        liquidity=event_data.get('liquidity', 0),
        liquidity_amm=event_data.get('liquidityAmm', 0),
        liquidity_clob=event_data.get('liquidityClob', 0),
        open_interest=event_data.get('openInterest', 0),

        volume=event_data.get('volume', 0),
        volume_24hr=event_data.get('volume24hr', 0),
        volume_1wk=event_data.get('volume1wk', 0),
        volume_1mo=event_data.get('volume1mo', 0),
        volume_1yr=event_data.get('volume1yr', 0),

        cyom=event_data.get('cyom', False),
        competitive=event_data.get('competitive', 0),
        comment_count=event_data.get('commentCount', 0),
        enable_order_book=event_data.get('enableOrderBook', False),
        neg_risk=event_data.get('negRisk', False),

        tags=event_data.get('tags', [])
    )


def create_market_from_api(market_data, event_id):
    """Create Market object from API data"""
    return Market(
        id=str(market_data.get('id')),
        event_id=event_id,

        slug=market_data.get('slug'),
        question=market_data.get('question'),
        description=market_data.get('description'),
        question_id=market_data.get('questionID'),
        condition_id=market_data.get('conditionId'),

        active=market_data.get('active', False),
        closed=market_data.get('closed', False),
        archived=market_data.get('archived', False),
        restricted=market_data.get('restricted', False),
        featured=market_data.get('featured', False),
        accepting_orders=market_data.get('acceptingOrders', False),

        created_at=parse_datetime(market_data.get('createdAt')),
        updated_at=parse_datetime(market_data.get('updatedAt')),
        start_date=parse_datetime(market_data.get('startDate')),
        end_date=parse_datetime(market_data.get('endDate')),
        end_date_iso=market_data.get('endDateIso'),
        event_start_time=parse_datetime(market_data.get('eventStartTime')),
        accepting_orders_timestamp=parse_datetime(market_data.get('acceptingOrdersTimestamp')),

        icon=market_data.get('icon'),
        image=market_data.get('image'),

        best_bid=float(market_data.get('bestBid', 0)),
        best_ask=float(market_data.get('bestAsk', 0)),
        spread=float(market_data.get('spread', 0)),
        last_trade_price=float(market_data.get('lastTradePrice', 0)),

        liquidity=str(market_data.get('liquidity', 0)),
        liquidity_num=market_data.get('liquidityNum', 0),
        liquidity_amm=market_data.get('liquidityAmm', 0),
        liquidity_clob=market_data.get('liquidityClob', 0),

        volume=str(market_data.get('volume', 0)),
        volume_num=market_data.get('volumeNum', 0),
        volume_24hr=market_data.get('volume24hr', 0),
        volume_1wk=market_data.get('volume1wk', 0),
        volume_1mo=market_data.get('volume1mo', 0),
        volume_1yr=market_data.get('volume1yr', 0),

        one_hour_price_change=float(market_data.get('oneHourPriceChange', 0)),
        one_day_price_change=float(market_data.get('oneDayPriceChange', 0)),
        one_week_price_change=float(market_data.get('oneWeekPriceChange', 0)),
        one_month_price_change=float(market_data.get('oneMonthPriceChange', 0)),
        one_year_price_change=float(market_data.get('oneYearPriceChange', 0)),

        order_min_size=market_data.get('orderMinSize', 0),
        order_price_min_tick_size=float(market_data.get('orderPriceMinTickSize', 0)),

        resolution_source=market_data.get('resolutionSource'),
        resolved_by=market_data.get('resolvedBy'),
        uma_bond=str(market_data.get('umaBond', '')),
        uma_reward=str(market_data.get('umaReward', '')),

        clob_token_ids=market_data.get('clobTokenIds', []),
        outcomes=market_data.get('outcomes', []),

        neg_risk=market_data.get('negRisk', False),
        enable_order_book=market_data.get('enableOrderBook', False),
        competitive=market_data.get('competitive', 0),
        cyom=market_data.get('cyom', False),

        submitted_by=market_data.get('submitted_by'),
        market_maker_address=market_data.get('marketMakerAddress')
    )


def populate_database(events_data):
    """Populate database with events and markets"""
    session = Session()

    try:
        events_added = 0
        events_updated = 0
        markets_added = 0
        markets_updated = 0

        for event_data in events_data:
            event_id = str(event_data.get('id'))

            # Check if event exists
            existing_event = session.query(Event).filter_by(id=event_id).first()

            if existing_event:
                # Update existing event
                for key, value in create_event_from_api(event_data).__dict__.items():
                    if not key.startswith('_'):
                        setattr(existing_event, key, value)
                events_updated += 1
            else:
                # Add new event
                new_event = create_event_from_api(event_data)
                session.add(new_event)
                events_added += 1

            # Process markets
            markets_data = event_data.get('markets', [])
            for market_data in markets_data:
                market_id = str(market_data.get('id'))

                # Check if market exists
                existing_market = session.query(Market).filter_by(id=market_id).first()

                if existing_market:
                    # Update existing market
                    for key, value in create_market_from_api(market_data, event_id).__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing_market, key, value)
                    markets_updated += 1
                else:
                    # Add new market
                    new_market = create_market_from_api(market_data, event_id)
                    session.add(new_market)
                    markets_added += 1

        session.commit()

        print(f"\nDatabase population complete:")
        print(f"  Events added: {events_added}")
        print(f"  Events updated: {events_updated}")
        print(f"  Markets added: {markets_added}")
        print(f"  Markets updated: {markets_updated}")

    except Exception as e:
        session.rollback()
        print(f"Error populating database: {e}")
        raise
    finally:
        session.close()


def query_examples():
    """Show some example queries"""
    session = Session()

    print("\n" + "=" * 80)
    print("Example Queries")
    print("=" * 80 + "\n")

    # Count total events and markets
    event_count = session.query(Event).count()
    market_count = session.query(Market).count()
    print(f"Total events in database: {event_count}")
    print(f"Total markets in database: {market_count}")

    # Show some active events
    print("\n5 Most recent active events:")
    recent_events = session.query(Event).filter_by(active=True).order_by(Event.created_at.desc()).limit(5).all()
    for event in recent_events:
        market_count = len(event.markets)
        print(f"  - {event.title} ({market_count} markets)")
        print(f"    Slug: {event.slug}")
        print(f"    End Date: {event.end_date}")

    # Show events with multiple markets
    print("\nEvents with multiple markets:")
    all_events = session.query(Event).filter_by(active=True).all()
    multi_market_events = [e for e in all_events if len(e.markets) > 1]
    for event in multi_market_events[:5]:
        print(f"  - {event.title} ({len(event.markets)} markets)")
        for market in event.markets:
            print(f"      └─ {market.question}")

    # Show markets accepting orders
    print("\nMarkets currently accepting orders:")
    accepting = session.query(Market).filter_by(accepting_orders=True).limit(5).all()
    for market in accepting:
        print(f"  - {market.question}")
        print(f"    Best Bid: {market.best_bid}, Best Ask: {market.best_ask}")
        print(f"    Volume 24h: {market.volume_24hr}")

    session.close()


def main():
    """Main execution function"""
    print("Polymarket Data Fetcher and Database Populator")
    print("=" * 80 + "\n")

    # Fetch events (limit to 500 for testing, remove limit for all)
    events = fetch_all_active_events(max_events=500)

    if events:
        # Populate database
        populate_database(events)

        # Show some example queries
        query_examples()
    else:
        print("No events fetched. Check your API connection.")


if __name__ == "__main__":
    main()