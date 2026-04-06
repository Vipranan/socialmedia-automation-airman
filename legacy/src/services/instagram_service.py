"""Instagram service for posting content."""
from instagrapi import Client

from src.config import INSTAGRAM_PASSWORD, INSTAGRAM_USERNAME
from src.logger import logger

# Initialize Instagram Client
cl = Client()


def login_instagram():
    """Login to Instagram."""
    logger.info(f"Logging into Instagram as {INSTAGRAM_USERNAME}...")
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    logger.info("Successfully logged into Instagram.")


def get_instagram_client():
    """Get the Instagram client instance."""
    return cl
