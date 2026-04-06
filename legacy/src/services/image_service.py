"""Image generation and formatting service."""
import asyncio
import io
import os
import uuid

from google import genai
from google.genai import types
from PIL import Image

from src.config import GEMINI_API_KEY
from src.logger import logger


def _get_genai_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API key not found in .env")
    return genai.Client(api_key=GEMINI_API_KEY)


async def generate_and_download_image(prompt: str) -> str:
    """Generates an image using Google Imagen 4.0 and saves it."""
    client = _get_genai_client()
    logger.info(f"Generating image with prompt: '{prompt}'")

    loop = asyncio.get_event_loop()

    def _generate():
        return client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )

    result = await loop.run_in_executor(None, _generate)

    if not result.generated_images:
        raise ValueError("Image generation failed to return an image from Google Imagen.")

    image = Image.open(io.BytesIO(result.generated_images[0].image.image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')

    filename = f"generated_{uuid.uuid4().hex[:8]}.jpg"
    image.save(filename, "JPEG")
    return filename


def format_image_for_instagram(image_path: str):
    """Resizes to 1080x1080 and adds the AIRMAN logo."""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        desired_size = 1080
        ratio = min(desired_size / img.width, desired_size / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        new_img = Image.new("RGB", (desired_size, desired_size), (0, 0, 0))
        paste_x = (desired_size - new_width) // 2
        paste_y = (desired_size - new_height) // 2
        new_img.paste(img, (paste_x, paste_y))
        img = new_img

        # Add logo
        try:
            logo_path = "assets/logo.png"
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_ratio = 80 / logo.width
                logo_resized = logo.resize((80, int(logo.height * logo_ratio)), Image.Resampling.LANCZOS)
                margin = 30
                px = img.width - logo_resized.width - margin
                img.paste(logo_resized, (px, margin), mask=logo_resized)
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")

        img = img.convert("RGB")
        img.save(image_path, "JPEG", quality=95)
        logger.info(f"Formatted and branded {image_path} for Instagram")
    except Exception as e:
        logger.error(f"Failed to format image: {e}")
