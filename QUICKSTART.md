# AIRMAN Social Media Automation

This Telegram bot automates fetching breaking aviation news, creating Instagram posts customized to the **AIRMAN** brand aesthetic, generating AI captions with Llama, scaling and laying out imagery, and automatically posting to Instagram.

## Prerequisites

1. **Python 3.12+** (Can use a local Conda environment, e.g., `py12`)
2. **Ollama Installed** and running locally on port `11434`.
3. **Llama Model**: You must have `llama3.1:8b` downloaded within Ollama.
   ```bash
   ollama pull llama3.1:8b
   ```
4. **macOS** *(Optional but recommended)*: The bot dynamically looks for Apple-native fonts (`Avenir.ttc` or `Futura.ttc`) to perfectly match the AIRMAN branding. It will fallback to Arial or default if not found.
5. **logo.png**: A transparent `/logo.png` must be placed in the project root directory. This will be automatically embedded onto the top-right corner of all generated Instagram posts.

## Installation

1. Clone or download this project.
2. Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file in the root directory. Copy the structure below and fill in your details:

### `.env` File Setup
Create a file named `.env` in this directory:
```env
TELEGRAM_BOT_TOKEN="your_botfather_token_here"
INSTAGRAM_USERNAME="we_are_airman"
INSTAGRAM_PASSWORD="your_instagram_password_here"
```

## Running the Bot

1. Ensure Ollama is running (`ollama serve` or open the Ollama desktop app).
2. Start the python script:
   ```bash
   conda run -n py12 python main.py
   # OR simply
   python main.py
   ```
3. Open Telegram and navigate to your bot.

## Usage

1. Send the `/start` command to wake the bot up.
2. Send the `/news` command.
3. The bot will scrape Google News specifically for "Aviation News" and present you with the top 5 breaking headlines.
4. Click one of the inline interactive **Option [1-5]** buttons to select your chosen news.

### What happens in following?
Once selected:
- ✍️ **Caption Generation**: Hits local `llama3.1:8b`, which is hardcoded via a system prompt to act as the official social media manager for the AIRMAN brand, keeping the tone clean, inspirational, and professional.
- 🌍 **Image Search**: Queries DuckDuckGo for high-res real-world images matching the aviation news headline. (If this is blocked by rate-limits, it uses intelligent fallbacks).
- 🎨 **Image Processing**: Crops and pads the downloaded photograph to a perfect **1:1 Instagram Square**, pastes the `logo.png` mask, burns the headline directly onto the image in Clean All-Caps Avenir/Futura font over a semi-transparent readability gradient, and prints the URL at the bottom.
- 🚀 **Instagram API**: Ships the finished artwork and Llama's generated caption directly to the `@we_are_airman` feed.

---

### Troubleshooting
- **`Image_process_failed` from Instagram**: This usually means the image dimension ratio is odd. The newest version pads the image to exactly `1080x1080` to prevent this safely.
- **Connection timeouts**: The bot has built-in 30-second to 60-second timeouts for Ollama. If `llama3.1:8b` is extremely slow on your machine, you might need to increase the `httpx` timeout in `main.py`.
- **"Cannot start bot without successful Instagram login"**: Double-check your `.env` password avoiding any weird unescaped characters, and ensure Instagram isn't temporarily throwing a "Challenge Required" (Captcha/2FA) wall on your account.
