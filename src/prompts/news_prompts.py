"""Image and caption prompts for the /news command."""

# ---------------------------------------------------------------------------
# Caption prompt
# ---------------------------------------------------------------------------

NEWS_CAPTION_SYSTEM_PROMPT = (
    "You are the official AI social media manager for 'AIRMAN' (https://www.theairman.org/). "
    "AIRMAN is a highly premium, sleek, futuristic aviation tech brand. We build Maverick AI and Skynet AI. "
    "Our visual identity is airy, blue skies, cloud-tech, and aspirational. "
    "Our tone is educational, empowering, tech-forward, and extremely professional. "
    "I will provide you with a recent aviation news headline.\n\n"
    "Your task:\n"
    "1. Write a highly engaging Instagram caption about this news. Speak as the AIRMAN brand, relate the news to the future of aviation/innovation, use spacing, emojis (✈️ 🚀 ☁️), and hashtags.\n"
    "2. Create a short, punchy 2-5 word title for the poster image (e.g., 'THE FUTURE OF FLIGHT', 'AUTONOMY TAKES FLIGHT').\n"
    "3. Write a one-sentence factual summary of what the news is about (plain English, no brand voice).\n"
    "Output ONLY a valid JSON object with keys 'caption', 'poster_title', and 'summary'. "
    "Do not include markdown formatting or backticks around the JSON."
)


# ---------------------------------------------------------------------------
# Imagen prompt builder
# ---------------------------------------------------------------------------

def build_news_imagen_prompt_request(
    headline: str, summary: str, poster_title: str, font_desc: str
) -> str:
    """
    Build the Gemini request that asks the model to write an Imagen prompt
    for a news poster.

    font_desc: visual description of the chosen Google Font (from font_styles.py).
    """
    return f"""Aviation news: {headline}. {summary}

Write an Imagen image generation prompt for a Hero Image with Text Overlay style Instagram poster.

Rules:
- 65% of the image is a rich aviation scene relevant to the news — airport, runway, cockpit, pilot, passengers, jet engine, control tower, hangar, cargo plane, helicopter, sky, whatever fits best. Lighting and colour palette decided naturally by the news context. Photorealistic, magazine cover quality.
- 35% of the image is the headline text rendered as a Hero Image with Text Overlay. The headline for this news is "{poster_title}". Use this exact text as the headline of the poster. The text is overlaid directly on top of the aviation scene — not in a separate box or panel. Place it anywhere that looks natural and visually balanced — the model decides where. The font must be white, {font_desc}. The text size must be small to medium — the letters should occupy no more than 25–30% of the image height. It should feel like a clean editorial headline sitting naturally on the scene, not dominating or overwhelming the image.
- No logos. No other text. Only "{poster_title}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""
