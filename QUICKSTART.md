# AIRMAN Social Media Automation

This Telegram bot automates fetching breaking aviation news, creating Instagram posts customized to the **AIRMAN** brand aesthetic, generating AI captions with Gemini, synthesizing cinematic images with Imagen 4.0, scaling and laying out imagery, and automatically posting to Instagram.

## Prerequisites

1. **Python 3.12+** (Can use a local Conda environment, e.g., `py12`)
2. **Google Gemini API Key**: You must have a free API key from Google AI Studio. The bot uses `gemini-2.5-flash` for captioning and `imagen-4.0-generate-001` for image generation.
3. **macOS** *(Optional but recommended)*: The bot dynamically looks for Apple-native fonts (`Avenir.ttc` or `Futura.ttc`) to perfectly match the AIRMAN branding. It will fallback to Arial or default if not found.
4. **logo.png**: A transparent `/logo.png` must be placed in the project root directory. This will be automatically embedded onto the top-right corner of all generated Instagram posts.

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
GEMINI_API="your_gemini_api_key_here"
```

## Running the Bot

1. Start the python script:
   ```bash
   conda run -n py12 python main.py
   # OR simply
   python main.py
   ```
2. Open Telegram and navigate to your bot.

## Usage

1. Send the `/start` command to wake the bot up.
2. Send the `/news` command.
3. The bot will scrape Google News specifically for "Aviation News" and present you with the top 5 breaking headlines.
4. Click one of the inline interactive **Option [1-5]** buttons to select your chosen news.

### What happens in following?
Once selected:
- ✍️ **Caption Generation**: Hits the ultra-fast `gemini-2.5-flash` API, which is hardcoded via a system prompt to act as the official social media manager for the AIRMAN brand, keeping the tone clean, inspirational, and professional.
- 🎨 **Image Generation**: Sends a cinematic prompt to Google's highly unreleased `imagen-4.0-generate` to synthesize a stunning, hyper-realistic 8k aesthetic photo representing the news directly. 
- 🖼️ **Image Processing**: Clips and sizes the generated photograph to a perfect **1:1 Instagram Square**, pastes the `logo.png` mask, burns the headline directly onto the image in Clean All-Caps Avenir/Futura font over a semi-transparent readability gradient, and prints the URL at the bottom.
- 🚀 **Instagram API**: Ships the finished artwork and Gemini's generated caption directly to the `@we_are_airman` feed.

---

### Troubleshooting
- **`Image_process_failed` from Instagram**: This usually means the image dimension ratio is odd. The newest version pads the image to exactly `1080x1080` to prevent this safely.
- **Imagen 4.0 Error**: Ensure your Google API key actually has access to the cutting-edge Image models. 
- **"Cannot start bot without successful Instagram login"**: Double-check your `.env` password avoiding any weird unescaped characters, and ensure Instagram isn't temporarily throwing a "Challenge Required" (Captcha/2FA) wall on your account.
