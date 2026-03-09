# AIRMAN Social Media Bot - Project Structure

This document describes the organized file structure of the project.

---

## 📁 Directory Tree

```
airman-social-bot/
│
├── 📄 main.py                          # Core application entry point
├── 📄 run.py                           # Convenience runner script
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .env.example                     # Environment variables template
├── 📄 .env                            # Environment variables (gitignored)
├── 📄 .gitignore                      # Git ignore rules
├── 📄 README.md                       # Project overview
│
├── 📂 src/                            # Source code modules
│   ├── 📄 config.py                   # App configuration & environment
│   ├── 📄 logger.py                   # Logging setup
│   ├── 📂 services/                   # Core business logic (news, images, IG, etc.)
│   ├── 📂 utils/                      # Helper utilities (CSV logger, news tracker)
│   └── 📂 prompts/                    # Generative AI prompts
│
├── 📂 docs/                           # Documentation
│   ├── README.md                      # Documentation index
│   ├── QUICKSTART.md                  # Setup and usage guide
│   ├── ARCHITECTURE.md                # System architecture
│   ├── PROJECT_STRUCTURE.md           # This file
│   └── CODEBASE_DOCUMENTATION.md      # Complete technical reference
│
├── 📂 tests/                          # Testing scripts
│   ├── README.md                      # Testing guide
│   ├── api_test.py                    # Test APIs
│   └── test_*.py                      # Unit/integration tests
│
├── 📂 assets/                         # Brand assets and images
│   ├── README.md                      # Assets documentation
│   ├── logo.png                       # AIRMAN brand logo (required)
│   ├── sunset.jpg                     # Sample image for testing
│   ├── gemini_test_output.jpg         # Test output (generated)
│   └── generated_*.jpg                # AI-generated images (temporary)
│
├── 📂 data/                           # Application data files
│   ├── .gitkeep                       # Keep directory in git
│   ├── shown_news.txt                 # Headline tracking (auto-generated)
│   └── posted_festivals_*.txt         # Festival tracking (auto-generated)
│
├── 📂 scripts/                        # Shell/helper scripts
│
└── 📂 logs/                           # Application logs
    ├── .gitkeep                       # Keep directory in git
    └── bot.log                        # Main application log (auto-generated)
```

---

## 📋 File Descriptions

### Root Level Files

| File | Purpose | Type |
|------|---------|------|
| `main.py` | Core bot application entry point | Application |
| `run.py` | Convenience script for running the bot | Application |
| `requirements.txt` | Python package dependencies | Configuration |
| `.env` | API keys and credentials (gitignored) | Configuration |
| `.env.example` | Template for environment variables | Configuration |
| `.gitignore` | Git ignore patterns | Configuration |
| `README.md` | Project overview and quick start | Documentation |

### Source Code (`src/`)

| File/Directory | Purpose |
|----------------|---------|
| `config.py` | Environment variable parsing and global configuration |
| `logger.py` | Standardized logging setup for the application |
| `services/` | Business logic for different domains (News, Images, Instagram, Content) |
| `utils/` | General helper functions, CSV logging, state tracking |
| `prompts/` | System prompts and templates for Gemini AI models |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `README.md` | Documentation index and overview |
| `QUICKSTART.md` | Setup guide, installation, basic usage |
| `ARCHITECTURE.md` | System architecture and design |
| `PROJECT_STRUCTURE.md` | This file - project organization |
| `CODEBASE_DOCUMENTATION.md` | Complete technical reference (16 sections) |

### Testing Scripts (`tests/`)

| File | Purpose |
|------|---------|
| `api_test.py` | Test Google Gemini API (text + image) |
| `test_ig.py` | Validate Instagram credentials |
| `test_tg.py` | Test Telegram bot connectivity |
| `list_models.py` | List available GenAI models |
| `test_font.py` | Test font rendering capabilities |
| `test_font2.py` | Additional font tests |

### Assets (`assets/`)

| File | Purpose | Required |
|------|---------|----------|
| `README.md` | Assets documentation | No |
| `logo.png` | AIRMAN brand logo for compositing | **Yes** |
| `sunset.jpg` | Sample image for testing | No |
| `gemini_test_output.jpg` | Test output from API tests | No (generated) |
| `generated_*.jpg` | AI-generated images | No (temporary) |

