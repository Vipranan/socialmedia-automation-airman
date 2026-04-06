"""
Module: news_fetcher.py
3-bucket aviation news pipeline.

Bucket 1 — Fetch: pull all articles from RSS sources (last 48 hours)
Bucket 2 — Categorise: assign each article to one of 7 priority categories
Bucket 3 — Select: pick the most recent article from each category → up to 7 results

Priority order:
  1. Aircraft Crashes & Incidents
  2. Pilot Mayday Calls
  3. Airshows & Air Events
  4. Aircraft Expos & Trade Shows
  5. Aviation Jobs & Openings
  6. Aviation Fun Facts & Myths
  7. Airline Deals & Contracts
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime

import feedparser
import requests

from config.settings import (
    NEWS_API_KEY,
)  # NEWS_COUNT no longer needed — bucket selects 1 per category

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# RSS sources
# ---------------------------------------------------------------------------

RSS_SOURCES = [
    # Broad aviation search
    {
        "name": "Google News – Aviation",
        "url": "https://news.google.com/rss/search?q=aviation+airline+aircraft&hl=en-IN&gl=IN&ceid=IN:en",
    },
    {
        "name": "Google News – Incidents",
        "url": "https://news.google.com/rss/search?q=aircraft+crash+incident+emergency+mayday&hl=en&gl=US&ceid=US:en",
    },
    {
        "name": "Google News – Airline",
        "url": "https://news.google.com/rss/search?q=airline+deal+order+contract+jobs&hl=en&gl=US&ceid=US:en",
    },
    # Specialist aviation outlets
    {"name": "Simple Flying", "url": "https://simpleflying.com/feed/"},
    {"name": "Aviation Week", "url": "https://aviationweek.com/rss.xml"},
    {"name": "AeroTime", "url": "https://aerotime.aero/feed"},
    {"name": "Airways Magazine", "url": "https://airwaysmag.com/feed/"},
    {"name": "Airline Geeks", "url": "https://airlinegeeks.com/feed/"},
    {"name": "AirInsight", "url": "https://airinsight.com/feed/"},
    {"name": "The Aviation Herald", "url": "https://avherald.com/rss.xml"},
    {"name": "AviationSource", "url": "https://aviationsourcenews.com/feed/"},
    {"name": "Leeham News", "url": "https://leehamnews.com/feed/"},
    # Bing News – no API key required
    {
        "name": "Bing – Aviation",
        "url": "https://www.bing.com/news/search?q=aviation+airline&format=RSS",
    },
    {
        "name": "Bing – Aircraft Incidents",
        "url": "https://www.bing.com/news/search?q=aircraft+crash+incident&format=RSS",
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AirmanBot/1.0)"}

# NewsAPI queries (uses existing NEWS_API_KEY from settings)
NEWSAPI_URL = "https://newsapi.org/v2/everything"
NEWSAPI_QUERIES = [
    "aviation OR airline OR aircraft",
    "plane crash OR aircraft incident OR mayday",
    "airshow OR aviation expo OR aviation jobs",
]

# ---------------------------------------------------------------------------
# Priority categories (order = priority, index 0 is highest)
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "priority": 1,
        "name": "✈️  Crash & Incident",
        "keywords": [
            "crash",
            "crashed",
            "incident",
            "accident",
            "emergency landing",
            "collision",
            "missing",
            "wreckage",
            "fatality",
            "killed",
            "dead",
            "injured",
            "fire on board",
            "explosion",
            "runway excursion",
            "bird strike",
            "forced landing",
            "ditching",
            "hull loss",
        ],
    },
    {
        "priority": 2,
        "name": "🆘  Pilot Mayday",
        "keywords": [
            "mayday",
            "distress call",
            "declare emergency",
            "engine failure",
            "fuel emergency",
            "sos",
            "emergency declared",
            "squawk 7700",
            "loss of control",
            "pressurisation",
            "depressurisation",
        ],
    },
    {
        "priority": 3,
        "name": "🎪  Airshow & Air Event",
        "keywords": [
            "airshow",
            "air show",
            "aerobatic",
            "display team",
            "fly-in",
            "airfest",
            "aviation festival",
            "flight display",
            "air tattoo",
            "flying display",
            "formation flight",
            "airshow season",
        ],
    },
    {
        "priority": 4,
        "name": "🏛️  Expo & Trade Show",
        "keywords": [
            "expo",
            "exhibition",
            "trade show",
            "farnborough",
            "paris air show",
            "singapore airshow",
            "dubai airshow",
            "nbaa",
            "mro",
            "ebace",
            "aviation conference",
            "aviation summit",
            "aerospace expo",
        ],
    },
    {
        "priority": 5,
        "name": "💼  Jobs & Openings",
        "keywords": [
            "hiring",
            "job opening",
            "career",
            "recruitment",
            "vacancy",
            "pilot shortage",
            "cabin crew hiring",
            "cadet pilot",
            "cadet program",
            "training program",
            "pilot training",
            "aviation jobs",
            "job fair",
        ],
    },
    {
        "priority": 6,
        "name": "🧠  Fun Facts & History",
        "keywords": [
            "fun fact",
            "did you know",
            "myth",
            "history",
            "record",
            "anniversary",
            "heritage",
            "trivia",
            "first flight",
            "pioneer",
            "oldest airline",
            "aviation history",
            "legendary",
            "milestone",
            "aviation fact",
        ],
    },
    {
        "priority": 7,
        "name": "🤝  Deals & Contracts",
        "keywords": [
            "deal",
            "order",
            "contract",
            "partnership",
            "merger",
            "acquisition",
            "agreement",
            "fleet order",
            "purchase",
            "lease",
            "mou",
            "signed",
            "billion dollar",
            "multi-year",
            "code share",
            "joint venture",
        ],
    },
]


# ---------------------------------------------------------------------------
# Bucket 1 — Fetch all recent news
# ---------------------------------------------------------------------------


def _fetch_rss() -> list[dict]:
    """Fetch articles from all RSS sources.

    Returns:
        A list of article dictionaries from RSS feeds.
    """
    articles = []
    for source in RSS_SOURCES:
        try:
            resp = requests.get(source["url"], headers=HEADERS, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            parsed = _parse_feed(feed, source["name"])
            logger.info(f"{source['name']}: {len(parsed)} articles")
            articles.extend(parsed)
        except Exception as e:
            logger.warning(f"RSS fetch failed [{source['name']}]: {e}")
    return articles


def _fetch_newsapi() -> list[dict]:
    """Fetch from NewsAPI using the existing NEWS_API_KEY. Skips silently if key not set.

    Returns:
        A list of article dictionaries from NewsAPI.
    """
    if not NEWS_API_KEY:
        return []

    cutoff = datetime.now(UTC) - timedelta(hours=48)
    from_date = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
    articles = []

    for query in NEWSAPI_QUERIES:
        try:
            resp = requests.get(
                NEWSAPI_URL,
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 100,
                    "from": from_date,
                    "apiKey": NEWS_API_KEY,
                },
                headers=HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("articles", []):
                title = (item.get("title") or "").strip()
                if not title or "[Removed]" in title:
                    continue
                pub_str = item.get("publishedAt", "")
                try:
                    pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                except Exception:
                    pub_dt = None
                articles.append(
                    {
                        "title": title,
                        "description": (item.get("description") or "")[:300],
                        "url": item.get("url", ""),
                        "source": item.get("source", {}).get("name", "NewsAPI"),
                        "published_at": pub_dt.isoformat() if pub_dt else "",
                        "category": "",
                        "category_priority": 0,
                    }
                )
            logger.info(
                f"NewsAPI [{query[:30]}]: {len(data.get('articles', []))} articles"
            )
        except Exception as e:
            logger.warning(f"NewsAPI fetch failed [{query[:30]}]: {e}")

    return articles


def _fetch_all() -> list[dict]:
    """Fetch and deduplicate all articles from RSS and NewsAPI.

    Returns:
        A list of unique article dictionaries, sorted newest first.
    """
    all_articles = _fetch_rss() + _fetch_newsapi()

    # Deduplicate by title
    seen, unique = set(), []
    for a in all_articles:
        key = a["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    # Sort newest first
    unique.sort(key=lambda x: x["published_at"], reverse=True)
    logger.info(f"Bucket 1: {len(unique)} unique articles after dedup")
    return unique


# ---------------------------------------------------------------------------
# Bucket 2 — Categorise
# ---------------------------------------------------------------------------


def _categorise(articles: list[dict]) -> dict[int, list[dict]]:
    """Categorize articles by priority based on keywords.

    Args:
        articles: A list of article dictionaries to categorize.

    Returns:
        A dictionary keyed by priority (1–7), each value is a list of articles
        that match that category, sorted newest first.
        Unmatched articles are placed in priority 7 (Deals & Contracts) as fallback.
    """
    buckets: dict[int, list[dict]] = {c["priority"]: [] for c in CATEGORIES}

    for article in articles:
        text = (article["title"] + " " + article["description"]).lower()
        matched = False
        for cat in CATEGORIES:
            if any(kw in text for kw in cat["keywords"]):
                article["category"] = cat["name"]
                article["category_priority"] = cat["priority"]
                buckets[cat["priority"]].append(article)
                matched = True
                break  # assign to highest-priority matching category only

        if not matched:
            # Fallback: assign to lowest priority bucket
            article["category"] = CATEGORIES[-1]["name"]
            article["category_priority"] = CATEGORIES[-1]["priority"]
            buckets[CATEGORIES[-1]["priority"]].append(article)

    total = sum(len(v) for v in buckets.values())
    logger.info(
        f"Bucket 2: {total} articles categorised across {sum(1 for v in buckets.values() if v)} categories"
    )
    return buckets


# ---------------------------------------------------------------------------
# Bucket 3 — Select top article per category
# ---------------------------------------------------------------------------


def _select_top(buckets: dict[int, list[dict]]) -> list[dict]:
    """Pick the most recent article from each non-empty category, in priority order.

    Args:
        buckets: A dictionary of categorized articles by priority.

    Returns:
        A list of selected articles (one per category).
    """
    selected = []
    for cat in CATEGORIES:
        p = cat["priority"]
        if buckets.get(p):
            selected.append(buckets[p][0])  # already sorted newest first
    logger.info(f"Bucket 3: {len(selected)} articles selected (one per category)")
    return selected


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def fetch_aviation_news() -> list[dict]:
    """Full 3-bucket pipeline.

    Returns:
        Returns up to 7 articles — one per priority category, ordered 1→7.
        Each article has: title, description, url, source, published_at, category, category_priority.
    """
    raw = _fetch_all()
    if not raw:
        return []
    buckets = _categorise(raw)
    return _select_top(buckets)


def is_major_aviation_news(articles: list[dict]) -> bool:
    """Check if there are any articles available.

    Args:
        articles: A list of article dictionaries.

    Returns:
        True if there is at least one article, False otherwise.
    """
    return len(articles) > 0


# ---------------------------------------------------------------------------
# Feed parsing helpers
# ---------------------------------------------------------------------------


def _parse_feed(feed: feedparser.FeedParserDict, source_name: str) -> list[dict]:
    articles = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        if not title or "[Removed]" in title:
            continue

        pub_dt = _parse_date(entry)
        if pub_dt and (datetime.now(UTC) - pub_dt) > timedelta(hours=48):
            continue

        summary = entry.get("summary", "") or entry.get("description", "")
        summary = _strip_html(summary)[:300]

        articles.append(
            {
                "title": title,
                "description": summary or "No description available.",
                "url": entry.get("link", ""),
                "source": source_name,
                "published_at": pub_dt.isoformat() if pub_dt else "",
                "category": "",
                "category_priority": 0,
            }
        )
    return articles


def _parse_date(entry) -> datetime | None:
    for field in ("published", "updated"):
        raw = entry.get(field)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        except Exception:
            pass
    for field in ("published_parsed", "updated_parsed"):
        parsed = entry.get(field)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=UTC)
            except Exception:
                pass
    return None


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()
