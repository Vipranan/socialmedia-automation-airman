import os
import logging
import asyncio
import uuid
import httpx
import feedparser
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap
from dotenv import load_dotenv

from google import genai
from google.genai import types

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from instagrapi import Client

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Initialize Instagram Client
cl = Client()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hello! I am the AIRMAN Social Media Bot. ✈️\n\nSend /help to see all available skills and commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 **AIRMAN Social Media Bot Skills:**\n\n"
        "📰 **/news** - Fetch the top 5 trending aviation news headlines. You can select one to instantly generate an Instagram post and AI caption.\n\n"
        "🚀 **/startauto** - Turn on Auto-Pilot. The bot will autonomously fetch new aviation news, synthesize a cinematic image, write a caption, and post to Instagram every 2 minutes.\n\n"
        "🛑 **/stopauto** - Deactivate Auto-Pilot scheduling.\n\n"
        "ℹ️ **/help** - Show this help message."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Global set to track headlines we've already shown so we don't repeat them
SHOWN_NEWS_FILE = "shown_news.txt"

def load_shown_news():
    if os.path.exists(SHOWN_NEWS_FILE):
        with open(SHOWN_NEWS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_shown_news(headline):
    with open(SHOWN_NEWS_FILE, "a") as f:
        f.write(f"{headline}\n")

SHOWN_NEWS_HEADLINES = load_shown_news()

def fetch_top_aviation_news(limit=5):
    """Fetches the latest aviation news headlines from an RSS feed without repeating."""
    global SHOWN_NEWS_HEADLINES
    feed_url = 'https://news.google.com/rss/search?q=aviation+news&hl=en-US&gl=US&ceid=US:en'
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        raise Exception("Could not fetch aviation news.")
        
    headlines = []
    
    # If we've shown almost everything in the feed, clear the history to start over
    if len(SHOWN_NEWS_HEADLINES) >= len(feed.entries) - limit + 1:
        logger.info("Resetting SHOWN_NEWS_HEADLINES as we exhausted the RSS feed.")
        SHOWN_NEWS_HEADLINES.clear()
        if os.path.exists(SHOWN_NEWS_FILE):
            os.remove(SHOWN_NEWS_FILE)
        
    for entry in feed.entries:
        title = entry.title
        if " - " in title:
            title = title.rsplit(" - ", 1)[0]
            
        if title not in SHOWN_NEWS_HEADLINES:
            headlines.append(title)
            SHOWN_NEWS_HEADLINES.add(title)
            save_shown_news(title)
            if len(headlines) == limit:
                break
                
    return headlines

async def generate_and_download_image(prompt: str) -> str:
    """Generates an image using Google Imagen 4.0 and saves it."""
    import io
    
    gemini_api_key = os.getenv("GEMINI_API")
    if not gemini_api_key:
        raise ValueError("GEMINI_API key not found in .env")
        
    client = genai.Client(api_key=gemini_api_key)
    logger.info(f"Generating image with prompt: '{prompt}'")
    
    loop = asyncio.get_event_loop()
    def _generate_image():
        return client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
    result = await loop.run_in_executor(None, _generate_image)
    
    if result.generated_images:
        generated_image = result.generated_images[0]
        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        filename = f"generated_{uuid.uuid4().hex[:8]}.jpg"
        image.save(filename, "JPEG")
        return filename
    else:
        raise ValueError("Image generation failed to return an image from Google Imagen.")

def format_image_for_instagram(image_path: str):
    """Resizes internal generation to 1080x1080 and adds the AIRMAN logo, relying on Imagen for text."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Instagram prefers 1080x1080 (1:1 square)
        desired_size = 1080
        
        # Calculate resize ratio to fit within 1080x1080 while maintaining aspect
        ratio = min(desired_size / img.width, desired_size / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new blank black 1080x1080 image
        new_img = Image.new("RGB", (desired_size, desired_size), (0, 0, 0))
        
        # Paste the resized original image into the center
        paste_x = (desired_size - new_width) // 2
        paste_y = (desired_size - new_height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        img = new_img
        
        # --- Add Logo ---
        try:
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_ratio = 90 / logo.width
                logo_resized = logo.resize((90, int(logo.height * logo_ratio)), Image.Resampling.LANCZOS)
                
                margin = 30
                paste_x = img.width - logo_resized.width - margin
                paste_y = margin
                
                # Paste using its alpha channel as a mask
                img.paste(logo_resized, (paste_x, paste_y), mask=logo_resized)
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")
            
        # Convert back to RGB to save as JPEG safely
        img = img.convert("RGB")
        img.save(image_path, "JPEG", quality=95)
        logger.info(f"Formatted and branded {image_path} for Instagram")
    except Exception as e:
        logger.error(f"Failed to format image: {e}")

async def handle_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches top news and presents them to the user to choose."""
    message = update.message
    
    try:
        await message.reply_text("🔎 Fetching top 5 Aviation News...")
        headlines = fetch_top_aviation_news(5)
        
        # Store in user data for retrieval in callback
        context.user_data['headlines'] = headlines
        
        keyboard = []
        text = "📰 **Top 5 Aviation News Headlines:**\n\n"
        
        for i, headline in enumerate(headlines):
            text += f"**{i+1}.** {headline}\n\n"
            keyboard.append([InlineKeyboardButton(f"Option {i+1}", callback_data=str(i))])
            
        text += "Please choose a news item to post! 👇"
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Failed to fetch news: {repr(e)}"
        logger.exception("Error in handle_news_command:")
        await message.reply_text(error_msg)

async def generate_and_post(headline: str) -> tuple[str, str]:
    """Handles generating the caption, image, and posting to Instagram. Returns (caption, image_path)."""
    # 1. Ask Gemini to create the Caption AND Poster Title
    system_prompt = (
        "You are the official AI social media manager for 'AIRMAN' (https://www.theairman.org/). "
        "AIRMAN is a highly premium, sleek, futuristic aviation tech brand. We build Maverick AI and Skynet AI. "
        "Our visual identity is airy, blue skies, cloud-tech, and aspirational. "
        "Our tone is educational, empowering, tech-forward, and extremely professional. "
        "I will provide you with a recent aviation news headline.\n\n"
        "Your task:\n"
        "1. Write a highly engaging Instagram caption about this news. Speak as the AIRMAN brand, relate the news to the future of aviation/innovation, use spacing, emojis (\u2708\ufe0f \ud83d\ude80 \u2601\ufe0f), and hashtags.\n"
        "2. Create a short, punchy 2-5 word title for the poster image (e.g., 'THE FUTURE OF FLIGHT', 'AUTONOMY TAKES FLIGHT').\n"
        "Output ONLY a valid JSON object with keys 'caption' and 'poster_title'. Do not include markdown formatting or backticks around the JSON."
    )
    
    user_prompt = f"Headline: '{headline}'"
    
    gemini_api_key = os.getenv("GEMINI_API")
    if not gemini_api_key:
        raise ValueError("GEMINI_API key not found in .env")
    genai_client = genai.Client(api_key=gemini_api_key)
    
    loop = asyncio.get_event_loop()
    def _generate_caption():
        return genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt + "\n\n" + user_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
    
    response = await loop.run_in_executor(None, _generate_caption)
    try:
        data = json.loads(response.text.strip())
        caption = data.get("caption", "Aviation News")
        poster_title = data.get("poster_title", "AVIATION NEWS")
    except Exception as e:
        logger.error(f"Failed to parse JSON from Gemini: {e}")
        caption = response.text.strip()
        poster_title = headline[:30]

    # 2. Generate a relevant image online using Imagen 4.0
    image_prompt = (
        f"A hyper-realistic, highly cinematic, premium, modern aviation poster representing: '{headline}'. "
        f"The text '{poster_title}' MUST be beautifully and creatively integrated into the scene environment "
        "(e.g., written gracefully as volumetric clouds in the sky, as massive cinematic 3D letters integrated into the environment, or elegant graphic poster typography). "
        "Ensure the typography flawlessly blends with the aviation scene. High quality, 8k resolution, aspirational."
    )
        
    image_path = await generate_and_download_image(image_prompt)
    
    # 3. Format the image perfectly for Instagram (no bulk overlay text)
    format_image_for_instagram(image_path)
    
    # 4. Post to Instagram
    caption += "\n\n🌐 https://www.theairman.org/"
    logger.info(f"Attempting to post to Instagram with caption: {caption}")
    media = await loop.run_in_executor(None, cl.photo_upload, image_path, caption)
    
    logger.info(f"Successfully posted to Instagram. Media ID: {media.pk}")
    return caption, image_path

async def process_news_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the user's news selection and proceeds to post it."""
    query = update.callback_query
    await query.answer()
    message = query.message
    image_path = None
    
    try:
        idx = int(query.data)
        headlines = context.user_data.get('headlines', [])
        
        if not headlines or idx >= len(headlines):
            await query.edit_message_text(text="❌ Session expired or invalid selection. Please run /news again.")
            return
            
        headline = headlines[idx]
        
        await query.edit_message_text(text=f"✅ **You selected:**\n{headline}\n\n✍️ Generating caption and image... Hang tight!", parse_mode='Markdown')
        
        caption, image_path = await generate_and_post(headline)
        await message.reply_photo(photo=open(image_path, 'rb'), caption="✅ Post successfully published to Instagram!")
        
        # Send full caption in a separate message because Telegram caps image captions at 1024 chars
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await message.reply_text(f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"❌ Failed to process or post: {repr(e)}"
        logger.exception("Error in process_news_selection:")
        await message.reply_text(error_msg)
        
    finally:
        # Clean up the downloaded image
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"Cleaned up {image_path}")

async def auto_post_news(context: ContextTypes.DEFAULT_TYPE) -> None:
    """The automated recurring job to fetch and post news."""
    job = context.job
    chat_id = job.chat_id
    image_path = None
    try:
        await context.bot.send_message(chat_id, "⚙️ Auto-pilot: Waking up to post new aviation news...")
        
        headlines = fetch_top_aviation_news(1) # We only need 1 headline for the automated post
        if not headlines:
            await context.bot.send_message(chat_id, "⚙️ Auto-pilot: No new news found right now. Skipping.")
            return
            
        headline = headlines[0]
        caption, image_path = await generate_and_post(headline)
        
        await context.bot.send_photo(chat_id, photo=open(image_path, 'rb'), caption="✅ Auto-pilot successfully published!")
        
        # Send full caption in a separate message because Telegram caps image captions at 1024 chars
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await context.bot.send_message(chat_id, f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')
        
    except Exception as e:
        logger.exception("Error in auto_post_news:")
        await context.bot.send_message(chat_id, f"❌ Auto-pilot error: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            
async def startauto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the automated posting."""
    chat_id = update.effective_message.chat_id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        await update.message.reply_text("⚠️ Auto-posting is already running!")
        return
        
    # Start job every 120 seconds (2 minutes), post first one immediately (delay 5 seconds)
    context.job_queue.run_repeating(auto_post_news, interval=120, first=5, chat_id=chat_id, name=str(chat_id))
    await update.message.reply_text("🚀 Auto-pilot ACTIVATED! I'm posting a post now, and will continue to post every 2 minutes.\nSend /stopauto anytime to turn it off.")

async def stopauto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stops the automated posting."""
    chat_id = update.effective_message.chat_id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not current_jobs:
        await update.message.reply_text("⚠️ Auto-posting is not currently running.")
        return
        
    for job in current_jobs:
        job.schedule_removal()
    await update.message.reply_text("🛑 Auto-pilot DEACTIVATED.")

def login_instagram():
    """Login to Instagram."""
    try:
        logger.info(f"Logging into Instagram as {INSTAGRAM_USERNAME}...")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        logger.info("Successfully logged into Instagram.")
    except Exception as e:
        logger.error(f"Failed to login to Instagram: {e}")
        raise

def main() -> None:
    """Start the bot."""
    if not all([TELEGRAM_BOT_TOKEN, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return

    # Login to Instagram
    try:
        login_instagram()
    except Exception as e:
        logger.error("Cannot start bot without successful Instagram login.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", handle_news_command))
    application.add_handler(CommandHandler("startauto", startauto))
    application.add_handler(CommandHandler("stopauto", stopauto))
    
    # regex patterns to separate the callbacks
    application.add_handler(CallbackQueryHandler(process_news_selection, pattern=r"^\d+$"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
