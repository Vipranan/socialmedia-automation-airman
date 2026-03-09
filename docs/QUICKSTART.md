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
- **macOS** - For native Avenir/Futura fonts (falls back to Arial on other systems)
- **AIRMAN logo** - PNG file in `assets/` directory (transparent PNG)

---

## 🔧 Installation

### Step 1: Clone or Download Project
```bash
git clone <repository-url>
cd airman-social-bot
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

### Step 3: Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
GEMINI_API=your_google_gemini_api_key

# Optional LinkedIn Support
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
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
- Fetch top 5 trending aviation headlines from Google News
- Display them as interactive buttons (Option 1-5)

**Step 2**: Click one of the options

The bot will:
1. Generate an Instagram caption using Gemini 2.5 Flash
2. Create a hyper-realistic image using Imagen 4.0
3. Apply AIRMAN branding (resize to 1080x1080, add logo)
4. Post to Instagram automatically
5. Send you a preview in Telegram with the caption

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
- January 26 - Republic Day (India)
- February 14 - Valentine's Day
- March 8 - International Women's Day
- April 22 - Earth Day
- August 15 - Independence Day (India)
- August 19 - National Aviation Day
- October 2 - Gandhi Jayanti
- October 24 - United Nations Day
- November 11 - National Education Day (India)
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
Imagen 4.0 creates images based on prompts like:
```
A hyper-realistic, highly cinematic, premium, modern aviation poster 
representing: '[headline]'. The text '[poster_title]' MUST be beautifully 
integrated into the scene environment. High quality, 8k resolution, aspirational.
```

### Image Processing (Pillow)
1. Resize to 1080x1080 (Instagram square format)
2. Composite AIRMAN logo with alpha blending
3. Save as high-quality JPEG (95% quality)

### Instagram Publishing
Posts via Instagrapi with:
- Finalized image
- AI-generated caption
- Brand URL
- Relevant hashtags

---

## 🧪 Testing Your Setup

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

## 🐛 Troubleshooting

### Bot Won't Start

**Error**: `Missing required environment variables`
- **Fix**: Check `.env` file exists and has all 4 required variables

**Error**: `Failed to login to Instagram`
- **Fix**: Verify Instagram username/password are correct
- **Fix**: Check if Instagram requires 2FA or captcha (try logging in manually first)
- **Fix**: Avoid special characters in password that need escaping

### Image Generation Fails

**Error**: `Failed to generate image`
- **Fix**: Verify Gemini API key has Imagen access
- **Fix**: Check API quota limits at [Google AI Studio](https://aistudio.google.com/)
- **Fix**: Ensure internet connection is stable

### Posts Not Appearing on Instagram

**Error**: `Image_process_failed`
- **Fix**: Image is automatically resized to 1080x1080, but check `logo.png` exists
- **Fix**: Verify Instagram account isn't restricted or shadowbanned

**Error**: `Challenge Required`
- **Fix**: Instagram detected unusual activity - log in manually via app/browser first
- **Fix**: Wait a few hours before retrying

### Duplicate Headlines

**Issue**: Same news appearing repeatedly
- **Fix**: Delete `shown_news.txt` to reset tracking
- **Fix**: Check if Google News RSS feed is updating (may be stale)

### Font Issues

**Issue**: Text looks wrong on generated images
- **Fix**: On macOS, fonts should work automatically (Avenir/Futura)
- **Fix**: On other systems, Arial is used as fallback
- **Fix**: Install custom fonts and update `format_image_for_instagram()` function

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

---

## ⚙️ Advanced Configuration

### Adjust Auto-Pilot Timing

Edit `main.py` to change posting frequency:
```python
# Current: Every 1 hour
context.job_queue.run_repeating(auto_post_news, interval=3600, first=10)

# Change to every 2 hours:
context.job_queue.run_repeating(auto_post_news, interval=7200, first=10)
```

### Modify Festival Calendar

Edit the `FESTIVALS` dictionary in `src/services/content_service.py`:
```python
FESTIVALS = {
    "01-01": "New Year",
    "12-31": "New Year's Eve",  # Add new festival
    # ... more dates
}
```

### Customize Brand Voice

Edit the system prompts in `src/prompts/news_prompts.py` and `src/prompts/festival_prompts.py` to adjust caption styles.

---

## 🔐 Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use strong passwords** - Especially for Instagram
3. **Rotate API keys** - Periodically regenerate Gemini API keys
4. **Monitor usage** - Check Google AI Studio for API quota
5. **Backup tracking files** - Save `shown_news.txt` and festival logs

---

## 📚 Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
- Check [CODEBASE_DOCUMENTATION.md](./CODEBASE_DOCUMENTATION.md) for complete technical reference
- Explore `main.py` to customize bot behavior
- Add more festival dates or adjust posting schedules

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
