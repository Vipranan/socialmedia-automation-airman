# Testing Scripts

This directory contains scripts to test individual components of the bot.

## Available Tests

### API Tests

**api_test.py** - Test Google Gemini API
```bash
python tests/api_test.py
```
Tests both text generation (Gemini 2.5 Flash) and image generation (Imagen 4.0).

**test_ig.py** - Test Instagram Login
```bash
python tests/test_ig.py
```
Validates Instagram credentials and login functionality.

**test_tg.py** - Test Telegram Bot
```bash
python tests/test_tg.py
```
Tests basic Telegram bot connectivity and commands.

### Utility Scripts

**list_models.py** - List Available GenAI Models
```bash
python tests/list_models.py
```
Lists all available Google GenAI models accessible with your API key.

**test_font.py** - Test Font Rendering
```bash
python tests/test_font.py
```
Tests font availability and text rendering on images.

**test_font2.py** - Additional Font Tests
```bash
python tests/test_font2.py
```
Additional font rendering tests.

---

## Running Tests

Before running the main bot, it's recommended to test each component:

```bash
# 1. Test Gemini API
python tests/api_test.py

# 2. Test Instagram login
python tests/test_ig.py

# 3. Test Telegram bot
python tests/test_tg.py

# 4. List available models
python tests/list_models.py
```

All tests require a properly configured `.env` file in the project root.
