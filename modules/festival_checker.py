"""
Module: festival_checker.py
Detects Indian festivals and major aviation events for the current date.
Returns festival name if today matches, otherwise None.
"""

from datetime import date

from config.settings import INDIAN_FESTIVALS


def get_todays_festival() -> str | None:
    """
    Check if today is an Indian festival or major event.
    Returns the festival name string, or None.
    """
    today = date.today()
    key = (today.month, today.day)
    return INDIAN_FESTIVALS.get(key)


def is_festival_day() -> bool:
    return get_todays_festival() is not None
