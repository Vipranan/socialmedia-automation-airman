"""
Module: feedback_store.py
Training-oriented post database.

Schema: posts table
  id              INTEGER PRIMARY KEY
  timestamp       TEXT NOT NULL
  post_type       TEXT NOT NULL          'news' | 'festival'
  news_title      TEXT
  news_source     TEXT
  news_url        TEXT
  headline        TEXT
  image_prompt    TEXT
  caption         TEXT
  image_path      TEXT
  post_id         TEXT                   platform post ID after publishing
  approved        INTEGER                1 = posted, 0 = rejected
  feedback_type   TEXT                   'positive' | 'negative'
  feedback_label  TEXT                   one of the 8 labels below

Positive labels : image_good | headline_good | caption_good | font_good
Negative labels : headline_font_bad | image_bad | caption_bad | news_image_mismatch
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime

from config.settings import FEEDBACK_DB_PATH

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Label definitions (used by both bot UI and DB)
# ---------------------------------------------------------------------------

POSITIVE_LABELS = ("image_good", "headline_good", "caption_good", "font_good")
NEGATIVE_LABELS = (
    "headline_font_bad",
    "image_bad",
    "caption_bad",
    "news_image_mismatch",
)

LABEL_DISPLAY = {
    "image_good": "🖼️  Image is great",
    "headline_good": "📰  Headline is great",
    "caption_good": "✍️  Caption is great",
    "font_good": "🔤  Font is great",
    "headline_font_bad": "🔤  Headline / Font are bad",
    "image_bad": "🖼️  Image is bad",
    "caption_bad": "✍️  Caption is bad",
    "news_image_mismatch": "🔗  News & image don't match",
}


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(FEEDBACK_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Drop legacy feedback table if present; create training posts table."""
    with _conn() as conn:
        conn.execute("DROP TABLE IF EXISTS feedback")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                post_type       TEXT    NOT NULL DEFAULT 'news',
                news_title      TEXT,
                news_source     TEXT,
                news_url        TEXT,
                headline        TEXT,
                image_prompt    TEXT,
                caption         TEXT,
                image_path      TEXT,
                post_id         TEXT,
                approved        INTEGER NOT NULL DEFAULT 0,
                feedback_type   TEXT,
                feedback_label  TEXT
            )
        """)
        conn.commit()
    logger.info("Posts database initialized.")


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------


def create_post_record(
    post_type: str,
    news_title: str,
    news_source: str = "",
    news_url: str = "",
    headline: str = "",
    image_prompt: str = "",
    caption: str = "",
    image_path: str = "",
) -> int:
    """Insert a pending post record.

    Args:
        post_type: The type of post ('news' or 'festival').
        news_title: The title of the news article.
        news_source: The source of the news article.
        news_url: The URL to the original news article.
        headline: The headline for the post.
        image_prompt: The prompt used to generate the image.
        caption: The caption for the post.
        image_path: The path to the generated image file.

    Returns:
        The row id of the inserted record.
    """
    with _conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO posts
                (timestamp, post_type, news_title, news_source, news_url,
                 headline, image_prompt, caption, image_path, approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                datetime.utcnow().isoformat(),
                post_type,
                news_title,
                news_source,
                news_url,
                headline,
                image_prompt,
                caption,
                image_path,
            ),
        )
        conn.commit()
        return cur.lastrowid


def mark_posted(record_id: int, post_id: str) -> None:
    """Mark a record as approved and store the platform post ID.

    Args:
        record_id: The database record id to mark as posted.
        post_id: The platform-specific post ID after publishing.
    """
    with _conn() as conn:
        conn.execute(
            "UPDATE posts SET approved = 1, post_id = ? WHERE id = ?",
            (post_id, record_id),
        )
        conn.commit()


def save_feedback(record_id: int, feedback_type: str, feedback_label: str) -> None:
    """Store admin feedback on an existing post record.

    Args:
        record_id: The database record id to add feedback to.
        feedback_type: The type of feedback ('positive' or 'negative').
        feedback_label: The specific label from the predefined set.
    """
    with _conn() as conn:
        conn.execute(
            "UPDATE posts SET feedback_type = ?, feedback_label = ? WHERE id = ?",
            (feedback_type, feedback_label, record_id),
        )
        conn.commit()
    logger.info(
        f"Feedback saved — record {record_id}: {feedback_type} / {feedback_label}"
    )


# ---------------------------------------------------------------------------
# Read / Export
# ---------------------------------------------------------------------------


def get_all_posts() -> list[dict]:
    """Retrieve all posts from the database, ordered by id descending.

    Returns:
        A list of dictionaries representing post records.
    """
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def get_feedback_summary() -> dict:
    """Get a summary of all feedback data from the database.

    Returns:
        A dictionary with total, posted, rejected, positive, negative counts,
        and a breakdown by feedback label.
    """
    with _conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        posted = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE approved = 1"
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE approved = 0"
        ).fetchone()[0]
        positive = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE feedback_type = 'positive'"
        ).fetchone()[0]
        negative = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE feedback_type = 'negative'"
        ).fetchone()[0]

        label_counts: dict[str, int] = {}
        for label in (*POSITIVE_LABELS, *NEGATIVE_LABELS):
            count = conn.execute(
                "SELECT COUNT(*) FROM posts WHERE feedback_label = ?", (label,)
            ).fetchone()[0]
            if count > 0:
                label_counts[label] = count

    return {
        "total": total,
        "posted": posted,
        "rejected": rejected,
        "positive": positive,
        "negative": negative,
        "label_breakdown": label_counts,
    }


def export_to_json(output_path: str = "data/posts_export.json") -> None:
    """Export all posts to a JSON file.

    Args:
        output_path: The file path to write the JSON output to.
    """
    import json

    records = get_all_posts()
    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)
    logger.info(f"Posts exported to {output_path}")
