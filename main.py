import os
import json
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from google import genai as _genai
from google.genai import types as _types

from src.logger import logger
from config.settings import GEMINI_API_KEY, GEMINI_TEXT_MODEL, TELEGRAM_BOT_TOKEN, LINKEDIN_ACCESS_TOKEN

# --- Modules (new backend) ---
from modules.news_fetcher import fetch_aviation_news
from modules.gemini_client import (
    generate_news_headline, generate_image_prompt, generate_caption,
    generate_image,
)
from modules.image_branding import apply_branding
from modules.instagram_poster import post_to_instagram
from modules.linkedin_poster import post_to_linkedin as _linkedin_post
from modules.feedback_store import init_db, create_post_record, mark_posted
from modules.festival_checker import get_todays_festival

# --- Improved prompts from src ---
from src.prompts.festival_prompts import build_festival_caption_prompt
from src.prompts.font_styles import FONT_STYLES, DEFAULT_FONT_KEY, font_keyboard_rows
from src.utils.csv_logger import log_post_to_csv

_gemini_client = _genai.Client(api_key=GEMINI_API_KEY)

load_dotenv()

_USER_PREFS_FILE = "data/user_prefs.json"


# ---------------------------------------------------------------------------
# User font preference helpers (unchanged)
# ---------------------------------------------------------------------------

