"""
Module: image_branding.py
Applies Airman Aeronautics branding on the generated image.

Layout:
  Top-right  : airman.png logo (88×88px)
  Bottom bar : [HEADLINE]  — Impact / Neo-Grotesque condensed bold
               [www.airman.org] — same font family, lighter, white, centred
"""

import os

from PIL import Image, ImageDraw, ImageFont

from config.settings import (
    COMPANY_LOGO_PATH,
    IMAGE_OUTPUT_DIR,
)

_ASSETS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))

# Font search order — condensed bold neo-grotesque (Impact / Anton / DIN Condensed)
_IMPACT_PATHS = [
    os.path.join(_ASSETS, "Anton-Regular.ttf"),          # download from Google Fonts → assets/
    "/System/Library/Fonts/Supplemental/Impact.ttf",     # macOS
    "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
    os.path.join(_ASSETS, "BricolageGrotesque-Bold.ttf"),
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

DISPLAY_URL = "www.theairman.org"


def _load_impact(size: int) -> ImageFont.FreeTypeFont:
    """Load Impact / condensed bold neo-grotesque font."""
    for path in _IMPACT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def apply_branding(
    image_path: str,
    headline: str = "",
    output_filename: str = "branded_image.png",
) -> str:
    """
    Apply Airman branding on the Imagen-generated scene.

    Elements added by Pillow (guaranteed font & layout):
      1. Logo          — top-right, 88×88px
      2. Headline      — Impact/Anton condensed bold, large, white + drop-shadow
      3. www.airman.org — same font family, smaller, pure white, centred below headline
    """
    img = Image.open(image_path).convert("RGBA")
    W, H = img.size
    MARGIN = int(W * 0.035)
    LOGO_SIZE = 88

    # -------------------------------------------------------------------
    # 1. Logo — top-right corner, clean margin
    # -------------------------------------------------------------------
    if os.path.exists(COMPANY_LOGO_PATH):
        try:
            logo = Image.open(COMPANY_LOGO_PATH).convert("RGBA")
            logo = logo.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
            lx = W - LOGO_SIZE - MARGIN
            ly = MARGIN
            img.paste(logo, (lx, ly), logo)
        except Exception:
            pass

    # -------------------------------------------------------------------
    # 2. Website URL — single thin semi-transparent line at bottom
    # -------------------------------------------------------------------
    draw = ImageDraw.Draw(img)

    url_size = max(16, W // 58)   # small, clean

    # Helvetica Neue for website URL
    url_font = None
    for path in [
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        os.path.join(_ASSETS, "Manrope-Regular.ttf"),
    ]:
        if os.path.exists(path):
            try:
                url_font = ImageFont.truetype(path, url_size)
                break
            except Exception:
                continue
    if url_font is None:
        url_font = _load_impact(url_size)

    url_bbox   = draw.textbbox((0, 0), DISPLAY_URL, font=url_font)
    url_text_h = url_bbox[3] - url_bbox[1]
    url_text_w = url_bbox[2] - url_bbox[0]

    PAD_V  = int(MARGIN * 0.5)
    BAR_H  = url_text_h + PAD_V * 2

    # Single thin semi-transparent strip — just enough for the URL
    bar = Image.new("RGBA", (W, BAR_H), (0, 0, 0, 100))
    img.paste(bar, (0, H - BAR_H), bar)
    draw = ImageDraw.Draw(img)

    ux = (W - url_text_w) // 2
    uy = H - BAR_H + PAD_V
    draw.text((ux, uy), DISPLAY_URL, font=url_font, fill=(255, 255, 255, 255))

    # -------------------------------------------------------------------
    # 3. Save
    # -------------------------------------------------------------------
    output_path = os.path.join(IMAGE_OUTPUT_DIR, output_filename)
    img.convert("RGB").save(output_path, "PNG", quality=95)
    return output_path
