"""Tests for news_fetcher module."""

import pytest
from modules.news_fetcher import fetch_aviation_news, _categorise


def test_fetch_aviation_news_returns_list():
    """Test that fetch_aviation_news returns a list."""
    result = fetch_aviation_news()
    assert isinstance(result, list)


def test_categorise_assigns_categories(sample_article):
    """Test that categorise assigns categories to articles."""
    result = _categorise([sample_article])
    assert isinstance(result, dict)
    assert 1 in result or 8 in result
