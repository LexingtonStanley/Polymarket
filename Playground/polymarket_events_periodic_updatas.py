# update_database.py

import time
from fetch_and_populate import fetch_all_active_events, populate_database


def continuous_update(interval_seconds=300):
    """
    Continuously update the database at specified intervals

    Args:
        interval_seconds: Time between updates (default 5 minutes)
    """
    print(f"Starting continuous update (interval: {interval_seconds}s)")
    print("Press Ctrl+C to stop\n")

    while True:
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Fetching updates...")
            events = fetch_all_active_events()

            if events:
                populate_database(events)

            print(f"Next update in {interval_seconds} seconds...")
            time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\nStopping continuous update.")
            break
        except Exception as e:
            print(f"Error during update: {e}")
            print(f"Retrying in {interval_seconds} seconds...")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    # Update every 5 minutes
    continuous_update(interval_seconds=300)