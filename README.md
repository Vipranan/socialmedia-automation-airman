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
├── pyproject.toml             # Project config (ruff, mypy, pytest)
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── .pre-commit-config.yaml   # Git hooks for code quality
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
│   ├── prompts/              # AI prompts
│   │   ├── festival_prompts.py
│   │   └── font_styles.py
│   └── utils/                # Helper utilities
│       └── csv_logger.py
│
├── legacy/                    # Deprecated code (reference only)
│   └── src/                  # Original src/ (superseded by modules/)
│
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_gemini_client.py
│   ├── test_news_fetcher.py
│   └── test_feedback_store.py
│
├── docs/                     # Documentation
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   └── CODEBASE_DOCUMENTATION.md
│
├── assets/                   # Brand assets
│   └── logo.png             # AIRMAN logo
│
├── data/                     # Data files (auto-generated)
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
- **Content Sourcing**: feedparser

---

## 🧪 Testing & Code Quality

```bash
# Run tests
pytest tests/ -v

# Lint code
ruff check .

# Type checking
mypy modules/ --config-file=pyproject.toml

# Install pre-commit hooks
pre-commit install
```

---

## 📋 Requirements

- Python 3.12+
- Telegram Bot Token
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