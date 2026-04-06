"""
Module: orchestrator.py
Workflow engine — silent generation, single post preview, label-based feedback.

Flows:
  run_news_workflow()        — /news command (admin selects article, approves post)
  run_festival_workflow()    — /fest command (admin approves festival post)
  run_auto_news_workflow()   — hourly scheduler (auto-selects, 10-min timer)
  run_daily_workflow()       — 9 AM scheduler entry point
"""

import asyncio
import logging
import os
from datetime import datetime

from config.settings import IMAGE_OUTPUT_DIR
from modules import (
    feedback_store,
    festival_checker,
    gemini_client,
    image_branding,
    instagram_poster,
    linkedin_poster,
    news_fetcher,
)
from modules.telegram_bot import (
    get_app,
    send_auto_news_preview,
    send_festival_preview,
    send_negative_feedback_request,
    send_news_post_preview,
    send_news_selection,
    send_positive_feedback_request,
    send_simple_message,
)

logger = logging.getLogger(__name__)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _wait_for_bot_data(key: str, timeout: int = 300, poll: float = 2.0):
    """Poll bot_data for key. Raises TimeoutError if not set within timeout."""
    app  = get_app()
    elapsed = 0.0
    while elapsed < timeout:
        value = app.bot_data.get(key)
        if value is not None:
            del app.bot_data[key]
            return value
        await asyncio.sleep(poll)
        elapsed += poll
    raise TimeoutError(f"No response within {timeout}s for '{key}'")


def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _clear_stale(*keys: str) -> None:
    bot_data = get_app().bot_data
    for k in keys:
        bot_data.pop(k, None)


# ---------------------------------------------------------------------------
# News workflow  (/news)
# ---------------------------------------------------------------------------

async def run_news_workflow() -> None:
    _clear_stale("news_selection", "post_approval", "last_feedback")

    articles = news_fetcher.fetch_aviation_news()
    if not articles:
        await send_simple_message("📭  No aviation news found right now. Try again later.")
        return

    # Let admin pick which article to post
    await send_news_selection(articles)

    try:
        selection = await _wait_for_bot_data("news_selection", timeout=600)
    except TimeoutError:
        await send_simple_message("⏱  Timed out waiting for your selection.")
        return

    idx = int(selection) - 1
    if not (0 <= idx < len(articles)):
        await send_simple_message("Invalid selection. Use /news to try again.")
        return

    selected = articles[idx]

    # Single loading message — no intermediate step messages
    await send_simple_message("⏳  Generating your post, please wait…")

    headline     = gemini_client.generate_news_headline(selected["title"])
    image_prompt = gemini_client.generate_image_prompt(
        selected["title"], selected["description"], headline
    )
    raw_path     = gemini_client.generate_image(image_prompt, f"news_raw_{_stamp()}.png")
    branded_path = image_branding.apply_branding(
        raw_path, output_filename=f"news_branded_{_stamp()}.png"
    )
    caption      = gemini_client.generate_caption(
        selected["title"], selected["description"],
        selected.get("source", ""), selected.get("url", ""),
    )

    # Create DB record before showing preview
    record_id = feedback_store.create_post_record(
        post_type    = "news",
        news_title   = selected["title"],
        news_source  = selected.get("source", ""),
        news_url     = selected.get("url", ""),
        headline     = headline,
        image_prompt = image_prompt,
        caption      = caption,
        image_path   = branded_path,
    )

    # Show post once — Post or Reject
    await send_news_post_preview(branded_path, caption)

    try:
        approved = await _wait_for_bot_data("post_approval", timeout=600)
    except TimeoutError:
        await send_simple_message("⏱  No response. Post cancelled.")
        return

    if approved:
        post_id = "n/a"
        ig_ok   = True
        li_ok   = True

        try:
            post_id = instagram_poster.post_to_instagram(branded_path, caption)
        except Exception as e:
            ig_ok = False
            logger.error(f"Instagram post failed: {e}")

        try:
            linkedin_poster.post_to_linkedin(branded_path, caption)
        except Exception as e:
            li_ok = False
            logger.error(f"LinkedIn post failed: {e}")

        feedback_store.mark_posted(record_id, post_id)
        await send_positive_feedback_request(ig_ok=ig_ok, li_ok=li_ok)
    else:
        await send_negative_feedback_request()

    # Wait for feedback label
    try:
        fb = await _wait_for_bot_data("last_feedback", timeout=3600)
    except TimeoutError:
        logger.warning("No feedback received within 1 hour — skipping.")
        return

    feedback_store.save_feedback(
        record_id      = record_id,
        feedback_type  = fb["feedback_type"],
        feedback_label = fb["feedback_label"],
    )


# ---------------------------------------------------------------------------
# Festival workflow  (/fest)
# ---------------------------------------------------------------------------

