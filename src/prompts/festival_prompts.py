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

def _intimate_prompt(festival_name: str, poster_title: str, font_desc: str) -> str:
    return f"""You are a world-class aviation photographer and Instagram art director. Create a photorealistic, cinematic Imagen prompt for a {festival_name} festival post for the AIRMAN brand.

MOOD: Intimate, warm, emotionally resonant — feels like a real photograph, not a render.

SCENE DIRECTION:
- ONE tightly framed aviation detail that emotionally connects to {festival_name}: e.g. a pilot's gloved hands resting on the yoke as warm festival light streams through the cockpit window, or a passenger's hand beside an oval window with soft festival colours glowing in the clouds below.
- Partial human presence only (hands, forearm, silhouette edge) — never a full face.
- Shot on a Sony A7R V with a 85mm f/1.4 lens. Shallow depth of field, subject razor-sharp, background melts into warm bokeh. Film grain texture, not digital clean.
- Lighting: natural — golden hour, candle-warm, or cool blue-hour. Never artificial studio light.
- Colour grade: muted warm tones or desaturated cool blues. Think Roger Deakins. NO over-saturation.
- Bottom 35–40% falls into natural deep shadow (dark cockpit panel, dark cabin floor, dark seat leather) — organic, not a gradient overlay.
- Composition: subject occupies centre-left. Right side breathes open.

TEXT OVERLAY (mandatory, rendered IN the image):
- Text: "{poster_title}"
- Position: bottom-left corner, clear of subject
- Style: white, {font_desc}, title case, no background box, no shadow box
- No logos. No URLs. No other text whatsoever. Only "{poster_title}".

Output: ONE single Imagen generation prompt only. No explanation. Do NOT include aspect ratio or any spec notes in the prompt."""


def _celebration_prompt(festival_name: str, poster_title: str, font_desc: str) -> str:
    return f"""You are a world-class aviation photographer and Instagram art director. Create a photorealistic, cinematic Imagen prompt for a {festival_name} festival post for the AIRMAN brand.

MOOD: Triumphant, energetic, patriotic — feels like a real press photograph from an airshow.

SCENE DIRECTION:
- TWO or THREE military jets in tight delta formation, captured mid-pass low over an airfield at high speed. Coloured smoke trails in colours iconic to {festival_name}.
- Camera angle: ground level, wide 24mm lens, slight upward tilt. Jets fill the upper two-thirds of frame.
- Crowd silhouettes occupy only the bottom 10–15% of the frame — dark, no faces, no individual detail.
- Lighting: harsh midday sun OR dramatic golden hour backlight creating lens flare along the jet edges. Real light, not CGI.
- Motion blur on smoke trails to convey speed. Aircraft body crisp and detailed — rivets, markings, exhaust heat shimmer visible.
- Colour grade: high contrast, slightly desaturated — like a TIME Magazine cover shot. No oversaturation.
- Bottom 25% naturally dark from crowd shadow and dark tarmac.

TEXT OVERLAY (mandatory, rendered IN the image):
- Text: "{poster_title}"
- Position: bottom-left corner
- Style: white, {font_desc}, title case, no background box
- No logos. No URLs. No other text. Only "{poster_title}".

Output: ONE single Imagen generation prompt only. No explanation. Do NOT include aspect ratio or any spec notes in the prompt."""


def _cinematic_prompt(festival_name: str, poster_title: str, font_desc: str) -> str:
    return f"""You are a world-class aviation photographer and Instagram art director. Create a photorealistic, cinematic Imagen prompt for a {festival_name} festival post for the AIRMAN brand.

MOOD: Epic, awe-inspiring, scroll-stopping — feels like a real photograph shot for a magazine cover.

SCENE DIRECTION:
- ONE wide-body commercial aircraft (A380 or Boeing 777 silhouette) either on a rain-wet runway at night OR lifting off at low angle against a dramatic sky.
- Camera: ground level or low 3-point angle, 24mm wide lens. Aircraft dominates 50–60% of the frame. Sky owns the upper half.
- ONE single atmospheric element tied to {festival_name} visible in the sky — choose whichever single element is most visually iconic for this festival (e.g. distant fireworks, drifting sky lanterns, heavy snowfall, a blood-orange dusk). Do NOT combine multiple elements.
- Lighting: the scene is lit by that atmospheric element + ambient — no studio lights, no artificial fill. If fireworks: their burst glow reflects on the wet tarmac. If lanterns: warm orange glow halos the fuselage. If snow: cold blue-white moonlight. If dusk: long shadow from the aircraft.
- Photography style: National Geographic meets Roger Deakins. Film grain, natural vignette, slightly underexposed midtones, luminous highlights.
- Colour grade: cinematic — deep shadows, rich blacks, muted midtones, glowing highlights. No HDR look, no over-sharpening.
- Bottom 30% is deep black naturally (wet tarmac reflections, dark ground, runway edge lights).

TEXT OVERLAY (mandatory, rendered IN the image):
- Text: "{poster_title}"
- Position: bottom-left corner, sitting just above the dark ground zone
- Style: white, {font_desc}, title case, no background box, no outline
- No logos. No URLs. No other text. Only "{poster_title}".

Output: ONE single Imagen generation prompt only. No explanation. Do NOT include aspect ratio or any spec notes in the prompt."""


# Public entry point used by content_service
_STYLE_BUILDERS = {
    "intimate": _intimate_prompt,
    "celebration": _celebration_prompt,
    "cinematic": _cinematic_prompt,
}


def build_festival_imagen_prompt_request(
    festival_name: str, poster_title: str, font_desc: str
) -> str:
    """
    Return the Gemini request that asks the model to write an Imagen prompt
    for a festival poster, choosing the correct style automatically.

    font_desc: visual description of the chosen Google Font (from font_styles.py).
    """
    style = get_festival_style(festival_name)
    return _STYLE_BUILDERS[style](festival_name, poster_title, font_desc)
