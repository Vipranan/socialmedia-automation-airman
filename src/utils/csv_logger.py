"""CSV logging utilities."""

import os
import csv
from datetime import datetime
from config.settings import POST_LOG_FILE

FIELDNAMES = ["timestamp", "date", "time", "post_type", "content", "media_id", "status"]


def _needs_header() -> bool:
    if not os.path.exists(POST_LOG_FILE):
        return True
    try:
        with open(POST_LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return "status" not in (reader.fieldnames or [])
    except Exception:
        return True


def _migrate_if_needed() -> None:
    if not os.path.exists(POST_LOG_FILE):
        return
    try:
        with open(POST_LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "status" in (reader.fieldnames or []):
                return
            rows = list(reader)

        with open(POST_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                row.setdefault("status", "posted")
                writer.writerow({k: row.get(k, "") for k in FIELDNAMES})
    except Exception as e:
        pass


def log_post_to_csv(
    post_type: str, content: str, media_id: str = None, status: str = "posted"
):
    try:
        _migrate_if_needed()

        with open(POST_LOG_FILE, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

            if _needs_header():
                writer.writeheader()

            now = datetime.now()
            writer.writerow(
                {
                    "timestamp": now.isoformat(),
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "post_type": post_type,
                    "content": content,
                    "media_id": media_id or "N/A",
                    "status": status,
                }
            )
    except Exception as e:
        pass