async def run_festival_workflow(festival_name: str) -> None:
    logger.info(f"Festival workflow: {festival_name}")
    _clear_stale("festival_approval", "last_feedback")

    await send_simple_message(f"⏳  Generating festival post for *{festival_name}*, please wait…")

    headline     = gemini_client.generate_festival_headline(festival_name)
    caption      = gemini_client.generate_festival_caption(festival_name)
    image_prompt = gemini_client.generate_festival_image_prompt(festival_name, headline)
    raw_path     = gemini_client.generate_image(image_prompt, f"festival_raw_{_stamp()}.png")
    branded_path = image_branding.apply_branding(
        raw_path, output_filename=f"festival_branded_{_stamp()}.png"
    )

    record_id = feedback_store.create_post_record(
        post_type    = "festival",
        news_title   = festival_name,
        headline     = headline,
        image_prompt = image_prompt,
        caption      = caption,
        image_path   = branded_path,
    )

    await send_festival_preview(branded_path, caption, festival_name)

    try:
        approved = await _wait_for_bot_data("festival_approval", timeout=600)
    except TimeoutError:
        await send_simple_message("⏱  No response. Festival post cancelled.")
        return

    if approved:
        post_id = "n/a"
        ig_ok   = True
        li_ok   = True

        try:
            post_id = instagram_poster.post_to_instagram(branded_path, caption)
        except Exception as e:
            ig_ok = False
            logger.error(f"Instagram festival post failed: {e}")

        try:
            linkedin_poster.post_to_linkedin(branded_path, caption)
        except Exception as e:
            li_ok = False
            logger.error(f"LinkedIn festival post failed: {e}")

        feedback_store.mark_posted(record_id, post_id)
        await send_positive_feedback_request(ig_ok=ig_ok, li_ok=li_ok)
    else:
        await send_negative_feedback_request()

    try:
        fb = await _wait_for_bot_data("last_feedback", timeout=3600)
    except TimeoutError:
        logger.warning("No festival feedback received — skipping.")
        return

    feedback_store.save_feedback(
        record_id      = record_id,
        feedback_type  = fb["feedback_type"],
        feedback_label = fb["feedback_label"],
    )


# ---------------------------------------------------------------------------
# Auto news workflow  (hourly scheduler)
# ---------------------------------------------------------------------------

async def run_auto_news_workflow() -> None:
    logger.info("Auto news workflow triggered.")
    _clear_stale("post_approval", "last_feedback")

    articles = news_fetcher.fetch_aviation_news()
    if not articles:
        logger.info("Auto-check: no news found.")
        return

    selected = articles[0]
    await send_simple_message(
        f"⏳  *Auto-post* — generating from:\n_{selected['title']}_"
    )

    headline     = gemini_client.generate_news_headline(selected["title"])
    image_prompt = gemini_client.generate_image_prompt(
        selected["title"], selected["description"], headline
    )
    raw_path     = gemini_client.generate_image(image_prompt, f"news_raw_{_stamp()}.png")
    branded_path = image_branding.apply_branding(
        raw_path, output_filename=f"news_branded_{_stamp()}.png"
    )
    caption      = gemini_client.generate_caption(
        selected["title"], selected["description"],
        selected.get("source", ""), selected.get("url", ""),
    )

    record_id = feedback_store.create_post_record(
        post_type    = "news",
        news_title   = selected["title"],
        news_source  = selected.get("source", ""),
        news_url     = selected.get("url", ""),
        headline     = headline,
        image_prompt = image_prompt,
        caption      = caption,
        image_path   = branded_path,
    )

    await send_auto_news_preview(branded_path, caption)

    try:
        approved = await _wait_for_bot_data("post_approval", timeout=600)
    except TimeoutError:
        approved = True  # auto-post after 10 min silence
        await send_simple_message("⏱  No response — auto-posting now…")

    if not approved:
        await send_simple_message("🚫  Auto-post cancelled.")
        return

    post_id = "n/a"
    ig_ok   = True
    li_ok   = True

    try:
        post_id = instagram_poster.post_to_instagram(branded_path, caption)
    except Exception as e:
        ig_ok = False
        logger.error(f"Instagram auto-post failed: {e}")

    try:
        linkedin_poster.post_to_linkedin(branded_path, caption)
    except Exception as e:
        li_ok = False
        logger.error(f"LinkedIn auto-post failed: {e}")

    feedback_store.mark_posted(record_id, post_id)
    await send_positive_feedback_request(ig_ok=ig_ok, li_ok=li_ok)

    try:
        fb = await _wait_for_bot_data("last_feedback", timeout=3600)
    except TimeoutError:
        logger.warning("No auto-post feedback received — skipping.")
        return

    feedback_store.save_feedback(
        record_id      = record_id,
        feedback_type  = fb["feedback_type"],
        feedback_label = fb["feedback_label"],
    )


# ---------------------------------------------------------------------------
# Daily entry point  (9 AM scheduler)
# ---------------------------------------------------------------------------

async def run_daily_workflow() -> None:
    logger.info("Daily workflow started.")

    festival = festival_checker.get_todays_festival()
    if festival:
        await run_festival_workflow(festival)

    await run_news_workflow()
