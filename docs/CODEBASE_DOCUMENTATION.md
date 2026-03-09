# AIRMAN Social Media Bot - Technical Documentation

> **Version**: 1.0 | **Last Updated**: March 9, 2026 | **Maintained By**: AIRMAN Development Team

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [External Services](#external-services)
6. [Configuration](#configuration)
7. [Bot Commands](#bot-commands)
8. [Content Generation](#content-generation)
9. [Data Management](#data-management)
10. [Technical Details](#technical-details)
11. [Brand Guidelines](#brand-guidelines)
12. [Development](#development)
13. [Troubleshooting](#troubleshooting)
14. [Future Enhancements](#future-enhancements)
15. [Resources](#resources)

---

## 1. Overview

### Purpose
The AIRMAN Social Media Bot is an intelligent, fully-automated Instagram content publication system for the AIRMAN aviation brand (https://www.theairman.org/). It automates the entire social media workflow from content discovery to publication while maintaining brand consistency.

### What It Does
- Fetches trending aviation news from Google News RSS
- Generates brand-aligned captions using Gemini 2.5 Flash
- Creates hyper-realistic images using Imagen 4.0
- Applies AIRMAN branding and formatting
- Posts directly to Instagram
- Supports automated scheduling and festival posts

### Key Benefits
- Reduces manual content creation effort
- Maintains consistent brand voice and visual identity
- Enables 24/7 automated posting
- Prevents duplicate content
- Supports special occasion posts

---

## 2. Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Telegram)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ /news, /startauto, /forcefestival
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Telegram Bot Handler                       │
│              (python-telegram-bot)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              News Fetching & Selection                      │
│         (Google News RSS + feedparser)                      │
│         • Fetch top 5 headlines                             │
│         • Track shown headlines                             │
│         • Present interactive keyboard                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Parallel AI Content Generation                    │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  Gemini 2.5 Flash    │  │    Imagen 4.0        │        │
│  │  Caption + Title     │  │  8K Cinematic Image  │        │
│  └──────────────────────┘  └──────────────────────┘        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Image Processing (Pillow)                      │
│         • Resize to 1080x1080                               │
│         • Center on black canvas                            │
│         • Composite AIRMAN logo                             │
│         • Save as high-quality JPEG                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Instagram Publishing (Instagrapi)                 │
│         • Upload image                                      │
│         • Post with caption                                 │
│         • Return confirmation                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI/ML** | Google Gemini 2.5 Flash | Caption generation |
| **AI/ML** | Google Imagen 4.0 | Image synthesis |
| **Bot Framework** | python-telegram-bot | User interface |
| **Social Media** | Instagrapi | Instagram posting |
| **Image Processing** | Pillow (PIL) | Branding & formatting |
| **Content Sourcing** | feedparser | RSS feed parsing |
| **Async Runtime** | asyncio | Non-blocking operations |
| **Environment** | python-dotenv | Configuration management |

---

## 3. Project Structure

### File Organization

```text
airman-social-bot/
├── main.py                          # Core application entry point
├── run.py                           # Convenience runner script
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Environment template
│
├── src/                            # Source code modules
│   ├── config.py                   # App configuration & environment
│   ├── logger.py                   # Logging setup
│   ├── services/                   # Core business logic
│   ├── utils/                      # Helper utilities
│   └── prompts/                    # Generative AI prompts
│
├── docs/                           # Documentation
│   ├── README.md                   # Project overview
│   ├── QUICKSTART.md              # Setup guide
│   ├── ARCHITECTURE.md            # System design
│   ├── PROJECT_STRUCTURE.md       # Directory layout documentation
│   └── CODEBASE_DOCUMENTATION.md  # This file
│
├── tests/                          # Tests
│   ├── api_test.py                # Test Gemini API
│   └── test_*.py                  # Unit/integration tests
│
├── data/                           # Auto-generated tracking files
│   ├── shown_news.txt             # Headline tracking
│   └── posted_festivals_2026.txt  # Festival tracking
│
├── logs/                           # Automated bot logs
│   └── bot.log                    # Application execution logs
│
└── assets/                         # Assets (logo, temp images)
    ├── logo.png                   # Brand logo
    ├── generated_*.jpg            # AI-generated images
    └── sunset.jpg                 # Sample image
```

### Key Files

| File | Purpose | Type |
|------|---------|------|
| `main.py` | Core bot initialization, handlers setup, start polling | Application |
| `src/config.py` | Environment loading and global configurations | Configuration |
| `src/services/` | Modules handling news, images, IG, and Telegram | Application Module |
| `requirements.txt` | Python package dependencies | Configuration |
| `.env` | API keys and credentials | Configuration |
| `assets/logo.png` | AIRMAN brand logo for compositing | Asset |
| `data/shown_news.txt` | Tracks shown headlines | Data |
| `logs/bot.log` | Application execution logs | Data |

---

## 4. Core Components

### 4.1 Command Handlers

| Function | Command | Description |
|----------|---------|-------------|
| `start()` | `/start` | Welcome message and bot initialization |
| `help_command()` | `/help` | Display all available commands |
| `handle_news_command()` | `/news` | Fetch top 5 headlines with interactive selection |
| `process_news_selection()` | Callback | Handle user's headline selection |
| `startauto()` | `/startauto` | Enable auto-pilot mode |
| `stopauto()` | `/stopauto` | Disable auto-pilot mode |
| `forcefestival()` | `/forcefestival [Name]` | Manually generate festival post |

### 4.2 Content Generation

| Function | Purpose | Returns |
|----------|---------|---------|
| `generate_and_post(headline)` | Orchestrate news post creation | `(caption, image_path)` |
| `generate_and_post_festival(festival_name)` | Orchestrate festival post creation | `(caption, image_path)` |
| `generate_and_download_image(prompt)` | Call Imagen 4.0 API | `image_path` |
| `format_image_for_instagram(image_path)` | Apply branding and formatting | `None` (modifies in-place) |

### 4.3 News & Data Management

| Function | Purpose | Returns |
|----------|---------|---------|
| `fetch_top_aviation_news(limit)` | Parse RSS feed, track headlines | `list[str]` |
| `load_shown_news()` | Load headline history on startup | `set[str]` |
| `save_shown_news(headline)` | Append headline to tracking file | `None` |

### 4.4 Automation Jobs

| Function | Trigger | Interval | Purpose |
|----------|---------|----------|---------|
| `auto_post_news()` | `/startauto` | 120s (starts at 5s) | Auto-post news |
| `auto_post_calendar()` | `/startauto` | 120s (starts at 20s) | Check & post festivals |

### 4.5 Authentication & Entry Point

| Function | Purpose |
|----------|---------|
| `login_instagram()` | Authenticate with Instagram via Instagrapi |
| `main()` | Entry point: validate env, login, setup handlers, start polling |

---

## 5. External Services

### 5.1 Google GenAI Suite

#### Gemini 2.5 Flash
- **Model ID**: `gemini-2.5-flash`
- **Purpose**: Caption and title generation
- **Input**: System prompt + news headline
- **Output**: JSON with `caption` and `poster_title`
- **Response Type**: `application/json`

#### Imagen 4.0
- **Model ID**: `imagen-4.0-generate-001`
- **Purpose**: Hyper-realistic image generation
- **Input**: Detailed cinematic prompt
- **Output**: 8K image bytes (1:1 aspect ratio)
- **Format**: JPEG with UUID filename

### 5.2 Social Media APIs

#### Google News RSS
- **URL**: `https://news.google.com/rss/search?q=aviation+news&hl=en-US&gl=US&ceid=US:en`
- **Purpose**: Source for trending aviation headlines
- **Parser**: feedparser library
- **Frequency**: On-demand or every 2 minutes (auto-pilot)

#### Telegram Bot API
- **Library**: python-telegram-bot
- **Purpose**: User interface and command handling
- **Features**: Inline keyboards, callback queries, job scheduling
- **Authentication**: Bot token from BotFather

#### Instagram Mobile API
- **Library**: Instagrapi (reverse-engineered)
- **Purpose**: Content publishing
- **Authentication**: Username + password
- **Limitations**: May break with Instagram updates

---

## 6. Configuration

### 6.1 Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Instagram Account Credentials
INSTAGRAM_USERNAME=we_are_airman
INSTAGRAM_PASSWORD=your_secure_password

# Google GenAI API Key
GEMINI_API=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq
```

### 6.2 Dependencies

Install via `pip install -r requirements.txt`:

```
python-telegram-bot[job-queue]  # Telegram bot framework
instagrapi                      # Instagram API client
Pillow                          # Image processing
google-genai                    # Google AI SDK
feedparser                      # RSS feed parser
python-dotenv                   # Environment management
httpx                           # HTTP client
```

### 6.3 System Requirements

- **Python**: 3.12 or higher
- **OS**: macOS recommended (for native fonts), Linux/Windows supported
- **Network**: Stable internet connection for API calls
- **Assets**: `logo.png` in project root (transparent PNG)

---

## 7. Bot Commands

### 7.1 User Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| **Start** | `/start` | Initialize bot | `/start` |
| **Help** | `/help` | Show command list | `/help` |
| **News** | `/news` | Fetch & select headlines | `/news` |
| **Auto-Pilot** | `/startauto` | Enable automation | `/startauto` |
| **Stop Auto** | `/stopauto` | Disable automation | `/stopauto` |
| **Festival** | `/forcefestival [Name]` | Manual festival post | `/forcefestival Diwali` |

### 7.2 Auto-Pilot Mode

When enabled via `/startauto`:

#### News Posting Job
- **Interval**: Every 120 seconds
- **First Run**: 5 seconds after activation
- **Job Name**: `news_{chat_id}`
- **Behavior**:
  1. Fetch 1 new headline
  2. Generate caption + image
  3. Post to Instagram
  4. Send confirmation to Telegram

#### Festival Calendar Job
- **Interval**: Every 120 seconds
- **First Run**: 20 seconds after activation
- **Job Name**: `cal_{chat_id}`
- **Behavior**:
  1. Check if today matches festival date
  2. Verify not already posted this year
  3. Generate festival content
  4. Post to Instagram
  5. Record in `posted_festivals_[YEAR].txt`

### 7.3 Festival Calendar

Hardcoded dates in `FESTIVALS` dictionary (MM-DD format):

| Date | Festival |
|------|----------|
| 01-01 | New Year |
| 01-14 | Makar Sankranti & Pongal |
| 01-26 | Republic Day (India) |
| 02-14 | Valentine's Day |
| 03-08 | International Women's Day |
| 04-22 | Earth Day |
| 08-15 | Independence Day (India) |
| 08-19 | National Aviation Day |
| 10-31 | Halloween |
| 12-25 | Christmas |

---

## 8. Content Generation

### 8.1 Caption Generation (Gemini 2.5 Flash)

#### System Prompt Structure

```
You are the official AI social media manager for 'AIRMAN' (https://www.theairman.org/).

BRAND IDENTITY:
- Highly premium, sleek, futuristic aviation tech brand
- Products: Maverick AI and Skynet AI
- Visual identity: airy, blue skies, cloud-tech, aspirational
- Tone: educational, empowering, tech-forward, extremely professional

TASK:
1. Write highly engaging Instagram caption about this news
2. Relate news to future of aviation/innovation
3. Use spacing, emojis (✈️ 🚀 ☁️), and hashtags
4. Create short 2-5 word title for poster image

OUTPUT:
JSON object with keys 'caption' and 'poster_title'
```

#### Post-Processing
1. Strip markdown formatting (````json```)
2. Parse JSON response
3. Extract `caption` and `poster_title`
4. Append `\n\n🌐 https://www.theairman.org/`
5. Fallback to raw text if parsing fails

### 8.2 Image Generation (Imagen 4.0)

#### Prompt Template (News)

```
A hyper-realistic, highly cinematic, premium, modern aviation poster 
representing: '[HEADLINE]'. 

The text '[POSTER_TITLE]' MUST be beautifully and creatively integrated 
into the scene environment (e.g., written gracefully as volumetric clouds 
in the sky, as massive cinematic 3D letters integrated into the environment, 
or elegant graphic poster typography). 

Ensure the typography flawlessly blends with the aviation scene. 
High quality, 8k resolution, aspirational.
```

#### Prompt Template (Festival)

```
A hyper-realistic, highly cinematic, premium, modern aviation poster 
celebrating the festival/holiday: '[FESTIVAL_NAME]'. 

The text '[POSTER_TITLE]' MUST be beautifully and creatively integrated 
into the scene environment (e.g., written gracefully as volumetric clouds 
in the sky, painted elegantly on the runway, or as massive cinematic 3D 
letters integrated into the environment). 

Ensure the typography flawlessly blends with the aviation scene. 
High quality, 8k resolution, aspirational, no generic memes.
```

#### API Configuration
- **Aspect Ratio**: 1:1 (square)
- **Number of Images**: 1
- **Output Format**: JPEG
- **Filename**: `generated_[UUID].jpg`

### 8.3 Image Processing Pipeline

#### Step-by-Step Process

1. **Load & Convert**
   - Open generated image
   - Convert to RGB mode

2. **Calculate Dimensions**
   - Target size: 1080x1080
   - Calculate resize ratio maintaining aspect
   - Resize using LANCZOS resampling

3. **Center on Canvas**
   - Create black 1080x1080 canvas
   - Calculate center position
   - Paste resized image

4. **Logo Compositing**
   - Load `logo.png` as RGBA
   - Resize to 90px width (maintain aspect)
   - Position at top-right (30px margin)
   - Paste using alpha mask

5. **Save**
   - Convert to RGB
   - Save as JPEG (95% quality)

#### Technical Specifications
- **Final Size**: 1080x1080 pixels
- **Format**: JPEG
- **Quality**: 95%
- **Logo Size**: 90px width
- **Logo Position**: Top-right, 30px margin
- **Resampling**: LANCZOS (high quality)

---

## 9. Data Management

### 9.1 Headline Tracking

#### File: `shown_news.txt`

**Purpose**: Prevent duplicate news posts

**Format**: One headline per line
```
Boeing unveils new 737 MAX variant
SpaceX launches Starlink satellites
FAA approves new drone regulations
```

**Behavior**:
- Loaded on bot startup via `load_shown_news()`
- New headlines appended via `save_shown_news()`
- Auto-resets when feed exhausted: `len(SHOWN_NEWS_HEADLINES) >= len(feed.entries) - limit + 1`

### 9.2 Festival Tracking

#### File: `posted_festivals_[YEAR].txt`

**Purpose**: Ensure festivals post only once per year

**Format**: One festival name per line
```
New Year
Valentine's Day
Independence Day
```

**Behavior**:
- Checked before posting festival content
- Appended after successful post
- New file created each year automatically

### 9.3 Logging

#### File: `bot.log`

**Configuration**:
```python
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
```

**Log Levels**:
- **INFO**: Normal operations, API calls, posts
- **WARNING**: Missing logo, non-critical issues
- **ERROR**: API failures, login issues
- **EXCEPTION**: Full stack traces for debugging

---

## 10. Technical Details

### 10.1 Async Execution

#### Executor Pattern

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_function, *args)
```

#### Functions in Executor
- `genai_client.models.generate_content()` - Gemini API
- `client.models.generate_images()` - Imagen API
- `cl.photo_upload()` - Instagram posting

#### Async Components
- All Telegram command handlers
- Callback query handlers
- Job queue callbacks

#### Benefits
- Non-blocking API calls
- Responsive bot during long operations
- Multiple users can interact simultaneously
- Parallel caption and image generation

### 10.2 Job Queue Management

#### Job Naming Convention
- News jobs: `news_{chat_id}`
- Calendar jobs: `cal_{chat_id}`

#### Job Control
```python
# Start jobs
context.job_queue.run_repeating(callback, interval=120, first=5, chat_id=chat_id, name=job_name)

# Stop jobs
jobs = context.job_queue.get_jobs_by_name(job_name)
for job in jobs:
    job.schedule_removal()
```

#### Per-Chat Isolation
- Each chat has independent jobs
- Prevents cross-chat interference
- Allows multiple users simultaneously

### 10.3 Error Handling

#### Startup Validation
```python
if not all([TELEGRAM_BOT_TOKEN, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
    logger.error("Missing required environment variables")
    return
```

#### Instagram Login
```python
try:
    login_instagram()
except Exception as e:
    logger.error("Cannot start bot without successful Instagram login")
    return
```

#### API Failures
- Logged with full exception trace
- Reported to user via Telegram
- Image cleanup in `finally` block

---

## 11. Brand Guidelines

### 11.1 AIRMAN Brand Identity

| Element | Specification |
|---------|---------------|
| **Brand Name** | AIRMAN |
| **Website** | https://www.theairman.org/ |
| **Products** | Maverick AI, Skynet AI |
| **Industry** | Aviation Technology |
| **Positioning** | Premium, sleek, futuristic |

### 11.2 Visual Standards

| Aspect | Standard |
|--------|----------|
| **Image Format** | 1080x1080 JPEG (Instagram square) |
| **Image Quality** | 95% JPEG compression |
| **Source Resolution** | 8K (downscaled to 1080x1080) |
| **Logo Size** | 90px width |
| **Logo Position** | Top-right corner, 30px margin |
| **Background** | Black canvas for centering |
| **Style** | Hyper-realistic, cinematic, aspirational |

### 11.3 Typography

| Platform | Primary Font | Fallback |
|----------|-------------|----------|
| **macOS** | Avenir, Futura | Arial |
| **Linux/Windows** | Arial | System default |

### 11.4 Tone & Voice

**Characteristics**:
- Educational and empowering
- Tech-forward and professional
- Aspirational and inspirational
- Clean and minimalist

**Emojis**: ✈️ 🚀 ☁️ (aviation-themed only)

**URL**: Always append `https://www.theairman.org/` to captions

### 11.5 Color Palette

**Primary Theme**: Blue skies, cloud-tech aesthetics
- Airy and light
- Sky blues and whites
- Cloud-inspired gradients

---

## 12. Development

### 12.1 Setup Workflow

```bash
# 1. Clone repository
git clone <repository-url>
cd airman-social-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Add brand assets
# Place logo.png in project root

# 5. Test components
python api_test.py      # Test Gemini API
python test_ig.py       # Test Instagram login
python test_tg.py       # Test Telegram bot

# 6. Run bot
python main.py
```

### 12.2 Testing Scripts

| Script | Purpose | Expected Output |
|--------|---------|-----------------|
| `api_test.py` | Test Gemini text + image generation | Generated text and image file |
| `test_ig.py` | Validate Instagram credentials | Login success message |
| `test_tg.py` | Test Telegram bot connectivity | Bot responds to commands |
| `list_models.py` | List available GenAI models | Model names and IDs |

### 12.3 Development Best Practices

**Code Style**:
- Follow PEP 8 conventions
- Use type hints where applicable
- Add docstrings to functions
- Keep functions focused and small

**Error Handling**:
- Use try-except blocks for API calls
- Log exceptions with full trace
- Clean up resources in finally blocks
- Provide user-friendly error messages

**Security**:
- Never commit `.env` file
- Use environment variables for secrets
- Validate user input
- Sanitize file paths

**Testing**:
- Test each component independently
- Verify API connectivity before deployment
- Check Instagram login regularly
- Monitor bot.log for issues

---

## 13. Troubleshooting

### 13.1 Bot Won't Start

#### Missing Environment Variables
**Symptom**: `Missing required environment variables`
**Solution**:
- Verify `.env` file exists in project root
- Check all 4 variables are present: `TELEGRAM_BOT_TOKEN`, `INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`, `GEMINI_API`
- Ensure no extra spaces or quotes

#### Instagram Login Failure
**Symptom**: `Failed to login to Instagram`
**Solutions**:
- Verify username and password are correct
- Check if Instagram requires 2FA (disable for bot account)
- Try logging in manually via browser first
- Wait a few hours if Instagram flagged unusual activity
- Avoid special characters in password that need escaping

### 13.2 Image Generation Issues

#### API Key Invalid
**Symptom**: `GEMINI_API key not found` or authentication errors
**Solutions**:
- Verify API key is correct in `.env`
- Check key has Imagen access at [Google AI Studio](https://aistudio.google.com/)
- Regenerate key if expired
- Check API quota limits

#### Image Generation Fails
**Symptom**: `Image generation failed to return an image`
**Solutions**:
- Test with `api_test.py`
- Check internet connection
- Verify Imagen 4.0 model is available
- Review prompt for problematic content
- Check Google AI Studio for service status

### 13.3 Instagram Posting Issues

#### Image Process Failed
**Symptom**: `Image_process_failed` from Instagram
**Solutions**:
- Verify image is exactly 1080x1080
- Check `logo.png` exists and is valid PNG
- Ensure image is RGB JPEG format
- Test with sample image first

#### Challenge Required
**Symptom**: Instagram returns "Challenge Required"
**Solutions**:
- Log in manually via Instagram app/browser
- Complete any security challenges
- Wait 24-48 hours before retrying
- Reduce posting frequency
- Use residential IP (avoid VPN/proxy)

#### Account Restricted
**Symptom**: Posts not appearing or account warnings
**Solutions**:
- Check Instagram account status
- Verify account isn't shadowbanned
- Reduce auto-pilot frequency
- Review Instagram's automation policies
- Use different account for testing

### 13.4 Content Issues

#### Duplicate Headlines
**Symptom**: Same news appearing repeatedly
**Solutions**:
- Delete `shown_news.txt` to reset tracking
- Check if Google News RSS feed is updating
- Verify `SHOWN_NEWS_HEADLINES` set is working
- Note: Auto-resets when feed exhausted

#### Festival Posts Repeating
**Symptom**: Same festival posted multiple times
**Solutions**:
- Check `posted_festivals_[YEAR].txt` exists
- Verify file is readable and writable
- Ensure one festival name per line
- Delete file to reset for current year

#### Caption Too Long
**Symptom**: Caption truncated with "..."
**Solutions**:
- Telegram caps at 4000 chars (bot handles this)
- Instagram has no hard limit but may truncate in feed
- Adjust Gemini prompt to request shorter captions
- Split long captions into multiple messages

### 13.5 Automation Issues

#### Auto-Pilot Won't Stop
**Symptom**: Jobs continue after `/stopauto`
**Solutions**:
- Verify command sent from same chat as `/startauto`
- Check job names: `news_{chat_id}` and `cal_{chat_id}`
- Restart bot if jobs are stuck
- Check `bot.log` for errors

#### Jobs Not Running
**Symptom**: No posts after `/startauto`
**Solutions**:
- Check bot is running and connected
- Verify no errors in `bot.log`
- Ensure RSS feed is accessible
- Test manual `/news` command first
- Check Instagram login is still valid

### 13.6 Performance Issues

#### Slow Response Times
**Symptom**: Bot takes long to respond
**Solutions**:
- Check internet connection speed
- Verify API endpoints are responsive
- Monitor API quota usage
- Consider reducing image resolution
- Check system resources (CPU, memory)

#### Memory Leaks
**Symptom**: Bot memory usage grows over time
**Solutions**:
- Verify image cleanup in finally blocks
- Check for unclosed file handles
- Restart bot periodically
- Monitor with system tools (htop, Activity Monitor)

---

## 14. Future Enhancements

### 14.1 Infrastructure Improvements

**Database Integration**
- Replace text files with PostgreSQL/MongoDB
- Enable advanced querying and analytics
- Improve scalability and reliability
- Add transaction support

**Caching Layer**
- Implement Redis for API response caching
- Cache RSS feed results
- Rate limiting with Redis
- Session management

**Containerization**
- Docker container for easy deployment
- Docker Compose for multi-service setup
- Kubernetes for orchestration
- CI/CD pipeline integration

**Cloud Deployment**
- AWS/GCP deployment with auto-scaling
- Load balancing for multiple instances
- Managed database services
- CDN for image delivery

### 14.2 Feature Additions

**Multi-Account Support**
- Manage multiple Instagram accounts
- Account rotation for rate limiting
- Per-account configuration
- Centralized dashboard

**Dynamic Festival Calendar**
- API integration (Calendarific, Holiday API)
- Support for regional holidays
- Custom festival additions via command
- Timezone-aware scheduling

**Content Scheduling**
- Web dashboard for scheduling posts
- Calendar view of upcoming posts
- Draft mode with preview
- Bulk upload and queue management

**Advanced Image Templates**
- Multiple logo positions
- Custom overlays and filters
- Text overlay options
- Brand template library

### 14.3 Analytics & Insights

**Engagement Tracking**
- Track likes, comments, shares
- Follower growth metrics
- Best posting time analysis
- Hashtag effectiveness

**A/B Testing**
- Test different caption styles
- Compare image variations
- Optimize posting times
- Measure conversion rates

**Performance Dashboard**
- Real-time metrics visualization
- Historical trend analysis
- Export reports (PDF, CSV)
- Alert system for anomalies

### 14.4 Reliability Enhancements

**Retry Logic**
- Exponential backoff for API failures
- Automatic retry on transient errors
- Circuit breaker pattern
- Fallback mechanisms

**Monitoring & Alerting**
- Prometheus metrics collection
- Grafana dashboards
- PagerDuty/Slack alerts
- Health check endpoints

**Graceful Shutdown**
- Complete in-progress jobs
- Save state before exit
- Cleanup temporary files
- Reconnection handling

**Rate Limiting**
- Respect Instagram API limits
- Adaptive posting frequency
- Queue management
- Backpressure handling

### 14.5 User Experience

**Web Interface**
- React/Vue.js dashboard
- Mobile-responsive design
- Real-time updates via WebSocket
- User authentication

**Feedback Loop**
- Thumbs up/down on posts
- Comment on generated content
- Suggest improvements
- Report issues

**Customization**
- Configurable brand voice
- Custom prompt templates
- Image editing tools
- Multi-language support

### 14.6 Content Expansion

**Video Support**
- Instagram Reels generation
- Video editing and effects
- Text-to-video AI
- Thumbnail generation

**Carousel Posts**
- Multiple images per post
- Swipeable content
- Story-telling format
- Before/after comparisons

**Cross-Platform**
- Twitter/X integration
- LinkedIn posting
- Facebook pages
- TikTok support

**Content Sources**
- Multiple RSS feeds
- Custom news sources
- User-submitted content
- Trending topics API

---

## 15. Resources

### 15.1 Official Documentation

| Service | Documentation URL |
|---------|------------------|
| **Telegram Bot API** | https://core.telegram.org/bots/api |
| **Google GenAI** | https://ai.google.dev/ |
| **Instagrapi** | https://github.com/adw0rd/instagrapi |
| **Pillow (PIL)** | https://pillow.readthedocs.io/ |
| **python-telegram-bot** | https://docs.python-telegram-bot.org/ |

### 15.2 API References

**Google AI Studio**
- Console: https://aistudio.google.com/
- API Keys: https://aistudio.google.com/app/apikey
- Model Garden: https://aistudio.google.com/app/models

**Telegram BotFather**
- Create Bot: https://t.me/botfather
- Bot Management: Send `/mybots` to BotFather

### 15.3 Community & Support

**AIRMAN Brand**
- Website: https://www.theairman.org/
- Instagram: [@we_are_airman](https://www.instagram.com/we_are_airman/)

**Technical Support**
- GitHub Issues: (if applicable)
- Email: (if applicable)
- Slack/Discord: (if applicable)

### 15.4 Related Projects

**Similar Bots**
- Social media automation frameworks
- Instagram bot libraries
- Content generation tools

**Inspiration**
- AI-powered social media managers
- Automated content pipelines
- Brand consistency tools

---

## 16. Appendix

### 16.1 Limitations & Known Issues

#### Instagram API
- ⚠️ Uses reverse-engineered Instagrapi (may break with updates)
- ⚠️ May trigger "Challenge Required" with aggressive posting
- ⚠️ Rate limits not explicitly handled
- ⚠️ Single account only

#### Content Management
- ⚠️ RSS feed may be stale or limited
- ⚠️ Headline tracking resets when exhausted
- ⚠️ Festival calendar is hardcoded
- ⚠️ No database (text files only)

#### Image Generation
- ⚠️ Imagen text integration quality varies
- ⚠️ Logo placement not configurable
- ⚠️ Generated images deleted after posting
- ⚠️ No retry logic for failures

#### Automation
- ⚠️ Aggressive 2-minute intervals
- ⚠️ Festival checks every 2 minutes (inefficient)
- ⚠️ No graceful shutdown
- ⚠️ No global rate limiting

#### Error Handling
- ⚠️ Limited retry logic
- ⚠️ Caption truncation at 4000 chars
- ⚠️ No corruption detection for tracking files
- ⚠️ Missing logo logs warning but continues

### 16.2 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | March 9, 2026 | Initial release |

### 16.3 License

Built for AIRMAN - https://www.theairman.org/

### 16.4 Contributors

Maintained by AIRMAN Development Team

---

**End of Documentation**

For questions or issues, refer to the [Troubleshooting](#13-troubleshooting) section or contact the AIRMAN development team.
