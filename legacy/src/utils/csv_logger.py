"""CSV logging utilities."""
import csv
import os
from datetime import datetime

from src.config import POST_LOG_FILE
from src.logger import logger

FIELDNAMES = ['timestamp', 'date', 'time', 'post_type', 'content', 'media_id', 'status']


def _needs_header() -> bool:
    """Return True if the CSV file doesn't exist or is missing the 'status' column."""
    if not os.path.exists(POST_LOG_FILE):
        return True
    try:
        with open(POST_LOG_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return 'status' not in (reader.fieldnames or [])
    except Exception:
        return True


def _migrate_if_needed() -> None:
    """Add 'status' column to existing rows if the file uses the old schema."""
    if not os.path.exists(POST_LOG_FILE):
        return
    try:
        with open(POST_LOG_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'status' in (reader.fieldnames or []):
                return  # Already up to date
            rows = list(reader)

        # Rewrite with new schema, backfilling status as "posted" for old rows
        with open(POST_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                row.setdefault('status', 'posted')
                writer.writerow({k: row.get(k, '') for k in FIELDNAMES})

        logger.info("CSV log migrated to include 'status' column.")
    except Exception as e:
        logger.error(f"Failed to migrate CSV log: {e}")


def log_post_to_csv(post_type: str, content: str, media_id: str = None, status: str = "posted"):
    """Log post details to CSV file."""
    try:
        _migrate_if_needed()

        with open(POST_LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

            if _needs_header():
                writer.writeheader()

            now = datetime.now()
            writer.writerow({
                'timestamp': now.isoformat(),
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S'),
                'post_type': post_type,
                'content': content,
                'media_id': media_id or 'N/A',
                'status': status,
            })
            logger.info(f"Logged post to CSV: [{status}] {post_type} - {content[:50]}...")
    except Exception as e:
        logger.error(f"Failed to log post to CSV: {e}")
