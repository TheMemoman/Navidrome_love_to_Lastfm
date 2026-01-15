# Navidrome_love_to_LastFM
A Python script to synchronize your loved tracks from your Navidrome database to your Last.fm profile.

## Description

This script connects to your Navidrome database and retrieves all tracks you’ve marked as “loved” (starred) within a configurable date range (`START_DATE` to `END_DATE`). Each track is then submitted to Last.fm using the Last.fm API, marking it as “loved” on your profile.  

The script supports **batch processing** and a **retry mechanism**, allowing it to handle large libraries and temporary network or API issues gracefully. Progress is printed to the console, including counts of successfully loved tracks and any errors encountered.

## How It Works

1. **Query Loved Tracks**  
   The script connects to your SQLite Navidrome database and queries all tracks with `starred = 1` in the `annotation` table. Tracks are filtered by the `starred_at` date within the `START_DATE` and `END_DATE` range, though tracks without a date are also included.

2. **Batch Submission**  
   Tracks are divided into batches of configurable size (`BATCH_SIZE`). Each batch is submitted to Last.fm sequentially, with a short pause (`BATCH_PAUSE`) between batches to avoid hitting rate limits.

3. **Retry Mechanism**  
   If a batch fails due to network or API issues, the script retries it up to `MAX_RETRIES` times with a 5-second delay between retries. Individual track failures are logged without stopping the batch.

4. **Resume Option**  
   The script supports resuming from a specific row index using the `--resume-from` argument, allowing recovery from interruptions without reprocessing all tracks.

## Configure the following variables

| Name           | Description                                                                                     | Suggested Value                     |
|----------------|-------------------------------------------------------------------------------------------------|------------------------------------|
| `DB_PATH`      | Path to your Navidrome SQLite database                                                          | `/path/to/navidrome.db`            |
| `API_KEY`      | Your Last.fm API key (see [last.fm API docs](https://www.last.fm/api/authentication)) | `xxxxxxxxxxxxxxxxxxx`               |
| `API_SECRET`   | Your Last.fm API secret (see [last.fm API docs](https://www.last.fm/api/authentication)) | `xxxxxxxxxxxxxxxx`                  |
| `SESSION_KEY`  | Your Last.fm session key (from authentication)                                                 | `xxxxxxxxx`                         |
| `START_DATE`         | Starting date limit to avoid uploading all likes every time. Can be the date of the latest execution           | `"2025-01-01"`                     |
| `END_DATE`           | Ending date limit. Can be the date of the current execution                                                    | `"2026-01-15"`                     |

## Execute the script

```bash
python3 love_tracks_lastfm.py
