"""News fetching service using RSS feeds — 3-bucket pipeline."""
import os
import feedparser
from src.logger import logger
from src.config import PRIORITY_FEEDS, SHOWN_NEWS_FILE
from src.utils import load_shown_news, save_shown_news

# Global set to track headlines already shown
SHOWN_NEWS_HEADLINES = load_shown_news()


def _fetch_feed_headlines(query: str) -> list[str]:
    """Fetch fresh headlines from a single Google News RSS query, stripping source tags."""
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    titles = []
    for entry in feed.entries:
        title = entry.title
        if " - " in title:
            title = title.rsplit(" - ", 1)[0].strip()
        if title not in SHOWN_NEWS_HEADLINES:
            titles.append(title)
    return titles


# ---------------------------------------------------------------------------
# Bucket 1 — Collect raw pool
# ---------------------------------------------------------------------------

def _bucket1_collect_raw_news(per_category_cap: int = 5) -> list[dict]:
    """
    Bucket 1: Collect a wide raw pool of fresh headlines from every source.

    Each item in the returned list is a dict:
        { 'title': str, 'category': str, 'priority_rank': int }

    priority_rank matches the order in PRIORITY_FEEDS (0 = most important).
    General aviation headlines get rank = len(PRIORITY_FEEDS).

    per_category_cap: max headlines taken per category so high-volume feeds
    (Crashes, Mayday) don't crowd out lower-volume ones before Bucket 2 runs.
    """
    raw_pool: list[dict] = []
    seen: set[str] = set()

    # From each priority feed — capped so every category gets a fair slot
    for rank, (category, query) in enumerate(PRIORITY_FEEDS):
        fresh = _fetch_feed_headlines(query)
        added = 0
        for title in fresh:
            if added >= per_category_cap:
                break
            if title not in seen:
                seen.add(title)
                raw_pool.append({
                    "title": title,
                    "category": category,
                    "priority_rank": rank,
                })
                added += 1
        logger.info(f"[Bucket 1] [{category}] {added} fresh headlines collected")

    # From general aviation (lowest priority) — also capped
    general_query = "aviation+OR+aircraft+OR+airline+OR+pilot"
    general_fresh = _fetch_feed_headlines(general_query)
    general_rank = len(PRIORITY_FEEDS)
    added = 0
    for title in general_fresh:
        if added >= per_category_cap:
            break
        if title not in seen:
            seen.add(title)
            raw_pool.append({
                "title": title,
                "category": "General Aviation",
                "priority_rank": general_rank,
            })
            added += 1
    logger.info(f"[Bucket 1] [General Aviation] {added} fresh headlines collected")

    logger.info(f"[Bucket 1] Total raw pool: {len(raw_pool)} headlines")
    return raw_pool


# ---------------------------------------------------------------------------
# Bucket 2 — Select by priority
# ---------------------------------------------------------------------------

def _bucket2_select_by_priority(raw_pool: list[dict], select_count: int) -> list[dict]:
    """
    Bucket 2: Select news with variety across categories, respecting priority order.

    Uses round-robin over categories sorted by priority_rank:
      Round 1 → 1 headline from each category (crashes first, then mayday, …)
      Round 2 → 2nd headline from each category in the same order
      … until select_count is reached.

    This guarantees every priority category gets represented before any category
    gets a second slot.
    """
    from collections import defaultdict

    # Group raw pool items by priority_rank, preserving feed order within each group
    by_rank: dict[int, list[dict]] = defaultdict(list)
    for item in raw_pool:
        by_rank[item["priority_rank"]].append(item)

    sorted_ranks = sorted(by_rank.keys())  # [0, 1, 2, …, 7]

    selected: list[dict] = []
    round_num = 0
    while len(selected) < select_count:
        added_this_round = False
        for rank in sorted_ranks:
            if len(selected) >= select_count:
                break
            items = by_rank[rank]
            if round_num < len(items):
                selected.append(items[round_num])
                added_this_round = True
        if not added_this_round:
            break  # All categories exhausted
        round_num += 1

    logger.info(f"[Bucket 2] Selected {len(selected)} headlines (round-robin by priority):")
    for item in selected:
        logger.info(f"  [rank {item['priority_rank']} | {item['category']}] {item['title'][:70]}")

    return selected


# ---------------------------------------------------------------------------
# Bucket 3 — Finalise and return
# ---------------------------------------------------------------------------

def fetch_top_aviation_news(limit: int = 5) -> list[str]:
    """
    Public API — runs the full 3-bucket pipeline and returns plain headline strings.

    Bucket 1 → collect raw pool
    Bucket 2 → select by priority
    Bucket 3 → mark as shown and emit final list
    """
    global SHOWN_NEWS_HEADLINES

    # Bucket 1
    raw_pool = _bucket1_collect_raw_news()

    # Bucket 2
    selected = _bucket2_select_by_priority(raw_pool, select_count=limit)

    # Bucket 3 — mark shown and build output
    headlines = _finalise(selected)

    # Fallback: all feeds exhausted — reset and retry once
    if not headlines:
        logger.info("[Bucket 3] All feeds exhausted — resetting shown headlines and retrying.")
        SHOWN_NEWS_HEADLINES.clear()
        if os.path.exists(SHOWN_NEWS_FILE):
            os.remove(SHOWN_NEWS_FILE)
        raw_pool = _bucket1_collect_raw_news()
        selected = _bucket2_select_by_priority(raw_pool, select_count=limit)
        headlines = _finalise(selected)

    logger.info(f"[Bucket 3] Returning {len(headlines)} final headlines")
    return headlines


def fetch_top_aviation_news_detailed(limit: int = 5) -> list[dict]:
    """
    Same 3-bucket pipeline but returns dicts with 'title' and 'category' keys.
    Used by the Telegram bot to display the category tag alongside each headline.
    """
    global SHOWN_NEWS_HEADLINES

    # Bucket 1
    raw_pool = _bucket1_collect_raw_news()

    # Bucket 2
    selected = _bucket2_select_by_priority(raw_pool, select_count=limit)

    # Fallback
    if not selected:
        logger.info("[Bucket 3] All feeds exhausted — resetting shown headlines and retrying.")
        SHOWN_NEWS_HEADLINES.clear()
        if os.path.exists(SHOWN_NEWS_FILE):
            os.remove(SHOWN_NEWS_FILE)
        raw_pool = _bucket1_collect_raw_news()
        selected = _bucket2_select_by_priority(raw_pool, select_count=limit)

    # Bucket 3 — mark shown
    _finalise(selected)

    logger.info(f"[Bucket 3] Returning {len(selected)} final detailed headlines")
    return selected


def _finalise(selected: list[dict]) -> list[str]:
    """Mark selected headlines as shown and return their titles."""
    headlines = []
    for item in selected:
        title = item["title"]
        SHOWN_NEWS_HEADLINES.add(title)
        save_shown_news(title)
        headlines.append(title)
    return headlines
