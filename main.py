import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from src.logger import logger
from src.config import (
    TELEGRAM_BOT_TOKEN, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD,
    LINKEDIN_ACCESS_TOKEN,
)
from src.services.instagram_service import login_instagram, get_instagram_client
from src.services.linkedin_service import post_to_linkedin, validate_linkedin_credentials
from src.services.news_service import fetch_top_aviation_news, fetch_top_aviation_news_detailed
from src.services.content_service import (
    generate_content, generate_festival_content, FESTIVALS,
)
from src.prompts.font_styles import FONT_STYLES, DEFAULT_FONT_KEY, font_keyboard_rows
from src.utils.csv_logger import log_post_to_csv

# Load environment variables
load_dotenv()

# User font preferences persisted to disk
_USER_PREFS_FILE = "data/user_prefs.json"


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
    """Return the user's chosen font key, falling back to the default."""
    # Check in-session first (fastest), then disk, then default
    font = context.user_data.get("font_key")
    if font:
        return font
    prefs = _load_user_prefs()
    return prefs.get(str(user_id), DEFAULT_FONT_KEY)


# --- Telegram command handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I am the AIRMAN Social Media Bot. ✈️\n\n"
        "Send /help to see all available skills and commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🤖 **AIRMAN Social Media Bot Skills:**\n\n"
        "📰 **/news** - Fetch the top 10 trending aviation news headlines.\n\n"
        "🎉 **/forcefestival [Name]** - Instantly generate a special festival poster (e.g. /forcefestival Diwali).\n\n"
        "🔤 **/font** - Choose a Google Font style for poster text.\n\n"
        "🚀 **/startauto** - Turn on Auto-Pilot for both daily news and calendar festivals.\n\n"
        "🛑 **/stopauto** - Deactivate Auto-Pilot scheduling.\n\n"
        "ℹ️ **/help** - Show this help message."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def font_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show a font picker so the user can choose their poster text style."""
    current_key = _get_user_font(context, update.effective_user.id)
    current_label = FONT_STYLES[current_key]["label"]

    keyboard = [
        [InlineKeyboardButton(label, callback_data=cb)]
        for label, cb in font_keyboard_rows()
    ]
    await update.message.reply_text(
        f"🔤 **Choose a Google Font for your posters:**\n\n"
        f"Current font: `{current_label}`\n\n"
        f"Pick one below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown',
    )


async def handle_font_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle font picker callback."""
    query = update.callback_query
    await query.answer()

    font_key = query.data[len("font_"):]  # strip 'font_' prefix
    if font_key not in FONT_STYLES:
        await query.edit_message_text("❌ Unknown font. Please try /font again.")
        return

    style = FONT_STYLES[font_key]
    context.user_data["font_key"] = font_key
    _save_user_font(query.from_user.id, font_key)

    await query.edit_message_text(
        f"✅ Font updated!\n\n"
        f"**{style['label']}**\n"
        f"Preview feel: _{style['preview']}_\n\n"
        f"Your next poster will use this style.",
        parse_mode='Markdown',
    )


