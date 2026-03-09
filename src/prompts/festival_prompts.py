"""Image and caption prompts for the /forcefestival command."""

# ---------------------------------------------------------------------------
# Festival style classification
# ---------------------------------------------------------------------------

FESTIVAL_STYLE_CINEMATIC = {
    "New Year", "Makar Sankranti & Pongal", "Diwali", "Halloween", "Christmas",
    "Earth Day", "Eid", "Holi",
}
FESTIVAL_STYLE_INTIMATE = {
    "Valentine's Day", "Mother's Day", "Fathers Day", "International Women's Day",
    "Republic Day", "Thanksgiving",
}
FESTIVAL_STYLE_CELEBRATION = {
    "Independence Day", "National Aviation Day", "Airshow",
}


def get_festival_style(festival_name: str) -> str:
    name = festival_name.strip()
    if name in FESTIVAL_STYLE_INTIMATE:
        return "intimate"
    if name in FESTIVAL_STYLE_CELEBRATION:
        return "celebration"
    return "cinematic"


# ---------------------------------------------------------------------------
# Caption prompt builder
# ---------------------------------------------------------------------------

def build_festival_caption_prompt(festival_name: str) -> str:
    """
    Build the Gemini prompt that generates the Instagram caption and poster
    title for a festival post.
    """
    return (
        "You are the official AI social media manager for 'AIRMAN' (https://www.theairman.org/). "
        "AIRMAN is a highly premium, sleek, futuristic aviation tech brand. "
        "Our visual identity is airy, blue skies, cloud-tech, and aspirational. "
        f"Today is {festival_name}.\n\n"
        "Your task:\n"
        f"1. Write a highly engaging Instagram caption celebrating '{festival_name}'. "
        "Speak as the AIRMAN brand, beautifully connecting the festival's specific themes to aviation, skies, flight, or engineered progress.\n"
        "2. Create a short, punchy 2-5 word title for the poster image (e.g., 'LOVE IS IN THE AIR').\n"
        "Output ONLY a valid JSON object with keys 'caption' and 'poster_title'."
    )


# ---------------------------------------------------------------------------
# Imagen prompt builders (one per style)
# ---------------------------------------------------------------------------

def _intimate_prompt(festival_name: str, poster_title: str) -> str:
    return f"""Festival: {festival_name}. Create a social-media-ready aviation poster for Instagram.

Think like a professional social media manager: emotional, warm, scroll-stopping. Real and believable, NOT over-produced.

Write an Imagen prompt for an INTIMATE CLOSE-UP (1:1 square).

Rules:
- ONE tight, emotionally resonant aviation detail that naturally fits {festival_name}: pilot hands resting on controls at golden hour, passenger hands near a window with soft clouds outside, an empty first-class seat by an oval window at dawn. Real, quiet, human.
- Partial human elements (hands, forearm, silhouette) allowed if they add warmth — never a full face.
- Shallow depth of field, natural warm or blue-hour light. Shot on 50mm lens. NO fake bokeh rings, no CGI.
- Bottom 35–40% must fall into natural deep shadow (dark seat, dark cockpit panel, dark cabin) — no gradient strip.
- TEXT: "{poster_title}" bottom-left, white Helvetica Neue Bold, title case. Clean, no box.
- No logos. No URL. No other text. Only "{poster_title}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""


def _celebration_prompt(festival_name: str, poster_title: str) -> str:
    return f"""Festival: {festival_name}. Create a social-media-ready aviation poster for Instagram.

Think like a professional social media manager: patriotic, energetic, real-looking. NOT over-produced or fantasy.

Write an Imagen prompt for a CELEBRATION / AIRSHOW WIDE SHOT (1:1 square).

Rules:
- TWO or THREE military jets in tight formation flying low over an airfield, coloured smoke trails in {festival_name} national colours. Wide angle, shot from ground level, crowd silhouettes at the very bottom edge.
- Real daylight or golden-hour light. Crisp jet detail. No CGI texture.
- Crowd is dark silhouette only at the bottom 15% — no faces, no detail.
- Bottom 25–30% naturally dark from crowd shadow and dark ground.
- TEXT: "{poster_title}" bottom-left, white Helvetica Neue Bold, title case. Clean, no box.
- No logos. No URL. No other text. Only "{poster_title}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""


def _cinematic_prompt(festival_name: str, poster_title: str) -> str:
    return f"""Festival: {festival_name}. Create a social-media-ready aviation poster for Instagram.

Think like a professional social media manager: the image must stop the scroll, feel real, and be instantly beautiful. NOT over-produced, NOT a fantasy composite.

Write an Imagen prompt for a CINEMATIC WIDE SHOT (1:1 square).

Rules:
- ONE aircraft (commercial airliner silhouette or wide-body jet) on a runway or taking off, photographed from ground level or low angle. The aircraft is the clear subject.
- ONE single atmospheric element from {festival_name} in the sky — just one: either sky lanterns drifting, OR fireworks bursting, OR snowfall, OR golden dusk light. NOT multiple combined. Pick whichever single element is most iconic for {festival_name}.
- Sky fills the upper 65% of the frame. Natural, real-looking light — no CGI glow, no over-saturated colours. Think National Geographic quality.
- Bottom 30% is dark naturally (runway tarmac at night, dark horizon) — no fake gradient.
- TEXT: "{poster_title}" bottom-left, white Helvetica Neue Bold, title case. Clean, no box.
- No logos. No URL. No other text. Only "{poster_title}".

Return ONLY the image generation prompt. Aspect ratio 1:1."""


# Public entry point used by content_service
_STYLE_BUILDERS = {
    "intimate": _intimate_prompt,
    "celebration": _celebration_prompt,
    "cinematic": _cinematic_prompt,
}


def build_festival_imagen_prompt_request(festival_name: str, poster_title: str) -> str:
    """
    Return the Gemini request that asks the model to write an Imagen prompt
    for a festival poster, choosing the correct style automatically.
    """
    style = get_festival_style(festival_name)
    return _STYLE_BUILDERS[style](festival_name, poster_title)
