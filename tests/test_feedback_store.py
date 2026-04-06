"""Tests for feedback_store module."""

import os

os.environ["FEEDBACK_DB_PATH"] = ":memory:"


def test_init_db_creates_table(tmp_path):
    """Test that init_db creates the posts table."""
    from modules.feedback_store import get_all_posts, init_db

    db_path = str(tmp_path / "test.db")
    os.environ["FEEDBACK_DB_PATH"] = db_path
    init_db()
    posts = get_all_posts()
    assert isinstance(posts, list)


def test_create_post_record(tmp_path):
    """Test creating a post record returns an ID."""
    from modules.feedback_store import create_post_record, init_db

    db_path = str(tmp_path / "test.db")
    os.environ["FEEDBACK_DB_PATH"] = db_path
    init_db()
    record_id = create_post_record(
        post_type="news",
        news_title="Test News",
        news_source="Test Source",
    )
    assert isinstance(record_id, int)
    assert record_id > 0


def test_mark_posted(tmp_path):
    """Test marking a record as posted."""
    from modules.feedback_store import (
        create_post_record,
        get_all_posts,
        init_db,
        mark_posted,
    )

    db_path = str(tmp_path / "test.db")
    os.environ["FEEDBACK_DB_PATH"] = db_path
    init_db()
    record_id = create_post_record(post_type="news", news_title="Test")
    mark_posted(record_id, "IG:123|LI:456")
    posts = get_all_posts()
    posted = [p for p in posts if p["id"] == record_id]
    assert len(posted) == 1
    assert posted[0]["approved"] == 1
