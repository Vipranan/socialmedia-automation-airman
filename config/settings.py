"""Centralised settings for all modules. Reads from .env via python-dotenv."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID: str | None = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
TELEGRAM_ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()
]

# --- Instagram ---
INSTAGRAM_USERNAME: str | None = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD: str | None = os.getenv("INSTAGRAM_PASSWORD")

# --- LinkedIn ---
LINKEDIN_ACCESS_TOKEN: str | None = os.getenv("LINKEDIN_ACCESS_TOKEN")

# --- Gemini / Vertex AI ---
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API")
GEMINI_TEXT_MODEL: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "imagen-4.0-generate-001")
GCP_PROJECT_ID: str | None = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")

# --- NewsAPI (optional — modules skip gracefully if not set) ---
NEWS_API_KEY: str | None = os.getenv("NEWS_API_KEY")

# --- Brand ---
COMPANY_NAME: str = "Airman Aeronautics"
COMPANY_WEBSITE: str = "https://www.theairman.org/"
COMPANY_LOGO_PATH: str = os.getenv("COMPANY_LOGO_PATH", "assets/airman.png")

# --- Paths ---
IMAGE_OUTPUT_DIR: str = "data/images"
FEEDBACK_DB_PATH: str = "data/feedback.db"
POST_LOG_FILE: str = "data/post_history.csv"

# --- Festival calendar (month, day) → name ---
INDIAN_FESTIVALS: dict[tuple[int, int], str] = {
    (1, 1): "New Year",
    (1, 14): "Makar Sankranti & Pongal",
    (1, 26): "Republic Day",
    (2, 14): "Valentine's Day",
    (3, 8): "International Women's Day",
    (4, 14): "Baisakhi",
    (4, 22): "Earth Day",
    (8, 15): "Independence Day",
    (8, 19): "National Aviation Day",
    (10, 2): "Gandhi Jayanti",
    (10, 31): "Halloween",
    (11, 1): "Diwali Season",
    (12, 25): "Christmas",
}

# --- Ensure directories exist ---
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("assets", exist_ok=True)
