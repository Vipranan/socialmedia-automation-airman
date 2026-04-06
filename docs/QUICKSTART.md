# AIRMAN Social Media Bot - Quick Start Guide

Get the AIRMAN Instagram automation bot up and running in minutes. This guide covers installation, configuration, and basic usage.

---

## 📋 Prerequisites

### Required
1. **Python 3.12+** installed on your system
2. **Telegram Bot Token** - Get one from [@BotFather](https://t.me/botfather) on Telegram
3. **Instagram Account** - Username and password for posting
4. **Google Gemini API Key** - Free key from [Google AI Studio](https://aistudio.google.com/)
   - Must have access to `gemini-2.5-flash` (text generation)
   - Must have access to `imagen-4.0-generate-001` (image generation)

### Optional but Recommended
- **AIRMAN logo** - PNG file in `assets/` directory (transparent PNG)
- **LinkedIn API credentials** - For dual-platform posting

---

## 🔧 Installation

### Step 1: Clone or Download Project
```bash
git clone https://github.com/Vipranan/socialmedia-automation-airman.git
cd socialmedia-automation-airman
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `python-telegram-bot[job-queue]` - Telegram bot framework
- `instagrapi` - Instagram API client
- `Pillow` - Image processing
- `google-genai` - Google AI SDK
- `feedparser` - RSS feed parser
- `python-dotenv` - Environment management
- `httpx` - HTTP client
- `requests` - HTTP library

### Step 3: Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_CHAT_ID=your_telegram_chat_id
TELEGRAM_ADMIN_IDS=123456789
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
GEMINI_API=your_google_gemini_api_key

# Optional LinkedIn Support
LINKEDIN_ACCESS_TOKEN=your_access_token
```

**Important**: Never commit `.env` to version control. It's already in `.gitignore`.

### Step 4: Add Brand Assets

Place your `logo.png` file in the `assets/` directory. This logo will be composited onto all generated Instagram posts.

```bash
cp /path/to/your/logo.png assets/logo.png
```

---

## 🚀 Running the Bot

### Start the Bot
```bash
python main.py
```

You should see:
```
INFO - Logging into Instagram as [username]...
INFO - Successfully logged into Instagram.
INFO - Application started and polling for updates.
```

### Test the Connection

1. Open Telegram and find your bot (search for the username you set in BotFather)
2. Send `/start` - You should receive a welcome message
3. Send `/help` - View all available commands

---

## 📱 Using the Bot

### Manual News Posting

**Step 1**: Send `/news` command

The bot will:
- Fetch top 7 aviation headlines (one per category)
- Display them as interactive buttons

**Step 2**: Click one of the options

The bot will:
1. Generate an Instagram caption using Gemini 2.5 Flash
2. Create a hyper-realistic image using Imagen 4.0
3. Apply AIRMAN branding (add logo, website URL)
4. Show preview for approval
5. Post to Instagram and/or LinkedIn

**Timeline**: Entire process takes 15-30 seconds depending on API response times.

---

### Auto-Pilot Mode

Enable automated posting:
```
/startauto
```

This activates:
- **News Posting**: Every 1 hour, automatically fetches and posts aviation news
- **Festival Checks**: Every 1 hour, checks for special occasions and posts themed content

Disable auto-pilot:
```
/stopauto
```

---

### Festival Posts

Generate festival-themed posts manually:
```
/forcefestival Diwali
/forcefestival Christmas
/forcefestival Independence Day
```

The bot will create a special branded post for that occasion.

**Built-in Festival Calendar**:
- January 1 - New Year
- January 14 - Makar Sankranti & Pongal
- January 26 - Republic Day
- February 14 - Valentine's Day
- March 8 - International Women's Day
- April 14 - Baisakhi
- April 22 - Earth Day
- August 15 - Independence Day
- August 19 - National Aviation Day
- October 2 - Gandhi Jayanti
- October 31 - Halloween
- November 1 - Diwali Season
- December 25 - Christmas

---

## 🎨 What Happens Behind the Scenes

### Caption Generation
Gemini 2.5 Flash receives a system prompt defining AIRMAN's brand voice:
- Premium, futuristic aviation tech brand
- Educational, empowering, tech-forward tone
- Includes relevant emojis (✈️ 🚀 ☁️) and hashtags
- Always appends `https://www.theairman.org/`

### Image Generation
Imagen 4.0 creates images based on prompts optimized for Instagram.

### Image Processing (Pillow)
1. Resize to 1080x1080 (Instagram square format)
2. Composite AIRMAN logo with alpha blending
3. Add website URL at bottom
4. Save as high-quality PNG

### Instagram Publishing
Posts via Instagrapi with the finalized image and AI-generated caption.

---

## 🧪 Testing Your Setup

### Run Test Suite
```bash
pytest tests/ -v
```

Expected output: 6 tests passing

### Test Individual Components

**Test Gemini API**:
```bash
python tests/api_test.py
```

**Test Instagram Login**:
```bash
python tests/test_ig.py
```

**Test Telegram Bot**:
```bash
python tests/test_tg.py
```

**List Available AI Models**:
```bash
python tests/list_models.py
```

---

## 🧹 Code Quality

This project uses professional development tools:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check .

# Run type checking
mypy modules/ --config-file=pyproject.toml

# Format code
ruff format .
```

---

## 🐛 Troubleshooting

### Bot Won't Start

**Error**: `Missing required environment variables`
- **Fix**: Check `.env` file exists and has all required variables

**Error**: `Failed to login to Instagram`
- **Fix**: Verify Instagram username/password are correct
- **Fix**: Check if Instagram requires 2FA or captcha
- **Fix**: Avoid special characters in password

### Image Generation Fails

**Error**: `Failed to generate image`
- **Fix**: Verify Gemini API key has Imagen access
- **Fix**: Check API quota limits at [Google AI Studio](https://aistudio.google.com/)

### Posts Not Appearing on Instagram

**Error**: `Image_process_failed`
- **Fix**: Check `logo.png` exists in `assets/`
- **Fix**: Verify Instagram account isn't restricted

**Error**: `Challenge Required`
- **Fix**: Instagram detected unusual activity - log in manually first
- **Fix**: Wait a few hours before retrying

### Duplicate Headlines

**Issue**: Same news appearing repeatedly
- **Fix**: Delete `data/shown_news.txt` to reset tracking

---

## 📊 Monitoring

### Log Files

Check `logs/bot.log` for detailed execution logs:
```bash
tail -f logs/bot.log
```

### Tracking Files

- `data/shown_news.txt` - Previously shown headlines (prevents duplicates)
- `data/posted_festivals_2026.txt` - Posted festivals for current year
- `data/feedback.db` - Post records and feedback

---

## ⚙️ Advanced Configuration

### Adjust Auto-Pilot Timing

Edit `main.py` to change posting frequency:
```python
# Current: Every 1 hour (3600 seconds)
context.job_queue.run_repeating(auto_post_news, interval=3600, first=10)
```

### Modify Festival Calendar

Edit `config/settings.py`:
```python
INDIAN_FESTIVALS = {
    (1, 1): "New Year",
    (12, 31): "New Year's Eve",  # Add new festival
    # ... more dates
}
```

---

## 🔐 Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use strong passwords** - Especially for Instagram
3. **Rotate API keys** - Periodically regenerate Gemini API keys
4. **Monitor usage** - Check Google AI Studio for API quota

---

## 📚 Project Structure

```
airman-social-bot/
├── main.py                    # Entry point
├── run.py                     # Runner script
├── config/settings.py         # Configuration
├── modules/                   # Core modules
│   ├── gemini_client.py       # AI integration
│   ├── news_fetcher.py       # News fetching
│   ├── image_branding.py     # Image processing
│   ├── instagram_poster.py   # Instagram posting
│   └── feedback_store.py    # Post tracking
├── tests/                     # Test suite
├── assets/                    # Brand assets
├── data/                      # Data files
└── logs/                      # Log files
```

---

## 🆘 Getting Help

**Common Issues**: See troubleshooting section above

**API Documentation**:
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google GenAI SDK](https://ai.google.dev/)
- [Instagrapi Docs](https://github.com/adw0rd/instagrapi)

**AIRMAN Brand**: https://www.theairman.org/

---

**Ready to automate your social media? Run `python main.py` and send `/start` to your bot!** ✈️