# AIRMAN Social Media Automation Bot

> **Intelligent Instagram content automation for the AIRMAN aviation brand**

An AI-powered Telegram bot that automates the complete social media workflow: fetching aviation news → generating captions with Gemini 2.5 Flash → creating images with Imagen 4.0 → posting to Instagram.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Add logo
# Place logo.png in assets/ folder

# 4. Run the bot
python main.py
```

---

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Setup and basic usage
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design
- **[Complete Documentation](docs/CODEBASE_DOCUMENTATION.md)** - Technical reference

---

## 📁 Project Structure

```
airman-social-bot/
├── main.py                    # Entry point for Telegram bot
├── run.py                     # Convenience runner script
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
│
├── config/                    # Configuration
│   └── settings.py           # Centralized settings
│
├── modules/                   # Core bot modules
│   ├── telegram_bot.py       # Telegram bot handlers
│   ├── orchestrator.py       # Workflow orchestration
│   ├── gemini_client.py      # Gemini AI integration
│   ├── news_fetcher.py       # News fetching (RSS/API)
│   ├── image_branding.py     # Image processing & branding
│   ├── instagram_poster.py   # Instagram publishing
│   ├── linkedin_poster.py   # LinkedIn publishing
│   ├── festival_checker.py  # Festival calendar
│   └── feedback_store.py    # Post tracking & feedback
│
├── src/                       # Utility modules
│   ├── logger.py             # Logging setup
│   ├── config.py             # App configuration
│   ├── services/             # Core services
│   │   ├── news_service.py
│   │   ├── image_service.py
│   │   ├── content_service.py
│   │   ├── linkedin_service.py
│   │   └── instagram_service.py
│   ├── prompts/              # AI prompts
│   │   ├── festival_prompts.py
│   │   ├── news_prompts.py
│   │   └── font_styles.py
│   └── utils/                # Helper utilities
│       ├── csv_logger.py
│       └── news_tracker.py
│
├── docs/                     # Documentation
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   ├── CODEBASE_DOCUMENTATION.md
│   └── ORGANIZATION_*.md
│
├── tests/                    # Testing scripts
│   ├── test_tg.py
│   ├── test_ig.py
│   ├── api_test.py
│   └── list_models.py
│
├── assets/                   # Brand assets
│   └── logo.png             # AIRMAN logo
│
├── data/                     # Data files (auto-generated)
│   ├── feedback.db           # Post records & feedback
│   ├── post_history.csv     # Posting history
│   ├── instagram_session.json
│   └── images/              # Generated images
│
└── logs/                     # Application logs
```

---

## 🎯 Features

- ✈️ **Aviation News Pipeline** - Fetch trending headlines from Google News
- 🤖 **AI Caption Generation** - Gemini 2.5 Flash creates brand-aligned captions
- 🎨 **Image Synthesis** - Imagen 4.0 generates hyper-realistic 8K images
- 📱 **Instagram Publishing** - Automatic posting with branding
- 💼 **LinkedIn Integration** - Automated dual-platform posting
- ⏰ **Auto-Pilot Mode** - Scheduled news and festival posts
- 🎉 **Festival Calendar** - Automatic themed posts for special occasions

---

## 🛠️ Tech Stack

- **AI/ML**: Google Gemini 2.5 Flash, Imagen 4.0
- **Bot Framework**: python-telegram-bot
- **Social Media**: Instagrapi, LinkedIn API
- **Image Processing**: Pillow (PIL)
- **Content Sourcing**: feedparser, requests
- **Database**: SQLite (feedback tracking)

---

## 📋 Requirements

- Python 3.12+
- Telegram Bot Token
- Telegram Admin Chat ID & User IDs
- Instagram credentials
- Google Gemini API key
- AIRMAN logo (PNG)
- (Optional) LinkedIn API credentials

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot |
| `/help` | Show commands |
| `/news` | Fetch & post news |
| `/font` | Choose Google Font style |
| `/startauto` | Enable auto-pilot |
| `/stopauto` | Disable auto-pilot |
| `/forcefestival [Name]` | Manual festival post |

---

## 🔒 Security

- All credentials stored in `.env` (gitignored)
- No hardcoded secrets
- API key validation on startup

---

## 📄 License

Built for AIRMAN - https://www.theairman.org/

---

## 🆘 Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: Check [Troubleshooting](docs/CODEBASE_DOCUMENTATION.md#13-troubleshooting)
- **AIRMAN**: https://www.theairman.org/