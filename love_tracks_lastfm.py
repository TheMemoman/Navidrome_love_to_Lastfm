#!/usr/bin/env python3

import sqlite3
import pylast
import argparse
import sys
import time
from datetime import datetime

# ================= USER CONFIG =================
DB_PATH = "navidrome.db"  # change this to your DB path
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
SESSION_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
# ===============================================

# ----- BATCH AND RETRY CONFIG -----
BATCH_SIZE = 50
MAX_RETRIES = 5
BATCH_PAUSE = 1  # seconds between batches

# ----- DATE RANGE FOR STARRED -----
START_DATE = "2007-01-01"  # inclusive - last used
END_DATE = "2025-12-31"    # inclusive - current day

def query_loved_tracks():
    """
    Query Navidrome for loved/favorited tracks within START_DATE and END_DATE.
    Uses 'starred_at' date for filtering. Tracks with NULL starred_at will be included.
    Adjust the 'starred' column to your schema if different.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = f"""
    SELECT mf.artist, mf.title, a.starred_at
    FROM media_file mf
    JOIN annotation a ON a.item_id = mf.id
    WHERE a.starred = 1
      AND (
            (a.starred_at IS NOT NULL AND a.starred_at >= '{START_DATE}' AND a.starred_at <= '{END_DATE}')
            OR a.starred_at IS NULL
          )
    ORDER BY mf.artist, mf.title
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def love_tracks(rows):
    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        session_key=SESSION_KEY
    )

    total = len(rows)
    loved_count = 0
    num_batches = (total - 1) // BATCH_SIZE + 1
    print(f"Total loved tracks found: {total}")
    print(f"Submitting in {num_batches} batches of {BATCH_SIZE} tracks each")
    print("-" * 50)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = rows[batch_start:batch_start + BATCH_SIZE]

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                for artist, title, _ in batch:
                    try:
                        track = network.get_track(artist, title)
                        track.love()
                        loved_count += 1
                        print(f"❤️ Loved: ({loved_count}/{total}): {artist} - {title}")
                    except Exception as e:
                        print(f"❌ Error: {artist} - {title}: {e}")
                break  # success, exit retry loop
            except Exception as e:
                print(f"Attempt {attempt} failed for batch starting at index {batch_start}: {e}")
                if attempt < MAX_RETRIES:
                    print(f"Retrying batch in 5 seconds...")
                    time.sleep(5)
                else:
                    print("⏭ Skip: Max retries reached for this batch.")
        time.sleep(BATCH_PAUSE)

    print("-" * 50)
    print("All loved tracks processed.")
    print(f"Resume with: --resume-from {loved_count}")

def main():
    parser = argparse.ArgumentParser(
        description="Sync loved tracks from Navidrome to Last.fm"
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Resume syncing from this row index"
    )

    args = parser.parse_args()

    rows = query_loved_tracks()
    if not rows:
        print("No loved tracks found. Exiting.")
        sys.exit(0)

    if args.resume_from > 0:
        rows = rows[args.resume_from:]

    love_tracks(rows)

if __name__ == "__main__":
    main()