def _load_user_prefs() -> dict:
    if os.path.exists(_USER_PREFS_FILE):
        try:
            with open(_USER_PREFS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_user_font(user_id: int, font_key: str) -> None:
    prefs = _load_user_prefs()
    prefs[str(user_id)] = font_key
    with open(_USER_PREFS_FILE, "w") as f:
        json.dump(prefs, f)


def _get_user_font(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    font = context.user_data.get("font_key")
    if font:
        return font
    prefs = _load_user_prefs()
    return prefs.get(str(user_id), DEFAULT_FONT_KEY)


# ---------------------------------------------------------------------------
# Content generation helpers (modules backend)
# ---------------------------------------------------------------------------

async def _generate_news_content(article: dict) -> tuple[str, str]:
    """Generate branded image + caption for a news article using modules."""
    loop = asyncio.get_event_loop()
    stamp = int(time.time())

    title   = article["title"]
    summary = article.get("description", "")
    source  = article.get("source", "Aviation News")
    url     = article.get("url", "")

    headline     = await loop.run_in_executor(None, generate_news_headline, title)
    image_prompt = await loop.run_in_executor(None, generate_image_prompt, title, summary, headline)
    raw_path     = await loop.run_in_executor(None, generate_image, image_prompt, f"news_raw_{stamp}.png")
    branded_path = await loop.run_in_executor(None, apply_branding, raw_path, headline, f"news_{stamp}.png")
    caption      = await loop.run_in_executor(None, generate_caption, title, summary, source, url)

    if raw_path != branded_path and os.path.exists(raw_path):
        os.remove(raw_path)

    caption += "\n\n🌐 https://www.theairman.org/"
    return caption, branded_path


async def _generate_festival_content(festival_name: str) -> tuple[str, str]:
    """Generate branded image + caption for a festival using improved prompts."""
    loop  = asyncio.get_event_loop()
    stamp = int(time.time())

    # 1. Caption + poster_title via AIRMAN brand prompt (returns JSON)
    def _gen_caption():
        return _gemini_client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=build_festival_caption_prompt(festival_name),
            config=_types.GenerateContentConfig(response_mime_type="application/json"),
        )

    response = await loop.run_in_executor(None, _gen_caption)
    try:
        raw_text     = response.text.strip().replace("```json", "").replace("```", "").strip()
        data         = json.loads(raw_text)
        caption      = data.get("caption", f"Happy {festival_name}!")
        poster_title = data.get("poster_title", festival_name.upper())
    except Exception:
        caption      = response.text.strip()
        poster_title = festival_name.upper()

    # 2. Direct Imagen prompt — no intermediate Gemini step
    image_prompt = (
        f"A photorealistic photograph celebrating '{festival_name}' with an aviation theme. "
        f"ONE cohesive real-world scene — NOT illustrated, NOT CGI, NOT a collage. "
        f"Prominently feature authentic {festival_name} visual elements (decorations, colors, symbols, cultural details) "
        "naturally integrated into a real aviation setting. "
        f"For example, if Diwali: glowing oil lamps lining a real runway at night, rangoli on tarmac, warm bokeh lights, aircraft silhouette. "
        "If Christmas: snow-dusted aircraft on a real airport apron, soft festive lights. If New Year: real fireworks over an airport skyline. "
        "Subtle cinematic quality through lighting only — golden hour, volumetric light, shallow depth of field, natural atmosphere. "
        f"The text '{poster_title}' overlaid once as clean minimal 2D sans-serif typography. "
        "Shot on professional camera, 8K resolution, single unified real-world composition."
    )

    # 3. Generate image + apply branding
    raw_path     = await loop.run_in_executor(None, generate_image, image_prompt, f"festival_raw_{stamp}.png")
    branded_path = await loop.run_in_executor(None, apply_branding, raw_path, poster_title, f"festival_{stamp}.png")

    if raw_path != branded_path and os.path.exists(raw_path):
        os.remove(raw_path)

    caption += "\n\n🌐 https://www.theairman.org/"
    return caption, branded_path


def _format_linkedin_caption(caption: str) -> str:
    text = caption.replace("🌐 https://www.theairman.org/", "").strip()
    text += "\n\n#AIRMAN #Aviation #AviationNews #FutureOfFlight"
    text += "\n\nLearn more: https://www.theairman.org/"
    return text


# ---------------------------------------------------------------------------
# Telegram command handlers (UX unchanged)
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I am the AIRMAN Social Media Bot. ✈️\n\n"
        "Send /help to see all available skills and commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🤖 **AIRMAN Social Media Bot Skills:**\n\n"
        "📰 **/news** - Fetch the top trending aviation news headlines.\n\n"
        "🎉 **/forcefestival [Name]** - Instantly generate a special festival poster (e.g. /forcefestival Diwali).\n\n"
        "🔤 **/font** - Choose a Google Font style for poster text.\n\n"
        "🚀 **/startauto** - Turn on Auto-Pilot for both daily news and calendar festivals.\n\n"
        "🛑 **/stopauto** - Deactivate Auto-Pilot scheduling.\n\n"
        "ℹ️ **/help** - Show this help message."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def font_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_key   = _get_user_font(context, update.effective_user.id)
    current_label = FONT_STYLES[current_key]["label"]
    keyboard = [
        [InlineKeyboardButton(label, callback_data=cb)]
        for label, cb in font_keyboard_rows()
    ]
    await update.message.reply_text(
        f"🔤 **Choose a Google Font for your posters:**\n\n"
        f"Current font: `{current_label}`\n\nPick one below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown',
    )


async def handle_font_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    font_key = query.data[len("font_"):]
    if font_key not in FONT_STYLES:
        await query.edit_message_text("❌ Unknown font. Please try /font again.")
        return

    style = FONT_STYLES[font_key]
    context.user_data["font_key"] = font_key
    _save_user_font(query.from_user.id, font_key)

    await query.edit_message_text(
        f"✅ Font updated!\n\n**{style['label']}**\n_{style['preview']}_\n\nYour next poster will use this style.",
        parse_mode='Markdown',
    )


async def handle_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    try:
        await message.reply_text(
            "🔎 Fetching top Aviation News...\n"
            "_(Bucket 1: collecting → Bucket 2: categorising → Bucket 3: ready)_",
            parse_mode='Markdown',
        )

        articles = fetch_aviation_news()
        if not articles:
            await message.reply_text("❌ No aviation news found right now. Try again later.")
            return

        context.user_data['articles'] = articles

        keyboard = []
        text = "📰 **Top Aviation News Headlines:**\n\n"
        for i, item in enumerate(articles):
            text += f"**{i+1}.** `[{item['category']}]`\n{item['title']}\n\n"
            keyboard.append([InlineKeyboardButton(f"Option {i+1}", callback_data=str(i))])
        text += "Please choose a news item to post! 👇"

        await message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
        )
    except Exception as e:
        logger.exception("Error in handle_news_command:")
        await message.reply_text(f"❌ Failed to fetch news: {repr(e)}")


