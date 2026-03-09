# Project Refactoring Guide

## New Project Structure

```
socialmedia-automation-airman/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration and environment variables
│   ├── logger.py                 # Logging configuration
│   ├── bot.py                    # Main bot logic (to be created)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── news_service.py       # RSS news fetching
│   │   ├── image_service.py      # Image generation & formatting (to be created)
│   │   ├── content_service.py    # Content generation with Gemini (to be created)
│   │   ├── instagram_service.py  # Instagram posting
│   │   └── linkedin_service.py   # LinkedIn posting
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── news_handler.py       # /news command handlers (to be created)
│   │   ├── auto_handler.py       # Auto-posting handlers (to be created)
│   │   └── festival_handler.py   # Festival posting handlers (to be created)
│   └── utils/
│       ├── __init__.py
│       ├── csv_logger.py         # CSV logging utilities
│       └── news_tracker.py       # News tracking to avoid duplicates
├── data/                         # Data files (CSV, shown news)
├── logs/                         # Log files
├── assets/                       # Images and assets
├── tests/                        # Test files
├── docs/                         # Documentation
├── main.py                       # Original monolithic file (keep for now)
├── run.py                        # New entry point
├── requirements.txt
└── README.md
```

## Migration Status

### ✅ Completed
- `src/config.py` - All configuration and environment variables
- `src/logger.py` - Logging setup
- `src/utils/csv_logger.py` - CSV logging functionality
- `src/utils/news_tracker.py` - News tracking utilities
- `src/services/news_service.py` - News fetching from RSS feeds
- `src/services/instagram_service.py` - Instagram client and login
- `src/services/linkedin_service.py` - LinkedIn posting API
- `run.py` - New entry point

### 🔄 To Be Created
- `src/services/image_service.py` - Image generation and formatting
- `src/services/content_service.py` - Content generation with Gemini AI
- `src/handlers/news_handler.py` - News command handlers
- `src/handlers/auto_handler.py` - Auto-posting handlers
- `src/handlers/festival_handler.py` - Festival handlers
- `src/bot.py` - Main bot initialization and command registration

## Benefits of New Structure

1. **Modularity**: Each service has a single responsibility
2. **Testability**: Easy to unit test individual components
3. **Maintainability**: Changes are isolated to specific modules
4. **Scalability**: Easy to add new features without touching existing code
5. **Readability**: Clear separation of concerns

## How to Use

### Current (Old Way)
```bash
python main.py
```

### New Way (After Full Migration)
```bash
python run.py
```

## Next Steps

1. Extract image generation functions to `src/services/image_service.py`
2. Extract content generation to `src/services/content_service.py`
3. Extract Telegram handlers to `src/handlers/`
4. Create `src/bot.py` with main bot logic
5. Test the new structure
6. Update documentation
7. Archive or remove old `main.py`
