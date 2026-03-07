import os
import logging
import asyncio
import uuid
import httpx
import feedparser
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
    await update.message.reply_text("Hello! Send me the command /news to fetch the latest Aviation News, search for a relevant image, write a caption, and post it to Instagram!")

# Global set to track headlines we've already shown so we don't repeat them
SHOWN_NEWS_HEADLINES = set()

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
        
    for entry in feed.entries:
        title = entry.title
        if " - " in title:
            title = title.rsplit(" - ", 1)[0]
            
        if title not in SHOWN_NEWS_HEADLINES:
            headlines.append(title)
            SHOWN_NEWS_HEADLINES.add(title)
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

def add_headline_to_image(image_path: str, headline: str):
    """Adds the news headline as text over the downloaded image and formats for Instagram."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Instagram prefers 1080x1080 (1:1 square) or at least standard ratios.
        # To avoid BadRequest('Image_process_failed'), we will pad the image to a perfect 1080x1080 square.
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
                logo_ratio = 150 / logo.width
                logo_resized = logo.resize((150, int(logo.height * logo_ratio)), Image.Resampling.LANCZOS)
                
                margin = 30
                paste_x = img.width - logo_resized.width - margin
                paste_y = margin
                
                # Paste using its alpha channel as a mask
                img.paste(logo_resized, (paste_x, paste_y), mask=logo_resized)
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")
            
        draw = ImageDraw.Draw(img, "RGBA")
        width, height = img.size
        
        # Upper case headline for that clean marketing look
        display_headline = headline.upper()
        
        # Use a modern, clean font like Avenir or Futura (found on macOS) instead of Impact
        try:
            font_size = int(width * 0.045)
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Avenir.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", font_size)
            except:
                try: 
                    font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                    
        char_width = font.getbbox("A")[2] if hasattr(font, 'getbbox') else 10
        chars_per_line = max(20, int(width * 0.9 / char_width))
        wrapped_text = textwrap.fill(display_headline, width=chars_per_line)

        lines = wrapped_text.split('\n')
        line_height = font.getbbox("A")[3] if hasattr(font, 'getbbox') else 15
        text_height = len(lines) * line_height * 1.5
        
        # Add a subtle dark gradient/rectangle at the bottom for readability (elegant look)
        overlay_height = int(text_height + (height * 0.15))
        overlay_y = height - overlay_height
        draw.rectangle([(0, overlay_y), (width, height)], fill=(0, 0, 0, 160))
        
        # Add URL at the bottom of the overlay
        url_text = "www.theairman.org"
        try:
            url_font_size = int(width * 0.03)
            url_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Avenir.ttc", url_font_size)
        except:
            try:
                url_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", url_font_size)
            except:
                url_font = font
            
        url_width = url_font.getlength(url_text) if hasattr(url_font, 'getlength') else len(url_text)*8
        url_x = (width - url_width) / 2
        url_y = height - (url_font.getbbox("A")[3] if hasattr(url_font, 'getbbox') else 15) - (height * 0.03)
        draw.text((url_x, url_y), url_text, font=url_font, fill=(200, 210, 255, 230))
                
        # Draw headline text
        y_position = overlay_y + (height * 0.04)
        
        for line in lines:
            line_width = font.getlength(line) if hasattr(font, 'getlength') else len(line)*10
            x_position = (width - line_width) / 2
            
            # Draw text clean white, no tacky outlines needed because of the overlay
            draw.text((x_position, y_position), line, font=font, fill=(255, 255, 255, 255))
            y_position += line_height * 1.5
            
        # Convert back to RGB to save as JPEG safely
        img = img.convert("RGB")
        img.save(image_path, "JPEG", quality=95)
        logger.info(f"Added headline text to {image_path}")
    except Exception as e:
        logger.error(f"Failed to add text to image: {e}")

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
        
        await query.edit_message_text(text=f"✅ **You selected:**\n{headline}\n\n✍️ Asking Gemini 2.5 Flash for a caption...", parse_mode='Markdown')
        
        # 1. Ask Gemini to create the Caption
        system_prompt = (
            "You are the official AI social media manager for 'AIRMAN' (https://www.theairman.org/). "
            "AIRMAN is a highly premium, sleek, futuristic aviation tech brand. We build Maverick AI and Skynet AI. "
            "Our visual identity is airy, blue skies, cloud-tech, and aspirational. "
            "Our tone is educational, empowering, tech-forward, and extremely professional. "
            "We use phrases like 'The Era of Aviation Intelligence', 'Fly smarter', 'From Classroom to Cockpit'. "
            "I will provide you with a recent aviation news headline. "
            "Your task is to write a highly engaging Instagram caption about this news. "
            "You MUST speak as the AIRMAN brand. Relate the news back to the future of aviation, pilot safety, and innovation. "
            "Keep the caption snappy, use structured spacing, include premium emojis (✈️ 🚀 ☁️), a hook, and hashtags. "
            "Output ONLY the exact Instagram caption, NO conversational fluff, no greetings."
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
            )
        
        response = await loop.run_in_executor(None, _generate_caption)
        caption = response.text.strip().strip('"').strip("'")

        # 2. Generate a relevant image online using Imagen 4.0
        await message.reply_text("🎨 Generating an aviation aesthetic image via Imagen 4.0...")
        
        image_prompt = (
            "A hyper-realistic, highly cinematic, premium, modern, sleek aviation photograph representing: "
            f'"{headline}". '
            "High quality, 8k resolution, aspirational, no text in the image."
        )
            
        image_path = await generate_and_download_image(image_prompt)
        
        # 3. Burn the headline onto the image!
        add_headline_to_image(image_path, headline)
        
        # Send preview to Telegram
        await message.reply_photo(photo=open(image_path, 'rb'), caption="✅ Image found & text written. Now posting to Instagram...")
        
        # 4. Post to Instagram
        caption += "\n\n🌐 https://www.theairman.org/"
        logger.info(f"Attempting to post to Instagram with caption: {caption}")
        loop = asyncio.get_event_loop()
        media = await loop.run_in_executor(None, cl.photo_upload, image_path, caption)
        
        logger.info(f"Successfully posted to Instagram. Media ID: {media.pk}")
        await message.reply_text(f"✅ Post successfully published to Instagram!\n\nCaption used:\n{caption}")
        
    except Exception as e:
        error_msg = f"❌ Failed to process or post: {repr(e)}"
        logger.exception("Error in process_news_selection:")
        await message.reply_text(error_msg)
        
    finally:
        # Clean up the downloaded image
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"Cleaned up {image_path}")

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
    application.add_handler(CommandHandler("news", handle_news_command))
    application.add_handler(CallbackQueryHandler(process_news_selection))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
