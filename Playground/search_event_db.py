# query_database.py

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database_schema import Event, Market

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///polymarket.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_future_events(limit=10):
    """Get events that haven't ended yet"""
    session = Session()
    now = datetime.now(timezone.utc)

    future_events = session.query(Event).filter(
        Event.end_date > now,
        Event.active == True
    ).order_by(Event.end_date.asc()).limit(limit).all()

    session.close()
    return future_events


def get_events_by_tag(tag_keyword, limit=10):
    """
    Get events that contain a specific tag keyword

    Args:
        tag_keyword: String to search for in tags (e.g., 'crypto', 'sports', 'politics')
        limit: Maximum number of events to return
    """
    session = Session()
    now = datetime.now(timezone.utc)

    # Query events with future end dates
    all_future_events = session.query(Event).filter(
        Event.end_date > now,
        Event.active == True
    ).all()

    # Filter by tag (tags are stored as JSON array)
    matching_events = []
    for event in all_future_events:
        if event.tags:
            # Check if any tag contains the keyword (case-insensitive)
            for tag in event.tags:
                if isinstance(tag, dict):
                    tag_label = tag.get('label', '').lower()
                    tag_slug = tag.get('slug', '').lower()
                    if tag_keyword.lower() in tag_label or tag_keyword.lower() in tag_slug:
                        matching_events.append(event)
                        break
                elif isinstance(tag, str):
                    if tag_keyword.lower() in tag.lower():
                        matching_events.append(event)
                        break

        if len(matching_events) >= limit:
            break

    session.close()
    return matching_events


def display_event_details(event):
    """Display detailed information about an event"""
    print(f"\n{'=' * 80}")
    print(f"Event: {event.title}")
    print(f"{'=' * 80}")
    print(f"ID: {event.id}")
    print(f"Slug: {event.slug}")
    print(f"End Date: {event.end_date}")
    print(f"Active: {event.active}")
    print(f"Closed: {event.closed}")
    print(f"Volume 24h: ${event.volume_24hr:,}")
    print(f"Liquidity: ${event.liquidity:,}")

    print(
        f"\nTags: {', '.join([tag.get('label', tag) if isinstance(tag, dict) else tag for tag in event.tags]) if event.tags else 'None'}")

    print(f"\nDescription (first 200 chars):")
    print(f"{event.description[:200]}..." if event.description and len(event.description) > 200 else event.description)

    print(f"\nMarkets ({len(event.markets)}):")
    for i, market in enumerate(event.markets, 1):
        print(f"  {i}. {market.question}")
        print(f"     Outcomes: {', '.join(market.outcomes) if market.outcomes else 'N/A'}")
        print(f"     Accepting Orders: {market.accepting_orders}")
        print(f"     Best Bid: {market.best_bid:.3f}, Best Ask: {market.best_ask:.3f}")
        print(f"     Volume 24h: ${market.volume_24hr:,}")


def search_markets_by_keyword(keyword, limit=10):
    """Search markets by keyword in question or description"""
    session = Session()
    now = datetime.now(timezone.utc)

    markets = session.query(Market).filter(
        and_(
            Market.end_date > now,
            Market.active == True,
            or_(
                Market.question.ilike(f'%{keyword}%'),
                Market.description.ilike(f'%{keyword}%')
            )
        )
    ).order_by(Market.end_date.asc()).limit(limit).all()

    session.close()
    return markets


def get_all_unique_tags():
    """Get all unique tags from the database"""
    session = Session()

    all_events = session.query(Event).all()
    unique_tags = set()

    for event in all_events:
        if event.tags:
            for tag in event.tags:
                if isinstance(tag, dict):
                    unique_tags.add(tag.get('label', ''))
                elif isinstance(tag, str):
                    unique_tags.add(tag)

    session.close()
    return sorted(list(unique_tags))


def main():
    print("Polymarket Database Query Tool")
    print("=" * 80 + "\n")

    # Get database stats
    session = Session()
    total_events = session.query(Event).count()
    total_markets = session.query(Market).count()
    now = datetime.now(timezone.utc)
    future_events_count = session.query(Event).filter(Event.end_date > now).count()
    session.close()

    print(f"Database Stats:")
    print(f"  Total Events: {total_events:,}")
    print(f"  Total Markets: {total_markets:,}")
    print(f"  Future Events: {future_events_count:,}")

    # Show all available tags
    print("\n" + "=" * 80)
    print("Available Tags (first 30):")
    print("=" * 80)
    all_tags = get_all_unique_tags()
    for tag in all_tags[:30]:
        print(f"  - {tag}")
    if len(all_tags) > 30:
        print(f"  ... and {len(all_tags) - 30} more")

    # Query crypto events by tag
    print("\n" + "=" * 80)
    print("CRYPTO EVENTS (searching by 'crypto' tag)")
    print("=" * 80)

    crypto_events = get_events_by_tag('crypto', limit=5)

    if crypto_events:
        print(f"\nFound {len(crypto_events)} crypto events with future end dates:\n")
        for event in crypto_events[:3]:  # Show first 3 in detail
            display_event_details(event)
    else:
        print("\nNo crypto events found by tag. Trying keyword search...")

        # Try keyword search instead
        crypto_markets = search_markets_by_keyword('bitcoin', limit=5)
        crypto_markets.extend(search_markets_by_keyword('ethereum', limit=5))
        crypto_markets.extend(search_markets_by_keyword('crypto', limit=5))

        # Get unique markets
        seen_ids = set()
        unique_markets = []
        for market in crypto_markets:
            if market.id not in seen_ids:
                unique_markets.append(market)
                seen_ids.add(market.id)

        print(f"\nFound {len(unique_markets)} crypto markets by keyword search:\n")
        for market in unique_markets[:5]:
            print(f"\n{'-' * 80}")
            print(f"Market: {market.question}")
            print(f"End Date: {market.end_date}")
            print(f"Outcomes: {', '.join(market.outcomes) if market.outcomes else 'N/A'}")
            print(f"Best Bid: {market.best_bid:.3f}, Best Ask: {market.best_ask:.3f}")
            print(f"Volume 24h: ${market.volume_24hr:,}")
            print(f"Accepting Orders: {market.accepting_orders}")

    # Show some other future events
    print("\n" + "=" * 80)
    print("SAMPLE FUTURE EVENTS (next 5 ending soonest)")
    print("=" * 80)

    future_events = get_future_events(limit=5)
    for event in future_events:
        print(f"\n{event.title}")
        print(f"  End Date: {event.end_date}")
        print(f"  Markets: {len(event.markets)}")
        print(
            f"  Tags: {', '.join([tag.get('label', tag) if isinstance(tag, dict) else tag for tag in (event.tags or [])])}")


if __name__ == "__main__":
    main()