"""News tracking utilities to avoid duplicates."""
import os
from src.config import SHOWN_NEWS_FILE


def load_shown_news():
    """Load previously shown news headlines."""
    if os.path.exists(SHOWN_NEWS_FILE):
        with open(SHOWN_NEWS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_shown_news(headline):
    """Save a headline to the shown news file."""
    with open(SHOWN_NEWS_FILE, "a") as f:
        f.write(f"{headline}\n")
