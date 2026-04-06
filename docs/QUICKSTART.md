# AIRMAN Social Media Bot - Quick Start Guide

Get the AIRMAN Instagram automation bot up and running in minutes.

---

## 📋 Prerequisites

- **Python 3.12+**
- **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
- **Instagram Account** - Username and password
- **Google Gemini API Key** - From [Google AI Studio](https://aistudio.google.com/)
- **AIRMAN logo** - PNG in `assets/` directory

---

## 🔧 Installation

### Step 1: Clone Project
```bash
git clone https://github.com/Vipranan/socialmedia-automation-airman.git
cd socialmedia-automation-airman
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_CHAT_ID=your_chat_id
TELEGRAM_ADMIN_IDS=123456789
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
GEMINI_API=your_gemini_key
LINKEDIN_ACCESS_TOKEN=your_token  # optional
```

### Step 4: Add Logo
```bash
cp /path/to/logo.png assets/logo.png
```

---

## 🚀 Running the Bot

```bash
python main.py
```

Test: Send `/start` to your bot on Telegram.

---

## 🤖 Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot |
| `/help` | Show commands |
| `/news` | Fetch & post news |
| `/font` | Choose font style |
| `/startauto` | Enable auto-pilot |
| `/stopauto` | Disable auto-pilot |
| `/forcefestival Diwali` | Manual festival post |

---

## 🎯 Features

- **Aviation News** - Fetches from Google News RSS feeds
- **AI Captions** - Gemini 2.5 Flash generates brand-aligned captions
- **Image Generation** - Imagen 4.0 creates images
- **Branding** - Auto-adds logo and website URL
- **Dual Posting** - Instagram + LinkedIn
- **Auto-Pilot** - Hourly scheduled posts
- **Festival Calendar** - Auto-detects special days

---

## 📁 Project Structure

```
airman-social-bot/
├── main.py                  # Entry point
├── config/settings.py       # Configuration
├── modules/                 # Core modules
│   ├── gemini_client.py     # AI integration
│   ├── news_fetcher.py      # News fetching
│   ├── image_branding.py    # Image processing
│   ├── instagram_poster.py  # Instagram posting
│   └── feedback_store.py    # Post tracking
├── src/                     # Utilities
│   ├── services/            # Core services
│   └── prompts/             # AI prompts
├── tests/                   # Test scripts
├── assets/                  # Brand assets
└── data/                    # Data files
```

---

## 🐛 Troubleshooting

**Bot won't start**: Check `.env` has all required variables

**Instagram login fails**: Verify credentials, check for 2FA

**Image generation fails**: Verify Gemini API has Imagen access

---

## 📚 More Info

- [Architecture](docs/ARCHITECTURE.md)
- [Documentation](docs/CODEBASE_DOCUMENTATION.md)

**Ready? Run `python main.py` and start automating!** ✈️