"""
Module: instagram_poster.py
Publishes images to Instagram using instagrapi (username + password login).
"""

import logging
import os
import time

from instagrapi import Client

from config.settings import INSTAGRAM_PASSWORD, INSTAGRAM_USERNAME

logger = logging.getLogger(__name__)

SESSION_FILE = "data/instagram_session.json"
_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is not None:
        return _client

    cl = Client()
    cl.delay_range = [2, 5]  # add human-like delay between requests

    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logger.info("Logged in using saved session.")
        except Exception:
            logger.warning("Saved session invalid — logging in fresh.")
            cl = Client()
            cl.delay_range = [2, 5]
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    else:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        logger.info("Logged in fresh to Instagram.")

    cl.dump_settings(SESSION_FILE)
    _client = cl
    return _client


def post_to_instagram(image_path: str, caption: str) -> str:
    cl = _get_client()
    time.sleep(3)  # small pause before posting
    media = cl.photo_upload(image_path, caption)
    post_id = str(media.pk)
    logger.info(f"Post published successfully. Post ID: {post_id}")
    return post_id
