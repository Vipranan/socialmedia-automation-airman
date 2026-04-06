"""Content generation service using Gemini AI."""
import asyncio
import json

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY
from src.logger import logger
from src.prompts.festival_prompts import build_festival_caption_prompt
from src.prompts.font_styles import DEFAULT_FONT_KEY, get_font_description
from src.prompts.news_prompts import (
    NEWS_CAPTION_SYSTEM_PROMPT,
    build_news_imagen_prompt_request,
)
from src.services.image_service import (
    format_image_for_instagram,
    generate_and_download_image,
)

# Festival calendar
FESTIVALS = {
    "01-01": "New Year",
    "01-14": "Makar Sankranti & Pongal",
    "01-26": "Republic Day",
    "02-14": "Valentine's Day",
    "03-08": "International Women's Day",
    "04-22": "Earth Day",
    "08-15": "Independence Day",
    "08-19": "National Aviation Day",
    "10-31": "Halloween",
    "12-25": "Christmas",
}


def _get_genai_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API key not found in .env")
    return genai.Client(api_key=GEMINI_API_KEY)


async def _run_in_executor(func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func)


async def generate_content(headline: str, font_key: str = DEFAULT_FONT_KEY) -> tuple[str, str]:
    """Generate caption and image for a news headline. Returns (caption, image_path)."""
    client = _get_genai_client()
    font_desc = get_font_description(font_key)

    def _gen_caption():
        return client.models.generate_content(
            model='gemini-2.5-flash',
            contents=NEWS_CAPTION_SYSTEM_PROMPT + "\n\nHeadline: '" + headline + "'",
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

    response = await _run_in_executor(_gen_caption)
    try:
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        caption = data.get("caption", "Aviation News")
        poster_title = data.get("poster_title", "AVIATION NEWS")
        summary = data.get("summary", headline)
    except Exception as e:
        logger.error(f"Failed to parse JSON from Gemini: {e}")
        caption = response.text.strip()
        poster_title = headline[:30]
        summary = headline

    imagen_prompt_request = build_news_imagen_prompt_request(headline, summary, poster_title, font_desc)

    def _gen_imagen_prompt():
        return client.models.generate_content(
            model='gemini-2.5-flash',
            contents=imagen_prompt_request
        )

    imagen_response = await _run_in_executor(_gen_imagen_prompt)
    image_prompt = imagen_response.text.strip()
    logger.info(f"Imagen prompt: {image_prompt}")

    image_path = await generate_and_download_image(image_prompt)
    format_image_for_instagram(image_path)

    caption += "\n\n🌐 https://www.theairman.org/"
    return caption, image_path


async def generate_festival_content(festival_name: str, font_key: str = DEFAULT_FONT_KEY) -> tuple[str, str]:
    """Generate caption and image for a festival. Returns (caption, image_path)."""
    logger.info(f"Starting festival post generation for: {festival_name}")
    client = _get_genai_client()

    def _gen_caption():
        return client.models.generate_content(
            model='gemini-2.5-flash',
            contents=build_festival_caption_prompt(festival_name),
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

    response = await _run_in_executor(_gen_caption)
    try:
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_text)
        caption = data.get("caption", f"Happy {festival_name}!")
        poster_title = data.get("poster_title", f"HAPPY {festival_name}".upper())
        logger.info(f"Caption generated successfully. Title: {poster_title}")
    except Exception as e:
        logger.warning(f"Failed to parse JSON from Gemini: {e}")
        caption = response.text.strip()
        poster_title = festival_name.upper()

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
    logger.info(f"Imagen prompt: {image_prompt}")

    image_path = await generate_and_download_image(image_prompt)
    logger.info(f"Image generated: {image_path}")

    format_image_for_instagram(image_path)

    caption += "\n\n🌐 https://www.theairman.org/"
    return caption, image_path
