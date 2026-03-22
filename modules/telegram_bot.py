"""
Module: telegram_bot.py
Telegram admin bot — professional UX, training-oriented feedback.

Commands:
  /news    — Fetch aviation news and generate a post
  /fest    — Generate a festival post for today (or specify: /fest Diwali)
  /status  — Show post & feedback stats
  /help    — List all commands
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID, TELEGRAM_ADMIN_IDS
from modules.feedback_store import LABEL_DISPLAY, POSITIVE_LABELS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Callback data constants
# ---------------------------------------------------------------------------

CB_NEWS_SELECT      = "ns"   # ns:{1-5}
CB_POST_APPROVE     = "pa"
CB_POST_REJECT      = "pr"
CB_FESTIVAL_APPROVE = "fa"
CB_FESTIVAL_REJECT  = "fr"
CB_FEEDBACK         = "fb"   # fb:{label}

# ---------------------------------------------------------------------------
# Reusable keyboards
# ---------------------------------------------------------------------------

APPROVAL_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton("✅  Post",    callback_data=CB_POST_APPROVE),
    InlineKeyboardButton("❌  Reject",  callback_data=CB_POST_REJECT),
]])

FESTIVAL_KEYBOARD = InlineKeyboardMarkup([[
    InlineKeyboardButton("✅  Post",    callback_data=CB_FESTIVAL_APPROVE),
    InlineKeyboardButton("❌  Reject",  callback_data=CB_FESTIVAL_REJECT),
]])

POSITIVE_FEEDBACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🖼️  Image is great",    callback_data=f"{CB_FEEDBACK}:image_good")],
    [InlineKeyboardButton("📰  Headline is great", callback_data=f"{CB_FEEDBACK}:headline_good")],
    [InlineKeyboardButton("✍️  Caption is great",  callback_data=f"{CB_FEEDBACK}:caption_good")],
    [InlineKeyboardButton("🔤  Font is great",     callback_data=f"{CB_FEEDBACK}:font_good")],
])

NEGATIVE_FEEDBACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔤  Headline / Font are bad",   callback_data=f"{CB_FEEDBACK}:headline_font_bad")],
    [InlineKeyboardButton("🖼️  Image is bad",              callback_data=f"{CB_FEEDBACK}:image_bad")],
    [InlineKeyboardButton("✍️  Caption is bad",            callback_data=f"{CB_FEEDBACK}:caption_bad")],
    [InlineKeyboardButton("🔗  News & image don't match",  callback_data=f"{CB_FEEDBACK}:news_image_mismatch")],
])

# ---------------------------------------------------------------------------
# Singleton app
# ---------------------------------------------------------------------------

_app: Application | None = None

def get_app() -> Application:
    global _app
    if _app is None:
        _app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    return _app


# ---------------------------------------------------------------------------
# Outbound message helpers (called by orchestrator)
# ---------------------------------------------------------------------------

async def send_simple_message(text: str) -> None:
    await get_app().bot.send_message(
        chat_id=TELEGRAM_ADMIN_CHAT_ID,
        text=text,
        parse_mode="Markdown",
    )


async def send_news_selection(articles: list[dict]) -> None:
    """Categorised news list — one article per priority category."""
    lines = [
        "✈️  *AIRMAN AERONAUTICS*",
        "━━━━━━━━━━━━━━━━━━━━",
        "📰  *Today's Top Aviation News*\n",
    ]
    for i, a in enumerate(articles, 1):
        category = a.get("category", "")
        lines.append(f"*{i}.* {category}")
        lines.append(f"_{a['title']}_")
        lines.append(f"    {a.get('source', 'Unknown')}\n")

    lines.append("👇  *Select an article to post*")

    buttons = []
    for i, a in enumerate(articles, 1):
        category = a.get("category", f"#{i}")
        buttons.append([InlineKeyboardButton(
            f"{category}",
            callback_data=f"{CB_NEWS_SELECT}:{i}",
        )])

    await get_app().bot.send_message(
        chat_id=TELEGRAM_ADMIN_CHAT_ID,
        text="\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def send_news_post_preview(image_path: str, caption: str) -> None:
    """Send generated image with caption for admin review."""
    cap_display = caption[:880] + "\n…" if len(caption) > 880 else caption
    preview_caption = (
        "📋  *POST PREVIEW*\n"
        "─────────────────────\n\n"
        f"{cap_display}\n\n"
        "─────────────────────\n"
        "Ready to publish?"
    )
    with open(image_path, "rb") as f:
        await get_app().bot.send_photo(
            chat_id=TELEGRAM_ADMIN_CHAT_ID,
            photo=f,
            caption=preview_caption,
            parse_mode="Markdown",
            reply_markup=APPROVAL_KEYBOARD,
        )


async def send_festival_preview(image_path: str, caption: str, festival_name: str) -> None:
    cap_display = caption[:880] + "\n…" if len(caption) > 880 else caption
    preview_caption = (
        f"🎉  *{festival_name.upper()} POST PREVIEW*\n"
        "─────────────────────\n\n"
        f"{cap_display}\n\n"
        "─────────────────────\n"
        "Ready to publish?"
    )
    with open(image_path, "rb") as f:
        await get_app().bot.send_photo(
            chat_id=TELEGRAM_ADMIN_CHAT_ID,
            photo=f,
            caption=preview_caption,
            parse_mode="Markdown",
            reply_markup=FESTIVAL_KEYBOARD,
        )


async def send_auto_news_preview(image_path: str, caption: str) -> None:
    cap_display = caption[:860] + "\n…" if len(caption) > 860 else caption
    preview_caption = (
        "⏱  *AUTO-POST PREVIEW*\n"
        "─────────────────────\n"
        "_Will post in 10 min unless cancelled_\n\n"
        f"{cap_display}"
    )
    with open(image_path, "rb") as f:
        await get_app().bot.send_photo(
            chat_id=TELEGRAM_ADMIN_CHAT_ID,
            photo=f,
            caption=preview_caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅  Post Now", callback_data=CB_POST_APPROVE),
                InlineKeyboardButton("🚫  Cancel",   callback_data=CB_POST_REJECT),
            ]]),
        )


async def send_positive_feedback_request(ig_ok: bool = True, li_ok: bool = True) -> None:
    ig_line = "📸  Instagram   ✓" if ig_ok else "📸  Instagram   ✗ (failed)"
    li_line = "💼  LinkedIn    ✓" if li_ok else "💼  LinkedIn    ✗ (failed)"
    await get_app().bot.send_message(
        chat_id=TELEGRAM_ADMIN_CHAT_ID,
        text=(
            "✅  *POSTED SUCCESSFULLY*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{ig_line}\n"
            f"{li_line}\n\n"
            "Rate this post 👇"
        ),
        parse_mode="Markdown",
        reply_markup=POSITIVE_FEEDBACK_KEYBOARD,
    )


async def send_negative_feedback_request() -> None:
    await get_app().bot.send_message(
        chat_id=TELEGRAM_ADMIN_CHAT_ID,
        text=(
            "❌  *POST REJECTED*\n"
            "━━━━━━━━━━━━━━━\n\n"
            "What needs improvement? 👇"
        ),
        parse_mode="Markdown",
        reply_markup=NEGATIVE_FEEDBACK_KEYBOARD,
    )


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _is_admin(update: Update) -> bool:
    return update.effective_chat.id in TELEGRAM_ADMIN_IDS


def _admin_only(func):
    """Decorator: block and warn non-admin users."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not _is_admin(update):
            logger.warning(f"Unauthorized access attempt from chat_id={update.effective_chat.id}")
            await update.message.reply_text(
                "🔒  *Access Denied*\n\n"
                "This bot is private and restricted to authorized users only.",
                parse_mode="Markdown",
            )
            return
        await func(update, context)
    return wrapper


