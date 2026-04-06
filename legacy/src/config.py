"""Configuration and environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Instagram
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# LinkedIn
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API")

# File paths
POST_LOG_FILE = "data/post_history.csv"
SHOWN_NEWS_FILE = "data/shown_news.txt"

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("assets", exist_ok=True)

# Priority-ordered RSS search queries for Google News
PRIORITY_FEEDS = [
    ("Aircraft Crashes & Incidents", "aircraft+crash+OR+plane+crash+OR+aviation+incident+OR+emergency+landing"),
    ("Pilot Mayday", "pilot+mayday+OR+aviation+emergency+mayday+OR+distress+call+aviation"),
    ("Global Airshow", "airshow+OR+air+show+aviation+OR+RIAT+OR+Paris+Air+Show+OR+Dubai+Airshow"),
    ("Aviation Expo & FlightLogger", "FlightLogger+OR+aviation+expo+OR+aviation+training+software+OR+aviation+management+platform"),
    ("Aviation Jobs", "aviation+jobs+OR+pilot+hiring+OR+airline+recruitment+OR+pilot+shortage"),
    ("Aviation Fun Facts & Myths", "aviation+facts+OR+flying+myths+OR+aviation+history+OR+did+you+know+flying"),
    ("Aircraft Dealings", "aircraft+order+OR+airbus+boeing+deal+OR+planes+sold+OR+aircraft+purchase"),
]
