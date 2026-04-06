"""Tests for gemini_client module."""

from unittest.mock import patch

from modules.gemini_client import generate_news_headline


@patch("modules.gemini_client._generate_text")
def test_generate_news_headline(mock_generate):
    """Test headline generation."""
    mock_generate.return_value = "New Aircraft Order Confirmed"
    result = generate_news_headline("Airline announces new order")
    assert isinstance(result, str)
    assert len(result.split()) <= 7