HELP_TEXT = (
    "✈️  *AIRMAN AERONAUTICS BOT*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Available commands:\n\n"
    "📰  /news    — Generate & post aviation news\n"
    "🎉  /fest    — Generate a festival post\n"
    "📊  /status  — View post & feedback stats\n"
    "❓  /help    — Show this message"
)


@_admin_only
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


@_admin_only
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


@_admin_only
async def handle_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    asyncio.create_task(_run_news_workflow())


@_admin_only
async def handle_fest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    festival_name = " ".join(context.args).strip() if context.args else ""
    asyncio.create_task(_run_festival_workflow(festival_name))


@_admin_only
async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from modules.feedback_store import get_feedback_summary, LABEL_DISPLAY
    s = get_feedback_summary()

    lines = [
        "📊  *POST STATISTICS*",
        "━━━━━━━━━━━━━━━━━━",
        f"Total posts   :  {s['total']}",
        f"✅  Posted     :  {s['posted']}",
        f"❌  Rejected   :  {s['rejected']}",
        "",
        f"👍  Positive feedback  :  {s['positive']}",
        f"👎  Negative feedback  :  {s['negative']}",
    ]

    if s["label_breakdown"]:
        lines.append("\n*Breakdown:*")
        for label, count in s["label_breakdown"].items():
            display = LABEL_DISPLAY.get(label, label)
            lines.append(f"  {display}  ×{count}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ---------------------------------------------------------------------------
# Workflow runners (background tasks)
# ---------------------------------------------------------------------------

async def _run_news_workflow() -> None:
    from modules.orchestrator import run_news_workflow
    try:
        await run_news_workflow()
    except Exception as e:
        logger.exception("News workflow failed")
        await send_simple_message(f"⚠️  Workflow error:\n`{e}`")


async def _run_festival_workflow(festival_name: str = "") -> None:
    from modules.orchestrator import run_festival_workflow
    from modules.festival_checker import get_todays_festival
    try:
        festival = festival_name or get_todays_festival()
        if festival:
            await run_festival_workflow(festival)
        else:
            await send_simple_message(
                "📅  No festival today.\n\nSpecify one with `/fest Diwali`"
            )
    except Exception as e:
        logger.exception("Festival workflow failed")
        await send_simple_message(f"⚠️  Festival workflow error:\n`{e}`")


# ---------------------------------------------------------------------------
# Callback handler
# ---------------------------------------------------------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not _is_admin(update):
        await query.answer("🔒 Access denied.", show_alert=True)
        return
    await query.answer()

    parts  = query.data.split(":", 1)
    action = parts[0]
    value  = parts[1] if len(parts) > 1 else ""

    if action == CB_NEWS_SELECT:
        context.bot_data["news_selection"] = int(value)
        await query.edit_message_reply_markup(reply_markup=None)

    elif action == CB_POST_APPROVE:
        context.bot_data["post_approval"] = True
        await query.edit_message_caption(
            caption="⏳  *Posting to Instagram & LinkedIn…*",
            parse_mode="Markdown",
        )

    elif action == CB_POST_REJECT:
        context.bot_data["post_approval"] = False
        await query.edit_message_caption(
            caption="❌  Post rejected.",
            parse_mode="Markdown",
        )

    elif action == CB_FESTIVAL_APPROVE:
        context.bot_data["festival_approval"] = True
        await query.edit_message_caption(
            caption="⏳  *Posting to Instagram & LinkedIn…*",
            parse_mode="Markdown",
        )

    elif action == CB_FESTIVAL_REJECT:
        context.bot_data["festival_approval"] = False
        await query.edit_message_caption(
            caption="❌  Festival post rejected.",
            parse_mode="Markdown",
        )

    elif action == CB_FEEDBACK:
        label         = value
        feedback_type = "positive" if label in POSITIVE_LABELS else "negative"
        context.bot_data["last_feedback"] = {
            "feedback_type":  feedback_type,
            "feedback_label": label,
        }
        display = LABEL_DISPLAY.get(label, label)
        await query.edit_message_text(
            text=(
                f"📊  *Feedback recorded*\n"
                f"─────────────────────\n"
                f"✓  {display}\n\n"
                f"_Use /news to generate a new post._"
            ),
            parse_mode="Markdown",
        )


# ---------------------------------------------------------------------------
# Text fallback
# ---------------------------------------------------------------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        logger.warning(f"Unauthorized message from chat_id={update.effective_chat.id}")
        await update.message.reply_text(
            "🔒  *Access Denied*\n\n"
            "This bot is private and restricted to authorized users only.",
            parse_mode="Markdown",
        )
        return
    await update.message.reply_text(
        "Type /help to see available commands.",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Start bot
# ---------------------------------------------------------------------------

def run_bot() -> None:
    app = get_app()

    # Register commands so Telegram shows them when user types "/"
    async def _set_commands(application: Application) -> None:
        await application.bot.set_my_commands([
            BotCommand("news",   "Generate & post aviation news"),
            BotCommand("fest",   "Generate a festival post"),
            BotCommand("status", "View post & feedback stats"),
            BotCommand("help",   "Show available commands"),
        ])

    app.post_init = _set_commands

    app.add_handler(CommandHandler("start",  handle_start))
    app.add_handler(CommandHandler("help",   handle_help))
    app.add_handler(CommandHandler("news",   handle_news))
    app.add_handler(CommandHandler("fest",   handle_fest))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Telegram bot started. Commands: /news /fest /status /help")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
