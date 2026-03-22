import os
import logging
from google import genai
from google.genai import types
from config.settings import (
    GEMINI_API_KEY,
    GEMINI_TEXT_MODEL,
    GEMINI_IMAGE_MODEL,
    COMPANY_NAME,
    COMPANY_WEBSITE,
    IMAGE_OUTPUT_DIR,
)

logger = logging.getLogger(__name__)

# Text generation — standard Gemini API (API key)
client = genai.Client(api_key=GEMINI_API_KEY)

os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------


CAPTION_TEMPLATE = """
You are the social media manager for {company} — India's aviation intelligence platform.

Write an Instagram caption for this aviation news:

News Title: {title}
News Summary: {summary}
Source: {source}

--- CAPTION STRUCTURE (follow exactly) ---

PART 1 — NEWS STORY (3-4 sentences):
- Start with a strong hook — a fact, stat, or bold statement from the news (no "Exciting!" or "Big news!")
- Explain clearly what happened, who is involved, and why it matters to the aviation world
- Add relevant context — impact on passengers, airlines, India's aviation sector, or the industry
- Use 2-3 relevant emojis naturally within the text (✈️ 🛫 🌏 🚀 🏆 🔧 etc.) — not at the start of every line

PART 2 — ABOUT AIRMAN (exactly 2 lines):
- Line 1: Airman Aeronautics is India's aviation intelligence platform — your go-to for pilot career guidance, aviation news, and industry insights.
- Line 2: Follow us for more → www.theairman.org

PART 3 — HASHTAGS (new line, 20-25 tags):
- Always include: #AirmanAeronautics #Aviation #AviationNews #AviationIndia #IndianAviation
- Add news-specific tags (airline name, aircraft type, route, regulatory body, etc.)
- End with: #Pilot #AviationCommunity #Aviator #AerospaceEngineering #theairman

Output ONLY the caption. No labels, no section headings, no explanations.
"""


FESTIVAL_CAPTION_TEMPLATE = """
Write an Instagram caption for {company} celebrating {festival}.

Requirements:
- Warm, festive greeting tied to aviation
- 2-3 sentences about the festival and what it means for the aviation community
- Professional tone for an aviation brand
- Company website: {website}
- 10-15 relevant hashtags including #{festival_tag} and #AirmanAeronautics

Output ONLY the caption with hashtags.
"""


# ---------------------------------------------------------------------------
# Text generation helpers
# ---------------------------------------------------------------------------

def _generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
    )
    return response.text.strip()


def generate_news_headline(title: str) -> str:
    """Generate a short punchy headline (max 7 words) from a news title."""
    headline = _generate_text(
        f"Write a punchy headline for this aviation news: '{title}'. "
        f"Maximum 7 words. Title case. No punctuation at the end. No quotes. Just the headline."
    )
    headline = headline.replace("*", "").replace("_", "").replace("#", "").replace('"', "").strip()
    words = headline.split()
    if len(words) > 7:
        headline = " ".join(words[:7])
    return headline


def generate_image_prompt(title: str, summary: str, headline: str) -> str:
    instruction = f"""Aviation news: {title}. {summary}

Write an Imagen image generation prompt for a Hero Image with Text Overlay style Instagram poster.

Rules:
- 65% of the image is a rich aviation scene relevant to the news — airport, runway, cockpit, pilot, passengers, jet engine, control tower, hangar, cargo plane, helicopter, sky, whatever fits best. Lighting and colour palette decided naturally by the news context. Photorealistic, magazine cover quality.
- 35% of the image is the headline text rendered as a Hero Image with Text Overlay. The headline for this news is "{headline}". Use this exact text as the headline of the poster. The text is overlaid directly on top of the aviation scene — not in a separate box or panel. Place it anywhere that looks natural and visually balanced — the model decides where. The font must be a condensed bold neo-grotesque sans-serif, exactly like Impact or Anton: heavy weight, tight letter-spacing, all uppercase letters, no font variation allowed. Keep the text size moderate — not too large, it should feel like a clean editorial headline, not overwhelming the image.
- No logos. No other text. Only "{headline}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""

    prompt = _generate_text(instruction)
    print(f"\n{'='*60}\nGENERATED IMAGE PROMPT:\n{prompt}\n{'='*60}\n")
    logger.info(f"Image prompt generated: {prompt[:120]}...")
    return prompt.strip()


def generate_caption(title: str, summary: str, source: str, url: str) -> str:
    return _generate_text(CAPTION_TEMPLATE.format(
        company=COMPANY_NAME, title=title, summary=summary,
        source=source, url=url, website=COMPANY_WEBSITE,
    ))


def generate_festival_headline(festival_name: str) -> str:
    headline = _generate_text(
        f"Write a headline for a {festival_name} Instagram post for an aviation brand. "
        f"Maximum 8 words. Plain text only. No punctuation at the end. No asterisks. No quotes. Just the headline."
    )
    headline = headline.replace("*", "").replace("_", "").replace("#", "").strip()
    # Hard limit to 8 words regardless of model output
    words = headline.split()
    if len(words) > 8:
        headline = " ".join(words[:8])
    return headline


def generate_festival_image_prompt(festival_name: str, headline: str) -> str:
    instruction = f"""Festival: {festival_name}. Headline: {headline}.