### Data Files (`data/`)

| File | Purpose | Auto-Generated |
|------|---------|----------------|
| `.gitkeep` | Keep directory in git | No |
| `shown_news.txt` | Tracks shown headlines | Yes |
| `posted_festivals_*.txt` | Tracks posted festivals per year | Yes |
| `post_history.csv` | Complete log of all posts with timestamps | Yes |

### Logs (`logs/`)

| File | Purpose | Auto-Generated |
|------|---------|----------------|
| `.gitkeep` | Keep directory in git | No |
| `bot.log` | Application execution logs | Yes |

---

## 🔄 File Lifecycle

### Persistent Files (Committed to Git)
- `main.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md`
- All files in `docs/`
- All files in `tests/`
- `assets/logo.png` (required)
- `assets/README.md`
- `.gitkeep` files

### Generated Files (Gitignored)
- `.env` - Created by user from `.env.example`
- `data/shown_news.txt` - Created on first news fetch
- `data/posted_festivals_*.txt` - Created on first festival post
- `logs/bot.log` - Created on bot startup
- `assets/generated_*.jpg` - Created and deleted per post

### Temporary Files (Deleted After Use)
- `assets/generated_*.jpg` - Deleted after Instagram posting
- `assets/downloaded_*.jpg` - Deleted after processing

---

## 🚀 Setup Workflow

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd airman-social-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Add Brand Assets**
   ```bash
   # Place logo.png in assets/ directory
   cp /path/to/your/logo.png assets/logo.png
   ```

5. **Test Components**
   ```bash
   python tests/api_test.py
   python tests/test_ig.py
   python tests/test_tg.py
   ```

6. **Run Bot**
   ```bash
   python main.py
   ```

---

## 📦 Directory Creation

The following directories are automatically created by `main.py` if they don't exist:
- `data/`
- `logs/`
- `assets/`

This ensures the bot can run even if these directories are missing.

---

## 🔒 Security Notes

### Gitignored Files (Never Commit)
- `.env` - Contains sensitive API keys
- `data/shown_news.txt` - May contain sensitive data
- `data/posted_festivals_*.txt` - Tracking data
- `logs/*.log` - May contain sensitive information
- `assets/generated_*.jpg` - Temporary files

### Required Manual Setup
- `.env` file must be created from `.env.example`
- `assets/logo.png` must be added manually

---

## 📊 File Size Expectations

| Directory | Typical Size | Notes |
|-----------|-------------|-------|
| `docs/` | ~100 KB | Documentation files |
| `tests/` | ~50 KB | Test scripts |
| `assets/` | ~5 MB | Logo + generated images |
| `data/` | ~10 KB | Text tracking files |
| `logs/` | ~1-10 MB | Grows over time |

---

## 🧹 Cleanup Commands

### Clean Generated Images
```bash
rm -f assets/generated_*.jpg
rm -f assets/downloaded_*.jpg
```

### Clean Logs
```bash
rm -f logs/bot.log
```

### Clean Data (Reset Tracking)
```bash
rm -f data/shown_news.txt
rm -f data/posted_festivals_*.txt
```

### Clean All Generated Files
```bash
rm -f assets/generated_*.jpg assets/downloaded_*.jpg
rm -f logs/bot.log
rm -f data/shown_news.txt data/posted_festivals_*.txt
```

---

## 📝 Maintenance

### Regular Tasks
- Monitor `logs/bot.log` for errors
- Check `data/shown_news.txt` size (reset if too large)
- Clean old generated images in `assets/`
- Update documentation in `docs/` as needed

### Backup Important Files
- `.env` (store securely, not in git)
- `assets/logo.png` (brand asset)
- `data/shown_news.txt` (if needed)

---

## 🔗 Related Documentation

- **Setup Guide**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Technical Reference**: [docs/CODEBASE_DOCUMENTATION.md](docs/CODEBASE_DOCUMENTATION.md)
- **Testing Guide**: [tests/README.md](tests/README.md)
- **Assets Guide**: [assets/README.md](assets/README.md)

---

**Last Updated**: March 9, 2026