async def handle_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches top news via the 3-bucket pipeline and presents them to the user to choose."""
    message = update.message
    try:
        await message.reply_text(
            "🔎 Fetching top 10 Aviation News...\n"
            "_(Bucket 1: collecting → Bucket 2: prioritising → Bucket 3: ready)_",
            parse_mode='Markdown',
        )
        # Bucket 3 result — each item has 'title' and 'category'
        news_items = fetch_top_aviation_news_detailed(10)
        context.user_data['headlines'] = [item['title'] for item in news_items]

        keyboard = []
        text = "📰 **Top 10 Aviation News Headlines:**\n\n"
        for i, item in enumerate(news_items):
            text += f"**{i+1}.** `[{item['category']}]`\n{item['title']}\n\n"
            keyboard.append([InlineKeyboardButton(f"Option {i+1}", callback_data=str(i))])
        text += "Please choose a news item to post! 👇"

        await message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
        )
    except Exception as e:
        logger.exception("Error in handle_news_command:")
        try:
            await message.reply_text(f"❌ Failed to fetch news: {repr(e)}")
        except Exception:
            pass


async def process_news_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the user's news selection and generates content for approval."""
    query = update.callback_query
    await query.answer()
    message = query.message

    try:
        idx = int(query.data)
        headlines = context.user_data.get('headlines', [])

        if not headlines or idx >= len(headlines):
            await query.edit_message_text(text="❌ Session expired or invalid selection. Please run /news again.")
            return

        headline = headlines[idx]
        font_key = _get_user_font(context, query.from_user.id)
        await query.edit_message_text(
            text=f"✅ **You selected:**\n{headline}\n\n✍️ Generating caption and image... Hang tight!",
            parse_mode='Markdown'
        )

        caption, image_path = await generate_content(headline, font_key=font_key)

        context.user_data['pending_post'] = {
            'type': 'news',
            'headline': headline,
            'caption': caption,
            'image_path': image_path,
        }

        # Telegram caption limit is 1024 chars
        prefix = "📝 Preview:\n\n"
        suffix = "\n\n👇 Choose where to post:"
        max_len = 900 - len(prefix) - len(suffix)
        safe_caption = caption[:max_len] + "..." if len(caption) > max_len else caption

        keyboard = [
            [
                InlineKeyboardButton("✅ Post to Both", callback_data="approve_both"),
                InlineKeyboardButton("📷 Instagram Only", callback_data="approve_instagram"),
            ],
            [
                InlineKeyboardButton("💼 LinkedIn Only", callback_data="approve_linkedin"),
                InlineKeyboardButton("❌ Cancel", callback_data="approve_cancel"),
            ],
        ]

        with open(image_path, 'rb') as photo:
            await message.reply_photo(
                photo=photo,
                caption=f"{prefix}{safe_caption}{suffix}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
    except Exception as e:
        logger.exception("Error in process_news_selection:")
        await message.reply_text(f"❌ Failed to generate content: {repr(e)}")


async def handle_post_approval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user approval for posting."""
    query = update.callback_query
    await query.answer()

    action = query.data
    pending = context.user_data.get('pending_post')

    if not pending:
        await query.edit_message_caption(caption="❌ Session expired. Please start over.")
        return

    try:
        if action == "approve_cancel":
            if os.path.exists(pending['image_path']):
                os.remove(pending['image_path'])
            await query.edit_message_caption(caption="❌ Post cancelled.")
            context.user_data.pop('pending_post', None)
            return

        await query.edit_message_caption(caption="📤 Publishing...")

        caption = pending['caption']
        image_path = pending['image_path']
        headline = pending.get('headline') or pending.get('content', 'Unknown')
        post_type = pending['type']
        cl = get_instagram_client()
        loop = asyncio.get_event_loop()

        instagram_id = None
        linkedin_id = None

        if action in ("approve_both", "approve_instagram"):
            logger.info("Posting to Instagram...")
            media = await loop.run_in_executor(None, cl.photo_upload, image_path, caption)
            instagram_id = media.pk
            logger.info(f"Successfully posted to Instagram. Media ID: {instagram_id}")

        if action in ("approve_both", "approve_linkedin"):
            if LINKEDIN_ACCESS_TOKEN:
                linkedin_caption = _format_linkedin_caption(caption)
                linkedin_result = await post_to_linkedin(linkedin_caption, image_path)
                linkedin_id = linkedin_result.get('id', 'N/A')
                logger.info(f"Successfully posted to LinkedIn. Post ID: {linkedin_id}")
            else:
                logger.warning("LinkedIn credentials not found - skipping LinkedIn post")

        log_post_to_csv(
            post_type="News" if post_type == "news" else "Festival",
            content=headline,
            media_id=f"IG:{instagram_id or 'N/A'}|LI:{linkedin_id or 'N/A'}",
        )

        platforms = []
        if instagram_id:
            platforms.append("Instagram")
        if linkedin_id:
            platforms.append("LinkedIn")

        await query.message.reply_text(f"✅ Successfully posted to {' and '.join(platforms)}!")
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await query.message.reply_text(f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')

    except Exception as e:
        logger.exception("Error in handle_post_approval:")
        await query.message.reply_text(f"❌ Failed to post: {repr(e)}")
    finally:
        if pending and os.path.exists(pending['image_path']):
            os.remove(pending['image_path'])
            logger.info(f"Cleaned up {pending['image_path']}")
        context.user_data.pop('pending_post', None)


# --- Auto-pilot jobs ---

async def auto_post_news(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automated job: fetch and post news."""
    chat_id = context.job.chat_id
    image_path = None
    try:
        await context.bot.send_message(chat_id, "⚙️ Auto-pilot: Waking up to post new aviation news...")

        headlines = fetch_top_aviation_news(1)
        if not headlines:
            await context.bot.send_message(chat_id, "⚙️ Auto-pilot: No new news found right now. Skipping.")
            return

        headline = headlines[0]
        caption, image_path = await generate_content(headline)

        cl = get_instagram_client()
        loop = asyncio.get_event_loop()

        media = await loop.run_in_executor(None, cl.photo_upload, image_path, caption)
        logger.info(f"Auto-post to Instagram. Media ID: {media.pk}")

        linkedin_id = None
        try:
            if LINKEDIN_ACCESS_TOKEN:
                linkedin_caption = _format_linkedin_caption(caption)
                result = await post_to_linkedin(linkedin_caption, image_path)
                linkedin_id = result.get('id', 'N/A')
        except Exception as e:
            logger.warning(f"LinkedIn auto-post failed (continuing): {e}")

        log_post_to_csv(
            post_type="News",
            content=headline,
            media_id=f"IG:{media.pk}|LI:{linkedin_id or 'N/A'}",
        )

        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id, photo=photo, caption="✅ Auto-pilot successfully published!")
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await context.bot.send_message(chat_id, f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')

    except Exception as e:
        logger.exception("Error in auto_post_news:")
        await context.bot.send_message(chat_id, f"❌ Auto-pilot error: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


async def auto_post_calendar(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automated job: check for festivals today and post."""
    chat_id = context.job.chat_id
    today_str = datetime.now().strftime("%m-%d")

    if today_str not in FESTIVALS:
        return

    festival_name = FESTIVALS[today_str]
    record_file = f"data/posted_festivals_{datetime.now().year}.txt"

    if os.path.exists(record_file):
        with open(record_file, "r") as f:
            if festival_name in f.read():
                return

    await context.bot.send_message(
        chat_id, f"🎉 **Calendar Trigger:** Today is {festival_name}! Generating special poster..."
    )
    image_path = None
    try:
        caption, image_path = await _post_festival(festival_name)
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id, photo=photo, caption="✅ Festival published!")
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await context.bot.send_message(chat_id, f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')

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

    context.job_queue.run_repeating(auto_post_news, interval=3600, first=10, chat_id=chat_id, name=f"news_{chat_id}")
    context.job_queue.run_repeating(auto_post_calendar, interval=3600, first=30, chat_id=chat_id, name=f"cal_{chat_id}")
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
    font_key = _get_user_font(context, update.effective_user.id)
    logger.info(f"Force festival command received for: {festival_name}")
    await update.message.reply_text(f"🚀 Generating special festival post for '{festival_name}'...")
    image_path = None
    try:
        caption, image_path = await _post_festival(festival_name, font_key=font_key)
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="✅ Festival post published to Instagram!")
        safe_caption = caption[:4000] + "..." if len(caption) > 4000 else caption
        await update.message.reply_text(f"📝 **Caption used:**\n\n{safe_caption}", parse_mode='Markdown')
        logger.info(f"Successfully posted festival: {festival_name}")
    except Exception as e:
        logger.exception(f"Error in forcefestival for {festival_name}:")
        await update.message.reply_text(f"❌ Error: {repr(e)}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# --- Helpers ---

def _format_linkedin_caption(caption: str) -> str:
    """Convert an Instagram caption to LinkedIn format."""
    text = caption.replace("🌐 https://www.theairman.org/", "").strip()
    text += "\n\n#AIRMAN #Aviation #AviationNews #FutureOfFlight"
    text += "\n\nLearn more: https://www.theairman.org/"
    return text


async def _post_festival(festival_name: str, font_key: str = DEFAULT_FONT_KEY) -> tuple[str, str]:
    """Generate festival content and post to Instagram + LinkedIn. Returns (caption, image_path)."""
    caption, image_path = await generate_festival_content(festival_name, font_key=font_key)

    cl = get_instagram_client()
    loop = asyncio.get_event_loop()

    media = await loop.run_in_executor(None, cl.photo_upload, image_path, caption)
    logger.info(f"Festival posted to Instagram. Media ID: {media.pk}")

    linkedin_id = None
    try:
        if LINKEDIN_ACCESS_TOKEN:
            linkedin_caption = _format_linkedin_caption(caption)
            result = await post_to_linkedin(linkedin_caption, image_path)
            linkedin_id = result.get('id', 'N/A')
            logger.info("Festival posted to LinkedIn")
    except Exception as e:
        logger.warning(f"LinkedIn festival post failed (continuing): {e}")

    log_post_to_csv(
        post_type="Festival",
        content=festival_name,
        media_id=f"IG:{media.pk}|LI:{linkedin_id or 'N/A'}",
    )
    return caption, image_path


# --- Main ---

def main() -> None:
    if not all([TELEGRAM_BOT_TOKEN, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return

    try:
        login_instagram()
    except Exception:
        logger.error("Cannot start bot without successful Instagram login.")
        return

    validate_linkedin_credentials()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", handle_news_command))
    application.add_handler(CommandHandler("font", font_command))
    application.add_handler(CommandHandler("startauto", startauto))
    application.add_handler(CommandHandler("stopauto", stopauto))
    application.add_handler(CommandHandler("forcefestival", forcefestival))
    application.add_handler(CallbackQueryHandler(handle_font_selection, pattern=r"^font_"))
    application.add_handler(CallbackQueryHandler(process_news_selection, pattern=r"^\d+$"))
    application.add_handler(CallbackQueryHandler(handle_post_approval, pattern=r"^approve_"))

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)

    application.add_error_handler(error_handler)

    logger.info("Bot is now polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