Write an Imagen image generation prompt for a Hero Image with Text Overlay style Instagram poster celebrating {festival_name} for a premium aviation brand. The result must look like a high-budget campaign poster from a world-class airline or aviation company. think premium Airlines festival ads.

Rules:
- First understand what {festival_name} - festival or day or event is truly about — its emotion, its people, its core meaning.
- match the {festival_name} with an aviation scene that fit emotion and meaning with object and things realted to the {festival_name}, make scene and concept that truly captures the essence of the festival in an aviation context. Be creative and authentic — don't just add a random prop or colour and call it a day. The scene should feel like it belongs to that festival, not just a generic aviation image with a festival element pasted on.
- If it is a cultural, religious, or national occasion, the scene captures the authentic mood, atmosphere, and spirit of that occasion within an aviation setting.
- Single clean composition. One strong focal point. No clutter, no crowds, no props piled together. Strong negative space. Cinematic depth.
- Festival mood through lighting, colour grading, and atmosphere — use any object needed for that festival (e.g. Diwali diyas, Holi colours, Christmas lights, Independence Day sky) but make it feel natural and not forced. The festival element should be part of the scene, not an added prop.
- If humans appear, they must look completely real — must me real human like natural skin texture, real facial features, genuine unposed expression, authentic body posture. Not perfect, not plastic, not symmetrical like a render. Like a real person photographed in a real moment. like realtisic people not as look like artificially generated ones.
- Lighting and colour must match the mood of {festival_name} — choose naturally from sky blue, soft daylight, cool white, golden sunlight or natural ambient tones. Let the festival decide the colour, not a fixed style.
- Composition: rule of thirds, breathing room, strong leading lines.
- The headline "{headline}" overlaid directly on the scene as bold Hero Text — not in a box or panel. Font: heavy weight, bold, strong — like Impact or Anton. Thick strokes, no decorative details, maximum legibility. Medium size, well-spaced. Placed in a visually balanced position — top, bottom, or center — wherever it sits naturally without blocking the main subject. Letter case: Sentence case or Title Case for patriotic festivals, title case for warm ones.
- No logos. No other text. Only "{headline}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""

    prompt = _generate_text(instruction)
    print(f"\n{'='*60}\nFESTIVAL IMAGE PROMPT:\n{prompt}\n{'='*60}\n")
    logger.info(f"Festival image prompt generated: {prompt[:120]}...")
    return prompt.strip()


def generate_festival_caption(festival_name: str) -> str:
    festival_tag = festival_name.replace(" ", "")
    return _generate_text(FESTIVAL_CAPTION_TEMPLATE.format(
        company=COMPANY_NAME, festival=festival_name,
        website=COMPANY_WEBSITE, festival_tag=festival_tag,
    ))


# ---------------------------------------------------------------------------
# Image generation (Imagen 4)
# ---------------------------------------------------------------------------

def generate_image(image_prompt: str, filename: str = "generated_image.png") -> str:
    """
    Generate an image using Imagen via the standard Gemini API key (no GCP credentials needed).
    Attempt 1: full prompt
    Attempt 2: truncated prompt (first 300 chars)
    """
    output_path = os.path.join(IMAGE_OUTPUT_DIR, filename)

    for attempt, prompt in enumerate([image_prompt, image_prompt[:300]], start=1):
        logger.info(f"Image generation attempt {attempt}...")
        result = client.models.generate_images(
            model=GEMINI_IMAGE_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            ),
        )
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Image saved to {output_path}")
            return output_path
        logger.warning(f"Attempt {attempt} returned no images.")

    raise ValueError("Imagen 4 returned no images after 2 attempts. Check the prompt or API quota.")
