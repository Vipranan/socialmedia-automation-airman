# Source Code Structure

## Overview
This directory contains the organized, modular source code for the AIRMAN Social Media Automation Bot.

## Directory Structure

### `config.py`
Central configuration file containing:
- Environment variables
- API keys and credentials
- File paths
- RSS feed priorities

### `logger.py`
Logging configuration for the entire application.

### `services/`
External service integrations:
- `news_service.py` - Fetches aviation news from RSS feeds
- `instagram_service.py` - Instagram API client and posting
- `linkedin_service.py` - LinkedIn API posting
- `image_service.py` - Image generation using Gemini Imagen
- `content_service.py` - Content generation using Gemini AI

### `handlers/`
Telegram bot command handlers:
- `news_handler.py` - Handles /news command and news selection
- `auto_handler.py` - Handles /startauto and /stopauto commands
- `festival_handler.py` - Handles festival posting

### `utils/`
Utility functions:
- `csv_logger.py` - Logs posts to CSV file
- `news_tracker.py` - Tracks shown news to avoid duplicates

### `bot.py`
Main bot initialization, command registration, and application startup.

## Import Examples

```python
# Import configuration
from src.config import TELEGRAM_BOT_TOKEN, PRIORITY_FEEDS

# Import services
from src.services import fetch_top_aviation_news, post_to_linkedin

# Import utilities
from src.utils import log_post_to_csv, load_shown_news

# Import logger
from src.logger import logger
```

## Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Injection**: Services are loosely coupled
3. **Configuration Centralization**: All config in one place
4. **Error Handling**: Comprehensive logging and error handling
5. **Async/Await**: Proper async patterns for I/O operations