async def process_news_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    message = query.message

    try:
        idx      = int(query.data)
        articles = context.user_data.get('articles', [])

        if not articles or idx >= len(articles):
            await query.edit_message_text("❌ Session expired. Please run /news again.")
            return

        article = articles[idx]
        await query.edit_message_text(
            text=f"✅ **You selected:**\n{article['title']}\n\n✍️ Generating caption and image... Hang tight!",
            parse_mode='Markdown',
        )

        caption, image_path = await _generate_news_content(article)

        # Create a feedback_store record for this post attempt
        record_id = create_post_record(
            post_type="news",
            news_title=article["title"],
            news_source=article.get("source", ""),
            news_url=article.get("url", ""),
            caption=caption,
            image_path=image_path,
        )

        context.user_data['pending_post'] = {
            'type':      'news',
            'headline':  article['title'],
            'caption':   caption,
            'image_path': image_path,
            'record_id': record_id,
        }

        prefix   = "📝 Preview:\n\n"
        suffix   = "\n\n👇 Choose where to post:"
        max_len  = 900 - len(prefix) - len(suffix)
        safe_cap = caption[:max_len] + "..." if len(caption) > max_len else caption

        keyboard = [
            [
                InlineKeyboardButton("✅ Post to Both",      callback_data="approve_both"),
                InlineKeyboardButton("📷 Instagram Only",    callback_data="approve_instagram"),
            ],
            [
                InlineKeyboardButton("💼 LinkedIn Only",     callback_data="approve_linkedin"),
                InlineKeyboardButton("❌ Cancel",            callback_data="approve_cancel"),
            ],
        ]

        with open(image_path, 'rb') as photo:
            await message.reply_photo(
                photo=photo,
                caption=f"{prefix}{safe_cap}{suffix}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
    except Exception as e:
        logger.exception("Error in process_news_selection:")
        await message.reply_text(f"❌ Failed to generate content: {repr(e)}")


async def handle_post_approval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    action  = query.data
    pending = context.user_data.get('pending_post')

    if not pending:
        await query.edit_message_caption(caption="❌ Session expired. Please start over.")
        return

    try:
        if action == "approve_cancel":
            reason_keyboard = [
                [
                    InlineKeyboardButton("🖼 Poor image quality",    callback_data="cancel_reason_poor_image"),
                    InlineKeyboardButton("✍️ Caption needs editing", callback_data="cancel_reason_caption"),
                ],
                [
                    InlineKeyboardButton("📰 Not relevant",          callback_data="cancel_reason_not_relevant"),
                    InlineKeyboardButton("🔁 Wrong content",         callback_data="cancel_reason_wrong_content"),
                ],
                [
                    InlineKeyboardButton("🚫 Other",                 callback_data="cancel_reason_other"),
                ],
            ]
            await query.edit_message_caption(
                caption="❌ Post cancelled.\n\n❓ Why did you cancel?",
                reply_markup=InlineKeyboardMarkup(reason_keyboard),
            )
            return

        await query.edit_message_caption(caption="📤 Publishing...")

        caption    = pending['caption']
        image_path = pending['image_path']
        headline   = pending.get('headline', 'Unknown')
        post_type  = pending['type']
        record_id  = pending.get('record_id')
        loop       = asyncio.get_event_loop()

        instagram_id = None
        linkedin_id  = None

        if action in ("approve_both", "approve_instagram"):
            logger.info("Posting to Instagram...")
            instagram_id = await loop.run_in_executor(None, post_to_instagram, image_path, caption)
            logger.info(f"Posted to Instagram. ID: {instagram_id}")

        if action in ("approve_both", "approve_linkedin"):
            if LINKEDIN_ACCESS_TOKEN:
                linkedin_caption = _format_linkedin_caption(caption)
                linkedin_id = await loop.run_in_executor(None, _linkedin_post, image_path, linkedin_caption)
                logger.info(f"Posted to LinkedIn. ID: {linkedin_id}")
            else:
                logger.warning("LinkedIn token not set — skipping LinkedIn post")

        combined_id = f"IG:{instagram_id or 'N/A'}|LI:{linkedin_id or 'N/A'}"
        log_post_to_csv(
            post_type="News" if post_type == "news" else "Festival",
            content=headline,
            media_id=combined_id,
        )

        if record_id:
            mark_posted(record_id, combined_id)

        platforms = []
        if instagram_id:
            platforms.append("Instagram")
        if linkedin_id:
            platforms.append("LinkedIn")

        await query.message.reply_text(f"✅ Successfully posted to {' and '.join(platforms or ['nowhere'])}!")
        safe_cap = caption[:4000] + "..." if len(caption) > 4000 else caption
        await query.message.reply_text(f"📝 **Caption used:**\n\n{safe_cap}", parse_mode='Markdown')

    except Exception as e:
        logger.exception("Error in handle_post_approval:")
        await query.message.reply_text(f"❌ Failed to post: {repr(e)}")
    finally:
        if pending and os.path.exists(pending['image_path']):
            os.remove(pending['image_path'])
        context.user_data.pop('pending_post', None)


async def handle_cancel_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    reason_map = {
        "cancel_reason_poor_image":    "Poor image quality",
        "cancel_reason_caption":       "Caption needs editing",
        "cancel_reason_not_relevant":  "Not relevant",
        "cancel_reason_wrong_content": "Wrong content",
        "cancel_reason_other":         "Other",
    }
    reason  = reason_map.get(query.data, "Unknown")
    pending = context.user_data.get('pending_post')

    if pending:
        if os.path.exists(pending['image_path']):
            os.remove(pending['image_path'])
        content   = pending.get('headline', 'Unknown')
        post_type = pending.get('type', 'unknown')
        log_post_to_csv(post_type, content, status=f"cancelled: {reason}")
        context.user_data.pop('pending_post', None)

    await query.edit_message_caption(
        caption=f"❌ Post cancelled.\n📋 Reason: {reason}\n\nThank you for the feedback!",
        reply_markup=None,
    )


# ---------------------------------------------------------------------------
# Auto-pilot jobs
# ---------------------------------------------------------------------------

async def auto_post_news(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id    = context.job.chat_id
    image_path = None
    try:
        await context.bot.send_message(chat_id, "⚙️ Auto-pilot: Waking up to post new aviation news...")

        articles = fetch_aviation_news()
        if not articles:
            await context.bot.send_message(chat_id, "⚙️ Auto-pilot: No new news found right now. Skipping.")
            return

        article  = articles[0]
        caption, image_path = await _generate_news_content(article)

        loop = asyncio.get_event_loop()
        instagram_id = await loop.run_in_executor(None, post_to_instagram, image_path, caption)
        logger.info(f"Auto-post to Instagram. ID: {instagram_id}")

        linkedin_id = None
        try:
            if LINKEDIN_ACCESS_TOKEN:
                linkedin_caption = _format_linkedin_caption(caption)
                linkedin_id = await loop.run_in_executor(None, _linkedin_post, image_path, linkedin_caption)
        except Exception as e:
            logger.warning(f"LinkedIn auto-post failed (continuing): {e}")

        combined_id = f"IG:{instagram_id}|LI:{linkedin_id or 'N/A'}"
        log_post_to_csv(post_type="News", content=article['title'], media_id=combined_id)

        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id, photo=photo, caption="✅ Auto-pilot successfully published!")
        safe_cap = caption[:4000] + "..." if len(caption) > 4000 else caption
        await context.bot.send_message(chat_id, f"📝 **Caption used:**\n\n{safe_cap}", parse_mode='Markdown')

    except Exception as e:
        logger.exception("Error in auto_post_news:")
        await context.bot.send_message(chat_id, f"❌ Auto-pilot error: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


async def auto_post_calendar(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id      = context.job.chat_id
    festival_name = get_todays_festival()

    if not festival_name:
        return

    record_file = f"data/posted_festivals_{datetime.now().year}.txt"
    if os.path.exists(record_file):
        with open(record_file) as f:
            if festival_name in f.read():
                return

    await context.bot.send_message(
        chat_id, f"🎉 **Calendar Trigger:** Today is {festival_name}! Generating special poster...",
        parse_mode='Markdown',
    )
    image_path = None
    try:
        caption, image_path = await _post_festival(festival_name)

        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id, photo=photo, caption="✅ Festival published!")
        safe_cap = caption[:4000] + "..." if len(caption) > 4000 else caption
        await context.bot.send_message(chat_id, f"📝 **Caption used:**\n\n{safe_cap}", parse_mode='Markdown')

        with open(record_file, "a") as f:
            f.write(festival_name + "\n")
    except Exception as e:
        logger.exception("Error in auto_post_calendar:")
        await context.bot.send_message(chat_id, f"❌ Festival auto-pilot error: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


async def startauto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    if context.job_queue.get_jobs_by_name(f"news_{chat_id}"):
        await update.message.reply_text("⚠️ Auto-posting is already running!")
        return

    context.job_queue.run_repeating(auto_post_news,     interval=3600, first=10,  chat_id=chat_id, name=f"news_{chat_id}")
    context.job_queue.run_repeating(auto_post_calendar, interval=3600, first=30,  chat_id=chat_id, name=f"cal_{chat_id}")
    await update.message.reply_text(
        "🚀 Auto-pilot ACTIVATED!\n"
        "Posting news every 1 hour, and checking for calendar festivals hourly.\n"
        "Send /stopauto anytime to turn it off."
    )


async def stopauto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    removed = False
    for prefix in ("news_", "cal_"):
        for job in context.job_queue.get_jobs_by_name(f"{prefix}{chat_id}"):
            job.schedule_removal()
            removed = True

    if removed:
        await update.message.reply_text("🛑 Auto-pilot DEACTIVATED.")
    else:
        await update.message.reply_text("⚠️ Auto-posting is not currently running.")


async def forcefestival(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please provide a festival name.\nUsage: `/forcefestival Diwali`", parse_mode='Markdown'
        )
        return

    festival_name = " ".join(context.args)
    logger.info(f"Force festival command received for: {festival_name}")
    await update.message.reply_text(f"🚀 Generating special festival post for '{festival_name}'...")
    image_path = None
    try:
        caption, image_path = await _post_festival(festival_name)
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="✅ Festival post published to Instagram!")
        safe_cap = caption[:4000] + "..." if len(caption) > 4000 else caption
        await update.message.reply_text(f"📝 **Caption used:**\n\n{safe_cap}", parse_mode='Markdown')
    except Exception as e:
        logger.exception(f"Error in forcefestival for {festival_name}:")
        await update.message.reply_text(f"❌ Error: {repr(e)}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# ---------------------------------------------------------------------------
# Festival posting helper
# ---------------------------------------------------------------------------

async def _post_festival(festival_name: str) -> tuple[str, str]:
    """Generate festival content and post to Instagram + LinkedIn."""
    caption, image_path = await _generate_festival_content(festival_name)

    loop = asyncio.get_event_loop()
    instagram_id = await loop.run_in_executor(None, post_to_instagram, image_path, caption)
    logger.info(f"Festival posted to Instagram. ID: {instagram_id}")

    linkedin_id = None
    try:
        if LINKEDIN_ACCESS_TOKEN:
            linkedin_caption = _format_linkedin_caption(caption)
            linkedin_id = await loop.run_in_executor(None, _linkedin_post, image_path, linkedin_caption)
            logger.info(f"Festival posted to LinkedIn. ID: {linkedin_id}")
    except Exception as e:
        logger.warning(f"LinkedIn festival post failed (continuing): {e}")

    log_post_to_csv(
        post_type="Festival",
        content=festival_name,
        media_id=f"IG:{instagram_id}|LI:{linkedin_id or 'N/A'}",
    )
    return caption, image_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Please check your .env file.")
        return

    # Initialise SQLite feedback database
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start",         start))
    application.add_handler(CommandHandler("help",          help_command))
    application.add_handler(CommandHandler("news",          handle_news_command))
    application.add_handler(CommandHandler("font",          font_command))
    application.add_handler(CommandHandler("startauto",     startauto))
    application.add_handler(CommandHandler("stopauto",      stopauto))
    application.add_handler(CommandHandler("forcefestival", forcefestival))

    application.add_handler(CallbackQueryHandler(handle_font_selection, pattern=r"^font_"))
    application.add_handler(CallbackQueryHandler(process_news_selection, pattern=r"^\d+$"))
    application.add_handler(CallbackQueryHandler(handle_post_approval,   pattern=r"^approve_"))
    application.add_handler(CallbackQueryHandler(handle_cancel_reason,   pattern=r"^cancel_reason_"))

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)

    application.add_error_handler(error_handler)

    logger.info("Bot is now polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()