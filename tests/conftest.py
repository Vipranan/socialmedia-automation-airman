"""Pytest configuration and fixtures."""

import os

import pytest

# Set test environment
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
os.environ["TELEGRAM_ADMIN_CHAT_ID"] = "123456"
os.environ["TELEGRAM_ADMIN_IDS"] = "123456"
os.environ["GEMINI_API"] = "test_key"
os.environ["INSTAGRAM_USERNAME"] = "test_user"
os.environ["INSTAGRAM_PASSWORD"] = "test_pass"
os.environ["LINKEDIN_ACCESS_TOKEN"] = "test_token"


@pytest.fixture
def temp_image_dir(tmp_path):
    """Create temporary image directory."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    return img_dir


@pytest.fixture
def sample_article():
    """Sample news article for testing."""
    return {
        "title": "Test Aviation News: New Aircraft Order",
        "description": "Airline places order for 50 new aircraft.",
        "url": "https://example.com/news",
        "source": "Test Source",
        "published_at": "2024-01-15T10:00:00+00:00",
        "category": "Deals & Contracts",
        "category_priority": 7,
    }
